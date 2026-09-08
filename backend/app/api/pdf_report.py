"""PDF report generation for analysis results using the ReportLab publication engine."""
import io
import json
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import ProjectAnalysis, AnalysisMatch
from app.models.opportunity import Opportunity
from app.engine.project_pdf_report import generate_project_analysis_pdf
from app.engine.capital_stack_engine import calculate_capital_stack

router = APIRouter()


@router.get("/analyze/{analysis_id}/pdf")
def export_pdf(analysis_id: int, db: Session = Depends(get_db)):
    """Exports a publication-grade PDF summary report for a persisted project analysis."""
    analysis = db.query(ProjectAnalysis).get(analysis_id)
    if not analysis:
        raise HTTPException(404, "Analysis record not found")

    matches = db.query(AnalysisMatch).filter(AnalysisMatch.analysis_id == analysis_id).order_by(AnalysisMatch.fit_score.desc()).all()

    # Build structured data payload for the PDF builder
    structured_profile = {}
    if analysis.structured_profile:
        try:
            structured_profile = json.loads(analysis.structured_profile)
        except Exception:
            structured_profile = {}

    tech_areas = []
    if analysis.technology_areas:
        try: tech_areas = json.loads(analysis.technology_areas)
        except Exception: tech_areas = [analysis.technology_areas]

    activity_types = []
    if analysis.activity_types:
        try: activity_types = json.loads(analysis.activity_types)
        except Exception: activity_types = [analysis.activity_types]

    match_list = []
    for m in matches:
        opp = db.query(Opportunity).get(m.opportunity_id) if m.opportunity_id else None
        if opp:
            assessment = {}
            if m.assessment:
                try: assessment = json.loads(m.assessment)
                except Exception: assessment = {}
            match_list.append({
                "opportunity_id": opp.id,
                "name": opp.name,
                "agency": opp.agency,
                "solicitation_number": opp.solicitation_number,
                "match_score_pct": int((m.fit_score or 0.8) * 100),
                "fit_score": m.fit_score,
                "match_type": m.match_type or "strong",
                "max_per_award": opp.max_per_award,
                "total_funding": opp.total_funding,
                "next_deadline": opp.deadline.strftime("%m/%d/%Y") if opp.deadline else "Rolling",
                "why_it_fits": m.why_it_fits or assessment.get("verdict_detail", ""),
                "assessment": assessment,
            })

    # Compute Capital Stack
    cost_val = analysis.project_cost or structured_profile.get("estimated_cost") or 10_000_000.0
    top_grant = match_list[0].get("max_per_award") if match_list else None
    top_agency = match_list[0].get("agency") if match_list else "NYSERDA / DOE"
    top_sol = match_list[0].get("name") if match_list else "Clean Energy Grant"

    capital_stack = calculate_capital_stack(
        project_cost=float(cost_val),
        matched_grant_max=top_grant,
        technology_category=tech_areas[0] if tech_areas else "energy storage",
        solicitation_name=top_sol,
        agency=top_agency,
    )

    data_payload = {
        "analysis_id": analysis.id,
        "input_text": analysis.input_text,
        "summary": analysis.summary or structured_profile.get("summary") or analysis.input_text,
        "extracted_profile": {
            "project_title": structured_profile.get("project_title") or f"Project Analysis #{analysis.id}",
            "location": analysis.target_location or structured_profile.get("location") or "US / National",
            "applicant_type": analysis.applicant_type or structured_profile.get("applicant_type") or "Business / Commercial",
            "estimated_trl": analysis.estimated_trl or structured_profile.get("estimated_trl") or 5,
            "estimated_cost": float(cost_val),
            "timeline": analysis.project_timeline or structured_profile.get("timeline") or "2025–2028",
            "partners": structured_profile.get("partners", []),
            "technology_areas": tech_areas,
            "activity_types": activity_types,
        },
        "strong_matches": match_list[:10],
        "capital_stack": capital_stack,
    }

    output_buffer = io.BytesIO()
    generate_project_analysis_pdf(data_payload, output_buffer)
    pdf_bytes = output_buffer.getvalue()

    raw_title = structured_profile.get("project_title") or f"Project_{analysis.id}"
    clean_title = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in raw_title)[:40].strip('_')
    filename = f"{clean_title}_Match_and_Financing_Report.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
