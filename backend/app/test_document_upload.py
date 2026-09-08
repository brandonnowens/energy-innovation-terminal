"""Test script to verify document extraction, LLM analysis, and project matching."""

import io
import sys
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestDocumentUpload")

def create_sample_docx() -> bytes:
    """Creates an in-memory sample DOCX technical proposal."""
    import docx
    doc = docx.Document()
    doc.add_heading("Next-Gen Solid-State Battery Electrolyte Scaling", level=1)
    doc.add_paragraph(
        "Project Scope: Development and pilot roll-to-roll manufacturing of a non-flammable ceramic solid-state "
        "lithium-metal electrolyte achieving >450 Wh/kg energy density and 1,500 continuous fast-charge cycles (10C) "
        "for electric vehicles and aerospace applications."
    )
    doc.add_heading("Technical Milestones & Work Breakdown", level=2)
    doc.add_paragraph("Workstream 1: Synthesis and automated roll-to-roll coating at TRL 5 in relevant lab environment.")
    doc.add_paragraph("Workstream 2: Third-party cell pouch assembly and thermal runaway testing at 150°C.")

    # Add a budget table
    table = doc.add_table(rows=3, cols=2)
    table.rows[0].cells[0].text = "Category"
    table.rows[0].cells[1].text = "Amount (USD)"
    table.rows[1].cells[0].text = "Pilot Scale Equipment & Gloveboxes"
    table.rows[1].cells[1].text = "$6,500,000"
    table.rows[2].cells[0].text = "Total Estimated CapEx"
    table.rows[2].cells[1].text = "$12,000,000"

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def create_sample_pptx() -> bytes:
    """Creates an in-memory sample PPTX pitch deck."""
    import pptx
    prs = pptx.Presentation()
    
    # Slide 1: Title
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Modular Direct Air Capture (DAC) Scale-Up"
    slide.placeholders[1].text = "Solid Sorbent Low-Temperature Desorption Pilot · Boulder, CO"

    # Slide 2: Technical Overview
    slide_layout2 = prs.slide_layouts[1]
    slide2 = prs.slides.add_slide(slide_layout2)
    slide2.shapes.title.text = "Value Proposition & Energy Performance"
    slide2.placeholders[1].text = (
        "• Target Cost: <$150/ton CO2 captured utilizing low-temperature industrial waste heat\n"
        "• Capacity: 10,000 metric tons CO2/year modular demonstration\n"
        "• Technology Stage: TRL 6 pilot demonstration\n"
        "• Teaming Partners: National Renewable Energy Laboratory (NREL) and Regional Cement Facility"
    )

    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()


def create_sample_pdf() -> bytes:
    """Creates an in-memory sample PDF proposal."""
    import pymupdf as fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 72),
        "Dynamic Line Rating (DLR) and Transmission Microgrid Deployment\n\n"
        "Applicant: California Electric Utility Partner / Technology Provider\n"
        "Location: California (CA)\n"
        "Target Readiness: TRL 7 operational demonstration\n"
        "Budget: $15,000,000 total capital expenditure\n"
        "Scope: Installation of real-time Dynamic Line Rating LiDAR sensors and power flow controllers "
        "across 150 miles of congested high-voltage transmission lines, paired with a 10 MW black-start substation microgrid."
    )
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def create_sample_xlsx() -> bytes:
    """Creates an in-memory sample XLSX budget sheet."""
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Budget Breakdown"
    ws.append(["Line Item", "Year 1 ($)", "Year 2 ($)", "Total ($)"])
    ws.append(["Direct Labor & Engineering", 1500000, 2000000, 3500000])
    ws.append(["Demonstration Hardware & Microgrid Inverters", 4000000, 2500000, 6500000])
    ws.append(["Utility Interconnection & M&V", 500000, 500000, 1000000])
    ws.append(["Total Project CapEx", 6000000, 5000000, 11000000])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_extraction_and_analysis():
    from app.engine.document_extractor import extract_multiple_documents
    from app.engine.project_doc_analyzer import analyze_project_documents

    docx_bytes = create_sample_docx()
    pptx_bytes = create_sample_pptx()
    pdf_bytes = create_sample_pdf()
    xlsx_bytes = create_sample_xlsx()

    files = [
        ("Solid_State_Battery_Proposal.docx", docx_bytes),
        ("Modular_DAC_Pitch_Deck.pptx", pptx_bytes),
        ("DLR_Microgrid_Spec.pdf", pdf_bytes),
        ("Project_Budget_Waterfall.xlsx", xlsx_bytes),
    ]

    logger.info(f"Extracting {len(files)} multi-format files...")
    extracted = extract_multiple_documents(files)

    assert extracted["total_files"] == 4, "Should extract 4 files"
    assert extracted["success_count"] == 4, "All 4 files should extract successfully"
    assert len(extracted["combined_text"]) > 500, "Should have rich text corpus"
    logger.info(f"Extraction successful: {extracted['total_words']} words, {extracted['total_bytes']} bytes across 4 documents")

    for doc in extracted["documents"]:
        logger.info(f"  - {doc['filename']}: {doc['doc_type']} ({doc['word_count']} words, status={doc['status']})")

    logger.info("Running AI Project Document Analysis...")
    profile = analyze_project_documents(
        document_corpus=extracted["combined_text"],
        doc_metadata=extracted["documents"],
    )

    logger.info(f"Analyzed Project Title: {profile['project_title']}")
    logger.info(f"Technologies: {profile['technology_areas']}")
    logger.info(f"Activities: {profile['activity_types']}")
    logger.info(f"TRL: {profile['estimated_trl']} ({profile['trl_rationale']})")
    logger.info(f"Cost: ${profile['estimated_cost']:,.0f}")
    logger.info(f"Applicant: {profile['applicant_type']}, Location: {profile['location']}")
    logger.info(f"Key Innovations ({len(profile['key_innovations'])}): {profile['key_innovations']}")
    logger.info(f"Quantitative Targets: {profile['quantitative_targets']}")
    logger.info(f"Engine Used: {profile['engine_used']}")

    assert profile["estimated_trl"] in range(1, 10), "TRL must be 1-9"
    assert profile["estimated_cost"] > 0, "Cost must be positive"
    assert len(profile["technology_areas"]) > 0, "Must have technology areas"
    assert len(profile["summary"]) > 100, "Summary must be rich"

    logger.info("ALL EXTRACTION AND ANALYSIS TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_extraction_and_analysis()
