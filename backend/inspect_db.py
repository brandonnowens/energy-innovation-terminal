import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text, inspect
from app.database import engine

print(f"=== Database Engine: {engine.dialect.name} ===")
with engine.connect() as conn:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    print(f"Total tables: {len(table_names)}")
    for t in sorted(table_names):
        try:
            cnt = conn.execute(text(f'SELECT count(*) FROM "{t}"')).scalar()
            print(f"  {t:35s}: {cnt:,}")
        except Exception as e:
            print(f"  {t:35s}: error ({e})")

