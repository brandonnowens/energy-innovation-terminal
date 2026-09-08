"""Agencies & Organizations structured taxonomy API endpoint."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.database import get_db
from app.models.opportunity import Opportunity
from app.ingest.organization_taxonomy import get_organization_profile, ORGANIZATION_TAXONOMY

router = APIRouter()

CATEGORY_META = {
    "utility": {
        "id": "utility",
        "label": "Electric & Gas Utilities",
        "icon": "Zap",
        "color": "amber",
        "description": "Investor-owned utilities, public power authorities, and municipal grid operators.",
    },
    "federal": {
        "id": "federal",
        "label": "Federal Agencies",
        "icon": "Landmark",
        "color": "indigo",
        "description": "Cabinet departments and independent federal research agencies.",
    },
    "state": {
        "id": "state",
        "label": "State Energy Agencies",
        "icon": "Building2",
        "color": "blue",
        "description": "State clean energy centers, public utility commissions, and energy offices.",
    },
    "foundation": {
        "id": "foundation",
        "label": "Philanthropic Foundations",
        "icon": "HeartHandshake",
        "color": "emerald",
        "description": "Private climate funds and philanthropic grant-making foundations.",
    },
    "national_lab": {
        "id": "national_lab",
        "label": "Research Institutions",
        "icon": "FlaskConical",
        "color": "purple",
        "description": "National laboratories and independent power research institutes.",
    },
}

_AGENCIES_CACHE = {}
_AGENCIES_CACHE_TIME = {}

@router.get("/agencies")
def list_agencies(
    category: Optional[str] = Query(None),
    exclude_nyserda: Optional[bool] = Query(None),
    x_include_nyserda: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """List all available organizations and utilities with structured categorization,
    opportunity counts, program counts, and category summaries with TTL cache."""
    is_excluded = exclude_nyserda is True or x_include_nyserda == "false"
    import time
    cache_key = f"{category or 'all'}:ex_{is_excluded}"
    now = time.time()
    if cache_key in _AGENCIES_CACHE and (now - _AGENCIES_CACHE_TIME.get(cache_key, 0) < 300):
        return _AGENCIES_CACHE[cache_key]
    
    # 1. Total and open opps per agency
    opp_stats = db.execute(text("""
        SELECT agency,
               COUNT(id) as total_opps,
               SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as active_opps,
               COUNT(DISTINCT program_id) as program_count
        FROM opportunities
        WHERE agency IS NOT NULL AND agency != ''
        GROUP BY agency
        ORDER BY total_opps DESC
    """)).fetchall()

    results: List[Dict[str, Any]] = []
    category_counts: Dict[str, int] = {k: 0 for k in CATEGORY_META.keys()}
    total_organizations = 0

    for row in opp_stats:
        agency_name = row[0]
        if is_excluded and (agency_name == "NYSERDA" or "NYSERDA" in agency_name.upper()):
            continue
        total_opps = row[1] or 0
        active_opps = row[2] or 0
        prog_count = row[3] or 0

        profile = get_organization_profile(agency_name)
        if is_excluded and (profile.get("code") == "NYSERDA" or "NYSERDA" in profile.get("name", "").upper()):
            continue
        cat_id = profile.get("category", "state")

        if cat_id in category_counts:
            category_counts[cat_id] += 1
        total_organizations += 1

        org_item = {
            "name": agency_name,
            "code": profile.get("code", agency_name),
            "full_name": profile.get("full_name", agency_name),
            "count": total_opps,
            "active_count": active_opps,
            "program_count": prog_count,
            "category": cat_id,
            "category_label": profile.get("category_label", CATEGORY_META.get(cat_id, {}).get("label", "Other")),
            "jurisdiction": profile.get("jurisdiction", "New York"),
            "state": profile.get("state", "NY"),
            "sub_type": profile.get("sub_type", "Energy Entity"),
            "logo_domain": profile.get("logo_domain"),
            "website": profile.get("website"),
            "description": profile.get("description"),
        }

        if not category or cat_id == category:
            results.append(org_item)

    # Sort results by category, then by count descending
    category_order = ["utility", "federal", "state", "foundation", "national_lab"]
    results.sort(key=lambda x: (category_order.index(x["category"]) if x["category"] in category_order else 99, -x["count"]))

    res = {
        "items": results,
        "total": total_organizations,
        "categories": [
            {
                **meta,
                "count": category_counts.get(cat_key, 0)
            }
            for cat_key, meta in CATEGORY_META.items()
        ]
    }
    _AGENCIES_CACHE[cache_key] = res
    _AGENCIES_CACHE_TIME[cache_key] = time.time()
    return res
