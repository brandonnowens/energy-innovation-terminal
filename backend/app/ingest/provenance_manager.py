"""Field-Level Provenance & Evidence Manager.

Centralized API for:
1. Recording field-level evidence (extracted vs normalized value, citation, confidence, status).
2. Capturing source snapshots with SHA-256 hashes and change tracking.
3. Enforcing source authority hierarchy (Statute > FOA > Official Webpage > Award DB > Secondary).
4. Non-destructive entity aliasing and merge review queueing.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select, and_, text
from sqlalchemy.orm import Session

from app.models.source import (
    FieldProvenance,
    SourceSnapshot,
    EntityAlias,
    EntityMergeReview,
    SourceConflict,
    DataQualityIssue,
)

logger = logging.getLogger("ProvenanceManager")

AUTHORITY_RANKS = {
    "statute": 1,
    "commission_order": 1,
    "tariff": 1,
    "solicitation": 2,
    "foa": 2,
    "rfp": 2,
    "pon": 2,
    "official_webpage": 3,
    "agency_portal": 3,
    "award_announcement": 4,
    "award_database": 4,
    "recipient_announcement": 5,
    "secondary": 6,
}


def compute_sha256(content: str | bytes) -> str:
    """Compute deterministic SHA-256 hash."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def log_field_provenance(
    db: Session,
    entity_type: str,
    entity_id: int,
    field_name: str,
    extracted_value: Any,
    normalized_value: Any = None,
    source_url: Optional[str] = None,
    source_title: Optional[str] = None,
    source_organization: Optional[str] = None,
    source_document_type: str = "solicitation",
    publication_date: Optional[datetime] = None,
    effective_date: Optional[datetime] = None,
    source_document_hash: Optional[str] = None,
    page_or_section_ref: Optional[str] = None,
    supporting_excerpt: Optional[str] = None,
    extraction_method: str = "deterministic_adapter",
    confidence: float = 1.0,
    verification_status: str = "verified",
) -> FieldProvenance:
    """Records field-level evidence in the field_provenances table."""
    ext_str = json.dumps(extracted_value) if isinstance(extracted_value, (dict, list)) else (str(extracted_value) if extracted_value is not None else None)
    norm_str = json.dumps(normalized_value) if isinstance(normalized_value, (dict, list)) else (str(normalized_value) if normalized_value is not None else ext_str)

    # Check for existing active provenance for this field
    existing = db.execute(
        select(FieldProvenance).where(
            and_(
                FieldProvenance.entity_type == entity_type,
                FieldProvenance.entity_id == entity_id,
                FieldProvenance.field_name == field_name,
                FieldProvenance.is_superseded == False,
            )
        )
    ).scalars().first()

    if existing:
        # Check for conflicts if value changed
        if existing.normalized_value != norm_str:
            new_rank = AUTHORITY_RANKS.get(source_document_type.lower(), 5)
            old_rank = AUTHORITY_RANKS.get((existing.source_document_type or "solicitation").lower(), 5)

            # If incoming source has equal or higher authority, supersede existing
            if new_rank <= old_rank:
                existing.is_superseded = True
                existing.conflict_status = True
            else:
                # Lower authority trying to overwrite higher authority -> record conflict and do not overwrite
                conflict = SourceConflict(
                    entity_type=entity_type,
                    entity_id=str(entity_id),
                    field_name=field_name,
                    value_a=existing.normalized_value,
                    source_a=existing.source_url or existing.source_title,
                    value_b=norm_str,
                    source_b=source_url or source_title,
                    resolution_note=f"Retained higher authority ({existing.source_document_type}) over lower authority ({source_document_type})",
                )
                db.add(conflict)
                return existing

    record = FieldProvenance(
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        extracted_value=ext_str,
        normalized_value=norm_str,
        source_url=source_url,
        source_title=source_title,
        source_organization=source_organization,
        source_document_type=source_document_type,
        publication_date=publication_date,
        retrieval_date=datetime.now(timezone.utc),
        effective_date=effective_date,
        source_document_hash=source_document_hash,
        page_or_section_ref=page_or_section_ref,
        supporting_excerpt=supporting_excerpt,
        extraction_method=extraction_method,
        confidence=confidence,
        verification_status=verification_status,
        last_verified_at=datetime.now(timezone.utc),
    )
    db.add(record)
    return record


def record_snapshot(
    db: Session,
    source_url: str,
    raw_payload: str,
    source_type: str = "html",
    http_status: int = 200,
    etag: Optional[str] = None,
    headers: Optional[Dict[str, Any]] = None,
) -> tuple[SourceSnapshot, bool]:
    """Records raw payload snapshot and detects content shifts."""
    content_hash = compute_sha256(raw_payload)

    # Check latest snapshot for this URL
    last_snap = db.execute(
        select(SourceSnapshot)
        .where(SourceSnapshot.source_url == source_url)
        .order_by(SourceSnapshot.captured_at.desc())
    ).scalars().first()

    has_changed = False
    if last_snap and last_snap.content_hash != content_hash:
        has_changed = True

    snapshot = SourceSnapshot(
        source_url=source_url,
        content_hash=content_hash,
        source_type=source_type,
        http_status=http_status,
        etag=etag,
        raw_payload_text=raw_payload[:500000],  # Bound text storage
        headers_json=headers,
        captured_at=datetime.now(timezone.utc),
        has_changed=has_changed,
    )
    db.add(snapshot)
    return snapshot, has_changed


def register_entity_alias(
    db: Session,
    entity_type: str,
    canonical_id: int,
    alias_name: str,
    alias_type: str = "alternate_name",
    source_ref: Optional[str] = None,
    confidence: float = 1.0,
):
    """Registers an entity alias if not already existing."""
    clean_alias = alias_name.strip()
    if not clean_alias:
        return

    exists = db.execute(
        select(EntityAlias).where(
            and_(
                EntityAlias.entity_type == entity_type,
                EntityAlias.canonical_id == canonical_id,
                EntityAlias.alias_name.ilike(clean_alias),
            )
        )
    ).scalars().first()

    if not exists:
        alias = EntityAlias(
            entity_type=entity_type,
            canonical_id=canonical_id,
            alias_name=clean_alias,
            alias_type=alias_type,
            source_reference=source_ref,
            confidence=confidence,
        )
        db.add(alias)


def flag_quality_issue(
    db: Session,
    issue_type: str,
    severity: str,
    entity_type: Optional[str],
    entity_id: Optional[str],
    description: str,
):
    """Records a data quality issue in data_quality_issues table."""
    issue = DataQualityIssue(
        issue_type=issue_type,
        severity=severity,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        description=description,
        resolved=False,
    )
    db.add(issue)
