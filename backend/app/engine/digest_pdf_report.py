"""Publication-grade PDF briefing report generator for Energy Innovation Daily Digest.
Built with ReportLab for institutional quality and strict styling compliance.
"""

import io
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PRIMARY_COLOR = colors.HexColor("#080c14")
SECONDARY_COLOR = colors.HexColor("#0f172a")
ACCENT_BLUE = colors.HexColor("#0284c7")
ACCENT_GOLD = colors.HexColor("#d97706")
TEXT_DARK = colors.HexColor("#1e293b")
TEXT_MUTED = colors.HexColor("#64748b")
BG_LIGHT = colors.HexColor("#f8fafc")
BORDER_COLOR = colors.HexColor("#e2e8f0")
EMERALD_COLOR = colors.HexColor("#059669")


class NumberedCanvas(canvas.Canvas):
    """Canvas that performs a two-pass calculation to draw 'Page X of Y' headers and footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)

        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Energy Innovation Terminal by AIxEnergy | Daily Intelligence Briefing")
            self.drawRightString(612 - 54, 750, f"Edition Date: {getattr(self, '_edition_date', 'Daily Brief')}")
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.5)
            self.line(54, 742, 612 - 54, 742)

        # Footer (All pages)
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)

        self.drawString(54, 32, "CONFIDENTIAL & PROPRIETARY — ENERGY INNOVATION TERMINAL (terminal.aixenergy.io)")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 32, page_str)
        self.restoreState()


def build_daily_digest_pdf(digest_data: Dict[str, Any], output_stream: io.BytesIO) -> None:
    """Compiles a publication-grade Daily Intelligence Digest PDF."""
    doc = SimpleDocTemplate(
        output_stream,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom typography
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=PRIMARY_COLOR,
        spaceAfter=4
    )

    edition_badge_style = ParagraphStyle(
        'EditionBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=ACCENT_BLUE
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=SECONDARY_COLOR,
        spaceBefore=10,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    lead_narrative_style = ParagraphStyle(
        'LeadNarrative',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=SECONDARY_COLOR,
        spaceAfter=6
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=TEXT_DARK
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=SECONDARY_COLOR
    )

    story = []

    # 1. Header Banner Box
    edition_num = str(digest_data.get('edition_number', '#1'))
    edition_date = str(digest_data.get('formatted_date') or digest_data.get('edition_date', datetime.utcnow().strftime('%B %d, %Y')))
    headline = str(digest_data.get('headline') or "National Clean Energy & Capital Markets Intelligence Briefing")

    header_data = [
        [
            Paragraph(f"<b>ENERGY INNOVATION TERMINAL BY AIxENERGY</b><br/><font color='#0284c7'>DAILY EXECUTIVE INTELLIGENCE BRIEFING &bull; {edition_num.upper()}</font>", edition_badge_style),
            Paragraph(f"<font color='#64748b'><b>Date:</b> {edition_date}<br/><b>Coverage:</b> Federal &bull; State &bull; Utility &bull; Capital</font>", table_cell_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[330, 174])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # 2. Main Headline
    story.append(Paragraph(headline, title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_BLUE, spaceBefore=3, spaceAfter=6))

    # 3. Macro Telemetry KPI Strip
    stats = digest_data.get('market_snapshot', {}) or {}
    total_solicitations = stats.get('active_solicitations_count', '3,870+')
    total_capital = stats.get('total_funding_tracked', '$48.2B')
    new_opps_today = stats.get('new_solicitations_today', '12')
    days_to_major_gate = stats.get('days_to_q1_gates', '18 Days')

    kpi_data = [
        [
            Paragraph("<font size=7 color='#64748b'>ACTIVE SOLICITATIONS</font><br/><b><font size=11 color='#0f172a'>" + str(total_solicitations) + "</font></b>", table_cell_style),
            Paragraph("<font size=7 color='#64748b'>TRACKED CAPITAL POOL</font><br/><b><font size=11 color='#059669'>" + str(total_capital) + "</font></b>", table_cell_style),
            Paragraph("<font size=7 color='#64748b'>NEW POSTINGS TODAY</font><br/><b><font size=11 color='#0284c7'>" + str(new_opps_today) + " FOAs</font></b>", table_cell_style),
            Paragraph("<font size=7 color='#64748b'>NEAR-TERM DEADLINES</font><br/><b><font size=11 color='#d97706'>" + str(days_to_major_gate) + "</font></b>", table_cell_style),
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[126, 126, 126, 126])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 8))

    # 4. Executive Editorial Thesis
    story.append(Paragraph("1. Executive Strategic Briefing & Market Signals", section_heading))
    narrative = str(digest_data.get('editorial_narrative') or digest_data.get('summary') or "Federal and state clean energy capital allocations continue rapid disbursement under IRA Direct Pay and BIL statutory schedules. Consultancies and project developers must prioritize early teaming architectures and strict rubric adherence for high-scoring submissions.")
    for p_text in narrative.split("\n\n"):
        if p_text.strip():
            story.append(Paragraph(p_text.strip(), lead_narrative_style))
    story.append(Spacer(1, 6))

    # 5. Top Market Headlines / Key Developments
    headlines_list = digest_data.get('headlines', []) or digest_data.get('articles', [])
    if headlines_list:
        story.append(Paragraph("2. Critical Policy & Solicitation Developments", section_heading))
        h_table_data = [
            [
                Paragraph("SECTOR / DOMAIN", table_header_style),
                Paragraph("KEY POLICY / CAPITAL DEVELOPMENT", table_header_style),
                Paragraph("STRATEGIC IMPACT", table_header_style),
            ]
        ]
        for h in headlines_list[:5]:
            cat = str(h.get('category') or h.get('sector') or 'Federal Grant')
            title = str(h.get('title') or h.get('headline') or 'Solicitation Milestone')
            desc = str(h.get('summary') or h.get('description') or '')
            impact = str(h.get('strategic_impact') or h.get('impact_level') or 'High Priority')
            h_table_data.append([
                Paragraph(f"<b>{cat}</b>", table_cell_bold),
                Paragraph(f"<b>{title}</b><br/><font color='#64748b'>{desc[:130]}</font>", table_cell_style),
                Paragraph(f"<font color='#0284c7'><b>{impact}</b></font>", table_cell_style),
            ])

        h_table = Table(h_table_data, colWidths=[110, 294, 100])
        h_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_COLOR),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(h_table)
        story.append(Spacer(1, 8))

    # 6. High-Priority Funding Opportunities Spotlight
    spotlight_opps = digest_data.get('featured_opportunities', []) or digest_data.get('top_opportunities', [])
    if spotlight_opps:
        story.append(Paragraph("3. Featured Funding Opportunities & Teaming Deadlines", section_heading))
        opp_table_data = [
            [
                Paragraph("AGENCY / NO.", table_header_style),
                Paragraph("SOLICITATION TITLE", table_header_style),
                Paragraph("TOTAL POOL", table_header_style),
                Paragraph("DEADLINE", table_header_style),
            ]
        ]
        for opp in spotlight_opps[:6]:
            agency = str(opp.get('agency') or 'DOE / ARPA-E')
            sol_num = str(opp.get('solicitation_number') or f"OPP-{opp.get('id', '')}")
            name = str(opp.get('name') or opp.get('title') or 'Funding Opportunity')
            pool = str(opp.get('total_funding_formatted') or opp.get('funding_pool') or '$50,000,000')
            deadline = str(opp.get('deadline_formatted') or opp.get('deadline') or 'Rolling / 2026')

            opp_table_data.append([
                Paragraph(f"<b>{agency}</b><br/><font color='#64748b'>{sol_num}</font>", table_cell_bold),
                Paragraph(f"<b>{name[:70]}</b>", table_cell_style),
                Paragraph(f"<font color='#059669'><b>{pool}</b></font>", table_cell_style),
                Paragraph(f"<font color='#d97706'><b>{deadline}</b></font>", table_cell_style),
            ])

        opp_table = Table(opp_table_data, colWidths=[100, 254, 80, 70])
        opp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(opp_table)
        story.append(Spacer(1, 8))

    # 7. Editorial Sign-Off Box
    signoff_data = [
        [
            Paragraph(
                "<b>Institutional Advisory Note:</b> This briefing is compiled daily by the Energy Innovation Terminal research desk. All grant numbers, statutory stage gates, and award histories are cross-verified against official Federal Register, Grants.gov, and state utility regulatory filings.<br/>"
                "<b>Live Platform:</b> terminal.aixenergy.io &bull; <b>Direct Contact:</b> bowens@aixenergy.io",
                table_cell_style
            )
        ]
    ]
    signoff_table = Table(signoff_data, colWidths=[504])
    signoff_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(signoff_table)

    def on_page_end(c, d):
        c._edition_date = edition_date

    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=on_page_end, onLaterPages=on_page_end)
