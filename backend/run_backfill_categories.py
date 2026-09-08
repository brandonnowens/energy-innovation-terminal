import sys
import os

# Set up sys.path to ensure we can import from app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
# Must import all models to avoid mapper errors
from app.models import opportunity, award, source, program, project, analysis
from app.ingest.backfill_categories import backfill_all_categories

def run():
    print("Starting category backfill...")
    db = SessionLocal()
    try:
        stats = backfill_all_categories(db)
        print("Backfill complete. Summary stats:")
        print(f"- Opportunities processed: {stats['opportunities_processed']}")
        print(f"- Categories added: {stats['categories_added']}")
        print(f"- Already tagged matches skipped: {stats['already_tagged']}")
    except Exception as e:
        print(f"Error during backfill: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run()
