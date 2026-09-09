"""
V1 Canonical Organizations Router.

Provides funding agency, utility, and foundation lookups, historical funding analytics,
and Say-Yes propensity ranking.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.database import get_db
from app.repositories import OrganizationRepository, OpportunityRepository, AwardRepository
from app.models.opportunity import Opportunity
from app.models.award import Award
from app.engine.profile import ProjectProfile
from app.intelligence import (
    rank_funder_propensity,
    get_funding_organization_directory,
    generate_organization_forecast_briefing,
)

router = APIRouter(prefix="/organizations", tags=["V1 Organizations"])


class PropensityInput(BaseModel):
    project_title: Optional[str] = "Candidate Project"
    summary: str = Field(..., description="Project description")
    technology_areas: Optional[List[str]] = Field(default_factory=list)
    sectors: Optional[List[str]] = Field(default_factory=list)
    target_location: Optional[str] = "NY"
    limit: int = Field(25, ge=1, le=50)


@router.get("")
def list_organizations(
    q: Optional[str] = Query(None, description="Search query"),
    org_type: Optional[str] = Query(None, description="funder, utility, agency, foundation"),
    state: Optional[str] = Query(None, description="State abbreviation"),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search funding organizations, state energy offices, and utilities."""
    repo = OrganizationRepository(db)
    orgs = repo.search_organizations(query=q, org_type=org_type, state=state, limit=limit, offset=offset)

    return {
        "status": "success",
        "count": len(orgs),
        "organizations": [
            {
                "id": o.id,
                "code": o.code,
                "name": o.name,
                "org_type": o.org_type,
                "state": o.state,
                "geographic_scope": o.geographic_scope,
                "annual_budget": o.annual_budget,
                "clean_energy_allocation": o.clean_energy_allocation,
                "website": o.website_url
            }
            for o in orgs
        ]
    }


@router.get("/directory")
def get_forecasting_directory(db: Session = Depends(get_db)):
    """Retrieve full funding organization directory with cadence and regularity scores."""
    directory = get_funding_organization_directory(db)
    return {
        "status": "success",
        "count": len(directory),
        "directory": directory
    }


@router.get("/{organization_id}")
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve complete organization record and statutory mandates."""
    repo = OrganizationRepository(db)
    org = repo.get_by_id(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {organization_id} not found")

    return {
        "status": "success",
        "organization": {
            "id": org.id,
            "code": org.code,
            "name": org.name,
            "org_type": org.org_type,
            "state": org.state,
            "geographic_scope": org.geographic_scope,
            "statutory_mandates": org.primary_statutory_mandates,
            "annual_budget": org.annual_budget,
            "clean_energy_allocation": org.clean_energy_allocation,
            "website": org.website_url,
            "description": org.description
        }
    }


@router.get("/{organization_id}/funding-profile")
def get_organization_funding_profile(
    organization_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve historical funding analytics, average award amounts, and active solicitations."""
    org_repo = OrganizationRepository(db)
    org = org_repo.get_by_id(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {organization_id} not found")

    # Aggregate historical awards
    awards_query = db.query(Award).filter(
        or_(Award.agency.ilike(f"%{org.name}%"), Award.agency.ilike(f"%{org.code}%"))
    )
    total_awards = awards_query.count()
    total_amount = db.query(func.sum(Award.award_amount)).filter(
        or_(Award.agency.ilike(f"%{org.name}%"), Award.agency.ilike(f"%{org.code}%"))
    ).scalar() or 0.0

    avg_amount = (total_amount / total_awards) if total_awards > 0 else 0.0

    # Active opportunities
    opps_query = db.query(Opportunity).filter(
        or_(
            Opportunity.organization_id == org.id,
            Opportunity.agency.ilike(f"%{org.name}%"),
            Opportunity.agency.ilike(f"%{org.code}%")
        )
    )
    active_opps_count = opps_query.filter(Opportunity.status == "open").count()
    all_opps_count = opps_query.count()

    return {
        "status": "success",
        "organization_id": org.id,
        "organization_name": org.name,
        "total_historical_awards": total_awards,
        "total_historical_funding": total_amount,
        "average_award_amount": round(avg_amount, 2),
        "active_opportunities_count": active_opps_count,
        "total_solicitations_count": all_opps_count
    }


@router.get("/{organization_id_or_code}/forecast-briefing")
def get_forecast_briefing(
    organization_id_or_code: str,
    prompt: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generate strategic LLM opportunity forecast brief for an organization."""
    briefing = generate_organization_forecast_briefing(
        db=db,
        org_code=organization_id_or_code,
        custom_prompt=prompt
    )
    return briefing


@router.post("/rank-propensity")
def rank_organizations_propensity(
    payload: PropensityInput,
    db: Session = Depends(get_db)
):
    """Rank funding organizations and utility decision-makers by Say-Yes propensity score."""
    profile = ProjectProfile(
        project_title=payload.project_title,
        summary=payload.summary,
        technology_areas=payload.technology_areas,
        sectors=payload.sectors,
        target_location=payload.target_location
    )

    ranked_orgs = rank_funder_propensity(db=db, profile=profile, limit=payload.limit)

    return {
        "status": "success",
        "count": len(ranked_orgs),
        "organizations": ranked_orgs
    }
