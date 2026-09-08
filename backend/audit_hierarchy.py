import sys
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent))
from app.database import engine

with engine.begin() as c:
    print('=== HIERARCHY VIOLATIONS ===')
    print('\n--- Orphan programs (no opportunities) ---')
    for r in c.execute(text('''SELECT p.id, p.name, p.program_type FROM programs p WHERE p.id NOT IN (SELECT DISTINCT program_id FROM opportunities WHERE program_id IS NOT NULL)''')).fetchall():
        print(r)

    print('\n--- Programs with wrong agency ---')
    for r in c.execute(text('''SELECT p.id, p.name, p.program_type, string_agg(DISTINCT o.agency, ', ') as agencies FROM programs p JOIN opportunities o ON o.program_id = p.id GROUP BY p.id, p.name, p.program_type HAVING COUNT(DISTINCT o.agency) > 1''')).fetchall():
        print(r)

    print('\n--- Opps without program ---')
    print(c.execute(text('SELECT COUNT(*) FROM opportunities WHERE program_id IS NULL')).scalar())

    print('\n--- Awards without opportunity ---')
    print(c.execute(text('SELECT COUNT(*) FROM awards WHERE opportunity_id IS NULL OR opportunity_id NOT IN (SELECT id FROM opportunities)')).scalar())

    print('\n--- NYSERDA awardee geo coverage ---')
    for r in c.execute(text('''SELECT 
      COUNT(*) as total,
      SUM(CASE WHEN latitude IS NOT NULL THEN 1 ELSE 0 END) as geocoded,
      SUM(CASE WHEN latitude IS NULL THEN 1 ELSE 0 END) as missing
    FROM awards WHERE agency = 'NYSERDA' ''')).fetchall():
        print(f'total={r[0]}, geocoded={r[1]}, missing={r[2]}')

    print('\n--- All agency geo coverage ---')
    for r in c.execute(text('''SELECT agency, COUNT(*) as total, SUM(CASE WHEN latitude IS NOT NULL THEN 1 ELSE 0 END) as geocoded FROM awards GROUP BY agency ORDER BY total DESC LIMIT 10''')).fetchall():
        print(r)

    print('\n--- NY state awards ---')
    print(c.execute(text("SELECT COUNT(*) FROM awards WHERE recipient_state = 'NY'")).scalar())

    print('\n--- Awards with city but no geocode ---')
    print(c.execute(text("SELECT COUNT(*) FROM awards WHERE recipient_city IS NOT NULL AND recipient_city != '' AND latitude IS NULL")).scalar())

    print('\n--- Awardee status distribution ---')
    for r in c.execute(text('''SELECT 
      CASE WHEN o.status = 'open' THEN 'active_opp' ELSE 'historical_opp' END as opp_status,
      COUNT(DISTINCT a.id) as award_count
    FROM awards a 
    JOIN opportunities o ON o.id = a.opportunity_id
    GROUP BY CASE WHEN o.status = 'open' THEN 'active_opp' ELSE 'historical_opp' END''')).fetchall():
        print(r)

