"""Ingestion Pipeline Orchestrator and Scheduler."""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.ingestion.grants_gov_worker import GrantsGovWorker
from app.services.ingestion.state_feeds_worker import StateFeedsWorker
from app.services.ingestion.utility_psc_worker import UtilityPscWorker

logger = logging.getLogger("IngestionOrchestrator")

WORKERS = {
    "grants_gov": GrantsGovWorker(),
    "state_clean_energy": StateFeedsWorker(),
    "utility_psc": UtilityPscWorker(),
}

_SCHEDULER_RUNNING = False
_LAST_RUN_TIMES: Dict[str, datetime] = {}
_POLL_INTERVAL_MINUTES = 60  # Default 60-minute cycle


def get_all_worker_statuses() -> List[Dict[str, Any]]:
    """Return status and heartbeat for all automated workers."""
    statuses = []
    now = datetime.utcnow()
    for code, worker in WORKERS.items():
        last_run = _LAST_RUN_TIMES.get(code)
        next_run = (last_run + timedelta(minutes=_POLL_INTERVAL_MINUTES)) if last_run else now
        statuses.append({
            "code": code,
            "name": worker.source_name,
            "agency": worker.agency_name,
            "jurisdiction": worker.jurisdiction,
            "is_active": True,
            "poll_interval_minutes": _POLL_INTERVAL_MINUTES,
            "last_run": last_run.isoformat() if last_run else None,
            "next_run": next_run.isoformat() if next_run else now.isoformat(),
            "status": "idle" if last_run else "ready"
        })
    return statuses


def run_pipeline(source_code: str = "all") -> Dict[str, Any]:
    """Execute ingestion for a single worker or all workers."""
    results = []
    with SessionLocal() as db:
        if source_code == "all":
            for code, worker in WORKERS.items():
                res = worker.run_sync(db)
                _LAST_RUN_TIMES[code] = datetime.utcnow()
                results.append(res)
        elif source_code in WORKERS:
            worker = WORKERS[source_code]
            res = worker.run_sync(db)
            _LAST_RUN_TIMES[source_code] = datetime.utcnow()
            results.append(res)
        else:
            return {"error": f"Unknown source code '{source_code}'"}

    total_inserted = sum(r.get("inserted", 0) for r in results)
    total_updated = sum(r.get("updated", 0) for r in results)
    total_alerts = sum(r.get("alerts_dispatched", 0) for r in results)

    return {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "total_sources_polled": len(results),
        "total_new_opportunities_inserted": total_inserted,
        "total_existing_updated": total_updated,
        "total_alerts_dispatched": total_alerts,
        "details": results
    }


def _background_scheduler_loop():
    """Continuous background loop running every 60 minutes."""
    global _SCHEDULER_RUNNING
    logger.info("Starting Automated Continuous Ingestion Scheduler (60-minute cycle)...")
    while _SCHEDULER_RUNNING:
        # Initial sleep before execution cycle to prevent blocking server boot
        for _ in range(_POLL_INTERVAL_MINUTES * 2):
            if not _SCHEDULER_RUNNING:
                break
            time.sleep(30)
        if not _SCHEDULER_RUNNING:
            break
        try:
            logger.info("Executing scheduled hourly ingestion sync across all feeds...")
            run_pipeline("all")
        except Exception as e:
            logger.error(f"Error during scheduled ingestion run: {e}")



def start_scheduler(poll_interval_minutes: int = 60):
    """Start continuous background ingestion thread."""
    global _SCHEDULER_RUNNING, _POLL_INTERVAL_MINUTES
    _POLL_INTERVAL_MINUTES = poll_interval_minutes
    if not _SCHEDULER_RUNNING:
        _SCHEDULER_RUNNING = True
        t = threading.Thread(target=_background_scheduler_loop, daemon=True)
        t.start()
        logger.info(f"Background Ingestion Scheduler started with {poll_interval_minutes}m interval.")
