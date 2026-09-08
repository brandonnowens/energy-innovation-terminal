"""Full data audit - check completeness of all ingested data."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.database import SessionLocal, engine
from app.models.opportunity import Opportunity
from app.models.source import IngestionRun
from sqlalchemy import func, text, case

db = SessionLocal()

# Opportunity breakdown
total = db.query(Opportunity).count()

print("=== OPPORTUNITIES BY AGENCY ===")
rows = db.query(
    Opportunity.agency,
    func.count().label("total"),
    func.count(case((Opportunity.is_historical == True, 1))).label("hist"),
).group_by(Opportunity.agency).order_by(func.count().desc()).all()
for agency, cnt, h in rows:
    print(f"  {agency:<25} total={cnt:<6} current={cnt-h:<6} historical={h}")

# Data quality
print()
print("=== DATA QUALITY ===")
with_desc = db.query(Opportunity).filter(Opportunity.short_description != None, Opportunity.short_description != "").count()
with_funding = db.query(Opportunity).filter(Opportunity.total_funding != None).count()
with_max = db.query(Opportunity).filter(Opportunity.max_per_award != None).count()
with_url = db.query(Opportunity).filter(Opportunity.source_url != None).count()
with_year = db.query(Opportunity).filter(Opportunity.year != None).count()
with_keywords = db.query(Opportunity).filter(Opportunity.keywords != None, Opportunity.keywords != "").count()
with_raw = db.query(Opportunity).filter(Opportunity.raw_source_data != None).count()
with_provenance = db.query(Opportunity).filter(Opportunity.data_provenance != None).count()
print(f"  Has description:    {with_desc}/{total} ({100*with_desc//total}%)")
print(f"  Has total_funding:  {with_funding}/{total} ({100*with_funding//total}%)")
print(f"  Has max_per_award:  {with_max}/{total} ({100*with_max//total}%)")
print(f"  Has detail_url:     {with_url}/{total} ({100*with_url//total}%)")
print(f"  Has year:           {with_year}/{total} ({100*with_year//total}%)")
print(f"  Has keywords:       {with_keywords}/{total} ({100*with_keywords//total}%)")
print(f"  Has raw_source_data:{with_raw}/{total} ({100*with_raw//total}%)")
print(f"  Has data_provenance:{with_provenance}/{total} ({100*with_provenance//total}%)")

# Relationships
print()
print("=== RELATIONSHIPS ===")
try:
    rel_count = db.execute(text("SELECT COUNT(*) FROM opportunity_relationships")).scalar()
    print(f"  Relationships detected: {rel_count}")
except Exception as e:
    print(f"  Relationships: {e}")

# FTS
print()
print("=== FULL-TEXT SEARCH ===")
try:
    fts_count = db.execute(text("SELECT COUNT(*) FROM opportunities_fts")).scalar()
    print(f"  FTS indexed: {fts_count}/{total}")
except Exception as e:
    print(f"  FTS: {e}")

# Ingestion runs
print()
print("=== LAST INGESTION RUNS ===")
runs = db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(30).all()
for r in runs:
    added = r.records_added or 0
    updated = r.records_updated or 0
    errors = r.errors or 0
    print(f"  {r.source_name:<25} status={r.status:<8} added={added} updated={updated} errors={errors}")

# Year distribution for historical
print()
print("=== YEAR DISTRIBUTION (where year is set) ===")
year_rows = db.query(Opportunity.year, func.count()).filter(Opportunity.year != None).group_by(Opportunity.year).order_by(Opportunity.year.desc()).limit(15).all()
for yr, cnt in year_rows:
    print(f"  {yr}: {cnt}")

db.close()
