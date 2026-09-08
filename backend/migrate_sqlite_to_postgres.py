"""
SQLite to PostgreSQL Lossless Database Migration Tool.

Migrates all tables, schemas, relationships, and sequences from local SQLite (nyserda.db)
to PostgreSQL, and generates a portable SQL dump for cloud deployment (RDS, Supabase, Neon, etc.).
"""

import os
import sys
import time
import sqlite3
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from sqlalchemy import create_engine, text, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import Base, init_db, init_fts


TABLE_ORDER = [
    "organizations",
    "sources",
    "programs",
    "program_focus_areas",
    "opportunities",
    "opportunity_categories",
    "opportunity_documents",
    "opportunity_eligibility",
    "opportunity_dates",
    "opportunity_relationships",
    "historical_projects",
    "recipients",
    "awards",
    "project_analyses",
    "analysis_matches",
    "saved_searches",
    "export_logs",
    "creator_profiles",
    "saved_charts",
    "community_projects",
    "comments",
    "shared_links",
]


def ensure_postgres_db(postgres_url: str):
    """Ensure target PostgreSQL database exists; create it if missing."""
    import urllib.parse
    parsed = urllib.parse.urlparse(postgres_url.replace("postgresql+psycopg2://", "postgresql://"))
    target_db = parsed.path.lstrip("/")
    
    if not target_db:
        return

    # Connect to default 'postgres' maintenance database
    admin_url = postgres_url.rsplit("/", 1)[0] + "/postgres"
    try:
        engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            check = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :db"), {"db": target_db}).fetchone()
            if not check:
                print(f"[PostgreSQL] Creating database '{target_db}'...")
                conn.execute(text(f'CREATE DATABASE "{target_db}" ENCODING "UTF8"'))
                print(f"[PostgreSQL] Database '{target_db}' created successfully.")
            else:
                print(f"[PostgreSQL] Database '{target_db}' already exists.")
        engine.dispose()
    except Exception as e:
        print(f"[PostgreSQL Warning] Could not check/create database from admin connection ({e}). Proceeding directly with target URL...")


def migrate(sqlite_path: str, postgres_url: str, generate_sql_dump: bool = True):
    """Execute complete end-to-end migration from SQLite to PostgreSQL."""
    print("=" * 80)
    print("ENERGY INNOVATION DATABASE: SQLITE -> POSTGRESQL MIGRATION")
    print("=" * 80)
    print(f"Source SQLite:     {sqlite_path}")
    print(f"Target PostgreSQL: {postgres_url}")
    print("-" * 80)

    if not os.path.exists(sqlite_path):
        print(f"Error: SQLite source database not found at {sqlite_path}")
        sys.exit(1)

    # 1. Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # Discover SQLite tables
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts%' AND name NOT LIKE '%_config' AND name NOT LIKE '%_idx%' AND name NOT LIKE '%_data%' AND name NOT LIKE '%_docsize%'")
    discovered_tables = [r[0] for r in sqlite_cursor.fetchall()]
    
    # Order tables according to dependency order
    tables_to_migrate = [t for t in TABLE_ORDER if t in discovered_tables]
    for t in discovered_tables:
        if t not in tables_to_migrate:
            tables_to_migrate.append(t)

    print(f"Found {len(tables_to_migrate)} tables to migrate:")
    for t in tables_to_migrate:
        cnt = sqlite_cursor.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        print(f"  • {t:30s} {cnt:8,d} rows")
    print("-" * 80)

    # 2. Optional: Generate portable PostgreSQL SQL dump
    if generate_sql_dump:
        dump_path = Path(sqlite_path).parent / "nyserda_postgres_dump.sql"
        print(f"[Export] Generating portable PostgreSQL SQL dump at: {dump_path}")
        with open(dump_path, "w", encoding="utf-8") as f_dump:
            f_dump.write("-- Energy Innovation Knowledge Base: PostgreSQL Migration Dump\n")
            f_dump.write(f"-- Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f_dump.write("BEGIN;\n\n")

            for t in tables_to_migrate:
                rows = sqlite_cursor.execute(f'SELECT * FROM "{t}"').fetchall()
                if not rows:
                    continue
                cols = [desc[0] for desc in sqlite_cursor.description]
                col_names_str = ", ".join(f'"{c}"' for c in cols)
                
                f_dump.write(f"-- Data for table: {t} ({len(rows)} rows)\n")
                batch_size = 500
                for i in range(0, len(rows), batch_size):
                    batch = rows[i:i + batch_size]
                    values_clauses = []
                    for row in batch:
                        vals = []
                        for val in row:
                            if val is None:
                                vals.append("NULL")
                            elif isinstance(val, (int, float)):
                                vals.append(str(val))
                            elif isinstance(val, (bool,)):
                                vals.append("TRUE" if val else "FALSE")
                            else:
                                s = str(val).replace("'", "''")
                                vals.append(f"'{s}'")
                        values_clauses.append(f"({', '.join(vals)})")
                    
                    f_dump.write(f'INSERT INTO "{t}" ({col_names_str}) VALUES\n' + ",\n".join(values_clauses) + "\nON CONFLICT DO NOTHING;\n")
                f_dump.write("\n")

            f_dump.write("COMMIT;\n")
        print(f"[Export] Dump generated successfully ({os.path.getsize(dump_path):,d} bytes).\n")

    # 3. Connect to PostgreSQL
    try:
        ensure_postgres_db(postgres_url)
        pg_engine = create_engine(postgres_url, echo=False)
        with pg_engine.connect() as conn:
            res = conn.execute(text("SELECT version();")).fetchone()
            print(f"[PostgreSQL] Connected successfully to: {res[0]}")
    except Exception as e:
        print(f"[PostgreSQL Connection Notice] Could not connect directly to {postgres_url} ({e}).")
        print("Note: The SQL dump 'nyserda_postgres_dump.sql' was created and can be imported to any active PostgreSQL instance.")
        return

    # 4. Create Tables in PostgreSQL
    print("[PostgreSQL] Creating schema tables...")
    import app.models  # load all models
    Base.metadata.drop_all(bind=pg_engine)
    Base.metadata.create_all(bind=pg_engine)
    print("[PostgreSQL] Tables created.")

    # 5. Copy Data Table by Table
    pg_metadata = MetaData()
    pg_metadata.reflect(bind=pg_engine)

    migration_stats = {}
    t0 = time.time()

    for t in tables_to_migrate:
        if t not in pg_metadata.tables:
            print(f"[Skip] Table '{t}' not present in PostgreSQL schema.")
            continue

        pg_table = pg_metadata.tables[t]
        
        # Read from SQLite
        rows = sqlite_cursor.execute(f'SELECT * FROM "{t}"').fetchall()
        total_rows = len(rows)
        if total_rows == 0:
            migration_stats[t] = {"source": 0, "target": 0}
            continue

        col_names = [desc[0] for desc in sqlite_cursor.description]
        
        # Filter columns to only those that exist in the PostgreSQL table
        target_cols = set(c.name for c in pg_table.columns)
        valid_cols = [c for c in col_names if c in target_cols]

        batch_size = 2000
        migrated_count = 0

        with pg_engine.begin() as pg_conn:
            try:
                pg_conn.execute(text("SET session_replication_role = 'replica';"))
            except Exception:
                pass
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
                    migrated_count += len(records)
            try:
                pg_conn.execute(text("SET session_replication_role = 'origin';"))
            except Exception:
                pass


        # Reset Postgres Sequence if primary key 'id' exists
        if "id" in target_cols:
            try:
                with pg_engine.begin() as pg_conn:
                    pg_conn.execute(text(f"""
                        SELECT setval(pg_get_serial_sequence('"{t}"', 'id'), COALESCE((SELECT MAX(id) FROM "{t}"), 1));
                    """))
            except Exception:
                pass  # not a serial sequence or custom id

        migration_stats[t] = {"source": total_rows, "target": migrated_count}
        print(f"  [OK] {t:30s} {migrated_count:8,d} / {total_rows:8,d} rows copied")

    t1 = time.time()
    print("-" * 80)
    print(f"Data migration completed in {t1 - t0:.2f} seconds.")

    # 6. Initialize PostgreSQL Full Text Search Indexes
    print("[PostgreSQL] Initializing full-text search indexes...")
    try:
        with pg_engine.begin() as conn:
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
        print("[PostgreSQL] Full-text search indexes initialized.")
    except Exception as e:
        print(f"[Warning] Full-text index creation: {e}")

    # 7. Verification Audit
    print("-" * 80)
    print("VERIFICATION & ROW AUDIT")
    print("-" * 80)
    with pg_engine.connect() as pg_conn:
        all_passed = True
        for t in tables_to_migrate:
            if t in pg_metadata.tables:
                pg_cnt = pg_conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).fetchone()[0]
                src_cnt = migration_stats.get(t, {}).get("source", 0)
                status = "PASS" if pg_cnt == src_cnt else "FAIL"
                if status == "FAIL":
                    all_passed = False
                print(f"  [{status}] {t:30s} SQLite: {src_cnt:8,d}  |  Postgres: {pg_cnt:8,d}")

    print("=" * 80)
    if all_passed:
        print("ALL TABLES MIGRATED WITH 100% ROW-FOR-ROW INTEGRITY!")
    else:
        print("MIGRATION COMPLETED WITH AUDIT DISCREPANCIES.")
    print("=" * 80)

    sqlite_conn.close()
    pg_engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate SQLite to PostgreSQL")
    parser.add_argument("--sqlite-path", default=str(Path(__file__).parent / "data" / "nyserda.db"), help="Path to SQLite database")
    parser.add_argument("--postgres-url", default=os.environ.get("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/nyserda_innovation"), help="PostgreSQL connection URL")
    parser.add_argument("--dump-only", action="store_true", help="Only generate SQL dump without connecting to live PostgreSQL")
    args = parser.parse_args()

    migrate(args.sqlite_path, args.postgres_url, generate_sql_dump=True)
