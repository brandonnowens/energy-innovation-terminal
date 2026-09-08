"""Runner script for backfilling general programs."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import (
    analysis, award, community, contact, opportunity,
    opportunity_organization, organization, program, project, relationship, source
)
from app.ingest.backfill_general_programs import backfill_general_programs
from sqlalchemy import text

def run():
    print("=== Starting General Programs Creation & Opportunity Linking ===")
    db = SessionLocal()
    try:
        stats = backfill_general_programs(db)
        print("\n=== Backfill Summary ===")
        for k, v in stats.items():
            print(f"  {k}: {v:,}" if isinstance(v, (int, float)) else f"  {k}: {v}")

        # Rebuild programs_fts virtual table
        print("\nRebuilding programs_fts virtual table...")
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM programs_fts"))
            conn.execute(text(
                "INSERT INTO programs_fts(rowid, name, description) "
                "SELECT id, name, COALESCE(description, '') FROM programs"
            ))
            conn.commit()
        print("programs_fts virtual table updated successfully!")

    except Exception as e:
        print(f"Error during general programs backfill: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run()
