"""Tier 13 States (Ranks 49-51): Alaska, Wyoming, Vermont."""

TIER13_DATA = {
    "AK": {
        "state_code": "AK",
        "state_name": "Alaska",
        "gdp_billions": 67,
        "rank": 49,
        "regulatory_body": "Regulatory Commission of Alaska (RCA)",
        "utilities": [
            {
                "name": "Chugach Electric Association",
                "short_name": "Chugach Electric",
                "org_type": "utility",
                "sub_type": "Electric Cooperative",
                "parent_holding_company": "Chugach Member-Owners",
                "website": "https://www.chugachelectric.com",
                "domain": "chugachelectric.com",
                "city": "Anchorage",
                "state": "AK",
                "zip_code": "99501",
                "service_territory": "Railbelt Region (Anchorage, Mat-Su Valley, Kenai Peninsula)",
                "description": "Alaska's largest electric cooperative, serving over 113,000 members across the Railbelt electric grid, operating the Southcentral Power Project and Eklutna Hydro.",
                "logo_domain": "chugachelectric.com",
                "founded_year": 1948,
                "programs": [
                    {
                        "name": "Chugach Railbelt Grid Modernization & Storage Innovation",
                        "program_type": "innovation",
                        "description": "Railbelt BESS integration, dynamic hydro-wind balancing (Fire Island Wind), and microgrid islanding for sub-arctic extreme weather.",
                        "url": "https://www.chugachelectric.com/energy-solutions",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "CHUGACH-RAILBELT-STORAGE-2026",
                        "name": "Chugach Railbelt Sub-Arctic Grid Battery Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 25000000.0,
                        "max_per_award": 8000000.0,
                        "short_description": "Procurement of cold-weather thermal insulated 50MW/100MWh battery energy storage systems and fast spinning-reserve replacement software on the Alaska Railbelt.",
                        "service_territory": "Anchorage & Kenai Peninsula / Railbelt Grid",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.chugachelectric.com/bids",
                        "year": 2026,
                        "keywords": "sub-arctic storage, Railbelt grid, spinning reserve, cold climate BESS, Chugach Electric, Anchorage",
                        "technologies": ["Energy Storage", "Microgrids & Resilience", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "CHUGACH-AWD-2025-01",
                        "recipient_name": "Tesla Energy Operations",
                        "recipient_type": "company",
                        "project_title": "Cold-Weather Megapack Battery Energy Storage System for Chugach Railbelt Reserve",
                        "award_amount": 7800000.0,
                        "year": 2025,
                        "recipient_city": "Anchorage",
                        "recipient_state": "AK",
                        "latitude": 61.2181,
                        "longitude": -149.9003,
                        "pi_name": "Mike Snyder",
                        "opportunity_sol_num": "CHUGACH-RAILBELT-STORAGE-2026",
                        "technologies": ["Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Golden Valley Electric Association",
                "short_name": "GVEA",
                "org_type": "utility",
                "sub_type": "Electric Cooperative",
                "parent_holding_company": "GVEA Member-Owners",
                "website": "https://www.gvea.com",
                "domain": "gvea.com",
                "city": "Fairbanks",
                "state": "AK",
                "zip_code": "99701",
                "service_territory": "Interior Alaska (Fairbanks, Delta Junction, Nenana, Healy, Cantwell)",
                "description": "Electric cooperative serving 100,000 residents in Interior Alaska, historic operator of the Guinness World Record Fairbanks BESS (world's first large utility Ni-Cd battery, now modernized).",
                "logo_domain": "gvea.com",
                "founded_year": 1946,
                "programs": [
                    {
                        "name": "GVEA Clean Energy Transition & Modernized BESS Center",
                        "program_type": "innovation",
                        "description": "Modernizing the Fairbanks BESS with advanced lithium-iron phosphate storage and integrating wind energy (Eva Creek Wind).",
                        "url": "https://www.gvea.com/clean-energy/",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "GVEA-BESS-MODERN-2026",
                        "name": "GVEA Fairbanks Modernized 46MW Battery Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 22000000.0,
                        "max_per_award": 7000000.0,
                        "short_description": "Procurement of next-generation cold-weather sub-arctic BESS modules, smart inverters, and automated blackout prevention controllers in Fairbanks.",
                        "service_territory": "Fairbanks / Interior Alaska",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.gvea.com/suppliers",
                        "year": 2026,
                        "keywords": "Fairbanks BESS, sub-arctic, extreme cold, Eva Creek, blackout prevention, GVEA",
                        "technologies": ["Energy Storage", "Power Electronics & Inverters", "Microgrids & Resilience"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "GVEA-AWD-2024-01",
                        "recipient_name": "ABB Inc.",
                        "recipient_type": "company",
                        "project_title": "Sub-Zero Inverter Systems and Fast Islanding Controllers for Fairbanks BESS Upgrade",
                        "award_amount": 6400000.0,
                        "year": 2024,
                        "recipient_city": "Fairbanks",
                        "recipient_state": "AK",
                        "latitude": 64.8378,
                        "longitude": -147.7164,
                        "pi_name": "Massimo Danieli",
                        "opportunity_sol_num": "GVEA-BESS-MODERN-2026",
                        "technologies": ["Power Electronics & Inverters", "Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "WY": {
        "state_code": "WY",
        "state_name": "Wyoming",
        "gdp_billions": 50,
        "rank": 50,
        "regulatory_body": "Wyoming Public Service Commission (WPSC)",
        "utilities": [
            {
                "name": "Rocky Mountain Power (Wyoming)",
                "short_name": "Rocky Mountain Power WY",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Berkshire Hathaway Energy",
                "website": "https://www.rockymountainpower.net",
                "domain": "rockymountainpower.net",
                "city": "Casper",
                "state": "WY",
                "zip_code": "82601",
                "service_territory": "Casper, Cheyenne, Laramie, Rock Springs, Gillette, and throughout Wyoming",
                "description": "PacifiCorp operating company serving 145,000 customers in Wyoming, utility partner for the commercial TerraPower Natrium Advanced Nuclear Reactor demonstration in Kemmerer, WY.",
                "logo_domain": "rockymountainpower.net",
                "founded_year": 1912,
                "programs": [
                    {
                        "name": "Rocky Mountain Power & TerraPower Natrium Advanced Nuclear Demonstration",
                        "program_type": "innovation",
                        "description": "Flagship DOE Advanced Reactor Demonstration Program (ARDP) project deploying a 345MWe sodium-cooled fast reactor with molten salt thermal energy storage at retiring Naughton Coal Plant in Kemmerer, WY.",
                        "url": "https://www.terrapower.com/natrium-kemmerer/",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "RMPWY-NATRIUM-SMR-2026",
                        "name": "Rocky Mountain Power Natrium Advanced Reactor Interconnection & Thermal Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 180000000.0,
                        "max_per_award": 60000000.0,
                        "short_description": "Engineering, high-temperature molten salt thermal storage integration, and high-voltage grid interconnection for the 345MWe/1GWh Natrium Advanced Reactor in Kemmerer, Wyoming.",
                        "service_territory": "Kemmerer / Lincoln County / Southwest Wyoming",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.rockymountainpower.net/suppliers",
                        "year": 2026,
                        "keywords": "Natrium, TerraPower, SMR, advanced nuclear, molten salt storage, Kemmerer, Rocky Mountain Power WY",
                        "technologies": ["Nuclear & Advanced SMRs", "Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"],
                        "fuels": ["Nuclear", "Storage & Chemical", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "RMPWY-AWD-2025-01",
                        "recipient_name": "TerraPower, LLC",
                        "recipient_type": "company",
                        "project_title": "Natrium Sodium-Cooled Fast Reactor & Molten Salt Thermal Energy Storage Commercial Demonstration",
                        "award_amount": 55000000.0,
                        "year": 2025,
                        "recipient_city": "Kemmerer",
                        "recipient_state": "WY",
                        "latitude": 41.7919,
                        "longitude": -110.5363,
                        "pi_name": "Chris Levesque",
                        "opportunity_sol_num": "RMPWY-NATRIUM-SMR-2026",
                        "technologies": ["Nuclear & Advanced SMRs", "Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    },
                    {
                        "external_award_id": "RMPWY-AWD-2024-02",
                        "recipient_name": "Bechtel Power Corporation",
                        "recipient_type": "company",
                        "project_title": "Engineering and Site Infrastructure Design for Kemmerer Natrium Nuclear Island",
                        "award_amount": 22000000.0,
                        "year": 2024,
                        "recipient_city": "Reston",
                        "recipient_state": "VA",
                        "latitude": 38.9586,
                        "longitude": -77.3570,
                        "pi_name": "Craig Albert",
                        "opportunity_sol_num": "RMPWY-NATRIUM-SMR-2026",
                        "technologies": ["Nuclear & Advanced SMRs"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "VT": {
        "state_code": "VT",
        "state_name": "Vermont",
        "gdp_billions": 43,
        "rank": 51,
        "regulatory_body": "Vermont Public Utility Commission (VPUC) / ISO-NE",
        "utilities": [
            {
                "name": "Green Mountain Power",
                "short_name": "GMP",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU - B-Corp Certified)",
                "parent_holding_company": "Énergir",
                "website": "https://greenmountainpower.com",
                "domain": "greenmountainpower.com",
                "city": "Colchester / Rutland",
                "state": "VT",
                "zip_code": "05446",
                "service_territory": "Approximately 75% of Vermont (Burlington area, Rutland, Montpelier, Brattleboro)",
                "description": "The first utility in the world to become a Certified B Corp, serving 270,000 customers in Vermont, national pioneer with the Zero Outages Initiative and residential Tesla Powerwall Virtual Power Plant.",
                "logo_domain": "greenmountainpower.com",
                "founded_year": 1928,
                "programs": [
                    {
                        "name": "GMP Zero Outages Initiative & Powerwall VPP Program",
                        "program_type": "innovation",
                        "description": "Groundbreaking plan to end power outages across Vermont by deploying residential battery storage (5,000+ Powerwalls), utility microgrids, and undergrounding lines.",
                        "url": "https://greenmountainpower.com/zero-outages-initiative/",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "GMP-ZERO-OUTAGE-2026",
                        "name": "Green Mountain Power Zero Outages Battery Storage & Islanding Microgrid RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 25000000.0,
                        "max_per_award": 6000000.0,
                        "short_description": "Procurement of residential/commercial battery storage aggregations, rural microgrid controllers, and storm-hardening systems to deliver zero outage resilience across Vermont.",
                        "service_territory": "Statewide Vermont / Rutland & Colchester",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://greenmountainpower.com/procurement",
                        "year": 2026,
                        "keywords": "Zero Outages, Tesla Powerwall, VPP, residential battery, B Corp, Green Mountain Power, Vermont",
                        "technologies": ["Energy Storage", "Microgrids & Resilience", "Non-Wires Solutions (NWS)"],
                        "sectors": ["Residential", "Electric Grid & Utility"],
                        "fuels": ["Electricity", "Storage & Chemical"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "GMP-AWD-2025-01",
                        "recipient_name": "Tesla Energy Operations",
                        "recipient_type": "company",
                        "project_title": "Fleet Powerwall Home Battery Energy Storage Aggregation for Zero Outages Grid Dispatch",
                        "award_amount": 8200000.0,
                        "year": 2025,
                        "recipient_city": "Rutland",
                        "recipient_state": "VT",
                        "latitude": 43.6106,
                        "longitude": -72.9726,
                        "pi_name": "Mike Snyder",
                        "opportunity_sol_num": "GMP-ZERO-OUTAGE-2026",
                        "technologies": ["Energy Storage", "Non-Wires Solutions (NWS)"],
                        "sectors": ["Residential", "Electric Grid & Utility"]
                    },
                    {
                        "external_award_id": "GMP-AWD-2024-02",
                        "recipient_name": "Dynapower Company LLC",
                        "recipient_type": "company",
                        "project_title": "High-Efficiency Substation Inverters for Stafford Hill 100% Solar-Storage Microgrid",
                        "award_amount": 3400000.0,
                        "year": 2024,
                        "recipient_city": "South Burlington",
                        "recipient_state": "VT",
                        "latitude": 44.4669,
                        "longitude": -73.1709,
                        "pi_name": "Adam Knudsen",
                        "opportunity_sol_num": "GMP-ZERO-OUTAGE-2026",
                        "technologies": ["Power Electronics & Inverters", "Microgrids & Resilience"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    }
}
