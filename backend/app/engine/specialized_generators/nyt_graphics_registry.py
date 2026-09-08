"""
NYT-Grade Topic-Specific Geospatial Clusters & Knowledge Graph Registry.
Provides verified coordinates, funding metrics, callout leader annotations,
and tailored institutional consortium topologies for every executive monograph.
"""

from typing import Dict, Any, List, Tuple

NYT_GRAPHICS_REGISTRY: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # 1. CLEAN POWER GENERATION
    # =========================================================================
    "clean_gen_dossier": {
        "map_title": "Geospatial Offshore Wind Ports, Perovskite Solar & EGS Geothermal Siting",
        "clusters": [
            ("S. Brooklyn Terminal", 40.66, -74.01, 560, '#0F172A', "$860M OSW Hub"),
            ("Port of Albany", 42.63, -73.76, 420, '#0284C7', "$350M Towers"),
            ("New Bedford Port", 41.63, -70.92, 440, '#0284C7', "$450M Marine Port"),
            ("Utah FORGE", 38.50, -112.90, 480, '#059669', "$220M EGS Testbed"),
            ("Fervo Cape Station", 39.40, -117.10, 520, '#059669', "$400M Baseload EGS"),
            ("NREL Flatirons", 39.91, -105.22, 380, '#0284C7', "$310M Solar/Wind R&D"),
            ("Humboldt Bay", 40.76, -124.22, 490, '#0F172A', "$426M Floating OSW"),
            ("Morro Bay", 35.37, -120.85, 470, '#0F172A', "$620M Deep OSW Block"),
            ("Plant Vogtle", 33.14, -81.76, 580, '#D97706', "$3.4B Nuclear Baseload"),
        ],
        "callouts": [
            {"name": "S. Brooklyn & Albany", "lat": 41.6, "lng": -73.8, "text": "South Brooklyn & Port of Albany\n$1.21B OSW Port Staging & Tower Hub", "offset_x": 14, "offset_y": 6},
            {"name": "Utah FORGE & Fervo", "lat": 38.9, "lng": -114.5, "text": "Utah FORGE & Fervo Energy\n400 MW Deep Commercial EGS", "offset_x": -20, "offset_y": -5},
            {"name": "Humboldt Deep OSW", "lat": 40.7, "lng": -124.2, "text": "Humboldt Deepwater Lease Block\nFloating OSW Continental Shelf", "offset_x": -18, "offset_y": 7},
        ],
        "network_title": "Clean Generation Consortia: Offshore Developers, Ports & Labs",
        "nodes": [
            ("BOEM / DOE Wind", 0.0, 0.0, 560, '#0F172A', 'Federal Agency Core'),
            ("Ørsted / Equinor", -0.42, 0.35, 490, '#0284C7', 'Offshore Wind Prime'),
            ("Cornell Atkinson", 0.45, 0.32, 440, '#0284C7', 'University R&D Anchor'),
            ("GE Vernova OSW", 0.38, -0.38, 460, '#059669', 'Turbine Equipment OEM'),
            ("Fervo Energy", -0.48, -0.32, 450, '#059669', 'Deep EGS Scaleup'),
            ("NYSERDA OSW Team", 0.0, 0.58, 420, '#0F172A', 'State Energy Authority'),
            ("NREL Wind Center", -0.58, 0.05, 390, '#0284C7', 'National Laboratory'),
            ("ConEd Interconnects", 0.56, -0.08, 380, '#D97706', 'Subsea Grid Utility')
        ],
        "edges": [
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 3), (1, 5), (1, 7),
            (2, 6), (3, 7), (4, 6), (5, 1), (5, 7), (6, 0), (2, 5)
        ]
    },

    # =========================================================================
    # 2. ENERGY STORAGE & BATTERIES
    # =========================================================================
    "energy_storage_dossier": {
        "map_title": "Geospatial 100-Hr LDES, Gigafactories & Closed-Loop Recycling Atlas",
        "clusters": [
            ("Form Energy Weirton", 40.41, -80.58, 560, '#059669', "$760M Iron-Air Plant"),
            ("NY-BEST Testbed", 42.65, -73.75, 440, '#0F172A', "$180M Safety Center"),
            ("Binghamton Battery-NY", 42.09, -75.91, 480, '#0284C7', "$113M Nobel Hub"),
            ("Tesla Lathrop", 37.82, -121.28, 540, '#0F172A', "$1.5B Megapack Plant"),
            ("Solid Power / QS", 39.97, -105.13, 470, '#0284C7', "$650M Solid-State"),
            ("Eos Turtle Creek", 40.40, -79.82, 430, '#059669', "$398M Zinc Flow Battery"),
            ("Redwood Materials", 39.52, -119.81, 550, '#059669', "$2.0B Cathode Recycling"),
            ("Ambri Liquid Metal", 42.34, -71.55, 410, '#0284C7', "$144M Antimony LDES"),
            ("ConEd Astoria BESS", 40.77, -73.91, 460, '#D97706', "$275M Urban Peaker")
        ],
        "callouts": [
            {"name": "Form Energy Weirton", "lat": 40.4, "lng": -80.5, "text": "Form Energy Weirton WV\n$760M 100-Hour Iron-Air Facility", "offset_x": 16, "offset_y": 7},
            {"name": "Binghamton Battery-NY", "lat": 42.1, "lng": -75.9, "text": "Binghamton University Battery-NY\nWhittingham Nobel Chemistries Hub", "offset_x": 14, "offset_y": -6},
            {"name": "Redwood Materials", "lat": 39.5, "lng": -119.8, "text": "Redwood Materials Sparks NV\n$2.0B Closed-Loop Recycling", "offset_x": -18, "offset_y": 6}
        ],
        "network_title": "Storage Innovation Network: LDES Pioneers, Universities & Utilities",
        "nodes": [
            ("DOE OE / LDES Shot", 0.0, 0.0, 560, '#0F172A', 'Federal Storage Core'),
            ("Form Energy", -0.42, 0.35, 500, '#059669', '100-Hr LDES Pioneer'),
            ("Binghamton Univ.", 0.45, 0.32, 470, '#0284C7', 'Battery-NY Research'),
            ("NY-BEST Center", 0.38, -0.38, 440, '#0F172A', 'Fire Safety Testbed'),
            ("ConEd BESS Ops", -0.48, -0.32, 450, '#D97706', 'Regulated Grid Utility'),
            ("Argonne (ReCell)", 0.0, 0.58, 430, '#0284C7', 'Recycling National Lab'),
            ("NY Green Bank", -0.58, 0.05, 410, '#059669', 'First-Loss Capital'),
            ("Tesla & Fluence", 0.56, -0.08, 420, '#0F172A', 'Utility BESS Primes')
        ],
        "edges": [
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 6),
            (2, 5), (2, 3), (3, 4), (4, 7), (5, 6), (6, 1), (7, 4)
        ]
    },

    # =========================================================================
    # 3. ALTERNATIVE FUELS & CLEAN HYDROGEN
    # =========================================================================
    "alt_fuels_dossier": {
        "map_title": "Geospatial Regional Clean Hydrogen Hubs & Direct Air Capture Atlas",
        "clusters": [
            ("MACH2 H2 Hub", 39.74, -75.54, 560, '#0284C7', "$1.2B Electrolyzer Hub"),
            ("ARCHES CA Hub", 34.05, -118.24, 550, '#0284C7', "$1.2B Heavy Transit H2"),
            ("HyVelocity Gulf", 29.76, -95.36, 570, '#0F172A', "$1.2B Industrial H2"),
            ("ARCH2 Appalachian", 39.00, -80.50, 500, '#0284C7', "$925M Clean Gas Hub"),
            ("Midwest MACHH", 41.87, -87.62, 520, '#0284C7', "$1.0B Steelmaking H2"),
            ("Plug Power Giga", 43.15, -77.60, 460, '#059669', "$290M PEM Stacks"),
            ("Project Bison DAC", 41.58, -109.20, 490, '#059669', "$550M Basalt DAC"),
            ("Heirloom Tracy", 37.73, -121.42, 450, '#059669', "$200M Direct Carbon"),
            ("LanzaJet SAF", 32.37, -82.59, 470, '#D97706', "$250M Alcohol SAF")
        ],
        "callouts": [
            {"name": "MACH2 & Plug Power", "lat": 41.0, "lng": -76.0, "text": "MACH2 & Plug Power Rochester\n$1.49B PEM Electrolyzer Ecosystem", "offset_x": 16, "offset_y": 7},
            {"name": "HyVelocity Gulf Coast", "lat": 29.8, "lng": -95.4, "text": "HyVelocity Gulf Coast Hub\nIndustrial Refining & Ammonia Decarb", "offset_x": 14, "offset_y": -6},
            {"name": "Project Bison WY", "lat": 41.6, "lng": -109.2, "text": "Project Bison Wyoming\nMegaton Direct Air Basalt Capture", "offset_x": -18, "offset_y": 6}
        ],
        "network_title": "Clean Molecules Network: Hydrogen Hubs, Electrolyzer OEMs & DAC",
        "nodes": [
            ("DOE Hydrogen Shot", 0.0, 0.0, 560, '#0F172A', 'Federal $1/kg Program'),
            ("Plug Power", -0.42, 0.35, 490, '#059669', 'PEM Electrolyzer OEM'),
            ("Brookhaven Lab", 0.45, 0.32, 440, '#0284C7', 'Electrochemical R&D'),
            ("Climeworks & Heirloom", 0.38, -0.38, 470, '#059669', 'DAC Frontier Ventures'),
            ("Columbia Energy Ctr", -0.48, -0.32, 430, '#0284C7', 'Carbon Policy & Markets'),
            ("Air Liquide & Linde", 0.0, 0.58, 460, '#0F172A', 'Industrial Gas Primes'),
            ("MACH2 Consortia", -0.58, 0.05, 450, '#0284C7', 'Regional H2 Hub Lead'),
            ("United/Delta Coalition", 0.56, -0.08, 410, '#D97706', 'Commercial SAF Off-Takers')
        ],
        "edges": [
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 6), (1, 5), (2, 4),
            (3, 4), (5, 6), (6, 7), (1, 7), (3, 0), (5, 0), (2, 0)
        ]
    },

    # =========================================================================
    # 4. ADVANCED NUCLEAR & SMRs
    # =========================================================================
    "advanced_nuclear_smr": {
        "map_title": "Geospatial SMR Demonstrations, TRISO Fuel & Fusion Energy Atlas",
        "clusters": [
            ("TerraPower Natrium", 41.79, -110.53, 570, '#059669', "$2.0B Sodium Fast SMR"),
            ("Kairos Hermes", 36.01, -84.26, 520, '#059669', "$303M Molten Salt Demo"),
            ("X-energy Seadrift", 28.38, -96.71, 510, '#0284C7', "$1.2B HTGR Clean Heat"),
            ("Idaho National Lab", 43.49, -112.03, 550, '#0F172A', "$1.4B Microreactor Hub"),
            ("Centrus Piketon", 39.07, -83.01, 460, '#0F172A', "$150M HALEU Cascade"),
            ("CFS SPARC Fusion", 42.53, -71.61, 560, '#059669', "$1.8B 20T Tokamak"),
            ("Helion Polaris", 47.97, -122.20, 480, '#059669', "$500M Magneto Fusion"),
            ("Constellation Crane", 40.15, -76.72, 540, '#D97706', "$1.6B AI Hyperscale PPA")
        ],
        "callouts": [
            {"name": "TerraPower Natrium", "lat": 41.8, "lng": -110.5, "text": "TerraPower Natrium Kemmerer WY\n345 MWe Sodium Fast Reactor Plant", "offset_x": 16, "offset_y": 7},
            {"name": "Kairos Hermes TN", "lat": 36.0, "lng": -84.3, "text": "Kairos Power Hermes Oak Ridge\n$303M Fluoride Salt High-Temp Demo", "offset_x": 14, "offset_y": -6},
            {"name": "CFS SPARC Fusion MA", "lat": 42.5, "lng": -71.6, "text": "Commonwealth Fusion SPARC\n20-Tesla Superconducting Tokamak", "offset_x": 15, "offset_y": 7}
        ],
        "network_title": "Advanced Nuclear Network: ARDP Scaleups, National Labs & Utilities",
        "nodes": [
            ("DOE ARDP Office", 0.0, 0.0, 560, '#0F172A', 'Federal Nuclear Core'),
            ("TerraPower", -0.42, 0.35, 510, '#059669', 'Sodium Fast SMR'),
            ("Kairos Power", 0.45, 0.32, 490, '#059669', 'Molten Salt TRISO'),
            ("Idaho National Lab", 0.38, -0.38, 480, '#0F172A', 'Lead Nuclear Lab'),
            ("MIT Plasma Center", -0.48, -0.32, 450, '#0284C7', 'Superconducting Fusion'),
            ("Constellation Fleet", 0.0, 0.58, 470, '#D97706', 'Nuclear Baseload Operator'),
            ("CFS SPARC", -0.58, 0.05, 480, '#059669', 'Commercial Fusion'),
            ("Centrus Energy", 0.56, -0.08, 420, '#0F172A', 'HALEU Fuel Supplier')
        ],
        "edges": [
            (0, 1), (0, 2), (0, 3), (0, 7), (1, 3), (2, 3), (1, 5), (2, 5),
            (4, 6), (4, 0), (6, 5), (7, 1), (7, 2), (3, 0), (5, 0)
        ]
    },

    # =========================================================================
    # 5. GRID MODERNIZATION & TRANSMISSION
    # =========================================================================
    "grid_modernization_dossier": {
        "map_title": "Geospatial HVDC Corridors, Dynamic Line Rating & ISO Control Hubs",
        "clusters": [
            ("Champlain HVDC", 40.71, -74.00, 580, '#0F172A', "$6.0B 1,250 MW Subsea"),
            ("Grain Belt Express", 39.00, -92.00, 570, '#0284C7', "$7.0B 5,000 MW HVDC"),
            ("SunZia Transmission", 33.50, -107.50, 590, '#0284C7', "$8.0B Clean Corridor"),
            ("NYISO Control Ctr", 42.60, -73.70, 440, '#0F172A', "$150M Smart Grid HQ"),
            ("LineVision DLR Hub", 42.36, -71.05, 460, '#059669', "$85M Dynamic Line Sensors"),
            ("Smart Wires Hub", 37.77, -122.41, 450, '#059669', "$120M Power Flow Control"),
            ("CAISO Folsom HQ", 38.67, -121.17, 470, '#0F172A', "$210M Western Market"),
            ("Oak Ridge GRID-C", 35.95, -84.31, 430, '#0284C7', "$240M Cyber Testbed")
        ],
        "callouts": [
            {"name": "Champlain Hudson HVDC", "lat": 42.0, "lng": -74.0, "text": "Champlain Hudson Power Express\n$6.0B Subsea Clean Hydro Intertie", "offset_x": 16, "offset_y": 7},
            {"name": "Grain Belt & SunZia", "lat": 35.0, "lng": -102.0, "text": "SunZia & Grain Belt HVDC\n13,000 MW Interstate Transmission", "offset_x": 14, "offset_y": -6},
            {"name": "LineVision GETs Hub", "lat": 42.4, "lng": -71.1, "text": "LineVision & Smart Wires\n+40% Dynamic Line Capacity Unlock", "offset_x": 15, "offset_y": -7}
        ],
        "network_title": "Grid Modernization Network: ISOs, Regulators, Utilities & GETs",
        "nodes": [
            ("FERC / Grid Office", 0.0, 0.0, 560, '#0F172A', 'Federal Transmission Core'),
            ("NYISO & CAISO", -0.42, 0.35, 500, '#0F172A', 'Independent Operators'),
            ("Con Edison Grid", 0.45, 0.32, 470, '#D97706', 'Regulated Utility Planning'),
            ("LineVision DLR", 0.38, -0.38, 460, '#059669', 'Dynamic Line Sensors'),
            ("EPRI Power Delivery", -0.48, -0.32, 440, '#0284C7', 'Grid R&D Institute'),
            ("RPI Smart Grid Hub", 0.0, 0.58, 430, '#0284C7', 'University Power Lab'),
            ("GE Vernova Grid", -0.58, 0.05, 470, '#0F172A', 'HVDC Converter OEM'),
            ("National Grid HVDC", 0.56, -0.08, 440, '#D97706', 'Subsea Interconnects')
        ],
        "edges": [
            (0, 1), (0, 2), (0, 6), (1, 2), (1, 3), (2, 3), (2, 7), (3, 4),
            (4, 5), (5, 0), (6, 7), (7, 0), (1, 6), (3, 0)
        ]
    },

    # =========================================================================
    # 6. BUILDING DECARBONIZATION & THERMAL NETWORKS
    # =========================================================================
    "buildings_thermal_dossier": {
        "map_title": "Geospatial District Geothermal Thermal Networks & Clean Heat Hubs",
        "clusters": [
            ("NYC ConEd TENs", 40.74, -73.99, 540, '#059669', "$120M Chelsea Urban TEN"),
            ("Eversource Framingham", 42.27, -71.41, 510, '#059669', "$45M First Utility TEN"),
            ("National Grid Riverhead", 40.91, -72.66, 460, '#0284C7', "$65M Ambient Water Loop"),
            ("Ithaca Decarb", 42.44, -76.50, 480, '#059669', "$100M Citywide Electrification"),
            ("BE-Ex New York", 40.71, -74.00, 470, '#0F172A', "$35M High-Rise Retrofit Hub"),
            ("Carrier Syracuse CoE", 43.04, -76.14, 490, '#0284C7', "$400M EVI Heat Pump Plant"),
            ("MassCEC Clean Heat", 42.35, -71.05, 450, '#0F172A', "$80M Innovation Center")
        ],
        "callouts": [
            {"name": "Eversource Framingham", "lat": 42.3, "lng": -71.4, "text": "Eversource Framingham MA\nFirst Regulated District TENs Loop", "offset_x": 15, "offset_y": 7},
            {"name": "NYC ConEd Chelsea", "lat": 40.7, "lng": -74.0, "text": "NYC Con Edison Chelsea Pilot\nHigh-Rise Urban Waste Heat Recovery", "offset_x": 14, "offset_y": -6},
            {"name": "Carrier & Syracuse CoE", "lat": 43.0, "lng": -76.1, "text": "Carrier & Syracuse CoE\nCold-Climate EVI Heat Pump R&D", "offset_x": -18, "offset_y": 6}
        ],
        "network_title": "Building Thermal Network: Utilities, Heat Pump OEMs & Labor",
        "nodes": [
            ("NYSERDA Clean Heat", 0.0, 0.0, 560, '#0F172A', 'State Program Authority'),
            ("ConEd & Eversource", -0.42, 0.35, 500, '#D97706', 'Utility TENs Operators'),
            ("BE-Ex Resource Ctr", 0.45, 0.32, 450, '#0F172A', 'Building Decarb Hub'),
            ("Steven Winter Assoc.", 0.38, -0.38, 460, '#0284C7', 'Building Science Eng.'),
            ("Syracuse CoE", -0.48, -0.32, 440, '#0284C7', 'HVAC Research Center'),
            ("Carrier / Daikin", 0.0, 0.58, 480, '#059669', 'Heat Pump OEM Primes'),
            ("BlocPower", -0.58, 0.05, 450, '#059669', 'Urban Electrification'),
            ("Labor Pipefitters", 0.56, -0.08, 430, '#0F172A', 'Union Just Transition')
        ],
        "edges": [
            (0, 1), (0, 2), (0, 5), (1, 7), (1, 3), (2, 3), (3, 6), (4, 5),
            (5, 6), (6, 0), (7, 1), (5, 0), (2, 0), (4, 0)
        ]
    },

    # =========================================================================
    # 7. INDUSTRIAL DECARBONIZATION & CLEAN HEAT
    # =========================================================================
    "industrial_decarb_dossier": {
        "map_title": "Geospatial Low-Carbon Steel, Electrochemical Cement & Industrial Heat Atlas",
        "clusters": [
            ("Boston Metal", 42.47, -71.15, 520, '#059669', "$320M Molten Oxide Steel"),
            ("Sublime Systems", 42.20, -72.61, 500, '#059669', "$175M Clean Cement"),
            ("Cleveland-Cliffs", 39.51, -84.40, 560, '#0F172A', "$575M Green H2-DRI"),
            ("CF Industries CCUS", 30.10, -91.00, 540, '#0284C7', "$1.0B Ammonia CCS"),
            ("Heidelberg Mitchell", 38.73, -86.47, 480, '#0F172A', "$500M Oxy-Fuel Cement"),
            ("Electra Iron", 40.01, -105.27, 460, '#059669', "$180M Electro-Refining"),
            ("NREL Process Heat", 39.75, -105.22, 440, '#0284C7', "$160M Thermal Testing")
        ],
        "callouts": [
            {"name": "Boston Metal & Sublime", "lat": 42.4, "lng": -71.5, "text": "Boston Metal & Sublime Systems\nZero-Carbon Steel & Cement Pioneers", "offset_x": 15, "offset_y": 7},
            {"name": "Cleveland-Cliffs OH", "lat": 39.5, "lng": -84.4, "text": "Cleveland-Cliffs Middletown Works\n$575M Green H2-DRI Steelmaking", "offset_x": 14, "offset_y": -6},
            {"name": "CF Industries LA", "lat": 30.1, "lng": -91.0, "text": "CF Industries Donaldsonville\nMegaton Industrial Ammonia CCUS", "offset_x": 14, "offset_y": -7}
        ],
        "network_title": "Industrial Decarb Network: Heavy Primes, Venture Pioneers & DOE",
        "nodes": [
            ("DOE IEDO Office", 0.0, 0.0, 560, '#0F172A', 'Federal Industrial Core'),
            ("Boston Metal", -0.42, 0.35, 490, '#059669', 'Electrochemical Steel'),
            ("Sublime Systems", 0.45, 0.32, 480, '#059669', 'Low-Carbon Cement'),
            ("Cleveland-Cliffs", 0.38, -0.38, 500, '#0F172A', 'Steelmaking Prime'),
            ("MIT Materials Lab", -0.48, -0.32, 450, '#0284C7', 'Electrochemistry R&D'),
            ("NREL Heat Testing", 0.0, 0.58, 440, '#0284C7', 'High-Temp Lab'),
            ("Holcim / Heidelberg", -0.58, 0.05, 460, '#0F172A', 'Global Cement Primes'),
            ("Breakthrough Energy", 0.56, -0.08, 440, '#059669', 'Hardtech Climate VC')
        ],
        "edges": [
            (0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 0), (4, 0), (5, 0),
            (6, 2), (7, 1), (7, 2), (3, 7), (6, 0)
        ]
    },

    # =========================================================================
    # 8. CRITICAL MINERALS & SUPPLY CHAIN
    # =========================================================================
    "critical_minerals_dossier": {
        "map_title": "Geospatial Direct Lithium Extraction, Rare Earths & Recycling Atlas",
        "clusters": [
            ("Thacker Pass Lithium", 41.70, -118.00, 580, '#0F172A', "$2.26B Lithium Mine"),
            ("Salton Sea Brines", 33.20, -115.60, 530, '#059669', "$650M DLE Geothermal"),
            ("Smackover Brines", 33.21, -92.66, 490, '#059669', "$400M Direct Extraction"),
            ("Albemarle Silver Peak", 37.75, -117.63, 510, '#0F172A', "$1.3B Lithium Refining"),
            ("Redwood Materials", 39.52, -119.81, 570, '#059669', "$2.0B Gigafactory Recycling"),
            ("Ascend Elements", 36.86, -87.48, 520, '#059669', "$1.0B Hydro-to-Cathode"),
            ("MP Materials Pass", 35.48, -115.53, 500, '#0F172A', "$700M Rare Earth Magnetics"),
            ("Albany NanoTech WBG", 42.69, -73.83, 470, '#0284C7', "$350M Gallium Semi Hub")
        ],
        "callouts": [
            {"name": "Thacker Pass NV", "lat": 41.7, "lng": -118.0, "text": "Thacker Pass Lithium Americas\n$2.26B Domestic Lithium Mine", "offset_x": 16, "offset_y": 7},
            {"name": "Salton Sea & Smackover", "lat": 33.2, "lng": -115.6, "text": "Salton Sea & Smackover Brines\nDLE Direct Lithium Extraction", "offset_x": 14, "offset_y": -6},
            {"name": "Redwood & Ascend", "lat": 39.5, "lng": -119.8, "text": "Redwood & Ascend Elements\n99%+ Closed-Loop Cathode Recovery", "offset_x": -18, "offset_y": 6}
        ],
        "network_title": "Critical Minerals Network: DLE Innovators, Refiners & Auto OEMs",
        "nodes": [
            ("DOE Critical Materials", 0.0, 0.0, 560, '#0F172A', 'Federal Supply Chain Core'),
            ("Lilac & EnergyX", -0.42, 0.35, 490, '#059669', 'DLE Extraction Innovators'),
            ("Albemarle / Lithium Am.", 0.45, 0.32, 510, '#0F172A', 'Mining & Refining Primes'),
            ("Redwood Materials", 0.38, -0.38, 500, '#059669', 'Closed-Loop Recycling'),
            ("Argonne ReCell Lab", -0.48, -0.32, 450, '#0284C7', 'Battery Recycling Center'),
            ("Binghamton Hub", 0.0, 0.58, 440, '#0284C7', 'Nobel Chemistry Lab'),
            ("MP Materials", -0.58, 0.05, 470, '#0F172A', 'Rare Earth Sintered Magnets'),
            ("Tesla / GM Gigas", 0.56, -0.08, 480, '#D97706', 'Automotive Off-Takers')
        ],
        "edges": [
            (0, 1), (0, 2), (0, 3), (0, 6), (1, 2), (2, 7), (3, 7), (4, 3),
            (5, 0), (6, 7), (5, 2), (4, 0), (3, 0)
        ]
    },

    # =========================================================================
    # 9. AI & DATA CENTER ENERGY INNOVATION
    # =========================================================================
    "ai_datacenter_dossier": {
        "map_title": "Geospatial Hyperscale AI Compute Hubs & Clean Baseload Microgrids",
        "clusters": [
            ("Ashburn Data Center", 39.04, -77.48, 600, '#0F172A', "$12.0B 3,000 MW AI Alley"),
            ("Columbus AI Corridor", 40.08, -82.80, 540, '#0284C7', "$7.5B Hyperscale Hub"),
            ("Phoenix AI Hub", 33.41, -111.83, 530, '#0284C7', "$6.0B Clean Microgrids"),
            ("Quincy Hydro Compute", 47.23, -119.85, 490, '#059669', "$3.5B Hydro-Powered"),
            ("Albany NanoTech AI", 42.69, -73.83, 580, '#0F172A', "$10.0B Extreme EUV R&D"),
            ("Constellation Clean PPA", 40.15, -76.72, 550, '#D97706', "$2.5B 24/7 Nuclear PPA"),
            ("NREL Liquid HPC", 39.75, -105.22, 450, '#0284C7', "$180M Immersion Testbed"),
            ("Austin Compute Hub", 30.26, -97.74, 500, '#059669', "$2.8B Microgrid Center")
        ],
        "callouts": [
            {"name": "Ashburn Data Center Alley", "lat": 39.0, "lng": -77.5, "text": "Ashburn Data Center Alley VA\n3,000+ MW Hyperscale Compute Hub", "offset_x": 16, "offset_y": 7},
            {"name": "Constellation Nuclear PPAs", "lat": 40.2, "lng": -76.7, "text": "Constellation Clean Energy PPA\n24/7 Dedicated Nuclear Baseload", "offset_x": 14, "offset_y": -6},
            {"name": "Albany NanoTech Complex", "lat": 42.7, "lng": -73.8, "text": "Albany NanoTech Complex NY\n$10B Next-Gen Silicon & AI Hardware", "offset_x": 15, "offset_y": 7}
        ],
        "network_title": "AI & Energy Network: Hyperscalers, Compute OEMs & Nuclear Fleets",
        "nodes": [
            ("DOE Scientific Compute", 0.0, 0.0, 560, '#0F172A', 'Federal Advanced Computing'),
            ("NVIDIA Infrastructure", -0.42, 0.35, 520, '#059669', 'Accelerated AI Hardware'),
            ("Microsoft / OpenAI", 0.45, 0.32, 510, '#0284C7', 'Hyperscale Energy Buyers'),
            ("Constellation Fleet", 0.38, -0.38, 500, '#D97706', 'Nuclear Baseload Generation'),
            ("Albany NanoTech", -0.48, -0.32, 480, '#0F172A', 'Semiconductor Ecosystem'),
            ("NREL HPC Lab", 0.0, 0.58, 440, '#0284C7', 'Liquid Immersion Cooling'),
            ("Submer / GRC", -0.58, 0.05, 450, '#059669', 'Immersion Cooling Innovators'),
            ("Dominion Energy / PJM", 0.56, -0.08, 470, '#0F172A', 'Grid Interconnection Utility')
        ],
        "edges": [
            (0, 1), (0, 2), (1, 2), (2, 3), (2, 7), (1, 4), (1, 6), (5, 6),
            (3, 7), (4, 0), (5, 0), (7, 0), (3, 2)
        ]
    },

    # =========================================================================
    # 10. TRANSPORTATION ELECTRIFICATION & HEAVY TRUCKS
    # =========================================================================
    "transportation_ev_dossier": {
        "map_title": "Geospatial Megawatt Charging Systems (MCS) & Fleet Transit Depots",
        "clusters": [
            ("Port of Long Beach", 33.77, -118.19, 580, '#0F172A', "$850M Zero-Emission Freight"),
            ("I-95 MCS Corridor", 39.50, -76.00, 530, '#059669', "$420M 3.75 MW Megawatt Hubs"),
            ("MTA Grand Ave Depot", 40.71, -73.91, 510, '#059669', "$180M 100-Bus Microgrid"),
            ("Chicago CTA Depot", 41.88, -87.63, 490, '#0284C7', "$150M Transit Electrification"),
            ("Texas Triangle Freight", 30.50, -97.50, 540, '#0F172A', "$620M Class 8 Freight Corridor"),
            ("Detroit Heavy Assembly", 42.33, -83.05, 560, '#0F172A', "$2.5B Commercial EV Trucks"),
            ("Port Authority NY/NJ", 40.69, -74.17, 500, '#0284C7', "$310M Terminal EV Fleet")
        ],
        "callouts": [
            {"name": "Port of Long Beach", "lat": 33.8, "lng": -118.2, "text": "Port of Long Beach & LA Freight\nZero-Emission Drayage Truck Hub", "offset_x": 16, "offset_y": 7},
            {"name": "MTA Grand Ave Depot", "lat": 40.7, "lng": -73.9, "text": "MTA Grand Avenue Bus Depot\n100-Bus Urban Smart Depot Microgrid", "offset_x": 14, "offset_y": -6},
            {"name": "I-95 MCS Corridor", "lat": 39.5, "lng": -76.0, "text": "I-95 MCS Freight Corridor\n3.75 MW Ultra-Fast Heavy Charging", "offset_x": 15, "offset_y": 7}
        ],
        "network_title": "Fleet Electrification Network: Transit Agencies, OEMs & Utilities",
        "nodes": [
            ("Joint Office of Energy/DOT", 0.0, 0.0, 560, '#0F172A', 'Federal Heavy EV Program'),
            ("CALSTART Freight", -0.42, 0.35, 490, '#0284C7', 'Consortia Fleet Lead'),
            ("MTA New York Transit", 0.45, 0.32, 510, '#0F172A', 'Municipal Transit Operator'),
            ("ABB & Kempower", 0.38, -0.38, 480, '#059669', 'Megawatt MCS Hardware'),
            ("Proterra & New Flyer", -0.48, -0.32, 470, '#059669', 'Heavy Transit OEMs'),
            ("ConEd Fleet Services", 0.0, 0.58, 460, '#D97706', 'Depot Interconnection Utility'),
            ("NREL Center for Mobility", -0.58, 0.05, 440, '#0284C7', 'Fleet DNA Laboratory'),
            ("Amazon / FedEx Freight", 0.56, -0.08, 480, '#0F172A', 'Commercial Fleet Operators')
        ],
        "edges": [
            (0, 1), (0, 2), (1, 2), (2, 3), (2, 5), (3, 5), (4, 2), (6, 1),
            (7, 3), (7, 5), (4, 0), (6, 0), (5, 0)
        ]
    },

    # =========================================================================
    # NUCLEAR FUSION STRATEGIC DOSSIER
    # =========================================================================
    "nuclear_fusion_dossier": {
        "map_title": "Geospatial Commercial Fusion Pilot Plants, National Labs & HTS Supply Hubs",
        "clusters": [
            ("CFS Devens Campus", 42.55, -71.61, 580, '#0F172A', "$2.0B+ SPARC Tokamak"),
            ("Princeton PPPL", 40.35, -74.60, 520, '#0284C7', "$850M Fusion Lab"),
            ("Helion Everett WA", 47.98, -122.20, 560, '#059669', "$600M+ Polaris FRC"),
            ("Zap Energy FuZE-Q", 47.91, -122.25, 480, '#059669', "$200M Z-Pinch Hub"),
            ("LLNL NIF Ignition", 37.69, -121.70, 590, '#0F172A', "$3.5B Laser Ignition"),
            ("TAE Foothill Ranch", 33.68, -117.66, 540, '#059669', "$1.2B FRC Scaleup"),
            ("Rochester LLE OMEGA", 43.12, -77.63, 490, '#0284C7', "$450M Laser Lab"),
            ("Type One Oak Ridge", 36.01, -84.26, 510, '#059669', "$120M Stellarator"),
            ("Realta Fusion Madison", 43.07, -89.40, 440, '#0284C7', "$45M HTS Mirror"),
            ("General Fusion US Hub", 35.95, -84.30, 460, '#0284C7', "$300M MTF Pilot")
        ],
        "callouts": [
            {"name": "CFS Devens & MIT PSFC", "lat": 42.6, "lng": -71.6, "text": "Commonwealth Fusion Systems & MIT\n$2.0B+ SPARC 20T HTS Tokamak", "offset_x": 15, "offset_y": 7},
            {"name": "Pacific NW Fusion Hub", "lat": 48.0, "lng": -122.2, "text": "Helion Energy & Zap Energy\nPolaris FRC & Sheared-Flow Z-Pinch", "offset_x": -18, "offset_y": 7},
            {"name": "LLNL NIF & TAE CA", "lat": 37.7, "lng": -121.7, "text": "Lawrence Livermore & TAE Technologies\nLaser Ignition & Norman/Copernicus", "offset_x": -18, "offset_y": -6},
            {"name": "ORNL & Type One", "lat": 36.0, "lng": -84.3, "text": "Oak Ridge Lab & Type One Energy\nInfinity One Stellarator at TVA Site", "offset_x": 15, "offset_y": -6}
        ],
        "network_title": "Nuclear Fusion Innovation Network: Commercial Startups, Labs & Offtakers",
        "nodes": [
            ("DOE Fusion Sciences & ARPA-E", 0.0, 0.0, 560, '#0F172A', 'Federal Policy Core'),
            ("Commonwealth Fusion Systems", -0.42, 0.35, 520, '#0F172A', 'HTS Tokamak Leader'),
            ("MIT PSFC Research", 0.45, 0.32, 480, '#0284C7', 'Academic Plasma Anchor'),
            ("LLNL (NIF) & PPPL Labs", 0.38, -0.38, 500, '#0284C7', 'National Laboratories'),
            ("Helion & Zap Energy", -0.48, -0.32, 490, '#059669', 'Pacific NW Innovators'),
            ("TAE Technologies & Google", 0.0, 0.58, 470, '#059669', 'FRC & Machine Learning'),
            ("REBCO Superconductor OEMs", -0.58, 0.05, 450, '#D97706', 'HTS Tape Supply Chain'),
            ("Microsoft (Offtaker PPA)", 0.56, -0.08, 480, '#7C3AED', 'Hyperscale Offtaker')
        ],
        "edges": [
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 6), (1, 7),
            (2, 3), (3, 5), (4, 7), (5, 3), (6, 1), (7, 4), (0, 6)
        ]
    }
}

def get_nyt_graphics_for_preset(preset_id: str) -> Dict[str, Any]:
    """Retrieves custom NYT graphics data for a preset, with smart fallback if not specifically keyed."""
    return NYT_GRAPHICS_REGISTRY.get(preset_id, {
        "map_title": "Geospatial Clean Tech Capital Deployment & Research Clusters",
        "clusters": [
            ("NYC Metro", 40.71, -74.00, 520, '#0F172A', "$18.7B Tracked"),
            ("Boston Hub", 42.36, -71.05, 460, '#0284C7', "$14.2B Tracked"),
            ("Bay Area", 37.77, -122.41, 500, '#0284C7', "$21.5B Tracked"),
            ("Albany/Cap.", 42.65, -73.75, 420, '#059669', "$6.8B Tracked"),
            ("Chicago Hub", 41.87, -87.62, 380, '#0284C7', "$5.9B Tracked"),
            ("Austin Hub", 30.26, -97.74, 360, '#059669', "$4.8B Tracked"),
            ("Seattle", 47.60, -122.33, 390, '#0284C7', "$6.2B Tracked"),
            ("Denver", 39.73, -104.99, 320, '#38BDF8', "$3.9B Tracked"),
            ("Wash. DC", 38.90, -77.03, 480, '#0F172A', "$12.4B Tracked"),
            ("Los Angeles", 34.05, -118.24, 430, '#0284C7', "$8.7B Tracked")
        ],
        "callouts": [
            {"name": "Northeast Corridor", "lat": 41.5, "lng": -73.0, "text": "Northeast R&D Corridor\n$32.9B Capital Concentration", "offset_x": 14, "offset_y": 6},
            {"name": "West Coast Tech", "lat": 36.5, "lng": -120.0, "text": "West Coast Innovation Corridor\n$30.2B Venture & Grant Synergy", "offset_x": -18, "offset_y": -5}
        ],
        "network_title": "Institutional Knowledge Graph: Labs, Tier-1 Universities & Primes",
        "nodes": [
            ("Federal Energy Agency", 0.0, 0.0, 560, '#0F172A', 'Federal Policy Core'),
            ("Tier-1 R1 Universities", -0.42, 0.35, 480, '#0284C7', 'Basic Science R&D'),
            ("Corporate OEMs & Primes", 0.45, 0.32, 460, '#059669', 'Commercial Deployment'),
            ("Electric Utilities", 0.38, -0.38, 440, '#D97706', 'Grid Interconnection'),
            ("Climate Venture Capital", -0.48, -0.32, 420, '#7C3AED', 'Private Syndication'),
            ("State Tech Authorities", 0.0, 0.58, 430, '#0284C7', 'Regional Testbeds'),
            ("TRL 4-7 Scaleups", -0.58, 0.05, 410, '#059669', 'Demonstration Ventures'),
            ("Supply Chain Primes", 0.56, -0.08, 390, '#475569', 'Component Suppliers')
        ],
        "edges": [
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 4), (1, 5),
            (2, 3), (2, 6), (3, 6), (4, 6), (5, 7), (1, 7), (2, 7)
        ]
    })
