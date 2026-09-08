"""Tier 11 States (Ranks 41-44): Hawaii, West Virginia, Delaware, Maine."""

TIER11_DATA = {
    "HI": {
        "state_code": "HI",
        "state_name": "Hawaii",
        "gdp_billions": 108,
        "rank": 41,
        "regulatory_body": "Hawaii Public Utilities Commission (HI PUC)",
        "utilities": [
            {
                "name": "Hawaiian Electric Company",
                "short_name": "HECO",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Hawaiian Electric Industries",
                "website": "https://www.hawaiianelectric.com",
                "domain": "hawaiianelectric.com",
                "city": "Honolulu",
                "state": "HI",
                "zip_code": "96813",
                "service_territory": "Oahu (HECO), Maui County (MECO), and Hawaii Island (HELCO) - serving 95% of state's population",
                "description": "Operating on five isolated island grids, Hawaiian Electric is a global leader in high-penetration distributed solar, grid-scale storage, and 100% renewable portfolio standards by 2045.",
                "logo_domain": "hawaiianelectric.com",
                "founded_year": 1891,
                "programs": [
                    {
                        "name": "HECO Stage 3 Clean Energy & Grid-Scale Storage RFP",
                        "program_type": "innovation",
                        "description": "Procuring over 500MW solar and 2,000MWh battery storage, fast frequency response (FFR), and grid-forming inverter technology for isolated island grids.",
                        "url": "https://www.hawaiianelectric.com/clean-energy-hawaii/selling-power-to-the-utility/competitive-bidding-for-system-resources",
                        "active": True,
                        "target_stage": "deployment",
                    },
                    {
                        "name": "HECO Shifted Energy Water Heater VPP & Emergency Demand Response",
                        "program_type": "innovation",
                        "description": "Aggregating 10,000+ smart grid-connected water heaters and residential batteries for automated fast frequency response.",
                        "url": "https://www.hawaiianelectric.com/products-and-services/customer-energy-programs",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "HECO-STAGE3-STORAGE-2026",
                        "name": "HECO Stage 3 Island Grid-Forming Battery Storage & Solar RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 60000000.0,
                        "max_per_award": 25000000.0,
                        "short_description": "Competitive procurement of 250MW/1,000MWh grid-forming battery storage systems (GFMs) for black start and dynamic stability on Oahu and Maui.",
                        "service_territory": "Oahu, Maui, and Hawaii Island",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.hawaiianelectric.com/suppliers",
                        "year": 2026,
                        "keywords": "grid-forming inverters, Stage 3 RFP, island grid, fast frequency response, BESS, HECO, Honolulu",
                        "technologies": ["Power Electronics & Inverters", "Energy Storage", "Solar PV", "Microgrids & Resilience"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Solar", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "HECO-AWD-2025-01",
                        "recipient_name": "Plus Power LLC",
                        "recipient_type": "company",
                        "project_title": "Kapolei 185MW/565MWh Energy Storage Facility with Grid-Forming Inverter System on Oahu",
                        "award_amount": 26000000.0,
                        "year": 2025,
                        "recipient_city": "Kapolei",
                        "recipient_state": "HI",
                        "latitude": 21.3358,
                        "longitude": -158.0800,
                        "pi_name": "Brandon Keefe",
                        "opportunity_sol_num": "HECO-STAGE3-STORAGE-2026",
                        "technologies": ["Energy Storage", "Power Electronics & Inverters"],
                        "sectors": ["Electric Grid & Utility"]
                    },
                    {
                        "external_award_id": "HECO-AWD-2024-02",
                        "recipient_name": "Shifted Energy, Inc.",
                        "recipient_type": "company",
                        "project_title": "Oahu Smart Water Heater Fast Frequency Response Virtual Power Plant Network",
                        "award_amount": 4200000.0,
                        "year": 2024,
                        "recipient_city": "Honolulu",
                        "recipient_state": "HI",
                        "latitude": 21.3069,
                        "longitude": -157.8583,
                        "pi_name": "Forest Frizzell",
                        "opportunity_sol_num": "HECO-STAGE3-STORAGE-2026",
                        "technologies": ["Non-Wires Solutions (NWS)", "AI, Computing & Energy Cyber"],
                        "sectors": ["Residential", "Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Kauai Island Utility Cooperative",
                "short_name": "KIUC",
                "org_type": "utility",
                "sub_type": "Electric Cooperative",
                "parent_holding_company": "KIUC Member-Owners",
                "website": "https://www.kiuc.coop",
                "domain": "kiuc.coop",
                "city": "Lihue",
                "state": "HI",
                "zip_code": "96766",
                "service_territory": "Island of Kauai",
                "description": "Member-owned electric cooperative operating an isolated island grid generating 70%+ of electricity from renewable resources, operating the West Kauai Energy Project.",
                "logo_domain": "kiuc.coop",
                "founded_year": 2002,
                "programs": [
                    {
                        "name": "KIUC West Kauai Energy Project (WKEP) & Pumped Storage",
                        "program_type": "innovation",
                        "description": "Innovative integration of pumped storage hydroelectricity, irrigation water supply, and solar PV.",
                        "url": "https://kiuc.coop/wkep",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "KIUC-WKEP-HYDRO-2026",
                        "name": "KIUC Pumped Hydro Storage & Island Autonomous Grid RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 18000000.0,
                        "max_per_award": 6000000.0,
                        "short_description": "Procurement of reversible pump-turbines, digital governors, and solar-coupled energy management controls for the West Kauai Energy Project.",
                        "service_territory": "Island of Kauai",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://kiuc.coop/procurement",
                        "year": 2026,
                        "keywords": "pumped storage hydro, WKEP, 100% renewable island, KIUC, Kauai, solar hydro",
                        "technologies": ["Water & Marine Power", "Energy Storage", "Solar PV", "Microgrids & Resilience"],
                        "sectors": ["Electric Grid & Utility", "Agriculture & Forestry"],
                        "fuels": ["Hydro & Marine", "Solar", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "KIUC-AWD-2024-01",
                        "recipient_name": "AES Distributed Energy",
                        "recipient_type": "company",
                        "project_title": "West Kauai Pumped Storage Hydro and 35MW Solar PV Hybrid Integration",
                        "award_amount": 5800000.0,
                        "year": 2024,
                        "recipient_city": "Lihue",
                        "recipient_state": "HI",
                        "latitude": 21.9811,
                        "longitude": -159.3711,
                        "pi_name": "Woody Rubin",
                        "opportunity_sol_num": "KIUC-WKEP-HYDRO-2026",
                        "technologies": ["Water & Marine Power", "Solar PV", "Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "WV": {
        "state_code": "WV",
        "state_name": "West Virginia",
        "gdp_billions": 99,
        "rank": 42,
        "regulatory_body": "Public Service Commission of West Virginia (PSC WV) / PJM",
        "utilities": [
            {
                "name": "Appalachian Power (West Virginia)",
                "short_name": "Appalachian Power WV",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "American Electric Power",
                "website": "https://www.appalachianpower.com",
                "domain": "appalachianpower.com",
                "city": "Charleston",
                "state": "WV",
                "zip_code": "25301",
                "service_territory": "Southern West Virginia (Charleston, Huntington, Beckley, Bluefield)",
                "description": "AEP operating company delivering electricity to nearly 500,000 customers in 21 West Virginia counties.",
                "logo_domain": "appalachianpower.com",
                "founded_year": 1926,
                "programs": [
                    {
                        "name": "Appalachian Power WV Clean Energy & Battery Storage Demonstration",
                        "program_type": "deployment",
                        "description": "Procuring utility-scale solar and battery storage in coal country, grid resilience, and mine land renewable re-powering.",
                        "url": "https://www.appalachianpower.com/cleanenergy",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "APCOWV-MINE-SOLAR-2026",
                        "name": "Appalachian Power Post-Mining Land Solar & Battery Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 30000000.0,
                        "max_per_award": 10000000.0,
                        "short_description": "Procurement of 100MW utility solar and 30MW battery storage on reclaimed surface coal mine lands in southern West Virginia.",
                        "service_territory": "Kanawha, Boone, and Logan Counties",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.aep.com/suppliers",
                        "year": 2026,
                        "keywords": "mine land solar, coal country, BESS, AEP, Appalachian Power, Charleston",
                        "technologies": ["Solar PV", "Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility", "Industry & Manufacturing"],
                        "fuels": ["Solar", "Storage & Chemical", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "APCOWV-AWD-2024-01",
                        "recipient_name": "Savion, LLC",
                        "recipient_type": "company",
                        "project_title": "Reclaimed Surface Mine Solar and Substation Interconnection at Boone County",
                        "award_amount": 9200000.0,
                        "year": 2024,
                        "recipient_city": "Charleston",
                        "recipient_state": "WV",
                        "latitude": 38.3498,
                        "longitude": -81.6326,
                        "pi_name": "Nick Lincon",
                        "opportunity_sol_num": "APCOWV-MINE-SOLAR-2026",
                        "technologies": ["Solar PV", "Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "DE": {
        "state_code": "DE",
        "state_name": "Delaware",
        "gdp_billions": 94,
        "rank": 43,
        "regulatory_body": "Delaware Public Service Commission (DE PSC) / PJM",
        "utilities": [
            {
                "name": "Delmarva Power (Delaware)",
                "short_name": "Delmarva Power DE",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Exelon",
                "website": "https://www.delmarva.com",
                "domain": "delmarva.com",
                "city": "Wilmington / Newark",
                "state": "DE",
                "zip_code": "19801",
                "service_territory": "New Castle, Kent, and Sussex counties (entire state of Delaware)",
                "description": "Exelon utility providing electric delivery service to 330,000 customers and gas to 140,000 customers in Delaware.",
                "logo_domain": "delmarva.com",
                "founded_year": 1909,
                "programs": [
                    {
                        "name": "Delmarva Power Smart Energy Network & V2G Innovation",
                        "program_type": "deployment",
                        "description": "Smart Energy Network AMI deployment, University of Delaware V2G pioneer integration, and coastal storm hardening.",
                        "url": "https://www.delmarva.com/smartenergy",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "DELMDE-SMART-V2G-2026",
                        "name": "Delmarva Power Grid Modernization & Fleet V2G Solicitations",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 16000000.0,
                        "max_per_award": 5000000.0,
                        "short_description": "Procurement of smart distribution sensors, bi-directional V2G charging aggregators, and coastal flood-hardened reclosers in Delaware.",
                        "service_territory": "State of Delaware / Wilmington & Sussex County",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.delmarva.com/suppliers",
                        "year": 2026,
                        "keywords": "Smart Energy Network, V2G, University of Delaware, Delmarva Power, Wilmington",
                        "technologies": ["EV Charging & Infrastructure", "Grid Modernization & Smart Grid", "Electric Vehicles & Clean Transit"],
                        "sectors": ["Transportation", "Electric Grid & Utility"],
                        "fuels": ["Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "DELMDE-AWD-2024-01",
                        "recipient_name": "University of Delaware (Center for Composite Materials & V2G Lab)",
                        "recipient_type": "university",
                        "project_title": "Grid-Integrated Vehicle-to-Grid Frequency Regulation Fleet Commercialization Pilot",
                        "award_amount": 4500000.0,
                        "year": 2024,
                        "recipient_city": "Newark",
                        "recipient_state": "DE",
                        "latitude": 39.6837,
                        "longitude": -75.7497,
                        "pi_name": "Dr. Willett Kempton",
                        "opportunity_sol_num": "DELMDE-SMART-V2G-2026",
                        "technologies": ["EV Charging & Infrastructure", "Electric Vehicles & Clean Transit"],
                        "sectors": ["Transportation", "Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "ME": {
        "state_code": "ME",
        "state_name": "Maine",
        "gdp_billions": 91,
        "rank": 44,
        "regulatory_body": "Maine Public Utilities Commission (MPUC) / ISO-NE",
        "utilities": [
            {
                "name": "Central Maine Power",
                "short_name": "CMP",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Avangrid",
                "website": "https://www.cmpco.com",
                "domain": "cmpco.com",
                "city": "Augusta",
                "state": "ME",
                "zip_code": "04336",
                "service_territory": "Southern and Central Maine (Portland, Lewiston, Augusta, Bangor corridor)",
                "description": "Avangrid subsidiary delivering electricity to more than 650,000 customers in central and southern Maine (over 80% of Maine's population).",
                "logo_domain": "cmpco.com",
                "founded_year": 1899,
                "programs": [
                    {
                        "name": "CMP Non-Wires Alternatives & Grid Modernization (MPUC Docket)",
                        "program_type": "innovation",
                        "description": "Statutory Non-Wires Alternatives (NWA) procurement through the Maine Office of the Public Advocate and Efficiency Maine.",
                        "url": "https://www.cmpco.com/cleanenergy",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "CMP-NWA-ISLAND-2026",
                        "name": "Central Maine Power Non-Wires Alternatives & Island Microgrid RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 20000000.0,
                        "max_per_award": 6000000.0,
                        "short_description": "Procurement of battery energy storage, heat pump peak demand flexibility, and smart inverters to defer transmission line rebuilds in rural Maine.",
                        "service_territory": "Midcoast & Western Maine",
                        "utility_program_type": "NWA",
                        "procurement_portal_url": "https://www.cmpco.com/suppliers",
                        "year": 2026,
                        "keywords": "NWA, non-wires alternative, battery storage, heat pump, Central Maine Power, Augusta",
                        "technologies": ["Non-Wires Solutions (NWS)", "Energy Storage", "Heat Pumps & Building Electrification"],
                        "sectors": ["Electric Grid & Utility", "Residential"],
                        "fuels": ["Electricity", "Storage & Chemical"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "CMP-AWD-2024-01",
                        "recipient_name": "ReVision Energy",
                        "recipient_type": "company",
                        "project_title": "Boothbay Peninsula Community Solar + Battery Storage NWA Capacity Relief Project",
                        "award_amount": 5200000.0,
                        "year": 2024,
                        "recipient_city": "South Portland",
                        "recipient_state": "ME",
                        "latitude": 43.6415,
                        "longitude": -70.2409,
                        "pi_name": "Fortunat Mueller",
                        "opportunity_sol_num": "CMP-NWA-ISLAND-2026",
                        "technologies": ["Solar PV", "Energy Storage", "Non-Wires Solutions (NWS)"],
                        "sectors": ["Electric Grid & Utility", "Residential"]
                    }
                ]
            }
        ]
    }
}
