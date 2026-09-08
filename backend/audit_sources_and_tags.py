import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

from collections import Counter, defaultdict

conn = engine.connect()
c = conn.cursor()

print("=" * 80)
print("OPPORTUNITY SOURCE & INFERENCE AUDIT")
print("=" * 80)

# Check opportunities by agency
print("Opportunities by Agency:")
for ag, cnt in c.execute(text("SELECT agency, COUNT(*) FROM opportunities GROUP BY agency ORDER BY COUNT(*) DESC LIMIT 15")):
    print(f"   {ag:<35}: {cnt:,}")

# Check opportunities by program
print("\nTop 15 Programs with most opportunities:")
for prog, cnt in c.execute(text("SELECT p.name, COUNT(o.id) FROM opportunities o LEFT JOIN programs p ON o.program_id = p.id GROUP BY p.name ORDER BY COUNT(o.id) DESC LIMIT 15")):
    print(f"   {str(prog):<45}: {cnt:,}")

# Check NYSERDA solicitations (PONs/RFPs)
print("\nSample NYSERDA solicitations and their current tags:")
for r in c.execute(text("SELECT o.id, o.solicitation_number, o.name, p.name FROM opportunities o LEFT JOIN programs p ON o.program_id = p.id WHERE o.agency='NYSERDA' LIMIT 8")):
    cats = c.execute("SELECT category_type, category_value FROM opportunity_categories WHERE opportunity_id=?", (r[0],)).fetchall()
    print(f"   [{r[1]}] {r[2][:50]} (Prog: {r[3]})")
    by_type = defaultdict(list)
    for t, v in cats:
        by_type[t].append(v)
    for t, vals in by_type.items():
        print(f"      - {t}: {vals}")

# Check DOE solicitations
print("\nSample DOE solicitations and their current tags:")
for r in c.execute(text("SELECT o.id, o.solicitation_number, o.name, p.name FROM opportunities o LEFT JOIN programs p ON o.program_id = p.id WHERE o.agency='DOE' LIMIT 8")):
    cats = c.execute("SELECT category_type, category_value FROM opportunity_categories WHERE opportunity_id=?", (r[0],)).fetchall()
    print(f"   [{r[1]}] {r[2][:50]} (Prog: {r[3]})")
    by_type = defaultdict(list)
    for t, v in cats:
        by_type[t].append(v)
    for t, vals in by_type.items():
        print(f"      - {t}: {vals}")

# Check NSF solicitations
print("\nSample NSF solicitations and their current tags:")
for r in c.execute(text("SELECT o.id, o.solicitation_number, o.name, p.name FROM opportunities o LEFT JOIN programs p ON o.program_id = p.id WHERE o.agency='NSF' LIMIT 8")):
    cats = c.execute("SELECT category_type, category_value FROM opportunity_categories WHERE opportunity_id=?", (r[0],)).fetchall()
    print(f"   [{r[1]}] {r[2][:50]} (Prog: {r[3]})")
    by_type = defaultdict(list)
    for t, v in cats:
        by_type[t].append(v)
    for t, vals in by_type.items():
        print(f"      - {t}: {vals}")

conn.close()
