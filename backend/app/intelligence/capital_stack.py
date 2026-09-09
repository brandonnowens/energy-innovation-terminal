"""
Canonical Capital Stack, IRA Direct Pay Tax Credits & Blended WACC Module.

Provides financial engineering for clean energy assets under IRC Title 26:
- Section 48 / 48E Investment Tax Credit (ITC)
- Section 45 / 45Y Production Tax Credit (PTC)
- Section 45V Clean Hydrogen
- Section 45Q Carbon Sequestration
- Section 48C / 45X Advanced Energy Manufacturing
- Section 6417 Direct Pay for tax-exempt / municipal entities
- Concessionary Green Bank debt leverage and Blended WACC solver
"""

from typing import Optional, List, Dict, Any
import logging

from app.engine.capital_stack_engine import (
    calculate_capital_stack as engine_calculate_capital_stack,
    classify_technology_statutory_eligibility,
)

logger = logging.getLogger("CanonicalCapitalStack")

SUPPORTED_TECHNOLOGIES = [
    "energy_storage",
    "solar",
    "wind",
    "hydrogen",
    "carbon_capture",
    "geothermal",
    "building_electrification",
    "clean_transportation",
    "microgrid",
    "clean_manufacturing",
    "nuclear",
    "bioenergy"
]


def solve_capital_stack(
    total_project_cost: float,
    grant_request: float,
    technology_type: str = "energy_storage",
    location_state: str = "NY",
    is_prevailing_wage_compliant: bool = True,
    is_energy_community: bool = False,
    is_domestic_content_compliant: bool = False,
    senior_debt_share_pct: Optional[float] = None,
    equity_cost_of_capital_pct: Optional[float] = None,
    applicant_type: Optional[str] = None,
    project_summary: Optional[str] = None,
    skip_llm: bool = False
) -> Dict[str, Any]:
    """
    Computes audited multi-layer project capital stack, IRC Title 26 IRA tax incentives,
    concessionary Green Bank leverage, sponsor equity requirements, and blended WACC savings.
    """
    capex = max(10_000.0, float(total_project_cost))
    grant = min(float(grant_request), capex * 0.80)

    # Call underlying calculation engine
    engine_result = engine_calculate_capital_stack(
        project_cost=capex,
        matched_grant_max=grant,
        technology_category=technology_type,
        technology_areas=[technology_type],
        project_summary=project_summary or f"Deployment of {technology_type} in {location_state}",
        applicant_type=applicant_type,
        energy_community_bonus=is_energy_community,
        domestic_content_bonus=is_domestic_content_compliant,
        prevailing_wage_compliant=is_prevailing_wage_compliant,
        skip_llm=skip_llm
    )

    # Derive standardized return payload
    tax_equity_pct = engine_result.get("tax_credit_pct", 30.0)
    tax_equity_amount = (tax_equity_pct / 100.0) * capex

    # Non-dilutive and concessionary layers
    green_bank_debt = engine_result.get("green_bank_debt_amount", capex * 0.35)
    sponsor_equity = max(0.0, capex - (grant + tax_equity_amount + green_bank_debt))

    blended_wacc = engine_result.get("optimized_blended_wacc_pct", 5.2)
    commercial_wacc = engine_result.get("unsubsidized_commercial_wacc_pct", 11.5)

    return {
        "total_project_cost": capex,
        "technology_type": technology_type,
        "location_state": location_state,
        "capital_stack_breakdown": {
            "non_dilutive_grant": {
                "amount": grant,
                "share_pct": round((grant / capex) * 100, 1),
                "cost_of_capital_pct": 0.0,
                "description": "State / Federal Non-Dilutive Grant"
            },
            "ira_tax_monetization": {
                "amount": tax_equity_amount,
                "share_pct": round((tax_equity_amount / capex) * 100, 1),
                "cost_of_capital_pct": 0.0,
                "description": f"IRC §48 / §45 Direct Pay Tax Monetization ({tax_equity_pct}%)"
            },
            "concessionary_green_bank_debt": {
                "amount": green_bank_debt,
                "share_pct": round((green_bank_debt / capex) * 100, 1),
                "cost_of_capital_pct": 4.5,
                "description": f"Concessionary Green Bank Debt ({location_state} Green Bank)"
            },
            "sponsor_equity": {
                "amount": sponsor_equity,
                "share_pct": round((sponsor_equity / capex) * 100, 1),
                "cost_of_capital_pct": 12.0,
                "description": "Sponsor Equity Requirement"
            }
        },
        "ira_tax_credits": {
            "total_credit_pct": tax_equity_pct,
            "statutory_name": engine_result.get("statutory_credit_name", "Clean Energy Investment Tax Credit (§ 48)"),
            "statutory_code": engine_result.get("statutory_code_ref", "26 U.S.C. § 48"),
            "prevailing_wage_multiplier_applied": is_prevailing_wage_compliant,
            "energy_community_bonus_applied": is_energy_community,
            "domestic_content_bonus_applied": is_domestic_content_compliant,
            "direct_pay_eligible": engine_result.get("is_direct_pay_eligible", True)
        },
        "blended_wacc_pct": blended_wacc,
        "commercial_benchmark_wacc_pct": commercial_wacc,
        "annual_interest_savings": round((commercial_wacc - blended_wacc) / 100.0 * capex, 2),
        "engine_detail": engine_result
    }


def calculate_ira_direct_pay_incentive(
    technology_type: str,
    project_cost: float,
    prevailing_wage: bool = True,
    energy_community: bool = False,
    domestic_content: bool = False
) -> Dict[str, Any]:
    """Calculates Title 26 IRA elective payment value for a given CapEx."""
    is_eligible, name, code, notes, base_rate = classify_technology_statutory_eligibility(
        tech_category=technology_type,
        technology_areas=[technology_type]
    )

    rate = base_rate
    if is_eligible:
        if prevailing_wage:
            rate = max(0.30, rate * 5.0 if rate == 0.06 else 0.30)
        if energy_community:
            rate += 0.10
        if domestic_content:
            rate += 0.10

    total_value = rate * project_cost

    return {
        "is_eligible": is_eligible,
        "statutory_name": name,
        "statutory_code": code,
        "effective_credit_rate_pct": round(rate * 100, 1),
        "projected_cash_credit_value": round(total_value, 2),
        "notes": notes
    }


def get_supported_technologies() -> List[str]:
    """Returns list of supported clean tech classifications."""
    return SUPPORTED_TECHNOLOGIES
