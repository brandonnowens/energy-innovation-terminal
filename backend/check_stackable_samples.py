import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine


def test_stackable():
    conn = engine.connect()
    cur = conn

    print("=== SAMPLE STACKABLE RELATIONSHIPS ===")
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
        print(f"• [{r['confidence']:.2f}] {r['src_agency']} ('{r['src_name'][:35]}...') + {r['tgt_agency']} ('{r['tgt_name'][:35]}...')")
        print(f"  Rationale: {r['rationale']}\n")

    print("=== SAMPLE OPPORTUNITY RESTRICTIONS ===")
    for r in cur.execute("""
        SELECT o.name, o.agency, res.category, res.title, res.description, res.severity
        FROM opportunity_restrictions res
        JOIN opportunities o ON res.opportunity_id = o.id
        LIMIT 5
    """).fetchall():
        print(f"• [{r['category'].upper()}] ({r['agency']}: {r['name'][:30]}...)")
        print(f"  Title: {r['title']}")
        print(f"  Rule: {r['description']}")
        print(f"  Severity: {r['severity']}\n")

    conn.close()

if __name__ == '__main__':
    test_stackable()
