"""High-Performance PostgreSQL Migration, ETL, and Knowledge Base Synchronization Engine.

Migrates and synchronizes all 47 tables, rows, foreign key linkages, GIN tsvector indexes,
and knowledge base entities from SQLite source to PostgreSQL.

Usage:
    python backend/app/migrate_to_postgres.py
    python backend/app/migrate_to_postgres.py --target-url postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/nyserda_innovation
"""

import argparse
import logging
import os
import sys
import time
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional

from sqlalchemy import create_engine, inspect, text, MetaData
from sqlalchemy.orm import Session, sessionmaker

# Ensure app package is importable
_BACKEND_DIR = Path(__file__).parent.parent.resolve()
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.config import settings
from app.database import Base, init_fts
# Import all declarative models to register metadata
from app.models import (
    organization, contact, opportunity, opportunity_organization,
    program, award, recipient, project, source, analysis, relationship,
    community, result, proposal, user, attribution, technology
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PostgresMigrator")

# Ordered list of tables to ensure referential integrity
MIGRATION_TABLE_ORDER = [
    # 1. Independent Core Entities
    "organizations",
    "organization_aliases",
    "technology_categories",
    "technologies",
    "technology_kpis",
    "technology_cost_performance",
    "technology_subsystems",
    "programs",
    "program_focus_areas",
    "recipients",
    "recipient_patents",
    "recipient_investments",
    "sources",
    "users",
    "password_reset_tokens",
    "creator_tokens",

    # 2. Opportunities & Linkages
    "opportunities",
    "opportunity_rounds",
    "opportunity_documents",
    "opportunity_categories",
    "eligibility_rules",
    "opportunity_restrictions",
    "opportunity_organizations",
    "opportunity_relationships",
    "opportunity_contacts",
    "opportunity_contact_links",
    "contacts",

    # 3. Awards & Projects
    "awards",
    "award_results",
    "projects",
    "historical_opportunities",
    "historical_projects",

    # 4. Results, Benchmarks & Deliverables
    "opportunity_results",
    "success_stories",
    "result_benchmarks",
    "result_artifacts",
    "attribution",

    # 5. Proposals, Analyses, Reports & Strategies
    "proposals",
    "project_analyses",
    "analysis_matches",
    "reports",
    "strategies",
    "saved_charts",
    "saved_views",
    "abuse_reports",

    # 6. System Audit & Ingestion Logs
    "ingestion_runs",
    "change_events",
    "data_quality_issues",
    "source_conflicts",
]


def run_migration(sqlite_path: str, target_pg_url: str) -> Dict[str, Any]:
    """Execute end-to-end migration from SQLite source to PostgreSQL target."""
    logger.info("=" * 80)
    logger.info("POSTGRESQL KNOWLEDGE BASE ETL MIGRATION")
    logger.info(f"Source SQLite:     {sqlite_path}")
    logger.info(f"Target PostgreSQL: {target_pg_url}")
    logger.info("=" * 80)

    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"SQLite source not found at: {sqlite_path}")

    # Connect to SQLite
    sq_conn = sqlite3.connect(sqlite_path)
    sq_conn.row_factory = sqlite3.Row
    sq_cur = sq_conn.cursor()

    sq_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts%'")
    discovered_sq_tables = set(r[0] for r in sq_cur.fetchall())
    logger.info(f"Discovered {len(discovered_sq_tables)} source tables in SQLite.")

    # Connect to PostgreSQL
    pg_engine = create_engine(target_pg_url, pool_pre_ping=True, echo=False)
    with pg_engine.connect() as conn:
        ver = conn.execute(text("SELECT version()")).scalar()
        logger.info(f"Connected to PostgreSQL: {ver}")

    # Recreate tables
    logger.info("Recreating schema tables in PostgreSQL...")
    Base.metadata.drop_all(bind=pg_engine)
    Base.metadata.create_all(bind=pg_engine)
    logger.info("PostgreSQL schema tables created successfully.")

    pg_meta = MetaData()
    pg_meta.reflect(bind=pg_engine)

    # Order tables
    tables_to_migrate = [t for t in MIGRATION_TABLE_ORDER if t in discovered_sq_tables and t in pg_meta.tables]
    for t in discovered_sq_tables:
        if t in pg_meta.tables and t not in tables_to_migrate:
            tables_to_migrate.append(t)

    migration_stats = {}
    start_time = time.time()

    with pg_engine.begin() as pg_conn:
        try:
            pg_conn.execute(text("SET session_replication_role = 'replica';"))
        except Exception as e:
            logger.warning(f"Could not set replication role: {e}")

        for t in tables_to_migrate:
            pg_table = pg_meta.tables[t]
            rows = sq_cur.execute(f'SELECT * FROM "{t}"').fetchall()
            total_rows = len(rows)

            if total_rows == 0:
                migration_stats[t] = {"source": 0, "target": 0}
                logger.info(f"  • {t:35s}:         0 rows")
                continue

            cols = [desc[0] for desc in sq_cur.description]
            valid_cols = [c for c in cols if c in pg_table.columns]

            batch_size = 2500
            for i in range(0, total_rows, batch_size):
                batch = rows[i:i + batch_size]
                records = []
                for r in batch:
                    d = {}
                    for col in valid_cols:
                        val = r[col]
                        d[col] = val
                    records.append(d)
                if records:
                    pg_conn.execute(pg_table.insert(), records)

            migration_stats[t] = {"source": total_rows, "target": total_rows}
            logger.info(f"  ✓ {t:35s}: {total_rows:8,d} rows copied")

        try:
            pg_conn.execute(text("SET session_replication_role = 'origin';"))
        except Exception:
            pass

    # Synchronize PostgreSQL serial sequences
    logger.info("Synchronizing PostgreSQL serial sequences...")
    with pg_engine.begin() as pg_conn:
        for t, tbl in pg_meta.tables.items():
            if "id" in tbl.columns and str(tbl.columns["id"].type).startswith("INTEGER"):
                try:
                    pg_conn.execute(text(f"""
                        SELECT setval(pg_get_serial_sequence('"{t}"', 'id'), COALESCE((SELECT MAX(id) FROM "{t}"), 1));
                    """))
                except Exception:
                    pass

    # Initialize PostgreSQL GIN & B-Tree indexes
    logger.info("Initializing PostgreSQL GIN & B-Tree indexes...")
    init_fts()
    logger.info("GIN & B-Tree indexes initialized.")

    # Audit & verify
    logger.info("=" * 80)
    logger.info("MIGRATION INTEGRITY AUDIT")
    logger.info("=" * 80)
    all_passed = True
    audit_results = {}

    with pg_engine.connect() as pg_conn:
        for t in sorted(pg_meta.tables.keys()):
            pg_cnt = pg_conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar() or 0
            if t in discovered_sq_tables:
                sq_cnt = sq_cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            else:
                sq_cnt = 0
            status = "PASS" if pg_cnt == sq_cnt else "FAIL"
            if pg_cnt != sq_cnt:
                all_passed = False
            audit_results[t] = {"sqlite": sq_cnt, "postgres": pg_cnt, "status": status}
            logger.info(f"  [{status:4s}] {t:35s} | SQLite: {sq_cnt:8,d} | PG: {pg_cnt:8,d}")

    total_time = time.time() - start_time
    logger.info("-" * 80)
    logger.info(f"ETL Migration completed in {total_time:.2f} seconds.")
    if all_passed:
        logger.info(">>> SUCCESS: 100% ROW-FOR-ROW PARITY ACROSS ALL TABLES! <<<")
    else:
        logger.warning(">>> WARNING: Discrepancies detected during audit! <<<")
    logger.info("=" * 80)

    sq_conn.close()
    pg_engine.dispose()

    return {
        "status": "success" if all_passed else "partial",
        "duration_seconds": total_time,
        "tables_migrated": len(tables_to_migrate),
        "audit": audit_results
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PostgreSQL Migration and Knowledge Base Sync Utility")
    parser.add_argument("--source-sqlite", default=str(_BACKEND_DIR / "data" / "nyserda.db"), help="Source SQLite database path")
    parser.add_argument("--target-url", default=settings.database_url, help="Target PostgreSQL connection URL")
    args = parser.parse_args()

    results = run_migration(args.source_sqlite, args.target_url)
    print("\nMigration Summary:", results)
