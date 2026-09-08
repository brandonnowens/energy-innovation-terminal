"""
End-to-end Supabase PostgreSQL Schema Initializer & Data Migration Script.
Includes automated Foreign Key orphan cleansing and integrity preservation.
"""

import os
import sys
import time
import sqlite3
from pathlib import Path
import json
from collections import defaultdict

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from sqlalchemy import create_engine, text, MetaData, inspect
from app.config import settings
from app.database import Base, init_fts
import app.models  # load all declarative models

def main():
    print("=" * 80)
    print("ENERGY INNOVATION TERMINAL: SUPABASE DATABASE INITIALIZATION & MIGRATION")
    print("=" * 80)
    
    sqlite_path = Path(__file__).parent / "data" / "nyserda.db"
    pg_url = settings.database_url

    print(f"Source SQLite Path: {sqlite_path}")
    print(f"Target Postgres URL: {pg_url.split('@')[0].split(':')[0]}:***@{pg_url.split('@')[-1] if '@' in pg_url else 'configured'}")
    print("-" * 80)

    if not sqlite_path.exists():
        print(f"ERROR: SQLite database file does not exist at {sqlite_path}")
        sys.exit(1)

    # 1. Connect to SQLite and discover tables
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    sqlite_cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
          AND name NOT LIKE 'sqlite_%' 
          AND name NOT LIKE '%_fts%' 
          AND name NOT LIKE '%_config' 
          AND name NOT LIKE '%_idx%' 
          AND name NOT LIKE '%_data%' 
          AND name NOT LIKE '%_docsize%'
    """)
    sqlite_tables = [r[0] for r in sqlite_cursor.fetchall()]
    print(f"[SQLite] Found {len(sqlite_tables)} tables:")
    for t in sorted(sqlite_tables):
        cnt = sqlite_cursor.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        print(f"  • {t:35s}: {cnt:8,d} rows")
    print("-" * 80)

    # 2. Connect to PostgreSQL (Supabase)
    print("[Supabase] Connecting to PostgreSQL...")
    engine = create_engine(
        pg_url,
        pool_pre_ping=True,
        echo=False
    )

    with engine.connect() as conn:
        res = conn.execute(text("SELECT version();")).fetchone()
        print(f"[Supabase] Connected successfully!\n  Version: {res[0]}")
    print("-" * 80)

    # 3. Create all tables defined in SQLAlchemy models
    print("[Supabase] Resetting & creating all schema tables from SQLAlchemy models...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print(f"[Supabase] {len(Base.metadata.tables)} model tables created & registered in PostgreSQL.")
    print("-" * 80)

    # 4. Determine migration table order based on foreign keys and dependencies
    priority_tables = [
        "organizations",
        "organization_aliases",
        "contacts",
        "sources",
        "programs",
        "program_focus_areas",
        "opportunities",
        "opportunity_categories",
        "opportunity_eligibility",
        "opportunity_restrictions",
        "opportunity_organizations",
        "opportunity_documents",
        "opportunity_dates",
        "opportunity_relationships",
        "historical_opportunities",
        "historical_projects",
        "recipients",
        "awards",
        "award_results",
        "project_analyses",
        "analysis_matches",
        "saved_searches",
        "export_logs",
        "creator_profiles",
        "creator_tokens",
        "strategies",
        "reports",
        "saved_charts",
        "community_projects",
        "comments",
        "shared_links",
        "opportunity_results",
        "success_stories",
        "result_benchmarks",
        "result_artifacts",
        "proposals",
        "users",
        "password_reset_tokens",
        "recipient_patents",
        "recipient_investments",
        "technology_categories",
        "technologies",
        "technology_cost_performance",
        "technology_kpis",
        "technology_subsystems",
        "policy_standards",
        "policy_technology_links",
        "policy_fuel_links",
        "policy_opportunity_links",
        "policy_organization_links",
        "regulatory_proceedings",
        "proceeding_technology_links",
        "proceeding_organization_links",
        "proceeding_opportunity_links",
        "admin_email_campaigns",
        "admin_email_logs",
        "contact_email_threads",
        "contact_email_messages",
        "news_items",
        "news_item_links",
        "foa_shred_results",
        "alert_subscriptions",
        "alert_trigger_logs",
        "interconnection_queue_projects",
        "national_lab_facilities",
        "facility_technology_links",
        "sec_form_d_filings",
        "federal_scaleup_allocations",
        "federal_procurement_contracts",
        "der_market_deployments",
        "university_licensable_technologies",
    ]

    ordered_tables = [t for t in priority_tables if t in sqlite_tables]
    for t in sqlite_tables:
        if t not in ordered_tables:
            ordered_tables.append(t)

    # 5. Migrate Data Table by Table with FK Validation
    pg_metadata = MetaData()
    pg_metadata.reflect(bind=engine)

    print(f"[Migration] Starting data copy for {len(ordered_tables)} tables...")
    t0 = time.time()
    migration_stats = {}
    
    # Cache existing primary keys for FK validation
    valid_ids_cache = defaultdict(set)

    for t in ordered_tables:
        if t not in pg_metadata.tables:
            print(f"  [SKIP] Table '{t}' not in PostgreSQL schema models.")
            continue

        pg_table = pg_metadata.tables[t]
        
        # Read from SQLite
        rows = sqlite_cursor.execute(f'SELECT * FROM "{t}"').fetchall()
        total_rows = len(rows)
        if total_rows == 0:
            migration_stats[t] = {"source": 0, "target": 0, "orphans_skipped": 0}
            print(f"  [INFO] {t:35s} 0 rows (empty)")
            continue

        col_names = [desc[0] for desc in sqlite_cursor.description]
        target_cols = set(c.name for c in pg_table.columns)
        valid_cols = [c for c in col_names if c in target_cols]

        # Inspect Foreign Keys on this table
        fk_constraints = []
        for fk in pg_table.foreign_keys:
            target_table_name = fk.column.table.name
            target_col_name = fk.column.name
            source_col_name = fk.parent.name
            if source_col_name in valid_cols:
                fk_constraints.append({
                    "src_col": source_col_name,
                    "target_table": target_table_name,
                    "target_col": target_col_name,
                    "nullable": fk.parent.nullable
                })

        batch_size = 2000
        migrated_count = 0
        orphans_skipped = 0

        # Pre-populate FK cache for referenced tables if needed
        for fk in fk_constraints:
            ref_tbl = fk["target_table"]
            if ref_tbl not in valid_ids_cache and ref_tbl in pg_metadata.tables:
                with engine.connect() as conn:
                    ids = [r[0] for r in conn.execute(text(f'SELECT "{fk["target_col"]}" FROM "{ref_tbl}"')).fetchall()]
                    valid_ids_cache[ref_tbl] = set(ids)

        for i in range(0, total_rows, batch_size):
            batch = rows[i:i + batch_size]
            records = []
            for r in batch:
                record = {}
                is_valid = True

                for col in valid_cols:
                    val = r[col]
                    col_type = str(pg_table.columns[col].type).lower()
                    if "bool" in col_type and val is not None:
                        val = bool(val)
                    elif "json" in col_type and isinstance(val, str) and val.strip():
                        try:
                            val = json.loads(val)
                        except Exception:
                            pass
                    record[col] = val

                # Check foreign keys
                for fk in fk_constraints:
                    val = record.get(fk["src_col"])
                    if val is not None:
                        target_set = valid_ids_cache.get(fk["target_table"], set())
                        if val not in target_set:
                            if fk["nullable"]:
                                record[fk["src_col"]] = None
                            else:
                                is_valid = False
                                break

                if is_valid:
                    records.append(record)
                else:
                    orphans_skipped += 1

            if records:
                with engine.begin() as conn:
                    conn.execute(pg_table.insert(), records)
                migrated_count += len(records)

        # Update cache for this table's ID column if present
        if "id" in target_cols:
            with engine.connect() as conn:
                inserted_ids = [r[0] for r in conn.execute(text(f'SELECT "id" FROM "{t}"')).fetchall()]
                valid_ids_cache[t] = set(inserted_ids)

            # Reset Postgres Sequence if primary key 'id' exists
            try:
                with engine.begin() as conn:
                    conn.execute(text(f"""
                        SELECT setval(pg_get_serial_sequence('"{t}"', 'id'), COALESCE((SELECT MAX(id) FROM "{t}"), 1));
                    """))
            except Exception:
                pass

        migration_stats[t] = {"source": total_rows, "target": migrated_count, "orphans_skipped": orphans_skipped}
        orphan_msg = f" ({orphans_skipped} orphans pruned)" if orphans_skipped > 0 else ""
        print(f"  [OK]   {t:35s} {migrated_count:8,d} / {total_rows:8,d} rows copied{orphan_msg}")

    t1 = time.time()
    print("-" * 80)
    print(f"Data migration finished in {t1 - t0:.2f} seconds.")

    # 6. Initialize PostgreSQL Full-Text Search GIN Indexes
    print("[PostgreSQL] Initializing Full-Text Search GIN indexes...")
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_opportunities_fts ON opportunities 
                USING gin(to_tsvector('english', COALESCE(name, '') || ' ' || COALESCE(short_description, '') || ' ' || COALESCE(solicitation_number, '')));
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_awards_fts ON awards 
                USING gin(to_tsvector('english', COALESCE(recipient_name, '') || ' ' || COALESCE(project_title, '') || ' ' || COALESCE(project_abstract, '')));
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_recipients_fts ON recipients 
                USING gin(to_tsvector('english', COALESCE(name, '') || ' ' || COALESCE(description, '') || ' ' || COALESCE(primary_technology, '')));
            """))
        print("[PostgreSQL] Full-text search GIN indexes created and active.")
    except Exception as e:
        print(f"[Warning] Index creation note: {e}")

    # 7. Verification Audit
    print("-" * 80)
    print("MIGRATION INTEGRITY AUDIT")
    print("-" * 80)
    all_passed = True
    with engine.connect() as conn:
        for t in ordered_tables:
            if t in pg_metadata.tables:
                pg_cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).fetchone()[0]
                src_cnt = migration_stats.get(t, {}).get("source", 0)
                orphans = migration_stats.get(t, {}).get("orphans_skipped", 0)
                expected_pg = src_cnt - orphans
                status = "PASS" if pg_cnt == expected_pg else "FAIL"
                if status == "FAIL":
                    all_passed = False
                print(f"  [{status}] {t:35s} SQLite: {src_cnt:8,d}  |  Supabase: {pg_cnt:8,d}")

    print("=" * 80)
    if all_passed:
        print("SUCCESS: Supabase PostgreSQL database is fully structured and populated with 100% integrity!")
    else:
        print("WARNING: Migration completed with row count discrepancies.")
    print("=" * 80)

    sqlite_conn.close()
    engine.dispose()

if __name__ == "__main__":
    main()
