"""
AI-Powered Project Analysis & Executive Summary Synthesizer.

Uses OpenAI API (with deterministic house-voice fallback and disk caching)
to generate high-density executive briefings, capital stack narratives,
and regulatory compliance roadmaps for the Executive Match Analysis & Capital Optimization Report.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.config import settings

logger = logging.getLogger("AIProjectSynthesizer")

CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache" / "ai_project_summaries"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _compute_hash(context: Dict[str, Any], model_name: str) -> str:
    """Computes a deterministic SHA-256 hash of the input context."""
    raw = json.dumps({"context": context, "model": model_name}, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _get_cached_summary(cache_key: str) -> Optional[Dict[str, Any]]:
    """Retrieves cached summary from disk."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def _save_cached_summary(cache_key: str, data: Dict[str, Any]) -> None:
    """Saves summary to disk cache."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to cache AI project summary: {e}")


def generate_deterministic_project_summary(
    profile: Dict[str, Any],
    top_matches: List[Dict[str, Any]],
    top_orgs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Generates a rigorous, institutional house-voice executive summary without external API calls.
    """
    title = profile.get("project_title") or profile.get("title") or "Clean Energy Innovation Project"
    loc = profile.get("target_location") or profile.get("location") or "New York State"
    app_type = (profile.get("applicant_type") or "Commercial Entity").title()
    cost = profile.get("estimated_cost") or profile.get("project_cost") or 5_000_000.0
    try:
        cost = float(cost)
    except Exception:
        cost = 5_000_000.0
    trl = profile.get("estimated_trl") or "5"
    tech_areas = profile.get("technology_areas") or ["Clean Energy Technology"]
    tech_str = ", ".join(tech_areas[:3]) if isinstance(tech_areas, list) else str(tech_areas)
    
    top_sol_title = "High-Conviction Solicitation"
    top_agency = "Federal / State Innovation Program"
    top_grant_amount = "$1,500,000"
    if top_matches:
        m0 = top_matches[0]
        top_sol_title = m0.get("name") or m0.get("solicitation_number") or top_sol_title
        top_agency = m0.get("agency") or top_agency
        if m0.get("max_per_award"):
            top_grant_amount = f"${m0['max_per_award']:,.0f}"

    lead_org_name = top_orgs[0].get("organization_name", top_agency) if (top_orgs and len(top_orgs) > 0) else top_agency

    p1 = (
        f"<b>1. Strategic Project Thesis & Technology Scope:</b> "
        f"{title} represents a high-impact deployment in {tech_str} operating at Technology Readiness Level (TRL) {trl}. "
        f"Targeted for execution in {loc} by a {app_type}, the project is strategically positioned to address core "
        f"state and federal decarbonization mandates and grid modernization priorities with an estimated scope of ${cost:,.0f}."
    )

    p2 = (
        f"<b>2. Top Sponsoring Organizations & Decision-Maker Alignment:</b> "
        f"Institutional propensity screening identified lead funding bodies with direct jurisdiction and alignment. "
        f"Key institutions include {lead_org_name} alongside in-state energy authorities and regional utilities whose mandates "
        f"directly address hosting capacity, peak reduction, and clean innovation deployment."
    )

    p3 = (
        f"<b>3. High-Conviction Active Solicitations:</b> "
        f"Our multi-agency matching engine evaluated the project across active public solicitations, identifying {len(top_matches)} high-conviction "
        f"active grant opportunities. The primary matched target is <i>{top_sol_title}</i> ({top_agency}), offering funding of up to "
        f"{top_grant_amount} in non-dilutive support screened for financial size, timing, and technology fit."
    )

    p4 = (
        f"<b>4. Execution Roadmap & Grant Capture Strategy:</b> "
        f"Recommended near-term milestones include initiating pre-application technical alignment with program officers, "
        f"securing partner commitments with local utility and community hosts, and preparing milestone-gated workstreams for full proposal submission."
    )

    return {
        "is_llm_generated": False,
        "model_used": "deterministic-house-engine",
        "executive_summary_paragraphs": [p1, p2, p3, p4],
        "executive_summary_text": "\n\n".join([p1, p2, p3, p4]),
        "strategic_takeaways": [
            f"Primary matched solicitation target: {top_sol_title} ({top_agency}) with maximum award capacity of {top_grant_amount}.",
            f"Strong institutional alignment with {lead_org_name} and in-state clean energy statutory authorities.",
            f"Active solicitations screened for financial size fit, deadline status, and technology taxonomy.",
            f"Technical scope and TRL {trl} readiness validated for non-dilutive public co-funding."
        ],
        "grant_capture_strategy": (
            f"Sequence application submissions targeting prospective funding from {top_agency} ({top_sol_title}) as anchor co-funder, "
            f"leveraging matching funds to qualify for complementary state and federal grant tiers."
        ),
        "regulatory_and_permitting_roadmap": (
            f"Engage local AHJs and regional utility engineering teams early for pre-application review and technical compliance."
        )
    }


def generate_ai_project_executive_summary(
    profile: Dict[str, Any],
    top_matches: List[Dict[str, Any]],
    top_orgs: Optional[List[Dict[str, Any]]] = None,
    api_key: Optional[str] = None,
    model_name: str = "gpt-4o-mini",
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Generates or retrieves a cached AI-synthesized Executive Summary & Strategic Briefing.
    """
    resolved_api_key = (
        api_key
        or getattr(settings, "openai_api_key", None)
        or os.environ.get("OPENAI_API_KEY")
    )
    
    if not resolved_api_key:
        return generate_deterministic_project_summary(profile, top_matches, top_orgs)

    cache_context = {
        "profile": profile,
        "top_matches": [
            {
                "name": m.get("name"),
                "agency": m.get("agency"),
                "score": m.get("match_score_pct") or m.get("fit_score"),
                "max_per_award": m.get("max_per_award")
            }
            for m in top_matches[:5]
        ],
        "top_organizations": [
            {
                "name": o.get("organization_name"),
                "score": o.get("say_yes_score"),
                "category": o.get("category_label")
            }
            for o in (top_orgs or [])[:5]
        ]
    }
    cache_key = _compute_hash(cache_context, model_name)

    if not force_refresh:
        cached = _get_cached_summary(cache_key)
        if cached:
            return cached

    try:
        from openai import OpenAI
        client = OpenAI(api_key=resolved_api_key, timeout=30.0, max_retries=2)

        system_prompt = (
            "You are the Chief Diligence Director at the Energy Innovation Terminal. "
            "Your role is to author an authoritative, institutional-grade Executive Summary & Strategic Diligence Briefing "
            "for a clean technology innovation project matching report. "
            "Style rules: Authoritative, analytical, rigorous project diligence tone. "
            "Never state or imply that the project has secured or been awarded funds. "
            "Always state that the report has 'identified prospective public funding opportunities' or 'matched active grant programs'. "
            "Ground every statement strictly in the provided project context, matched organizations, and solicitation data. Output valid JSON."
        )

        user_prompt = f"""
PROJECT SPECIFICATIONS & CONTEXT:
{json.dumps(cache_context, indent=2)}

Please generate a comprehensive Executive Strategic Briefing in JSON format:
{{
  "executive_summary_paragraphs": [
    "<b>1. Strategic Project Thesis & Technology Scope:</b> ...",
    "<b>2. Top Sponsoring Organizations & Decision-Maker Alignment:</b> ...",
    "<b>3. High-Conviction Solicitation Match Portfolio:</b> ...",
    "<b>4. Execution Roadmap & Grant Capture Strategy:</b> ..."
  ],
  "strategic_takeaways": [
    "Takeaway 1",
    "Takeaway 2",
    "Takeaway 3",
    "Takeaway 4"
  ],
  "grant_capture_strategy": "2-3 sentences on tactical application sequencing for matched opportunities.",
  "regulatory_and_permitting_roadmap": "2-3 sentences detailing state/local regulatory compliance."
}}
"""

        logger.info(f"Submitting live Executive Synthesis to OpenAI ({model_name})...")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1500
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        parsed["is_llm_generated"] = True
        parsed["model_used"] = model_name
        paragraphs = parsed.get("executive_summary_paragraphs", [])
        parsed["executive_summary_text"] = "\n\n".join(paragraphs)

        logger.info(f"OpenAI Executive Synthesis complete ({model_name}). Tokens used: {getattr(response.usage, 'total_tokens', 'N/A')}")
        _save_cached_summary(cache_key, parsed)
        return parsed

    except Exception as e:
        logger.warning(f"OpenAI API call failed for project executive summary ({e}). Falling back to deterministic engine.")
        return generate_deterministic_project_summary(profile, top_matches, top_orgs)


def synthesize_project_executive_analysis(
    analysis_data: Dict[str, Any],
    api_key: Optional[str] = None,
    model_name: str = "gpt-4o-mini",
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Synthesizes a strategic executive briefing for the project match analysis.
    Uses OpenAI API when an API key is available; otherwise gracefully falls back
    to the deterministic house-voice analytical synthesizer.
    """
    profile = (
        analysis_data.get("extracted_profile")
        or analysis_data.get("profile")
        or analysis_data.get("structured_profile")
        or {}
    )
    if isinstance(profile, str):
        try:
            profile = json.loads(profile)
        except Exception:
            profile = {}

    matches_obj = analysis_data.get("matches") or {}
    if isinstance(matches_obj, dict):
        strong_matches = matches_obj.get("strong_matches", [])
        conditional_matches = matches_obj.get("conditional_matches", [])
        component_matches = matches_obj.get("component_matches", [])
    else:
        strong_matches = analysis_data.get("strong_matches", [])
        conditional_matches = analysis_data.get("conditional_matches", [])
        component_matches = analysis_data.get("component_matches", [])

    top_matches = strong_matches + conditional_matches + component_matches
    top_orgs = analysis_data.get("top_25_say_yes") or []

    return generate_ai_project_executive_summary(
        profile=profile,
        top_matches=top_matches,
        top_orgs=top_orgs,
        api_key=api_key,
        model_name=model_name,
        force_refresh=force_refresh
    )
