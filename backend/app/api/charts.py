"""Charts API endpoints."""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models.community import SavedChart
from app.api.community import require_creator_hash
from pydantic import BaseModel
import csv
import io
import json

router = APIRouter()

class ChartDataRequest(BaseModel):
    metric: str
    group_by: str
    filters: Optional[Dict[str, Any]] = None
    sort: Optional[str] = None
    limit: Optional[int] = 100

class ChartSaveRequest(BaseModel):
    title: str
    chart_type: str
    config_json: Dict[str, Any]
    data_query: str
    filters_json: Optional[Dict[str, Any]] = None

@router.post("/charts/data")
def get_chart_data(req: ChartDataRequest, x_include_nyserda: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Dynamic SQL aggregation across opportunities and awards tables."""
    metric = req.metric or "funding"
    group_by = req.group_by or "year"
    limit = req.limit or 100
    is_ex = (req.filters and req.filters.get("exclude_nyserda") is True) or x_include_nyserda == "false"

    # If querying award metrics
    if metric in ("award_amount", "awards_count", "recipients"):
        col_map = {
            "year": "a.year",
            "agency": "a.agency",
            "state": "a.recipient_state",
            "recipient_type": "a.recipient_type",
            "recipient": "a.recipient_name",
        }
        group_col = col_map.get(group_by, "a.year")
        agg = "COALESCE(SUM(a.award_amount), 0)" if metric == "award_amount" else "COUNT(a.id)"
        ex_clause = "AND a.agency NOT LIKE '%NYSERDA%' AND a.source_name NOT LIKE '%NYSERDA%'" if is_ex else ""
        sql = f"""
            SELECT {group_col} as label, {agg} as value, COUNT(a.id) as count
            FROM awards a
            WHERE {group_col} IS NOT NULL AND {group_col} != '' {ex_clause}
            GROUP BY {group_col}
            ORDER BY value DESC
            LIMIT :limit
        """
        rows = db.execute(text(sql), {"limit": limit}).fetchall()
        return [{"label": str(r[0]), "value": float(r[1]) if r[1] else 0.0, "count": r[2]} for r in rows]

    # Otherwise aggregate from opportunities
    col_map = {
        "year": "o.year",
        "agency": "o.agency",
        "jurisdiction": "o.jurisdiction",
        "status": "o.status",
        "org_type": "o.org_type",
        "funding_type": "o.funding_type",
    }
    group_col = col_map.get(group_by, "o.year")
    agg = "COALESCE(SUM(o.total_funding), 0)" if metric == "funding" else "COUNT(o.id)"
    ex_clause = "AND o.agency NOT LIKE '%NYSERDA%' AND o.source_name NOT LIKE '%NYSERDA%'" if is_ex else ""
    sql = f"""
        SELECT {group_col} as label, {agg} as value, COUNT(o.id) as count
        FROM opportunities o
        WHERE {group_col} IS NOT NULL AND {group_col} != '' {ex_clause}
        GROUP BY {group_col}
        ORDER BY value DESC
        LIMIT :limit
    """
    rows = db.execute(text(sql), {"limit": limit}).fetchall()
    return [{"label": str(r[0]), "value": float(r[1]) if r[1] else 0.0, "count": r[2]} for r in rows]


@router.post("/charts/save")
def save_chart(req: ChartSaveRequest, creator_hash: str = Depends(require_creator_hash), db: Session = Depends(get_db)):
    c = SavedChart(
        creator_hash=creator_hash,
        title=req.title,
        chart_type=req.chart_type,
        config_json=req.config_json,
        data_query=req.data_query,
        filters_json=req.filters_json
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.get("/charts/saved")
def list_saved_charts(creator_hash: str = Depends(require_creator_hash), db: Session = Depends(get_db)):
    charts = db.query(SavedChart).filter_by(creator_hash=creator_hash).all()
    return charts

@router.post("/charts/export/csv")
def export_chart_csv():
    """Bulk CSV chart export is disabled."""
    raise HTTPException(
        status_code=403,
        detail="Raw CSV dataset export is disabled. Please use high-resolution chart image and PDF publication exports."
    )

@router.post("/charts/export/json")
def export_chart_json():
    """Raw JSON chart export is disabled."""
    raise HTTPException(
        status_code=403,
        detail="Raw JSON dataset export is disabled. Please use high-resolution chart image and PDF publication exports."
    )
