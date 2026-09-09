"""
Canonical Solicitation Forecasting & Pre-Positioning Radar Module.

Forecasts upcoming unreleased, recurring, and anticipated multi-agency solicitations
across all organizations in the database by modeling historical release cadences,
statutory appropriations, and programmatic lifecycles.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.engine.profile import ProjectProfile
from app.engine.forecasting_radar import (
    get_predictive_solicitation_forecasts,
    match_project_against_forecasts,
    synthesize_llm_projection_briefing,
    get_forecasting_organization_directory,
    PROBABILISTIC_DISCLAIMER,
)

logger = logging.getLogger("CanonicalForecasting")


def forecast_upcoming_solicitations(
    db: Session,
    org_name: Optional[str] = None,
    agency: Optional[str] = None,
    org_type: Optional[str] = None,
    location: Optional[str] = None,
    tech_area: Optional[str] = None,
    horizon: Optional[str] = None,
    search: Optional[str] = None,
    conviction_tier: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Returns high-conviction forecasted solicitations across funding agencies and utilities.
    """
    try:
        return get_predictive_solicitation_forecasts(
            db=db,
            org_name=org_name,
            agency=agency,
            org_type=org_type,
            location=location,
            tech_area=tech_area,
            horizon=horizon,
            search=search,
            conviction_tier=conviction_tier
        )
    except Exception as e:
        logger.error(f"Error retrieving predictive forecasts: {e}")
        return []


def match_profile_forecasts(
    db: Session,
    profile: ProjectProfile
) -> List[Dict[str, Any]]:
    """
    Matches a user's specific project profile against upcoming forecasted solicitations.
    """
    try:
        return match_project_against_forecasts(db, profile)
    except Exception as e:
        logger.error(f"Error matching project against forecasts: {e}")
        return []


def generate_organization_forecast_briefing(
    db: Session,
    org_code: str,
    custom_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a strategic LLM forecasting brief for a specific organization.
    """
    try:
        return synthesize_llm_projection_briefing(db, org_code, custom_prompt)
    except Exception as e:
        logger.error(f"Error generating forecast briefing for {org_code}: {e}")
        return {
            "status": "error",
            "message": str(e),
            "disclaimer": PROBABILISTIC_DISCLAIMER
        }


def get_funding_organization_directory(db: Session) -> List[Dict[str, Any]]:
    """
    Retrieves the directory of funding organizations with cadence regularity and pipeline metrics.
    """
    try:
        return get_forecasting_organization_directory(db)
    except Exception as e:
        logger.error(f"Error retrieving forecasting organization directory: {e}")
        return []
