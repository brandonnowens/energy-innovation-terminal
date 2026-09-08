"""Opportunities API endpoints."""

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy import text, func, case, not_
from sqlalchemy.orm import Session, selectinload


from app.database import get_db
from app.models.opportunity import (
    Opportunity,
    OpportunityCategory,
    OpportunityContact,
    OpportunityDocument,
    OpportunityRestriction,
    OpportunityRound,
    EligibilityRule,
)
from app.models.award import Award
from app.models.result import ResultArtifact
from app.models.source import ChangeEvent, SourceConflict

router = APIRouter()


def _compute_days_since_release(opp: Opportunity) -> tuple[Optional[str], Optional[int]]:
    """Compute normalized release date and days elapsed since release."""
    now = datetime.now()
    rel_date = None
    if opp.open_date:
        rel_date = opp.open_date
    elif opp.revision_date:
        try:
            rel_date = datetime.fromisoformat(opp.revision_date.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            pass

    if not rel_date:
        if opp.year and opp.year < now.year:
            rel_date = datetime(opp.year, 6, 1)
        elif opp.first_seen_at:
            rel_date = opp.first_seen_at
        elif opp.created_at:
            rel_date = opp.created_at
        elif opp.year:
            rel_date = datetime(opp.year, 1, 1)

    if rel_date:
        if hasattr(rel_date, "tzinfo") and rel_date.tzinfo:
            rel_date = rel_date.replace(tzinfo=None)
        days = max(0, (now - rel_date).days)
        return rel_date.strftime("%Y-%m-%d"), days
    return None, None


def _opp_to_list_dict(opp: Opportunity, winning_proposals_count: int = 0, artifacts_count: int = 0, restrictions_count: int = 0) -> dict:
    """Lightweight serializer for table listing view without heavy JSON payloads."""
    next_deadline = None
    if hasattr(opp, "rounds") and opp.rounds:
        for r in opp.rounds:
            if r.status == "Open" and r.due_date:
                if next_deadline is None or r.due_date < next_deadline:
                    next_deadline = r.due_date

    release_date_str, days_since_release = _compute_days_since_release(opp)

    return {
        "id": opp.id,
        "agency": getattr(opp, "agency", None),
        "agency_code": getattr(opp, "agency_code", None),
        "jurisdiction": getattr(opp, "jurisdiction", None),
        "solicitation_number": opp.solicitation_number,
        "name": opp.name,
        "type": opp.solicitation_type,
        "category": opp.solicitation_category,
        "status": opp.status,
        "enrollment_type": opp.enrollment_type,
        "short_description": opp.short_description,
        "total_funding": opp.total_funding,
        "max_per_award": opp.max_per_award,
        "cost_share_pct": opp.cost_share_pct,
        "concept_paper_required": opp.concept_paper_required,
        "manual_submission_only": opp.manual_submission_only,
        "ny_green_bank": opp.ny_green_bank,
        "next_deadline": next_deadline.isoformat() if next_deadline else None,
        "due_date_display": opp.due_date_display,
        "release_date": release_date_str,
        "days_since_release": days_since_release,
        "is_historical": opp.is_historical,
        "org_type": getattr(opp, "org_type", None),
        "winning_proposals_count": winning_proposals_count,
        "has_winning_proposals": winning_proposals_count > 0,
        "artifacts_count": artifacts_count,
        "has_artifacts": artifacts_count > 0,
        "bundle_download_url": f"/api/opportunities/{opp.id}/artifacts/download-bundle" if (artifacts_count > 0 or winning_proposals_count > 0) else None,
        "restrictions": [{"id": i} for i in range(restrictions_count)],
        "source_name": opp.source_name,
        "last_verified": opp.last_verified_at.isoformat() if opp.last_verified_at else None,
    }



def _opp_to_dict(opp: Opportunity, winning_proposals_count: int = 0, artifacts_count: int = 0) -> dict:
    """Convert opportunity to dict with full relationships, proposal counts, and artifact metadata."""
    rounds = [
        {
            "round_number": r.round_number,
            "status": r.status,
            "due_date": r.due_date.isoformat() if r.due_date else None,
            "concept_paper_due_date": r.concept_paper_due_date.isoformat() if r.concept_paper_due_date else None,
        }
        for r in sorted(opp.rounds, key=lambda r: r.due_date or __import__("datetime").datetime.max)
    ]

    contacts = [
        {"name": c.name, "email": c.email, "phone": c.phone, "sequence": c.sequence}
        for c in opp.contacts
    ]

    documents = [
        {
            "name": d.document_name,
            "url": d.document_url,
            "sequence": d.document_sequence,
        }
        for d in sorted(opp.documents, key=lambda d: int(d.document_sequence or "0"))
    ]

    categories = [
        {
            "type": c.category_type,
            "value": c.category_value,
            "confidence": c.confidence,
        }
        for c in opp.categories
    ]

    eligibility_rules = [
        {
            "type": r.rule_type,
            "key": r.rule_key,
            "value": r.rule_value,
            "operator": r.rule_operator,
            "is_hard": r.is_hard_requirement,
            "source": r.source,
            "confidence": r.confidence,
        }
        for r in opp.eligibility_rules
    ]

    restrictions = [
        {
            "id": r.id,
            "category": r.category,
            "title": r.title,
            "description": r.description,
            "severity": r.severity,
            "source": r.source,
            "source_text": r.source_text,
            "confidence": r.confidence,
        }
        for r in (opp.restrictions if hasattr(opp, "restrictions") and opp.restrictions else [])
    ]

    # Next open deadline
    next_deadline = None
    for r in opp.rounds:
        if r.status == "Open" and r.due_date:
            if next_deadline is None or r.due_date < next_deadline:
                next_deadline = r.due_date

    release_date_str, days_since_release = _compute_days_since_release(opp)

    return {
        "id": opp.id,
        "agency": getattr(opp, "agency", None),
        "agency_code": getattr(opp, "agency_code", None),
        "jurisdiction": getattr(opp, "jurisdiction", None),
        "solicitation_number": opp.solicitation_number,
        "name": opp.name,
        "type": opp.solicitation_type,
        "category": opp.solicitation_category,
        "status": opp.status,
        "enrollment_type": opp.enrollment_type,
        "short_description": opp.short_description,
        "total_funding": opp.total_funding,
        "max_per_award": opp.max_per_award,
        "cost_share_pct": opp.cost_share_pct,
        "concept_paper_required": opp.concept_paper_required,
        "manual_submission_only": opp.manual_submission_only,
        "ny_green_bank": opp.ny_green_bank,
        "next_deadline": next_deadline.isoformat() if next_deadline else None,
        "due_date_display": opp.due_date_display,
        "release_date": release_date_str,
        "days_since_release": days_since_release,
        "revision_date": opp.revision_date,
        "revision_notes": opp.revision_notes,
        "detail_url": opp.detail_page_url,
        "portal_url": opp.portal_url,
        "winning_proposals_count": winning_proposals_count,
        "has_winning_proposals": winning_proposals_count > 0,

        "artifacts_count": artifacts_count,
        "has_artifacts": artifacts_count > 0,
        "bundle_download_url": f"/api/opportunities/{opp.id}/artifacts/download-bundle" if (artifacts_count > 0 or winning_proposals_count > 0) else None,
        "rounds": rounds,
        "contacts": contacts,
        "documents": documents,
        "categories": categories,
        "eligibility_rules": eligibility_rules,
        "restrictions": restrictions,
        "source_name": opp.source_name,
        "last_verified": opp.last_verified_at.isoformat() if opp.last_verified_at else None,
        "first_seen": opp.first_seen_at.isoformat() if opp.first_seen_at else None,
    }


@router.get("/opportunities")
def list_opportunities(
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    agency: Optional[str] = Query(None),
    jurisdiction: Optional[str] = Query(None),
    has_artifacts: Optional[bool] = Query(None, description="Filter to opportunities with downloadable deliverables/technical reports"),
    has_winning_proposals: Optional[bool] = Query(None, description="Filter to opportunities with winning proposals / funded awards"),
    # New filters
    org_type: Optional[str] = Query(None),
    funding_type: Optional[str] = Query(None),
    is_historical: Optional[bool] = Query(None),
    year_min: Optional[int] = Query(None),
    year_max: Optional[int] = Query(None),
    amount_min: Optional[float] = Query(None),
    amount_max: Optional[float] = Query(None),
    technology: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    sort_by: str = Query("solicitation_number"),
    sort_dir: str = Query("desc"),
    exclude_nyserda: Optional[bool] = Query(None),
    x_include_nyserda: Optional[str] = Header(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all opportunities with optional filters."""
    status = status if isinstance(status, str) else None
    type = type if isinstance(type, str) else None
    search = search if isinstance(search, str) else None
    agency = agency if isinstance(agency, str) else None
    jurisdiction = jurisdiction if isinstance(jurisdiction, str) else None
    org_type = org_type if isinstance(org_type, str) else None
    funding_type = funding_type if isinstance(funding_type, str) else None
    is_historical = is_historical if isinstance(is_historical, bool) else None
    year_min = year_min if isinstance(year_min, int) else None
    year_max = year_max if isinstance(year_max, int) else None
    amount_min = amount_min if isinstance(amount_min, (int, float)) else None
    amount_max = amount_max if isinstance(amount_max, (int, float)) else None
    technology = technology if isinstance(technology, str) else None
    sector = sector if isinstance(sector, str) else None
    sort_by = sort_by if isinstance(sort_by, str) else "solicitation_number"
    sort_dir = sort_dir if isinstance(sort_dir, str) else "desc"
    page = page if isinstance(page, int) else 1
    page_size = page_size if isinstance(page_size, int) else 50

    query = db.query(Opportunity)

    if exclude_nyserda is True or x_include_nyserda == "false":
        query = query.filter(
            ~Opportunity.agency.ilike("%NYSERDA%"),
            ~Opportunity.source_name.ilike("%NYSERDA%"),
        )

    if status:
        query = query.filter(Opportunity.status == status)
    if type:
        query = query.filter(Opportunity.solicitation_type == type)
    if agency:
        query = query.filter(Opportunity.agency == agency)
    if jurisdiction and jurisdiction != "ALL":
        j_lower = jurisdiction.lower()
        if j_lower in ("ca", "state_ca", "california"):
            query = query.filter(Opportunity.jurisdiction.in_(["CA", "state_ca"]) | Opportunity.agency.ilike("%CEC%") | Opportunity.agency.ilike("%California%"))
        elif j_lower in ("ma", "state_ma", "massachusetts"):
            query = query.filter(Opportunity.jurisdiction.in_(["MA", "state_ma"]) | Opportunity.agency.ilike("%Mass%"))
        elif j_lower in ("ny", "state_ny", "new york", "nyserda"):
            query = query.filter(Opportunity.jurisdiction.in_(["NY", "state_ny", "utility_ny"]) | Opportunity.agency.ilike("%NYSERDA%") | Opportunity.agency.ilike("%New York%"))
        elif j_lower in ("us_fed", "fed", "federal", "national"):
            query = query.filter(Opportunity.jurisdiction.in_(["US_FED", "federal", "national"]))
        else:
            query = query.filter(Opportunity.jurisdiction == jurisdiction)
    if org_type:
        query = query.filter(Opportunity.org_type == org_type)
    if funding_type:
        query = query.filter(Opportunity.funding_type == funding_type)
    if is_historical is not None:
        query = query.filter(Opportunity.is_historical == is_historical)
    if year_min is not None:
        query = query.filter(Opportunity.year >= year_min)
    if year_max is not None:
        query = query.filter(Opportunity.year <= year_max)
    if amount_min is not None:
        query = query.filter(Opportunity.total_funding >= amount_min)
    if amount_max is not None:
        query = query.filter(Opportunity.total_funding <= amount_max)
    
    if has_artifacts is True:
        query = query.filter(Opportunity.id.in_(db.query(ResultArtifact.opportunity_id).filter(ResultArtifact.opportunity_id.isnot(None))))
    elif has_artifacts is False:
        query = query.filter(~Opportunity.id.in_(db.query(ResultArtifact.opportunity_id).filter(ResultArtifact.opportunity_id.isnot(None))))

    if has_winning_proposals is True:
        query = query.filter(Opportunity.id.in_(db.query(Award.opportunity_id).filter(Award.opportunity_id.isnot(None))))
    elif has_winning_proposals is False:
        query = query.filter(~Opportunity.id.in_(db.query(Award.opportunity_id).filter(Award.opportunity_id.isnot(None))))

    if technology or sector:
        query = query.join(Opportunity.categories)
        if technology:
            query = query.filter(
                OpportunityCategory.category_type == "technology",
                OpportunityCategory.category_value == technology
            )
        if sector:
            query = query.filter(
                OpportunityCategory.category_type == "sector",
                OpportunityCategory.category_value == sector
            )
            
    # Apply FTS / text search filter
    if search:
        is_postgres = db.bind.dialect.name == "postgresql" if db.bind else False
        if is_postgres:
            search_pattern = f"%{search.lower()}%"
            query = query.filter(
                func.lower(Opportunity.name).like(search_pattern) |
                func.lower(Opportunity.short_description).like(search_pattern) |
                func.lower(Opportunity.solicitation_number).like(search_pattern) |
                func.lower(Opportunity.agency).like(search_pattern)
            )
        else:
            try:
                with db.begin_nested():
                    result = db.execute(
                        text("SELECT rowid FROM opportunities_fts WHERE opportunities_fts MATCH :q"),
                        {"q": search},
                    ).fetchall()
                    fts_ids = {r[0] for r in result}
                    if fts_ids:
                        query = query.filter(Opportunity.id.in_(fts_ids))
                    else:
                        query = query.filter(Opportunity.id == -1)
            except Exception:
                search_lower = f"%{search.lower()}%"
                query = query.filter(
                    func.lower(Opportunity.name).like(search_lower) |
                    func.lower(Opportunity.short_description).like(search_lower) |
                    func.lower(Opportunity.solicitation_number).like(search_lower)
                )


    # Sort
    if sort_by == "next_deadline":
        # next_deadline is computed from the minimum open round due_date
        from sqlalchemy import select, func as sa_func
        next_dl_subq = (
            select(sa_func.min(OpportunityRound.due_date))
            .where(OpportunityRound.opportunity_id == Opportunity.id)
            .where(OpportunityRound.status == "Open")
            .correlate(Opportunity)
            .scalar_subquery()
        )
        if sort_dir.lower() == "desc":
            query = query.order_by(
                next_dl_subq.desc().nulls_last(),
                func.coalesce(Opportunity.total_funding, Opportunity.max_per_award, 0).desc().nulls_last()
            )
        else:
            query = query.order_by(
                next_dl_subq.asc().nulls_last(),
                func.coalesce(Opportunity.total_funding, Opportunity.max_per_award, 0).desc().nulls_last()
            )
    elif sort_by in ("recent", "recency", "most_recent", "solicitation_number", "default"):
        # Primary sort: Most recent to least recent (Open status first, year desc)
        # Secondary sort: Financial amount available / award size (total_funding / max_per_award desc, nulls last)
        if sort_dir.lower() == "asc":
            query = query.order_by(
                Opportunity.year.asc().nulls_last(),
                func.coalesce(Opportunity.total_funding, Opportunity.max_per_award, Opportunity.award_typical, 0).asc().nulls_last(),
                Opportunity.first_seen_at.asc().nulls_last(),
                Opportunity.id.asc()
            )
        else:
            query = query.order_by(
                case((Opportunity.status == "open", 1), else_=2),
                Opportunity.year.desc().nulls_last(),
                func.coalesce(Opportunity.total_funding, Opportunity.max_per_award, Opportunity.award_typical, 0).desc().nulls_last(),
                Opportunity.first_seen_at.desc().nulls_last(),
                Opportunity.id.desc()
            )
    elif sort_by in ("total_funding", "funding", "amount", "max_per_award"):
        if sort_dir.lower() == "asc":
            query = query.order_by(
                func.coalesce(Opportunity.total_funding, Opportunity.max_per_award, Opportunity.award_typical, 0).asc().nulls_last(),
                Opportunity.year.desc().nulls_last(),
                Opportunity.first_seen_at.desc().nulls_last(),
                Opportunity.id.desc()
            )
        else:
            query = query.order_by(
                func.coalesce(Opportunity.total_funding, Opportunity.max_per_award, Opportunity.award_typical, 0).desc().nulls_last(),
                case((Opportunity.status == "open", 1), else_=2),
                Opportunity.year.desc().nulls_last(),
                Opportunity.first_seen_at.desc().nulls_last(),
                Opportunity.id.desc()
            )

    elif sort_by in ("days_since_release", "days_old", "release_date", "age"):
        # Days since release: Ascending sort means newest release first (0 days, 1 day, 2 days...)
        # Descending sort means oldest release first
        rel_date_col = func.coalesce(
            Opportunity.open_date,
            Opportunity.first_seen_at,
            Opportunity.created_at
        )
        if sort_dir.lower() == "desc":
            # Oldest release first (highest days since release)
            query = query.order_by(
                Opportunity.year.asc().nulls_last(),
                rel_date_col.asc().nulls_last(),
                func.coalesce(Opportunity.total_funding, Opportunity.max_per_award, Opportunity.award_typical, 0).desc().nulls_last(),
                Opportunity.id.asc()
            )
        else:
            # Fewest days since release first (most recent)
            query = query.order_by(
                case((Opportunity.status == "open", 1), else_=2),
                Opportunity.year.desc().nulls_last(),
                rel_date_col.desc().nulls_last(),
                func.coalesce(Opportunity.total_funding, Opportunity.max_per_award, Opportunity.award_typical, 0).desc().nulls_last(),
                Opportunity.id.desc()
            )
    else:
        sort_col = getattr(Opportunity, sort_by, Opportunity.solicitation_number)
        if sort_dir.lower() == "desc":
            query = query.order_by(
                sort_col.desc().nulls_last(),
                func.coalesce(Opportunity.total_funding, Opportunity.max_per_award, 0).desc().nulls_last(),
                Opportunity.id.desc()
            )
        else:
            query = query.order_by(
                sort_col.asc().nulls_last(),
                func.coalesce(Opportunity.total_funding, Opportunity.max_per_award, 0).desc().nulls_last(),
                Opportunity.id.desc()
            )



    total = query.count()
    
    opportunities = (
        query.options(
            selectinload(Opportunity.rounds),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    
    opp_ids = [o.id for o in opportunities]
    awards_counts = {}
    artifacts_counts = {}
    restrictions_counts = {}
    if opp_ids:
        aw_rows = db.query(Award.opportunity_id, func.count(Award.id)).filter(Award.opportunity_id.in_(opp_ids)).group_by(Award.opportunity_id).all()
        for opp_id, cnt in aw_rows:
            awards_counts[opp_id] = cnt
            
        art_rows = db.query(ResultArtifact.opportunity_id, func.count(ResultArtifact.id)).filter(ResultArtifact.opportunity_id.in_(opp_ids)).group_by(ResultArtifact.opportunity_id).all()
        for opp_id, cnt in art_rows:
            artifacts_counts[opp_id] = cnt

        rest_rows = db.query(OpportunityRestriction.opportunity_id, func.count(OpportunityRestriction.id)).filter(OpportunityRestriction.opportunity_id.in_(opp_ids)).group_by(OpportunityRestriction.opportunity_id).all()
        for opp_id, cnt in rest_rows:
            restrictions_counts[opp_id] = cnt

    return {
        "items": [
            _opp_to_list_dict(
                o,
                awards_counts.get(o.id, 0),
                artifacts_counts.get(o.id, 0),
                restrictions_counts.get(o.id, 0),
            )
            for o in opportunities
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/opportunities/{opp_id}")
def get_opportunity(opp_id: int, db: Session = Depends(get_db)):
    """Get detailed opportunity information."""
    opp = (
        db.query(Opportunity)
        .options(
            selectinload(Opportunity.rounds),
            selectinload(Opportunity.contacts),
            selectinload(Opportunity.documents),
            selectinload(Opportunity.categories),
            selectinload(Opportunity.eligibility_rules),
            selectinload(Opportunity.restrictions),
        )
        .filter_by(id=opp_id)
        .first()
    )
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    result = _opp_to_dict(opp)

    # Extra fields the modal needs
    result["overview"] = getattr(opp, "objectives", None) or opp.short_description
    result["description"] = opp.short_description
    result["year"] = getattr(opp, "year", None)
    result["max_award"] = opp.max_per_award
    result["performance_period"] = getattr(opp, "performance_period", None)
    result["expected_awards"] = getattr(opp, "expected_awards", None)
    result["geographic_scope"] = getattr(opp, "geographic_scope", None)
    result["trl_min"] = getattr(opp, "target_trl_min", None)
    result["trl_max"] = getattr(opp, "target_trl_max", None)
    result["funding_type"] = getattr(opp, "funding_type", None)
    result["is_historical"] = getattr(opp, "is_historical", None)
    result["open_date"] = opp.open_date.isoformat() if getattr(opp, "open_date", None) else None
    result["close_date"] = opp.close_date.isoformat() if getattr(opp, "close_date", None) else None
    result["award_date"] = opp.award_date.isoformat() if getattr(opp, "award_date", None) else None
    result["source_url"] = getattr(opp, "source_url", None)

    # Awards count and total
    awards_stats = db.execute(text(
        "SELECT COUNT(*), COALESCE(SUM(award_amount), 0) FROM awards WHERE opportunity_id = :oid"
    ), {"oid": opp_id}).fetchone()
    result["awards_count"] = awards_stats[0] if awards_stats else 0
    result["total_awarded"] = awards_stats[1] if awards_stats else 0

    # Relationships
    rels_out = db.execute(text("""
        SELECT r.target_opp_id, r.relationship_type, r.confidence, o.name
        FROM opportunity_relationships r
        JOIN opportunities o ON o.id = r.target_opp_id
        WHERE r.source_opp_id = :oid LIMIT 20
    """), {"oid": opp_id}).fetchall()
    rels_in = db.execute(text("""
        SELECT r.source_opp_id, r.relationship_type, r.confidence, o.name
        FROM opportunity_relationships r
        JOIN opportunities o ON o.id = r.source_opp_id
        WHERE r.target_opp_id = :oid LIMIT 20
    """), {"oid": opp_id}).fetchall()
    result["relationships"] = [
        {"id": r[0], "relationship_type": r[1], "confidence": r[2], "name": r[3], "direction": "outbound"}
        for r in rels_out
    ] + [
        {"id": r[0], "relationship_type": r[1], "confidence": r[2], "name": r[3], "direction": "inbound"}
        for r in rels_in
    ]

    # Add change history
    changes = (
        db.query(ChangeEvent)
        .filter_by(entity_type="opportunity", entity_id=opp.solicitation_number)
        .order_by(ChangeEvent.detected_at.desc())
        .limit(20)
        .all()
    )
    result["changes"] = [
        {
            "type": c.change_type,
            "field": c.field_name,
            "old_value": c.old_value,
            "new_value": c.new_value,
            "detected_at": c.detected_at.isoformat(),
        }
        for c in changes
    ]

    # Add conflicts
    conflicts = (
        db.query(SourceConflict)
        .filter_by(entity_type="opportunity", entity_id=opp.solicitation_number, resolved=False)
        .all()
    )
    result["conflicts"] = [
        {
            "field": c.field_name,
            "value_a": c.value_a,
            "source_a": c.source_a,
            "value_b": c.value_b,
            "source_b": c.source_b,
        }
        for c in conflicts
    ]

    return result


@router.get("/opportunities/{opp_id}/win-rate-benchmark")
def get_opportunity_win_rate_benchmark(opp_id: int, db: Session = Depends(get_db)):
    """Get empirical predictive win-rate & competitiveness benchmark for a specific opportunity."""
    from app.engine.win_rate_engine import calculate_win_rate_analytics
    
    opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    return calculate_win_rate_analytics(
        db=db,
        opp=opp,
        fit_score=0.75,
    )
