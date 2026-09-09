"""
Lightweight Asynchronous Background Job Runner.

Provides in-process background job submission, status tracking, concurrency control,
and result retrieval without requiring Redis, Celery, or external queue brokers.
"""

import asyncio
import threading
import logging
import uuid
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable, Awaitable, List
from enum import Enum

logger = logging.getLogger("JobRunner")


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BackgroundJob:
    def __init__(self, job_id: str, job_type: str, metadata: Optional[Dict[str, Any]] = None):
        self.id = job_id
        self.job_type = job_type
        self.status = JobStatus.PENDING
        self.created_at = datetime.now(timezone.utc)
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.progress_pct: int = 0
        self.message: str = "Job queued"
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.metadata: Dict[str, Any] = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.id,
            "job_type": self.job_type,
            "status": self.status.value,
            "progress_pct": self.progress_pct,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": (
                (self.completed_at - self.started_at).total_seconds()
                if self.completed_at and self.started_at
                else None
            ),
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
        }


class JobRunner:
    """Singleton in-memory async task manager and status tracker."""

    def __init__(self, max_history: int = 100):
        self._jobs: Dict[str, BackgroundJob] = {}
        self._max_history = max_history

    def submit_job(
        self,
        job_type: str,
        coroutine_func: Callable[..., Awaitable[Any]],
        *args,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> BackgroundJob:
        """Submit an async task to run in the background."""
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        job = BackgroundJob(job_id=job_id, job_type=job_type, metadata=metadata)
        self._jobs[job_id] = job
        self._trim_history()

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._execute_wrapper(job, coroutine_func, *args, **kwargs))
        except RuntimeError:
            # When called outside an active event loop (e.g. synchronous unit test thread)
            thread = threading.Thread(
                target=lambda: asyncio.run(self._execute_wrapper(job, coroutine_func, *args, **kwargs)),
                daemon=True
            )
            thread.start()

        return job

    async def _execute_wrapper(
        self,
        job: BackgroundJob,
        coroutine_func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs
    ):
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        job.message = "Job is executing..."
        job.progress_pct = 10
        logger.info(f"Starting background job [{job.id}] type={job.job_type}")

        try:
            result = await coroutine_func(*args, **kwargs)
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            job.progress_pct = 100
            job.message = "Job completed successfully."
            job.result = result
            logger.info(f"Background job [{job.id}] completed successfully in {(job.completed_at - job.started_at).total_seconds():.2f}s")
        except Exception as e:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now(timezone.utc)
            job.error = str(e)
            job.message = f"Job failed: {str(e)}"
            logger.error(f"Background job [{job.id}] failed: {traceback.format_exc()}")

    def get_job(self, job_id: str) -> Optional[BackgroundJob]:
        """Retrieve job by ID."""
        return self._jobs.get(job_id)

    def list_jobs(self, limit: int = 50, job_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List recently submitted jobs."""
        jobs = list(self._jobs.values())
        if job_type:
            jobs = [j for j in jobs if j.job_type == job_type]
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return [j.to_dict() for j in jobs[:limit]]

    def _trim_history(self):
        """Keep memory bounded by removing oldest jobs beyond max_history."""
        if len(self._jobs) > self._max_history:
            sorted_jobs = sorted(self._jobs.values(), key=lambda j: j.created_at)
            to_remove = sorted_jobs[: len(self._jobs) - self._max_history]
            for j in to_remove:
                self._jobs.pop(j.id, None)


# Global singleton job runner
default_job_runner = JobRunner()
