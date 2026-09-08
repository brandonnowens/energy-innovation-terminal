"""
Centralized Energy Innovation Relevance and Negative Filtering Engine.

Ensures only genuine clean energy, energy transition, grid modernization,
decarbonization, and advanced energy hardware/software opportunities and awards
are ingested and maintained in the Energy Innovation Terminal database.

Eliminates false positives from biomedical, reproductive health, clinical medicine,
pharmaceuticals, surgery, pure astrophysics, and non-energy military systems.
"""

import re
from typing import Tuple, Optional

# ==============================================================================
# COMPREHENSIVE NEGATIVE / EXCLUSION PATTERNS
# ==============================================================================

EXCLUSION_PATTERNS = [
    # 1. Human health, reproductive medicine, gynecology, obstetrics
    r"\b(contracept\w*|birth control|vaginal\w*|cervical\w*|uter\w*|ovarian\w*|pregnancy|pregnant|childbirth|preterm labor|menstrual\w*|obstetric\w*|gynecolog\w*|fertility|infertility|sperm\w*|testicular|prostate cancer|endometriosis|mammograph\w*|breast cancer)\b",
    
    # 2. Medical diaphragms (disambiguated: allow electrolyzer/fuel cell/compressor diaphragm)
    r"\bdiaphragm\b(?!\s*(?:compressor|pump\b|electrolyzer|fuel cell|membrane|cell separator|electrochemical))",
    
    # 3. Oncology & Cancer biology
    r"\b(cancer|oncolog\w*|tumor\w*|neoplasm\w*|leukemia|melanoma|carcinoma|sarcoma|chemotherap\w*|radiotherap\w*\b(?!.*(?:reactor|nuclear power)))\b",
    
    # 4. Cardiovascular, pulmonary & organ systems
    r"\b(cardiac|cardiovascular|cardiopulmonary|artery|arteries|heart disease|stroke\b(?!.*(?:thermal|line))|pacemaker|angioplasty|arrhythmia|blood vessel\w*|vascular|blood pressure|hemoglobin|plasma donor|dialysis)\b",
    
    # 5. Pharmaceuticals, therapeutics & drug discovery
    r"\b(pharmaceutical\w*|therapeutic drug\w*|drug delivery|drug discovery|pharmacokin\w*|pharmacology|pharmacotherapy|antibiotic\w*|antimicrobial\b(?!.*(?:coating|marine antifouling|fouling))|antiviral|analgesic|opioid|anesthetic)\b",
    
    # 6. Clinical medicine, neurology, surgery, implants & diseases
    r"\b(clinical trial\w*|clinical study|clinical studies|in-silico evaluation of automated perfusion|patient-circuit|prosthetic\w*|orthopedic\w*|dental\w*|orthodontic|implantable sensor\w*|brain-machine|neurological\w*|alzheimer\w*|parkinson\w*|diabetes|insulin|kidney disease|pulmonary bypass)\b",
    r"\b(surgery|surgical\w*|minimally invasive surgical|endoscop\w*|laparoscop\w*|surgeon\w*|operating room|hospital patient\w*|intensive care)\b",
    
    # 7. Infectious disease, virology & immunology
    r"\b(infectious disease\w*|hiv\b(?!.*(?:navigation|visual aids))|aids\b(?!.*(?:navigation|visual aids))|tuberculosis|malaria|pathogen\w*|viral infection\w*|virus\b(?!.*(?:cyber|computer))|vaccine\w*|vaccination|immunology|immunotherap\w*|antibody|antibodies|antigen\w*)\b",
    
    # 8. Pure biology / genetics / cell culture (without bioenergy context)
    r"\b(gene therapy|crispr|tissue engineering|histology|biomarker\w*|dna sequencing|mrna|cell culture\b(?!.*(?:fuel|biofuel|algae|biomass))|cellular signaling\b(?!.*(?:telecom|grid)))\b",
    
    # 9. Pure astrophysics & deep cosmology (unrelated to terrestrial solar/energy tech)
    r"\b(dark matter|exoplanet\w*|astronom\w*|astrophysic\w*|cosmolog\w*|black hole\w*|telescope\b(?!.*(?:optical solar))|stellar corona|galaxy cluster\w*|quasars|pulsars|supernova\w*)\b",
    
    # 10. Military weaponry / ordnance / tactical combat (unrelated to clean operational base power)
    r"\b(missile guidance|warhead\w*|projectile\w*|artillery|gunshot|ammunition|explosive ordnance|lethal payload|torpedo\b(?!.*(?:turbine|hydro))|combat helmet|aircraft occupant safety during ejection|ejection seat)\b",
]

COMPILED_EXCLUSIONS = [re.compile(p, re.IGNORECASE) for p in EXCLUSION_PATTERNS]

# ==============================================================================
# HIGH-PRECISION POSITIVE CLEAN ENERGY INNOVATION PATTERNS
# ==============================================================================

POSITIVE_ENERGY_PATTERNS = [
    # Solar Photovoltaics & Systems
    r"\b(solar|photovoltaic\w*|\bpv\b|perovskite|agrivoltaic\w*|heliostat|concentrated solar|bifacial solar|rooftop solar|community solar|utility-scale solar)\b",
    
    # Wind Energy & Offshore Systems
    r"\b(wind (?:energy|power|turbine\w*|farm\w*|generation|resource)|offshore wind|onshore wind|floating wind|nadir wind)\b",
    
    # Energy Storage & Advanced Batteries
    r"\b(battery|batteries|energy storage|\bbess\b|lithium[- ]ion|flow battery|flow batteries|solid[- ]state battery|solid[- ]state batteries|iron[- ]air|sodium[- ]ion|zinc[- ]air|ldes|long[- ]duration energy storage|thermal energy storage|mechanical storage|compressed air energy storage|pumped storage hydro|battery management system|\bbms\b|battery recycling|stationary storage)\b",
    
    # Grid Modernization, Transmission & Smart Power
    r"\b(grid modernization|smart grid|microgrid\w*|power grid|electric grid|transmission line\w*|power distribution|substation automation|\bderms\b|\badms\b|dynamic line rating|\bdlr\b|high voltage direct current|\bhvdc\b|grid-forming|grid-interactive|power electronics|smart inverter\w*|inverters\b|synchrophasor|\bpmu\b|\bami\b|advanced metering|demand response|distributed energy resource\w*|\bder\b|\bders\b|virtual power plant|\bvpp\b|non-wires solution\w*|\bnws\b|\bnwa\b)\b",
    
    # Building Decarbonization, Heat Pumps & Thermal Networks
    r"\b(heat pump\w*|cold-climate heat pump\w*|air-source heat pump\w*|ground-source heat pump\w*|building electrification|building decarbonization|building efficiency|energy efficiency in buildings|whole-building|weatherization|building envelope|building insulation|\bhvac\b|smart thermostat|thermal energy network\w*|utility thermal energy network\w*|\btens\b|district heating|district geothermal)\b",
    
    # Electric Vehicles, Charging & Clean Transit
    r"\b(electric vehicle\w*|\bevs\b|zero-emission vehicle\w*|\bzev\b|\bzevs\b|ev charging|ev chargers|charging infrastructure|fast charging|\bdcfc\b|megawatt charging system|\bmcs\b|vehicle-to-grid|\bv2g\b|fleet electrification|electric transit|electric bus|electric buses|electric truck|electric trucks|clean transportation|e-mobility)\b",
    
    # Hydrogen & Clean Fuel Cells
    r"\b(clean hydrogen|green hydrogen|blue hydrogen|electrolyzer\w*|water electrolysis|pem electrolysis|solid oxide electrolysis|\bsoec\b|fuel cell\w*|solid oxide fuel cell\w*|\bsofc\b|\bpemfc\b|stationary fuel cell\w*|hydrogen infrastructure|hydrogen pipeline|hydrogen storage|hydrogen fuel)\b",
    
    # Industrial Decarbonization & Clean Heat
    r"\b(industrial decarbonization|clean process heat|industrial heat pump\w*|green steel|\bh2-dri\b|low-carbon cement|clinker substitution|industrial electrification|chemical decarbonization|high-temperature thermal|industrial emissions reduction)\b",
    
    # Nuclear & Advanced SMRs / Fusion
    r"\b(small modular reactor\w*|\bsmr\b|\bsmrs\b|advanced nuclear|advanced reactor\w*|gen iv reactor|sodium-cooled fast reactor|high-temperature gas-cooled reactor|\bhtgr\b|\bhaleu\b|nuclear fusion|fusion energy|stellarator|tokamak|fission power|clean nuclear)\b",
    
    # Carbon Management & Direct Air Capture
    r"\b(carbon capture|carbon capture and storage|\bccs\b|carbon capture utilization and storage|\bccus\b|direct air capture|\bdac\b|carbon dioxide removal|\bcdr\b|carbon mineralization|point-source capture|carbon sequestration|geologic storage of co2)\b",
    
    # Bioenergy & Sustainable Fuels
    r"\b(biofuel\w*|sustainable aviation fuel\w*|\bsaf\b|biomass energy|biogas|renewable natural gas|\brng\b|anaerobic digestion|anaerobic digester\w*|biomethane|biomass-to-energy|bio-oil|cellulosic ethanol)\b",
    
    # Geothermal & Subsurface Energy
    r"\b(geothermal|enhanced geothermal|\begs\b|deep geothermal|supercritical geothermal|geothermal brine|subsurface energy|geothermal district heating)\b",
    
    # Water & Hydrokinetics
    r"\b(hydropower|hydroelectric|hydrokinetic\w*|marine energy|tidal energy|wave energy|ocean energy|river current energy|run-of-river)\b",
    
    # AI & Energy Computing
    r"\b(artificial intelligence for energy|machine learning for grid|ai-driven grid|energy data analytics|digital twin for power|grid cybersecurity|energy management software|scada security|predictive maintenance for turbines)\b",
    
    # Cross-cutting Clean Energy Innovation
    r"\b(clean energy technology|clean energy innovation|energy transition|cleantech|clean tech|clean power|renewable power|clean electricity|power generation|decarboniz\w*|net[- ]zero|zero[- ]carbon|low[- ]carbon power|emissions reduction|ghg abatement)\b",
]

COMPILED_POSITIVES = [re.compile(p, re.IGNORECASE) for p in POSITIVE_ENERGY_PATTERNS]

# Core energy institutions whose solicitations are inherently clean energy focused
CORE_ENERGY_AGENCIES = {
    "NYSERDA", "DOE", "DOE-EERE", "DOE-ARPAE", "ARPA-E", "DOE-NETL", "DOE-SC",
    "DOE-OE", "DOE-OCED", "DOE-MESC", "CEC", "MASSCEC", "NY GREEN BANK",
    "GREEN BANK", "CALIFORNIA ENERGY COMMISSION"
}

def is_energy_innovation_relevant(
    title: Optional[str] = None,
    text_content: Optional[str] = None,
    agency: Optional[str] = None,
    keywords: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Authoritative relevance evaluation for opportunities, awards, and proposals.
    
    Returns:
        (is_valid: bool, rationale: str)
    """
    combined = f"{title or ''} {text_content or ''} {keywords or ''}"
    
    # 1. Run strict negative exclusion filters first
    for exc in COMPILED_EXCLUSIONS:
        m = exc.search(combined)
        if m:
            matched_term = m.group(0)
            return False, f"Excluded by negative non-energy filter: '{matched_term}'"
            
    # 2. Check if originated from a core dedicated energy agency (NYSERDA, DOE EERE/ARPA-E, CEC, MassCEC)
    agency_clean = (agency or "").upper().strip()
    if any(core in agency_clean for core in CORE_ENERGY_AGENCIES):
        return True, f"Core clean energy agency: {agency}"
        
    # 3. Check for genuine clean energy innovation pattern matches
    for pos in COMPILED_POSITIVES:
        if pos.search(combined):
            return True, "Matched verified clean energy pattern"
            
    return False, "No clean energy innovation pattern match"


def clean_opportunity_text(text_val: Optional[str]) -> str:
    """Normalize text content for classification."""
    if not text_val:
        return ""
    # Strip HTML tags
    clean = re.sub(r'<[^>]+>', ' ', text_val)
    # Strip non-printable chars
    clean = re.sub(r'[\u200b\u200c\u200d\ufeff\u200e\u200f\u202a\u202c\xa0]', ' ', clean)
    # Normalize whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean
