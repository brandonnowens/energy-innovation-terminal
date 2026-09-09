"""
64-Bit Integer Bitmask Screening Engine.

Provides sub-millisecond candidate pre-filtering and attribute matching
using CPU-register level bitwise integer operations.
"""

from typing import Dict, List, Optional, Any
from app.models.opportunity import Opportunity
from app.engine.profile import ProjectProfile

# ==============================================================================
# 1. 64-Bit Technology Domain Bitmask Mapping
# ==============================================================================

TECHNOLOGY_BITS: Dict[str, int] = {
    "solar": 1 << 0,
    "solar pv": 1 << 0,
    "photovoltaic": 1 << 0,
    "perovskite": 1 << 0,
    "wind": 1 << 1,
    "offshore wind": 1 << 1,
    "energy storage": 1 << 2,
    "battery": 1 << 2,
    "long duration energy storage": 1 << 2,
    "bess": 1 << 2,
    "flow battery": 1 << 2,
    "hydrogen": 1 << 3,
    "fuel cell": 1 << 3,
    "electrolyzer": 1 << 3,
    "geothermal": 1 << 4,
    "heat pump": 1 << 5,
    "thermal energy storage": 1 << 5,
    "buildings": 1 << 6,
    "building decarbonization": 1 << 6,
    "hvac": 1 << 6,
    "energy efficiency": 1 << 7,
    "grid": 1 << 8,
    "grid modernization": 1 << 8,
    "transmission": 1 << 8,
    "distribution": 1 << 8,
    "microgrid": 1 << 8,
    "substation": 1 << 8,
    "power electronics": 1 << 9,
    "inverter": 1 << 9,
    "electric vehicles": 1 << 10,
    "ev": 1 << 10,
    "ev charging": 1 << 10,
    "clean transportation": 1 << 10,
    "fleet": 1 << 10,
    "carbon capture": 1 << 11,
    "direct air capture": 1 << 11,
    "dac": 1 << 11,
    "ccus": 1 << 11,
    "carbon storage": 1 << 11,
    "industrial decarbonization": 1 << 12,
    "process heat": 1 << 12,
    "manufacturing": 1 << 13,
    "advanced manufacturing": 1 << 13,
    "clean energy manufacturing": 1 << 13,
    "semiconductor": 1 << 14,
    "data center": 1 << 15,
    "data centers & computing": 1 << 15,
    "computing": 1 << 15,
    "immersion cooling": 1 << 15,
    "nuclear": 1 << 16,
    "smr": 1 << 16,
    "fusion": 1 << 16,
    "hydropower": 1 << 17,
    "marine energy": 1 << 17,
    "bioenergy": 1 << 18,
    "biofuels": 1 << 18,
    "biomass": 1 << 18,
    "materials science": 1 << 19,
    "advanced materials": 1 << 19,
    "sensors & controls": 1 << 20,
    "software & ai": 1 << 21,
    "artificial intelligence": 1 << 21,
    "cybersecurity": 1 << 22,
    "water & wastewater": 1 << 23,
    "waste heat": 1 << 24,
    "circular economy": 1 << 25,
    "agriculture & forestry": 1 << 26,
    "environmental justice": 1 << 27,
    "justice40": 1 << 27,
    "community benefits": 1 << 27,
}

# ==============================================================================
# 2. 16-Bit Activity Type Bitmask Mapping
# ==============================================================================

ACTIVITY_BITS: Dict[str, int] = {
    "r&d": 1 << 0,
    "research": 1 << 0,
    "fundamental r&d": 1 << 0,
    "applied r&d": 1 << 0,
    "demonstration": 1 << 1,
    "pilot": 1 << 1,
    "field test": 1 << 1,
    "demo": 1 << 1,
    "deployment": 1 << 2,
    "commercialization": 1 << 2,
    "scale": 1 << 2,
    "infrastructure": 1 << 2,
    "testing & validation": 1 << 3,
    "testing": 1 << 3,
    "validation": 1 << 3,
    "feasibility study": 1 << 4,
    "feasibility": 1 << 4,
    "assessment": 1 << 4,
    "product development": 1 << 5,
    "prototype": 1 << 5,
    "software & controls": 1 << 6,
    "workforce development": 1 << 7,
    "training": 1 << 7,
    "technical assistance": 1 << 8,
}

# ==============================================================================
# 3. 16-Bit Applicant Type Bitmask Mapping
# ==============================================================================

APPLICANT_BITS: Dict[str, int] = {
    "business": 1 << 0,
    "for_profit": 1 << 0,
    "company": 1 << 0,
    "commercial": 1 << 0,
    "startup": 1 << 0,
    "small_business": 1 << 1,
    "sbir": 1 << 1,
    "university": 1 << 2,
    "academic": 1 << 2,
    "higher_ed": 1 << 2,
    "nonprofit": 1 << 3,
    "non_profit": 1 << 3,
    "ngo": 1 << 3,
    "national_lab": 1 << 4,
    "ffrdc": 1 << 4,
    "municipality": 1 << 5,
    "local_gov": 1 << 5,
    "state_gov": 1 << 6,
    "tribal": 1 << 7,
    "utility": 1 << 8,
    "individual": 1 << 9,
}

# ==============================================================================
# 4. 64-Bit Geographic State Bitmask Mapping
# ==============================================================================

STATE_LIST = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC", "PR", "VI", "GU"
]

STATE_BITS: Dict[str, int] = {st: (1 << idx) for idx, st in enumerate(STATE_LIST)}
STATE_BITS["US_NATIONAL"] = (1 << 60) - 1  # Matches all states


# ==============================================================================
# Helper Constructors
# ==============================================================================

def compute_text_tech_mask(text: str) -> int:
    """Computes a 64-bit technology mask by scanning keywords in text."""
    if not text:
        return 0
    t_lower = text.lower()
    mask = 0
    for term, bit in TECHNOLOGY_BITS.items():
        if term in t_lower:
            mask |= bit
    return mask


def compute_tech_mask_from_list(techs: Optional[List[str]]) -> int:
    """Computes technology mask from a list of technology terms."""
    if not techs:
        return 0
    mask = 0
    for t in techs:
        if not t:
            continue
        t_low = t.lower().strip()
        if t_low in TECHNOLOGY_BITS:
            mask |= TECHNOLOGY_BITS[t_low]
        else:
            for term, bit in TECHNOLOGY_BITS.items():
                if term in t_low or t_low in term:
                    mask |= bit
    return mask


def compute_activity_mask(activities: Optional[List[str]]) -> int:
    """Computes activity mask from a list of activity terms."""
    if not activities:
        return 0
    mask = 0
    for a in activities:
        if not a:
            continue
        a_low = a.lower().strip()
        if a_low in ACTIVITY_BITS:
            mask |= ACTIVITY_BITS[a_low]
        else:
            for term, bit in ACTIVITY_BITS.items():
                if term in a_low:
                    mask |= bit
    return mask


def compute_applicant_mask(applicant_type: Optional[str]) -> int:
    """Computes applicant type mask."""
    if not applicant_type:
        return (1 << 16) - 1  # Open to all
    a_low = applicant_type.lower().strip()
    return APPLICANT_BITS.get(a_low, 1 << 0)


def compute_geo_mask(state: Optional[str], jurisdiction: Optional[str] = None) -> int:
    """Computes jurisdiction bitmask."""
    if jurisdiction in ("us_fed", "federal", "national", "nationwide"):
        return STATE_BITS["US_NATIONAL"]
    if not state:
        return STATE_BITS["US_NATIONAL"]
    st_upper = state.upper().strip()
    return STATE_BITS.get(st_upper, STATE_BITS["US_NATIONAL"])


def build_opportunity_bitmasks(opp: Opportunity) -> Dict[str, int]:
    """
    Constructs and returns pre-computed bitmasks for an Opportunity record.
    """
    cats = getattr(opp, "_cached_categories", None)
    if cats is None:
        cats = getattr(opp, "categories", None) or []

    # 1. Tech Mask
    tech_mask = 0
    if cats:
        for c in cats:
            if getattr(c, "category_type", None) in ("technology", "sector", "fuel"):
                val = (getattr(c, "category_value", "") or "").lower()
                tech_mask |= compute_tech_mask_from_list([val])
    
    # Enrich tech mask from title/keywords
    text_corpus = ((opp.name or "") + " " + (opp.keywords or "") + " " + (opp.short_description or ""))
    tech_mask |= compute_text_tech_mask(text_corpus)

    # 2. Activity Mask
    act_mask = 0
    if cats:
        for c in cats:
            if getattr(c, "category_type", None) == "activity":
                act_mask |= compute_activity_mask([getattr(c, "category_value", "")])
    act_mask |= compute_activity_mask([opp.name, opp.short_description])

    # 3. Applicant Mask
    app_mask = (1 << 16) - 1  # Default open
    sol_cat = (getattr(opp, "solicitation_category", "") or "").lower()
    if "university" in sol_cat or "academic" in sol_cat:
        app_mask = APPLICANT_BITS["university"] | APPLICANT_BITS["nonprofit"]
    elif "small business" in sol_cat or "sbir" in sol_cat:
        app_mask = APPLICANT_BITS["small_business"]

    # 4. Geo Mask
    agency = (opp.agency or "").lower()
    geo_scope = (getattr(opp, "geographic_scope", "") or "").lower()
    jurisdiction = (getattr(opp, "jurisdiction", "") or "").lower()

    if any(fed in agency for fed in ["doe", "arpa-e", "nsf", "epa", "usda", "dod"]) or jurisdiction in ("us_fed", "federal", "national") or geo_scope == "national":
        geo_mask = STATE_BITS["US_NATIONAL"]
    elif "nyserda" in agency or "new york" in agency or "ny" in geo_scope or "state_ny" in jurisdiction:
        geo_mask = STATE_BITS.get("NY", 0)
    elif "cec" in agency or "california" in agency or "ca" in geo_scope or "state_ca" in jurisdiction:
        geo_mask = STATE_BITS.get("CA", 0)
    elif "masscec" in agency or "massachusetts" in agency or "ma" in geo_scope or "state_ma" in jurisdiction:
        geo_mask = STATE_BITS.get("MA", 0)
    else:
        geo_mask = STATE_BITS["US_NATIONAL"]

    return {
        "tech_mask": tech_mask,
        "act_mask": act_mask,
        "app_mask": app_mask,
        "geo_mask": geo_mask,
    }


def compute_bitmask_compatibility(
    proj_tech_mask: int,
    proj_act_mask: int,
    proj_app_mask: int,
    proj_geo_mask: int,
    opp_tech_mask: int,
    opp_act_mask: int,
    opp_app_mask: int,
    opp_geo_mask: int,
) -> tuple[float, bool]:
    """
    Computes candidate compatibility score and prime applicant eligibility in < 0.0001 ms.
    
    Returns:
        (overlap_score: float, is_prime_eligible: bool)
    """
    # Geographic filter (Hard check)
    if proj_geo_mask and opp_geo_mask:
        if not (proj_geo_mask & opp_geo_mask):
            return 0.0, False

    # Prime applicant eligibility
    is_prime_eligible = True
    if proj_app_mask and opp_app_mask:
        if not (proj_app_mask & opp_app_mask):
            is_prime_eligible = False

    # Technology & activity bit overlap
    tech_overlap = (proj_tech_mask & opp_tech_mask) if (proj_tech_mask and opp_tech_mask) else 0
    act_overlap = (proj_act_mask & opp_act_mask) if (proj_act_mask and opp_act_mask) else 0

    overlap_bits = bin(tech_overlap).count("1") * 0.4 + bin(act_overlap).count("1") * 0.2
    score = min(1.0, 0.30 + overlap_bits)

    return score, is_prime_eligible
