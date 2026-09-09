"""
Canonical Agent Tools Layer.

Provides grounded, deterministic, analytical tool functions designed for autonomous AI agents
(OpenAI, Anthropic, Gemini, LangChain, CrewAI, AutoGen) with strict parameter validation,
auditable provenance, and standard schema manifests.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc

from app.repositories import (
    OpportunityRepository,
    AwardRepository,
    OrganizationRepository,
    RecipientRepository,
    ProgramRepository,
)
from app.models.opportunity import Opportunity
from app.models.organization import Organization
from app.models.award import Award
from app.engine.profile import ProjectProfile
from app.intelligence.opportunity_fit import score_opportunity_fit, rank_opportunities_for_profile
from app.intelligence.capital_stack import solve_capital_stack
from app.intelligence.bankability import evaluate_technology_bankability
from app.intelligence.win_rate import evaluate_win_rate
from app.intelligence.teaming import assemble_consortium_stack
from app.intelligence.forecasting import forecast_upcoming_solicitations
from app.intelligence.propensity import rank_funder_propensity
from app.intelligence.reviewer_rubric import generate_reviewer_rubric

logger = logging.getLogger("AgentTools")


# ─────────────────────────────────────────────────────────────────────────────
# Core Grounded Agent Tool Functions
# ─────────────────────────────────────────────────────────────────────────────

def search_opportunities_tool(
    db: Session,
    query: Optional[str] = None,
    agency: Optional[str] = None,
    status: Optional[str] = "open",
    min_funding: Optional[float] = None,
    max_funding: Optional[float] = None,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """Search solicitations across federal, state, and utility programs with criteria filters."""
    repo = OpportunityRepository(db)
    opps, total = repo.search_opportunities(
        query=query,
        agency=agency,
        status=status,
        min_funding=min_funding,
        max_funding=max_funding,
        limit=min(limit, 50),
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
            "close_date": close_d.isoformat() if close_d and hasattr(close_d, "isoformat") else None,
            "summary": str(sum_text)[:300]
        })
    return {
        "total_matches": total,
        "count": len(results),
        "results": results
    }


def get_opportunity_details_tool(
    db: Session,
    opportunity_id: int
) -> Dict[str, Any]:
    """Retrieve complete verified opportunity record including rounds, contacts, documents, and restrictions."""
    repo = OpportunityRepository(db)
    opp = repo.get_by_id_eager(opportunity_id)
    if not opp:
        return {"error": f"Opportunity with ID {opportunity_id} not found"}

    cls_d = getattr(opp, "close_date", None)
    sum_full = getattr(opp, "description", None) or getattr(opp, "short_description", None) or getattr(opp, "summary", "")

    return {
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
        "close_date": cls_d.isoformat() if cls_d and hasattr(cls_d, "isoformat") else None,
        "summary": sum_full,
        "eligibility_description": getattr(opp, "eligibility_description", None),
        "source_url": getattr(opp, "detail_page_url", None) or getattr(opp, "portal_url", None) or getattr(opp, "source_url", None),
        "rounds": [
            {
                "round_number": r.round_number,
                "round_title": r.title,
                "due_date": r.due_date.isoformat() if r.due_date else None,
                "round_budget": r.allocated_funding,
            }
            for r in (opp.rounds or [])
        ],
        "contacts": [
            {
                "name": c.name_display,
                "title": c.title,
                "email": c.email,
                "role": c.role_type
            }
            for c in (opp.contacts or [])
        ],
        "documents": [
            {
                "title": d.title,
                "doc_type": d.doc_type,
                "url": d.url
            }
            for d in (opp.documents or [])
        ]
    }


def get_organization_profile_tool(
    db: Session,
    org_id_or_code: str
) -> Dict[str, Any]:
    """Retrieve comprehensive profile for a funding agency, utility, or philanthropic fund."""
    repo = OrganizationRepository(db)
    org = None
    if org_id_or_code.isdigit():
        org = repo.get_by_id(int(org_id_or_code))
    if not org:
        org = repo.get_by_code(org_id_or_code)
    if not org:
        matches = repo.search_organizations(query=org_id_or_code, limit=1)
        if matches:
            org = matches[0]

    if not org:
        return {"error": f"Organization '{org_id_or_code}' not found"}

    # Count historical solicitations and awards
    opp_repo = OpportunityRepository(db)
    award_repo = AwardRepository(db)
    opp_count = db.query(func.count(Opportunity.id)).filter(
        or_(Opportunity.organization_id == org.id, Opportunity.agency.ilike(f"%{org.name}%"))
    ).scalar() or 0
    award_count = db.query(func.count(Award.id)).filter(
        Award.agency.ilike(f"%{org.name}%")
    ).scalar() or 0

    return {
        "id": org.id,
        "code": org.code,
        "name": org.name,
        "org_type": org.org_type,
        "state": org.state,
        "geographic_scope": org.geographic_scope,
        "statutory_mandates": org.primary_statutory_mandates,
        "annual_budget": org.annual_budget,
        "clean_energy_allocation": org.clean_energy_allocation,
        "historical_solicitations_count": opp_count,
        "historical_awards_count": award_count,
        "website": org.website_url
    }


def rank_opportunities_tool(
    db: Session,
    summary: str,
    technology_areas: Optional[List[str]] = None,
    sectors: Optional[List[str]] = None,
    trl: Optional[int] = None,
    target_location: Optional[str] = None,
    requested_funding: Optional[float] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """Rank open solicitations against a proposed project profile using multi-dimensional fit math."""
    profile = ProjectProfile(
        project_title="Candidate Project",
        summary=summary,
        technology_areas=technology_areas or [],
        sectors=sectors or [],
        trl_start=trl,
        trl_end=trl + 1 if trl else None,
        target_location=target_location,
        target_cost=requested_funding,
        total_project_cost=requested_funding,
    )

    ranked = rank_opportunities_for_profile(
        db=db,
        profile=profile,
        limit=min(limit, 25),
        status_filter="open"
    )

    return {
        "ranked_count": len(ranked),
        "results": [
            {
                "id": item["opportunity"].id,
                "solicitation_number": item["opportunity"].solicitation_number,
                "title": item["opportunity"].name,
                "agency": item["opportunity"].agency,
                "overall_fit_score": item["fit_score"]["overall_fit"],
                "fit_breakdown": item["fit_score"]["breakdown"],
                "total_funding": item["opportunity"].total_funding,
                "close_date": item["opportunity"].close_date.isoformat() if item["opportunity"].close_date else None,
                "summary": (item["opportunity"].summary or "")[:250]
            }
            for item in ranked
        ]
    }


def analyze_funding_history_tool(
    db: Session,
    technology_keyword: Optional[str] = None,
    agency: Optional[str] = None,
    recipient_name: Optional[str] = None,
    state: Optional[str] = None,
    min_year: Optional[int] = 2020,
    limit: int = 15
) -> Dict[str, Any]:
    """Analyze historical grant awards grounded in the database of 54,000+ historical awards."""
    repo = AwardRepository(db)
    awards, total = repo.search_awards(
        query=technology_keyword,
        agency=agency,
        recipient_name=recipient_name,
        state=state,
        min_year=min_year,
        limit=min(limit, 50)
    )

    # Compute quick aggregates
    total_awarded = sum(float(a.award_amount or 0) for a in awards)
    avg_award = (total_awarded / len(awards)) if awards else 0

    return {
        "total_historical_matches": total,
        "sample_size": len(awards),
        "sample_total_funding": total_awarded,
        "sample_average_award": round(avg_award, 2),
        "awards": [
            {
                "id": a.id,
                "recipient": a.recipient_name,
                "agency": a.agency,
                "program": a.program_name,
                "award_amount": a.award_amount,
                "award_date": a.award_date.isoformat() if a.award_date else None,
                "project_title": a.project_title,
                "state": a.state,
                "solicitation_number": a.solicitation_number
            }
            for a in awards
        ]
    }


def solve_capital_stack_tool(
    db: Session,
    total_project_cost: float,
    grant_request: float,
    technology_type: str = "energy_storage",
    location_state: str = "NY",
    is_prevailing_wage_compliant: bool = True,
    is_energy_community: bool = False,
    is_domestic_content_compliant: bool = False
) -> Dict[str, Any]:
    """Calculate blended non-dilutive capital stack with Title 26 IRA tax credits and Green Bank leverage."""
    return solve_capital_stack(
        total_project_cost=total_project_cost,
        grant_request=grant_request,
        technology_type=technology_type,
        location_state=location_state,
        is_prevailing_wage_compliant=is_prevailing_wage_compliant,
        is_energy_community=is_energy_community,
        is_domestic_content_compliant=is_domestic_content_compliant
    )


def evaluate_technology_bankability_tool(
    db: Session,
    technology_name: str,
    trl: int = 6,
    pilot_operating_hours: int = 1500,
    field_deployments_count: int = 3,
    degradation_rate_pct_annual: float = 1.5,
    has_tier1_warranty_backing: bool = False,
    has_ul_iec_safety_certification: bool = True,
    has_independent_engineer_report: bool = False,
    offtake_contract_status: str = "signed_loi"
) -> Dict[str, Any]:
    """Evaluate commercial bankability rating across technical de-risking, warranty backing, and revenue certainty."""
    return evaluate_technology_bankability(
        technology_name=technology_name,
        trl=trl,
        pilot_operating_hours=pilot_operating_hours,
        field_deployments_count=field_deployments_count,
        degradation_rate_pct_annual=degradation_rate_pct_annual,
        has_tier1_warranty_backing=has_tier1_warranty_backing,
        has_ul_iec_safety_certification=has_ul_iec_safety_certification,
        has_independent_engineer_report=has_independent_engineer_report,
        offtake_contract_status=offtake_contract_status
    )


def assemble_teaming_consortia_tool(
    db: Session,
    opportunity_id: Optional[int] = None,
    technology_area: Optional[str] = None,
    state_scope: Optional[str] = None
) -> Dict[str, Any]:
    """Recommend optimal consortia teaming partners (universities, national labs, utilities, startups)."""
    return assemble_consortium_stack(
        db=db,
        opportunity_id=opportunity_id,
        technology_area=technology_area,
        state_scope=state_scope
    )


def generate_strategic_plan_tool(
    db: Session,
    project_summary: str,
    technology_area: str,
    target_opportunity_id: int,
    total_project_cost: float = 2000000.0,
    requested_grant: float = 1000000.0,
    trl: int = 6
) -> Dict[str, Any]:
    """Generate an end-to-end strategic proposal architecture for a specific opportunity."""
    repo = OpportunityRepository(db)
    opp = repo.get_by_id_eager(target_opportunity_id)
    if not opp:
        return {"error": f"Opportunity {target_opportunity_id} not found"}

    profile = ProjectProfile(
        project_title="Strategic Application",
        summary=project_summary,
        technology_areas=[technology_area],
        trl_start=trl,
        target_cost=requested_grant,
        total_project_cost=total_project_cost
    )

    fit_result = score_opportunity_fit(opp, profile)
    win_rate_res = evaluate_win_rate(db, opp, profile, fit_score=fit_result["overall_fit"], user_cost=total_project_cost)
    rubric_res = generate_reviewer_rubric(db, profile, opp, match_score=fit_result["overall_fit"])
    cap_stack_res = solve_capital_stack(total_project_cost=total_project_cost, grant_request=requested_grant, technology_type=technology_area)
    teaming_res = assemble_consortium_stack(db, opportunity_id=opp.id, technology_area=technology_area)

    return {
        "opportunity": {
            "id": opp.id,
            "solicitation_number": opp.solicitation_number,
            "title": opp.name,
            "agency": opp.agency,
            "total_funding": opp.total_funding,
            "close_date": opp.close_date.isoformat() if opp.close_date else None
        },
        "fit_evaluation": fit_result,
        "win_rate_competitiveness": win_rate_res,
        "capital_stack_optimization": cap_stack_res,
        "winning_angle_and_rubric": rubric_res,
        "teaming_recommendations": teaming_res
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool Manifest (OpenAI / Anthropic Function Calling Specification)
# ─────────────────────────────────────────────────────────────────────────────

AGENT_TOOLS_MANIFEST: List[Dict[str, Any]] = [
    {
        "name": "search_opportunities",
        "description": "Search clean energy funding solicitations and grants across DOE, NYSERDA, CEC, EPA, NSF, and state agencies.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Free text search terms (e.g., 'iron flow battery long duration storage')"},
                "agency": {"type": "string", "description": "Agency name filter (e.g. 'DOE', 'NYSERDA', 'CEC')"},
                "status": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
                "min_funding": {"type": "number", "description": "Minimum award ceiling / budget"},
                "max_funding": {"type": "number", "description": "Maximum award ceiling / budget"},
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "get_opportunity_details",
        "description": "Retrieve comprehensive details for a specific funding opportunity by ID, including rounds, contacts, and eligibility.",
        "parameters": {
            "type": "object",
            "properties": {
                "opportunity_id": {"type": "integer", "description": "The unique integer ID of the opportunity"}
            },
            "required": ["opportunity_id"]
        }
    },
    {
        "name": "get_organization_profile",
        "description": "Retrieve profile, statutory mandates, clean energy budget, and historical metrics for a funding organization.",
        "parameters": {
            "type": "object",
            "properties": {
                "org_id_or_code": {"type": "string", "description": "Organization code (e.g., 'NYSERDA', 'ARPA-E', 'CONED') or database ID"}
            },
            "required": ["org_id_or_code"]
        }
    },
    {
        "name": "rank_opportunities",
        "description": "Evaluate and rank open funding solicitations against a project's technology, sector, TRL, and funding needs.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Technical description of the proposed project or innovation"},
                "technology_areas": {"type": "array", "items": {"type": "string"}, "description": "List of technology domains"},
                "sectors": {"type": "array", "items": {"type": "string"}, "description": "Target commercial sectors"},
                "trl": {"type": "integer", "description": "Current Technology Readiness Level (1-9)"},
                "target_location": {"type": "string", "description": "Geographic jurisdiction (e.g., 'NY', 'CA', 'National')"},
                "requested_funding": {"type": "number", "description": "Desired grant amount in USD"},
                "limit": {"type": "integer", "default": 10}
            },
            "required": ["summary"]
        }
    },
    {
        "name": "analyze_funding_history",
        "description": "Query 54,000+ historical grant awards to identify precedent award sizes, recipient patterns, and agency funding trends.",
        "parameters": {
            "type": "object",
            "properties": {
                "technology_keyword": {"type": "string", "description": "Technology domain (e.g. 'hydrogen', 'microgrid', 'heat pump')"},
                "agency": {"type": "string", "description": "Awarding agency"},
                "recipient_name": {"type": "string", "description": "Recipient company or university"},
                "state": {"type": "string", "description": "Two-letter US state code"},
                "min_year": {"type": "integer", "default": 2020},
                "limit": {"type": "integer", "default": 15}
            }
        }
    },
    {
        "name": "solve_capital_stack",
        "description": "Calculate non-dilutive capital stack blending grant funding with Title 26 IRA 48/45X ITC/PTC Direct Pay tax credits and Green Bank loans.",
        "parameters": {
            "type": "object",
            "properties": {
                "total_project_cost": {"type": "number", "description": "Total CapEx project cost in USD"},
                "grant_request": {"type": "number", "description": "Requested non-dilutive grant amount in USD"},
                "technology_type": {"type": "string", "description": "Technology classification (e.g., 'energy_storage', 'solar', 'hydrogen', 'geothermal')"},
                "location_state": {"type": "string", "default": "NY"},
                "is_prevailing_wage_compliant": {"type": "boolean", "default": True},
                "is_energy_community": {"type": "boolean", "default": False},
                "is_domestic_content_compliant": {"type": "boolean", "default": False}
            },
            "required": ["total_project_cost", "grant_request"]
        }
    },
    {
        "name": "evaluate_technology_bankability",
        "description": "Calculate a 4-Pillar Technology Bankability Rating (TBR) and identify commercialization gaps for clean tech assets.",
        "parameters": {
            "type": "object",
            "properties": {
                "technology_name": {"type": "string", "description": "Name or classification of the technology"},
                "trl": {"type": "integer", "default": 6},
                "pilot_operating_hours": {"type": "integer", "default": 1500},
                "field_deployments_count": {"type": "integer", "default": 3},
                "degradation_rate_pct_annual": {"type": "number", "default": 1.5},
                "has_tier1_warranty_backing": {"type": "boolean", "default": False},
                "has_ul_iec_safety_certification": {"type": "boolean", "default": True},
                "has_independent_engineer_report": {"type": "boolean", "default": False},
                "offtake_contract_status": {"type": "string", "enum": ["no_contract", "signed_loi", "pilot_agreement", "binding_ppa_offtake"], "default": "signed_loi"}
            },

            "required": ["technology_name"]
        }
    },
    {
        "name": "assemble_teaming_consortia",
        "description": "Identify optimal academic labs, utilities, national labs, and small business partners for an opportunity.",
        "parameters": {
            "type": "object",
            "properties": {
                "opportunity_id": {"type": "integer", "description": "Opportunity ID"},
                "technology_area": {"type": "string", "description": "Technology focus domain"},
                "state_scope": {"type": "string", "description": "Target state"}
            }
        }
    },
    {
        "name": "generate_strategic_plan",
        "description": "Generate an end-to-end strategic proposal architecture combining fit scoring, win rate, capital stack, and reviewer rubric.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_summary": {"type": "string", "description": "Detailed project description"},
                "technology_area": {"type": "string", "description": "Primary technology area"},
                "target_opportunity_id": {"type": "integer", "description": "Target opportunity ID"},
                "total_project_cost": {"type": "number", "default": 2000000.0},
                "requested_grant": {"type": "number", "default": 1000000.0},
                "trl": {"type": "integer", "default": 6}
            },
            "required": ["project_summary", "technology_area", "target_opportunity_id"]
        }
    }
]


def get_agent_tools_manifest() -> List[Dict[str, Any]]:
    """Returns the JSON Schema specification for all grounded agent tools."""
    return AGENT_TOOLS_MANIFEST


TOOL_REGISTRY = {
    "search_opportunities": search_opportunities_tool,
    "get_opportunity_details": get_opportunity_details_tool,
    "get_organization_profile": get_organization_profile_tool,
    "rank_opportunities": rank_opportunities_tool,
    "analyze_funding_history": analyze_funding_history_tool,
    "solve_capital_stack": solve_capital_stack_tool,
    "evaluate_technology_bankability": evaluate_technology_bankability_tool,
    "assemble_teaming_consortia": assemble_teaming_consortia_tool,
    "generate_strategic_plan": generate_strategic_plan_tool,
}


def execute_agent_tool(tool_name: str, arguments: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Execute a registered agent tool with runtime parameter injection and error handling."""
    func = TOOL_REGISTRY.get(tool_name)
    if not func:
        return {
            "error": f"Tool '{tool_name}' is not recognized in the canonical agent registry.",
            "available_tools": list(TOOL_REGISTRY.keys())
        }

    try:
        return func(db=db, **arguments)
    except TypeError as te:
        logger.warning(f"Invalid arguments for tool '{tool_name}': {te}")
        return {"error": f"Invalid arguments for tool '{tool_name}': {str(te)}"}
    except Exception as e:
        logger.error(f"Error executing agent tool '{tool_name}': {e}")
        return {"error": f"Execution error in tool '{tool_name}': {str(e)}"}
