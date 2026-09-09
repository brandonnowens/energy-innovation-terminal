"""
Recipient Funding Dossier PDF Report Generator.

Generates an institutional-grade, multi-page publication PDF report containing:
1. Executive Identity Banner & Technology Classification
2. 5-Stage Capital Continuum Financial Ledger (Grants, SEC Reg D, VC, Scale-Up, Offtake)
3. Tracked Public Grant Awards Ledger
4. SEC Form D Exempt Private Capital Offerings
5. Venture Capital & Equity Rounds
6. Commercial IP & Bayh-Dole Patent Inventions
7. Decarbonization Mandate & Strategic Innovation Scope
"""

import io
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

from app.engine.specialized_generators.base import (
    COLOR_BRAND_NAVY, COLOR_BRAND_CYAN, COLOR_BRAND_EMERALD,
    COLOR_BRAND_AMBER, COLOR_BRAND_SLATE, COLOR_BRAND_MUTED,
    COLOR_BRAND_BORDER, COLOR_BRAND_BORDER_LIGHT, COLOR_BRAND_BG_LIGHT,
    COLOR_BRAND_BG_EMERALD, COLOR_BRAND_BG_CYAN,
    format_currency, SOURCE_ATTRIBUTION
)


class RecipientDossierNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for total page count and professional running headers/footers."""
    def __init__(self, *args, recipient_name: str = "RECIPIENT DOSSIER", **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.recipient_name = recipient_name or "RECIPIENT DOSSIER"

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        
        # Outer archival neatline border
        self.setStrokeColor(COLOR_BRAND_NAVY)
        self.setLineWidth(1.2)
        self.rect(26, 26, 560, 740)

        # Inner subtle neatline
        self.setStrokeColor(COLOR_BRAND_BORDER_LIGHT)
        self.setLineWidth(0.5)
        self.rect(30, 30, 552, 732)

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            clean_name = self.recipient_name[:65]
            self.setFont("Helvetica-Bold", 6.5)
            self.setFillColor(COLOR_BRAND_CYAN)
            self.drawString(40, 748, f"ENERGY INNOVATION TERMINAL BY AIxENERGY // RECIPIENT DOSSIER: {clean_name.upper()}")

            self.setFont("Helvetica", 6.5)
            self.setFillColor(COLOR_BRAND_MUTED)
            self.drawRightString(572, 748, f"CAPITAL INTELLIGENCE ARCHIVE · terminal.aixenergy.io")

            self.setStrokeColor(COLOR_BRAND_BORDER_LIGHT)
            self.setLineWidth(0.5)
            self.line(40, 742, 572, 742)

        # Running Footer (all pages)
        self.setStrokeColor(COLOR_BRAND_BORDER_LIGHT)
        self.setLineWidth(0.5)
        self.line(40, 44, 572, 44)

        self.setFont("Helvetica", 6.5)
        self.setFillColor(COLOR_BRAND_MUTED)
        self.drawString(40, 34, "Energy Innovation Terminal by AIxEnergy · terminal.aixenergy.io · Multi-Stage Capital Continuum")

        self.setFont("Helvetica-Bold", 7)
        self.setFillColor(COLOR_BRAND_NAVY)
        self.drawRightString(572, 34, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def generate_recipient_dossier_pdf(dossier_data: Dict[str, Any]) -> io.BytesIO:
    """Compiles a publication-grade PDF dossier for a clean energy recipient organization."""
    buffer = io.BytesIO()

    recipient = dossier_data.get("recipient") or {}
    continuum = dossier_data.get("continuum") or {}
    aggregates = continuum.get("financial_aggregates") or {}
    grants = continuum.get("grants") or []
    sec_filings = continuum.get("sec_form_d_filings") or []
    vc_rounds = continuum.get("vc_rounds") or []
    patents = continuum.get("patents") or []
    scaleups = continuum.get("scaleup_allocations") or []
    procurements = continuum.get("procurement_contracts") or []

    rec_name = recipient.get("name") or "Innovator Entity"

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=38,
        rightMargin=38,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    style_super_title = ParagraphStyle(
        'SuperTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=9,
        textColor=COLOR_BRAND_CYAN, textTransform='uppercase', spaceAfter=2
    )
    style_h1 = ParagraphStyle(
        'MainH1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        textColor=COLOR_BRAND_NAVY, spaceAfter=4
    )
    style_h2 = ParagraphStyle(
        'SectionH2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14,
        textColor=COLOR_BRAND_NAVY, spaceBefore=12, spaceAfter=6,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'BodyDark', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11,
        textColor=COLOR_BRAND_SLATE
    )
    style_body_bold = ParagraphStyle(
        'BodyBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=11,
        textColor=COLOR_BRAND_NAVY
    )
    style_mono = ParagraphStyle(
        'MonoTable', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=10,
        textColor=COLOR_BRAND_NAVY
    )
    style_mono_green = ParagraphStyle(
        'MonoGreen', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=10,
        textColor=COLOR_BRAND_EMERALD
    )
    style_table_cell = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.5, leading=10,
        textColor=COLOR_BRAND_SLATE
    )
    style_table_header = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=10,
        textColor=colors.white
    )

    story: List[Any] = []

    # ── HEADER MASTHEAD ──
    story.append(Paragraph("ENERGY INNOVATION TERMINAL // RECIPIENT FUNDING DOSSIER", style_super_title))
    story.append(Paragraph(rec_name, style_h1))

    # Meta Tags Banner
    tech_str = recipient.get("primary_technology") or "Energy Innovation"
    city = recipient.get("headquarters_city") or ""
    state = recipient.get("headquarters_state") or ""
    loc_str = f"{city}, {state}".strip(", ") or "United States"
    stage_str = recipient.get("commercialization_stage") or "Commercial Deployment"
    emp_str = recipient.get("employee_range") or "50–200"
    web_str = recipient.get("website_url") or "https://terminal.aixenergy.io"

    meta_text = (
        f"<b>Technology Domain:</b> {tech_str} &nbsp;|&nbsp; "
        f"<b>Headquarters:</b> {loc_str} &nbsp;|&nbsp; "
        f"<b>Maturity Stage:</b> {stage_str} &nbsp;|&nbsp; "
        f"<b>Employees:</b> {emp_str} &nbsp;|&nbsp; "
        f"<b>Website:</b> {web_str}"
    )
    story.append(Paragraph(meta_text, style_body))
    story.append(Spacer(1, 8))

    # ── CAPITAL CONTINUUM TOTALS EXECUTIVE SCORECARD ──
    grand_total = aggregates.get("grand_total_capital_usd") or recipient.get("total_funding_received") or 0
    total_grants = aggregates.get("total_public_grants_usd") or recipient.get("total_funding_received") or 0
    total_sec_d = aggregates.get("total_sec_form_d_usd") or 0
    total_vc = aggregates.get("total_vc_investments_usd") or 0
    total_scaleup = aggregates.get("total_scaleup_allocations_usd") or 0
    total_proc = aggregates.get("total_procurement_offtake_usd") or 0

    scorecard_data = [
        [
            Paragraph("<b>GRAND TOTAL CAPITAL</b>", style_table_header),
            Paragraph("<b>1. PUBLIC GRANTS</b>", style_table_header),
            Paragraph("<b>2. SEC FORM D</b>", style_table_header),
            Paragraph("<b>3. VC EQUITY</b>", style_table_header),
            Paragraph("<b>4. SCALE-UP (LPO)</b>", style_table_header),
        ],
        [
            Paragraph(f"<font size=11 color='#059669'><b>{format_currency(grand_total)}</b></font>", style_mono_green),
            Paragraph(f"<b>{format_currency(total_grants)}</b><br/><font size=6 color='#64748B'>{len(grants)} Awards</font>", style_table_cell),
            Paragraph(f"<b>{format_currency(total_sec_d)}</b><br/><font size=6 color='#64748B'>{len(sec_filings)} Filings</font>", style_table_cell),
            Paragraph(f"<b>{format_currency(total_vc)}</b><br/><font size=6 color='#64748B'>{len(vc_rounds)} Rounds</font>", style_table_cell),
            Paragraph(f"<b>{format_currency(total_scaleup)}</b><br/><font size=6 color='#64748B'>{len(scaleups)} Facilities</font>", style_table_cell),
        ]
    ]

    t_scorecard = Table(scorecard_data, colWidths=[116, 105, 105, 105, 105])
    t_scorecard.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_NAVY),
        ('BACKGROUND', (0, 1), (-1, 1), COLOR_BRAND_BG_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER),
        ('PADDING', (0, 0), (-1, -1), 4.5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_scorecard)
    story.append(Spacer(1, 10))

    # Executive Overview
    desc = recipient.get("description") or f"{rec_name} is an advanced energy innovation enterprise developing commercial solutions in {tech_str}."
    story.append(Paragraph(f"<b>Executive Summary &amp; Scope:</b> {desc}", style_body))
    story.append(Spacer(1, 8))

    # ── SECTION 1: PUBLIC GRANTS & DEMONSTRATION AWARDS ──
    story.append(Paragraph("1. Tracked Public Grant Awards & Solicitations Ledger", style_h2))
    if grants:
        grant_rows = [
            [
                Paragraph("<b>Award ID / Solicitation</b>", style_table_header),
                Paragraph("<b>Agency</b>", style_table_header),
                Paragraph("<b>Obligated Capital</b>", style_table_header),
                Paragraph("<b>Award Date</b>", style_table_header),
                Paragraph("<b>Project Title & Scope</b>", style_table_header),
            ]
        ]
        for g in grants[:10]:
            grant_rows.append([
                Paragraph(str(g.get("solicitation_number") or g.get("id") or "GRANT"), style_mono),
                Paragraph(str(g.get("agency") or "DOE"), style_table_cell),
                Paragraph(format_currency(g.get("award_amount") or 0), style_mono_green),
                Paragraph(str(g.get("award_date") or "—"), style_table_cell),
                Paragraph(str(g.get("project_title") or "Commercial Clean Energy Project")[:65], style_table_cell),
            ])

        t_grants = Table(grant_rows, colWidths=[100, 70, 75, 65, 226])
        t_grants.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_NAVY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BRAND_BG_LIGHT]),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
            ('PADDING', (0, 0), (-1, -1), 3.5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_grants)
    else:
        story.append(Paragraph("<i>No public grants ledger items recorded in current active vintage.</i>", style_body))

    story.append(Spacer(1, 10))

    # ── SECTION 2: SEC FORM D & VENTURE CAPITAL LEDGER ──
    story.append(Paragraph("2. Private Capital Continuum (SEC Form D & Venture Rounds)", style_h2))
    
    col_w = 265
    left_table_data = [
        [Paragraph("<b>SEC Form D Exempt Offerings</b>", style_table_header), Paragraph("<b>Amount Sold</b>", style_table_header)]
    ]
    if sec_filings:
        for s in sec_filings[:5]:
            left_table_data.append([
                Paragraph(f"CIK #{s.get('cik')} · {s.get('filing_date') or 'N/A'}<br/><font size=6 color='#64748B'>{s.get('num_investors') or 1} Investors · Rule 506</font>", style_table_cell),
                Paragraph(format_currency(s.get('amount_sold_usd') or 0), style_mono_green)
            ])
    else:
        left_table_data.append([Paragraph("<i>No SEC Form D filings indexed.</i>", style_table_cell), Paragraph("—", style_table_cell)])

    t_sec = Table(left_table_data, colWidths=[180, 85])
    t_sec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_SLATE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BRAND_BG_LIGHT]),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 3),
    ]))

    right_table_data = [
        [Paragraph("<b>VC Round & Lead Investor</b>", style_table_header), Paragraph("<b>Round Amount</b>", style_table_header)]
    ]
    if vc_rounds:
        for v in vc_rounds[:5]:
            lead = v.get("lead_investor") or "Syndicate"
            right_table_data.append([
                Paragraph(f"{v.get('round_type') or 'Equity'} · {v.get('round_date') or 'N/A'}<br/><font size=6 color='#64748B'>Lead: {lead}</font>", style_table_cell),
                Paragraph(format_currency(v.get('amount_usd') or 0), style_mono_green)
            ])
    else:
        right_table_data.append([Paragraph("<i>No venture rounds indexed.</i>", style_table_cell), Paragraph("—", style_table_cell)])

    t_vc = Table(right_table_data, colWidths=[180, 85])
    t_vc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_SLATE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BRAND_BG_LIGHT]),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 3),
    ]))

    split_table = Table([[t_sec, t_vc]], colWidths=[268, 268])
    split_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(split_table)
    story.append(Spacer(1, 10))

    # ── SECTION 3: COMMERCIAL IP & PATENTS ──
    story.append(Paragraph("3. Commercial IP, Bayh-Dole Inventions & Patents", style_h2))
    if patents:
        pat_rows = [
            [
                Paragraph("<b>Patent Number</b>", style_table_header),
                Paragraph("<b>Grant Date</b>", style_table_header),
                Paragraph("<b>Bayh-Dole Gov Interest</b>", style_table_header),
                Paragraph("<b>Patent Title & Technology Scope</b>", style_table_header),
            ]
        ]
        for p in patents[:6]:
            bd = p.get("bayh_dole_citation") or "Commercial Proprietary"
            pat_rows.append([
                Paragraph(f"US #{p.get('patent_number')}", style_mono),
                Paragraph(str(p.get("grant_date") or "—"), style_table_cell),
                Paragraph(str(bd)[:30], style_table_cell),
                Paragraph(str(p.get("title") or "Energy Innovation System")[:70], style_table_cell),
            ])
        t_pat = Table(pat_rows, colWidths=[85, 65, 120, 266])
        t_pat.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_NAVY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BRAND_BG_LIGHT]),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
            ('PADDING', (0, 0), (-1, -1), 3),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_pat)
    else:
        story.append(Paragraph("<i>No patent filings recorded in current active ledger.</i>", style_body))

    story.append(Spacer(1, 10))

    # ── SECTION 4: CLIMATE IMPACT & STRATEGIC INNOVATION FOCUS ──
    impact = recipient.get("climate_impact_focus")
    innov = recipient.get("key_innovations")
    if impact or innov:
        story.append(Paragraph("4. Decarbonization Mandate & Core Technology Architecture", style_h2))
        if impact:
            story.append(Paragraph(f"<b>Climate &amp; Environmental Mandate:</b> {impact}", style_body))
            story.append(Spacer(1, 4))
        if innov:
            story.append(Paragraph(f"<b>Key Engineering Innovations:</b> {innov}", style_body))

    # Build Document with two-pass numbered canvas
    doc.build(story, canvasmaker=lambda *args, **kwargs: RecipientDossierNumberedCanvas(*args, recipient_name=rec_name, **kwargs))
    buffer.seek(0)
    return buffer
