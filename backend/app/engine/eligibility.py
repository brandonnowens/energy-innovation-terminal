"""Deterministic eligibility engine.

Evaluates structured eligibility rules against a project profile.
Each test returns PASS / FAIL / UNKNOWN.
Explicit FAIL cannot be overridden by semantic similarity.

Enforces strict in-state awardee and project-sponsor restrictions for all
state-level government programs and utility organizations across all US states.
"""

import re
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional, List, Dict, Set

from sqlalchemy.orm import Session

from app.engine.profile import ProjectProfile
from app.ingest.organization_taxonomy import get_organization_profile
from app.models.opportunity import EligibilityRule, Opportunity, OpportunityRound

logger = logging.getLogger(__name__)


@dataclass
class EligibilityTest:
    """Result of a single eligibility test."""
    rule_type: str
    rule_key: str
    result: str  # PASS, FAIL, UNKNOWN
    reason: str
    is_hard: bool = True
    source: Optional[str] = None


@dataclass
class EligibilityResult:
    """Aggregate eligibility result for an opportunity."""
    opportunity_id: int
    solicitation_number: str
    overall: str  # ELIGIBLE, INELIGIBLE, UNCERTAIN
    tests: list[EligibilityTest]
    hard_fails: int = 0
    passes: int = 0
    unknowns: int = 0

    def to_dict(self) -> dict:
        return {
            "overall": self.overall,
            "hard_fails": self.hard_fails,
            "passes": self.passes,
            "unknowns": self.unknowns,
            "tests": [
                {
                    "rule_type": t.rule_type,
                    "rule_key": t.rule_key,
                    "result": t.result,
                    "reason": t.reason,
                    "is_hard": t.is_hard,
                    "source": t.source,
                }
                for t in self.tests
            ],
        }


# ==============================================================================
# Comprehensive US State & Geographic Normalization
# ==============================================================================

ALL_US_STATES: Dict[str, str] = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "DC": "District of Columbia", "PR": "Puerto Rico", "VI": "Virgin Islands", "GU": "Guam"
}

STATE_LOCATIONS: Dict[str, List[str]] = {
    "NY": ["new york", "nyc", "manhattan", "brooklyn", "queens", "bronx", "staten island", "long island",
           "buffalo", "rochester", "syracuse", "albany", "yonkers", "ithaca", "westchester", "nassau",
           "suffolk", "schenectady", "troy", "utica", "binghamton", "poughkeepsie", "newburgh", "white plains",
           "niagara", "erie", "monroe", "onondaga", "new york state"],
    "CA": ["california", "los angeles", "san francisco", "san diego", "sacramento", "san jose", "oakland",
           "fresno", "palo alto", "silicon valley", "berkeley", "long beach", "irvine", "anaheim", "bakersfield",
           "riverside", "santa clara", "pasadena", "sunnyvale", "california state"],
    "MA": ["massachusetts", "boston", "cambridge", "worcester", "springfield", "somerville", "lowell", "newton",
           "quincy", "lynn", "fall river", "new bedford", "brockton", "massachusetts state"],
    "TX": ["texas", "houston", "dallas", "austin", "san antonio", "fort worth", "el paso", "arlington",
           "corpus christi", "plano", "lubbock", "irving", "laredo", "garland", "frisco", "texas state"],
    "IL": ["illinois", "chicago", "springfield", "peoria", "naperville", "aurora", "rockford", "joliet",
           "evanston", "elgin", "illinois state"],
    "CO": ["colorado", "denver", "boulder", "aurora", "colorado springs", "fort collins", "lakewood", "thornton", "arvada", "colorado state"],
    "NJ": ["new jersey", "newark", "jersey city", "trenton", "princeton", "paterson", "elizabeth", "edison", "woodbridge", "lakewood", "new jersey state"],
    "WA": ["washington state", "seattle", "tacoma", "spokane", "olympia", "bellevue", "everett", "kent", "renton", "yakima", "washington"],
    "PA": ["pennsylvania", "philadelphia", "pittsburgh", "allentown", "erie", "reading", "scranton", "bethlehem", "lancaster", "harrisburg", "pennsylvania state"],
    "OH": ["ohio", "columbus", "cleveland", "cincinnati", "toledo", "akron", "dayton", "parma", "canton", "ohio state"],
    "MI": ["michigan", "detroit", "grand rapids", "warren", "sterling heights", "ann arbor", "lansing", "flint", "dearborn", "michigan state"],
    "GA": ["georgia", "atlanta", "augusta", "columbus", "macon", "savannah", "athens", "sandy springs", "roswell", "georgia state"],
    "NC": ["north carolina", "charlotte", "raleigh", "greensboro", "durham", "winston-salem", "fayetteville", "cary", "wilmington", "north carolina state"],
    "VA": ["virginia", "virginia beach", "norfolk", "chesapeake", "richmond", "newport news", "alexandria", "hampton", "roanoke", "portsmouth", "virginia state"],
    "FL": ["florida", "miami", "orlando", "tampa", "jacksonville", "st. petersburg", "hialeah", "tallahassee", "fort lauderdale", "cape coral", "florida state"],
    "MN": ["minnesota", "minneapolis", "st. paul", "duluth", "rochester", "bloomington", "brooklyn park", "plymouth", "minnesota state"],
    "WI": ["wisconsin", "milwaukee", "madison", "green bay", "kenosha", "racine", "appleton", "waukesha", "oshkosh", "wisconsin state"],
    "MD": ["maryland", "baltimore", "annapolis", "bethesda", "silver spring", "frederick", "rockville", "gaithersburg", "bowie", "maryland state"],
    "AZ": ["arizona", "phoenix", "tucson", "mesa", "chandler", "scottsdale", "glendale", "gilbert", "tempe", "peoria", "arizona state"],
    "OR": ["oregon", "portland", "salem", "eugene", "gresham", "hillsboro", "beaverton", "bend", "medford", "oregon state"],
    "CT": ["connecticut", "bridgeport", "new haven", "stamford", "hartford", "waterbury", "norwalk", "danbury", "new britain", "connecticut state"],
    "NM": ["new mexico", "albuquerque", "santa fe", "las cruces", "rio rancho", "roswell", "farmington", "new mexico state"],
    "ME": ["maine", "portland", "augusta", "bangor", "lewiston", "south portland", "auburn", "maine state"],
}

# State agency to primary state code mapping
KNOWN_STATE_AGENCIES: Dict[str, str] = {
    # New York
    "NYSERDA": "NY",
    "Empire State Development": "NY",
    "NY PSC": "NY",
    "LIPA": "NY",
    "NYPA": "NY",
    # California
    "CEC": "CA",
    "California GO-Biz": "CA",
    "CPUC": "CA",
    "CARB": "CA",
    # Massachusetts
    "MassCEC": "MA",
    "DOER": "MA",
    # New Jersey
    "NJEDA": "NJ",
    "NJBPU": "NJ",
    # Colorado
    "Colorado CEO": "CO",
    "Colorado OEDIT": "CO",
    # Connecticut
    "Connecticut Innovations": "CT",
    # Illinois
    "IL DCEO": "IL",
    # Ohio
    "JobsOhio": "OH",
    # Maryland
    "MD MEA": "MD",
    # Michigan
    "MEDC": "MI",
    # Minnesota
    "MN DEED": "MN",
    # New Mexico
    "NM EMNRD": "NM",
    # Texas
    "TX SECO": "TX",
    # Virginia
    "VIPC": "VA",
    # Washington
    "WA Commerce": "WA",
    # Wisconsin
    "WI OEI": "WI",
    # Pennsylvania
    "Ben Franklin Tech Partners": "PA",
    # Maine
    "Efficiency Maine": "ME",
}

# Utility organizations mapped to operating state
UTILITY_STATE_MAP: Dict[str, str] = {
    # NY Utilities
    "Con Edison": "NY", "Con Edison / NY PSC": "NY", "National Grid": "NY",
    "Central Hudson": "NY", "Orange & Rockland": "NY", "NYSEG": "NY",
    "RG&E": "NY", "PSEG Long Island": "NY", "Joint Utilities of NY": "NY",
    # CA Utilities
    "Pacific Gas and Electric": "CA", "PG&E / CPUC": "CA", "Southern California Edison": "CA",
    "San Diego Gas & Electric": "CA", "Southern California Gas": "CA",
    "Sacramento Municipal Utility District": "CA", "Los Angeles Department of Water and Power": "CA",
    # MA Utilities
    "Eversource Energy (Massachusetts)": "MA", "National Grid Massachusetts": "MA",
    # IL Utilities
    "Commonwealth Edison": "IL", "Ameren Illinois": "IL",
    # TX Utilities
    "CenterPoint Energy Houston Electric": "TX", "Oncor Electric Delivery": "TX",
    "Austin Energy": "TX", "CPS Energy": "TX",
    # FL Utilities
    "Florida Power & Light": "FL", "Duke Energy Florida": "FL", "Orlando Utilities Commission": "FL",
    # GA Utilities
    "Georgia Power": "GA", "Cobb EMC": "GA",
    # WA Utilities
    "Seattle City Light": "WA", "Puget Sound Energy": "WA", "Snohomish County PUD": "WA",
    # OR Utilities
    "Portland General Electric": "OR",
    # AZ Utilities
    "Arizona Public Service": "AZ", "Salt River Project": "AZ",
    # CO Utilities
    "Public Service Company of Colorado": "CO", "Tri-State Generation and Transmission": "CO",
    # CT Utilities
    "Eversource Connecticut": "CT", "United Illuminating": "CT",
    # DE Utilities
    "Delmarva Power (Delaware)": "DE",
    # IN Utilities
    "AES Indiana": "IN", "Duke Energy Indiana": "IN",
    # MD Utilities
    "Baltimore Gas and Electric": "MD", "Potomac Electric Power Company (Maryland)": "MD",
    # MI Utilities
    "Consumers Energy": "MI", "DTE Energy": "MI",
    # MN Utilities
    "Northern States Power (Minnesota)": "MN", "Great River Energy": "MN",
    # MO Utilities
    "Ameren Missouri": "MO", "Evergy Missouri": "MO",
    # NC Utilities
    "Duke Energy Carolinas": "NC", "North Carolina Electric Membership Corp": "NC",
    # NJ Utilities
    "Public Service Electric and Gas": "NJ",
    # OH Utilities
    "AEP Ohio": "OH", "AES Ohio": "OH",
    # PA Utilities
    "PECO Energy": "PA", "PPL Electric Utilities": "PA", "Duquesne Light Company": "PA",
    # SC Utilities
    "Dominion Energy South Carolina": "SC", "Santee Cooper": "SC",
    # VA Utilities
    "Dominion Energy Virginia": "VA",
    # WI Utilities
    "We Energies": "WI", "Madison Gas and Electric": "WI",
}


@lru_cache(maxsize=1024)
def extract_state_from_location(location_str: Optional[str]) -> Optional[str]:
    """
    Normalizes a user project location string (e.g. 'NYC', 'San Francisco', 'Boston, MA', 'NY')
    into a standardized 2-letter US state code.
    Returns 'ALL' if the project is specified as nationwide, national, or US-wide.
    """
    if not location_str or not location_str.strip():
        return None

    loc_clean = location_str.strip()
    loc_lower = loc_clean.lower()

    # Check for nationwide / multi-state designations
    if any(term in loc_lower for term in ["nationwide", "national", "us-wide", "united states", "usa", "all states", "multi-state", "federal"]):
        return "ALL"

    # Check explicit 2-letter uppercase state code bounded by word boundary or comma
    # e.g., "New York, NY", "Albany, NY", "CA", "Austin, TX"
    state_code_match = re.search(r'(?:^|[,\s\b])([A-Z]{2})(?:$|[,\s\b])', loc_clean)
    if state_code_match:
        code = state_code_match.group(1)
        if code in ALL_US_STATES:
            return code

    # Check state specific location name keywords
    for state_code, place_names in STATE_LOCATIONS.items():
        if any(place in loc_lower for place in place_names):
            return state_code

    # Check state full names
    for state_code, full_name in ALL_US_STATES.items():
        if full_name.lower() in loc_lower:
            return state_code

    return None


@lru_cache(maxsize=4096)
def _cached_opportunity_required_state(agency_clean: str, jurisdiction_clean: str) -> Optional[str]:
    agency = agency_clean
    jurisdiction = jurisdiction_clean
    agency_lower = agency.lower()
    jurisdiction_lower = jurisdiction.lower()

    # 1. Federal agencies and philanthropic foundations are open to all states (Nationwide scope)
    if agency in ["DOE", "ARPA-E", "NSF", "EPA", "USDA", "DOD", "DOT", "DOC", "NIST"] or jurisdiction_lower in ["federal", "national", "foundation"]:
        return None

    # 2. National / Multi-state utility holding companies without strict single-state retail restrictions
    multi_state_parents = [
        "nextera energy", "duke energy", "the southern company", "southern company",
        "exelon", "american electric power", "aep", "xcel energy", "dominion energy",
        "avangrid", "entergy", "dte energy", "alliant energy", "firstenergy"
    ]
    is_multi_state_parent = any(p in agency_lower for p in multi_state_parents) and not any(
        sub in agency_lower for sub in ["massachusetts", "florida", "ohio", "indiana", "carolinas", "houston", "illinois", "virginia"]
    )
    if is_multi_state_parent:
        return None

    # 3. Check taxonomy profile registry
    try:
        prof = get_organization_profile(agency_clean)
        if prof:
            cat = prof.get("category")
            st = prof.get("state")
            sub_type = prof.get("sub_type", "")
            if cat in ("state", "utility") and st and st != "US" and "Holding Company" not in sub_type:
                if st in ALL_US_STATES:
                    return st
    except Exception:
        pass

    # 4. Check known state agency registry
    if agency in KNOWN_STATE_AGENCIES:
        return KNOWN_STATE_AGENCIES[agency]

    # 5. Check known utility organization registry
    if agency in UTILITY_STATE_MAP:
        return UTILITY_STATE_MAP[agency]

    # 6. Check explicit jurisdiction tags (e.g. 'state_ny', 'state_ca', 'NY', 'CA', 'utility_ny')
    if jurisdiction_lower.startswith("state_"):
        code = jurisdiction_lower.replace("state_", "").upper()
        if code in ALL_US_STATES:
            return code

    if jurisdiction_lower.startswith("utility_"):
        code = jurisdiction_lower.replace("utility_", "").upper()
        if code in ALL_US_STATES:
            return code

    if jurisdiction.upper() in ALL_US_STATES:
        return jurisdiction.upper()

    return None


def get_opportunity_required_state(opp: Opportunity) -> Optional[str]:
    """
    Determines if an opportunity is a state-level or utility-level program restricted to in-state entities.
    Returns the required 2-letter state code (e.g. 'NY', 'CA', 'MA'), or None if federal/national/open.
    """
    cached = getattr(opp, "_required_state", ...)
    if cached is not ...:
        return cached
    agency = (getattr(opp, "agency", "") or "").strip()
    jurisdiction = (getattr(opp, "jurisdiction", "") or "").strip()
    return _cached_opportunity_required_state(agency, jurisdiction)


def evaluate_eligibility(
    db: Session,
    opportunity: Opportunity,
    profile: ProjectProfile,
) -> EligibilityResult:
    """Evaluate all eligibility rules for an opportunity against a project profile."""

    tests: list[EligibilityTest] = []

    # 1. Check if opportunity is open
    tests.append(_check_status(opportunity))

    # 2. Check deadline
    tests.append(_check_deadline(opportunity))

    # 3. Evaluate stored rules
    rules = getattr(opportunity, "_cached_eligibility_rules", None)
    if rules is None:
        if hasattr(opportunity, "eligibility_rules") and opportunity.eligibility_rules is not None:
            rules = opportunity.eligibility_rules
        else:
            rules = db.query(EligibilityRule).filter_by(opportunity_id=opportunity.id).all()

    for rule in rules:
        test = _evaluate_rule(rule, profile, opportunity)
        tests.append(test)

    # 4. ENFORCE STRICT IN-STATE RESTRICTION FOR ALL STATE & UTILITY PROGRAMS
    required_state = get_opportunity_required_state(opportunity)
    if required_state:
        tests.append(_eval_strict_state_restriction(required_state, profile, opportunity))

    # 5. ENFORCE SECTOR COMPATIBILITY (Prevent residential consumer matches on manufacturing/grid projects)
    tests.append(_eval_sector_compatibility(profile, opportunity))

    # 6. ENFORCE FUEL COMPATIBILITY (Prevent solid wood heater/coal matches on solar/hydrogen/electric projects)
    tests.append(_eval_fuel_compatibility(profile, opportunity))

    # Aggregate
    hard_fails = sum(1 for t in tests if t.result == "FAIL" and t.is_hard)
    passes = sum(1 for t in tests if t.result == "PASS")
    unknowns = sum(1 for t in tests if t.result == "UNKNOWN")

    if hard_fails > 0:
        overall = "INELIGIBLE"
    elif unknowns > 0:
        overall = "UNCERTAIN"
    else:
        overall = "ELIGIBLE"

    return EligibilityResult(
        opportunity_id=opportunity.id,
        solicitation_number=opportunity.solicitation_number,
        overall=overall,
        tests=tests,
        hard_fails=hard_fails,
        passes=passes,
        unknowns=unknowns,
    )


def _eval_strict_state_restriction(
    required_state: str,
    profile: ProjectProfile,
    opp: Opportunity,
) -> EligibilityTest:
    """
    Enforces strict in-state restrictions for all state-level organizations and state programs.
    If the project is in a different state, returns a HARD FAIL (is_hard=True).
    """
    agency_name = opp.agency or "State Program"
    state_full_name = ALL_US_STATES.get(required_state, required_state)

    if not profile.target_location:
        return EligibilityTest(
            rule_type="geography",
            rule_key=f"state_restriction_{required_state.lower()}",
            result="UNKNOWN",
            reason=f"State-level program ({agency_name} - {state_full_name}) requires in-state awardee/sponsor activities in {required_state}. Please specify location to verify eligibility.",
            is_hard=False,
            source="state_in_state_restriction",
        )

    project_state = extract_state_from_location(profile.target_location)

    # Project is nationwide / open to all US states
    if project_state == "ALL":
        return EligibilityTest(
            rule_type="geography",
            rule_key=f"state_restriction_{required_state.lower()}",
            result="PASS",
            reason=f"Nationwide / Multi-state scope satisfies {required_state} ({state_full_name}) in-state requirements.",
            is_hard=True,
            source="state_in_state_restriction",
        )

    # Project state matches opportunity required state
    if project_state == required_state:
        return EligibilityTest(
            rule_type="geography",
            rule_key=f"state_restriction_{required_state.lower()}",
            result="PASS",
            reason=f"In-state requirement verified: Project location '{profile.target_location}' is in {required_state} ({state_full_name}), qualifying for {agency_name}.",
            is_hard=True,
            source="state_in_state_restriction",
        )

    # Project is located in a different state -> STRICT HARD FAIL
    project_state_name = ALL_US_STATES.get(project_state, project_state) if project_state else profile.target_location
    return EligibilityTest(
        rule_type="geography",
        rule_key=f"state_restriction_{required_state.lower()}",
        result="FAIL",
        reason=(
            f"State program in-state restriction: {agency_name} ({state_full_name}) is strictly restricted "
            f"to in-state awardees, project sponsors, and facilities in {required_state}. "
            f"Your project location '{profile.target_location}' ({project_state_name}) is out of state and ineligible."
        ),
        is_hard=True,
        source="state_in_state_restriction",
    )


def _eval_sector_compatibility(profile: ProjectProfile, opp: Opportunity) -> EligibilityTest:
    """
    Evaluates sector compatibility to prevent inappropriate cross-sector matches
    (e.g., residential consumer/homeowner rebates matching commercial/industrial manufacturing facilities).
    """
    opp_name = (opp.name or "").lower()
    opp_desc = (opp.short_description or "").lower()
    opp_text = f"{opp_name} {opp_desc}"

    # 1. Residential Consumer / Homeowner / Retail Rebate Opportunity Detection
    is_res_program = getattr(opp, "_is_res_program", None)
    if is_res_program is None:
        residential_consumer_patterns = [
            r'\bresidential\s+(?:rebate|incentive|program|storage|clean\s+heat|microgrid|energy\s+code)\b',
            r'\bhomeowner\b',
            r'\bsingle[\s-]family\b',
            r'\bweatherization\s+assistance\b',
            r'\bweatherization\s+formula\b',
            r'\bwhole[\s-]house\b',
            r'\bhvacr\s+to\s+home\s+performance\b',
            r'\bresidential\s+wood\s+heater\b',
            r'\bempower\s*new\s*york\b',
            r'\bempower\+\b',
            r'\bgeothermal\s+heat\s+pump\s+rebates\b',
        ]
        is_res_program = any(re.search(pat, opp_text) for pat in residential_consumer_patterns)

    # Check if project is industrial / manufacturing / commercial / utility grid
    is_industrial_or_commercial = any(
        s in ["Industrial & Manufacturing", "Electric Grid & Utility", "Commercial Buildings", "Transportation & Mobility"]
        for s in profile.sectors
    ) or (profile.applicant_type in ["business", "company", "startup", "manufacturer", "corporate", "utility"] and "Residential Buildings" not in profile.sectors)

    # If project is high-capex commercial/industrial (> $2M or industrial activity)
    is_large_scale = (profile.project_cost and profile.project_cost >= 2_000_000) or any(
        a in ["Manufacturing", "Utility Integration", "Commercialization"] for a in profile.activity_types
    )

    if is_res_program and (is_industrial_or_commercial or is_large_scale) and "Residential Buildings" not in profile.sectors:
        return EligibilityTest(
            rule_type="sector",
            rule_key="residential_consumer_mismatch",
            result="FAIL",
            reason=(
                f"Program ({opp.name}) is strictly a residential homeowner / consumer rebate initiative, "
                f"which is ineligible for commercial, industrial manufacturing, and grid infrastructure facilities."
            ),
            is_hard=True,
            source="sector_compatibility_enforcement",
        )

    # Downstream Building Installation Rebate vs Upstream Factory Manufacturing
    is_downstream_installation_rebate = getattr(opp, "_is_downstream_installation_rebate", None)
    if is_downstream_installation_rebate is None:
        is_downstream_installation_rebate = bool(re.search(
            r'\b(incentives?\s+for\s+the\s+installation|market\s+acceleration\s+incentives?|residential\s+and\s+(?:retail|nonresidential)\s+incentive|contractors\s+and\s+builders\s+to\s+install|rebates?\s+for\s+installing)\b',
            opp_text
        ))
    if is_downstream_installation_rebate and ("Manufacturing" in profile.activity_types or "Industrial & Manufacturing" in profile.sectors):
        return EligibilityTest(
            rule_type="sector",
            rule_key="installation_rebate_mismatch",
            result="FAIL",
            reason=(
                f"Program ({opp.name}) is a downstream contractor/building installation rebate, "
                f"which is ineligible for upstream manufacturing plants and equipment production facilities."
            ),
            is_hard=True,
            source="sector_compatibility_enforcement",
        )

    # 2. Industrial Manufacturing & Heavy Industry Opportunity Detection
    is_industrial_opp = getattr(opp, "_is_industrial_opp", None)
    if is_industrial_opp is None:
        industrial_patterns = [
            r'\bindustrial\s+decarbonization\b',
            r'\bclean\s+energy\s+manufacturing\b',
            r'\bmanufacturing\s+plant\b',
            r'\bchemical\s+manufacturing\b',
            r'\bgreen\s+steel\b',
            r'\blow-carbon\s+cement\b',
        ]
        is_industrial_opp = any(re.search(pat, opp_text) for pat in industrial_patterns)

    is_pure_residential_project = (
        "Residential Buildings" in profile.sectors
        and not any(s in ["Industrial & Manufacturing", "Electric Grid & Utility", "Commercial Buildings"] for s in profile.sectors)
        and (profile.applicant_type in ["homeowner", "consumer", "individual"] or (profile.project_cost and profile.project_cost < 100_000))
    )

    if is_industrial_opp and is_pure_residential_project:
        return EligibilityTest(
            rule_type="sector",
            rule_key="industrial_manufacturing_mismatch",
            result="FAIL",
            reason=(
                f"Program ({opp.name}) is strictly for industrial manufacturing and heavy production facilities, "
                f"which is ineligible for residential consumer projects."
            ),
            is_hard=True,
            source="sector_compatibility_enforcement",
        )

    return EligibilityTest(
        rule_type="sector",
        rule_key="sector_compatibility",
        result="PASS",
        reason="Sector parameters compatible with solicitation scope.",
        is_hard=False,
        source="sector_compatibility_enforcement",
    )


def _eval_fuel_compatibility(profile: ProjectProfile, opp: Opportunity) -> EligibilityTest:
    """
    Evaluates fuel compatibility to prevent severe fuel mismatches
    (e.g., solid wood stoves / coal combustion matching pure solar or hydrogen projects).
    """
    opp_name = (opp.name or "").lower()
    opp_desc = (opp.short_description or "").lower()
    opp_text = f"{opp_name} {opp_desc}"

    # Wood heater / coal / solid biomass combustion / fossil feedstock check
    is_fossil_or_solid_combustion = getattr(opp, "_is_fossil_or_solid_combustion", None)
    if is_fossil_or_solid_combustion is None:
        is_fossil_or_solid_combustion = bool(re.search(
            r'\b(coal\s+value\s+chain|coal-based|fossil\s+feedstock|coal\s+combustion|coal\s+mine|wood\s+heater|wood\s+stove|biomass\s+combustion\s+for\s+cooking)\b',
            opp_text
        ))

    if is_fossil_or_solid_combustion:
        has_clean_fuel = any(f in ["Solar", "Hydrogen", "Wind", "Battery Storage", "Electricity"] for f in profile.fuel_types)
        has_biomass = "Biomass / Biogas" in profile.fuel_types
        has_fossil = "Natural Gas" in profile.fuel_types

        if has_clean_fuel and not (has_biomass or has_fossil):
            return EligibilityTest(
                rule_type="fuel",
                rule_key="fuel_vector_mismatch",
                result="FAIL",
                reason=f"Solicitation ({opp.name}) strictly evaluates coal/fossil feedstocks or solid wood combustion, incompatible with project clean fuel vector.",
                is_hard=True,
                source="fuel_compatibility_enforcement",
            )

    return EligibilityTest(
        rule_type="fuel",
        rule_key="fuel_compatibility",
        result="PASS",
        reason="Fuel vector compatible with solicitation scope.",
        is_hard=False,
        source="fuel_compatibility_enforcement",
    )


def _check_status(opp: Opportunity) -> EligibilityTest:
    """Check opportunity status."""
    if opp.status == "open":
        return EligibilityTest(
            rule_type="status", rule_key="open", result="PASS",
            reason="Opportunity is currently open", is_hard=True,
        )
    elif opp.status == "draft":
        return EligibilityTest(
            rule_type="status", rule_key="open", result="PASS",
            reason="Solicitation is in draft (upcoming cycle)", is_hard=False,
        )
    elif opp.status == "awarded":
        return EligibilityTest(
            rule_type="status", rule_key="open", result="PASS",
            reason="Active federal/state funding program & benchmarked award track", is_hard=False,
        )
    elif opp.status == "closed":
        return EligibilityTest(
            rule_type="status", rule_key="open", result="UNKNOWN",
            reason="Previous solicitation round completed (recurring program cycle)", is_hard=False,
        )
    else:
        return EligibilityTest(
            rule_type="status", rule_key="open", result="UNKNOWN",
            reason=f"Opportunity status is '{opp.status}'", is_hard=False,
        )


def _check_deadline(opp: Opportunity) -> EligibilityTest:
    """Check submission deadline status."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    all_rounds = getattr(opp, "_cached_rounds", None)
    if all_rounds is None:
        all_rounds = getattr(opp, "rounds", []) or []
    open_rounds = [r for r in all_rounds if r.status == "Open"]

    if not open_rounds:
        if opp.enrollment_type and any(term in opp.enrollment_type.lower() for term in ["open", "rolling", "continuous"]):
            return EligibilityTest(
                rule_type="deadline", rule_key="has_future_deadline", result="PASS",
                reason="Open / rolling enrollment — no fixed cutoff deadline", is_hard=False,
            )
        return EligibilityTest(
            rule_type="deadline", rule_key="has_future_deadline", result="PASS",
            reason="Recurring or multi-round program — check upcoming solicitation cycle", is_hard=False,
        )

    future_rounds = [r for r in open_rounds if r.due_date and r.due_date > now]
    if future_rounds:
        next_deadline = min(r.due_date for r in future_rounds)
        return EligibilityTest(
            rule_type="deadline", rule_key="has_future_deadline", result="PASS",
            reason=f"Next active deadline: {next_deadline.strftime('%m/%d/%Y')}", is_hard=False,
        )
    else:
        return EligibilityTest(
            rule_type="deadline", rule_key="has_future_deadline", result="UNKNOWN",
            reason="Recent round completed; monitor for next submission window", is_hard=False,
        )


def _evaluate_rule(rule: EligibilityRule, profile: ProjectProfile, opp: Opportunity) -> EligibilityTest:
    """Evaluate a single eligibility rule against the project profile."""

    if rule.rule_type == "geography":
        return _eval_geography(rule, profile, opp)
    elif rule.rule_type == "applicant":
        return _eval_applicant(rule, profile)
    elif rule.rule_type == "technology":
        return _eval_technology(rule, profile)
    elif rule.rule_type == "trl":
        return _eval_trl(rule, profile)
    elif rule.rule_type == "cost_share":
        return _eval_cost_share(rule, profile)
    elif rule.rule_type == "activity":
        return _eval_activity(rule, profile)
    elif rule.rule_type == "service_territory":
        return _eval_service_territory(rule, profile, opp)
    elif rule.rule_type == "vendor_registration":
        return _eval_vendor_registration(rule, profile)
    else:
        return EligibilityTest(
            rule_type=rule.rule_type,
            rule_key=rule.rule_key,
            result="UNKNOWN",
            reason=f"Cannot evaluate rule type: {rule.rule_type}",
            is_hard=rule.is_hard_requirement,
            source=rule.source,
        )


def _eval_geography(rule: EligibilityRule, profile: ProjectProfile, opp: Opportunity) -> EligibilityTest:
    jurisdiction = getattr(opp, "jurisdiction", "state")
    if jurisdiction and jurisdiction.lower() == "federal":
        return EligibilityTest(
            rule_type="geography", rule_key=rule.rule_key, result="PASS",
            reason="Federal opportunity is open to all US entities",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    if not profile.target_location:
        return EligibilityTest(
            rule_type="geography", rule_key=rule.rule_key, result="UNKNOWN",
            reason="No location specified in project profile",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    project_state = extract_state_from_location(profile.target_location)
    rule_state = extract_state_from_location(rule.rule_value) or rule.rule_value.upper()

    if project_state == "ALL" or project_state == rule_state:
        return EligibilityTest(
            rule_type="geography", rule_key=rule.rule_key, result="PASS",
            reason=f"Project location '{profile.target_location}' satisfies geography requirement ({rule.rule_value})",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    return EligibilityTest(
        rule_type="geography", rule_key=rule.rule_key, result="FAIL" if rule.is_hard_requirement else "UNKNOWN",
        reason=f"Project location '{profile.target_location}' does not match required geography '{rule.rule_value}'",
        is_hard=rule.is_hard_requirement, source=rule.source,
    )


def _eval_applicant(rule: EligibilityRule, profile: ProjectProfile) -> EligibilityTest:
    if not profile.applicant_type:
        return EligibilityTest(
            rule_type="applicant", rule_key=rule.rule_key, result="UNKNOWN",
            reason="Applicant type not specified",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    type_mapping = {
        "university": ["university", "academic", "research_institution"],
        "startup": ["business", "corporate", "startup", "company"],
        "business": ["business", "corporate", "company"],
        "utility": ["utility"],
        "municipality": ["public_sector", "municipality", "government"],
        "nonprofit": ["nonprofit", "non_profit", "501(c)(3)"],
        "hospital": ["hospital"],
        "labor_organization": ["labor_organization"],
        "retailer_contractor": ["retailer_contractor"],
    }

    allowed = type_mapping.get(profile.applicant_type, [profile.applicant_type])
    if rule.rule_value in allowed or profile.applicant_type == rule.rule_value:
        return EligibilityTest(
            rule_type="applicant", rule_key=rule.rule_key, result="PASS",
            reason=f"Applicant type '{profile.applicant_type}' matches requirement '{rule.rule_value}'",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    if rule.rule_operator == "in":
        # Check if eligible via Consortium / Subcontract Teaming
        if any(u in (rule.rule_value or "").lower() for u in ["university", "academic", "higher_ed", "nonprofit"]):
            if (profile.applicant_type or "").lower() in ["business", "startup", "company", "commercial", "for_profit"]:
                return EligibilityTest(
                    rule_type="applicant",
                    rule_key=rule.rule_key,
                    result="TEAMING",
                    reason=f"Solicitation requires academic lead ({rule.rule_value}). Company is eligible as funded commercialization / industrial demonstration partner or subcontractor.",
                    is_hard=False,
                    source=rule.source,
                )
        return EligibilityTest(
            rule_type="applicant", rule_key=rule.rule_key, result="FAIL",
            reason=f"Applicant type '{profile.applicant_type}' does not match required '{rule.rule_value}'",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    return EligibilityTest(
        rule_type="applicant", rule_key=rule.rule_key, result="UNKNOWN",
        reason=f"Cannot confirm applicant type match for '{rule.rule_value}'",
        is_hard=rule.is_hard_requirement, source=rule.source,
    )


def _eval_technology(rule: EligibilityRule, profile: ProjectProfile) -> EligibilityTest:
    if not profile.technology_areas:
        return EligibilityTest(
            rule_type="technology", rule_key=rule.rule_key, result="UNKNOWN",
            reason="No technology areas identified in project",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    rule_val = rule.rule_value.lower()
    for tech in profile.technology_areas:
        if rule_val in tech.lower() or tech.lower() in rule_val:
            return EligibilityTest(
                rule_type="technology", rule_key=rule.rule_key, result="PASS",
                reason=f"Project technology '{tech}' matches '{rule.rule_value}'",
                is_hard=rule.is_hard_requirement, source=rule.source,
            )

    return EligibilityTest(
        rule_type="technology", rule_key=rule.rule_key, result="UNKNOWN",
        reason=f"Project technologies {profile.technology_areas} may not match '{rule.rule_value}'",
        is_hard=rule.is_hard_requirement, source=rule.source,
    )


def _eval_trl(rule: EligibilityRule, profile: ProjectProfile) -> EligibilityTest:
    if profile.estimated_trl is None:
        return EligibilityTest(
            rule_type="trl", rule_key=rule.rule_key, result="UNKNOWN",
            reason="TRL not estimated for project",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    try:
        req_val = int(rule.rule_value)
    except ValueError:
        return EligibilityTest(
            rule_type="trl", rule_key=rule.rule_key, result="UNKNOWN",
            reason=f"Cannot parse TRL requirement: {rule.rule_value}",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    if rule.rule_operator == "gte" and profile.estimated_trl >= req_val:
        return EligibilityTest(
            rule_type="trl", rule_key=rule.rule_key, result="PASS",
            reason=f"Project TRL {profile.estimated_trl} >= required {req_val}",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )
    elif rule.rule_operator == "lte" and profile.estimated_trl <= req_val:
        return EligibilityTest(
            rule_type="trl", rule_key=rule.rule_key, result="PASS",
            reason=f"Project TRL {profile.estimated_trl} <= max {req_val}",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    return EligibilityTest(
        rule_type="trl", rule_key=rule.rule_key, result="FAIL",
        reason=f"Project TRL {profile.estimated_trl} does not meet {rule.rule_operator} {req_val}",
        is_hard=rule.is_hard_requirement, source=rule.source,
    )


def _eval_cost_share(rule: EligibilityRule, profile: ProjectProfile) -> EligibilityTest:
    return EligibilityTest(
        rule_type="cost_share", rule_key=rule.rule_key, result="UNKNOWN",
        reason=f"Cost share of {rule.rule_value}% required — verify applicant can meet this",
        is_hard=False, source=rule.source,
    )


def _eval_activity(rule: EligibilityRule, profile: ProjectProfile) -> EligibilityTest:
    if not profile.activity_types:
        return EligibilityTest(
            rule_type="activity", rule_key=rule.rule_key, result="UNKNOWN",
            reason="No activity types identified in project",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    rule_val = rule.rule_value.lower()
    for activity in profile.activity_types:
        if rule_val in activity.lower() or activity.lower() in rule_val:
            return EligibilityTest(
                rule_type="activity", rule_key=rule.rule_key, result="PASS",
                reason=f"Project activity '{activity}' matches '{rule.rule_value}'",
                is_hard=rule.is_hard_requirement, source=rule.source,
            )

    return EligibilityTest(
        rule_type="activity", rule_key=rule.rule_key, result="UNKNOWN",
        reason=f"Cannot confirm activity match for '{rule.rule_value}'",
        is_hard=rule.is_hard_requirement, source=rule.source,
    )


def _eval_service_territory(rule: EligibilityRule, profile: ProjectProfile, opp: Opportunity) -> EligibilityTest:
    agency = getattr(opp, "agency", "")

    if agency == "NYPA":
        return EligibilityTest(
            rule_type="service_territory", rule_key=rule.rule_key, result="PASS",
            reason="NYPA serves all of New York State",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    if not profile.target_location:
        return EligibilityTest(
            rule_type="service_territory", rule_key=rule.rule_key, result="UNKNOWN",
            reason="No project location specified — cannot verify service territory",
            is_hard=rule.is_hard_requirement, source=rule.source,
        )

    # Check utility state
    req_state = UTILITY_STATE_MAP.get(agency)
    proj_state = extract_state_from_location(profile.target_location)

    if req_state and proj_state and proj_state != "ALL" and proj_state != req_state:
        return EligibilityTest(
            rule_type="service_territory", rule_key=rule.rule_key, result="FAIL",
            reason=f"Project in {proj_state} is outside {agency} operating territory ({req_state})",
            is_hard=True, source=rule.source,
        )

    location_lower = profile.target_location.lower()
    from app.engine.profile import _NY_SERVICE_TERRITORIES
    territory_locations = _NY_SERVICE_TERRITORIES.get(agency, [])
    if territory_locations:
        for loc in territory_locations:
            if loc in location_lower or location_lower in loc:
                return EligibilityTest(
                    rule_type="service_territory", rule_key=rule.rule_key, result="PASS",
                    reason=f"Project location '{profile.target_location}' is within {agency} service territory",
                    is_hard=rule.is_hard_requirement, source=rule.source,
                )

    return EligibilityTest(
        rule_type="service_territory", rule_key=rule.rule_key, result="PASS" if (proj_state == req_state or proj_state == "ALL") else "UNKNOWN",
        reason=f"Project in {proj_state or profile.target_location} matches {agency} service region",
        is_hard=rule.is_hard_requirement, source=rule.source,
    )


def _eval_vendor_registration(rule: EligibilityRule, profile: ProjectProfile) -> EligibilityTest:
    return EligibilityTest(
        rule_type="vendor_registration", rule_key=rule.rule_key, result="UNKNOWN",
        reason=f"Vendor registration required: {rule.rule_value}. Register before submitting a bid.",
        is_hard=False, source=rule.source,
    )
