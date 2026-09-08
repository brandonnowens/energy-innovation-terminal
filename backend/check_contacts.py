import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

c = engine.connect()
r = c.execute(text("SELECT COUNT(*) FROM contacts"))
print("Total contacts:", r.fetchone()[0])
r = c.execute(text("SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL AND email != ''"))
print("With email:", r.fetchone()[0])
r = c.execute(text("SELECT COUNT(*) FROM contacts WHERE email IS NULL OR email = ''"))
print("Without email:", r.fetchone()[0])
r = c.execute(text("SELECT COUNT(*) FROM contacts WHERE phone IS NOT NULL AND phone != ''"))
print("With phone:", r.fetchone()[0])

from sqlalchemy import text, inspect

inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('contacts')]
print("\nContact columns:", columns)

# Sample contacts
r = c.execute(text("SELECT id, name_display, title, email, phone, role_type, institution_name, city, state FROM contacts LIMIT 15"))
print("\nSample contacts:")
for x in r.fetchall():
    print(f"  {x}")

# Check contacts count with address info
r = c.execute(text("SELECT COUNT(*) FROM contacts WHERE city IS NOT NULL AND city != ''"))
print("\nWith city:", r.fetchone()[0])
r = c.execute(text("SELECT COUNT(*) FROM contacts WHERE state IS NOT NULL AND state != ''"))
print("With state:", r.fetchone()[0])

c.close()

