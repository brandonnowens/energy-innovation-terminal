"""
Unified Daily Automation Routine Orchestrator.

Executes all recurring daily routines in an idempotent, fault-tolerant sequence:
1. Phase 1: Energy News Ingestion & Entity Linkage Sync
2. Phase 2: Multi-Agency Opportunity & Solicitation Feeds (Grants.gov, State Feeds, Utility PSC)
3. Phase 3: Daily Intelligence Digest & Executive Briefing Generation
4. Phase 4: User Telemetry & Daily Usage Intelligence Reports
5. Phase 5: Data Quality Scorecard & Readiness Gate Audit
6. Phase 6: Cache Warming for Fast Sub-Second API Responses

Can be run via:
    python -m app.cron.daily_routine
    python -m app.jobs.cron_sync --source all
"""

import sys
import time
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("DailyAutomationRoutine")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Global execution state for status monitoring
_LATEST_ROUTINE_STATE: Dict[str, Any] = {
    "status": "idle",
    "last_run_started_at": None,
    "last_run_completed_at": None,
    "last_duration_seconds": None,
    "phase_results": {},
    "last_error": None,
}


def get_latest_daily_routine_status() -> Dict[str, Any]:
    """Return the status and summary of the most recent automated routine run."""
    return dict(_LATEST_ROUTINE_STATE)


def run_full_daily_automation(
    target_date: Optional[datetime] = None,
    skip_ingestion: bool = False,
    force_news_seed: bool = False
) -> Dict[str, Any]:
    """
    Executes the end-to-end daily automated operations sequence.
    Handles exceptions per phase so failure in one phase does not block the others.
    """
    global _LATEST_ROUTINE_STATE

    if target_date is None:
        target_date = datetime.now(timezone.utc)

    target_date_str = target_date.strftime("%Y-%m-%d")
    start_time = time.time()
    iso_start = target_date.isoformat()

    logger.info(f"================================================================")
    logger.info(f"  STARTING DAILY AUTOMATION ROUTINE FOR {target_date_str}")
    logger.info(f"================================================================")

    _LATEST_ROUTINE_STATE["status"] = "running"
    _LATEST_ROUTINE_STATE["last_run_started_at"] = iso_start
    _LATEST_ROUTINE_STATE["last_error"] = None
    phase_results: Dict[str, Any] = {}

    from app.database import SessionLocal

    # -------------------------------------------------------------
    # Phase 1: Energy News Ingestion & Linkage Sync
    # -------------------------------------------------------------
    logger.info("[Phase 1/5] Ingesting Daily Energy News & Linking Entities...")
    t0 = time.time()
    try:
        from app.services.news_service import run_news_ingestion_sync
        with SessionLocal() as db:
            news_res = run_news_ingestion_sync(db, force_seed=force_news_seed)
        phase_results["news_ingestion"] = {
            "status": "success",
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "items_added": news_res.get("new_items_persisted", 0),
            "links_created": news_res.get("total_links_created", 0),
        }
        logger.info(f"[Phase 1/5] News Ingestion complete: +{news_res.get('new_items_persisted', 0)} articles, +{news_res.get('total_links_created', 0)} links.")
    except Exception as e:
        logger.warning(f"[Phase 1/5 Warning] News ingestion encountered: {e}")
        phase_results["news_ingestion"] = {
            "status": "warning",
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "error": str(e),
        }

    # -------------------------------------------------------------
    # Phase 2: Multi-Agency Ingestion Pipeline
    # -------------------------------------------------------------
    if not skip_ingestion:
        logger.info("[Phase 2/5] Running Multi-Agency Opportunity Feed Workers (Grants.gov, State, Utility)...")
        t0 = time.time()
        try:
            from app.services.ingestion.orchestrator import run_pipeline
            ingest_res = run_pipeline("all")
            phase_results["feed_ingestion"] = {
                "status": "success",
                "duration_ms": round((time.time() - t0) * 1000, 1),
                "sources_polled": ingest_res.get("total_sources_polled", 0),
                "new_opportunities": ingest_res.get("total_new_opportunities_inserted", 0),
                "updated_opportunities": ingest_res.get("total_existing_updated", 0),
                "alerts_dispatched": ingest_res.get("total_alerts_dispatched", 0),
            }
            logger.info(f"[Phase 2/5] Feed Ingestion complete: {ingest_res.get('total_sources_polled', 0)} sources polled, +{ingest_res.get('total_new_opportunities_inserted', 0)} new opps.")
        except Exception as e:
            logger.warning(f"[Phase 2/5 Warning] Feed ingestion encountered: {e}")
            phase_results["feed_ingestion"] = {
                "status": "warning",
                "duration_ms": round((time.time() - t0) * 1000, 1),
                "error": str(e),
            }
    else:
        logger.info("[Phase 2/5] Feed ingestion skipped by flag.")
        phase_results["feed_ingestion"] = {"status": "skipped"}

    # -------------------------------------------------------------
    # Phase 3: Daily Intelligence Digest Synthesis & Cache Warming
    # -------------------------------------------------------------
    logger.info(f"[Phase 3/5] Generating Daily Intelligence Digest for {target_date_str}...")
    t0 = time.time()
    try:
        from app.engine.daily_digest import generate_daily_digest, warm_digest_cache
        with SessionLocal() as db:
            digest_res = generate_daily_digest(db, target_date_str)
        warm_digest_cache()
        phase_results["daily_digest"] = {
            "status": "success",
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "edition": digest_res.get("edition_number"),
            "target_date": digest_res.get("formatted_date"),
            "active_solicitations": digest_res.get("macro_stats", {}).get("total_active_solicitations", 0),
            "total_active_capital": digest_res.get("macro_stats", {}).get("total_active_capital_formatted", "$0"),
        }
        logger.info(f"[Phase 3/5] Daily Digest generated: {digest_res.get('edition_number')} ({digest_res.get('formatted_date')}) with {digest_res.get('macro_stats', {}).get('total_active_capital_formatted')} active capital.")
    except Exception as e:
        logger.warning(f"[Phase 3/5 Warning] Daily Digest generation encountered: {e}")
        phase_results["daily_digest"] = {
            "status": "warning",
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "error": str(e),
        }

    # -------------------------------------------------------------
    # Phase 4: User Telemetry & Daily Usage Summary Reports
    # -------------------------------------------------------------
    logger.info("[Phase 4/5] Compiling Daily User Usage & Engagement Intelligence Report...")
    t0 = time.time()
    try:
        from app.services.daily_usage_summary import generate_and_save_daily_user_summary
        with SessionLocal() as db:
            usage_res = generate_and_save_daily_user_summary(db, target_date)
        phase_results["usage_summary"] = {
            "status": "success",
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "date": usage_res.get("date"),
            "today_unique_visitors": usage_res.get("user_summary", {}).get("today_unique_visitors", 0),
            "yesterday_unique_visitors": usage_res.get("user_summary", {}).get("yesterday_unique_visitors", 0),
            "today_requests": usage_res.get("user_summary", {}).get("today_requests", 0),
            "wau_unique_visitors": usage_res.get("user_summary", {}).get("wau_unique_visitors", 0),
            "latest_file": usage_res.get("latest_file"),
            "daily_file": usage_res.get("daily_file"),
        }
        logger.info(f"[Phase 4/5] Usage Report generated: {usage_res.get('user_summary', {}).get('today_unique_visitors', 0)} today DAU vs {usage_res.get('user_summary', {}).get('yesterday_unique_visitors', 0)} yesterday DAU ({usage_res.get('user_summary', {}).get('wau_unique_visitors', 0)} WAU).")
    except Exception as e:
        logger.warning(f"[Phase 4/5 Warning] Usage Report generation encountered: {e}")
        phase_results["usage_summary"] = {
            "status": "warning",
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "error": str(e),
        }

    # -------------------------------------------------------------
    # Phase 5: Data Quality Audit & Readiness Gates
    # -------------------------------------------------------------
    logger.info("[Phase 5/5] Executing Data Quality Scorecard & Readiness Gate Audit...")
    t0 = time.time()
    try:
        from app.audit.data_quality_report import generate_data_quality_report
        audit_res = generate_data_quality_report()
        gate = audit_res.get("readiness_gate", {})
        phase_results["data_quality_audit"] = {
            "status": "success",
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "readiness_gate_passed": gate.get("passed", False),
            "criteria_passed": f"{gate.get('criteria_passed', 0)}/{gate.get('criteria_evaluated', 0)}",
        }
        logger.info(f"[Phase 5/5] Data Quality Audit complete: Readiness Gate Passed={gate.get('passed', False)} ({gate.get('criteria_passed', 0)}/{gate.get('criteria_evaluated', 0)} passed).")
    except Exception as e:
        logger.warning(f"[Phase 5/5 Warning] Data Quality Audit encountered: {e}")
        phase_results["data_quality_audit"] = {
            "status": "warning",
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "error": str(e),
        }

    # -------------------------------------------------------------
    # Completion & Summary Telemetry
    # -------------------------------------------------------------
    total_elapsed = round(time.time() - start_time, 2)
    iso_end = datetime.now(timezone.utc).isoformat()

    _LATEST_ROUTINE_STATE["status"] = "success"
    _LATEST_ROUTINE_STATE["last_run_completed_at"] = iso_end
    _LATEST_ROUTINE_STATE["last_duration_seconds"] = total_elapsed
    _LATEST_ROUTINE_STATE["phase_results"] = phase_results

    logger.info(f"================================================================")
    logger.info(f"  DAILY AUTOMATION ROUTINE COMPLETED IN {total_elapsed}s")
    logger.info(f"================================================================")

    return {
        "success": True,
        "date": target_date_str,
        "started_at": iso_start,
        "completed_at": iso_end,
        "duration_seconds": total_elapsed,
        "phase_results": phase_results
    }


def main():
    """CLI entry point for automated execution."""
    import argparse
    parser = argparse.ArgumentParser(description="Unified Daily Automation Routine Orchestrator")
    parser.add_argument("--skip-ingestion", action="store_true", help="Skip external feed ingestion")
    parser.add_argument("--force-news-seed", action="store_true", help="Force baseline news seeding if feeds are empty")
    args = parser.parse_args()

    res = run_full_daily_automation(
        skip_ingestion=args.skip_ingestion,
        force_news_seed=args.force_news_seed
    )
    if not res.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
