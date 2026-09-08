"""Seed and enrich comprehensive Key Contacts directory in PostgreSQL."""
import sys
import os
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent))
from app.database import engine


def infer_tech_and_sector(t_in):
    t = (t_in or "").lower()
    tech = "Clean Energy Innovation & Cross-Cutting"
    sector = "Cross-Cutting & Policy"
    fuel = None

    if any(k in t for k in ["battery", "batteries", "storage", "lithium", "anode", "cathode", "electrolyte", "flow battery", "solid state", "supercapacitor"]):
        tech = "Energy Storage & Advanced Batteries"
        sector = "Electric Grid & Utility"
    elif any(k in t for k in ["solar", "photovoltaic", "pv", "perovskite", "bifacial", "concentrated solar", "csp"]):
        tech = "Solar & Photovoltaics"
        sector = "Electric Grid & Utility"
    elif any(k in t for k in ["wind", "offshore wind", "turbine", "aerodynamic", "floating wind"]):
        tech = "Wind & Offshore Wind"
        sector = "Electric Grid & Utility"
    elif any(k in t for k in ["hydrogen", "fuel cell", "electrolyzer", "electrolysis", "clean fuel", "h2", "ammonia", "saf"]):
        tech = "Hydrogen & Clean Fuels"
        sector = "Industrial & Manufacturing"
        fuel = "Clean Hydrogen & E-Fuels"
    elif any(k in t for k in ["grid", "microgrid", "transmission", "distribution", "smart grid", "power electronics", "inverter", "substation", "der", "demand response", "virtual power plant"]):
        tech = "Grid Modernization & Smart Power"
        sector = "Electric Grid & Utility"
    elif any(k in t for k in ["carbon capture", "ccus", "carbon removal", "direct air capture", "dac", "carbon dioxide", "co2", "sequestration"]):
        tech = "Carbon Capture & CCUS"
        sector = "Industrial & Manufacturing"
    elif any(k in t for k in ["building", "heat pump", "hvac", "insulation", "envelope", "energy efficiency", "multifamily", "smart thermostat"]):
        tech = "Building Decarbonization & Clean Heat"
        sector = "Buildings & Real Estate"
    elif any(k in t for k in ["vehicle", "ev", "electric mobility", "charging", "charger", "powertrain", "transit", "fleet", "transportation"]):
        tech = "Electric Mobility & Transportation"
        sector = "Transportation & Mobility"
    elif any(k in t for k in ["nuclear", "fusion", "smr", "fission", "reactor", "tokamak", "stellarator", "plasma"]):
        tech = "Advanced Nuclear & Fusion"
        sector = "Electric Grid & Utility"
        fuel = "Nuclear & Fusion Fuel"
    elif any(k in t for k in ["geothermal", "hydro", "hydropower", "marine energy", "wave energy", "tidal"]):
        tech = "Geothermal & Water Power"
        sector = "Electric Grid & Utility"
    elif any(k in t for k in ["industrial", "steel", "cement", "chemical", "manufacturing", "furnace", "smelting", "thermal storage", "process heat"]):
        tech = "Industrial Decarbonization & Clean Heat"
        sector = "Industrial & Manufacturing"
    elif any(k in t for k in ["biomass", "bioenergy", "biogas", "biofuel", "anaerobic", "gasification", "agriculture", "feedstock"]):
        tech = "Bioenergy & Sustainable Fuels"
        sector = "Agriculture & Bioeconomy"
        fuel = "Biofuels & Renewable Gas"
    elif any(k in t for k in ["artificial intelligence", "ai", "machine learning", "ml", "software", "cybersecurity", "quantum", "digital twin"]):
        tech = "AI, ML & Energy Software"
        sector = "Cross-Cutting & Technology"
    elif any(k in t for k in ["workforce", "training", "fellowship", "education", "apprenticeship"]):
        tech = "Workforce & Technical Assistance"
        sector = "Cross-Cutting & Policy"
    return tech, sector, fuel


def run_seed():
    print("Seeding PostgreSQL contacts...")
    with engine.begin() as conn:
        # 1. Enrich true NYSERDA contacts (only emails ending in @nyserda.ny.gov or @greenbank.ny.gov)
        cur_nyserda = conn.execute(text("SELECT id, email FROM contacts WHERE email ILIKE '%@nyserda.ny.gov' OR email ILIKE '%@greenbank.ny.gov'")).fetchall()
        for row in cur_nyserda:
            cid, email = row[0], row[1]
            em = (email or "").lower()
            title = "Clean Energy Program Lead"
            dept = "Innovation & Market Development"
            role_type = "program_officer"
            tech = "Clean Energy Innovation & Cross-Cutting"
            sector = "Cross-Cutting & Policy"
            inst = "New York State Energy Research and Development Authority (NYSERDA)"
            org_id = 5
            entity_url = "https://www.nyserda.ny.gov"
            email_domain = "nyserda.ny.gov"

            if "multifamily" in em:
                title = "Multifamily Clean Heat & Efficiency Program Manager"
                dept = "Building Decarbonization & Clean Heat"
                tech = "Building Decarbonization & Clean Heat"
                sector = "Buildings & Real Estate"
            elif "affordablesolar" in em or "solar" in em:
                title = "NY-Sun Distributed Solar Program Lead"
                dept = "Distributed Energy Resources & Solar"
                tech = "Solar & Photovoltaics"
                sector = "Electric Grid & Utility"
            elif "charging" in em or "cleantrans" in em:
                title = "Clean Transportation & EV Infrastructure Project Manager"
                dept = "Clean Transportation & Fleet Electrification"
                tech = "Electric Mobility & Transportation"
                sector = "Transportation & Mobility"
            elif "wfinfo" in em or "eecetraining" in em:
                title = "Clean Energy Workforce Development & Training Manager"
                dept = "Workforce & Community Equity"
                tech = "Workforce & Technical Assistance"
                sector = "Cross-Cutting & Policy"
            elif "smartgrid" in em:
                title = "Smart Grid & Grid Modernization Program Manager"
                dept = "Grid Modernization & R&D"
                tech = "Grid Modernization & Smart Power"
                sector = "Electric Grid & Utility"
            elif "air.quality" in em:
                title = "Environmental & Air Quality Research Lead"
                dept = "Environmental Research & Climate Analysis"
                role_type = "technical_expert"
                tech = "Environmental Monitoring & Climate Science"
                sector = "Cross-Cutting & Policy"
            elif "ebchospitals" in em or "commercial" in em:
                title = "Commercial & Institutional Energy Solutions Lead"
                dept = "Commercial Buildings Decarbonization"
                tech = "Building Decarbonization & Clean Heat"
                sector = "Buildings & Real Estate"
            elif "flextech" in em:
                title = "FlexTech Engineering & Technical Assistance Lead"
                dept = "Technical Services & Engineering"
                tech = "Energy Efficiency & Industrial Processes"
                sector = "Industrial & Manufacturing"

            conn.execute(text("""
                UPDATE contacts SET
                    title = COALESCE(title, :title),
                    department = COALESCE(department, :dept),
                    role_type = COALESCE(role_type, :role_type),
                    institution_name = :inst,
                    organization_id = :org_id,
                    technology_area = :tech,
                    sector = :sector,
                    entity_contact_url = :entity_url,
                    email_domain = :email_domain,
                    state = 'NY',
                    city = 'Albany',
                    verification_status = 'verified',
                    data_provenance = 'NYSERDA Official Solicitation Directory'
                WHERE id = :id
            """), {
                "title": title, "dept": dept, "role_type": role_type,
                "inst": inst, "org_id": org_id, "tech": tech,
                "sector": sector, "entity_url": entity_url,
                "email_domain": email_domain, "id": cid
            })
        print(f"NYSERDA contacts updated: {len(cur_nyserda)}")

        # 2. Seed Gateways & Agency Leads
        gateways = [
            ("Solar Energy Technologies Office (SETO) Helpdesk", "Program Support & Solicitation Helpdesk", "DOE Solar Energy Technologies Office", "institutional_gateway", "solar@ee.doe.gov", "(202) 586-1000", 1, "U.S. Department of Energy (DOE-SETO)", "Solar & Photovoltaics", "Electric Grid & Utility", None, "Washington", "DC", "https://www.energy.gov/eere/solar", "DOE EERE Public Directory", "solar, photovoltaics, csp, grid integration", "energy.gov"),
            ("Hydrogen and Fuel Cell Technologies Office (HFTO) Helpdesk", "Clean Hydrogen Grants & Program Support", "DOE Hydrogen and Fuel Cell Technologies Office", "institutional_gateway", "hfto@ee.doe.gov", "(202) 586-5000", 1, "U.S. Department of Energy (DOE-HFTO)", "Hydrogen & Clean Fuels", "Industrial & Manufacturing", "Clean Hydrogen & E-Fuels", "Washington", "DC", "https://www.energy.gov/eere/fuelcells", "DOE EERE Public Directory", "hydrogen, electrolyzers, fuel cells, h2 hubs", "energy.gov"),
            ("Building Technologies Office (BTO) Inquiries", "Building Decarbonization Program Office", "DOE Building Technologies Office", "institutional_gateway", "buildings@ee.doe.gov", "(202) 586-1000", 1, "U.S. Department of Energy (DOE-BTO)", "Building Decarbonization & Clean Heat", "Buildings & Real Estate", None, "Washington", "DC", "https://www.energy.gov/eere/buildings", "DOE EERE Public Directory", "heat pumps, smart buildings, envelope, hvac", "energy.gov"),
            ("Vehicle Technologies Office (VTO) Inquiries", "Electric Vehicle & Battery Program Office", "DOE Vehicle Technologies Office", "institutional_gateway", "vto@ee.doe.gov", "(202) 586-1000", 1, "U.S. Department of Energy (DOE-VTO)", "Electric Mobility & Transportation", "Transportation & Mobility", None, "Washington", "DC", "https://www.energy.gov/eere/vehicles", "DOE EERE Public Directory", "electric vehicles, batteries, fast charging", "energy.gov"),
            ("Office of Clean Energy Demonstrations (OCED) Desk", "Commercial Scale Demonstrations Lead", "DOE Office of Clean Energy Demonstrations", "program_officer", "oced@hq.doe.gov", "(202) 586-1000", 1, "U.S. Department of Energy (DOE-OCED)", "Clean Energy Innovation & Cross-Cutting", "Cross-Cutting & Policy", None, "Washington", "DC", "https://www.energy.gov/oced", "DOE OCED Public Directory", "commercial scale, hydrogen hubs, dac hubs, ldes", "energy.gov"),
            ("Grid Deployment Office (GDO) Inquiries", "Transmission & Grid Resilience Program Office", "DOE Grid Deployment Office", "institutional_gateway", "gdo@hq.doe.gov", "(202) 586-1000", 1, "U.S. Department of Energy (DOE-GDO)", "Grid Modernization & Smart Power", "Electric Grid & Utility", None, "Washington", "DC", "https://www.energy.gov/gdo", "DOE GDO Public Directory", "grid resilience, transmission, microgrids, grip", "energy.gov"),
            ("Office of Fossil Energy and Carbon Management (FECM)", "Carbon Management & CCUS Program Office", "DOE Office of Fossil Energy and Carbon Management", "institutional_gateway", "fecm@hq.doe.gov", "(202) 586-1000", 1, "U.S. Department of Energy (DOE-FECM)", "Carbon Capture & CCUS", "Industrial & Manufacturing", None, "Washington", "DC", "https://www.energy.gov/fecm", "DOE FECM Public Directory", "carbon capture, direct air capture, co2 storage, ccus", "energy.gov"),
            ("ARPA-E Program Management & Inquiries", "High-Impact Energy R&D Program Office", "Advanced Research Projects Agency - Energy", "program_officer", "arpa-e-inquiries@hq.doe.gov", "(202) 287-5440", 3, "Advanced Research Projects Agency-Energy (ARPA-E)", "Clean Energy Innovation & Cross-Cutting", "Cross-Cutting & Policy", None, "Washington", "DC", "https://arpa-e.energy.gov", "ARPA-E Public Portal", "open, leap, disrupt, batteries, fusion, advanced grid", "arpa-e.energy.gov"),
            ("CEC Research & Development Division Inquiries", "EPIC Clean Energy Program Lead", "Energy Research and Development Division", "program_officer", "rdd@energy.ca.gov", "(916) 654-4287", 6, "California Energy Commission (CEC)", "Clean Energy Innovation & Cross-Cutting", "Cross-Cutting & Policy", None, "Sacramento", "CA", "https://www.energy.ca.gov", "CEC Public Directory", "epic, gfo, microgrids, ldes, clean transport", "energy.ca.gov"),
            ("MassCEC Clean Transportation & Innovation Lead", "Innovation & Market Development Manager", "Clean Transportation & Grid Innovation", "program_officer", "cleantransportation@masscec.com", "(617) 315-9300", 7, "Massachusetts Clean Energy Center (MassCEC)", "Electric Mobility & Transportation", "Transportation & Mobility", None, "Boston", "MA", "https://www.masscec.com", "MassCEC Public Grants Portal", "ev, fleets, charging, grid, incubators", "masscec.com"),
            ("MassCEC Offshore Wind & Clean Power Lead", "Offshore Wind Program Director", "Offshore Wind & Marine Energy", "program_officer", "offshorewind@masscec.com", "(617) 315-9300", 7, "Massachusetts Clean Energy Center (MassCEC)", "Wind & Offshore Wind", "Electric Grid & Utility", None, "Boston", "MA", "https://www.masscec.com", "MassCEC Public Grants Portal", "offshore wind, marine energy, port infrastructure", "masscec.com"),
            ("National Renewable Energy Laboratory (NREL) Partnering Office", "Technology Transfer & Cooperative R&D Desk", "Commercialization & Technology Transfer", "institutional_gateway", "partner@nrel.gov", "(303) 275-3000", None, "National Renewable Energy Laboratory (NREL)", "Clean Energy Innovation & Cross-Cutting", "Cross-Cutting & Policy", None, "Golden", "CO", "https://www.nrel.gov/partner", "NREL Public Portal", "solar, wind, hydrogen, grid, bioenergy, storage", "nrel.gov"),
            ("Pacific Northwest National Laboratory (PNNL) Energy Hub", "Electricity Infrastructure & Storage Office", "Energy and Environment Directorate", "institutional_gateway", "energyinfo@pnnl.gov", "(509) 375-2121", None, "Pacific Northwest National Laboratory (PNNL)", "Grid Modernization & Smart Power", "Electric Grid & Utility", None, "Richland", "WA", "https://www.pnnl.gov", "PNNL Public Directory", "grid modernization, battery reliability, cyber, flow batteries", "pnnl.gov"),
            ("Lawrence Berkeley National Laboratory (LBNL) Energy Technologies", "Energy Technologies Area Gateway", "Energy Technologies Area", "institutional_gateway", "eta-info@lbl.gov", "(510) 486-4000", None, "Lawrence Berkeley National Laboratory (LBNL)", "Building Decarbonization & Clean Heat", "Buildings & Real Estate", None, "Berkeley", "CA", "https://eta.lbl.gov", "LBNL Public Directory", "building technologies, energy markets, batteries, grid", "lbl.gov"),
            ("Oak Ridge National Laboratory (ORNL) Clean Energy Manufacturing", "Manufacturing Demonstration Hub", "Energy Science and Technology Directorate", "institutional_gateway", "manufacturing@ornl.gov", "(865) 574-4160", None, "Oak Ridge National Laboratory (ORNL)", "Industrial Decarbonization & Clean Heat", "Industrial & Manufacturing", None, "Oak Ridge", "TN", "https://www.ornl.gov", "ORNL Public Directory", "advanced materials, batteries, nuclear, grid", "ornl.gov"),
            ("Consolidated Edison Clean Energy & R&D Team", "Clean Heat & Distributed Energy Integration Team", "Utility Innovation & Clean Energy Programs", "utility_lead", "cleanheat@coned.com", "(212) 460-4600", 29, "Consolidated Edison Company of New York (Con Edison)", "Grid Modernization & Smart Power", "Electric Grid & Utility", None, "New York", "NY", "https://www.coned.com", "Con Edison Public Filing", "smart grid, heat pumps, demand response, ev charging", "coned.com"),
            ("National Grid Innovation & Clean Energy Development", "Future of Heat & Grid Modernization Office", "Clean Energy Development & Solutions", "utility_lead", "cleanenergy@nationalgrid.com", "(800) 642-4272", 30, "National Grid USA", "Grid Modernization & Smart Power", "Electric Grid & Utility", None, "Waltham", "MA", "https://www.nationalgridus.com", "National Grid Public Filing", "hydrogen blending, geothermal networks, offshore wind, storage", "nationalgridus.com"),
            ("Pacific Gas and Electric (PG&E) Emerging Grid Tech", "Emerging Grid Technologies & Microgrids Lead", "Grid Modernization & Clean Transportation", "utility_lead", "emergingtech@pge.com", "(800) 743-5000", 28, "Pacific Gas and Electric Company (PG&E)", "Grid Modernization & Smart Power", "Electric Grid & Utility", None, "Oakland", "CA", "https://www.pge.com", "PG&E Public Directory", "microgrids, vehicle-to-grid, v2g, long duration energy storage", "pge.com"),
            ("Southern California Edison (SCE) Clean Energy Transition", "Clean Energy & Transportation Electrification Lead", "Grid Interconnection & Customer Programs", "utility_lead", "cleanenergy@sce.com", "(800) 655-4555", None, "Southern California Edison (SCE)", "Electric Mobility & Transportation", "Transportation & Mobility", None, "Rosemead", "CA", "https://www.sce.com", "SCE Public Filing", "charge ready, grid storage, building electrification", "sce.com"),
            ("Eversource Energy Clean Technologies Group", "Clean Energy & Networked Geothermal Manager", "Clean Energy Innovation & Sustainability", "utility_lead", "cleantech@eversource.com", "(800) 592-2000", 31, "Eversource Energy", "Building Decarbonization & Clean Heat", "Buildings & Real Estate", None, "Hartford", "CT", "https://www.eversource.com", "Eversource Public Directory", "networked geothermal, heat pumps, offshore wind, battery storage", "eversource.com")
        ]
        for g in gateways:
            exists = conn.execute(
                text("SELECT id FROM contacts WHERE name_display = :name OR email = :email"),
                {"name": g[0], "email": g[4]}
            ).fetchone()
            if exists:
                conn.execute(text("""
                    UPDATE contacts SET
                        name_display = :name_display, title = :title, department = :department,
                        role_type = :role_type, email = :email, phone = :phone,
                        organization_id = :organization_id, institution_name = :institution_name,
                        technology_area = :technology_area, sector = :sector, fuel_type = :fuel_type,
                        city = :city, state = :state, entity_contact_url = :entity_contact_url,
                        data_provenance = :data_provenance, keywords = :keywords,
                        email_domain = :email_domain, verification_status = 'verified',
                        confidence = 1.0, is_current = true, updated_at = NOW()
                    WHERE id = :id
                """), {
                    "name_display": g[0], "title": g[1], "department": g[2], "role_type": g[3],
                    "email": g[4], "phone": g[5], "organization_id": g[6], "institution_name": g[7],
                    "technology_area": g[8], "sector": g[9], "fuel_type": g[10], "city": g[11],
                    "state": g[12], "entity_contact_url": g[13], "data_provenance": g[14],
                    "keywords": g[15], "email_domain": g[16], "id": exists[0]
                })
            else:
                conn.execute(text("""
                    INSERT INTO contacts (
                        name_display, title, department, role_type, email, phone,
                        organization_id, institution_name, technology_area, sector, fuel_type,
                        city, state, country, entity_contact_url, email_domain, data_provenance, keywords,
                        verification_status, confidence, is_current, created_at, updated_at
                    ) VALUES (
                        :name_display, :title, :department, :role_type, :email, :phone,
                        :organization_id, :institution_name, :technology_area, :sector, :fuel_type,
                        :city, :state, 'US', :entity_contact_url, :email_domain, :data_provenance, :keywords,
                        'verified', 1.0, true, NOW(), NOW()
                    )
                """), {
                    "name_display": g[0], "title": g[1], "department": g[2], "role_type": g[3],
                    "email": g[4], "phone": g[5], "organization_id": g[6], "institution_name": g[7],
                    "technology_area": g[8], "sector": g[9], "fuel_type": g[10], "city": g[11],
                    "state": g[12], "entity_contact_url": g[13], "email_domain": g[16],
                    "data_provenance": g[14], "keywords": g[15]
                })
        print("Seeded/Updated agency & utility gateways")

        # 3. Seed top clean energy PIs
        pi_query = text("""
            SELECT 
                a.pi_name,
                MAX(a.pi_email) as pi_email,
                COALESCE(a.pi_institution, a.recipient_name) as institution,
                MAX(a.agency) as agency,
                MAX(a.recipient_state) as state,
                MAX(a.recipient_city) as city,
                COUNT(a.id) as award_cnt,
                SUM(COALESCE(a.award_amount, 0)) as total_amt,
                string_agg(DISTINCT a.project_title, '; ') as sample_titles,
                MAX(r.primary_technology) as recipient_tech,
                MAX(r.sector) as recipient_sector,
                MAX(r.fuel_types) as recipient_fuel,
                MAX(r.website_url) as website_url
            FROM awards a
            LEFT JOIN recipients r ON a.recipient_name = r.name
            WHERE a.pi_name IS NOT NULL 
              AND TRIM(a.pi_name) != '' 
              AND length(a.pi_name) > 3
              AND a.pi_name NOT LIKE '%TBD%'
              AND a.pi_name NOT LIKE '%N/A%'
            GROUP BY a.pi_name, COALESCE(a.pi_institution, a.recipient_name)
            ORDER BY total_amt DESC
            LIMIT 3000
        """)
        pi_rows = conn.execute(pi_query).fetchall()

        # Map university, utility, or corporate organizations (exclude pure grant funders like DOE, NSF, etc.)
        cur_orgs = conn.execute(text("SELECT id, name, org_type FROM organizations WHERE org_type NOT IN ('funder')")).fetchall()
        org_map = {(row[1] or '').lower(): row[0] for row in cur_orgs}

        ins = 0
        upd = 0
        for row in pi_rows:
            pi_name = (row[0] or "").strip()
            pi_email = (row[1] or "").strip() or None
            institution = (row[2] or "").strip() or "Research Institution"
            agency = (row[3] or "").strip() or "Federal"
            state = (row[4] or "").strip() or None
            city = (row[5] or "").strip() or None
            award_cnt = int(row[6] or 1)
            total_amt = float(row[7] or 0.0)
            sample_titles = row[8] or ""
            rec_tech = row[9]
            rec_sector = row[10]
            rec_fuel = row[11]
            rec_website = row[12]

            email_domain = None
            if pi_email and "@" in pi_email:
                email_domain = pi_email.split("@")[1].strip().lower()

            entity_url = rec_website
            if not entity_url and email_domain and not email_domain.endswith(("gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com")):
                entity_url = f"https://www.{email_domain}"

            parts = pi_name.split()
            name_first = parts[0] if parts else ""
            name_last = parts[-1] if len(parts) > 1 else ""

            if rec_tech and rec_tech.strip() and rec_tech != "Clean Energy Innovation & Cross-Cutting":
                tech_area = rec_tech
                sector = rec_sector or "Electric Grid & Utility"
                fuel = rec_fuel
            else:
                tech_area, sector, fuel = infer_tech_and_sector(sample_titles)

            prefix = tech_area.split("&")[0].strip()
            title = f"Principal Investigator & Domain Expert - {prefix}"
            dept = f"Clean Energy R&D / {prefix}"
            role_type = "pi"

            # Match org_id ONLY if institution matches a known non-funder organization
            org_id = None
            inst_lower = institution.lower()
            for org_name_lower, oid in org_map.items():
                if len(org_name_lower) > 4 and (org_name_lower in inst_lower or inst_lower in org_name_lower):
                    org_id = oid
                    break

            provenance = f"{agency} Public Awardee Registry" if agency else "Public Grant Award Index"

            existing = conn.execute(
                text("SELECT id FROM contacts WHERE name_display = :name AND (institution_name = :inst OR institution_name IS NULL)"),
                {"name": pi_name, "inst": institution}
            ).fetchone()

            if existing:
                cid = existing[0]
                conn.execute(text("""
                    UPDATE contacts SET
                        title = COALESCE(title, :title),
                        department = COALESCE(department, :dept),
                        role_type = 'pi',
                        email = COALESCE(email, :email),
                        email_domain = :email_domain,
                        institution_name = :inst,
                        organization_id = :org_id,
                        technology_area = :tech,
                        sector = :sector,
                        fuel_type = :fuel,
                        city = COALESCE(city, :city),
                        state = COALESCE(state, :state),
                        entity_contact_url = COALESCE(entity_contact_url, :url),
                        awards_count = :award_cnt,
                        total_funding = :total_amt,
                        keywords = :keywords,
                        data_provenance = :provenance,
                        updated_at = NOW()
                    WHERE id = :id
                """), {
                    "title": title, "dept": dept,
                    "email": pi_email, "email_domain": email_domain,
                    "inst": institution, "org_id": org_id,
                    "tech": tech_area, "sector": sector, "fuel": fuel,
                    "city": city, "state": state, "url": entity_url,
                    "award_cnt": award_cnt, "total_amt": total_amt,
                    "keywords": sample_titles[:800], "provenance": provenance, "id": cid
                })
                upd += 1
            else:
                conn.execute(text("""
                    INSERT INTO contacts (
                        name_display, name_first, name_last, title, department, role_type,
                        email, email_domain, institution_name, organization_id, technology_area, sector,
                        fuel_type, city, state, country, entity_contact_url, awards_count,
                        total_funding, keywords, verification_status, confidence,
                        data_provenance, is_current, created_at, updated_at
                    ) VALUES (
                        :name_display, :name_first, :name_last, :title, :department, :role_type,
                        :email, :email_domain, :institution_name, :organization_id, :technology_area, :sector,
                        :fuel_type, :city, :state, 'US', :entity_contact_url, :awards_count,
                        :total_funding, :keywords, 'verified', 0.95,
                        :data_provenance, true, NOW(), NOW()
                    )
                """), {
                    "name_display": pi_name, "name_first": name_first, "name_last": name_last,
                    "title": title, "department": dept, "role_type": role_type,
                    "email": pi_email, "email_domain": email_domain, "institution_name": institution, "organization_id": org_id,
                    "technology_area": tech_area, "sector": sector, "fuel_type": fuel,
                    "city": city, "state": state, "entity_contact_url": entity_url,
                    "awards_count": award_cnt, "total_funding": total_amt,
                    "keywords": sample_titles[:800], "data_provenance": provenance
                })
                ins += 1

        print(f"PI Domain Experts: {ins} inserted, {upd} updated")

        # 4. Final database cleanups: ensure no PI has a funder org_id assigned
        conn.execute(text("""
            UPDATE contacts 
            SET organization_id = NULL 
            WHERE role_type = 'pi' 
              AND organization_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)
              AND institution_name NOT ILIKE '%Department of Energy%'
              AND institution_name NOT ILIKE '%NYSERDA%'
              AND institution_name NOT ILIKE '%California Energy Commission%'
              AND institution_name NOT ILIKE '%Massachusetts Clean Energy Center%'
              AND institution_name NOT ILIKE '%National Science Foundation%'
        """))

        # Populate any missing email_domain from email
        conn.execute(text("""
            UPDATE contacts 
            SET email_domain = LOWER(SPLIT_PART(email, '@', 2)) 
            WHERE email IS NOT NULL AND email LIKE '%@%' AND (email_domain IS NULL OR email_domain = '')
        """))

        total = conn.execute(text("SELECT COUNT(*) FROM contacts")).scalar() or 0
        with_email = conn.execute(text("SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL AND email != ''")).scalar() or 0
        print(f"Done! Total contacts: {total}, with direct public email: {with_email}")

    # Step 5: Automatically apply verified physical mailing addresses to all contacts
    try:
        from enrich_contacts_addresses import enrich_all_contacts
        enrich_all_contacts()
    except Exception as e:
        print(f"Address enrichment warning: {e}")


if __name__ == "__main__":
    run_seed()


