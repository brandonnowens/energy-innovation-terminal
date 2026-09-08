import re
from sqlalchemy import text
from app.database import engine
from app.engine.energy_filter import is_energy_innovation_relevant

def main():
    print("=== Master Taxonomies & Accurate Sector/Tech Tagging ===")
    
    # Taxonomies definitions
    taxonomies = [
        # Technologies
        ('technology', 'Solar', 'Photovoltaic, Solar Power, Solar Energy, Rooftop Solar', 1),
        ('technology', 'Wind', 'Wind Power, Wind Energy, Wind Turbine', 2),
        ('technology', 'Offshore Wind', 'OSW, Offshore Wind Farm', 3),
        ('technology', 'Energy Storage', 'Battery, Energy Storage System, BESS, Battery Storage', 4),
        ('technology', 'Hydrogen', 'Green Hydrogen, Clean Hydrogen, Hydrogen Fuel, Electrolyzer', 5),
        ('technology', 'Fuel Cells', 'Fuel Cell, Solid Oxide', 6),
        ('technology', 'Geothermal', 'Ground Source, Geothermal Energy, Geothermal Heat Pump', 7),
        ('technology', 'Nuclear', 'SMR, Advanced Nuclear, Nuclear Reactor, Fission, Fusion', 8),
        ('technology', 'Grid Modernization', 'Smart Grid, Power Grid, Transmission Line, Grid Modernization', 9),
        ('technology', 'Carbon Management', 'CCUS, Carbon Capture, Direct Air Capture, Carbon Sequestration', 10),
        ('technology', 'Clean Transportation', 'Electric Vehicle, Zero Emission Vehicle, EV Fleet, Clean Transit', 11),
        ('technology', 'Building Electrification', 'Building Electrification, Heat Pump, Whole Building Energy', 12),
        ('technology', 'Industrial Decarbonization', 'Industrial Decarbonization, Clean Process Heat, Low Carbon Industrial', 13),
        ('technology', 'Bioenergy/Biomass', 'Biofuel, Biogas, Renewable Natural Gas, Sustainable Aviation Fuel', 14),
        ('technology', 'Water/Wastewater', 'Wastewater Energy, Water Treatment Energy, Desalination', 15),
        ('technology', 'Environmental Monitoring', 'Emissions Monitoring, GHG Sensors, Methane Detection', 16),
        ('technology', 'Cybersecurity', 'Grid Cybersecurity, Energy Cyber, Industrial Control Systems Security', 17),
        ('technology', 'AI/ML', 'Artificial Intelligence for Energy, Machine Learning for Grid', 18),
        ('technology', 'Resilience', 'Grid Resilience, Climate Resilient Power, Severe Weather Hardening', 19),
        ('technology', 'Microgrids', 'Microgrid, Islanded Power, Distributed Microgrid', 20),
        ('technology', 'EV Charging', 'EV Charging Station, Fast Charging, EVSE, Vehicle to Grid', 21),
        ('technology', 'Heat Pumps', 'Air Source Heat Pump, Ground Source Heat Pump, Cold Climate Heat Pump', 22),
        ('technology', 'Weatherization', 'Building Envelope, Building Insulation, Weatherization Assistance', 23),
        ('technology', 'Advanced Manufacturing', 'Clean Energy Manufacturing, Battery Manufacturing, Photovoltaic Manufacturing', 24),
        ('technology', 'Other', '', 25),

        # Sectors
        ('sector', 'Buildings', 'Residential Buildings, Commercial Buildings, Multifamily, Building Efficiency, Architecture', 1),
        ('sector', 'Transportation', 'Transit, Freight, Heavy Duty Vehicles, Passenger Vehicles, Rail', 2),
        ('sector', 'Industry', 'Industrial Manufacturing, Steel, Cement, Chemicals, Manufacturing Facilities', 3),
        ('sector', 'Electric Grid', 'Electric Utility, Power Distribution, Transmission Grid, ISO, RTO', 4),
        ('sector', 'Agriculture', 'Farming, Agricultural, Agrivoltaics, Dairy Farm, Livestock Energy, On-Farm Renewable', 5),
        ('sector', 'Water', 'Wastewater Treatment, Municipal Water, Water Infrastructure', 6),
        ('sector', 'Multi-Sector', 'Cross-Cutting Energy, System-Wide Decarbonization', 7),
        ('sector', 'Commercial', 'Commercial Buildings, Retail Energy, Office Buildings', 8),
        ('sector', 'Residential', 'Single Family Homes, Residential Solar, Home Energy', 9),
        ('sector', 'Government/Municipal', 'Municipal Government, State Facilities, Public Buildings', 10),
        ('sector', 'Military/Defense', 'Department of Defense, Military Base, Tactical Energy', 11),
        ('sector', 'Other', '', 12),

        # Fuels
        ('fuel', 'Electricity', 'Electric Power, Renewable Electricity, Grid Electricity', 1),
        ('fuel', 'Natural Gas', 'Fossil Gas, Methane Gas, Pipeline Gas', 2),
        ('fuel', 'Hydrogen', 'Clean Hydrogen, Hydrogen Gas, H2 Fuel', 3),
        ('fuel', 'Solar Thermal', 'Solar Hot Water, Concentrated Solar Thermal', 4),
        ('fuel', 'Geothermal', 'Geothermal Fluid, Ground Source Heat', 5),
        ('fuel', 'Biomass/Biogas', 'Biomethane, Renewable Natural Gas, Wood Pellets, Bio-oil', 6),
        ('fuel', 'Diesel/Petroleum', 'Petroleum Fuel, Diesel Generator, Jet Fuel', 7),
        ('fuel', 'Nuclear Fuel', 'Uranium, Thorium, SMR Fuel', 8),
        ('fuel', 'Coal', 'Coal Combustion, Coal Derived Fuel', 9),
        ('fuel', 'Other', '', 10)
    ]

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM taxonomies"))
        insert_tax_sql = text("""
            INSERT INTO taxonomies (category_type, canonical_value, aliases, sort_order)
            VALUES (:category_type, :canonical_value, :aliases, :sort_order)
        """)
        tax_dicts = [
            {"category_type": t[0], "canonical_value": t[1], "aliases": t[2], "sort_order": t[3]}
            for t in taxonomies
        ]
        conn.execute(insert_tax_sql, tax_dicts)

        # Clear old taxonomy backfill entries
        conn.execute(text("DELETE FROM opportunity_categories WHERE source='taxonomy_backfill'"))
        print("Cleared previous taxonomy_backfill category entries.")

        # Build in-memory existing category lookup
        existing_rows = conn.execute(text("SELECT DISTINCT opportunity_id, category_type FROM opportunity_categories")).fetchall()
        existing_cat_map = {(r[0], r[1]) for r in existing_rows}

        # Compile patterns
        tax_map = {'technology': [], 'sector': [], 'fuel': []}
        for cat_type, canonical, aliases_str, _ in taxonomies:
            aliases = [a.strip() for a in aliases_str.split(',')] if aliases_str else []
            aliases.append(canonical)
            patterns = []
            for a in aliases:
                if not a: continue
                pat = re.compile(r'\b' + re.escape(a) + r'\b', re.IGNORECASE)
                patterns.append((a, pat))

            tax_map[cat_type].append({
                'canonical': canonical,
                'patterns': patterns
            })

        # Fetch all opportunities
        opportunities = conn.execute(text("SELECT id, name, keywords, short_description, objectives, agency FROM opportunities")).fetchall()

        insert_batch = []

        for opp in opportunities:
            opp_id = opp[0]
            name_val = opp[1] or ""
            kw_val = opp[2] or ""
            desc_val = opp[3] or ""
            obj_val = opp[4] or ""
            agency_val = opp[5] or ""
            
            is_valid, _ = is_energy_innovation_relevant(
                title=name_val,
                text_content=f"{desc_val} {obj_val}",
                agency=agency_val,
                keywords=kw_val
            )
            if not is_valid:
                continue

            text_to_search = ' '.join(filter(None, [name_val, kw_val, desc_val, obj_val]))

            for cat_type in ['technology', 'sector', 'fuel']:
                matched_categories = []
                for tax_entry in tax_map[cat_type]:
                    canonical = tax_entry['canonical']
                    if canonical in ['Other', 'Unknown']:
                        continue

                    best_conf = 0.0
                    for alias_text, pat in tax_entry['patterns']:
                        if pat.search(text_to_search):
                            conf = 0.85 if alias_text.lower() == canonical.lower() else 0.70
                            if conf > best_conf:
                                best_conf = conf

                    if best_conf > 0:
                        matched_categories.append((canonical, best_conf))

                # Check if this category type is already covered for this opportunity
                if (opp_id, cat_type) not in existing_cat_map:
                    if matched_categories:
                        for canonical, conf in matched_categories:
                            insert_batch.append({
                                "opp_id": opp_id, "cat_type": cat_type, 
                                "cat_val": canonical, "src": 'taxonomy_backfill', "conf": conf
                            })
                    else:
                        insert_batch.append({
                            "opp_id": opp_id, "cat_type": cat_type, 
                            "cat_val": 'Other', "src": 'taxonomy_backfill', "conf": 0.3
                        })

        if insert_batch:
            insert_opp_cat_sql = text("""
                INSERT INTO opportunity_categories 
                (opportunity_id, category_type, category_value, source, confidence) 
                VALUES (:opp_id, :cat_type, :cat_val, :src, :conf)
            """)
            batch_size = 2000
            for i in range(0, len(insert_batch), batch_size):
                conn.execute(insert_opp_cat_sql, insert_batch[i:i + batch_size])

        print(f"Successfully inserted {len(insert_batch)} accurate taxonomy category entries.")

        distribution = conn.execute(text("""
            SELECT category_value, COUNT(DISTINCT opportunity_id) 
            FROM opportunity_categories 
            WHERE category_type='sector' 
            GROUP BY category_value 
            ORDER BY COUNT(DISTINCT opportunity_id) DESC
        """)).fetchall()
        print("\nCleaned Sector Category Distribution:")
        for r in distribution:
            print(f"  Sector '{r[0]}': {r[1]} opps")

if __name__ == '__main__':
    main()
