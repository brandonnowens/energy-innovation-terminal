"""Multi-format project document extractor with multi-tier fallback parsing.

Extracts text, structural hierarchy, and metadata from:
- PDF (.pdf) - PyMuPDF page text, block text, metadata, form fields, and raw stream recovery
- Word (.docx, .doc) - python-docx, direct OpenXML zip parsing, RTF, and binary OLE string extraction
- PowerPoint (.pptx, .ppt) - python-pptx (including recursive group shapes, tables, notes), direct OpenXML zip parsing, and binary string extraction
- Excel & CSV (.xlsx, .xls, .csv) - openpyxl, sharedStrings XML parsing, and CSV sniffer
- Plain Text & Markdown (.txt, .md, .rtf, .json, .yaml) - multi-encoding fallback
"""

import io
import re
import csv
import zipfile
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

logger = logging.getLogger("DocumentExtractor")


def _clean_text(text: str) -> str:
    """Cleans up excessive whitespace, null bytes, and control characters."""
    if not text:
        return ""
    # Remove null bytes and non-printable control chars (preserve newlines and tabs)
    text = text.replace("\x00", "")
    text = re.sub(r"[\r\f\v]", " ", text)
    # Normalize excessive spaces
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespaces per line
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def _extract_binary_strings(content: bytes, min_len: int = 4) -> str:
    """Extracts printable ASCII and UTF-16LE text strings from binary streams (for legacy .doc, .ppt, or corrupted files)."""
    extracted = []

    # 1. UTF-16LE strings (common in Microsoft Office binary formats)
    utf16_pattern = rb"(?:[\x20-\x7E\t\n]\x00){" + str(min_len).encode() + rb",}"
    for match in re.finditer(utf16_pattern, content):
        try:
            s = match.group(0).decode("utf-16le", errors="ignore").strip()
            if len(s) >= min_len and not re.match(r"^[\W_]+$", s):
                extracted.append(s)
        except Exception:
            continue

    # 2. ASCII strings
    ascii_pattern = rb"[\x20-\x7E\t\n]{" + str(min_len).encode() + rb",}"
    for match in re.finditer(ascii_pattern, content):
        try:
            s = match.group(0).decode("ascii", errors="ignore").strip()
            if len(s) >= min_len and not re.match(r"^[\W_]+$", s):
                extracted.append(s)
        except Exception:
            continue

    # Remove duplicates while preserving order
    seen = set()
    unique_lines = []
    for line in extracted:
        if line not in seen and len(line) > 3:
            seen.add(line)
            unique_lines.append(line)

    return "\n".join(unique_lines)


def _run_multimodal_ocr(images_bytes: List[bytes]) -> str:
    """
    Performs multimodal OCR and structural layout recovery on rasterized document page images
    using Gemini 2.5 Flash, OpenAI GPT-4o-mini, or Claude 3.5 Sonnet.
    Returns extracted markdown text preserving tables, headings, and budget metrics.
    """
    if not images_bytes:
        return ""

    import os
    import json
    import base64
    try:
        from app.config import settings
        openai_key = getattr(settings, "openai_api_key", None) or os.environ.get("OPENAI_API_KEY")
        gemini_key = getattr(settings, "gemini_api_key", None) or os.environ.get("GEMINI_API_KEY")
        anthropic_key = getattr(settings, "anthropic_api_key", None) or os.environ.get("ANTHROPIC_API_KEY")
    except Exception:
        openai_key = os.environ.get("OPENAI_API_KEY")
        gemini_key = os.environ.get("GEMINI_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if not (openai_key or gemini_key or anthropic_key):
        return ""

    prompt_instruction = (
        "You are an expert technical document OCR and document structure recovery engine. "
        "Extract all text, sections, headers, tables, financial figures, budget breakdowns, "
        "and technical specifications from these scanned document pages. "
        "Format your output cleanly in Markdown, preserving table structures with Markdown pipes."
    )

    # 1. Try Gemini
    if gemini_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=gemini_key)
            parts = [prompt_instruction]
            for img_b in images_bytes:
                parts.append(types.Part.from_bytes(data=img_b, mime_type="image/png"))
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=parts,
            )
            if response.text and len(response.text.strip()) > 20:
                logger.info("Successfully recovered scanned PDF text via Gemini 2.5 Flash Multimodal OCR")
                return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini multimodal OCR failed: {e}")

    # 2. Try OpenAI
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key, timeout=30.0, max_retries=2)
            content_list: List[Dict[str, Any]] = [{"type": "text", "text": prompt_instruction}]
            for img_b in images_bytes:
                b64 = base64.b64encode(img_b).decode("utf-8")
                content_list.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"}
                })
            
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a multimodal document parser. Output clean Markdown."},
                    {"role": "user", "content": content_list}
                ],
                max_tokens=3000,
                temperature=0.1,
            )
            extracted = resp.choices[0].message.content or ""
            if len(extracted.strip()) > 20:
                logger.info("Successfully recovered scanned PDF text via OpenAI GPT-4o-mini Multimodal OCR")
                return extracted.strip()
        except Exception as e:
            logger.warning(f"OpenAI multimodal OCR failed: {e}")

    # 3. Try Anthropic
    if anthropic_key:
        try:
            import urllib.request
            content_blocks: List[Dict[str, Any]] = [{"type": "text", "text": prompt_instruction}]
            for img_b in images_bytes:
                b64 = base64.b64encode(img_b).decode("utf-8")
                content_blocks.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": b64
                    }
                })
            req_data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 3000,
                "temperature": 0.1,
                "messages": [{"role": "user", "content": content_blocks}]
            }
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps(req_data).encode("utf-8"),
                headers={
                    "x-api-key": anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30.0) as r:
                res_json = json.loads(r.read().decode("utf-8"))
                extracted = res_json.get("content", [{}])[0].get("text", "")
                if len(extracted.strip()) > 20:
                    logger.info("Successfully recovered scanned PDF text via Claude 3.5 Sonnet Multimodal OCR")
                    return extracted.strip()
        except Exception as e:
            logger.warning(f"Anthropic multimodal OCR failed: {e}")

    return ""


def extract_from_pdf(content: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
    """Extracts text and metadata from PDF files using multi-tier strategies."""
    if not content:
        return {"filename": filename, "doc_type": "PDF Document", "file_size": 0, "text": "", "word_count": 0, "status": "error", "error": "Empty file (0 bytes)"}

    pages_text = []
    total_pages = 0
    doc_title = filename
    doc_author = ""
    doc_type = "PDF Document"
    doc_obj = None

    # Strategy 1: PyMuPDF standard text extraction
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz

        doc_obj = fitz.open(stream=content, filetype="pdf")
        total_pages = len(doc_obj)
        metadata = doc_obj.metadata or {}
        doc_title = metadata.get("title") or filename
        doc_author = metadata.get("author") or ""

        for page_num in range(total_pages):
            page = doc_obj[page_num]
            
            # Primary: plain text
            text = page.get_text("text").strip()

            # Secondary: block text if plain text is sparse
            if not text or len(text.split()) < 5:
                blocks = page.get_text("blocks")
                block_texts = [b[4].strip() for b in blocks if len(b) > 4 and b[4].strip()]
                if block_texts:
                    text = "\n".join(block_texts)

            if text:
                pages_text.append(f"### Page {page_num + 1}\n{text}")

    except Exception as e:
        logger.warning(f"PyMuPDF standard extraction encountered error on {filename}: {e}")

    full_text = "\n\n".join(pages_text)
    cleaned = _clean_text(full_text)
    words = len(cleaned.split())

    # Strategy 2: Multimodal OCR if extracted text is sparse (< 25 words) and pages exist
    if words < 25 and doc_obj is not None and total_pages > 0:
        logger.info(f"PDF {filename} contains only {words} words across {total_pages} pages. Attempting Multimodal OCR...")
        try:
            images_bytes = []
            for p_idx in range(min(total_pages, 5)):
                try:
                    pix = doc_obj[p_idx].get_pixmap(dpi=150)
                    images_bytes.append(pix.tobytes("png"))
                except Exception as p_err:
                    logger.warning(f"Failed to render page {p_idx+1} for OCR: {p_err}")
            
            if images_bytes:
                ocr_result = _run_multimodal_ocr(images_bytes)
                if ocr_result and len(ocr_result.split()) >= 10:
                    cleaned = _clean_text(ocr_result)
                    words = len(cleaned.split())
                    doc_type = "Scanned PDF (Multimodal OCR Recovered)"
        except Exception as ocr_err:
            logger.warning(f"Multimodal OCR pipeline encountered error for {filename}: {ocr_err}")

    if doc_obj is not None:
        try:
            doc_obj.close()
        except Exception:
            pass

    # Strategy 3: If extracted text is still empty (e.g. scanned or corrupted stream without OCR), extract binary strings
    if words < 5:
        logger.info(f"Attempting binary string recovery on PDF {filename}...")
        raw_strings = _extract_binary_strings(content, min_len=4)
        if raw_strings.strip():
            cleaned = _clean_text(f"### Extracted Document Content\n{raw_strings}")
            words = len(cleaned.split())

    return {
        "filename": filename,
        "doc_type": doc_type,
        "file_size": len(content),
        "page_count": total_pages or 1,
        "title": doc_title,
        "author": doc_author,
        "text": cleaned,
        "word_count": words,
        "status": "success" if words > 0 else "error",
        "error": "No extractable text found in PDF (file may be an image-only scan without OCR text layer)" if words == 0 else None,
    }


def _extract_docx_xml(content: bytes) -> str:
    """Directly extracts all text from a Word .docx zip package using XML parsing."""
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            extracted_parts = []
            
            # Read main document
            if "word/document.xml" in z.namelist():
                xml_data = z.read("word/document.xml")
                root = ET.fromstring(xml_data)
                # Word XML namespaces
                ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                for p in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
                    p_texts = [t.text for t in p.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if t.text]
                    if p_texts:
                        extracted_parts.append("".join(p_texts))

            # Also check headers and footers
            for name in z.namelist():
                if name.startswith("word/header") or name.startswith("word/footer") or name.startswith("word/footnotes"):
                    try:
                        xml_data = z.read(name)
                        root = ET.fromstring(xml_data)
                        texts = [t.text for t in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if t.text]
                        if texts:
                            extracted_parts.append(" ".join(texts))
                    except Exception:
                        continue

            return "\n\n".join(extracted_parts)
    except Exception as e:
        logger.warning(f"Direct XML docx extraction failed: {e}")
        return ""


def extract_from_docx(content: bytes, filename: str = "document.docx") -> Dict[str, Any]:
    """Extracts structured text from Word DOCX files with multi-tier fallback."""
    if not content:
        return {"filename": filename, "doc_type": "Word Document (.docx)", "file_size": 0, "text": "", "word_count": 0, "status": "error", "error": "Empty file (0 bytes)"}

    paragraphs_text = []

    # Strategy 1: python-docx library
    try:
        import docx
        doc = docx.Document(io.BytesIO(content))

        for p in doc.paragraphs:
            txt = p.text.strip()
            if not txt:
                continue
            style_name = p.style.name.lower() if p.style and p.style.name else ""
            if "heading 1" in style_name:
                paragraphs_text.append(f"# {txt}")
            elif "heading 2" in style_name:
                paragraphs_text.append(f"## {txt}")
            elif "heading 3" in style_name:
                paragraphs_text.append(f"### {txt}")
            elif "bullet" in style_name or "list" in style_name:
                paragraphs_text.append(f"- {txt}")
            else:
                paragraphs_text.append(txt)

        # Extract tables
        for table_idx, table in enumerate(doc.tables, 1):
            table_rows = []
            for row in table.rows:
                row_cells = [c.text.strip().replace("\n", " ") for c in row.cells]
                if any(row_cells):
                    table_rows.append(" | ".join(row_cells))
            if table_rows:
                paragraphs_text.append(f"\n[Table {table_idx}]\n" + "\n".join(table_rows) + "\n")
    except Exception as e:
        logger.warning(f"python-docx parsing encountered error for {filename}: {e}")

    full_text = "\n\n".join(paragraphs_text)

    # Strategy 2: Direct XML Zip parsing if python-docx returned empty or failed
    if not full_text.strip():
        logger.info(f"Attempting direct OpenXML extraction on {filename}...")
        full_text = _extract_docx_xml(content)

    # Strategy 3: Binary string recovery
    if not full_text.strip():
        logger.info(f"Attempting binary string recovery on Word document {filename}...")
        full_text = _extract_binary_strings(content, min_len=4)

    cleaned = _clean_text(full_text)
    words = len(cleaned.split())

    return {
        "filename": filename,
        "doc_type": "Word Document (.docx)",
        "file_size": len(content),
        "text": cleaned,
        "word_count": words,
        "status": "success" if words > 0 else "error",
        "error": "No readable text could be extracted from Word document" if words == 0 else None,
    }


def _extract_pptx_shapes_recursive(shape) -> List[str]:
    """Recursively extracts text from any PowerPoint shape, including GroupShapes and tables."""
    texts = []

    # Check text frame
    if hasattr(shape, "has_text_frame") and shape.has_text_frame:
        txt = shape.text_frame.text.strip()
        if txt:
            texts.append(txt)

    # Check table
    elif hasattr(shape, "has_table") and shape.has_table:
        table = shape.table
        table_rows = []
        for row in table.rows:
            row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            if any(row_cells):
                table_rows.append(" | ".join(row_cells))
        if table_rows:
            texts.append("\n".join(table_rows))

    # Check group shapes (recursive traversal)
    elif hasattr(shape, "shapes"):
        for sub_shape in shape.shapes:
            texts.extend(_extract_pptx_shapes_recursive(sub_shape))

    return texts


def _extract_pptx_xml(content: bytes) -> str:
    """Directly extracts slide text from PowerPoint .pptx zip package using XML parsing."""
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            slides_text = []
            slide_files = sorted([f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")])

            for idx, slide_file in enumerate(slide_files, 1):
                try:
                    xml_data = z.read(slide_file)
                    root = ET.fromstring(xml_data)
                    texts = [t.text for t in root.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}t") if t.text]
                    if texts:
                        slides_text.append(f"### Slide {idx}\n" + "\n".join(texts))
                except Exception:
                    continue

            return "\n\n".join(slides_text)
    except Exception as e:
        logger.warning(f"Direct XML pptx extraction failed: {e}")
        return ""


def extract_from_pptx(content: bytes, filename: str = "presentation.pptx") -> Dict[str, Any]:
    """Extracts slides, titles, shapes, tables, and notes from PowerPoint PPTX with multi-tier fallback."""
    if not content:
        return {"filename": filename, "doc_type": "PowerPoint Presentation (.pptx)", "file_size": 0, "text": "", "word_count": 0, "status": "error", "error": "Empty file (0 bytes)"}

    slides_text = []
    slide_count = 0

    # Strategy 1: python-pptx
    try:
        import pptx
        prs = pptx.Presentation(io.BytesIO(content))
        slide_count = len(prs.slides)

        for slide_idx, slide in enumerate(prs.slides, 1):
            slide_parts = []
            slide_title = ""

            # Title
            if slide.shapes.title and slide.shapes.title.text.strip():
                slide_title = slide.shapes.title.text.strip()
                slide_parts.append(f"Title: {slide_title}")

            # All shapes (including groups and tables)
            for shape in slide.shapes:
                if shape == slide.shapes.title:
                    continue
                shape_texts = _extract_pptx_shapes_recursive(shape)
                for st in shape_texts:
                    if st != slide_title and st not in slide_parts:
                        slide_parts.append(st)

            # Speaker notes
            if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
                notes = slide.notes_slide.notes_text_frame.text.strip()
                if notes:
                    slide_parts.append(f"[Speaker Notes: {notes}]")

            if slide_parts:
                header = f"### Slide {slide_idx}: {slide_title}" if slide_title else f"### Slide {slide_idx}"
                slides_text.append(f"{header}\n" + "\n".join(slide_parts))
    except Exception as e:
        logger.warning(f"python-pptx parsing encountered error for {filename}: {e}")

    full_text = "\n\n".join(slides_text)

    # Strategy 2: Direct XML Zip parsing
    if not full_text.strip():
        logger.info(f"Attempting direct OpenXML extraction on PowerPoint {filename}...")
        full_text = _extract_pptx_xml(content)

    # Strategy 3: Binary string recovery
    if not full_text.strip():
        logger.info(f"Attempting binary string recovery on PowerPoint {filename}...")
        full_text = _extract_binary_strings(content, min_len=4)

    cleaned = _clean_text(full_text)
    words = len(cleaned.split())

    return {
        "filename": filename,
        "doc_type": "PowerPoint Presentation (.pptx)",
        "file_size": len(content),
        "slide_count": slide_count or 1,
        "text": cleaned,
        "word_count": words,
        "status": "success" if words > 0 else "error",
        "error": "No readable text could be extracted from PowerPoint presentation" if words == 0 else None,
    }


def extract_from_doc_or_ppt_binary(content: bytes, filename: str = "document.doc") -> Dict[str, Any]:
    """Extracts text from legacy binary Word (.doc) or PowerPoint (.ppt) files."""
    if not content:
        return {"filename": filename, "doc_type": "Legacy Office Document", "file_size": 0, "text": "", "word_count": 0, "status": "error", "error": "Empty file (0 bytes)"}

    # Check if it might actually be a modern .docx/.pptx renamed to .doc/.ppt
    if content.startswith(b"PK\x03\x04"):
        if filename.lower().endswith(".doc") or filename.lower().endswith(".docx"):
            return extract_from_docx(content, filename)
        else:
            return extract_from_pptx(content, filename)

    # Check if it is an RTF file
    if content.startswith(b"{\\rtf"):
        return extract_from_plain_text(content, filename)

    # Extract binary strings (UTF-16LE and ASCII)
    full_text = _extract_binary_strings(content, min_len=4)
    cleaned = _clean_text(full_text)
    words = len(cleaned.split())

    return {
        "filename": filename,
        "doc_type": "Legacy Office Document (.doc/.ppt)",
        "file_size": len(content),
        "text": cleaned,
        "word_count": words,
        "status": "success" if words > 0 else "error",
        "error": "No readable text could be extracted from binary document" if words == 0 else None,
    }


def extract_from_spreadsheet(content: bytes, filename: str = "sheet.xlsx") -> Dict[str, Any]:
    """Extracts tabular data, budget figures, and milestone sheets from Excel or CSV files."""
    if not content:
        return {"filename": filename, "doc_type": "Spreadsheet", "file_size": 0, "text": "", "word_count": 0, "status": "error", "error": "Empty file (0 bytes)"}

    ext = Path(filename).suffix.lower()

    if ext == ".csv" or not content.startswith(b"PK\x03\x04"):
        for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                text_str = content.decode(enc)
                reader = csv.reader(io.StringIO(text_str))
                rows = [" | ".join(r) for r in reader if any(r)]
                if rows:
                    full_text = "\n".join(rows[:200])
                    cleaned = _clean_text(full_text)
                    return {
                        "filename": filename,
                        "doc_type": "CSV Spreadsheet",
                        "file_size": len(content),
                        "row_count": len(rows),
                        "text": cleaned,
                        "word_count": len(cleaned.split()),
                        "status": "success",
                    }
            except Exception:
                continue

    # Openpyxl for Excel XLSX
    sheet_texts = []
    sheet_count = 0
    try:
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
        sheet_count = len(wb.sheetnames)

        for sheet_name in wb.sheetnames[:5]:
            sheet = wb[sheet_name]
            rows_data = []
            for row in sheet.iter_rows(values_only=True):
                if any(v is not None for v in row):
                    formatted_cells = [str(c).strip() if c is not None else "" for c in row]
                    rows_data.append(" | ".join(formatted_cells[:12]))
                if len(rows_data) >= 80:
                    break

            if rows_data:
                sheet_texts.append(f"### Sheet: {sheet_name}\n" + "\n".join(rows_data))
        wb.close()
    except Exception as e:
        logger.warning(f"openpyxl parsing failed for {filename}: {e}")

    full_text = "\n\n".join(sheet_texts)

    # Fallback to binary strings if needed
    if not full_text.strip():
        full_text = _extract_binary_strings(content, min_len=4)

    cleaned = _clean_text(full_text)
    words = len(cleaned.split())

    return {
        "filename": filename,
        "doc_type": "Excel Spreadsheet (.xlsx)",
        "file_size": len(content),
        "sheet_count": sheet_count or 1,
        "text": cleaned,
        "word_count": words,
        "status": "success" if words > 0 else "error",
        "error": "No readable table data found in spreadsheet" if words == 0 else None,
    }


def extract_from_plain_text(content: bytes, filename: str = "document.txt") -> Dict[str, Any]:
    """Decodes plain text, Markdown, or RTF with encoding fallbacks."""
    if not content:
        return {"filename": filename, "doc_type": "Text Document", "file_size": 0, "text": "", "word_count": 0, "status": "error", "error": "Empty file (0 bytes)"}

    decoded_text = ""
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252", "utf-16", "utf-16-le", "utf-16-be"]:
        try:
            decoded_text = content.decode(enc)
            if decoded_text:
                break
        except UnicodeDecodeError:
            continue

    if not decoded_text:
        decoded_text = content.decode("ascii", errors="ignore")

    # Simple RTF tag stripper if .rtf or begins with {\rtf
    if filename.lower().endswith(".rtf") or decoded_text.startswith("{\\rtf"):
        decoded_text = re.sub(r"\\[a-z0-9\-]+ ?|[{}]", "", decoded_text)

    clean = _clean_text(decoded_text)
    words = len(clean.split())

    return {
        "filename": filename,
        "doc_type": "Text Document",
        "file_size": len(content),
        "text": clean,
        "word_count": words,
        "status": "success" if words > 0 else "error",
        "error": "Empty text file" if words == 0 else None,
    }


def extract_document_text(filename: str, content: bytes) -> Dict[str, Any]:
    """
    Dispatches document extraction based on magic bytes and file extension.
    Auto-detects format even if file extension is missing or incorrect.
    """
    if not content or len(content) == 0:
        return {
            "filename": filename,
            "doc_type": "Empty Document",
            "file_size": 0,
            "text": "",
            "word_count": 0,
            "status": "error",
            "error": f"The uploaded file '{filename}' is empty (0 bytes). Please upload a valid document.",
        }

    ext = Path(filename).suffix.lower()

    # Magic byte inspection
    is_pdf = content.startswith(b"%PDF-") or ext == ".pdf"
    is_zip = content.startswith(b"PK\x03\x04")
    is_ole = content.startswith(b"\xd0\xcf\x11\xe0")
    is_rtf = content.startswith(b"{\\rtf")

    try:
        if is_pdf:
            return extract_from_pdf(content, filename)
        elif is_zip:
            # Determine if docx, pptx, or xlsx
            if ext in [".docx", ".docm"] or "word/" in str(content[:1000]):
                return extract_from_docx(content, filename)
            elif ext in [".pptx", ".pptm"] or "ppt/" in str(content[:1000]):
                return extract_from_pptx(content, filename)
            elif ext in [".xlsx", ".xlsm"] or "xl/" in str(content[:1000]):
                return extract_from_spreadsheet(content, filename)
            else:
                # Try docx then pptx
                res = extract_from_docx(content, filename)
                if res.get("text"):
                    return res
                return extract_from_pptx(content, filename)
        elif is_ole:
            return extract_from_doc_or_ppt_binary(content, filename)
        elif is_rtf:
            return extract_from_plain_text(content, filename)
        elif ext in [".docx", ".doc"]:
            return extract_from_docx(content, filename)
        elif ext in [".pptx", ".ppt"]:
            return extract_from_pptx(content, filename)
        elif ext in [".xlsx", ".xls", ".csv", ".tsv"]:
            return extract_from_spreadsheet(content, filename)
        else:
            return extract_from_plain_text(content, filename)

    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {e}", exc_info=True)
        # Ultimate fallback: binary string extraction
        raw_fallback = _extract_binary_strings(content, min_len=4)
        if raw_fallback.strip():
            cleaned = _clean_text(raw_fallback)
            return {
                "filename": filename,
                "doc_type": "Recovered Binary Document",
                "file_size": len(content),
                "text": cleaned,
                "word_count": len(cleaned.split()),
                "status": "success",
            }

        return {
            "filename": filename,
            "doc_type": "Unreadable Document",
            "file_size": len(content),
            "text": "",
            "word_count": 0,
            "status": "error",
            "error": f"Failed to parse '{filename}': {str(e)}",
        }


def extract_multiple_documents(files: List[Tuple[str, bytes]]) -> Dict[str, Any]:
    """Extracts and consolidates multiple project documents into a structured corpus."""
    extracted_docs = []
    combined_sections = []
    total_bytes = 0
    total_words = 0

    for filename, content in files:
        doc_result = extract_document_text(filename, content)
        extracted_docs.append(doc_result)
        total_bytes += doc_result.get("file_size", len(content))
        total_words += doc_result.get("word_count", 0)

        if doc_result.get("text") and doc_result["text"].strip():
            combined_sections.append(
                f"=================================================================\n"
                f"DOCUMENT: {filename} ({doc_result.get('doc_type', 'Document')})\n"
                f"=================================================================\n\n"
                f"{doc_result['text']}\n"
            )

    full_corpus = "\n\n".join(combined_sections)

    return {
        "documents": extracted_docs,
        "combined_text": full_corpus,
        "total_files": len(files),
        "total_bytes": total_bytes,
        "total_words": total_words,
        "success_count": sum(1 for d in extracted_docs if d.get("status") == "success" and d.get("text")),
    }
