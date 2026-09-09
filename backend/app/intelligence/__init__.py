"""
Canonical Intelligence Layer for Energy Innovation Terminal.

Centralizes all proprietary scoring algorithms, policy compliance solvers,
bankability ratings, predictive win rates, consortia teaming engines,
and grounded agent tools.
"""

from app.intelligence.opportunity_fit import (
    score_opportunity_fit,
    rank_opportunities_for_profile,
    create_project_profile,
)
from app.intelligence.capital_stack import (
    solve_capital_stack,
    calculate_ira_direct_pay_incentive,
    get_supported_technologies,
)
from app.intelligence.bankability import (
    evaluate_technology_bankability,
    get_bankability_rubric_weights,
)
from app.intelligence.win_rate import (
    evaluate_win_rate,
    get_agency_competition_benchmark,
)
from app.intelligence.teaming import (
    assemble_consortium_stack,
)
from app.intelligence.forecasting import (
    forecast_upcoming_solicitations,
    match_profile_forecasts,
    generate_organization_forecast_briefing,
    get_funding_organization_directory,
)
from app.intelligence.propensity import (
    rank_funder_propensity,
    get_aligned_organization_codes,
    get_organization_pain_points_catalog,
)
from app.intelligence.reviewer_rubric import (
    generate_reviewer_rubric,
)
from app.intelligence.agent_tools import (
    get_agent_tools_manifest,
    execute_agent_tool,
    search_opportunities_tool,
    get_opportunity_details_tool,
    get_organization_profile_tool,
    rank_opportunities_tool,
    analyze_funding_history_tool,
    solve_capital_stack_tool,
    evaluate_technology_bankability_tool,
    assemble_teaming_consortia_tool,
    generate_strategic_plan_tool,
)

__all__ = [
    # Fit & Scoring
    "score_opportunity_fit",
    "rank_opportunities_for_profile",
    "create_project_profile",
    # Capital Stack
    "solve_capital_stack",
    "calculate_ira_direct_pay_incentive",
    "get_supported_technologies",
    # Bankability
    "evaluate_technology_bankability",
    "get_bankability_rubric_weights",
    # Win Rate
    "evaluate_win_rate",
    "get_agency_competition_benchmark",
    # Teaming
    "assemble_consortium_stack",
    # Forecasting
    "forecast_upcoming_solicitations",
    "match_profile_forecasts",
    "generate_organization_forecast_briefing",
    "get_funding_organization_directory",
    # Propensity
    "rank_funder_propensity",
    "get_aligned_organization_codes",
    "get_organization_pain_points_catalog",
    # Rubric
    "generate_reviewer_rubric",
    # Agent Tools
    "get_agent_tools_manifest",
    "execute_agent_tool",
    "search_opportunities_tool",
    "get_opportunity_details_tool",
    "get_organization_profile_tool",
    "rank_opportunities_tool",
    "analyze_funding_history_tool",
    "solve_capital_stack_tool",
    "evaluate_technology_bankability_tool",
    "assemble_teaming_consortia_tool",
    "generate_strategic_plan_tool",
]
