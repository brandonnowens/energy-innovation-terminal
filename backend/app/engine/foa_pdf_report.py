"""
FOA Requirements, Compliance & Scoring Blueprint PDF Report Generator.

Generates an institutional-grade, multi-page publication PDF report containing:
1. Solicitation Identity & Programmatic Meta Box
2. Executive Summary & Statutory Authority Scope
3. Official Reviewer Evaluation Rubric & Criterion Weightings Table
4. Mandatory Compliance Gates & Disqualification Thresholds
5. Proposal Submission Volume Checklist (Page Limits, Font Rules, Deliverables)
6. Red-Team Winning Themes & Strategic Proposal Positioning
7. Critical Disqualification Fatal Flaws to Avoid
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
    format_currency, SOURCE_ATTRIBUTION
)


class FoaBlueprintNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for total page count and professional running headers/footers."""
    def __init__(self, *args, sol_number: str = "SOLICITATION BLUEPRINT", **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.sol_number = sol_number or "SOLICITATION BLUEPRINT"

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
            clean_sol = self.sol_number[:65]
            self.setFont("Helvetica-Bold", 6.5)
            self.setFillColor(COLOR_BRAND_AMBER)
            self.drawString(40, 748, f"ENERGY INNOVATION TERMINAL BY AIxENERGY // FOA BLUEPRINT: {clean_sol.upper()}")

            self.setFont("Helvetica", 6.5)
            self.setFillColor(COLOR_BRAND_MUTED)
            self.drawRightString(572, 748, f"PROPOSAL COMPLIANCE & SCORING ARCHIVE · terminal.aixenergy.io")

            self.setStrokeColor(COLOR_BRAND_BORDER_LIGHT)
            self.setLineWidth(0.5)
            self.line(40, 742, 572, 742)

        # Running Footer (all pages)
        self.setStrokeColor(COLOR_BRAND_BORDER_LIGHT)
        self.setLineWidth(0.5)
        self.line(40, 44, 572, 44)

        self.setFont("Helvetica", 6.5)
        self.setFillColor(COLOR_BRAND_MUTED)
        self.drawString(40, 34, "Energy Innovation Terminal by AIxEnergy · terminal.aixenergy.io · Institutional Grant Intelligence")

        self.setFont("Helvetica-Bold", 7)
        self.setFillColor(COLOR_BRAND_NAVY)
        self.drawRightString(572, 34, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def generate_foa_blueprint_pdf(shred_data: Dict[str, Any]) -> io.BytesIO:
    """Compiles a publication-grade PDF FOA proposal blueprint."""
    buffer = io.BytesIO()

    title = shred_data.get("title") or "Funding Opportunity Announcement"
    sol_num = shred_data.get("solicitation_number") or "FOA SOLICITATION"
    agency = shred_data.get("agency") or "Public Energy Agency"
    total_funding = shred_data.get("total_funding") or 0
    max_award = shred_data.get("max_award") or 0
    cost_share_pct = shred_data.get("cost_share_required_pct") or 0.0
    cost_share_rule = shred_data.get("cost_share_rule_explanation") or "Standard non-federal matching requirement."
    trl_min = shred_data.get("trl_min") or 3
    trl_max = shred_data.get("trl_max") or 8
    summary = shred_data.get("executive_summary") or shred_data.get("description") or "Complete solicitation blueprint."
    rubric = shred_data.get("scoring_rubric") or []
    compliance = shred_data.get("compliance_gates") or []
    checklist = shred_data.get("submission_checklist") or []
    win_themes = shred_data.get("key_win_themes") or []
    fatal_flaws = shred_data.get("red_team_fatal_flaws_to_avoid") or []

    # Ensure robust 5-gate compliance matrix if not explicitly present
    if not compliance:
        compliance = [
            {
                "gate": "GATE-01-COSTSHARE",
                "rule": f"Mandatory {cost_share_pct:.0f}% non-federal matching funds with verified third-party commitment letters.",
                "consequence": "Immediate Administrative Rejection (No Review)"
            },
            {
                "gate": "GATE-02-SAM-UEI",
                "rule": "Active SAM.gov registration, valid CAGE Code, and Unique Entity Identifier (UEI) prior to submission.",
                "consequence": "Electronic Gateway Rejection"
            },
            {
                "gate": "GATE-03-DOMESTIC",
                "rule": "Build America, Buy America (BABA) compliance and 100% domestic iron, steel, and manufactured goods certification.",
                "consequence": "Post-Award Mandatory Clawback"
            },
            {
                "gate": "GATE-04-JUSTICE40",
                "rule": "Community Benefits Plan (CBP) committing measurable investments to disadvantaged communities and workforce equity.",
                "consequence": "Scoring Penalty (Up to -20 Points)"
            },
            {
                "gate": "GATE-05-FEOC-EXCLUSION",
                "rule": "Exclusion of foreign entities of concern (FEOC) from clean tech supply chain, critical minerals, and IP ownership.",
                "consequence": "Statutory Eligibility Bar"
            }
        ]

    # Ensure robust submission volumes if not present
    if not checklist:
        checklist = [
            {"volume": 1, "section_code": "VOL-1-NARRATIVE", "title": "Technical Volume / Project Narrative", "page_limit": 25, "font_rules": "11pt Times or Arial, 1-inch margins", "mandatory": True, "description": "Executive summary, technical background, work breakdown structure (WBS), and risk matrix."},
            {"volume": 2, "section_code": "VOL-2-SOPO", "title": "Statement of Project Objectives (SOPO)", "page_limit": 10, "font_rules": "Standard table template", "mandatory": True, "description": "Quarterly milestone table, Go/No-Go decision points, and technical deliverables."},
            {"volume": 3, "section_code": "VOL-3-BUDGET", "title": "Detailed Budget Justification (SF-424A)", "page_limit": None, "font_rules": "Standard Excel workbook", "mandatory": True, "description": f"Direct labor, equipment, subcontracts, travel, and verified {cost_share_pct:.0f}% non-federal cost-share commitment letters."},
            {"volume": 4, "section_code": "VOL-4-CBP", "title": "Community Benefits Plan (CBP) / Justice40", "page_limit": 8, "font_rules": "11pt font", "mandatory": True, "description": "Diversity, Equity, Inclusion, accessibility, and direct economic investments in disadvantaged communities."},
            {"volume": 5, "section_code": "VOL-5-LETTERS", "title": "Letters of Commitment & Teaming MOUs", "page_limit": None, "font_rules": "Signed PDF letterhead", "mandatory": True, "description": "Signed letters from industrial host sites, utility partners, and test facilities."}
        ]

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
        fontName='Helvetica-Bold', fontSize=7.5, leading=9,
        textColor=COLOR_BRAND_AMBER, textTransform='uppercase', spaceAfter=2
    )
    style_h1 = ParagraphStyle(
        'MainH1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=16, leading=20,
        textColor=COLOR_BRAND_NAVY, spaceAfter=4
    )
    style_h2 = ParagraphStyle(
        'SectionH2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10.5, leading=13,
        textColor=COLOR_BRAND_NAVY, spaceBefore=10, spaceAfter=5,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        'BodyDark', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11,
        textColor=COLOR_BRAND_SLATE
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
    style_mono_amber = ParagraphStyle(
        'MonoAmber', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=10,
        textColor=COLOR_BRAND_AMBER
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
    story.append(Paragraph("ENERGY INNOVATION TERMINAL // FOA REQUIREMENTS &amp; COMPLIANCE BLUEPRINT", style_super_title))
    story.append(Paragraph(f"{sol_num}: {title}", style_h1))

    # Meta Scorecard Box
    meta_data = [
        [
            Paragraph("<b>ISSUING AGENCY</b>", style_table_header),
            Paragraph("<b>TOTAL FUNDING POOL</b>", style_table_header),
            Paragraph("<b>MAX PER AWARD</b>", style_table_header),
            Paragraph("<b>MANDATORY COST SHARE</b>", style_table_header),
            Paragraph("<b>TARGET TRL RANGE</b>", style_table_header),
        ],
        [
            Paragraph(f"<b>{agency}</b>", style_mono),
            Paragraph(f"<font color='#059669'><b>{format_currency(total_funding)}</b></font>", style_mono_green),
            Paragraph(f"<b>{format_currency(max_award) if max_award else 'Varies'}</b>", style_mono),
            Paragraph(f"<font color='#D97706'><b>{cost_share_pct}% Required</b></font>", style_mono_amber),
            Paragraph(f"<b>TRL {trl_min}–{trl_max}</b>", style_mono),
        ]
    ]

    t_meta = Table(meta_data, colWidths=[120, 110, 105, 110, 91])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_NAVY),
        ('BACKGROUND', (0, 1), (-1, 1), COLOR_BRAND_BG_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # Executive Overview
    story.append(Paragraph(f"<b>Executive Solicitation Scope:</b> {summary}", style_body))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Cost-Share Statutory Guidelines:</b> {cost_share_rule}", style_body))
    story.append(Spacer(1, 8))

    # ── SECTION 1: OFFICIAL REVIEWER EVALUATION RUBRIC ──
    story.append(Paragraph("1. Official Reviewer Evaluation Rubric &amp; Weightings Matrix", style_h2))
    if rubric:
        rubric_rows = [
            [
                Paragraph("<b>Evaluation Criterion</b>", style_table_header),
                Paragraph("<b>Weight %</b>", style_table_header),
                Paragraph("<b>Reviewer Scope &amp; Scoring Factors</b>", style_table_header),
                Paragraph("<b>Primary Technical Hurdle</b>", style_table_header),
            ]
        ]
        for r in rubric:
            rubric_rows.append([
                Paragraph(str(r.get("criterion") or "Technical Innovation"), style_mono),
                Paragraph(f"<b>{r.get('weight_pct', 25)}%</b>", style_mono_green),
                Paragraph(str(r.get("description") or "Reviewer criteria")[:120], style_table_cell),
                Paragraph(str(r.get("key_focus") or "Focus area")[:80], style_table_cell),
            ])

        t_rubric = Table(rubric_rows, colWidths=[140, 55, 201, 140])
        t_rubric.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_NAVY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BRAND_BG_LIGHT]),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
            ('PADDING', (0, 0), (-1, -1), 3.5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_rubric)
    else:
        story.append(Paragraph("<i>Standard agency merit review weighting applies.</i>", style_body))

    story.append(Spacer(1, 8))

    # ── SECTION 2: STATUTORY COMPLIANCE STAGE GATES ──
    story.append(Paragraph("2. Mandatory Statutory Compliance Stage Gates (Pass / Fail)", style_h2))
    if compliance:
        comp_rows = [
            [
                Paragraph("<b>Gate Code</b>", style_table_header),
                Paragraph("<b>Mandatory Rule &amp; Verification Threshold</b>", style_table_header),
                Paragraph("<b>Failure Consequence</b>", style_table_header),
            ]
        ]
        for c in compliance:
            comp_rows.append([
                Paragraph(str(c.get("gate") or "GATE"), style_mono),
                Paragraph(str(c.get("rule") or "Compliance rule"), style_table_cell),
                Paragraph(f"<font color='#B91C1C'><b>{c.get('consequence') or 'Immediate Disqualification'}</b></font>", style_table_cell),
            ])

        t_comp = Table(comp_rows, colWidths=[110, 276, 150])
        t_comp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_SLATE),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BRAND_BG_LIGHT]),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
            ('PADDING', (0, 0), (-1, -1), 3.5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_comp)
    else:
        story.append(Paragraph("<i>Standard SAM.gov, domestic content, and cost-share compliance gates apply.</i>", style_body))

    story.append(Spacer(1, 8))

    # ── SECTION 3: PROPOSAL SUBMISSION VOLUME CHECKLIST ──
    story.append(Paragraph("3. Proposal Submission Volume Checklist (Page Limits &amp; Formatting)", style_h2))
    if checklist:
        vol_rows = [
            [
                Paragraph("<b>Volume &amp; Section Code</b>", style_table_header),
                Paragraph("<b>Document Title &amp; Description</b>", style_table_header),
                Paragraph("<b>Page Limit</b>", style_table_header),
                Paragraph("<b>Formatting Rules</b>", style_table_header),
            ]
        ]
        for v in checklist:
            lim = f"Max {v.get('page_limit')} Pages" if v.get('page_limit') else "No Limit"
            vol_rows.append([
                Paragraph(str(v.get("section_code") or f"VOL-{v.get('volume', 1)}"), style_mono),
                Paragraph(f"<b>{v.get('title')}</b><br/><font size=6 color='#64748B'>{v.get('description', '')[:70]}</font>", style_table_cell),
                Paragraph(lim, style_mono_amber),
                Paragraph(str(v.get("font_rules") or "11pt Arial, 1-inch margins"), style_table_cell),
            ])

        t_vol = Table(vol_rows, colWidths=[100, 236, 80, 120])
        t_vol.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_NAVY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BRAND_BG_LIGHT]),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
            ('PADDING', (0, 0), (-1, -1), 3.5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_vol)

    story.append(Spacer(1, 8))

    # ── SECTION 4: RED-TEAM WIN STRATEGY & FATAL FLAWS ──
    story.append(Paragraph("4. Red-Team Win Strategy &amp; Disqualification Traps", style_h2))
    
    left_themes = [
        [Paragraph("<b>Key Winning Themes to Feature</b>", style_table_header)]
    ]
    if win_themes:
        for wt in win_themes[:6]:
            left_themes.append([Paragraph(f"<font color='#059669'><b>✓</b></font> {wt}", style_table_cell)])
    else:
        left_themes.append([Paragraph("<i>Focus on quantitative baseline validation and verified cost-share.</i>", style_table_cell)])

    t_themes = Table(left_themes, colWidths=[265])
    t_themes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_BRAND_EMERALD),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BRAND_BG_EMERALD]),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 3.5),
    ]))

    right_flaws = [
        [Paragraph("<b>Red-Team Fatal Flaws to Avoid</b>", style_table_header)]
    ]
    if fatal_flaws:
        for ff in fatal_flaws[:6]:
            right_flaws.append([Paragraph(f"<font color='#DC2626'><b>✗</b></font> {ff}", style_table_cell)])
    else:
        right_flaws.append([Paragraph("<i>Avoid vague TRL assertions and uncommitted cost-share letters.</i>", style_table_cell)])

    t_flaws = Table(right_flaws, colWidths=[265])
    t_flaws.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC2626')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FEF2F2')]),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BRAND_BORDER_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 3.5),
    ]))

    split_strategy = Table([[t_themes, t_flaws]], colWidths=[268, 268])
    split_strategy.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(split_strategy)

    doc.build(story, canvasmaker=lambda *args, **kwargs: FoaBlueprintNumberedCanvas(*args, sol_number=sol_num, **kwargs))
    buffer.seek(0)
    return buffer
