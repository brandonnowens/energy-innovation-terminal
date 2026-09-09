"""
Render Cron Sync Script / CLI Entrypoint.

Can be run via:
    python -m app.jobs.cron_sync --source all
    python -m app.jobs.cron_sync --source grants_gov
"""

import sys
import argparse
import logging
from app.services.ingestion.orchestrator import run_pipeline, get_all_worker_statuses

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("CronSync")


def main():
    parser = argparse.ArgumentParser(description="Energy Innovation Terminal Automated Sync Runner")
    parser.add_argument(
        "--source",
        choices=["all", "grants_gov", "state_clean_energy", "utility_psc", "status"],
        default="all",
        help="Data source worker to run"
    )
    args = parser.parse_args()

    if args.source == "status":
        statuses = get_all_worker_statuses()
        logger.info(f"Worker Statuses: {statuses}")
        return

    logger.info(f"Triggering scheduled automated daily sync for source: '{args.source}'")
    try:
        result = run_pipeline(source_code=args.source)
        logger.info(f"Sync complete. Summary: inserted={result.get('total_new_opportunities_inserted', 0)}, updated={result.get('total_existing_updated', 0)}, alerts={result.get('total_alerts_dispatched', 0)}")
        logger.info(f"Full Result: {result}")
        if "error" in result:
            logger.error(f"Sync reported an error: {result['error']}")
            sys.exit(1)

        # Automatically compile and save the fresh daily digest for UI readers
        try:
            from app.database import SessionLocal
            from app.engine.daily_digest import generate_daily_digest
            with SessionLocal() as db:
                digest = generate_daily_digest(db)
                logger.info(f"Successfully compiled automated Daily Digest edition: {digest.get('edition_number')} ({digest.get('formatted_date')})")
        except Exception as digest_err:
            logger.warning(f"Non-fatal warning: Daily digest auto-compilation encountered: {digest_err}")

    except Exception as e:
        logger.exception(f"Fatal error during scheduled sync run: {e}")
        sys.exit(1)



if __name__ == "__main__":
    main()

