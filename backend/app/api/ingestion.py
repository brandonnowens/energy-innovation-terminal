'''Automated Ingestion Pipeline & Background Workers API Router.'''

from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

from app.database import get_db
from app.models.source import Source, IngestionRun
from app.services.ingestion.orchestrator import (
    get_all_worker_statuses, run_pipeline, start_scheduler
)

router = APIRouter(prefix="/ingestion", tags=["Automated Ingestion Workers"])


class StartSchedulerRequest(BaseModel):
    interval_minutes: int = 60


@router.get("/status")
def get_ingestion_pipeline_status(db: Session = Depends(get_db)):
    """Returns real-time status of all continuous scraper feeds and workers."""
    workers = get_all_worker_statuses()
    total_sources = db.query(Source).count()
    recent_runs = db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(10).all()
    return {
        "workers": workers,
        "total_sources_tracked": total_sources,
        "recent_runs": [
            {
                "id": r.id,
                "source_name": r.source_name,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "status": r.status,
                "records_added": r.records_added,
                "records_updated": r.records_updated,
                "records_unchanged": r.records_unchanged,
                "errors": r.errors,
                "error_details": r.error_details,
            }
            for r in recent_runs
        ],
    }


@router.post("/run/{source_code}")
def trigger_manual_ingestion_sync(source_code: str):
    """Trigger an immediate sync for a specific worker ('grants_gov', 'state_clean_energy', 'utility_psc', or 'all')."""
    result = run_pipeline(source_code)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/scheduler/start")
def start_automated_scheduler(req: StartSchedulerRequest):
    """Start the background 60‑minute automated ingestion loop."""
    interval = max(5, min(1440, req.interval_minutes))
    start_scheduler(interval)
    return {
        "status": "running",
        "interval_minutes": interval,
        "message": f"Continuous ingestion workers active: polling Grants.gov, State Portals, and Utility Dockets every {interval} minutes.",
    }

# ---------------------------------------------------------------------------
# New Real‑time ingestion endpoints
# ---------------------------------------------------------------------------

@router.post("/webhook/{source_code}")
async def receive_webhook(
    source_code: str,
    request: Request,
    x_webhook_token: str = Header(..., alias="X-Webhook-Token"),
    db: Session = Depends(get_db),
):
    """Accept JSON payloads from external sources.

    Validates the source against ``webhook_endpoints`` table and the provided secret token.
    Stores the raw payload for provenance and delegates to ``WebhookWorker`` for processing.
    """
    result = db.execute(
        "SELECT secret_token FROM webhook_endpoints WHERE source_code = :code AND enabled = true",
        {"code": source_code},
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Webhook source not found or disabled")
    stored_token = result[0]
    if stored_token != x_webhook_token:
        raise HTTPException(status_code=401, detail="Invalid webhook token")
    payload = await request.json()
    from app.services.ingestion.webhook_worker import WebhookWorker
    worker = WebhookWorker()
    try:
        worker.process_payload(payload, db)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"status": "processed"}

@router.get("/rss_feeds")
def list_rss_feeds(db: Session = Depends(get_db)):
    """List configured RSS feed sources."""
    rows = db.execute(
        "SELECT source_code, feed_url, poll_interval_minutes, enabled FROM rss_feed_sources"
    ).fetchall()
    return [
        {
            "source_code": r[0],
            "feed_url": r[1],
            "poll_interval_minutes": r[2],
            "enabled": r[3],
        }
        for r in rows
    ]

@router.post("/rss_feeds")
def add_rss_feed(
    source_code: str,
    feed_url: str,
    poll_interval_minutes: int = 15,
    enabled: bool = True,
    db: Session = Depends(get_db),
):
    """Create or update an RSS feed source configuration."""
    db.execute(
        "INSERT INTO rss_feed_sources (source_code, feed_url, poll_interval_minutes, enabled) "
        "VALUES (:code, :url, :interval, :en) ON CONFLICT (source_code) DO UPDATE SET "
        "feed_url = EXCLUDED.feed_url, poll_interval_minutes = EXCLUDED.poll_interval_minutes, enabled = EXCLUDED.enabled",
        {"code": source_code, "url": feed_url, "interval": poll_interval_minutes, "en": enabled},
    )
    db.commit()
    return {"status": "ok", "source_code": source_code}

# End of file

from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

from app.database import get_db
from app.models.source import Source, IngestionRun
from app.services.ingestion.orchestrator import (
    get_all_worker_statuses, run_pipeline, start_scheduler
)

router = APIRouter(prefix="/ingestion", tags=["Automated Ingestion Workers"])


class StartSchedulerRequest(BaseModel):
    interval_minutes: int = 60


@router.get("/status")
def get_ingestion_pipeline_status(db: Session = Depends(get_db)):
    """Returns real-time status of all continuous scraper feeds and workers."""
    workers = get_all_worker_statuses()
    total_sources = db.query(Source).count()
    recent_runs = db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(10).all()

    return {
        "workers": workers,
        "total_sources_tracked": total_sources,
        "recent_runs": [
            {
                "id": r.id,
                "source_name": r.source_name,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "status": r.status,
                "records_added": r.records_added,
                "records_updated": r.records_updated,
                "records_unchanged": r.records_unchanged,
                "errors": r.errors,
                "error_details": r.error_details
            }
            for r in recent_runs
        ]
    }


@router.post("/run/{source_code}")
def trigger_manual_ingestion_sync(source_code: str):
    """Trigger an immediate sync for a specific worker ('grants_gov', 'state_clean_energy', 'utility_psc', or 'all')."""
    result = run_pipeline(source_code)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/scheduler/start")
def start_automated_scheduler(req: StartSchedulerRequest):
    """Start the background 60-minute automated ingestion loop."""
    interval = max(5, min(1440, req.interval_minutes))
    start_scheduler(interval)
    return {
        "status": "running",
        "interval_minutes": interval,
        "message": f"Continuous ingestion workers active: polling Grants.gov, State Portals, and Utility Dockets every {interval} minutes."
    }
