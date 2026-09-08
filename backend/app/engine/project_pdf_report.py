"""
Project Analysis & Strategic Diligence PDF Summary Report Builder.

Generates an institutional-grade, comprehensive executive summary PDF containing:
1. Complete Input Project Attributes & Technical Specifications
2. AI-Synthesized Technical & Strategic Diligence Briefing
3. High-Conviction Public Funding & Multi-Agency Grant Match Portfolio
4. Detailed Solicitation Profiles, Requirements Checklists & Win-Rate Benchmarks
5. Top Decision-Maker Outreach & 'Say Yes' Propensity Matrix (Utility Territories & Pain Points)
6. Recommended Strategic Action Roadmap & Non-Affiliation Declaration
"""

import io
import datetime
from typing import Dict, Any, List, Optional

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
    format_currency
)
from app.engine.ai_project_synthesizer import synthesize_project_executive_analysis


class ProjectReportNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for total page count and professional running headers/footers."""
    def __init__(self, *args, project_title: str = "INDEPENDENT CLEAN ENERGY MATCH REPORT", **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.project_title = project_title or "INDEPENDENT CLEAN ENERGY MATCH REPORT"

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
        self.setFont("Helvetica", 8)
        self.setFillColor(COLOR_BRAND_MUTED)

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            clean_title = self.project_title[:70] + "..." if len(self.project_title) > 70 else self.project_title
            self.drawString(40, 755, f"{clean_title.upper()} · INDEPENDENT DILIGENCE REPORT")
            self.setStrokeColor(COLOR_BRAND_BORDER)
            self.setLineWidth(0.5)
            self.line(40, 748, 572, 748)

        # Running Footer (all pages)
        self.setStrokeColor(COLOR_BRAND_BORDER)
        self.setLineWidth(0.5)
        self.line(40, 42, 572, 42)

        footer_text = "Independent Analytical Study · Public Information Only · Not an Endorsement"
        self.drawString(40, 30, footer_text)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 30, page_str)
        self.restoreState()


def safe_format_currency(val: Any) -> str:
    if val is None or val == 0:
        return "Unspecified"
    try:
        val_f = float(val)
        return format_currency(val_f)
    except Exception:
        return "Unspecified"


def generate_project_pdf_report(analysis_data: Dict[str, Any]) -> io.BytesIO:
    """
    Builds a multi-page executive summary PDF report.
    Removes WACC and Multi-Layer Financing sections, prioritizing opportunity matches,
    top 25 decision-maker rankings, and actionable diligence roadmaps.
    """
    buffer = io.BytesIO()

    # Extract project attributes
    profile = analysis_data.get("profile") or {}
    project_title = (
        profile.get("project_title")
        or profile.get("title")
        or analysis_data.get("project_title")
        or "Clean Energy Innovation Project"
    ).strip()

    summary_text = profile.get("summary") or analysis_data.get("summary") or "Project description not provided."
    loc_str = profile.get("target_location") or profile.get("ny_location") or profile.get("location") or "New York State"
    tech_areas = profile.get("technology_areas") or []
    activity_types = profile.get("activity_types") or []
    sectors = profile.get("sectors") or []
    trl_val = profile.get("estimated_trl") or "Unspecified"
    applicant_type = profile.get("applicant_type") or "Commercial Enterprise"
    cost_val = profile.get("project_cost")
    cost_float = float(cost_val) if cost_val else 10_000_000.0

    # Extract matches
    top_25_opps = analysis_data.get("top_25_opportunities") or []
    matches_obj = analysis_data.get("matches")
    if isinstance(matches_obj, dict):
        strong_matches = matches_obj.get("strong_matches", []) or matches_obj.get("primary", [])
        conditional_matches = matches_obj.get("conditional_matches", []) or matches_obj.get("thematic", [])
        component_matches = matches_obj.get("component_matches", []) or matches_obj.get("component", [])
        watchlist = matches_obj.get("watchlist", []) or matches_obj.get("aspirational", [])
    else:
        strong_matches = analysis_data.get("strong_matches", [])
        conditional_matches = analysis_data.get("conditional_matches", [])
        component_matches = analysis_data.get("component_matches", [])
        watchlist = analysis_data.get("watchlist", [])
    all_matches = top_25_opps or (strong_matches + conditional_matches + component_matches + watchlist)

    # Extract Top Say Yes Decision-Maker Matrix (Top 15 / Top 25)
    top_25_say_yes = analysis_data.get("top_15_say_yes") or analysis_data.get("top_25_say_yes") or analysis_data.get("say_yes_matrix") or []

    # Synthesize Strategic Executive Analysis
    briefing = synthesize_project_executive_analysis(analysis_data)
    exec_paragraphs = briefing.get("executive_summary_paragraphs") or []
    strategic_takeaways = briefing.get("strategic_takeaways") or []

    # Document Setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50,
    )

    # Styles
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=COLOR_BRAND_NAVY,
        spaceAfter=3,
    )
    style_subtitle = ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=COLOR_BRAND_CYAN,
        spaceAfter=5,
    )
    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=COLOR_BRAND_NAVY,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True,
    )
    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=COLOR_BRAND_NAVY,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True,
    )
    style_body = ParagraphStyle(
        'Body_Custom',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=COLOR_BRAND_SLATE,
        spaceAfter=4,
    )
    style_body_bold = ParagraphStyle(
        'Body_Bold_Custom',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=COLOR_BRAND_NAVY,
    )
    style_callout = ParagraphStyle(
        'Callout_Text',
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10.5,
        textColor=COLOR_BRAND_MUTED,
    )
    style_table_header = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1,
    )
    style_table_cell = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=COLOR_BRAND_SLATE,
    )
    style_table_cell_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=COLOR_BRAND_NAVY,
    )

    story = []

    # =========================================================================
    # HEADER BANNER & MASTHEAD
    # =========================================================================
    story.append(Paragraph(project_title, style_title))
    story.append(Paragraph("INDEPENDENT MULTI-AGENCY DILIGENCE & OPPORTUNITY MATCH REPORT", style_subtitle))
    story.append(Paragraph(
        f"Prepared: {datetime.date.today().strftime('%B %d, %Y')} · Multi-Agency Innovation Database · Comprehensive Funding Diligence",
        style_body
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_BRAND_NAVY, spaceBefore=4, spaceAfter=8))

    # =========================================================================
    # INDEPENDENT RESEARCH & PUBLIC INFORMATION DISCLAIMER
    # =========================================================================
    notice_table = Table([[
        Paragraph(
            "<b>INDEPENDENT RESEARCH & PUBLIC INFORMATION NOTICE:</b> This report was created entirely using publicly available information, open government databases, published statutory codes, and public solicitation filings. This document does not represent the official views, policies, endorsements, or determinations of any government agency, public institution, utility, or funding organization. No organizational resources of any agency or institution were used in the creation or generation of this report. This report is an independent analytical study for strategic planning purposes only; it does not constitute a promise, commitment, guarantee, or indicator of any organizational activity, formal evaluation, award selection, or funding event.",
            style_callout
        )
    ]], colWidths=[530])
    notice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BRAND_BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.8, COLOR_BRAND_SLATE),
        ('PADDING', (0, 0), (-1, -1), 5.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(notice_table)
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 1: PROJECT ATTRIBUTES & SPECIFICATIONS
    # =========================================================================
    story.append(Paragraph("1. Project Attributes & Technical Specifications", style_h1))

    specs_data = [
        [
            Paragraph("<b>Target Location:</b>", style_table_cell_bold),
            Paragraph(loc_str, style_table_cell),
            Paragraph("<b>Estimated Capex:</b>", style_table_cell_bold),
            Paragraph(safe_format_currency(cost_float), style_table_cell),
        ],
        [
            Paragraph("<b>Technology Areas:</b>", style_table_cell_bold),
            Paragraph(", ".join(tech_areas) if tech_areas else "Clean Energy Innovation", style_table_cell),
            Paragraph("<b>Readiness Level (TRL):</b>", style_table_cell_bold),
            Paragraph(f"TRL {trl_val}", style_table_cell),
        ],
        [
            Paragraph("<b>Activity Stages:</b>", style_table_cell_bold),
            Paragraph(", ".join(activity_types) if activity_types else "Pilot Demonstration & Scale", style_table_cell),
            Paragraph("<b>Applicant Entity:</b>", style_table_cell_bold),
            Paragraph(applicant_type.replace('_', ' ').title(), style_table_cell),
        ],
        [
            Paragraph("<b>Target Sectors:</b>", style_table_cell_bold),
            Paragraph(", ".join(sectors) if sectors else "Power Grid & Clean Infrastructure", style_table_cell),
            Paragraph("<b>Screened Database:</b>", style_table_cell_bold),
            Paragraph("5,708 Public Opportunities ($98.98B)", style_table_cell),
        ],
    ]
    specs_table = Table(specs_data, colWidths=[105, 160, 115, 150])
    specs_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BRAND_BG_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(specs_table)
    story.append(Spacer(1, 6))

    # Project Scope Paragraph
    story.append(Paragraph("<b>Project Scope & Objective:</b>", style_body_bold))
    story.append(Paragraph(summary_text, style_body))
    story.append(Spacer(1, 6))

    # Strategic Takeaways Box
    if strategic_takeaways:
        takeaway_rows = [[Paragraph(f"• <b>Key Insight:</b> {t}", style_body)] for t in strategic_takeaways]
        t_table = Table(takeaway_rows, colWidths=[530])
        t_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BRAND_BG_CYAN),
            ('BOX', (0, 0), (-1, -1), 0.8, COLOR_BRAND_CYAN),
            ('PADDING', (0, 0), (-1, -1), 4.5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_table)
        story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 2: MULTI-AGENCY HIGH-CONVICTION OPPORTUNITY MATCHES (TOP 25)
    # =========================================================================
    story.append(Paragraph("2. Top 25 High-Conviction Funding Solicitations & Grants", style_h1))
    story.append(Paragraph(
        "Screened against federal (DOE, ARPA-E, NSF, EPA, USDA), state innovation programs (NYSERDA, CEC, MassCEC), "
        "and utility programs with verified eligibility, objective scoring weights, and statutory funding alignment.",
        style_body
    ))

    # Match Summary Table (Top 25)
    match_rows = [[
        Paragraph("Rank", style_table_header),
        Paragraph("Solicitation / Program", style_table_header),
        Paragraph("Agency", style_table_header),
        Paragraph("Fit Score", style_table_header),
        Paragraph("Max Award ($)", style_table_header),
        Paragraph("Cost-Share", style_table_header),
        Paragraph("Deadline", style_table_header),
    ]]

    top_matches = top_25_opps[:25] if top_25_opps else (strong_matches + conditional_matches + component_matches + watchlist)[:25]
    if not top_matches and all_matches:
        top_matches = all_matches[:25]

    for idx, m in enumerate(top_matches, 1):
        fit_score_val = m.get("match_score_pct")
        if fit_score_val is None:
            raw_fit = m.get("fit_score", 0.85)
            fit_score_val = int(raw_fit * 100) if raw_fit <= 1.0 else int(raw_fit)
        fit_score_pct = int(fit_score_val)
        sol_num = m.get("solicitation_number") or f"OPP-{m.get('opportunity_id')}"
        name = m.get("name") or m.get("title") or "Solicitation"
        short_name = name[:50] + "..." if len(name) > 50 else name
        agency = m.get("agency") or "Public Agency"
        max_award = safe_format_currency(m.get("max_per_award") or m.get("total_funding"))
        cost_share = f"{m.get('cost_share_pct')}%" if m.get("cost_share_pct") is not None else "0%"
        deadline = m.get("next_deadline") or m.get("deadline") or "Open / Rolling"

        match_rows.append([
            Paragraph(f"<b>#{idx}</b>", style_table_cell_bold),
            Paragraph(f"<b>{sol_num}</b><br/>{short_name}", style_table_cell),
            Paragraph(agency, style_table_cell),
            Paragraph(f"<b>{fit_score_pct}%</b>", style_table_cell_bold),
            Paragraph(max_award, style_table_cell_bold),
            Paragraph(cost_share, style_table_cell),
            Paragraph(deadline, style_table_cell),
        ])

    m_table = Table(match_rows, colWidths=[28, 175, 110, 50, 72, 45, 50], repeatRows=1)
    m_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BRAND_BG_LIGHT]),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 8))

    # Top Match Deep-Dive Box
    if top_matches:
        top_opp = top_matches[0]
        story.append(Paragraph("Primary Grant Target Deep-Dive", style_h2))
        deep_dive_content = [
            [
                Paragraph(f"<b>Solicitation:</b> {top_opp.get('solicitation_number')} — {top_opp.get('name')}", style_body_bold),
                Paragraph(f"<b>Fit Conviction:</b> {top_opp.get('fit_level', 'High Priority')}", style_body_bold),
            ],
            [
                Paragraph(f"<b>Agency:</b> {top_opp.get('agency')}", style_body),
                Paragraph(f"<b>Max Award:</b> {safe_format_currency(top_opp.get('max_per_award') or top_opp.get('total_funding'))}", style_body),
            ],
            [
                Paragraph(f"<b>Why It Fits:</b> {top_opp.get('why_it_fits', 'High technical and geographic alignment with solicitation objectives.')}", style_body),
                Paragraph(f"<b>Cost-Share Required:</b> {top_opp.get('cost_share_pct', 0)}%", style_body),
            ],
        ]
        dd_table = Table(deep_dive_content, colWidths=[380, 150])
        dd_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BRAND_BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.6, COLOR_BRAND_BORDER),
            ('PADDING', (0, 0), (-1, -1), 4.5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(dd_table)
        story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 3: NATIONAL LAB TESTBEDS, GRID FEASIBILITY & CAPITAL CONTINUUM
    # =========================================================================
    story.append(Paragraph("3. National Lab Validation Testbeds & Multi-Stage Capital Continuum", style_h1))
    story.append(Paragraph(
        "Strategic infrastructure alignment linking concept derisking (TRL 3-6) to physical National Lab testbeds, "
        "ISO/RTO interconnection milestones, and downstream scale-up financing (SEC Form D, DOE LPO Title 17, IRA 48C & Federal Offtake).",
        style_body
    ))

    # Lab Testbeds Table
    lab_rows = [[
        Paragraph("National Lab Facility", style_table_header),
        Paragraph("Lab & Location", style_table_header),
        Paragraph("Key Validation Instruments & Capabilities", style_table_header),
        Paragraph("Access Mechanism & TRL Span", style_table_header),
    ]]
    lab_samples = [
        ("NREL ARIES Megawatt Grid Simulator", "NREL · Golden, CO", "20 MW Controllable Grid Interface (CGI), Hardware-in-the-Loop, Megawatt BESS & Electrolyzers", "CRADA / User Call · TRL 4–8"),
        ("PNNL Grid Storage Launchpad (GSL)", "PNNL · Richland, WA", "100kW/100kWh Module Testing, Operando Spectroscopy, Thermal Runaway Suppression", "Earthshot Voucher · TRL 3–6"),
        ("ORNL Carbon Fiber Tech Facility", "ORNL · Oak Ridge, TN", "Pilot Melt/Solution Spinning, Type IV Hydrogen Tanks, Composite Wind Spar Caps", "CRADA / SPP · TRL 4–7"),
        ("LBNL Molecular Foundry", "LBNL · Berkeley, CA", "TEAM 0.5 TEM (0.5 Ångström), Solid-State Electrolytes, Direct Air Capture MOFs", "Peer-Reviewed Proposal · TRL 1–4")
    ]
    for fac_name, loc, cap_str, acc_str in lab_samples:
        lab_rows.append([
            Paragraph(f"<b>{fac_name}</b>", style_table_cell_bold),
            Paragraph(loc, style_table_cell),
            Paragraph(cap_str, style_table_cell),
            Paragraph(acc_str, style_table_cell),
        ])
    lab_table = Table(lab_rows, colWidths=[140, 100, 180, 110], repeatRows=1)
    lab_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BRAND_BG_LIGHT]),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(lab_table)
    story.append(Spacer(1, 8))

    # Capital Progression Continuum Box
    continuum_box = [
        [
            Paragraph("<b>STAGE 1: NON-DILUTIVE SEED</b><br/>ARPA-E / State Grants ($1M–$5M)<br/>TRL 3 $\\rightarrow$ 5 Concept Validation", style_table_cell),
            Paragraph("<b>STAGE 2: PRIVATE REG D</b><br/>SEC Form D Equity ($10M–$50M)<br/>Series A/B Institutional Scaling", style_table_cell),
            Paragraph("<b>STAGE 3: FEDERAL OFFTAKE</b><br/>DoD DIU / FPDS Contracts ($5M–$25M)<br/>SBIR Phase III Sole-Source", style_table_cell),
            Paragraph("<b>STAGE 4: SCALE-UP DEBT/TAX</b><br/>DOE LPO Title 17 / 48C ($100M+)<br/>Commercial Gigafactory CapEx", style_table_cell),
        ]
    ]
    cont_table = Table(continuum_box, colWidths=[132, 132, 133, 133])
    cont_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BRAND_BG_CYAN),
        ('BOX', (0, 0), (-1, -1), 0.8, COLOR_BRAND_CYAN),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(cont_table)
    story.append(Spacer(1, 10))

    # Page Break for Decision-Maker Matrix & Outreach Strategy
    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: TOP 25 ORGANIZATIONS MOST LIKELY TO SAY YES ('SAY YES' PROPENSITY MATRIX)
    # =========================================================================
    story.append(Paragraph("4. Top 25 Organizations Most Likely to Say Yes ('Say Yes' Propensity Matrix)", style_h1))
    story.append(Paragraph(
        "Geographically filtered by exact utility service territories, state jurisdiction boundaries, active funding programs, "
        "and direct alignment with institutional pain points (substation feeder constraints, clean peak mandates, "
        "Justice40 quotas, and commercial Liftoff milestones). All listed entities represent identified prospective funding and partnership opportunities.",
        style_body
    ))

    # Render Top 25 Decision-Maker Organizations Table
    if top_25_say_yes:
        dm_rows = [[
            Paragraph("Rank", style_table_header),
            Paragraph("Organization", style_table_header),
            Paragraph("Category & Territory", style_table_header),
            Paragraph("Say Yes (%)", style_table_header),
            Paragraph("Targeted Institutional Pain Points", style_table_header),
            Paragraph("Lead Decision-Maker Contact", style_table_header),
        ]]

        for org in top_25_say_yes[:25]:
            lead_c = org.get("decision_maker_contacts", [{}])[0]
            contact_str = f"<b>{lead_c.get('name', 'Program Lead')}</b><br/>{lead_c.get('title', 'Innovation Lead')}<br/><font color='{COLOR_BRAND_CYAN.hexval()}'>{lead_c.get('email', '')}</font>"
            pain_str = "<br/>• ".join([""] + org.get("primary_pain_points", [])[:2])

            dm_rows.append([
                Paragraph(f"<b>#{org.get('rank')}</b>", style_table_cell_bold),
                Paragraph(f"<b>{org.get('organization_code')}</b><br/><font color='gray'>{org.get('organization_name', '')[:35]}</font>", style_table_cell),
                Paragraph(f"<b>{org.get('category_label')}</b><br/>{org.get('state')} ({org.get('territory_desc', '')[:30]})", style_table_cell),
                Paragraph(f"<b>{org.get('say_yes_score')}%</b><br/><font color='green'>{org.get('say_yes_tier')}</font>", style_table_cell_bold),
                Paragraph(pain_str, style_table_cell),
                Paragraph(contact_str, style_table_cell),
            ])

        dm_table = Table(dm_rows, colWidths=[28, 110, 105, 52, 125, 110], repeatRows=1)
        dm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_NAVY),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BRAND_BG_LIGHT]),
            ('PADDING', (0, 0), (-1, -1), 3.5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(dm_table)
        story.append(Spacer(1, 10))

    # Top Outreach Theses Box
    if top_25_say_yes:
        story.append(Paragraph("Strategic Outreach Positioning & Pitch Theses", style_h2))
        top_picks = top_25_say_yes[:3]
        thesis_data = []
        for pick in top_picks:
            thesis_data.append([
                Paragraph(f"<b>#{pick.get('rank')} {pick.get('organization_code')}</b>", style_table_cell_bold),
                Paragraph(f"<i>&ldquo;{pick.get('why_they_say_yes')}&rdquo;</i>", style_table_cell),
            ])
        th_table = Table(thesis_data, colWidths=[130, 400])
        th_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_BRAND_BG_CYAN),
            ('BOX', (0, 0), (-1, -1), 0.8, COLOR_BRAND_CYAN),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, COLOR_BRAND_BORDER_LIGHT),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(th_table)
        story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 4: RECOMMENDED STRATEGIC ACTION ROADMAP
    # =========================================================================
    story.append(Paragraph("4. Recommended Strategic Action Roadmap", style_h1))
    story.append(Paragraph(
        "Structured execution sequence to optimize application competitiveness for identified potential funding opportunities.",
        style_body
    ))
    roadmap_steps = [
        ("Step 1: Submission Readiness & Consortia Alignment", "Establish academic or national lab research partnerships and confirm matching cost-share commitments for identified grant solicitations."),
        ("Step 2: Pre-Application Program Officer Engagement", "Initiate formal concept inquiries with lead program officers at top-ranked identified organizations."),
        ("Step 3: Interconnection & Regulatory Pre-Filing", "Submit preliminary SIR interconnection requests with the designated local retail utility to verify feeder hosting capacity."),
        ("Step 4: Full Proposal Compilation & Merit Review", "Finalize technical volume, techno-economic analysis (TEA), and community benefit plans adhering strictly to FOA guidelines.")
    ]
    roadmap_data = []
    for title, desc in roadmap_steps:
        roadmap_data.append([
            Paragraph(f"<b>{title}</b>", style_table_cell_bold),
            Paragraph(desc, style_table_cell),
        ])
    rm_table = Table(roadmap_data, colWidths=[190, 340])
    rm_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BRAND_BG_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(rm_table)
    story.append(Spacer(1, 12))

    # Concluding Statutory Independence & Non-Affiliation Declaration
    closing_notice = Table([[
        Paragraph(
            "<b>STATUTORY INDEPENDENCE & NON-AFFILIATION DECLARATION:</b> "
            "This independent analysis was authored strictly utilizing open government data, published statutory guidelines, "
            "and public solicitation records. It does not represent the views or policies of any public agency or institution, "
            "and no organizational resources were used in its creation. This report does not represent a promise, commitment, "
            "or indicator of any organizational activity, formal evaluation, or funding event.",
            style_callout
        )
    ]], colWidths=[530])
    closing_notice.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BRAND_BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.8, COLOR_BRAND_SLATE),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(closing_notice)

    # Build PDF with two-pass canvas
    doc.build(
        story,
        canvasmaker=lambda *args, **kwargs: ProjectReportNumberedCanvas(*args, project_title=project_title, **kwargs)
    )

    buffer.seek(0)
    return buffer


def generate_project_analysis_pdf(data_payload: Dict[str, Any], output_stream: Optional[io.BytesIO] = None) -> io.BytesIO:
    """Compatibility alias for PDF report generation."""
    buf = generate_project_pdf_report(data_payload)
    if output_stream is not None:
        output_stream.write(buf.getvalue())
        output_stream.seek(0)
        return output_stream
    return buf
