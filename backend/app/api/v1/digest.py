"""Daily Energy Innovation Intelligence Digest API Router (v1)."""

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
@router.get("/daily")
def get_latest_digest(db: Session = Depends(get_db)):
    """Retrieve today's Daily Energy Innovation Intelligence Digest."""
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


@router.get("/export-pdf")
@router.get("/latest/export-pdf")
def export_daily_digest_pdf(
    date: Optional[str] = Query(None, description="Edition date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """Generates and downloads a publication-grade PDF executive briefing for today's or specified date's daily digest."""
    import io
    from fastapi.responses import Response
    from app.engine.digest_pdf_report import build_daily_digest_pdf

    digest_data = get_daily_digest(db, target_date_str=date)
    if not digest_data:
        raise HTTPException(status_code=404, detail="Daily digest edition not found")

    buf = io.BytesIO()
    build_daily_digest_pdf(digest_data, buf)
    pdf_bytes = buf.getvalue()

    edition_date = digest_data.get("edition_date") or date or "latest"
    filename = f"Energy_Innovation_Daily_Briefing_{edition_date}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@router.get("/{date_str}/export-pdf")
def export_daily_digest_by_date_pdf(date_str: str, db: Session = Depends(get_db)):
    """Generates and downloads a publication-grade PDF executive briefing for a specific historical date."""
    return export_daily_digest_pdf(date=date_str, db=db)


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
