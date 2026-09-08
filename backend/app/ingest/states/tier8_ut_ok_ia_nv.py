"""Tier 8 States (Ranks 29-32): Utah, Oklahoma, Iowa, Nevada."""

TIER8_DATA = {
    "UT": {
        "state_code": "UT",
        "state_name": "Utah",
        "gdp_billions": 272,
        "rank": 29,
        "regulatory_body": "Public Service Commission of Utah (PSC Utah)",
        "utilities": [
            {
                "name": "Rocky Mountain Power (Utah)",
                "short_name": "Rocky Mountain Power",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Berkshire Hathaway Energy",
                "website": "https://www.rockymountainpower.net",
                "domain": "rockymountainpower.net",
                "city": "Salt Lake City",
                "state": "UT",
                "zip_code": "84116",
                "service_territory": "Wasatch Front, Salt Lake City, Ogden, Provo, Park City, and rural Utah",
                "description": "PacifiCorp operating company providing electric service to more than 920,000 customers in Utah (plus Idaho and Wyoming).",
                "logo_domain": "rockymountainpower.net",
                "founded_year": 1912,
                "programs": [
                    {
                        "name": "Rocky Mountain Power Utah Clean Energy & VPP Wattsmart",
                        "program_type": "innovation",
                        "description": "Wattsmart battery program (national benchmark with 3,000+ customer Sonnen residential batteries aggregated for grid frequency response) and Advanced Nuclear TerraPower partnership.",
                        "url": "https://www.rockymountainpower.net/savings-energy-choices/wattsmart-battery-program.html",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "RMP-WATTSMART-VPP-2026",
                        "name": "Rocky Mountain Power Wattsmart Battery VPP Expansion RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "grant",
                        "total_funding": 25000000.0,
                        "max_per_award": 6000000.0,
                        "short_description": "Competitive incentives for aggregating residential, multi-family, and commercial battery storage into Rocky Mountain Power's autonomous VPP dispatch system.",
                        "service_territory": "Wasatch Front / Salt Lake City",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.rockymountainpower.net/suppliers",
                        "year": 2026,
                        "keywords": "Wattsmart, VPP, residential battery storage, Sonnen, frequency response, Rocky Mountain Power",
                        "technologies": ["Energy Storage", "Non-Wires Solutions (NWS)", "AI, Computing & Energy Cyber"],
                        "sectors": ["Residential", "Commercial", "Electric Grid & Utility"],
                        "fuels": ["Electricity", "Storage & Chemical"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "RMP-AWD-2024-01",
                        "recipient_name": "Sonnen, Inc.",
                        "recipient_type": "company",
                        "project_title": "Wattsmart Smart Residential Battery Virtual Power Plant Dispatch System Expansion",
                        "award_amount": 7500000.0,
                        "year": 2024,
                        "recipient_city": "Salt Lake City",
                        "recipient_state": "UT",
                        "latitude": 40.7608,
                        "longitude": -111.8910,
                        "pi_name": "Blake Richetta",
                        "opportunity_sol_num": "RMP-WATTSMART-VPP-2026",
                        "technologies": ["Energy Storage", "Non-Wires Solutions (NWS)"],
                        "sectors": ["Residential", "Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Intermountain Power Agency",
                "short_name": "IPA",
                "org_type": "utility",
                "sub_type": "Municipal Public Power Agency",
                "parent_holding_company": "IPA Member Municipalities",
                "website": "https://www.ipautah.com",
                "domain": "ipautah.com",
                "city": "South Jordan / Delta",
                "state": "UT",
                "zip_code": "84095",
                "service_territory": "IPP Generating Station at Delta, Utah, providing wholesale power to Utah and Southern California (LADWP)",
                "description": "Political subdivision of Utah owning the Intermountain Power Project (IPP), currently executing the landmark IPP Renewed 840MW green hydrogen conversion project.",
                "logo_domain": "ipautah.com",
                "founded_year": 1977,
                "programs": [
                    {
                        "name": "IPA IPP Renewed Green Hydrogen & Salt Cavern Storage Hub",
                        "program_type": "innovation",
                        "description": "World's largest green hydrogen project, featuring 220MW electrolyzers, salt cavern underground hydrogen storage, and 840MW hydrogen-capable turbines at Delta, UT.",
                        "url": "https://www.ipautah.com/ipp-renewed/",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "IPA-H2-CAVERN-2026",
                        "name": "IPA Salt Cavern Geological Hydrogen Storage & Compression RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 80000000.0,
                        "max_per_award": 35000000.0,
                        "short_description": "Procurement of high-pressure hydrogen compressors, deep salt dome cavern monitoring systems, and electrolyzer integration equipment at Delta, Utah.",
                        "service_territory": "Millard County / Delta, Utah",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.ipautah.com/bids",
                        "year": 2026,
                        "keywords": "IPP Renewed, green hydrogen, salt cavern, underground hydrogen storage, Delta Utah, IPA",
                        "technologies": ["Hydrogen & Clean Fuels", "Energy Storage", "Industrial Decarbonization"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"],
                        "fuels": ["Hydrogen", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "IPA-AWD-2025-01",
                        "recipient_name": "Chevron New Energies / ACES Delta",
                        "recipient_type": "company",
                        "project_title": "Advanced Clean Energy Storage (ACES Delta) Salt Cavern Hydrogen Storage Hub",
                        "award_amount": 32000000.0,
                        "year": 2025,
                        "recipient_city": "Delta",
                        "recipient_state": "UT",
                        "latitude": 39.3522,
                        "longitude": -112.5769,
                        "pi_name": "Austin Knight",
                        "opportunity_sol_num": "IPA-H2-CAVERN-2026",
                        "technologies": ["Hydrogen & Clean Fuels", "Energy Storage"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"]
                    }
                ]
            }
        ]
    },
    "OK": {
        "state_code": "OK",
        "state_name": "Oklahoma",
        "gdp_billions": 242,
        "rank": 30,
        "regulatory_body": "Oklahoma Corporation Commission (OCC) / SPP",
        "utilities": [
            {
                "name": "Oklahoma Gas and Electric",
                "short_name": "OG&E",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "OGE Energy Corp.",
                "website": "https://www.oge.com",
                "domain": "oge.com",
                "city": "Oklahoma City",
                "state": "OK",
                "zip_code": "73102",
                "service_territory": "Oklahoma City metropolitan area, Fort Smith (AR), and central/western Oklahoma (30,000 sq miles)",
                "description": "Oklahoma's oldest and largest electric utility, serving more than 890,000 customers in Oklahoma and western Arkansas.",
                "logo_domain": "oge.com",
                "founded_year": 1902,
                "programs": [
                    {
                        "name": "OG&E Grid Modernization & Severe Weather Automation",
                        "program_type": "deployment",
                        "description": "Comprehensive distribution automation, storm-resilient automated reclosers (Tornado Alley hardening), and smart grid sensors.",
                        "url": "https://www.oge.com/wps/portal/oge/about-us/grid-enhancements",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "OGE-GRID-RESIL-2026",
                        "name": "OG&E Severe Storm Hardening & Smart Substation Automation RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 25000000.0,
                        "max_per_award": 6000000.0,
                        "short_description": "Procurement of tornado-hardened automated line switches, overhead optical sensors, and self-healing distribution grid systems.",
                        "service_territory": "Oklahoma City Metro & Central Oklahoma",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.oge.com/suppliers",
                        "year": 2026,
                        "keywords": "grid hardening, severe storm, automation, FLISR, OG&E, Oklahoma City",
                        "technologies": ["Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "OGE-AWD-2024-01",
                        "recipient_name": "S&C Electric Company",
                        "recipient_type": "company",
                        "project_title": "TripSaver II Cutout-Mounted Automated Reclosers for Severe Weather Rural Feeders",
                        "award_amount": 5400000.0,
                        "year": 2024,
                        "recipient_city": "Chicago",
                        "recipient_state": "IL",
                        "latitude": 41.8781,
                        "longitude": -87.6298,
                        "pi_name": "Anders Sjoelin",
                        "opportunity_sol_num": "OGE-GRID-RESIL-2026",
                        "technologies": ["Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "IA": {
        "state_code": "IA",
        "state_name": "Iowa",
        "gdp_billions": 248,
        "rank": 31,
        "regulatory_body": "Iowa Utilities Commission (IUC) / MISO",
        "utilities": [
            {
                "name": "MidAmerican Energy",
                "short_name": "MidAmerican",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Berkshire Hathaway Energy",
                "website": "https://www.midamericanenergy.com",
                "domain": "midamericanenergy.com",
                "city": "Des Moines",
                "state": "IA",
                "zip_code": "50309",
                "service_territory": "Des Moines, Cedar Rapids, Quad Cities, Sioux City, Council Bluffs, Iowa City",
                "description": "Iowa's largest energy provider, serving 813,000 electric and 789,000 natural gas customers, delivering 88%+ renewable energy annually through massive wind leadership.",
                "logo_domain": "midamericanenergy.com",
                "founded_year": 1995,
                "programs": [
                    {
                        "name": "MidAmerican GreenAdvantage & WindPrime Technology Program",
                        "program_type": "innovation",
                        "description": "WindPrime initiative funding advanced wind turbine repowering, small modular reactor (SMR) studies, and grid-scale battery storage.",
                        "url": "https://www.midamericanenergy.com/green-advantage",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "MIDAM-WINDPRIME-STORAGE-2026",
                        "name": "MidAmerican Energy Wind Integration & Battery Energy Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 50000000.0,
                        "max_per_award": 20000000.0,
                        "short_description": "Procurement of 200MW utility-scale battery energy storage systems and advanced wind turbine curtailment mitigation controls.",
                        "service_territory": "Central & Western Iowa",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.midamericanenergy.com/suppliers",
                        "year": 2026,
                        "keywords": "WindPrime, wind integration, BESS, battery storage, GreenAdvantage, MidAmerican, Des Moines",
                        "technologies": ["Onshore Wind", "Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Wind", "Storage & Chemical", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "MIDAM-AWD-2025-01",
                        "recipient_name": "Tesla Energy Operations",
                        "recipient_type": "company",
                        "project_title": "Megapack Utility Battery Storage for Iowa Wind Fleet Smoothing and Capacity Delivery",
                        "award_amount": 18500000.0,
                        "year": 2025,
                        "recipient_city": "Des Moines",
                        "recipient_state": "IA",
                        "latitude": 41.5868,
                        "longitude": -93.6250,
                        "pi_name": "Mike Snyder",
                        "opportunity_sol_num": "MIDAM-WINDPRIME-STORAGE-2026",
                        "technologies": ["Energy Storage", "Onshore Wind"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "NV": {
        "state_code": "NV",
        "state_name": "Nevada",
        "gdp_billions": 239,
        "rank": 32,
        "regulatory_body": "Public Utilities Commission of Nevada (PUCN)",
        "utilities": [
            {
                "name": "NV Energy",
                "short_name": "NV Energy",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Berkshire Hathaway Energy",
                "website": "https://www.nvenergy.com",
                "domain": "nvenergy.com",
                "city": "Las Vegas / Reno",
                "state": "NV",
                "zip_code": "89146",
                "service_territory": "Southern Nevada (Las Vegas, Henderson) and Northern Nevada (Reno, Sparks, Carson City)",
                "description": "Operating as Nevada Power Company in the south and Sierra Pacific Power Company in the north, providing power to 1.5 million customers across 45,500 square miles in Nevada.",
                "logo_domain": "nvenergy.com",
                "founded_year": 1906,
                "programs": [
                    {
                        "name": "NV Energy Greenlink Nevada & Solar-Plus-Storage Plan",
                        "program_type": "innovation",
                        "description": "$2.5B Greenlink transmission superhighway unlocking Nevada's vast solar and geothermal resources, paired with 1,000MW+ battery energy storage.",
                        "url": "https://www.nvenergy.com/cleanenergy/greenlink",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "NVE-GREENLINK-BESS-2026",
                        "name": "NV Energy Greenlink Nevada Solar + Geothermal + Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 75000000.0,
                        "max_per_award": 30000000.0,
                        "short_description": "Competitive procurement of 300MW/1,200MWh battery energy storage and enhanced geothermal systems (EGS) interconnected to the Greenlink transmission corridor.",
                        "service_territory": "Clark, Washoe, and White Pine Counties",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.nvenergy.com/suppliers",
                        "year": 2026,
                        "keywords": "Greenlink Nevada, geothermal, EGS, BESS, solar-plus-storage, NV Energy, Las Vegas",
                        "technologies": ["Geothermal Energy", "Energy Storage", "Solar PV", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Geothermal", "Solar", "Storage & Chemical", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "NVE-AWD-2025-01",
                        "recipient_name": "Fervo Energy",
                        "recipient_type": "company",
                        "project_title": "Commercial Enhanced Geothermal System (EGS) Power Integration for Greenlink Grid Delivery",
                        "award_amount": 28000000.0,
                        "year": 2025,
                        "recipient_city": "Reno",
                        "recipient_state": "NV",
                        "latitude": 39.5296,
                        "longitude": -119.8138,
                        "pi_name": "Tim Latimer",
                        "opportunity_sol_num": "NVE-GREENLINK-BESS-2026",
                        "technologies": ["Geothermal Energy"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    }
}
