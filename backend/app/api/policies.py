"""
Policy, Regulatory, Codes & Standards API Router.
Provides structured access, PostgreSQL full-text search, multi-hop technology linkages,
and regulatory compliance matrices for energy innovation.
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func, or_, and_, desc
from pydantic import BaseModel

from app.database import get_db
from app.models.policy import (
    PolicyStandard,
    PolicyTechnologyLink,
    PolicyFuelLink,
    PolicyOpportunityLink,
    PolicyOrganizationLink,
    RegulatoryProceeding,
    ProceedingTechnologyLink,
    ProceedingOrganizationLink,
    ProceedingOpportunityLink
)
from app.models.technology import Technology
from app.models.opportunity import Opportunity
from app.models.organization import Organization

logger = logging.getLogger("PoliciesAPI")
router = APIRouter(prefix="/policies", tags=["Policy, Codes & Standards"])

# Lazy import of SEED_POLICIES & SEED_PROCEEDINGS as in-memory fallback
_SEED_POLICIES_CACHE = None
_SEED_PROCEEDINGS_CACHE = None

def _get_seed_policies() -> List[Dict[str, Any]]:
    global _SEED_POLICIES_CACHE
    if _SEED_POLICIES_CACHE is None:
        try:
            from seed_policies import SEED_POLICIES
            _SEED_POLICIES_CACHE = SEED_POLICIES
        except Exception:
            _SEED_POLICIES_CACHE = []
    return _SEED_POLICIES_CACHE


def _get_seed_proceedings() -> List[Dict[str, Any]]:
    global _SEED_PROCEEDINGS_CACHE
    if _SEED_PROCEEDINGS_CACHE is None:
        try:
            from seed_proceedings import SEED_PROCEEDINGS
            _SEED_PROCEEDINGS_CACHE = SEED_PROCEEDINGS
        except Exception:
            _SEED_PROCEEDINGS_CACHE = []
    return _SEED_PROCEEDINGS_CACHE


def _get_fallback_policies(
    category: Optional[str] = None,
    jurisdiction_level: Optional[str] = None,
    jurisdiction_state: Optional[str] = None,
    technology_id: Optional[str] = None,
    fuel_vector: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Provides fallback policy results directly from the in-memory registry."""
    raw = _get_seed_policies()
    filtered = []

    for p in raw:
        if category and p.get("category") != category:
            continue
        if jurisdiction_level and p.get("jurisdiction_level") != jurisdiction_level:
            continue
        if jurisdiction_state and p.get("jurisdiction_state") != jurisdiction_state:
            continue
        if status and p.get("status") != status:
            continue
        if technology_id:
            tech_links = p.get("tech_links", [])
            if not any(tl.get("tech_id") == technology_id for tl in tech_links):
                continue
        if fuel_vector:
            fuel_links = p.get("fuel_links", [])
            if not any(fl.get("fuel_vector") == fuel_vector for fl in fuel_links):
                continue
        if search:
            s = search.lower().strip()
            haystack = (
                f"{p.get('code_identifier', '')} {p.get('title', '')} {p.get('short_title', '')} "
                f"{p.get('executive_summary', '')} {p.get('compliance_mandate', '')} {p.get('commercial_friction_points', '')}"
            ).lower()
            if s not in haystack:
                continue

        filtered.append({
            "id": p["id"],
            "code_identifier": p["code_identifier"],
            "title": p["title"],
            "short_title": p.get("short_title"),
            "category": p["category"],
            "jurisdiction_level": p["jurisdiction_level"],
            "jurisdiction_state": p.get("jurisdiction_state", "US"),
            "status": p.get("status", "active"),
            "effective_year": p.get("effective_year"),
            "sunset_year": p.get("sunset_year"),
            "latest_revision": p.get("latest_revision"),
            "executive_summary": p["executive_summary"],
            "compliance_mandate": p["compliance_mandate"],
            "commercial_friction_points": p.get("commercial_friction_points"),
            "associated_incentives": p.get("associated_incentives"),
            "official_source_url": p.get("official_source_url"),
            "linked_technologies_count": len(p.get("tech_links", [])),
            "linked_opportunities_count": len(p.get("opportunity_links", []))
        })

    total = len(filtered)
    page_items = filtered[offset : offset + limit]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "policies": page_items
    }


@router.get("")
def list_policies(
    category: Optional[str] = Query(None, description="Filter by category (e.g. safety_code, interconnection_rule, tax_incentive, state_statute, emissions_standard)"),
    jurisdiction_level: Optional[str] = Query(None, description="Filter by jurisdiction (federal, state, municipal, international)"),
    jurisdiction_state: Optional[str] = Query(None, description="Filter by state (e.g. NY, CA, US)"),
    technology_id: Optional[str] = Query(None, description="Filter by linked technology ID (e.g. iron_air_battery)"),
    fuel_vector: Optional[str] = Query(None, description="Filter by fuel carrier (e.g. green_hydrogen, saf, rng)"),
    status: Optional[str] = Query(None, description="Filter by status (active, proposed, under_revision)"),
    search: Optional[str] = Query(None, description="Keyword search across titles, codes, summaries, and mandates"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Search and filter energy innovation policies, regulations, and safety codes.
    Uses PostgreSQL GIN full-text search when search term is provided, with fallback.
    """
    try:
        query = db.query(PolicyStandard)

        if category:
            query = query.filter(PolicyStandard.category == category)
        if jurisdiction_level:
            query = query.filter(PolicyStandard.jurisdiction_level == jurisdiction_level)
        if jurisdiction_state:
            query = query.filter(PolicyStandard.jurisdiction_state == jurisdiction_state)
        if status:
            query = query.filter(PolicyStandard.status == status)

        # Filter by Technology ID
        if technology_id:
            query = query.join(PolicyTechnologyLink, PolicyStandard.id == PolicyTechnologyLink.policy_id)\
                         .filter(PolicyTechnologyLink.technology_id == technology_id)

        # Filter by Fuel Vector
        if fuel_vector:
            query = query.join(PolicyFuelLink, PolicyStandard.id == PolicyFuelLink.policy_id)\
                         .filter(PolicyFuelLink.fuel_vector == fuel_vector)

        # Full-Text Search in PostgreSQL
        if search and search.strip():
            s = search.strip()
            term = f"%{s}%"
            query = query.filter(or_(
                PolicyStandard.code_identifier.ilike(term),
                PolicyStandard.title.ilike(term),
                PolicyStandard.executive_summary.ilike(term),
                PolicyStandard.compliance_mandate.ilike(term)
            ))

        total = query.count()
        if total == 0:
            return _get_fallback_policies(category, jurisdiction_level, jurisdiction_state, technology_id, fuel_vector, status, search, limit, offset)

        # Batch query active opportunities and pipeline funding from view
        active_opp_map = {}
        try:
            view_rows = db.execute(text(
                "SELECT policy_id, active_linked_opportunities_count, total_linked_pipeline_funding_usd FROM vw_policy_statutory_mandates_matrix"
            )).fetchall()
            active_opp_map = {r[0]: (r[1], float(r[2] or 0.0)) for r in view_rows}
        except Exception as e:
            logger.debug(f"View lookup note in list_policies: {e}")

        policies = query.order_by(PolicyStandard.code_identifier.asc()).offset(offset).limit(limit).all()

        items = []
        for p in policies:
            active_cnt, pipeline_f = active_opp_map.get(p.id, (0, 0.0))
            items.append({
                "id": p.id,
                "code_identifier": p.code_identifier,
                "title": p.title,
                "short_title": p.short_title,
                "category": p.category,
                "jurisdiction_level": p.jurisdiction_level,
                "jurisdiction_state": p.jurisdiction_state,
                "status": p.status,
                "effective_year": p.effective_year,
                "sunset_year": p.sunset_year,
                "latest_revision": p.latest_revision,
                "executive_summary": p.executive_summary,
                "compliance_mandate": p.compliance_mandate,
                "commercial_friction_points": p.commercial_friction_points,
                "associated_incentives": p.associated_incentives,
                "official_source_url": p.official_source_url,
                "linked_technologies_count": len(p.technology_links) if p.technology_links else 0,
                "linked_opportunities_count": len(p.opportunity_links) if p.opportunity_links else 0,
                "active_opportunities_count": active_cnt,
                "total_pipeline_funding_usd": pipeline_f,
            })

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "policies": items
        }
    except Exception as e:
        logger.warning(f"Database query failed in list_policies, serving fallback: {e}")
        return _get_fallback_policies(category, jurisdiction_level, jurisdiction_state, technology_id, fuel_vector, status, search, limit, offset)


@router.get("/stats")
def get_policy_macro_stats(db: Session = Depends(get_db)):
    """Macro summary metrics across the policy, codes & standards database."""
    try:
        total_policies = db.query(func.count(PolicyStandard.id)).scalar() or 0
        if total_policies > 0:
            total_tech_links = db.query(func.count(PolicyTechnologyLink.id)).scalar() or 0
            total_fuel_links = db.query(func.count(PolicyFuelLink.id)).scalar() or 0
            total_opp_links = db.query(func.count(PolicyOpportunityLink.id)).scalar() or 0

            categories_raw = db.query(PolicyStandard.category, func.count(PolicyStandard.id))\
                               .group_by(PolicyStandard.category).all()
            categories = {cat: count for cat, count in categories_raw}

            jurisdictions_raw = db.query(PolicyStandard.jurisdiction_level, func.count(PolicyStandard.id))\
                                  .group_by(PolicyStandard.jurisdiction_level).all()
            jurisdictions = {jur: count for jur, count in jurisdictions_raw}

            return {
                "total_policies": total_policies,
                "total_technology_linkages": total_tech_links,
                "total_fuel_linkages": total_fuel_links,
                "total_opportunity_linkages": total_opp_links,
                "categories_breakdown": categories,
                "jurisdictions_breakdown": jurisdictions,
                "authoritative_sources": ["NFPA", "UL", "IEEE", "FERC", "EPA", "DOE", "NYPSC", "CPUC", "CARB"]
            }
    except Exception as e:
        logger.warning(f"Database query failed in get_policy_macro_stats: {e}")

    # Fallback stats
    raw = _get_seed_policies()
    cat_counts = {}
    jur_counts = {}
    tech_links_count = 0
    fuel_links_count = 0

    for p in raw:
        c = p.get("category", "safety_code")
        j = p.get("jurisdiction_level", "federal")
        cat_counts[c] = cat_counts.get(c, 0) + 1
        jur_counts[j] = jur_counts.get(j, 0) + 1
        tech_links_count += len(p.get("tech_links", []))
        fuel_links_count += len(p.get("fuel_links", []))

    return {
        "total_policies": len(raw),
        "total_technology_linkages": tech_links_count,
        "total_fuel_linkages": fuel_links_count,
        "total_opportunity_linkages": 0,
        "categories_breakdown": cat_counts,
        "jurisdictions_breakdown": jur_counts,
        "authoritative_sources": ["NFPA", "UL", "IEEE", "FERC", "EPA", "DOE", "NYPSC", "CPUC", "CARB"]
    }


@router.get("/by-technology/{tech_id}")
def get_policies_for_technology(tech_id: str, db: Session = Depends(get_db)):
    """
    Returns all standards, regulations, and tax incentives governing a specific technology.
    Includes compliance impact level (critical_gate, cost_driver, accelerator_tailwind) and friction points.
    """
    try:
        links = db.query(PolicyTechnologyLink).filter(PolicyTechnologyLink.technology_id == tech_id).all()
        if links:
            tech = db.query(Technology).filter(Technology.id == tech_id).first()
            results = []
            for link in links:
                pol = link.policy
                if not pol:
                    continue
                results.append({
                    "id": pol.id,
                    "code_identifier": pol.code_identifier,
                    "title": pol.title,
                    "short_title": pol.short_title,
                    "category": pol.category,
                    "jurisdiction_level": pol.jurisdiction_level,
                    "jurisdiction_state": pol.jurisdiction_state,
                    "relevance_type": link.relevance_type,
                    "compliance_impact": link.compliance_impact,
                    "impact_summary": link.impact_summary,
                    "compliance_mandate": pol.compliance_mandate,
                    "commercial_friction_points": pol.commercial_friction_points,
                    "associated_incentives": pol.associated_incentives,
                    "official_source_url": pol.official_source_url
                })

            impact_order = {"critical_gate": 1, "cost_driver": 2, "accelerator_tailwind": 3}
            results.sort(key=lambda x: impact_order.get(x["compliance_impact"], 4))

            return {
                "technology_id": tech_id,
                "technology_name": tech.name if tech else tech_id,
                "policies_count": len(results),
                "policies": results
            }
    except Exception as e:
        logger.warning(f"Database query failed in get_policies_for_technology({tech_id}): {e}")

    # Fallback to seed policies
    raw = _get_seed_policies()
    results = []
    for pol in raw:
        for tlink in pol.get("tech_links", []):
            if tlink.get("tech_id") == tech_id:
                results.append({
                    "id": pol["id"],
                    "code_identifier": pol["code_identifier"],
                    "title": pol["title"],
                    "short_title": pol.get("short_title"),
                    "category": pol["category"],
                    "jurisdiction_level": pol["jurisdiction_level"],
                    "jurisdiction_state": pol.get("jurisdiction_state", "US"),
                    "relevance_type": tlink.get("relevance_type", "mandatory_testing"),
                    "compliance_impact": tlink.get("compliance_impact", "critical_gate"),
                    "impact_summary": tlink.get("impact_summary"),
                    "compliance_mandate": pol["compliance_mandate"],
                    "commercial_friction_points": pol.get("commercial_friction_points"),
                    "associated_incentives": pol.get("associated_incentives"),
                    "official_source_url": pol.get("official_source_url")
                })

    impact_order = {"critical_gate": 1, "cost_driver": 2, "accelerator_tailwind": 3}
    results.sort(key=lambda x: impact_order.get(x["compliance_impact"], 4))

    return {
        "technology_id": tech_id,
        "technology_name": tech_id.replace("_", " ").title(),
        "policies_count": len(results),
        "policies": results
    }


@router.get("/by-opportunity/{opp_id}")
def get_policies_for_opportunity(opp_id: int, db: Session = Depends(get_db)):
    """Returns statutory basis and required compliance standards for a funding opportunity."""
    try:
        links = db.query(PolicyOpportunityLink).filter(PolicyOpportunityLink.opportunity_id == opp_id).all()
        opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
        if opp:
            results = []
            for link in links:
                pol = link.policy
                if not pol:
                    continue
                results.append({
                    "id": pol.id,
                    "code_identifier": pol.code_identifier,
                    "title": pol.title,
                    "short_title": pol.short_title,
                    "category": pol.category,
                    "jurisdiction_level": pol.jurisdiction_level,
                    "jurisdiction_state": pol.jurisdiction_state,
                    "link_reason": link.link_reason,
                    "compliance_mandate": pol.compliance_mandate,
                    "official_source_url": pol.official_source_url
                })

            return {
                "opportunity_id": opp_id,
                "solicitation_number": opp.solicitation_number,
                "opportunity_name": opp.name,
                "agency": opp.agency,
                "policies_count": len(results),
                "policies": results
            }
    except Exception as e:
        logger.warning(f"Database query failed in get_policies_for_opportunity({opp_id}): {e}")

    return {
        "opportunity_id": opp_id,
        "solicitation_number": f"OPP-{opp_id}",
        "opportunity_name": "Clean Energy Funding Opportunity",
        "agency": "State/Federal",
        "policies_count": 0,
        "policies": []
    }


# =============================================================================
# REGULATORY PROCEEDINGS & PUC DOCKETS ENDPOINTS
# =============================================================================
# REGULATORY PROCEEDINGS & PUC DOCKETS ENDPOINTS
# =============================================================================

def _get_fallback_proceedings(
    commission: Optional[str] = None,
    jurisdiction_level: Optional[str] = None,
    jurisdiction_state: Optional[str] = None,
    topic_category: Optional[str] = None,
    technology_id: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Provides fallback proceeding results directly from the in-memory registry."""
    raw = _get_seed_proceedings()
    filtered = []

    for p in raw:
        if commission and p.get("commission") != commission:
            continue
        if jurisdiction_level and p.get("jurisdiction_level") != jurisdiction_level:
            continue
        if jurisdiction_state and p.get("jurisdiction_state") != jurisdiction_state:
            continue
        if topic_category and p.get("topic_category") != topic_category:
            continue
        if status and p.get("status") != status:
            continue
        if technology_id:
            tech_links = p.get("tech_links", [])
            from seed_proceedings import TECH_ID_ALIASES
            resolved_id = TECH_ID_ALIASES.get(technology_id, technology_id)
            if not any(tl.get("tech_id") in (technology_id, resolved_id) for tl in tech_links):
                continue
        if search:
            s = search.lower().strip()
            haystack = (
                f"{p.get('docket_number', '')} {p.get('title', '')} {p.get('short_title', '')} "
                f"{p.get('commission', '')} {p.get('topic_category', '')} {p.get('executive_summary', '')} "
                f"{p.get('innovation_impact', '')} {p.get('commercial_tailwinds', '')} {p.get('commercial_friction_points', '')}"
            ).lower()
            if s not in haystack:
                continue

        filtered.append({
            "id": p["id"],
            "docket_number": p["docket_number"],
            "commission": p["commission"],
            "jurisdiction_level": p.get("jurisdiction_level", "state"),
            "jurisdiction_state": p.get("jurisdiction_state", "US"),
            "title": p["title"],
            "short_title": p.get("short_title"),
            "topic_category": p["topic_category"],
            "status": p.get("status", "active"),
            "open_date": p.get("open_date").isoformat() if hasattr(p.get("open_date"), "isoformat") else p.get("open_date"),
            "comment_deadline": p.get("comment_deadline").isoformat() if hasattr(p.get("comment_deadline"), "isoformat") else p.get("comment_deadline"),
            "expected_order_date": p.get("expected_order_date").isoformat() if hasattr(p.get("expected_order_date"), "isoformat") else p.get("expected_order_date"),
            "executive_summary": p["executive_summary"],
            "innovation_impact": p["innovation_impact"],
            "commercial_tailwinds": p.get("commercial_tailwinds"),
            "commercial_friction_points": p.get("commercial_friction_points"),
            "key_filings_summary": p.get("key_filings_summary"),
            "official_docket_url": p.get("official_docket_url"),
            "linked_technologies_count": len(p.get("tech_links", [])),
            "linked_organizations_count": len(p.get("org_names", []))
        })

    total = len(filtered)
    page_items = filtered[offset : offset + limit]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "proceedings": page_items
    }


@router.get("/proceedings")
def list_proceedings(
    commission: Optional[str] = Query(None, description="Filter by commission (e.g. NYPSC, CPUC, PUCT, FERC, Mass DPU, ICC)"),
    jurisdiction_level: Optional[str] = Query(None, description="Filter by jurisdiction (federal, state, rto_iso)"),
    jurisdiction_state: Optional[str] = Query(None, description="Filter by state (e.g. NY, CA, TX, US, MA, IL)"),
    topic_category: Optional[str] = Query(None, description="Filter by category (large_load_interconnection, storage_procurement, thermal_networks, interconnection_reform, vpp_rate_design, transmission_planning, clean_firm_procurement)"),
    technology_id: Optional[str] = Query(None, description="Filter by linked technology ID (e.g. iron_air_battery, smr_advanced_nuclear)"),
    status: Optional[str] = Query(None, description="Filter by status (active, staff_whitepaper, public_comment, order_issued, implementation)"),
    search: Optional[str] = Query(None, description="Keyword search across dockets, titles, summaries, and impact briefs"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Search and filter energy innovation regulatory proceedings and PUC/FERC dockets.
    Provides structured intelligence on large load interconnection, VPP tariffs, and clean procurement.
    """
    com_val = commission if isinstance(commission, str) else None
    jur_level_val = jurisdiction_level if isinstance(jurisdiction_level, str) else None
    jur_st_val = jurisdiction_state if isinstance(jurisdiction_state, str) else None
    topic_val = topic_category if isinstance(topic_category, str) else None
    tech_val = technology_id if isinstance(technology_id, str) else None
    status_val = status if isinstance(status, str) else None
    search_val = search.strip() if isinstance(search, str) and search.strip() else None
    limit_val = limit if isinstance(limit, int) else 50
    offset_val = offset if isinstance(offset, int) else 0

    try:
        query = db.query(RegulatoryProceeding)

        if com_val:
            query = query.filter(RegulatoryProceeding.commission == com_val)
        if jur_level_val:
            query = query.filter(RegulatoryProceeding.jurisdiction_level == jur_level_val)
        if jur_st_val:
            query = query.filter(RegulatoryProceeding.jurisdiction_state == jur_st_val)
        if topic_val:
            query = query.filter(RegulatoryProceeding.topic_category == topic_val)
        if status_val:
            query = query.filter(RegulatoryProceeding.status == status_val)

        # Filter by Technology ID
        if tech_val:
            from seed_proceedings import TECH_ID_ALIASES
            resolved_tech_id = TECH_ID_ALIASES.get(tech_val, tech_val)
            query = query.join(ProceedingTechnologyLink, RegulatoryProceeding.id == ProceedingTechnologyLink.proceeding_id)\
                         .filter(
                             or_(
                                 ProceedingTechnologyLink.technology_id == tech_val,
                                 ProceedingTechnologyLink.technology_id == resolved_tech_id
                             )
                         )

        # Keyword search
        if search_val:
            term = f"%{search_val}%"
            query = query.filter(or_(
                RegulatoryProceeding.docket_number.ilike(term),
                RegulatoryProceeding.title.ilike(term),
                RegulatoryProceeding.short_title.ilike(term),
                RegulatoryProceeding.executive_summary.ilike(term),
                RegulatoryProceeding.innovation_impact.ilike(term)
            ))

        total = query.count()
        if total == 0:
            return _get_fallback_proceedings(com_val, jur_level_val, jur_st_val, topic_val, tech_val, status_val, search_val, limit_val, offset_val)

        proceedings = query.order_by(RegulatoryProceeding.docket_number.asc()).offset(offset_val).limit(limit_val).all()

        items = []
        for p in proceedings:
            items.append({
                "id": p.id,
                "docket_number": p.docket_number,
                "commission": p.commission,
                "jurisdiction_level": p.jurisdiction_level,
                "jurisdiction_state": p.jurisdiction_state,
                "title": p.title,
                "short_title": p.short_title,
                "topic_category": p.topic_category,
                "status": p.status,
                "open_date": p.open_date.isoformat() if p.open_date else None,
                "comment_deadline": p.comment_deadline.isoformat() if p.comment_deadline else None,
                "expected_order_date": p.expected_order_date.isoformat() if p.expected_order_date else None,
                "executive_summary": p.executive_summary,
                "innovation_impact": p.innovation_impact,
                "commercial_tailwinds": p.commercial_tailwinds,
                "commercial_friction_points": p.commercial_friction_points,
                "key_filings_summary": p.key_filings_summary,
                "official_docket_url": p.official_docket_url,
                "linked_technologies_count": len(p.technology_links),
                "linked_organizations_count": len(p.organization_links)
            })

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "proceedings": items
        }
    except Exception as e:
        logger.warning(f"Database query failed in list_proceedings, serving fallback: {e}")
        return _get_fallback_proceedings(commission, jurisdiction_level, jurisdiction_state, topic_category, technology_id, status, search, limit, offset)


@router.get("/proceedings/stats")
def get_proceeding_macro_stats(db: Session = Depends(get_db)):
    """Macro summary metrics across the regulatory proceedings and PUC dockets registry."""
    try:
        total_proceedings = db.query(func.count(RegulatoryProceeding.id)).scalar() or 0
        if total_proceedings > 0:
            total_tech_links = db.query(func.count(ProceedingTechnologyLink.id)).scalar() or 0
            total_org_links = db.query(func.count(ProceedingOrganizationLink.id)).scalar() or 0

            commissions_raw = db.query(RegulatoryProceeding.commission, func.count(RegulatoryProceeding.id))\
                                .group_by(RegulatoryProceeding.commission).all()
            commissions = {com: count for com, count in commissions_raw}

            topics_raw = db.query(RegulatoryProceeding.topic_category, func.count(RegulatoryProceeding.id))\
                           .group_by(RegulatoryProceeding.topic_category).all()
            topics = {top: count for top, count in topics_raw}

            states_raw = db.query(RegulatoryProceeding.jurisdiction_state, func.count(RegulatoryProceeding.id))\
                           .group_by(RegulatoryProceeding.jurisdiction_state).all()
            states = {st: count for st, count in states_raw if st}

            return {
                "total_proceedings": total_proceedings,
                "total_technology_linkages": total_tech_links,
                "total_organization_linkages": total_org_links,
                "commissions_breakdown": commissions,
                "topics_breakdown": topics,
                "states_breakdown": states,
                "active_commissions_count": len(commissions)
            }
    except Exception as e:
        logger.warning(f"Database query failed in get_proceeding_macro_stats: {e}")

    # Fallback stats
    raw = _get_seed_proceedings()
    com_counts = {}
    top_counts = {}
    st_counts = {}
    tech_links_count = 0
    org_links_count = 0

    for p in raw:
        com = p.get("commission", "FERC")
        top = p.get("topic_category", "interconnection_reform")
        st = p.get("jurisdiction_state", "US")
        com_counts[com] = com_counts.get(com, 0) + 1
        top_counts[top] = top_counts.get(top, 0) + 1
        st_counts[st] = st_counts.get(st, 0) + 1
        tech_links_count += len(p.get("tech_links", []))
        org_links_count += len(p.get("org_names", []))

    return {
        "total_proceedings": len(raw),
        "total_technology_linkages": tech_links_count,
        "total_organization_linkages": org_links_count,
        "commissions_breakdown": com_counts,
        "topics_breakdown": top_counts,
        "states_breakdown": st_counts,
        "active_commissions_count": len(com_counts)
    }


@router.get("/proceedings/by-technology/{tech_id}")
def get_proceedings_for_technology(tech_id: str, db: Session = Depends(get_db)):
    """
    Returns all active and landmark PUC / FERC proceedings directly impacting a specific clean technology.
    Includes innovation implications, commercial tailwinds, and friction points.
    """
    try:
        from seed_proceedings import TECH_ID_ALIASES
        canonical_tech_id = TECH_ID_ALIASES.get(tech_id, tech_id)
        
        links = db.query(ProceedingTechnologyLink).filter(
            or_(
                ProceedingTechnologyLink.technology_id == tech_id,
                ProceedingTechnologyLink.technology_id == canonical_tech_id
            )
        ).all()

        if links:
            tech = db.query(Technology).filter(Technology.id == canonical_tech_id).first()
            results = []
            for link in links:
                proc = link.proceeding
                if not proc:
                    continue
                results.append({
                    "id": proc.id,
                    "docket_number": proc.docket_number,
                    "commission": proc.commission,
                    "jurisdiction_level": proc.jurisdiction_level,
                    "jurisdiction_state": proc.jurisdiction_state,
                    "title": proc.title,
                    "short_title": proc.short_title,
                    "topic_category": proc.topic_category,
                    "status": proc.status,
                    "impact_level": link.impact_level,
                    "commercial_vector": link.commercial_vector,
                    "impact_summary": link.impact_summary,
                    "executive_summary": proc.executive_summary,
                    "innovation_impact": proc.innovation_impact,
                    "commercial_tailwinds": proc.commercial_tailwinds,
                    "commercial_friction_points": proc.commercial_friction_points,
                    "official_docket_url": proc.official_docket_url
                })

            impact_order = {"high_catalyst": 1, "critical_gate": 2, "market_expansion": 3, "cost_driver": 4}
            results.sort(key=lambda x: impact_order.get(x["impact_level"], 5))

            return {
                "technology_id": tech_id,
                "technology_name": tech.name if tech else tech_id.replace("_", " ").title(),
                "proceedings_count": len(results),
                "proceedings": results
            }
    except Exception as e:
        logger.warning(f"Database query failed in get_proceedings_for_technology({tech_id}): {e}")

    # Fallback to seed proceedings
    raw = _get_seed_proceedings()
    from seed_proceedings import TECH_ID_ALIASES
    canonical_tech_id = TECH_ID_ALIASES.get(tech_id, tech_id)
    results = []

    for proc in raw:
        for tlink in proc.get("tech_links", []):
            if tlink.get("tech_id") in (tech_id, canonical_tech_id):
                results.append({
                    "id": proc["id"],
                    "docket_number": proc["docket_number"],
                    "commission": proc["commission"],
                    "jurisdiction_level": proc.get("jurisdiction_level", "state"),
                    "jurisdiction_state": proc.get("jurisdiction_state", "US"),
                    "title": proc["title"],
                    "short_title": proc.get("short_title"),
                    "topic_category": proc["topic_category"],
                    "status": proc.get("status", "active"),
                    "impact_level": tlink.get("impact_level", "high_catalyst"),
                    "commercial_vector": tlink.get("commercial_vector", "interconnection_access"),
                    "impact_summary": tlink.get("impact_summary"),
                    "executive_summary": proc["executive_summary"],
                    "innovation_impact": proc["innovation_impact"],
                    "commercial_tailwinds": proc.get("commercial_tailwinds"),
                    "commercial_friction_points": proc.get("commercial_friction_points"),
                    "official_docket_url": proc.get("official_docket_url")
                })

    impact_order = {"high_catalyst": 1, "critical_gate": 2, "market_expansion": 3, "cost_driver": 4}
    results.sort(key=lambda x: impact_order.get(x["impact_level"], 5))

    return {
        "technology_id": tech_id,
        "technology_name": tech_id.replace("_", " ").title(),
        "proceedings_count": len(results),
        "proceedings": results
    }


@router.get("/proceedings/{proceeding_id}")
def get_proceeding_detail(proceeding_id: str, db: Session = Depends(get_db)):
    """Returns full structured legal and strategic dossier for a specific regulatory proceeding or docket."""
    try:
        proc = db.query(RegulatoryProceeding).filter(RegulatoryProceeding.id == proceeding_id).first()
        if proc:
            techs = []
            for tlink in proc.technology_links:
                tech = tlink.technology
                techs.append({
                    "technology_id": tlink.technology_id,
                    "technology_name": tech.name if tech else tlink.technology_id,
                    "impact_level": tlink.impact_level,
                    "commercial_vector": tlink.commercial_vector,
                    "impact_summary": tlink.impact_summary
                })

            orgs = []
            for olink in proc.organization_links:
                org = olink.organization
                orgs.append({
                    "organization_id": olink.organization_id,
                    "organization_name": org.name if org else f"Org-{olink.organization_id}",
                    "role": olink.role
                })

            opps = []
            for polink in proc.opportunity_links:
                opp = polink.opportunity
                if opp:
                    opps.append({
                        "id": opp.id,
                        "solicitation_number": opp.solicitation_number,
                        "name": opp.name,
                        "agency": opp.agency,
                        "status": opp.status,
                        "link_reason": polink.link_reason
                    })

            return {
                "id": proc.id,
                "docket_number": proc.docket_number,
                "commission": proc.commission,
                "jurisdiction_level": proc.jurisdiction_level,
                "jurisdiction_state": proc.jurisdiction_state,
                "title": proc.title,
                "short_title": proc.short_title,
                "topic_category": proc.topic_category,
                "status": proc.status,
                "open_date": proc.open_date.isoformat() if proc.open_date else None,
                "comment_deadline": proc.comment_deadline.isoformat() if proc.comment_deadline else None,
                "expected_order_date": proc.expected_order_date.isoformat() if proc.expected_order_date else None,
                "executive_summary": proc.executive_summary,
                "innovation_impact": proc.innovation_impact,
                "commercial_tailwinds": proc.commercial_tailwinds,
                "commercial_friction_points": proc.commercial_friction_points,
                "key_filings_summary": proc.key_filings_summary,
                "official_docket_url": proc.official_docket_url,
                "metadata": proc.metadata_json or {},
                "linked_technologies": techs,
                "linked_organizations": orgs,
                "linked_opportunities": opps
            }
    except Exception as e:
        logger.warning(f"Database query failed in get_proceeding_detail({proceeding_id}): {e}")

    # Fallback to seed proceedings
    raw = _get_seed_proceedings()
    for p in raw:
        if p["id"] == proceeding_id:
            return {
                "id": p["id"],
                "docket_number": p["docket_number"],
                "commission": p["commission"],
                "jurisdiction_level": p.get("jurisdiction_level", "state"),
                "jurisdiction_state": p.get("jurisdiction_state", "US"),
                "title": p["title"],
                "short_title": p.get("short_title"),
                "topic_category": p["topic_category"],
                "status": p.get("status", "active"),
                "open_date": p.get("open_date").isoformat() if hasattr(p.get("open_date"), "isoformat") else p.get("open_date"),
                "comment_deadline": p.get("comment_deadline").isoformat() if hasattr(p.get("comment_deadline"), "isoformat") else p.get("comment_deadline"),
                "expected_order_date": p.get("expected_order_date").isoformat() if hasattr(p.get("expected_order_date"), "isoformat") else p.get("expected_order_date"),
                "executive_summary": p["executive_summary"],
                "innovation_impact": p["innovation_impact"],
                "commercial_tailwinds": p.get("commercial_tailwinds"),
                "commercial_friction_points": p.get("commercial_friction_points"),
                "key_filings_summary": p.get("key_filings_summary"),
                "official_docket_url": p.get("official_docket_url"),
                "metadata": {},
                "linked_technologies": [
                    {
                        "technology_id": tl["tech_id"],
                        "technology_name": tl["tech_id"].replace("_", " ").title(),
                        "impact_level": tl.get("impact_level", "high_catalyst"),
                        "commercial_vector": tl.get("commercial_vector"),
                        "impact_summary": tl.get("impact_summary")
                    } for tl in p.get("tech_links", [])
                ],
                "linked_organizations": [
                    {
                        "organization_id": idx + 1,
                        "organization_name": org_name,
                        "role": "affected_utility"
                    } for idx, org_name in enumerate(p.get("org_names", []))
                ],
                "linked_opportunities": []
            }

    raise HTTPException(status_code=404, detail=f"Regulatory proceeding '{proceeding_id}' not found")


@router.get("/proceedings/{proceeding_id}/commercial-impact")
def get_proceeding_commercial_impact(proceeding_id: str, db: Session = Depends(get_db)):
    """
    Synthesizes deep institutional commercial impact, stakeholder breakdown, bottlenecks,
    and revenue monetization pathways for a specific regulatory proceeding or PUC docket.
    """
    from app.engine.news_linker import synthesize_regulatory_commercial_impact
    
    # 1. Try DB
    proc = None
    try:
        proc = db.query(RegulatoryProceeding).filter(
            or_(
                RegulatoryProceeding.id == proceeding_id,
                RegulatoryProceeding.docket_number.ilike(f"%{proceeding_id}%"),
                RegulatoryProceeding.docket_number.ilike(f"%{proceeding_id.replace('-', ' ')}%")
            )
        ).first()
    except Exception as e:
        logger.warning(f"DB lookup failed for proceeding {proceeding_id}: {e}")

    if proc:
        tech_names = [tlink.technology.name if tlink.technology else tlink.technology_id for tlink in proc.technology_links]
        synth_res = synthesize_regulatory_commercial_impact(
            item_type="proceeding",
            identifier=proc.docket_number,
            title=proc.title,
            summary=proc.executive_summary or proc.short_title or proc.title,
            mandate_or_tailwinds=f"Innovation Impact: {proc.innovation_impact or ''}. Tailwinds: {proc.commercial_tailwinds or ''}",
            friction_points=proc.commercial_friction_points,
            linked_technologies=tech_names
        )
        synth_res["proceeding_id"] = proc.id
        synth_res["docket_number"] = proc.docket_number
        synth_res["commission"] = proc.commission
        synth_res["title"] = proc.title
        synth_res["topic_category"] = proc.topic_category
        return synth_res

    # 2. Fallback to seed proceedings
    raw = _get_seed_proceedings()
    clean_proc_id = proceeding_id.lower().replace("-", "_").replace(" ", "_")
    for p in raw:
        clean_seed_id = p["id"].lower().replace("-", "_").replace(" ", "_")
        clean_docket = p.get("docket_number", "").lower().replace("-", "_").replace(" ", "_")
        clean_short = p.get("short_title", "").lower().replace("-", "_").replace(" ", "_")
        if (clean_proc_id in clean_seed_id or clean_seed_id in clean_proc_id or
            clean_proc_id in clean_docket or clean_proc_id in clean_short or
            clean_docket in clean_proc_id or clean_short in clean_proc_id):
            tech_names = [tl["tech_id"].replace("_", " ").title() for tl in p.get("tech_links", [])]
            synth_res = synthesize_regulatory_commercial_impact(
                item_type="proceeding",
                identifier=p["docket_number"],
                title=p["title"],
                summary=p.get("executive_summary") or p.get("title"),
                mandate_or_tailwinds=f"Innovation Impact: {p.get('innovation_impact', '')}. Tailwinds: {p.get('commercial_tailwinds', '')}",
                friction_points=p.get("commercial_friction_points"),
                linked_technologies=tech_names
            )
            synth_res["proceeding_id"] = p["id"]
            synth_res["docket_number"] = p["docket_number"]
            synth_res["commission"] = p["commission"]
            synth_res["title"] = p["title"]
            synth_res["topic_category"] = p.get("topic_category")
            return synth_res

    raise HTTPException(status_code=404, detail=f"Regulatory proceeding '{proceeding_id}' not found")


# =============================================================================
# STATUTORY COMPLIANCE DEFICIT & INNOVATION GAP ENDPOINTS
# =============================================================================

@router.get("/deficits")
def list_statutory_deficits(db: Session = Depends(get_db)):
    """
    Returns statutory compliance deficit models comparing state/federal mandates (NY CLCPA,
    CA SB100, FERC Order 1920) against tracked awards, quantifying unprocured procurement deficits.
    """
    from app.engine.deficit_engine import get_all_statutory_deficits
    deficits = get_all_statutory_deficits(db)
    return {
        "total_mandates_tracked": len(deficits),
        "deficits": deficits
    }


@router.get("/deficits/{deficit_id}")
def get_statutory_deficit(deficit_id: str, db: Session = Depends(get_db)):
    """Returns detailed compliance deficit model for a specific mandate."""
    from app.engine.deficit_engine import get_statutory_deficit_by_id
    deficit = get_statutory_deficit_by_id(db, deficit_id)
    if not deficit:
        raise HTTPException(status_code=404, detail=f"Statutory mandate deficit '{deficit_id}' not found")
    return deficit


# =============================================================================
# SINGLE POLICY/STANDARD DOSSIER & COMMERCIAL IMPACT
# =============================================================================

@router.get("/{policy_id}/commercial-impact")
def get_policy_commercial_impact(policy_id: str, db: Session = Depends(get_db)):
    """
    Synthesizes institutional commercial impact, compliance risks, stakeholder analysis,
    and monetization pathways for a specific energy standard, statutory mandate, or code.
    """
    from app.engine.news_linker import synthesize_regulatory_commercial_impact

    # 1. Try DB
    pol = None
    try:
        pol = db.query(PolicyStandard).filter(
            or_(
                PolicyStandard.id == policy_id,
                PolicyStandard.code_identifier.ilike(f"%{policy_id}%"),
                PolicyStandard.code_identifier.ilike(f"%{policy_id.replace('-', ' ')}%")
            )
        ).first()
    except Exception as e:
        logger.warning(f"DB lookup failed for policy {policy_id}: {e}")

    if pol:
        tech_names = [tlink.technology.name if tlink.technology else tlink.technology_id for tlink in pol.technology_links]
        synth_res = synthesize_regulatory_commercial_impact(
            item_type="policy_standard",
            identifier=pol.code_identifier,
            title=pol.title,
            summary=pol.executive_summary or pol.title,
            mandate_or_tailwinds=f"Compliance Mandate: {pol.compliance_mandate or ''}. Associated Incentives: {pol.associated_incentives or ''}",
            friction_points=pol.commercial_friction_points,
            linked_technologies=tech_names
        )
        synth_res["policy_id"] = pol.id
        synth_res["code_identifier"] = pol.code_identifier
        synth_res["category"] = pol.category
        synth_res["jurisdiction_level"] = pol.jurisdiction_level
        synth_res["title"] = pol.title
        return synth_res

    # 2. Fallback to seed policies
    raw = _get_seed_policies()
    clean_pol_id = policy_id.lower().replace("-", "_").replace(" ", "_")
    for p in raw:
        clean_seed_id = p["id"].lower().replace("-", "_").replace(" ", "_")
        clean_code = p.get("code_identifier", "").lower().replace("-", "_").replace(" ", "_")
        if clean_pol_id in (clean_seed_id, clean_code) or clean_code in clean_pol_id or clean_seed_id in clean_pol_id:
            tech_names = [tl["tech_id"].replace("_", " ").title() for tl in p.get("tech_links", [])]
            synth_res = synthesize_regulatory_commercial_impact(
                item_type="policy_standard",
                identifier=p["code_identifier"],
                title=p["title"],
                summary=p.get("executive_summary") or p.get("title"),
                mandate_or_tailwinds=f"Compliance Mandate: {p.get('compliance_mandate', '')}. Associated Incentives: {p.get('associated_incentives', '')}",
                friction_points=p.get("commercial_friction_points"),
                linked_technologies=tech_names
            )
            synth_res["policy_id"] = p["id"]
            synth_res["code_identifier"] = p["code_identifier"]
            synth_res["category"] = p.get("category")
            synth_res["jurisdiction_level"] = p.get("jurisdiction_level")
            synth_res["title"] = p["title"]
            return synth_res

    raise HTTPException(status_code=404, detail=f"Policy/Standard '{policy_id}' not found")


@router.get("/{policy_id}")
def get_policy_detail(policy_id: str, db: Session = Depends(get_db)):
    """Returns full structured dossier for a specific policy, code, or standard."""
    try:
        pol = db.query(PolicyStandard).filter(PolicyStandard.id == policy_id).first()
        if pol:
            techs = []
            for tlink in pol.technology_links:
                tech = tlink.technology
                techs.append({
                    "technology_id": tlink.technology_id,
                    "technology_name": tech.name if tech else tlink.technology_id,
                    "relevance_type": tlink.relevance_type,
                    "compliance_impact": tlink.compliance_impact,
                    "impact_summary": tlink.impact_summary
                })

            fuels = []
            for flink in pol.fuel_links:
                fuels.append({
                    "fuel_vector": flink.fuel_vector,
                    "lifecycle_ci_threshold": flink.lifecycle_ci_threshold,
                    "impact_summary": flink.impact_summary
                })

            opps = []
            for olink in pol.opportunity_links:
                opp = olink.opportunity
                if opp:
                    opps.append({
                        "id": opp.id,
                        "solicitation_number": opp.solicitation_number,
                        "name": opp.name,
                        "agency": opp.agency,
                        "status": opp.status,
                        "link_reason": olink.link_reason
                    })

            return {
                "id": pol.id,
                "code_identifier": pol.code_identifier,
                "title": pol.title,
                "short_title": pol.short_title,
                "category": pol.category,
                "jurisdiction_level": pol.jurisdiction_level,
                "jurisdiction_state": pol.jurisdiction_state,
                "status": pol.status,
                "effective_year": pol.effective_year,
                "sunset_year": pol.sunset_year,
                "latest_revision": pol.latest_revision,
                "executive_summary": pol.executive_summary,
                "statutory_intent": pol.statutory_intent,
                "compliance_mandate": pol.compliance_mandate,
                "commercial_friction_points": pol.commercial_friction_points,
                "associated_incentives": pol.associated_incentives,
                "official_source_url": pol.official_source_url,
                "metadata": pol.metadata_json or {},
                "linked_technologies": techs,
                "linked_fuels": fuels,
                "linked_opportunities": opps
            }
    except Exception as e:
        logger.warning(f"Database query failed in get_policy_detail({policy_id}): {e}")

    # Fallback to seed policies
    raw = _get_seed_policies()
    for p in raw:
        if p["id"] == policy_id:
            return {
                "id": p["id"],
                "code_identifier": p["code_identifier"],
                "title": p["title"],
                "short_title": p.get("short_title"),
                "category": p["category"],
                "jurisdiction_level": p["jurisdiction_level"],
                "jurisdiction_state": p.get("jurisdiction_state", "US"),
                "status": p.get("status", "active"),
                "effective_year": p.get("effective_year"),
                "sunset_year": p.get("sunset_year"),
                "latest_revision": p.get("latest_revision"),
                "executive_summary": p["executive_summary"],
                "statutory_intent": p.get("statutory_intent"),
                "compliance_mandate": p["compliance_mandate"],
                "commercial_friction_points": p.get("commercial_friction_points"),
                "associated_incentives": p.get("associated_incentives"),
                "official_source_url": p.get("official_source_url"),
                "metadata": {},
                "linked_technologies": [
                    {
                        "technology_id": tl["tech_id"],
                        "technology_name": tl["tech_id"].replace("_", " ").title(),
                        "relevance_type": tl.get("relevance_type"),
                        "compliance_impact": tl.get("compliance_impact"),
                        "impact_summary": tl.get("impact_summary")
                    } for tl in p.get("tech_links", [])
                ],
                "linked_fuels": p.get("fuel_links", []),
                "linked_opportunities": []
            }

    raise HTTPException(status_code=404, detail=f"Policy/Standard '{policy_id}' not found")



