"""Fit scoring engine.

Evaluates semantic, technical, structural, and regulatory fit between a project and an opportunity.
Computes a quantified match score with granular dimensional breakdowns, requirements checklists,
and domain keyword highlights.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_, text

from app.engine.profile import ProjectProfile
from app.models.opportunity import Opportunity, OpportunityCategory, OpportunityRestriction
from app.models.award import Award
from app.models.project import HistoricalProject

logger = logging.getLogger(__name__)


@dataclass
class FitDimension:
    """Score for a single fit dimension."""
    dimension: str
    score: float  # 0.0 to 1.0
    explanation: str
    confidence: str = "medium"  # high, medium, low


@dataclass
class FitResult:
    """Aggregate fit result for an opportunity with quantified breakdowns."""
    opportunity_id: int
    solicitation_number: str
    overall_score: float
    match_score_pct: int
    match_type: str  # strong, conditional, component, watchlist
    dimensions: list[FitDimension]
    score_breakdown: dict = field(default_factory=dict)
    requirements_checklist: list[dict] = field(default_factory=list)
    restrictions: list[dict] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)
    applicable_components: list[str] = field(default_factory=list)
    why_it_fits: str = ""

    def to_dict(self) -> dict:
        return {
            "overall_score": round(self.overall_score, 3),
            "match_score_pct": self.match_score_pct,
            "match_type": self.match_type,
            "applicable_components": self.applicable_components,
            "why_it_fits": self.why_it_fits,
            "score_breakdown": self.score_breakdown,
            "requirements_checklist": self.requirements_checklist,
            "restrictions": self.restrictions,
            "matched_keywords": self.matched_keywords,
            "dimensions": [
                {
                    "dimension": d.dimension,
                    "score": round(d.score, 3),
                    "explanation": d.explanation,
                    "confidence": d.confidence,
                }
                for d in self.dimensions
            ],
        }


# Taxonomy alias mapping for intelligent matching
TAXONOMY_ALIASES: dict[str, list[str]] = {
    "Data Centers & Computing": [
        "data center", "datacenter", "compute", "computing", "cooling", "immersion",
        "clean energy innovation", "advanced tech", "power electronics", "smart power",
        "grid modernization", "electronics, photonics", "information technology",
    ],
    "Grid Modernization": [
        "grid modernization", "smart power", "smart grid", "power systems", "distribution",
        "transmission", "microgrid", "electric grid", "grid resilience", "der", "derms",
        "load management", "power electronics", "voltage", "substation",
    ],
    "Energy Storage": [
        "energy storage", "battery", "batteries", "bess", "ldes", "lithium", "flow battery",
        "storage & chemical", "bulk energy storage", "storage",
    ],
    "Solar": [
        "solar", "photovoltaic", "pv", "solar storage", "solar photovoltaics",
    ],
    "Building Electrification": [
        "building electrification", "buildings", "hvac", "heat pump", "space heating",
        "energy efficiency", "thermal",
    ],
    "Clean Transportation": [
        "clean transportation", "electric vehicles", "ev", "transit", "mobility", "fleet",
        "v2g", "charging",
    ],
    "Hydrogen & Alternative Fuels": [
        "hydrogen", "alternative fuels", "fuel cell", "electrolyzer", "clean fuels",
    ],
    "Industrial Decarbonization": [
        "industrial decarbonization", "industrial", "process heat", "manufacturing", "waste heat",
    ],
    "Clean Energy Manufacturing": [
        "clean energy manufacturing", "manufacturing", "fabrication", "supply chain",
        "semiconductor", "packaging",
    ],
    "Sustainable Materials & Circular Economy": [
        "sustainable materials", "circular economy", "textile", "textiles", "garment", "garments",
        "apparel", "circular fashion", "fabric", "fabrics", "bio-based dye", "dyeing", "natural fiber",
        "recycled fiber", "fiber recycling", "biomaterials", "textile recycling", "sustainable packaging",
        "bioplastics", "waste valorization",
    ],
    "Marine & Hydrokinetic": [
        "marine", "hydrokinetic", "wave energy", "tidal energy", "ocean energy", "water power",
        "mhk", "marine hydrokinetic", "ocean current", "subsea", "marine energy",
    ],
}

ACTIVITY_ALIASES: dict[str, list[str]] = {
    "R&D": ["applied r&d", "fundamental r&d", "research", "r&d", "innovation", "development", "novel"],
    "Demonstration": ["demonstration", "pilot", "field test", "demo", "deployment & infrastructure"],
    "Deployment": ["deployment", "infrastructure", "installation", "scale", "commercialization & scale"],
    "Testing & Validation": ["testing & validation", "testing", "validation", "lab test", "certification"],
    "Software & Controls": ["software & controls", "software", "controls", "algorithms", "analytics", "ai", "cyber"],
    "Feasibility Study": ["feasibility study", "feasibility", "assessment", "analysis", "study"],
    "Product Development": ["product development", "prototype", "design", "engineering"],
    "Workforce Development": ["workforce development", "technical assistance", "training", "education"],
}

EPA_REGION_STATES: dict[str, list[str]] = {
    "epa_region_1": ["CT", "ME", "MA", "NH", "RI", "VT"],
    "epa_r1": ["CT", "ME", "MA", "NH", "RI", "VT"],
    "epa_region_2": ["NY", "NJ", "PR", "VI"],
    "epa_r2": ["NY", "NJ", "PR", "VI"],
    "epa_region_3": ["DC", "DE", "MD", "PA", "VA", "WV"],
    "epa_r3": ["DC", "DE", "MD", "PA", "VA", "WV"],
    "epa_region_4": ["AL", "FL", "GA", "KY", "MS", "NC", "SC", "TN"],
    "epa_r4": ["AL", "FL", "GA", "KY", "MS", "NC", "SC", "TN"],
    "epa_region_5": ["IL", "IN", "MI", "MN", "OH", "WI"],
    "epa_r5": ["IL", "IN", "MI", "MN", "OH", "WI"],
    "epa_region_6": ["AR", "LA", "NM", "OK", "TX"],
    "epa_r6": ["AR", "LA", "NM", "OK", "TX"],
    "epa_region_7": ["IA", "KS", "MO", "NE"],
    "epa_r7": ["IA", "KS", "MO", "NE"],
    "epa_region_8": ["CO", "MT", "ND", "SD", "UT", "WY"],
    "epa_r8": ["CO", "MT", "ND", "SD", "UT", "WY"],
    "epa_region_9": ["AZ", "CA", "HI", "NV"],
    "epa_r9": ["AZ", "CA", "HI", "NV"],
    "epa_region_10": ["AK", "ID", "OR", "WA"],
    "epa_r10": ["AK", "ID", "OR", "WA"],
    "regional_new_england": ["CT", "ME", "MA", "NH", "RI", "VT"],
    "regional_midwest": ["MN", "WI", "IA", "ND", "SD"],
}

# Module-level pre-compiled regexes for high-performance compatibility gating
_RE_RES_PROGRAM = re.compile(
    r'\b(residential\s+(?:rebate|incentive|program|storage|clean\s+heat|microgrid|energy\s+code)|'
    r'homeowner|single[\s-]family|weatherization\s+assistance|weatherization\s+formula|'
    r'whole[\s-]house|hvacr\s+to\s+home\s+performance|residential\s+wood\s+heater|'
    r'empower\s*new\s*york|empower\+|geothermal\s+heat\s+pump\s+rebates)\b',
    re.IGNORECASE
)
_RE_INDUSTRIAL_OPP = re.compile(
    r'\b(industrial\s+decarbonization|clean\s+energy\s+manufacturing|manufacturing\s+plant|'
    r'chemical\s+manufacturing|green\s+steel|low-carbon\s+cement)\b',
    re.IGNORECASE
)
_RE_FOSSIL_SOLID_COMBUSTION = re.compile(
    r'\b(coal\s+value\s+chain|coal-based|fossil\s+feedstock|coal\s+combustion|coal\s+mine|'
    r'wood\s+heater|wood\s+stove|biomass\s+combustion\s+for\s+cooking)\b',
    re.IGNORECASE
)
_RE_NUCLEAR_OPP = re.compile(
    r'\b(nuclear\s+reactor|small\s+modular\s+reactor|\bsmr\b|fission|fusion|uranium|haleu)\b',
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
_RE_DOWNSTREAM_INSTALLATION_REBATE = re.compile(
    r'\b(incentives?\s+for\s+the\s+installation|market\s+acceleration\s+incentives?|'
    r'residential\s+and\s+(?:retail|nonresidential)\s+incentive|'
    r'contractors\s+and\s+builders\s+to\s+install|rebates?\s+for\s+installing)\b',
    re.IGNORECASE
)
_RE_MHK_OPP = re.compile(
    r'\b(marine\s+hydrokinetic|wave\s+energy|tidal\s+energy|ocean\s+energy|water\s+power|mhk|'
    r'river\s+hydrokinetic|subsea\s+power|wave\s+power|tidal\s+power)\b',
    re.IGNORECASE
)
_RE_TRANS_OPP = re.compile(
    r'\b(electric\s+vehicles?|vehicle\s+technologies|advanced\s+vehicle\s+engine|charging\s+infrastructure|'
    r'charge\s+ready|fleet\s+electrification|transit\s+bus|medium[\s-]duty\s+vehicles?|heavy[\s-]duty\s+vehicles?|'
    r'powertrain|evse|otaq|national\s+clean\s+diesel|diesel\s+emissions\s+reduction|clean\s+school\s+bus)\b',
    re.IGNORECASE
)
_RE_WIND_OPP = re.compile(
    r'\b(wind\s+manufacturing:\s+larger\s+blades|wind\s+turbine\s+blade|offshore\s+wind\s+mooring|'
    r'wind\s+energy\s+technologies\s+office|wind\s+turbine\s+aerodynamics)\b',
    re.IGNORECASE
)
_RE_SOLAR_OPP = re.compile(
    r'\b(concentrating\s+solar\s+power|sunshot\s+concentrating|perovskite\s+solar\s+cells?|bifacial\s+pv\s+cells?)\b',
    re.IGNORECASE
)
_RE_GRID_INFRA_OPP = re.compile(
    r'\b(grid\s+enhancing\s+technologies|transmission\s+line\s+capacity|substation\s+automation|'
    r'synchrophasor|utility\s+feeder|high\s+voltage\s+direct\s+current|\bhvdc\b|dynamic\s+line\s+rating)\b',
    re.IGNORECASE
)
_RE_H2_OPP = re.compile(
    r'\b(hydrogen\s+electrolyzer|clean\s+hydrogen\s+production\s+standard|proton\s+exchange\s+membrane\s+electrolyzer|'
    r'solid\s+oxide\s+electrolyzer|\bsoec\b|\bpem\s+electrolysis\b)\b',
    re.IGNORECASE
)
_RE_DAC_OPP = re.compile(
    r'\b(direct\s+air\s+capture\s+regional\s+hub|subsurface\s+co2\s+storage|geologic\s+carbon\s+sequestration|'
    r'point-source\s+carbon\s+capture)\b',
    re.IGNORECASE
)


def get_adaptive_weights(profile: ProjectProfile) -> dict[str, float]:
    """Dynamically computes archetype-calibrated weights based on project TRL and CapEx."""
    trl = profile.estimated_trl or 5
    cost = profile.project_cost or 2_000_000.0

    if trl <= 3:
        # Early-Stage Fundamental / Applied R&D
        return {
            "keyword_relevance": 0.30,
            "technology_fit": 0.45,
            "activity_fit": 0.15,
            "stage_requirements": 0.05,
            "funding_scale": 0.05,
        }
    elif trl >= 7 or cost >= 10_000_000:
        # Commercial Demonstration & Deployment Archetype
        return {
            "keyword_relevance": 0.25,
            "technology_fit": 0.25,
            "activity_fit": 0.20,
            "stage_requirements": 0.15,
            "funding_scale": 0.15,
        }
    else:
        # Field Pilot & Demonstration Archetype
        return {
            "keyword_relevance": 0.35,
            "technology_fit": 0.30,
            "activity_fit": 0.15,
            "stage_requirements": 0.10,
            "funding_scale": 0.10,
        }


def evaluate_fit(
    db: Session,
    opportunity: Opportunity,
    profile: ProjectProfile,
) -> FitResult:
    """Evaluate full fit between a project and an opportunity."""

    # Multi-Dimensional Alignment Multipliers: Geography, Sector, Fuel, Stage, Domain
    geo_multiplier, geo_reason = _score_geographic_jurisdiction_alignment(opportunity, profile)
    if geo_multiplier == 0.0:
        return FitResult(
            opportunity_id=opportunity.id,
            solicitation_number=opportunity.solicitation_number,
            overall_score=0.05,
            match_score_pct=5,
            match_type="watchlist",
            dimensions=[],
            score_breakdown={},
            requirements_checklist=[],
            restrictions=[],
            matched_keywords=[],
            applicable_components=[],
            why_it_fits="",
        )

    # 1. Keyword & Topic Relevance
    kw_fit, matched_kws = _score_keyword_topic_relevance(opportunity, profile)

    # In-memory Dense Vector Hybrid Blending
    dense_sim = getattr(opportunity, "_dense_sim", None)
    if dense_sim is not None:
        blended_kw = 0.40 * kw_fit.score + 0.60 * dense_sim
        kw_fit = FitDimension(
            "keyword_relevance",
            min(1.0, max(0.05, blended_kw)),
            f"{kw_fit.explanation} (Dense Semantic Proximity: {dense_sim:.2f})",
            "high" if dense_sim >= 0.60 else kw_fit.confidence
        )

    # 2. Technology & Sector Taxonomy Fit
    tech_fit, matched_techs = _score_technology_taxonomy_fit(db, opportunity, profile)

    # 3. Activity & Innovation Stage Fit
    act_fit, matched_acts = _score_activity_fit(db, opportunity, profile)

    # 4. Stage & Requirements Alignment
    stage_fit, req_checklist = _score_stage_and_requirements(opportunity, profile)

    # 5. Funding Scale Fit
    fund_fit = _score_funding_fit(opportunity, profile)

    dimensions = [kw_fit, tech_fit, act_fit, stage_fit, fund_fit]

    # Archetype-Adaptive Dynamic Weights (Cached on Profile)
    weights = getattr(profile, "_cached_adaptive_weights", None)
    if weights is None:
        weights = get_adaptive_weights(profile)
        profile._cached_adaptive_weights = weights

    total_weight = sum(weights.get(d.dimension, 0.2) for d in dimensions)
    base_overall = sum(
        d.score * weights.get(d.dimension, 0.2) for d in dimensions
    ) / total_weight if total_weight > 0 else 0.0

    # 6. Justice40 & Disadvantaged Communities Alignment Bonus
    dac_bonus = 0.0
    opp_text = getattr(opportunity, "_search_corpus_lower", "") or ""
    if profile.dac_components or (profile.location and any(d in profile.location.lower() for d in ["dac", "disadvantaged", "environmental justice", "ej", "bronx", "brooklyn"])):
        if any(j in opp_text for j in ["justice40", "disadvantaged", "community benefit", "environmental justice", "cbp"]):
            dac_bonus = 0.05

    sector_multiplier, sector_reason = _score_sector_compatibility(opportunity, profile)
    fuel_multiplier, fuel_reason = _score_fuel_compatibility(opportunity, profile)
    stage_multiplier, stage_reason = _score_stage_activity_compatibility(opportunity, profile)
    domain_multiplier, domain_reason = _score_domain_incompatibility(opportunity, profile)

    alignment_multiplier = geo_multiplier * sector_multiplier * fuel_multiplier * stage_multiplier * domain_multiplier
    overall = min(1.0, max(0.05, (base_overall + dac_bonus) * alignment_multiplier))

    # Match score percentage (0-100)
    match_score_pct = int(round(min(1.0, max(0.05, overall)) * 100))

    # Fast-Path: Skip heavy dictionary allocations, string generators, and regexes for non-viable matches (<0.15)
    if overall < 0.15:
        return FitResult(
            opportunity_id=opportunity.id,
            solicitation_number=opportunity.solicitation_number,
            overall_score=overall,
            match_score_pct=match_score_pct,
            match_type="watchlist",
            dimensions=dimensions,
            score_breakdown={},
            requirements_checklist=[],
            restrictions=[],
            matched_keywords=[],
            applicable_components=[],
            why_it_fits="",
        )

    # Determine match type tier
    if overall >= 0.70:
        match_type = "strong"
    elif overall >= 0.45:
        match_type = "conditional"
    elif overall >= 0.30:
        match_type = "component"
    else:
        match_type = "watchlist"

    # Applicable components
    applicable = _find_applicable_components(opportunity, profile)

    # Restrictions
    restrictions = _extract_restrictions(opportunity, profile)

    # Detailed Score Breakdown
    score_breakdown = {
        "overall_pct": match_score_pct,
        "geographic_alignment": {
            "multiplier": round(geo_multiplier, 2),
            "explanation": geo_reason,
        },
        "sector_alignment": {
            "multiplier": round(sector_multiplier, 2),
            "explanation": sector_reason,
        },
        "fuel_alignment": {
            "multiplier": round(fuel_multiplier, 2),
            "explanation": fuel_reason,
        },
        "stage_activity_alignment": {
            "multiplier": round(stage_multiplier, 2),
            "explanation": stage_reason,
        },
        "domain_alignment": {
            "multiplier": round(domain_multiplier, 2),
            "explanation": domain_reason,
        },
        "keyword_relevance": {
            "score": round(kw_fit.score, 2),
            "weight_pct": int(weights.get("keyword_relevance", 0.35) * 100),
            "explanation": kw_fit.explanation,
            "matched_terms": matched_kws[:8],
        },
        "technology_alignment": {
            "score": round(tech_fit.score, 2),
            "weight_pct": int(weights.get("technology_fit", 0.30) * 100),
            "explanation": tech_fit.explanation,
            "matched_areas": matched_techs,
        },
        "activity_stage": {
            "score": round(act_fit.score, 2),
            "weight_pct": int(weights.get("activity_fit", 0.15) * 100),
            "explanation": act_fit.explanation,
            "matched_activities": matched_acts,
        },
        "requirements_fit": {
            "score": round(stage_fit.score, 2),
            "weight_pct": int(weights.get("stage_requirements", 0.10) * 100),
            "explanation": stage_fit.explanation,
        },
        "funding_scale": {
            "score": round(fund_fit.score, 2),
            "weight_pct": int(weights.get("funding_scale", 0.10) * 100),
            "explanation": fund_fit.explanation,
        },
        "justice40_dac_bonus": round(dac_bonus, 2),
    }

    # Generate human-readable explanation
    why = _generate_fit_explanation(
        opportunity, profile, dimensions, applicable, matched_kws, matched_techs
    )

    return FitResult(
        opportunity_id=opportunity.id,
        solicitation_number=opportunity.solicitation_number,
        overall_score=overall,
        match_score_pct=match_score_pct,
        match_type=match_type,
        dimensions=dimensions,
        score_breakdown=score_breakdown,
        requirements_checklist=req_checklist,
        restrictions=restrictions,
        matched_keywords=matched_kws[:12],
        applicable_components=applicable,
        why_it_fits=why,
    )


GENERIC_MATCH_STOPWORDS = {
    "sustainable", "sustainability", "production", "system", "systems", "project", "projects",
    "facility", "facilities", "solution", "solutions", "technology", "technologies",
    "development", "innovation", "innovative", "advanced", "program", "programs",
    "new", "york", "state", "city", "nyc", "clean", "energy", "commercial",
    "demonstration", "deployment", "pilot", "scale", "scale-up", "scaleup",
    "initiative", "efficient", "efficiency", "support", "grant", "grants",
    "opportunity", "opportunities", "funding", "market", "applications", "application",
    "management", "process", "processes", "infrastructure", "environmental", "generation",
    "sector", "sectors", "area", "areas", "center", "centers", "national", "research",
}


def _score_keyword_topic_relevance(opp: Opportunity, profile: ProjectProfile) -> tuple[FitDimension, list[str]]:
    """Score text, topic, and domain keyword relevance against solicitation metadata."""
    opp_text_corpus = getattr(opp, "_search_corpus_lower", None)
    if opp_text_corpus is None:
        opp_text_corpus = (
            (opp.name or "") + " " +
            (opp.short_description or "") + " " +
            (opp.objectives or "") + " " +
            (opp.keywords or "") + " " +
            (opp.selection_criteria or "")
        ).lower()

    if not opp_text_corpus.strip():
        return FitDimension("keyword_relevance", 0.2, "Limited solicitation text available", "low"), []

    if not hasattr(profile, "_cached_search_terms"):
        all_search_terms = []
        if hasattr(profile, "extracted_phrases") and profile.extracted_phrases:
            all_search_terms.extend(profile.extracted_phrases)
        if hasattr(profile, "keywords") and profile.keywords:
            all_search_terms.extend(profile.keywords)
        if profile.technology_areas:
            all_search_terms.extend(profile.technology_areas)
        profile._cached_search_terms = [
            t.lower().strip() for t in dict.fromkeys(all_search_terms)
            if t and len(t.strip()) > 2 and (" " in t or t.lower().strip() not in GENERIC_MATCH_STOPWORDS)
        ]

    all_search_terms = profile._cached_search_terms

    if not all_search_terms:
        return FitDimension("keyword_relevance", 0.3, "Standard domain evaluation", "low"), []

    matched = []
    phrase_matches = []
    
    for term in all_search_terms:
        if term in opp_text_corpus:
            matched.append(term)
            if " " in term:
                phrase_matches.append(term)

    # Check title specifically for high-impact keywords (excluding generic stopwords)
    title_text = getattr(opp, "_name_lower", None) or (opp.name or "").lower()
    title_matches = [
        t for t in all_search_terms
        if t in title_text
    ]

    # Calibrated score calculation
    if phrase_matches:
        base_score = 0.55 + min(0.35, 0.15 * len(phrase_matches))
        if title_matches:
            base_score += min(0.15, 0.08 * len(title_matches))
    elif matched:
        base_score = 0.20 + min(0.40, 0.06 * len(matched))
        if title_matches:
            base_score += min(0.15, 0.08 * len(title_matches))
    else:
        base_score = 0.10

    score = min(1.0, max(0.05, base_score))

    if phrase_matches:
        detail = f"Matched core key phrases: {', '.join(phrase_matches[:4])}"
        conf = "high"
    elif matched:
        detail = f"Matched domain keywords: {', '.join(matched[:6])}"
        conf = "medium"
    else:
        detail = "No primary domain keywords matched"
        conf = "low"

    return FitDimension("keyword_relevance", score, detail, conf), matched


def _score_technology_taxonomy_fit(db: Session, opp: Opportunity, profile: ProjectProfile) -> tuple[FitDimension, list[str]]:
    """Score technology area alignment using taxonomy aliases and categories."""
    if not profile.technology_areas:
        return FitDimension("technology_fit", 0.5, "No specific technology areas restricted", "low"), []

    # Get opportunity categories
    opp_cat_str = getattr(opp, "_tech_cat_str", None)
    if opp_cat_str is None:
        opp_cat_values = getattr(opp, "_tech_cat_values", None)
        if opp_cat_values is None:
            cached_cats = getattr(opp, "_cached_categories", getattr(opp, "categories", None))
            if cached_cats is not None:
                tech_cats = [c for c in cached_cats if getattr(c, "category_type", None) in ("technology", "sector", "fuel")]
            else:
                tech_cats = db.query(OpportunityCategory).filter(
                    OpportunityCategory.opportunity_id == opp.id,
                    OpportunityCategory.category_type.in_(["technology", "sector", "fuel"])
                ).all()
            opp_cat_values = [getattr(c, "category_value", "").lower() for c in tech_cats]
        opp_cat_str = " ".join(opp_cat_values)

    opp_text = getattr(opp, "_search_corpus_lower", None)
    if opp_text is None:
        opp_text = ((opp.name or "") + " " + (opp.short_description or "") + " " + (opp.keywords or "")).lower()

    if not hasattr(profile, "_cached_tech_aliases"):
        profile._cached_tech_aliases = [
            (proj_tech, proj_tech.lower(), TAXONOMY_ALIASES.get(proj_tech, [proj_tech.lower()]))
            for proj_tech in profile.technology_areas
        ]

    matched_techs = []
    match_quality = 0.0

    for proj_tech, p_tech_lower, aliases in profile._cached_tech_aliases:
        # Check exact or partial category match in joined category string
        cat_hit = False
        if p_tech_lower in opp_cat_str:
            matched_techs.append(proj_tech)
            match_quality += 0.45
            cat_hit = True
        elif any(alias in opp_cat_str for alias in aliases):
            matched_techs.append(f"{proj_tech} (Taxonomy Match)")
            match_quality += 0.35
            cat_hit = True

        # If not in category table, check description/title text
        if not cat_hit:
            if any(alias in opp_text for alias in aliases):
                matched_techs.append(proj_tech)
                match_quality += 0.30

    matched_techs = list(dict.fromkeys(matched_techs))
    
    if matched_techs:
        score = min(1.0, 0.40 + match_quality)
        explanation = f"Aligned technology areas: {', '.join(matched_techs[:4])}"
        confidence = "high"
    else:
        score = 0.25
        explanation = "Secondary / adjacent technology alignment"
        confidence = "medium"

    return FitDimension("technology_fit", score, explanation, confidence), matched_techs


def _score_activity_fit(db: Session, opp: Opportunity, profile: ProjectProfile) -> tuple[FitDimension, list[str]]:
    """Score activity type alignment (R&D, Demonstration, Deployment, Testing)."""
    if not profile.activity_types:
        return FitDimension("activity_fit", 0.6, "Flexible across activity types", "low"), []

    opp_act_str = getattr(opp, "_act_cat_str", None)
    if opp_act_str is None:
        opp_acts = getattr(opp, "_act_cat_values", None)
        if opp_acts is None:
            cached_cats = getattr(opp, "_cached_categories", getattr(opp, "categories", None))
            if cached_cats is not None:
                act_cats = [c for c in cached_cats if getattr(c, "category_type", None) == "activity"]
            else:
                act_cats = db.query(OpportunityCategory).filter_by(
                    opportunity_id=opp.id, category_type="activity"
                ).all()
            opp_acts = [getattr(c, "category_value", "").lower() for c in act_cats]
        opp_act_str = " ".join(opp_acts)

    opp_text = getattr(opp, "_search_corpus_lower", None)
    if opp_text is None:
        opp_text = ((opp.name or "") + " " + (opp.short_description or "")).lower()

    if not hasattr(profile, "_cached_act_aliases"):
        profile._cached_act_aliases = [
            (act, ACTIVITY_ALIASES.get(act, [act.lower()]))
            for act in profile.activity_types
        ]

    matched_acts = []
    act_score = 0.3

    for act, aliases in profile._cached_act_aliases:
        # Check categories
        if any(alias in opp_act_str for alias in aliases):
            matched_acts.append(act)
            act_score += 0.30
        elif any(alias in opp_text for alias in aliases):
            matched_acts.append(act)
            act_score += 0.20

    matched_acts = list(dict.fromkeys(matched_acts))
    score = min(1.0, max(0.3, act_score))

    if matched_acts:
        explanation = f"Matched activity scopes: {', '.join(matched_acts[:3])}"
        confidence = "high"
    else:
        explanation = "General project activity scope"
        confidence = "medium"

    return FitDimension("activity_fit", score, explanation, confidence), matched_acts


def _score_stage_and_requirements(opp: Opportunity, profile: ProjectProfile) -> tuple[FitDimension, list[dict]]:
    """Evaluate TRL stage, applicant eligibility, geography, and produce checklist."""
    checklist = []
    score_components = []

    # 1. Applicant Type Check
    if profile.applicant_type:
        app_type = profile.applicant_type.lower()
        if opp.solicitation_category and "university" in opp.solicitation_category.lower() and app_type == "business":
            checklist.append({
                "name": "Applicant Type",
                "status": "note",
                "reason": "University lead often required; commercial subcontracts/partnerships eligible",
            })
            score_components.append(0.70)
        else:
            checklist.append({
                "name": "Applicant Eligibility",
                "status": "pass",
                "reason": f"Eligible entity type: {profile.applicant_type.capitalize()}",
            })
            score_components.append(0.95)
    else:
        checklist.append({
            "name": "Applicant Eligibility",
            "status": "pass",
            "reason": "Open to standard industry & research applicants",
        })
        score_components.append(0.85)

    # 2. Technology Readiness Level (TRL)
    if profile.estimated_trl is not None:
        trl = profile.estimated_trl
        min_trl = getattr(opp, "target_trl_min", None) or 1
        max_trl = getattr(opp, "target_trl_max", None) or 9

        if min_trl <= trl <= max_trl:
            checklist.append({
                "name": "Technology Readiness (TRL)",
                "status": "pass",
                "reason": f"Project TRL {trl} falls within target scope (TRL {min_trl}–{max_trl})",
            })
            score_components.append(0.95)
        elif trl < min_trl:
            checklist.append({
                "name": "Technology Readiness (TRL)",
                "status": "note",
                "reason": f"Project TRL {trl} is early; pilot phase recommended for target TRL {min_trl}+",
            })
            score_components.append(0.65)
        else:
            checklist.append({
                "name": "Technology Readiness (TRL)",
                "status": "note",
                "reason": f"Project TRL {trl} is advanced; focus proposal on market demonstration",
            })
            score_components.append(0.75)
    else:
        checklist.append({
            "name": "Technology Readiness (TRL)",
            "status": "pass",
            "reason": "Accommodates early R&D through demonstration stages",
        })
        score_components.append(0.85)

    # 3. Geographic / Jurisdiction Nexus
    jurisdiction = getattr(opp, "jurisdiction", "US_FED") or "US_FED"
    loc = (profile.target_location or profile.ny_location or "").upper()

    if jurisdiction in ("US_FED", "federal", "national") or opp.agency in ("DOE", "NSF", "ARPA-E", "EPA", "DOD", "USDA", "NIST"):
        checklist.append({
            "name": "Geographic Nexus",
            "status": "pass",
            "reason": "Federal solicitation — nationwide eligibility (US entities)",
        })
        score_components.append(1.0)
    elif "NY" in jurisdiction or opp.agency in ("NYSERDA", "Con Edison", "National Grid", "NYPA", "LIPA", "Central Hudson", "NYSEG", "RG&E"):
        if loc in ("NY", "NEW YORK", "NYC") or not loc or loc == "US":
            checklist.append({
                "name": "New York Nexus",
                "status": "pass",
                "reason": "New York State project activity or utility customer benefit",
            })
            score_components.append(0.90)
        else:
            checklist.append({
                "name": "New York Nexus",
                "status": "note",
                "reason": f"Project in {loc}; New York demonstration site or partner required",
            })
            score_components.append(0.60)
    elif "CA" in jurisdiction or opp.agency in ("CEC", "MassCEC", "PG&E", "SCE", "SDG&E"):
        checklist.append({
            "name": f"{opp.agency} Jurisdiction",
            "status": "pass" if (loc in ("CA", "MA") or not loc or loc == "US") else "note",
            "reason": f"State/Utility program — in-state demonstration or economic benefit",
        })
        score_components.append(0.85 if loc in ("CA", "MA", "US") else 0.65)
    else:
        checklist.append({
            "name": "Jurisdiction / Scope",
            "status": "pass",
            "reason": f"Standard institutional eligibility ({opp.agency})",
        })
        score_components.append(0.85)

    # 4. Cost Share Requirement
    cost_share = getattr(opp, "cost_share_pct", None)
    if cost_share and cost_share > 0:
        checklist.append({
            "name": "Cost Share Requirement",
            "status": "note",
            "reason": f"Requires {cost_share}% non-federal / applicant matching funds",
        })
    else:
        checklist.append({
            "name": "Cost Share Requirement",
            "status": "pass",
            "reason": "No mandatory cost-share requirement specified (0% cost share)",
        })

    avg_score = sum(score_components) / len(score_components) if score_components else 0.8
    pass_count = sum(1 for c in checklist if c["status"] == "pass")
    explanation = f"{pass_count}/{len(checklist)} institutional requirements fully verified"

    return FitDimension("stage_requirements", avg_score, explanation, "high"), checklist


def _score_geographic_jurisdiction_alignment(
    opp: Opportunity, profile: ProjectProfile
) -> tuple[float, str]:
    """
    Evaluates state geography and utility service territory alignment:
    - Tier 1 (In-State Alignment): Sponsored by an agency or local utility in the project's target state (1.25x priority).
    - Tier 2 (Federal Nationwide): Federal solicitations open nationwide (1.05x priority).
    - Tier 2b (Federal Regional - e.g. EPA Region 1, Region 3): Strictly restricted to states within that specific region (0.0x if out of region).
    - Tier 3 (National Unrestricted / Philanthropic Funds): Open to multi-state/national projects (0.95x - 1.0x).
    - Tier 4 (Out-of-State State Agency): Strictly penalizes state programs from outside the project's jurisdiction (0.15x / 0.0x).
    """
    if not hasattr(profile, "_cached_proj_state"):
        loc_lower = (profile.target_location or profile.ny_location or profile.location or "").lower()
        proj_st = "NY"
        if any(w in loc_lower for w in ["ca", "california", "los angeles", "san francisco", "sacramento", "san diego", "silicon valley"]):
            proj_st = "CA"
        elif any(w in loc_lower for w in ["ma", "massachusetts", "boston", "cambridge"]):
            proj_st = "MA"
        elif any(w in loc_lower for w in ["tx", "texas", "houston", "austin", "dallas"]):
            proj_st = "TX"
        elif any(w in loc_lower for w in ["co", "colorado", "denver", "boulder"]):
            proj_st = "CO"
        elif any(w in loc_lower for w in ["il", "illinois", "chicago"]):
            proj_st = "IL"
        elif any(w in loc_lower for w in ["nj", "new jersey", "newark"]):
            proj_st = "NJ"
        elif any(w in loc_lower for w in ["wa", "washington", "seattle"]):
            proj_st = "WA"
        elif any(w in loc_lower for w in ["pa", "pennsylvania", "philadelphia", "pittsburgh"]):
            proj_st = "PA"
        elif any(w in loc_lower for w in ["oh", "ohio", "columbus", "cleveland"]):
            proj_st = "OH"
        elif any(w in loc_lower for w in ["mi", "michigan", "detroit"]):
            proj_st = "MI"
        elif any(w in loc_lower for w in ["md", "maryland", "baltimore"]):
            proj_st = "MD"
        elif any(w in loc_lower for w in ["mn", "minnesota", "minneapolis"]):
            proj_st = "MN"
        elif any(w in loc_lower for w in ["va", "virginia", "richmond"]):
            proj_st = "VA"
        elif any(w in loc_lower for w in ["wi", "wisconsin", "milwaukee", "madison"]):
            proj_st = "WI"
        elif any(w in loc_lower for w in ["ny", "new york", "nyc", "brooklyn", "manhattan", "queens", "bronx", "staten island", "albany", "buffalo", "rochester", "syracuse", "yonkers", "long island"]):
            proj_st = "NY"
        profile._cached_proj_state = proj_st

    proj_state = profile._cached_proj_state

    # Fast cached EPA region check
    epa_region = getattr(opp, "_epa_region", None)
    if epa_region:
        r_states = EPA_REGION_STATES.get(epa_region, [])
        if proj_state in r_states:
            return 1.20, f"Direct Regional Federal Alignment: Solicitation covers {epa_region.upper()} (including {proj_state})"
        else:
            return 0.0, f"Out-of-Region Federal Program: Restricted to {epa_region.upper()} ({', '.join(r_states)}), project located in {proj_state}"

    # Fast cached State Agency / In-State Utility check
    st_agency = getattr(opp, "_state_agency_state", None)
    if st_agency:
        if proj_state == st_agency:
            return 1.25, f"Direct In-State Alignment: Sponsored by {st_agency} State agency or local service territory utility"
        else:
            return 0.05, f"Out-of-State Jurisdiction ({opp.agency}): Restricted to in-state projects in other jurisdictions"

    # Fast cached Federal check
    if getattr(opp, "_is_federal", False):
        return 1.05, "Federal solicitation — nationwide eligibility with federal funding priority"

    # Fast cached National Unrestricted / Philanthropic check
    if getattr(opp, "_is_national_unrestricted", False):
        return 0.95, f"National / Multi-State Innovation Sponsor ({opp.agency}): Open to multi-jurisdictional innovation projects"

    agency = (opp.agency or "").strip()
    agency_lower = agency.lower()
    jurisdiction = (getattr(opp, "jurisdiction", "") or "").lower()
    geo_scope = (getattr(opp, "geographic_scope", "") or "").lower()

    # 1. Regional Federal / EPA Program Check (Strict Regional Filter)
    for r_key, r_states in EPA_REGION_STATES.items():
        if geo_scope == r_key or jurisdiction == r_key:
            if proj_state in r_states:
                return 1.20, f"Direct Regional Federal Alignment: Solicitation covers {r_key.upper()} (including {proj_state})"
            else:
                return 0.0, f"Out-of-Region Federal Program: Restricted to {r_key.upper()} ({', '.join(r_states)}), project located in {proj_state}"

    # 2. In-State Alignment (Tier 1) - State Agencies & Local Utilities
    if proj_state == "NY":
        if any(ny in agency_lower for ny in ["nyserda", "new york", "con edison", "coned", "national grid", "nypa", "lipa", "central hudson", "nyseg", "rg&e", "orange & rockland", "orange and rockland", "empire state development", "fortis", "joint utilities"]) or "state_ny" in jurisdiction or "ny" in geo_scope:
            return 1.25, "Direct In-State Alignment: Sponsored by New York State agency or local service territory utility"
    elif proj_state == "CA":
        if any(ca in agency_lower for ca in ["cec", "california", "pg&e", "sce", "smud", "ladwp", "sdg&e", "pacific gas", "southern california", "san diego gas", "sacramento municipal", "go-biz", "sempra", "cpuc", "carb"]) or "state_ca" in jurisdiction or "ca" in geo_scope:
            return 1.25, "Direct In-State Alignment: Sponsored by California State agency or local service territory utility"
    elif proj_state == "MA":
        if any(ma in agency_lower for ma in ["masscec", "massachusetts", "eversource", "national grid massachusetts", "massventures", "doer"]) or "state_ma" in jurisdiction or "ma" in geo_scope:
            return 1.25, "Direct In-State Alignment: Sponsored by Massachusetts State agency or local service territory utility"
    elif proj_state == "TX":
        if any(tx in agency_lower for tx in ["texas", "oncor", "centerpoint", "cps energy", "austin energy", "seco"]) or "state_tx" in jurisdiction or "tx" in geo_scope:
            return 1.25, "Direct In-State Alignment: Sponsored by Texas agency or local service territory utility"
    elif proj_state == "CO":
        if any(co in agency_lower for co in ["colorado", "tri-state", "xcel energy", "public service company of colorado", "ceo", "oedit"]) or "state_co" in jurisdiction or "co" in geo_scope:
            return 1.25, "Direct In-State Alignment: Sponsored by Colorado agency or local service territory utility"
    elif proj_state == "IL":
        if any(il in agency_lower for il in ["illinois", "comed", "commonwealth edison", "dceo", "ameren illinois"]) or "state_il" in jurisdiction or "il" in geo_scope:
            return 1.25, "Direct In-State Alignment: Sponsored by Illinois agency or local service territory utility"
    elif proj_state == "NJ":
        if any(nj in agency_lower for nj in ["new jersey", "njeda", "njbpu", "pseg", "public service electric"]) or "state_nj" in jurisdiction or "nj" in geo_scope:
            return 1.25, "Direct In-State Alignment: Sponsored by New Jersey agency or local service territory utility"

    # 3. Federal Nationwide Programs (Tier 2)
    if any(f in agency_lower for f in ["doe", "u.s. department of energy", "arpa-e", "nsf", "national science foundation", "epa", "environmental protection", "usda", "dod", "doc", "federal"]) or jurisdiction in ("us_fed", "federal", "national") or geo_scope == "national":
        return 1.05, "Federal solicitation — nationwide eligibility with federal funding priority"

    # 4. Out-of-State National/Philanthropic Programs with No In-State Restrictions (Tier 3)
    is_national_unrestricted = any(n in agency_lower for n in [
        "gates", "bloomberg", "rockefeller", "bezos", "breakthrough", "nextera", "duke", "southern company", "exelon", "aep", "xcel", "dominion", "avangrid", "eversource", "entergy", "dte", "macarthur", "elemental", "prime coalition"
    ])
    if is_national_unrestricted:
        return 0.95, f"National / Multi-State Innovation Sponsor ({agency}): Open to multi-jurisdictional innovation projects"

    # 5. Out-of-State State Agency (Tier 4) -> Strictly exclude / penalize
    return 0.05, f"Out-of-State Jurisdiction ({agency}): Restricted to in-state projects in other jurisdictions"


def _score_sector_compatibility(opp: Opportunity, profile: ProjectProfile) -> tuple[float, str]:
    """
    Evaluates sector compatibility and penalizes cross-sector mismatches:
    - Residential Consumer/Homeowner Rebates vs Commercial/Industrial/Grid projects (0.05x penalty).
    - Heavy Industrial Manufacturing vs Residential projects (0.05x penalty).
    - Direct sector alignment (1.20x boost).
    """
    opp_text = getattr(opp, "_search_corpus_lower", None)
    if opp_text is None:
        opp_text = ((opp.name or "") + " " + (opp.short_description or "") + " " + (opp.keywords or "")).lower()

    # 1. Residential Consumer / Homeowner / Retail Rebates
    is_res_program = getattr(opp, "_is_res_program", None)
    if is_res_program is None:
        is_res_program = bool(_RE_RES_PROGRAM.search(opp_text))

    # Check if project is industrial / manufacturing / commercial / utility grid
    is_industrial_or_commercial = any(
        s in ["Industrial & Manufacturing", "Electric Grid & Utility", "Commercial Buildings", "Transportation & Mobility"]
        for s in profile.sectors
    ) or (profile.applicant_type in ["business", "company", "startup", "manufacturer", "corporate", "utility"] and "Residential Buildings" not in profile.sectors)

    is_large_scale = (profile.project_cost and profile.project_cost >= 2_000_000) or any(
        a in ["Manufacturing", "Utility Integration", "Commercialization"] for a in profile.activity_types
    )

    if is_res_program and (is_industrial_or_commercial or is_large_scale) and "Residential Buildings" not in profile.sectors:
        return 0.05, "Severe Sector Clash: Residential homeowner/consumer rebate program is incompatible with commercial, industrial manufacturing, or grid facilities."

    # 2. Heavy Industrial Decarbonization & Manufacturing Plant
    is_industrial_opp = getattr(opp, "_is_industrial_opp", None)
    if is_industrial_opp is None:
        is_industrial_opp = bool(_RE_INDUSTRIAL_OPP.search(opp_text))

    is_pure_residential_project = (
        "Residential Buildings" in profile.sectors
        and not any(s in ["Industrial & Manufacturing", "Electric Grid & Utility", "Commercial Buildings"] for s in profile.sectors)
        and (profile.applicant_type in ["homeowner", "consumer", "individual"] or (profile.project_cost and profile.project_cost < 100_000))
    )

    if is_industrial_opp and is_pure_residential_project:
        return 0.05, "Severe Sector Clash: Industrial manufacturing and heavy plant solicitation is incompatible with residential consumer projects."

    # Positive Alignment
    if "Industrial & Manufacturing" in profile.sectors and is_industrial_opp:
        return 1.20, "Direct Sector Alignment: Solicitation specifically targets industrial manufacturing and production facilities."

    if "Electric Grid & Utility" in profile.sectors and any(g in opp_text for g in ["grid modernization", "substation", "transmission", "distribution", "smart grid", "derms"]):
        return 1.20, "Direct Sector Alignment: Solicitation specifically targets electric grid and power system modernization."

    if ("Residential Buildings" in profile.sectors or "Multifamily Housing" in profile.sectors) and any(b in opp_text for b in ["residential", "multifamily", "building decarbonization", "heat pump", "weatherization"]):
        return 1.20, "Direct Sector Alignment: Solicitation specifically targets residential and multifamily building decarbonization."

    if "Transportation & Mobility" in profile.sectors and any(t in opp_text for t in ["electric vehicle", "charging", "fleet", "transit", "clean transportation"]):
        return 1.20, "Direct Sector Alignment: Solicitation specifically targets clean transportation and mobility infrastructure."

    return 1.00, "Compatible sector application."


def _score_fuel_compatibility(opp: Opportunity, profile: ProjectProfile) -> tuple[float, str]:
    """
    Evaluates fuel vector compatibility:
    - Solid wood/coal combustion/fossil feedstocks vs clean electric/solar/hydrogen (0.05x penalty).
    - Nuclear vs distributed rooftop solar (0.15x penalty).
    - Direct fuel vector match (1.20x boost).
    """
    opp_text = getattr(opp, "_search_corpus_lower", None)
    if opp_text is None:
        opp_text = ((opp.name or "") + " " + (opp.short_description or "") + " " + (opp.keywords or "")).lower()

    # Solid wood / coal combustion / fossil feedstock check
    is_fossil_or_solid_combustion = getattr(opp, "_is_fossil_or_solid_combustion", None)
    if is_fossil_or_solid_combustion is None:
        is_fossil_or_solid_combustion = bool(_RE_FOSSIL_SOLID_COMBUSTION.search(opp_text))

    if is_fossil_or_solid_combustion:
        has_clean_fuel = any(f in ["Solar", "Hydrogen", "Wind", "Battery Storage", "Electricity"] for f in profile.fuel_types)
        has_biomass = "Biomass / Biogas" in profile.fuel_types
        has_fossil = "Natural Gas" in profile.fuel_types

        if has_clean_fuel and not (has_biomass or has_fossil):
            return 0.05, "Severe Fuel Clash: Solicitation evaluates coal/fossil feedstocks or solid wood combustion, incompatible with clean solar/electric/hydrogen vectors."

    # Nuclear check
    is_nuclear_opp = getattr(opp, "_is_nuclear_opp", None)
    if is_nuclear_opp is None:
        is_nuclear_opp = bool(_RE_NUCLEAR_OPP.search(opp_text))

    if is_nuclear_opp and "Nuclear" not in profile.fuel_types and (profile.project_cost and profile.project_cost < 2_000_000):
        if any(f in ["Solar", "Building Electrification"] for f in profile.technology_areas):
            return 0.15, "Fuel Vector Mismatch: Advanced nuclear solicitation vs distributed solar/building project."

    # Positive Fuel Matches
    if "Hydrogen" in profile.fuel_types and any(h in opp_text for h in ["hydrogen", "electrolyzer", "fuel cell", "clean fuels"]):
        return 1.20, "Direct Fuel Vector Match: Program specifically finances clean hydrogen and fuel cell technologies."

    if "Solar" in profile.fuel_types and any(s in opp_text for s in ["solar", "photovoltaic", "pv", "perovskite"]):
        return 1.20, "Direct Fuel Vector Match: Program specifically finances solar photovoltaic innovations."

    if "Battery Storage" in profile.fuel_types and any(b in opp_text for b in ["battery", "energy storage", "bess", "ldes", "flow battery"]):
        return 1.20, "Direct Fuel Vector Match: Program specifically finances advanced battery and storage chemistry."

    if "Wind" in profile.fuel_types and any(w in opp_text for w in ["wind turbine", "offshore wind", "onshore wind", "floating wind"]):
        return 1.20, "Direct Fuel Vector Match: Program specifically finances wind energy technology."

    return 1.00, "Compatible fuel and energy carrier scope."


def _score_stage_activity_compatibility(opp: Opportunity, profile: ProjectProfile) -> tuple[float, str]:
    """
    Evaluates stage (TRL) and activity alignment:
    - Commercial Manufacturing scale-up vs Academic Basic Research grants (0.15x penalty).
    - Early R&D vs Operational Commercial Deployment (0.20x penalty).
    - Direct stage alignment (1.20x boost).
    """
    opp_text = getattr(opp, "_search_corpus_lower", None)
    if opp_text is None:
        opp_text = ((opp.name or "") + " " + (opp.short_description or "") + " " + (opp.keywords or "")).lower()

    trl = profile.estimated_trl or 5
    cost = profile.project_cost or 1_000_000.0

    is_academic_basic_research = getattr(opp, "_is_academic_basic_research", None)
    if is_academic_basic_research is None:
        is_academic_basic_research = bool(_RE_ACADEMIC_BASIC_RESEARCH.search(opp_text))

    is_manufacturing_scaleup = getattr(opp, "_is_manufacturing_scaleup", None)
    if is_manufacturing_scaleup is None:
        is_manufacturing_scaleup = bool(_RE_MANUFACTURING_SCALEUP.search(opp_text))

    is_commercial_deployment = getattr(opp, "_is_commercial_deployment", None)
    if is_commercial_deployment is None:
        is_commercial_deployment = bool(_RE_COMMERCIAL_DEPLOYMENT.search(opp_text))

    is_downstream_installation_rebate = getattr(opp, "_is_downstream_installation_rebate", None)
    if is_downstream_installation_rebate is None:
        is_downstream_installation_rebate = bool(_RE_DOWNSTREAM_INSTALLATION_REBATE.search(opp_text))

    # Upstream Component Manufacturing / Factory Scale-Up vs Downstream End-User Installation Rebates
    if ("Manufacturing" in profile.activity_types or "Industrial & Manufacturing" in profile.sectors) and is_downstream_installation_rebate:
        return 0.15, "Activity & Supply Chain Mismatch: Program provides downstream contractor/building installation rebates rather than capital funding for manufacturing plants and production lines."

    # Commercial Factory / Manufacturing Scale-Up vs Academic Theory
    if (trl >= 7 or "Manufacturing" in profile.activity_types or cost >= 5_000_000) and is_academic_basic_research and not is_manufacturing_scaleup:
        return 0.15, "Stage & Activity Mismatch: Academic basic research grant (TRL 1-2) is unsuitable for commercial manufacturing scale-up."

    # Early R&D (TRL 1-3) vs Shovel-Ready Commercial Deployment
    if trl <= 3 and is_commercial_deployment and not any(a in ["R&D", "Fundamental R&D"] for a in opp_text.split()):
        return 0.20, "Stage Mismatch: Program requires full-scale operational commercial deployment (TRL 8-9) rather than early-stage R&D."

    # Positive Stage Matches
    if (trl >= 7 or "Manufacturing" in profile.activity_types) and is_manufacturing_scaleup:
        return 1.20, "Optimal Commercialization Fit: Program directly funds industrial scale-up, pilot validation, and manufacturing capacity."

    if trl <= 4 and any(r in opp_text for r in ["sbir", "sttr", "arpa-e", "applied research", "proof of concept", "early-stage"]):
        return 1.20, "Optimal R&D Stage Fit: Program specifically supports proof-of-concept and innovative applied research."

    return 1.00, "Compatible technology readiness level and activity scope."


def _score_domain_incompatibility(opp: Opportunity, profile: ProjectProfile) -> tuple[float, str]:
    """
    Strictly gates and penalizes cross-domain technological false positives:
    - Marine & Hydrokinetic Water Power
    - Transportation, Electric Vehicles, Fleet Electrification, Engine Research
    - Wind Turbine Blade Aerodynamics & Offshore Wind Mooring
    - Concentrating Solar Power & Perovskite Solar Cells
    - Grid Transmission, Substation Automation, Synchrophasors & GETs
    - Hydrogen Electrolyzers & Fuel Cell Stacks
    - Carbon Capture & Subsurface Sequestration
    """
    opp_text = getattr(opp, "_search_corpus_lower", None)
    if opp_text is None:
        opp_text = (
            (opp.name or "") + " " +
            (opp.short_description or "") + " " +
            (opp.keywords or "") + " " +
            (opp.objectives or "")
        ).lower()

    if not hasattr(profile, "_cached_techs_set"):
        profile._cached_techs_set = set(profile.technology_areas or [])
        profile._cached_sectors_set = set(profile.sectors or [])
        profile._cached_fuels_set = set(profile.fuel_types or [])
        profile._cached_kws_text = " ".join(
            (profile.keywords or []) +
            (profile.extracted_phrases or []) +
            [profile.summary or "", profile.project_title or ""]
        ).lower()

    proj_techs = profile._cached_techs_set
    proj_sectors = profile._cached_sectors_set
    proj_fuels = profile._cached_fuels_set
    proj_kws_text = profile._cached_kws_text

    # 1. Marine & Hydrokinetic
    is_mhk_opp = getattr(opp, "_is_mhk_opp", None)
    if is_mhk_opp is None:
        is_mhk_opp = bool(_RE_MHK_OPP.search(opp_text))
    if is_mhk_opp:
        has_mhk_focus = (
            "Marine & Hydrokinetic" in proj_techs
            or any(k in proj_kws_text for k in ["hydrokinetic", "marine energy", "wave energy", "tidal energy", "ocean energy", "mhk", "river hydrokinetic", "ocean power", "wave power", "tidal power"])
        )
        if not has_mhk_focus:
            return 0.02, "Domain Incompatibility: Specialized marine/hydrokinetic water power solicitation is incompatible with non-marine project."

    # 2. Clean Transportation / Electric Vehicles / Charging Infrastructure / Fleet / Vehicle Engines
    is_trans_opp = getattr(opp, "_is_trans_opp", None)
    if is_trans_opp is None:
        is_trans_opp = bool(_RE_TRANS_OPP.search(opp_text))
    if is_trans_opp:
        has_trans_focus = (
            "Clean Transportation" in proj_techs
            or "Transportation & Mobility" in proj_sectors
            or any(k in proj_kws_text for k in ["electric vehicle", "ev charging", "vehicle", "transit bus", "fleet electrification", "powertrain", "evse", "automotive", "trucking", "clean transportation", "bus fleet", "diesel emission"])
        )
        if not has_trans_focus:
            return 0.02, "Domain Incompatibility: Specialized vehicle technologies / transportation infrastructure solicitation is incompatible with non-transportation project."

    # 3. Wind Turbine Aerodynamics & Blades
    is_wind_opp = getattr(opp, "_is_wind_opp", None)
    if is_wind_opp is None:
        is_wind_opp = bool(_RE_WIND_OPP.search(opp_text))
    if is_wind_opp:
        has_wind_focus = (
            "Wind" in proj_techs
            or "Offshore Wind" in proj_techs
            or "Wind" in proj_fuels
            or any(k in proj_kws_text for k in ["wind turbine", "offshore wind", "wind blade", "floating wind", "wind energy"])
        )
        if not has_wind_focus:
            return 0.02, "Domain Incompatibility: Specialized wind turbine blade / aerodynamics solicitation is incompatible with non-wind project."

    # 4. Concentrating Solar Thermal & Specialized Solar Photovoltaics
    is_solar_opp = getattr(opp, "_is_solar_opp", None)
    if is_solar_opp is None:
        is_solar_opp = bool(_RE_SOLAR_OPP.search(opp_text))
    if is_solar_opp:
        has_solar_focus = (
            "Solar" in proj_techs
            or "Solar" in proj_fuels
            or any(k in proj_kws_text for k in ["solar", "photovoltaic", "pv", "perovskite", "bifacial", "solar cell", "solar panel"])
        )
        if not has_solar_focus:
            return 0.02, "Domain Incompatibility: Specialized solar photovoltaic / concentrating solar power solicitation is incompatible with non-solar project."

    # 5. Grid Transmission Lines, Substation Automation, GETs & Synchrophasors
    is_grid_infra_opp = getattr(opp, "_is_grid_infra_opp", None)
    if is_grid_infra_opp is None:
        is_grid_infra_opp = bool(_RE_GRID_INFRA_OPP.search(opp_text))
    if is_grid_infra_opp:
        has_grid_focus = (
            "Grid Modernization" in proj_techs
            or "Electric Grid & Utility" in proj_sectors
            or any(k in proj_kws_text for k in ["grid modernization", "transmission", "substation", "synchrophasor", "derms", "power flow", "grid enhancing", "smart grid", "power system"])
        )
        if not has_grid_focus:
            return 0.05, "Domain Incompatibility: Specialized grid transmission / substation utility infrastructure solicitation is incompatible with non-grid project."

    # 6. Hydrogen Electrolyzers & Fuel Cell Stacks
    is_h2_opp = getattr(opp, "_is_h2_opp", None)
    if is_h2_opp is None:
        is_h2_opp = bool(_RE_H2_OPP.search(opp_text))
    if is_h2_opp:
        has_h2_focus = (
            "Hydrogen & Alternative Fuels" in proj_techs
            or "Hydrogen" in proj_fuels
            or any(k in proj_kws_text for k in ["hydrogen", "electrolyzer", "fuel cell", "clean hydrogen", "hydrogen fuel"])
        )
        if not has_h2_focus:
            return 0.05, "Domain Incompatibility: Specialized hydrogen electrolyzer / fuel cell solicitation is incompatible with non-hydrogen project."

    # 7. Direct Air Capture (DAC) / Geologic Carbon Sequestration
    is_dac_opp = getattr(opp, "_is_dac_opp", None)
    if is_dac_opp is None:
        is_dac_opp = bool(_RE_DAC_OPP.search(opp_text))
    if is_dac_opp:
        has_dac_focus = (
            "Carbon Management" in proj_techs
            or any(k in proj_kws_text for k in ["carbon capture", "direct air capture", "dac", "ccus", "sequestration", "carbon dioxide removal", "co2 capture"])
        )
        if not has_dac_focus:
            return 0.05, "Domain Incompatibility: Specialized carbon capture / subsurface sequestration solicitation is incompatible with non-carbon management project."

    return 1.00, "Domain compatible."


def _score_funding_fit(opp: Opportunity, profile: ProjectProfile) -> FitDimension:
    """Score funding award scale compatibility using non-linear tranche modeling."""
    max_award = opp.max_per_award or opp.total_funding
    if not max_award or not profile.project_cost:
        return FitDimension("funding_scale", 0.85, "Flexible funding scale — suited for phased development", "medium")

    cost = profile.project_cost
    ratio = cost / max_award if max_award > 0 else 1.0

    # Piecewise Non-Linear Tranche Evaluation
    if 0.40 <= ratio <= 2.5:
        score = 1.00
        explanation = f"Optimal Anchor Funding: Award cap (${max_award:,.0f}) directly covers primary capital envelope for ${cost:,.0f} scope"
    elif 0.15 <= ratio < 0.40:
        score = 0.90
        explanation = f"Full Coverage Capacity: Award capacity (${max_award:,.0f}) exceeds total budget (${cost:,.0f}), fully funding deployment"
    elif 2.5 < ratio <= 6.0:
        score = 0.85
        explanation = f"Catalytic Co-Funding Tranche: Award (${max_award:,.0f}) provides anchor non-dilutive match for ${cost:,.0f} deployment"
    elif 6.0 < ratio <= 12.0:
        score = 0.65
        explanation = f"Modular Component Tranche: Award (${max_award:,.0f}) covers sub-workstream in ${cost:,.0f} project"
    else:
        score = 0.40
        explanation = f"Capital Disparity: Requested budget (${cost:,.0f}) significantly exceeds program award ceiling (${max_award:,.0f})"

    return FitDimension("funding_scale", score, explanation, "medium")


def _extract_restrictions(opp: Opportunity, profile: ProjectProfile) -> list[dict]:
    """Extract and format restrictions and watch items for an opportunity."""
    restrictions = []

    # Database restrictions
    cached_restr = getattr(opp, "_cached_restrictions", getattr(opp, "restrictions", None)) or []
    for r in cached_restr:
        restrictions.append({
            "title": getattr(r, "title", "Program Restriction") or "Program Restriction",
            "description": getattr(r, "description", "") or "",
            "severity": getattr(r, "severity", "medium") or "medium",
        })

    # Inferred standard constraints
    if opp.concept_paper_required:
        restrictions.append({
            "title": "Concept Paper Prerequisite",
            "description": "Requires mandatory preliminary concept paper submission prior to full proposal.",
            "severity": "medium",
        })

    if opp.cost_share_pct and opp.cost_share_pct >= 20:
        restrictions.append({
            "title": f"{opp.cost_share_pct}% Non-Federal Cost Share",
            "description": f"Applicant must secure at least {opp.cost_share_pct}% non-federal co-funding or in-kind commitments.",
            "severity": "medium",
        })

    if getattr(opp, "vendor_registration_required", False):
        restrictions.append({
            "title": "Vendor Portal Registration",
            "description": "Pre-registration in procurement portal required before bid submission.",
            "severity": "low",
        })

    return restrictions


def _find_applicable_components(opp: Opportunity, profile: ProjectProfile) -> list[str]:
    """Find which project workstreams/components apply to this opportunity."""
    applicable = []
    desc = ((opp.name or "") + " " + (opp.short_description or "") + " " + (opp.objectives or "")).lower()

    for ws in profile.workstreams:
        ws_name = ws.get("activity_type", "").lower()
        if ws_name in desc:
            applicable.append(ws.get("name", "Workstream"))

    if not applicable:
        for tech in profile.technology_areas:
            if tech.lower() in desc or any(a in desc for a in TAXONOMY_ALIASES.get(tech, [])):
                applicable.append(f"{tech} Architecture")

    return applicable[:3] or ["Full Project Scope"]


def _generate_fit_explanation(
    opp: Opportunity, profile: ProjectProfile,
    dimensions: list[FitDimension], applicable: list[str],
    matched_kws: list[str], matched_techs: list[str],
) -> str:
    """Generate clear, institutional narrative explaining why this opportunity matches."""
    parts = []

    if matched_kws:
        parts.append(f"Direct alignment on key topics including {', '.join(matched_kws[:3])}")
    elif matched_techs:
        parts.append(f"Aligns with core technology focus in {', '.join(matched_techs[:2])}")
    else:
        parts.append("Institutional scope aligns with project parameters")

    if opp.agency:
        parts.append(f"sponsored by {opp.agency}")

    if applicable and applicable != ["Full Project Scope"]:
        parts.append(f"targeting {', '.join(applicable)}")

    max_award = opp.max_per_award or opp.total_funding
    if max_award:
        if max_award >= 1_000_000:
            parts.append(f"with funding up to ${(max_award / 1_000_000):.1f}M")
        else:
            parts.append(f"with funding up to ${(max_award / 1_000):.0f}K")

    return " ".join(parts) + "."


def find_precedents(db: Session, profile: ProjectProfile, limit: int = 10) -> list[dict]:
    """Find historically similar funded awards and projects across corpus."""
    search_terms = []
    
    # Priority: extracted phrases, keywords, technology areas
    if hasattr(profile, "extracted_phrases") and profile.extracted_phrases:
        search_terms.extend(profile.extracted_phrases[:4])
    if hasattr(profile, "keywords") and profile.keywords:
        search_terms.extend(profile.keywords[:4])
    if profile.technology_areas:
        search_terms.extend(profile.technology_areas[:3])

    search_terms = [t for t in dict.fromkeys(search_terms) if t and len(t) > 2]

    if not search_terms:
        search_terms = ["energy", "clean"]

    precedents = []

    # 1. Search modern Awards table
    try:
        bind = db.get_bind()
        is_postgres = (bind.dialect.name == "postgresql") if bind else False

        if is_postgres:
            clean_terms = []
            for term in search_terms[:5]:
                cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', term).strip()
                if cleaned:
                    clean_terms.append(cleaned)
            fts_query_str = " OR ".join(clean_terms) if clean_terms else "energy OR clean"

            awards = (
                db.query(Award)
                .filter(
                    text("to_tsvector('english', coalesce(project_title, '') || ' ' || coalesce(recipient_name, '')) @@ websearch_to_tsquery('english', :fts_query)")
                    .params(fts_query=fts_query_str)
                )
                .order_by(Award.award_amount.desc().nullslast())
                .limit(limit)
                .all()
            )
        else:
            award_clauses = []
            for term in search_terms[:5]:
                award_clauses.append(Award.project_title.ilike(f"%{term}%"))
                award_clauses.append(Award.project_abstract.ilike(f"%{term}%"))

            awards = db.query(Award).filter(or_(*award_clauses)).order_by(Award.award_amount.desc().nullslast()).limit(limit).all()

        for a in awards:
            precedents.append({
                "id": a.id,
                "project_title": a.project_title or "Clean Innovation Project",
                "contractor_name": a.recipient_name or getattr(a, "contractor_name", "Recipient Entity"),
                "contractor_type": a.recipient_type or "Business",
                "project_type": a.award_type or "Grant Award",
                "technology_1": a.cfda_title or (profile.technology_areas[0] if profile.technology_areas else "Clean Energy"),
                "award_amount": a.award_amount or a.total_estimated or 0,
                "award_date": a.award_date.strftime("%Y-%m-%d") if (a.award_date and hasattr(a.award_date, "strftime")) else (f"{getattr(a, 'award_year', '2024')}"),
                "contractor_city": a.recipient_city or "US",
                "contractor_state": a.recipient_state or "US",
            })
    except Exception as e:
        logger.warning(f"Award precedent query error: {e}")

    # 2. Search HistoricalProject table if needed
    if len(precedents) < limit:
        try:
            hp_clauses = []
            for term in search_terms[:3]:
                hp_clauses.append(HistoricalProject.project_title.ilike(f"%{term}%"))
                hp_clauses.append(HistoricalProject.technology_1.ilike(f"%{term}%"))

            hp_results = db.query(HistoricalProject).filter(or_(*hp_clauses)).order_by(HistoricalProject.award_amount.desc().nullslast()).limit(limit - len(precedents)).all()
            for hp in hp_results:
                precedents.append({
                    "id": hp.id,
                    "project_title": hp.project_title,
                    "contractor_name": hp.contractor_name,
                    "contractor_type": hp.contractor_type,
                    "project_type": hp.project_type,
                    "technology_1": hp.technology_1 or "Clean Tech",
                    "award_amount": hp.award_amount or 0,
                    "award_date": hp.award_date.strftime("%Y-%m-%d") if (hp.award_date and hasattr(hp.award_date, "strftime")) else "Historical",
                    "contractor_city": hp.contractor_city or "",
                    "contractor_state": hp.contractor_state or "",
                })
        except Exception as e:
            logger.warning(f"HistoricalProject precedent query error: {e}")

    return precedents[:limit]

