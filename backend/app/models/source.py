"""Source tracking, provenance, and data quality models."""

from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Source(Base):
    """A data source used by the system."""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    url: Mapped[str] = mapped_column(String(500))
    source_type: Mapped[str] = mapped_column(String(50))  # api, html, document, dataset
    authority_rank: Mapped[int] = mapped_column(Integer, default=5)  # 1=highest
    description: Mapped[Optional[str]] = mapped_column(Text)
    last_fetched_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    fetch_status: Mapped[Optional[str]] = mapped_column(String(50))  # success, error, partial
    content_hash: Mapped[Optional[str]] = mapped_column(String(64))
    record_count: Mapped[Optional[int]] = mapped_column(Integer)
    update_frequency: Mapped[Optional[str]] = mapped_column(String(50))  # daily, weekly, quarterly

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class FieldProvenance(Base):
    """Granular field-level evidence and provenance record."""

    __tablename__ = "field_provenances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)  # opportunity, organization, program, award, recipient
    entity_id: Mapped[int] = mapped_column(Integer, index=True)
    field_name: Mapped[str] = mapped_column(String(100), index=True)
    extracted_value: Mapped[Optional[str]] = mapped_column(Text)
    normalized_value: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    source_title: Mapped[Optional[str]] = mapped_column(String(500))
    source_organization: Mapped[Optional[str]] = mapped_column(String(255))
    source_document_type: Mapped[str] = mapped_column(String(100), default="solicitation")
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    retrieval_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    effective_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    source_document_hash: Mapped[Optional[str]] = mapped_column(String(64))
    page_or_section_ref: Mapped[Optional[str]] = mapped_column(String(255))
    supporting_excerpt: Mapped[Optional[str]] = mapped_column(Text)
    extraction_method: Mapped[str] = mapped_column(String(100), default="deterministic_adapter")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    verification_status: Mapped[str] = mapped_column(String(50), default="verified", index=True)  # verified, provisional, inferred, conflicting, unresolved
    is_superseded: Mapped[bool] = mapped_column(Boolean, default=False)
    superseded_by_id: Mapped[Optional[int]] = mapped_column(Integer)
    conflict_status: Mapped[bool] = mapped_column(Boolean, default=False)
    last_verified_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class SourceSnapshot(Base):
    """Durable payload snapshot of a source document or webpage for change detection."""

    __tablename__ = "source_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_url: Mapped[str] = mapped_column(String(1000), index=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    source_type: Mapped[str] = mapped_column(String(50), default="html")  # html, pdf, json, xml
    http_status: Mapped[int] = mapped_column(Integer, default=200)
    etag: Mapped[Optional[str]] = mapped_column(String(255))
    last_modified_header: Mapped[Optional[str]] = mapped_column(String(255))
    raw_payload_text: Mapped[Optional[str]] = mapped_column(Text)
    headers_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    has_changed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class StagedOpportunity(Base):
    """Idempotent staging table for candidate and updated opportunities."""

    __tablename__ = "staged_opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    solicitation_number: Mapped[Optional[str]] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(500))
    agency: Mapped[str] = mapped_column(String(255))
    program_name: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="open")
    open_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    close_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    total_funding: Mapped[Optional[float]] = mapped_column(Float)
    max_per_award: Mapped[Optional[float]] = mapped_column(Float)
    cost_share_pct: Mapped[Optional[float]] = mapped_column(Float)
    cost_share_mandatory: Mapped[Optional[bool]] = mapped_column(Boolean)
    target_trl_min: Mapped[Optional[int]] = mapped_column(Integer)
    target_trl_max: Mapped[Optional[int]] = mapped_column(Integer)
    geographic_scope: Mapped[Optional[str]] = mapped_column(String(500))
    eligible_applicant_types: Mapped[Optional[Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    eligible_technology_areas: Mapped[Optional[Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    eligible_activity_types: Mapped[Optional[Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    eligible_sectors: Mapped[Optional[Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    statutory_mandates: Mapped[Optional[Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    priority_problem_statements: Mapped[Optional[Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    scoring_rubric_weights: Mapped[Optional[Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    raw_payload: Mapped[Optional[str]] = mapped_column(Text)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64))
    staging_status: Mapped[str] = mapped_column(String(50), default="staged")
    merge_conflict_notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class StagedAward(Base):
    """Idempotent staging table for candidate and updated awards."""

    __tablename__ = "staged_awards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_award_id: Mapped[Optional[str]] = mapped_column(String(255))
    solicitation_number: Mapped[Optional[str]] = mapped_column(String(255))
    recipient_name: Mapped[str] = mapped_column(String(500))
    award_amount: Mapped[Optional[float]] = mapped_column(Float)
    award_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    project_title: Mapped[Optional[str]] = mapped_column(String(1000))
    agency: Mapped[Optional[str]] = mapped_column(String(255))
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    raw_data: Mapped[Optional[str]] = mapped_column(Text)
    staging_status: Mapped[str] = mapped_column(String(50), default="staged")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class EntityAlias(Base):
    """Mapping of canonical entity IDs to alternate names, acronyms, and historical DBA aliases."""

    __tablename__ = "entity_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    canonical_id: Mapped[int] = mapped_column(Integer, index=True)
    alias_name: Mapped[str] = mapped_column(String(500), index=True)
    alias_type: Mapped[str] = mapped_column(String(100), default="alternate_name")
    source_reference: Mapped[Optional[str]] = mapped_column(String(500))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class EntityMergeReview(Base):
    """Non-destructive merge candidate review queue for detected duplicate entities."""

    __tablename__ = "entity_merge_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    primary_entity_id: Mapped[int] = mapped_column(Integer, index=True)
    duplicate_entity_id: Mapped[int] = mapped_column(Integer, index=True)
    match_confidence: Mapped[Optional[float]] = mapped_column(Float)
    detection_method: Mapped[Optional[str]] = mapped_column(String(100))
    review_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, approved, rejected, deferred
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class SourceConflict(Base):
    """A detected conflict between two sources for the same data point."""

    __tablename__ = "source_conflicts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50))  # opportunity, program, project
    entity_id: Mapped[Optional[str]] = mapped_column(String(100))
    field_name: Mapped[str] = mapped_column(String(100))
    value_a: Mapped[Optional[str]] = mapped_column(Text)
    source_a: Mapped[Optional[str]] = mapped_column(String(200))
    value_b: Mapped[Optional[str]] = mapped_column(Text)
    source_b: Mapped[Optional[str]] = mapped_column(String(200))
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_note: Mapped[Optional[str]] = mapped_column(Text)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class IngestionRun(Base):
    """A record of a data ingestion run."""

    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(String(200))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="running")
    records_added: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_unchanged: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    error_details: Mapped[Optional[str]] = mapped_column(Text)


class ChangeEvent(Base):
    """A detected change to an entity."""

    __tablename__ = "change_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    entity_id: Mapped[str] = mapped_column(String(100))
    entity_name: Mapped[Optional[str]] = mapped_column(String(500))
    change_type: Mapped[str] = mapped_column(String(50))
    field_name: Mapped[Optional[str]] = mapped_column(String(100))
    old_value: Mapped[Optional[str]] = mapped_column(Text)
    new_value: Mapped[Optional[str]] = mapped_column(Text)
    source_name: Mapped[Optional[str]] = mapped_column(String(200))
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class DataQualityIssue(Base):
    """A detected data quality issue."""

    __tablename__ = "data_quality_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    issue_type: Mapped[str] = mapped_column(String(50))
    severity: Mapped[str] = mapped_column(String(20))  # critical, warning, info
    entity_type: Mapped[Optional[str]] = mapped_column(String(50))
    entity_id: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
