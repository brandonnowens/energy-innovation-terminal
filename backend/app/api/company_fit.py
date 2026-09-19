from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.intelligence.opportunity_fit import create_project_profile, rank_opportunities_for_profile
from app.engine.company_fit_pdf import generate_company_fit_pdf

router = APIRouter(prefix="/company-fit", tags=["Company FOA Fit Snapshot"])

class CompanyFitRequest(BaseModel):
    company_name: Optional[str] = "Hardtech Energy Co."
    domain: Optional[str] = None
    description: str = Field(..., min_length=10)
    tech_tags: Optional[List[str]] = None
    trl: Optional[int] = Field(None, ge=1, le=9)
    applicant_type: Optional[str] = None
    location: Optional[str] = None


FOA_CLASS_MAP = {
    "DOE": "DOE-EERE",
    "ARPA-E": "ARPA-E",
    "LPO": "DOE-LPO",
    "NYSERDA": "NYSERDA",
    "CEC": "CEC",
    "MassCEC": "MassCEC",
    "NSF": "NSF",
    "SBIR": "SBIR/STTR",
}

def _classify_opp(opp) -> str:
    agency = (opp.agency or "").upper()
    sol = (opp.solicitation_number or "").upper()
    if "ARPA" in agency or "ARPA" in sol:
        return "ARPA-E"
    if "LPO" in agency or "LOAN" in agency:
        return "DOE-LPO"
    if "DOE" in agency or "EERE" in agency or "NETL" in agency or "OE" in agency:
        return "DOE-EERE"
    if "NYSERDA" in agency:
        return "NYSERDA"
    if "CEC" in agency:
        return "CEC"
    if "MASSCEC" in agency or "MASS CEC" in agency:
        return "MassCEC"
    if "NSF" in agency:
        return "NSF"
    if "SBIR" in sol or "STTR" in sol:
        return "SBIR/STTR"
    return "Other Federal/State"


def build_company_fit_snapshot(request: CompanyFitRequest, db: Session) -> dict:
    profile = create_project_profile(
        title=request.company_name,
        summary=request.description,
        technology_areas=request.tech_tags,
        trl_start=request.trl,
        applicant_type=request.applicant_type,
        target_location=request.location
    )

    ranked_items = rank_opportunities_for_profile(db, profile, limit=50)

    class_best_opps = {}
    for item in ranked_items:
        opp = item["opportunity"]
        score = item["score"]
        cls_label = _classify_opp(opp)
        if cls_label not in class_best_opps or score > class_best_opps[cls_label]["score"]:
            class_best_opps[cls_label] = {
                "score": score,
                "opportunity": opp,
                "fit_data": item["fit_score"]
            }

    sorted_classes = sorted(class_best_opps.items(), key=lambda x: x[1]["score"], reverse=True)
    
    top_foa_classes = []
    misfit_warnings = []

    for cls_label, data in sorted_classes:
        score = data["score"]
        opp = data["opportunity"]
        fit_data = data["fit_data"]
        
        if score > 0.35 and len(top_foa_classes) < 3:
            # window risk
            window_risk = "forecasted"
            due = getattr(opp, "close_date", None)
            due_str = None
            if due:
                due_str = due.isoformat()
                days = (due - datetime.utcnow()).days
                if days < 0:
                    window_risk = "closed"
                elif days <= 14:
                    window_risk = "closing_soon"
                elif days <= 90:
                    window_risk = "open"
                else:
                    window_risk = "forecasted"

            why_fit = fit_data.get("why_it_fits")
            if not why_fit:
                tech = ", ".join(request.tech_tags) if request.tech_tags else "clean technology"
                why_fit = f"Your {tech} aligns well with {cls_label}'s focus on {opp.short_description[:50]}..."
                
            top_foa_classes.append({
                "class_label": cls_label,
                "agency": opp.agency or "Agency",
                "agency_code": opp.agency_code or cls_label,
                "why_fit": why_fit,
                "fit_score": score,
                "window_risk": window_risk,
                "example_solicitations": [{
                    "id": opp.id,
                    "name": opp.name or "",
                    "solicitation_number": opp.solicitation_number or "",
                    "agency": opp.agency or "",
                    "status": opp.status or "",
                    "due_date": due_str,
                    "max_per_award": opp.max_per_award
                }]
            })
    # ── Misfit Warning Generation ─────────────────────────────────────────────
    # Always generate at least one misfit warning.
    # Strategy: find the lowest-scoring class that a company of this profile might
    # plausibly target (based on common wrong-class patterns), OR just use the lowest
    # scored class from the DB with a meaningful explanation.

    MISFIT_REASONS: dict[str, dict] = {
        "NYSERDA": {
            "trl_too_low": "NYSERDA's Clean Energy Fund targets TRL 5–8 demonstration projects with confirmed New York host sites. Early-stage R&D below TRL 5 is routed to ARPA-E or NSF, not NYSERDA.",
            "geo": "NYSERDA requires in-state New York deployment, employment, and economic benefit. Non-NY companies cannot satisfy geographic eligibility requirements without a formal NY operating entity.",
            "default": "NYSERDA prioritizes in-state New York economic impact, on-grid deployment, and utility integration. Federal deep-tech hardtech programs (DOE/ARPA-E) are a better match for early-stage or non-NY companies."
        },
        "CEC": {
            "geo": "California Energy Commission grants require California-based project sites and in-state workforce benefit. Out-of-state deployments do not qualify.",
            "default": "CEC's EPIC program targets California-specific grid and building challenges. Unless you have California-sited assets or utility interconnection, DOE federal programs offer broader eligibility."
        },
        "MassCEC": {
            "geo": "MassCEC's Catalyst Fund and Innovation Pathway targets Massachusetts-based companies and in-state demonstration sites. Out-of-state applicants are not eligible.",
            "default": "MassCEC focuses on Massachusetts in-state deployments and economic benefit. Federal pathways are more appropriate for companies without Massachusetts nexus."
        },
        "ARPA-E": {
            "trl_too_high": "ARPA-E funds transformational high-risk research, not commercial demonstrations. Projects at TRL 7+ with proven commercial pathways are not competitive — ARPA-E reviewers explicitly down-score \"incremental\" approaches.",
            "trl_too_low": "ARPA-E requires a clear technical pathway from current TRL to TRL 6+ within the project period. Basic science at TRL 1–2 without a defined engineering prototype path will fail pre-screening.",
            "default": "ARPA-E targets high-risk / high-reward paradigm shifts. If your technology has prior DOE validation or industry adoption, DOE-EERE demonstration programs offer higher probability of success."
        },
        "DOE-LPO": {
            "trl_too_low": "DOE Loan Programs Office (Title 17) requires commercial-scale or near-commercial projects at TRL 7–9. Early-stage R&D and pilot projects do not qualify — LPO is a project finance tool, not a grant.",
            "default": "DOE-LPO (Loan Programs Office) is not a grant program — it issues debt financing for commercial-scale projects. Applying before reaching commercial demonstration scale is premature and will not advance past initial screening."
        },
        "NSF": {
            "trl_too_high": "NSF SBIR/STTR focuses on fundamental and applied research at TRL 1–4. Commercial scale-up and demonstration projects above TRL 5 are outside NSF's statutory scope.",
            "default": "NSF programs fund fundamental research and early-stage innovation. If you are past prototype validation and pursuing commercial demonstration, DOE-EERE or state energy programs are more appropriate."
        },
        "SBIR/STTR": {
            "eligibility": "SBIR/STTR is restricted to small businesses (fewer than 500 employees) with primary US performance. Consortium leads, universities as prime applicants, and companies with foreign ownership restrictions are disqualified.",
            "default": "SBIR/STTR is competitive for early-stage R&D but has strict small business eligibility, phase size caps (Phase I: ~$200K, Phase II: ~$2M), and requires primary US performance. If your raise has strategic investor involvement, verify eligibility before applying."
        },
    }

    def _generate_misfit_reason(cls_label: str, score: float, opp_obj, req: CompanyFitRequest) -> dict:
        reasons = MISFIT_REASONS.get(cls_label, {})
        trl = req.trl or 5
        desc_lower = (req.description or "").lower()

        if cls_label in ("ARPA-E", "NSF") and trl >= 7:
            why = reasons.get("trl_too_high", reasons.get("default", ""))
            risk = "trl_mismatch"
        elif cls_label in ("DOE-LPO",) and trl <= 5:
            why = reasons.get("trl_too_low", reasons.get("default", ""))
            risk = "trl_mismatch"
        elif cls_label in ("NYSERDA", "CEC", "MassCEC") and req.location and not any(
            kw in (req.location or "").lower() for kw in ["new york", "ny", "california", "ca", "massachusetts", "ma"]
        ):
            why = reasons.get("geo", reasons.get("default", ""))
            risk = "geo_restriction"
        else:
            why = reasons.get("default", f"Your profile scored {score:.0%} against {cls_label} opportunities — the lowest match in our database. Applying here risks burning a full application cycle for likely non-competitive results.")
            risk = "scope_mismatch"

        if opp_obj:
            agency_name = opp_obj.agency or cls_label
        else:
            agency_name = cls_label

        return {
            "class_label": cls_label,
            "agency_code": cls_label,
            "agency": agency_name,
            "why_wrong": why,
            "risk_type": risk,
            "fit_score": score,
        }

    # Collect misfit candidates from sorted_classes: any class with score < 0.4
    # Prefer classes that have a defined MISFIT_REASONS entry (high signal)
    misfit_candidates = [
        (cls_label, data)
        for cls_label, data in sorted_classes
        if data["score"] < 0.40
    ]

    # Sort: prioritize known high-risk misfit classes first
    priority_misfits = [c for c in misfit_candidates if c[0] in MISFIT_REASONS]
    other_misfits = [c for c in misfit_candidates if c[0] not in MISFIT_REASONS]
    ordered_misfits = priority_misfits + other_misfits

    for cls_label, data in ordered_misfits[:2]:
        misfit_warnings.append(
            _generate_misfit_reason(cls_label, data["score"], data.get("opportunity"), request)
        )

    # If still no misfits (e.g. all classes scored well), generate a synthetic one
    # from the class with the lowest score that is NOT already in top_foa_classes
    if not misfit_warnings and sorted_classes:
        top_labels = {c["class_label"] for c in top_foa_classes}
        for cls_label, data in reversed(sorted_classes):
            if cls_label not in top_labels:
                misfit_warnings.append(
                    _generate_misfit_reason(cls_label, data["score"], data.get("opportunity"), request)
                )
                break

    # ── Recommended Next Action ────────────────────────────────────────────────
    recommended_action = "Review your top matched FOA classes and prepare a concise concept paper for the highest-fit program."
    if top_foa_classes:
        top_c = top_foa_classes[0]
        sol_num = top_c["example_solicitations"][0].get("solicitation_number", "") if top_c["example_solicitations"] else ""
        window = top_c.get("window_risk", "forecasted")
        window_str = {
            "closing_soon": "⚠ Closing within 14 days — act immediately",
            "open": "open now",
            "forecasted": "expected to open — get on agency mailing list now",
            "closed": "currently closed — track next cycle"
        }.get(window, "")
        if sol_num:
            recommended_action = (
                f"Priority: {top_c['class_label']} ({top_c['agency']}) — window is {window_str}. "
                f"Prepare a 2-page concept paper referencing {sol_num} and request a pre-application agency briefing."
            )
        else:
            recommended_action = (
                f"Priority: {top_c['class_label']} ({top_c['agency']}) — window is {window_str}. "
                f"Submit a 2-page concept paper and request a pre-application agency briefing to confirm eligibility before full proposal investment."
            )

    snapshot = {
        "company": {
            "name": request.company_name or "",
            "description": request.description,
            "tech_tags": request.tech_tags or [],
            "trl": request.trl,
            "applicant_type": request.applicant_type or "unknown"
        },
        "snapshot_date": datetime.utcnow().isoformat(),
        "top_foa_classes": top_foa_classes,
        "misfit_warnings": misfit_warnings[:2],
        "recommended_next_action": recommended_action,
        "generated_by": "Energy Innovation Terminal — https://terminal.aixenergy.io"
    }

    return snapshot


@router.post("")
def create_company_fit_snapshot(request: CompanyFitRequest, db: Session = Depends(get_db)):
    return build_company_fit_snapshot(request, db)

@router.get("/snapshot-pdf")
def get_company_fit_snapshot_pdf(
    description: str,
    company_name: Optional[str] = "Hardtech Energy Co.",
    domain: Optional[str] = None,
    tech_tags: Optional[str] = None,
    trl: Optional[int] = Query(None, ge=1, le=9),
    applicant_type: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    tags_list = None
    if tech_tags:
        tags_list = [t.strip() for t in tech_tags.split(",") if t.strip()]
        
    req = CompanyFitRequest(
        company_name=company_name,
        domain=domain,
        description=description,
        tech_tags=tags_list,
        trl=trl,
        applicant_type=applicant_type,
        location=location
    )
    snapshot = build_company_fit_snapshot(req, db)
    pdf_buffer = generate_company_fit_pdf(snapshot)
    
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="company_fit_snapshot.pdf"'
        }
    )
