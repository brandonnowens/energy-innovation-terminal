"""
Universal Legal Notice, Public Records Provenance & Protective Contributor Disclaimer.

Standardized legal language for all printable artifacts, PDF reports, and UI exports:
- Confirms information is compiled strictly from public open records.
- Provides comprehensive non-affiliation and non-endorsement protections for public sector employees and contributors.
- Protects researchers without mentioning personal names or specific state authorities.
"""

from typing import Dict, Any, Optional
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer

PUBLIC_RECORDS_NOTICE_SHORT = (
    "Compiled strictly from public open records · Clean Energy Research, LLC · Independent Research"
)

LEGAL_DISCLAIMER_FULL_TEXT = (
    "<b>PUBLIC RECORDS NOTICE &amp; LEGAL DISCLAIMER:</b> All opportunity data, award histories, regulatory filings, "
    "and analytical models presented in this document are compiled strictly from publicly available open government records, "
    "statutory disclosure portals, and official agency procurement feeds. This report is an independent research work "
    "and does NOT constitute an official publication, policy, endorsement, or evaluation of any federal, state, regional, "
    "or municipal government agency, public utility commission, or state energy authority. Contributing researchers, "
    "engineers, and analysts who may be employed by or affiliated with public sector entities, state authorities, or universities "
    "contribute strictly in an independent, personal research capacity; no content, methodologies, or data representations "
    "herein reflect the official positions, policies, findings, or endorsements of their respective employers or any governmental body. "
    "All information is provided 'as is' for informational and research purposes only without warranty of any kind. "
    "Prospective applicants must consult official RFP, PON, and FOA solicitation documents directly with issuing authorities."
)


def get_pdf_disclaimer_flowable(doc_width: float = 522.0, font_size: float = 5.5, leading: float = 7.0) -> Table:
    """Returns a styled ReportLab Table flowable containing the standard protective legal disclaimer."""
    style = ParagraphStyle(
        'UniversalLegalDisclaimer',
        fontName='Helvetica',
        fontSize=font_size,
        leading=leading,
        textColor=colors.HexColor('#475569')
    )
    
    p = Paragraph(LEGAL_DISCLAIMER_FULL_TEXT, style)
    t = Table([[p]], colWidths=[doc_width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return t
