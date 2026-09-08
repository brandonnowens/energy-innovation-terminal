import sys
from pathlib import Path
import json

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.database import engine
from sqlalchemy import text

def analyze_data_gaps():
    with engine.connect() as conn:
        print("=== 1. ACTIVE / OPEN OPPORTUNITIES GAP AUDIT ===")
        open_by_agency = conn.execute(text("""
            SELECT COALESCE(agency, 'UNKNOWN') as ag,
                   COUNT(*) as total_open,
                   SUM(CASE WHEN total_funding > 0 THEN 1 ELSE 0 END) as with_funding,
                   SUM(CASE WHEN total_funding = 0 OR total_funding IS NULL THEN 1 ELSE 0 END) as zero_funding,
                   SUM(CASE WHEN close_date IS NOT NULL THEN 1 ELSE 0 END) as with_close_date,
                   SUM(CASE WHEN short_description IS NOT NULL AND LENGTH(TRIM(short_description)) > 50 THEN 1 ELSE 0 END) as with_desc
            FROM opportunities
            WHERE status ILIKE 'open%' OR status = 'active'
            GROUP BY ag
            ORDER BY total_open DESC
        """)).mappings().all()
        for r in open_by_agency:
            print(f"  - {r['ag']}: {r['total_open']} open (With Funding: {r['with_funding']}, Zero/Null Funding: {r['zero_funding']}, With Close Date: {r['with_close_date']})")

        print("\n=== 2. STATE-BY-STATE OPPORTUNITY COVERAGE ===")
        opp_by_state = conn.execute(text("""
            SELECT COALESCE(jurisdiction, 'UNKNOWN') as jur, COUNT(*) as cnt,
                   SUM(CASE WHEN status ILIKE 'open%' THEN 1 ELSE 0 END) as open_cnt
            FROM opportunities
            GROUP BY jur
            ORDER BY cnt DESC LIMIT 25
        """)).mappings().all()
        for r in opp_by_state:
            print(f"  - State/Jurisdiction {r['jur']}: {r['cnt']} total ({r['open_cnt']} open)")

        print("\n=== 3. STATE-BY-STATE AWARDS COVERAGE ===")
        awards_by_state = conn.execute(text("""
            SELECT COALESCE(recipient_state, 'UNKNOWN') as st, COUNT(*) as cnt,
                   SUM(COALESCE(award_amount, 0)) as total_dollars
            FROM awards
            GROUP BY st
            ORDER BY cnt DESC LIMIT 20
        """)).mappings().all()
        for r in awards_by_state:
            print(f"  - State {r['st']}: {r['cnt']} awards, ${r['total_dollars']:,.2f}")

        print("\n=== 4. VC & PATENT LINKAGE DENSITY GAPS ===")
        tot_recips = conn.execute(text("SELECT COUNT(*) FROM recipients")).scalar()
        vc_recips = conn.execute(text("SELECT COUNT(DISTINCT recipient_id) FROM recipient_investments")).scalar()
        pat_recips = conn.execute(text("SELECT COUNT(DISTINCT recipient_id) FROM recipient_patents")).scalar()
        contacts_cnt = conn.execute(text("SELECT COUNT(*) FROM contacts")).scalar()
        contacts_with_email = conn.execute(text("SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL AND TRIM(email) != ''")).scalar()
        print(f"Total Recipients: {tot_recips}")
        print(f"Recipients with VC Rounds: {vc_recips} ({vc_recips/tot_recips*100:.2f}% coverage)")
        print(f"Recipients with USPTO Patents: {pat_recips} ({pat_recips/tot_recips*100:.2f}% coverage)")
        print(f"Total Contacts: {contacts_cnt} (with email: {contacts_with_email})")

        print("\n=== 5. SPECIALIZED INFRASTRUCTURE LAYERS GAPS ===")
        iq_cnt = conn.execute(text("SELECT iso_rto, COUNT(*) FROM interconnection_queue_projects GROUP BY iso_rto")).fetchall()
        print("Interconnection Queues by ISO/RTO:")
        for r in iq_cnt:
            print(f"  - {r[0]}: {r[1]} projects")

        der_cnt = conn.execute(text("SELECT state, COUNT(*) FROM der_market_deployments GROUP BY state")).fetchall()
        print("\nDER Deployments by State:")
        for r in der_cnt:
            print(f"  - {r[0]}: {r[1]} deployments")

        scaleup_cnt = conn.execute(text("SELECT program_category, COUNT(*) FROM federal_scaleup_allocations GROUP BY program_category")).fetchall()
        print("\nFederal Scaleup Allocations:")
        for r in scaleup_cnt:
            print(f"  - {r[0]}: {r[1]} allocations")

if __name__ == "__main__":
    analyze_data_gaps()
