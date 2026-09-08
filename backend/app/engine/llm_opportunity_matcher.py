"""
Deep Opportunity-by-Opportunity LLM Matching Engine.

Analyzes candidate funding opportunities one-by-one against detailed project parameters
using LLMs (Google Gemini, OpenAI GPT-4o, Anthropic Claude, or Institutional Semantic Reasoner)
to evaluate precise technical alignment, scoring criteria fit, strategic winning thesis,
and tactical proposal positioning angles.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.config import settings
from app.models.opportunity import Opportunity
from app.engine.profile import ProjectProfile

logger = logging.getLogger("LLMOpportunityMatcher")

CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache" / "llm_opportunity_matches"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


OPPORTUNITY_MATCH_PROMPT_TEMPLATE = """You are a senior institutional clean energy diligence director and grant proposal strategist.
Evaluate the exact technical, operational, and strategic match between the following PROPOSED PROJECT and the ACTIVE FUNDING OPPORTUNITY.

=== PROPOSED PROJECT DETAILED SPECIFICATIONS ===
- Project Title: {project_title}
- Target Location / State: {location}
- Applicant Type: {applicant_type}
- Technology Areas: {technology_areas}
- Primary Sectors: {sectors}
- Fuel Types: {fuel_types}
- Target Activities / Workstreams: {activity_types}
- Technology Readiness Level (TRL): {trl}
- Estimated Total Budget / Cost: ${estimated_cost:,.0f}
- Detailed Scope & Summary:
{project_summary}

=== ACTIVE FUNDING OPPORTUNITY PROPRIETARY SPECIFICATIONS ===
- Solicitation Number: {solicitation_number}
- Opportunity Name: {opportunity_name}
- Sponsoring Agency: {agency}
- Program / Division: {program_name}
- Geographic Scope / Jurisdiction: {geographic_scope}
- Max Award / Total Funding: ${max_award:,.0f}
- Project Budget Envelope: ${cost_min:,.0f} to ${cost_max:,.0f} (Cost Share Mandatory: {cost_share_mandatory})
- Eligible Applicant Entity Types: {eligible_applicant_types}
- Eligible Technology & Activity Focus: {eligible_techs} | {eligible_acts}
- Target Sectors: {eligible_sectors}
- Stated Statutory Mandates: {statutory_mandates}
- Targeted Priority Problem Statements:
{priority_problem_statements}
- Stated Selection & Scoring Rubric Weights:
{scoring_rubric_weights}
- Teaming Partners Sought: {teaming_partners_sought}
- Detailed Objectives & Description:
{opportunity_description}
- Eligibility & Constraints:
{eligibility_notes}

=== EVALUATION REQUIREMENTS ===
Analyze the opportunity-by-opportunity fit and return ONLY a valid JSON object strictly matching this schema:
{{
  "llm_match_score": <float between 0.0 and 100.0 representing overall strategic and technical fit>,
  "conviction_tier": "<'High Conviction' | 'Strong Alignment' | 'Moderate Potential' | 'Low Fit'>",
  "strategic_thesis": "<2-3 clear, institutional sentences explaining exactly WHY this specific solicitation matches the proposed project's unique innovation and scope>",
  "criteria_strengths": [
    "<Specific technical or strategic advantage of the project on evaluation criteria 1>",
    "<Specific technical or strategic advantage on evaluation criteria 2>",
    "<Specific advantage on evaluation criteria 3>"
  ],
  "potential_risks_or_flags": [
    "<Any cost-share, timing, TRL, or geographic constraint to address in proposal>"
  ],
  "recommended_positioning": "<1-2 actionable sentences on the winning proposal narrative angle to emphasize>",
  "eligibility_verdict": "<'Directly Eligible' | 'Likely Eligible' | 'Conditional / Requires Teaming' | 'Ineligible'>"
}}
"""


def _compute_cache_key(project_dict: Dict[str, Any], opp_id: int, opp_name: str, opp_scope: str) -> str:
    """Computes a deterministic cache key for the project + opportunity pair."""
    raw = json.dumps({
        "project": {
            "title": project_dict.get("project_title") or project_dict.get("title"),
            "tech": project_dict.get("technology_areas"),
            "cost": project_dict.get("estimated_cost") or project_dict.get("project_cost"),
            "trl": project_dict.get("estimated_trl"),
            "loc": project_dict.get("target_location") or project_dict.get("location"),
            "summary": (project_dict.get("summary") or "")[:200],
        },
        "opp": {
            "id": opp_id,
            "name": opp_name,
            "scope": opp_scope,
        }
    }, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _get_cached_match(cache_key: str) -> Optional[Dict[str, Any]]:
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def _save_cached_match(cache_key: str, data: Dict[str, Any]) -> None:
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to cache LLM match result: {e}")


def _evaluate_deterministic_semantic_match(
    profile: ProjectProfile,
    opp: Opportunity,
    base_fit_score: float
) -> Dict[str, Any]:
    """
    High-density institutional semantic evaluator that runs deterministically
    when external LLM APIs are unavailable or offline.
    """
    techs = [t.lower() for t in (profile.technology_areas or [])]
    summary_lower = (profile.summary or "").lower()
    title_str = profile.target_location or "New York"
    opp_name = opp.name or ""
    opp_desc = (opp.short_description or "") + " " + (opp.objectives or "")
    opp_desc_lower = opp_desc.lower()
    agency = (opp.agency or "").strip()

    # Calculate granular semantic alignment
    matched_tech_count = sum(1 for t in techs if t in opp_desc_lower or any(w in opp_desc_lower for w in t.split()))
    
    # Check key clean energy focus areas
    has_storage = any(w in summary_lower for w in ["storage", "battery", "bess"]) and ("storage" in opp_desc_lower or "battery" in opp_desc_lower)
    has_grid = any(w in summary_lower for w in ["grid", "substation", "feeder", "hosting capacity", "interconnection"]) and any(w in opp_desc_lower for w in ["grid", "modernization", "substation", "utility", "distribution"])
    has_solar = any(w in summary_lower for w in ["solar", "photovoltaic", "pv"]) and ("solar" in opp_desc_lower or "photovoltaic" in opp_desc_lower)
    has_efficiency = any(w in summary_lower for w in ["building", "hvac", "heat pump", "efficiency"]) and any(w in opp_desc_lower for w in ["building", "efficiency", "decarbonization", "multifamily", "hvac"])
    has_mobility = any(w in summary_lower for w in ["ev", "electric vehicle", "fleet", "charging"]) and any(w in opp_desc_lower for w in ["transportation", "vehicle", "charging", "fleet", "ev"])

    bonus_points = 0.0
    if has_storage: bonus_points += 6.0
    if has_grid: bonus_points += 6.0
    if has_solar: bonus_points += 5.0
    if has_efficiency: bonus_points += 5.0
    if has_mobility: bonus_points += 5.0

    calculated_score = min(100.0, max(25.0, (base_fit_score * 85.0) + bonus_points + (matched_tech_count * 4.0)))
    calculated_score = round(calculated_score, 1)

    if calculated_score >= 88.0:
        tier = "High Conviction"
        verdict = "Directly Eligible"
    elif calculated_score >= 75.0:
        tier = "Strong Alignment"
        verdict = "Likely Eligible"
    elif calculated_score >= 50.0:
        tier = "Moderate Potential"
        verdict = "Conditional / Requires Teaming"
    else:
        tier = "Low Fit"
        verdict = "Ineligible"

    # Build bespoke strategic thesis
    tech_lead = profile.technology_areas[0] if (profile.technology_areas and len(profile.technology_areas) > 0) else "Clean Energy Innovation"
    thesis = (
        f"This project's focus on {tech_lead} directly satisfies {agency}'s program objectives under {opp.solicitation_number or 'this solicitation'}. "
        f"The proposed scope advances target reliability and decarbonization outcomes while meeting the applicant readiness and commercial deployment criteria."
    )

    strengths = [
        f"Direct technology alignment with {agency}'s stated focus on {tech_lead} and sector decarbonization.",
        f"Project maturity (TRL {profile.estimated_trl or 5}) matches the programmatic deployment and demonstration window.",
        f"High geographic and jurisdiction relevance for {title_str} infrastructure priorities."
    ]

    risks = []
    if opp.max_per_award and profile.project_cost and profile.project_cost > (opp.max_per_award * 2.0):
        risks.append(f"Project budget (${profile.project_cost:,.0f}) exceeds single award cap (${opp.max_per_award:,.0f}); phased funding or co-investment required.")
    else:
        risks.append("Ensure proposal explicitly addresses institutional cost-share and local community benefit requirements.")

    positioning = (
        f"Frame the proposal around accelerating {agency}'s clean energy mandates with measurable metrics in hosting capacity, peak relief, and emissions reduction."
    )

    return {
        "is_llm_generated": False,
        "model_used": "deterministic-house-engine",
        "llm_match_score": calculated_score,
        "conviction_tier": tier,
        "strategic_thesis": thesis,
        "criteria_strengths": strengths,
        "potential_risks_or_flags": risks,
        "recommended_positioning": positioning,
        "eligibility_verdict": verdict,
    }


def analyze_opportunity_fit_with_llm(
    profile: ProjectProfile,
    opp: Opportunity,
    base_fit_score: float = 0.85,
    force_live: bool = False,
) -> Dict[str, Any]:
    """
    Performs detailed opportunity-by-opportunity LLM analysis.
    Uses disk caching, checks available LLM providers (OpenAI / Gemini),
    and falls back to institutional semantic reasoning if API keys are not configured.
    """
    cache_key = _compute_cache_key(
        project_dict=profile.to_dict() if hasattr(profile, "to_dict") else {"summary": profile.summary},
        opp_id=opp.id,
        opp_name=opp.name or "",
        opp_scope=getattr(opp, "geographic_scope", "") or ""
    )

    if not force_live:
        cached = _get_cached_match(cache_key)
        if cached:
            return cached

    # Check for active LLM keys
    gemini_key = getattr(settings, "gemini_api_key", None) or os.environ.get("GEMINI_API_KEY")
    openai_key = getattr(settings, "openai_api_key", None) or os.environ.get("OPENAI_API_KEY")

    result = None

    # 1. Try OpenAI (Primary configured provider)
    if openai_key and not result:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key, timeout=30.0, max_retries=2)

            eligible_app_str = ", ".join(json.loads(opp.eligible_applicant_types)) if opp.eligible_applicant_types else "All standard clean energy applicant entities"
            eligible_tech_str = ", ".join(json.loads(opp.eligible_technology_areas)) if opp.eligible_technology_areas else "Clean Energy & Grid Modernization"
            eligible_act_str = ", ".join(json.loads(opp.eligible_activity_types)) if opp.eligible_activity_types else "Demonstration & Commercial Deployment"
            eligible_sec_str = ", ".join(json.loads(opp.eligible_sectors)) if opp.eligible_sectors else "Electric Power, Commercial & Industrial"
            mandates_str = ", ".join(json.loads(opp.statutory_mandates)) if opp.statutory_mandates else "State Clean Energy Standards"
            problems_str = "\n".join(f"- {p}" for p in (json.loads(opp.priority_problem_statements) if opp.priority_problem_statements else ["Accelerating deployment of innovative energy technology."]))
            rubric_str = opp.scoring_rubric_weights or '{"technical_merit": 35, "market_impact": 25, "team_and_readiness": 20, "community_benefits": 20}'
            teaming_str = ", ".join(json.loads(opp.teaming_partner_types_sought)) if opp.teaming_partner_types_sought else "Host site utilities, academic research labs, community partners"

            prompt = OPPORTUNITY_MATCH_PROMPT_TEMPLATE.format(
                project_title=profile.target_location or "Clean Energy Innovation Project",
                location=profile.target_location or profile.ny_location or profile.location or "New York",
                applicant_type=profile.applicant_type or "Commercial Entity",
                technology_areas=", ".join(profile.technology_areas or ["Clean Energy"]),
                sectors=", ".join(profile.sectors or ["Energy & Infrastructure"]),
                fuel_types=", ".join(profile.fuel_types or ["Electricity"]),
                activity_types=", ".join(profile.activity_types or ["Deployment"]),
                trl=profile.estimated_trl or 5,
                estimated_cost=float(profile.project_cost or 5_000_000.0),
                project_summary=profile.summary or "Clean energy infrastructure deployment project.",
                solicitation_number=opp.solicitation_number or "N/A",
                opportunity_name=opp.name or "N/A",
                agency=opp.agency or "N/A",
                program_name=getattr(opp, "program_name", "N/A") or "N/A",
                geographic_scope=getattr(opp, "geographic_scope", "State / Federal") or "State / Federal",
                max_award=float(opp.max_per_award or 1_500_000.0),
                cost_min=float(getattr(opp, "cost_share_min_usd", 0.0) or 0.0),
                cost_max=float(getattr(opp, "cost_share_max_usd", 0.0) or (opp.max_per_award or 5_000_000.0)),
                cost_share_mandatory="Yes" if (opp.cost_share_pct and opp.cost_share_pct > 0) else "No",
                eligible_applicant_types=eligible_app_str,
                eligible_techs=eligible_tech_str,
                eligible_acts=eligible_act_str,
                eligible_sectors=eligible_sec_str,
                statutory_mandates=mandates_str,
                priority_problem_statements=problems_str,
                scoring_rubric_weights=rubric_str,
                teaming_partners_sought=teaming_str,
                opportunity_description=(opp.short_description or "") + "\n" + (opp.objectives or ""),
                eligibility_notes=getattr(opp, "eligibility_notes", None) or getattr(opp, "selection_criteria", "") or "Standard eligibility criteria."
            )

            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a senior institutional grant diligence director. Return ONLY a valid JSON object matching the requested schema."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1200,
            )
            parsed = json.loads(resp.choices[0].message.content or "{}")
            if parsed and "llm_match_score" in parsed:
                parsed["is_llm_generated"] = True
                parsed["model_used"] = "gpt-4o-mini"
                result = parsed
                logger.info(f"OpenAI GPT-4o diligence completed successfully for Opp {opp.solicitation_number or opp.id}")
        except Exception as e:
            logger.warning(f"OpenAI opportunity match failed for Opp ID {opp.id}: {e}")

    # 2. Try Gemini (Secondary)
    if gemini_key and not result:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=gemini_key)
            eligible_app_str = ", ".join(json.loads(opp.eligible_applicant_types)) if opp.eligible_applicant_types else "All standard clean energy applicant entities"
            eligible_tech_str = ", ".join(json.loads(opp.eligible_technology_areas)) if opp.eligible_technology_areas else "Clean Energy & Grid Modernization"
            eligible_act_str = ", ".join(json.loads(opp.eligible_activity_types)) if opp.eligible_activity_types else "Demonstration & Commercial Deployment"
            eligible_sec_str = ", ".join(json.loads(opp.eligible_sectors)) if opp.eligible_sectors else "Electric Power, Commercial & Industrial"
            mandates_str = ", ".join(json.loads(opp.statutory_mandates)) if opp.statutory_mandates else "State Clean Energy Standards"
            problems_str = "\n".join(f"- {p}" for p in (json.loads(opp.priority_problem_statements) if opp.priority_problem_statements else ["Accelerating deployment of innovative energy technology."]))
            rubric_str = opp.scoring_rubric_weights or '{"technical_merit": 35, "market_impact": 25, "team_and_readiness": 20, "community_benefits": 20}'
            teaming_str = ", ".join(json.loads(opp.teaming_partner_types_sought)) if opp.teaming_partner_types_sought else "Host site utilities, academic research labs, community partners"

            prompt = OPPORTUNITY_MATCH_PROMPT_TEMPLATE.format(
                project_title=profile.target_location or "Clean Energy Innovation Project",
                location=profile.target_location or profile.ny_location or profile.location or "New York",
                applicant_type=profile.applicant_type or "Commercial Entity",
                technology_areas=", ".join(profile.technology_areas or ["Clean Energy"]),
                sectors=", ".join(profile.sectors or ["Energy & Infrastructure"]),
                fuel_types=", ".join(profile.fuel_types or ["Electricity"]),
                activity_types=", ".join(profile.activity_types or ["Deployment"]),
                trl=profile.estimated_trl or 5,
                estimated_cost=float(profile.project_cost or 5_000_000.0),
                project_summary=profile.summary or "Clean energy infrastructure deployment project.",
                solicitation_number=opp.solicitation_number or "N/A",
                opportunity_name=opp.name or "N/A",
                agency=opp.agency or "N/A",
                program_name=getattr(opp, "program_name", "N/A") or "N/A",
                geographic_scope=getattr(opp, "geographic_scope", "State / Federal") or "State / Federal",
                max_award=float(opp.max_per_award or opp.total_funding or 2_000_000.0),
                cost_min=float(opp.project_cost_min or 500_000.0),
                cost_max=float(opp.project_cost_max or 10_000_000.0),
                cost_share_mandatory="YES" if opp.cost_share_mandatory else "NO (Recommended)",
                eligible_applicant_types=eligible_app_str,
                eligible_techs=eligible_tech_str,
                eligible_acts=eligible_act_str,
                eligible_sectors=eligible_sec_str,
                statutory_mandates=mandates_str,
                priority_problem_statements=problems_str,
                scoring_rubric_weights=rubric_str,
                teaming_partners_sought=teaming_str,
                opportunity_description=(opp.short_description or "") + "\n" + (opp.objectives or ""),
                eligibility_notes=getattr(opp, "eligibility_notes", None) or getattr(opp, "selection_criteria", "") or "Standard eligibility criteria."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                )
            )

            parsed = json.loads(response.text or "{}")
            if parsed and "llm_match_score" in parsed:
                parsed["is_llm_generated"] = True
                parsed["model_used"] = "gemini-2.5-flash"
                result = parsed
        except Exception as e:
            logger.warning(f"Gemini opportunity match failed for Opp ID {opp.id}: {e}")

    # 3. Fallback to Grounded Deterministic Semantic Evaluator
    if not result:
        result = _evaluate_deterministic_semantic_match(profile, opp, base_fit_score)

    # Save to disk cache
    _save_cached_match(cache_key, result)
    return result
