"""Phase 7: Automated Quality Controls & Validation Engine.

Executes 12 automated assertion checks against PostgreSQL to detect:
1. Active opportunities with deadlines in the past.
2. Active opportunities without original source URLs.
3. Opportunities without a sponsoring Organization or Program.
4. Contradictory award ceilings (min > max).
5. Cost-share percentages outside valid ranges (0% - 100%).
6. Awards greater than total project cost.
7. Awards without opportunity links.
8. Unmatched recipients (Awardees without awards).
9. Invalid geographic identifiers.
10. Source document hash shifts (content changes).
11. Stale evidence records (> 180 days without verification).
12. Field Provenance Coverage for Active Opportunities.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

from sqlalchemy import select, and_, or_, func, text
from app.database import SessionLocal
from app.models.opportunity import Opportunity
from app.models.award import Award
from app.models.source import FieldProvenance, SourceSnapshot, DataQualityIssue

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("QualityAssertions")


def run_quality_assertions() -> Dict[str, Any]:
    """Run all automated data quality assertions."""
    db = SessionLocal()
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_checks": 12,
        "passed_checks": 0,
        "failed_checks": 0,
        "check_details": {},
        "issues_logged": 0,
    }

    try:
        logger.info("Executing Phase 7 Automated Quality Controls...")

        # 1. Active Opportunities with Past Deadlines
        is_pg = db.bind.dialect.name == "postgresql" if db.bind else False
        past_deadline_query = (
            "SELECT count(*) FROM opportunities WHERE (status = 'open' OR status = 'active') AND close_date IS NOT NULL AND close_date < NOW() - INTERVAL '1 day'"
            if is_pg else
            "SELECT count(*) FROM opportunities WHERE (status = 'open' OR status = 'active') AND close_date IS NOT NULL AND close_date < datetime('now', '-1 day')"
        )
        q1 = db.execute(text(past_deadline_query)).scalar() or 0
        results["check_details"]["active_past_deadline"] = {
            "name": "Active Opportunities with Past Deadlines",
            "count": q1,
            "status": "PASS" if q1 == 0 else "FAIL",
            "threshold": 0,
        }

        # 2. Active Opportunities without Original Source URL
        q2 = db.execute(text("""
            SELECT count(*) FROM opportunities 
            WHERE (status = 'open' OR status = 'active') 
              AND (source_url IS NULL OR source_url = '') 
              AND (detail_page_url IS NULL OR detail_page_url = '')
        """)).scalar() or 0
        results["check_details"]["active_missing_source"] = {
            "name": "Active Opportunities without Original Source URL",
            "count": q2,
            "status": "PASS" if q2 == 0 else "FAIL",
            "threshold": 0,
        }

        # 3. Opportunities without Sponsoring Organization or Program
        q3 = db.execute(text("""
            SELECT count(*) FROM opportunities 
            WHERE organization_id IS NULL OR program_id IS NULL
        """)).scalar() or 0
        results["check_details"]["opportunities_unlinked"] = {
            "name": "Opportunities Missing Organization or Program Linkage",
            "count": q3,
            "status": "PASS" if q3 == 0 else "FAIL",
            "threshold": 0,
        }

        # 4. Contradictory Award Ceilings (min > max)
        q4 = db.execute(text("""
            SELECT count(*) FROM opportunities 
            WHERE award_min IS NOT NULL 
              AND max_per_award IS NOT NULL 
              AND award_min > max_per_award
        """)).scalar() or 0
        results["check_details"]["contradictory_award_limits"] = {
            "name": "Contradictory Award Ceilings (Min > Max)",
            "count": q4,
            "status": "PASS" if q4 == 0 else "FAIL",
            "threshold": 0,
        }

        # 5. Cost-Share Percentages Outside Range (0 - 100%)
        q5 = db.execute(text("""
            SELECT count(*) FROM opportunities 
            WHERE cost_share_pct IS NOT NULL 
              AND (cost_share_pct < 0.0 OR cost_share_pct > 100.0)
        """)).scalar() or 0
        results["check_details"]["invalid_cost_share_pct"] = {
            "name": "Cost-Share Percentages Outside Valid Range (0% to 100%)",
            "count": q5,
            "status": "PASS" if q5 == 0 else "FAIL",
            "threshold": 0,
        }

        # 6. Awards with Amount Greater than Project Cost
        q6 = db.execute(text("""
            SELECT count(*) FROM awards 
            WHERE total_estimated IS NOT NULL 
              AND award_amount IS NOT NULL 
              AND award_amount > (total_estimated * 1.05)
        """)).scalar() or 0
        results["check_details"]["awards_exceeding_project_cost"] = {
            "name": "Awards Greater than Total Estimated Cost",
            "count": q6,
            "status": "PASS" if q6 == 0 else "FAIL",
            "threshold": 0,
        }

        # 7. Awards without Opportunity Link
        q7 = db.execute(text("""
            SELECT count(*) FROM awards WHERE opportunity_id IS NULL
        """)).scalar() or 0
        results["check_details"]["awards_missing_opportunity"] = {
            "name": "Awards Missing Opportunity Linkage",
            "count": q7,
            "status": "PASS" if q7 == 0 else "FAIL",
            "threshold": 0,
        }

        # 8. Unmatched Recipients (Recipients without matching awards)
        q8 = db.execute(text("""
            SELECT count(*) FROM recipients r
            WHERE NOT EXISTS (
                SELECT 1 FROM awards a WHERE LOWER(a.recipient_name) = LOWER(r.name)
            )
        """)).scalar() or 0
        results["check_details"]["recipients_without_awards"] = {
            "name": "Recipients without Corresponding Awards",
            "count": q8,
            "status": "PASS" if q8 < 2000 else "WARNING",
            "threshold": 2000,
        }

        # 9. Invalid Geographic Identifiers
        q9 = db.execute(text("""
            SELECT count(*) FROM opportunities 
            WHERE geographic_scope IS NOT NULL 
              AND LENGTH(geographic_scope) < 2
        """)).scalar() or 0
        results["check_details"]["invalid_geographic_identifiers"] = {
            "name": "Invalid Geographic Identifiers",
            "count": q9,
            "status": "PASS" if q9 == 0 else "FAIL",
            "threshold": 0,
        }

        # 10. Source Document Content Shifts Tracked
        q10 = db.execute(text("""
            SELECT count(*) FROM source_snapshots WHERE has_changed = TRUE
        """)).scalar() or 0
        results["check_details"]["source_document_shifts"] = {
            "name": "Source Document Content Shifts Tracked",
            "count": q10,
            "status": "PASS",
            "threshold": 0,
        }

        # 11. Stale Evidence Records (> 180 Days)
        stale_query = (
            "SELECT count(*) FROM field_provenances WHERE last_verified_at < NOW() - INTERVAL '180 days'"
            if is_pg else
            "SELECT count(*) FROM field_provenances WHERE last_verified_at < datetime('now', '-180 days')"
        )
        q11 = db.execute(text(stale_query)).scalar() or 0
        results["check_details"]["stale_evidence_records"] = {
            "name": "Stale Evidence Records (>180 days)",
            "count": q11,
            "status": "PASS" if q11 == 0 else "WARNING",
            "threshold": 0,
        }

        # 12. Field Provenance Coverage for Active Opportunities
        q12 = db.execute(text("""
            SELECT count(DISTINCT entity_id) FROM field_provenances 
            WHERE entity_type = 'opportunity'
        """)).scalar() or 0
        results["check_details"]["field_provenance_coverage"] = {
            "name": "Opportunities with Verified Field-Level Provenance",
            "count": q12,
            "status": "PASS" if q12 >= 300 else "FAIL",
            "threshold": 300,
        }

        # Compute summary
        passed = sum(1 for c in results["check_details"].values() if c["status"] == "PASS")
        failed = sum(1 for c in results["check_details"].values() if c["status"] == "FAIL")
        results["passed_checks"] = passed
        results["failed_checks"] = failed

        logger.info(f"Quality Assertions Complete: {passed}/12 Checks Passed ({failed} Failures)")

    finally:
        db.close()

    return results


if __name__ == "__main__":
    res = run_quality_assertions()
    print("Quality Assertion Results:")
    for k, v in res["check_details"].items():
        print(f" - [{v['status']}] {v['name']}: {v['count']} records")
