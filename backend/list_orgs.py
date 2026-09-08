import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

c = engine.connect()
print("=== ORGANIZATIONS ===")
for r in c.execute(text('SELECT DISTINCT agency FROM opportunities ORDER BY agency')).fetchall():
    print(r[0])
print("\n=== AWARD AGENCIES ===")
for r in c.execute(text('SELECT DISTINCT agency, COUNT(*) as cnt FROM awards GROUP BY agency ORDER BY cnt DESC')).fetchall():
    print(f"  {r[0]}: {r[1]}")
