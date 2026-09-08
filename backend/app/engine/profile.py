"""Project profile extraction from free-text descriptions.

Extracts structured project attributes from user-provided descriptions
using keyword matching and pattern recognition. Falls back to LLM
when available for deeper understanding.
"""

import json
import logging
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ProjectProfile:
    """Structured representation of a user's project."""

    project_title: Optional[str] = None
    summary: str = ""
    technology_areas: list[str] = field(default_factory=list)
    activity_types: list[str] = field(default_factory=list)
    sectors: list[str] = field(default_factory=list)
    fuel_types: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    extracted_phrases: list[str] = field(default_factory=list)
    estimated_trl: Optional[int] = None
    applicant_type: Optional[str] = None
    location: Optional[str] = None
    target_location: Optional[str] = None
    ny_location: Optional[str] = None
    project_cost: Optional[float] = None
    project_timeline: Optional[str] = None
    partners: list[str] = field(default_factory=list)
    host_sites: list[str] = field(default_factory=list)
    dac_components: list[str] = field(default_factory=list)
    workstreams: list[dict] = field(default_factory=list)
    uncertainties: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


# Technology area keyword mappings
TECHNOLOGY_KEYWORDS = {
    "Data Centers & Computing": [
        "data center", "datacenter", "compute", "computing", "immersion cooling",
        "liquid cooling", "direct liquid cooling", "server", "servers", "hyperscale",
        "hpc", "pue", "it load", "cloud infrastructure", "ai compute", "ai computing",
        "power safety", "thermal management", "chip cooling", "gpu cluster",
        "large load", "heterogeneous retention", "dielectric fluid", "cold plate",
    ],
    "Grid Modernization": [
        "grid", "transmission", "distribution", "substation", "power flow",
        "conductor", "synchrophasor", "DER integration", "microgrid",
        "grid enhancing", "GETs", "dynamic line rating", "topology",
        "DERMS", "ADMS", "grid sensor", "PMU", "inverter", "power electronics",
        "smart grid", "interconnection", "islanding", "grid-forming",
    ],
    "Energy Storage": [
        "battery", "energy storage", "flow battery", "lithium",
        "long duration", "LDES", "zinc", "iron-air", "solid state",
        "sodium", "compressed air", "pumped hydro", "thermal storage",
        "gravity storage", "BESS", "behind the meter",
    ],
    "Building Electrification": [
        "heat pump", "building electrification", "HVAC", "space heating",
        "water heating", "cold climate", "geothermal heat", "air source",
        "ground source", "building envelope", "insulation", "retrofit",
        "multifamily", "residential", "commercial building",
    ],
    "Hydrogen & Alternative Fuels": [
        "hydrogen", "electrolyzer", "fuel cell", "ammonia", "green hydrogen",
        "blue hydrogen", "hydrogen storage", "hydrogen infrastructure",
        "alternative fuel", "synthetic fuel", "e-fuel", "SAF",
        "sustainable aviation fuel",
    ],
    "Solar": [
        "solar", "photovoltaic", "PV", "solar panel", "solar cell",
        "perovskite", "bifacial", "solar inverter", "community solar",
    ],
    "Wind": [
        "wind", "wind turbine", "offshore wind", "onshore wind",
        "floating wind", "wind blade", "nacelle",
    ],
    "Clean Transportation": [
        "electric vehicle", "EV", "charging", "fleet electrification",
        "medium duty", "heavy duty", "truck", "bus", "transit",
        "vehicle to grid", "V2G", "smart charging", "EVSE", "megawatt charging",
    ],
    "Carbon Management": [
        "carbon capture", "CCUS", "CCS", "direct air capture", "DAC",
        "carbon utilization", "carbon dioxide", "CO2", "mineralization",
        "embodied carbon", "low carbon", "concrete", "cement", "steel",
    ],
    "Sustainable Materials & Circular Economy": [
        "garment", "garments", "textile", "textiles", "apparel", "clothing",
        "circular fashion", "fabric", "fabrics", "bio-based dye", "dyeing",
        "dyes", "natural fiber", "natural fibers", "recycled fiber", "fiber recycling",
        "sustainable materials", "circular materials", "material efficiency", "waste valorization",
        "biomaterials", "circular bioeconomy", "textile recycling", "sustainable packaging",
        "bioplastics", "recycled plastics", "bio-based materials", "yarn", "weaving",
    ],
    "Marine & Hydrokinetic": [
        "hydrokinetic", "marine energy", "wave energy", "tidal energy", "ocean energy",
        "wave power", "tidal power", "marine hydrokinetic", "mhk", "ocean current",
        "river hydrokinetic", "water power", "hydro turbine", "subsea power",
    ],
    "Industrial Decarbonization": [
        "industrial heat", "process heat", "industrial decarbonization",
        "manufacturing", "industrial electrification", "kiln", "furnace",
        "industrial energy efficiency", "waste heat recovery", "textile manufacturing",
        "garment production", "sustainable production", "material processing",
    ],
    "Clean Energy Manufacturing": [
        "manufacturing", "clean tech manufacturing", "semiconductor packaging",
        "battery manufacturing", "component fabrication", "scale up manufacturing",
        "domestic supply chain", "advanced packaging", "garment production",
        "textile manufacturing", "sustainable manufacturing",
    ],
    "Thermal Energy Networks": [
        "thermal energy network", "TEN", "district heating", "district cooling",
        "district geothermal", "networked geothermal",
    ],
    "Cybersecurity": [
        "cybersecurity", "cyber", "grid security", "OT security",
        "SCADA security", "power safety",
    ],
    "Resilience": [
        "resilience", "resilient", "storm", "flooding", "climate adaptation",
        "backup power", "islanding", "microgrid controller",
    ],
    "Environmental Research": [
        "air quality", "emissions", "methane", "pollution", "environmental",
        "health effects", "source apportionment",
    ],
    "Offshore Wind": [
        "offshore wind", "floating offshore", "offshore wind supply chain",
        "subsea cable", "offshore substation",
    ],
    "Workforce Development": [
        "workforce", "training", "apprenticeship", "career pathway",
        "clean energy jobs",
    ],
}

# Activity type keyword mappings
ACTIVITY_KEYWORDS = {
    "R&D": ["research", "R&D", "development", "novel", "innovative", "new approach"],
    "Feasibility Study": ["feasibility", "assessment", "evaluation", "study", "modeling", "simulation"],
    "Product Development": ["product", "prototype", "develop", "design", "engineer"],
    "Demonstration": ["demonstration", "demo", "pilot", "proof of concept", "field test"],
    "Deployment": ["deployment", "installation", "implementation", "rollout", "scale"],
    "Manufacturing": ["manufacturing", "production", "factory", "fabrication", "assembly line", "garment production", "textile production"],
    "Testing & Validation": ["testing", "validation", "certification", "performance testing", "lab test"],
    "Software & Controls": ["software", "controls", "algorithm", "platform", "analytics", "AI", "ML"],
    "Utility Integration": ["utility", "grid interconnection", "utility partner", "rate case"],
    "Host-Site Deployment": ["host site", "building owner", "facility", "on-site", "customer site"],
    "Measurement & Verification": ["M&V", "measurement", "verification", "monitoring"],
    "Commercialization": ["commercialization", "market", "go-to-market", "sales", "customer acquisition"],
    "Community & DAC": ["disadvantaged community", "DAC", "environmental justice", "LMI", "low income"],
    "Technical Assistance": ["technical assistance", "energy audit", "consulting"],
}

# Sector keyword mappings
SECTOR_KEYWORDS = {
    "Industrial & Manufacturing": [
        "manufacturing", "factory", "production line", "fabrication", "industrial plant",
        "foundry", "kiln", "steel mill", "cement plant", "chemical plant", "refinery",
        "industrial facility", "industrial decarbonization", "industrial process", "supply chain",
        "assembly plant", "clean tech manufacturing", "semiconductor packaging", "component manufacturing",
        "garment", "garments", "textile", "textiles", "apparel", "clothing", "fashion", "fabric", "fabrics", "dyeing",
    ],
    "Electric Grid & Utility": [
        "grid", "transmission", "substation", "utility", "distribution system", "power flow",
        "derms", "adms", "islanding", "microgrid", "interconnection", "power electronics",
        "utility-scale", "synchrophasor", "smart grid", "power system", "grid modernization",
    ],
    "Commercial Buildings": [
        "commercial building", "commercial real estate", "office building", "warehouse",
        "retail", "supermarket", "data center", "datacenter", "campus", "hotel",
        "commercial hvac", "commercial chiller", "commercial facility",
    ],
    "Residential Buildings": [
        "residential", "homeowner", "homeowners", "single family", "single-family",
        "household", "weatherization", "home energy", "residential heat pump", "residential solar",
        "residential building", "residential energy", "home performance",
    ],
    "Multifamily Housing": [
        "multifamily", "multi-family", "affordable housing", "apartment complex",
        "tenant", "public housing", "multi-unit residential",
    ],
    "Transportation & Mobility": [
        "fleet", "electric vehicle", "ev charging", "trucking", "transit", "bus fleet",
        "heavy duty", "medium duty", "maritime", "port", "aviation", "v2g", "depot",
        "clean transportation", "e-mobility",
    ],
    "Agriculture & Forestry": [
        "agriculture", "farm", "farming", "dairy", "livestock", "agrivoltaic",
        "forestry", "timber", "rural", "cropland", "greenhouse", "manure digester",
    ],
    "Higher Education & Research": [
        "university", "academic", "national lab", "laboratory", "campus research",
        "higher education", "postdoc", "phd", "fundamental research",
    ],
    "Government & Municipal": [
        "municipal", "municipality", "city government", "county", "town",
        "wastewater", "public works", "village", "water treatment", "state facility",
    ],
}

# Fuel type keyword mappings
FUEL_KEYWORDS = {
    "Electricity": ["electricity", "electric", "power", "grid power", "kwh", "mwh", "high voltage", "power grid"],
    "Solar": ["solar", "photovoltaic", "pv", "solar cell", "perovskite", "solar array", "bifacial", "solar module"],
    "Wind": ["wind", "wind turbine", "offshore wind", "onshore wind", "floating wind"],
    "Hydrogen": ["hydrogen", "clean hydrogen", "green hydrogen", "electrolyzer", "fuel cell", "pem", "soec", "h2", "ammonia"],
    "Battery Storage": ["battery", "bess", "energy storage", "lithium-ion", "flow battery", "solid-state", "ldes", "zinc-air", "iron-air"],
    "Biomass / Biogas": ["biomass", "biogas", "rng", "renewable natural gas", "anaerobic digester", "biofuel", "wood heater", "wood stove", "pellet"],
    "Geothermal": ["geothermal", "ground-source", "district geothermal", "enhanced geothermal", "egs", "borehole"],
    "Nuclear": ["nuclear", "smr", "small modular reactor", "fission", "fusion", "uranium", "haleu"],
    "Natural Gas": ["natural gas", "pipeline methane", "lng", "cng", "fossil gas"],
}


def extract_profile(
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
) -> ProjectProfile:
    """Extract a structured project profile from free-text description.

    Uses keyword matching for deterministic extraction, then merges
    user-provided structured selections (technology_areas, activity_types, etc.)
    which take priority.
    """
    profile = ProjectProfile()
    text_lower = (text or "").lower()

    # Technology areas — start with user selections, augment from keywords
    if technology_areas:
        profile.technology_areas = list(technology_areas)

    if text_lower:
        for tech, keywords in TECHNOLOGY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    if tech not in profile.technology_areas:
                        profile.technology_areas.append(tech)
                    break

    # Activity types — start with user selections, augment from keywords
    if activity_types:
        profile.activity_types = list(activity_types)

    if text_lower:
        for activity, keywords in ACTIVITY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    if activity not in profile.activity_types:
                        profile.activity_types.append(activity)
                    break

    # Sectors — start with user selections, augment from keywords
    if sectors:
        profile.sectors = list(sectors)

    if text_lower:
        for sector, keywords in SECTOR_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    if sector not in profile.sectors:
                        profile.sectors.append(sector)
                    break

    # Fuel types — start with user selections, augment from keywords
    if fuel_types:
        profile.fuel_types = list(fuel_types)

    if text_lower:
        for fuel, keywords in FUEL_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    if fuel not in profile.fuel_types:
                        profile.fuel_types.append(fuel)
                    break

    # Store structured sectors and fuels mappings to tech areas
    if profile.sectors:
        sector_tech_map = {
            "Residential Buildings": ["Buildings", "Building Electrification"],
            "Multifamily Housing": ["Multifamily Buildings", "Building Electrification"],
            "Commercial Buildings": ["Buildings", "Building Electrification"],
            "Industrial & Manufacturing": ["Industrial Decarbonization", "Clean Energy Manufacturing"],
            "Transportation & Mobility": ["Clean Transportation"],
            "Agriculture & Forestry": ["Environmental Research"],
            "Electric Grid & Utility": ["Grid Modernization"],
            "Government & Municipal": [],
            "Higher Education & Research": ["Workforce Development"],
        }
        for sector in profile.sectors:
            for tech in sector_tech_map.get(sector, []):
                if tech not in profile.technology_areas:
                    profile.technology_areas.append(tech)

    # Fuel types (map to technology areas)
    if profile.fuel_types:
        fuel_tech_map = {
            "Hydrogen": ["Hydrogen & Alternative Fuels"],
            "Natural Gas": [],
            "Electricity": ["Building Electrification"],
            "Solar": ["Solar"],
            "Wind": ["Wind"],
            "Geothermal": ["Thermal Energy Networks"],
            "Biomass / Biogas": ["Hydrogen & Alternative Fuels"],
            "Nuclear": [],
            "Battery Storage": ["Energy Storage"],
        }
        for fuel in profile.fuel_types:
            for tech in fuel_tech_map.get(fuel, []):
                if tech not in profile.technology_areas:
                    profile.technology_areas.append(tech)

    # Extract domain keywords and multi-word concepts from free text
    profile.keywords, profile.extracted_phrases = extract_domain_keywords(text or "")

    # TRL estimation from keywords
    if trl is not None:
        profile.estimated_trl = trl
    else:
        profile.estimated_trl = _estimate_trl(text_lower) if text_lower else None

    # Applicant type
    if applicant_type:
        profile.applicant_type = applicant_type
    elif text_lower:
        profile.applicant_type = _infer_applicant_type(text_lower)

    # Target location
    if location:
        profile.target_location = location
        if location.upper() in ("NY", "NEW YORK", "NYC"):
            profile.ny_location = location
    elif text_lower:
        profile.target_location = _extract_location(text or "")
        if profile.target_location and profile.target_location.upper() in ("NY", "NEW YORK", "NYC"):
            profile.ny_location = profile.target_location

    # Project cost
    if cost:
        profile.project_cost = cost
    elif text_lower:
        profile.project_cost = _extract_cost(text or "")

    # Timeline
    profile.project_timeline = timeline

    # Partners
    if partners:
        profile.partners = [p.strip() for p in partners.split(",")]

    # Generate summary
    tech_str = ", ".join(profile.technology_areas[:3]) if profile.technology_areas else "unspecified technology"
    activity_str = ", ".join(profile.activity_types[:3]) if profile.activity_types else "unspecified activities"
    profile.summary = f"Project involving {tech_str} with {activity_str} activities"
    if profile.estimated_trl:
        profile.summary += f" at TRL {profile.estimated_trl}"

    # Decompose into workstreams
    profile.workstreams = _decompose_workstreams(text_lower, profile)

    # Note uncertainties
    if not profile.technology_areas:
        profile.uncertainties.append("Could not determine specific technology area from description")
    if not profile.target_location:
        profile.uncertainties.append("No location mentioned — programs may require specific nexus")
    if not profile.estimated_trl:
        profile.uncertainties.append("Could not estimate technology readiness level")

    return profile


def extract_domain_keywords(text: str) -> tuple[list[str], list[str]]:
    """Extract domain keywords and 2-3 word key phrases from project text."""
    if not text:
        return [], []

    text_clean = text.lower()
    
    # Specific high-value clean energy and compute domain key phrases
    curated_phrases = [
        "data center", "datacenter", "immersion cooling", "direct liquid cooling",
        "liquid cooling", "chip cooling", "thermal management", "server cooling",
        "clean microgrid", "microgrid", "long duration storage", "energy storage",
        "bess", "battery storage", "carbon free", "grid modernization",
        "power electronics", "power safety", "power systems", "islanding",
        "demand response", "virtual power plant", "v2g", "vehicle to grid",
        "heat pump", "thermal energy network", "clean hydrogen", "electrolyzer",
        "fuel cell", "industrial decarbonization", "waste heat recovery",
        "semiconductor packaging", "photovoltaic", "solar storage",
    ]
    matched_curated = [p for p in curated_phrases if p in text_clean]

    # Tokenize words
    stopwords = {
        "and", "the", "for", "with", "from", "that", "this", "into", "pilot",
        "scale", "project", "next", "generation", "incorporating", "achieve",
        "design", "deployment", "system", "systems", "high", "our", "are",
        "will", "have", "been", "using", "used", "such", "than", "other",
    }
    raw_words = re.findall(r"[a-z0-9\-\_]{3,}", text_clean)
    meaningful_words = [w for w in raw_words if w not in stopwords]

    # Generate n-grams (2-word phrases)
    bigrams = []
    for i in range(len(meaningful_words) - 1):
        bigrams.append(f"{meaningful_words[i]} {meaningful_words[i+1]}")

    all_phrases = list(dict.fromkeys(matched_curated + bigrams[:12]))
    all_keywords = list(dict.fromkeys(matched_curated + meaningful_words[:20]))

    return all_keywords, all_phrases


def _estimate_trl(text: str) -> Optional[int]:
    """Estimate TRL from description keywords."""
    # TRL 1-3: Basic research
    if any(w in text for w in ["basic research", "theoretical", "concept", "literature review"]):
        return 2
    # TRL 3-4: Proof of concept
    if any(w in text for w in ["proof of concept", "lab scale", "laboratory", "bench scale"]):
        return 3
    # TRL 4-5: Validation
    if any(w in text for w in ["prototype", "validation", "simulated environment"]):
        return 5
    # TRL 5-6: Demonstration
    if any(w in text for w in ["demonstration", "pilot", "field test", "relevant environment"]):
        return 6
    # TRL 7-8: System/subsystem development
    if any(w in text for w in ["commercial", "market ready", "production", "manufacturing", "scale up"]):
        return 8
    # TRL 9: Deployed
    if any(w in text for w in ["deployed", "operating", "proven", "in service", "installed base"]):
        return 9
    return None


def _infer_applicant_type(text: str) -> Optional[str]:
    """Infer applicant type from description."""
    if any(w in text for w in ["university", "academic", "professor", "researcher"]):
        return "university"
    if any(w in text for w in ["startup", "start-up", "early stage company"]):
        return "startup"
    if any(w in text for w in ["utility", "electric utility", "gas utility"]):
        return "utility"
    if any(w in text for w in ["municipality", "city", "county", "town", "village", "public sector"]):
        return "municipality"
    if any(w in text for w in ["company", "corporation", "manufacturer", "business", "firm"]):
        return "business"
    if any(w in text for w in ["non-profit", "nonprofit", "NGO"]):
        return "nonprofit"
    return None


def _extract_location(text: str) -> Optional[str]:
    """Extract location from text."""
    cities = [
        "New York City", "NYC", "Manhattan", "Brooklyn", "Queens", "Bronx",
        "Staten Island", "Long Island", "Buffalo", "Rochester", "Syracuse",
        "Albany", "Yonkers", "Schenectady", "Ithaca", "Binghamton",
        "Utica", "Poughkeepsie", "Westchester", "Nassau", "Suffolk",
        "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin",
        "Jacksonville", "Fort Worth", "Columbus", "San Francisco",
        "Charlotte", "Indianapolis", "Seattle", "Denver", "Washington", "Boston"
    ]
    for city in cities:
        if city.lower() in text.lower():
            return city

    if "new york" in text.lower() or " ny " in text.lower():
        return "New York State"
    return None


def _extract_cost(text: str) -> Optional[float]:
    """Extract project cost from text."""
    patterns = [
        r'\$\s*([\d,.]+)\s*(million|M)\b',
        r'\$\s*([\d,.]+)\s*(billion|B)\b',
        r'\$\s*([\d,.]+)\s*(thousand|K)\b',
        r'budget\s*(?:of\s*)?\$\s*([\d,.]+)',
        r'project\s*cost\s*(?:of\s*)?\$\s*([\d,.]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1).replace(",", ""))
            if len(match.groups()) > 1:
                unit = match.group(2).lower()
                if unit in ("million", "m"):
                    value *= 1_000_000
                elif unit in ("billion", "b"):
                    value *= 1_000_000_000
                elif unit in ("thousand", "k"):
                    value *= 1_000
            return value
    return None


def _decompose_workstreams(text: str, profile: ProjectProfile) -> list[dict]:
    """Decompose project into legitimate constituent workstreams."""
    workstreams = []

    # Only add workstreams for activities actually present in the project
    workstream_defs = [
        ("R&D", "Research & Development", "Core R&D activities including fundamental research, experiments, and analysis"),
        ("Feasibility Study", "Feasibility & Modeling", "Technical and economic feasibility assessments"),
        ("Product Development", "Product/Technology Development", "Engineering, prototyping, and product development"),
        ("Testing & Validation", "Testing & Validation", "Laboratory and field testing, performance validation, certification"),
        ("Software & Controls", "Software & Controls Development", "Software platforms, control algorithms, analytics tools"),
        ("Demonstration", "Demonstration & Pilot", "Field demonstration at a relevant site or environment"),
        ("Deployment", "Deployment & Installation", "Full-scale deployment and installation"),
        ("Utility Integration", "Utility Integration", "Grid interconnection, utility coordination, rate structures"),
        ("Host-Site Deployment", "Host-Site Deployment", "Deployment at customer/host facility"),
        ("Measurement & Verification", "Measurement & Verification", "Performance monitoring, data collection, M&V"),
        ("Manufacturing", "Manufacturing Scale-up", "Production facility, manufacturing process, supply chain"),
        ("Commercialization", "Commercialization", "Market entry, sales channels, customer development"),
        ("Community & DAC", "Community & DAC Engagement", "Disadvantaged community benefits, environmental justice"),
    ]

    for activity_key, name, description in workstream_defs:
        if activity_key in profile.activity_types:
            # Determine which technologies this workstream involves
            relevant_tech = profile.technology_areas  # default: all
            workstreams.append({
                "name": name,
                "description": description,
                "activity_type": activity_key,
                "technology_areas": relevant_tech,
                "separable": True,  # Could be funded independently
            })

    return workstreams
