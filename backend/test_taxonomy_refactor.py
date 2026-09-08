import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.engine.taxonomy_engine import classify_text_deterministic, CANONICAL_TECHNOLOGIES, CANONICAL_SECTORS, CANONICAL_FUELS, CANONICAL_ACTIVITIES
from collections import Counter, defaultdict

conn = engine.connect()
c = conn.cursor()

print("=" * 80)
print("TESTING DETERMINISTIC TAXONOMY ENGINE ON OPPORTUNITIES")
print("=" * 80)

# Fetch all opportunities
opps = c.execute(text("SELECT o.id, o.agency, o.solicitation_number, o.name, o.short_description, p.name FROM opportunities o LEFT JOIN programs p ON o.program_id = p.id")).fetchall()
print(f"Total opportunities to classify: {len(opps):,}")

tech_counts = Counter()
sector_counts = Counter()
fuel_counts = Counter()
activity_counts = Counter()

sample_checks = []

for idx, (opp_id, agency, sol_num, name, desc, prog_name) in enumerate(opps):
    res = classify_text_deterministic(
        title=name or "",
        description=desc or "",
        program_name=prog_name or "",
        agency=agency or ""
    )
    for t in res["technology"]:
        tech_counts[t] += 1
    for s in res["sector"]:
        sector_counts[s] += 1
    for f in res["fuel"]:
        fuel_counts[f] += 1
    for a in res["activity"]:
        activity_counts[a] += 1

    if idx < 10 or sol_num in ['26-522', 'PON 6088', 'DE-FOA-0003662', 'PEPCODC-URBAN-MICRO-2026', 'HECO-STAGE3-STORAGE-2026']:
        sample_checks.append((opp_id, agency, sol_num, name, res))

print("\n--- NEW CANONICAL TECHNOLOGY DISTRIBUTION ---")
for t, cnt in tech_counts.most_common():
    print(f"   {t:<45}: {cnt:>5} ({cnt/len(opps)*100:>5.1f}%)")

print("\n--- NEW CANONICAL SECTOR DISTRIBUTION ---")
for s, cnt in sector_counts.most_common():
    print(f"   {s:<45}: {cnt:>5} ({cnt/len(opps)*100:>5.1f}%)")

print("\n--- NEW CANONICAL FUEL DISTRIBUTION ---")
for f, cnt in fuel_counts.most_common():
    print(f"   {f:<45}: {cnt:>5} ({cnt/len(opps)*100:>5.1f}%)")

print("\n--- NEW CANONICAL ACTIVITY / STAGE DISTRIBUTION ---")
for a, cnt in activity_counts.most_common():
    print(f"   {a:<45}: {cnt:>5} ({cnt/len(opps)*100:>5.1f}%)")

print("\n--- SAMPLE SPOT-CHECKS ---")
for opp_id, agency, sol_num, name, res in sample_checks[:10]:
    print(f"Opp #{opp_id} [{agency} - {sol_num}]: {name[:60]}")
    print(f"   Tech: {res['technology']}")
    print(f"   Sector: {res['sector']}")
    print(f"   Fuel: {res['fuel']}")
    print(f"   Stage: {res['activity']}\n")

conn.close()
