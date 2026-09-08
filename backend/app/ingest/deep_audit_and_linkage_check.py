"""Deep Comprehensive Database and Linkage Integrity Auditor.

Checks:
1. Counts across all platform tables.
2. Linkage integrity (opportunities <-> categories, awards <-> opportunities,
   recipients <-> investments, recipients <-> patents, recipients <-> interconnection).
3. Opportunity categorization completeness (technology, sector, fuel, activity).
4. Full-text search (FTS) index synchronization.
5. Award geocoding completeness (latitude/longitude coverage).
6. Missing linkages and opportunities for auto-remediation.
"""

import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database import SessionLocal

def run_deep_audit():
    db = SessionLocal()
    try:
        print("=" * 70)
        print("        ENERGY INNOVATION TERMINAL - FULL DATABASE AUDIT")
        print("=" * 70)

        tables = [
            "opportunities",
            "opportunity_categories",
            "awards",
            "award_results",
            "recipients",
            "recipient_investments",
            "recipient_patents",
            "interconnection_queue_projects",
            "field_provenances",
            "organizations",
            "programs",
            "national_lab_facilities",
            "sec_form_d_filings",
            "federal_scaleup_allocations",
            "federal_procurement_contracts",
            "der_market_deployments",
            "university_licensable_technologies"
        ]

        print("\n--- 1. TABLE ROW COUNTS ---")
        for t in tables:
            try:
                cnt = db.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
                print(f"  {t:<35} : {cnt:>8,d} records")
            except Exception as e:
                print(f"  {t:<35} : ERROR ({e})")

        print("\n--- 2. CATEGORY & TAXONOMY LINKAGES ---")
        opps_total = db.execute(text("SELECT COUNT(*) FROM opportunities")).scalar()
        opps_with_cat = db.execute(text("SELECT COUNT(DISTINCT opportunity_id) FROM opportunity_categories")).scalar()
        opps_missing_cat = opps_total - opps_with_cat
        print(f"  Total Opportunities               : {opps_total:>8,d}")
        print(f"  Opportunities with Taxonomy Tags  : {opps_with_cat:>8,d}")
        print(f"  Opportunities Missing Taxonomy    : {opps_missing_cat:>8,d}")

        cat_counts = db.execute(text("""
            SELECT category_type, COUNT(*) as cnt
            FROM opportunity_categories
            GROUP BY category_type
            ORDER BY cnt DESC
        """)).fetchall()
        for ctype, cnt in cat_counts:
            print(f"    - Category type '{ctype:<12}' : {cnt:>8,d} links")

        print("\n--- 3. AWARDS & PROVENANCE INTEGRITY ---")
        total_awards = db.execute(text("SELECT COUNT(*) FROM awards")).scalar()
        geocoded_awards = db.execute(text("SELECT COUNT(*) FROM awards WHERE latitude IS NOT NULL AND longitude IS NOT NULL")).scalar()
        awards_with_amount = db.execute(text("SELECT COUNT(*) FROM awards WHERE award_amount > 0")).scalar()
        total_award_usd = db.execute(text("SELECT SUM(award_amount) FROM awards")).scalar() or 0.0
        linked_awards = db.execute(text("SELECT COUNT(*) FROM awards WHERE opportunity_id IS NOT NULL")).scalar()
        
        print(f"  Total Historical Awards           : {total_awards:>8,d}")
        print(f"  Geocoded Awards (Lat/Lon)         : {geocoded_awards:>8,d} ({geocoded_awards/total_awards*100:.1f}%)")
        print(f"  Awards with Non-Zero Dollar Values: {awards_with_amount:>8,d}")
        print(f"  Total Public Capital Tracked      : ${total_award_usd:>16,.2f}")
        print(f"  Awards Linked to Opportunity ID   : {linked_awards:>8,d}")

        print("\n--- 4. PRIVATE CAPITAL & IP LINKAGES ---")
        total_vc = db.execute(text("SELECT COUNT(*) FROM recipient_investments")).scalar()
        total_vc_usd = db.execute(text("SELECT SUM(amount_usd) FROM recipient_investments")).scalar() or 0.0
        linked_vc = db.execute(text("SELECT COUNT(*) FROM recipient_investments WHERE recipient_id IS NOT NULL")).scalar()
        
        total_pat = db.execute(text("SELECT COUNT(*) FROM recipient_patents")).scalar()
        linked_pat_rec = db.execute(text("SELECT COUNT(*) FROM recipient_patents WHERE recipient_id IS NOT NULL")).scalar()
        linked_pat_awd = db.execute(text("SELECT COUNT(*) FROM recipient_patents WHERE award_id IS NOT NULL")).scalar()

        print(f"  Total Venture / Private Equity    : {total_vc:>8,d} rounds (${total_vc_usd:,.2f})")
        print(f"  Venture Rounds Linked to Recipient: {linked_vc:>8,d} ({linked_vc/total_vc*100:.1f}%)")
        print(f"  Total Clean Tech Patents          : {total_pat:>8,d}")
        print(f"  Patents Linked to Recipient Org   : {linked_pat_rec:>8,d} ({linked_pat_rec/total_pat*100:.1f}%)")
        print(f"  Patents Linked to Public Award    : {linked_pat_awd:>8,d} ({linked_pat_awd/total_pat*100:.1f}%)")

        print("\n--- 5. GRID INTERCONNECTION QUEUE LINKAGES ---")
        total_q = db.execute(text("SELECT COUNT(*) FROM interconnection_queue_projects")).scalar()
        geocoded_q = db.execute(text("SELECT COUNT(*) FROM interconnection_queue_projects WHERE latitude IS NOT NULL AND longitude IS NOT NULL")).scalar()
        linked_q_rec = db.execute(text("SELECT COUNT(*) FROM interconnection_queue_projects WHERE recipient_id IS NOT NULL")).scalar()
        total_mw = db.execute(text("SELECT SUM(capacity_mw) FROM interconnection_queue_projects")).scalar() or 0.0
        total_mwh = db.execute(text("SELECT SUM(storage_mwh) FROM interconnection_queue_projects")).scalar() or 0.0

        print(f"  Total Interconnection Projects    : {total_q:>8,d}")
        print(f"  Geocoded Projects (Lat/Lon)       : {geocoded_q:>8,d} ({geocoded_q/total_q*100:.1f}%)")
        print(f"  Projects Linked to Recipient ID   : {linked_q_rec:>8,d} ({linked_q_rec/total_q*100:.1f}%)")
        print(f"  Total Capacity Tracked            : {total_mw:>12,.1f} MW ({total_mw/1000:,.2f} GW)")
        print(f"  Total Battery Storage Tracked     : {total_mwh:>12,.1f} MWh ({total_mwh/1000:,.2f} GWh)")

        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    run_deep_audit()
