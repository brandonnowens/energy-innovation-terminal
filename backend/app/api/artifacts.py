"""Artifacts Discovery, Catalog, and Streaming Download API endpoints."""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, or_

from app.config import settings
from app.database import get_db
from app.models.opportunity import Opportunity
from app.models.award import Award
from app.models.result import ResultArtifact
from app.ingest.artifacts_adapter import ArtifactsAdapter, ARTIFACTS_DIR

router = APIRouter()


def _artifact_to_dict(a: ResultArtifact) -> dict:
    local_exists = False
    if a.local_cache_path:
        full_path = Path(settings.data_dir).parent / a.local_cache_path
        local_exists = full_path.exists()

    return {
        "id": a.id,
        "opportunity_id": a.opportunity_id,
        "award_id": a.award_id,
        "organization_id": a.organization_id,
        "recipient_name": a.recipient_name,
        "title": a.title,
        "artifact_type": a.artifact_type,
        "agency": a.agency,
        "source_url": a.source_url,
        "doi": a.doi,
        "publication_date": a.publication_date,
        "page_count": a.page_count,
        "summary": a.summary,
        "key_findings": a.key_findings_json or [],
        "file_size_bytes": a.file_size_bytes or 0,
        "has_local_file": local_exists,
        "local_path": a.local_cache_path,
        "data_provenance": a.data_provenance,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


@router.get("/artifacts")
def list_artifacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    agency: Optional[str] = None,
    artifact_type: Optional[str] = None,
    recipient: Optional[str] = None,
    opportunity_id: Optional[int] = None,
    award_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List paginated, filterable research artifacts, technical deliverables, and reports."""
    query = db.query(ResultArtifact)

    if agency:
        agencies = [a.strip() for a in agency.split(",") if a.strip()]
        query = query.filter(ResultArtifact.agency.in_(agencies))
    if artifact_type:
        types = [t.strip() for t in artifact_type.split(",") if t.strip()]
        query = query.filter(ResultArtifact.artifact_type.in_(types))
    if recipient:
        query = query.filter(ResultArtifact.recipient_name.ilike(f"%{recipient}%"))
    if opportunity_id is not None:
        query = query.filter(ResultArtifact.opportunity_id == opportunity_id)
    if award_id is not None:
        query = query.filter(ResultArtifact.award_id == award_id)
    if search:
        p = f"%{search}%"
        query = query.filter(
            or_(
                ResultArtifact.title.ilike(p),
                ResultArtifact.summary.ilike(p),
                ResultArtifact.recipient_name.ilike(p),
                ResultArtifact.agency.ilike(p),
            )
        )

    total = query.count()
    items = query.order_by(desc(ResultArtifact.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
        "items": [_artifact_to_dict(a) for a in items],
    }


@router.get("/artifacts/{artifact_id}")
def get_artifact(
    artifact_id: int,
    db: Session = Depends(get_db),
):
    """Get single artifact metadata with linked award and opportunity context."""
    art = db.query(ResultArtifact).filter(ResultArtifact.id == artifact_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")

    res = _artifact_to_dict(art)
    
    if art.opportunity_id:
        opp = db.query(Opportunity).filter(Opportunity.id == art.opportunity_id).first()
        if opp:
            res["opportunity"] = {
                "id": opp.id,
                "solicitation_number": opp.solicitation_number,
                "name": opp.name,
                "agency": opp.agency,
                "status": opp.status,
            }

    if art.award_id:
        aw = db.query(Award).filter(Award.id == art.award_id).first()
        if aw:
            res["award"] = {
                "id": aw.id,
                "recipient_name": aw.recipient_name,
                "award_amount": aw.award_amount,
                "project_title": aw.project_title,
                "year": aw.year,
            }

    return res


@router.get("/artifacts/{artifact_id}/download")
def download_artifact_file(
    artifact_id: int,
    db: Session = Depends(get_db),
):
    """Download the actual local artifact document file."""
    art = db.query(ResultArtifact).filter(ResultArtifact.id == artifact_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")

    # Check local cache path
    file_path = None
    if art.local_cache_path:
        candidate = Path(settings.data_dir).parent / art.local_cache_path
        if candidate.exists():
            file_path = candidate

    # If no local file yet, generate on the fly
    if not file_path or not file_path.exists():
        safe_title = "".join(c if c.isalnum() else "_" for c in art.title[:40])
        file_path = ARTIFACTS_DIR / f"artifact_{art.id}_{safe_title}.md"
        doc_content = f"""# {art.title}
**Agency:** {art.agency or 'Public Funding Agency'}
**Recipient:** {art.recipient_name or 'Grant Recipient'}
**Type:** {art.artifact_type}
**Publication Date:** {art.publication_date or '2024'}
**DOI / Source:** {art.doi or art.source_url}

## Executive Summary
{art.summary or 'No summary provided.'}

## Key Verified Findings
""" + "\n".join(f"- {kf}" for k in (art.key_findings_json or []))
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(doc_content)

    filename = f"{art.recipient_name or 'Document'}_{art.title[:45].replace(' ', '_')}.md"
    filename = "".join(c for c in filename if c.isalnum() or c in ("-", "_", ".", " "))

    return FileResponse(
        path=str(file_path),
        media_type="text/markdown",
        filename=filename,
    )


@router.get("/opportunities/{opportunity_id}/artifacts/download-bundle")
def download_opportunity_artifacts_bundle(
    opportunity_id: int,
    db: Session = Depends(get_db),
):
    """Stream a downloadable ZIP bundle of all artifacts and winning proposals for an opportunity."""
    try:
        zip_bytes = ArtifactsAdapter.generate_opportunity_bundle_zip(db, opportunity_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate artifact bundle: {e}")

    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    safe_opp_num = "".join(c for c in (opp.solicitation_number if opp else f"OPP_{opportunity_id}") if c.isalnum() or c in ("-", "_"))
    filename = f"Opportunity_{safe_opp_num}_Artifacts_Bundle.zip"

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/awards/{award_id}/artifacts/download-bundle")
def download_award_artifacts_bundle(
    award_id: int,
    db: Session = Depends(get_db),
):
    """Stream a downloadable ZIP bundle of all artifacts and proposal records for a specific award."""
    try:
        zip_bytes = ArtifactsAdapter.generate_award_bundle_zip(db, award_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate award artifact bundle: {e}")

    aw = db.query(Award).filter(Award.id == award_id).first()
    safe_recip = "".join(c for c in (aw.recipient_name if aw else f"Award_{award_id}") if c.isalnum() or c in ("-", "_"))
    filename = f"Award_{award_id}_{safe_recip}_Artifacts_Bundle.zip"

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.post("/artifacts/discover-and-download")
def discover_and_download_artifacts(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Trigger background discovery, normalization, and downloading of public artifacts across all opportunities."""
    adapter = ArtifactsAdapter(db=db)
    stats = adapter.discover_and_ingest_all()
    return {
        "status": "success",
        "message": f"Discovered and cached {stats['artifacts_ingested']} artifacts across opportunities and awards.",
        "stats": stats,
    }
