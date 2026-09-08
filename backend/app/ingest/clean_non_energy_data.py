"""
Database-wide Non-Energy Cleansing and Cascade Purging Engine.

Performs a comprehensive, transaction-safe purge of all non-energy records
(reproductive health, medical devices, clinical trials, oncology, pharmaceuticals,
pure astrophysics, and non-energy defense ordnance) across opportunities, awards,
taxonomies, recipients, and reports.
"""

import sys
import time
import logging
from pathlib import Path
from sqlalchemy import text
from typing import Dict, Any, List, Set

backend_dir = Path(__file__).parent.parent.parent.resolve()
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal, engine
from app.engine.energy_filter import is_energy_innovation_relevant

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DatabaseCleaner")


def purge_non_energy_data() -> Dict[str, Any]:
    """Execute complete database cleansing and cascade purging."""
    session = SessionLocal()
    stats = {
        "started_at": time.time(),
        "total_opportunities_scanned": 0,
        "purged_opportunities": 0,
        "total_awards_scanned": 0,
        "purged_awards": 0,
        "deleted_opportunity_categories": 0,
        "deleted_opportunity_restrictions": 0,
        "deleted_opportunity_rounds": 0,
        "deleted_opportunity_contacts": 0,
        "deleted_opportunity_documents": 0,
        "deleted_opportunity_organizations": 0,
        "deleted_opportunity_relationships": 0,
        "deleted_policy_links": 0,
        "deleted_benchmarks": 0,
        "deleted_award_results": 0,
        "deleted_opportunity_results": 0,
        "deleted_success_stories": 0,
        "purged_orphaned_recipients": 0,
    }

    try:
        logger.info("======================================================================")
        logger.info("STARTING DATABASE-WIDE ENERGY INNOVATION RE-EVALUATION & PURGE")
        logger.info("======================================================================")

        # ---------------------------------------------------------------------
        # 1. EVALUATE AND IDENTIFY NON-ENERGY OPPORTUNITIES
        # ---------------------------------------------------------------------
        logger.info("\n>>> STEP 1: Scanning Opportunities for non-energy records...")
        opp_rows = session.execute(text("""
            SELECT id, solicitation_number, name, short_description, agency, keywords, objectives
            FROM opportunities
        """)).fetchall()

        stats["total_opportunities_scanned"] = len(opp_rows)
        invalid_opp_ids: List[int] = []
        invalid_sol_nums: List[str] = []

        for row in opp_rows:
            opp_id, sol_num, name, short_desc, agency, kw, obj = row
            text_context = f"{short_desc or ''} {obj or ''}"
            is_valid, reason = is_energy_innovation_relevant(
                title=name,
                text_content=text_context,
                agency=agency,
                keywords=kw
            )
            if not is_valid:
                invalid_opp_ids.append(opp_id)
                if sol_num:
                    invalid_sol_nums.append(sol_num)

        stats["purged_opportunities"] = len(invalid_opp_ids)
        logger.info(f"    Found {len(invalid_opp_ids)} non-energy opportunities out of {len(opp_rows)} total.")

        # ---------------------------------------------------------------------
        # 2. EVALUATE AND IDENTIFY NON-ENERGY AWARDS
        # ---------------------------------------------------------------------
        logger.info("\n>>> STEP 2: Scanning Awards for non-energy records...")
        awd_rows = session.execute(text("""
            SELECT id, external_award_id, project_title, project_abstract, agency
            FROM awards
        """)).fetchall()

        stats["total_awards_scanned"] = len(awd_rows)
        invalid_awd_ids: List[int] = []

        for row in awd_rows:
            awd_id, ext_id, title, abst, agency = row
            is_valid, reason = is_energy_innovation_relevant(
                title=title,
                text_content=abst,
                agency=agency
            )
            if not is_valid:
                invalid_awd_ids.append(awd_id)

        stats["purged_awards"] = len(invalid_awd_ids)
        logger.info(f"    Found {len(invalid_awd_ids)} non-energy awards out of {len(awd_rows)} total.")

        # ---------------------------------------------------------------------
        # 3. CASCADE PURGE NON-ENERGY OPPORTUNITY RECORDS
        # ---------------------------------------------------------------------
        logger.info("\n>>> STEP 3: Purging non-energy opportunities and cascade tables...")
        chunk_size = 500

        if invalid_opp_ids:
            for i in range(0, len(invalid_opp_ids), chunk_size):
                chunk = invalid_opp_ids[i:i + chunk_size]
                chunk_str = ",".join(str(cid) for cid in chunk)

                # Opportunity categories
                res = session.execute(text(f"DELETE FROM opportunity_categories WHERE opportunity_id IN ({chunk_str})"))
                stats["deleted_opportunity_categories"] += res.rowcount or 0

                # Restrictions
                res = session.execute(text(f"DELETE FROM opportunity_restrictions WHERE opportunity_id IN ({chunk_str})"))
                stats["deleted_opportunity_restrictions"] += res.rowcount or 0

                # Rounds
                res = session.execute(text(f"DELETE FROM opportunity_rounds WHERE opportunity_id IN ({chunk_str})"))
                stats["deleted_opportunity_rounds"] += res.rowcount or 0

                # Documents
                res = session.execute(text(f"DELETE FROM opportunity_documents WHERE opportunity_id IN ({chunk_str})"))
                stats["deleted_opportunity_documents"] += res.rowcount or 0

                # Contacts & Links
                res = session.execute(text(f"DELETE FROM opportunity_contact_links WHERE opportunity_id IN ({chunk_str})"))
                stats["deleted_opportunity_contacts"] += res.rowcount or 0

                # Organizations linkages
                res = session.execute(text(f"DELETE FROM opportunity_organizations WHERE opportunity_id IN ({chunk_str})"))
                stats["deleted_opportunity_organizations"] += res.rowcount or 0

                # Relationships
                res = session.execute(text(f"DELETE FROM opportunity_relationships WHERE source_opp_id IN ({chunk_str}) OR target_opp_id IN ({chunk_str})"))
                stats["deleted_opportunity_relationships"] += res.rowcount or 0

                # Analysis matches
                session.execute(text(f"DELETE FROM analysis_matches WHERE opportunity_id IN ({chunk_str})"))

                # Policy links
                res = session.execute(text(f"DELETE FROM policy_opportunity_links WHERE opportunity_id IN ({chunk_str})"))
                stats["deleted_policy_links"] += res.rowcount or 0

                # Benchmarks
                res = session.execute(text(f"DELETE FROM result_benchmarks WHERE opportunity_id IN ({chunk_str})"))
                stats["deleted_benchmarks"] += res.rowcount or 0

                # Opportunity results & success stories linked to opp
                session.execute(text(f"DELETE FROM opportunity_results WHERE opportunity_id IN ({chunk_str})"))
                session.execute(text(f"DELETE FROM success_stories WHERE opportunity_id IN ({chunk_str})"))

                # Eligibility rules
                session.execute(text(f"DELETE FROM eligibility_rules WHERE opportunity_id IN ({chunk_str})"))

                # Finally delete opportunities
                session.execute(text(f"DELETE FROM opportunities WHERE id IN ({chunk_str})"))

            logger.info("    Opportunities cascade purge completed.")

        if invalid_sol_nums:
            for i in range(0, len(invalid_sol_nums), chunk_size):
                chunk = invalid_sol_nums[i:i + chunk_size]
                chunk_escaped = ",".join(f"'{s.replace("'", "''")}'" for s in chunk)
                session.execute(text(f"DELETE FROM historical_opportunities WHERE solicitation_number IN ({chunk_escaped})"))

        # ---------------------------------------------------------------------
        # 4. CASCADE PURGE NON-ENERGY AWARD RECORDS
        # ---------------------------------------------------------------------
        logger.info("\n>>> STEP 4: Purging non-energy awards and outcome tables...")
        if invalid_awd_ids:
            for i in range(0, len(invalid_awd_ids), chunk_size):
                chunk = invalid_awd_ids[i:i + chunk_size]
                chunk_str = ",".join(str(cid) for cid in chunk)

                # Award results
                res = session.execute(text(f"DELETE FROM award_results WHERE award_id IN ({chunk_str})"))
                stats["deleted_award_results"] += res.rowcount or 0

                # Opportunity results
                res = session.execute(text(f"DELETE FROM opportunity_results WHERE award_id IN ({chunk_str})"))
                stats["deleted_opportunity_results"] += res.rowcount or 0

                # Success stories
                res = session.execute(text(f"DELETE FROM success_stories WHERE award_id IN ({chunk_str})"))
                stats["deleted_success_stories"] += res.rowcount or 0

                # Delete awards
                session.execute(text(f"DELETE FROM awards WHERE id IN ({chunk_str})"))

            logger.info("    Awards cascade purge completed.")

        # ---------------------------------------------------------------------
        # 5. CLEAN ORPHANED RECIPIENTS (WITH 0 CLEAN ENERGY AWARDS)
        # ---------------------------------------------------------------------
        logger.info("\n>>> STEP 5: Purging orphaned recipients...")
        orphaned_recipients = session.execute(text("""
            SELECT r.id FROM recipients r
            LEFT JOIN awards a ON LOWER(r.name) = LOWER(a.recipient_name)
            LEFT JOIN proposals p ON LOWER(r.name) = LOWER(p.recipient_name)
            WHERE a.id IS NULL AND p.id IS NULL
        """)).fetchall()

        if orphaned_recipients:
            orph_ids = [r[0] for r in orphaned_recipients]
            for i in range(0, len(orph_ids), chunk_size):
                chunk = orph_ids[i:i + chunk_size]
                chunk_str = ",".join(str(cid) for cid in chunk)
                session.execute(text(f"DELETE FROM recipient_patents WHERE recipient_id IN ({chunk_str})"))
                session.execute(text(f"DELETE FROM recipient_investments WHERE recipient_id IN ({chunk_str})"))
                session.execute(text(f"DELETE FROM recipients WHERE id IN ({chunk_str})"))

            stats["purged_orphaned_recipients"] = len(orph_ids)
            logger.info(f"    Purged {len(orph_ids)} orphaned non-energy recipients.")

        session.commit()
        logger.info("    Committed all cleansing transactions to database.")

    except Exception as e:
        session.rollback()
        logger.error(f"Error during database cleansing: {e}", exc_info=True)
        raise
    finally:
        session.close()

    duration = round(time.time() - stats["started_at"], 2)
    stats["duration_sec"] = duration

    logger.info("======================================================================")
    logger.info(f"DATABASE CLEANSING COMPLETE IN {duration}s")
    logger.info(f"Clean Opportunities Remaining: {stats['total_opportunities_scanned'] - stats['purged_opportunities']}")
    logger.info(f"Clean Awards Remaining: {stats['total_awards_scanned'] - stats['purged_awards']}")
    logger.info("======================================================================")

    return stats

if __name__ == "__main__":
    purge_non_energy_data()
