"""Awards & Results API endpoints."""

import json
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, Header
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.cache_utils import TTLCache

router = APIRouter()

_award_stats_cache = TTLCache(ttl_seconds=300.0)
_recip_map_cache = TTLCache(ttl_seconds=300.0)


def _award_to_dict(row) -> dict:
    """Convert a raw row to dict."""
    cols = [
        "id", "opportunity_id", "external_award_id",
        "recipient_name", "recipient_type", "recipient_city", "recipient_state",
        "recipient_zip", "recipient_country", "recipient_uei",
        "pi_name", "pi_email", "pi_institution",
        "award_amount", "total_estimated", "cost_share_amount",
        "start_date", "end_date", "award_date",
        "project_title", "project_abstract",
        "award_type", "cfda_number", "cfda_title",
        "program_name", "program_office", "agency",
        "source_name", "source_url", "year",
        "latitude", "longitude", "artifacts_count",
    ]
    d = {}
    for i, col in enumerate(cols):
        if i < len(row):
            d[col] = row[i]
    d["artifacts_count"] = d.get("artifacts_count") or 0
    d["has_artifacts"] = d["artifacts_count"] > 0
    d["has_winning_proposal"] = bool(d.get("project_title") or d.get("award_amount"))
    d["proposal_id"] = f"prop-awd-{d['id']}" if d.get("id") else None
    return d



@router.get("/awards")
def list_awards(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, le=200),
    agency: Optional[str] = None,
    recipient: Optional[str] = None,
    recipient_type: Optional[str] = None,
    state: Optional[str] = None,
    technology: Optional[str] = None,
    sector: Optional[str] = None,
    fuel: Optional[str] = None,
    stage: Optional[str] = None,
    has_artifacts: Optional[bool] = Query(None, description="Filter to awards with downloadable artifacts/deliverables"),
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    award_type: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("award_amount", pattern="^(recipient_name|award_amount|year|agency|pi_name|start_date)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    exclude_nyserda: Optional[bool] = Query(None),
    x_include_nyserda: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Paginated, filterable award listing across all dimensions."""
    base_where = []
    params = {}

    if exclude_nyserda is True or x_include_nyserda == "false":
        base_where.append("(a.agency NOT LIKE '%NYSERDA%' AND a.source_name NOT LIKE '%NYSERDA%')")

    if agency:
        ag_list = [a.strip() for a in agency.split(",") if a.strip()]
        if len(ag_list) == 1:
            base_where.append("a.agency = :agency")
            params["agency"] = ag_list[0]
        elif len(ag_list) > 1:
            placeholders = [f":ag_{i}" for i in range(len(ag_list))]
            base_where.append(f"a.agency IN ({','.join(placeholders)})")
            for i, ag in enumerate(ag_list):
                params[f"ag_{i}"] = ag

    if recipient:
        base_where.append("a.recipient_name LIKE :recipient")
        params["recipient"] = f"%{recipient}%"

    if recipient_type:
        rt_list = [r.strip().lower() for r in recipient_type.split(",") if r.strip()]
        if len(rt_list) == 1:
            base_where.append("LOWER(a.recipient_type) = :recipient_type")
            params["recipient_type"] = rt_list[0]
        elif len(rt_list) > 1:
            placeholders = [f":rt_{i}" for i in range(len(rt_list))]
            base_where.append(f"LOWER(a.recipient_type) IN ({','.join(placeholders)})")
            for i, rt in enumerate(rt_list):
                params[f"rt_{i}"] = rt

    if state:
        st_list = [s.strip().upper() for s in state.split(",") if s.strip()]
        if len(st_list) == 1:
            base_where.append("a.recipient_state = :state")
            params["state"] = st_list[0]
        elif len(st_list) > 1:
            placeholders = [f":st_{i}" for i in range(len(st_list))]
            base_where.append(f"a.recipient_state IN ({','.join(placeholders)})")
            for i, st in enumerate(st_list):
                params[f"st_{i}"] = st

    if technology:
        tech_list = [t.strip() for t in technology.split(",") if t.strip()]
        if len(tech_list) == 1:
            base_where.append("a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'technology' AND category_value = :technology)")
            params["technology"] = tech_list[0]
        else:
            placeholders = [f":tech_{i}" for i in range(len(tech_list))]
            base_where.append(f"a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'technology' AND category_value IN ({','.join(placeholders)}))")
            for i, t in enumerate(tech_list):
                params[f"tech_{i}"] = t

    if sector:
        sec_list = [s.strip() for s in sector.split(",") if s.strip()]
        if len(sec_list) == 1:
            base_where.append("a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'sector' AND category_value = :sector)")
            params["sector"] = sec_list[0]
        else:
            placeholders = [f":sec_{i}" for i in range(len(sec_list))]
            base_where.append(f"a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'sector' AND category_value IN ({','.join(placeholders)}))")
            for i, s in enumerate(sec_list):
                params[f"sec_{i}"] = s

    if fuel:
        fuel_list = [f.strip() for f in fuel.split(",") if f.strip()]
        if len(fuel_list) == 1:
            base_where.append("a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'fuel' AND category_value = :fuel)")
            params["fuel"] = fuel_list[0]
        else:
            placeholders = [f":fuel_{i}" for i in range(len(fuel_list))]
            base_where.append(f"a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'fuel' AND category_value IN ({','.join(placeholders)}))")
            for i, f in enumerate(fuel_list):
                params[f"fuel_{i}"] = f

    if stage:
        stage_list = [s.strip() for s in stage.split(",") if s.strip()]
        if len(stage_list) == 1:
            base_where.append("a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'activity' AND category_value = :stage)")
            params["stage"] = stage_list[0]
        else:
            placeholders = [f":stage_{i}" for i in range(len(stage_list))]
            base_where.append(f"a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'activity' AND category_value IN ({','.join(placeholders)}))")
            for i, s in enumerate(stage_list):
                params[f"stage_{i}"] = s

    if year_min:
        base_where.append("a.year >= :year_min")
        params["year_min"] = year_min
    if year_max:
        base_where.append("a.year <= :year_max")
        params["year_max"] = year_max
    if amount_min:
        base_where.append("a.award_amount >= :amount_min")
        params["amount_min"] = amount_min
    if amount_max:
        base_where.append("a.award_amount <= :amount_max")
        params["amount_max"] = amount_max
    if has_artifacts is True:
        base_where.append("a.id IN (SELECT award_id FROM result_artifacts WHERE award_id IS NOT NULL)")
    elif has_artifacts is False:
        base_where.append("a.id NOT IN (SELECT award_id FROM result_artifacts WHERE award_id IS NOT NULL)")
    if award_type:
        base_where.append("a.award_type = :award_type")
        params["award_type"] = award_type
    if search:
        base_where.append("(a.recipient_name LIKE :search OR a.pi_name LIKE :search OR a.project_title LIKE :search OR a.project_abstract LIKE :search)")
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(base_where) if base_where else "1=1"

    # Count
    count_sql = f"SELECT COUNT(*) FROM awards a WHERE {where_clause}"
    total = db.execute(text(count_sql), params).scalar()

    # Query
    select_cols = """a.id, a.opportunity_id, a.external_award_id,
        a.recipient_name, a.recipient_type, a.recipient_city, a.recipient_state,
        a.recipient_zip, a.recipient_country, a.recipient_uei,
        a.pi_name, a.pi_email, a.pi_institution,
        a.award_amount, a.total_estimated, a.cost_share_amount,
        a.start_date, a.end_date, a.award_date,
        a.project_title, a.project_abstract,
        a.award_type, a.cfda_number, a.cfda_title,
        a.program_name, a.program_office, a.agency,
        a.source_name, a.source_url, a.year,
        a.latitude, a.longitude,
        (SELECT COUNT(*) FROM result_artifacts ra WHERE ra.award_id = a.id) AS artifacts_count"""

    safe_sort = sort_by if sort_by in ("recipient_name", "award_amount", "year", "agency", "pi_name", "start_date") else "award_amount"
    safe_dir = "ASC" if sort_dir == "asc" else "DESC"

    offset = (page - 1) * page_size
    data_sql = f"""SELECT {select_cols} FROM awards a
        WHERE {where_clause}
        ORDER BY a.{safe_sort} {safe_dir} NULLS LAST
        LIMIT :limit OFFSET :offset"""
    params["limit"] = page_size
    params["offset"] = offset

    rows = db.execute(text(data_sql), params).fetchall()

    return {
        "items": [_award_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


@router.get("/awards/stats")
def award_stats(db: Session = Depends(get_db)):
    """Aggregate award statistics with TTL in-memory caching."""
    cached = _award_stats_cache.get("stats")
    if cached is not None:
        return cached

    result = {}

    r = db.execute(text("SELECT COUNT(*), COALESCE(SUM(award_amount), 0), COUNT(DISTINCT recipient_name), COUNT(DISTINCT recipient_state) FROM awards")).fetchone()
    result["total_awards"] = r[0]
    result["total_funding"] = r[1]
    result["unique_recipients"] = r[2]
    result["states_covered"] = r[3]

    # By agency
    rows = db.execute(text("SELECT agency, COUNT(*), COALESCE(SUM(award_amount), 0) FROM awards GROUP BY agency ORDER BY COUNT(*) DESC")).fetchall()
    result["by_agency"] = [{"agency": a, "count": c, "total_funding": f} for a, c, f in rows]

    # By year
    rows = db.execute(text("SELECT year, COUNT(*), COALESCE(SUM(award_amount), 0) FROM awards WHERE year IS NOT NULL GROUP BY year ORDER BY year")).fetchall()
    result["by_year"] = [{"year": y, "count": c, "total_funding": f} for y, c, f in rows]

    # By recipient type
    rows = db.execute(text("SELECT recipient_type, COUNT(*), COALESCE(SUM(award_amount), 0) FROM awards WHERE recipient_type IS NOT NULL GROUP BY recipient_type ORDER BY COUNT(*) DESC")).fetchall()
    result["by_recipient_type"] = [{"type": t, "count": c, "total_funding": f} for t, c, f in rows]

    # By state (top 20)
    rows = db.execute(text("SELECT recipient_state, COUNT(*), COALESCE(SUM(award_amount), 0) FROM awards WHERE recipient_state IS NOT NULL GROUP BY recipient_state ORDER BY COUNT(*) DESC LIMIT 20")).fetchall()
    result["by_state"] = [{"state": s, "count": c, "total_funding": f} for s, c, f in rows]

    # Top recipients
    rows = db.execute(text("SELECT recipient_name, COUNT(*), COALESCE(SUM(award_amount), 0), MAX(recipient_type) FROM awards WHERE recipient_name IS NOT NULL GROUP BY recipient_name ORDER BY COUNT(*) DESC LIMIT 20")).fetchall()
    result["top_recipients"] = [{"name": n, "count": c, "total_funding": f, "type": t} for n, c, f, t in rows]

    _award_stats_cache.set("stats", result)
    return result


@router.get("/awards/recipients")
def list_recipients(
    search: Optional[str] = None,
    agency: Optional[str] = None,
    recipient_type: Optional[str] = None,
    state: Optional[str] = None,
    technology: Optional[str] = None,
    is_ny_only: Optional[bool] = None,
    nyserda_only: Optional[bool] = None,
    stage: Optional[str] = None,
    sort_by: str = Query("total_funding", pattern="^(award_count|total_funding|recipient_name|nyserda_funding)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    exclude_nyserda: Optional[bool] = Query(None),
    x_include_nyserda: Optional[str] = Header(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """List enriched awardee organizations with deep profiles, LLM research, and NYSERDA breakdown."""
    import json

    where_parts = []
    params = {}

    if exclude_nyserda is True or x_include_nyserda == "false":
        where_parts.append("(r.name NOT LIKE '%NYSERDA%' AND (r.funded_agencies NOT LIKE '%NYSERDA%' OR r.funded_agencies IS NULL))")

    if search:
        where_parts.append("(r.name LIKE :search OR r.headquarters_city LIKE :search OR r.description LIKE :search OR r.primary_technology LIKE :search)")
        params["search"] = f"%{search}%"

    if agency:
        ag_list = [a.strip() for a in agency.split(",") if a.strip()]
        if len(ag_list) == 1:
            where_parts.append("r.funded_agencies LIKE :agency")
            params["agency"] = f"%{ag_list[0]}%"
        elif len(ag_list) > 1:
            ag_sub = [f"r.funded_agencies LIKE :ag_{i}" for i in range(len(ag_list))]
            where_parts.append(f"({' OR '.join(ag_sub)})")
            for i, ag in enumerate(ag_list):
                params[f"ag_{i}"] = f"%{ag}%"

    if recipient_type:
        rt_list = [t.strip().lower() for t in recipient_type.split(",") if t.strip()]
        if len(rt_list) == 1:
            where_parts.append("LOWER(r.recipient_type) = :rtype")
            params["rtype"] = rt_list[0]
        elif len(rt_list) > 1:
            placeholders = [f":rt_{i}" for i in range(len(rt_list))]
            where_parts.append(f"LOWER(r.recipient_type) IN ({','.join(placeholders)})")
            for i, rt in enumerate(rt_list):
                params[f"rt_{i}"] = rt

    if state:
        st_list = [s.strip().upper() for s in state.split(",") if s.strip()]
        if len(st_list) == 1:
            where_parts.append("r.headquarters_state = :state")
            params["state"] = st_list[0]
        elif len(st_list) > 1:
            placeholders = [f":st_{i}" for i in range(len(st_list))]
            where_parts.append(f"r.headquarters_state IN ({','.join(placeholders)})")
            for i, st in enumerate(st_list):
                params[f"st_{i}"] = st

    if technology:
        where_parts.append("(r.primary_technology LIKE :tech OR r.technology_tags LIKE :tech)")
        params["tech"] = f"%{technology}%"

    if is_ny_only or (state and state.upper() == 'NY'):
        where_parts.append("(r.is_ny_based = TRUE OR r.headquarters_state = 'NY')")


    if nyserda_only:
        where_parts.append("r.total_nyserda_funding > 0")

    if stage:
        where_parts.append("r.commercialization_stage LIKE :stage")
        params["stage"] = f"%{stage}%"

    where_clause = " AND ".join(where_parts) if where_parts else "1=1"

    # Count
    count_sql = f"SELECT COUNT(*) FROM recipients r WHERE {where_clause}"
    total = db.execute(text(count_sql), params).scalar() or 0

    sort_map = {
        "total_funding": "r.total_funding_received",
        "award_count": "r.total_awards_count",
        "recipient_name": "r.name",
        "nyserda_funding": "r.total_nyserda_funding",
    }
    safe_sort = sort_map.get(sort_by, "r.total_funding_received")
    safe_dir = "ASC" if sort_dir == "asc" else "DESC"

    offset = (page - 1) * page_size
    data_sql = f"""
        SELECT 
            r.id, r.name, r.normalized_name, r.recipient_type, r.description,
            r.primary_technology, r.technology_tags, r.sector, r.commercialization_stage,
            r.headquarters_city, r.headquarters_state, r.headquarters_country,
            r.latitude, r.longitude, r.is_ny_based,
            r.website_url, r.founded_year, r.employee_range, r.leadership_team,
            r.total_awards_count, r.total_funding_received, r.total_nyserda_funding,
            r.nyserda_award_count, r.total_federal_funding, r.federal_award_count,
            r.funded_agencies, r.first_award_year, r.latest_award_year
        FROM recipients r
        WHERE {where_clause}
        ORDER BY {safe_sort} {safe_dir} NULLS LAST
        LIMIT :limit OFFSET :offset
    """
    params["limit"] = page_size
    params["offset"] = offset

    rows = db.execute(text(data_sql), params).fetchall()

    items = []
    for r in rows:
        tech_tags = []
        if r[6]:
            try:
                tech_tags = json.loads(r[6])
            except Exception:
                tech_tags = [r[5]] if r[5] else []
        
        leadership = []
        if r[18]:
            try:
                leadership = json.loads(r[18])
            except Exception:
                leadership = []

        agencies = [a.strip() for a in r[25].split(",") if a.strip()] if r[25] else []

        items.append({
            "id": r[0],
            "name": r[1],
            "normalized_name": r[2] or r[1],
            "type": r[3] or "company",
            "description": r[4] or "",
            "primary_technology": r[5] or "Clean Energy Innovation",
            "technology_tags": tech_tags,
            "sector": r[7] or "Energy & Infrastructure",
            "commercialization_stage": r[8] or "Applied R&D",
            "city": r[9] or "",
            "state": r[10] or "NY",
            "country": r[11] or "US",
            "lat": r[12],
            "lng": r[13],
            "is_ny_based": bool(r[14]),
            "website_url": r[15] or "",
            "founded_year": r[16],
            "employee_range": r[17] or "11-50",
            "leadership": leadership,
            "award_count": r[19] or 0,
            "total_funding": float(r[20] or 0.0),
            "nyserda_funding": float(r[21] or 0.0),
            "nyserda_award_count": r[22] or 0,
            "federal_funding": float(r[23] or 0.0),
            "federal_award_count": r[24] or 0,
            "agencies": agencies,
            "first_year": r[26],
            "last_year": r[27],
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


@router.get("/awards/recipients/map")
def recipients_map(
    search: Optional[str] = None,
    agency: Optional[str] = None,
    recipient_type: Optional[str] = None,
    state: Optional[str] = None,
    technology: Optional[str] = None,
    is_ny_only: Optional[bool] = None,
    nyserda_only: Optional[bool] = None,
    stage: Optional[str] = None,
    limit: int = Query(20000, le=50000),
    db: Session = Depends(get_db),
):
    """Geocoded awardee organization headquarters query for interactive map analysis."""
    is_default = not any([search, agency, recipient_type, state, technology, is_ny_only, nyserda_only, stage]) and limit >= 13000
    if is_default:
        cached_bytes = _recip_map_cache.get("default_map")
        if cached_bytes is not None:
            return Response(content=cached_bytes, media_type="application/json")

    where_parts = ["r.latitude IS NOT NULL", "r.longitude IS NOT NULL"]
    params = {}

    if search:
        where_parts.append("(r.name LIKE :search OR r.headquarters_city LIKE :search OR r.description LIKE :search)")
        params["search"] = f"%{search}%"

    if agency:
        ag_list = [a.strip() for a in agency.split(",") if a.strip()]
        if len(ag_list) == 1:
            where_parts.append("r.funded_agencies LIKE :agency")
            params["agency"] = f"%{ag_list[0]}%"
        elif len(ag_list) > 1:
            ag_sub = [f"r.funded_agencies LIKE :ag_{i}" for i in range(len(ag_list))]
            where_parts.append(f"({' OR '.join(ag_sub)})")
            for i, ag in enumerate(ag_list):
                params[f"ag_{i}"] = f"%{ag}%"

    if recipient_type:
        rt_list = [t.strip().lower() for t in recipient_type.split(",") if t.strip()]
        if len(rt_list) == 1:
            where_parts.append("LOWER(r.recipient_type) = :rtype")
            params["rtype"] = rt_list[0]
        elif len(rt_list) > 1:
            placeholders = [f":rt_{i}" for i in range(len(rt_list))]
            where_parts.append(f"LOWER(r.recipient_type) IN ({','.join(placeholders)})")
            for i, rt in enumerate(rt_list):
                params[f"rt_{i}"] = rt

    if state:
        st_list = [s.strip().upper() for s in state.split(",") if s.strip()]
        if len(st_list) == 1:
            where_parts.append("r.headquarters_state = :state")
            params["state"] = st_list[0]
        elif len(st_list) > 1:
            placeholders = [f":st_{i}" for i in range(len(st_list))]
            where_parts.append(f"r.headquarters_state IN ({','.join(placeholders)})")
            for i, st in enumerate(st_list):
                params[f"st_{i}"] = st

    if technology:
        where_parts.append("(r.primary_technology LIKE :tech OR r.technology_tags LIKE :tech)")
        params["tech"] = f"%{technology}%"

    if is_ny_only or (state and state.upper() == 'NY'):
        where_parts.append("(r.is_ny_based = TRUE OR r.headquarters_state = 'NY')")


    if nyserda_only:
        where_parts.append("r.total_nyserda_funding > 0")

    if stage:
        where_parts.append("r.commercialization_stage LIKE :stage")
        params["stage"] = f"%{stage}%"

    where_clause = " AND ".join(where_parts)

    sql = f"""
        SELECT 
            r.id, r.name, r.recipient_type, r.headquarters_city, r.headquarters_state,
            r.latitude, r.longitude, r.total_funding_received, r.total_nyserda_funding,
            r.total_awards_count, r.primary_technology, r.technology_tags,
            r.commercialization_stage, r.website_url, r.employee_range, r.description,
            r.is_ny_based, r.funded_agencies
        FROM recipients r
        WHERE {where_clause}
        ORDER BY r.total_funding_received DESC
        LIMIT :limit
    """
    params["limit"] = limit

    rows = db.execute(text(sql), params).fetchall()

    markers = []
    total_funding = 0.0
    for r in rows:
        tech_tags = []
        if r[11]:
            try:
                tech_tags = json.loads(r[11])
            except Exception:
                tech_tags = [r[10]] if r[10] else []

        funding = float(r[7] or 0.0)
        nyserda_funding = float(r[8] or 0.0)
        total_funding += funding

        agencies = [a.strip() for a in r[17].split(",") if a.strip()] if r[17] else []
        main_agency = "NYSERDA" if nyserda_funding > 0 else (agencies[0] if agencies else "Federal")

        markers.append({
            "id": r[0],
            "name": r[1],
            "type": r[2] or "company",
            "city": r[3] or "",
            "state": r[4] or "NY",
            "lat": float(r[5]),
            "lng": float(r[6]),
            "amount": funding,
            "nyserda_amount": nyserda_funding,
            "awards_count": r[9] or 1,
            "agency": main_agency,
            "agencies": agencies,
            "primary_technology": r[10] or "Clean Energy",
            "technologies": tech_tags,
            "stage": r[12] or "Applied R&D",
            "website": r[13] or "",
            "employees": r[14] or "11-50",
            "description": r[15] or "",
            "is_ny_based": bool(r[16]),
            "is_recipient": True,
        })

    result = {
        "markers": markers,
        "total": len(markers),
        "summary": {
            "total_funding": total_funding,
            "marker_count": len(markers),
            "unique_recipients": len(markers),
            "states_covered": len(set(m["state"] for m in markers if m["state"])),
            "by_agency": [],
            "top_states": [],
            "top_hubs": [],
        }
    }

    json_bytes = json.dumps(result).encode("utf-8")
    if is_default:
        _recip_map_cache.set("default_map", json_bytes)

    return Response(content=json_bytes, media_type="application/json")


@router.get("/awards/recipient/{recipient_id_or_name}")
def get_recipient_detail(
    recipient_id_or_name: str,
    db: Session = Depends(get_db),
):
    """Fetch complete single awardee organization dossier and award history."""
    import json

    is_id = recipient_id_or_name.isdigit()
    if is_id:
        sql = "SELECT * FROM recipients WHERE id = :query"
    else:
        sql = "SELECT * FROM recipients WHERE name = :query OR normalized_name = :query LIMIT 1"

    row = db.execute(text(sql), {"query": int(recipient_id_or_name) if is_id else recipient_id_or_name}).fetchone()

    if not row:
        return {"error": "Recipient not found"}

    rec_name = row[1]
    
    # Query all awards for this recipient
    award_rows = db.execute(text("""
        SELECT id, project_title, award_amount, agency, year, program_name, award_date, latitude, longitude
        FROM awards
        WHERE recipient_name = :name
        ORDER BY award_amount DESC LIMIT 50
    """), {"name": rec_name}).fetchall()

    awards_list = [{
        "id": a[0],
        "title": a[1],
        "amount": a[2],
        "agency": a[3],
        "year": a[4],
        "program": a[5],
        "date": a[6],
        "lat": a[7],
        "lng": a[8]
    } for a in award_rows]

    return {
        "id": row[0],
        "name": row[1],
        "normalized_name": row[2],
        "type": row[3],
        "description": row[4],
        "primary_technology": row[5],
        "technology_tags": json.loads(row[6]) if row[6] else [],
        "sector": row[7],
        "fuel_types": row[8],
        "commercialization_stage": row[9],
        "city": row[10],
        "state": row[11],
        "country": row[12],
        "address": row[13],
        "lat": row[14],
        "lng": row[15],
        "is_ny_based": bool(row[17]),
        "website_url": row[18],
        "founded_year": row[19],
        "employee_range": row[20],
        "leadership": json.loads(row[21]) if row[21] else [],
        "key_innovations": row[22],
        "diversity_certifications": row[23],
        "climate_impact": row[24],
        "total_awards_count": row[25],
        "total_funding_received": row[26],
        "total_state_funding": row[27],
        "state_award_count": row[28],
        "total_nyserda_funding": row[27],
        "nyserda_award_count": row[28],
        "total_federal_funding": row[29],
        "federal_award_count": row[30],
        "funded_agencies": row[31].split(",") if row[31] else [],
        "awards": awards_list,
    }


# In-memory cache for map filters and opportunity categories
_MAP_FILTERS_CACHE = None
_MAP_FILTERS_CACHE_TIME = 0
_ALL_OPP_CATS_CACHE = None
_ALL_OPP_CATS_CACHE_TIME = 0

# Approximate state centroids
STATE_CENTROIDS = {
    "AL": [32.806671, -86.791130], "AK": [61.370716, -152.404419], "AZ": [33.729759, -111.431221],
    "AR": [34.969704, -92.373123], "CA": [36.116203, -119.681564], "CO": [39.059811, -105.311104],
    "CT": [41.597782, -72.755371], "DE": [39.318523, -75.507141], "DC": [38.897438, -77.026817],
    "FL": [27.766279, -81.686783], "GA": [33.040619, -83.643074], "HI": [21.094318, -157.498337],
    "ID": [44.240459, -114.478828], "IL": [40.349457, -88.986137], "IN": [39.849426, -86.258278],
    "IA": [42.011539, -93.210526], "KS": [38.526600, -96.726486], "KY": [37.668140, -84.670067],
    "LA": [31.169546, -91.867805], "ME": [44.693947, -69.381927], "MD": [39.063946, -76.802101],
    "MA": [42.230171, -71.530106], "MI": [43.326618, -84.536095], "MN": [45.694454, -93.900192],
    "MS": [32.741646, -89.678696], "MO": [38.456085, -92.288368], "MT": [46.921925, -110.454353],
    "NE": [41.125370, -98.268082], "NV": [38.313515, -117.055374], "NH": [43.452492, -71.563896],
    "NJ": [40.298904, -74.521011], "NM": [34.840515, -106.248482], "NY": [42.165726, -74.948051],
    "NC": [35.630066, -79.806419], "ND": [47.528912, -99.784012], "OH": [40.388783, -82.764915],
    "OK": [35.565342, -96.928917], "OR": [44.572021, -122.070938], "PA": [40.590752, -77.209755],
    "RI": [41.680893, -71.511780], "SC": [33.856892, -80.945007], "SD": [44.299782, -99.438828],
    "TN": [35.747845, -86.692345], "TX": [31.054487, -97.563461], "UT": [40.150032, -111.862434],
    "VT": [44.045876, -72.710686], "VA": [37.769337, -78.169968], "WA": [47.400902, -121.490494],
    "WV": [38.491226, -80.954453], "WI": [44.268543, -89.616508], "WY": [42.755966, -107.302490],
    "PR": [18.220833, -66.590149],
}

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia",
    "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "PR": "Puerto Rico"
}


@router.get("/awards/map/filters")
def get_map_filters(db: Session = Depends(get_db)):
    """Return all available filter options with award counts."""
    global _MAP_FILTERS_CACHE, _MAP_FILTERS_CACHE_TIME
    import time
    if _MAP_FILTERS_CACHE and (time.time() - _MAP_FILTERS_CACHE_TIME < 300):
        return _MAP_FILTERS_CACHE

    # Category counts
    cat_rows = db.execute(text("""
        SELECT oc.category_type, oc.category_value, COUNT(DISTINCT a.id) as cnt
        FROM opportunity_categories oc
        JOIN awards a ON oc.opportunity_id = a.opportunity_id
        WHERE a.latitude IS NOT NULL AND oc.category_value != ''
        GROUP BY oc.category_type, oc.category_value
        ORDER BY oc.category_type, cnt DESC
    """)).fetchall()

    techs = []
    sectors = []
    fuels = []
    stages = []

    for ctype, cval, cnt in cat_rows:
        item = {"name": cval, "count": cnt}
        if ctype == "technology":
            techs.append(item)
        elif ctype == "sector":
            sectors.append(item)
        elif ctype == "fuel":
            fuels.append(item)
        elif ctype == "activity":
            stages.append(item)

    # Agency counts
    agency_rows = db.execute(text("""
        SELECT agency, COUNT(*), COALESCE(SUM(award_amount), 0)
        FROM awards WHERE latitude IS NOT NULL
        GROUP BY agency ORDER BY COUNT(*) DESC
    """)).fetchall()
    agencies = [{"agency": r[0], "count": r[1], "total_funding": r[2]} for r in agency_rows]

    # Recipient types
    rtype_rows = db.execute(text("""
        SELECT recipient_type, COUNT(*), COALESCE(SUM(award_amount), 0)
        FROM awards WHERE latitude IS NOT NULL AND recipient_type IS NOT NULL
        GROUP BY recipient_type ORDER BY COUNT(*) DESC
    """)).fetchall()
    recipient_types = [{"type": r[0], "count": r[1], "total_funding": r[2]} for r in rtype_rows]

    # Award types
    atype_rows = db.execute(text("""
        SELECT award_type, COUNT(*)
        FROM awards WHERE latitude IS NOT NULL AND award_type IS NOT NULL
        GROUP BY award_type ORDER BY COUNT(*) DESC
    """)).fetchall()
    award_types = [{"type": r[0], "count": r[1]} for r in atype_rows]

    # States
    state_rows = db.execute(text("""
        SELECT recipient_state, COUNT(*), COALESCE(SUM(award_amount), 0)
        FROM awards WHERE latitude IS NOT NULL AND recipient_state IS NOT NULL
        GROUP BY recipient_state ORDER BY recipient_state
    """)).fetchall()
    states = [{
        "code": r[0],
        "name": STATE_NAMES.get(r[0], r[0]),
        "count": r[1],
        "total_funding": r[2],
    } for r in state_rows if r[0]]

    # Year & Amount ranges
    range_row = db.execute(text("""
        SELECT MIN(year), MAX(year), MIN(award_amount), MAX(award_amount)
        FROM awards WHERE latitude IS NOT NULL
    """)).fetchone()

    res = {
        "agencies": agencies,
        "technologies": techs,
        "sectors": sectors,
        "fuels": fuels,
        "stages": stages,
        "recipient_types": recipient_types,
        "award_types": award_types,
        "states": states,
        "year_range": {"min": range_row[0] or 2000, "max": range_row[1] or 2026},
        "amount_range": {"min": range_row[2] or 0, "max": range_row[3] or 100000000},
    }

    _MAP_FILTERS_CACHE = res
    _MAP_FILTERS_CACHE_TIME = time.time()
    return res


_MAP_STATE_SUMMARY_CACHE = None
_MAP_STATE_SUMMARY_CACHE_TIME = 0

@router.get("/awards/map/state-summary")
def get_map_state_summary(db: Session = Depends(get_db)):
    """Return state-by-state funding and award aggregates for choropleth mapping."""
    global _MAP_STATE_SUMMARY_CACHE, _MAP_STATE_SUMMARY_CACHE_TIME
    import time
    if _MAP_STATE_SUMMARY_CACHE and (time.time() - _MAP_STATE_SUMMARY_CACHE_TIME < 300):
        return _MAP_STATE_SUMMARY_CACHE

    rows = db.execute(text("""
        SELECT a.recipient_state,
               COUNT(a.id) as award_count,
               COALESCE(SUM(a.award_amount), 0) as total_funding,
               COUNT(DISTINCT a.recipient_name) as recipient_count,
               AVG(a.latitude) as avg_lat,
               AVG(a.longitude) as avg_lng
        FROM awards a
        WHERE a.latitude IS NOT NULL AND a.recipient_state IS NOT NULL
        GROUP BY a.recipient_state
        ORDER BY total_funding DESC
    """)).fetchall()

    states_res = []
    for r in rows:
        st_code = r[0]
        if not st_code:
            continue
        centroid = STATE_CENTROIDS.get(st_code, [r[4] or 39.8, r[5] or -98.5])
        states_res.append({
            "state": st_code,
            "state_name": STATE_NAMES.get(st_code, st_code),
            "award_count": r[1],
            "total_funding": float(r[2]),
            "recipient_count": r[3],
            "lat": centroid[0],
            "lng": centroid[1],
        })

    _MAP_STATE_SUMMARY_CACHE = states_res
    _MAP_STATE_SUMMARY_CACHE_TIME = time.time()
    return states_res


_DEFAULT_AWARDS_MAP_CACHE = None
_DEFAULT_AWARDS_MAP_CACHE_TIME = 0
_DEFAULT_RECIP_MAP_CACHE = None
_DEFAULT_RECIP_MAP_CACHE_TIME = 0


@router.get("/awards/map")
def awards_map(
    agency: Optional[str] = None,
    recipient_type: Optional[str] = None,
    technology: Optional[str] = None,
    sector: Optional[str] = None,
    fuel: Optional[str] = None,
    stage: Optional[str] = None,
    program_name: Optional[str] = None,
    award_type: Optional[str] = None,
    state: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    search: Optional[str] = None,
    is_ny_only: Optional[bool] = None,
    nyserda_only: Optional[bool] = None,
    bbox: Optional[str] = None,  # min_lng,min_lat,max_lng,max_lat
    radius_lat: Optional[float] = None,
    radius_lng: Optional[float] = None,
    radius_miles: Optional[float] = None,
    limit: int = Query(60000, le=100000),
    db: Session = Depends(get_db),
):
    """Rich, high-performance geocoded awards query with multi-dimensional filtering and payload optimization."""
    import math
    import time
    global _DEFAULT_AWARDS_MAP_CACHE, _DEFAULT_AWARDS_MAP_CACHE_TIME

    is_default_query = not any([
        agency, recipient_type, technology, sector, fuel, stage, program_name,
        award_type, state, year_min, year_max, amount_min, amount_max, search,
        is_ny_only, nyserda_only, bbox, radius_lat, radius_lng, radius_miles
    ]) and limit >= 54000

    if is_default_query and _DEFAULT_AWARDS_MAP_CACHE and (time.time() - _DEFAULT_AWARDS_MAP_CACHE_TIME < 300):
        return Response(content=_DEFAULT_AWARDS_MAP_CACHE, media_type="application/json")

    where_parts = ["a.latitude IS NOT NULL", "a.longitude IS NOT NULL"]
    params: dict = {}

    if is_ny_only or (state and state.upper() == 'NY'):
        where_parts.append("(a.recipient_state = 'NY' OR a.recipient_state = 'New York')")

    if nyserda_only:
        where_parts.append("a.agency = 'NYSERDA'")

    # Support multiple comma-separated agencies
    if agency:
        ag_list = [a.strip() for a in agency.split(",") if a.strip()]
        if len(ag_list) == 1:
            where_parts.append("a.agency = :agency")
            params["agency"] = ag_list[0]
        elif len(ag_list) > 1:
            placeholders = [f":ag_{i}" for i in range(len(ag_list))]
            where_parts.append(f"a.agency IN ({','.join(placeholders)})")
            for i, ag in enumerate(ag_list):
                params[f"ag_{i}"] = ag

    if recipient_type:
        rt_list = [r.strip() for r in recipient_type.split(",") if r.strip()]
        if len(rt_list) == 1:
            where_parts.append("LOWER(a.recipient_type) = LOWER(:rtype)")
            params["rtype"] = rt_list[0]
        elif len(rt_list) > 1:
            placeholders = [f":rt_{i}" for i in range(len(rt_list))]
            where_parts.append(f"LOWER(a.recipient_type) IN ({','.join(placeholders)})")
            for i, rt in enumerate(rt_list):
                params[f"rt_{i}"] = rt.lower()

    if state and not is_ny_only:
        st_list = [s.strip().upper() for s in state.split(",") if s.strip()]
        if len(st_list) == 1:
            where_parts.append("a.recipient_state = :state")
            params["state"] = st_list[0]
        elif len(st_list) > 1:
            placeholders = [f":st_{i}" for i in range(len(st_list))]
            where_parts.append(f"a.recipient_state IN ({','.join(placeholders)})")
            for i, st in enumerate(st_list):
                params[f"st_{i}"] = st

    if award_type:
        where_parts.append("a.award_type = :award_type")
        params["award_type"] = award_type

    if program_name:
        where_parts.append("a.program_name LIKE :program_name")
        params["program_name"] = f"%{program_name}%"

    if year_min:
        where_parts.append("a.year >= :year_min")
        params["year_min"] = year_min
    if year_max:
        where_parts.append("a.year <= :year_max")
        params["year_max"] = year_max

    if amount_min:
        where_parts.append("a.award_amount >= :amount_min")
        params["amount_min"] = amount_min
    if amount_max:
        where_parts.append("a.award_amount <= :amount_max")
        params["amount_max"] = amount_max

    if search:
        where_parts.append("""
            (a.recipient_name LIKE :search 
             OR a.pi_name LIKE :search 
             OR a.project_title LIKE :search 
             OR a.recipient_city LIKE :search
             OR a.project_abstract LIKE :search)
        """)
        params["search"] = f"%{search}%"

    # Category filters via subqueries for fast indexed lookup
    if technology:
        tech_list = [t.strip() for t in technology.split(",") if t.strip()]
        if len(tech_list) == 1:
            where_parts.append("a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'technology' AND category_value = :technology)")
            params["technology"] = tech_list[0]
        else:
            placeholders = [f":tech_{i}" for i in range(len(tech_list))]
            where_parts.append(f"a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'technology' AND category_value IN ({','.join(placeholders)}))")
            for i, t in enumerate(tech_list):
                params[f"tech_{i}"] = t

    if sector:
        sec_list = [s.strip() for s in sector.split(",") if s.strip()]
        if len(sec_list) == 1:
            where_parts.append("a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'sector' AND category_value = :sector)")
            params["sector"] = sec_list[0]
        else:
            placeholders = [f":sec_{i}" for i in range(len(sec_list))]
            where_parts.append(f"a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'sector' AND category_value IN ({','.join(placeholders)}))")
            for i, s in enumerate(sec_list):
                params[f"sec_{i}"] = s

    if fuel:
        fuel_list = [f.strip() for f in fuel.split(",") if f.strip()]
        if len(fuel_list) == 1:
            where_parts.append("a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'fuel' AND category_value = :fuel)")
            params["fuel"] = fuel_list[0]
        else:
            placeholders = [f":fuel_{i}" for i in range(len(fuel_list))]
            where_parts.append(f"a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'fuel' AND category_value IN ({','.join(placeholders)}))")
            for i, f in enumerate(fuel_list):
                params[f"fuel_{i}"] = f

    if stage:
        stage_list = [s.strip() for s in stage.split(",") if s.strip()]
        if len(stage_list) == 1:
            where_parts.append("a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'activity' AND category_value = :stage)")
            params["stage"] = stage_list[0]
        else:
            placeholders = [f":stage_{i}" for i in range(len(stage_list))]
            where_parts.append(f"a.opportunity_id IN (SELECT opportunity_id FROM opportunity_categories WHERE category_type = 'activity' AND category_value IN ({','.join(placeholders)}))")
            for i, s in enumerate(stage_list):
                params[f"stage_{i}"] = s

    # Spatial bounding box filter (min_lng,min_lat,max_lng,max_lat)
    if bbox:
        try:
            min_lng, min_lat, max_lng, max_lat = [float(x) for x in bbox.split(",")]
            where_parts.append("a.longitude >= :min_lng AND a.longitude <= :max_lng AND a.latitude >= :min_lat AND a.latitude <= :max_lat")
            params["min_lng"] = min_lng
            params["max_lng"] = max_lng
            params["min_lat"] = min_lat
            params["max_lat"] = max_lat
        except Exception:
            pass

    # Spatial radius filter
    if radius_lat is not None and radius_lng is not None and radius_miles and radius_miles > 0:
        dlat = radius_miles / 69.0
        dlng = radius_miles / max(0.1, 69.0 * math.cos(math.radians(radius_lat)))
        where_parts.append("""
            a.latitude BETWEEN :r_min_lat AND :r_max_lat
            AND a.longitude BETWEEN :r_min_lng AND :r_max_lng
        """)
        params["r_min_lat"] = radius_lat - dlat
        params["r_max_lat"] = radius_lat + dlat
        params["r_min_lng"] = radius_lng - dlng
        params["r_max_lng"] = radius_lng + dlng

    where_clause = " AND ".join(where_parts)

    # 1. Get filtered total count and total amount
    count_row = db.execute(text(f"""
        SELECT COUNT(*), COALESCE(SUM(a.award_amount), 0), COUNT(DISTINCT a.recipient_name), COUNT(DISTINCT a.recipient_state)
        FROM awards a WHERE {where_clause}
    """), params).fetchone()

    total_count = count_row[0]
    total_funding = float(count_row[1])
    unique_recipients = count_row[2]
    states_count = count_row[3]

    # 2. Get top breakdowns from the filtered slice
    by_agency_rows = db.execute(text(f"""
        SELECT a.agency, COUNT(*), COALESCE(SUM(a.award_amount), 0)
        FROM awards a WHERE {where_clause}
        GROUP BY a.agency ORDER BY COUNT(*) DESC LIMIT 10
    """), params).fetchall()
    by_agency = [{"agency": r[0], "count": r[1], "total_funding": float(r[2])} for r in by_agency_rows if r[0]]

    top_states_rows = db.execute(text(f"""
        SELECT a.recipient_state, COUNT(*), COALESCE(SUM(a.award_amount), 0)
        FROM awards a WHERE {where_clause} AND a.recipient_state IS NOT NULL
        GROUP BY a.recipient_state ORDER BY COUNT(*) DESC LIMIT 10
    """), params).fetchall()
    top_states = [{"state": r[0], "count": r[1], "total_funding": float(r[2])} for r in top_states_rows]

    top_hubs_rows = db.execute(text(f"""
        SELECT a.recipient_city, a.recipient_state, COUNT(*), COALESCE(SUM(a.award_amount), 0), AVG(a.latitude), AVG(a.longitude)
        FROM awards a WHERE {where_clause} AND a.recipient_city IS NOT NULL
        GROUP BY a.recipient_city, a.recipient_state ORDER BY COUNT(*) DESC LIMIT 8
    """), params).fetchall()
    top_hubs = [{"city": r[0], "state": r[1], "count": r[2], "total_funding": float(r[3]), "lat": r[4], "lng": r[5]} for r in top_hubs_rows]

    # 3. Fetch awards markers
    params["limit"] = limit
    rows = db.execute(text(f"""
        SELECT a.id, a.opportunity_id, a.recipient_name, a.recipient_type, a.recipient_city, a.recipient_state,
               a.latitude, a.longitude, a.award_amount, a.agency, a.year,
               a.project_title, a.pi_name, a.program_name
        FROM awards a WHERE {where_clause}
        ORDER BY a.award_amount DESC NULLS LAST
        LIMIT :limit
    """), params).fetchall()

    # 4. Fetch category tags for returned opportunity_ids using memory cache
    global _ALL_OPP_CATS_CACHE, _ALL_OPP_CATS_CACHE_TIME
    if not _ALL_OPP_CATS_CACHE or (time.time() - _ALL_OPP_CATS_CACHE_TIME > 300):
        c_rows = db.execute(text("""
            SELECT opportunity_id, category_type, category_value
            FROM opportunity_categories
            WHERE category_value != ''
        """)).fetchall()
        full_map = {}
        for oid, ctype, cval in c_rows:
            if oid not in full_map:
                full_map[oid] = {"technology": [], "sector": [], "fuel": [], "activity": []}
            if ctype in full_map[oid] and cval not in full_map[oid][ctype]:
                full_map[oid][ctype].append(cval)
        _ALL_OPP_CATS_CACHE = full_map
        _ALL_OPP_CATS_CACHE_TIME = time.time()

    cat_map = _ALL_OPP_CATS_CACHE or {}

    markers = []
    empty_cats = {"technology": [], "sector": [], "fuel": [], "activity": []}
    for r in rows:
        oid = r[1]
        cats = cat_map.get(oid, empty_cats)
        tech_list = cats["technology"]
        sec_list = cats["sector"]
        fuel_list = cats["fuel"]
        act_list = cats["activity"]

        markers.append({
            "id": r[0],
            "opportunity_id": oid,
            "name": r[2],
            "type": r[3] or "company",
            "city": r[4] or "",
            "state": r[5] or "",
            "lat": r[6],
            "lng": r[7],
            "amount": float(r[8]) if r[8] is not None else 0.0,
            "agency": r[9] or "Federal",
            "year": r[10],
            "title": r[11] or "",
            "pi": r[12] or "",
            "program": r[13] or "",
            "primary_technology": tech_list[0] if tech_list else "Clean Tech",
            "primary_sector": sec_list[0] if sec_list else None,
            "primary_fuel": fuel_list[0] if fuel_list else None,
            "stage": act_list[0] if act_list else None,
            "technologies": tech_list[:2],
            "sectors": sec_list[:1],
            "fuels": fuel_list[:1],
            "stages": act_list[:1],
        })

    response_data = {
        "markers": markers,
        "total": total_count,
        "summary": {
            "total_funding": total_funding,
            "marker_count": len(markers),
            "total_matches": total_count,
            "unique_recipients": unique_recipients,
            "states_covered": states_count,
            "by_agency": by_agency,
            "top_states": top_states,
            "top_hubs": top_hubs,
        },
    }

    json_bytes = json.dumps(response_data).encode("utf-8")
    if is_default_query:
        _DEFAULT_AWARDS_MAP_CACHE = json_bytes
        _DEFAULT_AWARDS_MAP_CACHE_TIME = time.time()

    return Response(content=json_bytes, media_type="application/json")



@router.get("/awards/{award_id}")
def get_award(award_id: int, db: Session = Depends(get_db)):
    """Get full award detail including linked opportunity."""
    select_cols = """a.id, a.opportunity_id, a.external_award_id,
        a.recipient_name, a.recipient_type, a.recipient_city, a.recipient_state,
        a.recipient_zip, a.recipient_country, a.recipient_uei,
        a.pi_name, a.pi_email, a.pi_institution,
        a.award_amount, a.total_estimated, a.cost_share_amount,
        a.start_date, a.end_date, a.award_date,
        a.project_title, a.project_abstract,
        a.award_type, a.cfda_number, a.cfda_title,
        a.program_name, a.program_office, a.agency,
        a.source_name, a.source_url, a.year,
        a.latitude, a.longitude"""

    row = db.execute(text(f"SELECT {select_cols} FROM awards a WHERE a.id = :id"), {"id": award_id}).fetchone()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Award not found")

    award = _award_to_dict(row)

    # Get linked opportunity name
    if award.get("opportunity_id"):
        opp = db.execute(text("SELECT name, solicitation_number, status, agency FROM opportunities WHERE id = :id"), {"id": award["opportunity_id"]}).fetchone()
        if opp:
            award["opportunity"] = {
                "id": award["opportunity_id"],
                "name": opp[0], "solicitation_number": opp[1],
                "status": opp[2], "agency": opp[3],
            }

    # Get results
    results = db.execute(text("SELECT id, result_type, title, description, doi, patent_number, url, authors, date, source_name FROM award_results WHERE award_id = :id"), {"id": award_id}).fetchall()
    award["results"] = [{
        "id": r[0], "result_type": r[1], "title": r[2], "description": r[3],
        "doi": r[4], "patent_number": r[5], "url": r[6], "authors": r[7],
        "date": r[8], "source_name": r[9],
    } for r in results]

    return award
