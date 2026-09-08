import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

import re
from collections import Counter, defaultdict

conn = engine.connect()
c = conn.cursor()

print("=" * 80)
print("AUDITING FALSE POSITIVES & OVER-INFERENCES")
print("=" * 80)

# Check opportunities where astronomy / biology / medicine / non-energy was tagged with clean energy techs
non_energy_terms = [
    ('astronomy', ['astronomy', 'astronomical', 'astrophysics', 'telescope', 'cosmology', 'planetary']),
    ('biomedical', ['biomedical', 'clinical trial', 'cancer', 'neurology', 'therapeutic', 'pharmacology', 'immunology', 'genomics', 'cellular']),
    ('pure math/physics', ['quantum gravity', 'string theory', 'algebraic topology', 'number theory', 'high energy physics particle']),
]

for domain, keywords in non_energy_terms:
    print(f"\n--- Checking for {domain} tagged with Clean Energy ---")
    placeholders = " OR ".join(["o.name LIKE ? OR o.short_description LIKE ?" for _ in keywords])
    params = []
    for kw in keywords:
        params.extend([f"%{kw}%", f"%{kw}%"])
    
    query = f"""
        SELECT o.id, o.agency, o.solicitation_number, o.name, oc.category_type, oc.category_value
        FROM opportunities o
        JOIN opportunity_categories oc ON o.id = oc.opportunity_id
        WHERE ({placeholders})
        AND oc.category_type = 'technology'
        LIMIT 10
    """
    rows = c.execute(query, params).fetchall()
    print(f"Found sample matches for {domain}: {len(rows)}")
    for r in rows:
        print(f"   Opp #{r[0]} [{r[1]} - {r[2]}]: '{r[3][:60]}' -> {r[4]}: {r[5]}")

# Check specific keyword collisions in opportunities
collisions = [
    ("Solar PV in Astrophysics/Astronomy", "SELECT o.id, o.agency, o.name, oc.category_value FROM opportunities o JOIN opportunity_categories oc ON o.id=oc.opportunity_id WHERE oc.category_value='Solar PV' AND (o.name LIKE '%astronomy%' OR o.name LIKE '%astrophysics%' OR o.name LIKE '%telescope%')"),
    ("AI/ML matched on 'ml' (milliliters/etc)", "SELECT o.id, o.agency, o.name, oc.category_value FROM opportunities o JOIN opportunity_categories oc ON o.id=oc.opportunity_id WHERE oc.category_value='AI/ML' AND o.name NOT LIKE '%intelligence%' AND o.name NOT LIKE '%machine learning%' AND o.name NOT LIKE '%ai%' AND (o.short_description NOT LIKE '%artificial intelligence%' AND o.short_description NOT LIKE '%machine learning%')"),
    ("DERs matched on 'der'", "SELECT o.id, o.agency, o.name, oc.category_value FROM opportunities o JOIN opportunity_categories oc ON o.id=oc.opportunity_id WHERE oc.category_value='DERs' AND o.name NOT LIKE '%distributed energy%' AND o.short_description NOT LIKE '%distributed energy%'"),
    ("Maritime/Ports matched on 'port'", "SELECT o.id, o.agency, o.name, oc.category_value FROM opportunities o JOIN opportunity_categories oc ON o.id=oc.opportunity_id WHERE oc.category_value='Maritime/Ports' AND o.name NOT LIKE '%maritime%' AND o.name NOT LIKE '%marine%' AND o.name NOT LIKE '%port facility%' AND o.name NOT LIKE '%seaport%' AND o.name NOT LIKE '%harbor%'"),
]

print("\n" + "=" * 80)
print("SPECIFIC KEYWORD COLLISION AUDIT:")
print("=" * 80)
for label, sql in collisions:
    matches = c.execute(sql).fetchall()
    print(f"\n{label}: {len(matches)} suspicious records found")
    for m in matches[:5]:
        print(f"   Opp #{m[0]} [{m[1]}]: '{m[2][:60]}' -> Tag: {m[3]}")

conn.close()
