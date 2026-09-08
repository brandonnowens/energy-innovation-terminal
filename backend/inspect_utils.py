import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine


c = engine.connect()
print('=== Opportunities for NY Utilities ===')
for row in c.execute(text("SELECT id, solicitation_number, name, agency, jurisdiction, org_type, total_funding, organization_id, program_id, service_territory FROM opportunities WHERE jurisdiction = 'utility_ny' OR org_type = 'utility'")).fetchall():
    print(row)

print('\n=== Opportunity Organizations links for utility opps ===')
for row in c.execute(text("SELECT oo.id, oo.opportunity_id, oo.organization_id, oo.role, o.name, org.name FROM opportunity_organizations oo JOIN opportunities o ON o.id = oo.opportunity_id LEFT JOIN organizations org ON org.id = oo.organization_id WHERE o.org_type = 'utility' OR o.jurisdiction LIKE 'utility%'")).fetchall():
    print(row)

print('\n=== Programs for utilities ===')
for row in c.execute(text("SELECT p.id, p.name, p.program_type, p.description FROM programs p WHERE p.name LIKE '%Con Ed%' OR p.name LIKE '%Grid%' OR p.name LIKE '%LIPA%' OR p.name LIKE '%NYPA%' OR p.name LIKE '%Central Hudson%' OR p.name LIKE '%NYSEG%' OR p.name LIKE '%PSEG%' OR p.name LIKE '%RG&E%'")).fetchall():
    print(row)
