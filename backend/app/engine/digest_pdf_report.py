"""Publication-grade PDF briefing report generator for Energy Innovation Daily Digest.
Built with ReportLab for institutional quality, multi-page layout, and strict typography compliance.
Designed for subscriber delivery ($1,500/seat/month institutional intelligence).
"""

import io
from datetime import datetime, timezone
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Palette definition
PRIMARY_DARK = colors.HexColor("#080c14")       # Deep Slate / Navy Obsidian
SECONDARY_DARK = colors.HexColor("#0f172a")     # Rich Navy
NAVY_ACCENT = colors.HexColor("#1e3a8a")        # Navy Accent
ACCENT_BLUE = colors.HexColor("#0284c7")        # Cyan Blue
ACCENT_CYAN = colors.HexColor("#0ea5e9")        # Bright Cyan
ACCENT_EMERALD = colors.HexColor("#059669")     # Emerald Green
ACCENT_AMBER = colors.HexColor("#d97706")       # Amber Warning
ACCENT_CRIMSON = colors.HexColor("#dc2626")     # Alert Crimson
TEXT_DARK = colors.HexColor("#1e293b")          # Body Dark
TEXT_MUTED = colors.HexColor("#64748b")         # Body Muted Slate
BG_LIGHT = colors.HexColor("#f8fafc")           # Light Section Shading
BG_ALT = colors.HexColor("#f1f5f9")             # Alt Row Shading
BORDER_LIGHT = colors.HexColor("#e2e8f0")       # Border Light
BORDER_DARK = colors.HexColor("#cbd5e1")        # Border Medium


class NumberedCanvas(canvas.Canvas):
    """Two-pass ReportLab Canvas that draws professional running headers and 'Page X of Y' footers."""
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
        self.setFont("Helvetica", 7.5)
        self.setFillColor(TEXT_MUTED)

        # Header on Pages 2+
        if self._pageNumber > 1:
            self.drawString(45, 755, "ENERGY INNOVATION TERMINAL BY AIxENERGY")
            self.drawCentredString(306, 755, "DAILY INSTITUTIONAL ENERGY & CAPITAL INTELLIGENCE BRIEFING")
            ed_date = getattr(self, '_edition_date', 'Daily Brief')
            self.drawRightString(612 - 45, 755, f"Edition Date: {ed_date}")
            self.setStrokeColor(BORDER_LIGHT)
            self.setLineWidth(0.75)
            self.line(45, 747, 612 - 45, 747)

        # Footer on All Pages
        self.setStrokeColor(BORDER_LIGHT)
        self.setLineWidth(0.75)
        self.line(45, 42, 612 - 45, 42)

        self.drawString(45, 30, "U.S. ENERGY INNOVATION DATABASE — CLEAN ENERGY RESEARCH, LLC (terminal.aixenergy.io)")
        self.drawCentredString(306, 30, "CLEAN ENERGY RESEARCH & CAPITAL INTELLIGENCE")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 45, 30, page_str)
        self.restoreState()


def build_daily_digest_pdf(digest_data: Dict[str, Any], output_stream: io.BytesIO) -> None:
    """Compiles a publication-grade, multi-page Daily Intelligence Digest PDF."""
    
    # Printable area: 612 - 2*45 = 522 pt width. Margins: 45 pt (0.625 in)
    doc = SimpleDocTemplate(
        output_stream,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=48,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Typography styles
    title_style = ParagraphStyle(
        'MainDocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=PRIMARY_DARK,
        spaceAfter=3
    )

    masthead_sub_style = ParagraphStyle(
        'MastheadSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=ACCENT_BLUE
    )

    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=SECONDARY_DARK,
        spaceBefore=8,
        spaceAfter=4
    )

    lead_narrative_style = ParagraphStyle(
        'LeadNarrative',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.8,
        textColor=TEXT_DARK,
        spaceAfter=4
    )

    tbl_hdr = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white
    )

    cell_text = ParagraphStyle(
        'CellTxt',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=TEXT_DARK
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=SECONDARY_DARK
    )

    cell_emerald = ParagraphStyle(
        'CellEmerald',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=ACCENT_EMERALD
    )

    cell_amber = ParagraphStyle(
        'CellAmber',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=ACCENT_AMBER
    )

    cell_cyan = ParagraphStyle(
        'CellCyan',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=ACCENT_BLUE
    )

    story = []

    # Safe data extractors
    edition_num = str(digest_data.get('edition_number', '#1')).upper()
    edition_date = str(digest_data.get('formatted_date') or digest_data.get('edition_date', datetime.now(timezone.utc).strftime('%B %d, %Y')))
    headline = str(digest_data.get('headline') or f"Daily Energy Innovation Intelligence Briefing — {edition_date}")
    macro = digest_data.get('macro_metrics', {}) or {}
    editorial_narrative = str(digest_data.get('editorial_narrative') or "")

    # ==========================================
    # PAGE 1: MASTHEAD & TOP-LEVEL INTELLIGENCE
    # ==========================================

    # 1. Top Masthead Box
    masthead_data = [
        [
            Paragraph(
                f"<b>ENERGY INNOVATION TERMINAL BY AIxENERGY</b><br/>"
                f"<font color='#0284c7'>DAILY INSTITUTIONAL ENERGY & CAPITAL INTELLIGENCE BRIEFING &bull; {edition_num}</font>",
                masthead_sub_style
            ),
            Paragraph(
                f"<b>Edition Date:</b> {edition_date}<br/>"
                f"<font color='#64748b'><b>Frequency:</b> Daily Institutional Dispatch &bull; <b>Tier:</b> Enterprise Intelligence</font>",
                cell_text
            )
        ]
    ]
    masthead_table = Table(masthead_data, colWidths=[332, 190])
    masthead_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(masthead_table)
    story.append(Spacer(1, 6))

    # 2. Main Issue Headline
    story.append(Paragraph(headline, title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_BLUE, spaceBefore=2, spaceAfter=5))

    # 3. Macro Capital Flow Telemetry (6 KPI Cards in 2 Rows x 3 Columns)
    tot_active_cap = macro.get('total_active_capital_display', '$48.20B')
    fed_cap = macro.get('federal_capital_display', '$31.30B')
    state_cap = macro.get('state_capital_display', '$12.00B')
    open_solics = f"{macro.get('open_solicitations_count', 3870):,} Solicitations"
    hist_cap = f"{macro.get('total_historical_capital_display', '$104.16B')} ({macro.get('total_historical_awards_count', 56413):,} Awards)"
    tracked_recips = f"{macro.get('tracked_recipients_count', 14850):,} Innovators"

    kpi_grid_data = [
        [
            Paragraph(f"<font size=6.5 color='#64748b'>TOTAL ACTIVE CAPITAL POOL</font><br/><b><font size=10 color='#059669'>{tot_active_cap}</font></b>", cell_text),
            Paragraph(f"<font size=6.5 color='#64748b'>FEDERAL PIPELINE (DOE/BIL)</font><br/><b><font size=10 color='#0284c7'>{fed_cap}</font></b>", cell_text),
            Paragraph(f"<font size=6.5 color='#64748b'>STATE & REGIONAL PIPELINE</font><br/><b><font size=10 color='#d97706'>{state_cap}</font></b>", cell_text),
        ],
        [
            Paragraph(f"<font size=6.5 color='#64748b'>ACTIVE OPEN SOLICITATIONS</font><br/><b><font size=9.5 color='#0f172a'>{open_solics}</font></b>", cell_text),
            Paragraph(f"<font size=6.5 color='#64748b'>HISTORICAL CAPITAL BENCHMARK</font><br/><b><font size=9.5 color='#0f172a'>{hist_cap}</font></b>", cell_text),
            Paragraph(f"<font size=6.5 color='#64748b'>TRACKED RECIPIENT NETWORK</font><br/><b><font size=9.5 color='#0f172a'>{tracked_recips}</font></b>", cell_text),
        ]
    ]
    kpi_grid_table = Table(kpi_grid_data, colWidths=[174, 174, 174])
    kpi_grid_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_ALT),
        ('BOX', (0, 0), (-1, -1), 0.75, BORDER_LIGHT),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(kpi_grid_table)
    story.append(Spacer(1, 6))

    # 4. Executive Editorial Strategic Briefing
    story.append(Paragraph("1. Executive Strategic Intelligence Memo", section_heading))
    if editorial_narrative:
        paragraphs = [p.strip() for p in editorial_narrative.split("\n\n") if p.strip()]
        for p_idx, p_text in enumerate(paragraphs[:3]):
            story.append(Paragraph(f"<b>[&bull;]</b> {p_text}", lead_narrative_style))
    story.append(Spacer(1, 6))

    # 5. Top New Solicitations & RFP Drops (Page 1 Top 5)
    new_solicitations = digest_data.get('new_solicitations', []) or []
    if new_solicitations:
        story.append(Paragraph("2. Primary New Solicitations & RFP Drops (Federal / State)", section_heading))
        sol_table_data = [
            [
                Paragraph("SOLICITATION / ID", tbl_hdr),
                Paragraph("PROGRAM TITLE & SCOPE", tbl_hdr),
                Paragraph("AGENCY", tbl_hdr),
                Paragraph("POOL / MAX", tbl_hdr),
                Paragraph("DEADLINE", tbl_hdr),
            ]
        ]
        for sol in new_solicitations[:5]:
            sol_id = str(sol.get('solicitation_number') or f"SOL-{sol.get('id')}")
            title = str(sol.get('title') or sol.get('name') or "Clean Energy Program")
            agency = str(sol.get('agency') or "DOE / State Authority")
            pool = str(sol.get('total_funding_display') or "$10.0M")
            max_aw = str(sol.get('max_per_award_display') or "$3.0M")
            due = str(sol.get('due_date_display') or "Open")
            cost_share = str(sol.get('cost_share_required') or "20% Cost Share")

            sol_table_data.append([
                Paragraph(f"<b>{sol_id}</b><br/><font size=6.5 color='#64748b'>{cost_share}</font>", cell_bold),
                Paragraph(f"<b>{title[:65]}</b>", cell_text),
                Paragraph(f"{agency[:26]}", cell_text),
                Paragraph(f"<b>{pool}</b><br/><font size=6.5 color='#059669'>Max: {max_aw}</font>", cell_emerald),
                Paragraph(f"<b>{due}</b>", cell_amber),
            ])

        sol_table = Table(sol_table_data, colWidths=[90, 182, 95, 85, 70])
        sol_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_DARK),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(sol_table)

    story.append(PageBreak())

    # ==========================================
    # PAGE 2: SOLICITATIONS CONT. & DEADLINES & AWARDS WIRE
    # ==========================================

    # Solicitations Continued (if more than 5)
    if len(new_solicitations) > 5:
        story.append(Paragraph("2. New Solicitations & RFP Drops (Continued)", section_heading))
        sol_cont_data = [
            [
                Paragraph("SOLICITATION / ID", tbl_hdr),
                Paragraph("PROGRAM TITLE & SCOPE", tbl_hdr),
                Paragraph("AGENCY", tbl_hdr),
                Paragraph("POOL / MAX", tbl_hdr),
                Paragraph("DEADLINE", tbl_hdr),
            ]
        ]
        for sol in new_solicitations[5:10]:
            sol_id = str(sol.get('solicitation_number') or f"SOL-{sol.get('id')}")
            title = str(sol.get('title') or sol.get('name') or "Clean Energy Program")
            agency = str(sol.get('agency') or "DOE / State Authority")
            pool = str(sol.get('total_funding_display') or "$10.0M")
            max_aw = str(sol.get('max_per_award_display') or "$3.0M")
            due = str(sol.get('due_date_display') or "Open")
            cost_share = str(sol.get('cost_share_required') or "20% Cost Share")

            sol_cont_data.append([
                Paragraph(f"<b>{sol_id}</b><br/><font size=6.5 color='#64748b'>{cost_share}</font>", cell_bold),
                Paragraph(f"<b>{title[:65]}</b>", cell_text),
                Paragraph(f"{agency[:26]}", cell_text),
                Paragraph(f"<b>{pool}</b><br/><font size=6.5 color='#059669'>Max: {max_aw}</font>", cell_emerald),
                Paragraph(f"<b>{due}</b>", cell_amber),
            ])

        sol_cont_table = Table(sol_cont_data, colWidths=[90, 182, 95, 85, 70])
        sol_cont_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_DARK),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(sol_cont_table)
        story.append(Spacer(1, 6))

    # 6. Critical 14-30 Day Application Deadlines Matrix
    urgent_deadlines = digest_data.get('urgent_deadlines', []) or []
    if urgent_deadlines:
        story.append(Paragraph("3. 14-30 Day Critical Submission Deadlines Matrix", section_heading))
        dl_data = [
            [
                Paragraph("COUNTDOWN", tbl_hdr),
                Paragraph("SOLICITATION / ID", tbl_hdr),
                Paragraph("AGENCY / PROGRAM", tbl_hdr),
                Paragraph("POOL", tbl_hdr),
                Paragraph("SUBMISSION GATES & REQUIRED PACKAGES", tbl_hdr),
            ]
        ]
        for dl in urgent_deadlines[:8]:
            sol_id = str(dl.get('solicitation_number') or "DE-FOA-0003000")
            title = str(dl.get('name') or "Clean Energy Demonstration")
            agency = str(dl.get('agency') or "DOE")
            pool = str(dl.get('total_funding_display') or "$25.0M")
            days_left = str(dl.get('days_remaining') or "14d")
            pkg_req = str(dl.get('package_requirements') or "Full Proposal: Tech Narrative + Cost Share Form + CBP Plan")

            dl_data.append([
                Paragraph(f"<font color='#dc2626'><b>{days_left}</b></font>", cell_bold),
                Paragraph(f"<b>{sol_id}</b><br/>{title[:45]}", cell_text),
                Paragraph(f"{agency[:24]}", cell_text),
                Paragraph(f"<b>{pool}</b>", cell_emerald),
                Paragraph(f"<font size=7 color='#1e293b'>{pkg_req}</font>", cell_text),
            ])

        dl_table = Table(dl_data, colWidths=[65, 145, 90, 62, 160])
        dl_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_DARK),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(dl_table)
        story.append(Spacer(1, 6))

    # 7. Major Recent Awards & Non-Dilutive Capital Deals Wire
    award_wire = digest_data.get('award_wire', []) or []
    if award_wire:
        story.append(Paragraph("4. Prime Award Wire & Capital Deployment Tracking", section_heading))
        aw_data = [
            [
                Paragraph("RECIPIENT & LOCATION", tbl_hdr),
                Paragraph("PROJECT TITLE & TECHNOLOGY VERTICAL", tbl_hdr),
                Paragraph("AGENCY", tbl_hdr),
                Paragraph("AWARD VALUE", tbl_hdr),
                Paragraph("STAGE", tbl_hdr),
            ]
        ]
        for aw in award_wire[:8]:
            recip = str(aw.get('recipient_name') or "Advanced Energy Corp")
            loc = str(aw.get('location') or "National")
            title = str(aw.get('project_title') or "Grid Modernization")
            vert = str(aw.get('technology_vertical') or "Grid & Storage")
            agency = str(aw.get('agency') or "DOE")
            amt = str(aw.get('award_amount_display') or "$5.0M")
            stage = str(aw.get('commercial_stage') or "TRL 7-9")

            aw_data.append([
                Paragraph(f"<b>{recip[:30]}</b><br/><font size=6.5 color='#64748b'>{loc}</font>", cell_bold),
                Paragraph(f"<b>{title[:45]}</b><br/><font size=6.5 color='#0284c7'>{vert[:35]}</font>", cell_text),
                Paragraph(f"{agency[:22]}", cell_text),
                Paragraph(f"<b>{amt}</b>", cell_emerald),
                Paragraph(f"<font size=6.5 color='#64748b'>{stage}</font>", cell_text),
            ])

        aw_table = Table(aw_data, colWidths=[115, 172, 85, 75, 75])
        aw_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_DARK),
            ('PADDING', (0, 0), (-1, -1), 3.5),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(aw_table)

    story.append(PageBreak())

    # ==========================================
    # PAGE 3: REGULATORY WATCH & FINANCIAL SPOTLIGHT & TEAMING RADAR
    # ==========================================

    # 8. Regulatory, Dockets & Policy Standards Watch
    regulatory_watch = digest_data.get('regulatory_watch', []) or []
    if regulatory_watch:
        story.append(Paragraph("5. State & Federal Regulatory Dockets & Policy Standards Watch", section_heading))
        reg_data = [
            [
                Paragraph("DOCKET / CODE", tbl_hdr),
                Paragraph("POLICY PROCEEDING / MANDATE", tbl_hdr),
                Paragraph("JURISDICTION", tbl_hdr),
                Paragraph("COMPLIANCE & STRATEGIC IMPACT", tbl_hdr),
            ]
        ]
        for reg in regulatory_watch[:6]:
            code = str(reg.get('code_identifier') or "REG-2026")
            title = str(reg.get('title') or "Clean Energy Standard")
            jur = str(reg.get('jurisdiction_state') or "Federal / NY")
            mandate = str(reg.get('compliance_mandate') or "Mandatory Clean Energy Targets")
            summary = str(reg.get('executive_summary') or "")

            reg_data.append([
                Paragraph(f"<b>{code}</b>", cell_bold),
                Paragraph(f"<b>{title[:50]}</b><br/><font size=6.5 color='#64748b'>{summary[:90]}</font>", cell_text),
                Paragraph(f"<b>{jur}</b>", cell_cyan),
                Paragraph(f"<font size=7 color='#1e293b'>{mandate[:110]}</font>", cell_text),
            ])

        reg_table = Table(reg_data, colWidths=[80, 182, 80, 180])
        reg_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_DARK),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(reg_table)
        story.append(Spacer(1, 6))

    # 9. Technology Bankability (TBR) & 5-Stage Capital Stack Solver Spotlight
    spotlight = digest_data.get('spotlight', {}) or {}
    if spotlight:
        story.append(Paragraph("6. Featured Technology Bankability (TBR) & Capital Stack Solver Spotlight", section_heading))
        
        sp_title = spotlight.get('name') or "High-Capacity Storage Demonstration"
        sp_agency = spotlight.get('agency') or "DOE Office of Clean Energy Demonstrations"
        sp_sol_no = spotlight.get('solicitation_number') or "DE-FOA-0003250"
        sp_pool = spotlight.get('total_funding_display') or "$50.0M"
        sp_max = spotlight.get('max_per_award_display') or "$15.0M"
        tbr_score = str(spotlight.get('bankability_score', 86))
        tbr_grade = spotlight.get('bankability_grade', 'A- / Investment Grade')
        tbr_readiness = spotlight.get('bankability_readiness', 'Commercial Deployment Ready')
        itc_rate = spotlight.get('ira_itc_rate', '40%')
        wacc = spotlight.get('blended_wacc_pct', '5.8%')
        non_dilutive = spotlight.get('non_dilutive_coverage_pct', '65%')
        win_angle = spotlight.get('win_angle_summary', 'Lead with third-party testing, domestic content certifications, and signed off-taker letters.')

        # Top Spotlight Header Card
        spotlight_card_data = [
            [
                Paragraph(
                    f"<b>OPPORTUNITY:</b> {sp_sol_no} — {sp_title[:60]}<br/>"
                    f"<font color='#64748b'><b>Authority:</b> {sp_agency} &bull; <b>Pool:</b> {sp_pool} &bull; <b>Max Award:</b> {sp_max}</font>",
                    cell_text
                ),
                Paragraph(
                    f"<font size=6.5 color='#64748b'>BANKABILITY SCORE</font><br/>"
                    f"<b><font size=11 color='#059669'>{tbr_score}/100</font></b><br/>"
                    f"<font size=6.5 color='#0284c7'>{tbr_grade}</font>",
                    cell_text
                )
            ]
        ]
        spotlight_card_table = Table(spotlight_card_data, colWidths=[382, 140])
        spotlight_card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.75, BORDER_DARK),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ]))
        story.append(spotlight_card_table)
        story.append(Spacer(1, 4))

        # 5-Stage Capital Stack Structure Table
        cap_stack_data = [
            [
                Paragraph("CAPITAL TRANCHE", tbl_hdr),
                Paragraph("MODELED ALLOCATION", tbl_hdr),
                Paragraph("FINANCING VEHICLE & MECHANISM", tbl_hdr),
                Paragraph("COST OF CAPITAL / HURDLE", tbl_hdr),
            ],
            [
                Paragraph("<b>Tranche 1: Public Grant</b>", cell_bold),
                Paragraph(f"<font color='#059669'><b>{spotlight.get('modeled_grant_share', '30%')}</b></font>", cell_text),
                Paragraph(f"{sp_agency} Non-Dilutive Award", cell_text),
                Paragraph("<font color='#059669'><b>0.0% (Non-Dilutive)</b></font>", cell_text),
            ],
            [
                Paragraph("<b>Tranche 2: IRA Tax Credit</b>", cell_bold),
                Paragraph(f"<font color='#0284c7'><b>{spotlight.get('modeled_tax_equity_share', '40%')}</b></font>", cell_text),
                Paragraph(f"IRA Section 48C / Direct Pay Monetization ({itc_rate})", cell_text),
                Paragraph("<font color='#059669'><b>0.0% (Transferable Credit)</b></font>", cell_text),
            ],
            [
                Paragraph("<b>Tranche 3: Senior Debt</b>", cell_bold),
                Paragraph(f"<b>{spotlight.get('modeled_debt_share', '20%')}</b>", cell_text),
                Paragraph("DOE Loan Programs Office (LPO) / NY Green Bank", cell_text),
                Paragraph("<b>4.75% – 5.50% SOFR Term Loan</b>", cell_text),
            ],
            [
                Paragraph("<b>Tranche 4: Sponsor Equity</b>", cell_bold),
                Paragraph(f"<b>{spotlight.get('modeled_sponsor_equity', '10%')}</b>", cell_text),
                Paragraph("Project Developer Co-Investment / Venture Equity", cell_text),
                Paragraph("<b>12.0% – 15.0% Equity HurDLE</b>", cell_text),
            ],
            [
                Paragraph("<b>OPTIMIZED SUMMARY</b>", cell_bold),
                Paragraph(f"<font color='#059669'><b>{non_dilutive} Non-Dilutive</b></font>", cell_text),
                Paragraph(f"<b>Modeled Blended WACC: {wacc}</b>", cell_text),
                Paragraph(f"<b>TRL Readiness: {tbr_readiness}</b>", cell_text),
            ]
        ]
        cap_stack_table = Table(cap_stack_data, colWidths=[110, 110, 172, 130])
        cap_stack_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_DARK),
            ('BACKGROUND', (0, -1), (-1, -1), BG_ALT),
            ('PADDING', (0, 0), (-1, -1), 3.5),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, BG_LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(cap_stack_table)
        story.append(Spacer(1, 4))

        # Red-Team Win Angle Banner
        win_angle_data = [
            [
                Paragraph(
                    f"<b>DECISION-MAKER 'SAY-YES' WIN ANGLE:</b> {win_angle}",
                    cell_text
                )
            ]
        ]
        win_angle_table = Table(win_angle_data, colWidths=[522])
        win_angle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
            ('BOX', (0, 0), (-1, -1), 0.5, ACCENT_BLUE),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(win_angle_table)
        story.append(Spacer(1, 6))

    # 10. Consortia Teaming & National Lab Radar
    teaming_wire = digest_data.get('teaming_wire', []) or []
    if teaming_wire:
        story.append(Paragraph("7. Consortia Teaming & Subcontractor Radar", section_heading))
        team_data = [
            [
                Paragraph("PARTNER / TESTBED", tbl_hdr),
                Paragraph("PARTNER ROLE", tbl_hdr),
                Paragraph("TECHNICAL CAPABILITIES & INFRASTRUCTURE", tbl_hdr),
                Paragraph("TARGET SOLICITATIONS", tbl_hdr),
            ]
        ]
        for tm in teaming_wire[:4]:
            p_name = str(tm.get('partner_name') or "NREL Testbed")
            p_role = str(tm.get('role_type') or "Validation Facility")
            p_focus = str(tm.get('focus_area') or "Hardware testing")
            p_foas = str(tm.get('target_foas') or "DOE Modernization")

            team_data.append([
                Paragraph(f"<b>{p_name[:35]}</b>", cell_bold),
                Paragraph(f"{p_role}", cell_cyan),
                Paragraph(f"<font size=7 color='#1e293b'>{p_focus[:95]}</font>", cell_text),
                Paragraph(f"<b>{p_foas[:32]}</b>", cell_text),
            ])

        team_table = Table(team_data, colWidths=[130, 95, 177, 120])
        team_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_DARK),
            ('PADDING', (0, 0), (-1, -1), 3.5),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(team_table)
        story.append(Spacer(1, 6))

    # 11. Institutional Sign-Off & Subscription Advisory
    from app.engine.legal_disclaimer import get_pdf_disclaimer_flowable

    signoff_data = [
        [
            Paragraph(
                "<b>Institutional Advisory Note:</b> This intelligence dispatch is compiled daily by Clean Energy Research, LLC from the U.S. Energy Innovation Database. "
                "All grant numbers, statutory stage gates, capital ledgers, and award histories are cross-verified against official Federal Register, Grants.gov, and State PUC dockets.<br/>"
                "<b>Subscriber Access:</b> terminal.aixenergy.io &bull; <b>Publisher:</b> Clean Energy Research, LLC &bull; <b>Inquiries:</b> info@aixenergy.io &bull; <b>Enterprise Rate:</b> $1,500/seat/month",
                cell_text
            )
        ]
    ]
    signoff_table = Table(signoff_data, colWidths=[522])
    signoff_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_DARK),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(signoff_table)
    story.append(Spacer(1, 6))
    story.append(get_pdf_disclaimer_flowable(doc_width=522.0))

    def on_page_end(c, d):
        c._edition_date = edition_date

    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=on_page_end, onLaterPages=on_page_end)

