import sqlite3
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from sqlalchemy import MetaData
import app.models
from app.database import Base

def check_lengths():
    sqlite_path = Path(__file__).parent / "data" / "nyserda.db"
    conn = sqlite3.connect(sqlite_path)
    c = conn.cursor()

    for table_name, table in Base.metadata.tables.items():
        # Check if table exists in sqlite
        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not c.fetchone():
            continue

        for col in table.columns:
            col_type = col.type
            type_str = str(col_type)
            if "VARCHAR" in type_str.upper() or "STRING" in type_str.upper():
                max_allowed = getattr(col_type, 'length', None)
                if max_allowed:
                    try:
                        c.execute(f'SELECT MAX(LENGTH("{col.name}")) FROM "{table_name}" WHERE "{col.name}" IS NOT NULL')
                        res = c.fetchone()
                        max_in_db = res[0] if res else 0
                        if max_in_db and max_in_db > max_allowed:
                            print(f"TRUNCATION RISK: {table_name}.{col.name} allowed {max_allowed}, but SQLite has {max_in_db}")
                    except Exception as e:
                        pass

if __name__ == "__main__":
    check_lengths()
