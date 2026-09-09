"""
Canonical Reviewer Rubric & Winning Angle Intelligence Module.

Reverse-engineers the unwritten evaluation biases, scoring rubric criteria,
mandatory reviewer keywords, optimal teaming partner rosters, and red-flag landmines
for clean energy funding opportunities based on historical awards and institutional diligence precedents.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.engine.profile import ProjectProfile
from app.engine.winning_angle_engine import (
    WinningAngleReport,
    generate_grounded_winning_angle,
    generate_winning_angle_with_llm,
)

logger = logging.getLogger("CanonicalReviewerRubric")


def generate_reviewer_rubric(
    db: Session,
    profile: ProjectProfile,
    opportunity: Opportunity,
    match_score: float = 0.85,
    force_live_llm: bool = False
) -> Dict[str, Any]:
    """
    Generates a structured Reviewer Rubric and Winning Angle Report.
    
    Includes:
    - winning_hook: executive narrative hook
    - strategic_framing: alignment with unstated institutional mandates
    - hidden_rubric_breakdown: criteria, weights, target scores, and reviewer biases
    - mandatory_reviewer_keywords: mandatory domain and compliance terms
    - optimal_teaming_strategy: partner archetypes and strategic rationale
    - unwritten_evaluation_biases: agency-specific evaluator habits
    - red_flag_landmines: fatal flaw triggers to avoid
    - competitive_differentiation: positioning against typical applicant pool
    """
    try:
        report: WinningAngleReport = generate_winning_angle_with_llm(
            db=db,
            profile=profile,
            opp=opportunity,
            match_score=match_score,
            force_live=force_live_llm
        )
        return report.to_dict()
    except Exception as e:
        logger.warning(f"Live rubric generation failed, falling back to grounded model: {e}")
        try:
            grounded = generate_grounded_winning_angle(db, profile, opportunity, match_score)
            return grounded.to_dict()
        except Exception as err:
            logger.error(f"Fatal error generating reviewer rubric: {err}")
            return {
                "opportunity_id": getattr(opportunity, "id", None),
                "solicitation_number": getattr(opportunity, "solicitation_number", "SOL-UNKNOWN"),
                "opportunity_name": getattr(opportunity, "name", "Funding Opportunity"),
                "agency": getattr(opportunity, "agency", "Funding Agency"),
                "match_score_pct": int(match_score * 100),
                "winning_hook": "Position technical innovation against statutory decarbonization mandates.",
                "hidden_rubric_breakdown": [],
                "mandatory_reviewer_keywords": ["techno-economic analysis", "TRL verification", "DAC benefits"],
                "status": "fallback",
                "error": str(err)
            }
