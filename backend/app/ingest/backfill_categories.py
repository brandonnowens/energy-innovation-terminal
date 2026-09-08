import re
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.opportunity import Opportunity, OpportunityCategory

# Define keyword mappings for categories
CATEGORY_MAP = {
    'technology': {
        'Solar PV': [r'\bsolar pv\b', r'\bphotovoltaic\b'],
        'Solar Thermal': [r'\bsolar thermal\b'],
        'Concentrated Solar': [r'\bconcentrated solar\b', r'\bcsp\b'],
        'Onshore Wind': [r'\bonshore wind\b'],
        'Offshore Wind': [r'\boffshore wind\b'],
        'Battery Storage': [r'\bbattery storage\b', r'\blithium-ion\b'],
        'Pumped Hydro': [r'\bpumped hydro\b'],
        'Compressed Air': [r'\bcompressed air\b'],
        'Thermal Storage': [r'\bthermal storage\b'],
        'Long-Duration Storage': [r'\blong-duration storage\b', r'\bldes\b'],
        'Green Hydrogen': [r'\bgreen hydrogen\b'],
        'Blue Hydrogen': [r'\bblue hydrogen\b'],
        'Electrolysis': [r'\belectrolysis\b', r'\belectrolyzer\b'],
        'Fuel Cells': [r'\bfuel cell\b', r'\bfuel cells\b'],
        'Geothermal': [r'\bgeothermal\b'],
        'Enhanced Geothermal': [r'\benhanced geothermal\b', r'\begs\b'],
        'Carbon Capture': [r'\bcarbon capture\b'],
        'Direct Air Capture': [r'\bdirect air capture\b', r'\bdac\b'],
        'CCUS': [r'\bccus\b', r'\bcarbon capture utilization and storage\b'],
        'Grid Modernization': [r'\bgrid modernization\b'],
        'Smart Grid': [r'\bsmart grid\b'],
        'Microgrids': [r'\bmicrogrid\b', r'\bmicrogrids\b'],
        'DERs': [r'\bder\b', r'\bders\b', r'\bdistributed energy resource\b'],
        'V2G': [r'\bv2g\b', r'\bvehicle-to-grid\b'],
        'Heat Pumps': [r'\bheat pump\b', r'\bheat pumps\b'],
        'Building Electrification': [r'\bbuilding electrification\b'],
        'Energy Efficiency': [r'\benergy efficiency\b'],
        'Electric Vehicles': [r'\belectric vehicle\b', r'\belectric vehicles\b', r'\bevs\b', r'\bev\b'],
        'EV Charging': [r'\bev charging\b', r'\bevsui\b'],
        'E-Mobility': [r'\be-mobility\b', r'\bemobility\b'],
        'Nuclear': [r'\bnuclear\b'],
        'SMR (Small Modular Reactor)': [r'\bsmr\b', r'\bsmall modular reactor\b'],
        'Advanced Nuclear': [r'\badvanced nuclear\b'],
        'Nuclear Fusion': [r'\bnuclear fusion\b', r'\bfusion energy\b'],
        'Biomass': [r'\bbiomass\b'],
        'Biogas': [r'\bbiogas\b'],
        'Biofuels': [r'\bbiofuel\b', r'\bbiofuels\b'],
        'RNG': [r'\brng\b', r'\brenewable natural gas\b'],
        'Hydropower': [r'\bhydropower\b', r'\bhydroelectric\b'],
        'Tidal': [r'\btidal\b'],
        'Wave Energy': [r'\bwave energy\b'],
        'Data Analytics': [r'\bdata analytics\b'],
        'AI/ML': [r'\bai\b', r'\bartificial intelligence\b', r'\bmachine learning\b', r'\bml\b'],
        'Digital Twins': [r'\bdigital twin\b', r'\bdigital twins\b'],
        'Cybersecurity': [r'\bcybersecurity\b', r'\bcyber-security\b'],
        'Superconductors': [r'\bsuperconductor\b', r'\bsuperconductors\b'],
        'Advanced Materials': [r'\badvanced material\b', r'\badvanced materials\b'],
        'Weatherization': [r'\bweatherization\b'],
        'Insulation': [r'\binsulation\b'],
        'Building Envelope': [r'\bbuilding envelope\b']
    },
    'fuel': {
        'Solar': [r'\bsolar\b'],
        'Wind': [r'\bwind\b'],
        'Hydrogen': [r'\bhydrogen\b'],
        'Natural Gas': [r'\bnatural gas\b'],
        'Biomass': [r'\bbiomass\b'],
        'Geothermal': [r'\bgeothermal\b'],
        'Nuclear': [r'\bnuclear\b'],
        'Coal': [r'\bcoal\b'],
        'Petroleum': [r'\bpetroleum\b'],
        'Electricity': [r'\belectricity\b'],
        'Biofuels': [r'\bbiofuels\b', r'\bbiofuel\b'],
        'RNG': [r'\brng\b', r'\brenewable natural gas\b'],
        'Diesel': [r'\bdiesel\b'],
        'Propane': [r'\bpropane\b'],
        'Ammonia': [r'\bammonia\b']
    },
    'sector': {
        'Residential': [r'\bresidential\b'],
        'Commercial': [r'\bcommercial\b'],
        'Industrial': [r'\bindustrial\b'],
        'Transportation': [r'\btransportation\b', r'\btransit\b'],
        'Agriculture': [r'\bagriculture\b', r'\bagricultural\b'],
        'Utility/Grid': [r'\butility\b', r'\butilities\b', r'\bgrid\b'],
        'Government/Municipal': [r'\bgovernment\b', r'\bmunicipal\b', r'\bmunicipality\b'],
        'Education': [r'\beducation\b', r'\bschool\b', r'\bschools\b', r'\buniversity\b', r'\buniversities\b'],
        'Healthcare': [r'\bhealthcare\b', r'\bhospital\b', r'\bhospitals\b'],
        'Military/Defense': [r'\bmilitary\b', r'\bdefense\b'],
        'Data Centers': [r'\bdata center\b', r'\bdata centers\b'],
        'Maritime/Ports': [r'\bmaritime\b', r'\bport\b', r'\bports\b'],
        'Aviation': [r'\baviation\b', r'\baerospace\b', r'\baircraft\b', r'\bairlines\b'],
        'Mining': [r'\bmining\b', r'\bmine\b', r'\bmines\b']
    }
}

# Pre-compile regexes for performance
COMPILED_PATTERNS = {}
for category_type, values in CATEGORY_MAP.items():
    COMPILED_PATTERNS[category_type] = {}
    for value_name, patterns in values.items():
        COMPILED_PATTERNS[category_type][value_name] = [
            re.compile(p, re.IGNORECASE) for p in patterns
        ]

def infer_categories_from_text(text_to_search: str) -> list[dict]:
    """Infer categories from a string using keyword pattern matching."""
    inferred = []
    if not text_to_search or not text_to_search.strip():
        return inferred

    for category_type, value_dict in COMPILED_PATTERNS.items():
        for value_name, patterns in value_dict.items():
            for pattern in patterns:
                if pattern.search(text_to_search):
                    inferred.append({"type": category_type, "value": value_name})
                    break
    return inferred


def backfill_all_categories(db: Session) -> Dict[str, Any]:
    """
    Scans all opportunities and adds inferred categories based on text keywords.
    """
    stats = {
        "opportunities_processed": 0,
        "categories_added": 0,
        "already_tagged": 0
    }
    
    opportunities = db.query(Opportunity).all()
    stats["opportunities_processed"] = len(opportunities)
    
    for opp in opportunities:
        text_to_search = f"{opp.name or ''} {opp.short_description or ''}"
        
        if not text_to_search.strip():
            continue
            
        # Get existing categories for this opp to avoid duplicates
        existing_categories = db.query(OpportunityCategory).filter(
            OpportunityCategory.opportunity_id == opp.id
        ).all()
        
        existing_tags = {(c.category_type, c.category_value) for c in existing_categories}
        
        added_for_opp = False
        
        for category_type, value_dict in COMPILED_PATTERNS.items():
            for value_name, patterns in value_dict.items():
                # Check if it already has this tag
                if (category_type, value_name) in existing_tags:
                    stats["already_tagged"] += 1
                    continue
                    
                # Search for match
                matched = False
                for pattern in patterns:
                    if pattern.search(text_to_search):
                        matched = True
                        break
                        
                if matched:
                    new_category = OpportunityCategory(
                        opportunity_id=opp.id,
                        category_type=category_type,
                        category_value=value_name,
                        source="inferred_keyword_backfill",
                        confidence=0.8
                    )
                    db.add(new_category)
                    stats["categories_added"] += 1
                    added_for_opp = True
                    
        if added_for_opp:
            db.commit()
            
    return stats
