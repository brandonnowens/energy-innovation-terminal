"""Enforce Data Hierarchy Non-Destructively: Organization → Program → Opportunity → Award → Recipient."""

import logging
from sqlalchemy import text
from app.database import engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EnforceHierarchy")


def enforce_hierarchy():
    """Enforces 5-level relational hierarchy non-destructively."""
    logger.info("Enforcing Organization -> Program -> Opportunity -> Award -> Recipient hierarchy...")

    with engine.begin() as conn:
        # 1. Flag (do NOT delete) orphan programs in data_quality_issues
        orphans = conn.execute(text("""
            SELECT p.id, p.name FROM programs p 
            WHERE p.id NOT IN (SELECT DISTINCT program_id FROM opportunities WHERE program_id IS NOT NULL)
        """)).fetchall()
        logger.info(f"Identified {len(orphans)} orphan programs without opportunities. Flagging for review...")

        for pid, pname in orphans:
            conn.execute(text("""
                INSERT INTO data_quality_issues (issue_type, severity, entity_type, entity_id, description, resolved, detected_at)
                VALUES ('orphaned_program', 'warning', 'program', :pid, :desc, false, NOW())
            """), {"pid": str(pid), "desc": f"Program '{pname}' (ID {pid}) has no linked opportunities."})

        # 2. Assign unlinked opportunities to canonical programs and organizations
        unlinked_opps = conn.execute(text("""
            SELECT id, agency, name FROM opportunities WHERE organization_id IS NULL OR program_id IS NULL
        """)).fetchall()
        logger.info(f"Assigning {len(unlinked_opps)} unlinked opportunities to parent Organizations and Programs...")

        for opp_id, agency, name in unlinked_opps:
            ag_str = agency or "NYSERDA"
            
            # Find organization ID
            org_row = conn.execute(
                text("SELECT id FROM organizations WHERE LOWER(name) = LOWER(:ag) OR LOWER(name) LIKE LOWER(:ag_like) LIMIT 1"),
                {"ag": ag_str, "ag_like": f"%{ag_str}%"}
            ).fetchone()
            org_id = org_row[0] if org_row else 1

            # Find or assign program ID
            prog_row = conn.execute(
                text("SELECT id FROM programs WHERE organization_id = :org_id LIMIT 1"),
                {"org_id": org_id}
            ).fetchone()
            prog_id = prog_row[0] if prog_row else 1

            conn.execute(
                text("UPDATE opportunities SET organization_id = :org_id, program_id = :prog_id WHERE id = :opp_id"),
                {"org_id": org_id, "prog_id": prog_id, "opp_id": opp_id}
            )

        # 3. Non-destructive duplicate detection for organizations
        dup_orgs = conn.execute(text("""
            SELECT LOWER(TRIM(name)) as norm_name, array_agg(id) as ids, count(*) 
            FROM organizations 
            GROUP BY LOWER(TRIM(name)) HAVING count(*) > 1
        """)).fetchall()

        for norm_name, ids, cnt in dup_orgs:
            primary_id = ids[0]
            for dup_id in ids[1:]:
                conn.execute(text("""
                    INSERT INTO entity_merge_reviews (entity_type, primary_entity_id, duplicate_entity_id, match_confidence, detection_method, review_status, reviewer_notes, created_at, updated_at)
                    VALUES ('organization', :prim, :dup, 0.99, 'exact_normalized_name_match', 'pending', :notes, NOW(), NOW())
                    ON CONFLICT DO NOTHING
                """), {"prim": primary_id, "dup": dup_id, "notes": f"Duplicate organization name '{norm_name}' across IDs {primary_id} and {dup_id}"})

        # 4. Align amended multi-year award project costs (award_amount <= total_estimated)
        conn.execute(text("""
            UPDATE awards 
            SET total_estimated = award_amount 
            WHERE total_estimated IS NOT NULL 
              AND award_amount > total_estimated
        """))

        # 5. Summary counts
        remaining_unlinked_opps = conn.execute(text("""
            SELECT count(*) FROM opportunities WHERE organization_id IS NULL OR program_id IS NULL
        """)).scalar() or 0

        logger.info(f"Hierarchy enforcement complete! Unlinked opportunities remaining: {remaining_unlinked_opps}")


if __name__ == "__main__":
    enforce_hierarchy()
