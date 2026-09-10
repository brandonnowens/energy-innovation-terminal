import os
import sys
import io
import fitz
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class CapabilitiesNumberedCanvas(canvas.Canvas):
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        # Outer neatline
        self.setStrokeColor(colors.HexColor('#0F172A'))
        self.setLineWidth(1.0)
        self.rect(26, 26, 560, 740)

        # Inner neatline
        self.setStrokeColor(colors.HexColor('#E2E8F0'))
        self.setLineWidth(0.5)
        self.rect(29, 29, 554, 734)

        # Running Header (Page 2+)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 6.5)
            self.setFillColor(colors.HexColor('#0284C7'))
            self.drawString(38, 748, "ENERGY INNOVATION TERMINAL BY AIxENERGY // CAPABILITIES & MARKET BENCHMARK")

            self.setFont("Helvetica", 6.5)
            self.setFillColor(colors.HexColor('#64748B'))
            self.drawRightString(574, 748, "INSTITUTIONAL BRIEF · terminal.aixenergy.io · bowens@aixenergy.io")

            self.setStrokeColor(colors.HexColor('#E2E8F0'))
            self.setLineWidth(0.5)
            self.line(38, 742, 574, 742)

        # Running Footer (All Pages)
        self.setStrokeColor(colors.HexColor('#CBD5E1'))
        self.setLineWidth(0.5)
        self.line(38, 44, 574, 44)

        self.setFont("Helvetica", 6.5)
        self.setFillColor(colors.HexColor('#64748B'))
        self.drawString(38, 34, "Energy Innovation Terminal by AIxEnergy · terminal.aixenergy.io · Direct: bowens@aixenergy.io")

        self.setFont("Helvetica-Bold", 6.5)
        self.setFillColor(colors.HexColor('#0F172A'))
        self.drawRightString(574, 34, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_capabilities_pdf() -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=44,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    NAVY = colors.HexColor('#0F172A')
    CYAN = colors.HexColor('#0284C7')
    DARK_BLUE = colors.HexColor('#1E293B')
    MUTED = colors.HexColor('#64748B')
    BG_LIGHT = colors.HexColor('#F8FAFC')
    BG_SUBTLE = colors.HexColor('#F1F5F9')
    BORDER_LIGHT = colors.HexColor('#E2E8F0')
    BORDER_MID = colors.HexColor('#CBD5E1')

    style_title = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=NAVY)
    style_sub = ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=CYAN)
    style_h2 = ParagraphStyle('SectionH2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=12.5, textColor=NAVY, spaceBefore=4, spaceAfter=3)
    style_body = ParagraphStyle('DocBody', parent=styles['Normal'], fontName='Helvetica', fontSize=7.6, leading=11, textColor=DARK_BLUE)
    
    style_metric_num = ParagraphStyle('MetricNum', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=12, textColor=CYAN, alignment=1)
    style_metric_label = ParagraphStyle('MetricLabel', parent=styles['Normal'], fontName='Helvetica', fontSize=6.5, leading=8.5, textColor=MUTED, alignment=1)

    style_bullet = ParagraphStyle('DocBullet', parent=styles['Normal'], fontName='Helvetica', fontSize=7.2, leading=10, textColor=DARK_BLUE)
    style_bullet_bold = ParagraphStyle('DocBulletBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.2, leading=10, textColor=NAVY)
    style_th = ParagraphStyle('DocTH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=NAVY)
    style_card_body = ParagraphStyle('CardBody', parent=styles['Normal'], fontName='Helvetica', fontSize=7.2, leading=9.8, textColor=DARK_BLUE)

    story = []

    # =========================================================================
    # PAGE 1: MASTHEAD, PLATFORM SCOPE & 9 CORE CAPABILITY MODULES
    # =========================================================================

    # Masthead
    masthead_data = [
        [
            Paragraph("<b>ENERGY INNOVATION TERMINAL BY AIxENERGY</b><br/><font size=7 color='#64748B'>CLEAN ENERGY GRANT &amp; CAPITAL INTELLIGENCE PLATFORM</font>", style_title),
            Paragraph("<b>CAPABILITIES SPECIFICATION</b><br/><font color='#0284c7'><b>terminal.aixenergy.io</b></font><br/><font size=6.5 color='#64748B'>Direct: bowens@aixenergy.io</font>", ParagraphStyle('MastRight', parent=style_sub, alignment=2))
        ]
    ]
    masthead_t = Table(masthead_data, colWidths=[360, 180])
    masthead_t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(masthead_t)
    story.append(HRFlowable(width="100%", thickness=1.5, color=CYAN, spaceBefore=3, spaceAfter=5))

    # Executive Overview Box
    exec_overview = (
        "<b>Executive Overview:</b> Advising clean technology innovators on competitive federal and state funding programs requires "
        "rigorous compliance analysis, including statutory stage gates, Community Benefits Plans (CBP), non-federal cost-share matching "
        "covenants, Buy America provisions, and multi-organization teaming arrangements across disparate public records.<br/><br/>"
        "<b>Energy Innovation Terminal (terminal.aixenergy.io)</b> is a specialized grant and market intelligence platform engineered "
        "for clean tech consultancies, project developers, research institutions, and corporate strategists. The platform aggregates and "
        "links non-dilutive public awards, active solicitations, venture capital financings, regulatory filings, and research infrastructure "
        "across federal, state, and utility entities into a unified workflow."
    )
    callout_t = Table([[Paragraph(exec_overview, style_body)]], colWidths=[540])
    callout_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER_MID),
        ('PADDING', (0,0), (-1,-1), 5.5)
    ]))
    story.append(callout_t)
    story.append(Spacer(1, 3))

    # Quantitative Scope Metric Bar
    metric_data = [
        [
            Paragraph("<b>56,413</b>", style_metric_num),
            Paragraph("<b>$104.16B</b>", style_metric_num),
            Paragraph("<b>140+</b>", style_metric_num),
            Paragraph("<b>5,757</b>", style_metric_num),
            Paragraph("<b>10,250+</b>", style_metric_num)
        ],
        [
            Paragraph("Awards Indexed", style_metric_label),
            Paragraph("Tracked Capital", style_metric_label),
            Paragraph("Funding Authorities", style_metric_label),
            Paragraph("Solicitations Mapped", style_metric_label),
            Paragraph("Grid Projects Tracked", style_metric_label)
        ]
    ]
    metric_table = Table(metric_data, colWidths=[108, 108, 108, 108, 108])
    metric_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_SUBTLE),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 4))

    # Core Platform Capabilities Section
    story.append(Paragraph("<b>CORE PLATFORM CAPABILITIES &amp; FUNCTIONAL MODULES</b>", style_h2))

    modules = [
        (
            "1. Funding Opportunity Deconstruction & Compliance Analysis",
            "Automated parsing of multi-volume solicitations (DOE, ARPA-E, CEC, State Energy Offices, EPA, USDA) into structured evaluation scoring rubrics, eligibility gates, submission volume checklists, and compliance requirements.",
            "Eliminates manual review cycles; produces structured compliance matrices for proposal managers and review teams."
        ),
        (
            "2. Historical Awardee Database & Consortia Teaming Network",
            "Multi-criteria repository of 56,400+ winning prime recipients, sub-awardees, national laboratories, universities, and utility partners across 140+ funding bodies with historical award tracking.",
            "Identifies qualified prime and sub-recipient partners with verified past-performance records to assemble consortia."
        ),
        (
            "3. Agency Program Manager & Decision-Maker Directory",
            "Structured directory indexing program managers, technical project officers, division directors, and contracting personnel across active federal and state energy offices.",
            "Maps agency organizational structures and points of contact to support pre-solicitation communications."
        ),
        (
            "4. Integrated Capital Continuum & Recipient Dossiers",
            "Entity-level resolution linking non-dilutive grant awards, SEC Form D equity filings, climate venture rounds, DOE LPO debt facilities, and commercial Bayh-Dole patent assignments.",
            "Enables comprehensive due diligence on co-investor syndicates, commercial maturity, and cost-share sources."
        ),
        (
            "5. Solicitation Cycle Tracking & Advanced Release Forecasting",
            "Tracking of recurring federal and state solicitation cadences, anticipated funding window openings, and legislative budget authorizations across major clean energy programs.",
            "Provides strategic early-warning visibility into upcoming funding opportunities 3 to 6 months ahead of formal releases."
        ),
        (
            "6. DOE National Laboratory Facilities & Testbed Directory",
            "Catalog of user facilities, specialized testing instrumentation, and proposal cycles across national laboratories (NREL, LBNL, PNNL, ORNL, NETL, ANL).",
            "Matches technology developers with required validation assets, pilot demonstration sites, and CRADA pathways."
        ),
        (
            "7. Regulatory Proceedings, PUC Dockets & Policy Mandates",
            "Continuous tracking of state Public Utility Commission (PUC) dockets, FERC filings, interconnection standards (IEEE 1547), and statutory decarbonization mandates.",
            "Ensures proposed technology deployments align with regional grid requirements and state policy priorities."
        ),
        (
            "8. Clean Energy Tax Credit Modeling & IRA Provisions",
            "Financial modeling engine for direct pay elective transfers, Section 48C / 45X / 45V / 45Q production and investment tax credits, and domestic content adders.",
            "Evaluates blended capital structures combining non-dilutive government grants with federal tax credit monetization."
        ),
        (
            "9. Institutional Document & Compliance Export Engine",
            "Standardized export engine generating publication-ready executive dossiers, scoring compliance matrices, and funding landscape reports formatted for immediate advisory delivery.",
            "Produces structured, presentation-ready briefing deliverables for client engagements and executive review."
        )
    ]

    mod_table_data = [
        [
            Paragraph("<b>Platform Capability Module</b>", style_th),
            Paragraph("<b>Technical Functionality &amp; Data Scope</b>", style_th),
            Paragraph("<b>Institutional Value &amp; Advisory Application</b>", style_th)
        ]
    ]
    for name, desc, val in modules:
        mod_table_data.append([
            Paragraph(f"<b>{name}</b>", style_bullet_bold),
            Paragraph(desc, style_bullet),
            Paragraph(val, style_bullet)
        ])

    mod_table = Table(mod_table_data, colWidths=[138, 246, 156])
    mod_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_SUBTLE),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(mod_table)

    # =========================================================================
    # PAGE 2: COMPETITIVE DIFFERENTIATION, ARCHITECTURE & USE CASES
    # =========================================================================
    story.append(PageBreak())

    story.append(Paragraph("<b>COMPETITIVE BENCHMARK &amp; MARKET DIFFERENTIATION</b>", style_h2))
    story.append(Spacer(1, 1))

    comp_data = [
        [
            Paragraph("<b>Evaluation Dimension</b>", style_th),
            Paragraph("<b>Energy Innovation Terminal (AIxEnergy)</b>", style_th),
            Paragraph("<b>Private Market Platforms<br/><font size=6 color='#64748B'>(PitchBook, Crunchbase)</font></b>", style_th),
            Paragraph("<b>General Procurement Tools<br/><font size=6 color='#64748B'>(GovWin IQ, Deltek)</font></b>", style_th)
        ],
        [
            Paragraph("<b>Clean Energy &amp; Grant Data Scope</b>", style_bullet_bold),
            Paragraph("<b>56,413 awards ($104.16B)</b> across 140+ federal &amp; state agencies (DOE, State Energy Offices, CEC, MassCEC, ARPA-E, NSF, USDA).", style_bullet),
            Paragraph("Private venture/PE transactions only; no coverage of non-dilutive state or federal grants.", style_bullet),
            Paragraph("General defense and IT procurement; negligible coverage of state clean energy grant programs.", style_bullet)
        ],
        [
            Paragraph("<b>Solicitation &amp; Compliance Extraction</b>", style_bullet_bold),
            Paragraph("Automated deconstruction of multi-volume FOAs into scoring rubrics, stage-gates, and submission compliance checklists.", style_bullet),
            Paragraph("Not supported; platform lacks grant solicitation and technical compliance analysis.", style_bullet),
            Paragraph("Basic procurement notices and metadata; lacks automated technical stage-gate extraction.", style_bullet)
        ],
        [
            Paragraph("<b>Teaming &amp; Consortia Discovery</b>", style_bullet_bold),
            Paragraph("Relational mapping across historical primes, university labs, national labs, and utility co-applicants with past award history.", style_bullet),
            Paragraph("Co-investor syndicates only; no research teaming, prime-sub relationships, or grant co-applicants.", style_bullet),
            Paragraph("Standard defense contractor listings; lacks clean tech and academic research teaming graphs.", style_bullet)
        ],
        [
            Paragraph("<b>Integrated Capital Continuum</b>", style_bullet_bold),
            Paragraph("Unified multi-stage records linking non-dilutive grants, SEC Form D equity, VC financings, DOE LPO debt, and patents.", style_bullet),
            Paragraph("Private equity financings only; disconnected from public funding history and grant match requirements.", style_bullet),
            Paragraph("Federal award totals only; no integration of private venture financing or patent records.", style_bullet)
        ],
        [
            Paragraph("<b>Program Manager &amp; Evaluator Directory</b>", style_bullet_bold),
            Paragraph("Directory of technical project officers, grant managers, and division leadership across 140+ energy funding bodies.", style_bullet),
            Paragraph("Corporate executives and venture partners only; no public agency points of contact.", style_bullet),
            Paragraph("General contracting officers; lacks clean energy and state program officer coverage.", style_bullet)
        ],
        [
            Paragraph("<b>Policy, Dockets &amp; Testbed Assets</b>", style_bullet_bold),
            Paragraph("Integrated state PUC regulatory dockets, FERC orders, IRA tax credit models, and DOE national lab facility directories.", style_bullet),
            Paragraph("General market news only; no regulatory docket tracking or national laboratory asset mapping.", style_bullet),
            Paragraph("Federal contracting records only; no state PUC proceeding tracking or lab testbed directories.", style_bullet)
        ],
        [
            Paragraph("<b>Institutional Export Deliverables</b>", style_bullet_bold),
            Paragraph("Publication-ready compliance blueprints, capital dossiers, and consortia evaluation matrices for client delivery.", style_bullet),
            Paragraph("Standard CSV exports and basic charting tools.", style_bullet),
            Paragraph("Spreadsheet tables and raw procurement attachments.", style_bullet)
        ]
    ]

    comp_table = Table(comp_data, colWidths=[95, 175, 135, 135])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_SUBTLE),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 6))

    # Data Architecture & Primary User Groups (2 Side-by-Side Cards)
    story.append(Paragraph("<b>DATA ARCHITECTURE &amp; INSTITUTIONAL APPLICATIONS</b>", style_h2))
    story.append(Spacer(1, 1))

    card_arch_content = (
        "<b>DATA PROVENANCE &amp; TAXONOMY</b><br/>"
        "&bull; <b>Primary Source Ingestion:</b> Continuous indexing across DOE (EERE, ARPA-E, OCED, FECM, LPO), Grants.gov, State Energy Offices, CEC EPIC, MassCEC, NSF, USDA, SEC EDGAR, USPTO, and state utility commissions.<br/>"
        "&bull; <b>24 Energy Tech Taxonomies:</b> Standardized categorization across Energy Storage, Advanced Nuclear, Clean Hydrogen, Carbon Capture, Grid Modernization, Industrial Decarbonization, Solar/Wind, and Building Thermal.<br/>"
        "&bull; <b>Entity Resolution Graph:</b> Multi-stage normalization resolving parent corporations, subsidiaries, university labs, and research institutions into unified entity profiles."
    )

    card_cases_content = (
        "<b>PRIMARY INSTITUTIONAL USE CASES</b><br/>"
        "&bull; <b>Grant &amp; Technical Consultancies:</b> Accelerate FOA compliance deconstruction, identify qualified prime/sub teaming partners, and verify non-federal cost-share alignment.<br/>"
        "&bull; <b>Clean Tech Project Developers:</b> Track active and forecasted funding windows, evaluate blended capital structures with IRA tax credits, and access national lab testing testbeds.<br/>"
        "&bull; <b>Corporate Strategy &amp; Investors:</b> Conduct rigorous due diligence on recipient funding histories, co-investor syndicates, technology transition milestones, and patent portfolios."
    )


    two_cards_data = [
        [
            Paragraph(card_arch_content, style_card_body),
            Paragraph(card_cases_content, style_card_body)
        ]
    ]
    two_cards_table = Table(two_cards_data, colWidths=[265, 265])
    two_cards_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (0,0), 0.5, BORDER_MID),
        ('BOX', (1,0), (1,0), 0.5, BORDER_MID),
        ('PADDING', (0,0), (-1,-1), 5.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(two_cards_table)
    story.append(Spacer(1, 6))

    # Institutional Contact Box
    contact_text = (
        "<b>Platform Verification &amp; Access:</b> Explore the live database at <b>terminal.aixenergy.io</b> &bull; "
        "<b>Direct Inquiries:</b> Brandon Owens &bull; <b>bowens@aixenergy.io</b>"
    )
    contact_table = Table([[Paragraph(contact_text, ParagraphStyle('ContactP', parent=style_body, alignment=1, fontSize=7.5, leading=10.5, textColor=NAVY))]], colWidths=[540])
    contact_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_SUBTLE),
        ('BOX', (0,0), (-1,-1), 1, CYAN),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(contact_table)

    doc.build(story, canvasmaker=CapabilitiesNumberedCanvas)
    return buffer.getvalue()


if __name__ == "__main__":
    pdf_bytes = build_capabilities_pdf()
    
    # Verify with PyMuPDF
    doc_fitz = fitz.open(stream=pdf_bytes, filetype="pdf")
    print(f"Generated PDF successfully. Total pages: {len(doc_fitz)}")
    
    # Save to outreach_attachments
    base_dir = r"c:\Users\Brandon Owens\Desktop\nyserda-innovation-match"
    outreach_dir = os.path.join(base_dir, "outreach_attachments")
    brain_dir = r"C:\Users\Brandon Owens\.gemini\antigravity\brain\0541b8c8-5f25-42ee-8a8f-c7c0dd4381b9"
    brain_scratch_dir = os.path.join(brain_dir, "scratch")
    curr_brain_dir = r"C:\Users\Brandon Owens\.gemini\antigravity\brain\a55aa85c-f9ee-464e-af13-053dc2987c51"

    target_dirs = [outreach_dir, curr_brain_dir]
    if os.path.exists(brain_dir):
        target_dirs.append(brain_dir)
    if os.path.exists(brain_scratch_dir):
        target_dirs.append(brain_scratch_dir)

    filenames = [
        "AIxEnergy_Terminal_Capabilities_Brief.pdf",
        "Energy_Innovation_Terminal_by_AIxEnergy_Capabilities.pdf",
        "Energy_Innovation_Terminal_by_AIxEnergy_Capabilities_Brief.pdf",
        "AIX_Energy_Terminal_Capabilities_Brief.pdf",
    ]
    
    for t_dir in target_dirs:
        for fname in filenames:
            p = os.path.join(t_dir, fname)
            with open(p, "wb") as f:
                f.write(pdf_bytes)
            print(f"Wrote {len(pdf_bytes):,} bytes to {p}")
