"""
Canonical Technology Bankability Rating (TBR) & Commercial Readiness Module.

Evaluates clean tech commercial bankability across 4 core pillars:
1. Technical De-risking & Field Operating Hours (TRL, operating hours, degradation rate)
2. Performance Warranty & EPC Underwriting (Tier-1 warranty, insurance wrap, safety certs)
3. Regulatory Compliance & Interconnection Gate Velocity (UL/IEC standards, interconnection queue)
4. Revenue Contract Certainty & Offtake Structure (Binding PPA, offtake, merchant exposure)
"""

from typing import Optional, Dict, Any, List
import logging
from sqlalchemy.orm import Session

from app.engine.bankability_engine import (
    calculate_technology_bankability as engine_calc_bankability,
    SECTOR_BENCHMARKS,
)

logger = logging.getLogger("CanonicalBankability")

BANKABILITY_RUBRIC_WEIGHTS = {
    "technical_derisking": 0.35,
    "warranty_and_underwriting": 0.25,
    "regulatory_and_standards": 0.20,
    "revenue_certainty": 0.20,
}


def evaluate_technology_bankability(
    technology_name: str,
    trl: int = 6,
    pilot_operating_hours: int = 1500,
    field_deployments_count: int = 3,
    degradation_rate_pct_annual: float = 1.5,
    has_tier1_warranty_backing: bool = False,
    has_ul_iec_safety_certification: bool = True,
    has_independent_engineer_report: bool = False,
    offtake_contract_status: str = "signed_loi",  # no_contract, signed_loi, pilot_agreement, binding_ppa_offtake
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Evaluates institutional 4-Pillar Technology Bankability Rating (TBR),
    commercialization gaps, and project finance underwriting feasibility.
    """
    # Pillar 1: Technical De-risking (0-100)
    p1_score = min(100.0, (trl / 9.0) * 40.0 + min(35.0, (pilot_operating_hours / 3000.0) * 35.0) + min(25.0, field_deployments_count * 5.0))
    if degradation_rate_pct_annual > 3.0:
        p1_score *= 0.85

    # Pillar 2: Warranty & EPC Underwriting (0-100)
    p2_score = 40.0
    if has_tier1_warranty_backing:
        p2_score += 35.0
    if has_independent_engineer_report:
        p2_score += 25.0

    # Pillar 3: Regulatory & Standards Compliance (0-100)
    p3_score = 50.0
    if has_ul_iec_safety_certification:
        p3_score += 40.0
    if trl >= 7:
        p3_score += 10.0

    # Pillar 4: Revenue & Offtake Certainty (0-100)
    offtake_scores = {
        "no_contract": 20.0,
        "signed_loi": 55.0,
        "pilot_agreement": 75.0,
        "binding_ppa_offtake": 95.0,
    }
    p4_score = offtake_scores.get(offtake_contract_status, 50.0)

    # Composite Score (0-100)
    composite = (
        p1_score * BANKABILITY_RUBRIC_WEIGHTS["technical_derisking"] +
        p2_score * BANKABILITY_RUBRIC_WEIGHTS["warranty_and_underwriting"] +
        p3_score * BANKABILITY_RUBRIC_WEIGHTS["regulatory_and_standards"] +
        p4_score * BANKABILITY_RUBRIC_WEIGHTS["revenue_certainty"]
    )
    composite = round(min(100.0, max(10.0, composite)), 1)

    # Grade and Tier Assignment
    if composite >= 90.0:
        grade = "AAA"
        tier = "Tier 1 - Commercial Project Finance Ready"
    elif composite >= 80.0:
        grade = "AA"
        tier = "Tier 2 - Concessionary / Green Bank Financeable"
    elif composite >= 70.0:
        grade = "A"
        tier = "Tier 3 - Pilot Demonstration & Grant Supported"
    elif composite >= 55.0:
        grade = "BBB"
        tier = "Tier 4 - Early Stage Venture / R&D Scope"
    else:
        grade = "BB"
        tier = "Tier 5 - Fundamental Lab Stage"

    # Identify Commercialization Gaps
    gaps = []
    if not has_independent_engineer_report:
        gaps.append("Commission an accredited Independent Engineer (IE) technical review (e.g. DNV, Black & Veatch).")
    if not has_tier1_warranty_backing:
        gaps.append("Secure an investment-grade performance warranty or Munich Re / New Energy Risk insurance wrap.")
    if not has_ul_iec_safety_certification:
        gaps.append("Finalize UL 9540 / IEC 62933 safety certification testing.")
    if offtake_contract_status in ["no_contract", "signed_loi"]:
        gaps.append("Advance bilateral offtake discussions to binding long-term contracts or utility pilot agreements.")

    return {
        "technology_name": technology_name,
        "composite_bankability_score": composite,
        "bankability_grade": grade,
        "bankability_tier": tier,
        "pillars": {
            "technical_derisking": {
                "score": round(p1_score, 1),
                "weight_pct": 35,
                "status": "strong" if p1_score >= 75 else "developing"
            },
            "warranty_and_underwriting": {
                "score": round(p2_score, 1),
                "weight_pct": 25,
                "status": "strong" if p2_score >= 75 else "gap_detected"
            },
            "regulatory_and_standards": {
                "score": round(p3_score, 1),
                "weight_pct": 20,
                "status": "strong" if p3_score >= 75 else "developing"
            },
            "revenue_certainty": {
                "score": round(p4_score, 1),
                "weight_pct": 20,
                "status": "strong" if p4_score >= 75 else "gap_detected"
            }
        },
        "identified_commercialization_gaps": gaps,
        "recommended_underwriting_pathway": (
            "Suitable for senior debt and tax equity financing."
            if composite >= 80.0
            else "Requires blended capital: grant co-funding + Green Bank subordinated debt."
        )
    }


def compute_technology_bankability(
    db: Session,
    technology_id: str,
    technology_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes institutional 4-Pillar TBR using historical database awards and sector benchmarks.
    """
    return engine_calc_bankability(
        db=db,
        tech_id=technology_id,
        technology_name=technology_name,
    )


def get_bankability_rubric_weights() -> Dict[str, float]:
    """Returns the weights of the 4 bankability evaluation pillars."""
    return BANKABILITY_RUBRIC_WEIGHTS
