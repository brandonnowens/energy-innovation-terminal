"""Tier 7 States (Ranks 25-28): Oregon, Louisiana, Alabama, Kentucky."""

TIER7_DATA = {
    "OR": {
        "state_code": "OR",
        "state_name": "Oregon",
        "gdp_billions": 316,
        "rank": 25,
        "regulatory_body": "Public Utility Commission of Oregon (OPUC)",
        "utilities": [
            {
                "name": "Portland General Electric",
                "short_name": "PGE",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Portland General Electric",
                "website": "https://portlandgeneral.com",
                "domain": "portlandgeneral.com",
                "city": "Portland",
                "state": "OR",
                "zip_code": "97204",
                "service_territory": "Portland metropolitan area, Salem, and northern Willamette Valley (51 cities across 7 counties)",
                "description": "Oregon's largest electric utility, serving approximately 930,000 customers (nearly half of Oregon's population), recognized globally for the Smart Grid Testbed and Wheatridge Renewable Facility.",
                "logo_domain": "portlandgeneral.com",
                "founded_year": 1889,
                "programs": [
                    {
                        "name": "PGE Smart Grid Testbed & Virtual Power Plant Program",
                        "program_type": "innovation",
                        "description": "National award-winning living laboratory across three smart neighborhoods, aggregating 20,000+ customer DERs, water heaters, and smart thermostats into a flexible VPP.",
                        "url": "https://portlandgeneral.com/smart-grid-testbed",
                        "active": True,
                        "target_stage": "demonstration",
                    },
                    {
                        "name": "PGE Clean Energy Plan & All-Source Storage RFP",
                        "program_type": "deployment",
                        "description": "HB 2021 compliance targeting 100% emissions reduction by 2040, procuring multi-hundred megawatt battery energy storage and non-wires solutions.",
                        "url": "https://portlandgeneral.com/our-company/energy-strategy/clean-energy-plan",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "PGE-SGTB-DERMS-2026",
                        "name": "PGE Smart Grid Testbed Dynamic DERMS & Microgrid Solicitations",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "grant",
                        "total_funding": 25000000.0,
                        "max_per_award": 6000000.0,
                        "short_description": "Competitive funding for advanced DERMS artificial intelligence software, smart water heater load shifting, and commercial microgrid orchestration.",
                        "service_territory": "Portland, Hillsboro, and Milwaukie / Willamette Valley",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://portlandgeneral.com/suppliers",
                        "year": 2026,
                        "keywords": "Smart Grid Testbed, DERMS, VPP, demand flexibility, PGE, Portland, Hillsboro",
                        "technologies": ["Grid Modernization & Smart Grid", "AI, Computing & Energy Cyber", "Energy Storage", "Microgrids & Resilience"],
                        "sectors": ["Electric Grid & Utility", "Residential", "Commercial"],
                        "fuels": ["Electricity"],
                        "stage": "Pilot & Demonstration",
                    },
                    {
                        "solicitation_number": "PGE-CLEAN-STORAGE-2025",
                        "name": "PGE All-Source Clean Energy & 400MW Battery Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "closed",
                        "funding_type": "contract",
                        "total_funding": 75000000.0,
                        "max_per_award": 35000000.0,
                        "short_description": "Procurement of 400MW/1,600MWh utility-scale battery storage facilities to complement the Wheatridge Renewable Facility (wind+solar+storage).",
                        "service_territory": "PGE Service Area / Eastern & Western Oregon",
                        "utility_program_type": "Innovation RFP",
                        "year": 2025,
                        "keywords": "Wheatridge, battery storage, BESS, Clean Energy Plan, HB 2021, PGE",
                        "technologies": ["Energy Storage", "Solar PV", "Onshore Wind"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Solar", "Wind", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "PGE-AWD-2025-01",
                        "recipient_name": "NextEra Energy Resources",
                        "recipient_type": "company",
                        "project_title": "Seaside 200MW/800MWh Standalone Battery Storage Project for PGE Grid Reliability",
                        "award_amount": 34000000.0,
                        "year": 2025,
                        "recipient_city": "Juno Beach",
                        "recipient_state": "FL",
                        "latitude": 26.8798,
                        "longitude": -80.0534,
                        "pi_name": "Rebecca Kujawa",
                        "opportunity_sol_num": "PGE-CLEAN-STORAGE-2025",
                        "technologies": ["Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    },
                    {
                        "external_award_id": "PGE-AWD-2024-02",
                        "recipient_name": "AutoGrid Systems, Inc. (Uplight)",
                        "recipient_type": "company",
                        "project_title": "AutoGrid Flex Virtual Power Plant & Customer DER Co-Optimization Engine for PGE Testbed",
                        "award_amount": 5600000.0,
                        "year": 2024,
                        "recipient_city": "Portland",
                        "recipient_state": "OR",
                        "latitude": 45.5152,
                        "longitude": -122.6784,
                        "pi_name": "Amit Narayan",
                        "opportunity_sol_num": "PGE-SGTB-DERMS-2026",
                        "technologies": ["AI, Computing & Energy Cyber", "Non-Wires Solutions (NWS)"],
                        "sectors": ["Electric Grid & Utility", "Residential"]
                    }
                ]
            }
        ]
    },
    "LA": {
        "state_code": "LA",
        "state_name": "Louisiana",
        "gdp_billions": 309,
        "rank": 26,
        "regulatory_body": "Louisiana Public Service Commission (LPSC) / MISO",
        "utilities": [
            {
                "name": "Entergy Louisiana",
                "short_name": "Entergy LA",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Entergy",
                "website": "https://www.entergy-louisiana.com",
                "domain": "entergy.com",
                "city": "Baton Rouge",
                "state": "LA",
                "zip_code": "70802",
                "service_territory": "Southern, Central, and Northern Louisiana (Baton Rouge, Lake Charles, Lafayette, Monroe)",
                "description": "Entergy's largest operating company, delivering electricity to more than 1.1 million customers in 58 parishes across Louisiana.",
                "logo_domain": "entergy.com",
                "founded_year": 1927,
                "programs": [
                    {
                        "name": "Entergy Louisiana Grid Hardening & Clean Industrial Transition",
                        "program_type": "innovation",
                        "description": "DOE-partnered grid resilience and industrial decarbonization, floating microgrids for hurricane response, and industrial hydrogen/CCUS integration.",
                        "url": "https://www.entergy-louisiana.com/resilience",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "ENTLA-HARDEN-MICRO-2026",
                        "name": "Entergy Louisiana Hurricane Hardening & Industrial Microgrid RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 45000000.0,
                        "max_per_award": 15000000.0,
                        "short_description": "Procurement of hurricane-resilient microgrids, mobile black-start battery systems, and automated composite pole line sensors in coastal parishes.",
                        "service_territory": "Gulf Coast / Terrebonne, Lafourche & Calcasieu Parishes",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.entergy.com/suppliers",
                        "year": 2026,
                        "keywords": "grid hardening, hurricane resilience, microgrid, black start, Entergy Louisiana, Baton Rouge",
                        "technologies": ["Microgrids & Resilience", "Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"],
                        "fuels": ["Electricity", "Storage & Chemical"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "ENTLA-AWD-2025-01",
                        "recipient_name": "Mitsubishi Power Americas",
                        "recipient_type": "company",
                        "project_title": "Industrial Clean Hydrogen-Capable Gas Turbine and Microgrid Hardening at Geismar",
                        "award_amount": 14200000.0,
                        "year": 2025,
                        "recipient_city": "Geismar",
                        "recipient_state": "LA",
                        "latitude": 30.2227,
                        "longitude": -90.9634,
                        "pi_name": "Bill Newsom",
                        "opportunity_sol_num": "ENTLA-HARDEN-MICRO-2026",
                        "technologies": ["Hydrogen & Clean Fuels", "Microgrids & Resilience"],
                        "sectors": ["Industry & Manufacturing", "Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Cleco Power",
                "short_name": "Cleco",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Cleco Corporate Holdings",
                "website": "https://www.cleco.com",
                "domain": "cleco.com",
                "city": "Pineville",
                "state": "LA",
                "zip_code": "71360",
                "service_territory": "Central and Southeastern Louisiana (Alexandria, Pineville, Slidell)",
                "description": "Regulated electric utility providing power to approximately 290,000 customers in 24 parishes with groundbreaking Project Diamond Vault CCUS.",
                "logo_domain": "cleco.com",
                "founded_year": 1935,
                "programs": [
                    {
                        "name": "Cleco Project Diamond Vault Carbon Capture & Storage (CCUS)",
                        "program_type": "innovation",
                        "description": "$900M pioneering project to capture 95%+ of CO2 emissions at the Madison Parish power station and permanently sequester it deep underground.",
                        "url": "https://www.cleco.com/diamondvault",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "CLECO-CCUS-VAULT-2026",
                        "name": "Cleco Project Diamond Vault Carbon Sequestration Engineering RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 35000000.0,
                        "max_per_award": 12000000.0,
                        "short_description": "Front-End Engineering and Design (FEED) and dynamic CO2 monitoring systems for deep saline aquifer carbon sequestration in Louisiana.",
                        "service_territory": "Madison Parish / Central Louisiana",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.cleco.com/suppliers",
                        "year": 2026,
                        "keywords": "CCUS, carbon capture, Diamond Vault, sequestration, Cleco, Madison Parish",
                        "technologies": ["Carbon Capture & Management (CCUS)", "Industrial Decarbonization"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"],
                        "fuels": ["Electricity", "Natural Gas"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "CLECO-AWD-2024-01",
                        "recipient_name": "Sargent & Lundy LLC",
                        "recipient_type": "company",
                        "project_title": "Project Diamond Vault Commercial-Scale CCUS FEED Study and Geological Modeling",
                        "award_amount": 11800000.0,
                        "year": 2024,
                        "recipient_city": "Chicago",
                        "recipient_state": "IL",
                        "latitude": 41.8781,
                        "longitude": -87.6298,
                        "pi_name": "Victor Der",
                        "opportunity_sol_num": "CLECO-CCUS-VAULT-2026",
                        "technologies": ["Carbon Capture & Management (CCUS)"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"]
                    }
                ]
            }
        ]
    },
    "AL": {
        "state_code": "AL",
        "state_name": "Alabama",
        "gdp_billions": 300,
        "rank": 27,
        "regulatory_body": "Alabama Public Service Commission (APSC)",
        "utilities": [
            {
                "name": "Alabama Power",
                "short_name": "Alabama Power",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Southern Company",
                "website": "https://www.alabamapower.com",
                "domain": "alabamapower.com",
                "city": "Birmingham",
                "state": "AL",
                "zip_code": "35203",
                "service_territory": "Southern two-thirds of Alabama (Birmingham, Mobile, Montgomery, Tuscaloosa)",
                "description": "Southern Company electric utility providing power to 1.5 million customers across 44,500 square miles in Alabama.",
                "logo_domain": "alabamapower.com",
                "founded_year": 1906,
                "programs": [
                    {
                        "name": "Alabama Power Smart Neighborhood & Microgrid Innovation",
                        "program_type": "innovation",
                        "description": "Reynolds Landing Smart Neighborhood (first residential microgrid in the Southeast with solar+storage+smart homes) and grid modernization.",
                        "url": "https://www.alabamapower.com/smartneighborhood",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "ALP-SMART-MICRO-2026",
                        "name": "Alabama Power Advanced Residential Microgrid & Heat Pump RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "grant",
                        "total_funding": 20000000.0,
                        "max_per_award": 5000000.0,
                        "short_description": "Demonstration of automated connected community heat pumps, smart circuit panels, and centralized neighborhood battery storage.",
                        "service_territory": "Birmingham & Montgomery Metros",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.alabamapower.com/suppliers",
                        "year": 2026,
                        "keywords": "Smart Neighborhood, residential microgrid, heat pump, connected community, Alabama Power",
                        "technologies": ["Heat Pumps & Building Electrification", "Microgrids & Resilience", "Energy Storage"],
                        "sectors": ["Residential", "Buildings", "Electric Grid & Utility"],
                        "fuels": ["Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "ALP-AWD-2024-01",
                        "recipient_name": "Oak Ridge National Laboratory (ORNL)",
                        "recipient_type": "lab",
                        "project_title": "Smart Neighborhood Connected Homes Transactive Energy and Heat Pump Optimization",
                        "award_amount": 4700000.0,
                        "year": 2024,
                        "recipient_city": "Oak Ridge",
                        "recipient_state": "TN",
                        "latitude": 36.0104,
                        "longitude": -84.2696,
                        "pi_name": "Dr. Roderick Jackson",
                        "opportunity_sol_num": "ALP-SMART-MICRO-2026",
                        "technologies": ["Heat Pumps & Building Electrification", "AI, Computing & Energy Cyber"],
                        "sectors": ["Residential", "Buildings"]
                    }
                ]
            }
        ]
    },
    "KY": {
        "state_code": "KY",
        "state_name": "Kentucky",
        "gdp_billions": 277,
        "rank": 28,
        "regulatory_body": "Kentucky Public Service Commission (KY PSC) / PJM / MISO",
        "utilities": [
            {
                "name": "Louisville Gas and Electric and Kentucky Utilities",
                "short_name": "LG&E and KU",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "PPL Corporation",
                "website": "https://lge-ku.com",
                "domain": "lge-ku.com",
                "city": "Louisville",
                "state": "KY",
                "zip_code": "40202",
                "service_territory": "Louisville metropolitan area, Lexington, and 77 Kentucky counties (plus 5 in Virginia)",
                "description": "PPL Corporation subsidiaries providing electricity to 1 million customers and natural gas to 330,000 customers in Kentucky.",
                "logo_domain": "lge-ku.com",
                "founded_year": 1838,
                "programs": [
                    {
                        "name": "LG&E and KU Solar Share & E.W. Brown Energy Innovation Center",
                        "program_type": "innovation",
                        "description": "E.W. Brown Generating Station testing universal solar, 1MW/4MWh battery energy storage, and CCUS with the University of Kentucky.",
                        "url": "https://lge-ku.com/environment/renewable-energy",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "LGEKU-BROWN-STORAGE-2026",
                        "name": "LG&E and KU E.W. Brown Long-Duration Storage & Carbon Capture RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 30000000.0,
                        "max_per_award": 10000000.0,
                        "short_description": "Procurement of multi-hour battery storage, smart inverters, and post-combustion carbon capture pilot equipment at E.W. Brown site.",
                        "service_territory": "Mercer County / Central Kentucky",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://lge-ku.com/suppliers",
                        "year": 2026,
                        "keywords": "E.W. Brown, energy storage, BESS, carbon capture, CCUS, LG&E, KU, Louisville",
                        "technologies": ["Energy Storage", "Carbon Capture & Management (CCUS)", "Solar PV"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"],
                        "fuels": ["Storage & Chemical", "Solar", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "LGEKU-AWD-2024-01",
                        "recipient_name": "University of Kentucky Center for Applied Energy Research (CAER)",
                        "recipient_type": "university",
                        "project_title": "Field Pilot of 2MW Post-Combustion Solvent-Based Carbon Capture at E.W. Brown Plant",
                        "award_amount": 9200000.0,
                        "year": 2024,
                        "recipient_city": "Lexington",
                        "recipient_state": "KY",
                        "latitude": 38.0406,
                        "longitude": -84.5037,
                        "pi_name": "Dr. Rodney Andrews",
                        "opportunity_sol_num": "LGEKU-BROWN-STORAGE-2026",
                        "technologies": ["Carbon Capture & Management (CCUS)"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"]
                    }
                ]
            }
        ]
    }
}
