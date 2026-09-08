import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent if 'app' not in str(Path(__file__).parent) else Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from app.database import engine

import json

def deep_data_composition():
    conn = engine.connect()
    cur = conn

    print("=== SOURCE BREAKDOWN IN AWARDS ===")
    for r in cur.execute("""
        SELECT COALESCE(source_name, 'UNKNOWN') as src, COUNT(*) as cnt,
               MIN(year) as min_yr, MAX(year) as max_yr,
               SUM(COALESCE(award_amount, 0)) as total_usd
        FROM awards
        GROUP BY src
        ORDER BY cnt DESC
    """).fetchall():
        print(f"  {r['src']:<30}: {r['cnt']:>6,d} awards | {r['min_yr']}-{r['max_yr']} | ${r['total_usd']:>16,.2f}")

    print("\n=== SOURCE BREAKDOWN IN OPPORTUNITIES ===")
    for r in cur.execute("""
        SELECT COALESCE(source_name, 'UNKNOWN') as src, COUNT(*) as cnt,
               MIN(year) as min_yr, MAX(year) as max_yr
        FROM opportunities
        GROUP BY src
        ORDER BY cnt DESC
    """).fetchall():
        print(f"  {r['src']:<30}: {r['cnt']:>6,d} opps | {r['min_yr']}-{r['max_yr']}")

    print("\n=== TOP 20 RECIPIENTS BY TOTAL FUNDING ===")
    for r in cur.execute("""
        SELECT name, recipient_type, headquarters_state, total_awards_count, total_funding_received,
               total_nyserda_funding, total_federal_funding, funded_agencies
        FROM recipients
        ORDER BY total_funding_received DESC
        LIMIT 20
    """).fetchall():
        print(f"  {r['name'][:35]:<35} | {r['recipient_type']:<15} | {r['headquarters_state']} | {r['total_awards_count']:>4,d} awards | ${r['total_funding_received']:>15,.2f} | Agencies: {r['funded_agencies']}")

    print("\n=== TOP 10 RECIPIENTS BY NUMBER OF AWARDS ===")
    for r in cur.execute("""
        SELECT name, recipient_type, headquarters_state, total_awards_count, total_funding_received
        FROM recipients
        ORDER BY total_awards_count DESC
        LIMIT 10
    """).fetchall():
        print(f"  {r['name'][:35]:<35} | {r['recipient_type']:<15} | {r['headquarters_state']} | {r['total_awards_count']:>4,d} awards | ${r['total_funding_received']:>15,.2f}")

    print("\n=== RECIPIENT PATENTS SAMPLE ===")
    for r in cur.execute(text("SELECT id, recipient_id, patent_number, title FROM recipient_patents LIMIT 5")).fetchall():
        print(f"  Patent {r['patent_number']}: {r['title']}")

    print("\n=== RECIPIENT INVESTMENTS SAMPLE ===")
    for r in cur.execute(text("SELECT id, recipient_id, round_type, amount_usd, valuation_usd, round_date FROM recipient_investments LIMIT 5")).fetchall():
        print(f"  Round: {r['round_type']} | ${r['amount_usd']:,.0f} | Date: {r['round_date']}")

    print("\n=== DATA QUALITY ISSUES LOGGED IN DB ===")
    issues = cur.execute(text("SELECT issue_type, severity, entity_type, COUNT(*) FROM data_quality_issues GROUP BY issue_type, severity, entity_type")).fetchall()
    for r in issues:
        print(f"  {r[0]} ({r[1]} on {r[2]}): {r[3]}")

    print("\n=== FOREIGN KEY INTEGRITY CHECK ===")
    # Check awards linked to opportunities
    orphan_awards = cur.execute("""
        SELECT COUNT(*) FROM awards a 
        LEFT JOIN opportunities o ON a.opportunity_id = o.id 
        WHERE a.opportunity_id IS NOT NULL AND o.id IS NULL
    """).fetchone()[0]
    print(f"  Orphan awards (invalid opportunity_id): {orphan_awards}")

    # Check opportunity_organizations
    orphan_opp_orgs = cur.execute("""
        SELECT COUNT(*) FROM opportunity_organizations oo
        LEFT JOIN opportunities o ON oo.opportunity_id = o.id
        WHERE o.id IS NULL
    """).fetchone()[0]
    print(f"  Orphan opportunity_organizations (missing opp): {orphan_opp_orgs}")

    orphan_org_links = cur.execute("""
        SELECT COUNT(*) FROM opportunity_organizations oo
        LEFT JOIN organizations org ON oo.organization_id = org.id
        WHERE org.id IS NULL
    """).fetchone()[0]
    print(f"  Orphan opportunity_organizations (missing org): {orphan_org_links}")

    # Check relationships
    orphan_rels_src = cur.execute("""
        SELECT COUNT(*) FROM opportunity_relationships r
        LEFT JOIN opportunities o ON r.source_opp_id = o.id
        WHERE o.id IS NULL
    """).fetchone()[0]
    orphan_rels_tgt = cur.execute("""
        SELECT COUNT(*) FROM opportunity_relationships r
        LEFT JOIN opportunities o ON r.target_opp_id = o.id
        WHERE o.id IS NULL
    """).fetchone()[0]
    print(f"  Orphan relationships (missing source/target opp): src={orphan_rels_src}, tgt={orphan_rels_tgt}")

    conn.close()

if __name__ == '__main__':
    deep_data_composition()
