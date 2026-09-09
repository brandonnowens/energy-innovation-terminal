"""Publication-grade Statement of Project Objectives (SOPO) & Technical WBS Report Generator.
Built with ReportLab for institutional quality and DOE/ARPA-E stage gate compliance.
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
ACCENT_PURPLE = colors.HexColor("#4f46e5")
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
            self.drawString(54, 750, "Energy Innovation Terminal by AIxEnergy | SOPO Work Breakdown Structure")
            self.drawRightString(612 - 54, 750, f"Project: {getattr(self, '_proj_title', 'SOPO Package')[:40]}")
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


def build_sopo_package_pdf(proposal_data: Dict[str, Any], output_stream: io.BytesIO) -> None:
    """Compiles a publication-grade Statement of Project Objectives (SOPO) Package PDF."""
    doc = SimpleDocTemplate(
        output_stream,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Typography
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=PRIMARY_COLOR,
        spaceAfter=4
    )

    badge_style = ParagraphStyle(
        'BadgeStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=ACCENT_PURPLE
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=SECONDARY_COLOR,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_DARK,
        spaceAfter=5
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

    # Extract metadata
    title = str(proposal_data.get('title') or proposal_data.get('project_title') or "Statement of Project Objectives (SOPO)")
    sol_num = str(proposal_data.get('solicitation_number') or proposal_data.get('opportunity_number') or "DE-FOA-0003210")
    agency = str(proposal_data.get('agency') or proposal_data.get('target_agency') or "U.S. Department of Energy (DOE)")
    recipient = str(proposal_data.get('recipient_name') or proposal_data.get('applicant_name') or "Lead Principal Investigator")
    total_budget = str(proposal_data.get('total_budget') or proposal_data.get('award_amount_fmt') or "$3,750,000")
    cost_share = str(proposal_data.get('cost_share_pct') or "20%")
    duration = str(proposal_data.get('duration_months') or proposal_data.get('period_of_performance') or "36 Months (3 Budget Periods)")

    # 1. Header Banner
    header_data = [
        [
            Paragraph(f"<b>ENERGY INNOVATION TERMINAL BY AIxENERGY</b><br/><font color='#4f46e5'>STATEMENT OF PROJECT OBJECTIVES (SOPO) &bull; WORK BREAKDOWN STRUCTURE</font>", badge_style),
            Paragraph(f"<font color='#64748b'><b>Target Solicitation:</b> {sol_num}<br/><b>Granting Agency:</b> {agency}</font>", table_cell_style)
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

    # 2. Project Title
    story.append(Paragraph(title, title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_PURPLE, spaceBefore=3, spaceAfter=6))

    # 3. Parameters Strip
    param_data = [
        [
            Paragraph("<font size=7 color='#64748b'>LEAD APPLICANT</font><br/><b><font size=10 color='#0f172a'>" + recipient[:25] + "</font></b>", table_cell_style),
            Paragraph("<font size=7 color='#64748b'>TOTAL BUDGET</font><br/><b><font size=10 color='#059669'>" + total_budget + "</font></b>", table_cell_style),
            Paragraph("<font size=7 color='#64748b'>COST-SHARE COMMITMENT</font><br/><b><font size=10 color='#0284c7'>" + cost_share + "</font></b>", table_cell_style),
            Paragraph("<font size=7 color='#64748b'>PERFORMANCE PERIOD</font><br/><b><font size=10 color='#d97706'>" + duration + "</font></b>", table_cell_style),
        ]
    ]
    param_table = Table(param_data, colWidths=[126, 126, 126, 126])
    param_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(param_table)
    story.append(Spacer(1, 8))

    # 4. Project Objective & Executive Scope Narrative
    story.append(Paragraph("1. Project Technical Objectives & Scope of Work", section_heading))
    scope_narrative = str(proposal_data.get('scope_narrative') or proposal_data.get('executive_summary') or proposal_data.get('sopo_narrative') or "This project executes a multi-phase research, development, and demonstration program to validate prototype performance under extreme operational conditions, de-risk commercial scale-up, and deliver certified compliance data to federal and state utility stakeholders.")
    for p_text in scope_narrative.split("\n\n"):
        if p_text.strip():
            story.append(Paragraph(p_text.strip(), body_style))
    story.append(Spacer(1, 6))

    # 5. Work Breakdown Structure (WBS) & Task Matrix
    tasks = proposal_data.get('sopo_tasks') or proposal_data.get('tasks') or [
        {
            'task': 'Task 1.0: Preliminary Engineering & Design Review',
            'budget': '$450,000',
            'lead': 'Principal Investigator',
            'milestone': 'Milestone 1.2: Complete baseline system characterization.',
            'gate': 'Go/No-Go Gate 1: Formal engineering sign-off achieved.',
            'trl': 'TRL 4 -> TRL 5'
        },
        {
            'task': 'Task 2.0: Modular Cell Manufacturing & Validation Testing',
            'budget': '$2,200,000',
            'lead': 'Laboratory Team',
            'milestone': 'Milestone 2.3: Continuous operational performance testing.',
            'gate': 'Go/No-Go Gate 2: Safety certifications validated by independent lab.',
            'trl': 'TRL 5 -> TRL 6'
        },
        {
            'task': 'Task 3.0: Grid Interconnection Simulation & Utility Host Demonstration',
            'budget': '$1,100,000',
            'lead': 'Consortium OEM & Utility',
            'milestone': 'Milestone 3.1: 1,000 hours of continuous grid simulation logging.',
            'gate': 'Final Project Closeout: Full commercialization package and data transfer.',
            'trl': 'TRL 6 -> TRL 7'
        }
    ]

    story.append(Paragraph("2. Work Breakdown Structure (WBS) Tasks & Budget Allocations", section_heading))
    task_table_data = [
        [
            Paragraph("TASK / WORKSTREAM", table_header_style),
            Paragraph("ALLOCATION", table_header_style),
            Paragraph("RESPONSIBLE LEAD", table_header_style),
            Paragraph("TRL PROGRESSION", table_header_style),
        ]
    ]
    for t in tasks:
        task_name = str(t.get('task') or t.get('name') or 'Task')
        bgt = str(t.get('budget') or t.get('allocation') or '$500,000')
        lead = str(t.get('lead') or t.get('lead_org') or 'PI')
        trl = str(t.get('trl') or 'TRL 4 -> 6')

        task_table_data.append([
            Paragraph(f"<b>{task_name}</b>", table_cell_bold),
            Paragraph(f"<font color='#059669'><b>{bgt}</b></font>", table_cell_style),
            Paragraph(lead, table_cell_style),
            Paragraph(f"<font color='#4f46e5'><b>{trl}</b></font>", table_cell_style),
        ])

    task_table = Table(task_table_data, colWidths=[240, 80, 114, 70])
    task_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_COLOR),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(task_table)
    story.append(Spacer(1, 8))

    # 6. Detailed Milestones & Go/No-Go Stage Gates Table
    story.append(Paragraph("3. Technical Milestones & Mandatory Go/No-Go Decision Stage Gates", section_heading))
    gate_table_data = [
        [
            Paragraph("WBS TASK REF", table_header_style),
            Paragraph("VERIFIABLE MILESTONE DELIVERABLE", table_header_style),
            Paragraph("GO / NO-GO STAGE GATE CRITERION", table_header_style),
        ]
    ]
    for t in tasks:
        task_name = str(t.get('task') or 'Task')
        milestone = str(t.get('milestone') or 'System validation complete.')
        gate = str(t.get('gate') or 'Formal milestone sign-off achieved.')

        gate_table_data.append([
            Paragraph(f"<b>{task_name[:35]}</b>", table_cell_bold),
            Paragraph(milestone, table_cell_style),
            Paragraph(f"<font color='#b91c1c'><b>{gate}</b></font>", table_cell_style),
        ])

    gate_table = Table(gate_table_data, colWidths=[130, 190, 184])
    gate_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(gate_table)
    story.append(Spacer(1, 10))

    # 7. Compliance Verification Footer Box
    signoff_data = [
        [
            Paragraph(
                "<b>SOPO Stage-Gate Notice:</b> All work breakdown structures, technical deliverables, and milestone stage gates generated by the Energy Innovation Terminal are structured strictly in compliance with DOE Financial Assistance Instructions (2 CFR 200 / 2 CFR 910) and ARPA-E Technical Milestone Management Protocols.<br/>"
                "<b>Generated via Energy Innovation Terminal:</b> terminal.aixenergy.io &bull; <b>Lead Technical Architect:</b> bowens@aixenergy.io",
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
        c._proj_title = title

    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=on_page_end, onLaterPages=on_page_end)
