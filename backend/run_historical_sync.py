"""Runner script for comprehensive historical synchronization."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import opportunity, award, source, program, project, analysis
from app.ingest.sync_historical import sync_all_historical
from sqlalchemy import text

def run():
    print("=== Starting Full Historical Data Synchronization ===")
    db = SessionLocal()
    try:
        stats = sync_all_historical(db)
        print("\n=== Synchronization Complete ===")
        for k, v in stats.items():
            print(f"  {k}: {v:,}" if isinstance(v, (int, float)) else f"  {k}: {v}")

        # Rebuild FTS indexes
        print("\nRebuilding FTS virtual tables...")
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM opportunities_fts"))
            conn.execute(text(
                "INSERT INTO opportunities_fts(rowid, solicitation_number, name, short_description) "
                "SELECT id, solicitation_number, name, COALESCE(short_description, '') FROM opportunities"
            ))
            conn.commit()
        print("FTS virtual tables updated successfully!")

    except Exception as e:
        print(f"Error during historical synchronization: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run()
