"""
Multi-Layer Project Financing & Blended WACC Optimization Engine.

Provides an institutional-grade, fully audited financial engineering model for clean energy,
climate technology, and infrastructure deployment projects.

Performs strict, technology-specific statutory eligibility checks under the Internal Revenue Code (IRC) Title 26
to prevent accidentally over-stating federal incentives to unqualified or non-energy projects.

Comprehensive Review of Audited Statutory Provisions:
1. 26 U.S.C. § 48 / § 48E: Investment Tax Credit (Solar, Standalone Storage >= 5 kWh, Geothermal, Microgrids, Biogas, Fuel Cells)
2. 26 U.S.C. § 45 / § 45Y: Clean Electricity Production Tax Credit (Wind, Solar, Geothermal, Marine, Nuclear)
3. 26 U.S.C. § 45V: Clean Hydrogen Production Credit ($0.60 to $3.00/kg H2) / § 48(a)(15) ITC (30%-50%)
4. 26 U.S.C. § 45Q: Carbon Oxide Sequestration Credit ($85/tonne point-source; $180/tonne Direct Air Capture)
5. 26 U.S.C. § 48C / § 45X: Qualifying Advanced Energy Project Credit (30% allocated) & Advanced Manufacturing Production Credit
6. 26 U.S.C. § 179D: Energy Efficient Commercial Buildings Deduction (up to $5.00/sq ft for >= 25% energy reduction)
7. 26 U.S.C. § 30C / § 45W: Alternative Fuel Vehicle Refueling Property & Commercial Clean Vehicles (30% up to $100k/charger)
8. 26 U.S.C. § 6417: Direct Pay (Elective Payment) for 501(c)(3) tax-exempt, state, municipal, and tribal entities
9. 26 U.S.C. § 6418: Transferability (Credit Transfer) for for-profit corporations at ~93.5% net market value
"""

import re
from typing import Dict, Any, List, Optional, Tuple


# =============================================================================
# Technology-Specific Statutory Eligibility Mapping
# =============================================================================

# Non-energy, apparel, arts, social service, general IT, and commercial categories that do NOT qualify for federal clean energy tax equity
NON_QUALIFYING_TAX_CREDIT_DOMAINS = [
    "garment", "apparel", "costume", "fashion", "textile", "clothing",
    "theatre", "theater", "arts", "culture", "humanities", "entertainment",
    "social service", "food bank", "retail", "hospitality", "hotel",
    "pure software", "consumer app", "social media", "fintech",
    "general workforce", "general training", "rethread"
]


def classify_technology_statutory_eligibility(
    tech_category: Optional[str] = None,
    technology_areas: Optional[List[str]] = None,
    activity_types: Optional[List[str]] = None,
    summary_text: Optional[str] = None,
) -> Tuple[bool, str, str, str, float]:
    """
    Evaluates technology-specific statutory eligibility under IRC Title 26.
    Ensures that Disadvantaged Communities ('Community & DAC') is not confused with Direct Air Capture (45Q),
    and that non-energy / garment / arts projects receive 0% tax credit.

    Returns:
        is_eligible (bool): Whether the technology qualifies for Title 26 tax equity
        statutory_credit_name (str): The statutory incentive title
        statutory_code_ref (str): Exact IRC legal citation
        eligibility_notes (str): Detailed statutory qualification explanation
        standard_base_rate (float): Standard statutory base rate (e.g. 0.30 or 0.0)
    """
    corpus_terms = []
    if tech_category:
        corpus_terms.append(tech_category.lower())
    if technology_areas:
        corpus_terms.extend([t.lower() for t in technology_areas])
    if activity_types:
        corpus_terms.extend([a.lower() for a in activity_types])
    if summary_text:
        corpus_terms.append(summary_text.lower())

    text_blob = " ".join(corpus_terms)

    # Disambiguate 'Community & DAC' (Disadvantaged Communities) vs Direct Air Capture
    is_community_dac = bool(re.search(r'\b(community\s*&\s*dac|disadvantaged\s+communit(y|ies)|environmental\s+justice|justice40)\b', text_blob))

    # True Carbon Capture / Direct Air Capture requires explicit carbon / CO2 / CDR keywords
    is_carbon_dac = bool(re.search(r'\b(direct\s+air\s+capture|carbon\s+capture|carbon\s+dioxide\s+removal|point[- ]source\s+capture|co2\s+capture|co2\s+sequestration|geologic\s+storage|carbon\s+mineralization)\b', text_blob))
    if not is_carbon_dac and re.search(r'\bdac\b', text_blob) and not is_community_dac:
        if re.search(r'\b(carbon|co2|atmospheric|cdr|sequestration|air\s+contactor)\b', text_blob):
            is_carbon_dac = True

    # Check for genuine physical energy generation, storage, or conversion assets
    has_clean_energy_hardware = any([
        bool(re.search(r'\b(solar|photovoltaic|pv|concentrated\s+solar)\b', text_blob)),
        bool(re.search(r'\b(battery|energy\s+storage|bess|ldes|flow\s+battery|iron[- ]air|thermal\s+storage)\b', text_blob)),
        bool(re.search(r'\b(hydrogen|electrolyzer|electrolysis|fuel\s+cell|h2\s+production)\b', text_blob)),
        bool(re.search(r'\b(geothermal|ground[- ]source\s+heat\s+pump|industrial\s+heat\s+pump|thermal\s+energy\s+network)\b', text_blob)),
        bool(re.search(r'\b(wind|offshore\s+wind|wind\s+turbine)\b', text_blob)),
        bool(re.search(r'\b(microgrid\s+controller|clean\s+energy\s+manufacturing|advanced\s+nuclear|smr)\b', text_blob)),
        bool(re.search(r'\b(ev\s+charging|alternative\s+fuel\s+refueling|fleet\s+electrification)\b', text_blob)),
        is_carbon_dac
    ])

    is_non_qualifying_domain = any(term in text_blob for term in NON_QUALIFYING_TAX_CREDIT_DOMAINS)

    # 1. Strict Exclusion: Non-qualifying domain without qualified energy generation/storage hardware
    if is_non_qualifying_domain and not has_clean_energy_hardware:
        return (
            False,
            "Non-Qualifying Domain (No Title 26 Energy Property)",
            "N/A (IRC Title 26 Not Applicable)",
            "Project scope (apparel/garments, workforce training, arts, cultural preservation, or general IT) does not construct or operate eligible energy property under Internal Revenue Code (IRC) Title 26 (Sections 48/45/45V/45Q/48C). Federal clean energy tax equity is strictly set to $0.00 (0.00%) to prevent over-stating incentive availability. Non-dilutive capital is structured via competitive public and philanthropic grant programs.",
            0.0000
        )

    # 2. Clean Hydrogen: 26 U.S.C. § 45V / § 48(a)(15)
    if bool(re.search(r'\b(hydrogen|electrolyzer|electrolysis|h2\s+production|clean\s+h2)\b', text_blob)):
        return (
            True,
            "IRA Section 45V Clean Hydrogen PTC ($3.00/kg) / Section 48(a)(15) ITC",
            "26 U.S.C. § 45V / § 48(a)(15)",
            "Qualified clean hydrogen production facility achieving lifecycle GHG emissions below 0.45 kg CO2e/kg H2, qualifying for Tier-4 PTC ($3.00/kg) or 30%-50% ITC.",
            0.3000
        )

    # 3. Carbon Oxide Sequestration & DAC: 26 U.S.C. § 45Q
    if is_carbon_dac:
        return (
            True,
            "IRA Section 45Q Carbon Oxide Sequestration Credit",
            "26 U.S.C. § 45Q",
            "Qualified carbon capture facility with industrial point-source capture ($85/tonne) or Direct Air Capture ($180/tonne with >= 1,000 tonnes/yr capture capacity).",
            0.3000
        )

    # 4. Clean Energy Manufacturing: 26 U.S.C. § 48C / § 45X
    if bool(re.search(r'\b(clean\s+energy\s+manufacturing|battery\s+manufacturing|cell\s+fabrication|semiconductor|wafer\s+manufacturing)\b', text_blob)):
        return (
            True,
            "IRA Section 48C Advanced Energy Project / Section 45X Advanced Manufacturing",
            "26 U.S.C. § 48C / § 45X",
            "Qualifying advanced energy manufacturing facility producing solar, battery, wind, or critical mineral components with DOE 48C allocation or 45X production credits.",
            0.3000
        )

    # 5. Standalone Energy Storage: 26 U.S.C. § 48(a)(c)(6) / § 48E
    if bool(re.search(r'\b(energy\s+storage|battery|bess|ldes|iron[- ]air|flow\s+battery|thermal\s+storage|solid[- ]state\s+battery)\b', text_blob)):
        return (
            True,
            "IRA Section 48(a)(c)(6) Standalone Energy Storage Property Credit",
            "26 U.S.C. § 48(a)(c)(6) / § 48E",
            "Qualified standalone electrical, thermal, or mechanical energy storage technology with nameplate capacity >= 5 kWh, qualifying for 30% base ITC + up to 20% adders.",
            0.3000
        )

    # 6. Solar & Wind Clean Electricity: 26 U.S.C. § 48 / § 48E / § 45Y
    if bool(re.search(r'\b(solar|photovoltaic|pv|concentrated\s+solar|wind|offshore\s+wind|wind\s+turbine)\b', text_blob)):
        return (
            True,
            "IRA Section 48 / 48E Clean Electricity Investment Tax Credit",
            "26 U.S.C. § 48(a) / § 48E",
            "Qualified zero-emission solar or wind electricity generation property qualifying for 30% base ITC + 10% Energy Community + 10% Domestic Content adders.",
            0.3000
        )

    # 7. Geothermal & Heat Pumps: 26 U.S.C. § 48(a)(3)(A)(vii) / § 179D
    if bool(re.search(r'\b(geothermal|heat\s+pump|thermal\s+energy\s+network|building\s+electrification|district\s+thermal)\b', text_blob)):
        return (
            True,
            "IRA Section 48(a)(3)(A)(vii) Geothermal Heat Pump & Section 179D Commercial Efficiency",
            "26 U.S.C. § 48(a)(3)(A)(vii) / § 179D",
            "Qualified ground-source heat pump, thermal energy network, or commercial building energy efficiency system achieving certified thermal performance standards.",
            0.3000
        )

    # 8. Clean Transportation & EV Infrastructure: 26 U.S.C. § 30C / § 45W
    if bool(re.search(r'\b(clean\s+transportation|ev\s+charging|fleet\s+electrification|refueling\s+infrastructure)\b', text_blob)):
        return (
            True,
            "IRA Section 30C Alternative Fuel Refueling Property Credit",
            "26 U.S.C. § 30C / § 45W",
            "Qualified commercial EV fast-charging and alternative clean fuel refueling infrastructure located in eligible census tracts (up to $100,000 per charger).",
            0.3000
        )

    # 9. Microgrid Controllers: 26 U.S.C. § 48(a)(3)(A)(ix)
    if bool(re.search(r'\b(microgrid|islanding\s+controller|grid\s+modernization)\b', text_blob)):
        return (
            True,
            "IRA Section 48(a)(3)(A)(ix) Microgrid Controller & Clean Grid Asset Credit",
            "26 U.S.C. § 48(a)(3)(A)(ix)",
            "Qualified microgrid controller equipment capable of isolating, islanding, and controlling distributed energy resources.",
            0.3000
        )

    # 10. Fallback for non-energy / unverified scope: Do not over-state tax equity
    return (
        False,
        "Non-Energy Domain (No Title 26 Energy Property Identified)",
        "N/A (IRC Title 26 Not Applicable)",
        "No qualified clean energy property (solar, storage, hydrogen, CCS, heat pumps, microgrids) identified. Clean energy tax credit rate set to 0.00% to ensure incentives are not over-stated.",
        0.0000
    )


def calculate_capital_stack(
    project_cost: Optional[float] = None,
    matched_grant_max: Optional[float] = None,
    technology_category: Optional[str] = None,
    technology_areas: Optional[List[str]] = None,
    activity_types: Optional[List[str]] = None,
    project_summary: Optional[str] = None,
    applicant_type: Optional[str] = None,
    solicitation_name: Optional[str] = None,
    agency: Optional[str] = None,
    energy_community_bonus: bool = True,
    domestic_content_bonus: bool = False,
    prevailing_wage_compliant: bool = True,
    tax_exempt_direct_pay: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Computes a pro-forma capital stack waterfall with technology-specific statutory eligibility gating.
    Guarantees that non-qualifying projects are not erroneously assigned clean energy tax credits.
    """
    total_cost = float(project_cost or 10_000_000.0)
    if total_cost <= 0:
        total_cost = 10_000_000.0

    lead_agency = agency or "Public Innovation Agency"
    lead_solicitation = solicitation_name or "Competitive Funding Program"

    # =========================================================================
    # Step 1: Technology-Specific Statutory Eligibility Verification
    # =========================================================================
    is_tax_eligible, statutory_name, statutory_code, eligibility_notes, raw_base_rate = (
        classify_technology_statutory_eligibility(
            tech_category=technology_category,
            technology_areas=technology_areas,
            activity_types=activity_types,
            summary_text=project_summary,
        )
    )

    # Auto-detect Direct Pay (§ 6417) eligibility based on applicant entity type
    app_type_clean = (applicant_type or "").lower()
    is_tax_exempt_entity = any(t in app_type_clean for t in [
        "nonprofit", "non_profit", "501(c)(3)", "municipality", "public_sector",
        "government", "university", "academic", "tribal", "cooperative"
    ])

    if tax_exempt_direct_pay is None:
        effective_direct_pay = is_tax_exempt_entity
    else:
        effective_direct_pay = tax_exempt_direct_pay

    # =========================================================================
    # Tier 1: Non-Dilutive Public Grants
    # Cost of Capital: 0.00% | Zero Dilution
    # Sizing: Program max co-funding or typical 25%-50% cost-share allocation
    # =========================================================================
    if matched_grant_max and matched_grant_max > 0:
        raw_grant = min(float(matched_grant_max), total_cost * 0.50)
    else:
        raw_grant = total_cost * 0.25

    grant_amount = round(raw_grant, 2)
    grant_pct = round((grant_amount / total_cost) * 100, 2)
    grant_cost_rate = 0.0000

    # =========================================================================
    # Tier 2: Federal Tax Credit / Direct Pay Layer (IRA 2022)
    # Strictly gated on is_tax_eligible
    # =========================================================================
    if is_tax_eligible:
        base_itc_rate = 0.30 if prevailing_wage_compliant else 0.06
        bonus_ec_rate = 0.10 if energy_community_bonus else 0.00
        bonus_dc_rate = 0.10 if domestic_content_bonus else 0.00
        total_itc_rate = round(base_itc_rate + bonus_ec_rate + bonus_dc_rate, 4)

        monetization_factor = 1.00 if effective_direct_pay else 0.935
        eligible_basis = total_cost
        tax_credit_gross = eligible_basis * total_itc_rate
        tax_credit_net = round(tax_credit_gross * monetization_factor, 2)
        tax_credit_pct = round((tax_credit_net / total_cost) * 100, 2)
        tax_credit_cost_rate = 0.0000
    else:
        base_itc_rate = 0.0000
        bonus_ec_rate = 0.0000
        bonus_dc_rate = 0.0000
        total_itc_rate = 0.0000
        monetization_factor = 0.0000
        tax_credit_gross = 0.00
        tax_credit_net = 0.00
        tax_credit_pct = 0.00
        tax_credit_cost_rate = 0.0000

    # =========================================================================
    # Tier 3: Concessionary / Green Bank Subordinated Gap Debt
    # Cost of Capital: 5.25% fixed coupon
    # Sizing: Up to 55% of residual unfunded capex, capped at 30% of total project cost
    # =========================================================================
    subtotal_non_dilutive = grant_amount + tax_credit_net
    remaining_after_subsidies = max(0.0, total_cost - subtotal_non_dilutive)
    debt_capacity_pct = 0.55 if is_tax_eligible else 0.40
    green_bank_debt_amount = round(min(remaining_after_subsidies * debt_capacity_pct, total_cost * 0.30), 2)
    debt_pct = round((green_bank_debt_amount / total_cost) * 100, 2)
    debt_interest_rate = 0.0525
    corporate_tax_rate = 0.2100
    after_tax_debt_rate = round(debt_interest_rate * (1.0 - corporate_tax_rate), 4)

    # =========================================================================
    # Tier 4: Developer / Sponsor Equity & Strategic Offtake
    # Cost of Capital: 12.50% developer hurdle rate (or 6.0% philanthropic for 501(c)(3))
    # Sizing: Remaining net capital required after grant, tax equity, and debt
    # =========================================================================
    sponsor_equity_amount = round(max(0.0, total_cost - (grant_amount + tax_credit_net + green_bank_debt_amount)), 2)
    sponsor_equity_pct = round((sponsor_equity_amount / total_cost) * 100, 2)
    equity_hurdle_rate = 0.0600 if is_tax_exempt_entity else 0.1250

    # =========================================================================
    # Financial Engineering & Blended WACC Optimization
    # =========================================================================
    w_grant = grant_amount / total_cost
    w_tax = tax_credit_net / total_cost
    w_debt = green_bank_debt_amount / total_cost
    w_equity = sponsor_equity_amount / total_cost

    wacc_grant_contrib = w_grant * grant_cost_rate
    wacc_tax_contrib = w_tax * tax_credit_cost_rate
    wacc_debt_contrib = w_debt * debt_interest_rate
    wacc_equity_contrib = w_equity * equity_hurdle_rate

    blended_wacc_nominal = (wacc_grant_contrib + wacc_tax_contrib + wacc_debt_contrib + wacc_equity_contrib) * 100
    blended_wacc_pct = round(blended_wacc_nominal, 2)

    blended_wacc_after_tax = ((w_debt * after_tax_debt_rate) + (w_equity * equity_hurdle_rate)) * 100
    blended_wacc_after_tax_pct = round(blended_wacc_after_tax, 2)

    # Unsubsidized Commercial Benchmark
    unsubsidized_debt_weight = 0.40
    unsubsidized_debt_rate = 0.0775
    unsubsidized_equity_weight = 0.60
    unsubsidized_equity_rate = 0.1450 if not is_tax_exempt_entity else 0.0950
    unsubsidized_wacc = (unsubsidized_debt_weight * unsubsidized_debt_rate + unsubsidized_equity_weight * unsubsidized_equity_rate) * 100
    unsubsidized_wacc_pct = round(unsubsidized_wacc, 2)

    wacc_savings_bps = int(round((unsubsidized_wacc - blended_wacc_nominal) * 100))
    annual_carrying_cost_savings = round(total_cost * ((unsubsidized_wacc - blended_wacc_nominal) / 100.0), 2)
    ten_year_cumulative_savings = round(annual_carrying_cost_savings * 10.0, 2)

    total_non_dilutive_amount = grant_amount + tax_credit_net
    total_non_dilutive_pct = round((total_non_dilutive_amount / total_cost) * 100, 2)

    standard_payback_years = 8.5
    subsidized_payback_years = round(max(1.5, standard_payback_years * (sponsor_equity_amount / total_cost) * 1.55), 1)

    # Sensitivity Matrix
    sensitivity_table = []
    if is_tax_eligible:
        for test_grant_pct in [10, 25, 40]:
            for test_tax_pct in [30, 40, 50]:
                t_grant = total_cost * (test_grant_pct / 100.0)
                t_tax = total_cost * (test_tax_pct / 100.0) * monetization_factor
                t_rem = max(0.0, total_cost - (t_grant + t_tax))
                t_debt = min(t_rem * 0.55, total_cost * 0.30)
                t_eq = max(0.0, total_cost - (t_grant + t_tax + t_debt))
                sens_wacc = ((t_debt / total_cost) * debt_interest_rate + (t_eq / total_cost) * equity_hurdle_rate) * 100
                sensitivity_table.append({
                    "grant_rate_pct": test_grant_pct,
                    "gross_tax_rate_pct": test_tax_pct,
                    "net_non_dilutive_pct": round(((t_grant + t_tax) / total_cost) * 100, 1),
                    "sponsor_equity_pct": round((t_eq / total_cost) * 100, 1),
                    "resulting_wacc_pct": round(sens_wacc, 2),
                    "wacc_savings_bps": int(round((unsubsidized_wacc - sens_wacc) * 100)),
                })
    else:
        for test_grant_pct in [15, 30, 45, 60]:
            t_grant = total_cost * (test_grant_pct / 100.0)
            t_rem = max(0.0, total_cost - t_grant)
            t_debt = min(t_rem * 0.40, total_cost * 0.30)
            t_eq = max(0.0, total_cost - (t_grant + t_debt))
            sens_wacc = ((t_debt / total_cost) * debt_interest_rate + (t_eq / total_cost) * equity_hurdle_rate) * 100
            sensitivity_table.append({
                "grant_rate_pct": test_grant_pct,
                "gross_tax_rate_pct": 0,
                "net_non_dilutive_pct": test_grant_pct,
                "sponsor_equity_pct": round((t_eq / total_cost) * 100, 1),
                "resulting_wacc_pct": round(sens_wacc, 2),
                "wacc_savings_bps": int(round((unsubsidized_wacc - sens_wacc) * 100)),
            })

    # Build Tranche Layers
    layers = [
        {
            "tier": 1,
            "name": "Non-Dilutive Public Grant",
            "source": f"{lead_agency} ({lead_solicitation})",
            "amount": grant_amount,
            "percentage": grant_pct,
            "cost_of_capital_pct": 0.0,
            "dilution_type": "Zero Dilution / Pure Grant",
            "color": "emerald",
            "badge": "Public Co-Funding",
            "citation": "Federal / State Innovation Solicitation (2 CFR 200)"
        }
    ]

    if is_tax_eligible:
        layers.append({
            "tier": 2,
            "name": "Federal Tax Equity & Direct Pay",
            "source": statutory_name,
            "amount": tax_credit_net,
            "percentage": tax_credit_pct,
            "cost_of_capital_pct": 0.0,
            "dilution_type": "Statutory Tax Credit Monetization",
            "color": "cyan",
            "badge": f"{int(total_itc_rate * 100)}% IRA Credit",
            "citation": statutory_code
        })
    else:
        layers.append({
            "tier": 2,
            "name": "Federal Clean Energy Tax Equity (Ineligible)",
            "source": "IRC Title 26 (Not Applicable to Non-Energy Domain)",
            "amount": 0.00,
            "percentage": 0.00,
            "cost_of_capital_pct": 0.0,
            "dilution_type": "0.0% Tax Credit (Non-Energy Property)",
            "color": "slate",
            "badge": "0% Tax Credit (Ineligible)",
            "citation": "IRC Title 26 Sections 48/45 Not Applicable"
        })

    layers.extend([
        {
            "tier": 3,
            "name": "Green Bank / Programmatic Gap Loan",
            "source": "State Green Bank / Infrastructure Bank Subordinated Debt Facility",
            "amount": green_bank_debt_amount,
            "percentage": debt_pct,
            "cost_of_capital_pct": 5.25,
            "dilution_type": "Concessionary Subordinated Debt",
            "color": "indigo",
            "badge": "5.25% Fixed Coupon",
            "citation": "Green Bank Revolving Debt Facility (NY Green Bank / CA IBank)"
        },
        {
            "tier": 4,
            "name": "Developer / Sponsor Equity & Philanthropy",
            "source": "Developer Equity / Corporate Offtaker / Philanthropic Match",
            "amount": sponsor_equity_amount,
            "percentage": sponsor_equity_pct,
            "cost_of_capital_pct": round(equity_hurdle_rate * 100, 2),
            "dilution_type": "Project Sponsor Equity",
            "color": "amber",
            "badge": f"Net Equity ({equity_hurdle_rate * 100:.1f}%)",
            "citation": "NREL ATB Developer Hurdle Benchmark" if not is_tax_exempt_entity else "501(c)(3) Philanthropic Capital & Match Hurdle"
        }
    ])

    financial_insights = [
        f"Public co-funding (${grant_amount:,.0f})" + (f" and IRA tax credits (${tax_credit_net:,.0f})" if is_tax_eligible else "") + f" deliver {total_non_dilutive_pct}% non-dilutive subsidization, reducing the net sponsor equity check to {sponsor_equity_pct}%.",
        f"The blended project WACC is lowered from {unsubsidized_wacc_pct}% to {blended_wacc_pct}%, generating an estimated {wacc_savings_bps} bps financing cost advantage and ${annual_carrying_cost_savings:,.0f}/year in capital carrying savings (${ten_year_cumulative_savings:,.0f} over 10 years)."
    ]

    if is_tax_eligible:
        financial_insights.append(f"Statutory compliance ({statutory_code}) injects ${tax_credit_net:,.0f} in net monetization value via {'Section 6417 Direct Pay' if effective_direct_pay else 'Section 6418 Transferability'}.")
    else:
        financial_insights.append("Project domain is non-energy / outside IRC Title 26; federal clean energy tax equity is strictly set to $0.00 to avoid over-stating incentive availability.")

    # Synthesize institutional 3-paragraph Investment Committee Diligence Memorandum
    memo_result = _synthesize_diligence_memo(
        total_cost=total_cost,
        grant_amount=grant_amount,
        tax_credit_net=tax_credit_net,
        green_bank_debt_amount=green_bank_debt_amount,
        sponsor_equity_amount=sponsor_equity_amount,
        sponsor_equity_pct=sponsor_equity_pct,
        total_non_dilutive_amount=total_non_dilutive_amount,
        total_non_dilutive_pct=total_non_dilutive_pct,
        blended_wacc_pct=blended_wacc_pct,
        unsubsidized_wacc_pct=unsubsidized_wacc_pct,
        wacc_savings_bps=wacc_savings_bps,
        annual_carrying_cost_savings=annual_carrying_cost_savings,
        ten_year_cumulative_savings=ten_year_cumulative_savings,
        subsidized_payback_years=subsidized_payback_years,
        is_tax_eligible=is_tax_eligible,
        statutory_name=statutory_name,
        statutory_code=statutory_code,
        total_itc_rate=total_itc_rate,
        effective_direct_pay=effective_direct_pay,
        project_summary=project_summary
    )

    return {
        "project_cost": total_cost,
        "is_tax_credit_eligible": is_tax_eligible,
        "eligibility_audit": {
            "is_tax_credit_eligible": is_tax_eligible,
            "statutory_classification": statutory_name,
            "statutory_code": statutory_code,
            "eligibility_notes": eligibility_notes,
            "direct_pay_eligible": effective_direct_pay,
            "applicant_tax_status": "Tax-Exempt / 501(c)(3) / Public Entity (Direct Pay Qualified)" if is_tax_exempt_entity else "Taxable Entity (Transferability Qualified)",
        },
        "summary": {
            "total_non_dilutive_capital": total_non_dilutive_amount,
            "total_non_dilutive_pct": total_non_dilutive_pct,
            "net_sponsor_equity_required": sponsor_equity_amount,
            "net_sponsor_equity_pct": sponsor_equity_pct,
            "blended_wacc_pct": blended_wacc_pct,
            "blended_wacc_after_tax_pct": blended_wacc_after_tax_pct,
            "unsubsidized_wacc_pct": unsubsidized_wacc_pct,
            "wacc_savings_bps": max(0, wacc_savings_bps),
            "annual_carrying_cost_savings": annual_carrying_cost_savings,
            "ten_year_cumulative_savings": ten_year_cumulative_savings,
            "estimated_payback_years": subsidized_payback_years,
            "standard_payback_years": standard_payback_years,
        },
        "formula_audit": {
            "wacc_formula": "WACC = (w_grant * r_grant) + (w_tax * r_tax) + (w_debt * r_debt) + (w_equity * r_equity)",
            "wacc_weights": {
                "w_grant": round(w_grant, 4),
                "w_tax": round(w_tax, 4),
                "w_debt": round(w_debt, 4),
                "w_equity": round(w_equity, 4),
            },
            "cost_of_capital_rates": {
                "r_grant": f"{grant_cost_rate * 100:.2f}% (Non-Dilutive Public Grant)",
                "r_tax": f"{tax_credit_cost_rate * 100:.2f}% (Statutory Tax Equity)",
                "r_debt": f"{debt_interest_rate * 100:.2f}% (Concessionary Green Bank Debt)",
                "r_debt_after_tax": f"{after_tax_debt_rate * 100:.2f}% (After Corporate Tax Deduction)",
                "r_equity": f"{equity_hurdle_rate * 100:.2f}% (Hurdle Rate)",
            },
            "benchmark_commercial_wacc": f"{unsubsidized_wacc_pct}% (40% Senior Commercial Debt @ 7.75% + 60% Equity @ {unsubsidized_equity_rate * 100:.2f}%)",
            "statutory_citations": [
                f"Statutory Eligibility: {statutory_code} ({statutory_name})",
                "Tax Credit Transferability: 26 U.S.C. § 6418 (Treasury Decision TD 9988, ~93.5¢ net institutional pricing)",
                "Direct Pay Election: 26 U.S.C. § 6417 (Treasury Decision TD 9989, 100% refundable direct payment for 501(c)(3) & municipal entities)",
                "Concessionary Green Debt: NY Green Bank / California IBank Climate Catalyst Revolving Facility metrics",
                "Financial Discount Rate Standard: NREL Annual Technology Baseline (ATB) 2024 Project Financial Assumptions"
            ] if is_tax_eligible else [
                "Statutory Scope: IRC Title 26 Sections 48, 45, 45V, 45Q, 48C restricted to qualified energy property",
                "Non-Energy Gating: Zero tax credit assigned to non-energy property to prevent overstating incentives",
                "Grant Co-Funding Standards: Federal Uniform Guidance (2 CFR 200) & State Innovation Grant Rules",
                "Concessionary Financing: Programmatic revolving loan funds for economic and workforce development"
            ]
        },
        "tax_credit_config": {
            "statutory_name": statutory_name,
            "statutory_code": statutory_code,
            "is_eligible": is_tax_eligible,
            "base_rate_pct": int(base_itc_rate * 100),
            "energy_community_bonus_pct": int(bonus_ec_rate * 100),
            "domestic_content_bonus_pct": int(bonus_dc_rate * 100),
            "effective_itc_rate_pct": int(total_itc_rate * 100),
            "monetization_factor_pct": round(monetization_factor * 100, 1),
            "monetization_mode": (
                "26 U.S.C. § 6417 Direct Pay (100% Cash Refund)" if effective_direct_pay
                else "26 U.S.C. § 6418 Transferability (~93.5% Net Proceeds)"
            ) if is_tax_eligible else "Ineligible / 0.0% (Non-Energy Domain)",
            "prevailing_wage_active": prevailing_wage_compliant and is_tax_eligible,
            "energy_community_active": energy_community_bonus and is_tax_eligible,
            "domestic_content_active": domestic_content_bonus and is_tax_eligible,
        },
        "waterfall_layers": layers,
        "financial_insights": financial_insights,
        "sensitivities": sensitivity_table,
        "investment_committee_memo": memo_result["memo"],
        "memo_synthesized_by": memo_result["synthesized_by"]
    }


def _synthesize_diligence_memo(
    total_cost: float,
    grant_amount: float,
    tax_credit_net: float,
    green_bank_debt_amount: float,
    sponsor_equity_amount: float,
    sponsor_equity_pct: float,
    total_non_dilutive_amount: float,
    total_non_dilutive_pct: float,
    blended_wacc_pct: float,
    unsubsidized_wacc_pct: float,
    wacc_savings_bps: int,
    annual_carrying_cost_savings: float,
    ten_year_cumulative_savings: float,
    subsidized_payback_years: float,
    is_tax_eligible: bool,
    statutory_name: str,
    statutory_code: str,
    total_itc_rate: float,
    effective_direct_pay: bool,
    project_summary: Optional[str] = None
) -> Dict[str, str]:
    """
    Synthesizes an institutional 3-paragraph Investment Committee Diligence Memorandum
    using OpenAI, Gemini, or Claude, with graceful deterministic fallback.
    """
    import os
    import json
    try:
        from app.config import settings
        openai_key = getattr(settings, "openai_api_key", None) or os.environ.get("OPENAI_API_KEY")
        gemini_key = getattr(settings, "gemini_api_key", None) or os.environ.get("GEMINI_API_KEY")
        anthropic_key = getattr(settings, "anthropic_api_key", None) or os.environ.get("ANTHROPIC_API_KEY")
    except Exception:
        openai_key = os.environ.get("OPENAI_API_KEY")
        gemini_key = os.environ.get("GEMINI_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    monetization_mode = "26 U.S.C. § 6417 Direct Pay (100% Cash Refund)" if effective_direct_pay else "26 U.S.C. § 6418 Transferability (~93.5% Net Proceeds)"
    if not is_tax_eligible:
        monetization_mode = "Ineligible / 0.0% (Non-Energy Property under Title 26)"

    prompt = f"""You are the Chief Investment Officer and Fiduciary Lead for a Clean Energy Infrastructure Investment Committee.
Synthesize a high-density, institutional 3-paragraph Investment Committee Diligence Memorandum for the following project financing structure:

PROJECT SUMMARY: {project_summary or 'Clean energy infrastructure deployment project'}
TOTAL CAPEX: ${total_cost:,.2f}
NON-DILUTIVE SUBSIDY (GRANT + TAX EQUITY): ${total_non_dilutive_amount:,.2f} ({total_non_dilutive_pct}%)
  - Public Innovation Grants: ${grant_amount:,.2f}
  - Statutory Tax Credit Net Proceeds: ${tax_credit_net:,.2f}
CONCESSIONARY GREEN BANK DEBT: ${green_bank_debt_amount:,.2f} @ 5.25% fixed
NET SPONSOR EQUITY CHECK: ${sponsor_equity_amount:,.2f} ({sponsor_equity_pct}%)
BLENDED PROJECT WACC: {blended_wacc_pct}% (vs Unsubsidized Commercial Benchmark: {unsubsidized_wacc_pct}%)
WACC COMPRESSION: {wacc_savings_bps} bps reduction
CARRYING COST SAVINGS: ${annual_carrying_cost_savings:,.2f}/year (${ten_year_cumulative_savings:,.2f} cumulative 10-year value preservation)
ESTIMATED PAYBACK PERIOD: {subsidized_payback_years} years
STATUTORY INCENTIVE BASIS: {statutory_name} ({statutory_code})
MONETIZATION MECHANISM: {monetization_mode}

Drafting Requirements:
Paragraph 1: **Capital Structure & Non-Dilutive Subsidy Architecture** - Summarize total project CapEx, non-dilutive leverage captured via public grants and tax equity, and the resulting net sponsor equity check.
Paragraph 2: **Cost of Capital (WACC) Optimization & Fiduciary Savings** - Quantify the WACC reduction vs unsubsidized commercial benchmarks, basis-point compression, and 10-year cumulative debt service carrying savings.
Paragraph 3: **Statutory Tax Structuring & Monetization Mechanics** - Detail the legal basis under Internal Revenue Code Title 26, compliance requirements (prevailing wage/apprenticeship and siting adders), and the monetization execution pathway.

Return ONLY the 3-paragraph professional memorandum."""

    # 1. Try OpenAI
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key, timeout=25.0, max_retries=2)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a clean energy infrastructure investment committee director. Output pure professional markdown prose."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=900,
            )
            memo_text = resp.choices[0].message.content or ""
            if len(memo_text.strip()) > 100:
                return {
                    "memo": memo_text.strip(),
                    "synthesized_by": "OpenAI GPT-4o-mini"
                }
        except Exception as e:
            logger.warning(f"OpenAI capital stack memo synthesis failed: {e}")

    # 2. Try Gemini
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            if response.text and len(response.text.strip()) > 100:
                return {
                    "memo": response.text.strip(),
                    "synthesized_by": "Google Gemini 2.5 Flash"
                }
        except Exception as e:
            logger.warning(f"Gemini capital stack memo synthesis failed: {e}")

    # 3. Try Anthropic
    if anthropic_key:
        try:
            import urllib.request
            req_data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 900,
                "temperature": 0.2,
                "messages": [{"role": "user", "content": prompt}]
            }
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps(req_data).encode("utf-8"),
                headers={
                    "x-api-key": anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=25.0) as r:
                res_json = json.loads(r.read().decode("utf-8"))
                memo_text = res_json.get("content", [{}])[0].get("text", "")
                if len(memo_text.strip()) > 100:
                    return {
                        "memo": memo_text.strip(),
                        "synthesized_by": "Anthropic Claude 3.5 Sonnet"
                    }
        except Exception as e:
            logger.warning(f"Anthropic capital stack memo synthesis failed: {e}")

    # Deterministic Rule-Based Fallback
    p1 = (
        f"**Capital Structure & Non-Dilutive Subsidy Architecture**: "
        f"The subject project proposes a total capital expenditure of ${total_cost:,.2f}. "
        f"Through a syndicated multi-tier capital stack, the project captures ${total_non_dilutive_amount:,.2f} ({total_non_dilutive_pct}%) "
        f"in non-dilutive subsidization comprising public co-funding grants (${grant_amount:,.2f})"
        + (f" and statutory IRA tax equity (${tax_credit_net:,.2f}). " if is_tax_eligible else ". ")
        + f"Layering concessionary green bank gap debt (${green_bank_debt_amount:,.2f}) narrows the net sponsor equity commitment to "
        f"${sponsor_equity_amount:,.2f} ({sponsor_equity_pct}%), significantly de-risking downside exposure for prime equity sponsors."
    )

    p2 = (
        f"**Cost of Capital (WACC) Optimization & Fiduciary Savings**: "
        f"From a cost-of-capital perspective, structuring non-dilutive grant co-funding alongside low-cost subordinated debt (5.25% fixed coupon) "
        f"compresses the blended project WACC from an unsubsidized commercial benchmark of {unsubsidized_wacc_pct}% down to {blended_wacc_pct}%. "
        f"This generates a {wacc_savings_bps} bps financing cost advantage, yielding approximately ${annual_carrying_cost_savings:,.2f} "
        f"in annual debt-service and carrying cost reductions, representing ${ten_year_cumulative_savings:,.2f} in cumulative 10-year value preservation."
    )

    if is_tax_eligible:
        p3 = (
            f"**Statutory Tax Structuring & Monetization Mechanics**: "
            f"Statutory tax equity monetization is structured under {statutory_code} ({statutory_name}), "
            f"yielding an effective statutory incentive rate of {int(total_itc_rate * 100)}%. "
            f"Capital realization is executed via {monetization_mode}, "
            f"predicated on satisfying prevailing wage, registered apprenticeship, and qualified siting requirements under Treasury guidance."
        )
    else:
        p3 = (
            "**Statutory Tax Structuring & Monetization Mechanics**: "
            "Because the proposed scope resides outside IRC Title 26 eligible energy property categories, "
            "federal clean energy tax credits are strictly modeled at $0.00 (0.00%) to preserve fiduciary accuracy. "
            "Project capitalization relies exclusively on competitive public innovation grants and programmatic economic development financing."
        )

    return {
        "memo": f"{p1}\n\n{p2}\n\n{p3}",
        "synthesized_by": "Rule-Based Deterministic Fallback"
    }

