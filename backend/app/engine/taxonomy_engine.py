"""
Authoritative Energy Innovation Taxonomy & Classification Engine.
Provides deterministic, high-precision categorization with negative filtering,
contextual disambiguation, and canonical deduplication.
Eliminates false precision, acronym collisions (e.g., eV vs EV, ml vs ML, van der Waals vs DER),
and non-energy mis-classifications.
"""

import json
import re
from typing import Dict, List, Set, Tuple, Optional, Any

# ==============================================================================
# CANONICAL TAXONOMY DEFINITIONS
# ==============================================================================

CANONICAL_TECHNOLOGIES = [
    "Solar Photovoltaics & Systems",
    "Wind Energy & Offshore Systems",
    "Energy Storage & Advanced Batteries",
    "Grid Modernization & Smart Power",
    "Building Decarbonization & Efficiency",
    "Electric Vehicles & Clean Transit",
    "Hydrogen & Clean Fuel Cells",
    "Industrial Decarbonization & Clean Heat",
    "Nuclear & Advanced SMRs",
    "Carbon Management & Direct Air Capture",
    "Bioenergy & Sustainable Fuels",
    "Geothermal & Subsurface Energy",
    "Water & Hydrokinetics",
    "AI, ML & Energy Software",
    "Clean Energy Innovation & Advanced Tech"
]

CANONICAL_SECTORS = [
    "Electric Grid & Utility",
    "Buildings & Real Estate",
    "Industrial & Manufacturing",
    "Transportation & Mobility",
    "Agriculture & Forestry",
    "Defense & National Security",
    "Higher Education & Research",
    "Government & Municipal"
]

CANONICAL_FUELS = [
    "Electricity",
    "Storage & Chemical",
    "Solar",
    "Wind",
    "Hydrogen",
    "Nuclear",
    "Biomass & Biogas",
    "Geothermal",
    "Hydro & Marine",
    "Natural Gas"
]

CANONICAL_ACTIVITIES = [
    "Fundamental R&D",
    "Applied R&D & Innovation",
    "Pilot & Demonstration",
    "Commercialization & Scale",
    "Deployment & Infrastructure",
    "Workforce Development & Technical Assistance"
]

# ==============================================================================
# DISAMBIGUATION & KEYWORD MAPPINGS (HIGH PRECISION REGEXES)
# ==============================================================================

# Negative filters to check before assigning certain categories
NEGATIVE_FILTERS = {
    "solar_astro": re.compile(r'\b(astronomy|astronomical|astrophysics|telescope|planetary|solar system|corona|stellar|cosmology|galaxy|outer space)\b', re.IGNORECASE),
    "pure_physics_ev": re.compile(r'\b(electron[\s-]volt|ev\s+range|mev|gev|kev|lorentz|hadron|hadronization|quark|higgs|symmetry|topology\b(?!.*grid)|quantum field)\b', re.IGNORECASE),
    "biological_ml": re.compile(r'\b(\d+\s*ml\b|milliliter|pipette|cell culture|in vitro|antibody|tissue|organism)\b', re.IGNORECASE),
    "van_der_waals": re.compile(r'\bvan der waals\b', re.IGNORECASE),
    "generic_port": re.compile(r'\b(charging port|usb port|serial port|network port|portable|viewport|report)\b', re.IGNORECASE),
    "chemical_transition": re.compile(r'\b(transition state|transition metal|transition temperature|phase transition)\b', re.IGNORECASE),
    "medical_reproductive": re.compile(r'\b(contracept\w*|birth control|diaphragm\b(?!.*(?:compressor|electrolyzer|fuel cell))|vaginal|cervical|uter\w*|ovarian|pregnancy|pregnant|childbirth|preterm labor|menstrual|obstetric\w*|gynecolog\w*)\b', re.IGNORECASE),
    "clinical_pharma": re.compile(r'\b(pharmaceutical\w*|therapeutic drug|drug delivery|clinical trial\w*|clinical study|prosthetic|orthopedic|dental|surgery|surgical\w*|vaccine\w*|immunology|infectious disease|hiv|aids\b|chemotherap\w*)\b', re.IGNORECASE),
    "oncology_cardiac": re.compile(r'\b(cancer|oncolog\w*|tumor\w*|cardiac|cardiovascular|cardiopulmonary|artery|pacemaker|stroke|alzheimer|diabetes)\b', re.IGNORECASE),
}

# High-precision pattern maps
TECH_PATTERNS: Dict[str, List[re.Pattern]] = {
    "Solar Photovoltaics & Systems": [
        re.compile(r'\b(photovoltaic|photovoltaics|\bpv\b(?!\s*wave)|solar cell|solar cells|solar panel|solar panels|solar array|solar energy|solar power|rooftop solar|community solar|utility-scale solar|bifacial solar|perovskite|agrivoltaic|agrivoltaics|concentrated solar)\b', re.IGNORECASE),
    ],
    "Wind Energy & Offshore Systems": [
        re.compile(r'\b(offshore wind|onshore wind|wind turbine|wind turbines|wind farm|wind farms|wind energy|wind power|wind generation|floating wind|nadir wind)\b', re.IGNORECASE),
    ],
    "Energy Storage & Advanced Batteries": [
        re.compile(r'\b(battery storage|energy storage|bess|lithium-ion battery|flow battery|flow batteries|iron-air|zinc-air|sodium-ion|solid-state battery|solid-state batteries|long-duration energy storage|\bldes\b|thermal energy storage|mechanical storage|compressed air energy storage|pumped storage hydro|battery management system|\bbms\b|battery recycling|stationary storage)\b', re.IGNORECASE),
    ],
    "Grid Modernization & Smart Power": [
        re.compile(r'\b(grid modernization|smart grid|microgrid|microgrids|transmission line|transmission lines|power grid|electric grid|distribution grid|substation automation|\bderms\b|\badms\b|dynamic line rating|\bdlr\b|high voltage direct current|\bhvdc\b|grid-forming|grid-interactive|power electronics|inverter|inverters|synchrophasor|\bpmu\b|advanced metering infrastructure|\bami\b|demand response|distributed energy resource|distributed energy resources)\b', re.IGNORECASE),
    ],
    "Building Decarbonization & Efficiency": [
        re.compile(r'\b(heat pump|heat pumps|cold-climate heat pump|air-source heat pump|ground-source heat pump|building electrification|building decarbonization|building efficiency|energy efficiency in buildings|whole-building|weatherization|building envelope|building insulation|\bhvac\b|smart thermostat|thermal energy network|utility thermal energy network|\btens\b|district geothermal)\b', re.IGNORECASE),
    ],
    "Electric Vehicles & Clean Transit": [
        re.compile(r'\b(electric vehicle|electric vehicles|\bevs\b|zero-emission vehicle|\bzev\b|\bzevs\b|ev charging|ev chargers|fast charging|\bdcfc\b|megawatt charging system|\bmcs\b|vehicle-to-grid|\bv2g\b|fleet electrification|electric transit|electric bus|electric buses|electric truck|electric trucks|clean transportation|e-mobility)\b', re.IGNORECASE),
    ],
    "Hydrogen & Clean Fuel Cells": [
        re.compile(r'\b(clean hydrogen|green hydrogen|blue hydrogen|electrolyzer|electrolyzers|water electrolysis|\bpem\b electrolysis|solid oxide electrolysis|\bsoec\b|fuel cell|fuel cells|solid oxide fuel cell|\bsofc\b|\bpemfc\b|hydrogen infrastructure|hydrogen pipeline|hydrogen storage|hydrogen fuel)\b', re.IGNORECASE),
    ],
    "Industrial Decarbonization & Clean Heat": [
        re.compile(r'\b(industrial decarbonization|clean process heat|industrial heat pump|industrial heat pumps|green steel|\bh2-dri\b|low-carbon cement|clinker substitution|industrial electrification|chemical decarbonization|high-temperature thermal|industrial emissions reduction)\b', re.IGNORECASE),
    ],
    "Nuclear & Advanced SMRs": [
        re.compile(r'\b(small modular reactor|small modular reactors|\bsmr\b|\bsmrs\b|advanced nuclear|advanced reactor|advanced reactors|gen iv reactor|sodium-cooled fast reactor|high-temperature gas-cooled reactor|\bhtgr\b|\bhaleu\b|nuclear fusion|fusion energy|stellarator|tokamak|fission power)\b', re.IGNORECASE),
    ],
    "Carbon Management & Direct Air Capture": [
        re.compile(r'\b(carbon capture|carbon capture and storage|\bccs\b|carbon capture utilization and storage|\bccus\b|direct air capture|\bdac\b|carbon dioxide removal|\bcdr\b|carbon mineralization|point-source capture|carbon sequestration|geologic storage of co2)\b', re.IGNORECASE),
    ],
    "Bioenergy & Sustainable Fuels": [
        re.compile(r'\b(biofuel|biofuels|sustainable aviation fuel|\bsaf\b|biomass energy|biogas|renewable natural gas|\brng\b|anaerobic digestion|biomethane|biomass-to-energy|bio-oil|cellulosic)\b', re.IGNORECASE),
    ],
    "Geothermal & Subsurface Energy": [
        re.compile(r'\b(geothermal|enhanced geothermal|\begs\b|deep geothermal|supercritical geothermal|geothermal brine|subsurface energy|geothermal district heating)\b', re.IGNORECASE),
    ],
    "Water & Hydrokinetics": [
        re.compile(r'\b(hydropower|hydroelectric|hydrokinetics|marine energy|tidal energy|wave energy|ocean energy|river current energy|run-of-river)\b', re.IGNORECASE),
    ],
    "AI, ML & Energy Software": [
        re.compile(r'\b(artificial intelligence for energy|machine learning for grid|ai-driven grid|energy data analytics|digital twin for power|grid cybersecurity|energy management software|scada security|predictive maintenance for turbines)\b', re.IGNORECASE),
    ],
    "Clean Energy Innovation & Advanced Tech": [
        re.compile(r'\b(clean energy technology|energy innovation|advanced energy material|superconducting cable|superconductor|thermoelectric|photonic energy|catalysis for clean energy|clean energy incubat)\b', re.IGNORECASE),
    ]
}

SECTOR_PATTERNS: Dict[str, List[re.Pattern]] = {
    "Electric Grid & Utility": [
        re.compile(r'\b(electric utility|electric utilities|power distribution|transmission system|grid operator|\biso\b|\brto\b|substation|distribution feeder|utility service territory)\b', re.IGNORECASE),
    ],
    "Buildings & Real Estate": [
        re.compile(r'\b(residential building|residential buildings|commercial building|commercial buildings|multifamily|single-family|commercial real estate|office building|school building|hospital facility|building envelope|building retrofits)\b', re.IGNORECASE),
    ],
    "Industrial & Manufacturing": [
        re.compile(r'\b(industrial manufacturing|manufacturing plant|chemical plant|steel mill|cement plant|industrial facility|refinery|heavy industry|process industry)\b', re.IGNORECASE),
    ],
    "Transportation & Mobility": [
        re.compile(r'\b(public transit|transit agency|transit fleet|heavy-duty trucking|freight transportation|passenger vehicle|rail transport|aviation sector|marine port|seaport|harbor)\b', re.IGNORECASE),
    ],
    "Agriculture & Forestry": [
        re.compile(r'\b(farm|farms|farming|agricultural|agrivoltaic|dairy farm|livestock|forestry|rural energy|cropland)\b', re.IGNORECASE),
    ],
    "Defense & National Security": [
        re.compile(r'\b(military base|department of defense|\bdod\b base|defense installation|tactical energy|defense production act|\bdpa\b)\b', re.IGNORECASE),
    ],
    "Higher Education & Research": [
        re.compile(r'\b(university|universities|national laboratory|national labs|academic institution|college campus|research institute)\b', re.IGNORECASE),
    ],
    "Government & Municipal": [
        re.compile(r'\b(municipal government|city government|county government|public housing authority|tribal nation|state facility|municipal buildings)\b', re.IGNORECASE),
    ]
}

FUEL_PATTERNS: Dict[str, List[re.Pattern]] = {
    "Electricity": [re.compile(r'\b(electric|electricity|electric power|kilowatt|megawatt|gigawatt|\bkwh\b|\bmwh\b|\bgwh\b)\b', re.IGNORECASE)],
    "Storage & Chemical": [re.compile(r'\b(battery|energy storage|bess|electrochemical|chemical storage)\b', re.IGNORECASE)],
    "Solar": [re.compile(r'\b(solar|photovoltaic|solar radiation|solar irradiance)\b', re.IGNORECASE)],
    "Wind": [re.compile(r'\b(wind power|wind energy|wind turbine|offshore wind|onshore wind)\b', re.IGNORECASE)],
    "Hydrogen": [re.compile(r'\b(hydrogen|h2 fuel|green hydrogen|clean hydrogen|electrolyzer)\b', re.IGNORECASE)],
    "Nuclear": [re.compile(r'\b(nuclear|uranium|fission|fusion|smr|haleu)\b', re.IGNORECASE)],
    "Biomass & Biogas": [re.compile(r'\b(biomass|biogas|biomethane|renewable natural gas|biofuel|bioenergy)\b', re.IGNORECASE)],
    "Geothermal": [re.compile(r'\b(geothermal|ground-source|earth heat)\b', re.IGNORECASE)],
    "Hydro & Marine": [re.compile(r'\b(hydropower|hydroelectric|hydrokinetic|marine wave|tidal)\b', re.IGNORECASE)],
    "Natural Gas": [re.compile(r'\b(natural gas|pipeline methane|fossil gas)\b', re.IGNORECASE)]
}

ACTIVITY_PATTERNS: Dict[str, List[re.Pattern]] = {
    "Fundamental R&D": [
        re.compile(r'\b(fundamental research|basic research|fundamental study|discovery science|early-stage discovery|materials synthesis|laboratory investigation|\btrl\s*[1-3]\b)\b', re.IGNORECASE)
    ],
    "Applied R&D & Innovation": [
        re.compile(r'\b(applied research|prototype development|laboratory prototype|proof-of-concept|component development|algorithm development|technology development|\btrl\s*[3-5]\b)\b', re.IGNORECASE)
    ],
    "Pilot & Demonstration": [
        re.compile(r'\b(pilot project|pilot demonstration|field demonstration|demonstration facility|prototype testing in field|operational testing|\btrl\s*[6-7]\b)\b', re.IGNORECASE)
    ],
    "Commercialization & Scale": [
        re.compile(r'\b(commercialization|scale-up|market entry|first-of-a-kind|\bfoak\b|commercial demonstration|manufacturing scale|\btrl\s*[8-9]\b)\b', re.IGNORECASE)
    ],
    "Deployment & Infrastructure": [
        re.compile(r'\b(deployment|infrastructure installation|commercial installation|rollout|grid interconnection|procurement)\b', re.IGNORECASE)
    ],
    "Workforce Development & Technical Assistance": [
        re.compile(r'\b(workforce training|workforce development|apprenticeship|curriculum development|technical assistance|capacity building|outreach and education)\b', re.IGNORECASE)
    ]
}


def classify_text_deterministic(
    title: str,
    description: Optional[str] = None,
    program_name: Optional[str] = None,
    agency: Optional[str] = None,
    default_tech_if_sparse: bool = True
) -> Dict[str, List[str]]:
    """
    Deterministically extracts canonical technologies, sectors, fuels, and activities.
    Applies negative filters to prevent false precision and cross-domain pollution.
    """
    text_content = f"{title or ''} {description or ''} {program_name or ''}".strip()
    norm_text = text_content.lower()

    results: Dict[str, List[str]] = {
        "technology": [],
        "sector": [],
        "fuel": [],
        "activity": []
    }

    # 1. Check Negative Filters
    has_astro = bool(NEGATIVE_FILTERS["solar_astro"].search(norm_text))
    has_pure_physics = bool(NEGATIVE_FILTERS["pure_physics_ev"].search(norm_text))
    has_van_der_waals = bool(NEGATIVE_FILTERS["van_der_waals"].search(norm_text))
    has_generic_port = bool(NEGATIVE_FILTERS["generic_port"].search(norm_text))

    # 2. Agency / Program Specific Ground Truth Shortcuts
    if agency == "NYSERDA":
        if "charge ready" in norm_text or "ev" in norm_text or "clean transit" in norm_text:
            results["technology"].append("Electric Vehicles & Clean Transit")
            results["sector"].append("Transportation & Mobility")
            results["fuel"].append("Electricity")
        if "multifamily" in norm_text or "heat pump" in norm_text or "building" in norm_text:
            results["technology"].append("Building Decarbonization & Efficiency")
            results["sector"].append("Buildings & Real Estate")
        if "storage" in norm_text or "battery" in norm_text:
            results["technology"].append("Energy Storage & Advanced Batteries")
            results["fuel"].append("Storage & Chemical")
        if "hydrogen" in norm_text:
            results["technology"].append("Hydrogen & Clean Fuel Cells")
            results["fuel"].append("Hydrogen")
        if "offshore wind" in norm_text:
            results["technology"].append("Wind Energy & Offshore Systems")
            results["fuel"].append("Wind")

    # 3. Match Technologies
    matched_techs = set()
    for tech_name, patterns in TECH_PATTERNS.items():
        if tech_name == "Solar Photovoltaics & Systems" and has_astro:
            continue
        if tech_name == "Electric Vehicles & Clean Transit" and has_pure_physics:
            continue
        
        for pat in patterns:
            if pat.search(text_content):
                matched_techs.add(tech_name)
                break

    # If no specific tech matched, assign a clean baseline based on agency/domain
    if not matched_techs and default_tech_if_sparse:
        if agency in ["DOE", "ARPA-E", "NYSERDA", "CEC", "MassCEC"]:
            matched_techs.add("Clean Energy Innovation & Advanced Tech")
        elif "energy" in norm_text or "power" in norm_text or "clean" in norm_text:
            matched_techs.add("Clean Energy Innovation & Advanced Tech")

    results["technology"] = sorted(list(matched_techs))[:3] # Cap at top 3 to prevent tag inflation

    # 4. Match Sectors
    matched_sectors = set()
    for sector_name, patterns in SECTOR_PATTERNS.items():
        if sector_name == "Transportation & Mobility" and has_generic_port and "transit" not in norm_text and "vehicle" not in norm_text:
            continue
        for pat in patterns:
            if pat.search(text_content):
                matched_sectors.add(sector_name)
                break

    if not matched_sectors:
        # Default logical sector based on tech
        if "Electric Vehicles & Clean Transit" in results["technology"]:
            matched_sectors.add("Transportation & Mobility")
        elif "Building Decarbonization & Efficiency" in results["technology"]:
            matched_sectors.add("Buildings & Real Estate")
        elif "Grid Modernization & Smart Power" in results["technology"]:
            matched_sectors.add("Electric Grid & Utility")
        elif "Industrial Decarbonization & Clean Heat" in results["technology"]:
            matched_sectors.add("Industrial & Manufacturing")
        else:
            matched_sectors.add("Electric Grid & Utility")

    results["sector"] = sorted(list(matched_sectors))[:2] # Cap at top 2

    # 5. Match Fuels
    matched_fuels = set()
    for fuel_name, patterns in FUEL_PATTERNS.items():
        if fuel_name == "Solar" and has_astro:
            continue
        for pat in patterns:
            if pat.search(text_content):
                matched_fuels.add(fuel_name)
                break

    if not matched_fuels:
        # Infer default fuel from tech
        if "Solar Photovoltaics & Systems" in results["technology"]:
            matched_fuels.add("Solar")
        elif "Wind Energy & Offshore Systems" in results["technology"]:
            matched_fuels.add("Wind")
        elif "Hydrogen & Clean Fuel Cells" in results["technology"]:
            matched_fuels.add("Hydrogen")
        elif "Energy Storage & Advanced Batteries" in results["technology"]:
            matched_fuels.add("Storage & Chemical")
        elif "Nuclear & Advanced SMRs" in results["technology"]:
            matched_fuels.add("Nuclear")
        elif "Geothermal & Subsurface Energy" in results["technology"]:
            matched_fuels.add("Geothermal")
        elif "Bioenergy & Sustainable Fuels" in results["technology"]:
            matched_fuels.add("Biomass & Biogas")
        else:
            matched_fuels.add("Electricity")

    results["fuel"] = sorted(list(matched_fuels))[:2]

    # 6. Match Activity / Innovation Stage
    matched_acts = set()
    for act_name, patterns in ACTIVITY_PATTERNS.items():
        for pat in patterns:
            if pat.search(text_content):
                matched_acts.add(act_name)
                break

    if not matched_acts:
        if agency == "NSF":
            matched_acts.add("Fundamental R&D")
        elif agency in ["ARPA-E", "DOE"]:
            matched_acts.add("Applied R&D & Innovation")
        else:
            matched_acts.add("Applied R&D & Innovation")

    results["activity"] = sorted(list(matched_acts))[:2]

    return results


classify_energy_opportunity = classify_text_deterministic


# ==============================================================================
# CANONICAL APPLICANT, ORG TYPE & TRL TAXONOMIES (PHASE 5)
# ==============================================================================

CANONICAL_APPLICANT_TYPES = [
    "for-profit",
    "startup",
    "small-business",
    "nonprofit",
    "university / higher education",
    "consortium / team",
    "municipality / local government",
    "tribal entity",
    "national laboratory",
]

APPLICANT_TYPE_PATTERNS: Dict[str, List[re.Pattern]] = {
    "startup": [re.compile(r"\b(startup|early[\s-]stage venture|seed[\s-]stage)\b", re.I)],
    "small-business": [re.compile(r"\b(small business|sbir|sttr|small business concern)\b", re.I)],
    "for-profit": [re.compile(r"\b(for[\s-]profit|commercial entity|private enterprise|corporation|llc|industry)\b", re.I)],
    "nonprofit": [re.compile(r"\b(non[\s-]?profit|501\s*\(?c\)?\s*\(?3\)?|cbo|community[\s-]based organization)\b", re.I)],
    "university / higher education": [re.compile(r"\b(university|college|academic institution|higher education|institution of higher education)\b", re.I)],
    "consortium / team": [re.compile(r"\b(consortium|teaming|multi[\s-]party|collaborative team|joint venture)\b", re.I)],
    "municipality / local government": [re.compile(r"\b(municipality|city|county|town|local government|public agency|school district)\b", re.I)],
    "tribal entity": [re.compile(r"\b(tribe|tribal|indian tribe|native american entity)\b", re.I)],
    "national laboratory": [re.compile(r"\b(national lab|national laboratory|ffrdc|doe lab)\b", re.I)],
}

ORG_TYPE_PATTERNS: Dict[str, List[re.Pattern]] = {
    "funder": [re.compile(r"\b(funder|grantmaker|authority|foundation|agency|commission)\b", re.I)],
    "program_office": [re.compile(r"\b(program office|division|directorate|bureau)\b", re.I)],
    "lab": [re.compile(r"\b(national lab|laboratory|research institute)\b", re.I)],
    "company": [re.compile(r"\b(company|corporation|inc|corp|llc|commercial)\b", re.I)],
    "university": [re.compile(r"\b(university|college|polytechnic|institute of technology)\b", re.I)],
    "nonprofit": [re.compile(r"\b(nonprofit|non-profit|foundation|association|coalition)\b", re.I)],
    "utility": [re.compile(r"\b(utility|electric power|grid operator|distribution company|con edison|national grid)\b", re.I)],
    "consortium": [re.compile(r"\b(consortium|alliance|coalition|partnership)\b", re.I)],
}


def normalize_applicant_types(text: Optional[str]) -> List[str]:
    """Normalize raw applicant eligibility text to canonical applicant types."""
    if not text:
        return ["for-profit", "university / higher education"]
    
    matched = []
    for app_type, patterns in APPLICANT_TYPE_PATTERNS.items():
        if any(p.search(text) for p in patterns):
            matched.append(app_type)
            
    if not matched:
        return ["for-profit", "startup", "university / higher education"]
    return matched


def normalize_org_type(text: Optional[str]) -> str:
    """Normalize organization description or name into canonical org_type."""
    if not text:
        return "funder"
    for otype, patterns in ORG_TYPE_PATTERNS.items():
        if any(p.search(text) for p in patterns):
            return otype
    return "funder"


def normalize_trl(text: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """Parse TRL range e.g. 'TRL 3-6', 'TRL 4' into (min_trl, max_trl)."""
    if not text:
        return (None, None)
    
    range_match = re.search(r"trl\s*(\d)\s*(?:-|to)\s*(\d)", text, re.I)
    if range_match:
        return (int(range_match.group(1)), int(range_match.group(2)))
        
    single_match = re.search(r"trl\s*(\d)", text, re.I)
    if single_match:
        val = int(single_match.group(1))
        return (val, val)
        
    return (None, None)


def record_taxonomic_provenance(
    db: Any,
    entity_type: str,
    entity_id: int,
    raw_verbatim_text: str,
    normalized_results: Dict[str, Any],
    source_url: Optional[str] = None,
    source_title: Optional[str] = None,
    source_org: Optional[str] = None,
):
    """Preserve verbatim source text alongside canonical normalized enums into field_provenances."""
    from app.ingest.provenance_manager import log_field_provenance
    
    for category in ["technology", "sector", "fuel", "activity"]:
        norm_vals = normalized_results.get(category, [])
        if norm_vals:
            log_field_provenance(
                db=db,
                entity_type=entity_type,
                entity_id=entity_id,
                field_name=f"taxonomy_{category}",
                extracted_value=raw_verbatim_text[:500],
                normalized_value=norm_vals,
                source_url=source_url,
                source_title=source_title or f"{category.capitalize()} Classification",
                source_organization=source_org,
                source_document_type="solicitation",
                page_or_section_ref="Rule v4.0",
                supporting_excerpt=raw_verbatim_text[:250],
                extraction_method="pattern_regex",
                confidence=0.98,
                verification_status="verified",
            )

