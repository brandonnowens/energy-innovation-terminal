import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

conn = engine.connect()

print("=" * 60)
print("FINAL DATA INTEGRITY AUDIT")
print("=" * 60)

# Core table counts
tables = {
    'organizations': 'Organizations',
    'programs': 'Programs',
    'opportunities': 'Opportunities',
    'awards': 'Awards',
    'historical_projects': 'Historical Projects',
    'opportunity_relationships': 'Opportunity Relationships',
    'opportunity_organizations': 'Opp-Org Links',
    'opportunity_categories': 'Categories',
    'eligibility_rules': 'Eligibility Rules',
    'opportunity_restrictions': 'Restrictions',
    'opportunity_rounds': 'Rounds',
    'opportunity_contacts': 'Contacts',
    'opportunity_documents': 'Documents',
}

print("\n--- Table Row Counts ---")
for table, label in tables.items():
    try:
        cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar()
        print(f"  {label:30s}: {cnt:,}")
    except Exception as e:
        print(f"  {label:30s}: ERROR - {e}")

# Agency coverage
print("\n--- Opportunities by Agency ---")
for r in conn.execute(text("SELECT agency, COUNT(*) as cnt FROM opportunities GROUP BY agency ORDER BY cnt DESC")).fetchall():
    print(f"  {r[0] or 'Unknown':25s}: {r[1]:,}")

# Awards coverage
print("\n--- Awards by Agency ---")
for r in conn.execute(text("SELECT agency, COUNT(*) as cnt, COALESCE(SUM(award_amount), 0) as total FROM awards GROUP BY agency ORDER BY cnt DESC")).fetchall():
    total_str = f"${r[2]/1e6:.1f}M" if r[2] >= 1e6 else f"${r[2]:,.0f}"
    print(f"  {r[0] or 'Unknown':25s}: {r[1]:,} awards ({total_str})")

# Integrity checks
print("\n--- Integrity Checks ---")
opps_missing_prog = conn.execute(text("SELECT COUNT(*) FROM opportunities WHERE program_id IS NULL")).scalar()
print(f"  Opps missing program_id: {opps_missing_prog}")

opps_missing_agency = conn.execute(text("SELECT COUNT(*) FROM opportunities WHERE agency IS NULL OR agency = ''")).scalar()
print(f"  Opps missing agency: {opps_missing_agency}")

orphan_awards = conn.execute(text("SELECT COUNT(*) FROM awards WHERE opportunity_id IS NOT NULL AND opportunity_id NOT IN (SELECT id FROM opportunities)")).scalar()
print(f"  Awards with orphan opportunity_id: {orphan_awards}")

orphan_programs = conn.execute(text("""
    SELECT COUNT(*) FROM programs p
    WHERE p.id NOT IN (SELECT DISTINCT program_id FROM opportunities WHERE program_id IS NOT NULL)
""")).scalar()
print(f"  Orphan programs: {orphan_programs}")

# NYSERDA-specific checks
print("\n--- NYSERDA Program Distribution ---")
for r in conn.execute(text("""
    SELECT p.name, p.program_type, COUNT(o.id) as opp_count
    FROM programs p
    JOIN opportunities o ON o.program_id = p.id
    WHERE o.agency = 'NYSERDA'
    GROUP BY p.id, p.name, p.program_type
    ORDER BY opp_count DESC
""")).fetchall():
    print(f"  {r[0]:45s} ({r[1] or 'N/A':20s}) - {r[2]} opps")

print("\n" + "=" * 60)
print("AUDIT COMPLETE")
print("=" * 60)

conn.close()
