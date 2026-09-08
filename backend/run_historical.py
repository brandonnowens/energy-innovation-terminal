"""Run only Grants.gov Historical adapter to completion."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.database import SessionLocal
from app.models.opportunity import Opportunity
from sqlalchemy import func

db = SessionLocal()

try:
    print("Running Grants.gov Historical adapter...")
    from app.ingest.grants_gov_historical import GrantsGovHistoricalAdapter
    with GrantsGovHistoricalAdapter() as adapter:
        stats = adapter.ingest(db)
        print(f"  Result: {stats}")

    # Summary
    total = db.query(Opportunity).count()
    hist = db.query(Opportunity).filter(Opportunity.is_historical == True).count()
    counts = db.query(Opportunity.agency, func.count()).group_by(Opportunity.agency).order_by(func.count().desc()).all()
    print(f"\nTotal: {total} (current={total-hist}, historical={hist})")
    for agency, count in counts:
        print(f"  {agency}: {count}")
finally:
    db.close()
