"""Tier 5 States (Ranks 17-20): Indiana, Arizona, Minnesota, Wisconsin."""

TIER5_DATA = {
    "IN": {
        "state_code": "IN",
        "state_name": "Indiana",
        "gdp_billions": 497,
        "rank": 17,
        "regulatory_body": "Indiana Utility Regulatory Commission (IURC) / MISO / PJM",
        "utilities": [
            {
                "name": "AES Indiana",
                "short_name": "AES Indiana",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "AES Corporation",
                "website": "https://www.aes-indiana.com",
                "domain": "aes-indiana.com",
                "city": "Indianapolis",
                "state": "IN",
                "zip_code": "46204",
                "service_territory": "Indianapolis metropolitan area / Marion County and surrounding areas",
                "description": "Electric utility providing retail electric service to more than 512,000 residential, commercial, and industrial customers in Indianapolis.",
                "logo_domain": "aes-indiana.com",
                "founded_year": 1926,
                "programs": [
                    {
                        "name": "AES Indiana Grid Modernization & Storage RFP",
                        "program_type": "deployment",
                        "description": "Phasing out coal at Petersburg and deploying 200MW/800MWh of battery energy storage, smart inverters, and EV fleet charging.",
                        "url": "https://www.aes-indiana.com/clean-energy",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "AESIN-BESS-PETERS-2026",
                        "name": "AES Indiana Petersburg Energy Storage Center RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 50000000.0,
                        "max_per_award": 20000000.0,
                        "short_description": "Procurement of 200MW utility-scale battery energy storage systems co-located at the retiring Petersburg Generating Station.",
                        "service_territory": "Central & Southwestern Indiana",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.aes-indiana.com/doing-business-us",
                        "year": 2026,
                        "keywords": "Petersburg, coal conversion, battery storage, BESS, AES Indiana, Indianapolis",
                        "technologies": ["Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "AESIN-AWD-2025-01",
                        "recipient_name": "Fluence Energy, Inc.",
                        "recipient_type": "company",
                        "project_title": "Gridstack Pro Utility Battery Storage Deployment at Petersburg Center",
                        "award_amount": 19500000.0,
                        "year": 2025,
                        "recipient_city": "Arlington",
                        "recipient_state": "VA",
                        "latitude": 38.8799,
                        "longitude": -77.1067,
                        "pi_name": "Julian Nebreda",
                        "opportunity_sol_num": "AESIN-BESS-PETERS-2026",
                        "technologies": ["Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Duke Energy Indiana",
                "short_name": "Duke Indiana",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Duke Energy",
                "website": "https://www.duke-energy.com",
                "domain": "duke-energy.com",
                "city": "Plainfield",
                "state": "IN",
                "zip_code": "46168",
                "service_territory": "Central, North Central, and Southern Indiana (serving 69 of 92 counties)",
                "description": "Indiana's largest electric utility, serving approximately 890,000 electric customers across 23,000 square miles.",
                "logo_domain": "duke-energy.com",
                "founded_year": 1902,
                "programs": [
                    {
                        "name": "Duke Energy Indiana Crane Naval Base Microgrid Pilot",
                        "program_type": "innovation",
                        "description": "Collaborative military microgrid with the Department of Defense at Naval Support Activity Crane, featuring 17MW solar and battery storage.",
                        "url": "https://www.duke-energy.com/our-company/clean-energy",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "DEI-CRANE-MICRO-2026",
                        "name": "Duke Energy Indiana Naval Defense & Critical Facility Microgrid RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 25000000.0,
                        "max_per_award": 7500000.0,
                        "short_description": "Procurement of microgrid fast-islanding controllers, cyber-hardened substations, and battery storage for defense installations.",
                        "service_territory": "Southwestern Indiana / NSA Crane",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.duke-energy.com/suppliers",
                        "year": 2026,
                        "keywords": "military microgrid, NSA Crane, defense resilience, cyber hardening, Duke Indiana",
                        "technologies": ["Microgrids & Resilience", "AI, Computing & Energy Cyber", "Energy Storage", "Solar PV"],
                        "sectors": ["Defense & National Security", "Electric Grid & Utility"],
                        "fuels": ["Electricity", "Solar"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "DEI-AWD-2024-01",
                        "recipient_name": "Lockheed Martin Energy",
                        "recipient_type": "company",
                        "project_title": "GridStar Microgrid Controller and Advanced Cyber Armor for NSA Crane",
                        "award_amount": 6800000.0,
                        "year": 2024,
                        "recipient_city": "Bethesda",
                        "recipient_state": "MD",
                        "latitude": 38.9847,
                        "longitude": -77.0947,
                        "pi_name": "James Taiclet",
                        "opportunity_sol_num": "DEI-CRANE-MICRO-2026",
                        "technologies": ["Microgrids & Resilience", "AI, Computing & Energy Cyber"],
                        "sectors": ["Defense & National Security", "Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "AZ": {
        "state_code": "AZ",
        "state_name": "Arizona",
        "gdp_billions": 508,
        "rank": 18,
        "regulatory_body": "Arizona Corporation Commission (ACC)",
        "utilities": [
            {
                "name": "Arizona Public Service",
                "short_name": "APS",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Pinnacle West Capital",
                "website": "https://www.aps.com",
                "domain": "aps.com",
                "city": "Phoenix",
                "state": "AZ",
                "zip_code": "85004",
                "service_territory": "Phoenix metropolitan area and 11 of Arizona's 15 counties",
                "description": "Arizona's largest and longest-serving electric company, providing power to 1.4 million homes and businesses with a 100% clean, carbon-free electricity goal by 2050.",
                "logo_domain": "aps.com",
                "founded_year": 1886,
                "programs": [
                    {
                        "name": "APS Solar Innovation & Palo Verde Clean Hydrogen Center",
                        "program_type": "innovation",
                        "description": "DOE-supported clean hydrogen production at the Palo Verde Nuclear Generating Station (nation's largest nuclear plant), coupled with solar+storage microgrids.",
                        "url": "https://www.aps.com/en/About/Our-Energy/Clean-Energy-Commitment",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "APS-PV-H2-2026",
                        "name": "APS Palo Verde Nuclear-to-Hydrogen Demonstration RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "grant",
                        "total_funding": 35000000.0,
                        "max_per_award": 12000000.0,
                        "short_description": "Competitive solicitation for high-temperature steam electrolysis (SOEC), clean hydrogen compression, and turbine co-firing using Palo Verde clean nuclear power.",
                        "service_territory": "Palo Verde Generating Station / Maricopa County",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.aps.com/suppliers",
                        "year": 2026,
                        "keywords": "nuclear hydrogen, Palo Verde, SOEC, clean hydrogen, Pinnacle West, APS",
                        "technologies": ["Hydrogen & Clean Fuels", "Nuclear & Advanced SMRs", "Fuel Cells"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"],
                        "fuels": ["Nuclear", "Hydrogen", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "APS-AWD-2025-01",
                        "recipient_name": "Idaho National Laboratory (INL)",
                        "recipient_type": "lab",
                        "project_title": "High-Temperature Steam Electrolysis (HTSE) Integration and Dynamic Dispatch with Palo Verde Nuclear Unit",
                        "award_amount": 10500000.0,
                        "year": 2025,
                        "recipient_city": "Idaho Falls",
                        "recipient_state": "ID",
                        "latitude": 43.4927,
                        "longitude": -112.0401,
                        "pi_name": "Dr. Shannon Bragg-Sitton",
                        "opportunity_sol_num": "APS-PV-H2-2026",
                        "technologies": ["Hydrogen & Clean Fuels", "Nuclear & Advanced SMRs"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Salt River Project",
                "short_name": "SRP",
                "org_type": "utility",
                "sub_type": "Community Public Power District",
                "parent_holding_company": "SRP Board of Governors",
                "website": "https://www.srpnet.com",
                "domain": "srpnet.com",
                "city": "Tempe",
                "state": "AZ",
                "zip_code": "85281",
                "service_territory": "Phoenix East Valley, Scottsdale, Tempe, Mesa, Chandler, Gilbert",
                "description": "Community-based, not-for-profit public power utility providing electricity to over 1.1 million customers in the greater Phoenix metropolitan area.",
                "logo_domain": "srpnet.com",
                "founded_year": 1903,
                "programs": [
                    {
                        "name": "SRP Innovation Research & Storage Acceleration Program",
                        "program_type": "innovation",
                        "description": "Expanding utility-scale battery storage to over 1,500MW, pumped storage hydro research, and AI-driven thermal power plant flexibility.",
                        "url": "https://www.srpnet.com/grid-water-energy/grid/energy-storage",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "SRP-BESS-ALL-2026",
                        "name": "SRP All-Source Clean Energy & Long-Duration Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 60000000.0,
                        "max_per_award": 25000000.0,
                        "short_description": "Competitive procurement of 400MW/1,600MWh battery energy storage and long-duration storage technologies to meet extreme summer desert heat peak loads.",
                        "service_territory": "Phoenix Metro / East Valley",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.srpnet.com/procurement",
                        "year": 2026,
                        "keywords": "summer peak, desert heat, BESS, LDES, battery storage, SRP, Phoenix",
                        "technologies": ["Energy Storage", "Solar PV", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Solar", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "SRP-AWD-2024-01",
                        "recipient_name": "Plus Power LLC",
                        "recipient_type": "company",
                        "project_title": "Sierra Estrella 250MW/1,000MWh Standalone Battery Storage Facility in Avondale, AZ",
                        "award_amount": 24000000.0,
                        "year": 2024,
                        "recipient_city": "The Woodlands",
                        "recipient_state": "TX",
                        "latitude": 30.1588,
                        "longitude": -95.4894,
                        "pi_name": "Brandon Keefe",
                        "opportunity_sol_num": "SRP-BESS-ALL-2026",
                        "technologies": ["Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "MN": {
        "state_code": "MN",
        "state_name": "Minnesota",
        "gdp_billions": 472,
        "rank": 19,
        "regulatory_body": "Minnesota Public Utilities Commission (MPUC) / MISO",
        "utilities": [
            {
                "name": "Northern States Power (Minnesota)",
                "short_name": "Xcel Energy MN",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Xcel Energy",
                "website": "https://www.xcelenergy.com",
                "domain": "xcelenergy.com",
                "city": "Minneapolis",
                "state": "MN",
                "zip_code": "55401",
                "service_territory": "Twin Cities metropolitan area, St. Cloud, Fargo-Moorhead corridor",
                "description": "Xcel Energy's Minnesota utility, serving 1.3 million electric and 470,000 natural gas customers, advancing Minnesota's 100% Carbon-Free Electricity by 2040 statute.",
                "logo_domain": "xcelenergy.com",
                "founded_year": 1909,
                "programs": [
                    {
                        "name": "Xcel Energy Minnesota ECO Innovation & Sherco Storage Hub",
                        "program_type": "innovation",
                        "description": "Repurposing the Sherco Coal Plant in Becker, MN into a 460MW solar hub with 10MW/1,000MWh (100-hour) Form Energy multi-day battery storage.",
                        "url": "https://www.xcelenergy.com/company/clean_energy_plan/sherco",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "XCELMN-SHERCO-LDES-2026",
                        "name": "Xcel Energy MN Sherco Multi-Day Long-Duration Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 45000000.0,
                        "max_per_award": 20000000.0,
                        "short_description": "Procurement of multi-day long-duration energy storage (LDES) and advanced high-voltage grid interconnection at the retiring Sherco coal generating station.",
                        "service_territory": "Becker / Central Minnesota",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.xcelenergy.com/suppliers",
                        "year": 2026,
                        "keywords": "Sherco, coal conversion, 100-hour battery, LDES, Form Energy, Xcel Energy MN",
                        "technologies": ["Energy Storage", "Solar PV", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Solar", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "XCELMN-AWD-2025-01",
                        "recipient_name": "Form Energy, Inc.",
                        "recipient_type": "company",
                        "project_title": "10MW/1,000MWh Multi-Day Iron-Air Battery Energy Storage System at Sherco Site",
                        "award_amount": 18000000.0,
                        "year": 2025,
                        "recipient_city": "Somerville",
                        "recipient_state": "MA",
                        "latitude": 42.3876,
                        "longitude": -71.0995,
                        "pi_name": "Mateo Jaramillo",
                        "opportunity_sol_num": "XCELMN-SHERCO-LDES-2026",
                        "technologies": ["Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Great River Energy",
                "short_name": "Great River Energy",
                "org_type": "utility",
                "sub_type": "Generation & Transmission Cooperative",
                "parent_holding_company": "GRE Member Cooperatives",
                "website": "https://greatriverenergy.com",
                "domain": "greatriverenergy.com",
                "city": "Maple Grove",
                "state": "MN",
                "zip_code": "55369",
                "service_territory": "Minnesota and portions of Wisconsin (serving 27 member distribution co-ops and 1.7 million people)",
                "description": "Minnesota's largest generation and transmission cooperative, a national pioneer in long-duration iron-air battery storage (Cambridge, MN pilot).",
                "logo_domain": "greatriverenergy.com",
                "founded_year": 1999,
                "programs": [
                    {
                        "name": "Great River Energy Cambridge Multi-Day Storage & DER Innovation",
                        "program_type": "innovation",
                        "description": "First utility in the world to contract for a multi-day (100-hour) iron-air battery system (1.5MW/150MWh at Cambridge, MN).",
                        "url": "https://greatriverenergy.com/energy-resources/long-duration-battery-storage/",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "GRE-CAMBRIDGE-LDES-2026",
                        "name": "Great River Energy 100-Hour Multi-Day Battery Storage Expansion RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 18000000.0,
                        "max_per_award": 6000000.0,
                        "short_description": "Engineering, procurement, and grid validation for commercial scaling of multi-day storage assets for rural electric cooperative resilience.",
                        "service_territory": "Cambridge / East Central Minnesota",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://greatriverenergy.com",
                        "year": 2026,
                        "keywords": "100-hour battery, multi-day storage, Cambridge, cooperative, Great River Energy",
                        "technologies": ["Energy Storage", "Microgrids & Resilience"],
                        "sectors": ["Electric Grid & Utility", "Agriculture & Forestry"],
                        "fuels": ["Storage & Chemical", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "GRE-AWD-2024-01",
                        "recipient_name": "Form Energy, Inc.",
                        "recipient_type": "company",
                        "project_title": "Commercial Pilot of 1.5MW/150MWh Iron-Air Long-Duration Storage System at Cambridge Peaking Station",
                        "award_amount": 5500000.0,
                        "year": 2024,
                        "recipient_city": "Somerville",
                        "recipient_state": "MA",
                        "latitude": 42.3876,
                        "longitude": -71.0995,
                        "pi_name": "Mateo Jaramillo",
                        "opportunity_sol_num": "GRE-CAMBRIDGE-LDES-2026",
                        "technologies": ["Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "WI": {
        "state_code": "WI",
        "state_name": "Wisconsin",
        "gdp_billions": 414,
        "rank": 20,
        "regulatory_body": "Public Service Commission of Wisconsin (PSCW) / MISO",
        "utilities": [
            {
                "name": "We Energies",
                "short_name": "We Energies",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "WEC Energy Group",
                "website": "https://www.we-energies.com",
                "domain": "we-energies.com",
                "city": "Milwaukee",
                "state": "WI",
                "zip_code": "53203",
                "service_territory": "Southeastern Wisconsin (Milwaukee, Racine, Kenosha, Waukesha)",
                "description": "Wisconsin's largest utility, serving more than 1.1 million electric and 1.1 million natural gas customers in Southeastern Wisconsin.",
                "logo_domain": "we-energies.com",
                "founded_year": 1896,
                "programs": [
                    {
                        "name": "We Energies Paris & Darien Solar+Storage Center Programs",
                        "program_type": "deployment",
                        "description": "Major utility-scale battery energy storage deployment (Paris Solar-Battery Park 110MW BESS, Darien 75MW BESS).",
                        "url": "https://www.wecenergygroup.com/environment/renewable-energy.htm",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "WE-PARIS-BESS-2026",
                        "name": "We Energies Large-Scale BESS & Solar Integration Solicitations",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 55000000.0,
                        "max_per_award": 20000000.0,
                        "short_description": "Procurement of utility-scale battery energy storage systems, bi-directional inverters, and automated generation controllers across Kenosha and Walworth counties.",
                        "service_territory": "Southeastern Wisconsin / Kenosha & Walworth Counties",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.we-energies.com/suppliers",
                        "year": 2026,
                        "keywords": "Paris solar, Darien, battery storage, BESS, We Energies, Milwaukee",
                        "technologies": ["Energy Storage", "Solar PV", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Solar", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "WE-AWD-2025-01",
                        "recipient_name": "Invenergy LLC",
                        "recipient_type": "company",
                        "project_title": "Paris Solar-Battery Park 110MW/440MWh Lithium-Ion Battery Storage System",
                        "award_amount": 19000000.0,
                        "year": 2025,
                        "recipient_city": "Chicago",
                        "recipient_state": "IL",
                        "latitude": 41.8781,
                        "longitude": -87.6298,
                        "pi_name": "Michael Polsky",
                        "opportunity_sol_num": "WE-PARIS-BESS-2026",
                        "technologies": ["Energy Storage", "Solar PV"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Madison Gas and Electric",
                "short_name": "MGE",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "MGE Energy",
                "website": "https://www.mge.com",
                "domain": "mge.com",
                "city": "Madison",
                "state": "WI",
                "zip_code": "53703",
                "service_territory": "Greater Madison and Dane County",
                "description": "Public utility generating and distributing electricity to 161,000 customers and natural gas to 173,000 customers in Dane County with an Energy 2050 Net-Zero Carbon framework.",
                "logo_domain": "mge.com",
                "founded_year": 1896,
                "programs": [
                    {
                        "name": "MGE Energy 2050 Clean Technology Testbed & VPP",
                        "program_type": "innovation",
                        "description": "Collaborative research with UW-Madison for community microgrids, EV smart managed charging, and battery VPP aggregation.",
                        "url": "https://www.mge.com/clean-energy",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "MGE-VPP-TRANSIT-2026",
                        "name": "MGE Metro Transit Bus V2G & Virtual Power Plant Pilot RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "grant",
                        "total_funding": 12000000.0,
                        "max_per_award": 3500000.0,
                        "short_description": "Pilot demonstration of bidirectional V2G heavy transit bus charging, depot smart microgrid controls, and peak demand shaving in Madison.",
                        "service_territory": "Madison / Dane County",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.mge.com/suppliers",
                        "year": 2026,
                        "keywords": "V2G, electric bus, Madison Metro, VPP, smart charging, MGE",
                        "technologies": ["EV Charging & Infrastructure", "Electric Vehicles & Clean Transit", "Microgrids & Resilience"],
                        "sectors": ["Transportation", "Government & Municipal", "Electric Grid & Utility"],
                        "fuels": ["Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "MGE-AWD-2024-01",
                        "recipient_name": "University of Wisconsin-Madison (WEMPEC)",
                        "recipient_type": "university",
                        "project_title": "High-Power Bidirectional DC Fast Charging and Grid Power Quality Controller Validation",
                        "award_amount": 3100000.0,
                        "year": 2024,
                        "recipient_city": "Madison",
                        "recipient_state": "WI",
                        "latitude": 43.0731,
                        "longitude": -89.4012,
                        "pi_name": "Dr. Giri Venkataramanan",
                        "opportunity_sol_num": "MGE-VPP-TRANSIT-2026",
                        "technologies": ["Power Electronics & Inverters", "EV Charging & Infrastructure"],
                        "sectors": ["Transportation", "Electric Grid & Utility"]
                    }
                ]
            }
        ]
    }
}
