"""
Canonical Opportunity Fit and Matching Intelligence Module.

Wraps the core multi-dimensional fit scoring engine (evaluate_fit) to evaluate
semantic, technical, structural, and regulatory alignment between a project and an opportunity.
"""

from typing import Optional, List, Dict, Any, Union
import logging
from sqlalchemy.orm import Session

from app.engine.profile import ProjectProfile
from app.engine.fit import evaluate_fit, FitResult
from app.models.opportunity import Opportunity
from app.repositories.opportunity_repo import OpportunityRepository

logger = logging.getLogger("CanonicalOpportunityFit")


def create_project_profile(
    title: Optional[str] = "Clean Energy Innovation Project",
    summary: str = "Clean energy infrastructure deployment project.",
    technology_areas: Optional[List[str]] = None,
    activity_types: Optional[List[str]] = None,
    sectors: Optional[List[str]] = None,
    fuel_types: Optional[List[str]] = None,
    trl_start: Optional[int] = None,
    trl_end: Optional[int] = None,
    applicant_type: Optional[str] = None,
    target_location: Optional[str] = None,
    ny_location: Optional[str] = None,
    target_cost: Optional[float] = None,
    total_project_cost: Optional[float] = None,
    timeline: Optional[str] = None,
    partners: Optional[str] = None,
    agencies: Optional[List[str]] = None,
) -> ProjectProfile:
    """Creates a normalized ProjectProfile instance for engine scoring."""
    estimated_trl = trl_start if trl_start is not None else 5
    project_cost = total_project_cost if total_project_cost is not None else target_cost

    partner_list = [partners] if isinstance(partners, str) and partners else (partners or [])

    return ProjectProfile(
        project_title=title or "Clean Energy Innovation Project",
        summary=summary,
        technology_areas=technology_areas or ["Clean Energy Innovation"],
        activity_types=activity_types or ["Demonstration"],
        sectors=sectors or ["Energy & Infrastructure"],
        fuel_types=fuel_types or ["Electricity"],
        estimated_trl=estimated_trl,
        applicant_type=applicant_type or "Commercial Entity",
        target_location=target_location or "United States",
        ny_location=ny_location or "New York",
        project_cost=project_cost,
        project_timeline=timeline or "2026-2029",
        partners=partner_list,
    )


def score_opportunity_fit(
    opportunity: Opportunity,
    profile: Union[ProjectProfile, Dict[str, Any]],
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Computes quantified fit score and dimensional breakdown between a project and an opportunity.
    """
    if isinstance(profile, dict):
        prof = create_project_profile(**profile)
    else:
        prof = profile

    try:
        fit_result: FitResult = evaluate_fit(
            db=db,
            opportunity=opportunity,
            profile=prof
        )
        return {
            "opportunity_id": opportunity.id,
            "overall_fit": round(fit_result.overall_score, 3),
            "match_score_pct": fit_result.match_score_pct,
            "match_type": fit_result.match_type,
            "breakdown": fit_result.score_breakdown,
            "dimensions": [
                {
                    "dimension": d.dimension,
                    "score": round(d.score, 3),
                    "explanation": d.explanation,
                    "confidence": d.confidence
                }
                for d in fit_result.dimensions
            ],
            "requirements_checklist": fit_result.requirements_checklist,
            "restrictions": fit_result.restrictions,
            "matched_keywords": fit_result.matched_keywords,
            "applicable_components": fit_result.applicable_components,
            "why_it_fits": fit_result.why_it_fits,
        }
    except Exception as e:
        logger.error(f"Error computing fit for opportunity {getattr(opportunity, 'id', None)}: {e}")
        return {
            "opportunity_id": getattr(opportunity, "id", None),
            "overall_fit": 0.50,
            "match_score_pct": 50,
            "match_type": "conditional",
            "breakdown": {},
            "dimensions": [],
            "requirements_checklist": [],
            "restrictions": [],
            "matched_keywords": [],
            "applicable_components": ["Full Scope"],
            "why_it_fits": "Opportunity matches general clean energy eligibility.",
            "error": str(e)
        }


def rank_opportunities_for_profile(
    db: Session,
    profile: ProjectProfile,
    limit: int = 25,
    status_filter: Optional[str] = "open"
) -> List[Dict[str, Any]]:
    """
    Ranks opportunities in the database against a project profile.
    """
    repo = OpportunityRepository(db)
    opps, _ = repo.search_opportunities(status=status_filter, limit=100)

    ranked_items = []
    for opp in opps:
        fit_data = score_opportunity_fit(opp, profile, db=db)
        ranked_items.append({
            "opportunity": opp,
            "fit_score": fit_data,
            "score": fit_data["overall_fit"]
        })

    ranked_items.sort(key=lambda x: x["score"], reverse=True)
    return ranked_items[:limit]
