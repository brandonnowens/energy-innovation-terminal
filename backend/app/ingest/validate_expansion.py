"""Comprehensive QA Validation & Coverage Audit for Nationwide Utility Expansion."""

import os
import sys
import json
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app.database import engine
from app.ingest.state_utility_registry import STATE_GDP_RANKING, STATE_UTILITY_DATA


def run_qa_audit():
    print("=" * 80)
    print("      NATIONWIDE ENERGY-INNOVATION UTILITY EXPANSION QA AUDIT")
    print("=" * 80)

    with engine.begin() as conn:
        # 1. Total Metrics
        org_count = conn.execute(text("SELECT COUNT(*) FROM organizations")).scalar() or 0
        holding_count = conn.execute(text("SELECT COUNT(*) FROM organizations WHERE org_type = 'holding_company'")).scalar() or 0
        utility_count = conn.execute(text("SELECT COUNT(*) FROM organizations WHERE org_type = 'utility'")).scalar() or 0
        prog_count = conn.execute(text("SELECT COUNT(*) FROM programs")).scalar() or 0
        opp_count = conn.execute(text("SELECT COUNT(*) FROM opportunities")).scalar() or 0
        awd_count = conn.execute(text("SELECT COUNT(*) FROM awards")).scalar() or 0
        rec_count = conn.execute(text("SELECT COUNT(*) FROM recipients")).scalar() or 0
        cat_count = conn.execute(text("SELECT COUNT(*) FROM opportunity_categories")).scalar() or 0
        opp_org_count = conn.execute(text("SELECT COUNT(*) FROM opportunity_organizations")).scalar() or 0

        print("\n--- MASTER DATABASE TOTALS ---")
        print(f"  Organizations:            {org_count:,} (Holdings: {holding_count}, Utilities: {utility_count})")
        print(f"  Programs:                 {prog_count:,}")
        print(f"  Opportunities:            {opp_count:,}")
        print(f"  Awards:                   {awd_count:,}")
        print(f"  Awardees / Recipients:    {rec_count:,}")
        print(f"  Taxonomy Categories:      {cat_count:,}")
        print(f"  Opportunity-Org Links:    {opp_org_count:,}")

        # 2. Relational Hierarchy Integrity Checks
        print("\n--- RELATIONAL INTEGRITY CHECKS ---")

        # Check 1: Orphan Opportunities (no valid program_id)
        orphan_opps = conn.execute(text("SELECT COUNT(*) FROM opportunities WHERE program_id IS NULL OR program_id NOT IN (SELECT id FROM programs)")).scalar() or 0
        print(f"  [CHECK 1] Orphan Opportunities (missing program): {orphan_opps} {'[PASS]' if orphan_opps == 0 else '[FAIL]'}")

        # Check 2: Orphan Awards (no valid opportunity_id when assigned)
        orphan_awds = conn.execute(text("SELECT COUNT(*) FROM awards WHERE opportunity_id IS NOT NULL AND opportunity_id NOT IN (SELECT id FROM opportunities)")).scalar() or 0
        print(f"  [CHECK 2] Broken Award -> Opportunity links:      {orphan_awds} {'[PASS]' if orphan_awds == 0 else '[FAIL]'}")

        # Check 3: Orphan Programs (no opportunities)
        orphan_progs = conn.execute(text("SELECT COUNT(*) FROM programs WHERE id NOT IN (SELECT DISTINCT program_id FROM opportunities WHERE program_id IS NOT NULL)")).scalar() or 0
        print(f"  [CHECK 3] Orphan Programs (no opportunities):     {orphan_progs} {'[PASS]' if orphan_progs == 0 else '[FAIL]'}")

        # Check 4: Unlinked Opportunities in OpportunityOrganizations
        unlinked_opp_orgs = conn.execute(text("SELECT COUNT(*) FROM opportunities WHERE id NOT IN (SELECT DISTINCT opportunity_id FROM opportunity_organizations)")).scalar() or 0
        print(f"  [CHECK 4] Opportunities without Org sponsor link:  {unlinked_opp_orgs} (historical non-utility opps default to agency string)")

        # Check 5: Geocoding Coverage for Nationwide Awards
        geocoded_awds = conn.execute(text("SELECT COUNT(*) FROM awards WHERE latitude IS NOT NULL AND longitude IS NOT NULL")).scalar() or 0
        print(f"  [CHECK 5] Total Geocoded Awards:                  {geocoded_awds:,} / {awd_count:,} ({geocoded_awds*100//max(awd_count,1)}%)")

        # 3. State-by-State Coverage Table
        print("\n--- 51-JURISDICTION COVERAGE AUDIT (Sorted by GDP Rank) ---")
        print(f"{'Rank':<5} | {'State':<5} | {'Name':<22} | {'GDP ($B)':<9} | {'Utilities':<10} | {'Opps':<6} | {'Awards':<7} | {'Status'}")
        print("-" * 80)

        states_covered = 0
        total_expansion_opps = 0
        total_expansion_awds = 0

        for item in STATE_GDP_RANKING:
            code = item["state_code"]
            name = item["state_name"]
            rank = item["rank"]
            gdp = item["gdp_billions"]

            # Count in DB
            u_count = conn.execute(text("SELECT COUNT(*) FROM organizations WHERE state = :code AND org_type = 'utility'"), {"code": code}).scalar() or 0
            o_count = conn.execute(
                text("SELECT COUNT(*) FROM opportunities WHERE jurisdiction = :c1 OR jurisdiction = :c2 OR jurisdiction = :c3"),
                {"c1": code, "c2": f"state_{code.lower()}", "c3": f"utility_{code.lower()}"}
            ).scalar() or 0
            a_count = conn.execute(text("SELECT COUNT(*) FROM awards WHERE recipient_state = :code"), {"code": code}).scalar() or 0

            total_expansion_opps += o_count
            total_expansion_awds += a_count

            has_data = u_count > 0 or o_count > 0 or a_count > 0
            if has_data:
                states_covered += 1
                status = "COMPLETE"
            else:
                status = "PENDING"

            print(f"{rank:<5} | {code:<5} | {name:<22} | ${gdp:<8} | {u_count:<10} | {o_count:<6} | {a_count:<7} | {status}")

        print("-" * 80)
        print(f"Total Jurisdictions Covered: {states_covered}/51 ({states_covered*100//51}%)")
        print("=" * 80)

        return states_covered == 51


if __name__ == "__main__":
    run_qa_audit()

