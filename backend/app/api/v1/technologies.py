"""
V1 Canonical Technologies Router.

Provides clean technology market intelligence, funding momentum tracking,
and technology bankability evaluations.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc

from app.database import get_db
from app.models.award import Award
from app.models.opportunity import Opportunity
from app.intelligence import (
    evaluate_technology_bankability,
    get_supported_technologies,
)

router = APIRouter(prefix="/technologies", tags=["V1 Technologies"])


class TechnologyBankabilityInput(BaseModel):
    technology_name: str
    trl: int = Field(6, ge=1, le=9)
    pilot_operating_hours: int = Field(1500, ge=0)
    field_deployments_count: int = Field(3, ge=0)
    degradation_rate_pct_annual: float = Field(1.5, ge=0.0)
    has_tier1_warranty_backing: bool = False
    has_ul_iec_safety_certification: bool = True
    has_independent_engineer_report: bool = False
    offtake_contract_status: str = Field("signed_loi")


@router.get("")
def list_technologies():
    """Retrieve supported technology taxonomy domains and classifications."""
    return {
        "status": "success",
        "technologies": get_supported_technologies()
    }


@router.get("/{technology_name}/funding-momentum")
def get_technology_funding_momentum(
    technology_name: str,
    db: Session = Depends(get_db)
):
    """
    Analyze historical grant awards, funding trajectory, top funding agencies,
    and active solicitations for a specific clean energy technology.
    """
    tech_clean = technology_name.replace("-", " ").replace("_", " ").strip()

    # Query matching awards
    awards_query = db.query(Award).filter(
        or_(
            Award.project_title.ilike(f"%{tech_clean}%"),
            Award.program_name.ilike(f"%{tech_clean}%")
        )
    )
    total_awards = awards_query.count()
    total_funding = db.query(func.sum(Award.award_amount)).filter(
        or_(
            Award.project_title.ilike(f"%{tech_clean}%"),
            Award.program_name.ilike(f"%{tech_clean}%")
        )
    ).scalar() or 0.0

    # Top agencies
    agency_breakdown = (
        db.query(Award.agency, func.count(Award.id), func.sum(Award.award_amount))
        .filter(or_(Award.project_title.ilike(f"%{tech_clean}%"), Award.program_name.ilike(f"%{tech_clean}%")))
        .group_by(Award.agency)
        .order_by(desc(func.count(Award.id)))
        .limit(5)
        .all()
    )

    # Active opportunities
    active_opps = (
        db.query(Opportunity)
        .filter(
            Opportunity.status == "open",
            or_(
                Opportunity.name.ilike(f"%{tech_clean}%"),
                Opportunity.summary.ilike(f"%{tech_clean}%")
            )
        )
        .limit(10)
        .all()
    )

    return {
        "status": "success",
        "technology": tech_clean,
        "total_historical_awards": total_awards,
        "total_historical_funding": total_funding,
        "average_award_amount": round((total_funding / total_awards), 2) if total_awards > 0 else 0.0,
        "top_funding_agencies": [
            {
                "agency": r[0] or "Unknown Agency",
                "award_count": r[1],
                "total_amount": float(r[2] or 0.0)
            }
            for r in agency_breakdown
        ],
        "active_opportunities_count": len(active_opps),
        "active_opportunities": [
            {
                "id": o.id,
                "solicitation_number": o.solicitation_number,
                "title": o.name,
                "agency": o.agency,
                "total_funding": o.total_funding,
                "close_date": o.close_date.isoformat() if o.close_date else None
            }
            for o in active_opps
        ]
    }


@router.post("/bankability-evaluation")
def evaluate_tech_bankability(
    payload: TechnologyBankabilityInput
):
    """Calculate commercial bankability score and commercialization gap analysis."""
    result = evaluate_technology_bankability(
        technology_name=payload.technology_name,
        trl=payload.trl,
        pilot_operating_hours=payload.pilot_operating_hours,
        field_deployments_count=payload.field_deployments_count,
        degradation_rate_pct_annual=payload.degradation_rate_pct_annual,
        has_tier1_warranty_backing=payload.has_tier1_warranty_backing,
        has_ul_iec_safety_certification=payload.has_ul_iec_safety_certification,
        has_independent_engineer_report=payload.has_independent_engineer_report,
        offtake_contract_status=payload.offtake_contract_status
    )
    return {
        "status": "success",
        "bankability": result
    }
