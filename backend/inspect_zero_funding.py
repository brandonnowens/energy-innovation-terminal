import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT id, solicitation_number, name, short_description, agency, total_funding, max_per_award, cost_share_pct
        FROM opportunities
        WHERE (status ILIKE 'open%' OR status = 'active') AND (total_funding = 0 OR total_funding IS NULL)
        LIMIT 20
    """)).mappings().all()

    print(f"Sample zero-funding open opportunities ({len(rows)} samples):")
    for r in rows:
        print(f"\nID: {r['id']} | Sol #: {r['solicitation_number']} | Agency: {r['agency']}")
        print(f"Name: {r['name']}")
        print(f"Desc snippet: {(r['short_description'] or '')[:150]}")
