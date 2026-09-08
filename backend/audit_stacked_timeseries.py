import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.database import SessionLocal
from app.api.trends import get_stacked_timeseries

db = SessionLocal()

print("=" * 80)
print("AUDITING STACKED TIMESERIES API FOR ALL DIMENSIONS & DATA SOURCES")
print("=" * 80)

dims = ["organization", "technology", "sector", "fuel", "stage"]

print("\n--- AWARDS DATA SOURCE (Executed Real Disbursements) ---")
for dim in dims:
    res = get_stacked_timeseries(dimension=dim, data_source="awards", year_min=2015, year_max=2026, metric="funding", top_n=6, db=db)
    non_zero_years = sum(1 for y in res["data"] if y["total"] > 0)
    total_val = sum(y["total"] for y in res["data"])
    print(f"Dimension '{dim}':")
    print(f"   Series: {res['series']}")
    print(f"   Years with data: {non_zero_years}/{len(res['data'])}, Total: ${total_val/1e9:.2f}B")
    if non_zero_years == 0 or len(res['series']) == 0:
        print(f"   [WARNING] EMPTY DATA for dimension {dim}!")

print("\n--- PIPELINE / SANITIZED DATA SOURCE (Solicitations) ---")
for dim in dims:
    res = get_stacked_timeseries(dimension=dim, data_source="sanitized", year_min=2018, year_max=2026, metric="funding", top_n=6, db=db)
    non_zero_years = sum(1 for y in res["data"] if y["total"] > 0)
    total_val = sum(y["total"] for y in res["data"])
    print(f"Dimension '{dim}':")
    print(f"   Series: {res['series']}")
    print(f"   Years with data: {non_zero_years}/{len(res['data'])}, Total: ${total_val/1e9:.2f}B")
    if non_zero_years == 0 or len(res['series']) == 0:
        print(f"   [WARNING] EMPTY DATA for dimension {dim}!")

db.close()
