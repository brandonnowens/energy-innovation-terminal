"""Backfill missing year fields on opportunities.

Infers the year from open_date, close_date, solicitation number patterns,
or first_seen timestamp as a last resort.
"""

import re
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)


def _extract_year_from_sol_num(sol_num: str) -> int | None:
    """Try to extract a 4-digit year from a solicitation number."""
    if not sol_num:
        return None
    # Common patterns: DE-FOA-0003200, RFP-2025-001, NYSERDA-123-2024
    matches = re.findall(r'20[12]\d', sol_num)
    if matches:
        year = int(matches[-1])  # Take the last match (most likely the year)
        if 2015 <= year <= 2030:
            return year
    return None


def backfill_years(db: Session) -> dict:
    """Backfill missing year fields on all opportunities.

    Returns stats dict with counts of records updated by each method.
    """
    stats = {
        "total_missing": 0,
        "from_open_date": 0,
        "from_close_date": 0,
        "from_sol_num": 0,
        "from_first_seen": 0,
        "still_missing": 0,
    }

    opps = db.query(Opportunity).filter(Opportunity.year.is_(None)).all()
    stats["total_missing"] = len(opps)

    for opp in opps:
        year = None

        # Method 1: From open_date
        if opp.open_date:
            try:
                if isinstance(opp.open_date, datetime):
                    year = opp.open_date.year
                elif isinstance(opp.open_date, str):
                    dt = datetime.fromisoformat(opp.open_date.replace("Z", "+00:00"))
                    year = dt.year
            except (ValueError, AttributeError):
                pass

        if year and 2015 <= year <= 2030:
            opp.year = year
            stats["from_open_date"] += 1
            continue

        # Method 2: From close_date
        if opp.close_date:
            try:
                if isinstance(opp.close_date, datetime):
                    year = opp.close_date.year
                elif isinstance(opp.close_date, str):
                    dt = datetime.fromisoformat(opp.close_date.replace("Z", "+00:00"))
                    year = dt.year
            except (ValueError, AttributeError):
                pass

        if year and 2015 <= year <= 2030:
            opp.year = year
            stats["from_close_date"] += 1
            continue

        # Method 3: From solicitation number pattern
        year = _extract_year_from_sol_num(opp.solicitation_number)
        if year:
            opp.year = year
            stats["from_sol_num"] += 1
            continue

        # Method 4: From first_seen_at timestamp
        if opp.first_seen_at:
            try:
                if isinstance(opp.first_seen_at, datetime):
                    year = opp.first_seen_at.year
                elif isinstance(opp.first_seen_at, str):
                    dt = datetime.fromisoformat(opp.first_seen_at.replace("Z", "+00:00"))
                    year = dt.year
            except (ValueError, AttributeError):
                pass

        if year and 2015 <= year <= 2030:
            opp.year = year
            stats["from_first_seen"] += 1
            continue

        stats["still_missing"] += 1

    db.commit()
    return stats
