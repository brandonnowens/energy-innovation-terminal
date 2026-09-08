"""Tier 3 States (Ranks 9-12): Washington, North Carolina, Massachusetts, Michigan."""

TIER3_DATA = {
    "WA": {
        "state_code": "WA",
        "state_name": "Washington",
        "gdp_billions": 801,
        "rank": 9,
        "regulatory_body": "Washington Utilities and Transportation Commission (UTC)",
        "utilities": [
            {
                "name": "Puget Sound Energy",
                "short_name": "PSE",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Puget Energy",
                "website": "https://www.pse.com",
                "domain": "pse.com",
                "city": "Bellevue",
                "state": "WA",
                "zip_code": "98004",
                "service_territory": "Puget Sound Region (King, Pierce, Snohomish, Kitsap, Thurston, Whatcom, Skagit)",
                "description": "Washington state's oldest local energy utility, providing electric and natural gas service to approximately 1.5 million customers.",
                "logo_domain": "pse.com",
                "founded_year": 1873,
                "programs": [
                    {
                        "name": "PSE Clean Energy Transformation Act (CETA) & Microgrid Fund",
                        "program_type": "innovation",
                        "description": "Clean energy innovation fund established under CETA, funding community microgrids (Tenino, Bainbridge Island), battery storage, and VPPs.",
                        "url": "https://www.pse.com/cleanenergy",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "PSE-CETA-MICRO-2026",
                        "name": "PSE Community Microgrid & Clean Energy Innovation RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "grant",
                        "total_funding": 32000000.0,
                        "max_per_award": 6000000.0,
                        "short_description": "Competitive funding for community microgrids, distributed battery storage, and smart grid resilience in tribal and vulnerable communities.",
                        "service_territory": "Puget Sound / Western Washington",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.pse.com/pages/suppliers-and-contractors",
                        "year": 2026,
                        "keywords": "CETA, microgrid, Tenino, Bainbridge Island, battery storage, PSE, tribal energy",
                        "technologies": ["Microgrids & Resilience", "Energy Storage", "Solar PV"],
                        "sectors": ["Electric Grid & Utility", "Government & Municipal", "Residential"],
                        "fuels": ["Electricity", "Storage & Chemical"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "PSE-AWD-2025-01",
                        "recipient_name": "OneEnergy Renewables",
                        "recipient_type": "company",
                        "project_title": "Tenino High School Community Solar + Storage Resilient Microgrid Hub",
                        "award_amount": 5800000.0,
                        "year": 2025,
                        "recipient_city": "Seattle",
                        "recipient_state": "WA",
                        "latitude": 47.6062,
                        "longitude": -122.3321,
                        "pi_name": "Bill Eddie",
                        "opportunity_sol_num": "PSE-CETA-MICRO-2026",
                        "technologies": ["Microgrids & Resilience", "Solar PV", "Energy Storage"],
                        "sectors": ["Government & Municipal", "Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Seattle City Light",
                "short_name": "Seattle City Light",
                "org_type": "utility",
                "sub_type": "Municipal Utility / Public Power",
                "parent_holding_company": "City of Seattle",
                "website": "https://www.seattle.gov/city-light",
                "domain": "seattle.gov",
                "city": "Seattle",
                "state": "WA",
                "zip_code": "98104",
                "service_territory": "City of Seattle and surrounding metropolitan municipalities",
                "description": "Public utility providing reliable, affordable and environmentally responsible electricity to over 490,000 customers in the City of Seattle and surrounding areas.",
                "logo_domain": "seattle.gov",
                "founded_year": 1902,
                "programs": [
                    {
                        "name": "Seattle City Light Grid Modernization & Maritime Decarbonization",
                        "program_type": "innovation",
                        "description": "Pioneering shore power for cruise ships and maritime electrification, advanced grid sensors, and urban microgrids.",
                        "url": "https://www.seattle.gov/city-light/clean-energy",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "SCL-PORT-SHORE-2026",
                        "name": "Seattle City Light Port of Seattle Shore Power & Heavy Fleet Electrification RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 25000000.0,
                        "max_per_award": 8000000.0,
                        "short_description": "Procurement of high-capacity shore power converters, dynamic marine substations, and heavy-duty drayage truck charging systems.",
                        "service_territory": "Seattle Waterfront / Duwamish Valley",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://seattle.gov/city-light/business-customers",
                        "year": 2026,
                        "keywords": "shore power, maritime decarbonization, Port of Seattle, heavy EV charging, SCL",
                        "technologies": ["EV Charging & Infrastructure", "Electric Vehicles & Clean Transit", "Power Electronics & Inverters"],
                        "sectors": ["Transportation", "Industry & Manufacturing", "Electric Grid & Utility"],
                        "fuels": ["Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "SCL-AWD-2024-01",
                        "recipient_name": "ABB Inc.",
                        "recipient_type": "company",
                        "project_title": "Shore-to-Ship Megawatt Static Frequency Converters for Pier 66 Cruise Terminal",
                        "award_amount": 7200000.0,
                        "year": 2024,
                        "recipient_city": "Bellevue",
                        "recipient_state": "WA",
                        "latitude": 47.6101,
                        "longitude": -122.2015,
                        "pi_name": "Dave Sterlace",
                        "opportunity_sol_num": "SCL-PORT-SHORE-2026",
                        "technologies": ["Power Electronics & Inverters", "EV Charging & Infrastructure"],
                        "sectors": ["Transportation", "Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Snohomish County PUD",
                "short_name": "SnoPUD",
                "org_type": "utility",
                "sub_type": "Public Utility District / Public Power",
                "parent_holding_company": "Snohomish County PUD Board of Commissioners",
                "website": "https://www.snopud.com",
                "domain": "snopud.com",
                "city": "Everett",
                "state": "WA",
                "zip_code": "98201",
                "service_territory": "Snohomish County and Camano Island",
                "description": "Second largest publicly owned utility in Washington, serving more than 370,000 electric customers and national leader in modular microgrid standards (MESA).",
                "logo_domain": "snopud.com",
                "founded_year": 1949,
                "programs": [
                    {
                        "name": "SnoPUD Arlington Microgrid & Clean Energy Center (MESA)",
                        "program_type": "innovation",
                        "description": "Modular Energy Storage Architecture (MESA) demonstration, clean tech testbed, and 500kW solar + 1MW/1.4MWh battery with V2G fleet.",
                        "url": "https://www.snopud.com/community/clean-energy-center/",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "SNOPUD-MESA-V2G-2026",
                        "name": "SnoPUD Modular Energy Storage & V2G Fleet Integration RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 15000000.0,
                        "max_per_award": 5000000.0,
                        "short_description": "Procurement of open-standard MESA energy storage components, automated V2G bi-directional power flow, and local microgrid controllers.",
                        "service_territory": "Snohomish County & Camano Island",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.snopud.com/bids",
                        "year": 2026,
                        "keywords": "MESA, open standard, V2G, Arlington microgrid, energy storage, SnoPUD",
                        "technologies": ["Energy Storage", "Microgrids & Resilience", "EV Charging & Infrastructure"],
                        "sectors": ["Electric Grid & Utility", "Transportation"],
                        "fuels": ["Electricity", "Storage & Chemical"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "SNOPUD-AWD-2024-01",
                        "recipient_name": "Doosan GridTech",
                        "recipient_type": "company",
                        "project_title": "DESS Open-Standard MESA Storage Controller and Dynamic Optimizer for Arlington Microgrid",
                        "award_amount": 4500000.0,
                        "year": 2024,
                        "recipient_city": "Seattle",
                        "recipient_state": "WA",
                        "latitude": 47.6062,
                        "longitude": -122.3321,
                        "pi_name": "Daejin Choi",
                        "opportunity_sol_num": "SNOPUD-MESA-V2G-2026",
                        "technologies": ["Energy Storage", "Microgrids & Resilience"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "NC": {
        "state_code": "NC",
        "state_name": "North Carolina",
        "gdp_billions": 794,
        "rank": 10,
        "regulatory_body": "North Carolina Utilities Commission (NCUC)",
        "utilities": [
            {
                "name": "Duke Energy Carolinas",
                "short_name": "Duke Carolinas",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Duke Energy",
                "website": "https://www.duke-energy.com",
                "domain": "duke-energy.com",
                "city": "Charlotte",
                "state": "NC",
                "zip_code": "28202",
                "service_territory": "Piedmont & Western North Carolina (Charlotte, Raleigh-Durham, Greensboro, Winston-Salem, Asheville)",
                "description": "Duke Energy's largest regulated electric operating subsidiary, providing electricity to approximately 2.8 million customers in North Carolina.",
                "logo_domain": "duke-energy.com",
                "founded_year": 1904,
                "programs": [
                    {
                        "name": "Duke Energy Carolinas Carbon Plan & Microgrid Innovation",
                        "program_type": "innovation",
                        "description": "Carbon Plan-mandated offshore wind development, advanced nuclear SMR evaluation, grid-scale battery storage (Hot Springs, Asheville), and non-wires alternatives.",
                        "url": "https://www.duke-energy.com/our-company/carbon-plan",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "DEC-CARBON-BESS-2026",
                        "name": "Duke Energy Carolinas Mountain & Rural Microgrid Storage RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 65000000.0,
                        "max_per_award": 20000000.0,
                        "short_description": "Procurement of microgrid battery storage systems and advanced inverters in rugged Western NC mountain communities (Hot Springs, Mount Sterling).",
                        "service_territory": "Western North Carolina / Appalachian Mountain Region",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.duke-energy.com/partner-with-us/suppliers",
                        "year": 2026,
                        "keywords": "Hot Springs microgrid, mountain resilience, BESS, Carbon Plan, Duke Energy, Asheville",
                        "technologies": ["Microgrids & Resilience", "Energy Storage", "Solar PV"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "DEC-AWD-2025-01",
                        "recipient_name": "Invenergy LLC",
                        "recipient_type": "company",
                        "project_title": "Hot Springs Microgrid 4MW/16MWh Lithium-Iron Phosphate Battery Energy Storage System",
                        "award_amount": 18500000.0,
                        "year": 2025,
                        "recipient_city": "Chicago",
                        "recipient_state": "IL",
                        "latitude": 41.8781,
                        "longitude": -87.6298,
                        "pi_name": "Michael Polsky",
                        "opportunity_sol_num": "DEC-CARBON-BESS-2026",
                        "technologies": ["Energy Storage", "Microgrids & Resilience"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "North Carolina Electric Membership Corp",
                "short_name": "NCEMC",
                "org_type": "utility",
                "sub_type": "Generation & Transmission Cooperative",
                "parent_holding_company": "NC Electric Cooperatives",
                "website": "https://www.ncelectriccooperatives.com",
                "domain": "ncelectriccooperatives.com",
                "city": "Raleigh",
                "state": "NC",
                "zip_code": "27616",
                "service_territory": "Rural North Carolina (covering 26 independent distribution co-ops)",
                "description": "Generation and transmission cooperative owned by 26 local electric co-ops providing power to 2.8 million North Carolinians across 93 of the state's 100 counties.",
                "logo_domain": "ncelectriccooperatives.com",
                "founded_year": 1949,
                "programs": [
                    {
                        "name": "NCEMC Microgrid Innovation Network (Ocracoke, Butler Farms, Rose Acre)",
                        "program_type": "innovation",
                        "description": "National model for rural agricultural, island, and industrial microgrids integrating solar, swine biogas, and battery storage.",
                        "url": "https://www.ncelectriccooperatives.com/energy-innovation/microgrids/",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "NCEMC-AGRI-MICRO-2026",
                        "name": "NCEMC Agricultural Biogas & Resilient Microgrid Innovation RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "grant",
                        "total_funding": 20000000.0,
                        "max_per_award": 5000000.0,
                        "short_description": "Competitive funding for on-farm swine waste anaerobic digester microgrids, island microgrid storage, and co-op demand flexibility.",
                        "service_territory": "Eastern and Rural North Carolina",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.ncelectriccooperatives.com",
                        "year": 2026,
                        "keywords": "biogas, anaerobic digestion, agricultural microgrid, Ocracoke Island, NCEMC, co-op",
                        "technologies": ["Bioenergy & Biogas", "Microgrids & Resilience", "Energy Storage"],
                        "sectors": ["Agriculture & Forestry", "Electric Grid & Utility"],
                        "fuels": ["Biomass & Biogas", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "NCEMC-AWD-2024-01",
                        "recipient_name": "Butler Farms / Tideland EMC",
                        "recipient_type": "company",
                        "project_title": "Swine Waste Biogas Microgrid with Automated Islanding and Battery Peak Shaving",
                        "award_amount": 4100000.0,
                        "year": 2024,
                        "recipient_city": "Lillington",
                        "recipient_state": "NC",
                        "latitude": 35.3985,
                        "longitude": -78.8145,
                        "pi_name": "Tom Butler",
                        "opportunity_sol_num": "NCEMC-AGRI-MICRO-2026",
                        "technologies": ["Bioenergy & Biogas", "Microgrids & Resilience"],
                        "sectors": ["Agriculture & Forestry", "Electric Grid & Utility"]
                    }
                ]
            }
        ]
    },
    "MA": {
        "state_code": "MA",
        "state_name": "Massachusetts",
        "gdp_billions": 734,
        "rank": 11,
        "regulatory_body": "Massachusetts Department of Public Utilities (DPU) / MassCEC",
        "utilities": [
            {
                "name": "Eversource Energy (Massachusetts)",
                "short_name": "Eversource MA",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "Eversource Energy",
                "website": "https://www.eversource.com",
                "domain": "eversource.com",
                "city": "Boston",
                "state": "MA",
                "zip_code": "02199",
                "service_territory": "Greater Boston, Eastern and Western Massachusetts, Cape Cod & Martha's Vineyard",
                "description": "New England's largest energy delivery company, serving approximately 1.8 million electric and natural gas customers in Massachusetts.",
                "logo_domain": "eversource.com",
                "founded_year": 1966,
                "programs": [
                    {
                        "name": "Eversource GeoGrid Networked Geothermal Pilot (Framingham)",
                        "program_type": "innovation",
                        "description": "The nation's first utility-installed networked geothermal thermal energy network (TEN), connecting residential and commercial buildings.",
                        "url": "https://www.eversource.com/content/residential/save-money-energy/explore-alternatives/geothermal-energy/networked-geothermal",
                        "active": True,
                        "target_stage": "demonstration",
                    },
                    {
                        "name": "Eversource Clean Peak Energy Storage RFP",
                        "program_type": "deployment",
                        "description": "Procurement of utility-scale storage (e.g. Outer Cape Cod 25MW BESS) to avoid undersea cable replacement.",
                        "url": "https://www.eversource.com/procurement",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "EVRMA-GEOGRID-2026",
                        "name": "Eversource Networked Geothermal (TEN) Phase II Solicitations",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 35000000.0,
                        "max_per_award": 10000000.0,
                        "short_description": "Engineering, borehole drilling, and thermal heat pump integration for expanding utility networked geothermal across Framingham and MetroWest.",
                        "service_territory": "Framingham / MetroWest Massachusetts",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.eversource.com/suppliers",
                        "year": 2026,
                        "keywords": "geothermal network, GeoGrid, thermal energy network, Framingham, heat pump, Eversource",
                        "technologies": ["Geothermal Energy", "Heat Pumps & Building Electrification"],
                        "sectors": ["Buildings", "Residential", "Commercial"],
                        "fuels": ["Geothermal", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "EVRMA-AWD-2024-01",
                        "recipient_name": "HEET (Home Energy Efficiency Team)",
                        "recipient_type": "nonprofit",
                        "project_title": "Networked Geothermal Shared Loop Design and Community Co-Design Framework",
                        "award_amount": 3200000.0,
                        "year": 2024,
                        "recipient_city": "Cambridge",
                        "recipient_state": "MA",
                        "latitude": 42.3736,
                        "longitude": -71.1097,
                        "pi_name": "Zeyneb Magavi",
                        "opportunity_sol_num": "EVRMA-GEOGRID-2026",
                        "technologies": ["Geothermal Energy", "Heat Pumps & Building Electrification"],
                        "sectors": ["Buildings", "Residential"]
                    }
                ]
            },
            {
                "name": "National Grid Massachusetts",
                "short_name": "National Grid MA",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "National Grid USA",
                "website": "https://www.nationalgridus.com/MA-Home",
                "domain": "nationalgridus.com",
                "city": "Waltham",
                "state": "MA",
                "zip_code": "02451",
                "service_territory": "Central, Eastern, and Western Massachusetts (Worcester, Lowell, Brockton, North Shore)",
                "description": "Electric and gas distribution utility providing power to 1.3 million electric customers and 900,000 gas customers across 168 Massachusetts communities.",
                "logo_domain": "nationalgridus.com",
                "founded_year": 2000,
                "programs": [
                    {
                        "name": "National Grid MA Future of Heat & Geothermal Network Pilot",
                        "program_type": "innovation",
                        "description": "Lowell networked geothermal demonstration and clean hydrogen/RNG heating pathway pilots.",
                        "url": "https://www.nationalgridus.com/clean-energy-vision",
                        "active": True,
                        "target_stage": "demonstration",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "NGRIDMA-HEAT-2026",
                        "name": "National Grid MA Urban Thermal Network & Electrification RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 30000000.0,
                        "max_per_award": 8000000.0,
                        "short_description": "Competitive solicitation for urban district thermal energy network installation, ground-source heat pump retrofits, and thermal monitoring in Lowell, MA.",
                        "service_territory": "Lowell / Merrimack Valley",
                        "utility_program_type": "Pilot / Demonstration",
                        "procurement_portal_url": "https://www.nationalgridus.com/doing-business-with-us",
                        "year": 2026,
                        "keywords": "thermal network, geothermal, Lowell, building electrification, National Grid MA",
                        "technologies": ["Geothermal Energy", "Heat Pumps & Building Electrification"],
                        "sectors": ["Buildings", "Residential", "Commercial"],
                        "fuels": ["Geothermal", "Electricity"],
                        "stage": "Pilot & Demonstration",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "NGRIDMA-AWD-2025-01",
                        "recipient_name": "University of Massachusetts Lowell",
                        "recipient_type": "university",
                        "project_title": "Lowell Urban Thermal Energy Network Instrumentation and Thermal Efficiency Validation",
                        "award_amount": 4800000.0,
                        "year": 2025,
                        "recipient_city": "Lowell",
                        "recipient_state": "MA",
                        "latitude": 42.6334,
                        "longitude": -71.3162,
                        "pi_name": "Dr. Christopher Niezrecki",
                        "opportunity_sol_num": "NGRIDMA-HEAT-2026",
                        "technologies": ["Geothermal Energy", "Heat Pumps & Building Electrification"],
                        "sectors": ["Buildings", "Government & Municipal"]
                    }
                ]
            }
        ]
    },
    "MI": {
        "state_code": "MI",
        "state_name": "Michigan",
        "gdp_billions": 673,
        "rank": 12,
        "regulatory_body": "Michigan Public Service Commission (MPSC)",
        "utilities": [
            {
                "name": "DTE Energy",
                "short_name": "DTE Energy",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "DTE Energy Company",
                "website": "https://www.dteenergy.com",
                "domain": "dteenergy.com",
                "city": "Detroit",
                "state": "MI",
                "zip_code": "48226",
                "service_territory": "Southeast Michigan (Detroit metropolitan area, Ann Arbor, Thumb region)",
                "description": "Diversified energy company providing electricity to 2.3 million customers and natural gas to 1.3 million customers in Southeast Michigan.",
                "logo_domain": "dteenergy.com",
                "founded_year": 1903,
                "programs": [
                    {
                        "name": "DTE CleanVision Plan & Storage Demonstrations",
                        "program_type": "innovation",
                        "description": "Phasing out coal by 2032 and deploying 2,950MW of battery energy storage, Trenton Channel storage conversion, and smart grid automation.",
                        "url": "https://www.dteenergy.com/cleanvision",
                        "active": True,
                        "target_stage": "deployment",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "DTE-TRENTON-BESS-2026",
                        "name": "DTE Trenton Channel Energy Storage Center RFP",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 70000000.0,
                        "max_per_award": 30000000.0,
                        "short_description": "Procurement of 220MW/880MWh battery energy storage systems to repurpose the retired Trenton Channel Power Plant coal site into Michigan's largest storage hub.",
                        "service_territory": "Southeast Michigan / Detroit River",
                        "utility_program_type": "Innovation RFP",
                        "procurement_portal_url": "https://www.dteenergy.com/suppliers",
                        "year": 2026,
                        "keywords": "Trenton Channel, coal-to-storage, BESS, CleanVision, DTE, Detroit",
                        "technologies": ["Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Storage & Chemical", "Electricity"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "DTE-AWD-2025-01",
                        "recipient_name": "Powin Energy Corporation",
                        "recipient_type": "company",
                        "project_title": "Centipede Battery Energy Storage Platform for Trenton Channel Re-powering",
                        "award_amount": 28000000.0,
                        "year": 2025,
                        "recipient_city": "Tualatin",
                        "recipient_state": "OR",
                        "latitude": 45.3839,
                        "longitude": -122.7865,
                        "pi_name": "Jeff Waters",
                        "opportunity_sol_num": "DTE-TRENTON-BESS-2026",
                        "technologies": ["Energy Storage"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            },
            {
                "name": "Consumers Energy",
                "short_name": "Consumers Energy",
                "org_type": "utility",
                "sub_type": "Investor-Owned Utility (IOU)",
                "parent_holding_company": "CMS Energy",
                "website": "https://www.consumersenergy.com",
                "domain": "consumersenergy.com",
                "city": "Jackson",
                "state": "MI",
                "zip_code": "49201",
                "service_territory": "Lower Peninsula of Michigan (Grand Rapids, Lansing, Flint, Kalamazoo, Saginaw)",
                "description": "Michigan's largest utility, providing electricity and/or natural gas to 6.8 million of the state's 10 million residents across all 68 Lower Peninsula counties.",
                "logo_domain": "consumersenergy.com",
                "founded_year": 1886,
                "programs": [
                    {
                        "name": "Consumers Energy Clean Energy Plan & Non-Wires Alternatives",
                        "program_type": "innovation",
                        "description": "Eliminating coal by 2025 and deploying 550MW of battery storage, grid modernization, and NWA pilots in West Michigan.",
                        "url": "https://www.consumersenergy.com/cleanenergy",
                        "active": True,
                        "target_stage": "scale-up",
                    }
                ],
                "opportunities": [
                    {
                        "solicitation_number": "CMS-NWA-BESS-2026",
                        "name": "Consumers Energy Non-Wires Alternatives & Grid Storage Solicitations",
                        "solicitation_type": "RFP",
                        "status": "open",
                        "funding_type": "contract",
                        "total_funding": 40000000.0,
                        "max_per_award": 12000000.0,
                        "short_description": "Procurement of battery storage, commercial demand response, and smart grid DERMS to resolve substation congestion in Grand Rapids and Kalamazoo.",
                        "service_territory": "Lower Peninsula / West Michigan",
                        "utility_program_type": "NWA",
                        "procurement_portal_url": "https://www.consumersenergy.com/suppliers",
                        "year": 2026,
                        "keywords": "NWA, BESS, Clean Energy Plan, Grand Rapids, Consumers Energy, CMS",
                        "technologies": ["Non-Wires Solutions (NWS)", "Energy Storage", "Grid Modernization & Smart Grid"],
                        "sectors": ["Electric Grid & Utility"],
                        "fuels": ["Electricity", "Storage & Chemical"],
                        "stage": "Deployment & Infrastructure",
                    }
                ],
                "awards": [
                    {
                        "external_award_id": "CMS-AWD-2024-01",
                        "recipient_name": "Energy Vault, Inc.",
                        "recipient_type": "company",
                        "project_title": "B-VAULT Modular Battery Energy Storage System for Distribution Deferral",
                        "award_amount": 11500000.0,
                        "year": 2024,
                        "recipient_city": "Westlake Village",
                        "recipient_state": "CA",
                        "latitude": 34.1458,
                        "longitude": -118.8056,
                        "pi_name": "Robert Piconi",
                        "opportunity_sol_num": "CMS-NWA-BESS-2026",
                        "technologies": ["Energy Storage", "Non-Wires Solutions (NWS)"],
                        "sectors": ["Electric Grid & Utility"]
                    }
                ]
            }
        ]
    }
}
