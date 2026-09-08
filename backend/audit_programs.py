import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

c = engine.connect()

print('=== programs columns ===')
print([d[1] for d in c.execute(text('PRAGMA table_info(programs)')).fetchall()])

print('\n=== opportunities columns (program-related) ===')
cols = [d[1] for d in c.execute(text('PRAGMA table_info(opportunities)')).fetchall()]
print([c for c in cols if 'program' in c.lower() or 'agency' in c.lower()])

print('\n=== sample programs ===')
for r in c.execute(text('SELECT id, name, program_type, parent_program FROM programs LIMIT 15')).fetchall():
    print(r)

print('\n=== opps per program+agency ===')
for r in c.execute('''
    SELECT p.id, p.name, o.agency, COUNT(*) as cnt
    FROM opportunities o
    JOIN programs p ON p.id = o.program_id
    GROUP BY p.id, o.agency
    ORDER BY cnt DESC
    LIMIT 20
''').fetchall():
    print(r)

print('\n=== agencies with programs ===')
for r in c.execute('''
    SELECT o.agency, COUNT(DISTINCT o.program_id) as prog_count, COUNT(*) as opp_count
    FROM opportunities o
    WHERE o.program_id IS NOT NULL
    GROUP BY o.agency
    ORDER BY opp_count DESC
''').fetchall():
    print(r)
