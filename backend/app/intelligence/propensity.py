"""
Canonical Organization Say-Yes Propensity & Funder Ranking Module.

Ranks funding organizations, utilities, and foundations most likely to commit capital or partner
based on geographic jurisdiction, service territory alignment, statutory mandates, active solicitations,
and verified program officer access.
"""

import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.engine.profile import ProjectProfile
from app.engine.propensity_engine import (
    rank_top_25_say_yes_matrix,
    get_high_propensity_selected_organizations,
    ORGANIZATION_PAIN_POINTS,
)

logger = logging.getLogger("CanonicalPropensity")


def rank_funder_propensity(
    db: Session,
    profile: ProjectProfile,
    limit: int = 25
) -> List[Dict[str, Any]]:
    """
    Ranks organizations and decision-makers by Say-Yes propensity score (0-100).
    """
    try:
        return rank_top_25_say_yes_matrix(db, profile, limit=limit)
    except Exception as e:
        logger.error(f"Error ranking funder propensity: {e}")
        return []


def get_aligned_organization_codes(
    db: Session,
    profile: ProjectProfile,
    min_score: float = 70.0
) -> List[str]:
    """
    Returns list of organization codes meeting the minimum propensity threshold.
    """
    try:
        return get_high_propensity_selected_organizations(db, profile, min_score=min_score)
    except Exception as e:
        logger.error(f"Error getting aligned organization codes: {e}")
        return []


def get_organization_pain_points_catalog() -> Dict[str, Any]:
    """Returns the curated organization pain points and strategic pitch theses catalog."""
    return ORGANIZATION_PAIN_POINTS
