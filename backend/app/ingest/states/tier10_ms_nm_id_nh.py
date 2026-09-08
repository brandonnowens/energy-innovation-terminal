"""Tier 10 States (Ranks 37-40): Mississippi, New Mexico, Idaho, New Hampshire."""

TIER10_DATA = {
    "MS": {
        "state_code": "MS",
        "state_name": "Mississippi",
        "gdp_billions": 146,
        "rank": 37,
        "regulatory_body": "Mississippi Public Service Commission (MS PSC) / MISO / Southern",
        "utilities": [
            {
                "name": "Mississippi Power",
                "short_name": "Mississippi Power",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Southern Company",
                "website": "https://www.mississippipower.com",
                "domain": "mississippipower.com",
                "city": "Gulfport",
                "state": "MS",
                "zip_code": "39501",
                "service_territory": "Southeast Mississippi (Gulf Coast, Biloxi, Gulfport, Hattiesburg, Meridian)",
                "description": "Southern Company electric utility providing power to approximately 190,000 customers in 23 southeast Mississippi counties.",
                "logo_domain": "mississippipower.com",
                "founded_year": 1925,
                "programs": [
                    {
                        "name": "Mississippi Power Smart Grid & Coastal Storm Hardening",
                        "program_type": "deployment",
                        "description": "Gulf Coast hurricane hardening, smart automated reclosers, industrial solar expansion, and battery storage.",
                        "url": "https://www.mississippipower.com/cleanenergy",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "MSP-COASTAL-RESIL-2026",
                        "name": "Mississippi Power Coastal Resiliency & Industrial Microgrid RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 20000000.0,
                        "max_per_award": 6000000.0,
                        "short_description": "Procurement of storm-resilient automated distribution controllers, substation flood defenses, and industrial port microgrids on the Gulf Coast.",
                        "service_territory": "Gulfport / Biloxi / Mississippi Gulf Coast",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.mississippipower.com/suppliers",
                        "year": 2026,
                        "keywords": "coastal resilience, hurricane hardening, microgrid, Mississippi Power, Gulfport",
                        "technologies": ["Grid Modernization & Smart Grid", "Microgrids & Resilience"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"],
                        "fuels": ["Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "MSP-AWD-2024-01",
                        "recipient_name": "PowerSecure, Inc.",
                        "recipient_type": "company",
                        "project_title": "Port of Gulfport Resilient Microgrid and Automated Switchgear Integration",
                        "award_amount": 5200000.0,
                        "year": 2024,
                        "recipient_city": "Durham",
                        "recipient_state": "NC",
                        "latitude": 35.9940,
                        "longitude": -78.8986,
                        "pi_name": "Eric Dupont",
                        "opportunity_sol_num": "MSP-COASTAL-RESIL-2026",
                        "technologies": ["Microgrids & Resilience"],
                        "sectors": ["Industry & Manufacturing", "Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "NM": {
        "state_code": "NM",
        "state_name": "New Mexico",
        "gdp_billions": 130,
        "rank": 38,
        "regulatory_body": "New Mexico Public Regulation Commission (NMPRC)",
        "utilities": [
            {
                "name": "Public Service Company of New Mexico",
                "short_name": "PNM",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "PNM Resources",
                "website": "https://www.pnm.com",
                "domain": "pnm.com",
                "city": "Albuquerque",
                "state": "NM",
                "zip_code": "87158",
                "service_territory": "Albuquerque, Santa Fe, Rio Rancho, Silver City, Las Vegas (NM), and rural New Mexico",
                "description": "New Mexico's largest electricity provider, serving more than 530,000 customers with a statutory mandate under the Energy Transition Act (ETA) for 100% carbon-free electricity by 2045.",
                "logo_domain": "pnm.com",
                "founded_year": 1917,
                "programs": [
                    {
                        "name": "PNM Energy Transition Act (ETA) & San Juan Storage Center",
                        "program_type": "innovation",
                        "description": "Repurposing the retired San Juan Generating Station into solar+storage and piloting clean hydrogen blending and long-duration storage.",
                        "url": "https://www.pnm.com/cleanenergy",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "PNM-ETA-STORAGE-2026",
                        "name": "PNM Energy Transition Act Battery Energy Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 50000000.0,
                        "max_per_award": 20000000.0,
                        "short_description": "Procurement of 300MW/1,200MWh of utility-scale battery energy storage to replace retired coal capacity in northwest New Mexico.",
                        "service_territory": "San Juan County / Albuquerque Metro",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.pnm.com/suppliers",
                        "year": 2026,
                        "keywords": "Energy Transition Act, San Juan coal conversion, BESS, battery storage, PNM, Albuquerque",
                        "technologies": ["Energy Storage", "Solar PV", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Solar", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "PNM-AWD-2025-01",
                        "recipient_name": "Photosol US",
                        "recipient_type": "company",
                        "project_title": "San Juan 100MW Solar and 50MW/200MWh Battery Storage Project",
                        "award_amount": 18000000.0,
                        "year": 2025,
                        "recipient_city": "Albuquerque",
                        "recipient_state": "NM",
                        "latitude": 35.0844,
                        "longitude": -106.6504,
                        "pi_name": "Robin Weisman",
                        "opportunity_sol_num": "PNM-ETA-STORAGE-2026",
                        "technologies": ["Solar PV", "Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "ID": {
        "state_code": "ID",
        "state_name": "Idaho",
        "gdp_billions": 119,
        "rank": 39,
        "regulatory_body": "Idaho Public Utilities Commission (IPUC)",
        "utilities": [
            {
                "name": "Idaho Power",
                "short_name": "Idaho Power",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "IDACORP, Inc.",
                "website": "https://www.idahopower.com",
                "domain": "idahopower.com",
                "city": "Boise",
                "state": "ID",
                "zip_code": "83702",
                "service_territory": "Southern Idaho and eastern Oregon (Boise, Nampa, Meridian, Pocatello, Twin Falls, Idaho Falls)",
                "description": "Electric utility providing electricity to 620,000 customers in southern Idaho and eastern Oregon, pursuing a Clean Today, Cleaner Tomorrow goal of 100% clean energy by 2045.",
                "logo_domain": "idahopower.com",
                "founded_year": 1916,
                "programs": [
                    {
                        "name": "Idaho Power Clean Energy 2045 & Battery Storage Hub",
                        "program_type": "deployment",
                        "description": "Deploying 400MW+ battery energy storage (Hemingway 120MW BESS, Black Mesa BESS) to balance large-scale solar and Snake River hydropower.",
                        "url": "https://www.idahopower.com/cleanenergy",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "IDPWR-CLEAN-BESS-2026",
                        "name": "Idaho Power Grid-Scale Storage & Hydro Balancing RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 40000000.0,
                        "max_per_award": 15000000.0,
                        "short_description": "Competitive procurement of 150MW/600MWh battery energy storage systems integrated with Snake River hydroelectric facilities in the Treasure Valley.",
                        "service_territory": "Treasure Valley / Boise Metro",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.idahopower.com/suppliers",
                        "year": 2026,
                        "keywords": "Hemingway, battery storage, BESS, hydro balancing, Clean Today Cleaner Tomorrow, Idaho Power, Boise",
                        "technologies": ["Energy Storage", "Water & Marine Power", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility", "Agriculture & Forestry"],
                        "fuels": ["Storage & Chemical", "Hydro & Marine", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "IDPWR-AWD-2024-01",
                        "recipient_name": "Powin Energy Corporation",
                        "recipient_type": "company",
                        "project_title": "Hemingway 120MW/480MWh Standalone Lithium-Ion Battery Storage System",
                        "award_amount": 14200000.0,
                        "year": 2024,
                        "recipient_city": "Tualatin",
                        "recipient_state": "OR",
                        "latitude": 45.3839,
                        "longitude": -122.7865,
                        "pi_name": "Jeff Waters",
                        "opportunity_sol_num": "IDPWR-CLEAN-BESS-2026",
                        "technologies": ["Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "NH": {
        "state_code": "NH",
        "state_name": "New Hampshire",
        "gdp_billions": 111,
        "rank": 40,
        "regulatory_body": "New Hampshire Public Utilities Commission (NH PUC) / ISO-NE",
        "utilities": [
            {
                "name": "Eversource New Hampshire",
                "short_name": "Eversource NH",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Eversource Energy",
                "website": "https://www.eversource.com",
                "domain": "eversource.com",
                "city": "Manchester",
                "state": "NH",
                "zip_code": "03101",
                "service_territory": "Central, Southern, and Western New Hampshire (Manchester, Nashua, Portsmouth, Concord)",
                "description": "Operating as Public Service Company of New Hampshire (PSNH), providing electric service to approximately 530,000 customers in 211 New Hampshire cities and towns.",
                "logo_domain": "eversource.com",
                "founded_year": 1926,
                "programs": [
                    {
                        "name": "Eversource NH Clean Grid & Storage Demonstrations",
                        "program_type": "deployment",
                        "description": "Grid modernization, automated smart switches, and clean energy storage demonstrations in northern New England.",
                        "url": "https://www.eversource.com/cleanenergy",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "EVRNH-GRID-BESS-2026",
                        "name": "Eversource NH Substation Storage & Winter Peaking RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 18000000.0,
                        "max_per_award": 5000000.0,
                        "short_description": "Procurement of winter cold-climate battery energy storage and automated distribution grid restoration in Manchester and Nashua.",
                        "service_territory": "Southern & Central New Hampshire",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.eversource.com/suppliers",
                        "year": 2026,
                        "keywords": "winter peaking, cold climate storage, BESS, Eversource NH, Manchester",
                        "technologies": ["Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "EVRNH-AWD-2024-01",
                        "recipient_name": "Enel X North America",
                        "recipient_type": "company",
                        "project_title": "Cold-Climate Lithium-Ion Battery Storage System for Winter Peak Load Shaving",
                        "award_amount": 4600000.0,
                        "year": 2024,
                        "recipient_city": "Boston",
                        "recipient_state": "MA",
                        "latitude": 42.3601,
                        "longitude": -71.0589,
                        "pi_name": "Surya Panditi",
                        "opportunity_sol_num": "EVRNH-GRID-BESS-2026",
                        "technologies": ["Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    }
}
