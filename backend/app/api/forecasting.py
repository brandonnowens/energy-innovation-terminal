"""Predictive Solicitation Release Forecasting API router (Organization-Centric)."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.engine.profile import ProjectProfile
from app.engine.forecasting_radar import (
    get_predictive_solicitation_forecasts,
    get_forecasting_organization_directory,
    match_project_against_forecasts,
    synthesize_llm_projection_briefing,
    PROBABILISTIC_DISCLAIMER,
)

router = APIRouter()


class ProjectRadarMatchRequest(BaseModel):
    """Request to match a specific project profile against upcoming/unreleased solicitation forecasts."""
    project_title: Optional[str] = None
    summary: Optional[str] = None
    technology_areas: Optional[List[str]] = None
    activity_types: Optional[List[str]] = None
    sectors: Optional[List[str]] = None
    fuel_types: Optional[List[str]] = None
    estimated_trl: Optional[int] = None
    applicant_type: Optional[str] = None
    target_location: Optional[str] = None
    project_cost: Optional[float] = None
    max_results: Optional[int] = 10


class BriefingRequest(BaseModel):
    """Request for on-demand LLM strategic opportunity projection briefing."""
    organization_code: str
    custom_prompt: Optional[str] = None


@router.get("/organizations")
def get_forecasting_organizations(
    category: Optional[str] = Query(None, description="Filter by category: state, federal, utility, foundation, university, economic_development"),
    location: Optional[str] = Query(None, description="Filter by state or jurisdiction"),
    search: Optional[str] = Query(None, description="Search by organization name or tech"),
    db: Session = Depends(get_db)
):
    """
    Returns the complete directory of ALL 250 organizations in the database with upcoming
    and forecasted funding pipelines, categorized summaries, and total tracked capital envelopes.
    """
    orgs = get_forecasting_organization_directory(db)
    
    # Categorized summaries across all organizations
    categories: Dict[str, int] = {}
    locations: Dict[str, int] = {}
    for o in orgs:
        cat = o.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1
        st = o.get("state", "US")
        locations[st] = locations.get(st, 0) + 1

    # Filter directory if requested
    filtered_orgs = orgs
    if category and category.lower() != "all":
        filtered_orgs = [o for o in filtered_orgs if o.get("category", "").lower() == category.lower()]
    if location and location.lower() != "all":
        loc_low = location.lower()
        filtered_orgs = [
            o for o in filtered_orgs
            if loc_low in o.get("state", "").lower() or loc_low in o.get("jurisdiction", "").lower()
        ]
    if search and search.strip():
        q = search.strip().lower()
        filtered_orgs = [
            o for o in filtered_orgs
            if q in o.get("organization_name", "").lower()
            or q in o.get("full_name", "").lower()
            or q in o.get("primary_mandate", "").lower()
            or any(q in t.lower() for t in o.get("technologies_funded", []))
        ]

    total_pipeline = sum(o.get("total_pipeline_funding", 0) for o in orgs)

    return {
        "count": len(filtered_orgs),
        "total_directory_count": len(orgs),
        "total_tracked_pipeline": round(total_pipeline, 2),
        "organizations": filtered_orgs,
        "categories_summary": categories,
        "locations_summary": locations,
        "disclaimer": PROBABILISTIC_DISCLAIMER,
        "is_probabilistic_forecast": True,
    }


@router.get("/radar")
def get_forecasting_radar(
    organization: Optional[str] = Query(None, description="Filter by organization name or code"),
    agency: Optional[str] = Query(None, description="Alias for organization"),
    category: Optional[str] = Query(None, description="Filter by category: state, federal, utility, foundation, university, economic_development"),
    location: Optional[str] = Query(None, description="Filter by state / jurisdiction (e.g. NY, CA, MA, US)"),
    technology_area: Optional[str] = Query(None, description="Filter by technology area"),
    horizon: Optional[str] = Query(None, description="Filter by horizon: 30_days, 90_days, 2026, 2027"),
    conviction_tier: Optional[str] = Query(None, description="Filter by conviction tier (e.g. High Conviction, Anticipated)"),
    search: Optional[str] = Query(None, description="Free text keyword search"),
    limit: Optional[int] = Query(100, description="Max forecasts to return"),
    offset: Optional[int] = Query(0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    """
    Returns the intelligence early-warning radar of upcoming, recurring, and statutory funding solicitations
    across ALL database organizations, filtered by category, jurisdiction, or horizon.
    """
    target_org = organization or agency
    all_forecasts = get_predictive_solicitation_forecasts(
        db=db,
        org_name=target_org,
        agency=target_org,
        org_type=category,
        location=location,
        tech_area=technology_area,
        horizon=horizon,
        search=search,
        conviction_tier=conviction_tier,
    )
    
    total_count = len(all_forecasts)
    paginated_forecasts = all_forecasts[offset : offset + limit] if limit else all_forecasts

    return {
        "count": total_count,
        "returned_count": len(paginated_forecasts),
        "organization_filter": target_org,
        "category_filter": category,
        "location_filter": location,
        "horizon_filter": horizon,
        "forecasts": paginated_forecasts,
        "disclaimer": PROBABILISTIC_DISCLAIMER,
        "is_probabilistic_forecast": True,
    }


@router.get("/briefing/{org_code}")
def get_organization_briefing(
    org_code: str,
    prompt: Optional[str] = Query(None, description="Optional custom instructions for LLM synthesis"),
    db: Session = Depends(get_db),
):
    """
    Returns an in-depth probabilistic projection briefing for a specific organization,
    integrating historical cadence metrics, statutory drivers, and pre-positioning action steps.
    """
    result = synthesize_llm_projection_briefing(db=db, org_code=org_code, custom_prompt=prompt)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.post("/briefing")
def create_organization_briefing(
    req: BriefingRequest,
    db: Session = Depends(get_db),
):
    """POST endpoint to generate an on-demand LLM strategic opportunity projection briefing."""
    result = synthesize_llm_projection_briefing(db=db, org_code=req.organization_code, custom_prompt=req.custom_prompt)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.post("/project-radar")
def match_project_radar(
    req: ProjectRadarMatchRequest,
    db: Session = Depends(get_db),
):
    """
    Evaluates a specific clean energy project against all forecasted solicitations,
    returning high-confidence upcoming opportunities with strategic pre-positioning steps.
    """
    prof = ProjectProfile(
        project_title=req.project_title or "Clean Energy Innovation Project",
        summary=req.summary or "Clean energy infrastructure deployment project.",
        technology_areas=req.technology_areas or ["Clean Energy"],
        activity_types=req.activity_types or ["Demonstration"],
        sectors=req.sectors or ["Energy & Infrastructure"],
        fuel_types=req.fuel_types or ["Electricity"],
        estimated_trl=req.estimated_trl or 5,
        applicant_type=req.applicant_type or "Commercial Entity",
        target_location=req.target_location or "New York",
        project_cost=float(req.project_cost or 5_000_000.0),
    )

    matches = match_project_against_forecasts(db=db, profile=prof)
    if req.max_results:
        matches = matches[:req.max_results]
    return {
        "project_title": prof.project_title,
        "match_count": len(matches),
        "matched_forecasts": matches,
        "disclaimer": PROBABILISTIC_DISCLAIMER,
        "is_probabilistic_forecast": True,
    }


@router.get("/stats")
def get_forecasting_stats(db: Session = Depends(get_db)):
    """
    Provides aggregated intelligence summary across all forecasted pipeline programs
    and all 250 organizations in the database.
    """
    forecasts = get_predictive_solicitation_forecasts(db=db)
    orgs = get_forecasting_organization_directory(db)
    
    total_est_funding = sum(o.get("total_pipeline_funding", 0) for o in orgs)

    agencies: Dict[str, int] = {}
    horizons: Dict[str, int] = {}
    tech_areas: Dict[str, int] = {}
    categories: Dict[str, int] = {}

    for f in forecasts:
        ag = f.get("agency", "Unknown")
        agencies[ag] = agencies.get(ag, 0) + 1
        
        rel_win = f.get("forecasted_release_window", "2026/2027")
        horizons[rel_win] = horizons.get(rel_win, 0) + 1
        
        cat = f.get("organization_category", "state")
        categories[cat] = categories.get(cat, 0) + 1

        for ta in f.get("targeted_technologies", []):
            tech_areas[ta] = tech_areas.get(ta, 0) + 1

    return {
        "total_forecasts": len(forecasts),
        "total_organizations": len(orgs),
        "total_projected_funding": total_est_funding,
        "agency_distribution": agencies,
        "category_distribution": categories,
        "horizon_distribution": horizons,
        "technology_distribution": tech_areas,
        "disclaimer": PROBABILISTIC_DISCLAIMER,
        "is_probabilistic_forecast": True,
    }
