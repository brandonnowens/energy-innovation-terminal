import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

"""Audit awards coverage vs opportunities, and check data completeness."""
import json
from collections import Counter

c = engine.connect()

print("=" * 70)
print("COVERAGE AUDIT: Awards vs Opportunities")
print("=" * 70)

# All agencies with opps
opps = c.execute(text("SELECT agency, COUNT(*) FROM opportunities GROUP BY agency ORDER BY COUNT(*) DESC")).fetchall()
awards = c.execute(text("SELECT agency, COUNT(*) FROM awards GROUP BY agency ORDER BY COUNT(*) DESC")).fetchall()
award_map = dict(awards)

print(f"\n{'Agency':<30} {'Opps':>8} {'Awards':>8} {'Coverage':>10}")
print("-" * 60)
missing_agencies = []
for ag, cnt in opps:
    ac = award_map.get(ag, 0)
    cov = f"{ac/cnt*100:.0f}%" if cnt > 0 else "-"
    flag = " *** MISSING" if ac == 0 else ""
    print(f"{ag:<30} {cnt:>8} {ac:>8} {cov:>10}{flag}")
    if ac == 0:
        missing_agencies.append(ag)

# SBIR agencies not in opps
for ag, ac in awards:
    if ag not in dict(opps):
        print(f"{ag:<30} {'(no opps)':>8} {ac:>8} {'SBIR only':>10}")

print(f"\nAgencies with ZERO awards: {missing_agencies}")

# Data completeness
print(f"\n{'=' * 70}")
print("DATA COMPLETENESS")
print("=" * 70)

fields = [
    ("recipient_name", "Recipient Name"),
    ("recipient_type", "Recipient Type"),
    ("recipient_city", "City"),
    ("recipient_state", "State"),
    ("recipient_zip", "Zip"),
    ("pi_name", "PI Name"),
    ("pi_email", "PI Email"),
    ("award_amount", "Award Amount"),
    ("project_title", "Project Title"),
    ("project_abstract", "Abstract"),
    ("program_name", "Program"),
    ("award_type", "Award Type"),
    ("start_date", "Start Date"),
    ("end_date", "End Date"),
    ("award_date", "Award Date"),
    ("year", "Year"),
    ("cfda_number", "CFDA"),
    ("recipient_uei", "UEI"),
]

total = c.execute(text("SELECT COUNT(*) FROM awards")).fetchone()[0]
print(f"\nTotal awards: {total:,}")
print(f"\n{'Field':<20} {'Filled':>10} {'%':>6}")
print("-" * 40)
for col, label in fields:
    try:
        cnt = c.execute(f"SELECT COUNT(*) FROM awards WHERE {col} IS NOT NULL AND {col} != ''").fetchone()[0]
        print(f"{label:<20} {cnt:>10,} {cnt/total*100:>5.1f}%")
    except:
        print(f"{label:<20} {'N/A':>10}")

# Check SBIR extra data we could extract
print(f"\n{'=' * 70}")
print("SBIR DATA ENRICHMENT POTENTIAL")
print("=" * 70)

# Check if SBIR raw data has company website, employee count etc
sbir_sample = c.execute(text("SELECT source_url FROM awards WHERE source_name='sbir_gov' LIMIT 1")).fetchone()
print(f"SBIR source: {sbir_sample}")

# Check what state-level agencies have no awards
print(f"\nState-level agencies with zero awards:")
for ag in missing_agencies:
    cnt = c.execute("SELECT COUNT(*) FROM opportunities WHERE agency=?", (ag,)).fetchone()[0]
    statuses = c.execute("SELECT status, COUNT(*) FROM opportunities WHERE agency=? GROUP BY status", (ag,)).fetchall()
    print(f"  {ag}: {cnt} opps, statuses: {dict(statuses)}")

# Check existing table columns
cols = c.execute(text("PRAGMA table_info(awards)")).fetchall()
print(f"\nCurrent awards columns: {[col[1] for col in cols]}")

c.close()
