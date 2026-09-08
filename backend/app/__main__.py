"""CLI entry point for Energy Innovation Terminal.

Usage:
    python -m app.ingest --all
    python -m app.ingest --current
    python -m app.ingest --historical
    python -m app.ingest --closed
    python -m app.ingest --programs
    python -m app.check_updates
    python -m app.audit
"""

import argparse
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("nyserda")


def cmd_ingest(args):
    """Run data ingestion."""
    from app.database import init_db, init_fts, SessionLocal

    logger.info("Initializing database...")
    init_db()
    init_fts()

    db = SessionLocal()
    try:
        if args.all or args.current:
            logger.info("=== Ingesting current opportunities from NYSERDA API ===")
            from app.ingest.funding_api import FundingAPIAdapter
            with FundingAPIAdapter() as adapter:
                stats = adapter.ingest(db)
                logger.info(f"Current opportunities: {stats}")

        if args.all or args.programs:
            logger.info("=== Ingesting program data ===")
            from app.ingest.programs import ProgramsAdapter
            with ProgramsAdapter() as adapter:
                stats = adapter.ingest(db)
                logger.info(f"Programs: {stats}")

        if args.all or args.historical:
            logger.info("=== Ingesting historical R&D projects from Open NY ===")
            from app.ingest.socrata import SocrataAdapter
            with SocrataAdapter() as adapter:
                stats = adapter.ingest(db)
                logger.info(f"Historical projects: {stats}")

        if args.all or args.closed:
            logger.info("=== Ingesting closed opportunities ===")
            from app.ingest.closed import ClosedOpportunitiesAdapter
            with ClosedOpportunitiesAdapter() as adapter:
                stats = adapter.ingest(db)
                logger.info(f"Closed opportunities: {stats}")

        # Rebuild FTS after ingestion
        logger.info("Rebuilding FTS indexes...")
        _rebuild_fts(db)

        logger.info("Ingestion complete!")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


def _rebuild_fts(db):
    """Rebuild FTS5 indexes."""
    from sqlalchemy import text

    try:
        # Rebuild opportunities FTS
        db.execute(text("DELETE FROM opportunities_fts"))
        db.execute(text("""
            INSERT INTO opportunities_fts(rowid, solicitation_number, name, short_description)
            SELECT id, solicitation_number, name, COALESCE(short_description, '')
            FROM opportunities
        """))

        # Rebuild historical projects FTS
        db.execute(text("DELETE FROM historical_projects_fts"))
        db.execute(text("""
            INSERT INTO historical_projects_fts(rowid, project_title, contractor_name, project_description, technology_1, technology_2, technology_3)
            SELECT id, project_title, COALESCE(contractor_name, ''), COALESCE(project_description, ''),
                   COALESCE(technology_1, ''), COALESCE(technology_2, ''), COALESCE(technology_3, '')
            FROM historical_projects
        """))

        # Rebuild programs FTS
        db.execute(text("DELETE FROM programs_fts"))
        db.execute(text("""
            INSERT INTO programs_fts(rowid, name, description)
            SELECT id, name, COALESCE(description, '')
            FROM programs
        """))

        db.commit()
        logger.info("FTS indexes rebuilt successfully")
    except Exception as e:
        logger.warning(f"FTS rebuild warning: {e}")
        db.rollback()


def cmd_audit(args):
    """Run data quality audit."""
    from app.database import SessionLocal
    from app.audit import run_audit

    db = SessionLocal()
    try:
        summary = run_audit(db)
        print(f"\n{'='*60}")
        print("DATA QUALITY AUDIT REPORT")
        print(f"{'='*60}")
        print(f"Total issues: {summary['total_issues']}")
        print(f"  Critical: {summary['critical']}")
        print(f"  Warning:  {summary['warning']}")
        print(f"  Info:     {summary['info']}")
        print(f"{'='*60}")
        for issue in summary["issues"]:
            icon = {"critical": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue["severity"], "?")
            print(f"  {icon} [{issue['type']}] {issue['description']}")
        print(f"{'='*60}\n")
    finally:
        db.close()


def cmd_check_updates(args):
    """Check for updates since last run."""
    from app.database import SessionLocal
    from app.models.source import ChangeEvent

    logger.info("Checking for updates...")

    # Run current opportunities ingestion
    from app.database import init_db, init_fts
    init_db()
    init_fts()

    db = SessionLocal()
    try:
        from app.ingest.funding_api import FundingAPIAdapter
        with FundingAPIAdapter() as adapter:
            stats = adapter.ingest(db)

        # Show recent changes
        from datetime import datetime, timedelta, timezone
        since = datetime.now(timezone.utc) - timedelta(days=7)
        changes = db.query(ChangeEvent).filter(ChangeEvent.detected_at >= since).order_by(ChangeEvent.detected_at.desc()).all()

        print(f"\n{'='*60}")
        print("UPDATE CHECK RESULTS")
        print(f"{'='*60}")
        print(f"Ingestion: {stats}")
        print(f"Changes in last 7 days: {len(changes)}")
        for change in changes:
            print(f"  [{change.change_type}] {change.entity_type}: {change.entity_id} - {change.entity_name or ''}")
            if change.field_name:
                print(f"    {change.field_name}: {change.old_value} → {change.new_value}")
        print(f"{'='*60}\n")
    finally:
        db.close()


def cmd_enrich(args):
    """Run master enrichment and linkage across all tables."""
    from app.ingest.master_enrichment_suite import run_master_enrichment
    from app.database import init_db
    logger.info("Running Master Database Enrichment & Linkage Suite...")
    init_db()
    stats = run_master_enrichment()
    print(f"\n{'='*60}")
    print("MASTER ENRICHMENT COMPLETED")
    print(f"{'='*60}")
    for k, v in stats.items():
        print(f"  {k:30}: {v:,}")
    print(f"{'='*60}\n")


def cmd_migrate_postgres(args):
    """Run migration to PostgreSQL database."""
    from app.migrate_to_postgres import run_full_migration_pipeline
    logger.info(f"Starting PostgreSQL Migration Pipeline (Target: {args.target_url or 'default'})...")
    res = run_full_migration_pipeline(args.target_url)
    print(f"\n{'='*60}")
    print("POSTGRESQL MIGRATION SUMMARY")
    print(f"{'='*60}")
    print(res)
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Energy Innovation Terminal CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Run data ingestion")
    ingest_parser.add_argument("--all", action="store_true", help="Ingest from all sources")
    ingest_parser.add_argument("--current", action="store_true", help="Current opportunities only")
    ingest_parser.add_argument("--historical", action="store_true", help="Historical R&D projects")
    ingest_parser.add_argument("--closed", action="store_true", help="Closed opportunities")
    ingest_parser.add_argument("--programs", action="store_true", help="Programs and commercialization")
    ingest_parser.set_defaults(func=cmd_ingest)

    # Enrich command
    enrich_parser = subparsers.add_parser("enrich", help="Run master enrichment and linkages")
    enrich_parser.set_defaults(func=cmd_enrich)

    # Migrate Postgres command
    pg_parser = subparsers.add_parser("migrate_postgres", help="Migrate all data to PostgreSQL")
    pg_parser.add_argument("--target-url", type=str, default=None, help="Target PostgreSQL connection URL")
    pg_parser.set_defaults(func=cmd_migrate_postgres)

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Run data quality audit")
    audit_parser.set_defaults(func=cmd_audit)

    # Check updates command
    updates_parser = subparsers.add_parser("check_updates", help="Check for updates")
    updates_parser.set_defaults(func=cmd_check_updates)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
