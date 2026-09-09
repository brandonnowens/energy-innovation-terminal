"""
V1 Canonical Background Jobs Router.

Provides asynchronous job submission, status polling, and result retrieval.
"""

import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from app.jobs.runner import default_job_runner, JobStatus
from app.services.ingestion.orchestrator import run_pipeline, get_all_worker_statuses

router = APIRouter(prefix="/jobs", tags=["V1 Background Jobs"])


class IngestionJobRequest(BaseModel):
    source_code: str = Field("all", description="Source worker: all, grants_gov, state_clean_energy, utility_psc")


async def _async_pipeline_wrapper(source_code: str):
    # Run pipeline in a separate thread since run_pipeline is synchronous
    return await asyncio.to_thread(run_pipeline, source_code)


@router.get("")
def list_jobs(
    limit: int = Query(25, ge=1, le=100),
    job_type: Optional[str] = Query(None, description="Filter by job type")
):
    """List recent background tasks and their current execution statuses."""
    jobs = default_job_runner.list_jobs(limit=limit, job_type=job_type)
    return {
        "status": "success",
        "count": len(jobs),
        "jobs": jobs
    }


@router.get("/ingestion-workers")
def get_worker_status():
    """Retrieve health and last sync timestamps for all ingestion workers."""
    return {
        "status": "success",
        "workers": get_all_worker_statuses()
    }


@router.get("/{job_id}")
def get_job_status(job_id: str):
    """Retrieve execution status, progress, message, error, and result of a background task."""
    job = default_job_runner.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return {
        "status": "success",
        "job": job.to_dict()
    }


@router.post("/submit-ingestion")
def submit_ingestion_job(payload: IngestionJobRequest):
    """Submit an asynchronous multi-agency data ingestion sync job."""
    job = default_job_runner.submit_job(
        job_type="data_ingestion",
        coroutine_func=_async_pipeline_wrapper,
        source_code=payload.source_code,
        metadata={"source_code": payload.source_code}
    )

    return {
        "status": "success",
        "message": f"Ingestion job for '{payload.source_code}' queued successfully.",
        "job_id": job.id,
        "job_status": job.status.value
    }
