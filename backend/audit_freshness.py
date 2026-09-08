import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

import json

def check_freshness_and_details():
    conn = engine.connect()
    cur = conn

    print("=== OPPORTUNITIES BY YEAR ===")
    for r in cur.execute("""
        SELECT COALESCE(year, 'NULL') as yr, COUNT(*) as cnt,
               SUM(CASE WHEN status='open' THEN 1 ELSE 0 END) as open_cnt
        FROM opportunities
        GROUP BY yr
        ORDER BY yr DESC
        LIMIT 20
    """).fetchall():
        print(f"  Year {r['yr']}: {r['cnt']:>5,d} opps ({r['open_cnt']} open)")

    print("\n=== AWARDS BY YEAR (RECENT 15 YEARS) ===")
    for r in cur.execute("""
        SELECT COALESCE(year, 'NULL') as yr, COUNT(*) as cnt,
               SUM(COALESCE(award_amount, 0)) as total_usd
        FROM awards
        GROUP BY yr
        ORDER BY yr DESC
        LIMIT 15
    """).fetchall():
        print(f"  Year {r['yr']}: {r['cnt']:>6,d} awards | ${r['total_usd']:>15,.2f}")

    print("\n=== SAMPLE UTILITY OPPORTUNITIES ===")
    for r in cur.execute("""
        SELECT solicitation_number, name, agency, total_funding, service_territory, utility_program_type
        FROM opportunities
        WHERE org_type='utility'
        LIMIT 10
    """).fetchall():
        print(f"  [{r['agency']}] {r['solicitation_number']}: {r['name']} | ${r['total_funding']:,.0f} | Territory: {r['service_territory']} | Type: {r['utility_program_type']}")

    print("\n=== SAMPLE STACKABLE RELATIONSHIPS ===")
    for r in cur.execute("""
        SELECT r.relationship_type, r.confidence, r.rationale,
               o1.name as src_name, o1.agency as src_agency,
               o2.name as tgt_name, o2.agency as tgt_agency
        FROM opportunity_relationships r
        JOIN opportunities o1 ON r.source_opp_id = o1.id
        JOIN opportunities o2 ON r.target_opp_id = o2.id
        WHERE r.relationship_type = 'stackable'
        LIMIT 5
    """).fetchall():
        print(f"  [{r['confidence']:.2f}] {r['src_agency']} ('{r['src_name'][:30]}...') + {r['tgt_agency']} ('{r['tgt_name'][:30]}...')")
        print(f"       Rationale: {r['rationale']}")

    conn.close()

if __name__ == '__main__':
    check_freshness_and_details()
