"""
V1 Canonical Intelligence Router.

Centralizes analytical endpoints for ranking opportunities, capital stack optimization,
technology bankability evaluation, and predictive solicitation forecasting.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.engine.profile import ProjectProfile
from app.intelligence import (
    create_project_profile,
    rank_opportunities_for_profile,
    solve_capital_stack,
    evaluate_technology_bankability,
    forecast_upcoming_solicitations,
    get_agency_competition_benchmark,
    get_supported_technologies,
)

router = APIRouter(prefix="/intelligence", tags=["V1 Intelligence"])


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ProjectProfileInput(BaseModel):
    project_title: Optional[str] = "Candidate Project"
    summary: str = Field(..., description="Detailed description of the technology and project concept")
    technology_areas: Optional[List[str]] = Field(default_factory=list)
    sectors: Optional[List[str]] = Field(default_factory=list)
    trl_start: Optional[int] = Field(None, ge=1, le=9)
    trl_end: Optional[int] = Field(None, ge=1, le=9)
    target_location: Optional[str] = None
    target_cost: Optional[float] = None
    total_project_cost: Optional[float] = None
    applicant_type: Optional[str] = None
    status_filter: Optional[str] = "open"
    limit: Optional[int] = Field(20, ge=1, le=100)


class CapitalStackInput(BaseModel):
    total_project_cost: float = Field(..., gt=0, description="Total project CapEx in USD")
    grant_request: float = Field(..., ge=0, description="Requested non-dilutive grant amount in USD")
    technology_type: str = Field("energy_storage", description="Technology classification")
    location_state: str = Field("NY", description="Two-letter US state code")
    is_prevailing_wage_compliant: bool = True
    is_energy_community: bool = False
    is_domestic_content_compliant: bool = False
    senior_debt_share_pct: Optional[float] = None
    equity_cost_of_capital_pct: Optional[float] = None


class BankabilityInput(BaseModel):
    technology_name: str
    trl: int = Field(6, ge=1, le=9)
    pilot_operating_hours: int = Field(1500, ge=0)
    field_deployments_count: int = Field(3, ge=0)
    degradation_rate_pct_annual: float = Field(1.5, ge=0.0)
    has_tier1_warranty_backing: bool = False
    has_ul_iec_safety_certification: bool = True
    has_independent_engineer_report: bool = False
    offtake_contract_status: str = Field("signed_loi", description="no_contract, signed_loi, pilot_agreement, or binding_ppa_offtake")


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/rank-opportunities")
def rank_opportunities(
    input_data: ProjectProfileInput,
    db: Session = Depends(get_db)
):
    """
    Score and rank open funding opportunities against a candidate project profile
    using multi-dimensional fit scoring math (semantic, keyword, TRL, geographic, and funding alignment).
    """
    profile = create_project_profile(
        title=input_data.project_title,
        summary=input_data.summary,
        technology_areas=input_data.technology_areas,
        sectors=input_data.sectors,
        trl_start=input_data.trl_start,
        trl_end=input_data.trl_end,
        target_location=input_data.target_location,
        target_cost=input_data.target_cost,
        total_project_cost=input_data.total_project_cost,
        applicant_type=input_data.applicant_type,
    )

    ranked = rank_opportunities_for_profile(
        db=db,
        profile=profile,
        limit=input_data.limit,
        status_filter=input_data.status_filter
    )

    results = []
    for item in ranked:
        opp = item["opportunity"]
        close_d = getattr(opp, "close_date", None)
        sum_text = getattr(opp, "short_description", None) or getattr(opp, "description", None) or getattr(opp, "summary", "") or ""
        results.append({
            "opportunity_id": opp.id,
            "solicitation_number": opp.solicitation_number,
            "title": opp.name,
            "agency": opp.agency,
            "program_name": getattr(opp, "program_name", None) or getattr(opp, "solicitation_category", None),
            "status": opp.status,
            "total_funding": opp.total_funding,
            "award_ceiling": getattr(opp, "max_per_award", None) or getattr(opp, "award_ceiling", None),
            "award_floor": getattr(opp, "award_min", None) or getattr(opp, "award_floor", None),
            "cost_share_required": bool(getattr(opp, "cost_share_pct", 0) or getattr(opp, "cost_share_required", False)),
            "close_date": close_d.isoformat() if close_d and hasattr(close_d, "isoformat") else None,
            "overall_fit_score": item["fit_score"]["overall_fit"],
            "fit_breakdown": item["fit_score"]["breakdown"],
            "summary": str(sum_text)[:350]
        })

    return {
        "status": "success",
        "ranked_count": len(results),
        "results": results
    }


@router.post("/capital-stack")
def calculate_capital_stack(
    input_data: CapitalStackInput
):
    """
    Solve for an optimal non-dilutive capital stack blending grant funding,
    Title 26 IRA Section 48/45X ITC/PTC Direct Pay tax credits, and Green Bank concessionary debt.
    """
    stack = solve_capital_stack(
        total_project_cost=input_data.total_project_cost,
        grant_request=input_data.grant_request,
        technology_type=input_data.technology_type,
        location_state=input_data.location_state,
        is_prevailing_wage_compliant=input_data.is_prevailing_wage_compliant,
        is_energy_community=input_data.is_energy_community,
        is_domestic_content_compliant=input_data.is_domestic_content_compliant,
        senior_debt_share_pct=input_data.senior_debt_share_pct,
        equity_cost_of_capital_pct=input_data.equity_cost_of_capital_pct
    )
    return {
        "status": "success",
        "capital_stack": stack
    }


@router.get("/capital-stack/supported-technologies")
def list_supported_technologies():
    """Retrieve supported technology classifications for IRA tax credit modeling."""
    return {
        "technologies": get_supported_technologies()
    }


@router.post("/bankability")
def evaluate_bankability(
    input_data: BankabilityInput
):
    """
    Evaluate 4-Pillar Technology Bankability Rating (TBR), commercial readiness gaps,
    and required diligence milestones for project finance underwriting.
    """
    result = evaluate_technology_bankability(
        technology_name=input_data.technology_name,
        trl=input_data.trl,
        pilot_operating_hours=input_data.pilot_operating_hours,
        field_deployments_count=input_data.field_deployments_count,
        degradation_rate_pct_annual=input_data.degradation_rate_pct_annual,
        has_tier1_warranty_backing=input_data.has_tier1_warranty_backing,
        has_ul_iec_safety_certification=input_data.has_ul_iec_safety_certification,
        has_independent_engineer_report=input_data.has_independent_engineer_report,
        offtake_contract_status=input_data.offtake_contract_status
    )
    return {
        "status": "success",
        "bankability_evaluation": result
    }


@router.get("/forecasts")
def list_forecasts(
    org_name: Optional[str] = None,
    agency: Optional[str] = None,
    org_type: Optional[str] = None,
    location: Optional[str] = None,
    tech_area: Optional[str] = None,
    horizon: Optional[str] = None,
    search: Optional[str] = None,
    conviction_tier: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Query high-conviction unreleased, recurring, and anticipated solicitation forecasts
    across DOE, NYSERDA, CEC, EPA, utilities, and philanthropic funds.
    """
    forecasts = forecast_upcoming_solicitations(
        db=db,
        org_name=org_name,
        agency=agency,
        org_type=org_type,
        location=location,
        tech_area=tech_area,
        horizon=horizon,
        search=search,
        conviction_tier=conviction_tier
    )
    return {
        "status": "success",
        "count": len(forecasts),
        "forecasts": forecasts
    }


@router.get("/agency-benchmarks/{agency_name}")
def get_agency_benchmarks(agency_name: str):
    """Retrieve empirical historical competition benchmarks and field size metrics for a funding agency."""
    return {
        "status": "success",
        "benchmark": get_agency_competition_benchmark(agency_name)
    }
