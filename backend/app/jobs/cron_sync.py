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

    logger.info(f"Triggering scheduled sync for source: '{args.source}'")
    result = run_pipeline(source_code=args.source)
    logger.info(f"Sync complete. Results: {result}")


if __name__ == "__main__":
    main()
