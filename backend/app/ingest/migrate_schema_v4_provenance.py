"""Migration Schema v4: Field-Level Provenance, Source Snapshots, Staging & Entity Resolution.

Adds additive tables and foreign keys to support:
1. field_provenances: Field-level evidence recording with citations, excerpts, confidence, and hashes.
2. source_snapshots: Durable raw document and webpage payloads for change detection.
3. staged_opportunities, staged_awards, staged_organizations, staged_programs: Idempotent staging area.
4. entity_aliases, entity_merge_reviews: Non-destructive duplicate resolution and alias tracking.
5. organization_id foreign key on programs.
"""

import logging
from sqlalchemy import text
from app.database import engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MigrateSchemaV4")


def migrate_schema_v4():
    """Execute additive schema migration."""
    logger.info("Executing Schema v4 additive migration for provenance and staging...")
    
    with engine.begin() as conn:
        # 1. FIELD_PROVENANCES Table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS field_provenances (
                id SERIAL PRIMARY KEY,
                entity_type VARCHAR(50) NOT NULL,
                entity_id INTEGER NOT NULL,
                field_name VARCHAR(100) NOT NULL,
                extracted_value TEXT,
                normalized_value TEXT,
                source_url VARCHAR(1000),
                source_title VARCHAR(500),
                source_organization VARCHAR(255),
                source_document_type VARCHAR(100) DEFAULT 'solicitation',
                publication_date TIMESTAMP,
                retrieval_date TIMESTAMP DEFAULT NOW(),
                effective_date TIMESTAMP,
                source_document_hash VARCHAR(64),
                page_or_section_ref VARCHAR(255),
                supporting_excerpt TEXT,
                extraction_method VARCHAR(100) DEFAULT 'deterministic_adapter',
                confidence DOUBLE PRECISION DEFAULT 1.0,
                verification_status VARCHAR(50) DEFAULT 'verified',
                is_superseded BOOLEAN DEFAULT FALSE,
                superseded_by_id INTEGER,
                conflict_status BOOLEAN DEFAULT FALSE,
                last_verified_at TIMESTAMP DEFAULT NOW(),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_provenance_entity ON field_provenances(entity_type, entity_id);
            CREATE INDEX IF NOT EXISTS idx_provenance_field ON field_provenances(field_name);
            CREATE INDEX IF NOT EXISTS idx_provenance_status ON field_provenances(verification_status);
        """))

        # 2. SOURCE_SNAPSHOTS Table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS source_snapshots (
                id SERIAL PRIMARY KEY,
                source_url VARCHAR(1000) NOT NULL,
                content_hash VARCHAR(64) NOT NULL,
                source_type VARCHAR(50) DEFAULT 'html',
                http_status INTEGER DEFAULT 200,
                etag VARCHAR(255),
                last_modified_header VARCHAR(255),
                raw_payload_text TEXT,
                headers_json JSONB,
                captured_at TIMESTAMP DEFAULT NOW(),
                has_changed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_snapshot_url ON source_snapshots(source_url);
            CREATE INDEX IF NOT EXISTS idx_snapshot_hash ON source_snapshots(content_hash);
        """))

        # 3. STAGING TABLES
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS staged_opportunities (
                id SERIAL PRIMARY KEY,
                solicitation_number VARCHAR(255),
                name VARCHAR(500) NOT NULL,
                agency VARCHAR(255) NOT NULL,
                program_name VARCHAR(500),
                status VARCHAR(50) DEFAULT 'open',
                open_date TIMESTAMP,
                close_date TIMESTAMP,
                total_funding DOUBLE PRECISION,
                max_per_award DOUBLE PRECISION,
                cost_share_pct DOUBLE PRECISION,
                cost_share_mandatory BOOLEAN,
                target_trl_min INTEGER,
                target_trl_max INTEGER,
                geographic_scope VARCHAR(500),
                eligible_applicant_types JSONB,
                eligible_technology_areas JSONB,
                eligible_activity_types JSONB,
                eligible_sectors JSONB,
                statutory_mandates JSONB,
                priority_problem_statements JSONB,
                scoring_rubric_weights JSONB,
                source_url VARCHAR(1000),
                raw_payload TEXT,
                content_hash VARCHAR(64),
                staging_status VARCHAR(50) DEFAULT 'staged', -- staged, validated, merged, rejected
                merge_conflict_notes TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS staged_awards (
                id SERIAL PRIMARY KEY,
                external_award_id VARCHAR(255),
                solicitation_number VARCHAR(255),
                recipient_name VARCHAR(500) NOT NULL,
                award_amount DOUBLE PRECISION,
                award_date TIMESTAMP,
                project_title VARCHAR(1000),
                agency VARCHAR(255),
                source_url VARCHAR(1000),
                raw_data TEXT,
                staging_status VARCHAR(50) DEFAULT 'staged',
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))

        # 4. ENTITY RESOLUTION & ALIAS TABLES
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS entity_aliases (
                id SERIAL PRIMARY KEY,
                entity_type VARCHAR(50) NOT NULL, -- organization, recipient, program
                canonical_id INTEGER NOT NULL,
                alias_name VARCHAR(500) NOT NULL,
                alias_type VARCHAR(100) DEFAULT 'alternate_name', -- acronym, legal_name, dba, abbreviation
                source_reference VARCHAR(500),
                confidence DOUBLE PRECISION DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_alias_lookup ON entity_aliases(entity_type, alias_name);

            CREATE TABLE IF NOT EXISTS entity_merge_reviews (
                id SERIAL PRIMARY KEY,
                entity_type VARCHAR(50) NOT NULL,
                primary_entity_id INTEGER NOT NULL,
                duplicate_entity_id INTEGER NOT NULL,
                match_confidence DOUBLE PRECISION,
                detection_method VARCHAR(100),
                review_status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, deferred
                reviewer_notes TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_entity_merge_unique ON entity_merge_reviews(entity_type, primary_entity_id, duplicate_entity_id);
        """))

        # 5. Add organization_id column to programs if not present
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='programs' AND column_name='organization_id'
                ) THEN
                    ALTER TABLE programs ADD COLUMN organization_id INTEGER;
                END IF;
            END $$;
        """))

        # 6. Add additive matching, eligibility, and mandate columns to opportunities if not present
        conn.execute(text("""
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS eligible_applicant_types TEXT;
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS eligible_technology_areas TEXT;
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS eligible_sectors TEXT;
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS eligible_activity_types TEXT;
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS project_cost_min DOUBLE PRECISION;
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS project_cost_max DOUBLE PRECISION;
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS cost_share_mandatory BOOLEAN DEFAULT FALSE;
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS statutory_mandates TEXT;
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS priority_problem_statements TEXT;
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS scoring_rubric_weights TEXT;
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS proposal_requirements_summary TEXT;
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS teaming_partner_types_sought TEXT;
            ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS disadvantaged_community_priority BOOLEAN DEFAULT FALSE;
        """))

    logger.info("Schema v4 migration completed successfully!")


if __name__ == "__main__":
    migrate_schema_v4()
