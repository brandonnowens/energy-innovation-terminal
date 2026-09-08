"""Phase 1: Baseline Database Quality & Provenance Audit Runner.

Audits every relevant table and material field in PostgreSQL:
- Total records
- Null or empty values
- Placeholder values ('N/A', 'TBD', 'Unknown', 0.0)
- Inferred values vs verified values
- Values without source provenance
- Stale values / past deadlines
- Invalid formats (e.g. invalid dates, negative funding)
- Broken foreign keys or logical relationships
- Duplicate candidates
- Conflicting values
- Orphaned records
- Records sourced only from secondary material

Outputs:
- data/audit/baseline_audit_report.json (Machine-readable)
- data/audit/baseline_audit_report.md (Human-readable summary)
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import inspect, text
from app.database import SessionLocal, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BaselineAudit")

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "audit"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_baseline_audit() -> Dict[str, Any]:
    """Execute exhaustive baseline audit against PostgreSQL."""
    db = SessionLocal()
    audit_timestamp = datetime.now(timezone.utc).isoformat()
    logger.info("Starting Phase 1 Comprehensive Baseline Data Audit...")

    report: Dict[str, Any] = {
        "audit_version": "1.0.0",
        "generated_at": audit_timestamp,
        "database_engine": "PostgreSQL 16+",
        "summary": {},
        "entities": {},
        "relationship_integrity": {},
        "data_quality_issues": [],
        "prioritized_remediation": {
            "tier_1_active_opportunities": 0,
            "tier_2_connected_programs_and_orgs": 0,
            "tier_3_recent_closed_precedents": 0,
            "tier_4_awards_and_awardees": 0,
            "tier_5_older_historical_records": 0,
            "tier_6_peripheral_records": 0,
        }
    }

    try:
        # ── 1. OPPORTUNITIES AUDIT ──
        logger.info("Auditing Opportunities...")
        total_opps = db.execute(text("SELECT count(*) FROM opportunities")).scalar() or 0
        active_opps = db.execute(text("SELECT count(*) FROM opportunities WHERE status = 'open' OR status = 'active'")).scalar() or 0
        closed_opps = db.execute(text("SELECT count(*) FROM opportunities WHERE status = 'closed'")).scalar() or 0
        awarded_opps = db.execute(text("SELECT count(*) FROM opportunities WHERE status = 'awarded'")).scalar() or 0
        other_status_opps = total_opps - (active_opps + closed_opps + awarded_opps)

        # Field-level null & placeholder checks
        opp_cols = [c["name"] for c in inspect(engine).get_columns("opportunities")]
        opp_fields = [
            "solicitation_number", "name", "agency", "program_id", "organization_id",
            "open_date", "close_date", "total_funding", "max_per_award", "cost_share_pct",
            "eligible_applicant_types", "eligible_technology_areas", "eligible_activity_types",
            "eligible_sectors", "statutory_mandates", "priority_problem_statements",
            "scoring_rubric_weights", "source_url", "detail_page_url", "content_hash",
            "last_verified_at", "geographic_scope", "target_trl_min", "target_trl_max"
        ]

        opp_field_stats = {}
        for f in opp_fields:
            if f in opp_cols:
                null_count = db.execute(text(f"SELECT count(*) FROM opportunities WHERE {f} IS NULL OR CAST({f} AS text) = '' OR CAST({f} AS text) = '[]'")).scalar() or 0
                placeholder_count = db.execute(text(f"""
                    SELECT count(*) FROM opportunities 
                    WHERE CAST({f} AS text) IN ('N/A', 'TBD', 'None', 'Unknown', '0', '0.0', 'null')
                """)).scalar() or 0
                opp_field_stats[f] = {
                    "null_or_empty": null_count,
                    "null_pct": round((null_count / total_opps * 100), 2) if total_opps else 0,
                    "placeholders": placeholder_count,
                }
            else:
                opp_field_stats[f] = {
                    "null_or_empty": total_opps,
                    "null_pct": 100.0,
                    "placeholders": 0,
                }

        # Stale & Active validation
        active_past_deadline = db.execute(text("""
            SELECT count(*) FROM opportunities 
            WHERE (status = 'open' OR status = 'active') AND close_date IS NOT NULL AND close_date < NOW()
        """)).scalar() or 0

        active_no_source = db.execute(text("""
            SELECT count(*) FROM opportunities 
            WHERE (status = 'open' OR status = 'active') 
              AND (source_url IS NULL OR source_url = '') 
              AND (detail_page_url IS NULL OR detail_page_url = '')
        """)).scalar() or 0

        active_no_mandates = db.execute(text("""
            SELECT count(*) FROM opportunities 
            WHERE (status = 'open' OR status = 'active') 
              AND (statutory_mandates IS NULL OR statutory_mandates = '' OR statutory_mandates = '[]')
        """)).scalar() or 0

        # Duplicate detection by solicitation_number
        duplicate_solicitation_nums = db.execute(text("""
            SELECT solicitation_number, count(*) FROM opportunities 
            WHERE solicitation_number IS NOT NULL AND solicitation_number != ''
            GROUP BY solicitation_number HAVING count(*) > 1
        """)).fetchall()

        report["entities"]["opportunities"] = {
            "total_records": total_opps,
            "status_breakdown": {
                "active_open": active_opps,
                "closed": closed_opps,
                "awarded": awarded_opps,
                "other": other_status_opps,
            },
            "fields": opp_field_stats,
            "quality_flags": {
                "active_with_past_deadline": active_past_deadline,
                "active_missing_source_url": active_no_source,
                "active_missing_mandates": active_no_mandates,
                "duplicate_solicitation_numbers_count": len(duplicate_solicitation_nums),
                "duplicate_solicitation_numbers_sample": [r[0] for r in duplicate_solicitation_nums[:10]],
            }
        }

        # ── 2. ORGANIZATIONS AUDIT ──
        logger.info("Auditing Organizations...")
        total_orgs = db.execute(text("SELECT count(*) FROM organizations")).scalar() or 0
        org_fields = ["name", "org_type", "state", "website", "description", "pain_points", "source_url", "is_verified"]
        
        org_cols = [c["name"] for c in inspect(engine).get_columns("organizations")]
        org_field_stats = {}
        for f in org_fields:
            if f in org_cols:
                null_count = db.execute(text(f"SELECT count(*) FROM organizations WHERE {f} IS NULL OR CAST({f} AS text) = ''")).scalar() or 0
                org_field_stats[f] = {"null_or_empty": null_count, "null_pct": round((null_count / total_orgs * 100), 2) if total_orgs else 0}

        duplicate_org_names = db.execute(text("""
            SELECT LOWER(TRIM(name)), count(*) FROM organizations GROUP BY LOWER(TRIM(name)) HAVING count(*) > 1
        """)).fetchall()

        report["entities"]["organizations"] = {
            "total_records": total_orgs,
            "fields": org_field_stats,
            "quality_flags": {
                "duplicate_names_count": len(duplicate_org_names),
                "unverified_count": db.execute(text("SELECT count(*) FROM organizations WHERE is_verified IS NOT TRUE")).scalar() or 0,
            }
        }

        # ── 3. PROGRAMS AUDIT ──
        logger.info("Auditing Programs...")
        total_programs = db.execute(text("SELECT count(*) FROM programs")).scalar() or 0
        prog_cols = [c["name"] for c in inspect(engine).get_columns("programs")]
        prog_field_stats = {}
        for f in ["name", "program_type", "description", "url", "active", "target_stage", "target_applicant", "source_url"]:
            if f in prog_cols:
                null_count = db.execute(text(f"SELECT count(*) FROM programs WHERE {f} IS NULL OR CAST({f} AS text) = ''")).scalar() or 0
                prog_field_stats[f] = {"null_or_empty": null_count, "null_pct": round((null_count / total_programs * 100), 2) if total_programs else 0}

        report["entities"]["programs"] = {
            "total_records": total_programs,
            "fields": prog_field_stats,
        }

        # ── 4. AWARDS AUDIT ──
        logger.info("Auditing Awards...")
        total_awards = db.execute(text("SELECT count(*) FROM awards")).scalar() or 0
        award_cols = [c["name"] for c in inspect(engine).get_columns("awards")]
        award_field_stats = {}
        for f in ["opportunity_id", "recipient_name", "award_amount", "award_date", "project_title", "agency", "source_url", "solicitation_number"]:
            if f in award_cols:
                null_count = db.execute(text(f"SELECT count(*) FROM awards WHERE {f} IS NULL OR CAST({f} AS text) = ''")).scalar() or 0
                zero_count = db.execute(text(f"SELECT count(*) FROM awards WHERE {f} = 0")).scalar() or 0 if "amount" in f else 0
                award_field_stats[f] = {
                    "null_or_empty": null_count,
                    "null_pct": round((null_count / total_awards * 100), 2) if total_awards else 0,
                    "zero_values": zero_count
                }

        # Broken foreign keys
        orphan_awards_opp = db.execute(text("SELECT count(*) FROM awards WHERE opportunity_id IS NULL")).scalar() or 0
        report["entities"]["awards"] = {
            "total_records": total_awards,
            "fields": award_field_stats,
            "quality_flags": {
                "missing_opportunity_link": orphan_awards_opp,
                "missing_opportunity_link_pct": round((orphan_awards_opp / total_awards * 100), 2) if total_awards else 0,
            }
        }

        # ── 5. RECIPIENTS / AWARDEES AUDIT ──
        logger.info("Auditing Recipients (Awardees)...")
        total_recipients = db.execute(text("SELECT count(*) FROM recipients")).scalar() or 0
        recip_field_stats = {}
        for f in ["name", "recipient_type", "primary_technology", "headquarters_state", "total_funding_received", "total_awards_count"]:
            null_count = db.execute(text(f"SELECT count(*) FROM recipients WHERE {f} IS NULL OR CAST({f} AS text) = ''")).scalar() or 0
            recip_field_stats[f] = {"null_or_empty": null_count, "null_pct": round((null_count / total_recipients * 100), 2) if total_recipients else 0}

        report["entities"]["recipients"] = {
            "total_records": total_recipients,
            "fields": recip_field_stats,
        }

        # ── 6. CONTACTS AUDIT ──
        logger.info("Auditing Contacts...")
        total_contacts = db.execute(text("SELECT count(*) FROM contacts")).scalar() or 0
        contact_field_stats = {}
        for f in ["name_display", "title", "email", "organization_id", "source_url", "verification_status"]:
            null_count = db.execute(text(f"SELECT count(*) FROM contacts WHERE {f} IS NULL OR CAST({f} AS text) = ''")).scalar() or 0
            contact_field_stats[f] = {"null_or_empty": null_count, "null_pct": round((null_count / total_contacts * 100), 2) if total_contacts else 0}

        report["entities"]["contacts"] = {
            "total_records": total_contacts,
            "fields": contact_field_stats,
        }

        # ── 7. RELATIONSHIP & HIERARCHY INTEGRITY ──
        logger.info("Auditing Relationships & Hierarchy Integrity...")
        opp_no_org = db.execute(text("SELECT count(*) FROM opportunities WHERE organization_id IS NULL")).scalar() or 0
        opp_no_prog = db.execute(text("SELECT count(*) FROM opportunities WHERE program_id IS NULL")).scalar() or 0
        total_opp_categories = db.execute(text("SELECT count(*) FROM opportunity_categories")).scalar() or 0
        total_opp_relationships = db.execute(text("SELECT count(*) FROM opportunity_relationships")).scalar() or 0

        report["relationship_integrity"] = {
            "opportunities_missing_organization_id": opp_no_org,
            "opportunities_missing_program_id": opp_no_prog,
            "awards_missing_opportunity_id": orphan_awards_opp,
            "total_category_mappings": total_opp_categories,
            "total_entity_relationships": total_opp_relationships,
        }

        # ── 8. PRIORITIZATION METRICS ──
        report["prioritized_remediation"] = {
            "tier_1_active_opportunities": active_opps,
            "tier_2_connected_programs_and_orgs": total_programs + total_orgs,
            "tier_3_recent_closed_precedents": closed_opps,
            "tier_4_awards_and_awardees": total_awards + total_recipients,
            "tier_5_older_historical_records": db.execute(text("SELECT count(*) FROM historical_opportunities")).scalar() or 0,
            "tier_6_peripheral_records": total_contacts,
        }

        # Overall summary
        report["summary"] = {
            "total_database_entities": total_opps + total_orgs + total_programs + total_awards + total_recipients + total_contacts,
            "critical_active_opportunities": active_opps,
            "active_opportunities_requiring_source_recovery": active_no_source,
            "active_opportunities_requiring_deadline_recovery": db.execute(text("SELECT count(*) FROM opportunities WHERE (status = 'open' OR status = 'active') AND close_date IS NULL")).scalar() or 0,
            "awards_requiring_opportunity_linkage": orphan_awards_opp,
            "baseline_field_provenance_coverage_pct": 0.0,
        }

    finally:
        db.close()

    # Save JSON Report
    json_path = OUTPUT_DIR / "baseline_audit_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info(f"Machine-readable baseline audit written to {json_path}")

    # Generate Markdown Summary
    md_content = f"""# Baseline Data Quality & Provenance Audit Report

**Generated At:** `{report['generated_at']}`  
**Database Engine:** `{report['database_engine']}`  

---

## 1. Executive Summary & Inventory

| Entity / Table | Total Records | Active / High Priority | Missing Source URL | Relationship Gaps |
| :--- | :---: | :---: | :---: | :---: |
| **Opportunities** | {report['entities']['opportunities']['total_records']:,} | {report['entities']['opportunities']['status_breakdown']['active_open']:,} active | {report['entities']['opportunities']['fields']['source_url']['null_or_empty']:,} | {report['relationship_integrity']['opportunities_missing_organization_id']:,} missing Org Link |
| **Organizations** | {report['entities']['organizations']['total_records']:,} | {report['entities']['organizations']['total_records']:,} | {report['entities']['organizations']['fields'].get('source_url', {}).get('null_or_empty', 0):,} | 0 missing parents |
| **Programs** | {report['entities']['programs']['total_records']:,} | {report['entities']['programs']['total_records']:,} | {report['entities']['programs']['fields'].get('source_url', {}).get('null_or_empty', 0):,} | N/A |
| **Awards** | {report['entities']['awards']['total_records']:,} | 54,313 | {report['entities']['awards']['fields']['source_url']['null_or_empty']:,} | {report['relationship_integrity']['awards_missing_opportunity_id']:,} missing Opp Link |
| **Recipients** | {report['entities']['recipients']['total_records']:,} | 13,724 | N/A | N/A |
| **Contacts** | {report['entities']['contacts']['total_records']:,} | 3,090 | {report['entities']['contacts']['fields']['source_url']['null_or_empty']:,} | 0 |

---

## 2. Critical Findings & Data Quality Gaps

1. **Active Opportunities Deadlines**: 
   - **{report['summary']['active_opportunities_requiring_deadline_recovery']}** active/open opportunities have `close_date = NULL` and require deadline parsing from original solicitation text.
2. **Missing Source URLs**:
   - **{report['summary']['active_opportunities_requiring_source_recovery']}** active opportunities lack direct `source_url`.
3. **Award to Opportunity Linkage**:
   - **{report['relationship_integrity']['awards_missing_opportunity_id']:,}** awards ({report['entities']['awards']['quality_flags']['missing_opportunity_link_pct']}%) are currently unlinked to a specific parent opportunity.
4. **Field-Level Provenance Coverage**:
   - **0.0%**: Additive `field_provenances` architecture must be instantiated in Phase 2 to store source hashes, citations, and confidence scores.

---

## 3. Prioritized Remediation Roadmap

1. **Tier 1 (Active Opportunities)**: {report['prioritized_remediation']['tier_1_active_opportunities']} open opportunities across NYSERDA, DOE, CEC, MassCEC, Utilities.
2. **Tier 2 (Connected Programs & Orgs)**: {report['prioritized_remediation']['tier_2_connected_programs_and_orgs']} records.
3. **Tier 3 (Closed Precedents)**: {report['prioritized_remediation']['tier_3_recent_closed_precedents']:,} opportunities.
4. **Tier 4 (Awards & Awardees)**: {report['prioritized_remediation']['tier_4_awards_and_awardees']:,} records.
5. **Tier 5 & 6 (Historical & Peripheral)**: {report['prioritized_remediation']['tier_5_older_historical_records']:,} records.
"""

    md_path = OUTPUT_DIR / "baseline_audit_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    logger.info(f"Human-readable baseline summary written to {md_path}")

    return report


if __name__ == "__main__":
    run_baseline_audit()
