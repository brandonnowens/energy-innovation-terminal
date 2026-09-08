"""Organizations API endpoints with PostgreSQL querying and taxonomy fallback."""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.cache_utils import TTLCache
from app.models.organization import Organization
from app.models.contact import Contact
from app.models.opportunity_organization import OpportunityOrganization
from app.ingest.organization_taxonomy import ORGANIZATION_TAXONOMY, get_organization_profile

logger = logging.getLogger("OrganizationsAPI")
router = APIRouter()
_org_meta_cache = TTLCache(ttl_seconds=300.0)


def _get_fallback_organizations(
    org_type: Optional[str] = None,
    state: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    exclude_nyserda: bool = False,
) -> Dict[str, Any]:
    """Provides structured taxonomy fallback when database is empty or offline."""
    all_items = []
    type_counts: Dict[str, int] = {}
    geo_dist: Dict[str, int] = {}

    for idx, (org_name, meta) in enumerate(ORGANIZATION_TAXONOMY.items(), start=1):
        if exclude_nyserda and ("nyserda" in org_name.lower() or "new york state energy research" in (meta.get("full_name") or "").lower()):
            continue
        cat = meta.get("category", "state")
        st = meta.get("state")
        domain = meta.get("logo_domain")
        if not domain and meta.get("website"):
            domain = meta["website"].replace("https://", "").replace("http://", "").split("/")[0]

        item = {
            "id": idx,
            "name": org_name,
            "full_name": meta.get("full_name", org_name),
            "org_type": cat,
            "category": cat,
            "sub_type": meta.get("sub_type"),
            "domain": domain,
            "website": meta.get("website"),
            "state": st,
            "city": meta.get("city", ""),
            "jurisdiction": meta.get("jurisdiction", ""),
            "description": meta.get("description", ""),
            "founded_year": meta.get("founded_year", None),
            "is_verified": True,
            "confidence": 1.0
        }
        all_items.append(item)

        # Track type counts
        type_counts[cat] = type_counts.get(cat, 0) + 1
        if st:
            geo_dist[st] = geo_dist.get(st, 0) + 1

    # Filter
    filtered = all_items
    if org_type:
        filtered = [o for o in filtered if o["org_type"] == org_type or o.get("category") == org_type]
    if state:
        filtered = [o for o in filtered if o.get("state") == state]
    if search:
        s = search.lower().strip()
        filtered = [
            o for o in filtered
            if s in o["name"].lower()
            or s in (o.get("full_name") or "").lower()
            or s in (o.get("domain") or "").lower()
            or s in (o.get("state") or "").lower()
            or s in (o.get("description") or "").lower()
        ]

    total = len(filtered)
    start_idx = (page - 1) * page_size
    page_items = filtered[start_idx : start_idx + page_size]

    return {
        "items": page_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
        "meta": {
            "type_counts": type_counts,
            "geographic_distribution": geo_dist
        }
    }


@router.get("/organizations")
def list_organizations(
    org_type: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    exclude_nyserda: Optional[bool] = Query(None),
    x_include_nyserda: Optional[str] = Header(None, alias="X-Include-NYSERDA"),
    db: Session = Depends(get_db),
):
    should_exclude_nyserda = exclude_nyserda is True or (x_include_nyserda is not None and x_include_nyserda.strip().lower() in ("false", "0", "no"))
    try:
        query = db.query(Organization)
        
        if should_exclude_nyserda:
            query = query.filter(
                ~func.lower(Organization.name).like("%nyserda%"),
                ~func.lower(Organization.domain).like("%nyserda%")
            )

        if org_type:
            query = query.filter(Organization.org_type == org_type)
        if state:
            query = query.filter(Organization.state == state)
        if search:
            search_lower = f"%{search.lower()}%"
            query = query.filter(
                func.lower(Organization.name).like(search_lower) |
                func.lower(Organization.domain).like(search_lower)
            )
        
        total = query.count()
        if total == 0:
            # Fall back to structured canonical taxonomy
            return _get_fallback_organizations(org_type=org_type, state=state, search=search, page=page, page_size=page_size, exclude_nyserda=should_exclude_nyserda)

        organizations = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # Org type counts and geographic distribution (cached per exclusion state)
        cache_suffix = f"_ex_{should_exclude_nyserda}"
        type_counts = _org_meta_cache.get(f"type_counts{cache_suffix}")
        geo_dist = _org_meta_cache.get(f"geo_dist{cache_suffix}")
        if type_counts is None or geo_dist is None:
            base_q = db.query(Organization)
            if should_exclude_nyserda:
                base_q = base_q.filter(
                    ~func.lower(Organization.name).like("%nyserda%"),
                    ~func.lower(Organization.domain).like("%nyserda%")
                )
            type_counts = dict(base_q.with_entities(Organization.org_type, func.count(Organization.id))
                               .group_by(Organization.org_type).all())
            geo_dist = dict(base_q.with_entities(Organization.state, func.count(Organization.id))
                            .filter(Organization.state.isnot(None))
                            .group_by(Organization.state).all())
            _org_meta_cache.set(f"type_counts{cache_suffix}", type_counts)
            _org_meta_cache.set(f"geo_dist{cache_suffix}", geo_dist)
        
        return {
            "items": [{
                "id": o.id,
                "name": o.name,
                "org_type": o.org_type,
                "domain": o.domain,
                "website": o.website,
                "state": o.state,
                "city": o.city,
                "description": o.description,
                "founded_year": o.founded_year,
                "is_verified": o.is_verified,
                "confidence": o.confidence
            } for o in organizations],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
            "meta": {
                "type_counts": type_counts,
                "geographic_distribution": geo_dist
            }
        }
    except Exception as e:
        logger.warning(f"Database query failed in list_organizations, serving canonical taxonomy: {e}")
        return _get_fallback_organizations(org_type=org_type, state=state, search=search, page=page, page_size=page_size, exclude_nyserda=should_exclude_nyserda)


@router.get("/organizations/search")
def search_organizations(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, le=50),
    exclude_nyserda: Optional[bool] = Query(None),
    x_include_nyserda: Optional[str] = Header(None, alias="X-Include-NYSERDA"),
    db: Session = Depends(get_db)
):
    should_exclude_nyserda = exclude_nyserda is True or (x_include_nyserda is not None and x_include_nyserda.strip().lower() in ("false", "0", "no"))
    try:
        search_lower = f"%{q.lower()}%"
        sq = db.query(Organization).filter(
            func.lower(Organization.name).like(search_lower) |
            func.lower(Organization.domain).like(search_lower)
        )
        if should_exclude_nyserda:
            sq = sq.filter(
                ~func.lower(Organization.name).like("%nyserda%"),
                ~func.lower(Organization.domain).like("%nyserda%")
            )
        organizations = sq.limit(limit).all()
        
        if organizations:
            return [{"id": o.id, "name": o.name, "domain": o.domain, "org_type": o.org_type} for o in organizations]
    except Exception as e:
        logger.warning(f"Database query failed in search_organizations: {e}")

    # Fallback to taxonomy search
    s = q.lower()
    results = []
    for idx, (name, meta) in enumerate(ORGANIZATION_TAXONOMY.items(), start=1):
        if should_exclude_nyserda and ("nyserda" in name.lower() or "new york state energy research" in meta.get("full_name", "").lower()):
            continue
        if s in name.lower() or s in meta.get("full_name", "").lower():
            results.append({
                "id": idx,
                "name": name,
                "domain": meta.get("logo_domain", ""),
                "org_type": meta.get("category", "funder")
            })
        if len(results) >= limit:
            break
    return results


@router.get("/organizations/{org_id}")
def get_organization(org_id: int, db: Session = Depends(get_db)):
    try:
        org = db.query(Organization).filter_by(id=org_id).first()
        if org:
            links = db.query(OpportunityOrganization).filter_by(organization_id=org_id).all()
            opportunities = [{"id": link.opportunity_id, "role": link.role} for link in links]
            contacts = db.query(Contact).filter_by(organization_id=org_id).limit(10).all()
            
            return {
                "id": org.id,
                "name": org.name,
                "org_type": org.org_type,
                "website": org.website,
                "domain": org.domain,
                "address": org.address_line,
                "city": org.city,
                "state": org.state,
                "zip_code": org.zip_code,
                "country": org.country,
                "description": org.description,
                "founded_year": org.founded_year,
                "is_verified": org.is_verified,
                "opportunities": opportunities,
                "contacts": [{"id": c.id, "name_display": c.name_display, "title": c.title} for c in contacts],
                "funding_history": {},
                "relationships": [],
                "timeline": []
            }
    except Exception as e:
        logger.warning(f"Database query failed in get_organization({org_id}): {e}")

    # Fallback to taxonomy item by index
    items = list(ORGANIZATION_TAXONOMY.items())
    if 1 <= org_id <= len(items):
        name, meta = items[org_id - 1]
        domain = meta.get("logo_domain")
        if not domain and meta.get("website"):
            domain = meta["website"].replace("https://", "").replace("http://", "").split("/")[0]
        return {
            "id": org_id,
            "name": name,
            "org_type": meta.get("category", "funder"),
            "website": meta.get("website"),
            "domain": domain,
            "address": "",
            "city": meta.get("city", ""),
            "state": meta.get("state", ""),
            "zip_code": "",
            "country": "US",
            "description": meta.get("description", ""),
            "founded_year": meta.get("founded_year", None),
            "is_verified": True,
            "opportunities": [],
            "contacts": [],
            "funding_history": {},
            "relationships": [],
            "timeline": []
        }

    raise HTTPException(status_code=404, detail="Organization not found")


@router.get("/organizations/{org_id}/contacts")
def get_organization_contacts(org_id: int, db: Session = Depends(get_db)):
    try:
        contacts = db.query(Contact).filter_by(organization_id=org_id).all()
        return [{
            "id": c.id,
            "name_display": c.name_display,
            "title": c.title,
            "role_type": c.role_type,
            "verification_status": c.verification_status
        } for c in contacts]
    except Exception:
        return []
