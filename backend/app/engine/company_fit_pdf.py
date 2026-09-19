import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas

from app.engine.specialized_generators.base import (
    COLOR_BRAND_NAVY, COLOR_BRAND_AMBER, COLOR_BRAND_SLATE, COLOR_BRAND_MUTED,
    COLOR_BRAND_BORDER_LIGHT, COLOR_BRAND_BG_LIGHT, COLOR_BRAND_CYAN,
    format_currency
)

class CompanyFitCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def showPage(self):
        # Footer
        self.setStrokeColor(COLOR_BRAND_BORDER_LIGHT)
        self.setLineWidth(0.5)
        self.line(40, 44, 572, 44)

        self.setFont("Helvetica", 6.5)
        self.setFillColor(COLOR_BRAND_MUTED)
        self.drawString(40, 34, "© terminal.aixenergy.io · AI-generated for internal use only · Public records basis")

        super().showPage()

def generate_company_fit_pdf(snapshot: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=38,
        rightMargin=38,
        topMargin=46,
        bottomMargin=46
    )
    
    styles = getSampleStyleSheet()
    
    style_super_title = ParagraphStyle(
        'SuperTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=COLOR_BRAND_AMBER, textTransform='uppercase', spaceAfter=2
    )
    style_h1 = ParagraphStyle(
        'MainH1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=COLOR_BRAND_NAVY, spaceAfter=8
    )
    style_h2 = ParagraphStyle(
        'SectionH2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=12,
        textColor=COLOR_BRAND_NAVY, spaceBefore=10, spaceAfter=5
    )
    style_body = ParagraphStyle(
        'BodyDark', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11,
        textColor=COLOR_BRAND_SLATE
    )
    style_mono = ParagraphStyle(
        'MonoTable', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=COLOR_BRAND_NAVY
    )
    style_mono_amber = ParagraphStyle(
        'MonoAmber', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=COLOR_BRAND_AMBER
    )
    style_table_cell = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11,
        textColor=COLOR_BRAND_SLATE
    )
    style_table_header = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=colors.white
    )
    
    story = []
    
    date_str = datetime.fromisoformat(snapshot.get("snapshot_date", datetime.utcnow().isoformat())).strftime("%Y-%m-%d")
    
    story.append(Paragraph("Energy Innovation Terminal by AIxEnergy", style_super_title))
    story.append(Paragraph(f"FOA / Company Fit Snapshot — {date_str}", style_h1))
    
    comp = snapshot.get("company", {})
    name = comp.get("name") or "Unknown Company"
    tech = ", ".join(comp.get("tech_tags", [])) if comp.get("tech_tags") else "N/A"
    trl = comp.get("trl") or "N/A"
    app_type = comp.get("applicant_type") or "N/A"
    desc = str(comp.get("description", ""))[:200]
    
    story.append(Paragraph(f"<b>Company:</b> {name} &nbsp;&nbsp; <b>Tech:</b> {tech} &nbsp;&nbsp; <b>TRL:</b> {trl} &nbsp;&nbsp; <b>Type:</b> {app_type}", style_body))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<i>{desc}</i>", style_body))
    
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Top FOA Classes", style_h2))
    top_classes = snapshot.get("top_foa_classes", [])
    if top_classes:
        for tc in top_classes:
            score_pct = int(tc.get("fit_score", 0) * 100)
            
            ex_sol = tc.get("example_solicitations", [])
            ex_sol_text = ""
            if ex_sol:
                sol = ex_sol[0]
                sol_num = sol.get('solicitation_number', 'N/A')
                sol_name = sol.get('name', '')[:60]
                max_award = sol.get('max_per_award')
                award_text = f" ({format_currency(max_award)})" if max_award else ""
                ex_sol_text = f"Example: {sol_num} — {sol_name}{award_text}"
            
            card_data = [
                [
                    Paragraph(f"<b>{tc.get('class_label')}</b>", style_mono),
                    Paragraph(f"{tc.get('agency')}", style_table_cell),
                    Paragraph(f"<b>{tc.get('window_risk').upper()}</b>", style_mono_amber),
                    Paragraph(f"Fit: {score_pct}%", style_mono)
                ],
                [
                    Paragraph(tc.get('why_fit', ''), style_table_cell),
                    "", "", ""
                ],
                [
                    Paragraph(f"<font color='#64748B'>{ex_sol_text}</font>", style_table_cell),
                    "", "", ""
                ]
            ]
            
            t = Table(card_data, colWidths=[200, 150, 100, 80])
            t.setStyle(TableStyle([
                ('SPAN', (0, 1), (3, 1)),
                ('SPAN', (0, 2), (3, 2)),
                ('BACKGROUND', (0, 0), (-1, -1), COLOR_BRAND_BG_LIGHT),
                ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(t)
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No well-matched FOA classes found for this profile.", style_body))
        
    story.append(Spacer(1, 10))
    
    misfit = snapshot.get("misfit_warnings", [])
    if misfit:
        story.append(Paragraph("Misfit Warnings", style_h2))
        for mw in misfit:
            warn_data = [[
                Paragraph(f"<b>⚠ Wrong FOA Class to Avoid: {mw.get('class_label')}</b>", style_mono),
            ], [
                Paragraph(mw.get('why_wrong', ''), style_table_cell)
            ]]
            tw = Table(warn_data, colWidths=[530])
            tw.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FEF2F2')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#DC2626')),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(tw)
            story.append(Spacer(1, 6))
            
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"▶ {snapshot.get('recommended_next_action', '')}", ParagraphStyle('Action', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=COLOR_BRAND_AMBER)))
    
    doc.build(story, canvasmaker=CompanyFitCanvas)
    buffer.seek(0)
    return buffer
