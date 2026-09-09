"""Daily Clean Energy Intelligence Digest API Router (v1)."""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.engine.daily_digest import (
    get_daily_digest,
    generate_daily_digest,
    get_digest_archive_list
)

router = APIRouter(prefix="/digest", tags=["Daily Digest"])


@router.get("/latest")
@router.get("/today")
def get_latest_digest(db: Session = Depends(get_db)):
    """Retrieve today's Daily Clean Energy Intelligence Digest."""
    try:
        return get_daily_digest(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate daily digest: {str(e)}")


@router.get("/archive")
def list_digest_archive(db: Session = Depends(get_db)):
    """List available historical daily digest editions."""
    try:
        return get_digest_archive_list(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list digest archive: {str(e)}")


@router.get("/{date_str}")
def get_digest_by_date(date_str: str, db: Session = Depends(get_db)):
    """Retrieve a specific daily digest edition by YYYY-MM-DD."""
    try:
        return get_daily_digest(db, target_date_str=date_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve digest for date {date_str}: {str(e)}")


@router.post("/generate")
def force_generate_digest(
    date_str: Optional[str] = Query(None, description="Target date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """Force re-generate and refresh the daily digest for a given date."""
    try:
        return generate_daily_digest(db, target_date_str=date_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate daily digest: {str(e)}")
