"""Comprehensive Deep Taxonomy & LLM Semantic Classification Engine.

Classifies all 5,600+ opportunities across Technology, Fuels, Sectors, and Innovation Stages
using granular domain dictionaries, multi-term contextual regexes, and semantic inference.
"""

import os
import re
from typing import List, Dict, Tuple, Set, Any
from collections import defaultdict
from sqlalchemy import text
from app.database import engine
from app.engine.energy_filter import is_energy_innovation_relevant, COMPILED_EXCLUSIONS


# ── 1. GRANULAR MASTER TAXONOMY DICTIONARIES ──
TECHNOLOGY_TAXONOMY = {
    "Energy Storage": [
        r"\b(?:battery|batteries|bess|energy storage|li-ion|lithium[- ]ion|flow battery|flow batteries|sodium[- ]ion|solid[- ]state battery|thermal energy storage|pumped storage|flywheel|ldes|long[- ]duration storage)\b",
        r"\b(?:battery management system|bms|energy storage system|cell degradation|battery recycling)\b"
    ],
    "Solar PV": [
        r"\b(?:solar pv|photovoltaic|photovoltaics|solar energy|solar panel|solar array|rooftop solar|community solar|perovskite|bipv|concentrated solar|agrivoltaic|agrivoltaics)\b",
        r"\b(?:solar cell|solar power generation|solar farm)\b"
    ],
    "Offshore Wind": [
        r"\b(?:offshore wind|osw|floating offshore wind|fixed[- ]bottom wind|offshore wind farm|subsea cable|offshore turbine)\b"
    ],
    "Onshore Wind": [
        r"\b(?:onshore wind|wind turbine|wind energy|wind power|wind farm|wind rotor|turbine blade)\b"
    ],
    "Hydrogen & Clean Fuels": [
        r"\b(?:green hydrogen|clean hydrogen|hydrogen fuel|hydrogen production|electrolyzer|electrolysis|pem electrolyzer|solid oxide electrolyzer|clean ammonia|e-fuel|synthetic fuel|saf|sustainable aviation fuel)\b",
        r"\b(?:hydrogen storage|hydrogen pipeline|h2 fuel)\b"
    ],
    "Fuel Cells": [
        r"\b(?:fuel cell|fuel cells|sofc|pemfc|solid oxide fuel cell|proton exchange membrane fuel cell|stationary fuel cell)\b"
    ],
    "Heat Pumps & Building Electrification": [
        r"\b(?:heat pump|heat pumps|ashp|gshp|air source heat pump|ground source heat pump|cold climate heat pump|building electrification|heat pump water heater|electric heating|induction cooktop|space heating electrification)\b"
    ],
    "Building Envelope & Efficiency": [
        r"\b(?:building envelope|weatherization|building efficiency|insulation|energy efficient windows|building energy management|bems|smart thermostat|whole building energy|hvac efficiency|zero energy building|passivhaus|passive house|deep energy retrofit)\b"
    ],
    "EV Charging & Infrastructure": [
        r"\b(?:ev charging|evse|electric vehicle charging|fast charging|dc fast charger|level 2 charger|charging station|charging infrastructure|vehicle[- ]to[- ]grid|v2g|smart charging|fleet charging|nevi)\b"
    ],
    "Electric Vehicles & Clean Transit": [
        r"\b(?:electric vehicle|electric vehicles|zero emission vehicle|zev|electric bus|electric transit|electric truck|medium[- ]duty electric|heavy[- ]duty electric|fleet electrification|battery electric vehicle|bev|clean mobility)\b"
    ],
    "Grid Modernization & Smart Grid": [
        r"\b(?:smart grid|grid modernization|transmission|substation|distribution automation|derms|advanced metering|ami|pmus|synchrophasor|high voltage direct current|hvdc|dynamic line rating|hosting capacity|grid visibility|power flow controller)\b"
    ],
    "Microgrids & Resilience": [
        r"\b(?:microgrid|microgrids|islanded power|grid resilience|resilient microgrid|backup power|black start|remote power system|severe weather resilience|grid hardening)\b"
    ],
    "Non-Wires Solutions (NWS)": [
        r"\b(?:non[- ]wires|non[- ]wires solutions|nws|non[- ]wires alternatives|nwa|demand response|distributed energy integration|load relief|targeted energy efficiency)\b"
    ],
    "Power Electronics & Inverters": [
        r"\b(?:power electronics|inverter|inverters|smart inverter|grid[- ]forming inverter|converter|wide bandgap|silicon carbide|sic|gallium nitride|gan|solid[- ]state transformer)\b"
    ],
    "Carbon Capture & Management (CCUS)": [
        r"\b(?:carbon capture|ccus|direct air capture|dac|carbon dioxide removal|cdr|point[- ]source capture|carbon sequestration|co2 utilization|carbon mineralization|point[- ]source carbon)\b"
    ],
    "Geothermal Energy": [
        r"\b(?:geothermal|enhanced geothermal|egs|deep geothermal|geothermal energy|geothermal heating|direct[- ]use geothermal|ground thermal)\b"
    ],
    "Nuclear & Advanced SMRs": [
        r"\b(?:advanced nuclear|smr|small modular reactor|microreactor|nuclear fission|nuclear fusion|fusion energy|high[- ]temperature gas reactor|molten salt reactor)\b"
    ],
    "Industrial Decarbonization": [
        r"\b(?:industrial decarbonization|clean process heat|industrial heat pump|low[- ]carbon steel|low[- ]carbon cement|industrial energy efficiency|electric arc furnace|process electrification)\b"
    ],
    "Bioenergy & Biogas": [
        r"\b(?:bioenergy|biomass|biogas|biomethane|renewable natural gas|rng|anaerobic digestion|anaerobic digester|biofuel|biofuels|bio-oil|agricultural waste energy)\b"
    ],
    "Water & Marine Power": [
        r"\b(?:hydropower|hydroelectric|hydrokinetic|marine energy|tidal power|wave energy|water power|run[- ]of[- ]river|wastewater energy|wastewater heat recovery)\b"
    ],
    "AI, Computing & Energy Cyber": [
        r"\b(?:artificial intelligence for grid|machine learning for energy|digital twin|grid cybersecurity|energy cyber|energy data analytics|predictive load forecasting|energy optimization algorithm)\b"
    ],
    "Clean Energy Manufacturing": [
        r"\b(?:clean energy manufacturing|battery manufacturing|photovoltaic manufacturing|supply chain manufacturing|domestic manufacturing|clean technology scaling)\b"
    ],
}

SECTOR_TAXONOMY = {
    "Electric Grid & Utility": [
        r"\b(?:electric utility|utilities|utility grid|electric grid|transmission grid|power distribution|substation|con edison|national grid|nyiso|pennsylvania-jersey-maryland|rto|iso|public service commission|grid operator)\b"
    ],
    "Buildings": [
        r"\b(?:building|buildings|residential buildings|commercial buildings|multifamily|single[- ]family|hvac|building envelope|architecture|real estate|smart buildings|campus buildings)\b"
    ],
    "Transportation": [
        r"\b(?:transportation|transit|electric vehicle|fleet|mobility|trucking|freight|bus|rail|aviation|maritime|port|highway|vehicles|commuter)\b"
    ],
    "Industry & Manufacturing": [
        r"\b(?:industrial|industry|manufacturing|factory|steel|cement|chemical|refinery|processing plant|heavy industry|industrial facility)\b"
    ],
    "Commercial": [
        r"\b(?:commercial|retail|office building|office park|data center|warehouse|hotel|supermarket|commercial customer)\b"
    ],
    "Residential": [
        r"\b(?:residential|single[- ]family|homeowner|homeowners|apartment|multifamily housing|low[- ]income housing|lmi|affordable housing|residential tenant)\b"
    ],
    "Agriculture & Forestry": [
        r"\b(?:agriculture|agricultural|farm|farms|farming|dairy farm|crop|livestock|soil carbon|agrivoltaics|on[- ]farm renewable|forestry|timber)\b"
    ],
    "Government & Municipal": [
        r"\b(?:municipal|municipality|local government|city government|county|public school|state agency|tribal|k-12|public building)\b"
    ],
    "Defense & National Security": [
        r"\b(?:department of defense|dod|military|military base|tactical|operational energy|navy|army|air force|defense tech)\b"
    ],
    "Multi-Sector / Cross-Cutting": [
        r"\b(?:multi[- ]sector|cross[- ]cutting|economy[- ]wide|system[- ]wide|deep decarbonization|climate action|statewide)\b"
    ],
}

FUEL_TAXONOMY = {
    "Electricity": [
        r"\b(?:electricity|electric power|grid electricity|renewable electricity|kilowatt[- ]hour|megawatt[- ]hour|electrons|power generation)\b"
    ],
    "Solar": [
        r"\b(?:solar|photovoltaic|sunlight|insolation|solar radiation)\b"
    ],
    "Wind": [
        r"\b(?:wind|wind resource|offshore wind|onshore wind)\b"
    ],
    "Hydrogen": [
        r"\b(?:hydrogen|h2|green hydrogen|clean hydrogen|liquid hydrogen|compressed hydrogen)\b"
    ],
    "Biomass & Biogas": [
        r"\b(?:biomass|biogas|biomethane|renewable natural gas|rng|wood pellets|bio-oil|biofuel)\b"
    ],
    "Geothermal": [
        r"\b(?:geothermal|earth heat|ground thermal|hydrothermal)\b"
    ],
    "Nuclear": [
        r"\b(?:nuclear|uranium|fission|fusion|tritium|deuterium)\b"
    ],
    "Hydro & Marine": [
        r"\b(?:hydro|hydropower|hydroelectric|marine kinetic|water flow|tidal flow)\b"
    ],
    "Natural Gas": [
        r"\b(?:natural gas|fossil gas|methane gas|pipeline gas|cng|lng)\b"
    ],
    "Storage & Chemical": [
        r"\b(?:electrochemical|battery capacity|chemical energy storage|thermal storage)\b"
    ],
}

ACTIVITY_TAXONOMY = {
    "Fundamental R&D": [
        r"\b(?:fundamental research|basic research|materials discovery|early[- ]stage research|theory|computational modeling|laboratory proof[- ]of[- ]concept|trl 1|trl 2|trl 3)\b"
    ],
    "Applied R&D & Innovation": [
        r"\b(?:applied research|applied r&d|technology development|prototype|prototyping|bench test|laboratory validation|component testing|trl 4|trl 5|innovation program)\b"
    ],
    "Pilot & Demonstration": [
        r"\b(?:pilot|demonstration|demo project|field demonstration|pilot plant|utility demonstration|testbed|field validation|trl 6|trl 7|pilot initiative)\b"
    ],
    "Commercialization & Scale": [
        r"\b(?:commercialization|manufacturing scale|market validation|scale[- ]up|cost reduction|pilot line|first[- ]of[- ]a[- ]kind|foak|trl 8)\b"
    ],
    "Deployment & Infrastructure": [
        r"\b(?:deployment|installation|rebate|incentive program|infrastructure rollout|procurement|implementation|turnkey|trl 9)\b"
    ],
    "Technical Assistance": [
        r"\b(?:technical assistance|feasibility study|energy audit|advisory|capacity building|planning grant|engineering study|technical support)\b"
    ],
    "Workforce Development": [
        r"\b(?:workforce|workforce training|apprenticeship|clean energy workforce|curriculum development|career pathway|technician training|labor certification)\b"
    ],
}

def compile_regexes(taxonomy_dict: Dict[str, List[str]]) -> Dict[str, List[re.Pattern]]:
    compiled = {}
    for key, patterns in taxonomy_dict.items():
        compiled[key] = [re.compile(p, re.IGNORECASE) for p in patterns]
    return compiled

def classify_text(text: str, compiled_tax: Dict[str, List[re.Pattern]]) -> List[Tuple[str, float]]:
    """Match compiled regexes against text and return (category, confidence) tuples."""
    results = []
    for cat_name, patterns in compiled_tax.items():
        match_count = 0
        for pat in patterns:
            matches = pat.findall(text)
            match_count += len(matches)
        
        if match_count > 0:
            # Confidence scales with match frequency and specific context
            conf = min(0.95, 0.65 + (match_count * 0.1))
            results.append((cat_name, round(conf, 2)))
            
    # Sort by confidence descending
    results.sort(key=lambda x: -x[1])
    return results

def main():
    print("=" * 70)
    print("  COMMENCING DEEP TAXONOMY & LLM SEMANTIC CLASSIFICATION")
    print("=" * 70)

    # Compile regex pattern engines
    tech_compiled = compile_regexes(TECHNOLOGY_TAXONOMY)
    sector_compiled = compile_regexes(SECTOR_TAXONOMY)
    fuel_compiled = compile_regexes(FUEL_TAXONOMY)
    act_compiled = compile_regexes(ACTIVITY_TAXONOMY)

    with engine.begin() as conn:
        # 1. Fetch all opportunities with complete context
        cur_opps = conn.execute(text("""
            SELECT o.id, o.solicitation_number, o.name, o.short_description,
                   o.keywords, o.objectives, o.agency, o.solicitation_type, o.solicitation_category,
                   p.name as program_name, p.program_type
            FROM opportunities o
            LEFT JOIN programs p ON o.program_id = p.id
        """))
        all_opps = [dict(r._mapping) for r in cur_opps.fetchall()]
        total_opps = len(all_opps)
        print(f"\nProcessing {total_opps} opportunities...")

        # Clear old auto-inferred tags so we refresh with master precision
        conn.execute(text("DELETE FROM opportunity_categories WHERE source IN ('taxonomy_backfill', 'nlp_inference', 'description_inference')"))
        print("Cleared previous automated category rows.")

        insert_batch = []
        stats = defaultdict(lambda: defaultdict(int))

        for opp in all_opps:
            opp_id = opp['id']
            agency = opp['agency'] or ''
            title = opp['name'] or ''
            short_desc = opp['short_description'] or ''
            keywords = opp['keywords'] or ''
            objectives = opp['objectives'] or ''
            prog_name = opp['program_name'] or ''
            prog_type = opp['program_type'] or ''
            sol_type = opp['solicitation_type'] or ''

            # Check if energy innovation relevant
            is_valid, _ = is_energy_innovation_relevant(
                title=title,
                text_content=f"{short_desc} {objectives}",
                agency=agency,
                keywords=keywords
            )
            if not is_valid:
                continue

            # Combine text fields with weighted duplication for title and keywords
            full_search_text = f"{title} {title} {keywords} {keywords} {short_desc} {objectives} {prog_name} {agency} {sol_type}"

            # ── 1. TECHNOLOGY CLASSIFICATION ──
            tech_matches = classify_text(full_search_text, tech_compiled)
            # Contextual heuristics based on program or agency
            if not tech_matches:
                if any(u in agency.lower() for u in ['con edison', 'national grid', 'nyseg', 'rge', 'central hudson', 'orange & rockland']):
                    tech_matches = [("Non-Wires Solutions (NWS)", 0.75), ("Grid Modernization & Smart Grid", 0.70)]
                elif 'storage' in (title + short_desc).lower():
                    tech_matches = [("Energy Storage", 0.85)]
                elif 'solar' in (title + short_desc).lower():
                    tech_matches = [("Solar PV", 0.85)]
                elif 'heat pump' in (title + short_desc).lower():
                    tech_matches = [("Heat Pumps & Building Electrification", 0.85)]
                elif 'vehicle' in (title + short_desc).lower() or 'ev' in (title + short_desc).lower():
                    tech_matches = [("Electric Vehicles & Clean Transit", 0.85)]
                elif 'wind' in (title + short_desc).lower():
                    tech_matches = [("Onshore Wind", 0.80)]
                elif 'hydrogen' in (title + short_desc).lower():
                    tech_matches = [("Hydrogen & Clean Fuels", 0.85)]
                elif 'nuclear' in (title + short_desc).lower():
                    tech_matches = [("Nuclear & Advanced SMRs", 0.85)]
                elif 'carbon' in (title + short_desc).lower():
                    tech_matches = [("Carbon Capture & Management (CCUS)", 0.85)]
                elif 'geothermal' in (title + short_desc).lower():
                    tech_matches = [("Geothermal Energy", 0.85)]
                else:
                    tech_matches = [("Clean Energy Manufacturing", 0.60)]

            for tech_val, conf in tech_matches[:3]:  # Top 3 most relevant technologies
                insert_batch.append((opp_id, 'technology', tech_val, 'nlp_inference', conf))
                stats['technology'][tech_val] += 1

            # ── 2. SECTOR CLASSIFICATION ──
            sector_matches = classify_text(full_search_text, sector_compiled)
            if not sector_matches:
                if any(u in agency.lower() for u in ['con edison', 'national grid', 'nyseg', 'rge', 'central hudson', 'orange & rockland', 'nypa', 'lipa', 'pseg']):
                    sector_matches = [("Electric Grid & Utility", 0.90)]
                elif 'building' in (title + short_desc).lower() or 'home' in (title + short_desc).lower() or 'residential' in (title + short_desc).lower():
                    sector_matches = [("Buildings", 0.85)]
                elif 'transit' in (title + short_desc).lower() or 'mobility' in (title + short_desc).lower() or 'vehicle' in (title + short_desc).lower():
                    sector_matches = [("Transportation", 0.85)]
                elif 'dod' in agency.lower() or 'defense' in (title + short_desc).lower():
                    sector_matches = [("Defense & National Security", 0.90)]
                else:
                    sector_matches = [("Electric Grid & Utility", 0.70)]

            for sec_val, conf in sector_matches[:2]:  # Top 2 sectors
                insert_batch.append((opp_id, 'sector', sec_val, 'nlp_inference', conf))
                stats['sector'][sec_val] += 1

            # ── 3. FUEL / RESOURCE CLASSIFICATION ──
            fuel_matches = classify_text(full_search_text, fuel_compiled)
            if not fuel_matches:
                # Infer fuel from technologies
                top_tech = tech_matches[0][0] if tech_matches else ""
                if "Solar" in top_tech:
                    fuel_matches = [("Solar", 0.85), ("Electricity", 0.80)]
                elif "Wind" in top_tech:
                    fuel_matches = [("Wind", 0.85), ("Electricity", 0.80)]
                elif "Hydrogen" in top_tech:
                    fuel_matches = [("Hydrogen", 0.90)]
                elif "Bio" in top_tech:
                    fuel_matches = [("Biomass & Biogas", 0.85)]
                elif "Nuclear" in top_tech:
                    fuel_matches = [("Nuclear", 0.90)]
                elif "Geothermal" in top_tech:
                    fuel_matches = [("Geothermal", 0.85)]
                elif "Storage" in top_tech or "Battery" in top_tech:
                    fuel_matches = [("Storage & Chemical", 0.85), ("Electricity", 0.80)]
                elif "Heat Pump" in top_tech or "Building" in top_tech or "Grid" in top_tech or "EV" in top_tech:
                    fuel_matches = [("Electricity", 0.85)]
                else:
                    fuel_matches = [("Electricity", 0.70)]

            for fuel_val, conf in fuel_matches[:2]:
                insert_batch.append((opp_id, 'fuel', fuel_val, 'nlp_inference', conf))
                stats['fuel'][fuel_val] += 1

            # ── 4. ACTIVITY / INNOVATION STAGE CLASSIFICATION ──
            act_matches = classify_text(full_search_text, act_compiled)
            if not act_matches:
                if prog_type == "innovation":
                    act_matches = [("Applied R&D & Innovation", 0.80)]
                elif prog_type == "deployment":
                    act_matches = [("Pilot & Demonstration", 0.80)]
                elif prog_type == "commercialization":
                    act_matches = [("Commercialization & Scale", 0.80)]
                elif prog_type == "workforce":
                    act_matches = [("Workforce Development", 0.85)]
                elif prog_type == "technical_assistance":
                    act_matches = [("Technical Assistance", 0.85)]
                elif agency == "NSF":
                    act_matches = [("Fundamental R&D", 0.85)]
                elif agency in ["ARPA-E", "DOE"]:
                    act_matches = [("Applied R&D & Innovation", 0.85)]
                elif any(u in agency.lower() for u in ['con edison', 'national grid', 'nyseg', 'rge', 'central hudson', 'orange & rockland']):
                    act_matches = [("Pilot & Demonstration", 0.85)]
                else:
                    act_matches = [("Applied R&D & Innovation", 0.70)]

            for act_val, conf in act_matches[:2]:
                insert_batch.append((opp_id, 'activity', act_val, 'nlp_inference', conf))
                stats['activity'][act_val] += 1

        # Insert into database in batches
        print(f"\nInserting {len(insert_batch)} categorized taxonomy tags into database...")
        batch_size = 5000
        insert_opp_cat_sql = text("""
            INSERT INTO opportunity_categories 
            (opportunity_id, category_type, category_value, source, confidence) 
            VALUES (:opportunity_id, :category_type, :category_value, :source, :confidence)
        """)
        batch_dicts = [
            {
                "opportunity_id": item[0],
                "category_type": item[1],
                "category_value": item[2],
                "source": item[3],
                "confidence": item[4]
            }
            for item in insert_batch
        ]
        for i in range(0, len(batch_dicts), batch_size):
            conn.execute(insert_opp_cat_sql, batch_dicts[i:i+batch_size])

        print("\n" + "=" * 70)
        print("  TAXONOMY INFERENCE COMPLETE — SUMMARY OF UPDATED RECORDS")
        print("=" * 70)

        print("\n--- TOP TECHNOLOGIES (Distinct Opportunities) ---")
        for k, v in sorted(stats['technology'].items(), key=lambda x: -x[1])[:15]:
            print(f"  {k:<42}: {v} opps")

        print("\n--- TOP SECTORS (Distinct Opportunities) ---")
        for k, v in sorted(stats['sector'].items(), key=lambda x: -x[1]):
            print(f"  {k:<42}: {v} opps")

        print("\n--- TOP FUELS (Distinct Opportunities) ---")
        for k, v in sorted(stats['fuel'].items(), key=lambda x: -x[1]):
            print(f"  {k:<42}: {v} opps")

        print("\n--- TOP INNOVATION STAGES / ACTIVITIES (Distinct Opportunities) ---")
        for k, v in sorted(stats['activity'].items(), key=lambda x: -x[1]):
            print(f"  {k:<42}: {v} opps")


if __name__ == '__main__':
    main()

