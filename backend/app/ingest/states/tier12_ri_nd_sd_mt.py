"""Tier 12 States (Ranks 45-48): Rhode Island, North Dakota, South Dakota, Montana."""

TIER12_DATA = {
    "RI": {
        "state_code": "RI",
        "state_name": "Rhode Island",
        "gdp_billions": 77,
        "rank": 45,
        "regulatory_body": "Rhode Island Public Utilities Commission (RIPUC) / ISO-NE",
        "utilities": [
            {
                "name": "Rhode Island Energy",
                "short_name": "RI Energy",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "PPL Corporation",
                "website": "https://www.rienergy.com",
                "domain": "rienergy.com",
                "city": "Providence",
                "state": "RI",
                "zip_code": "02903",
                "service_territory": "Entire State of Rhode Island (Providence, Newport, Warwick, Cranston)",
                "description": "PPL Corporation electric and gas utility serving more than 780,000 customers in Rhode Island, operating under the state's 100% Renewable Electricity by 2033 law.",
                "logo_domain": "rienergy.com",
                "founded_year": 2022,
                "programs": [
                    {
                        "name": "Rhode Island Energy Future of Heat & Offshore Wind Grid Hub",
                        "program_type": "innovation",
                        "description": "Revolution Wind and Block Island Wind Farm interconnection, clean heat/geothermal pilots, and battery storage.",
                        "url": "https://www.rienergy.com/clean-energy",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "RIE-OSW-STORAGE-2026",
                        "name": "Rhode Island Energy Offshore Wind Interconnection & Battery Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 30000000.0,
                        "max_per_award": 10000000.0,
                        "short_description": "Procurement of onshore substation grid-forming battery storage and advanced voltage control systems supporting Revolution Wind interconnection.",
                        "service_territory": "Narragansett Bay / Providence & South County",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.rienergy.com/suppliers",
                        "year": 2026,
                        "keywords": "offshore wind, Revolution Wind, BESS, Block Island, Rhode Island Energy, Providence",
                        "technologies": ["Offshore Wind", "Energy Storage", "Power Electronics & Inverters"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Wind", "Storage & Chemical", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "RIE-AWD-2025-01",
                        "recipient_name": "Ørsted North America",
                        "recipient_type": "company",
                        "project_title": "Revolution Wind Onshore Substation Synchronous Condenser and Dynamic Filter Integration",
                        "award_amount": 11200000.0,
                        "year": 2025,
                        "recipient_city": "Providence",
                        "recipient_state": "RI",
                        "latitude": 41.8240,
                        "longitude": -71.4128,
                        "pi_name": "David Hardy",
                        "opportunity_sol_num": "RIE-OSW-STORAGE-2026",
                        "technologies": ["Offshore Wind", "Power Electronics & Inverters"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "ND": {
        "state_code": "ND",
        "state_name": "North Dakota",
        "gdp_billions": 74,
        "rank": 46,
        "regulatory_body": "North Dakota Public Service Commission (ND PSC) / MISO / SPP",
        "utilities": [
            {
                "name": "Basin Electric Power Cooperative",
                "short_name": "Basin Electric",
                "org_type": "utility",
                "sub_type": "Generation & Transmission Cooperative",
                "parent_holding_company": "Basin Electric Member Cooperatives",
                "website": "https://www.basinelectric.com",
                "domain": "basinelectric.com",
                "city": "Bismarck",
                "state": "ND",
                "zip_code": "58503",
                "service_territory": "9-state region in Northern Great Plains (North Dakota, South Dakota, Montana, Wyoming, Colorado, Nebraska, Minnesota, Iowa, New Mexico)",
                "description": "One of the nation's largest generation and transmission cooperatives, serving 3 million consumers across 141 member distribution cooperatives, pioneer in CCUS and wind energy.",
                "logo_domain": "basinelectric.com",
                "founded_year": 1961,
                "programs": [
                    {
                        "name": "Basin Electric Great Plains Synfuels & CCUS Innovation Program",
                        "program_type": "innovation",
                        "description": "Operating the Dakota Gasification Great Plains plant capturing 2+ million metric tons of CO2 annually (longest-running commercial CCUS project in North America) and testing hydrogen.",
                        "url": "https://www.basinelectric.com/about-us/carbon-capture",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "BASIN-CCUS-SYN-2026",
                        "name": "Basin Electric Carbon Dioxide Sequestration & Clean Hydrogen Pilot RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 40000000.0,
                        "max_per_award": 15000000.0,
                        "short_description": "Procurement of deep geological CO2 injection monitoring systems, clean hydrogen extraction, and synthetic fuel optimization in Mercer County, ND.",
                        "service_territory": "Beulah / Mercer County / North Dakota",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.basinelectric.com/procurement",
                        "year": 2026,
                        "keywords": "CCUS, Great Plains Synfuels, carbon capture, enhanced oil recovery, synthetic gas, Basin Electric",
                        "technologies": ["Carbon Capture & Management (CCUS)", "Hydrogen & Clean Fuels", "Industrial Decarbonization"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"],
                        "fuels": ["Hydrogen", "Natural Gas", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "BASIN-AWD-2024-01",
                        "recipient_name": "University of North Dakota Energy & Environmental Research Center (EERC)",
                        "recipient_type": "university",
                        "project_title": "Plains CO2 Reduction (PCOR) Partnership Deep Saline Formation Carbon Sequestration Validation",
                        "award_amount": 12800000.0,
                        "year": 2024,
                        "recipient_city": "Grand Forks",
                        "recipient_state": "ND",
                        "latitude": 47.9253,
                        "longitude": -97.0329,
                        "pi_name": "Charles Gorecki",
                        "opportunity_sol_num": "BASIN-CCUS-SYN-2026",
                        "technologies": ["Carbon Capture & Management (CCUS)"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"]
                    }
                ]
            }
        ]
    },
    "SD": {
        "state_code": "SD",
        "state_name": "South Dakota",
        "gdp_billions": 72,
        "rank": 47,
        "regulatory_body": "South Dakota Public Utilities Commission (SD PUC) / SPP / MISO",
        "utilities": [
            {
                "name": "Black Hills Power (South Dakota)",
                "short_name": "Black Hills Energy SD",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Black Hills Corporation",
                "website": "https://www.blackhillsenergy.com",
                "domain": "blackhillsenergy.com",
                "city": "Rapid City",
                "state": "SD",
                "zip_code": "57701",
                "service_territory": "Western South Dakota (Black Hills region, Rapid City, Sturgis, Spearfish)",
                "description": "Black Hills Corp operating company providing electricity to 74,000 customers in western South Dakota and northeast Wyoming.",
                "logo_domain": "blackhillsenergy.com",
                "founded_year": 1883,
                "programs": [
                    {
                        "name": "Black Hills Energy Renewable Ready & Resilient Grid Program",
                        "program_type": "deployment",
                        "description": "Cornette Converter Station HVDC tie modernization and utility solar+storage expansion.",
                        "url": "https://www.blackhillsenergy.com/sustainability",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "BHESD-HVDC-TIE-2026",
                        "name": "Black Hills SD Rapid City HVDC East-West Intertie Modernization RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 20000000.0,
                        "max_per_award": 6000000.0,
                        "short_description": "Procurement of high-voltage solid-state DC converter valves and dynamic power flow controllers bridging the Western and Eastern Interconnections.",
                        "service_territory": "Rapid City / Black Hills",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.blackhillsenergy.com/suppliers",
                        "year": 2026,
                        "keywords": "HVDC, East-West Intertie, power electronics, converter station, Black Hills Energy, Rapid City",
                        "technologies": ["Power Electronics & Inverters", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "BHESD-AWD-2024-01",
                        "recipient_name": "Hitachi Energy USA",
                        "recipient_type": "company",
                        "project_title": "HVDC Classic Converter Valve Modernization for Rapid City East-West Intertie Facility",
                        "award_amount": 5800000.0,
                        "year": 2024,
                        "recipient_city": "Raleigh",
                        "recipient_state": "NC",
                        "latitude": 35.7796,
                        "longitude": -78.6382,
                        "pi_name": "Anthony Allard",
                        "opportunity_sol_num": "BHESD-HVDC-TIE-2026",
                        "technologies": ["Power Electronics & Inverters", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "MT": {
        "state_code": "MT",
        "state_name": "Montana",
        "gdp_billions": 71,
        "rank": 48,
        "regulatory_body": "Montana Public Service Commission (MT PSC)",
        "utilities": [
            {
                "name": "NorthWestern Energy (Montana)",
                "short_name": "NorthWestern MT",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "NorthWestern Energy Group",
                "website": "https://www.northwesternenergy.com",
                "domain": "northwesternenergy.com",
                "city": "Butte / Helena",
                "state": "MT",
                "zip_code": "59701",
                "service_territory": "Western and Central Montana (Butte, Bozeman, Missoula, Helena, Great Falls, Billings)",
                "description": "Providing electricity to 395,000 customers and natural gas to 207,000 customers across Montana, delivering 60%+ carbon-free electricity through hydro, wind, and storage.",
                "logo_domain": "northwesternenergy.com",
                "founded_year": 1912,
                "programs": [
                    {
                        "name": "NorthWestern Montana Hydro Modernization & Battery Storage Program",
                        "program_type": "innovation",
                        "description": "Modernizing historic Missouri and Madison River hydroelectric facilities and integrating utility-scale battery storage (Yellowstone County Generating Station).",
                        "url": "https://www.northwesternenergy.com/clean-energy",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "NWEMT-HYDRO-STORAGE-2026",
                        "name": "NorthWestern MT Hydro Plant Modernization & Cold-Climate Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 25000000.0,
                        "max_per_award": 8000000.0,
                        "short_description": "Procurement of digital hydro governors, fish-friendly turbine runners, and cold-climate battery storage systems on the Missouri River hydro system.",
                        "service_territory": "Missouri River Valley / Great Falls & Helena",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.northwesternenergy.com/suppliers",
                        "year": 2026,
                        "keywords": "hydropower, Missouri River, fish-friendly turbine, cold-climate storage, NorthWestern Energy, Butte",
                        "technologies": ["Water & Marine Power", "Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Hydro & Marine", "Storage & Chemical", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "NWEMT-AWD-2024-01",
                        "recipient_name": "Andritz Hydro Corp.",
                        "recipient_type": "company",
                        "project_title": "Digital Hydro Automation and Turbine Efficiency Upgrades for Ryan Dam on Missouri River",
                        "award_amount": 6900000.0,
                        "year": 2024,
                        "recipient_city": "Charlotte",
                        "recipient_state": "NC",
                        "latitude": 35.2271,
                        "longitude": -80.8431,
                        "pi_name": "Klaus Preyler",
                        "opportunity_sol_num": "NWEMT-HYDRO-STORAGE-2026",
                        "technologies": ["Water & Marine Power"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    }
}
