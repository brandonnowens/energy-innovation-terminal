import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine


conn = engine.connect()
c = conn.cursor()
print("All distinct jurisdictions in opportunities:")
for row in c.execute(text("SELECT jurisdiction, count(*) FROM opportunities GROUP BY jurisdiction ORDER BY count(*) DESC")).fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\nUtilities in organizations table:")
for row in c.execute(text("SELECT state, count(*), GROUP_CONCAT(name, ', ') FROM organizations WHERE org_type = 'utility' GROUP BY state ORDER BY state")).fetchall():
    print(f"  {row[0]}: {row[1]} utilities -> {row[2]}")

print("\nHolding companies:")
for row in c.execute(text("SELECT name, domain, city, state FROM organizations WHERE org_type = 'holding_company' ORDER BY name")).fetchall():
    print(f"  {row[0]} ({row[1]}) - {row[2]}, {row[3]}")

conn.close()
