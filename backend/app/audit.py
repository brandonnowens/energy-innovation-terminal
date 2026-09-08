"""Data quality auditing."""

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity, OpportunityRound
from app.models.source import DataQualityIssue, SourceConflict

logger = logging.getLogger(__name__)


def run_audit(db: Session) -> dict:
    """Run data quality audit and return summary."""
    issues_found = 0

    # Clear old unresolved issues
    db.query(DataQualityIssue).filter_by(resolved=False).delete()
    db.commit()

    now = datetime.now(timezone.utc)

    # 1. Check for opportunities apparently open past deadline
    open_opps = db.query(Opportunity).filter_by(status="open").all()
    for opp in open_opps:
        open_rounds = [r for r in opp.rounds if r.status == "Open"]
        all_past = True
        for r in open_rounds:
            if r.due_date and r.due_date.replace(tzinfo=None) > now.replace(tzinfo=None):
                all_past = False
                break
        if open_rounds and all_past:
            db.add(DataQualityIssue(
                issue_type="past_deadline_open",
                severity="warning",
                entity_type="opportunity",
                entity_id=opp.solicitation_number,
                description=f"{opp.solicitation_number} is marked open but all open round deadlines have passed.",
            ))
            issues_found += 1

    # 2. Check for impossible dates (due date before 2020 or after 2035)
    all_rounds = db.query(OpportunityRound).all()
    for r in all_rounds:
        if r.due_date:
            if r.due_date.year < 2020 or r.due_date.year > 2035:
                db.add(DataQualityIssue(
                    issue_type="impossible_date",
                    severity="warning",
                    entity_type="opportunity_round",
                    entity_id=str(r.id),
                    description=f"Round {r.round_number} has unlikely due date: {r.due_date}",
                ))
                issues_found += 1

    # 3. Check for duplicate opportunities
    from sqlalchemy import func as sqlfunc
    dupes = (
        db.query(Opportunity.solicitation_number, sqlfunc.count(Opportunity.id))
        .group_by(Opportunity.solicitation_number)
        .having(sqlfunc.count(Opportunity.id) > 1)
        .all()
    )
    for sol_num, count in dupes:
        db.add(DataQualityIssue(
            issue_type="duplicate",
            severity="critical",
            entity_type="opportunity",
            entity_id=sol_num,
            description=f"Duplicate opportunities found for {sol_num}: {count} records",
        ))
        issues_found += 1

    # 4. Check for opportunities missing description
    no_desc = db.query(Opportunity).filter(
        (Opportunity.short_description == None) | (Opportunity.short_description == "")
    ).all()
    for opp in no_desc:
        db.add(DataQualityIssue(
            issue_type="missing_source",
            severity="info",
            entity_type="opportunity",
            entity_id=opp.solicitation_number,
            description=f"{opp.solicitation_number} has no description.",
        ))
        issues_found += 1

    # 5. Count unresolved conflicts
    conflicts = db.query(SourceConflict).filter_by(resolved=False).count()
    if conflicts > 0:
        db.add(DataQualityIssue(
            issue_type="contradictory",
            severity="warning",
            entity_type="system",
            description=f"{conflicts} unresolved source conflicts detected.",
        ))
        issues_found += 1

    # 6. Check for stale records (not verified in 7+ days)
    from datetime import timedelta
    stale_threshold = now - timedelta(days=7)
    stale = db.query(Opportunity).filter(
        Opportunity.last_verified_at < stale_threshold,
        Opportunity.status == "open",
    ).count()
    if stale > 0:
        db.add(DataQualityIssue(
            issue_type="stale_record",
            severity="info",
            entity_type="opportunity",
            description=f"{stale} open opportunities not verified in the last 7 days.",
        ))
        issues_found += 1

    db.commit()

    # Generate summary
    all_issues = db.query(DataQualityIssue).filter_by(resolved=False).all()
    summary = {
        "total_issues": len(all_issues),
        "critical": sum(1 for i in all_issues if i.severity == "critical"),
        "warning": sum(1 for i in all_issues if i.severity == "warning"),
        "info": sum(1 for i in all_issues if i.severity == "info"),
        "issues": [
            {
                "type": i.issue_type,
                "severity": i.severity,
                "entity": f"{i.entity_type}:{i.entity_id}" if i.entity_id else i.entity_type,
                "description": i.description,
            }
            for i in all_issues
        ],
    }

    logger.info(
        f"Audit complete: {summary['critical']} critical, "
        f"{summary['warning']} warnings, {summary['info']} info"
    )

    return summary
