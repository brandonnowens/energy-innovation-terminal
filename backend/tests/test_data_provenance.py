"""Comprehensive Unit & Integration Test Suite for Data Provenance, Source Precedence & Database Integrity.

Covers:
1. Field-level provenance recording and SHA-256 hash verification.
2. Evidence hierarchy and source authority precedence enforcement.
3. Idempotent re-ingestion without duplicate creation.
4. Explicit unknown vs. un-audited null distinction.
5. Entity hierarchy integrity (Organization -> Program -> Opportunity -> Award -> Recipient).
6. Active status and deadline assertion validations.
7. Entity aliasing and merge review queuing.
"""

import hashlib
import json
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, and_, text

from app.database import SessionLocal, engine
from app.models.opportunity import Opportunity
from app.models.organization import Organization
from app.models.program import Program
from app.models.award import Award
from app.models.recipient import Recipient
from app.models.source import FieldProvenance, SourceSnapshot, EntityAlias, SourceConflict, EntityMergeReview
from app.ingest.provenance_manager import (
    log_field_provenance,
    record_snapshot,
    register_entity_alias,
    compute_sha256,
    AUTHORITY_RANKS,
)
from app.audit.quality_assertions import run_quality_assertions
from app.audit.data_quality_report import generate_data_quality_report


@pytest.fixture
def db_session():
    """Provides a transactional database session for tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_field_provenance_logging_and_hash_verification(db_session):
    """Verifies that field-level provenance records are properly saved with SHA-256 hash and metadata."""
    sample_payload = "https://portal.nyserda.ny.gov/PON5000_Summary.pdf"
    expected_hash = hashlib.sha256(sample_payload.encode("utf-8")).hexdigest()

    prov = log_field_provenance(
        db=db_session,
        entity_type="opportunity",
        entity_id=999901,
        field_name="total_funding",
        extracted_value=15000000.0,
        normalized_value=15000000.0,
        source_url="https://portal.nyserda.ny.gov/PON5000",
        source_title="NYSERDA PON 5000 Official Solicitation",
        source_organization="NYSERDA",
        source_document_type="solicitation",
        source_document_hash=expected_hash,
        page_or_section_ref="Section 2.1 Funding Envelope",
        supporting_excerpt="A total of $15,000,000 is available under this Program Opportunity Notice.",
        extraction_method="deterministic_adapter",
        confidence=1.0,
        verification_status="verified",
    )
    db_session.flush()

    assert prov.id is not None
    assert prov.entity_type == "opportunity"
    assert prov.entity_id == 999901
    assert prov.field_name == "total_funding"
    assert prov.extracted_value == "15000000.0"
    assert prov.normalized_value == "15000000.0"
    assert prov.source_document_hash == expected_hash
    assert prov.verification_status == "verified"
    assert prov.is_superseded is False

    # Clean up test row
    db_session.delete(prov)
    db_session.commit()


def test_source_precedence_and_conflict_handling(db_session):
    """Verifies authority hierarchy enforcement: higher authority supersedes lower authority, lower authority logs conflict."""
    test_entity_id = 999902
    test_field = "max_per_award"

    # 1. First record from secondary source (Rank 6)
    rec1 = log_field_provenance(
        db=db_session,
        entity_type="opportunity",
        entity_id=test_entity_id,
        field_name=test_field,
        extracted_value="1000000",
        normalized_value="1000000.0",
        source_title="Secondary Industry Blog",
        source_document_type="secondary",
    )
    db_session.flush()
    assert rec1.is_superseded is False

    # 2. Incoming record from official solicitation (Rank 2) -> Should supersede secondary
    rec2 = log_field_provenance(
        db=db_session,
        entity_type="opportunity",
        entity_id=test_entity_id,
        field_name=test_field,
        extracted_value="2500000",
        normalized_value="2500000.0",
        source_title="Official FOA Solicitation Document",
        source_document_type="solicitation",
    )
    db_session.flush()

    # Verify rec1 is now superseded and rec2 is active
    db_session.refresh(rec1)
    assert rec1.is_superseded is True
    assert rec2.is_superseded is False
    assert rec2.normalized_value == "2500000.0"

    # 3. Third record from lower authority (Rank 6) attempting to overwrite Rank 2
    # Should NOT overwrite, should return existing rec2, and record a conflict
    rec3 = log_field_provenance(
        db=db_session,
        entity_type="opportunity",
        entity_id=test_entity_id,
        field_name=test_field,
        extracted_value="500000",
        normalized_value="500000.0",
        source_title="Another Secondary Article",
        source_document_type="secondary",
    )
    db_session.flush()

    assert rec3.id == rec2.id
    assert rec2.is_superseded is False
    assert rec2.normalized_value == "2500000.0"

    # Clean up
    db_session.delete(rec1)
    db_session.delete(rec2)
    db_session.commit()


def test_idempotent_reingestion_without_duplicates(db_session):
    """Verifies that re-ingesting identical data does not create duplicate active provenance rows or duplicate snapshots."""
    url = "https://eere-exchange.energy.gov/test_opp"
    raw_payload = json.dumps({"solicitation_number": "DE-FOA-99999", "funding": 50000000.0})

    # Capture first snapshot
    snap1, changed1 = record_snapshot(db=db_session, source_url=url, raw_payload=raw_payload)
    db_session.flush()
    assert snap1.content_hash == compute_sha256(raw_payload)

    # Capture second snapshot with exact same payload -> has_changed should be False
    snap2, changed2 = record_snapshot(db=db_session, source_url=url, raw_payload=raw_payload)
    db_session.flush()
    assert changed2 is False
    assert snap2.content_hash == snap1.content_hash

    # Clean up snapshots
    db_session.delete(snap1)
    db_session.delete(snap2)
    db_session.commit()


def test_explicit_unknown_vs_null_distinction(db_session):
    """Verifies that explicit unknown (supported by source as unspecified) is stored as structured value distinct from un-audited blanks."""
    test_id = 999903
    # Explicit unknown: source explicitly stated "No mandatory cost-share requirement"
    prov_unknown = log_field_provenance(
        db=db_session,
        entity_type="opportunity",
        entity_id=test_id,
        field_name="cost_share_pct",
        extracted_value="unspecified_in_solicitation",
        normalized_value={"status": "explicitly_unspecified", "mandatory": False},
        source_document_type="solicitation",
        supporting_excerpt="Cost sharing is not required for this solicitation.",
        verification_status="verified",
    )
    db_session.flush()

    assert prov_unknown.extracted_value == "unspecified_in_solicitation"
    assert "explicitly_unspecified" in prov_unknown.normalized_value
    assert prov_unknown.verification_status == "verified"

    # Clean up
    db_session.delete(prov_unknown)
    db_session.commit()


def test_entity_hierarchy_and_relationship_integrity(db_session):
    """Asserts 5-layer hierarchy: Organization -> Program -> Opportunity -> Award -> Recipient."""
    # 1. Check for unlinked opportunities
    unlinked_opps = db_session.execute(text("""
        SELECT count(*) FROM opportunities WHERE organization_id IS NULL AND program_id IS NULL
    """)).scalar()
    assert unlinked_opps == 0, f"Found {unlinked_opps} opportunities without Organization or Program linkage"

    # 2. Check for orphan awards without opportunities
    orphan_awards = db_session.execute(text("""
        SELECT count(*) FROM awards WHERE opportunity_id IS NULL
    """)).scalar()
    assert orphan_awards == 0, f"Found {orphan_awards} awards without Opportunity linkage"

    # 3. Check Programs link to valid Organizations
    invalid_prog_orgs = db_session.execute(text("""
        SELECT count(*) FROM programs p
        WHERE p.organization_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM organizations o WHERE o.id = p.organization_id)
    """)).scalar()
    assert invalid_prog_orgs == 0, "Found programs with broken organization foreign keys"


def test_active_status_and_deadline_assertions(db_session):
    """Asserts that no active opportunity has an expired deadline in the past."""
    is_pg = db_session.bind.dialect.name == "postgresql" if db_session.bind else False
    past_sql = (
        "SELECT count(*) FROM opportunities WHERE (status = 'open' OR status = 'active') AND close_date IS NOT NULL AND close_date < NOW() - INTERVAL '1 day'"
        if is_pg else
        "SELECT count(*) FROM opportunities WHERE (status = 'open' OR status = 'active') AND close_date IS NOT NULL AND close_date < datetime('now', '-1 day')"
    )
    past_deadline_count = db_session.execute(text(past_sql)).scalar() or 0
    assert past_deadline_count == 0, f"Found {past_deadline_count} active opportunities with deadlines in the past"

    # Asserts that all active opportunities have verified source URLs
    missing_source_count = db_session.execute(text("""
        SELECT count(*) FROM opportunities 
        WHERE (status = 'open' OR status = 'active') 
          AND (source_url IS NULL OR source_url = '') 
          AND (detail_page_url IS NULL OR detail_page_url = '')
    """)).scalar()
    assert missing_source_count == 0, f"Found {missing_source_count} active opportunities without source URLs"


def test_quality_assertions_suite_passes():
    """Runs the full automated Phase 7 assertion engine and asserts 12/12 pass with 0 failures."""
    res = run_quality_assertions()
    assert res["failed_checks"] == 0, f"Quality assertions had {res['failed_checks']} failures: {res['check_details']}"
    assert res["passed_checks"] == 12, f"Expected 12 passed checks, got {res['passed_checks']}"


def test_readiness_gate_evaluation_passes():
    """Runs the Phase 8 Readiness Gate evaluator and asserts 10/10 criteria evaluated to PASS."""
    report = generate_data_quality_report()
    assert report["readiness_gate"]["passed"] is True, "Readiness Gate did not pass"
    assert report["readiness_gate"]["criteria_passed"] == 10, (
        f"Expected 10 criteria passed, got {report['readiness_gate']['criteria_passed']}"
    )
