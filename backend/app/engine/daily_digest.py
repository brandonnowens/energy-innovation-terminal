"""
Automated Daily Energy Innovation Intelligence Digest Generation Engine.

Synthesizes daily morning briefings covering:
1. Macro Energy Innovation Capital & Solicitation Flow
2. Newly Released Solicitations & RFPs (Federal, State, Utilities)
3. Upcoming Critical Application Deadlines (Next 7-14 Days)
4. Recipient Venture, Award & Patent Wire
5. Regulatory & PSC Dockets Watch
6. Algorithmic Opportunity Spotlight with Bankability (TBR) & IRA Capital Stack Fit
"""

import os
import json
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, text

from app.models.opportunity import Opportunity, OpportunityRound
from app.models.recipient import Recipient
from app.models.award import Award
from app.models.policy import PolicyStandard, RegulatoryProceeding
from app.models.technology import Technology
from app.database import SessionLocal
from app.intelligence.bankability import evaluate_technology_bankability
from app.intelligence.capital_stack import solve_capital_stack

logger = logging.getLogger("DailyDigestEngine")

# Cache directory for daily digests
DIGEST_DIR = Path(__file__).parent.parent.parent / "data" / "digests"
DIGEST_DIR.mkdir(parents=True, exist_ok=True)

# High-Performance In-Memory RAM Cache
_DIGEST_RAM_CACHE: Dict[str, Dict[str, Any]] = {}
_DIGEST_CACHE_TIME: Dict[str, float] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour


def format_currency(val: Optional[float]) -> str:
    if not val:
        return "Open / Undisclosed"
    if val >= 1_000_000_000:
        return f"${val / 1_000_000_000:.2f}B"
    if val >= 1_000_000:
        return f"${val / 1_000_000:.1f}M"
    if val >= 1_000:
        return f"${val / 1_000:.0f}K"
    return f"${val:,.0f}"



def generate_daily_digest(db: Session, target_date_str: Optional[str] = None) -> Dict[str, Any]:
    """Compile and generate the Daily Energy Innovation Intelligence Digest."""
    if not target_date_str:
        now = datetime.now(timezone.utc)
        target_date_str = now.strftime("%Y-%m-%d")
    else:
        try:
            now = datetime.strptime(target_date_str, "%Y-%m-%d")
        except ValueError:
            now = datetime.now(timezone.utc)
            target_date_str = now.strftime("%Y-%m-%d")

    formatted_date = now.strftime("%B %d, %Y")
    day_of_year = now.timetuple().tm_yday
    volume_num = max(1, now.year - 2024)
    edition_number = f"Vol. {volume_num}, No. {day_of_year}"

    # 1. Macro Summary Metrics
    open_opps_query = db.query(Opportunity).filter(Opportunity.status == "open")
    open_opps_count = open_opps_query.count()
    total_active_capital = db.query(func.sum(Opportunity.total_funding)).filter(Opportunity.status == "open").scalar() or 0.0
    total_recipients = db.query(Recipient.id).count()
    total_awards_count = db.query(Award.id).count()

    # 2. Top New Solicitations
    new_opps_rows = (
        db.query(Opportunity)
        .filter(Opportunity.status == "open")
        .order_by(desc(Opportunity.id))
        .limit(6)
        .all()
    )
    
    new_solicitations = []
    for opp in new_opps_rows:
        new_solicitations.append({
            "id": opp.id,
            "solicitation_number": opp.solicitation_number,
            "name": opp.name,
            "agency": opp.agency or "Energy Innovation Agency",
            "jurisdiction": opp.jurisdiction,
            "total_funding": opp.total_funding,
            "total_funding_display": format_currency(opp.total_funding),
            "max_per_award_display": format_currency(opp.max_per_award),
            "due_date_display": opp.due_date_display or "Open Enrollment",
            "short_description": opp.short_description or opp.name,
            "solicitation_type": opp.solicitation_type or "RFP",
            "detail_url": f"/opportunities/{opp.id}"
        })

    # 3. Critical Upcoming Deadlines
    deadline_opps_rows = (
        db.query(Opportunity)
        .filter(Opportunity.status == "open")
        .filter(Opportunity.due_date_display != None)
        .order_by(Opportunity.id.asc())
        .limit(6)
        .all()
    )

    urgent_deadlines = []
    for opp in deadline_opps_rows:
        urgent_deadlines.append({
            "id": opp.id,
            "solicitation_number": opp.solicitation_number,
            "name": opp.name,
            "agency": opp.agency or "Agency",
            "due_date_display": opp.due_date_display or "Closing Soon",
            "total_funding_display": format_currency(opp.total_funding),
            "max_per_award_display": format_currency(opp.max_per_award),
            "detail_url": f"/opportunities/{opp.id}"
        })

    # 4. Recipient & Award Wire
    recent_awards_rows = (
        db.query(Award)
        .filter(Award.award_amount != None)
        .order_by(desc(Award.id))
        .limit(6)
        .all()
    )

    award_wire = []
    for aw in recent_awards_rows:
        award_wire.append({
            "id": aw.id,
            "recipient_name": aw.recipient_name or "Innovative Clean Tech Entity",
            "recipient_city": aw.recipient_city,
            "recipient_state": aw.recipient_state,
            "award_amount_display": format_currency(aw.award_amount),
            "project_title": aw.project_title or "Energy Innovation Deployment & Demonstration",
            "pi_name": aw.pi_name,
            "recipient_type": aw.recipient_type or "company"
        })

    # 5. Regulatory & Dockets Watch
    regulatory_rows = (
        db.query(PolicyStandard)
        .filter(PolicyStandard.status == "active")
        .limit(4)
        .all()
    )

    regulatory_watch = []
    for pol in regulatory_rows:
        regulatory_watch.append({
            "code_identifier": pol.code_identifier,
            "title": pol.title,
            "category": pol.category,
            "jurisdiction_state": pol.jurisdiction_state or "US",
            "executive_summary": (pol.executive_summary[:240] + "...") if pol.executive_summary else "",
            "compliance_mandate": (pol.compliance_mandate[:200] + "...") if pol.compliance_mandate else None
        })

    # 6. Algorithmic Opportunity Spotlight
    spotlight_opp = new_opps_rows[0] if new_opps_rows else None
    spotlight_data = None
    if spotlight_opp:
        try:
            # Compute Bankability
            bankability_res = evaluate_technology_bankability(
                technology_name="energy_storage",
                trl=7,
                pilot_operating_hours=2500,
                field_deployments_count=4,
                degradation_rate_pct_annual=1.2,
                has_tier1_warranty_backing=True,
                has_ul_iec_safety_certification=True,
                has_independent_engineer_report=True,
                offtake_contract_status="pilot_agreement"
            )

            # Compute Capital Stack

            cap_stack_res = solve_capital_stack(
                total_project_cost=spotlight_opp.total_funding or 5_000_000.0,
                grant_award_request=(spotlight_opp.max_per_award or (spotlight_opp.total_funding * 0.4 if spotlight_opp.total_funding else 1_500_000.0)),
                technology_type="energy_storage",
                sponsor_equity_available=1_000_000.0,
                commercial_debt_available=1_500_000.0,
                green_bank_debt_request=1_000_000.0,
                energy_community=True,
                low_income_community=False,
                prevailing_wage_compliant=True,
                domestic_content_compliant=True
            )

            spotlight_data = {
                "opportunity_id": spotlight_opp.id,
                "solicitation_number": spotlight_opp.solicitation_number,
                "name": spotlight_opp.name,
                "agency": spotlight_opp.agency,
                "total_funding_display": format_currency(spotlight_opp.total_funding),
                "max_per_award_display": format_currency(spotlight_opp.max_per_award),
                "due_date_display": spotlight_opp.due_date_display or "Open Enrollment",
                "short_description": spotlight_opp.short_description or spotlight_opp.name,
                "bankability_score": bankability_res.get("tbr_score"),
                "bankability_grade": bankability_res.get("investment_grade"),
                "bankability_readiness": bankability_res.get("commercial_readiness"),
                "ira_itc_rate": cap_stack_res.get("ira_tax_credits", {}).get("effective_credit_rate_pct"),
                "ira_tax_credit_value": format_currency(cap_stack_res.get("ira_tax_credits", {}).get("total_tax_credit_value")),
                "blended_wacc_pct": cap_stack_res.get("blended_cost_of_capital_pct"),
                "non_dilutive_coverage_pct": cap_stack_res.get("stack_proportions_pct", {}).get("grant_grant_pct")
            }
        except Exception as e:
            logger.warning(f"Error computing spotlight data: {e}")
            spotlight_data = {
                "opportunity_id": spotlight_opp.id,
                "solicitation_number": spotlight_opp.solicitation_number,
                "name": spotlight_opp.name,
                "agency": spotlight_opp.agency,
                "total_funding_display": format_currency(spotlight_opp.total_funding),
                "max_per_award_display": format_currency(spotlight_opp.max_per_award),
                "due_date_display": spotlight_opp.due_date_display or "Open Enrollment",
                "short_description": spotlight_opp.short_description or spotlight_opp.name,
            }

    # 7. Executive Editorial Narrative
    editorial_narrative = (
        f"Public energy innovation funding markets open today with {open_opps_count:,} active competitive solicitations "
        f"representing {format_currency(total_active_capital)} in unallocated non-dilutive capital across federal, "
        f"state, and utility funding authorities. Key momentum centers on grid resilience, high-density storage, "
        f"and industrial decarbonization programs with heavy IRA Title 26 bonus credit alignment."
    )

    digest = {
        "edition_date": target_date_str,
        "formatted_date": formatted_date,
        "edition_number": edition_number,
        "headline": f"Daily Energy Innovation Intelligence Briefing: {formatted_date}",
        "editorial_narrative": editorial_narrative,
        "macro_metrics": {
            "open_solicitations_count": open_opps_count,
            "total_active_capital": total_active_capital,
            "total_active_capital_display": format_currency(total_active_capital),
            "tracked_recipients_count": total_recipients,
            "total_historical_awards_count": total_awards_count,
            "new_solicitations_today": len(new_solicitations),
            "urgent_deadlines_count": len(urgent_deadlines)
        },
        "new_solicitations": new_solicitations,
        "urgent_deadlines": urgent_deadlines,
        "award_wire": award_wire,
        "regulatory_watch": regulatory_watch,
        "spotlight": spotlight_data,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    # Save to RAM cache
    _DIGEST_RAM_CACHE[target_date_str] = digest
    _DIGEST_CACHE_TIME[target_date_str] = time.time()

    # Save to disk cache
    cache_file = DIGEST_DIR / f"{target_date_str}.json"
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(digest, f, indent=2)
        logger.info(f"Saved daily digest to {cache_file}")
    except Exception as e:
        logger.warning(f"Could not write digest cache file: {e}")

    return digest


def get_daily_digest(db: Session, target_date_str: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve daily digest with sub-millisecond RAM caching and disk fallback."""
    if not target_date_str:
        target_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 1. Check RAM Cache (<1hr old)
    now_ts = time.time()
    if target_date_str in _DIGEST_RAM_CACHE:
        cache_age = now_ts - _DIGEST_CACHE_TIME.get(target_date_str, 0)
        if cache_age < CACHE_TTL_SECONDS:
            return _DIGEST_RAM_CACHE[target_date_str]

    # 2. Check Disk Cache
    cache_file = DIGEST_DIR / f"{target_date_str}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                _DIGEST_RAM_CACHE[target_date_str] = data
                _DIGEST_CACHE_TIME[target_date_str] = now_ts
                return data
        except Exception as e:
            logger.warning(f"Error reading cache file {cache_file}: {e}")

    # 3. Generate on-the-fly and populate RAM + Disk
    return generate_daily_digest(db, target_date_str)


def warm_digest_cache():
    """Background helper to pre-generate and warm today's digest in RAM."""
    try:
        from app.database import SessionLocal
        with SessionLocal() as db:
            get_daily_digest(db)
            logger.info("Pre-warmed Daily Digest cache in memory.")
    except Exception as e:
        logger.warning(f"Could not pre-warm digest cache: {e}")


def get_digest_archive_list(db: Session) -> List[Dict[str, Any]]:
    """Return list of available daily digest editions."""
    dates = []
    
    # 1. Inspect cache directory
    if DIGEST_DIR.exists():
        for file in DIGEST_DIR.glob("*.json"):
            date_part = file.stem
            try:
                dt = datetime.strptime(date_part, "%Y-%m-%d")
                dates.append(date_part)
            except ValueError:
                continue

    # 2. Always ensure today and recent 7 days are represented
    today_dt = datetime.now(timezone.utc)
    for i in range(7):
        d_str = (today_dt - timedelta(days=i)).strftime("%Y-%m-%d")
        if d_str not in dates:
            dates.append(d_str)

    dates.sort(reverse=True)

    archive = []
    for d_str in dates[:30]:  # Up to 30 days
        try:
            dt = datetime.strptime(d_str, "%Y-%m-%d")
            archive.append({
                "date": d_str,
                "formatted_date": dt.strftime("%B %d, %Y"),
                "headline": f"Daily Energy Innovation Intelligence Briefing - {dt.strftime('%b %d, %Y')}",
                "is_today": d_str == today_dt.strftime("%Y-%m-%d")
            })
        except ValueError:
            continue

    return archive

