"""Project analysis orchestrator.

Coordinates profile extraction, eligibility screening, fit scoring,
decomposition, precedent matching, and strategic reasoning.
"""

import re
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session, selectinload

from app.engine.eligibility import evaluate_eligibility
from app.engine.fit import evaluate_fit, find_precedents
from app.engine.profile import ProjectProfile, extract_profile
from app.engine.win_rate_engine import calculate_win_rate_analytics
from app.engine.propensity_engine import rank_top_25_say_yes_matrix
from app.engine.bitmasks import (
    build_opportunity_bitmasks,
    compute_tech_mask_from_list,
    compute_activity_mask,
    compute_applicant_mask,
    compute_geo_mask,
    compute_bitmask_compatibility,
)
from app.engine.vector_scorer import (
    build_opportunity_matrix,
    vectorize_profile,
    compute_dense_similarities,
)
from app.models.analysis import AnalysisMatch, ProjectAnalysis
from app.models.opportunity import Opportunity
from app.models.relationship import OpportunityRelationship
from app.models.program import Program

logger = logging.getLogger(__name__)

# Global in-memory opportunity cache for sub-second candidate resolution
_OPPORTUNITIES_CACHE: list[Opportunity] = []
_OPPORTUNITIES_CACHE_TIME: float = 0.0
_OPPORTUNITIES_CACHE_TTL: float = 300.0  # 5 minutes TTL


_RE_RESIDENTIAL_PROGRAM = re.compile(
    r'\b(residential\s+(?:rebate|incentive|program|storage|clean\s+heat|microgrid|energy\s+code)|'
    r'homeowner|single[\s-]family|weatherization\s+assistance|weatherization\s+formula|'
    r'whole[\s-]house|hvacr\s+to\s+home\s+performance|residential\s+wood\s+heater|'
    r'empower\s*new\s*york|empower\+|geothermal\s+heat\s+pump\s+rebates)\b',
    re.IGNORECASE
)
_RE_DOWNSTREAM_INSTALLATION_REBATE = re.compile(
    r'\b(incentives?\s+for\s+the\s+installation|market\s+acceleration\s+incentives?|'
    r'residential\s+and\s+(?:retail|nonresidential)\s+incentive|'
    r'contractors\s+and\s+builders\s+to\s+install|rebates?\s+for\s+installing)\b',
    re.IGNORECASE
)
_RE_INDUSTRIAL_OPP = re.compile(
    r'\b(industrial\s+decarbonization|clean\s+energy\s+manufacturing|manufacturing\s+plant|'
    r'chemical\s+manufacturing|green\s+steel|low-carbon\s+cement)\b',
    re.IGNORECASE
)
_RE_FOSSIL_SOLID_COMBUSTION = re.compile(
    r'\b(coal\s+value\s+chain|wood\s+heater|solid\s+fuel|wood\s+stove|'
    r'combustion\s+efficiency\s+testing|fossil\s+energy|coal\s+refinement)\b',
    re.IGNORECASE
)
_RE_ACADEMIC_BASIC_RESEARCH = re.compile(
    r'\b(fundamental\s+research|basic\s+science|graduate\s+fellowship|postdoctoral|'
    r'dissertation|early-career\s+faculty)\b',
    re.IGNORECASE
)
_RE_MANUFACTURING_SCALEUP = re.compile(
    r'\b(manufacturing\s+scale|commercial\s+production|factory\s+expansion|'
    r'clean\s+energy\s+manufacturing|supply\s+chain\s+expansion|demonstration\s+facility)\b',
    re.IGNORECASE
)
_RE_COMMERCIAL_DEPLOYMENT = re.compile(
    r'\b(turnkey\s+deployment|commercial\s+installation|market\s+rollout|shovel-ready)\b',
    re.IGNORECASE
)


def get_cached_opportunities(db: Session, force_refresh: bool = False) -> list[Opportunity]:
    """Retrieve pre-warmed opportunities with relations from memory cache."""
    global _OPPORTUNITIES_CACHE, _OPPORTUNITIES_CACHE_TIME
    now = time.time()
    if not _OPPORTUNITIES_CACHE or force_refresh or (now - _OPPORTUNITIES_CACHE_TIME > _OPPORTUNITIES_CACHE_TTL):
        from app.engine.fit import (
            _RE_RES_PROGRAM,
            _RE_INDUSTRIAL_OPP,
            _RE_FOSSIL_SOLID_COMBUSTION,
            _RE_NUCLEAR_OPP,
            _RE_ACADEMIC_BASIC_RESEARCH,
            _RE_MANUFACTURING_SCALEUP,
            _RE_COMMERCIAL_DEPLOYMENT,
            _RE_DOWNSTREAM_INSTALLATION_REBATE,
            _RE_MHK_OPP,
            _RE_TRANS_OPP,
            _RE_WIND_OPP,
            _RE_SOLAR_OPP,
            _RE_GRID_INFRA_OPP,
            _RE_H2_OPP,
            _RE_DAC_OPP,
            EPA_REGION_STATES,
        )
        from app.engine.eligibility import get_opportunity_required_state

        _OPPORTUNITIES_CACHE = (
            db.query(Opportunity)
            .options(
                selectinload(Opportunity.categories),
                selectinload(Opportunity.eligibility_rules),
                selectinload(Opportunity.rounds),
                selectinload(Opportunity.restrictions),
            )
            .all()
        )
        for opp in _OPPORTUNITIES_CACHE:
            opp._search_corpus_lower = (
                (opp.name or "") + " " +
                (opp.short_description or "") + " " +
                (opp.objectives or "") + " " +
                (opp.keywords or "") + " " +
                (opp.selection_criteria or "")
            ).lower()
            opp._name_lower = (opp.name or "").lower()
            opp._short_desc_lower = (opp.short_description or "").lower()
            opp_text = f"{opp._name_lower} {opp._short_desc_lower}"
            opp_corpus = opp._search_corpus_lower
            opp._agency_lower = (opp.agency or "").lower()
            opp._jurisdiction_lower = (getattr(opp, "jurisdiction", "") or "").lower()
            opp._geo_scope_lower = (getattr(opp, "geographic_scope", "") or "").lower()

            opp._is_res_program = bool(_RE_RES_PROGRAM.search(opp_text))
            opp._is_downstream_installation_rebate = bool(_RE_DOWNSTREAM_INSTALLATION_REBATE.search(opp_text))
            opp._is_industrial_opp = bool(_RE_INDUSTRIAL_OPP.search(opp_text))
            opp._is_fossil_or_solid_combustion = bool(_RE_FOSSIL_SOLID_COMBUSTION.search(opp_text))
            opp._is_nuclear_opp = bool(_RE_NUCLEAR_OPP.search(opp_text))
            opp._is_academic_basic_research = bool(_RE_ACADEMIC_BASIC_RESEARCH.search(opp_text))
            opp._is_manufacturing_scaleup = bool(_RE_MANUFACTURING_SCALEUP.search(opp_text))
            opp._is_commercial_deployment = bool(_RE_COMMERCIAL_DEPLOYMENT.search(opp_text))
            opp._is_mhk_opp = bool(_RE_MHK_OPP.search(opp_corpus))
            opp._is_trans_opp = bool(_RE_TRANS_OPP.search(opp_corpus))
            opp._is_wind_opp = bool(_RE_WIND_OPP.search(opp_corpus))
            opp._is_solar_opp = bool(_RE_SOLAR_OPP.search(opp_corpus))
            opp._is_grid_infra_opp = bool(_RE_GRID_INFRA_OPP.search(opp_corpus))
            opp._is_h2_opp = bool(_RE_H2_OPP.search(opp_corpus))
            opp._is_dac_opp = bool(_RE_DAC_OPP.search(opp_corpus))

            # Geographic alignment caching
            epa_reg = None
            for r_key in EPA_REGION_STATES:
                if opp._geo_scope_lower == r_key or opp._jurisdiction_lower == r_key:
                    epa_reg = r_key
                    break
            opp._epa_region = epa_reg

            opp._is_federal = (
                any(f in opp._agency_lower for f in [
                    "doe", "u.s. department of energy", "arpa-e", "nsf", "national science foundation",
                    "epa", "environmental protection", "usda", "dod", "doc", "federal"
                ])
                or opp._jurisdiction_lower in ("us_fed", "federal", "national")
                or opp._geo_scope_lower == "national"
            )

            opp._is_national_unrestricted = any(n in opp._agency_lower for n in [
                "gates", "bloomberg", "rockefeller", "bezos", "breakthrough", "nextera", "duke",
                "southern company", "exelon", "aep", "xcel", "dominion", "avangrid", "eversource",
                "entergy", "dte", "macarthur", "elemental", "prime coalition"
            ])

            opp._required_state = get_opportunity_required_state(opp)
            opp._state_agency_state = opp._required_state

            cats = opp.categories or []
            opp._cached_categories = list(cats)
            opp._cached_eligibility_rules = list(opp.eligibility_rules or [])
            opp._cached_rounds = list(opp.rounds or [])
            opp._cached_restrictions = list(opp.restrictions or [])
            opp._tech_cat_values = [
                c.category_value.lower() for c in cats
                if c.category_type in ("technology", "sector", "fuel")
            ]
            opp._tech_cat_str = " ".join(opp._tech_cat_values)
            opp._act_cat_values = [
                c.category_value.lower() for c in cats
                if c.category_type == "activity"
            ]
            opp._act_cat_str = " ".join(opp._act_cat_values)
            opp._bitmasks = build_opportunity_bitmasks(opp)

        build_opportunity_matrix(_OPPORTUNITIES_CACHE)
        _OPPORTUNITIES_CACHE_TIME = now
    return _OPPORTUNITIES_CACHE


def invalidate_opportunities_cache():
    """Invalidate in-memory opportunity cache (e.g. after data ingestion)."""
    global _OPPORTUNITIES_CACHE, _OPPORTUNITIES_CACHE_TIME
    _OPPORTUNITIES_CACHE = []
    _OPPORTUNITIES_CACHE_TIME = 0.0


def analyze_project(
    db: Session,
    text: str,
    applicant_type: Optional[str] = None,
    location: Optional[str] = None,
    trl: Optional[int] = None,
    cost: Optional[float] = None,
    timeline: Optional[str] = None,
    partners: Optional[str] = None,
    technology_areas: Optional[list[str]] = None,
    activity_types: Optional[list[str]] = None,
    sectors: Optional[list[str]] = None,
    fuel_types: Optional[list[str]] = None,
    target_agencies: Optional[list[str]] = None,
    fast_mode: bool = False,
) -> dict:
    """Run full project matching and opportunity diligence analysis."""

    # 1. Extract project profile
    profile = extract_profile(
        text,
        applicant_type=applicant_type,
        location=location,
        trl=trl,
        cost=cost,
        timeline=timeline,
        partners=partners,
        technology_areas=technology_areas,
        activity_types=activity_types,
        sectors=sectors,
        fuel_types=fuel_types,
    )

    # 2. Save analysis record
    analysis = ProjectAnalysis(
        input_text=text,
        structured_profile=profile.to_json(),
        technology_areas=json.dumps(profile.technology_areas),
        activity_types=json.dumps(profile.activity_types),
        estimated_trl=profile.estimated_trl,
        applicant_type=profile.applicant_type,
        target_location=profile.target_location,
        project_cost=profile.project_cost,
        project_timeline=profile.project_timeline,
        summary=profile.summary,
        decomposition=json.dumps(profile.workstreams),
    )
    db.add(analysis)
    db.flush()

    # 3. Rank Top 15 Organizations Most Likely to Say "YES"
    # 3. Rank Top Organizations Most Likely to Say 'YES'
    top_50_say_yes = []
    try:
        top_50_say_yes = rank_top_25_say_yes_matrix(
            db=db,
            profile=profile,
            target_agencies=target_agencies,
            limit=50
        )
    except Exception as e:
        logger.warning(f"Error computing top 50 say yes matrix: {e}")

    top_10_say_yes = top_50_say_yes[:10]
    top_15_say_yes = top_50_say_yes[:10]
    top_25_say_yes = top_50_say_yes[:10]

    top_org_names = set()
    for org in top_50_say_yes:
        top_org_names.add(org["organization_code"].lower())
        top_org_names.add(org["organization_name"].lower())

    # 4. Query candidate opportunities across multi-agency corpus (in-memory cached)
    all_opps = get_cached_opportunities(db)
    if target_agencies and len(target_agencies) > 0:
        from app.engine.propensity_engine import detect_project_state, get_all_state_agencies_for_state
        proj_st = detect_project_state(profile.target_location or profile.ny_location or profile.location or "")
        state_agencies = get_all_state_agencies_for_state(proj_st)
        effective_agencies = set(list(target_agencies) + state_agencies)
        opportunities = [o for o in all_opps if o.agency in effective_agencies]
    else:
        opportunities = all_opps

    # 4b. Dense Semantic Feature Vector Projection (Fast BLAS Dot Product in < 1.5ms)
    query_vec = vectorize_profile(profile)
    dense_sims = compute_dense_similarities(query_vec)

    # 4c. 64-Bit Integer Masks for profile
    proj_tech_mask = compute_tech_mask_from_list(profile.technology_areas)
    proj_act_mask = compute_activity_mask(profile.activity_types)
    proj_app_mask = compute_applicant_mask(profile.applicant_type)
    proj_geo_mask = compute_geo_mask(profile.target_location or profile.ny_location or profile.location)

    # 5. Screen eligibility and evaluate fit for each opportunity
    proj_st = getattr(profile, "_cached_proj_state", None)
    if not proj_st:
        from app.engine.propensity_engine import detect_project_state
        proj_st = detect_project_state(profile.target_location or profile.ny_location or profile.location or "")
        profile._cached_proj_state = proj_st

    matches = []
    for opp in opportunities:
        # Pre-filter strict out-of-state state agency / utility programs early (< 0.001ms)
        req_st = getattr(opp, "_required_state", None)
        if req_st and proj_st and proj_st != "ALL" and req_st != proj_st:
            continue

        # Pre-assign dense similarity for hybrid evaluation
        opp._dense_sim = dense_sims.get(opp.id, 0.25)

        # Bitmask fast-compatibility check
        opp_masks = getattr(opp, "_bitmasks", {})
        compat_score, is_prime = compute_bitmask_compatibility(
            proj_tech_mask, proj_act_mask, proj_app_mask, proj_geo_mask,
            opp_masks.get("tech_mask", 0),
            opp_masks.get("act_mask", 0),
            opp_masks.get("app_mask", 0),
            opp_masks.get("geo_mask", 0),
        )

        # Strict out-of-state bitmask zero-check
        if compat_score == 0.0 and opp_masks.get("geo_mask", 0) != 0:
            continue

        elig_result = evaluate_eligibility(db, opp, profile)
        if elig_result.overall == "INELIGIBLE":
            continue  # Skip hard-ineligible solicitations

        # Score fit (hybrid semantic-lexical, technology, activity, stage, funding scale, geographic alignment)
        fit_result = evaluate_fit(db, opp, profile)

        # Skip opportunities with zero/negligible fit or out-of-region restrictions
        if fit_result.overall_score < 0.15:
            continue

        # Apply institutional alignment boost if sponsored by an identified top organization
        opp_agency_lower = (opp.agency or "").lower()
        if any(top_name in opp_agency_lower or opp_agency_lower in top_name for top_name in top_org_names):
            fit_result.overall_score = min(1.0, fit_result.overall_score * 1.08)
            fit_result.match_score_pct = int(round(fit_result.overall_score * 100))

        # Build match record
        match_data = _build_match(db, analysis, opp, elig_result, fit_result, profile, detailed=False)
        match_data["is_prime_eligible"] = is_prime
        match_data["match_tier"] = "prime" if is_prime else "teaming_partner"
        if not is_prime:
            match_data["teaming_role"] = "Commercial Demonstration / Subcontract Partner"
            match_data["teaming_rationale"] = (
                "Solicitation targets academic or consortium lead. Project qualifies as commercialization or demonstration partner."
            )

        matches.append(match_data)

    # 6. Find matching programs and historical precedents
    program_matches = _find_program_matches(db, analysis, profile)
    precedents = find_precedents(db, profile)

    # 7. Sort matches descending by fit score
    matches.sort(key=lambda m: m["fit_score"], reverse=True)

    # Filter opportunities strictly to match score of 75% or higher
    min_score_pct = 75
    min_fit_score = 0.75
    qualifying_matches = [
        m for m in matches
        if (m.get("fit_score", 0) >= min_fit_score) or ((m.get("match_score_pct") or 0) >= min_score_pct) or ((m.get("llm_match_score") or 0) >= min_score_pct)
    ]

    # 8. Fast Multi-Criteria Semantic Matching & Selective Strategic Diligence
    opps_by_id = {opp.id: opp for opp in opportunities}
    from app.engine.llm_opportunity_matcher import (
        _evaluate_deterministic_semantic_match,
        analyze_opportunity_fit_with_llm
    )
    from app.engine.ai_project_synthesizer import (
        synthesize_project_executive_analysis,
        generate_deterministic_project_summary,
    )
    from app.engine.advisor_qc import screen_matched_opportunities_with_advisor

    # 8a. Final LLM Advisor QC Layer: Screen out domain mismatches and nonsensical candidate matches
    screened_matches, screened_out_matches = screen_matched_opportunities_with_advisor(
        profile=profile,
        matches=qualifying_matches,
        opportunities_by_id=opps_by_id,
        fast_mode=fast_mode,
    )
    qualifying_matches = screened_matches

    # 8b. Instant grounded deterministic semantic evaluation for all top matches (0 tokens, <5ms)
    for m in qualifying_matches[:50]:
        opp = opps_by_id.get(m["opportunity_id"])
        if opp:
            fast_eval = _evaluate_deterministic_semantic_match(profile, opp, m["fit_score"])
            m["llm_analysis"] = fast_eval
            m["strategic_thesis"] = fast_eval.get("strategic_thesis") or m.get("why_it_fits", "")
            m["criteria_strengths"] = fast_eval.get("criteria_strengths") or []
            m["potential_risks_or_flags"] = fast_eval.get("potential_risks_or_flags") or []
            m["recommended_positioning"] = fast_eval.get("recommended_positioning") or ""
            m["conviction_tier"] = fast_eval.get("conviction_tier") or "High Conviction"
            m["llm_match_score"] = fast_eval.get("llm_match_score", m["match_score_pct"])

    # 8b. Institutional Diversity Re-ranker (Max 5 opportunities per agency/organization from qualifying >=75% matches, top 20 overall)
    agency_counts = {}
    diversified_top_opportunities = []
    for m in qualifying_matches:
        ag = m.get("agency") or "Other"
        count = agency_counts.get(ag, 0)
        if count < 5:
            diversified_top_opportunities.append(m)
            agency_counts[ag] = count + 1
        if len(diversified_top_opportunities) >= 20:
            break

    # 8c. Hierarchical Grouping by Sponsoring Organization & Agency (Strictly Top 10 Organizations and >=75% Matches)
    org_matches_map = {}
    for m in qualifying_matches:
        ag = m.get("agency") or "Other"
        if ag not in org_matches_map:
            org_matches_map[ag] = []
        org_matches_map[ag].append(m)

    grouped_opportunities = []
    for org in top_10_say_yes:
        org_code = org["organization_code"]
        org_name = org["organization_name"]
        
        # Match opportunities associated with this organization
        opps_for_org = []
        for ag_key, ag_opps in org_matches_map.items():
            ag_k_low = ag_key.lower()
            org_c_low = org_code.lower()
            org_n_low = org_name.lower()
            if (
                ag_k_low == org_c_low
                or org_c_low in ag_k_low
                or ag_k_low in org_n_low
                or (org_c_low == "nyserda" and "nyserda" in ag_k_low)
                or (org_c_low in ("doe", "arpa-e") and ("energy" in ag_k_low or "doe" in ag_k_low or "arpa" in ag_k_low))
                or (org_c_low == "epa" and ("environmental" in ag_k_low or "epa" in ag_k_low))
                or (org_c_low == "nsf" and ("science" in ag_k_low or "nsf" in ag_k_low))
                or (org_c_low == "cec" and ("california" in ag_k_low or "cec" in ag_k_low))
                or (org_c_low == "masscec" and ("massachusetts" in ag_k_low or "masscec" in ag_k_low))
                or (org_c_low == "con edison" and ("con ed" in ag_k_low or "coned" in ag_k_low))
                or (org_c_low == "national grid" and "national grid" in ag_k_low)
                or (org_c_low == "nypa" and "power authority" in ag_k_low)
                or (org_c_low == "lipa" and "long island" in ag_k_low)
            ):
                opps_for_org.extend(ag_opps)

        # Deduplicate and keep only >=75% opportunities
        unique_opps = []
        seen_ids = set()
        for op in opps_for_org:
            if op["opportunity_id"] not in seen_ids:
                if (op.get("fit_score", 0) >= min_fit_score) or ((op.get("match_score_pct") or 0) >= min_score_pct) or ((op.get("llm_match_score") or 0) >= min_score_pct):
                    seen_ids.add(op["opportunity_id"])
                    unique_opps.append(op)
        unique_opps.sort(key=lambda x: x["fit_score"], reverse=True)

        grouped_opportunities.append({
            "organization_code": org_code,
            "organization_name": org_name,
            "category": org["category"],
            "category_label": org["category_label"],
            "state": org["state"],
            "say_yes_score": org["say_yes_score"],
            "say_yes_tier": org["say_yes_tier"],
            "tier_badge_color": org.get("tier_badge_color", "emerald"),
            "geographic_nexus": org.get("geographic_nexus", ""),
            "territory_desc": org.get("territory_desc", ""),
            "primary_pain_points": org.get("primary_pain_points", []),
            "why_they_say_yes": org.get("why_they_say_yes", ""),
            "decision_maker_contacts": org.get("decision_maker_contacts", []),
            "total_opportunities_count": len(unique_opps),
            "top_opportunities": unique_opps[:5],
            "all_opportunities": unique_opps[:15]
        })

    grouped_opportunities.sort(key=lambda x: x["say_yes_score"], reverse=True)
    top_20_opportunities = diversified_top_opportunities[:20] if diversified_top_opportunities else qualifying_matches[:20]
    top_25_opportunities = top_20_opportunities

    # Enrich top qualifying matches with deep timeline, evidence, blockers, and win-rate analytics
    for m in qualifying_matches[:30]:
        opp = opps_by_id.get(m["opportunity_id"])
        if opp:
            _enrich_match_details(m, opp, profile, db)
            try:
                m["win_rate_analytics"] = calculate_win_rate_analytics(
                    db=db,
                    opp=opp,
                    profile=profile,
                    fit_score=m["fit_score"],
                    user_cost=profile.project_cost if profile else None,
                    applicant_type=profile.applicant_type if profile else None,
                )
            except Exception:
                pass

    # 9. Group matches by type for response (strictly >=75% match score)
    strong_list = [m for m in qualifying_matches if m.get("fit_score", 0) >= 0.80 or (m.get("match_score_pct") or 0) >= 80]
    cond_list = [m for m in qualifying_matches if (0.75 <= m.get("fit_score", 0) < 0.80) or (75 <= (m.get("match_score_pct") or 0) < 80)]
    comp_list = [m for m in qualifying_matches if m.get("match_tier") == "teaming_partner"]
    watch_list = []
    prime_list = [m for m in qualifying_matches if m.get("match_tier") == "prime"]
    teaming_list = [m for m in qualifying_matches if m.get("match_tier") == "teaming_partner"]

    categorized = {
        "strong_matches": strong_list,
        "conditional_matches": cond_list,
        "component_matches": comp_list,
        "watchlist": watch_list,
        "primary": strong_list,
        "component": comp_list,
        "thematic": cond_list,
        "aspirational": watch_list,
        "prime_matches": prime_list,
        "teaming_matches": teaming_list,
        "screened_out_by_advisor": screened_out_matches,
    }

    # 10. Compute summary counts
    summary = {
        "total_matched": len(qualifying_matches),
        "primary_count": len(strong_list),
        "component_count": len(comp_list),
        "thematic_count": len(cond_list),
        "aspirational_count": 0,
        "advisor_qc_screened_count": len(screened_out_matches),
        "advisor_qc_verified_count": len(qualifying_matches),
        "average_fit_score": (
            sum(m["fit_score"] for m in qualifying_matches) / len(qualifying_matches)
            if qualifying_matches
            else 0.0
        ),
    }

    # 11. Funding Architecture and Stacking
    funding_arch = _build_funding_architecture(qualifying_matches if qualifying_matches else matches[:5], profile)
    funding_stacks = _build_funding_stacks(db, qualifying_matches if qualifying_matches else matches[:5])
    analysis.funding_architecture = json.dumps(funding_arch)

    # 12. Run Selective Deep LLM Synthesis and Executive Briefing Concurrently
    def _evaluate_single_match_llm(m):
        opp = opps_by_id.get(m["opportunity_id"])
        if not opp:
            return m, None
        try:
            res = analyze_opportunity_fit_with_llm(
                profile=profile,
                opp=opp,
                base_fit_score=m["fit_score"],
                force_live=False,
            )
            return m, res
        except Exception as e:
            logger.warning(f"Live LLM evaluation error for opp {m.get('opportunity_id')}: {e}")
            return m, None

    def _run_executive_briefing():
        try:
            analysis_payload = {
                "profile": profile.to_dict(),
                "matches": categorized,
                "top_25_say_yes": top_15_say_yes,
                "top_15_say_yes": top_15_say_yes,
                "top_25_opportunities": top_25_opportunities,
            }
            return synthesize_project_executive_analysis(analysis_payload)
        except Exception as e:
            logger.warning(f"Error synthesizing executive briefing: {e}")
            return None

    if fast_mode:
        executive_briefing = generate_deterministic_project_summary(
            profile=profile.to_dict(),
            top_matches=qualifying_matches if qualifying_matches else matches[:5],
            top_orgs=top_15_say_yes,
        )
    else:
        # Run Executive Briefing and Top Diversified Matches Diligence in parallel via ThreadPoolExecutor
        top_k_to_evaluate = diversified_top_opportunities[:5] if diversified_top_opportunities else qualifying_matches[:5]
        with ThreadPoolExecutor(max_workers=6) as executor:
            f_briefing = executor.submit(_run_executive_briefing)
            f_top_opps = [executor.submit(_evaluate_single_match_llm, m) for m in top_k_to_evaluate]

            try:
                executive_briefing = f_briefing.result(timeout=5.0)
            except Exception as e:
                logger.warning(f"Executive briefing synthesis timed out or failed: {e}")
                executive_briefing = None

            for fut in f_top_opps:
                try:
                    m_target, eval_result = fut.result(timeout=5.0)
                    if eval_result and m_target:
                        m_target["llm_analysis"] = eval_result
                        m_target["strategic_thesis"] = eval_result.get("strategic_thesis") or m_target.get("strategic_thesis", "")
                        m_target["criteria_strengths"] = eval_result.get("criteria_strengths") or m_target.get("criteria_strengths", [])
                        m_target["potential_risks_or_flags"] = eval_result.get("potential_risks_or_flags") or m_target.get("potential_risks_or_flags", [])
                        m_target["recommended_positioning"] = eval_result.get("recommended_positioning") or m_target.get("recommended_positioning", "")
                        m_target["conviction_tier"] = eval_result.get("conviction_tier") or m_target.get("conviction_tier", "High Conviction")
                        if "llm_match_score" in eval_result:
                            m_target["match_score_pct"] = int(round(eval_result["llm_match_score"]))
                            m_target["fit_score"] = round(eval_result["llm_match_score"] / 100.0, 3)
                except Exception as e:
                    logger.warning(f"Match LLM evaluation error: {e}")

        if not executive_briefing:
            executive_briefing = generate_deterministic_project_summary(
                profile=profile.to_dict(),
                top_matches=qualifying_matches if qualifying_matches else matches[:5],
                top_orgs=top_15_say_yes,
            )

    # 13. Batch Save Top Matches to DB
    db_matches = []
    for m in (qualifying_matches if qualifying_matches else matches)[:100]:
        db_match = AnalysisMatch(
            analysis_id=analysis.id,
            opportunity_id=m["opportunity_id"],
            match_type=m["match_type"],
            match_category=_match_type_to_category(m["match_type"]),
            fit_score=m["fit_score"],
            applicable_component=", ".join(m.get("applicable_components", [])),
            why_it_fits=m.get("strategic_thesis") or m.get("why_it_fits", ""),
            eligibility_summary=json.dumps(m.get("eligibility", {})),
            blockers=json.dumps(m.get("blockers", [])),
            unknowns=json.dumps(m.get("unknowns", [])),
            recommended_positioning=m.get("recommended_positioning"),
            evidence=json.dumps(m.get("evidence", [])),
            assessment_json=json.dumps(m.get("assessment", {})),
            timeline_json=json.dumps(m.get("timeline", {})),
            reasoning_type="inferred_fit",
        )
        db_matches.append(db_match)
    db.add_all(db_matches)
    db.commit()

    return {
        "analysis_id": analysis.id,
        "profile": profile.to_dict(),
        "summary": summary,
        "executive_briefing": executive_briefing,
        "top_10_say_yes": top_10_say_yes,
        "top_15_say_yes": top_10_say_yes,
        "top_25_say_yes": top_10_say_yes,
        "top_50_say_yes": top_10_say_yes,
        "top_say_yes": top_10_say_yes,
        "top_20_opportunities": top_20_opportunities,
        "top_25_opportunities": top_20_opportunities,
        "top_50_opportunities": top_20_opportunities,
        "raw_top_20_opportunities": qualifying_matches[:20],
        "raw_top_25_opportunities": qualifying_matches[:20],
        "grouped_opportunities": grouped_opportunities[:10],
        "matches": categorized,
        "programs": program_matches,
        "precedents": precedents[:10],
        "funding_architecture": funding_arch,
        "funding_stacks": funding_stacks,
        "disclaimer": (
            "INDEPENDENT RESEARCH & PUBLIC INFORMATION NOTICE: This analysis was created entirely using publicly available information, "
            "open government databases (NY Open Data, Grants.gov, USAspending, USPTO, and published agency portals), and public solicitation filings. "
            "This document does not represent the official views, policies, endorsements, or determinations of NYSERDA, New York State, the US Department of Energy (DOE), "
            "or any other government agency, utility, or funding organization. Zero non-public, draft, internal, or confidential agency data is utilized or contained herein. "
            "No organizational resources, equipment, or official hours of any public agency were used in the creation or generation of this tool or report. "
            "This analysis is an independent computational research study for informational and planning purposes only; it does not constitute an official proposal submission, "
            "nor does it confer any guarantee, evaluation preference, or indicator of award selection."
        ),
    }


# ---------------------------------------------------------------------------
# Competitive assessment
# ---------------------------------------------------------------------------

def _is_innovation_research(opp, db=None) -> bool:
    """Determine if an opportunity is from an Innovation & Research program.

    Uses activity categories, solicitation description, and known I&R solicitation patterns.
    """
    # Federal heuristics
    agency = getattr(opp, 'agency', None)
    if agency == 'ARPA-E':
        return True
    if agency == 'DOE' and getattr(opp, 'agency_code', None) in ('DOE-EERE', 'DOE-ARPAE'):
        return True
    if agency == 'NSF':
        return True

    # Known I&R activity types
    ir_activities = {"Research", "Demonstration", "Product Development", "Scale-up"}
    # Known I&R technology areas (core I&R portfolio)
    ir_techs = {
        "Energy Storage", "Grid Modernization", "Carbon Management",
        "Hydrogen & Alternative Fuels", "Environmental Research",
        "Offshore Wind", "Wind", "Solar",
    }

    cat_activities = set()
    cat_techs = set()
    categories = getattr(opp, "_cached_categories", getattr(opp, "categories", [])) or []
    for c in categories:
        c_type = getattr(c, "category_type", None)
        c_val = getattr(c, "category_value", None)
        if c_type == "activity":
            cat_activities.add(c_val)
        elif c_type == "technology":
            cat_techs.add(c_val)

    # Direct activity match
    if cat_activities & ir_activities:
        return True

    # I&R tech area with a PON/RFP type (not workforce/incentive)
    if cat_techs & ir_techs:
        non_ir_acts = {"Training", "Incentive Program", "Technical Assistance"}
        if not (cat_activities & non_ir_acts):
            return True

    # Description keyword check
    desc = ((opp.short_description or "") + " " + (opp.name or "")).lower()
    ir_keywords = ["innovation", "research", "demonstration", "prototype", "pilot",
                    "proof of concept", "r&d", "technology development"]
    if any(kw in desc for kw in ir_keywords):
        return True

    return False


def _assess_competitiveness(opp, elig_result, fit_result, profile, db=None, match_dict=None) -> dict:
    """Produce an honest, specific competitive assessment for one opportunity.

    Every strength, concern, and deal-breaker sentence names the specific
    opportunity by solicitation number so context is never ambiguous.
    """
    sol = opp.solicitation_number or "Solicitation"
    if match_dict:
        score = match_dict.get("fit_score", 0.5)
        raw_dims = match_dict.get("fit_dimensions", [])
        dims = {d.get("dimension") if isinstance(d, dict) else getattr(d, "dimension", ""): d for d in raw_dims}
        elig = match_dict.get("eligibility", {})
        tests = elig.get("tests", []) if isinstance(elig, dict) else []
        hard_fails = [t.get("reason", "") if isinstance(t, dict) else getattr(t, "reason", "") for t in tests if (t.get("result") if isinstance(t, dict) else getattr(t, "result", "")) == "FAIL" and (t.get("is_hard") if isinstance(t, dict) else getattr(t, "is_hard", False))]
        soft_fails = [t.get("reason", "") if isinstance(t, dict) else getattr(t, "reason", "") for t in tests if (t.get("result") if isinstance(t, dict) else getattr(t, "result", "")) == "FAIL" and not (t.get("is_hard") if isinstance(t, dict) else getattr(t, "is_hard", False))]
        unknowns = [t.get("reason", "") if isinstance(t, dict) else getattr(t, "reason", "") for t in tests if (t.get("result") if isinstance(t, dict) else getattr(t, "result", "")) == "UNKNOWN"]
        passes = [t.get("rule_key", "") if isinstance(t, dict) else getattr(t, "rule_key", "") for t in tests if (t.get("result") if isinstance(t, dict) else getattr(t, "result", "")) == "PASS"]
    else:
        score = fit_result.overall_score if fit_result else 0.5
        raw_dims = getattr(fit_result, "dimensions", []) if fit_result else []
        dims = {getattr(d, "dimension", d.get("dimension") if isinstance(d, dict) else ""): d for d in raw_dims}
        tests = getattr(elig_result, "tests", []) if elig_result else []
        hard_fails = [getattr(t, "reason", "") for t in tests if getattr(t, "result", None) == "FAIL" and getattr(t, "is_hard", False)]
        soft_fails = [getattr(t, "reason", "") for t in tests if getattr(t, "result", None) == "FAIL" and not getattr(t, "is_hard", False)]
        unknowns = [getattr(t, "reason", "") for t in tests if getattr(t, "result", None) == "UNKNOWN"]
        passes = [getattr(t, "rule_key", "") for t in tests if getattr(t, "result", None) == "PASS"]

    def _get_dim_score(dim_name: str) -> float:
        d = dims.get(dim_name)
        if not d: return 0.0
        return float(d.get("score", 0.0) if isinstance(d, dict) else getattr(d, "score", 0.0))

    def _get_dim_expl(dim_name: str) -> str:
        d = dims.get(dim_name)
        if not d: return ""
        return str(d.get("explanation", "") if isinstance(d, dict) else getattr(d, "explanation", ""))

    strengths = []
    concerns = []
    deal_breakers = []

    # --- Technology fit ---
    tech_score = _get_dim_score("technology_fit")
    tech_expl = _get_dim_expl("technology_fit")
    if "technology_fit" in dims:
        if tech_score >= 0.7:
            strengths.append(
                f"{sol} directly targets your technology area ({tech_expl})."
            )
        elif tech_score >= 0.4:
            concerns.append(
                f"{sol} covers adjacent but not identical technology areas — "
                f"partial overlap only."
            )
        else:
            deal_breakers.append(
                f"{sol} funds different technology areas than this project's core focus."
            )

    # --- Activity fit ---
    act_score = _get_dim_score("activity_fit")
    act_expl = _get_dim_expl("activity_fit")
    if "activity_fit" in dims:
        if act_score >= 0.7:
            strengths.append(
                f"{sol}'s scope matches the proposed activity type ({act_expl})."
            )
        elif act_score < 0.3:
            concerns.append(
                f"{sol} may not be looking for the type of activity this project proposes "
                f"(e.g. demonstration vs. deployment vs. research)."
            )

    # --- Funding scale ---
    if "funding_scale" in dims and profile.project_cost:
        if opp.max_per_award and profile.project_cost > 0:
            ratio = profile.project_cost / opp.max_per_award if opp.max_per_award > 0 else 0
            if ratio > 5:
                agency_lbl = opp.agency or "Program"
                deal_breakers.append(
                    f"{sol} max award is ${opp.max_per_award:,.0f} — your project cost "
                    f"(${profile.project_cost:,.0f}) is {ratio:.0f}× that. {agency_lbl} funding "
                    f"through this program would cover only a small fraction."
                )
            elif ratio > 2:
                concerns.append(
                    f"{sol} max award (${opp.max_per_award:,.0f}) is well below your "
                    f"project cost (${profile.project_cost:,.0f}). Substantial co-funding required."
                )
            elif ratio >= 0.3:
                strengths.append(
                    f"{sol}'s funding scale (up to ${opp.max_per_award:,.0f}) aligns "
                    f"with the project's cost."
                )
        elif opp.total_funding and profile.project_cost > opp.total_funding:
            concerns.append(
                f"{sol} has a total program budget of ${opp.total_funding:,.0f}, which is "
                f"below the project's ${profile.project_cost:,.0f} cost."
            )

    # --- Eligibility ---
    if hard_fails:
        for hf in hard_fails:
            deal_breakers.append(f"{sol}: Hard eligibility fail — {hf}.")
    if soft_fails:
        for sf in soft_fails:
            concerns.append(f"{sol}: Eligibility concern — {sf}.")
    if passes:
        if passes:
            strengths.append(
                f"{sol}: Passes eligibility checks ({', '.join(passes[:3])})."
            )

    # --- Text relevance ---
    txt_score = _get_dim_score("text_relevance") or _get_dim_score("keyword_relevance")
    if txt_score >= 0.7:
        strengths.append(
            f"{sol}'s solicitation language closely matches the project description."
        )

    # --- TRL / Stage mismatch ---
    # I&R programs typically fund early-to-mid TRL; deployment projects are often TRL 7-9
    if profile.estimated_trl:
        categories = getattr(opp, "_cached_categories", getattr(opp, "categories", [])) or []
        cat_acts = {getattr(c, "category_value", None) for c in categories if getattr(c, "category_type", None) == "activity"}

        # Detect if this is an R&D/early-stage solicitation
        is_rd_scope = bool(cat_acts & {"Research", "Product Development"})
        is_demo_scope = "Demonstration" in cat_acts
        is_deploy_scope = bool(cat_acts & {"Deployment", "Incentive Program", "Retrofit"})

        if profile.estimated_trl >= 8 and is_rd_scope and not is_deploy_scope:
            concerns.append(
                f"{sol} targets research and product development (typically TRL 1-6). "
                f"This project at TRL {profile.estimated_trl} is deploying proven technology, "
                f"not developing new technology — a fundamental scope mismatch."
            )
        elif profile.estimated_trl >= 8 and is_demo_scope and not is_deploy_scope:
            # Demo programs at high TRL can sometimes work if the demo is the point
            if "host site" in desc_lower or "demonstration site" in desc_lower:
                strengths.append(
                    f"{sol} seeks demonstration host sites, which could align with "
                    f"a high-TRL deployment."
                )
            else:
                concerns.append(
                    f"{sol} funds technology demonstrations (proving a technology works), "
                    f"but this project at TRL {profile.estimated_trl} is deploying already-proven "
                    f"systems. NYSERDA I&R demonstrations typically test novel or pre-commercial "
                    f"technologies, not standard installations of mature products."
                )
        elif profile.estimated_trl <= 4 and is_deploy_scope and not is_rd_scope:
            concerns.append(
                f"{sol} funds deployment and scale-up, but this project at TRL "
                f"{profile.estimated_trl} may be too early-stage for a deployment program."
            )

    # --- Scope specificity: narrow program scope vs broad project ---
    # Parse the description for highly specific program scopes
    desc_lower = (opp.short_description or "").lower()
    opp_name_lower = (opp.name or "").lower()
    combined_text = desc_lower + " " + opp_name_lower

    # Detect narrow technology scopes from the description
    narrow_scopes = []
    scope_patterns = {
        "window heat pump": "packaged window heat pumps in multifamily buildings",
        "through wall heat pump": "through-wall/packaged terminal heat pumps (PTHPs)",
        "packaged terminal heat pump": "through-wall/packaged terminal heat pumps (PTHPs)",
        "grid enhancing technolog": "grid-enhancing technologies (GETs) for utility operations",
        "advanced nuclear": "advanced nuclear energy technology",
        "air quality": "energy-related air quality and health effects research",
        "alternative fuel": "large-scale alternative fuels and infrastructure",
        "offshore wind": "offshore wind energy development",
        "hydrogen": "hydrogen production and infrastructure",
        "electric vehicle": "electric vehicle infrastructure and technology",
        "ev charging": "EV charging infrastructure",
    }

    for pattern, scope_desc in scope_patterns.items():
        if pattern in combined_text:
            narrow_scopes.append(scope_desc)

    if narrow_scopes:
        scope_str = narrow_scopes[0]
        # Check if the project actually matches this narrow scope
        project_text = (profile.summary or "").lower()
        project_techs = [t.lower() for t in profile.technology_areas]

        pattern_in_project = any(
            p in project_text or any(p in pt for pt in project_techs)
            for p in scope_patterns.keys() if p in combined_text
        )

        if not pattern_in_project:
            concerns.append(
                f"{sol} has a narrow scope: {scope_str}. This project's focus "
                f"({', '.join(profile.technology_areas[:3])}) does not directly match "
                f"that specific program target."
            )
        else:
            strengths.append(
                f"{sol} targets {scope_str}, which directly aligns with this project."
            )

    # --- Multifamily-specific scope check ---
    if "multifamily" in combined_text and profile.applicant_type:
        if profile.applicant_type.lower() in ["university", "academic"]:
            concerns.append(
                f"{sol} targets multifamily residential buildings. A university campus "
                f"with academic, dormitory, and athletic facilities is a different building "
                f"stock — eligibility should be confirmed directly with the program manager."
            )

    # --- Determine I&R status ---
    is_ir = _is_innovation_research(opp, db)

    # --- Determine verdict ---
    if hard_fails:
        verdict = "wrong_program"
        verdict_label = "Not Eligible"
        verdict_detail = (
            f"{sol}: Hard eligibility failure — {hard_fails[0]}. "
            f"This opportunity does not apply."
        )
    elif score >= 0.70 and not deal_breakers and len(concerns) <= 1:
        verdict = "slam_dunk"
        verdict_label = "Slam Dunk"
        verdict_detail = (
            f"{sol} is a strong, direct match. The project's technology, activity type, "
            f"and scope align well with what this solicitation is designed to fund."
        )
    elif score >= 0.60 and not deal_breakers:
        verdict = "strong_fit"
        verdict_label = "Strong Fit"
        verdict_detail = (
            f"{sol} is a solid match worth pursuing. There may be minor gaps to address "
            f"in the proposal, but the core alignment is there."
        )
    elif score >= 0.45 and not deal_breakers:
        verdict = "plausible"
        verdict_label = "Plausible — Needs Work"
        if concerns:
            verdict_detail = (
                f"{sol} has partial alignment but {concerns[0][len(sol)+1:].strip() if concerns[0].startswith(sol) else concerns[0].lower()}"
            )
        else:
            verdict_detail = (
                f"{sol} has some alignment, but the project would need to be scoped or "
                f"framed carefully to be competitive under this solicitation."
            )
    elif score >= 0.30:
        verdict = "stretch"
        verdict_label = "Stretch"
        verdict_detail = (
            f"{sol} is a reach. Some surface-level alignment exists, but significant "
            f"re-framing or project decomposition would be needed."
        )
    else:
        verdict = "long_shot"
        verdict_label = "Long Shot"
        verdict_detail = (
            f"{sol} has minimal alignment with this project. Not recommended unless "
            f"the project scope changes significantly."
        )

    return {
        "verdict": verdict,
        "verdict_label": verdict_label,
        "verdict_detail": verdict_detail,
        "strengths": strengths,
        "concerns": concerns,
        "deal_breakers": deal_breakers,
        "is_innovation_research": is_ir,
    }


# ---------------------------------------------------------------------------
# Timing & action timeline
# ---------------------------------------------------------------------------

def _build_action_timeline(opp, profile) -> dict:
    """Build a specific action timeline for pursuing this opportunity.

    Returns:
      timing_status  – open_now, closing_soon, continuous, future, closed
      urgency        – immediate, weeks, months, no_rush, n/a
      actions        – ordered list of {step, description, deadline?, weeks_from_now?}
      timing_note    – 1-sentence timing summary
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    actions = []

    # Find next round deadline
    next_deadline = None
    next_round = None
    concept_deadline = None
    all_rounds = []
    for r in opp.rounds:
        all_rounds.append(r)
        if r.status == "Open":
            if r.due_date:
                if next_deadline is None or r.due_date < next_deadline:
                    next_deadline = r.due_date
                    next_round = r
            if r.concept_paper_due_date:
                concept_deadline = r.concept_paper_due_date

    # Determine timing status and urgency
    if next_deadline:
        days_until = (next_deadline - now).days
        if days_until < 0:
            timing_status = "closed"
            urgency = "n/a"
            timing_note = "This round's deadline has passed. Check for future rounds."
        elif days_until <= 21:
            timing_status = "closing_soon"
            urgency = "immediate"
            timing_note = f"Deadline in {days_until} days ({next_deadline.strftime('%B %d, %Y')}). Act now if pursuing."
        elif days_until <= 60:
            timing_status = "open_now"
            urgency = "weeks"
            timing_note = f"Open with {days_until} days remaining (due {next_deadline.strftime('%B %d, %Y')}). Start preparation now."
        else:
            timing_status = "open_now"
            urgency = "months"
            timing_note = f"Open with {days_until} days remaining (due {next_deadline.strftime('%B %d, %Y')}). Adequate time to prepare."
    elif opp.enrollment_type and "continuous" in (opp.enrollment_type or "").lower():
        timing_status = "continuous"
        urgency = "no_rush"
        timing_note = "This is a continuously open enrollment program. You can apply at any time."
    else:
        timing_status = "open_now"
        urgency = "no_rush"
        timing_note = "No specific deadline posted. Likely rolling or continuous enrollment."

    # Build action steps
    step = 1

    # Concept paper?
    if opp.concept_paper_required:
        cp_date = concept_deadline.strftime("%B %d, %Y") if concept_deadline else "TBD"
        actions.append({
            "step": step,
            "action": "Submit Concept Paper",
            "description": f"This solicitation requires a concept paper before a full proposal. Deadline: {cp_date}.",
            "deadline": concept_deadline.isoformat() if concept_deadline else None,
            "type": "required",
        })
        step += 1

    # Download and review solicitation documents
    actions.append({
        "step": step,
        "action": "Download & Review Solicitation Documents",
        "description": "Read the full solicitation, scoring criteria, and eligible activities. Verify your project fits before investing in a proposal.",
        "type": "required",
    })
    step += 1

    # Check specific eligibility
    actions.append({
        "step": step,
        "action": "Confirm Eligibility Requirements",
        "description": "Verify applicant type, NY-nexus, cost-share ability, and any sector-specific requirements in the solicitation.",
        "type": "required",
    })
    step += 1

    # Cost share
    if opp.cost_share_pct:
        actions.append({
            "step": step,
            "action": f"Secure {opp.cost_share_pct}% Cost Share",
            "description": f"This program requires a {opp.cost_share_pct}% cost share from the applicant. Identify co-funding sources.",
            "type": "required",
        })
        step += 1

    # Host/utility partner if relevant
    desc = (opp.short_description or "").lower()
    if any(kw in desc for kw in ["host site", "utility partner", "demonstration site", "host facilit"]):
        actions.append({
            "step": step,
            "action": "Identify Host Site / Utility Partner",
            "description": "This program likely requires a NY-based host site or utility partner for demonstration. Secure a letter of commitment.",
            "type": "recommended",
        })
        step += 1

    # Submit proposal
    dl = next_deadline.strftime("%B %d, %Y") if next_deadline else "rolling"
    actions.append({
        "step": step,
        "action": "Submit Full Proposal",
        "description": f"Complete and submit the full proposal by {dl}.",
        "deadline": next_deadline.isoformat() if next_deadline else None,
        "type": "required",
    })
    step += 1

    # Contact program manager
    opp_contacts = opp.__dict__.get("contacts")
    if opp_contacts:
        contact = opp_contacts[0]
        contact_info = getattr(contact, "name", "Program Officer")
        if getattr(contact, "email", None):
            contact_info += f" ({contact.email})"
        actions.append({
            "step": step,
            "action": "Contact Program Manager",
            "description": f"Reach out to {contact_info} to discuss your project before submitting. This is standard practice and strongly recommended.",
            "type": "recommended",
        })
    elif opp.agency:
        actions.append({
            "step": step,
            "action": "Contact Program Manager",
            "description": f"Reach out to the {opp.agency} program team to discuss your project before submitting. This is standard practice and strongly recommended.",
            "type": "recommended",
        })

    return {
        "timing_status": timing_status,
        "urgency": urgency,
        "timing_note": timing_note,
        "deadline": next_deadline.strftime("%m/%d/%Y") if next_deadline else None,
        "deadline_iso": next_deadline.isoformat() if next_deadline else None,
        "actions": actions,
    }


def _enrich_match_details(m: dict, opp: Opportunity, profile: ProjectProfile, db: Session = None) -> None:
    """Enrich a top-ranked match with action timeline, evidence, blockers, and assessment."""
    timeline = _build_action_timeline(opp, profile)
    m["timeline"] = timeline
    m["next_deadline"] = timeline.get("deadline") if isinstance(timeline, dict) else None

    evidence = []
    if opp.source_name:
        evidence.append({
            "source": opp.source_name,
            "url": opp.source_url,
            "verified_at": opp.last_verified_at.isoformat() if opp.last_verified_at else None,
        })
    if opp.detail_page_url:
        evidence.append({
            "source": "NYSERDA Portal",
            "url": opp.detail_page_url,
        })
    m["evidence"] = evidence

    elig = m.get("eligibility", {})
    tests = elig.get("tests", []) if isinstance(elig, dict) else []
    m["blockers"] = [t.get("reason", "") for t in tests if t.get("result") == "FAIL" and not t.get("is_hard")]
    m["unknowns"] = [t.get("reason", "") for t in tests if t.get("result") == "UNKNOWN"]
    m["assessment"] = _assess_competitiveness(opp, None, None, profile, db=db, match_dict=m)


def _build_match(db, analysis, opp, elig_result, fit_result, profile, detailed: bool = False) -> dict:
    """Build a match record for an opportunity."""
    if detailed:
        assessment = _assess_competitiveness(opp, elig_result, fit_result, profile, db=db)
        timeline = _build_action_timeline(opp, profile)
        evidence = []
        if opp.source_name:
            evidence.append({
                "source": opp.source_name,
                "url": opp.source_url,
                "verified_at": opp.last_verified_at.isoformat() if opp.last_verified_at else None,
            })
        if opp.detail_page_url:
            evidence.append({
                "source": "NYSERDA Portal",
                "url": opp.detail_page_url,
            })
        blockers = [
            t.reason for t in elig_result.tests
            if t.result == "FAIL" and not t.is_hard
        ]
        unknowns = [
            t.reason for t in elig_result.tests
            if t.result == "UNKNOWN"
        ]
    else:
        assessment = {}
        timeline = {}
        evidence = []
        blockers = []
        unknowns = []

    # Lifecycle status designation
    agency = getattr(opp, 'agency', 'NYSERDA')
    if opp.status == "open":
        lifecycle = "Open Solicitation"
    elif opp.status == "draft":
        lifecycle = "Draft / Upcoming"
    elif opp.status == "awarded":
        lifecycle = "Active Program / Benchmark"
    elif "utility" in (getattr(opp, "jurisdiction", "") or "").lower() or getattr(opp, "org_type", "") == "utility":
        lifecycle = "Utility Innovation RFP"
    else:
        lifecycle = "Recurring Program Cycle"

    # Win-Rate & Competitiveness Analytics only for top detailed matches
    win_rate = calculate_win_rate_analytics(
        db=db,
        opp=opp,
        profile=profile,
        fit_score=fit_result.overall_score,
        user_cost=profile.project_cost if profile else None,
        applicant_type=profile.applicant_type if profile else None,
    ) if detailed else {}

    match_data = {
        "opportunity_id": opp.id,
        "solicitation_number": opp.solicitation_number,
        "name": opp.name,
        "status": opp.status,
        "lifecycle_status": lifecycle,
        "enrollment_type": opp.enrollment_type,
        "match_type": fit_result.match_type,
        "fit_score": fit_result.overall_score,
        "match_score_pct": getattr(fit_result, "match_score_pct", int(round(fit_result.overall_score * 100))),
        "score_breakdown": getattr(fit_result, "score_breakdown", {}),
        "requirements_checklist": getattr(fit_result, "requirements_checklist", []),
        "restrictions": getattr(fit_result, "restrictions", []),
        "matched_keywords": getattr(fit_result, "matched_keywords", []),
        "total_funding": opp.total_funding,
        "max_per_award": opp.max_per_award,
        "cost_share_pct": opp.cost_share_pct,
        "next_deadline": timeline.get("deadline") if isinstance(timeline, dict) else None,
        "concept_paper_required": opp.concept_paper_required,
        "applicable_components": fit_result.applicable_components,
        "why_it_fits": fit_result.why_it_fits,
        "eligibility": elig_result.to_dict(),
        "fit_dimensions": fit_result.to_dict()["dimensions"],
        "blockers": blockers,
        "unknowns": unknowns,
        "evidence": evidence,
        "last_verified": opp.last_verified_at.isoformat() if opp.last_verified_at else None,
        "detail_url": opp.detail_page_url,
        "portal_url": opp.portal_url,
        # Competitive assessment & Win-Rate
        "assessment": assessment,
        "win_rate_analysis": win_rate,
        # Action timeline
        "timeline": timeline,
        # Multi-agency
        "agency": agency,
        "agency_code": getattr(opp, 'agency_code', None),
        # Proprietary Diligence & Matching Fields
        "statutory_mandates": json.loads(opp.statutory_mandates) if opp.statutory_mandates else [],
        "priority_problem_statements": json.loads(opp.priority_problem_statements) if opp.priority_problem_statements else [],
        "scoring_rubric_weights": json.loads(opp.scoring_rubric_weights) if opp.scoring_rubric_weights else {},
        "teaming_partner_types_sought": json.loads(opp.teaming_partner_types_sought) if opp.teaming_partner_types_sought else [],
        "project_cost_min": opp.project_cost_min,
        "project_cost_max": opp.project_cost_max,
        "cost_share_mandatory": opp.cost_share_mandatory,
        "disadvantaged_community_priority": opp.disadvantaged_community_priority,
    }

    return match_data


def _find_program_matches(db, analysis, profile: ProjectProfile) -> list[dict]:
    """Find matching commercialization and ecosystem programs."""
    programs = db.query(Program).filter_by(active=True).all()
    matches = []

    for prog in programs:
        # Simple keyword matching against program description and focus areas
        desc = (prog.description or "").lower()
        relevance_score = 0

        for tech in profile.technology_areas:
            if tech.lower() in desc:
                relevance_score += 0.3

        for activity in profile.activity_types:
            if activity.lower() in desc:
                relevance_score += 0.2

        # Check target stage match
        if prog.target_stage and profile.estimated_trl:
            trl = profile.estimated_trl
            if prog.target_stage == "early-stage" and trl <= 4:
                relevance_score += 0.2
            elif prog.target_stage == "growth" and 5 <= trl <= 7:
                relevance_score += 0.2
            elif prog.target_stage == "scale-up" and trl >= 7:
                relevance_score += 0.2

        if relevance_score >= 0.2:
            matches.append({
                "program_id": prog.id,
                "name": prog.name,
                "program_type": prog.program_type,
                "description": prog.description,
                "url": prog.url,
                "target_stage": prog.target_stage,
                "relevance_score": round(relevance_score, 2),
                "reasoning_type": "inferred_fit",
            })

            # Save match
            db.add(AnalysisMatch(
                analysis_id=analysis.id,
                program_id=prog.id,
                match_type="commercialization" if prog.program_type == "commercialization" else "component",
                match_category="ecosystem_support",
                fit_score=relevance_score,
                why_it_fits=f"Program targets {prog.target_stage or 'various'} stage projects",
                reasoning_type="inferred_fit",
            ))

    db.commit()
    matches.sort(key=lambda m: m["relevance_score"], reverse=True)
    return matches


def _categorize_matches(matches: list[dict]) -> dict:
    """Categorize matches into groups."""
    return {
        "strong_matches": [m for m in matches if m["match_type"] == "strong"],
        "conditional_matches": [m for m in matches if m["match_type"] == "conditional"],
        "component_matches": [m for m in matches if m["match_type"] == "component"],
        "watchlist": [m for m in matches if m["match_type"] == "watchlist"],
    }


def _build_funding_architecture(matches: list[dict], profile: ProjectProfile) -> list[dict]:
    """Build a project-level funding architecture from matches."""
    architecture = []

    for ws in profile.workstreams:
        # Find best matching opportunity for this workstream
        best_match = None
        best_score = 0

        for match in matches:
            if match["match_type"] in ["strong", "conditional"]:
                # Check if workstream is in applicable components
                ws_name = ws["name"].lower()
                applicable = [c.lower() for c in match.get("applicable_components", [])]
                if any(ws_name in a or a in ws_name for a in applicable) or "full project" in applicable:
                    if match["fit_score"] > best_score:
                        best_match = match
                        best_score = match["fit_score"]

        if best_match:
            architecture.append({
                "workstream": ws["name"],
                "activity_type": ws["activity_type"],
                "opportunity": best_match["solicitation_number"],
                "opportunity_name": best_match["name"],
                "fit_score": best_match["fit_score"],
                "max_award": best_match.get("max_per_award"),
                "reasoning_type": "strategic_option",
            })

    return architecture


def _generate_summary(categorized: dict, programs: list, precedents: list) -> str:
    """Generate a concise summary of results."""
    parts = []

    strong = len(categorized.get("strong_matches", []))
    conditional = len(categorized.get("conditional_matches", []))
    component = len(categorized.get("component_matches", []))
    watchlist = len(categorized.get("watchlist", []))

    if strong > 0:
        parts.append(f"{strong} strong current match{'es' if strong != 1 else ''}")
    if conditional > 0:
        parts.append(f"{conditional} conditional/component opportunit{'ies' if conditional != 1 else 'y'}")
    if component > 0:
        parts.append(f"{component} component/funding-stack option{'s' if component != 1 else ''}")
    if programs:
        parts.append(f"{len(programs)} ecosystem support program{'s' if len(programs) != 1 else ''}")
    if watchlist > 0:
        parts.append(f"{watchlist} watchlist item{'s' if watchlist != 1 else ''}")
    if precedents:
        parts.append(f"{len(precedents)} historical precedent{'s' if len(precedents) != 1 else ''}")

    if not parts:
        return "No strong current funding opportunities identified across indexed agencies for this project."

    return ", ".join(parts) + "."


def _match_type_to_category(match_type: str) -> str:
    """Convert match type to category."""
    mapping = {
        "strong": "current_match",
        "conditional": "conditional_match",
        "component": "component_stack",
        "watchlist": "historical_precedent",
    }
    return mapping.get(match_type, "current_match")


def _build_funding_stacks(db, matches: list[dict]) -> list[dict]:
    """Find funding stacks using opportunity relationships."""
    stacks = []
    
    # Extract IDs of top relevant matched opportunities
    strong_opp_ids = [m["opportunity_id"] for m in matches if m["match_type"] in ["strong", "conditional", "component"]][:25]
    
    if not strong_opp_ids:
        return stacks
        
    rels = db.query(OpportunityRelationship).filter(
        (OpportunityRelationship.source_opp_id.in_(strong_opp_ids)) | 
        (OpportunityRelationship.target_opp_id.in_(strong_opp_ids))
    ).all()
    
    needed_ids = set()
    for rel in rels:
        needed_ids.add(rel.source_opp_id)
        needed_ids.add(rel.target_opp_id)
        
    if not needed_ids:
        return stacks
        
    opps_by_id = {
        opp.id: opp for opp in db.query(Opportunity).filter(Opportunity.id.in_(needed_ids)).all()
    }
    
    for rel in rels:
        if rel.relationship_type in ["stackable", "complementary", "predecessor"]:
            current_opp = opps_by_id.get(rel.source_opp_id)
            other_opp = opps_by_id.get(rel.target_opp_id)
            
            if current_opp and other_opp:
                agencies = list(set([current_opp.agency, other_opp.agency]))
                total = (current_opp.max_per_award or 0) + (other_opp.max_per_award or 0)
                
                stacks.append({
                    "name": f"{rel.relationship_type.title()} Stack",
                    "opportunities": [current_opp.solicitation_number, other_opp.solicitation_number],
                    "agencies": agencies,
                    "rationale": rel.rationale,
                    "total_potential": total,
                    "confidence": rel.confidence
                })
                
    # Deduplicate by opportunity pairs
    unique_stacks = {}
    for s in stacks:
        key = tuple(sorted(s["opportunities"]))
        if key not in unique_stacks:
            unique_stacks[key] = s
            
    return list(unique_stacks.values())

