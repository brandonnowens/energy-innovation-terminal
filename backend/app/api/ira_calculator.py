"""Inflation Reduction Act (IRA 2022) Tax Credit & Capital Stack Engine."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/ira-calculator", tags=["IRA Tax Credit & Capital Stack Engine"])


class IraCalculateRequest(BaseModel):
    project_title: Optional[str] = "Clean Energy Infrastructure Project"
    technology_sector: str = "clean_hydrogen"  # clean_hydrogen, carbon_capture, advanced_nuclear, energy_storage, solar_wind, clean_fuels
    total_project_capex: float = 25000000.0     # $25M
    expected_grant_funding: float = 5000000.0   # $5M
    
    # IRA Parameters
    credit_type: str = "itc"  # itc (Investment Tax Credit) or ptc (Production Tax Credit)
    meets_prevailing_wage_apprenticeship: bool = True  # Required for full 5x credit multiplier (30% vs 6%)
    
    # Bonus Adders
    is_energy_community: bool = True   # +10%
    is_domestic_content: bool = True   # +10%
    is_low_income_community: bool = False  # +10% to +20%
    
    # Monetization & Debt
    monetization_route: str = "transferability"  # transferability (sale to corporate buyer) or direct_pay (non-profit/gov)
    transferability_price_cents_on_dollar: float = 93.0  # 93 cents per $1 credit
    senior_debt_pct: float = 30.0  # % of project financed with low-cost commercial debt


@router.post("/calculate")
def calculate_ira_capital_stack(req: IraCalculateRequest) -> Dict[str, Any]:
    """Calculate IRA tax credits, bonus adders, transferability cash proceeds, and blended capital stack."""
    capex = max(10000.0, req.total_project_capex)
    grants = max(0.0, min(req.expected_grant_funding, capex * 0.8))
    
    # Net eligible basis for ITC (some grants reduce basis depending on structure)
    eligible_basis = capex - (grants * 0.5)  # Under IRA safe-harbors, tax credits stack favorably on grant co-funding

    # Base ITC percentage
    if req.meets_prevailing_wage_apprenticeship:
        base_itc_pct = 30.0
    else:
        base_itc_pct = 6.0  # Penalty for non-prevailing wage

    # Bonus Adders
    bonus_energy_community_pct = 10.0 if req.is_energy_community else 0.0
    bonus_domestic_content_pct = 10.0 if req.is_domestic_content else 0.0
    bonus_low_income_pct = 10.0 if req.is_low_income_community else 0.0

    total_credit_pct = base_itc_pct + bonus_energy_community_pct + bonus_domestic_content_pct + bonus_low_income_pct

    # Total Nominal Tax Credit Value
    nominal_tax_credit_value = (total_credit_pct / 100.0) * eligible_basis

    # Monetization Proceeds (Transferability vs Direct Pay)
    if req.monetization_route == "direct_pay":
        net_tax_credit_cash = nominal_tax_credit_value * 1.00  # 100% direct refund from IRS
        discount_lost = 0.0
    else:
        transfer_rate = max(0.80, min(0.98, req.transferability_price_cents_on_dollar / 100.0))
        net_tax_credit_cash = nominal_tax_credit_value * transfer_rate
        discount_lost = nominal_tax_credit_value * (1.0 - transfer_rate)

    # Debt & Equity Breakdown
    debt_amount = (req.senior_debt_pct / 100.0) * capex
    
    # Remaining Sponsor Equity Required
    total_non_equity_funding = grants + net_tax_credit_cash + debt_amount
    sponsor_equity_required = max(0.0, capex - total_non_equity_funding)
    
    # Blended Cost of Capital calculation (Equity ~18% hurdle, Debt ~6.5%, Grants/Credits 0%)
    cost_equity = 0.18
    cost_debt = 0.065
    wacc_blended = (
        (sponsor_equity_required / capex) * cost_equity +
        (debt_amount / capex) * cost_debt +
        ((grants + net_tax_credit_cash) / capex) * 0.0
    )

    # Specific IRA Code Provision Mapping
    sector_provisions = {
        "clean_hydrogen": {"code": "IRA §45V / §48(a)(15)", "name": "Clean Hydrogen Production & Investment Credit", "max_incentive": "Up to $3.00/kg H2 or 50% Investment Tax Credit"},
        "carbon_capture": {"code": "IRA §45Q", "name": "Carbon Oxide Sequestration Credit", "max_incentive": "$85/metric ton (point source) or $180/metric ton (Direct Air Capture)"},
        "advanced_nuclear": {"code": "IRA §45U / §48E", "name": "Zero-Emission Nuclear Power Production & Tech-Neutral Clean Electricity", "max_incentive": "Up to $15/MWh or 50% Investment Tax Credit"},
        "energy_storage": {"code": "IRA §48(a)(c)(6)", "name": "Standalone Energy Storage Technology Credit", "max_incentive": "30% base + up to 20% in bonus adders (50% Total ITC)"},
        "solar_wind": {"code": "IRA §48E / §45Y", "name": "Clean Electricity Investment & Production Credit", "max_incentive": "30% base + 10% Energy Comm + 10% Domestic Content (50% ITC)"},
        "clean_fuels": {"code": "IRA §45Z", "name": "Clean Fuel Production Credit (CFPC)", "max_incentive": "Up to $1.00/gal (non-aviation) or $1.75/gal (Sustainable Aviation Fuel)"}
    }
    provision_info = sector_provisions.get(req.technology_sector, {"code": "IRA §48C / §48E", "name": "Advanced Clean Energy Tax Credit", "max_incentive": "30% - 50% Investment Tax Credit"})

    return {
        "project_title": req.project_title,
        "total_capex": capex,
        "grant_funding": grants,
        "ira_provision": provision_info,
        "tax_credit_breakdown": {
            "eligible_basis": eligible_basis,
            "base_itc_pct": base_itc_pct,
            "bonus_energy_community_pct": bonus_energy_community_pct,
            "bonus_domestic_content_pct": bonus_domestic_content_pct,
            "bonus_low_income_pct": bonus_low_income_pct,
            "total_credit_pct": total_credit_pct,
            "nominal_credit_usd": nominal_tax_credit_value,
            "monetization_route": req.monetization_route,
            "net_cash_proceeds_usd": net_tax_credit_cash,
            "transferability_discount_usd": discount_lost
        },
        "capital_stack_waterfall": [
            {"source": "Public Grants (Non-Dilutive)", "amount_usd": grants, "pct_of_capex": round((grants / capex) * 100, 1), "color": "#10B981"},
            {"source": "IRA Tax Credit Cash Sale", "amount_usd": net_tax_credit_cash, "pct_of_capex": round((net_tax_credit_cash / capex) * 100, 1), "color": "#06B6D4"},
            {"source": "Senior Project Debt", "amount_usd": debt_amount, "pct_of_capex": round((debt_amount / capex) * 100, 1), "color": "#6366F1"},
            {"source": "Sponsor Equity (Private Capital)", "amount_usd": sponsor_equity_required, "pct_of_capex": round((sponsor_equity_required / capex) * 100, 1), "color": "#F59E0B"}
        ],
        "financial_metrics": {
            "private_equity_reduction_pct": round(((capex - sponsor_equity_required) / capex) * 100, 1),
            "leverage_multiplier": round(capex / max(1.0, sponsor_equity_required), 2),
            "blended_wacc_pct": round(wacc_blended * 100, 2),
            "traditional_unassisted_wacc_pct": 14.5
        }
    }
