import sys
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent))
from app.database import engine

with engine.begin() as c:
    print('=== POSTGRESQL TABLE ROW COUNTS ===')
    tables = c.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name")).fetchall()
    for t in tables:
        cnt = c.execute(text(f'SELECT COUNT(*) FROM "{t[0]}"')).scalar()
        print(f'{t[0]}: {cnt}')
    print()
    print('=== OPPORTUNITY CATEGORIES ===')
    for r in c.execute(text('SELECT category_type, COUNT(*), COUNT(DISTINCT category_value) FROM opportunity_categories GROUP BY category_type')).fetchall():
        print(f'  {r[0]}: {r[1]} rows, {r[2]} unique values')
    print()
    print('=== CATEGORY SAMPLES ===')
    for ct in ['technology','sector','fuel','activity','applicant']:
        vals = c.execute(text(f"SELECT DISTINCT category_value FROM opportunity_categories WHERE category_type='{ct}' ORDER BY category_value LIMIT 20")).fetchall()
        if vals: print(f'  {ct}: {[v[0] for v in vals]}')
        else: print(f'  {ct}: NONE')
    print()
    print('=== FINANCIAL COVERAGE ===')
    print('Opps with total_funding:', c.execute(text('SELECT COUNT(*) FROM opportunities WHERE total_funding IS NOT NULL AND total_funding > 0')).scalar())
    print('Opps total:', c.execute(text('SELECT COUNT(*) FROM opportunities')).scalar())
    print('Opps with max_per_award:', c.execute(text('SELECT COUNT(*) FROM opportunities WHERE max_per_award IS NOT NULL AND max_per_award > 0')).scalar())
    print('Awards with amount:', c.execute(text('SELECT COUNT(*) FROM awards WHERE award_amount IS NOT NULL AND award_amount > 0')).scalar())
    print('Awards total:', c.execute(text('SELECT COUNT(*) FROM awards')).scalar())
    print('Awards with lat/lng:', c.execute(text('SELECT COUNT(*) FROM awards WHERE latitude IS NOT NULL')).scalar())
    print()
    print('=== AGENCIES ===')
    for r in c.execute(text('SELECT agency, COUNT(*) FROM opportunities GROUP BY agency ORDER BY COUNT(*) DESC')).fetchall():
        print(f'  {r[0]}: {r[1]}')
    print()
    print('=== PROGRAMS ===')
    for r in c.execute(text('SELECT id, name, active FROM programs ORDER BY name')).fetchall():
        print(f'  {r[0]}: {r[1]} (active={r[2]})')
    print()
    print('=== RELATIONSHIPS ===')
    for r in c.execute(text('SELECT relationship_type, COUNT(*) FROM opportunity_relationships GROUP BY relationship_type')).fetchall():
        print(f'  {r[0]}: {r[1]}')
    print()
    print('=== ORG TYPES ===')
    for r in c.execute(text('SELECT org_type, COUNT(*) FROM organizations GROUP BY org_type')).fetchall():
        print(f'  {r[0]}: {r[1]}')
    print()
    print('=== NYSERDA CHECK ===')
    print('NYSERDA opps:', c.execute(text("SELECT COUNT(*) FROM opportunities WHERE agency='NYSERDA'")).scalar())
    print('NYSERDA opps with funding:', c.execute(text("SELECT COUNT(*) FROM opportunities WHERE agency='NYSERDA' AND total_funding > 0")).scalar())
    print('NYSERDA awards:', c.execute(text("SELECT COUNT(*) FROM awards WHERE agency='NYSERDA'")).scalar())

