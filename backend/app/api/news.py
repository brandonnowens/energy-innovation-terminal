"""
FastAPI Router for Bloomberg-Style Energy Innovation News Ticker & Database Linkages.
Exposes high-speed streaming ticker feed, entity-specific news queries, and manual sync endpoints.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.news_service import (
    get_news_ticker_items,
    get_news_item_detail,
    get_news_items_paginated,
    get_news_for_element,
    get_news_telemetry,
    run_news_ingestion_sync
)

router = APIRouter(prefix="/news", tags=["Energy Innovation News Ticker"])


@router.get("/ticker")
def get_ticker_feed(
    limit: int = Query(25, ge=1, le=100, description="Number of items to stream in ticker"),
    db: Session = Depends(get_db)
):
    """
    Returns high-speed stream of latest energy innovation news for the Bloomberg-style ticker tape.
    Includes sentiment badges and top database entity linkage pills.
    """
    items = get_news_ticker_items(db, limit=limit)
    return {
        "count": len(items),
        "items": items,
        "mode": "live_wire",
        "cadence": "daily_sync"
    }


@router.get("")
def list_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by category tag"),
    search: Optional[str] = Query(None, description="Search keyword in title, summary, or source"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment tag"),
    element_type: Optional[str] = Query(None, description="Filter by linked element type (opportunity, org, tech, policy)"),
    element_id: Optional[str] = Query(None, description="Filter by linked element ID"),
    db: Session = Depends(get_db)
):
    """Paginated search across the persistent clean energy news archive."""
    return get_news_items_paginated(
        db=db,
        page=page,
        page_size=page_size,
        category=category,
        search=search,
        sentiment=sentiment,
        element_type=element_type,
        element_id=element_id
    )


@router.get("/stats")
def get_news_statistics(db: Session = Depends(get_db)):
    """Returns database telemetry, total news records, sources, and explicit linkage counts."""
    return get_news_telemetry(db)


@router.get("/element/{element_type}/{element_id}")
def get_element_news(
    element_type: str,
    element_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Returns all clean tech news items explicitly linked to a specific database element."""
    return {
        "element_type": element_type,
        "element_id": element_id,
        "news": get_news_for_element(db, element_type=element_type, element_id=element_id, limit=limit)
    }


@router.get("/{news_id}")
def get_news_detail(news_id: int, db: Session = Depends(get_db)):
    """
    Returns full details for a news item, including LLM executive summary,
    original article metadata, and all explicit database entity linkages with navigation routes.
    """
    item = get_news_item_detail(db, news_id=news_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"News item #{news_id} not found")
    return item


@router.post("/ingest")
def trigger_news_ingestion(
    background_tasks: BackgroundTasks,
    force_seed: bool = Query(True, description="Ensure baseline verified records are ingested"),
    db: Session = Depends(get_db)
):
    """Admin / Automated endpoint to trigger on-demand daily news ingestion run."""
    stats = run_news_ingestion_sync(db, force_seed=force_seed)
    return {
        "status": "success",
        "message": "Daily news ingestion executed successfully",
        "telemetry": stats
    }
