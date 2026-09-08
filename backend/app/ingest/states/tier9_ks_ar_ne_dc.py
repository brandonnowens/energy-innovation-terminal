"""Tier 9 States (Ranks 33-36): Kansas, Arkansas, Nebraska, District of Columbia."""

TIER9_DATA = {
    "KS": {
        "state_code": "KS",
        "state_name": "Kansas",
        "gdp_billions": 226,
        "rank": 33,
        "regulatory_body": "Kansas Corporation Commission (KCC) / SPP",
        "utilities": [
            {
                "name": "Evergy Kansas",
                "short_name": "Evergy KS",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Evergy",
                "website": "https://www.evergy.com",
                "domain": "evergy.com",
                "city": "Topeka / Wichita",
                "state": "KS",
                "zip_code": "66612",
                "service_territory": "Eastern and South Central Kansas (Wichita, Topeka, Lawrence, Manhattan, Hutchinson)",
                "description": "Operating as Evergy Kansas Central and Evergy Kansas South, serving approximately 1 million customers across eastern and central Kansas.",
                "logo_domain": "evergy.com",
                "founded_year": 1909,
                "programs": [
                    {
                        "name": "Evergy Kansas Wind Integration & Transmission Innovation",
                        "program_type": "innovation",
                        "description": "Integrating world-class Kansas wind capacity with dynamic grid controls, Wolf Creek Nuclear support, and battery storage.",
                        "url": "https://www.evergy.com/cleanenergy",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "EVERGYKS-WIND-STORAGE-2026",
                        "name": "Evergy Kansas Wind Fleet Smoothing & Substation Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 35000000.0,
                        "max_per_award": 12000000.0,
                        "short_description": "Procurement of 100MW battery energy storage systems, advanced inverters, and wind forecasting AI algorithms in the SPP market.",
                        "service_territory": "Central & Eastern Kansas / Wichita & Topeka",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.evergy.com/suppliers",
                        "year": 2026,
                        "keywords": "wind integration, BESS, SPP, battery storage, Evergy Kansas, Wichita, Topeka",
                        "technologies": ["Onshore Wind", "Energy Storage", "AI, Computing & Energy Cyber"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Wind", "Storage & Chemical", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "EVERGYKS-AWD-2024-01",
                        "recipient_name": "NextEra Energy Resources",
                        "recipient_type": "company",
                        "project_title": "Soldier Creek Wind and Battery Co-Located Grid Support Center",
                        "award_amount": 11500000.0,
                        "year": 2024,
                        "recipient_city": "Topeka",
                        "recipient_state": "KS",
                        "latitude": 39.0558,
                        "longitude": -95.6890,
                        "pi_name": "Rebecca Kujawa",
                        "opportunity_sol_num": "EVERGYKS-WIND-STORAGE-2026",
                        "technologies": ["Onshore Wind", "Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "AR": {
        "state_code": "AR",
        "state_name": "Arkansas",
        "gdp_billions": 176,
        "rank": 34,
        "regulatory_body": "Arkansas Public Service Commission (APSC) / MISO / SPP",
        "utilities": [
            {
                "name": "Entergy Arkansas",
                "short_name": "Entergy AR",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Entergy",
                "website": "https://www.entergy-arkansas.com",
                "domain": "entergy.com",
                "city": "Little Rock",
                "state": "AR",
                "zip_code": "72201",
                "service_territory": "Central, Eastern, and Southern Arkansas (Little Rock, Pine Bluff, Jonesboro, Hot Springs, El Dorado)",
                "description": "Arkansas's largest electric utility, providing electricity to approximately 730,000 customers in 63 of Arkansas's 75 counties.",
                "logo_domain": "entergy.com",
                "founded_year": 1913,
                "programs": [
                    {
                        "name": "Entergy Arkansas Solar-Plus-Storage & Grid Hardening",
                        "program_type": "deployment",
                        "description": "Deploying 1.2GW+ utility solar (Searcy, Stuttgart, Chicot, Walnut Bend) paired with utility battery storage and Arkansas Nuclear One clean baseload.",
                        "url": "https://www.entergy-arkansas.com/cleanenergy",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "ENTAR-SOLAR-BESS-2026",
                        "name": "Entergy Arkansas Large-Scale Solar + Battery Energy Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 45000000.0,
                        "max_per_award": 15000000.0,
                        "short_description": "Competitive procurement of 150MW solar and 50MW/200MWh battery storage facilities in central and eastern Arkansas Delta regions.",
                        "service_territory": "Arkansas Delta & Central Arkansas",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.entergy.com/suppliers",
                        "year": 2026,
                        "keywords": "solar-plus-storage, BESS, Arkansas Delta, Searcy, Entergy Arkansas, Little Rock",
                        "technologies": ["Solar PV", "Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility", "Agriculture & Forestry"],
                        "fuels": ["Solar", "Storage & Chemical", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "ENTAR-AWD-2025-01",
                        "recipient_name": "NextEra Energy Resources",
                        "recipient_type": "company",
                        "project_title": "Searcy 100MW Solar and 30MW/120MWh Battery Storage Project",
                        "award_amount": 14500000.0,
                        "year": 2025,
                        "recipient_city": "Searcy",
                        "recipient_state": "AR",
                        "latitude": 35.2506,
                        "longitude": -91.7362,
                        "pi_name": "Rebecca Kujawa",
                        "opportunity_sol_num": "ENTAR-SOLAR-BESS-2026",
                        "technologies": ["Solar PV", "Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Arkansas Electric Cooperative Corporation",
                "short_name": "AECC",
                "org_type": "utility",
                "sub_type": "Generation & Transmission Cooperative",
                "parent_holding_company": "AECC Member Cooperatives",
                "website": "https://www.aecc.com",
                "domain": "aecc.com",
                "city": "Little Rock",
                "state": "AR",
                "zip_code": "72209",
                "service_territory": "Rural Arkansas (serving 17 local electric distribution co-ops and 1.3 million people)",
                "description": "Wholesale generation and transmission cooperative owned by 17 electric distribution cooperatives in Arkansas.",
                "logo_domain": "aecc.com",
                "founded_year": 1949,
                "programs": [
                    {
                        "name": "AECC Hydro & Clean Co-op Innovation Program",
                        "program_type": "innovation",
                        "description": "Operating run-of-the-river hydroelectric stations on the Arkansas River and integrating utility-scale solar and co-op battery storage.",
                        "url": "https://www.aecc.com/generation-resources/",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "AECC-HYDRO-STORAGE-2026",
                        "name": "AECC Arkansas River Hydro Modernization & Rural Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 20000000.0,
                        "max_per_award": 6000000.0,
                        "short_description": "Modernization of turbine controls on Arkansas River lock-and-dam hydro facilities and rural battery storage for agricultural load peaks.",
                        "service_territory": "Arkansas River Valley & Rural Arkansas",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.aecc.com/about-aecc",
                        "year": 2026,
                        "keywords": "hydropower, run-of-river, Arkansas River, rural storage, AECC, electric cooperative",
                        "technologies": ["Water & Marine Power", "Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility", "Agriculture & Forestry"],
                        "fuels": ["Hydro & Marine", "Storage & Chemical", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "AECC-AWD-2024-01",
                        "recipient_name": "Voith Hydro Inc.",
                        "recipient_type": "company",
                        "project_title": "Digital Turbine Governor and Excitation System Upgrades for Clyde T. Ellis Hydro Station",
                        "award_amount": 5800000.0,
                        "year": 2024,
                        "recipient_city": "York",
                        "recipient_state": "PA",
                        "latitude": 39.9626,
                        "longitude": -76.7277,
                        "pi_name": "Stanley Kocon",
                        "opportunity_sol_num": "AECC-HYDRO-STORAGE-2026",
                        "technologies": ["Water & Marine Power"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "NE": {
        "state_code": "NE",
        "state_name": "Nebraska",
        "gdp_billions": 179,
        "rank": 35,
        "regulatory_body": "Nebraska Power Review Board (100% Public Power State) / SPP",
        "utilities": [
            {
                "name": "Nebraska Public Power District",
                "short_name": "NPPD",
                "org_type": "utility",
                "sub_type": "Public Power District",
                "parent_holding_company": "NPPD Board of Directors",
                "website": "https://www.nppd.com",
                "domain": "nppd.com",
                "city": "Columbus",
                "state": "NE",
                "zip_code": "68601",
                "service_territory": "84 of Nebraska's 93 counties (serving 600,000 Nebraskans directly and through wholesale public power)",
                "description": "Nebraska's largest electric utility (Nebraska is the only state in the nation where all electric utilities are 100% publicly owned), leader in clean hydrogen partnerships.",
                "logo_domain": "nppd.com",
                "founded_year": 1970,
                "programs": [
                    {
                        "name": "NPPD Monolith Materials Clean Hydrogen & Decarbonization Hub",
                        "program_type": "innovation",
                        "description": "Landmark partnership with Monolith Materials (Olive Creek plant) for methane pyrolysis converting natural gas into clean carbon black and turquoise hydrogen.",
                        "url": "https://www.nppd.com/cleanenergy",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "NPPD-H2-PYRO-2026",
                        "name": "NPPD Clean Turquoise Hydrogen & Grid Integration RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 40000000.0,
                        "max_per_award": 15000000.0,
                        "short_description": "Procurement of high-voltage transmission substation equipment and clean hydrogen co-firing testing at Sheldon Station.",
                        "service_territory": "Hallam / Lancaster County / Eastern Nebraska",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.nppd.com/suppliers",
                        "year": 2026,
                        "keywords": "Monolith Materials, turquoise hydrogen, methane pyrolysis, carbon black, Sheldon Station, NPPD",
                        "technologies": ["Hydrogen & Clean Fuels", "Carbon Capture & Management (CCUS)", "Industrial Decarbonization"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"],
                        "fuels": ["Hydrogen", "Electricity", "Natural Gas"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "NPPD-AWD-2025-01",
                        "recipient_name": "Monolith Materials, Inc.",
                        "recipient_type": "company",
                        "project_title": "Commercial Methane Pyrolysis Olive Creek Phase II Clean Hydrogen Facility Integration",
                        "award_amount": 14800000.0,
                        "year": 2025,
                        "recipient_city": "Hallam",
                        "recipient_state": "NE",
                        "latitude": 40.5367,
                        "longitude": -96.7878,
                        "pi_name": "Rob Hanson",
                        "opportunity_sol_num": "NPPD-H2-PYRO-2026",
                        "technologies": ["Hydrogen & Clean Fuels", "Industrial Decarbonization"],
                        "sectors": ["Industry & Manufacturing", "Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Omaha Public Power District",
                "short_name": "OPPD",
                "org_type": "utility",
                "sub_type": "Public Power District",
                "parent_holding_company": "OPPD Board of Directors",
                "website": "https://www.oppd.com",
                "domain": "oppd.com",
                "city": "Omaha",
                "state": "NE",
                "zip_code": "68102",
                "service_territory": "Omaha metropolitan area and 13 southeastern Nebraska counties",
                "description": "Publicly owned electric utility serving more than 400,000 customer-owners across 5,000 square miles in southeast Nebraska with a Net-Zero Carbon by 2050 target.",
                "logo_domain": "oppd.com",
                "founded_year": 1946,
                "programs": [
                    {
                        "name": "OPPD Power with Purpose Clean Energy Program",
                        "program_type": "deployment",
                        "description": "Adding up to 600MW of utility-scale solar and up to 600MW of modern dual-fuel natural gas and battery storage.",
                        "url": "https://www.oppd.com/power-with-purpose",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "OPPD-PWP-SOLAR-2026",
                        "name": "OPPD Power with Purpose Utility Solar & Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 35000000.0,
                        "max_per_award": 12000000.0,
                        "short_description": "Procurement of utility-scale solar photovoltaic facilities and battery energy storage across Saunders and Douglas counties.",
                        "service_territory": "Greater Omaha / Saunders & Douglas Counties",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.oppd.com/suppliers",
                        "year": 2026,
                        "keywords": "Power with Purpose, public power, solar, battery storage, OPPD, Omaha",
                        "technologies": ["Solar PV", "Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Solar", "Storage & Chemical", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "OPPD-AWD-2024-01",
                        "recipient_name": "NextEra Energy Resources",
                        "recipient_type": "company",
                        "project_title": "Platteview 81MW Utility Solar Facility in Saunders County for OPPD Grid",
                        "award_amount": 11500000.0,
                        "year": 2024,
                        "recipient_city": "Yutan",
                        "recipient_state": "NE",
                        "latitude": 41.2464,
                        "longitude": -96.3986,
                        "pi_name": "Rebecca Kujawa",
                        "opportunity_sol_num": "OPPD-PWP-SOLAR-2026",
                        "technologies": ["Solar PV"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "DC": {
        "state_code": "DC",
        "state_name": "District of Columbia",
        "gdp_billions": 174,
        "rank": 36,
        "regulatory_body": "Public Service Commission of the District of Columbia (DC PSC) / PJM",
        "utilities": [
            {
                "name": "Potomac Electric Power Company (District of Columbia)",
                "short_name": "Pepco DC",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Exelon",
                "website": "https://www.pepco.com",
                "domain": "pepco.com",
                "city": "Washington",
                "state": "DC",
                "zip_code": "20068",
                "service_territory": "Entire District of Columbia",
                "description": "Electric utility providing transmission and distribution service to more than 300,000 customers in the nation's capital, operating under DC's 100% Renewable Portfolio Standard by 2032.",
                "logo_domain": "pepco.com",
                "founded_year": 1896,
                "programs": [
                    {
                        "name": "Pepco DC Climate Action & Urban Microgrid Program",
                        "program_type": "innovation",
                        "description": "Underground DC Power Line (DC PLUG) modernization, urban community microgrids (St. Elizabeths East Campus), and high-density EV charging hubs.",
                        "url": "https://www.pepco.com/cleanenergy",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "PEPCODC-URBAN-MICRO-2026",
                        "name": "Pepco DC Urban Resiliency & Community Microgrid RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "grant",
                        "total_funding": 25000000.0,
                        "max_per_award": 6000000.0,
                        "short_description": "Competitive solicitation for urban solar canopies, battery energy storage, and smart microgrid controllers at critical municipal and hospital hubs in Washington DC.",
                        "service_territory": "District of Columbia",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.pepco.com/suppliers",
                        "year": 2026,
                        "keywords": "urban microgrid, DC PLUG, community solar, battery storage, Pepco DC, Washington",
                        "technologies": ["Microgrids & Resilience", "Solar PV", "Energy Storage", "EV Charging & Infrastructure"],
                        "sectors": ["Government & Municipal", "Electric Grid & Utility", "Commercial"],
                        "fuels": ["Electricity", "Solar", "Storage & Chemical"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "PEPCODC-AWD-2025-01",
                        "recipient_name": "Ameresco, Inc.",
                        "recipient_type": "company",
                        "project_title": "St. Elizabeths East Campus Clean Microgrid with Rooftop Solar and Battery Storage",
                        "award_amount": 5800000.0,
                        "year": 2025,
                        "recipient_city": "Washington",
                        "recipient_state": "DC",
                        "latitude": 38.9072,
                        "longitude": -77.0369,
                        "pi_name": "George Sakellaris",
                        "opportunity_sol_num": "PEPCODC-URBAN-MICRO-2026",
                        "technologies": ["Microgrids & Resilience", "Solar PV", "Energy Storage"],
                        "sectors": ["Government & Municipal", "Electric Grid & Utility"]
                    }
                ]
            }
        ]
    }
}
