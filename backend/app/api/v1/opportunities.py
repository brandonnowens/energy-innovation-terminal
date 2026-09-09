"""
V1 Canonical Opportunities Router.

Provides verified opportunity discovery, deep entity graph retrieval,
fit scoring, teaming assembly, and reviewer rubric generation.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import OpportunityRepository, AwardRepository
from app.engine.profile import ProjectProfile
from app.intelligence import (
    score_opportunity_fit,
    evaluate_win_rate,
    assemble_consortium_stack,
    generate_reviewer_rubric,
)

router = APIRouter(prefix="/opportunities", tags=["V1 Opportunities"])


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response Schemas
# ─────────────────────────────────────────────────────────────────────────────

class EvaluateFitInput(BaseModel):
    summary: str = Field(..., description="Project description")
    technology_areas: Optional[List[str]] = Field(default_factory=list)
    sectors: Optional[List[str]] = Field(default_factory=list)
    trl: Optional[int] = Field(None, ge=1, le=9)
    target_location: Optional[str] = None
    requested_funding: Optional[float] = None
    total_project_cost: Optional[float] = None


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("")
def search_opportunities(
    q: Optional[str] = Query(None, description="Keyword search query"),
    agency: Optional[str] = Query(None, description="Agency name filter"),
    status: Optional[str] = Query("open", description="open, closed, or all"),
    min_funding: Optional[float] = Query(None, ge=0),
    max_funding: Optional[float] = Query(None, ge=0),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search and filter clean energy funding opportunities using the canonical repository layer."""
    repo = OpportunityRepository(db)
    opps, total = repo.search_opportunities(
        query=q,
        agency=agency,
        status=status,
        min_funding=min_funding,
        max_funding=max_funding,
        limit=limit,
        offset=offset
    )

    results = []
    for o in opps:
        close_d = getattr(o, "close_date", None)
        sum_text = getattr(o, "short_description", None) or getattr(o, "description", None) or getattr(o, "summary", "") or ""
        results.append({
            "id": o.id,
            "solicitation_number": o.solicitation_number,
            "title": o.name,
            "agency": o.agency,
            "program_name": getattr(o, "program_name", None) or getattr(o, "solicitation_category", None),
            "status": o.status,
            "total_funding": o.total_funding,
            "award_ceiling": getattr(o, "max_per_award", None) or getattr(o, "award_ceiling", None),
            "award_floor": getattr(o, "award_min", None) or getattr(o, "award_floor", None),
            "cost_share_required": bool(getattr(o, "cost_share_pct", 0) or getattr(o, "cost_share_required", False)),
            "cost_share_percentage": getattr(o, "cost_share_pct", None),
            "close_date": close_d.isoformat() if close_d and hasattr(close_d, "isoformat") else None,
            "summary": str(sum_text)[:350],
            "rounds_count": len(getattr(o, "rounds", []) or []),
            "contacts_count": len(getattr(o, "contacts", []) or []),
        })

    return {
        "status": "success",
        "total": total,
        "count": len(results),
        "limit": limit,
        "offset": offset,
        "opportunities": results
    }


@router.get("/{opportunity_id}")
def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve complete opportunity record with eager-loaded rounds, contacts, documents, and restrictions."""
    repo = OpportunityRepository(db)
    opp = repo.get_by_id_eager(opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail=f"Opportunity {opportunity_id} not found")

    rel_d = getattr(opp, "release_date", None)
    cls_d = getattr(opp, "close_date", None)
    sum_full = getattr(opp, "description", None) or getattr(opp, "short_description", None) or getattr(opp, "summary", "")

    return {
        "status": "success",
        "opportunity": {
            "id": opp.id,
            "solicitation_number": opp.solicitation_number,
            "title": opp.name,
            "agency": opp.agency,
            "program_name": getattr(opp, "program_name", None) or getattr(opp, "solicitation_category", None),
            "status": opp.status,
            "total_funding": opp.total_funding,
            "award_ceiling": getattr(opp, "max_per_award", None) or getattr(opp, "award_ceiling", None),
            "award_floor": getattr(opp, "award_min", None) or getattr(opp, "award_floor", None),
            "cost_share_required": bool(getattr(opp, "cost_share_pct", 0) or getattr(opp, "cost_share_required", False)),
            "cost_share_percentage": getattr(opp, "cost_share_pct", None),
            "release_date": rel_d.isoformat() if rel_d and hasattr(rel_d, "isoformat") else None,
            "close_date": cls_d.isoformat() if cls_d and hasattr(cls_d, "isoformat") else None,
            "summary": sum_full,
            "eligibility_description": getattr(opp, "eligibility_description", None),
            "source_url": getattr(opp, "detail_page_url", None) or getattr(opp, "portal_url", None) or getattr(opp, "source_url", None),
            "categories": [
                {
                    "category_type": c.category_type,
                    "category_value": c.category_value
                }
                for c in (opp.categories or [])
            ],
            "rounds": [
                {
                    "id": r.id,
                    "round_number": r.round_number,
                    "title": r.title,
                    "due_date": r.due_date.isoformat() if r.due_date else None,
                    "allocated_funding": r.allocated_funding,
                    "status": r.status
                }
                for r in (opp.rounds or [])
            ],
            "contacts": [
                {
                    "id": c.id,
                    "name": c.name_display,
                    "title": c.title,
                    "email": c.email,
                    "role_type": c.role_type,
                    "institution": c.institution_name
                }
                for c in (opp.contacts or [])
            ],
            "documents": [
                {
                    "id": d.id,
                    "title": d.title,
                    "doc_type": d.doc_type,
                    "url": d.url,
                    "published_date": d.published_date.isoformat() if d.published_date else None
                }
                for d in (opp.documents or [])
            ],
            "restrictions": [
                {
                    "id": rx.id,
                    "restriction_type": rx.restriction_type,
                    "description": rx.description
                }
                for rx in (opp.restrictions or [])
            ]
        }
    }


@router.post("/{opportunity_id}/fit")
def evaluate_opportunity_fit(
    opportunity_id: int,
    payload: EvaluateFitInput,
    db: Session = Depends(get_db)
):
    """Evaluate multi-dimensional fit, empirical win rate, and competitiveness index for a specific opportunity."""
    repo = OpportunityRepository(db)
    opp = repo.get_by_id_eager(opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail=f"Opportunity {opportunity_id} not found")

    profile = ProjectProfile(
        project_title="Opportunity Candidate",
        summary=payload.summary,
        technology_areas=payload.technology_areas,
        sectors=payload.sectors,
        trl_start=payload.trl,
        target_location=payload.target_location,
        target_cost=payload.requested_funding,
        total_project_cost=payload.total_project_cost
    )

    fit_score = score_opportunity_fit(opp, profile)
    win_rate = evaluate_win_rate(
        db=db,
        opportunity=opp,
        profile=profile,
        fit_score=fit_score["overall_fit"],
        user_cost=payload.total_project_cost
    )

    return {
        "status": "success",
        "opportunity_id": opportunity_id,
        "fit_score": fit_score,
        "win_rate_analytics": win_rate
    }


@router.get("/{opportunity_id}/similar-awards")
def get_similar_awards(
    opportunity_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Find historical awards precedent awarded under this opportunity or related programs."""
    opp_repo = OpportunityRepository(db)
    opp = opp_repo.get_by_id(opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail=f"Opportunity {opportunity_id} not found")

    award_repo = AwardRepository(db)
    awards = award_repo.get_by_opportunity_id(opportunity_id, limit=limit)

    if not awards and opp.solicitation_number:
        awards = award_repo.get_by_solicitation_number(opp.solicitation_number, limit=limit)

    if not awards:
        # Fallback to agency + technology search
        awards, _ = award_repo.search_awards(
            agency=opp.agency,
            query=opp.name,
            limit=limit
        )

    return {
        "status": "success",
        "opportunity_id": opportunity_id,
        "precedent_awards_count": len(awards),
        "precedent_awards": [
            {
                "id": a.id,
                "recipient": a.recipient_name,
                "award_amount": a.award_amount,
                "award_date": a.award_date.isoformat() if a.award_date else None,
                "project_title": a.project_title,
                "agency": a.agency,
                "program_name": a.program_name
            }
            for a in awards
        ]
    }


@router.get("/{opportunity_id}/teaming")
def get_opportunity_teaming_stack(
    opportunity_id: int,
    technology_area: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Assemble recommended consortia partners (academic labs, utilities, national labs, startups)."""
    stack = assemble_consortium_stack(
        db=db,
        opportunity_id=opportunity_id,
        technology_area=technology_area,
        state_scope=state
    )
    return {
        "status": "success",
        "consortium_stack": stack
    }


@router.post("/{opportunity_id}/rubric")
def get_opportunity_reviewer_rubric(
    opportunity_id: int,
    payload: EvaluateFitInput,
    force_live_llm: bool = False,
    db: Session = Depends(get_db)
):
    """Generate a reverse-engineered reviewer rubric, scoring biases, and winning framing."""
    repo = OpportunityRepository(db)
    opp = repo.get_by_id_eager(opportunity_id)
    if not opp:
        raise HTTPException(status_code=404, detail=f"Opportunity {opportunity_id} not found")

    profile = ProjectProfile(
        project_title="Application",
        summary=payload.summary,
        technology_areas=payload.technology_areas,
        sectors=payload.sectors,
        trl_start=payload.trl,
        target_location=payload.target_location,
        target_cost=payload.requested_funding,
        total_project_cost=payload.total_project_cost
    )

    fit_score = score_opportunity_fit(opp, profile)
    rubric = generate_reviewer_rubric(
        db=db,
        profile=profile,
        opportunity=opp,
        match_score=fit_score["overall_fit"],
        force_live_llm=force_live_llm
    )

    return {
        "status": "success",
        "reviewer_rubric": rubric
    }
