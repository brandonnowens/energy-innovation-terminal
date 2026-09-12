"""
In-App Continuous Daily Automation Scheduler.

Runs continuously inside the FastAPI background lifecycle, triggering the daily
automation routine every 24 hours at a scheduled hour (default: 06:00 UTC).
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger("InAppDailyScheduler")

_SCHEDULER_TASK: Optional[asyncio.Task] = None
_RUNNING = False


def compute_seconds_until_next_target_hour(target_hour_utc: int = 6) -> float:
    """Compute the number of seconds until the next occurrence of target_hour_utc."""
    now = datetime.now(timezone.utc)
    target = now.replace(hour=target_hour_utc, minute=0, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def _daily_scheduler_loop(target_hour_utc: int = 6):
    """Asynchronous loop waiting until scheduled hour and running the daily routine."""
    global _RUNNING
    _RUNNING = True
    logger.info(f"In-App Daily Automation Scheduler initialized. Target daily execution: {target_hour_utc:02d}:00 UTC.")

    while _RUNNING:
        sleep_sec = compute_seconds_until_next_target_hour(target_hour_utc)
        logger.info(f"Daily Automation Scheduler sleeping for {round(sleep_sec / 3600, 2)} hours until {target_hour_utc:02d}:00 UTC.")

        # Sleep in chunks to allow fast cancellation on server shutdown
        while sleep_sec > 0 and _RUNNING:
            step = min(sleep_sec, 60.0)
            await asyncio.sleep(step)
            sleep_sec -= step

        if not _RUNNING:
            break

        try:
            logger.info("Triggering scheduled automated daily operations routine...")
            from app.cron.daily_routine import run_full_daily_automation
            await asyncio.to_thread(run_full_daily_automation)
            logger.info("Scheduled automated daily operations routine completed successfully.")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error during scheduled daily automation run: {e}", exc_info=True)


def start_daily_automation_scheduler(target_hour_utc: int = 6) -> Optional[asyncio.Task]:
    """Start the in-app daily background scheduler task."""
    global _SCHEDULER_TASK
    if _SCHEDULER_TASK and not _SCHEDULER_TASK.done():
        logger.info("In-App Daily Automation Scheduler is already running.")
        return _SCHEDULER_TASK

    try:
        loop = asyncio.get_running_loop()
        _SCHEDULER_TASK = loop.create_task(_daily_scheduler_loop(target_hour_utc))
        logger.info("In-App Daily Automation Scheduler task spawned.")
        return _SCHEDULER_TASK
    except RuntimeError:
        logger.warning("No running asyncio event loop; daily scheduler not started.")
        return None


def stop_daily_automation_scheduler():
    """Stop the in-app daily background scheduler."""
    global _RUNNING, _SCHEDULER_TASK
    _RUNNING = False
    if _SCHEDULER_TASK and not _SCHEDULER_TASK.done():
        _SCHEDULER_TASK.cancel()
        logger.info("In-App Daily Automation Scheduler stopped.")
