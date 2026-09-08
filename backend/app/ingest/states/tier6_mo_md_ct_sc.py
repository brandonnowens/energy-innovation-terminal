"""Tier 6 States (Ranks 21-24): Missouri, Maryland, Connecticut, South Carolina."""

TIER6_DATA = {
    "MO": {
        "state_code": "MO",
        "state_name": "Missouri",
        "gdp_billions": 422,
        "rank": 21,
        "regulatory_body": "Missouri Public Service Commission (MoPSC) / MISO / SPP",
        "utilities": [
            {
                "name": "Ameren Missouri",
                "short_name": "Ameren MO",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Ameren",
                "website": "https://www.ameren.com/missouri",
                "domain": "ameren.com",
                "city": "St. Louis",
                "state": "MO",
                "zip_code": "63103",
                "service_territory": "Eastern and Central Missouri (St. Louis metropolitan area, Jefferson City, Columbia)",
                "description": "Electric utility providing electricity to 1.2 million customers and natural gas to 134,000 customers in central and eastern Missouri.",
                "logo_domain": "ameren.com",
                "founded_year": 1902,
                "programs": [
                    {
                        "name": "Ameren Missouri Smart Energy Plan & BESS Pilots",
                        "program_type": "deployment",
                        "description": "$8.4B Smart Energy Plan modernizing distribution substations, deploying smart self-healing switches, and battery storage.",
                        "url": "https://www.ameren.com/missouri/company/smart-energy-plan",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "AMERENMO-SMART-2026",
                        "name": "Ameren Missouri Smart Substation & Distributed Battery Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 30000000.0,
                        "max_per_award": 8000000.0,
                        "short_description": "Procurement of automated distribution switches, smart grid monitoring, and localized battery storage systems across St. Louis metro.",
                        "service_territory": "Greater St. Louis Area",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.ameren.com/suppliers",
                        "year": 2026,
                        "keywords": "Smart Energy Plan, self-healing grid, BESS, St. Louis, Ameren Missouri",
                        "technologies": ["Grid Modernization & Smart Grid", "Energy Storage"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Electricity", "Storage & Chemical"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "AMERENMO-AWD-2024-01",
                        "recipient_name": "Aclara Technologies LLC (Hubbell)",
                        "recipient_type": "company",
                        "project_title": "Advanced Smart Distribution Grid Sensor Network and Outage Analytics Platform",
                        "award_amount": 7100000.0,
                        "year": 2024,
                        "recipient_city": "St. Louis",
                        "recipient_state": "MO",
                        "latitude": 38.6270,
                        "longitude": -90.1994,
                        "pi_name": "Kumi Premathilake",
                        "opportunity_sol_num": "AMERENMO-SMART-2026",
                        "technologies": ["Grid Modernization & Smart Grid", "AI, Computing & Energy Cyber"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Evergy Missouri",
                "short_name": "Evergy MO",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Evergy",
                "website": "https://www.evergy.com",
                "domain": "evergy.com",
                "city": "Kansas City",
                "state": "MO",
                "zip_code": "64106",
                "service_territory": "Western Missouri (Kansas City metropolitan area, St. Joseph)",
                "description": "Operating as Evergy Missouri West and Evergy Missouri Metro, serving approximately 800,000 customers in western Missouri.",
                "logo_domain": "evergy.com",
                "founded_year": 1882,
                "programs": [
                    {
                        "name": "Evergy Clean Energy Transition & EV Clean Charge Network",
                        "program_type": "innovation",
                        "description": "Kansas City Clean Charge Network (one of America's largest utility-installed public EV charging networks) and solar+storage integration.",
                        "url": "https://www.evergy.com/clean-energy",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "EVERGY-CLEAN-EV-2026",
                        "name": "Evergy Clean Charge Fleet Electrification & Microgrid RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 20000000.0,
                        "max_per_award": 5000000.0,
                        "short_description": "Procurement of fleet depot high-capacity fast charging systems, V2G bi-directional software, and microgrid islanding for municipal facilities.",
                        "service_territory": "Kansas City Metro",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.evergy.com/suppliers",
                        "year": 2026,
                        "keywords": "Clean Charge Network, EV fleet, V2G, Kansas City, Evergy",
                        "technologies": ["EV Charging & Infrastructure", "Electric Vehicles & Clean Transit", "Microgrids & Resilience"],
                        "sectors": ["Transportation", "Government & Municipal", "Electric Grid & Utility"],
                        "fuels": ["Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "EVERGY-AWD-2024-01",
                        "recipient_name": "ChargePoint Holdings, Inc.",
                        "recipient_type": "company",
                        "project_title": "Express Plus High-Power Fleet Charging Depot and Grid Load Optimization Platform",
                        "award_amount": 4900000.0,
                        "year": 2024,
                        "recipient_city": "Campbell",
                        "recipient_state": "CA",
                        "latitude": 37.2872,
                        "longitude": -121.9499,
                        "pi_name": "Pasquale Romano",
                        "opportunity_sol_num": "EVERGY-CLEAN-EV-2026",
                        "technologies": ["EV Charging & Infrastructure"],
                        "sectors": ["Transportation", "Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "MD": {
        "state_code": "MD",
        "state_name": "Maryland",
        "gdp_billions": 492,
        "rank": 22,
        "regulatory_body": "Maryland Public Service Commission (MD PSC) / PJM",
        "utilities": [
            {
                "name": "Baltimore Gas and Electric",
                "short_name": "BGE",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Exelon",
                "website": "https://www.bge.com",
                "domain": "bge.com",
                "city": "Baltimore",
                "state": "MD",
                "zip_code": "21201",
                "service_territory": "Central Maryland (Baltimore City, Baltimore, Anne Arundel, Howard, Harford, Carroll, Prince George's counties)",
                "description": "Maryland's largest electric and gas utility (the nation's first gas utility, founded 1816), serving more than 1.3 million electric customers and 700,000 gas customers.",
                "logo_domain": "bge.com",
                "founded_year": 1816,
                "programs": [
                    {
                        "name": "BGE Smart Energy Future & Community Microgrid",
                        "program_type": "innovation",
                        "description": "EVsmart charging network, distribution battery storage (Fairhaven 2.5MW/10MWh BESS), and resiliency microgrid pilots.",
                        "url": "https://www.bge.com/smart-energy",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "BGE-MICRO-STORAGE-2026",
                        "name": "BGE Community Resiliency Microgrid & Storage Solicitations",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 25000000.0,
                        "max_per_award": 7000000.0,
                        "short_description": "Competitive solicitation for community battery storage microgrids, solar aggregation, and islanding software across storm-prone Chesapeake Bay communities.",
                        "service_territory": "Central Maryland / Anne Arundel & Calvert Counties",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.bge.com/suppliers",
                        "year": 2026,
                        "keywords": "microgrid, BESS, Fairhaven, Chesapeake Bay resilience, EVsmart, BGE, Baltimore",
                        "technologies": ["Microgrids & Resilience", "Energy Storage", "Solar PV"],
                        "sectors": ["Electric Grid & Utility", "Government & Municipal"],
                        "fuels": ["Electricity", "Storage & Chemical"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "BGE-AWD-2024-01",
                        "recipient_name": "Schneider Electric USA",
                        "recipient_type": "company",
                        "project_title": "EcoStruxure Microgrid Advisor and Energy Control Center for Central Maryland Resiliency Hub",
                        "award_amount": 6200000.0,
                        "year": 2024,
                        "recipient_city": "Hanover",
                        "recipient_state": "MD",
                        "latitude": 39.1929,
                        "longitude": -76.7241,
                        "pi_name": "Aamir Paul",
                        "opportunity_sol_num": "BGE-MICRO-STORAGE-2026",
                        "technologies": ["Microgrids & Resilience", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility", "Government & Municipal"]
                    }
                ]
            },
            {
                "name": "Potomac Electric Power Company (Maryland)",
                "short_name": "Pepco MD",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Exelon",
                "website": "https://www.pepco.com",
                "domain": "pepco.com",
                "city": "Bethesda / Washington",
                "state": "MD",
                "zip_code": "20814",
                "service_territory": "Montgomery and Prince George's counties in suburban Maryland",
                "description": "Electric utility delivering electricity to approximately 600,000 customers in Montgomery and Prince George's counties.",
                "logo_domain": "pepco.com",
                "founded_year": 1896,
                "programs": [
                    {
                        "name": "Pepco Maryland Climate Action & Resilient Grid Program",
                        "program_type": "deployment",
                        "description": "Smart grid modernizations, distribution automation, transit bus electrification (Montgomery County Ride On), and public safety microgrids.",
                        "url": "https://www.pepco.com/cleanenergy",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "PEPCOMD-TRANSIT-EV-2026",
                        "name": "Pepco MD Brookville Smart Bus Depot & Microgrid Phase II RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 22000000.0,
                        "max_per_award": 6500000.0,
                        "short_description": "Procurement of solar canopy microgrid expansion, battery storage, and 100+ bus charging power management at Brookville Smart Transit Center.",
                        "service_territory": "Montgomery County / Silver Spring",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.pepco.com/suppliers",
                        "year": 2026,
                        "keywords": "Brookville, smart bus depot, Ride On, transit electrification, microgrid, Pepco MD",
                        "technologies": ["EV Charging & Infrastructure", "Microgrids & Resilience", "Electric Vehicles & Clean Transit"],
                        "sectors": ["Transportation", "Government & Municipal", "Electric Grid & Utility"],
                        "fuels": ["Electricity", "Solar"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "PEPCOMD-AWD-2024-01",
                        "recipient_name": "AlphaStruxure (Schneider / Carlyle JV)",
                        "recipient_type": "company",
                        "project_title": "Brookville Smart Energy Bus Depot Microgrid and Charging Management System Expansion",
                        "award_amount": 5900000.0,
                        "year": 2024,
                        "recipient_city": "Bethesda",
                        "recipient_state": "MD",
                        "latitude": 38.9847,
                        "longitude": -77.0947,
                        "pi_name": "Juan Macias",
                        "opportunity_sol_num": "PEPCOMD-TRANSIT-EV-2026",
                        "technologies": ["Microgrids & Resilience", "EV Charging & Infrastructure"],
                        "sectors": ["Transportation", "Government & Municipal"]
                    }
                ]
            }
        ]
    },
    "CT": {
        "state_code": "CT",
        "state_name": "Connecticut",
        "gdp_billions": 340,
        "rank": 23,
        "regulatory_body": "Connecticut Public Utilities Regulatory Authority (PURA) / ISO-NE",
        "utilities": [
            {
                "name": "Eversource Connecticut",
                "short_name": "Eversource CT",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Eversource Energy",
                "website": "https://www.eversource.com",
                "domain": "eversource.com",
                "city": "Hartford / Berlin",
                "state": "CT",
                "zip_code": "06037",
                "service_territory": "Northern, Central, and Eastern Connecticut (Hartford, Stamford, Waterbury, New London)",
                "description": "Operating as The Connecticut Light and Power Company (CL&P), serving approximately 1.3 million electric customers in 149 Connecticut cities and towns.",
                "logo_domain": "eversource.com",
                "founded_year": 1883,
                "programs": [
                    {
                        "name": "Eversource CT Energy Storage Solutions (PURA Docket 17-12-03RE03)",
                        "program_type": "deployment",
                        "description": "PURA-mandated statewide program deploying 580MW of residential, commercial, and utility-scale battery storage by 2030.",
                        "url": "https://energystoragect.com",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "EVRCT-STORAGE-2026",
                        "name": "Eversource CT Grid-Scale & Commercial Energy Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "grant",
                        "total_funding": 35000000.0,
                        "max_per_award": 8000000.0,
                        "short_description": "Competitive incentives for front-of-meter and large commercial battery energy storage systems integrated into ISO-NE demand markets.",
                        "service_territory": "Eversource Connecticut Territory",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.eversource.com/suppliers",
                        "year": 2026,
                        "keywords": "Energy Storage Solutions, PURA, battery storage, ISO-NE, Eversource CT, Hartford",
                        "technologies": ["Energy Storage", "Non-Wires Solutions (NWS)", "Solar PV"],
                        "sectors": ["Electric Grid & Utility", "Commercial", "Industry & Manufacturing"],
                        "fuels": ["Electricity", "Storage & Chemical"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "EVRCT-AWD-2025-01",
                        "recipient_name": "Agitas Energy",
                        "recipient_type": "company",
                        "project_title": "10MW/40MWh Standalone Battery Storage Facility for Substation Capacity Relief in Waterbury",
                        "award_amount": 7500000.0,
                        "year": 2025,
                        "recipient_city": "Hartford",
                        "recipient_state": "CT",
                        "latitude": 41.7658,
                        "longitude": -72.6734,
                        "pi_name": "David Bebrin",
                        "opportunity_sol_num": "EVRCT-STORAGE-2026",
                        "technologies": ["Energy Storage", "Non-Wires Solutions (NWS)"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "United Illuminating",
                "short_name": "UI",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Avangrid",
                "website": "https://www.uinet.com",
                "domain": "uinet.com",
                "city": "Orange",
                "state": "CT",
                "zip_code": "06477",
                "service_territory": "Greater New Haven and Bridgeport (Southwestern Connecticut coastal corridor)",
                "description": "Avangrid subsidiary providing electric service to approximately 340,000 customers in 17 southwestern Connecticut towns.",
                "logo_domain": "uinet.com",
                "founded_year": 1899,
                "programs": [
                    {
                        "name": "UI EV Infrastructure & Microgrid Innovation Program",
                        "program_type": "innovation",
                        "description": "EV make-ready infrastructure, Bridgeport microgrid hub, and battery storage demand response.",
                        "url": "https://www.uinet.com/cleanenergy",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "UI-BRIDGE-MICRO-2026",
                        "name": "United Illuminating Coastal Resiliency & Critical Facility Microgrid RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 18000000.0,
                        "max_per_award": 5000000.0,
                        "short_description": "Procurement of microgrid controllers, battery storage, and clean backup power for coastal flood-vulnerable municipal centers in Bridgeport and New Haven.",
                        "service_territory": "Bridgeport / New Haven Coastal Corridor",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.uinet.com/suppliers",
                        "year": 2026,
                        "keywords": "microgrid, coastal flood resilience, battery storage, Bridgeport, New Haven, UI, Avangrid",
                        "technologies": ["Microgrids & Resilience", "Energy Storage", "Solar PV"],
                        "sectors": ["Electric Grid & Utility", "Government & Municipal"],
                        "fuels": ["Electricity", "Storage & Chemical"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "UI-AWD-2024-01",
                        "recipient_name": "FuelCell Energy, Inc.",
                        "recipient_type": "company",
                        "project_title": "SureSource Stationary Fuel Cell Clean Power and Thermal Microgrid at Bridgeport Center",
                        "award_amount": 4800000.0,
                        "year": 2024,
                        "recipient_city": "Danbury",
                        "recipient_state": "CT",
                        "latitude": 41.3948,
                        "longitude": -73.4540,
                        "pi_name": "Jason Few",
                        "opportunity_sol_num": "UI-BRIDGE-MICRO-2026",
                        "technologies": ["Fuel Cells", "Microgrids & Resilience"],
                        "sectors": ["Electric Grid & Utility", "Government & Municipal"]
                    }
                ]
            }
        ]
    },
    "SC": {
        "state_code": "SC",
        "state_name": "South Carolina",
        "gdp_billions": 322,
        "rank": 24,
        "regulatory_body": "Public Service Commission of South Carolina (PSC SC)",
        "utilities": [
            {
                "name": "Dominion Energy South Carolina",
                "short_name": "Dominion Energy SC",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Dominion Energy",
                "website": "https://www.dominionenergy.com/south-carolina",
                "domain": "dominionenergy.com",
                "city": "Cayce / Columbia",
                "state": "SC",
                "zip_code": "29033",
                "service_territory": "Central, Southern, and Southwestern South Carolina (Columbia, Charleston, Aiken)",
                "description": "Regulated public utility providing electric service to approximately 800,000 customers and natural gas to 430,000 customers in South Carolina.",
                "logo_domain": "dominionenergy.com",
                "founded_year": 1846,
                "programs": [
                    {
                        "name": "Dominion Energy SC Clean Energy Plan & Storage Innovation",
                        "program_type": "deployment",
                        "description": "Grid modernization, solar integration, and 300MW battery energy storage additions under the Integrated Resource Plan.",
                        "url": "https://www.dominionenergy.com/south-carolina/clean-energy",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "DOMSC-BESS-IRP-2026",
                        "name": "Dominion Energy South Carolina Utility-Scale Battery Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 45000000.0,
                        "max_per_award": 15000000.0,
                        "short_description": "Procurement of 150MW/600MWh lithium-ion battery storage and solar integration in the Charleston and Columbia regions.",
                        "service_territory": "Central & Coastal South Carolina",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.dominionenergy.com/suppliers",
                        "year": 2026,
                        "keywords": "battery storage, BESS, solar integration, Charleston, Columbia, Dominion SC",
                        "technologies": ["Energy Storage", "Solar PV", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Solar", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "DOMSC-AWD-2024-01",
                        "recipient_name": "FlexGen Power Systems",
                        "recipient_type": "company",
                        "project_title": "HybridOS Energy Management System and Utility Battery Storage Integration",
                        "award_amount": 13800000.0,
                        "year": 2024,
                        "recipient_city": "Durham",
                        "recipient_state": "NC",
                        "latitude": 35.9940,
                        "longitude": -78.8986,
                        "pi_name": "Kelcy Pegler",
                        "opportunity_sol_num": "DOMSC-BESS-IRP-2026",
                        "technologies": ["Energy Storage", "AI, Computing & Energy Cyber"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Santee Cooper",
                "short_name": "Santee Cooper",
                "org_type": "utility",
                "sub_type": "State Public Power Authority",
                "parent_holding_company": "State of South Carolina",
                "website": "https://www.santeecooper.com",
                "domain": "santeecooper.com",
                "city": "Moncks Corner",
                "state": "SC",
                "zip_code": "29461",
                "service_territory": "Directly serves Grand Strand (Myrtle Beach) and wholesale power to 20 electric cooperatives statewide",
                "description": "South Carolina's state-owned electric and water utility, the state's largest power producer serving 2 million people directly and through wholesale co-ops.",
                "logo_domain": "santeecooper.com",
                "founded_year": 1934,
                "programs": [
                    {
                        "name": "Santee Cooper Clean Energy & Grid Transformation",
                        "program_type": "innovation",
                        "description": "Adding 1,000MW+ solar, battery storage, and advanced hydroelectric modernization (Pinopolis Hydro Plant).",
                        "url": "https://www.santeecooper.com/cleanenergy",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "SANTEE-CLEAN-STORAGE-2026",
                        "name": "Santee Cooper Clean Energy & Co-op Storage Solicitations",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 30000000.0,
                        "max_per_award": 10000000.0,
                        "short_description": "Competitive procurement of 100MW solar+storage and distribution automation to support rural cooperative wholesale delivery.",
                        "service_territory": "Grand Strand & Statewide Cooperative Network",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.santeecooper.com/procurement",
                        "year": 2026,
                        "keywords": "Santee Cooper, public power, solar, battery storage, wholesale co-op, Myrtle Beach",
                        "technologies": ["Solar PV", "Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Solar", "Storage & Chemical", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "SANTEE-AWD-2025-01",
                        "recipient_name": "Silicon Ranch Corporation",
                        "recipient_type": "company",
                        "project_title": "Regenerative Solar + Battery Energy Storage Facility for Wholesale Co-op Delivery",
                        "award_amount": 9500000.0,
                        "year": 2025,
                        "recipient_city": "Nashville",
                        "recipient_state": "TN",
                        "latitude": 36.1627,
                        "longitude": -86.7816,
                        "pi_name": "Reagan Farr",
                        "opportunity_sol_num": "SANTEE-CLEAN-STORAGE-2026",
                        "technologies": ["Solar PV", "Energy Storage"],
                        "sectors": ["Electric Grid & Utility", "Agriculture & Forestry"]
                    }
                ]
            }
        ]
    }
}
