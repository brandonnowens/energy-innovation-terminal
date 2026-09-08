"""
News Service and 24-Hour Daily Periodic Ingestion Scheduler.
Orchestrates high-frequency query caching, database linkage retrieval, and background sync.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_

from app.database import SessionLocal
from app.models.news import NewsItem, NewsItemLink
from app.ingest.news_adapter import ingest_daily_energy_news
from app.engine.news_linker import clean_and_shorten_headline

logger = logging.getLogger("NewsService")

# Ingestion Telemetry State
_LAST_INGESTION_STATS: Dict[str, Any] = {
    "last_run_at": None,
    "items_added": 0,
    "links_created": 0,
    "status": "idle"
}
_SCHEDULER_TASK: Optional[asyncio.Task] = None


def run_news_ingestion_sync(db: Optional[Session] = None, force_seed: bool = True) -> Dict[str, Any]:
    """Triggers a synchronous daily news ingestion run and updates telemetry."""
    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        _LAST_INGESTION_STATS["status"] = "running"
        stats = ingest_daily_energy_news(db, force_seed_baseline=force_seed)
        _LAST_INGESTION_STATS["last_run_at"] = datetime.utcnow().isoformat()
        _LAST_INGESTION_STATS["items_added"] = stats.get("new_items_persisted", 0)
        _LAST_INGESTION_STATS["links_created"] = stats.get("total_links_created", 0)
        _LAST_INGESTION_STATS["status"] = "success"
        _LAST_INGESTION_STATS["details"] = stats
        return stats
    except Exception as e:
        logger.error(f"Error executing news ingestion: {e}")
        _LAST_INGESTION_STATS["status"] = "error"
        _LAST_INGESTION_STATS["error"] = str(e)
        return {"status": "error", "message": str(e)}
    finally:
        if owns_session:
            db.close()


def get_news_ticker_items(db: Session, limit: int = 25) -> List[Dict[str, Any]]:
    """
    Returns lightweight ticker feed payload optimized for continuous horizontal marquee scroller.
    Includes top entity linkage badge and sentiment pill.
    """
    items = (
        db.query(NewsItem)
        .filter(NewsItem.is_active == True)
        .order_by(desc(NewsItem.published_at))
        .limit(limit)
        .all()
    )

    results = []
    now = datetime.utcnow()

    for item in items:
        # Calculate human-friendly relative time
        delta = now - (item.published_at or now)
        if delta.days > 0:
            time_ago = f"{delta.days}d ago"
        elif delta.seconds >= 3600:
            time_ago = f"{delta.seconds // 3600}h ago"
        elif delta.seconds >= 60:
            time_ago = f"{delta.seconds // 60}m ago"
        else:
            time_ago = "just now"

        # Find primary database linkage
        top_link = None
        if item.links:
            primary = item.links[0]
            top_link = {
                "element_type": primary.element_type,
                "element_id": primary.element_id,
                "element_title": primary.element_title,
                "element_url_path": primary.element_url_path,
                "link_rationale": primary.link_rationale
            }

        # Ensure title is cleaned and shortened
        display_title = clean_and_shorten_headline(item.title, item.raw_content or "", item.source_name)

        results.append({
            "id": item.id,
            "title": display_title or item.title,
            "url": item.url,
            "source_name": item.source_name,
            "source_domain": item.source_domain,
            "published_at": item.published_at.isoformat() if item.published_at else None,
            "time_ago": time_ago,
            "summary": item.summary,
            "sentiment": item.sentiment,
            "category_tag": item.category_tag,
            "relevance_score": item.relevance_score,
            "primary_link": top_link,
            "total_links_count": len(item.links)
        })

    return results


def get_news_item_detail(db: Session, news_id: int) -> Optional[Dict[str, Any]]:
    """Returns detailed news item record with full LLM summary and all explicit database links."""
    item = db.query(NewsItem).filter_by(id=news_id).first()
    if not item:
        return None

    links = []
    for l in item.links:
        links.append({
            "id": l.id,
            "element_type": l.element_type,
            "element_id": l.element_id,
            "element_title": l.element_title,
            "element_url_path": l.element_url_path,
            "link_rationale": l.link_rationale,
            "confidence_score": l.confidence_score,
            "created_at": l.created_at.isoformat() if l.created_at else None
        })

    return {
        "id": item.id,
        "title": item.title,
        "url": item.url,
        "canonical_url": item.canonical_url,
        "source_name": item.source_name,
        "source_domain": item.source_domain,
        "published_at": item.published_at.isoformat() if item.published_at else None,
        "author": item.author,
        "raw_content": item.raw_content,
        "summary": item.summary,
        "sentiment": item.sentiment,
        "relevance_score": item.relevance_score,
        "category_tag": item.category_tag,
        "is_active": item.is_active,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "links": links
    }


def get_news_items_paginated(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
    sentiment: Optional[str] = None,
    element_type: Optional[str] = None,
    element_id: Optional[str] = None
) -> Dict[str, Any]:
    """Search and paginate news items with multi-criteria filters."""
    query = db.query(NewsItem).filter(NewsItem.is_active == True)

    if category:
        query = query.filter(NewsItem.category_tag.ilike(f"%{category}%"))

    if sentiment:
        query = query.filter(NewsItem.sentiment == sentiment)

    if search:
        query = query.filter(
            or_(
                NewsItem.title.ilike(f"%{search}%"),
                NewsItem.summary.ilike(f"%{search}%"),
                NewsItem.source_name.ilike(f"%{search}%")
            )
        )

    if element_type or element_id:
        query = query.join(NewsItem.links)
        if element_type:
            query = query.filter(NewsItemLink.element_type == element_type)
        if element_id:
            query = query.filter(NewsItemLink.element_id.ilike(f"%{element_id}%"))

    total = query.distinct().count()
    items = (
        query.order_by(desc(NewsItem.published_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    results = []
    for item in items:
        links = [{
            "id": l.id,
            "element_type": l.element_type,
            "element_id": l.element_id,
            "element_title": l.element_title,
            "element_url_path": l.element_url_path,
            "link_rationale": l.link_rationale
        } for l in item.links]

        results.append({
            "id": item.id,
            "title": item.title,
            "url": item.url,
            "source_name": item.source_name,
            "source_domain": item.source_domain,
            "published_at": item.published_at.isoformat() if item.published_at else None,
            "summary": item.summary,
            "sentiment": item.sentiment,
            "category_tag": item.category_tag,
            "relevance_score": item.relevance_score,
            "links": links
        })

    return {
        "items": results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 1
    }


def get_news_for_element(db: Session, element_type: str, element_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieves all news items explicitly linked to a given entity."""
    links = (
        db.query(NewsItemLink)
        .filter(
            NewsItemLink.element_type == element_type.lower(),
            NewsItemLink.element_id.ilike(f"%{element_id}%")
        )
        .join(NewsItem)
        .filter(NewsItem.is_active == True)
        .order_by(desc(NewsItem.published_at))
        .limit(limit)
        .all()
    )

    results = []
    for l in links:
        item = l.news_item
        results.append({
            "news_id": item.id,
            "title": item.title,
            "url": item.url,
            "source_name": item.source_name,
            "published_at": item.published_at.isoformat() if item.published_at else None,
            "summary": item.summary,
            "sentiment": item.sentiment,
            "category_tag": item.category_tag,
            "link_rationale": l.link_rationale,
            "confidence_score": l.confidence_score
        })

    return results


def get_news_telemetry(db: Session) -> Dict[str, Any]:
    """Returns database news intelligence metrics and telemetry."""
    total_news = db.query(func.count(NewsItem.id)).scalar() or 0
    total_links = db.query(func.count(NewsItemLink.id)).scalar() or 0
    
    categories = db.query(
        NewsItem.category_tag, func.count(NewsItem.id)
    ).group_by(NewsItem.category_tag).all()

    sources = db.query(
        NewsItem.source_name, func.count(NewsItem.id)
    ).group_by(NewsItem.source_name).all()

    link_types = db.query(
        NewsItemLink.element_type, func.count(NewsItemLink.id)
    ).group_by(NewsItemLink.element_type).all()

    return {
        "total_news_items": total_news,
        "total_explicit_links": total_links,
        "categories": [{"name": c[0], "count": c[1]} for c in categories if c[0]],
        "sources": [{"name": s[0], "count": s[1]} for s in sources if s[0]],
        "linkage_distribution": [{"element_type": lt[0], "count": lt[1]} for lt in link_types if lt[0]],
        "ingestion_telemetry": _LAST_INGESTION_STATS
    }


async def _daily_news_scheduler_loop():
    """Background loop that runs daily news ingestion every 24 hours (86,400s)."""
    logger.info("Starting Daily Energy Innovation News Ingestion Scheduler (24h period).")
    # Initial startup sync
    await asyncio.sleep(2)
    try:
        run_news_ingestion_sync()
    except Exception as e:
        logger.warning(f"Startup news ingestion note: {e}")

    while True:
        try:
            # 24 hours sleep interval
            await asyncio.sleep(86400)
            logger.info("Executing scheduled 24-hour daily energy news ingestion run...")
            run_news_ingestion_sync()
        except asyncio.CancelledError:
            logger.info("Daily news scheduler cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in daily news scheduler loop: {e}")
            await asyncio.sleep(300)  # Retry in 5 minutes on unexpected crash


def start_daily_news_scheduler():
    """Launches the daily recurring background task non-blockingly."""
    import threading
    global _SCHEDULER_TASK
    try:
        try:
            loop = asyncio.get_running_loop()
            _SCHEDULER_TASK = loop.create_task(_daily_news_scheduler_loop())
        except RuntimeError:
            t = threading.Thread(target=lambda: asyncio.run(_daily_news_scheduler_loop()), daemon=True)
            t.start()
    except Exception as e:
        logger.warning(f"Could not initialize daily news scheduler: {e}")
