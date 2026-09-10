"""
Comprehensive Master Technology & Fuels Reference & Innovation Frontier Knowledge Engine.
Defines 15 clean energy sectors and 36 deep-tech conversion systems and molecular fuel pathways,
providing plain-English mechanical fundamentals, fuel vector profiles (Carbon Intensity,
energy density, feedstock origins, drop-in compatibility), 3-era evolution arcs, standardized KPI
targets, critical bottlenecks, active frontier R&D tracks, and empirical database evidence aggregations.
"""

import hashlib
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.models.technology import (
    TechnologyCategory,
    Technology,
    TechnologyCostPerformance,
    TechnologyKPI,
    TechnologySubsystem
)

logger = logging.getLogger(__name__)

CACHE_DIR = Path("data/tech_ref_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# 1. TAXONOMY CATEGORIES (15 SECTORS GROUNDED IN THE DATABASE)
# ==============================================================================

CATEGORIES = [
    {
        "id": "solar_systems",
        "name": "Solar Photovoltaics & Advanced Solar Systems",
        "icon": "Sun",
        "description": "Perovskite-silicon tandems, dual-use agrivoltaics, concentrated solar thermal (CSP), and building-integrated PV.",
        "color": "from-amber-400 to-yellow-600",
        "accent": "amber"
    },
    {
        "id": "wind_systems",
        "name": "Wind Energy & Offshore Systems",
        "icon": "Wind",
        "description": "Deepwater floating offshore wind, 15MW+ fixed-bottom monopiles, distributed micro-turbines, and airborne wind kites.",
        "color": "from-sky-400 to-blue-600",
        "accent": "sky"
    },
    {
        "id": "hydro_marine",
        "name": "Water, Marine Hydrokinetics & Hydropower",
        "icon": "Compass",
        "description": "Wave energy converters, tidal stream turbines, closed-loop pumped storage hydro (PSH), and run-of-river hydro.",
        "color": "from-blue-500 to-cyan-700",
        "accent": "blue"
    },
    {
        "id": "geothermal_subsurface",
        "name": "Geothermal & Subsurface Energy",
        "icon": "Flame",
        "description": "Enhanced Geothermal Systems (EGS), superhot rock (>400C) drilling, closed-loop conduction, and direct district heating.",
        "color": "from-red-500 to-orange-600",
        "accent": "red"
    },
    {
        "id": "energy_storage",
        "name": "Energy Storage & Advanced Chemistries",
        "icon": "BatteryCharging",
        "description": "100-hour iron-air LDES, vanadium/iron redox flow, solid-state lithium metal, and sodium-ion battery architectures.",
        "color": "from-orange-500 to-amber-600",
        "accent": "orange"
    },
    {
        "id": "grid_modernization",
        "name": "Grid Modernization, GETs & Digital Power",
        "icon": "Network",
        "description": "Grid-Enhancing Technologies (DLR/power flow), grid-forming inverters, HVDC links, and DERMS/VPP orchestration.",
        "color": "from-indigo-500 to-blue-600",
        "accent": "indigo"
    },
    {
        "id": "clean_hydrogen",
        "name": "Clean Hydrogen & Synthetic Molecules",
        "icon": "Zap",
        "description": "Electrolyzers (PEM, SOEC, AEM), salt cavern storage, clean fuel cells, turquoise pyrolysis, and e-molecules.",
        "color": "from-cyan-500 to-teal-600",
        "accent": "cyan"
    },
    {
        "id": "bioenergy_waste",
        "name": "Bioenergy, Sustainable Fuels & Waste-to-Energy",
        "icon": "Layers",
        "description": "Sustainable Aviation Fuels (SAF), renewable natural gas (RNG) via anaerobic digestion, and biomass gasification.",
        "color": "from-emerald-500 to-green-700",
        "accent": "emerald"
    },
    {
        "id": "advanced_nuclear",
        "name": "Advanced Nuclear & Fusion Energy",
        "icon": "Atom",
        "description": "Small Modular Reactors (SMRs), microreactors, molten salt / fast reactors, and magnetic/laser fusion systems.",
        "color": "from-violet-500 to-purple-600",
        "accent": "violet"
    },
    {
        "id": "industrial_decarb",
        "name": "Industrial Decarbonization & Process Heat",
        "icon": "Factory",
        "description": "Industrial high-temperature heat pumps (150C+), green steel (H2-DRI/EAF), electrified calcination, and thermal bricks.",
        "color": "from-rose-500 to-red-600",
        "accent": "rose"
    },
    {
        "id": "buildings_thermal",
        "name": "Buildings, Thermal Networks & Heat Pumps",
        "icon": "Home",
        "description": "Utility Thermal Energy Networks (TENs), cold-climate heat pumps (ccASHP), low-GWP refrigerants, and aerogel insulation.",
        "color": "from-teal-500 to-emerald-600",
        "accent": "teal"
    },
    {
        "id": "clean_transportation",
        "name": "Clean Transportation & Heavy-Duty Mobility",
        "icon": "Truck",
        "description": "Megawatt charging systems (MCS), silicon-anode EV batteries, bidirectional V2G inverters, and zero-emission transit.",
        "color": "from-lime-500 to-green-600",
        "accent": "lime"
    },
    {
        "id": "carbon_management",
        "name": "Carbon Capture, Utilization & Removal (CCUS/CDR)",
        "icon": "Wind",
        "description": "Direct Air Capture (DAC), point-source post-combustion scrubbers, concrete mineralization, and Class VI geologic storage.",
        "color": "from-stone-500 to-slate-700",
        "accent": "stone"
    },
    {
        "id": "critical_minerals",
        "name": "Critical Minerals & Closed-Loop Supply Chains",
        "icon": "Layers",
        "description": "Direct Lithium Extraction (DLE), battery scrap hydrometallurgy, rare earth magnet recycling, and synthetic anodes.",
        "color": "from-yellow-500 to-amber-600",
        "accent": "yellow"
    },
    {
        "id": "ai_datacenter",
        "name": "AI, HPC, Resilience & Data Center Decarb",
        "icon": "Cpu",
        "description": "Direct-to-chip liquid cooling, black-start microgrids, AI autonomous grid dispatch, and data center waste heat export.",
        "color": "from-fuchsia-500 to-pink-600",
        "accent": "fuchsia"
    }
]

# ==============================================================================
# 2. MASTER TECHNOLOGY DEFINITIONS (36 HIGH-IMPACT ENGINES)
# ==============================================================================

TECHNOLOGY_REGISTRY: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # 1. SOLAR PHOTOVOLTAICS & ADVANCED SOLAR SYSTEMS
    # -------------------------------------------------------------------------
    "perovskite_tandem_solar": {
        "id": "perovskite_tandem_solar",
        "name": "Perovskite-Silicon Tandem Photovoltaics",
        "category_id": "solar_systems",
        "category_name": "Solar Photovoltaics & Advanced Solar Systems",
        "headline": "Stacking thin-film perovskite crystals on silicon to break the 29% single-junction efficiency ceiling.",
        "trl_current": 6,
        "trl_target": 9,
        "keywords": ["perovskite", "tandem solar", "photovoltaic", "solar cell", "silicon tandem", "efficiency record", "NREL"],
        "sector": "Clean Electricity Generation",
        "fuel_vector": "Solar Radiance",
        "plain_english": {
            "what_is_it": "Next-generation solar panels that add an ultra-thin layer of synthetic perovskite crystal on top of traditional silicon, allowing the panel to convert both blue/green and red/infrared light into electricity simultaneously.",
            "how_it_works": "Silicon panels absorb red and infrared sunlight efficiently but waste blue photons as excess heat. By coating silicon with a perovskite top-cell tailored for high-energy blue photons, the combined tandem stack absorbs the full solar spectrum.",
            "why_it_matters": "Silicon solar cells are approaching their theoretical physics limit (~29%). Perovskite tandems raise commercial panel efficiency from 22% to 32%+, generating 40% more electricity from the exact same roof or land area.",
            "macro_problem_solved": "Land-constrained solar deployment and diminishing efficiency returns on legacy crystalline silicon."
        },
        "evolution": {
            "past": "Single-junction crystalline silicon and thin-film CdTe panels capped at 18-22% efficiency (1980s-2020).",
            "present": "Lab-scale tandem cells reaching 34.6% efficiency; pilot manufacturing runs (Oxford PV, Qcells, Swift Solar).",
            "future": "Universal 30%+ commercial tandem modules with 25-year moisture-barrier encapsulation by 2028-2032."
        },
        "frontier": {
            "moonshot_goal": "Mass-produce commercial 30%+ efficiency tandem modules with <0.5%/year degradation over a 25-year warranted lifespan.",
            "kpis": [
                {"name": "Lab Cell Efficiency", "current": "33.9% - 34.6%", "target_2030": "> 36.0%", "status": "achieved"},
                {"name": "Commercial Module Efficiency", "current": "24.5% - 27.0%", "target_2030": "> 30.0%", "status": "on_track"},
                {"name": "Operational Lifetime (T80)", "current": "5 - 10 Years", "target_2030": "> 25 Years", "status": "challenging"},
                {"name": "Levelized Cost of Electricity (LCOE)", "current": "$0.045 / kWh", "target_2030": "< $0.020 / kWh", "status": "on_track"}
            ],
            "bottlenecks": [
                "Intrinsic chemical instability under continuous moisture, oxygen, heat, and ultraviolet illumination.",
                "Ion migration inside the perovskite crystal lattice causing localized phase segregation and defect traps.",
                "Lead (Pb) toxicity concerns requiring robust zero-leach encapsulation in catastrophic hail/shatter events."
            ],
            "active_research_tracks": [
                "2D/3D heterostructure passivation layers and fluorinated self-assembled monolayers (DOE SETO / NREL).",
                "Roll-to-roll slot-die coating of perovskite films on flexible and glass substrates.",
                "Lead-free tin/bismuth-based double perovskite absorbers."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 95,
            "capex_competitiveness": 85,
            "duration_scalability": 90,
            "technology_maturity": 65,
            "domestic_supply_chain": 78,
            "siting_permitting_ease": 92
        },
        "trade_offs": {
            "strengths": ["Breaks the 29% theoretical efficiency ceiling of pure silicon", "Compatible with existing silicon module manufacturing lines", "Low materials cost and ultra-thin active layer"],
            "weaknesses": ["Degrades faster than pure silicon when exposed to moisture and UV heat", "Manufacturing requires cleanroom precision to prevent microscopic pinhole defects", "Encapsulation polymers add balance-of-system cost"],
            "competing_technologies": ["Heterojunction (HJT) Silicon", "TOPCon Silicon", "Gallium Arsenide (GaAs) Multijunctions"]
        }
    },
    "agrivoltaics_bifacial_solar": {
        "id": "agrivoltaics_bifacial_solar",
        "name": "Dual-Use Agrivoltaics & Smart Bifacial Tracking",
        "category_id": "solar_systems",
        "category_name": "Solar Photovoltaics & Advanced Solar Systems",
        "headline": "Elevated bifacial solar tracking arrays that co-locate active crop farming, grazing, and pollinator habitats with clean power generation.",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["agrivoltaics", "bifacial", "dual use solar", "agriculture", "smart tracking", "crop yield", "pollinator"],
        "sector": "Clean Electricity Generation",
        "fuel_vector": "Solar Radiance",
        "plain_english": {
            "what_is_it": "Solar panel arrays raised high enough off the ground and spaced widely enough to allow tractors, cattle, sheep, and crops to grow underneath, capturing sunlight from both the top and bottom sides of the panels.",
            "how_it_works": "Bifacial glass panels capture direct overhead sunlight and reflected light from the green crop canopy underneath (albedo effect). Smart single-axis trackers rotate panels to provide crops with optimal shade during scorching midday heat, reducing crop water loss by 30%.",
            "why_it_matters": "Eliminates the 'land-use conflict' between agricultural food production and large clean energy projects. Farmers earn steady supplemental energy revenue while improving crop yields in drought-prone regions.",
            "macro_problem_solved": "Rural land competition between utility solar farms and food agriculture."
        },
        "evolution": {
            "past": "Clear-cut ground-mount solar arrays with fencing that eliminated agricultural activity (2000-2018).",
            "present": "Commercial sheep grazing and shade-tolerant crop pilot projects (NYSERDA, DOE FARMS, Cornell Agrivoltaics).",
            "future": "Fully automated, tall-clearance smart tracking arrays with robotic farming compatibility standard nationwide by 2030."
        },
        "frontier": {
            "moonshot_goal": "Deploy 50+ GW of dual-use solar that increases combined land productivity (Land Equivalent Ratio > 1.4) while cutting irrigation water by 30%.",
            "kpis": [
                {"name": "Land Equivalent Ratio (LER)", "current": "1.15 - 1.25", "target_2030": "> 1.40", "status": "on_track"},
                {"name": "Crop Water Reduction", "current": "15% - 25%", "target_2030": "> 35%", "status": "achieved"},
                {"name": "Bifacial Energy Yield Boost", "current": "8% - 14%", "target_2030": "> 20%", "status": "on_track"},
                {"name": "Structural Steel Cost Premium", "current": "+18% vs standard", "target_2030": "< +5% vs standard", "status": "on_track"}
            ],
            "bottlenecks": [
                "Higher racking structural costs due to 8-10 ft elevated clearances for agricultural tractors.",
                "Microclimate variation and uneven rain runoff causing localized soil erosion under drip lines.",
                "Custom tracker control algorithms required for differing regional crop shade tolerances."
            ],
            "active_research_tracks": [
                "Spectral-selective semi-transparent organic PV transmitting photosynthetic PAR wavelengths while generating power (DOE SETO).",
                "Dynamic tracking algorithms balancing ISO electricity market pricing against real-time crop photosynthetic stress.",
                "Automated drip irrigation integration using tracker torque tubes as water conduits."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 92,
            "capex_competitiveness": 80,
            "duration_scalability": 95,
            "technology_maturity": 85,
            "domestic_supply_chain": 90,
            "siting_permitting_ease": 96
        },
        "trade_offs": {
            "strengths": ["Eliminates rural local community pushback and farmland loss", "Cuts crop irrigation water demand during peak summer heat", "Provides dual revenue streams (cash crops + kilowatt-hours) for rural landowners"],
            "weaknesses": ["Higher upfront racking and foundation steel cost", "Requires specialized farm equipment clearances", "Slightly lower panel density per acre than packed utility solar"],
            "competing_technologies": ["Rooftop Solar", "Brownfield Ground-Mount Solar", "Floating Solar (Floatovoltaics)"]
        }
    },
    "concentrated_solar_power_csp": {
        "id": "concentrated_solar_power_csp",
        "name": "Next-Gen Concentrated Solar Power (CSP) & Molten Salt Storage",
        "category_id": "solar_systems",
        "category_name": "Solar Photovoltaics & Advanced Solar Systems",
        "headline": "Mirrored heliostat solar towers heating molten chloride salts or ceramic particles to 700C+ for 16-hour dispatchable thermal power.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["CSP", "concentrated solar", "molten salt", "heliostat", "thermal energy storage", "supercritical CO2", "dispatchable solar"],
        "sector": "Clean Electricity Generation",
        "fuel_vector": "Solar Thermal Heat",
        "plain_english": {
            "what_is_it": "Thousands of curved mirrors (heliostats) that track the sun and concentrate solar rays onto a central tower, heating liquid salts or ceramic sand to over 1,300F (700C). The stored heat runs steam or supercritical CO2 turbines to produce clean power all night long.",
            "how_it_works": "Unlike photovoltaic panels that turn sunlight directly into DC electricity and stop working when the sun sets, CSP converts sunlight into ultra-hot thermal energy stored in insulated tanks. This thermal battery drives electric generators whenever the grid needs power.",
            "why_it_matters": "Provides 12 to 16 hours of continuous, synchronous, spinning-reserve clean electricity from solar energy, solving multi-hour nighttime power demands without requiring electrochemical battery packs.",
            "macro_problem_solved": "Overnight solar dispatchability and providing synchronous grid inertia without fossil fuels."
        },
        "evolution": {
            "past": "Parabolic trough oil-fluid plants with 4-hour nitrate salt storage (1990s-2015).",
            "present": "Commercial molten nitrate salt solar towers (Noor Midelt, Cerro Dominador, Ivanpah) operating at 565C.",
            "future": "Gen3 CSP utilizing liquid chloride salts or falling ceramic particles with supercritical sCO2 turbines at >700C by 2028."
        },
        "frontier": {
            "moonshot_goal": "Achieve levelized cost of electricity (LCOE) <$0.05/kWh with 14+ hours of thermal storage at >700C operating temperature.",
            "kpis": [
                {"name": "Receiver Operating Temp", "current": "565C (Nitrate salt)", "target_2030": "> 720C (Chloride/Particles)", "status": "on_track"},
                {"name": "Power Cycle Efficiency", "current": "40% - 42% (Steam)", "target_2030": "> 50% (sCO2 Brayton)", "status": "on_track"},
                {"name": "Thermal Storage Capital Cost", "current": "$25 - $32 / kWh-th", "target_2030": "< $15 / kWh-th", "status": "on_track"},
                {"name": "LCOE with 14hr Storage", "current": "$0.085 / kWh", "target_2030": "< $0.050 / kWh", "status": "challenging"}
            ],
            "bottlenecks": [
                "Severe high-temperature chemical corrosion of receiver tubes and piping from molten chloride salts.",
                "Heliostat field optical alignment drift caused by desert thermal expansion and wind buffeting.",
                "High initial capital expenditure compared to cheap photovoltaic solar plus lithium-ion storage."
            ],
            "active_research_tracks": [
                "Falling ceramic particle receivers capable of withstanding >800C without corrosion (DOE Gen3 CSP / Sandia).",
                "High-nickel superalloys (Inconel 740H / Haynes 282) for high-pressure supercritical CO2 heat exchangers.",
                "AI camera-based closed-loop heliostat tracking calibration."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 60,
            "capex_competitiveness": 65,
            "duration_scalability": 95,
            "technology_maturity": 75,
            "domestic_supply_chain": 88,
            "siting_permitting_ease": 70
        },
        "trade_offs": {
            "strengths": ["Built-in 12-16 hour thermal storage without expensive chemical batteries", "Provides spinning synchronous inertia and black-start capabilities", "Produces high-temperature industrial steam for manufacturing"],
            "weaknesses": ["Requires high direct normal irradiance (DNI) arid desert environments", "High upfront project CapEx ($500M+ per facility)", "Mechanical complexity with pumps, valves, and rotating turbines"],
            "competing_technologies": ["Solar PV + Lithium Iron Phosphate", "Solar PV + Iron-Air LDES", "Enhanced Geothermal Systems"]
        }
    },

    # -------------------------------------------------------------------------
    # 2. WIND ENERGY & OFFSHORE SYSTEMS
    # -------------------------------------------------------------------------
    "floating_offshore_wind": {
        "id": "floating_offshore_wind",
        "name": "Deepwater Floating Offshore Wind Turbines",
        "category_id": "wind_systems",
        "category_name": "Wind Energy & Offshore Systems",
        "headline": "Moored floating substructures unlocking the 80% of global offshore wind resources in waters deeper than 60 meters.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["floating wind", "offshore wind", "deepwater", "semi-submersible", "spar buoy", "dynamic cable", "15MW"],
        "sector": "Clean Electricity Generation",
        "fuel_vector": "Kinetic Wind Energy",
        "plain_english": {
            "what_is_it": "Giant 15-to-20 megawatt wind turbines mounted on buoyant steel or concrete floating hulls that are tethered to the seabed with heavy mooring cables, operating miles out to sea in deep water.",
            "how_it_works": "Traditional offshore wind turbines are fixed directly into the ocean floor (monopiles), which becomes economically impossible in waters deeper than 200 feet (60 meters). Floating wind uses buoyant semi-submersible or spar-buoy platforms anchored by synthetic tendons, with dynamic high-voltage cables carrying power back to shore.",
            "why_it_matters": "Over 80% of the world's best, strongest, and most consistent offshore wind blows in deep waters (including the US Pacific Coast, Gulf of Maine, and Europe). Floating wind allows turbines to access uninterrupted gale-force winds with capacity factors above 50%.",
            "macro_problem_solved": "Water depth limitations of seabed-fixed wind and unlocking deepwater coastal energy."
        },
        "evolution": {
            "past": "Single-turbine prototypes like Hywind Demo (2.3MW, 2009).",
            "present": "Commercial pre-arrays (Hywind Tampen 88MW, Kincardine 50MW, US BOEM Pacific lease auctions).",
            "future": "Gigawatt-scale floating wind farms with industrialized concrete serial manufacturing and 20MW+ turbines by 2030."
        },
        "frontier": {
            "moonshot_goal": "Reduce levelized cost of floating offshore wind from $130/MWh to <$45/MWh by 2035 (DOE Floating Offshore Wind Shot).",
            "kpis": [
                {"name": "Levelized Cost (LCOE)", "current": "$110 - $145 / MWh", "target_2030": "< $45 / MWh", "status": "on_track"},
                {"name": "Turbine Nameplate Capacity", "current": "10 - 15 MW", "target_2030": "18 - 22 MW", "status": "achieved"},
                {"name": "Platform Steel/Concrete Mass", "current": "350 tons / MW", "target_2030": "< 180 tons / MW", "status": "on_track"},
                {"name": "Dynamic Export Cable Voltage", "current": "66 kV AC", "target_2030": "132 kV AC / +/-320 kV HVDC", "status": "on_track"}
            ],
            "bottlenecks": [
                "Lack of deepwater quayside ports and heavy-lift installation vessels with 200m+ crane hook heights.",
                "Fatigue wear on dynamic subsea high-voltage power cables flexing constantly in 50-foot storm waves.",
                "High fabrication cost of massive 3,000-ton semi-submersible steel hulls."
            ],
            "active_research_tracks": [
                "Modular pre-stressed ultra-high-performance concrete (UHPC) hulls fabricated locally in dry docks (DOE ARPA-E ATLANTIS).",
                "Active aerodynamic pitch control damping wave-induced platform pitch motions.",
                "Shared synthetic mooring arrays connecting adjacent floating turbines to cut seabed anchor count by 50%."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 95,
            "capex_competitiveness": 60,
            "duration_scalability": 98,
            "technology_maturity": 70,
            "domestic_supply_chain": 65,
            "siting_permitting_ease": 72
        },
        "trade_offs": {
            "strengths": ["Accesses the world's richest wind resources in deep coastal waters", "Higher and steadier capacity factors (>50%) than onshore wind or solar", "Invisible from shore when sited 20+ miles out, reducing visual permitting resistance"],
            "weaknesses": ["High initial CapEx and heavy reliance on specialized installation port infrastructure", "Dynamic power cables require subsea fatigue monitoring", "O&M offshore vessel logistics are costly during winter storms"],
            "competing_technologies": ["Fixed-Bottom Offshore Wind", "Long-Distance HVDC Transmitted Onshore Wind", "Advanced Nuclear SMRs"]
        }
    },
    "fixed_bottom_offshore_wind": {
        "id": "fixed_bottom_offshore_wind",
        "name": "15MW+ Fixed-Bottom Offshore Wind & Monopiles",
        "category_id": "wind_systems",
        "category_name": "Wind Energy & Offshore Systems",
        "headline": "Massive 15MW direct-drive turbines anchored to shallow seabed continental shelves delivering gigawatts of coastal power.",
        "trl_current": 9,
        "trl_target": 9,
        "keywords": ["fixed bottom", "offshore wind", "monopile", "jacket foundation", "15MW", "coastal power", "Vineyard Wind"],
        "sector": "Clean Electricity Generation",
        "fuel_vector": "Kinetic Wind Energy",
        "plain_english": {
            "what_is_it": "Colossal offshore wind turbines—taller than the Washington Monument with blades longer than a football field—driven deep into the seabed in shallow coastal waters (up to 150 feet deep) to power millions of homes.",
            "how_it_works": "Heavy steel monopiles (cylinders up to 30 feet in diameter) are driven into the ocean floor. A 15-megawatt permanent magnet direct-drive turbine is bolted on top, turning strong Atlantic ocean winds directly into electricity without needing a mechanical gearbox.",
            "why_it_matters": "Major coastal cities (New York, Boston, Washington) have limited land for solar farms. Shallow offshore wind delivers enormous volumes of clean power right on the doorstep of high-demand coastal population centers.",
            "macro_problem_solved": "Land scarcity for clean energy near dense coastal mega-regions."
        },
        "evolution": {
            "past": "First European coastal arrays with 2MW geared turbines in shallow 10m waters (1990s-2010).",
            "present": "Commercial gigawatt projects deploying 13-15MW turbines (Vineyard Wind, South Fork Wind, Empire Wind).",
            "future": "Standardized 18MW+ digital direct-drive turbines with circular recyclable composite blades by 2028-2032."
        },
        "frontier": {
            "moonshot_goal": "Deploy 30 GW of domestic offshore wind by 2030 with >98% availability and 100% recyclable resin blades.",
            "kpis": [
                {"name": "Turbine Capacity Factor", "current": "45% - 50%", "target_2030": "> 55%", "status": "achieved"},
                {"name": "Levelized Cost (LCOE)", "current": "$65 - $85 / MWh", "target_2030": "< $50 / MWh", "status": "on_track"},
                {"name": "Blade Recyclability", "current": "15% (Landfilled/co-processed)", "target_2030": "100% Fully Recyclable Resin", "status": "on_track"},
                {"name": "Jones Act Compliant Installation Ships", "current": "1 in construction (Charybdis)", "target_2030": "4+ Purpose-Built", "status": "on_track"}
            ],
            "bottlenecks": [
                "Domestic Jones Act compliant Wind Turbine Installation Vessel (WTIV) scarcity.",
                "Supply chain inflation on high-grade structural steel and rare earth permanent magnets.",
                "Complex multi-agency federal and state environmental and fisheries permitting timelines."
            ],
            "active_research_tracks": [
                "Thermoplastic and bio-epoxy recyclable blade resin chemistries (DOE NREL / Elium).",
                "Quiet hydraulic vibratory and bubble-curtain monopile driving mitigating underwater marine mammal acoustic impact.",
                "AI-driven lidar wake steering to increase total wind farm energy yield by 4-8%."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 95,
            "capex_competitiveness": 75,
            "duration_scalability": 95,
            "technology_maturity": 92,
            "domestic_supply_chain": 72,
            "siting_permitting_ease": 68
        },
        "trade_offs": {
            "strengths": ["Enormous energy density located immediately adjacent to coastal load centers", "Commercial maturity with proven gigawatt-scale financeability", "High winter capacity factors matching seasonal heating peak demand"],
            "weaknesses": ["Restricted to shallow continental shelf waters (<60m depth)", "Vulnerable to supply chain and specialized installation vessel bottlenecks", "Visual and marine fishery stakeholder opposition"],
            "competing_technologies": ["Floating Offshore Wind", "Imported Canadian Hydropower", "Advanced Nuclear SMRs"]
        }
    },

    # -------------------------------------------------------------------------
    # 3. WATER, MARINE HYDROKINETICS & HYDROPOWER
    # -------------------------------------------------------------------------
    "marine_hydrokinetic_wave_tidal": {
        "id": "marine_hydrokinetic_wave_tidal",
        "name": "Marine Hydrokinetics, Wave & Tidal Stream Energy",
        "category_id": "hydro_marine",
        "category_name": "Water, Marine Hydrokinetics & Hydropower",
        "headline": "Subsea turbines and floating oscillating water columns tapping predictable ocean tides and dense wave kinetic energy.",
        "trl_current": 6,
        "trl_target": 8,
        "keywords": ["marine hydrokinetic", "MHK", "wave energy", "tidal turbine", "ocean energy", "PacWave", "tidal stream"],
        "sector": "Clean Electricity Generation",
        "fuel_vector": "Kinetic Ocean Power",
        "plain_english": {
            "what_is_it": "Underwater turbines and wave buoys that generate clean electricity from the natural ebb and flow of ocean tides and the continuous mechanical motion of ocean surface waves.",
            "how_it_works": "Tidal turbines look like underwater windmills anchored in high-speed ocean channels where moon gravity forces massive water movements twice a day. Wave energy converters use floating hinged floats that pump hydraulic fluid or turn direct-drive magnets as waves lift them.",
            "why_it_matters": "Water is 800 times denser than air, meaning a small ocean turbine packs tremendous energy. Unlike wind and solar, ocean tides are 100% predictable hundreds of years in advance.",
            "macro_problem_solved": "Intermittency of weather-dependent renewables and powering isolated coastal/island communities."
        },
        "evolution": {
            "past": "Single prototype wave buoys destroyed by winter ocean storms (1990-2015).",
            "present": "Grid-connected open-water test facilities (PacWave Oregon, EMEC Scotland, Verdant Power East River NYC).",
            "future": "Multi-megawatt commercial tidal arrays and autonomous wave-powered offshore charging hubs by 2030."
        },
        "frontier": {
            "moonshot_goal": "Achieve levelized cost of energy <$0.10/kWh for commercial marine hydrokinetic arrays with 5+ year maintenance intervals.",
            "kpis": [
                {"name": "MHK Levelized Cost (LCOE)", "current": "$0.25 - $0.45 / kWh", "target_2030": "< $0.10 / kWh", "status": "challenging"},
                {"name": "Subsea Mean Time Between Failures", "current": "18 - 24 Months", "target_2030": "> 60 Months", "status": "on_track"},
                {"name": "Tidal Generation Predictability", "current": "100% Astronomical", "target_2030": "100% Astronomical", "status": "achieved"},
                {"name": "Capacity Factor in Tidal Chokepoints", "current": "35% - 42%", "target_2030": "> 48%", "status": "on_track"}
            ],
            "bottlenecks": [
                "Extreme saltwater corrosion, biofouling, and violent storm wave fatigue loads destroying mechanical seals.",
                "High cost of specialized subsea support vessels and divers for maintenance operations.",
                "Environmental permitting uncertainties regarding fish and marine mammal interactions."
            ],
            "active_research_tracks": [
                "Direct-drive linear magnetic generators eliminating failure-prone hydraulic fluid circuits (DOE WPTO).",
                "Advanced biomimetic flexible composite hydrofoils shedding biofouling without toxic anti-fouling paints.",
                "Off-grid marine applications (wave-powered oceanographic sensors, aquaculture, and seawater desalination)."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 85,
            "capex_competitiveness": 55,
            "duration_scalability": 75,
            "technology_maturity": 60,
            "domestic_supply_chain": 70,
            "siting_permitting_ease": 65
        },
        "trade_offs": {
            "strengths": ["100% predictable tidal generation cycles determined by lunar physics", "Enormous energy density (water is 830x denser than air)", "Zero visual onshore landscape footprint for submerged subsea turbines"],
            "weaknesses": ["Harsh marine environment creates high maintenance and vessel intervention costs", "High capital cost per installed kilowatt in early commercialization", "Deployment limited to specific geographical ocean passes and energetic coasts"],
            "competing_technologies": ["Offshore Wind", "Subsea Interconnection Cables", "Battery Energy Storage Systems"]
        }
    },
    "pumped_storage_hydropower": {
        "id": "pumped_storage_hydropower",
        "name": "Advanced Closed-Loop Pumped Storage Hydropower (PSH)",
        "category_id": "hydro_marine",
        "category_name": "Water, Marine Hydrokinetics & Hydropower",
        "headline": "Closed-loop off-river gravity water storage providing 12–24 hours of multi-gigawatt-hour grid balancing.",
        "trl_current": 9,
        "trl_target": 9,
        "keywords": ["pumped storage", "hydro", "PSH", "closed loop", "variable speed turbine", "gravity storage", "long duration"],
        "sector": "Grid Energy Storage",
        "fuel_vector": "Hydro Potential Energy",
        "plain_english": {
            "what_is_it": "Two water reservoirs located at different elevations. When electricity is cheap and abundant, water is pumped uphill to the upper reservoir; when electricity demand peaks, water flows down through turbines into the lower reservoir to produce instant power.",
            "how_it_works": "Modern 'closed-loop' pumped hydro builds both reservoirs away from natural rivers, eliminating fish impacts. Advanced variable-speed reversible pump-turbines allow the system to rapidly adjust power output in seconds to balance solar and wind fluctuations.",
            "why_it_matters": "Pumped hydro represents over 90% of all utility-scale energy storage capacity currently operating in the United States, providing rock-solid 10 to 24-hour storage with a operating lifetime of 60 to 100 years.",
            "macro_problem_solved": "Bulk multi-gigawatt grid balancing and seasonal storage with zero chemical degradation."
        },
        "evolution": {
            "past": "Open-river conventional pumped hydro dams built in the 1960s-1980s (e.g. NYPA Blenheim-Gilboa, Bath County).",
            "present": "Upgrading legacy plants with fast-responding variable-speed pump-turbines; closed-loop off-river permitting.",
            "future": "Closed-loop modular underground and abandoned mine PSH with ternary machine sets providing sub-second inertia by 2030."
        },
        "frontier": {
            "moonshot_goal": "Permit and construct modular closed-loop pumped storage facilities in <5 years utilizing brownfields and abandoned open-pit mines.",
            "kpis": [
                {"name": "Round-Trip Efficiency (RTE)", "current": "75% - 82%", "target_2030": "> 85%", "status": "achieved"},
                {"name": "Operating Asset Lifetime", "current": "50 - 80 Years", "target_2030": "> 100 Years", "status": "achieved"},
                {"name": "Response Time (Pumping to Gen)", "current": "2 - 5 Minutes", "target_2030": "< 30 Seconds", "status": "on_track"},
                {"name": "Development & Permitting Duration", "current": "7 - 12 Years", "target_2030": "< 4 Years", "status": "challenging"}
            ],
            "bottlenecks": [
                "Lengthy multi-agency federal FERC licensing and environmental impact review timelines.",
                "High initial civil engineering capital expenditure ($1B+ per facility) requiring long-term off-take contracts.",
                "Specific topography requirements requiring significant elevation differences (head > 200 meters)."
            ],
            "active_research_tracks": [
                "Underground pumped hydro using deep flooded mines and excavated subterranean caverns (DOE WPTO / NREL).",
                "Full-converter variable-speed ternary pump-turbines capable of instant switching between charge and discharge.",
                "Geomembrane liners eliminating reservoir seepage water losses in arid western regions."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 82,
            "capex_competitiveness": 78,
            "duration_scalability": 98,
            "technology_maturity": 95,
            "domestic_supply_chain": 95,
            "siting_permitting_ease": 55
        },
        "trade_offs": {
            "strengths": ["Proven 60-100 year operational asset life with zero chemical degradation", "Lowest levelized cost of storage (LCOS) for 10-24 hour bulk durations", "Provides massive physical spinning inertia and black-start grid stabilization"],
            "weaknesses": ["High upfront capital cost and 5-8 year construction timelines", "Requires specific elevation topography", "Complex FERC regulatory and environmental licensing processes"],
            "competing_technologies": ["Iron-Air Batteries", "Compressed Air Energy Storage (CAES)", "Hydrogen Storage"]
        }
    },

    # -------------------------------------------------------------------------
    # 4. GEOTHERMAL & SUBSURFACE ENERGY
    # -------------------------------------------------------------------------
    "enhanced_geothermal_egs": {
        "id": "enhanced_geothermal_egs",
        "name": "Enhanced Geothermal Systems (EGS) & Hydraulic Stimulation",
        "category_id": "geothermal_subsurface",
        "category_name": "Geothermal & Subsurface Energy",
        "headline": "Engineered subsurface heat exchangers unlocking 24/7 baseload clean power anywhere on Earth.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["geothermal", "EGS", "enhanced geothermal", "fracking", "baseload clean power", "Fervo Energy", "FORGE"],
        "sector": "Clean Electricity Generation",
        "fuel_vector": "Subsurface Heat",
        "plain_english": {
            "what_is_it": "Drilling deep underground (2 to 4 miles) into hot dry granite rock, creating a network of tiny fractures, and pumping water through the hot rock to create a massive artificial underground radiator that generates continuous steam electricity 24 hours a day, 365 days a year.",
            "how_it_works": "Adapts horizontal drilling and hydraulic stimulation tools from the shale oil revolution. Two parallel horizontal wells are drilled into 400F+ (200C+) basement rock. Cold water is injected into one well, gets superheated as it flows through the fractures, and returns up the second production well to drive power turbines.",
            "why_it_matters": "Traditional geothermal only works in rare volcanic hot springs. EGS can be deployed virtually anywhere, providing rock-solid 24/7 clean baseload power that perfectly replaces retiring coal and natural gas plants using 99% less land than solar or wind.",
            "macro_problem_solved": "24/7 firm zero-carbon baseload electricity and replacing fossil thermal plants without batteries."
        },
        "evolution": {
            "past": "Conventional hydrothermal volcanic plants (The Geysers CA, Nevada, 1960-2015).",
            "present": "Commercial multi-MW EGS pilot plants delivering power to Google and NV Energy (Fervo Energy, Utah FORGE).",
            "future": "Gigawatt-scale deep closed-loop and superhot rock drilling reaching $0.045/kWh baseload power by 2030-2035."
        },
        "frontier": {
            "moonshot_goal": "Reduce the cost of EGS by 90% to $45/MWh by 2035 and deploy 90+ GW of firm clean baseload power across North America (DOE Enhanced Geothermal Shot).",
            "kpis": [
                {"name": "Levelized Cost of Electricity", "current": "$70 - $110 / MWh", "target_2030": "< $45 / MWh", "status": "on_track"},
                {"name": "Drilling Speed in Granite", "current": "30 - 50 ft / hr", "target_2030": "> 150 ft / hr", "status": "on_track"},
                {"name": "Well Pair Thermal Output", "current": "3.5 - 5.0 MW-e", "target_2030": "> 10.0 MW-e", "status": "on_track"},
                {"name": "Drilling Cost per Well", "current": "$4.5M - $7.0M", "target_2030": "< $2.5M", "status": "on_track"}
            ],
            "bottlenecks": [
                "Drill bit wear and tool electronic failure in abrasive, high-temperature (>250C) hard crystalline basement rock.",
                "Induced seismicity monitoring and community seismic risk mitigation during hydraulic stimulation.",
                "Thermal short-circuiting where water flows through only a single fracture instead of heating across the entire rock mass."
            ],
            "active_research_tracks": [
                "Polycrystalline diamond compact (PDC) bits optimized for ultra-hard igneous rocks (DOE GTO / Sandia).",
                "Fiber-optic distributed acoustic sensing (DAS) mapping subsurface fracture fluid pathways in real time.",
                "Supercritical CO2 working fluids replacing water to prevent mineral dissolution and boost thermal efficiency."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 90,
            "capex_competitiveness": 72,
            "duration_scalability": 100,
            "technology_maturity": 75,
            "domestic_supply_chain": 95,
            "siting_permitting_ease": 78
        },
        "trade_offs": {
            "strengths": ["True 24/7/365 firm clean baseload power with >90% capacity factor", "Smallest surface land footprint of any clean energy technology", "Directly re-employs oil and gas drilling workforce, supply chains, and rigs"],
            "weaknesses": ["High upfront capital cost per drilled exploration well pair", "Risk of induced micro-earthquakes requires careful seismic telemetry", "Deep drilling tool degradation in extreme heat (>200C)"],
            "competing_technologies": ["Small Modular Nuclear Reactors (SMRs)", "Long-Duration Energy Storage (LDES)", "Combined-Cycle Gas + CCUS"]
        }
    },
    "superhot_rock_geothermal": {
        "id": "superhot_rock_geothermal",
        "name": "Superhot Rock Geothermal (>400C Supercritical)",
        "category_id": "geothermal_subsurface",
        "category_name": "Geothermal & Subsurface Energy",
        "headline": "Drilling into 400C–500C supercritical crust to produce 10x more energy per well than conventional geothermal.",
        "trl_current": 4,
        "trl_target": 7,
        "keywords": ["superhot rock", "supercritical", "deep geothermal", "400C", "plasma drilling", "millimeter wave", "Quaise"],
        "sector": "Clean Electricity Generation",
        "fuel_vector": "Supercritical Earth Heat",
        "plain_english": {
            "what_is_it": "Drilling 6 to 12 miles (10 to 20 km) into the deep Earth's crust to tap superhot rock exceeding 750F to 900F (400C to 500C). At this temperature, water becomes 'supercritical'—neither a liquid nor a gas—carrying ten times more energy per gallon than ordinary steam.",
            "how_it_works": "Uses high-energy millimeter wave gyrotrons or fusion-grade plasma torches to vaporize ultra-hard rock without mechanical drill bits that wear out, reaching depths and temperatures impossible with conventional oilfield rotary drilling.",
            "why_it_matters": "Superhot rock has so much energy density that just 2 to 3 wells can repower an entire 500-megawatt coal power plant, using the plant's existing steam turbines and power lines with zero fossil emissions.",
            "macro_problem_solved": "Repowering legacy fossil steam turbine infrastructure and unlocking infinite baseload power anywhere on the planet."
        },
        "evolution": {
            "past": "Accidental volcanic penetrations like Iceland Deep Drilling Project IDDP-1 hitting magma at 2.1km (2009).",
            "present": "Laboratory gyrotron beam drilling tests and deep well design (Quaise Energy, AltaRock, Clean Air Task Force).",
            "future": "First commercial 500C supercritical deep demonstration wells repowering coal plant turbines by 2030-2035."
        },
        "frontier": {
            "moonshot_goal": "Demonstrate continuous power production from a 450C+ supercritical well drilled with non-contact energy beams at <$30/MWh.",
            "kpis": [
                {"name": "Subsurface Temperature Reached", "current": "250C - 300C", "target_2030": "> 450C - 500C", "status": "challenging"},
                {"name": "Energy Output per Well", "current": "3 - 5 MW-e", "target_2030": "40 - 50 MW-e (10x Boost)", "status": "on_track"},
                {"name": "Drilling Depth", "current": "3 - 5 km", "target_2030": "8 - 12 km", "status": "challenging"},
                {"name": "LCOE Levelized Cost", "current": "Pre-commercial", "target_2030": "< $35 / MWh", "status": "on_track"}
            ],
            "bottlenecks": [
                "Drill string material failure, casing collapse, and sensor electronics meltdown above 350C.",
                "Rock behaves plastically (like putty) at >450C, making fracture networks prone to self-healing shut.",
                "Extremely high pressure (>22 MPa) supercritical fluid chemistry causing silica and mineral scaling."
            ],
            "active_research_tracks": [
                "Gyrotron-powered millimeter-wave thermal rock ablation and glass vitrification (DOE ARPA-E OPEN).",
                "High-entropy superalloy well casing liners resistant to supercritical corrosion.",
                "Supercritical CO2 closed-loop thermosiphon wellbore circulation."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 95,
            "capex_competitiveness": 65,
            "duration_scalability": 100,
            "technology_maturity": 40,
            "domestic_supply_chain": 80,
            "siting_permitting_ease": 85
        },
        "trade_offs": {
            "strengths": ["10x higher energy density per wellbore than conventional geothermal", "Can directly repower existing coal and gas steam turbine plants without new infrastructure", "Infinite, inexhaustible baseload power available anywhere on the globe"],
            "weaknesses": ["Very low technology maturity (TRL 4) requiring unproven non-contact drilling technologies", "Extreme materials challenges with casing metallurgy at >450C", "High exploratory R&D capital risk"],
            "competing_technologies": ["Enhanced Geothermal Systems (EGS)", "Fusion Energy", "Small Modular Reactors (SMRs)"]
        }
    },

    # -------------------------------------------------------------------------
    # 5. ENERGY STORAGE & ADVANCED CHEMISTRIES
    # -------------------------------------------------------------------------
    "iron_air_battery": {
        "id": "iron_air_battery",
        "name": "Iron-Air Long-Duration Battery Storage (100-Hour LDES)",
        "category_id": "energy_storage",
        "category_name": "Energy Storage & Advanced Chemistries",
        "headline": "Ultra-low-cost multi-day (100-hour) electrochemical storage utilizing reversible iron rust chemistry.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["iron-air", "LDES", "long duration", "rust", "multi-day", "form energy", "100 hour"],
        "sector": "Grid Energy Storage",
        "fuel_vector": "Electricity Storage",
        "plain_english": {
            "what_is_it": "A battery that breathes in oxygen to turn iron into rust during discharge, releasing electrical energy, and applies electric current to turn the rust back into metallic iron and breathe out oxygen during charging.",
            "how_it_works": "The battery uses an iron metal anode, an air-breathing cathode, and a non-flammable water-based alkaline electrolyte. When discharging, iron oxidizes into iron hydroxide and electrons flow to the grid. When charging, the process is reversed, regenerating pure iron without consuming precious metals.",
            "why_it_matters": "Conventional lithium-ion batteries become economically unviable beyond 4 to 8 hours of discharge. Iron-air provides 100 hours of continuous power at one-tenth the capital cost, allowing the power grid to survive multi-day winter storms and wind lulls ('dunkelflaute') using 100% renewable power.",
            "macro_problem_solved": "Multi-day seasonal renewable intermittency and replacement of fossil-fueled peaker plants."
        },
        "evolution": {
            "past": "Single-cycle iron batteries and short-duration Lead-Acid / Pumped Hydro facilities (1970s-2000s).",
            "present": "Multi-MW pilot deployments (Form Energy, DOE OCED / NYSERDA testbeds, 10-100 MW multi-day storage installations).",
            "future": "Universal sub-station and industrial co-location providing 100-hour firm clean power at <$20/kWh capex by 2030."
        },
        "frontier": {
            "moonshot_goal": "Achieve 100-hour multi-day discharge with 20+ year cycle life at an installed capital cost below $20/kWh.",
            "kpis": [
                {"name": "Installed System CapEx", "current": "$70 - $110 / kWh", "target_2030": "< $20 / kWh", "status": "on_track"},
                {"name": "Discharge Duration", "current": "100 Hours", "target_2030": "100 - 150 Hours", "status": "achieved"},
                {"name": "Round-Trip Efficiency (RTE)", "current": "45% - 50%", "target_2030": "55% - 60%", "status": "challenging"},
                {"name": "Degradation Rate", "current": "< 1.5% / year", "target_2030": "< 0.5% / year", "status": "on_track"}
            ],
            "bottlenecks": [
                "Parasitic Hydrogen Evolution Reaction (HER) during charging reducing round-trip efficiency.",
                "Air cathode catalyst poisoning from atmospheric carbon dioxide forming carbonate crusts.",
                "Large physical footprint compared to lithium-ion, limiting use to rural/substation utility sites rather than dense urban footprints."
            ],
            "active_research_tracks": [
                "Novel electrolyte additives to suppress hydrogen side-reactions at the iron anode (ARPA-E OPEN / PNNL).",
                "Advanced bifunctional oxygen reduction/evolution catalysts with high CO2 tolerance.",
                "Modular factory assembly techniques to achieve multi-gigawatt-hour annual production volume."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 50,
            "capex_competitiveness": 95,
            "duration_scalability": 100,
            "technology_maturity": 70,
            "domestic_supply_chain": 95,
            "siting_permitting_ease": 85
        },
        "trade_offs": {
            "strengths": ["Abundant, non-toxic, domestically available raw materials (iron, water, air)", "Zero fire/thermal runaway risk", "Unbeatable levelized cost for 24-100 hour storage"],
            "weaknesses": ["Lower round-trip efficiency (45-50% vs Li-ion 85-90%)", "Low volumetric energy density (requires 3x ground footprint)", "Slow response time (not suited for fast sub-second frequency regulation)"],
            "competing_technologies": ["Vanadium Redox Flow Batteries", "Pumped Thermal Energy Storage", "Hydrogen Underground Cavern Storage"]
        }
    },
    "vanadium_redox_flow": {
        "id": "vanadium_redox_flow",
        "name": "Vanadium Redox Flow Batteries (VRFB)",
        "category_id": "energy_storage",
        "category_name": "Energy Storage & Advanced Chemistries",
        "headline": "Decoupled power and energy liquid storage with infinite electrolyte reuse and zero degradation.",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["vanadium", "flow battery", "VRFB", "redox flow", "liquid electrolyte", "long duration"],
        "sector": "Grid Energy Storage",
        "fuel_vector": "Electricity Storage",
        "plain_english": {
            "what_is_it": "A battery where energy is stored in two liquid tanks of vanadium-dissolved water. Pumps circulate the liquids past a central membrane cell stack to charge and discharge electricity.",
            "how_it_works": "Vanadium exists in four different oxidation states in solution. Storing energy in liquid tanks means you can increase energy capacity simply by building larger tanks, completely independent of the power rating of the cell stack.",
            "why_it_matters": "Unlike solid batteries that physically degrade after a few thousand cycles, the liquid electrolyte in a flow battery lasts 30+ years without degrading and can be fully recycled or reconditioned.",
            "macro_problem_solved": "Heavy cycling 8-to-24 hour grid stabilization and commercial/industrial peak shaving."
        },
        "evolution": {
            "past": "NASA and UNSW lab proofs-of-concept; early small-scale utility trials (1980s-2010s).",
            "present": "Utility-scale 100MW/400MWh installations globally; multi-hour microgrid and commercial peak-shaving deployments.",
            "future": "Non-vanadium low-cost organic & all-iron chemistries driving system CapEx down to $120/kWh."
        },
        "frontier": {
            "moonshot_goal": "Eliminate raw vanadium commodity price exposure through synthetic organic molecules and domestic slag recovery.",
            "kpis": [
                {"name": "System Capital Cost", "current": "$280 - $380 / kWh", "target_2030": "< $150 / kWh", "status": "challenging"},
                {"name": "Cycle Life", "current": "20,000+ Cycles", "target_2030": "30,000+ Cycles", "status": "achieved"},
                {"name": "Round-Trip Efficiency", "current": "70% - 75%", "target_2030": "80% - 82%", "status": "on_track"},
                {"name": "Membrane Lifetime", "current": "10 - 15 Years", "target_2030": "25+ Years", "status": "on_track"}
            ],
            "bottlenecks": [
                "High raw vanadium chemical cost representing 35-45% of total system CapEx.",
                "Ion crossover through the ion-exchange membrane causing gradual capacity unbalance.",
                "Pumping parasitic losses and thermal management constraints in sub-freezing climates."
            ],
            "active_research_tracks": [
                "Hydrocarbon-based non-PFAS ion-exchange membranes with zero vanadium crossover (DOE EERE).",
                "High-concentration mixed-acid electrolytes operating across wider temperature windows (-10C to 50C).",
                "Electrolyte leasing business models separating capital cost from project balance sheets."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 72,
            "capex_competitiveness": 65,
            "duration_scalability": 90,
            "technology_maturity": 85,
            "domestic_supply_chain": 75,
            "siting_permitting_ease": 88
        },
        "trade_offs": {
            "strengths": ["Near-infinite cycle life (>20,000 cycles) with zero degradation", "Independent scaling of power (kW) and energy (kWh)", "100% non-flammable water-based chemistry"],
            "weaknesses": ["Higher upfront capital cost than Lithium Iron Phosphate (LFP) for <6hr duration", "Fluid piping, pumps, and valves require mechanical maintenance", "Moderate energy density requires large footprint"],
            "competing_technologies": ["Lithium Iron Phosphate (LFP)", "Iron-Air Batteries", "Sodium-Sulfur High Temp Batteries"]
        }
    },
    "solid_state_lithium": {
        "id": "solid_state_lithium",
        "name": "All-Solid-State Lithium Metal Batteries (ASSB)",
        "category_id": "energy_storage",
        "category_name": "Energy Storage & Advanced Chemistries",
        "headline": "Replacing flammable liquid electrolytes with solid ceramic/sulfide separators to achieve >450 Wh/kg and 10-minute fast charging.",
        "trl_current": 6,
        "trl_target": 9,
        "keywords": ["solid-state", "lithium metal", "solid electrolyte", "ceramic separator", "EV battery", "QuantumScape", "Solid Power"],
        "sector": "High-Density Energy Storage",
        "fuel_vector": "Electrochemical Storage",
        "plain_english": {
            "what_is_it": "Batteries that replace the flammable liquid chemical electrolyte found inside current phone and EV batteries with a non-flammable solid ceramic or polymer layer, paired with a pure lithium metal anode.",
            "how_it_works": "Traditional lithium batteries use porous plastic soaked in flammable organic solvent. Solid-state batteries conduct lithium ions directly through a solid crystal lattice (sulfides, oxides, or halides). Because the separator is physically solid and puncture-proof, it enables pure lithium metal anodes that hold twice as much energy.",
            "why_it_matters": "Eliminates EV battery fires, doubles vehicle driving range on a single charge (500-700 miles), and enables ultra-fast 10-minute charging without overheating or degrading the battery.",
            "macro_problem_solved": "EV range anxiety, charging dwell time, and flammable thermal runaway risks."
        },
        "evolution": {
            "past": "Thin-film micro-batteries for medical implants and smart cards (1990s-2015).",
            "present": "Automotive A-sample and B-sample multi-layer cell testing (QuantumScape, Solid Power, Factorial, Toyota).",
            "future": "Commercial gigafactory roll-out powering premium EVs and electric aviation by 2028-2032."
        },
        "frontier": {
            "moonshot_goal": "Produce commercial automotive cells delivering >500 Wh/kg and 1,000 Wh/L with 1,000 cycles at <$70/kWh pack cost.",
            "kpis": [
                {"name": "Gravimetric Energy Density", "current": "380 - 420 Wh / kg", "target_2030": "> 500 Wh / kg", "status": "on_track"},
                {"name": "Fast Charge Time (10% to 80%)", "current": "12 - 15 Minutes", "target_2030": "< 8 Minutes", "status": "on_track"},
                {"name": "Operating Pressure Required", "current": "1 - 5 MPa (Stack clamp)", "target_2030": "< 0.2 MPa (Ambient)", "status": "challenging"},
                {"name": "Manufacturing Scrap Rate", "current": "20% - 35% (Pilot)", "target_2030": "< 5% (Commercial)", "status": "challenging"}
            ],
            "bottlenecks": [
                "Lithium dendrite growth short-circuiting along microscopic ceramic grain boundaries during high-rate fast charging.",
                "Solid-solid interfacial contact impedance causing high resistance as the lithium metal anode expands and contracts during cycling.",
                "Sulfide solid electrolytes generate toxic hydrogen sulfide (H2S) gas if exposed to ambient moisture during manufacturing."
            ],
            "active_research_tracks": [
                "Ultra-thin (10-20 um) flexible oxide/polymer composite separators with high mechanical shear modulus (DOE VTO).",
                "Lithium-free anode-less architectures plating pure lithium in-situ on first charge.",
                "Dry-room roll-to-roll continuous calender manufacturing reducing capital equipment costs."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 94,
            "capex_competitiveness": 65,
            "duration_scalability": 75,
            "technology_maturity": 65,
            "domestic_supply_chain": 80,
            "siting_permitting_ease": 95
        },
        "trade_offs": {
            "strengths": ["Near-zero fire or thermal runaway risk", "2x higher energy density than traditional Lithium Iron Phosphate (LFP)", "Enables sub-10 minute EV fast charging"],
            "weaknesses": ["Requires high stack pressure clamps inside the battery pack", "High manufacturing scrap rates in early production", "Vulnerable to lithium dendrite short circuits under freezing conditions"],
            "competing_technologies": ["Silicon-Dominant Anode Lithium-Ion", "Sodium-Ion Batteries", "Lithium-Sulfur Batteries"]
        }
    },
    "sodium_ion_battery": {
        "id": "sodium_ion_battery",
        "name": "Sodium-Ion Batteries (NIB) & Prussian Blue Chemistries",
        "category_id": "energy_storage",
        "category_name": "Energy Storage & Advanced Chemistries",
        "headline": "Zero-lithium, zero-cobalt, zero-nickel electrochemical storage utilizing cheap, abundant table salt precursors.",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["sodium-ion", "Prussian blue", "hard carbon", "zero lithium", "CATL", "Natron Energy", "low cost battery"],
        "sector": "Cost-Optimized Energy Storage",
        "fuel_vector": "Electrochemical Storage",
        "plain_english": {
            "what_is_it": "Batteries that work just like lithium-ion batteries, but swap out expensive lithium, cobalt, and nickel for cheap, universally abundant sodium (from salt) and iron/manganese.",
            "how_it_works": "Sodium ions move between a hard-carbon anode and a layered oxide or Prussian Blue cathode. Because sodium doesn't form alloys with aluminum, cheap aluminum foil can be used for both positive and negative current collectors instead of expensive copper.",
            "why_it_matters": "Sodium is 1,000 times more abundant than lithium and can be safely discharged all the way to 0 volts for 100% safe zero-risk transport. It performs exceptionally well in sub-zero freezing weather (-4F / -20C).",
            "macro_problem_solved": "Lithium/nickel supply chain bottlenecks and cold-weather battery degradation."
        },
        "evolution": {
            "past": "Academic research in parallel with early lithium batteries in the 1980s (abandoned due to lower energy density).",
            "present": "Mass production scaling in commercial stationary BESS and compact urban EVs (CATL, Natron Energy, HiNa Battery).",
            "future": "Dominating 40%+ of global stationary grid storage and entry-level EVs at <$40/kWh pack cost by 2028."
        },
        "frontier": {
            "moonshot_goal": "Achieve 200 Wh/kg cell energy density and 5,000+ cycle life at a raw materials cost under $30/kWh.",
            "kpis": [
                {"name": "Gravimetric Energy Density", "current": "145 - 165 Wh / kg", "target_2030": "> 200 Wh / kg", "status": "on_track"},
                {"name": "Sub-Zero Capacity Retention (-20C)", "current": "88% - 92%", "target_2030": "> 95%", "status": "achieved"},
                {"name": "Cycle Life (Stationary)", "current": "4,000 - 8,000 Cycles", "target_2030": "> 12,000 Cycles", "status": "on_track"},
                {"name": "Pack Manufacturing Cost", "current": "$60 - $85 / kWh", "target_2030": "< $40 / kWh", "status": "on_track"}
            ],
            "bottlenecks": [
                "Larger ionic radius of sodium (1.02 A vs 0.76 A for lithium) causing slower diffusion and electrode swelling.",
                "Lower energy density limits use in long-range premium electric vehicles and aviation.",
                "First-cycle Coulombic efficiency loss on hard-carbon anodes requiring pre-sodiation steps."
            ],
            "active_research_tracks": [
                "Bio-derived hard carbon anodes synthesized from agricultural waste (lignin, sugar, peanut shells).",
                "High-entropy Prussian white crystal cathode structures with defect-free water elimination.",
                "Non-flammable all-solid polymer and ionic liquid sodium electrolytes."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 90,
            "capex_competitiveness": 96,
            "duration_scalability": 85,
            "technology_maturity": 85,
            "domestic_supply_chain": 95,
            "siting_permitting_ease": 92
        },
        "trade_offs": {
            "strengths": ["Immune to lithium, nickel, and cobalt commodity price spikes", "Can be safely shipped and transported at 0 Volts (zero fire risk)", "Superior cold-weather capacity retention down to -20C"],
            "weaknesses": ["Lower energy density than nickel-manganese-cobalt (NMC) lithium batteries", "Larger physical pack weight for the same vehicle range", "Mature supply chain still expanding outside Asia"],
            "competing_technologies": ["Lithium Iron Phosphate (LFP)", "Sodium-Sulfur", "Redox Flow Batteries"]
        }
    },

    # -------------------------------------------------------------------------
    # 6. GRID MODERNIZATION, GETS & DIGITAL POWER
    # -------------------------------------------------------------------------
    "grid_enhancing_technologies": {
        "id": "grid_enhancing_technologies",
        "name": "Grid-Enhancing Technologies (GETs) & Dynamic Line Rating",
        "category_id": "grid_modernization",
        "category_name": "Grid Modernization, GETs & Digital Power",
        "headline": "Dynamic Line Rating (DLR), modular power flow control, and topology optimization unlocking 30-40% more grid capacity on existing transmission lines.",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["GETs", "dynamic line rating", "DLR", "power flow control", "grid enhancing", "topology optimization", "FERC 1920", "Smart Wires", "LineVision"],
        "sector": "Transmission & Distribution Infrastructure",
        "fuel_vector": "Transmission Optimization",
        "plain_english": {
            "what_is_it": "Hardware sensors and smart routing devices clamped onto existing high-voltage transmission lines that calculate how much wind is cooling the wires in real time, allowing utilities to push 30% to 40% more renewable electricity through existing power lines without building new towers.",
            "how_it_works": "Power lines are normally capped at static, conservative summer limits because wires sag when they get hot. Dynamic Line Rating (DLR) sensors measure real-time wind speed, temperature, and line sag. Modular power flow controllers act like smart highway valves, pushing power away from congested lines onto empty parallel circuits.",
            "why_it_matters": "Building new transmission lines takes 10 to 15 years due to permitting battles. GETs can be installed in months at 5% of the cost, instantly unclogging the 2,600+ gigawatt renewable interconnection queue waiting to connect to the US grid.",
            "macro_problem_solved": "Transmission interconnection bottlenecks and multi-year permitting delays for new power lines."
        },
        "evolution": {
            "past": "Fixed seasonal thermal line ratings and manually operated mechanical substation switches (1950-2015).",
            "present": "Commercial utility sensor deployments (LineVision, Smart Wires, Heimdall Power) mandated by FERC Order 881/1920.",
            "future": "Fully autonomous closed-loop AI dynamic line rating and solid-state power flow control across all ISO/RTO grids by 2028."
        },
        "frontier": {
            "moonshot_goal": "Double the effective transmission throughput of the existing North American transmission grid with zero new rights-of-way.",
            "kpis": [
                {"name": "Transmission Capacity Unlock", "current": "15% - 28% typical", "target_2030": "35% - 50% continuous", "status": "on_track"},
                {"name": "Deployment Duration per Line", "current": "3 - 6 Months", "target_2030": "< 2 Weeks (Plug-and-play)", "status": "achieved"},
                {"name": "Cost vs Building New Lines", "current": "5% - 10% of new line capex", "target_2030": "< 3% of new line capex", "status": "achieved"},
                {"name": "Closed-Loop EMS Integration", "current": "Advisory/Day-ahead", "target_2030": "Sub-minute automated dispatch", "status": "on_track"}
            ],
            "bottlenecks": [
                "Utility cost-of-service incentive models rewarding capital-intensive new wire construction over software/hardware efficiency.",
                "Legacy Energy Management Systems (EMS) software cannot digest real-time dynamic thermal ratings without cybersecurity re-validation.",
                "Lack of standardized liability frameworks during extreme storm-driven N-1 contingency overloads."
            ],
            "active_research_tracks": [
                "Advanced composite core conductors (ACCC) doubling ampacity on existing rights-of-way (DOE Grid Modernization Lab Consortium).",
                "Non-contact lidar and ultrasonic electromagnetic acoustic sensors monitoring conductor core annealing.",
                "AI-driven topology optimization automatically switching substation breakers to route around bottlenecks."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 99,
            "capex_competitiveness": 98,
            "duration_scalability": 95,
            "technology_maturity": 88,
            "domestic_supply_chain": 90,
            "siting_permitting_ease": 98
        },
        "trade_offs": {
            "strengths": ["Installs in weeks with zero environmental or right-of-way permitting battles", "5-10% the cost of building new high-voltage transmission lines", "Immediately relieves wind and solar curtailment bottlenecks"],
            "weaknesses": ["Does not add physical new rights-of-way for 1,000-mile cross-country bulk power exports", "Requires operational integration with legacy utility Energy Management Systems (EMS)", "Utility regulatory incentives often favor capital-heavy new asset buildouts"],
            "competing_technologies": ["High-Voltage Direct Current (HVDC) Lines", "Advanced Reconductoring (ACCC)", "Battery Energy Storage as Transmission Assets (SATA)"]
        }
    },
    "advanced_inverters_grid_forming": {
        "id": "advanced_inverters_grid_forming",
        "name": "Grid-Forming Inverters (GFM) & Black-Start Synchronous Emulation",
        "category_id": "grid_modernization",
        "category_name": "Grid Modernization, GETs & Digital Power",
        "headline": "Inverter-based power electronics providing synthetic inertia, voltage reference, and black-start restoration without fossil generators.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["grid-forming", "GFM", "inverter", "synthetic inertia", "black-start", "IEEE 2800", "UNIFI", "microgrid"],
        "sector": "Grid Reliability & Power Electronics",
        "fuel_vector": "Power Electronics Control",
        "plain_english": {
            "what_is_it": "Smart power electronic converters connected to solar and battery facilities that act like giant spinning turbine generators, establishing and stabilizing the electric grid's 60-hertz heartbeat without needing a single fossil fuel turbine.",
            "how_it_works": "Conventional solar/battery inverters are 'grid-following'—they need the utility grid to already be stable and simply inject current into it. 'Grid-forming' (GFM) inverters act as a pure voltage source, instantaneously responding to power surges in microseconds and restarting the entire power grid from scratch after a total blackout ('black-start').",
            "why_it_matters": "As fossil and nuclear plants retire, the grid loses the physical spinning mass (inertia) that keeps frequency stable. GFM inverters allow grids to run reliably on 100% inverter-based wind, solar, and battery storage with zero fossil spinning reserves.",
            "macro_problem_solved": "Frequency instability and loss of grid inertia in high-renewable zero-fossil power systems."
        },
        "evolution": {
            "past": "Grid-following inverters that tripped offline during voltage dips or severe frequency disturbances (2000-2020).",
            "present": "Utility battery installations operating in GFM mode in Hawaii, South Australia (Hornsdale), and Texas ERCOT.",
            "future": "Universal IEEE 2800 compliance making grid-forming control standard across all utility-scale solar, wind, and storage by 2028."
        },
        "frontier": {
            "moonshot_goal": "Operate an interconnected regional grid on 100% inverter-based resources with faster transient response and higher stability than fossil steam generators.",
            "kpis": [
                {"name": "Instantaneous Inertia Response", "current": "< 5 Milliseconds", "target_2030": "< 1 Millisecond (Sub-cycle)", "status": "achieved"},
                {"name": "Inverter Resource Penetration", "current": "75% - 85% peak instantaneous", "target_2030": "100% Stable Operation", "status": "on_track"},
                {"name": "Black-Start Restoration Time", "current": "15 - 30 Minutes", "target_2030": "< 5 Minutes", "status": "on_track"},
                {"name": "Hardware Cost Premium vs GFL", "current": "+4% - +8%", "target_2030": "0% (Pure firmware standard)", "status": "on_track"}
            ],
            "bottlenecks": [
                "Silicon IGBT semiconductors have strict thermal current limits and cannot provide 5x-6x overcurrent fault surge like heavy iron spinning generators.",
                "Sub-synchronous resonance (SSR) and control interaction oscillations between adjacent multi-vendor GFM inverters.",
                "Lack of standardized interconnection compensation tariffs paying storage developers for providing synthetic inertia."
            ],
            "active_research_tracks": [
                "Silicon Carbide (SiC) and Gallium Nitride (GaN) wide-bandgap semiconductors with 3x higher surge current tolerance (DOE UNIFI).",
                "Virtual Synchronous Machine (VSM) and Droop Control harmonization across heterogeneous wind/solar/BESS fleets.",
                "Adaptive damping algorithms suppressing low-frequency inter-area oscillations."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 98,
            "capex_competitiveness": 92,
            "duration_scalability": 95,
            "technology_maturity": 78,
            "domestic_supply_chain": 85,
            "siting_permitting_ease": 95
        },
        "trade_offs": {
            "strengths": ["Enables 100% renewable power grids without keeping fossil plants running for inertia", "Instantaneous sub-millisecond frequency response (10x faster than mechanical governors)", "Can black-start isolated microgrids and island grids without external power"],
            "weaknesses": ["Inverters cannot provide heavy sustained overcurrent during lightning short-circuits without oversized silicon", "Control interactions between competing vendor software algorithms can cause harmonic ringing", "Utility operators require new protection relay schemes"],
            "competing_technologies": ["Synchronous Condensers (Free-Spinning Motors)", "Hydroelectric Governors", "Fossil Gas Peaker Turbines"]
        }
    },
    "hvdc_transmission_interconnects": {
        "id": "hvdc_transmission_interconnects",
        "name": "High-Voltage Direct Current (HVDC) Transmission & Interconnects",
        "category_id": "grid_modernization",
        "category_name": "Grid Modernization, GETs & Digital Power",
        "headline": "Voltage-Source Converter (VSC) HVDC moving gigawatts of wind and solar over 1,000+ miles with 50% lower line losses.",
        "trl_current": 9,
        "trl_target": 9,
        "keywords": ["HVDC", "high voltage direct current", "VSC", "transmission", "subsea cable", "interconnection", "TransWest Express"],
        "sector": "Transmission Infrastructure",
        "fuel_vector": "Bulk Power Transmission",
        "plain_english": {
            "what_is_it": "High-tech electricity superhighways that convert alternating current (AC) power into direct current (DC) to transport massive amounts of clean wind and solar electricity across thousands of miles or underwater with almost zero line losses.",
            "how_it_works": "AC power loses significant energy over long distances due to electromagnetic capacitance. HVDC converter stations turn AC into +/- 525kV or +/- 800kV DC power, shoot it across thin underground or overhead cables, and convert it back to AC at city gates, linking separate regional power grids without frequency interference.",
            "why_it_matters": "The best wind blows in Wyoming and the Plains, and the best solar is in the Desert Southwest, but the biggest cities are on the coasts. HVDC connects low-cost remote clean energy directly to urban centers.",
            "macro_problem_solved": "Long-distance renewable transmission loss and linking asynchronous regional power grids (Eastern, Western, ERCOT)."
        },
        "evolution": {
            "past": "Line-Commutated Converter (LCC) thyristor links requiring strong AC grids (1970-2010).",
            "present": "Voltage-Source Converter (VSC) multi-terminal projects (Champlain Hudson Power Express, TransWest Express).",
            "future": "Nationwide multi-terminal HVDC Supergrid interconnecting Eastern, Western, and Texas grids by 2035."
        },
        "frontier": {
            "moonshot_goal": "Deploy a 50+ GW inter-regional HVDC macrogrid bridging the Eastern, Western, and ERCOT interconnections with sub-second bi-directional flow.",
            "kpis": [
                {"name": "Transmission Line Losses", "current": "3% per 1,000 km", "target_2030": "< 2% per 1,000 km", "status": "achieved"},
                {"name": "Converter Station Footprint", "current": "Large Substation (5-8 Acres)", "target_2030": "< 2 Acres (Modular SiC)", "status": "on_track"},
                {"name": "Multi-Terminal DC Circuit Breaker", "current": "Hybrid Prototype (<5ms)", "target_2030": "< 2ms Solid-State Standard", "status": "on_track"},
                {"name": "Cross-Interconnection Transfer Cap", "current": "1.3 GW (Asynchronous ties)", "target_2030": "> 30.0 GW Macrogrid", "status": "on_track"}
            ],
            "bottlenecks": [
                "Extreme multi-state right-of-way permitting and interstate cost-allocation disputes.",
                "High upfront capital cost of bi-directional AC-DC converter stations ($300M-$500M per station).",
                "Lack of standardized multi-vendor DC circuit breakers for meshed multi-terminal DC networks."
            ],
            "active_research_tracks": [
                "Modular Multilevel Converters (MMC) using high-voltage Silicon Carbide MOSFETs (DOE OE).",
                "High-temperature superconducting (HTS) underground DC cables carrying 5 GW in a 1-meter trench.",
                "Subsea HVDC dynamic cables connecting deepwater floating offshore wind clusters."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 96,
            "capex_competitiveness": 65,
            "duration_scalability": 100,
            "technology_maturity": 90,
            "domestic_supply_chain": 75,
            "siting_permitting_ease": 58
        },
        "trade_offs": {
            "strengths": ["Lowest electrical loss for long-distance (>500 miles) and underwater power transmission", "Allows complete decoupling of asynchronous regional power grids (zero blackout cascading)", "Can be routed underground along existing railroad and highway rights-of-way"],
            "weaknesses": ["Very high capital cost for AC-DC converter terminal stations", "Complex multi-state regulatory and interstate commerce permitting", "Multi-terminal branching is technically complex compared to simple AC substations"],
            "competing_technologies": ["Ultra-High Voltage AC (UHVAC)", "Local Distributed Solar + Storage", "On-site Green Hydrogen Generation & Pipelines"]
        }
    },
    "vpp_derms_orchestration": {
        "id": "vpp_derms_orchestration",
        "name": "Virtual Power Plants (VPPs) & DERMS Orchestration",
        "category_id": "grid_modernization",
        "category_name": "Grid Modernization, GETs & Digital Power",
        "headline": "Cloud software aggregating hundreds of thousands of residential batteries, smart thermostats, and EVs into dispatchable gigawatt power plants.",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["VPP", "virtual power plant", "DERMS", "demand response", "distributed energy", "smart thermostat", "Tesla Electric", "OhmConnect"],
        "sector": "Digital Grid Software",
        "fuel_vector": "Flexible Electric Load",
        "plain_english": {
            "what_is_it": "Smart cloud software that connects thousands of everyday home batteries, electric cars, smart thermostats, and water heaters into a single giant 'virtual' power plant that supplies power to the grid during heatwaves and freezes.",
            "how_it_works": "When grid demand spikes, the VPP platform sends automatic digital signals to pre-cool buildings, slightly pause EV charging, or discharge home solar batteries for 1 to 2 hours. Homeowners get cash rewards and lower utility bills while remaining completely comfortable.",
            "why_it_matters": "Building new gas peaker plants costs hundreds of millions of dollars and takes years. VPPs unlock gigawatts of clean, instant peaking capacity from equipment people already own, saving consumers and utilities billions in grid upgrades.",
            "macro_problem_solved": "Peak electricity demand spikes and avoiding costly fossil gas peaker plant construction."
        },
        "evolution": {
            "past": "Manual utility telephone calls asking industrial factories to shut down during grid emergencies (1990-2015).",
            "present": "Automated residential VPP programs aggregating 50-500 MW in California, Texas, and New York (NYSERDA, ERCOT, CEC).",
            "future": "Universal AI autonomous DERMS orchestrating 100+ GW of flexible distributed energy nationwide by 2030."
        },
        "frontier": {
            "moonshot_goal": "Scale US Virtual Power Plant capacity from 25 GW to 160 GW by 2030, serving 15% of peak national power demand (DOE Liftoff VPP).",
            "kpis": [
                {"name": "Aggregated US VPP Capacity", "current": "25 - 30 GW (Mostly C&I)", "target_2030": "> 160 GW (Residential + Fleet)", "status": "on_track"},
                {"name": "Dispatch Response Latency", "current": "1 - 5 Minutes", "target_2030": "< 4 Seconds (Fast frequency)", "status": "on_track"},
                {"name": "Customer Net Annual Earnings", "current": "$150 - $400 / year", "target_2030": "> $800 / year", "status": "on_track"},
                {"name": "Utility System CapEx Savings", "current": "$2B / year", "target_2030": "> $10B / year", "status": "on_track"}
            ],
            "bottlenecks": [
                "Fragmented utility regulatory tariffs and complex customer enrollment friction.",
                "Lack of standardized API protocols across disparate smart device and EV manufacturers (OpenADR / IEEE 2030.5).",
                "Cybersecurity concerns regarding simultaneous remote control of millions of grid-connected consumer endpoints."
            ],
            "active_research_tracks": [
                "Edge-AI decentralized coordination optimizing transformer-level loading without centralized cloud latency (DOE OE).",
                "Automated zero-click customer onboarding integrations with smart meters.",
                "Dynamic retail real-time locational marginal pricing (LMP) signals passed directly to home energy management systems."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 95,
            "capex_competitiveness": 99,
            "duration_scalability": 90,
            "technology_maturity": 88,
            "domestic_supply_chain": 95,
            "siting_permitting_ease": 98
        },
        "trade_offs": {
            "strengths": ["Zero physical land or environmental footprint (uses existing consumer hardware)", "Ultra-low capital cost compared to building new gas peaker plants", "Directly pays money back to residential and business utility customers"],
            "weaknesses": ["Dependent on consumer behavior and opt-in participation rates", "Limited duration (typically 1-4 hours per demand response event)", "Complex cybersecurity attack surface across millions of IoT devices"],
            "competing_technologies": ["Fossil Gas Peaker Plants", "Utility-Scale 4-Hour Battery Storage", "Grid-Enhancing Technologies (GETs)"]
        }
    },

    # -------------------------------------------------------------------------
    # 7. CLEAN HYDROGEN & SYNTHETIC MOLECULES
    # -------------------------------------------------------------------------
    "pem_soec_electrolyzers": {
        "id": "pem_soec_electrolyzers",
        "name": "Advanced Electrolyzers (PEM, SOEC & AEM)",
        "category_id": "clean_hydrogen",
        "category_name": "Clean Hydrogen & Synthetic Molecules",
        "headline": "Splitting pure water molecules into zero-carbon hydrogen at scale using renewable electricity and steam.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["electrolyzer", "green hydrogen", "PEM", "SOEC", "AEM", "water splitting", "Hydrogen Shot", "Plug Power"],
        "sector": "Clean Fuel Synthesis",
        "fuel_vector": "Green Hydrogen (H2)",
        "vector_type": "fuel_carrier",
        "fuel_profile": {
            "carrier_name": "Clean Molecular Hydrogen (H2)",
            "chemical_formula": "H2 (Zero-Carbon Molecular Fuel)",
            "carbon_intensity_ci": "0.0 - 0.45 kg CO2e/kg H2 (<4 g CO2e/MJ with renewable power)",
            "energy_density_gravimetric": "120.0 MJ/kg (LHV) / 141.8 MJ/kg (HHV)",
            "energy_density_volumetric": "10.8 MJ/m³ (Gas at NTP) / 8.5 MJ/L (Liquid at 20 K)",
            "feedstock_pathway": "Deionized water + renewable/nuclear electricity (electrolysis); methane pyrolysis",
            "drop_in_compatibility": "Up to 5-15% pipeline blend in existing gas networks; 100% dedicated H2 pipelines, industrial furnaces, or fuel cell vehicles",
            "policy_incentives": "IRA §45V Clean Hydrogen Production Credit ($3.00/kg top tier), DOE Hydrogen Shot ($1/kg)"
        },
        "plain_english": {
            "what_is_it": "Machines that use clean electricity to split plain water into pure hydrogen and pure oxygen gas, creating a clean-burning fuel that releases only water vapor when used in trucks, steel mills, and power plants.",
            "how_it_works": "Proton Exchange Membrane (PEM) units use precious metal catalysts to split room-temperature water instantly. Solid Oxide (SOEC) units operate at red-hot temperatures (1,300F / 700C) using industrial waste steam to achieve over 90% electrical efficiency. Anion Exchange Membrane (AEM) combines the speed of PEM with cheap, non-precious nickel catalysts.",
            "why_it_matters": "Heavy industry (steel, fertilizer, chemicals, maritime shipping) cannot run on batteries alone. Clean hydrogen replaces fossil natural gas and coal in high-heat manufacturing and long-haul transportation.",
            "macro_problem_solved": "Decarbonizing heavy industrial chemicals, maritime fuel, and seasonal energy storage."
        },
        "evolution": {
            "past": "Fossil steam methane reforming (gray hydrogen) and bulky alkaline liquid electrolyzers (1950-2015).",
            "present": "Multi-megawatt PEM and alkaline automated gigafactories (Plug Power, Nel, Electric Hydrogen, Bloom Energy).",
            "future": "Gigawatt-scale standardized stacks operating at <$1.50/kg clean H2 with zero iridium catalysts by 2030."
        },
        "frontier": {
            "moonshot_goal": "Reduce the cost of clean hydrogen to $1 per 1 kilogram in 1 decade (DOE Hydrogen Shot: '1 1 1').",
            "kpis": [
                {"name": "Levelized Production Cost", "current": "$3.80 - $5.50 / kg H2", "target_2030": "< $1.50 / kg H2", "status": "challenging"},
                {"name": "Stack Electrical Efficiency", "current": "62% - 70% (PEM) / 82% (SOEC)", "target_2030": "> 85% (PEM) / > 92% (SOEC)", "status": "on_track"},
                {"name": "Iridium Loading in Anode", "current": "0.4 - 0.8 mg / cm2", "target_2030": "< 0.05 mg / cm2 (90% cut)", "status": "on_track"},
                {"name": "Stack Lifetime (Continuous)", "current": "40,000 - 60,000 Hours", "target_2030": "> 80,000 Hours", "status": "on_track"}
            ],
            "bottlenecks": [
                "Extreme global scarcity and price volatility of Iridium catalysts required on PEM oxygen-evolving anodes.",
                "Thermal cycling degradation and ceramic seal cracking in high-temperature Solid Oxide (SOEC) cells during renewable on/off cycles.",
                "High electricity cost: Power represents 65-75% of total clean hydrogen production costs."
            ],
            "active_research_tracks": [
                "Porous transport layer (PTL) titanium micro-coatings and non-PGM catalysts (DOE HFTO / NREL).",
                "Pressurized direct alkaline and AEM water electrolysis generating 30-bar hydrogen directly without mechanical compressors.",
                "Co-electrolysis of steam (H2O) and captured carbon dioxide (CO2) to synthesize green syngas in a single step."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 68,
            "capex_competitiveness": 70,
            "duration_scalability": 98,
            "technology_maturity": 78,
            "domestic_supply_chain": 82,
            "siting_permitting_ease": 80
        },
        "trade_offs": {
            "strengths": ["Zero-emission replacement for fossil fuels in high-heat industry and heavy freight", "Energy can be stored in massive underground salt caverns for months", "Can be synthesized into green ammonia, methanol, and aviation fuels"],
            "weaknesses": ["Electricity-to-hydrogen-to-electricity round-trip efficiency is lower (35-45%) than direct batteries (85-90%)", "Hydrogen molecules are tiny and prone to leak or embrittle legacy steel pipes", "Requires low-cost renewable power (<$0.025/kWh) to be commercially competitive"],
            "competing_technologies": ["Steam Methane Reforming + CCUS (Blue H2)", "Methane Pyrolysis (Turquoise H2)", "Direct Industrial Electrification"]
        }
    },
    "underground_hydrogen_storage": {
        "id": "underground_hydrogen_storage",
        "name": "Underground Salt Cavern Hydrogen Storage",
        "category_id": "clean_hydrogen",
        "category_name": "Clean Hydrogen & Synthetic Molecules",
        "headline": "Storing thousands of tons of compressed pure hydrogen in geological salt domes to provide seasonal multi-terawatt-hour storage.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["salt cavern", "hydrogen storage", "geological storage", "seasonal storage", "ACES Delta", "solution mining"],
        "sector": "Bulk Energy Storage",
        "fuel_vector": "Geological Gas Storage",
        "vector_type": "fuel_carrier",
        "fuel_profile": {
            "carrier_name": "Geologically Stored Molecular Hydrogen",
            "chemical_formula": "H2 Compressed in Salt Caverns (150-200 bar)",
            "carbon_intensity_ci": "Preserves upstream zero-carbon production CI (<0.45 kg CO2e/kg H2)",
            "energy_density_gravimetric": "120.0 MJ/kg (LHV)",
            "energy_density_volumetric": "150 - 250 bar downhole working gas pressure",
            "feedstock_pathway": "Deep bedded salt domes, solution-mined salt caverns, and depleted gas fields",
            "drop_in_compatibility": "Direct withdrawal into regional hydrogen transport pipelines and industrial clusters",
            "policy_incentives": "DOE Regional Clean Hydrogen Hubs ($8B federal program), BIL Section 40314"
        },
        "plain_english": {
            "what_is_it": "Hollowing out giant airtight caverns thousands of feet underground inside deep geological salt domes to store millions of pounds of pure green hydrogen gas, acting as a nation-sized battery for seasonal power.",
            "how_it_works": "Water is pumped into deep underground salt formations to dissolve salt and create cavernous underground rooms ('solution mining'). Green hydrogen generated during sunny spring months is compressed and stored in the cavern. In winter, the hydrogen is withdrawn to run power turbines and heat cities.",
            "why_it_matters": "Batteries can store electricity for hours; salt caverns can store terawatt-hours of energy for months with zero leakage, guaranteeing that cities never run out of clean energy during extended multi-week winter storms.",
            "macro_problem_solved": "Inter-seasonal renewable energy storage and strategic national clean fuel reserves."
        },
        "evolution": {
            "past": "Natural gas and petroleum strategic reserves stored in salt domes (e.g. US Strategic Petroleum Reserve, 1970-present).",
            "present": "World's largest clean hydrogen storage facility under construction in Delta, Utah (ACES Delta, DOE LPO loan guarantee).",
            "future": "Interconnected nationwide salt cavern storage nodes supporting regional hydrogen transport pipelines by 2030."
        },
        "frontier": {
            "moonshot_goal": "Demonstrate zero-leakage, high-cycling salt cavern storage holding >5,000 tons of hydrogen with <$0.20/kg levelized storage cost.",
            "kpis": [
                {"name": "Cavern Storage Working Gas", "current": "2,000 - 5,500 Tons H2", "target_2030": "> 10,000 Tons H2", "status": "on_track"},
                {"name": "Levelized Storage Cost", "current": "$0.50 - $0.80 / kg H2", "target_2030": "< $0.20 / kg H2", "status": "on_track"},
                {"name": "Hydrogen Gas Loss Rate", "current": "< 0.05% / year", "target_2030": "< 0.01% / year", "status": "achieved"},
                {"name": "Withdrawal Flow Rate", "current": "50 - 100 Tons / day", "target_2030": "> 250 Tons / day", "status": "on_track"}
            ],
            "bottlenecks": [
                "Salt domes are geographically restricted to the US Gulf Coast, Texas, Utah, and portions of the Great Lakes/New York.",
                "Microbial contamination (methanogens and sulfate-reducing bacteria) consuming hydrogen underground and generating toxic H2S.",
                "Wellhead steel casing and elastomer seal embrittlement under cyclic 150-bar hydrogen pressure."
            ],
            "active_research_tracks": [
                "Depleted gas field and porous sandstone aquifer hydrogen storage testing for regions without natural salt domes (DOE HFTO).",
                "Advanced polymer wellbore packers and corrosion-resistant nickel alloy liners.",
                "Thermodynamic modeling of rapid cavern de-pressurization avoiding salt wall spalling and micro-fracturing."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 75,
            "capex_competitiveness": 90,
            "duration_scalability": 100,
            "technology_maturity": 75,
            "domestic_supply_chain": 95,
            "siting_permitting_ease": 75
        },
        "trade_offs": {
            "strengths": ["Lowest capital cost per kilowatt-hour for seasonal multi-month storage", "Impermeable self-healing salt walls prevent hydrogen leakage", "Enormous capacity (one cavern can power a medium city for weeks)"],
            "weaknesses": ["Geographically constrained to locations with natural subsurface salt formations", "Requires brine disposal infrastructure during cavern solution mining", "High cushion gas requirements (requires keeping 30% of gas permanently in the cavern for pressure stability)"],
            "competing_technologies": ["High-Pressure Above-Ground Steel Tanks", "Cryogenic Liquid Hydrogen Storage", "Chemical Carrier Molecules (Ammonia / LOHC)"]
        }
    },

    # -------------------------------------------------------------------------
    # 8. BIOENERGY, SUSTAINABLE FUELS & WASTE-TO-ENERGY
    # -------------------------------------------------------------------------
    "sustainable_aviation_fuels": {
        "id": "sustainable_aviation_fuels",
        "name": "Sustainable Aviation Fuels (SAF) & Alcohol-to-Jet",
        "category_id": "bioenergy_waste",
        "category_name": "Bioenergy, Sustainable Fuels & Waste-to-Energy",
        "headline": "100% drop-in synthetic jet fuel produced from waste oils, agricultural residues, and captured CO2 + green hydrogen.",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["SAF", "sustainable aviation fuel", "HEFA", "alcohol to jet", "ATJ", "e-kerosene", "aviation decarb", "LanzaJet"],
        "sector": "Clean Transportation Fuels",
        "fuel_vector": "Synthetic Hydrocarbon Fuel",
        "vector_type": "fuel_carrier",
        "fuel_profile": {
            "carrier_name": "Sustainable Aviation Fuel (SAF / Synthetic Kerosene)",
            "chemical_formula": "CnH2n+2 (Drop-in Paraffinic Kerosene Blend)",
            "carbon_intensity_ci": "15 - 28 g CO2e/MJ (65-85% GHG reduction vs fossil Jet A-1 at 89 g/MJ)",
            "energy_density_gravimetric": "43.2 - 43.8 MJ/kg",
            "energy_density_volumetric": "34.5 - 35.2 MJ/L (Liquid Kerosene)",
            "feedstock_pathway": "Used cooking oils (HEFA), forestry slash, agricultural residues (ATJ), captured CO2 + green H2 (PtL)",
            "drop_in_compatibility": "ASTM D7566 certified up to 50% blend; 100% unblended drop-in demonstration flights authorized",
            "policy_incentives": "IRA §40B / §45Z Clean Fuel Production Credit ($1.25-$1.75/gal), NY State SAF Procurement & LCFS"
        },
        "plain_english": {
            "what_is_it": "Drop-in liquid jet fuel made from used cooking oils, agricultural waste, non-food biomass, or captured carbon dioxide that can be poured directly into existing commercial Boeing and Airbus airplanes without modifying the engines or fueling systems.",
            "how_it_works": "Hydroprocessed Esters and Fatty Acids (HEFA) refines waste fats into jet hydrocarbons. Alcohol-to-Jet (ATJ) ferments industrial plant starches or agricultural wastes into ethanol and converts the alcohol into long-chain jet kerosene. Power-to-Liquid (PtL) combines green hydrogen and captured CO2 into synthetic kerosene.",
            "why_it_matters": "Commercial passenger airliners cannot fly across oceans on heavy batteries or bulky hydrogen tanks. SAF reduces aviation lifecycle greenhouse gas emissions by up to 80% while working seamlessly in all existing airport fueling infrastructure.",
            "macro_problem_solved": "Hard-to-abate long-haul commercial aviation and defense flight emissions."
        },
        "evolution": {
            "past": "First test flights using 50% biofuel blends (2008-2015).",
            "present": "Commercial production scaling across North America (World Energy, LanzaJet Freedom Pines, Neste, Montana Renewables).",
            "future": "Supplying 100% of commercial jet fuel demand (35 billion gallons/yr in US) via waste biomass and Power-to-Liquid by 2050."
        },
        "frontier": {
            "moonshot_goal": "Produce 3 billion gallons of domestic SAF per year by 2030 with >50% emissions reduction, scaling to 35 billion gallons by 2050 (DOE SAF Grand Challenge).",
            "kpis": [
                {"name": "US Annual SAF Production", "current": "150M - 300M Gallons / yr", "target_2030": "> 3.0 Billion Gallons / yr", "status": "on_track"},
                {"name": "Lifecycle GHG Reduction", "current": "65% - 80% vs Jet A", "target_2030": "> 85% - 100% (Carbon negative)", "status": "on_track"},
                {"name": "Production Cost Premium", "current": "2.0x - 3.5x fossil jet", "target_2030": "< 1.25x fossil jet parity", "status": "challenging"},
                {"name": "Certified Fuel Blend Ratio", "current": "50% Blend Limit", "target_2030": "100% Unblended Drop-in", "status": "on_track"}
            ],
            "bottlenecks": [
                "Scarcity and regional competition for HEFA waste fats, oils, and greases (FOG) feedstock.",
                "High capital cost for commercial-scale Alcohol-to-Jet and Fischer-Tropsch gasification refineries.",
                "Aromatic hydrocarbon requirements in legacy engine O-ring elastomer seals preventing 100% unblended synthetic use."
            ],
            "active_research_tracks": [
                "Synthetic aromatic chemistry synthesis from lignin enabling 100% unblended drop-in aviation certification (DOE BETO).",
                "Electro-catalytic Power-to-Liquid converting CO2 directly to kerosene with low energy penalty.",
                "Winter cover crops (Carinata, Camelina, Pennycress) providing non-food agricultural oil feedstocks."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 70,
            "capex_competitiveness": 72,
            "duration_scalability": 95,
            "technology_maturity": 85,
            "domestic_supply_chain": 88,
            "siting_permitting_ease": 88
        },
        "trade_offs": {
            "strengths": ["100% compatible with existing commercial airplanes and global airport fuel pipelines", "High gravimetric energy density necessary for intercontinental trans-ocean flight", "Cuts particulate contrail formation by 50-70%, reducing high-altitude radiative forcing"],
            "weaknesses": ["Currently costs 2x to 3x more than cheap fossil Jet-A fuel", "Biomass feedstock availability is constrained and must avoid food crop competition", "Requires significant capital investment in regional biorefineries"],
            "competing_technologies": ["Hydrogen Combustion Aircraft", "Battery-Electric Short-Haul Commuter Planes", "Hybrid Turboprops"]
        }
    },
    "anaerobic_digestion_biomethane": {
        "id": "anaerobic_digestion_biomethane",
        "name": "Renewable Natural Gas (RNG) & Anaerobic Digestion",
        "category_id": "bioenergy_waste",
        "category_name": "Bioenergy, Sustainable Fuels & Waste-to-Energy",
        "headline": "Capturing methane from dairy manure, wastewater, and food waste to produce carbon-negative pipeline-quality gas.",
        "trl_current": 9,
        "trl_target": 9,
        "keywords": ["RNG", "renewable natural gas", "anaerobic digestion", "biomethane", "dairy manure", "wastewater", "carbon negative"],
        "sector": "Waste-to-Energy & Biofuels",
        "fuel_vector": "Biomethane (CH4)",
        "vector_type": "fuel_carrier",
        "fuel_profile": {
            "carrier_name": "Renewable Natural Gas (RNG / Biomethane)",
            "chemical_formula": "CH4 (>97% purity post-upgrading)",
            "carbon_intensity_ci": "-150 to -300 g CO2e/MJ (Dairy Manure) / 20 to 45 g CO2e/MJ (Landfill/Wastewater)",
            "energy_density_gravimetric": "50.0 - 55.5 MJ/kg",
            "energy_density_volumetric": "36.4 MJ/m³ (Gas at NTP) / 21.0 MJ/L (LNG)",
            "feedstock_pathway": "Dairy manure, municipal organic solid waste, wastewater treatment sludge, food waste",
            "drop_in_compatibility": "100% Pipeline-grade drop-in replacement for fossil methane; injected directly into gas grids",
            "policy_incentives": "EPA RFS D3 RINs, NYSERDA PON 5236, California LCFS, Section 48 Investment Tax Credit"
        },
        "plain_english": {
            "what_is_it": "Airtight industrial tanks (digesters) that break down dairy cow manure, food scraps, and sewage using natural bacteria to capture methane gas before it escapes into the atmosphere, refining it into clean Renewable Natural Gas (RNG).",
            "how_it_works": "Bacteria digest organic wastes in oxygen-free heated tanks, producing raw biogas (60% methane, 40% CO2). Gas upgrading systems scrub out the CO2, water, and sulfur to produce 99% pure biomethane that is injected directly into utility natural gas pipelines or used to fuel heavy transit buses.",
            "why_it_matters": "Methane is 28 times more potent than CO2 as a greenhouse gas. By capturing fugitive dairy farm and landfill methane and displacing fossil gas, RNG achieves a deeply negative carbon intensity score (-150 to -300 gCO2e/MJ).",
            "macro_problem_solved": "Agricultural and municipal methane emissions and decarbonizing the existing gas grid."
        },
        "evolution": {
            "past": "Flaring agricultural biogas into the open air or running inefficient local combined heat and power engines (1980-2015).",
            "present": "Commercial multi-farm cluster projects with pipeline injection (California LCFS, NYSERDA, Vanguard Renewables).",
            "future": "Universal food waste digesters co-located with bio-CO2 sequestration for negative-emission power by 2030."
        },
        "frontier": {
            "moonshot_goal": "Capture 80%+ of municipal food waste and dairy methane across the US, supplying 2+ TCF of carbon-negative RNG annually.",
            "kpis": [
                {"name": "Carbon Intensity (Dairy Feedstock)", "current": "-150 to -250 gCO2e / MJ", "target_2030": "< -300 gCO2e / MJ", "status": "achieved"},
                {"name": "Methane Recovery Efficiency", "current": "88% - 94%", "target_2030": "> 98.5%", "status": "on_track"},
                {"name": "Gas Upgrading Capital Cost", "current": "$2.5M - $5.0M / facility", "target_2030": "< $1.5M (Modular)", "status": "on_track"},
                {"name": "Pipeline Interconnection Timeline", "current": "12 - 24 Months", "target_2030": "< 6 Months", "status": "challenging"}
            ],
            "bottlenecks": [
                "Utility gas pipeline interconnect testing and strict heating value / siloxane contamination standards.",
                "Volatile environmental credit market pricing (California LCFS and EPA RFS RINs).",
                "High upfront capital cost for manure collection, scrape systems, and anaerobic digester tanks."
            ],
            "active_research_tracks": [
                "Biological methanation converting digester byproduct CO2 into additional methane using green hydrogen.",
                "Membrane biogas upgrading systems with >99.5% methane recovery and zero methane slip.",
                "Nutrient recovery systems extracting dry fertilizer and phosphorus from digester liquid digestate."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 88,
            "capex_competitiveness": 82,
            "duration_scalability": 90,
            "technology_maturity": 92,
            "domestic_supply_chain": 95,
            "siting_permitting_ease": 80
        },
        "trade_offs": {
            "strengths": ["Deeply carbon-negative fuel lifecycle score under clean fuel standards", "100% drop-in substitute for fossil natural gas in pipelines and heavy transport", "Provides supplemental income and nutrient management for agricultural dairy farms"],
            "weaknesses": ["Total nationwide resource potential is finite (covers 10-15% of national gas demand)", "Utility pipeline interconnection approvals can be lengthy and expensive", "Methane slip in poorly operated digesters can negate climate benefits"],
            "competing_technologies": ["Direct Pipeline Electrification", "Green Hydrogen Blending", "Synthetic E-Methane"]
        }
    },

    "clean_ammonia_marine_fertilizer": {
        "id": "clean_ammonia_marine_fertilizer",
        "name": "Green Ammonia (NH3) & Zero-Carbon Marine Fuels",
        "category_id": "clean_hydrogen",
        "category_name": "Clean Hydrogen & Synthetic Molecules",
        "headline": "Haber-Bosch chemical synthesis powered by green hydrogen for maritime shipping, long-duration fuel cells, and fertilizer decarbonization.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["ammonia", "green ammonia", "NH3", "marine fuel", "bunkering", "Haber Bosch", "maritime decarb", "fertilizer"],
        "sector": "Clean Fuel Synthesis & Maritime Carriers",
        "fuel_vector": "Clean Ammonia (NH3)",
        "vector_type": "fuel_carrier",
        "fuel_profile": {
            "carrier_name": "Green Ammonia (NH3)",
            "chemical_formula": "NH3 (Anhydrous Liquid Ammonia)",
            "carbon_intensity_ci": "0 - 15 g CO2e/MJ (90-100% reduction vs heavy marine bunker fuel)",
            "energy_density_gravimetric": "18.6 - 22.5 MJ/kg (LHV)",
            "energy_density_volumetric": "11.5 - 13.8 MJ/L (Liquid at -33°C or 8.5 bar)",
            "feedstock_pathway": "Green hydrogen from water electrolysis + atmospheric nitrogen (N2) via air separation unit (ASU)",
            "drop_in_compatibility": "Utilizes existing global refrigerated chemical tanker fleet and 120+ deepwater ports; maritime 2-stroke dual-fuel engines commercializing by 2026-2027 (MAN ES, WinGD)",
            "policy_incentives": "IMO 2030/2050 Net-Zero GHG Strategy, IRA §45V ($3.00/kg H2), EU FuelEU Maritime and ETS compliance"
        },
        "plain_english": {
            "what_is_it": "A zero-carbon liquid chemical fuel made by combining clean hydrogen with nitrogen captured directly from ambient air, creating an energy-dense molecule that can power massive trans-oceanic container ships without producing any carbon dioxide.",
            "how_it_works": "Water electrolyzers generate clean hydrogen, which is fed alongside air-separated nitrogen into an electrified Haber-Bosch reactor. The resulting ammonia liquifies under modest pressure (8.5 bar) or chilling (-33C), making it vastly easier to transport and store than cryogenic liquid hydrogen (-253C).",
            "why_it_matters": "Global shipping carries 80% of world trade and burns 300 million tons of heavy fossil fuel oil annually. Green ammonia provides the necessary range and density for 30-day ocean crossings while eliminating 100% of carbon emissions.",
            "macro_problem_solved": "Decarbonizing deep-sea maritime transport, agricultural fertilizer production, and global bulk energy export."
        },
        "evolution": {
            "past": "Fossil gas-fed Haber-Bosch ammonia plants responsible for 1.8% of all global industrial CO2 emissions (1913-2020).",
            "present": "Multi-megawatt green ammonia pilot plants and first commercial ammonia-ready dual-fuel cargo ships (Yara Eyde, NYK Line, Fortescue).",
            "future": "Gigawatt-scale coastal export hubs supplying >100 million tons of maritime bunkering fuel and seasonal power by 2030-2035."
        },
        "frontier": {
            "moonshot_goal": "Achieve green ammonia production costs below $400/metric ton (<$0.020/kWh equivalent) with zero NOx slip in maritime combustion engines.",
            "kpis": [
                {"name": "Levelized Production Cost", "current": "$700 - $950 / ton NH3", "target_2030": "< $420 / ton NH3", "status": "challenging"},
                {"name": "Synthesis Loop Operating Pressure", "current": "150 - 250 bar", "target_2030": "< 50 bar (Low-P catalysts)", "status": "on_track"},
                {"name": "Direct Electrochemical Efficiency", "current": "20% - 35% (Lab Faradaic)", "target_2030": "> 65% Faradaic Efficiency", "status": "challenging"},
                {"name": "Combustion Engine NOx Slip", "current": "Selective Catalytic Reduction (SCR)", "target_2030": "< 0.05 g/kWh with advanced SCR", "status": "on_track"}
            ],
            "bottlenecks": [
                "Toxicity and strict safety handling protocols required for port bunkering and marine crew operations.",
                "NOx and unburned ammonia slip during combustion requiring robust high-efficiency SCR catalyst aftertreatment.",
                "High capital intensity of combined renewable generation, electrolysis, and chemical synthesis loops."
            ],
            "active_research_tracks": [
                "Direct electrochemical nitrogen reduction (eNRR) producing ammonia at ambient pressure without Haber-Bosch loops (DOE ARPA-E REFUEL).",
                "Ruthenium and cobalt-molybdenum low-temperature/low-pressure synthesis catalysts.",
                "Direct ammonia solid oxide fuel cells (SOFC) generating clean electricity with zero combustion emissions."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 65,
            "capex_competitiveness": 75,
            "duration_scalability": 98,
            "technology_maturity": 80,
            "domestic_supply_chain": 86,
            "siting_permitting_ease": 74
        },
        "trade_offs": {
            "strengths": ["Liquid at modest cooling (-33C) or pressure (8.5 bar), vastly simpler than cryogenic liquid H2", "Existing worldwide handling and pipeline infrastructure (180M tons traded annually)", "True zero-carbon combustion molecule for long-haul maritime vessels"],
            "weaknesses": ["Acute toxicity to humans and aquatic ecosystems requiring fail-safe double-walled piping", "Lower flame speed requires pilot fuel or turbo-charging in internal combustion engines", "Synthesis energy losses result in lower round-trip efficiency than direct electrification"],
            "competing_technologies": ["E-Methanol", "Liquefied Bio-LNG / Methane", "Cryogenic Liquid Hydrogen", "Nuclear Marine Propulsion"]
        }
    },
    "e_methanol_synthetic_fuels": {
        "id": "e_methanol_synthetic_fuels",
        "name": "E-Methanol & Power-to-Liquid Synthetic Molecules",
        "category_id": "clean_hydrogen",
        "category_name": "Clean Hydrogen & Synthetic Molecules",
        "headline": "Catalytic hydrogenation of captured biogenic CO2 with green hydrogen to synthesize drop-in liquid molecules for shipping and chemical manufacturing.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["e-methanol", "synthetic fuel", "power to liquid", "PtX", "CO2 utilization", "Maersk", "methanol bunkering", "green chemicals"],
        "sector": "Clean Fuel Synthesis & Liquid Carriers",
        "fuel_vector": "E-Methanol (CH3OH)",
        "vector_type": "fuel_carrier",
        "fuel_profile": {
            "carrier_name": "E-Methanol & Power-to-X Liquid",
            "chemical_formula": "CH3OH (Liquid Synthetic Alcohol)",
            "carbon_intensity_ci": "5 - 20 g CO2e/MJ (80-95% reduction vs fossil marine bunker fuel)",
            "energy_density_gravimetric": "19.9 - 22.7 MJ/kg",
            "energy_density_volumetric": "15.8 - 18.0 MJ/L (Ambient Liquid)",
            "feedstock_pathway": "Point-source biogenic CO2 (from bioenergy, pulp, or fermentation) + green hydrogen via copper/zinc catalytic hydrogenation reactors",
            "drop_in_compatibility": "Liquid at ambient temperature and standard atmospheric pressure; over 200 dual-fuel container vessels on order globally with commercial bunkering active in Europe, Asia, and US ports",
            "policy_incentives": "IMO 2030/2050 Net-Zero Strategy, FuelEU Maritime mandates, IRA §45Z Clean Fuel Production Credit, NY State Alternative Fuels Initiatives"
        },
        "plain_english": {
            "what_is_it": "A clean liquid alcohol fuel created by capturing carbon dioxide from industrial smokestacks or biogenic fermenters and chemically fusing it with green hydrogen, creating an ambient liquid fuel that replaces petroleum.",
            "how_it_works": "Pure biogenic CO2 and green H2 are compressed and passed over heated copper-zinc catalysts at 250C (480F). The chemical reaction produces water and liquid methanol, which stays liquid at room temperature and pressure like ordinary gasoline.",
            "why_it_matters": "Methanol requires no cryogenic refrigeration or high-pressure tanks, meaning existing ocean ships, fuel trucks, and gas stations can store it with simple tank coatings. Global shipping leaders (Maersk, CMA CGM) have ordered hundreds of methanol-fueled container ships.",
            "macro_problem_solved": "Providing a safe, room-temperature zero-carbon liquid fuel for container shipping and chemical feedstock."
        },
        "evolution": {
            "past": "Methanol synthesized from fossil coal and natural gas syngas (gray methanol, 1920-2020).",
            "present": "First commercial e-methanol plants operating and fueling transatlantic container ships (Kassø Denmark, European Energy, HIF Global).",
            "future": "Millions of tons of domestic e-methanol produced annually across US coastal and river corridors by 2030-2035."
        },
        "frontier": {
            "moonshot_goal": "Produce e-methanol at under $550/metric ton with >90% lifecycle GHG reduction utilizing 100% biogenic CO2 sources.",
            "kpis": [
                {"name": "Levelized Production Cost", "current": "$850 - $1,200 / ton", "target_2030": "< $550 / ton", "status": "challenging"},
                {"name": "CO2 Conversion Single-Pass Yield", "current": "35% - 48%", "target_2030": "> 70% Single-Pass", "status": "on_track"},
                {"name": "Catalyst Lifetime Under Dynamic Cycling", "current": "2 - 3 Years", "target_2030": "> 5 Years", "status": "on_track"},
                {"name": "Electrolyzer Power Consumption", "current": "10.0 kWh / kg CH3OH", "target_2030": "< 7.5 kWh / kg CH3OH", "status": "on_track"}
            ],
            "bottlenecks": [
                "Securing concentrated biogenic CO2 point-sources (ethanol plants, paper mills) near cheap renewable power.",
                "Water byproduct formation in direct CO2-to-methanol reactors accelerating copper catalyst deactivation.",
                "Price premium compared to untaxed fossil heavy fuel oil in maritime bunkering."
            ],
            "active_research_tracks": [
                "Indium oxide and noble-metal promoted catalysts with high selectivity avoiding reverse water-gas shift (RWGS) byproduct losses.",
                "Direct electrochemical reduction of CO2 directly to liquid methanol in aqueous flow cells (DOE BETO).",
                "Integration of direct air capture (DAC) thermal desorption with methanol synthesis waste heat."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 72,
            "capex_competitiveness": 78,
            "duration_scalability": 95,
            "technology_maturity": 82,
            "domestic_supply_chain": 88,
            "siting_permitting_ease": 85
        },
        "trade_offs": {
            "strengths": ["Liquid at ambient room temperature and atmospheric pressure", "Vastly easier to store, handle, and bunker than liquid hydrogen or ammonia", "Rapid commercial adoption by global container shipping lines with hundreds of ships on order"],
            "weaknesses": ["Requires continuous supply of biogenic CO2 to achieve net-zero carbon accounting", "Volumetric energy density is approximately half that of fossil diesel (requires 2x fuel tank volume)", "Higher cost than fossil fuel without carbon pricing or clean fuel subsidies"],
            "competing_technologies": ["Green Ammonia", "Sustainable Aviation Fuels (SAF)", "Bio-LNG", "Direct Battery Electric"]
        }
    },
    "pyrolysis_biochar_biofuels": {
        "id": "pyrolysis_biochar_biofuels",
        "name": "Fast Pyrolysis, Bio-Oil & Carbon-Negative Biochar",
        "category_id": "bioenergy_waste",
        "category_name": "Bioenergy, Sustainable Fuels & Waste-to-Energy",
        "headline": "Thermochemical deconstruction of agricultural biomass and forestry residues into drop-in renewable crude and 1,000-year permanent soil biochar.",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["pyrolysis", "bio-oil", "biochar", "carbon removal", "CDR", "biomass", "forestry residue", "carbon negative"],
        "sector": "Waste-to-Energy & Carbon Removal",
        "fuel_vector": "Pyrolysis Bio-Oil & Biochar",
        "vector_type": "fuel_carrier",
        "fuel_profile": {
            "carrier_name": "Pyrolysis Bio-Oil & Solid Biocarbon",
            "chemical_formula": "Oxygenated hydrocarbon bio-oil + >80% fixed elemental carbon biochar",
            "carbon_intensity_ci": "-80 to -180 g CO2e/MJ (Net carbon-negative lifecycle score when biochar is applied to soils)",
            "energy_density_gravimetric": "16.0 - 19.0 MJ/kg (Liquid Bio-Oil) / 28.0 - 32.0 MJ/kg (Solid Biochar)",
            "energy_density_volumetric": "19.0 - 22.5 MJ/L (Liquid Bio-Oil)",
            "feedstock_pathway": "Forestry slash, sawmill sawdust, agricultural corn stover, almond shells, and invasive woody biomass",
            "drop_in_compatibility": "Bio-oil is hydrotreated and co-processed in conventional petroleum refineries into gasoline/diesel/SAF; biochar is blended into agricultural topsoils or concrete matrices",
            "policy_incentives": "Carbon Dioxide Removal (CDR) verified credits ($150-$250/ton via Puro.earth), USDA BCAP, NYSERDA PON solicitations, EPA RFS D4/D5 RINs"
        },
        "plain_english": {
            "what_is_it": "Super-heating wood scraps, forestry waste, and crop stalks in a sealed chamber with no oxygen, flash-converting the wood into two valuable products: a dark liquid bio-fuel that can be refined into gasoline and jet fuel, and a rich black charcoal (biochar) that locks carbon in farm soil for a thousand years.",
            "how_it_works": "Biomass particles are heated to 500C (930F) for just two seconds in a fluidized bed reactor. The vapors rapidly condense into liquid bio-oil, while the solid residue forms high-surface-area biochar that retains plant nutrients and water in farm topsoil.",
            "why_it_matters": "When dead wood rots in forests or burns in wildfires, it releases all its carbon back into the air. Pyrolysis captures that carbon permanently, making the resulting fuels net carbon-negative while helping farmers improve soil fertility.",
            "macro_problem_solved": "Forestry wildfire fuel reduction, agricultural waste disposal, and permanent durable carbon dioxide removal."
        },
        "evolution": {
            "past": "Traditional charcoal kilns emitting unburned smoke and methane (ancient-1980s).",
            "present": "Commercial fast pyrolysis plants producing refinery-ready bio-oil and certified carbon removal credits (Charm Industrial, Biochar Supreme, Ensyn, Carbo Culture).",
            "future": "Distributed modular pyrolysis skids processing regional forest thinning across millions of acres by 2030."
        },
        "frontier": {
            "moonshot_goal": "Deploy 10,000 regional pyrolysis modules sequestering >50 million metric tons of CO2 annually while producing 2 billion gallons of biocrude.",
            "kpis": [
                {"name": "Carbon Removal Permanence (Biochar)", "current": "500 - 1,000+ Years", "target_2030": "> 1,000 Years (H:Corg < 0.4)", "status": "achieved"},
                {"name": "Biocrude Hydrotreating Yield", "current": "55% - 68% Mass Yield", "target_2030": "> 80% Mass Yield", "status": "on_track"},
                {"name": "Bio-Oil Oxygen Content", "current": "35% - 40% (Acidic)", "target_2030": "< 15% (Catalytic Pyrolysis)", "status": "on_track"},
                {"name": "Levelized CDR Cost", "current": "$180 - $280 / ton CO2", "target_2030": "< $90 / ton CO2", "status": "on_track"}
            ],
            "bottlenecks": [
                "Raw bio-oil is corrosive and chemically unstable due to high organic acid and water content.",
                "Biomass feedstock collection, drying, and grinding logistics add transport costs.",
                "Refinery co-processing catalyst fouling if bio-oil contains alkali metals (potassium, sodium)."
            ],
            "active_research_tracks": [
                "In-situ catalytic fast pyrolysis using zeolites (ZSM-5) to de-oxygenate bio-oil vapors before condensation (DOE BETO).",
                "Deep-well underground bio-oil geologic sequestration for ultra-permanent carbon removal.",
                "Engineered biochar additions in asphalt and structural concrete replacing cement clinker."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 82,
            "capex_competitiveness": 85,
            "duration_scalability": 94,
            "technology_maturity": 85,
            "domestic_supply_chain": 96,
            "siting_permitting_ease": 88
        },
        "trade_offs": {
            "strengths": ["Simultaneously generates drop-in liquid fuel precursors and permanent soil carbon removal (CDR)", "Utilizes low-cost forestry waste and agricultural residues with zero food crop competition", "Improves drought resistance and water retention in agricultural soils"],
            "weaknesses": ["Raw bio-oil requires hydrogen upgrading to remove oxygen before standard refinery blending", "Biomass transport economics typically limit collection radius to 50-75 miles", "Requires strict quality control to prevent heavy metal contamination in agricultural biochar"],
            "competing_technologies": ["Biomass Gasification", "Direct Air Capture (DAC)", "Hydrothermal Liquefaction (HTL)"]
        }
    },
    # -------------------------------------------------------------------------
    # 9. ADVANCED NUCLEAR & FUSION ENERGY
    # -------------------------------------------------------------------------
    "smr_advanced_nuclear": {
        "id": "smr_advanced_nuclear",
        "name": "Small Modular Reactors (SMRs) & High-Temperature Gas",
        "category_id": "advanced_nuclear",
        "category_name": "Advanced Nuclear & Fusion Energy",
        "headline": "Factory-built 50MW–300MW fission reactors with walk-away passive safety and high-temperature industrial steam output.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["SMR", "small modular reactor", "nuclear", "TRISO", "passive safety", "X-energy", "NuScale", "Kairos Power"],
        "sector": "Clean Baseload Generation",
        "fuel_vector": "Nuclear Fission",
        "vector_type": "hardware",
        "fuel_profile": {
            "carrier_name": "High-Assay Low-Enriched Uranium (HALEU) & TRISO",
            "chemical_formula": "UO2 / UCO encapsulated in PyC/SiC ceramic layers",
            "carbon_intensity_ci": "5 - 12 g CO2e/kWh lifecycle equivalent",
            "energy_density_gravimetric": "3,900,000 MJ/kg U-235 (Enormous energy density)",
            "feedstock_pathway": "5% - 20% enriched U-235 in silicon carbide coated ceramic matrix",
            "drop_in_compatibility": "Reactor-specific modular core loading; walk-away safe meltdown immunity",
            "policy_incentives": "DOE ARDP, IRA §45U Nuclear Power Production Credit, BIL Advanced Nuclear Funding"
        },
        "plain_english": {
            "what_is_it": "Compact, factory-manufactured nuclear power units that produce 50 to 300 megawatts of clean electricity (enough for 200,000 homes) that can be mass-produced on an assembly line and shipped by rail or truck to site.",
            "how_it_works": "Unlike massive custom-built 1,000MW reactors that require complex active cooling pumps, SMRs use physics-based 'passive safety' (natural convection of water, helium, or liquid metal). If power is completely lost, the reactor cools itself down automatically without human intervention or emergency generators.",
            "why_it_matters": "High-temperature gas-cooled and molten-salt SMRs produce extreme heat (500C to 800C), allowing them to power chemical plants, data centers, and clean hydrogen factories while replacing retired coal boilers on existing grid connections.",
            "macro_problem_solved": "Firm, land-efficient 24/7 zero-carbon power and decarbonizing high-temperature industrial heat."
        },
        "evolution": {
            "past": "Gigawatt-scale custom Light Water Reactors (LWRs) plagued by multi-billion dollar construction cost overruns (1970-2015).",
            "present": "NRC standard design approvals and commercial demonstration builds (NuScale, TerraPower Natrium, X-energy Xe-100, GE Hitachi BWRX-300).",
            "future": "Standardized serial factory manufacturing delivering operational units in <36 months at <$60/MWh by 2030-2035."
        },
        "frontier": {
            "moonshot_goal": "Achieve factory-built SMR overnight capital costs below $3,500/kW with licensed walk-away safety and 60-year operational design life.",
            "kpis": [
                {"name": "Overnight Capital Cost", "current": "$6,000 - $8,500 / kW (First-of-a-kind)", "target_2030": "< $3,500 / kW (Nth-of-a-kind)", "status": "challenging"},
                {"name": "On-site Construction Duration", "current": "5 - 8 Years", "target_2030": "< 3 Years", "status": "on_track"},
                {"name": "Coolant Outlet Temperature", "current": "300C (Light water) / 550C (Sodium)", "target_2030": "> 750C (HTGR)", "status": "on_track"},
                {"name": "Fuel Cycle Uranium Utilization", "current": "< 1% (Once-through LWR)", "target_2030": "> 30% - 90% (Fast spectrum)", "status": "on_track"}
            ],
            "bottlenecks": [
                "Domestic High-Assay Low-Enriched Uranium (HALEU, 5-20% U-235) commercial enrichment supply chain shortages.",
                "First-of-a-kind (FOAK) licensing review timelines and high NRC fee structures for non-light-water designs.",
                "Long-term consolidated spent fuel repository policy and public acceptance."
            ],
            "active_research_tracks": [
                "TRISO (Tristructural-Isotropic) robust meltdown-proof fuel particles capable of withstanding >1,600C (DOE ARDP).",
                "Advanced manufacturing techniques (electron-beam welding, powder metallurgy hot isostatic pressing) cutting vessel build time by 80%.",
                "Co-located data center and clean hydrogen production integration."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 95,
            "capex_competitiveness": 68,
            "duration_scalability": 100,
            "technology_maturity": 75,
            "domestic_supply_chain": 72,
            "siting_permitting_ease": 65
        },
        "trade_offs": {
            "strengths": ["True 24/7 firm baseload power with 95%+ capacity factors", "High-temperature steam output (up to 750C) for industrial manufacturing and hydrogen", "Can directly repower retired coal plant sites using existing grid substations"],
            "weaknesses": ["High initial first-of-a-kind (FOAK) capital investment", "Requires domestic HALEU fuel enrichment infrastructure scaling", "Complex regulatory licensing and long-term spent fuel management"],
            "competing_technologies": ["Enhanced Geothermal Systems (EGS)", "Natural Gas + CCUS", "Fusion Energy"]
        }
    },
    "magnetic_inertial_fusion": {
        "id": "magnetic_inertial_fusion",
        "name": "Commercial Magnetic & Laser Fusion Systems",
        "category_id": "advanced_nuclear",
        "category_name": "Advanced Nuclear & Fusion Energy",
        "headline": "Recreating the power of the Sun on Earth using high-temperature superconducting magnets and laser ignition.",
        "trl_current": 4,
        "trl_target": 7,
        "keywords": ["fusion", "tokamak", "stellarator", "high temperature superconductor", "HTS magnet", "net energy", "Commonwealth Fusion", "Helion"],
        "sector": "Limitless Clean Power",
        "fuel_vector": "Nuclear Fusion (Deuterium/Tritium/He-3)",
        "vector_type": "hardware",
        "fuel_profile": {
            "carrier_name": "Deuterium-Tritium / Helium-3 Isotopic Fuel",
            "chemical_formula": "2H + 3H -> 4He + n + 17.6 MeV",
            "carbon_intensity_ci": "0 g CO2e direct emissions; zero long-lived transuranic nuclear waste",
            "energy_density_gravimetric": "340,000,000 MJ/kg (Highest physical energy density known)",
            "feedstock_pathway": "Deuterium from seawater distillation; Tritium bred in-situ from lithium blankets",
            "drop_in_compatibility": "Magnetic confinement tokamaks/stellarators and laser inertial confinement fusion",
            "policy_incentives": "DOE Milestone-Based Fusion Development Program, ARPA-E OPEN & BETHE"
        },
        "plain_english": {
            "what_is_it": "The holy grail of clean energy: fusing hydrogen atoms together at 180 million degrees Fahrenheit (100 million Celsius) inside magnetic bottles to generate massive amounts of clean heat without creating long-lived radioactive waste, meltdown risks, or carbon emissions.",
            "how_it_works": "High-Temperature Superconducting (HTS) magnets (Rare-Earth Barium Copper Oxide, REBCO) generate intense magnetic fields (20 Tesla) that squeeze superheated plasma inside a donut-shaped chamber (tokamak or stellarator), forcing hydrogen isotopes (Deuterium and Tritium) to fuse into helium, releasing enormous energy.",
            "why_it_matters": "Fusion fuel comes from seawater and lithium—abundant enough to power human civilization for millions of years. A single glass of water has the fusion fuel equivalent of 200 gallons of gasoline, with zero possibility of a meltdown.",
            "macro_problem_solved": "Infinite, safe, geographically universal clean baseload power with zero carbon or long-lived waste."
        },
        "evolution": {
            "past": "Government megaprojects building massive, slow copper tokamaks with net energy loss (1950-2020).",
            "present": "Net energy gain achieved at NIF (2022); commercial high-field HTS prototypes under construction (Commonwealth Fusion SPARC, Helion, TAE).",
            "future": "First commercial grid-connected fusion pilot plants delivering 200MW+ net electric power by 2032-2038."
        },
        "frontier": {
            "moonshot_goal": "Demonstrate a commercial fusion power plant generating net electricity (Q_electric > 5) onto the public grid by 2035.",
            "kpis": [
                {"name": "Plasma Energy Gain (Q)", "current": "Q = 1.5 (NIF Laser) / Q ~ 1.0 (Joint European Torus)", "target_2030": "Q > 10 (Net thermal gain)", "status": "on_track"},
                {"name": "HTS Magnetic Field Strength", "current": "20.1 Tesla (World Record)", "target_2030": "> 25.0 Tesla", "status": "achieved"},
                {"name": "Tritium Breeding Ratio (TBR)", "current": "Simulation (1.05 - 1.15)", "target_2030": "> 1.10 (Self-sustaining loop)", "status": "on_track"},
                {"name": "First-Wall Neutron Lifetime", "current": "1 - 2 Years (Design limit)", "target_2030": "> 5 Years (Advanced alloys)", "status": "challenging"}
            ],
            "bottlenecks": [
                "Severe 14.1 MeV fusion neutron bombardment damaging and activating the internal vacuum vessel first-wall materials.",
                "Tritium fuel scarcity requiring efficient in-situ lithium blanket breeding and extraction loops.",
                "Plasma turbulence, edge localized modes (ELMs), and sudden magnetic disruptions quenching the superconducting magnets."
            ],
            "active_research_tracks": [
                "Liquid metal (lithium/lead-lithium) first-wall divertor shields absorbing neutron damage (DOE INFUSE / ARPA-E).",
                "Advanced AI plasma control networks predicting and suppressing magnetohydrodynamic disruptions in microseconds.",
                "Aneutronic proton-boron (p-B11) and Deuterium-Helium3 direct energy conversion."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 95,
            "capex_competitiveness": 50,
            "duration_scalability": 100,
            "technology_maturity": 45,
            "domestic_supply_chain": 68,
            "siting_permitting_ease": 82
        },
        "trade_offs": {
            "strengths": ["Inexhaustible fuel supply from seawater and lithium (millions of years of fuel)", "Zero possibility of a nuclear meltdown (reaction stops instantly if interrupted)", "No long-lived high-level radioactive waste (materials decay safely in decades)"],
            "weaknesses": ["Very high technological and physics complexity (plasma confinement at 100M C)", "Extreme neutron damage requires novel first-wall metallurgy", "High early capital investment before commercial operational proof"],
            "competing_technologies": ["Fission SMRs", "Enhanced Geothermal Systems (EGS)", "Ultra-Deep Superhot Rock Geothermal"]
        }
    },

    # -------------------------------------------------------------------------
    # 10. INDUSTRIAL DECARBONIZATION & PROCESS HEAT
    # -------------------------------------------------------------------------
    "industrial_high_temp_heat_pumps": {
        "id": "industrial_high_temp_heat_pumps",
        "name": "Industrial High-Temperature Heat Pumps (HTHP, 120C–200C)",
        "category_id": "industrial_decarb",
        "category_name": "Industrial Decarbonization & Process Heat",
        "headline": "Electrifying manufacturing process steam and drying with 300%+ thermodynamic efficiency.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["HTHP", "industrial heat pump", "steam generation", "process heat", "waste heat recovery", "low GWP", "turbocompressor"],
        "sector": "Industrial Heat Decarbonization",
        "fuel_vector": "Electric Thermal Energy",
        "plain_english": {
            "what_is_it": "Heavy-duty electric industrial heat pumps that capture low-temperature waste heat from manufacturing plants (cooling water, exhaust air) and boost it to boiling steam temperatures (250F to 400F / 120C to 200C) for food processing, papermaking, and chemical production.",
            "how_it_works": "Uses high-pressure twin-screw or centrifugal turbocompressors with specialized ultra-low-GWP refrigerants (hydrofluoroolefins or natural water/steam). For every 1 kilowatt of electricity consumed, the system delivers 2.5 to 3.5 kilowatts of high-temperature heat by harvesting free industrial waste energy.",
            "why_it_matters": "Process steam accounts for over 50% of all fossil natural gas burned in factories. HTHPs cut industrial fossil fuel consumption by 70% while delivering huge energy bill savings.",
            "macro_problem_solved": "Fossil boiler emissions in food, paper, chemical, and textile manufacturing."
        },
        "evolution": {
            "past": "Low-temperature residential heat pumps capped at 60C (140F) and fossil gas boilers (1970-2018).",
            "present": "Commercial 120C-160C steam heat pump installations in food/beverage and district heating (Siemens, Heaten, AtmosZero).",
            "future": "Standardized 200C+ steam generation heat pumps replacing all light-to-medium industrial fossil boilers by 2030."
        },
        "frontier": {
            "moonshot_goal": "Deliver clean industrial process steam up to 200C with a Coefficient of Performance (COP) > 2.5 at capital parity with gas boilers.",
            "kpis": [
                {"name": "Maximum Output Temperature", "current": "130C - 165C", "target_2030": "> 200C (Superheated steam)", "status": "on_track"},
                {"name": "Coefficient of Performance (COP)", "current": "2.2 - 2.8", "target_2030": "> 3.2 - 3.8", "status": "on_track"},
                {"name": "Refrigerant Global Warming Potential", "current": "< 10 (HFO / Hydrocarbons)", "target_2030": "< 1 (Natural Water / CO2)", "status": "achieved"},
                {"name": "Installed Capital Cost", "current": "$450 - $700 / kW-th", "target_2030": "< $250 / kW-th", "status": "on_track"}
            ],
            "bottlenecks": [
                "Refrigerant thermal stability and lubricating oil breakdown at temperatures above 150C.",
                "Compressor volumetric efficiency drop and seal leakage under high pressure ratios.",
                "Cheap natural gas prices in North America challenging operating cost parity without carbon pricing."
            ],
            "active_research_tracks": [
                "Water (R-718 / steam) as the direct working fluid with supersonic compression rotors (DOE IEDO / ORNL).",
                "Acoustic and Stirling-cycle thermoacoustic heat pumps operating without chemical refrigerants.",
                "Phase change thermal storage integration smoothing fluctuating factory steam demand."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 95,
            "capex_competitiveness": 80,
            "duration_scalability": 90,
            "technology_maturity": 78,
            "domestic_supply_chain": 90,
            "siting_permitting_ease": 96
        },
        "trade_offs": {
            "strengths": ["Delivers 2.5x to 3.5x more thermal energy than the electricity consumed (COP 2.5-3.5)", "Directly recovers and recycles industrial waste heat that was previously vented into the air", "Eliminates on-site combustion air pollution (NOx, SOx, particulates) in manufacturing communities"],
            "weaknesses": ["Temperature range currently limited to <180C (cannot supply 1,000C+ heat for steel or cement kilns)", "Higher upfront equipment CapEx than a simple replacement fossil gas boiler", "Requires industrial facilities to have adequate high-voltage electrical service capacity"],
            "competing_technologies": ["Electric Resistance Boilers", "Thermal Brick Storage", "Hydrogen Combustion Boilers"]
        }
    },
    "green_steel_h2_dri": {
        "id": "green_steel_h2_dri",
        "name": "Green Steel: Hydrogen Direct Reduced Iron (H2-DRI) & Electric Arc",
        "category_id": "industrial_decarb",
        "category_name": "Industrial Decarbonization & Process Heat",
        "headline": "Eliminating coal coke blast furnaces to produce primary virgin steel with 95%+ lower carbon emissions.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["green steel", "H2-DRI", "direct reduced iron", "electric arc furnace", "EAF", "coke replacement", "SSAB HYBRIT", "Cleveland-Cliffs"],
        "sector": "Heavy Industrial Materials",
        "fuel_vector": "Green Hydrogen & Clean Power",
        "plain_english": {
            "what_is_it": "Making brand-new steel from iron ore using green hydrogen instead of burning coal coke in a blast furnace, emitting pure water vapor instead of carbon dioxide.",
            "how_it_works": "In a Direct Reduced Iron (DRI) vertical shaft tower, hydrogen gas reacts with iron ore pellets at 1,500F (800C) to strip away oxygen, leaving pure solid sponge iron. The sponge iron is then melted in an Electric Arc Furnace (EAF) powered by clean electricity to produce structural steel.",
            "why_it_matters": "Traditional steelmaking produces 7-8% of ALL global greenhouse gas emissions. H2-DRI eliminates 95% of these emissions while producing the exact same high-strength automotive and structural steel required for modern civilization.",
            "macro_problem_solved": "Heavy industrial emissions from coal-fueled primary steel manufacturing."
        },
        "evolution": {
            "past": "Coal-fired blast furnace and basic oxygen furnaces emitting ~1.8 tons of CO2 per ton of steel (1850-present).",
            "present": "Commercial demonstration plants producing fossil-free steel (HYBRIT Sweden, Stegra/H2 Green Steel, DOE OCED grants).",
            "future": "Universal conversion of primary steelmaking to green hydrogen DRI and direct iron electrolysis by 2035."
        },
        "frontier": {
            "moonshot_goal": "Produce commercial automotive-grade virgin steel at <$600/ton with <0.1 ton CO2 per ton steel produced.",
            "kpis": [
                {"name": "CO2 Emissions per Ton Steel", "current": "1.8 - 2.2 tons CO2 (Blast Furnace)", "target_2030": "< 0.08 tons CO2 (H2-DRI + EAF)", "status": "achieved"},
                {"name": "Hydrogen Consumption per Ton Iron", "current": "50 - 65 kg H2 / ton DRI", "target_2030": "< 45 kg H2 / ton DRI", "status": "on_track"},
                {"name": "Green Premium vs Conventional", "current": "+20% - +35% cost premium", "target_2030": "< +5% cost parity", "status": "challenging"},
                {"name": "DRI Shaft Hydrogen Blend", "current": "30% - 70% H2 (Mixed with gas)", "target_2030": "100% Pure Green Hydrogen", "status": "on_track"}
            ],
            "bottlenecks": [
                "Scarcity of low-cost clean hydrogen (<$2/kg) required for economic operating parity with cheap metallurgical coal.",
                "Shortage of high-grade (>67% Fe) direct-reduction iron ore pellets, requiring beneficiation upgrades.",
                "High capital expenditure ($1B-$2B) to replace depreciated legacy blast furnaces."
            ],
            "active_research_tracks": [
                "Direct low-temperature aqueous electrowinning of iron ore (Electra / Boston Metal molten oxide electrolysis).",
                "Submerged electric arc furnace slag chemistry optimizing melting of lower-grade iron ores.",
                "Hydrogen shaft gas recirculation and waste heat recuperation."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 85,
            "capex_competitiveness": 65,
            "duration_scalability": 95,
            "technology_maturity": 75,
            "domestic_supply_chain": 88,
            "siting_permitting_ease": 78
        },
        "trade_offs": {
            "strengths": ["Cuts carbon emissions of primary steelmaking by over 95%", "Produces high-purity virgin steel required for safety-critical automotive and defense uses", "Retains and upgrades existing high-paying union steel manufacturing jobs"],
            "weaknesses": ["Requires massive volumes of cheap green hydrogen (50 kg H2 per ton of steel)", "Requires high-grade iron ore pellets (>67% iron content)", "Multi-billion dollar capital expense to retire and rebuild integrated steel mills"],
            "competing_technologies": ["Recycled Steel Scrap Melting (EAF)", "Blast Furnace + Carbon Capture (CCUS)", "Molten Oxide Direct Iron Electrolysis"]
        }
    },

    # -------------------------------------------------------------------------
    # 11. BUILDINGS, THERMAL NETWORKS & HEAT PUMPS
    # -------------------------------------------------------------------------
    "thermal_energy_networks_tens": {
        "id": "thermal_energy_networks_tens",
        "name": "Utility Thermal Energy Networks (TENs) & Geothermal Loops",
        "category_id": "buildings_thermal",
        "category_name": "Buildings, Thermal Networks & Heat Pumps",
        "headline": "Neighborhood-scale shared ambient water loops sharing heating and cooling across multiple city buildings.",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["thermal energy networks", "TENs", "networked geothermal", "district heating", "ambient loop", "NYSERDA TENs", "Eversource"],
        "sector": "Building Electrification",
        "fuel_vector": "Shared Ambient Geothermal Water",
        "plain_english": {
            "what_is_it": "Underground street water pipes that connect entire neighborhoods, apartment buildings, schools, and businesses together to share heating and cooling. When an ice rink or supermarket rejects heat, that free heat is piped to warm nearby homes and schools.",
            "how_it_works": "Water circulates through an ambient temperature loop (50F to 70F) connected to deep geothermal borehole fields, subway exhaust vents, and wastewater sewers. Individual heat pumps inside each building pull heat from or push heat into this common street loop with extreme efficiency (COP > 4.5).",
            "why_it_matters": "Networked geothermal allows regulated gas utilities to transition their existing pipe-fitting workforce to build clean thermal pipes under city streets, heating entire urban communities without overloading the electric power grid.",
            "macro_problem_solved": "Urban building heating decarbonization without overwhelming local electric distribution grids."
        },
        "evolution": {
            "past": "High-temperature steam district heating systems burning coal or oil (1880-1990).",
            "present": "Utility-scale pilot TENs authorized by state legislation (NY Community Heat Pump Systems Act, MassCEC Framingham, Eversource).",
            "future": "Universal ambient geothermal loops standard across all cold-climate cities and public housing by 2030."
        },
        "frontier": {
            "moonshot_goal": "Deploy 1,000+ utility thermal energy networks across North America, cutting peak winter electric grid demand by 40% compared to standalone air-source units.",
            "kpis": [
                {"name": "System Heating Efficiency (COP)", "current": "3.8 - 4.5 (Ambient loop)", "target_2030": "> 5.5 (Multi-source loop)", "status": "on_track"},
                {"name": "Winter Peak Grid Load vs ASHP", "current": "35% Lower peak kW", "target_2030": "> 50% Lower peak kW", "status": "achieved"},
                {"name": "Utility Workforce Transition", "current": "Pilots (100s retrained)", "target_2030": "100% Retraining of gas pipefitters", "status": "on_track"},
                {"name": "Borehole Drilling Cost", "current": "$25 - $38 / linear foot", "target_2030": "< $12 / linear foot", "status": "on_track"}
            ],
            "bottlenecks": [
                "Crowded underground urban utility rights-of-way (competing with gas, sewer, water, fiber optic).",
                "High upfront borehole drilling and street excavation capital costs.",
                "Regulatory utility rate design and cross-customer thermal metering structures."
            ],
            "active_research_tracks": [
                "High-speed sonic resonance and coiled-tubing drilling rigs for tight urban borehole alleys (DOE BTO / NYSERDA).",
                "Thermal energy extraction from municipal wastewater sewer mains and data center liquid loops.",
                "Smart thermal balancing algorithms dynamically trading BTUs between diverse building load profiles."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 96,
            "capex_competitiveness": 75,
            "duration_scalability": 95,
            "technology_maturity": 85,
            "domestic_supply_chain": 95,
            "siting_permitting_ease": 78
        },
        "trade_offs": {
            "strengths": ["Highest thermodynamic efficiency of any heating system (COP 4.5 to 5.5+)", "Levels out winter peak electric grid spikes that would otherwise blow transformers", "Directly transitions gas utility pipefitter unions to clean energy careers"],
            "weaknesses": ["High upfront capital cost to dig street trenches and drill vertical boreholes", "Requires coordinating multi-building property owners and municipal street permits", "Difficult to retrofit in dense historic downtowns with congested underground infrastructure"],
            "competing_technologies": ["Standalone Air-Source Heat Pumps (ASHP)", "Variable Refrigerant Flow (VRF)", "Direct Geothermal Single-Home Loops"]
        }
    },
    "cold_climate_heat_pumps": {
        "id": "cold_climate_heat_pumps",
        "name": "Cold-Climate Air-Source Heat Pumps (ccASHP) & Low-GWP Refrigerants",
        "category_id": "buildings_thermal",
        "category_name": "Buildings, Thermal Networks & Heat Pumps",
        "headline": "Variable-speed vapor-injection heat pumps delivering 100% heating capacity down to -15F (-26C).",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["ccASHP", "cold climate heat pump", "vapor injection", "heat pump", "variable speed", "inverter compressor", "R-290", "R-454B"],
        "sector": "Building Electrification",
        "fuel_vector": "Electric Heating & Cooling",
        "plain_english": {
            "what_is_it": "Advanced electric heat pumps designed specifically for freezing northern winters that pull heat energy out of outdoor air even when temperatures drop to -15F (-26C), completely replacing fossil oil and gas heating without needing backup electric resistance coils.",
            "how_it_works": "Uses variable-speed inverter compressors and flash vapor injection. By injecting a small stream of intermediate-pressure refrigerant vapor into the compressor, the heat pump keeps the refrigerant flowing at high density without overheating the compressor, maintaining full heat output in sub-zero blizzard conditions.",
            "why_it_matters": "Historically, heat pumps struggled below freezing, requiring backup fossil heat. ccASHPs enable 100% clean electric heating across the northern US, cutting residential heating emissions by 60-80% while saving homeowners money on fuel oil and propane.",
            "macro_problem_solved": "Sub-zero building space heating decarbonization across cold northern climates."
        },
        "evolution": {
            "past": "Single-stage heat pumps that shut down below 32F (0C) and switched to inefficient electric heat strips (1980s-2015).",
            "present": "DOE Cold Climate Heat Pump Challenge certified units operating in Alaska, Maine, Minnesota, and New York.",
            "future": "Ultra-low GWP natural refrigerant (Propane R-290 / CO2) monobloc heat pumps reaching COP > 3.0 at 0F by 2028."
        },
        "frontier": {
            "moonshot_goal": "Deliver 100% rated heating capacity at -20F with COP > 2.2 using climate-friendly low-GWP refrigerants (GWP < 5).",
            "kpis": [
                {"name": "Capacity Retention at 5F (-15C)", "current": "85% - 100%", "target_2030": "> 100%", "status": "achieved"},
                {"name": "COP at 5F (-15C)", "current": "1.8 - 2.2", "target_2030": "> 2.6", "status": "on_track"},
                {"name": "Minimum Operating Temperature", "current": "-15F (-26C)", "target_2030": "-25F (-32C)", "status": "on_track"},
                {"name": "Refrigerant GWP", "current": "466 - 675 (R-454B/R-32)", "target_2030": "< 3 (Propane R-290/CO2)", "status": "on_track"}
            ],
            "bottlenecks": [
                "Frost accumulation on outdoor evaporator coils in high-humidity 25-35F weather requiring energy-consuming defrost cycles.",
                "High upfront equipment and installation electrical panel upgrade costs for older homes.",
                "Flammability safety standards (ASHRAE 15 / A2L/A3) limiting charge sizes of high-efficiency natural propane refrigerants indoors."
            ],
            "active_research_tracks": [
                "Superhydrophobic and ultrasonic frost-shedding coatings on outdoor evaporator fins (DOE BTO / ORNL).",
                "Sealed outdoor monobloc systems using Propane (R-290) that circulate only water indoors, bypassing refrigerant safety rules.",
                "Smart grid interactive load-shifting algorithms pre-heating homes ahead of morning winter peak hours."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 92,
            "capex_competitiveness": 85,
            "duration_scalability": 90,
            "technology_maturity": 88,
            "domestic_supply_chain": 90,
            "siting_permitting_ease": 94
        },
        "trade_offs": {
            "strengths": ["Eliminates fossil fuel pipes and heating oil tanks from homes", "Provides high-efficiency summer air conditioning from the same system", "Reaches 200-300% efficiency (COP 2.0-3.0) compared to 95% for top gas furnaces"],
            "weaknesses": ["Efficiency drops in extreme sub-zero weather compared to mild days", "May require 200A home electrical panel service upgrades", "Upfront installation cost is higher than a simple replacement gas furnace"],
            "competing_technologies": ["Networked Geothermal Thermal Energy Networks (TENs)", "Hybrid Dual-Fuel Heat Pump Systems", "Wood Pellet Biomass Boilers"]
        }
    },

    # -------------------------------------------------------------------------
    # 12. CLEAN TRANSPORTATION & HEAVY-DUTY MOBILITY
    # -------------------------------------------------------------------------
    "megawatt_charging_systems_mcs": {
        "id": "megawatt_charging_systems_mcs",
        "name": "Megawatt Charging Systems (MCS) & Fleet Electrification",
        "category_id": "clean_transportation",
        "category_name": "Clean Transportation & Heavy-Duty Mobility",
        "headline": "High-voltage 1.0MW–3.75MW DC ultra-fast charging architectures for Class 8 heavy freight and maritime vessels.",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["MCS", "megawatt charging", "fleet electrification", "Class 8", "heavy duty EV", "liquid cooled cable", "depot charging"],
        "sector": "Heavy Commercial Transport",
        "fuel_vector": "High-Power DC Electricity",
        "plain_english": {
            "what_is_it": "Heavy-duty electric truck chargers that deliver up to 3.75 megawatts of electrical power through a liquid-cooled cable, adding 300+ miles of driving range to a fully-loaded 80,000-pound semi-truck in under 30 minutes during a driver's required rest break.",
            "how_it_works": "Operates at up to 1,250 volts and 3,000 amps. To handle this immense current without overheating the cable, the charging connector and internal conductors circulate coolant fluid directly through the handle.",
            "why_it_matters": "Heavy freight trucks represent only 4% of vehicles on US roads, but generate over 25% of all transportation greenhouse gas emissions and the vast majority of urban diesel smog in port communities. MCS makes zero-emission long-haul trucking commercially viable.",
            "macro_problem_solved": "Heavy-duty diesel freight emissions and charging dwell time bottlenecks."
        },
        "evolution": {
            "past": "Passenger CCS/NACS chargers capped at 150-350 kW (2010-2022).",
            "present": "CharIN MCS standardization and pilot fleet depots operating along California freight corridors (I-5, I-10, NY Port).",
            "future": "Nationwide interstate freight corridor MCS charging plazas with on-site BESS and microgrids by 2028-2032."
        },
        "frontier": {
            "moonshot_goal": "Deploy 3+ MW automated pantograph and plug-in MCS chargers delivering >98% efficiency at <$0.12/kWh delivered depot cost.",
            "kpis": [
                {"name": "Maximum Charging Power", "current": "1.0 - 1.2 MW", "target_2030": "3.75 MW", "status": "on_track"},
                {"name": "Full Pack Charge Time (600 kWh)", "current": "45 - 60 Minutes", "target_2030": "< 20 Minutes", "status": "on_track"},
                {"name": "Connector Thermal Stability", "current": "Liquid-cooled 1,500A", "target_2030": "3,000A Continuous", "status": "on_track"},
                {"name": "Grid Interconnection Buffer", "current": "Direct utility tie", "target_2030": "Integrated BESS buffer", "status": "achieved"}
            ],
            "bottlenecks": [
                "Local utility distribution transformer constraints (a 20-truck depot requires 20-40 MW of power, equal to a small city).",
                "High utility peak demand charges without co-located behind-the-meter battery storage.",
                "Connector durability under harsh outdoor trucking terminal conditions."
            ],
            "active_research_tracks": [
                "Solid-state transformer (SST) medium-voltage direct grid interconnection (DOE VTO / NREL).",
                "Automated robotic connection arms for hands-free freight depot charging.",
                "Vehicle-to-Grid (V2G) multi-megawatt depot power injection supporting summer peak grid events."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 95,
            "capex_competitiveness": 78,
            "duration_scalability": 88,
            "technology_maturity": 82,
            "domestic_supply_chain": 88,
            "siting_permitting_ease": 70
        },
        "trade_offs": {
            "strengths": ["Enables mandatory 30-minute rest-break charging for long-haul Class 8 trucks", "Standardized worldwide under CharIN MCS protocol", "Cuts diesel particulate pollution in frontline port and corridor communities"],
            "weaknesses": ["Massive localized electric grid capacity requirements (10-50 MW per truck stop)", "Requires heavy liquid-cooled cables or automated connection robotics", "High equipment CapEx for high-voltage DC dispensers"],
            "competing_technologies": ["Hydrogen Fuel Cell Heavy Trucks", "Battery Swapping Depots", "Catenary Overhead Wire Charging"]
        }
    },

    # -------------------------------------------------------------------------
    # 13. CARBON MANAGEMENT, CCUS & DIRECT REMOVAL
    # -------------------------------------------------------------------------
    "direct_air_capture_dac": {
        "id": "direct_air_capture_dac",
        "name": "Direct Air Capture (DAC) & Permanent Geologic Storage",
        "category_id": "carbon_management",
        "category_name": "Carbon Capture, Utilization & Removal (CCUS/CDR)",
        "headline": "Engineered vacuum systems extracting ambient CO2 directly from atmosphere for permanent underground Class VI mineralization.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["DAC", "direct air capture", "CDR", "carbon removal", "geologic storage", "Climeworks", "1PointFive", "Class VI"],
        "sector": "Engineered Carbon Removal",
        "fuel_vector": "CO2 Removal",
        "plain_english": {
            "what_is_it": "Giant fan facilities that pull ambient air through chemical filters that scrub out carbon dioxide, compressing the captured CO2 into a dense liquid that is pumped miles underground into deep basalt or saline rocks where it turns into stone forever.",
            "how_it_works": "Solid-sorbent DAC uses amine-coated honeycomb filters that trap CO2 molecules and release pure CO2 when heated to 200F (100C). Liquid-solvent DAC uses potassium hydroxide air contactors with high-temperature calciners (1,600F / 900C) to release pure CO2 for permanent Class VI well injection.",
            "why_it_matters": "Even after reaching 100% clean energy, society must remove legacy historical CO2 emissions already in the atmosphere. DAC provides permanent, verifiable, 1,000+ year carbon removal with zero reliance on vulnerable forest acreage.",
            "macro_problem_solved": "Atmospheric legacy carbon concentration reduction and neutralizing hard-to-abate residual emissions."
        },
        "evolution": {
            "past": "Small lab prototypes and submarine/spacecraft CO2 scrubbers (1960-2015).",
            "present": "Commercial megaton hubs under construction in Texas and Louisiana (Occidental/1PointFive, Climeworks Mammoth, DOE DAC Hubs).",
            "future": "Gigaton-scale global DAC industry powered by dedicated geothermal/nuclear energy at <$100/ton by 2035."
        },
        "frontier": {
            "moonshot_goal": "Remove atmospheric CO2 and permanently store it at a verified net cost below $100 per metric ton (DOE Carbon Negative Shot).",
            "kpis": [
                {"name": "Net Cost per Ton CO2 Removed", "current": "$400 - $700 / ton CO2", "target_2030": "< $150 / ton CO2", "status": "challenging"},
                {"name": "Thermal Regeneration Energy", "current": "1,500 - 2,500 kWh / ton CO2", "target_2030": "< 900 kWh / ton CO2", "status": "on_track"},
                {"name": "Sorbent Lifetime / Cycles", "current": "2,000 - 5,000 Cycles", "target_2030": "> 15,000 Cycles", "status": "on_track"},
                {"name": "Storage Permanence Duration", "current": "> 1,000 Years (Class VI)", "target_2030": "> 10,000 Years (Mineralized)", "status": "achieved"}
            ],
            "bottlenecks": [
                "Ultra-low atmospheric CO2 concentration (420 ppm or ~0.04%), requiring enormous volumes of air moving through fans.",
                "High thermal energy consumption for sorbent regeneration competing with clean grid electrification.",
                "Class VI EPA underground injection well permitting backlogs and regional CO2 pipeline right-of-way disputes."
            ],
            "active_research_tracks": [
                "Metal-Organic Frameworks (MOFs) with ultra-high selective CO2 binding affinity at low regeneration temps (DOE FECM).",
                "Electrochemical pH-swing and moisture-swing regeneration eliminating thermal heat requirements.",
                "In-situ basalt mineralization (Carbfix / 44.01) turning CO2 into solid carbonate rock within 24 months."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 70,
            "capex_competitiveness": 55,
            "duration_scalability": 100,
            "technology_maturity": 70,
            "domestic_supply_chain": 85,
            "siting_permitting_ease": 68
        },
        "trade_offs": {
            "strengths": ["Provides true net-negative carbon removal with 1,000+ year permanence", "99% smaller land footprint than biological tree planting (afforestation)", "Location flexible: can be built directly on top of geological storage formations"],
            "weaknesses": ["High energy intensity (requires dedicated clean power and heat)", "Current cost is high ($400-$700/ton) requiring voluntary carbon markets or 45Q tax credits", "Requires heavy fan air moving equipment and Class VI storage wells"],
            "competing_technologies": ["Enhanced Rock Weathering", "Ocean Alkalinity Enhancement", "Bioenergy with Carbon Capture and Storage (BECCS)"]
        }
    },

    # -------------------------------------------------------------------------
    # 14. CRITICAL MINERALS & CLOSED-LOOP SUPPLY CHAINS
    # -------------------------------------------------------------------------
    "direct_lithium_extraction_dle": {
        "id": "direct_lithium_extraction_dle",
        "name": "Direct Lithium Extraction (DLE) from Brines",
        "category_id": "critical_minerals",
        "category_name": "Critical Minerals & Closed-Loop Supply Chains",
        "headline": "Extracting battery-grade lithium from geothermal brines in hours with 95%+ recovery and zero evaporation ponds.",
        "trl_current": 7,
        "trl_target": 9,
        "keywords": ["DLE", "direct lithium extraction", "battery recycling", "salton sea", "brine", "hydrometallurgy", "lithium carbonate"],
        "sector": "Critical Minerals & Materials",
        "fuel_vector": "Mineral Processing",
        "plain_english": {
            "what_is_it": "A technology that pulls battery-grade lithium out of geothermal salt water in minutes using chemical filters, and pumps the water right back underground without needing giant open-pit mines or massive evaporation ponds.",
            "how_it_works": "Geothermal brine is passed through an adsorption column filled with microscopic lithium-selective beads or ion-exchange resins. The beads capture lithium while letting other salts pass. Fresh water rinses the beads to produce pure lithium chloride, which is processed into battery-grade lithium hydroxide.",
            "why_it_matters": "Traditional lithium evaporation ponds take 18 months and consume billions of gallons of water in arid deserts. DLE takes under 2 hours, has a 95% smaller land footprint, and creates a 100% domestic battery supply chain (e.g. California Salton Sea, Arkansas Smackover).",
            "macro_problem_solved": "Geopolitical critical mineral dependence and environmental damage from open-pit mining."
        },
        "evolution": {
            "past": "Solar evaporation ponds (Chile/Argentina) and open-pit hard-rock spodumene mining (Australia, 1970s-2020).",
            "present": "Commercial pilot plants operating in Salton Sea (BHE Renewables, EnergySource) and Arkansas (ExxonMobil, Standard Lithium).",
            "future": "Supplying 50%+ of North American battery lithium from domestic brines and recycled scrap by 2030."
        },
        "frontier": {
            "moonshot_goal": "Produce battery-grade lithium hydroxide at <$4,000/ton with >95% recovery rate and near-zero freshwater consumption.",
            "kpis": [
                {"name": "Extraction Time", "current": "1 - 3 Hours", "target_2030": "< 30 Minutes", "status": "achieved"},
                {"name": "Lithium Recovery Efficiency", "current": "80% - 90%", "target_2030": "> 95%", "status": "on_track"},
                {"name": "Freshwater Intensity", "current": "10 - 25 m3 / ton Li", "target_2030": "< 2 m3 / ton Li (Closed loop)", "status": "on_track"},
                {"name": "Production Operating Cost", "current": "$4,500 - $6,000 / ton LiOH", "target_2030": "< $3,800 / ton LiOH", "status": "on_track"}
            ],
            "bottlenecks": [
                "Sorbent attrition and chemical fouling in hypersaline, high-temperature (>100C) geothermal brines.",
                "Separation of chemically similar competing divalent ions (Calcium, Magnesium, Iron, Zinc).",
                "Reinjection well chemistry management preventing silica and barium sulfate precipitation."
            ],
            "active_research_tracks": [
                "Electrochemical and membrane capacitive deionization extracting lithium without chemical eluent reagents (DOE AMMTO).",
                "Crown-ether and metal-organic framework (MOF) nanofiltration membranes with angstrom-level ion selectivity.",
                "Closed-loop hydrometallurgical recycling extracting 99% of Lithium, Nickel, Cobalt, and Manganese from black mass."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 90,
            "capex_competitiveness": 85,
            "duration_scalability": 95,
            "technology_maturity": 75,
            "domestic_supply_chain": 95,
            "siting_permitting_ease": 80
        },
        "trade_offs": {
            "strengths": ["Extracts lithium in hours instead of 18-24 months for evaporation ponds", "95% smaller land footprint with zero open-pit mining scars", "Co-located with geothermal clean power generation"],
            "weaknesses": ["Hypersaline geothermal brine chemistry causes sorbent degradation over time", "Requires reliable water reinjection management to avoid pore plugging", "Higher initial facility CapEx than simple evaporation ponds"],
            "competing_technologies": ["Hard-Rock Spodumene Mining", "Clay-Hosted Lithium Acid Leaching", "Closed-Loop Battery Recycling"]
        }
    },
    "closed_loop_battery_recycling": {
        "id": "closed_loop_battery_recycling",
        "name": "Closed-Loop Battery Hydrometallurgy & Direct Recycling",
        "category_id": "critical_minerals",
        "category_name": "Critical Minerals & Closed-Loop Supply Chains",
        "headline": "Recovering 95%+ of battery-grade Lithium, Nickel, and Cobalt from spent EV packs with 70% lower emissions than virgin mining.",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["battery recycling", "hydrometallurgy", "black mass", "direct recycling", "Redwood Materials", "Li-Cycle", "Ascend Elements"],
        "sector": "Circular Supply Chains",
        "fuel_vector": "Critical Materials Recovery",
        "plain_english": {
            "what_is_it": "Advanced recycling facilities that shred old electric vehicle batteries and electronics, dissolve the shredded powder (called 'black mass') in mild acid baths, and extract pure battery-grade lithium, nickel, cobalt, and graphite to make brand-new EV batteries.",
            "how_it_works": "Hydrometallurgy uses chemical precipitation, solvent extraction, and crystallization at low temperatures instead of burning batteries in a blast furnace (pyrometallurgy). Direct recycling goes one step further: it repairs and rejuvenates degraded cathode crystals without breaking them down to raw elements.",
            "why_it_matters": "Recycled battery metals perform identically to newly-mined materials, but require 70% less energy, consume zero mining land, and keep toxic heavy metals out of landfills while establishing a domestic circular economy.",
            "macro_problem_solved": "EV battery waste management and establishing a domestic critical mineral supply chain."
        },
        "evolution": {
            "past": "Smelting batteries in high-emission pyrometallurgical furnaces that burned off lithium (1990s-2015).",
            "present": "Commercial hydrometallurgical processing facilities scaling across North America (Redwood Materials, Ascend Elements, Li-Cycle).",
            "future": "Closed-loop direct cathode-to-cathode synthesis supplying 40%+ of domestic US battery manufacturing demand by 2035."
        },
        "frontier": {
            "moonshot_goal": "Achieve >98% elemental recovery of Lithium, Nickel, Cobalt, and Graphite with lower carbon intensity than virgin mining at <$1.50/kg processed.",
            "kpis": [
                {"name": "Lithium Recovery Rate", "current": "88% - 93%", "target_2030": "> 98%", "status": "on_track"},
                {"name": "Nickel & Cobalt Recovery Rate", "current": "95% - 98%", "target_2030": "> 99%", "status": "achieved"},
                {"name": "Carbon Footprint vs Virgin Mining", "current": "50% - 60% Lower", "target_2030": "> 75% Lower", "status": "on_track"},
                {"name": "Direct Cathode Re-synthesis Yield", "current": "Pilot (80%)", "target_2030": "> 95% Commercial", "status": "on_track"}
            ],
            "bottlenecks": [
                "Logistics and fire-safety transport regulations for damaged or end-of-life high-voltage battery packs.",
                "Varying battery pack chemistries (NMC, LFP, NCA, Sodium-ion) requiring flexible chemical separation processes.",
                "Economical recovery of lower-value Lithium Iron Phosphate (LFP) chemistries where nickel and cobalt are absent."
            ],
            "active_research_tracks": [
                "Direct cathode regeneration using hydrothermal relithiation (DOE ReCell Center / ANL).",
                "Automated robotic pack disassembly and cell sorting eliminating manual labor.",
                "Electrochemical selective extraction of lithium from LFP black mass with zero acid effluent."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 90,
            "capex_competitiveness": 85,
            "duration_scalability": 90,
            "technology_maturity": 85,
            "domestic_supply_chain": 96,
            "siting_permitting_ease": 82
        },
        "trade_offs": {
            "strengths": ["Creates an infinite domestic loop of battery minerals without mining", "Low carbon footprint and zero toxic wastewater discharge in modern closed-loop plants", "Complies with strict IRA domestic content and battery sourcing statutory rules"],
            "weaknesses": ["Volume of end-of-life EV packs is still ramping up (most near-term feedstock is factory scrap)", "Economic margins are tighter on low-cost LFP packs compared to high-nickel packs", "Requires nationwide battery collection and safe transport infrastructure"],
            "competing_technologies": ["High-Temperature Pyrometallurgical Smelting", "Virgin Hard-Rock Mining", "Second-Life Stationary Storage Repurposing"]
        }
    },

    # -------------------------------------------------------------------------
    # 15. AI, HPC & DATA CENTER DECARBONIZATION
    # -------------------------------------------------------------------------
    "ai_datacenter_liquid_cooling": {
        "id": "ai_datacenter_liquid_cooling",
        "name": "Direct-to-Chip & Immersion Liquid Cooling for AI",
        "category_id": "ai_datacenter",
        "category_name": "AI, HPC, Resilience & Data Center Decarb",
        "headline": "Direct liquid cold plates and two-phase dielectric immersion cooling slashing data center power usage effectiveness (PUE) below 1.05.",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["liquid cooling", "direct to chip", "immersion cooling", "data center", "PUE", "AI compute", "NVIDIA Blackwell", "waste heat reuse"],
        "sector": "High-Performance Computing Infrastructure",
        "fuel_vector": "Thermal Energy Transfer",
        "plain_english": {
            "what_is_it": "Cooling systems for artificial intelligence supercomputers that pump chilled liquid directly across scorching hot GPU chips or submerge entire server racks in non-conductive mineral oil baths, eliminating loud, energy-hogging air conditioning fans.",
            "how_it_works": "Water conducts heat 24 times better than air. Direct-to-chip copper cold plates capture heat directly from 1,000-watt AI processors. Immersion cooling submerges servers in clear dielectric fluid that boils at low temperatures, carrying heat away as vapor that condenses on cold coils and drips back down.",
            "why_it_matters": "AI chips generate so much concentrated heat that standard air cooling physically cannot keep them from melting. Liquid cooling cuts data center cooling electricity by 90% and produces hot water (140F / 60C) that can be piped to heat nearby homes and greenhouses.",
            "macro_problem_solved": "Skyrocketing electricity and water consumption of generative AI data centers."
        },
        "evolution": {
            "past": "Perimeter CRAC chilled-air conditioning units with high PUE > 1.6 (1990-2020).",
            "present": "Mandatory direct-to-chip liquid cooling for ultra-dense 100kW+ AI racks (NVIDIA GB200, Google TPU, Microsoft).",
            "future": "Waste-heat exporting AI microgrid data centers with integrated fuel cells, geothermal, and district heating by 2028."
        },
        "frontier": {
            "moonshot_goal": "Achieve continuous Power Usage Effectiveness (PUE) < 1.03 for 100 kW+ per rack AI clusters with 100% waste heat export.",
            "kpis": [
                {"name": "Power Usage Effectiveness (PUE)", "current": "1.12 - 1.25 (Liquid/Air hybrid)", "target_2030": "< 1.03 (Full liquid)", "status": "on_track"},
                {"name": "Rack Power Density", "current": "40 - 100 kW / rack", "target_2030": "> 250 kW / rack", "status": "achieved"},
                {"name": "Cooling Water Consumption", "current": "1 - 3 Gallons / kWh", "target_2030": "0 Gallons (Closed loop dry cooler)", "status": "on_track"},
                {"name": "Waste Heat Export Temperature", "current": "45C - 55C", "target_2030": "> 65C - 80C (District heating)", "status": "on_track"}
            ],
            "bottlenecks": [
                "Quick-disconnect fitting leaks and dielectric fluid compatibility with server motherboard polymers and optical transceivers.",
                "High thermal interface material (TIM) resistance between the silicon die and copper cold plate.",
                "Lack of district heating infrastructure near rural mega-watt AI data center campuses to accept hot water."
            ],
            "active_research_tracks": [
                "Micro-channel silicon embedded 3D cooling channels etched directly inside the semiconductor substrate (DARPA / DOE ARPA-E COOLER).",
                "Two-phase thermosiphon loops eliminating mechanical pumps.",
                "Behind-the-meter small modular reactor (SMR) and geothermal co-location powering off-grid AI gigawatt campuses."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 96,
            "capex_competitiveness": 82,
            "duration_scalability": 90,
            "technology_maturity": 85,
            "domestic_supply_chain": 90,
            "siting_permitting_ease": 92
        },
        "trade_offs": {
            "strengths": ["Eliminates 90% of cooling power consumption (PUE < 1.05)", "Enables ultra-dense compute clusters (>100 kW per rack)", "Produces hot water output (50-65C) ideal for heating surrounding neighborhoods and buildings"],
            "weaknesses": ["Higher upfront server and plumbing rack CapEx", "Requires fluid-handling equipment and technician retraining", "PFAS regulations restrict certain two-phase engineered fluids"],
            "competing_technologies": ["High-Efficiency Rear-Door Heat Exchangers", "Evaporative Cooling Towers", "Chilled-Water CRAC Air Units"]
        }
    },
    "black_start_microgrids": {
        "id": "black_start_microgrids",
        "name": "Black-Start Multi-Resource Microgrids & Resilience Hubs",
        "category_id": "ai_datacenter",
        "category_name": "AI, HPC, Resilience & Data Center Decarb",
        "headline": "Autonomous localized power islands with black-start restoration and seamless sub-cycle grid disconnection.",
        "trl_current": 8,
        "trl_target": 9,
        "keywords": ["microgrid", "black-start", "islanding", "resilience hub", "critical facility", "severe weather", "distributed generation"],
        "sector": "Grid Reliability & Resilience",
        "fuel_vector": "Hybrid Clean Distributed Power",
        "plain_english": {
            "what_is_it": "Self-contained localized electrical networks connecting solar panels, battery storage, and clean backup generators at critical facilities (like hospitals, water treatment plants, fire stations, and emergency shelters) that instantly disconnect from the main power grid during a blackout and keep power running independently.",
            "how_it_works": "An intelligent microgrid controller monitors grid stability. If a hurricane or wildfire knocks out the main utility line, high-speed static switches isolate the microgrid in milliseconds. 'Black-start' inverters then energize the local wires without needing any external power surge.",
            "why_it_matters": "Climate-driven extreme storms (hurricanes, ice storms, heat waves) are increasing grid outage frequency. Microgrids ensure life-saving community infrastructure never loses power, while earning revenue on regular days by exporting clean power to the utility.",
            "macro_problem_solved": "Catastrophic power outages during extreme weather events and securing mission-critical community infrastructure."
        },
        "evolution": {
            "past": "Diesel backup generators that frequently failed to start or ran out of fuel (1970s-2015).",
            "present": "Multi-resource solar+storage microgrids deployed at military bases, university campuses, and hospitals (NY Prize, CEC EPC).",
            "future": "Federated community microgrids dynamically trading power with neighbors during regional disasters by 2028-2032."
        },
        "frontier": {
            "moonshot_goal": "Achieve 100% autonomous seamless islanding and indefinite black-start survival with zero diesel fuel across frontline community hubs.",
            "kpis": [
                {"name": "Grid Disconnection Transfer Time", "current": "10 - 50 Milliseconds", "target_2030": "< 4 Milliseconds (Zero flicker)", "status": "on_track"},
                {"name": "Off-Grid Islanding Survival Duration", "current": "2 - 7 Days", "target_2030": "Indefinite (Renewable solar/BESS)", "status": "on_track"},
                {"name": "Microgrid Controller Setup Time", "current": "6 - 12 Months custom", "target_2030": "< 2 Weeks modular", "status": "on_track"},
                {"name": "Diesel Replacement Ratio", "current": "75% - 85%", "target_2030": "100% Zero-Carbon", "status": "achieved"}
            ],
            "bottlenecks": [
                "Complex utility interconnection and anti-islanding protection relay coordination.",
                "Custom engineering and control integration across multiple inverter and generator vendors.",
                "Regulatory utility franchise laws prohibiting sharing microgrid power across public street rights-of-way."
            ],
            "active_research_tracks": [
                "Plug-and-play IEEE 2030.7 compliant microgrid controllers with self-configuring agent-based architectures (DOE OE).",
                "Sub-harmonic oscillation suppression during sudden heavy motor starts (e.g. water pumps/elevators).",
                "Multi-microgrid clustering where adjacent neighborhood microgrids automatically connect to help each other."
            ]
        },
        "radar_scores": {
            "round_trip_efficiency": 92,
            "capex_competitiveness": 85,
            "duration_scalability": 95,
            "technology_maturity": 88,
            "domestic_supply_chain": 92,
            "siting_permitting_ease": 80
        },
        "trade_offs": {
            "strengths": ["Guarantees uninterrupted power for critical life-safety and emergency services", "Operates as a flexible capacity asset providing grid support 99% of the year", "100% eliminates diesel fuel delivery vulnerabilities during natural disasters"],
            "weaknesses": ["Utility interconnection approvals can be protracted", "Higher upfront capital cost than a simple standalone diesel generator", "Cross-property power sharing often restricted by state utility regulations"],
            "competing_technologies": ["Fossil Diesel / Gas Generators", "Utility Substation Hardening", "Behind-the-Meter Standalone BESS"]
        }
    }
}

# Memory Cache for Evidence Aggregations
_LIVE_EVIDENCE_CACHE: Dict[str, Dict[str, Any]] = {}

def get_live_technology_evidence(db: Session, tech_id: str) -> Dict[str, Any]:
    """
    Executes live SQL queries against the database (awards, opportunities,
    recipient_patents, recipients) to ground each technology dossier in empirical facts.
    """
    if tech_id in _LIVE_EVIDENCE_CACHE:
        return _LIVE_EVIDENCE_CACHE[tech_id]

    disk_file = CACHE_DIR / f"evidence_{tech_id}.json"
    if disk_file.exists():
        try:
            with open(disk_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    _LIVE_EVIDENCE_CACHE[tech_id] = data
                    return data
        except Exception:
            pass

    tech_def = TECHNOLOGY_REGISTRY.get(tech_id)
    if not tech_def:
        return {}

    keywords = tech_def.get("keywords", [tech_id])
    active_keywords = [kw for kw in keywords if len(kw) >= 3][:6] or [tech_id]
    
    award_conditions = []
    opp_conditions = []
    patent_conditions = []
    
    for kw in active_keywords:
        clean_kw = kw.replace("'", "''")
        award_conditions.append(f"LOWER(project_title) LIKE '%{clean_kw.lower()}%'")
        opp_conditions.append(f"LOWER(name) LIKE '%{clean_kw.lower()}%'")
        patent_conditions.append(f"LOWER(title) LIKE '%{clean_kw.lower()}%' OR LOWER(technology_area) LIKE '%{clean_kw.lower()}%'")
    
    award_where = " OR ".join(award_conditions)
    opp_where = " OR ".join(opp_conditions)
    patent_where = " OR ".join(patent_conditions)


    # 1. Total Funding & Award Counts
    total_funding = 0.0
    award_count = 0
    distinct_recipients = 0
    try:
        sql = text(f"""
            SELECT 
                COALESCE(SUM(award_amount), 0) as total_amt,
                COUNT(id) as cnt,
                COUNT(DISTINCT recipient_name) as rec_cnt
            FROM awards
            WHERE ({award_where})
        """)
        row = db.execute(sql).fetchone()
        if row:
            total_funding = float(row[0] or 0.0)
            award_count = int(row[1] or 0)
            distinct_recipients = int(row[2] or 0)
    except Exception as e:
        logger.warning(f"Error querying total funding for {tech_id}: {e}")
        try:
            db.rollback()
        except Exception:
            pass

    avg_funding = (total_funding / award_count) if award_count > 0 else 0.0

    # 2. Top 5 Funded Recipients (Directly from awards table)
    top_recipients = []
    try:
        top_rec_sql = text(f"""
            SELECT 
                recipient_name,
                recipient_city,
                recipient_state,
                recipient_type,
                COUNT(id) as aw_cnt,
                COALESCE(SUM(award_amount), 0) as rec_total
            FROM awards
            WHERE ({award_where}) AND recipient_name IS NOT NULL
            GROUP BY recipient_name, recipient_city, recipient_state, recipient_type
            ORDER BY rec_total DESC
            LIMIT 5
        """)
        rec_rows = db.execute(top_rec_sql).fetchall()
        for r in rec_rows:
            tot = float(r[5] or 0.0)
            top_recipients.append({
                "name": r[0] or "Undisclosed Entity",
                "city": r[1] or "N/A",
                "state": r[2] or "N/A",
                "type": r[3] or "Organization",
                "awards_count": r[4],
                "total_awarded": tot,
                "total_awarded_fmt": f"${tot / 1e6:,.1f}M" if tot >= 1e6 else f"${tot:,.0f}"
            })
    except Exception as e:
        logger.warning(f"Error querying top recipients for {tech_id}: {e}")
        try:
            db.rollback()
        except Exception:
            pass

    # 3. Active Open Solicitations
    active_solicitations = []
    total_pipeline_opps = 0
    try:
        opp_sql = text(f"""
            SELECT 
                id,
                solicitation_number,
                name,
                agency,
                total_funding,
                status
            FROM opportunities
            WHERE ({opp_where}) AND LOWER(status) = 'open'
            ORDER BY total_funding DESC
            LIMIT 5
        """)
        opp_rows = db.execute(opp_sql).fetchall()
        total_pipeline_opps = len(opp_rows)
        for o in opp_rows:
            fnd = float(o[4] or 0.0)
            active_solicitations.append({
                "id": o[0],
                "solicitation_number": o[1] or "FOA",
                "name": o[2],
                "agency": o[3] or "State/Federal Agency",
                "total_funding": fnd,
                "funding_fmt": f"${fnd / 1e6:,.1f}M" if fnd >= 1e6 else (f"${fnd:,.0f}" if fnd > 0 else "Funding Varies"),
                "status": o[5] or "Open"
            })
    except Exception as e:
        logger.warning(f"Error querying active opportunities for {tech_id}: {e}")
        try:
            db.rollback()
        except Exception:
            pass

    # 4. Recent Historical Project Awards
    recent_awards = []
    try:
        aw_sql = text(f"""
            SELECT 
                id,
                project_title,
                recipient_name,
                agency,
                award_amount,
                year,
                recipient_state
            FROM awards
            WHERE ({award_where})
            ORDER BY year DESC, award_amount DESC
            LIMIT 5
        """)
        aw_rows = db.execute(aw_sql).fetchall()
        for a in aw_rows:
            amt = float(a[4] or 0.0)
            recent_awards.append({
                "id": a[0],
                "title": a[1] or "Advanced Innovation Award",
                "recipient": a[2] or "Research Institution",
                "agency": a[3] or "Agency",
                "amount": amt,
                "amount_fmt": f"${amt / 1e6:,.2f}M" if amt >= 1e6 else f"${amt:,.0f}",
                "year": a[5] or 2024,
                "state": a[6] or "NY"
            })
    except Exception as e:
        logger.warning(f"Error querying recent awards for {tech_id}: {e}")
        try:
            db.rollback()
        except Exception:
            pass

    # 5. Linked USPTO Patents
    top_patents = []
    patent_count = 0
    try:
        pat_sql = text(f"""
            SELECT 
                id,
                patent_number,
                title,
                assignee_name,
                grant_date
            FROM recipient_patents
            WHERE ({patent_where})
            ORDER BY grant_date DESC
            LIMIT 5
        """)
        pat_rows = db.execute(pat_sql).fetchall()
        patent_count = len(pat_rows)
        for p in pat_rows:
            date_val = p[4]
            date_str = date_val.strftime("%Y-%m-%d") if hasattr(date_val, "strftime") else (str(date_val)[:10] if date_val else None)
            top_patents.append({
                "id": p[0],
                "number": p[1],
                "title": p[2],
                "assignee": p[3] or "Innovator",
                "date": date_str
            })
    except Exception as e:
        logger.warning(f"Error querying patents for {tech_id}: {e}")
        try:
            db.rollback()
        except Exception:
            pass
        logger.warning(f"Error querying patents for {tech_id}: {e}")

    result = {
        "tracked_capital_usd": total_funding,
        "tracked_capital_fmt": f"${total_funding / 1e9:,.2f}B" if total_funding >= 1e9 else f"${total_funding / 1e6:,.1f}M",
        "award_count": award_count,
        "average_award_fmt": f"${avg_funding / 1e6:,.2f}M" if avg_funding >= 1e6 else f"${avg_funding:,.0f}",
        "distinct_recipients_count": distinct_recipients,
        "temporal_vintage": "1991 - 2026",
        "total_solicitations": total_pipeline_opps,
        "active_solicitations_count": len(active_solicitations),
        "pipeline_funding_fmt": f"${sum(s['total_funding'] for s in active_solicitations) / 1e6:,.1f}M" if active_solicitations else "$0.0M",
        "top_recipients": top_recipients,
        "recent_awards": recent_awards,
        "active_solicitations": active_solicitations,
        "top_patents": top_patents,
        "patent_count": patent_count
    }
    _LIVE_EVIDENCE_CACHE[tech_id] = result
    try:
        with open(disk_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    except Exception:
        pass
    return result

# ==============================================================================
# 4. DOSSIER & LIST RETRIEVAL SERVICES
# ==============================================================================

def get_technology_categories(db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """Returns list of 15 clean energy sectors from database."""
    if db:
        try:
            cats = db.query(TechnologyCategory).order_by(TechnologyCategory.sort_order).all()
            if cats:
                return [{
                    "id": c.id,
                    "name": c.name,
                    "icon": c.icon,
                    "description": c.description,
                    "color": c.color,
                    "accent": c.accent
                } for c in cats]
        except Exception as e:
            logger.warning(f"Error reading categories from DB: {e}")
            try:
                db.rollback()
            except Exception:
                pass
    return CATEGORIES

def get_technologies_list(db: Optional[Session] = None, category_id: Optional[str] = None, search: Optional[str] = None, vector_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns indexed list of technologies with headline metadata from database."""
    cat_id_str = category_id if isinstance(category_id, str) and category_id.strip() else None
    search_str = search if isinstance(search, str) and search.strip() else None
    vec_type_str = vector_type if isinstance(vector_type, str) and vector_type.strip() else None

    if db:
        try:
            q = db.query(Technology)
            if cat_id_str:
                q = q.filter(Technology.category_id == cat_id_str)
            rows = q.all()
            if rows:
                results = []
                for r in rows:
                    reg_item = TECHNOLOGY_REGISTRY.get(r.id, {})
                    v_type = getattr(r, 'vector_type', None) or reg_item.get('vector_type', 'hardware')
                    if vec_type_str and vec_type_str != 'all' and v_type != vec_type_str:
                        continue
                    keywords = json.loads(r.keywords_json or "[]")
                    if search_str:
                        s = search_str.lower().strip()
                        name_match = s in r.name.lower()
                        headline_match = s in (r.headline or "").lower()
                        keyword_match = any(s in kw.lower() for kw in keywords)
                        fuel_match = s in (r.fuel_vector or "").lower()
                        if not (name_match or headline_match or keyword_match or fuel_match):
                            continue
                    results.append({
                        "id": r.id,
                        "name": r.name,
                        "category_id": r.category_id,
                        "category_name": r.category.name if r.category else r.category_id,
                        "headline": r.headline,
                        "trl_current": r.trl_current,
                        "trl_target": r.trl_target,
                        "sector": r.sector,
                        "fuel_vector": r.fuel_vector,
                        "vector_type": v_type,
                        "keywords": keywords
                    })
                return results
        except Exception as e:
            logger.warning(f"Error querying technologies list from DB: {e}")
            try:
                db.rollback()
            except Exception:
                pass

    # Fallback to in-memory registry
    results = []
    for tech_id, t in TECHNOLOGY_REGISTRY.items():
        if cat_id_str and t.get("category_id") != cat_id_str:
            continue
        v_type = t.get("vector_type", "hardware")
        if vec_type_str and vec_type_str != 'all' and v_type != vec_type_str:
            continue
        if search_str:
            s = search_str.lower().strip()
            name_match = s in t.get("name", "").lower()
            headline_match = s in t.get("headline", "").lower()
            keyword_match = any(s in kw.lower() for kw in t.get("keywords", []))
            fuel_match = s in t.get("fuel_vector", "").lower()
            if not (name_match or headline_match or keyword_match or fuel_match):
                continue

        results.append({
            "id": t["id"],
            "name": t["name"],
            "category_id": t["category_id"],
            "category_name": t["category_name"],
            "headline": t["headline"],
            "trl_current": t["trl_current"],
            "trl_target": t["trl_target"],
            "sector": t["sector"],
            "fuel_vector": t["fuel_vector"],
            "vector_type": v_type,
            "keywords": t["keywords"]
        })
    return results

def synthesize_cost_performance(tech_id: str, tech_def: Dict[str, Any]) -> Dict[str, Any]:
    """Provides quantitative cost and performance baseline vs target trajectories aligned with DOE Earthshots."""
    if "cost_performance" in tech_def:
        return tech_def["cost_performance"]

    cat_id = tech_def.get("category_id", "")
    
    # Domain-specific cost & performance trajectories
    if cat_id == "solar_systems":
        return {
            "cost_metric": {
                "name": "Levelized Cost of Electricity (LCOE)",
                "unit": "$/kWh",
                "baseline_2024": 0.045,
                "baseline_fmt": "$0.045 / kWh",
                "target_2030": 0.020,
                "target_2030_fmt": "$0.020 / kWh",
                "target_2035": 0.015,
                "target_2035_fmt": "$0.015 / kWh",
                "reduction_pct": "-67%",
                "primary_driver": "40% higher energy yield per watt and automated roll-to-roll balance-of-system integration."
            },
            "performance_metric": {
                "name": "Commercial Module Efficiency",
                "unit": "%",
                "baseline_2024": 24.5,
                "baseline_fmt": "24.5%",
                "target_2030": 30.0,
                "target_2030_fmt": "30.0%",
                "target_2035": 33.5,
                "target_2035_fmt": "33.5%",
                "improvement_pct": "+37%",
                "primary_driver": "Wide-bandgap top perovskite capture of blue/UV photons breaking the single-junction ceiling."
            },
            "learning_rate": "18% cost decline per doubling of cumulative manufacturing scale",
            "earthshot_goal": "DOE Solar 2030 Earthshot Target (<$0.020/kWh utility solar)"
        }
    elif cat_id == "wind_systems":
        return {
            "cost_metric": {
                "name": "Offshore Wind Levelized Cost (LCOE)",
                "unit": "$/MWh",
                "baseline_2024": 85.0,
                "baseline_fmt": "$85 / MWh",
                "target_2030": 45.0,
                "target_2030_fmt": "$45 / MWh",
                "target_2035": 32.0,
                "target_2035_fmt": "$32 / MWh",
                "reduction_pct": "-62%",
                "primary_driver": "15MW+ serial production, industrialized port logistics, and automated installation vessels."
            },
            "performance_metric": {
                "name": "Nameplate Single-Turbine Capacity",
                "unit": "MW",
                "baseline_2024": 15.0,
                "baseline_fmt": "15 MW",
                "target_2030": 22.0,
                "target_2030_fmt": "22 MW",
                "target_2035": 25.0,
                "target_2035_fmt": "25 MW",
                "improvement_pct": "+67%",
                "primary_driver": "Carbon-hybrid composite blades and permanent-magnet direct-drive generators."
            },
            "learning_rate": "14% cost decline per doubling of global installed offshore capacity",
            "earthshot_goal": "DOE Floating Offshore Wind Shot ($45/MWh by 2035)"
        }
    elif cat_id == "energy_storage":
        return {
            "cost_metric": {
                "name": "Levelized Cost of Storage (LCOS)",
                "unit": "$/kWh-cycle",
                "baseline_2024": 0.25,
                "baseline_fmt": "$0.250 / kWh",
                "target_2030": 0.050,
                "target_2030_fmt": "$0.050 / kWh",
                "target_2035": 0.020,
                "target_2035_fmt": "$0.020 / kWh",
                "reduction_pct": "-92%",
                "primary_driver": "Abundant commodity raw materials (iron, air, sodium, vanadium) replacing scarce cobalt/nickel."
            },
            "performance_metric": {
                "name": "Continuous Full-Power Discharge Duration",
                "unit": "Hours",
                "baseline_2024": 12.0,
                "baseline_fmt": "12 Hours",
                "target_2030": 100.0,
                "target_2030_fmt": "100 Hours",
                "target_2035": 150.0,
                "target_2035_fmt": "150 Hours",
                "improvement_pct": "+1,150%",
                "primary_driver": "Electrode active material thickness and decoupled power-to-energy architecture."
            },
            "learning_rate": "21% cost reduction per doubling of cumulative MWh deployed",
            "earthshot_goal": "DOE Long Duration Storage Shot (90% cost reduction to <$0.05/kWh LCOS)"
        }
    elif cat_id == "geothermal_subsurface":
        return {
            "cost_metric": {
                "name": "Enhanced Geothermal Levelized Cost (LCOE)",
                "unit": "$/MWh",
                "baseline_2024": 95.0,
                "baseline_fmt": "$95 / MWh",
                "target_2030": 45.0,
                "target_2030_fmt": "$45 / MWh",
                "target_2035": 35.0,
                "target_2035_fmt": "$35 / MWh",
                "reduction_pct": "-63%",
                "primary_driver": "Fast-penetration PDC drilling bits, multi-stage horizontal lateral fracturing, and shared surface plant."
            },
            "performance_metric": {
                "name": "Production Well Flow Rate (Superheated Brine)",
                "unit": "L/s",
                "baseline_2024": 60.0,
                "baseline_fmt": "60 L/s",
                "target_2030": 140.0,
                "target_2030_fmt": "140 L/s",
                "target_2035": 200.0,
                "target_2035_fmt": "200 L/s",
                "improvement_pct": "+233%",
                "primary_driver": "Precision multi-stage hydraulic stimulation connecting extensive high-permeability fractures."
            },
            "learning_rate": "15% well construction cost decline per doubling of drilled EGS footage",
            "earthshot_goal": "DOE Enhanced Geothermal Shot ($45/MWh by 2035)"
        }
    elif cat_id == "clean_hydrogen":
        return {
            "cost_metric": {
                "name": "Levelized Cost of Clean Hydrogen (LCOH)",
                "unit": "$/kg H2",
                "baseline_2024": 6.50,
                "baseline_fmt": "$6.50 / kg",
                "target_2030": 1.50,
                "target_2030_fmt": "$1.50 / kg",
                "target_2035": 1.00,
                "target_2035_fmt": "$1.00 / kg",
                "reduction_pct": "-85%",
                "primary_driver": "Multi-gigawatt automated stack manufacturing and sub-$0.02/kWh dedicated renewable power."
            },
            "performance_metric": {
                "name": "System Electrical Consumption (Efficiency)",
                "unit": "kWh/kg",
                "baseline_2024": 55.0,
                "baseline_fmt": "55 kWh/kg",
                "target_2030": 42.0,
                "target_2030_fmt": "42 kWh/kg",
                "target_2035": 38.0,
                "target_2035_fmt": "38 kWh/kg",
                "improvement_pct": "+31%",
                "primary_driver": "High-temperature steam electrolysis (SOEC) and low-resistance AEM membranes."
            },
            "learning_rate": "19% electrolyzer CapEx reduction per doubling of manufacturing capacity",
            "earthshot_goal": "DOE Hydrogen Shot ($1 per 1 kg clean hydrogen in 1 decade)"
        }
    elif cat_id == "bioenergy_waste":
        return {
            "cost_metric": {
                "name": "Sustainable Aviation Fuel Levelized Production Cost",
                "unit": "$/gallon",
                "baseline_2024": 6.80,
                "baseline_fmt": "$6.80 / gal",
                "target_2030": 2.80,
                "target_2030_fmt": "$2.80 / gal",
                "target_2035": 2.10,
                "target_2035_fmt": "$2.10 / gal",
                "reduction_pct": "-69%",
                "primary_driver": "Alcohol-to-Jet scaling, non-food cover crop feedstock supply, and modular hydroprocessing skids."
            },
            "performance_metric": {
                "name": "Lifecycle Greenhouse Gas (GHG) Reduction",
                "unit": "% vs Jet A-1",
                "baseline_2024": 70.0,
                "baseline_fmt": "70.0%",
                "target_2030": 90.0,
                "target_2030_fmt": "90.0%",
                "target_2035": 105.0,
                "target_2035_fmt": "105.0% (Net-Negative)",
                "improvement_pct": "+50%",
                "primary_driver": "Biogenic carbon capture co-location and regenerative agricultural feedstock tillage practices."
            },
            "learning_rate": "17% cost decline per doubling of cumulative commercial biorefinery capacity",
            "earthshot_goal": "DOE Clean Fuels & Products Earthshot (85% lower greenhouse gas footprint by 2035)"
        }
    elif cat_id == "carbon_management":
        return {
            "cost_metric": {
                "name": "Direct Air Capture Net Removed Cost",
                "unit": "$/ton CO2",
                "baseline_2024": 600.0,
                "baseline_fmt": "$600 / ton",
                "target_2030": 150.0,
                "target_2030_fmt": "$150 / ton",
                "target_2035": 80.0,
                "target_2035_fmt": "$80 / ton",
                "reduction_pct": "-87%",
                "primary_driver": "Low-pressure-drop structured sorbent monoliths and utilization of co-located industrial waste heat."
            },
            "performance_metric": {
                "name": "Thermal Desorption Energy Requirement",
                "unit": "kWh/ton",
                "baseline_2024": 2200.0,
                "baseline_fmt": "2,200 kWh/t",
                "target_2030": 1200.0,
                "target_2030_fmt": "1,200 kWh/t",
                "target_2035": 800.0,
                "target_2035_fmt": "800 kWh/t",
                "improvement_pct": "+64%",
                "primary_driver": "High-capacity amine/MOF sorbents releasing CO2 under mild 80C-100C temperatures."
            },
            "learning_rate": "20% CapEx reduction per doubling of cumulative megatonne capture capacity",
            "earthshot_goal": "DOE Carbon Negative Shot (<$100/net metric ton CO2 removed)"
        }
    elif cat_id == "advanced_nuclear":
        return {
            "cost_metric": {
                "name": "SMR Overnight Installed Capital Cost",
                "unit": "$/kW",
                "baseline_2024": 8500.0,
                "baseline_fmt": "$8,500 / kW",
                "target_2030": 3600.0,
                "target_2030_fmt": "$3,600 / kW",
                "target_2035": 2800.0,
                "target_2035_fmt": "$2,800 / kW",
                "reduction_pct": "-67%",
                "primary_driver": "Standardized factory assembly-line fabrication and modular containment vessels."
            },
            "performance_metric": {
                "name": "Outlet Coolant Temperature for Clean Heat",
                "unit": "°C",
                "baseline_2024": 300.0,
                "baseline_fmt": "300°C",
                "target_2030": 750.0,
                "target_2030_fmt": "750°C",
                "target_2035": 850.0,
                "target_2035_fmt": "850°C",
                "improvement_pct": "+183%",
                "primary_driver": "TRISO fuel pebbles and inert high-pressure helium or molten salt coolant loops."
            },
            "learning_rate": "12% cost decline per serial nth-of-a-kind unit manufactured",
            "earthshot_goal": "DOE ARDP Advanced Reactor Demonstration Deployment"
        }
    elif cat_id == "industrial_decarb":
        return {
            "cost_metric": {
                "name": "Industrial High-Temp Heat Pump Installed CapEx",
                "unit": "$/kW-th",
                "baseline_2024": 1200.0,
                "baseline_fmt": "$1,200 / kW-th",
                "target_2030": 450.0,
                "target_2030_fmt": "$450 / kW-th",
                "target_2035": 300.0,
                "target_2035_fmt": "$300 / kW-th",
                "reduction_pct": "-75%",
                "primary_driver": "Standardized hermetic turbo-compressors and packaged modular industrial skids."
            },
            "performance_metric": {
                "name": "Maximum Process Steam Temperature",
                "unit": "°C",
                "baseline_2024": 110.0,
                "baseline_fmt": "110°C",
                "target_2030": 180.0,
                "target_2030_fmt": "180°C",
                "target_2035": 220.0,
                "target_2035_fmt": "220°C",
                "improvement_pct": "+100%",
                "primary_driver": "Low-GWP specialized hydrofluoroolefin (HFO) and natural refrigerant blends."
            },
            "learning_rate": "16% cost decline per doubling of industrial MW-thermal installed",
            "earthshot_goal": "DOE Industrial Heat Shot (85% lower greenhouse gas industrial heat)"
        }
    else:
        # Default high-impact trajectory
        return {
            "cost_metric": {
                "name": "Installed Unit Capital Cost (CapEx)",
                "unit": "$/unit",
                "baseline_2024": 1000.0,
                "baseline_fmt": "$1,000 / unit",
                "target_2030": 350.0,
                "target_2030_fmt": "$350 / unit",
                "target_2035": 200.0,
                "target_2035_fmt": "$200 / unit",
                "reduction_pct": "-80%",
                "primary_driver": "Supply chain localization, automated mass production, and modular balance-of-plant."
            },
            "performance_metric": {
                "name": "System Overall Efficiency & Operational Uptime",
                "unit": "%",
                "baseline_2024": 65.0,
                "baseline_fmt": "65.0%",
                "target_2030": 88.0,
                "target_2030_fmt": "88.0%",
                "target_2035": 95.0,
                "target_2035_fmt": "95.0%",
                "improvement_pct": "+46%",
                "primary_driver": "Advanced composite materials, digital twins, and autonomous control algorithms."
            },
            "learning_rate": "15% cost decline per doubling of cumulative commercial volume",
            "earthshot_goal": "Clean Energy 2030 Decarbonization Earthshot Alignment"
        }

def get_technology_dossier(db: Session, tech_id: str) -> Optional[Dict[str, Any]]:
    """Builds the comprehensive dossier combining DB tables and live empirical DB evidence."""
    tech_row = None
    if db:
        try:
            tech_row = db.query(Technology).filter(Technology.id == tech_id).first()
        except Exception as e:
            logger.warning(f"Error fetching technology row for {tech_id}: {e}")
            try:
                db.rollback()
            except Exception:
                pass

    if tech_row:
        evidence = get_live_technology_evidence(db, tech_id)
        keywords = json.loads(tech_row.keywords_json or "[]")
        bottlenecks = json.loads(tech_row.bottlenecks_json or "[]")
        active_research = json.loads(tech_row.active_research_json or "[]")
        strengths = json.loads(tech_row.tradeoffs_strengths_json or "[]")
        weaknesses = json.loads(tech_row.tradeoffs_weaknesses_json or "[]")
        competing_techs = json.loads(tech_row.competing_techs_json or "[]")
        radar_scores = json.loads(tech_row.radar_scores_json or "{}")

        # KPIs from relational table
        kpis = []
        for k in tech_row.kpis:
            kpis.append({
                "name": k.name,
                "current": k.current_value,
                "target_2030": k.target_2030,
                "status": k.status
            })

        # Cost & Performance from relational table
        cost_perf = None
        cp_row = tech_row.cost_performance
        if cp_row:
            cost_perf = {
                "cost_metric": {
                    "name": cp_row.cost_metric_name,
                    "unit": cp_row.cost_unit,
                    "baseline_2024": cp_row.cost_baseline_2024,
                    "baseline_fmt": cp_row.cost_baseline_fmt,
                    "target_2030": cp_row.cost_target_2030,
                    "target_2030_fmt": cp_row.cost_target_2030_fmt,
                    "target_2035": cp_row.cost_target_2035,
                    "target_2035_fmt": cp_row.cost_target_2035_fmt,
                    "reduction_pct": cp_row.cost_reduction_pct,
                    "primary_driver": cp_row.cost_primary_driver
                },
                "performance_metric": {
                    "name": cp_row.perf_metric_name,
                    "unit": cp_row.perf_unit,
                    "baseline_2024": cp_row.perf_baseline_2024,
                    "baseline_fmt": cp_row.perf_baseline_fmt,
                    "target_2030": cp_row.perf_target_2030,
                    "target_2030_fmt": cp_row.perf_target_2030_fmt,
                    "target_2035": cp_row.perf_target_2035,
                    "target_2035_fmt": cp_row.perf_target_2035_fmt,
                    "improvement_pct": cp_row.perf_improvement_pct,
                    "primary_driver": cp_row.perf_primary_driver
                },
                "learning_rate": cp_row.learning_rate,
                "earthshot_goal": cp_row.earthshot_goal
            }

        radar_data = [
            {"dimension": "Efficiency / Yield", "score": radar_scores.get("round_trip_efficiency", 80), "benchmark": 75},
            {"dimension": "CapEx Competitiveness", "score": radar_scores.get("capex_competitiveness", 80), "benchmark": 70},
            {"dimension": "Scalability & Duration", "score": radar_scores.get("duration_scalability", 80), "benchmark": 65},
            {"dimension": "TRL / Tech Maturity", "score": radar_scores.get("technology_maturity", 70), "benchmark": 80},
            {"dimension": "Domestic Supply Chain", "score": radar_scores.get("domestic_supply_chain", 80), "benchmark": 60},
            {"dimension": "Siting & Permitting", "score": radar_scores.get("siting_permitting_ease", 80), "benchmark": 70}
        ]

        trl_progression = [
            {"stage": "TRL 1-3: Basic Principles & Lab Feasibility", "active": tech_row.trl_current >= 3, "description": "Proof of concept demonstrated in lab."},
            {"stage": "TRL 4-6: Subsystem Validation & Pilot", "active": tech_row.trl_current >= 6, "description": "Engineered prototype tested in operational environment."},
            {"stage": "TRL 7-8: Full-Scale Field Demonstration", "active": tech_row.trl_current >= 8, "description": "Commercial-scale unit operating in utility/industrial setting."},
            {"stage": "TRL 9: Commercial Deployment", "active": tech_row.trl_current >= 9, "description": "Standardized serial factory manufacturing and global bankability."}
        ]

        reg_info = TECHNOLOGY_REGISTRY.get(tech_row.id, {})
        fuel_profile = reg_info.get("fuel_profile")
        if hasattr(tech_row, 'fuel_profile_json') and tech_row.fuel_profile_json:
            try:
                fuel_profile = json.loads(tech_row.fuel_profile_json)
            except Exception:
                pass

        # Subsystems from relational table
        subsystems = []
        if tech_row.subsystems:
            for s in tech_row.subsystems:
                subsystems.append({
                    "id": s.node_id,
                    "name": s.name,
                    "category": s.category,
                    "x": s.x,
                    "y": s.y,
                    "icon": s.icon,
                    "summary": s.summary,
                    "operatingValue": s.operating_value,
                    "materials": s.materials,
                    "failureMode": s.failure_mode,
                    "frontierBottleneck": s.frontier_bottleneck,
                    "activeResearch": s.active_research
                })

        return {
            "id": tech_row.id,
            "name": tech_row.name,
            "category_id": tech_row.category_id,
            "category_name": tech_row.category.name if tech_row.category else tech_row.category_id,
            "headline": tech_row.headline,
            "trl_current": tech_row.trl_current,
            "trl_target": tech_row.trl_target,
            "sector": tech_row.sector,
            "fuel_vector": tech_row.fuel_vector,
            "vector_type": getattr(tech_row, 'vector_type', None) or reg_info.get('vector_type', 'hardware'),
            "fuel_profile": fuel_profile,
            "keywords": keywords,
            "plain_english": {
                "what_is_it": tech_row.plain_what_is_it,
                "how_it_works": tech_row.plain_how_it_works,
                "why_it_matters": tech_row.plain_why_it_matters,
                "macro_problem_solved": tech_row.plain_macro_problem_solved
            },
            "evolution": {
                "past": tech_row.evolution_past,
                "present": tech_row.evolution_present,
                "future": tech_row.evolution_future
            },
            "frontier": {
                "moonshot_goal": tech_row.moonshot_goal,
                "kpis": kpis,
                "bottlenecks": bottlenecks,
                "active_research_tracks": active_research
            },
            "cost_performance": cost_perf,
            "radar_scores": radar_scores,
            "radar_data": radar_data,
            "trl_progression": trl_progression,
            "subsystems": subsystems,
            "trade_offs": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "competing_technologies": competing_techs
            },
            "evidence": evidence
        }

    # Fallback to in-memory definition
    tech_def = TECHNOLOGY_REGISTRY.get(tech_id)
    if not tech_def:
        return None

    evidence = get_live_technology_evidence(db, tech_id)
    cost_performance = synthesize_cost_performance(tech_id, tech_def)
    
    radar_scores = tech_def.get("radar_scores", {
        "round_trip_efficiency": 80,
        "capex_competitiveness": 80,
        "duration_scalability": 80,
        "technology_maturity": 70,
        "domestic_supply_chain": 80,
        "siting_permitting_ease": 80
    })

    radar_data = [
        {"dimension": "Efficiency / Yield", "score": radar_scores.get("round_trip_efficiency", 80), "benchmark": 75},
        {"dimension": "CapEx Competitiveness", "score": radar_scores.get("capex_competitiveness", 80), "benchmark": 70},
        {"dimension": "Scalability & Duration", "score": radar_scores.get("duration_scalability", 80), "benchmark": 65},
        {"dimension": "TRL / Tech Maturity", "score": radar_scores.get("technology_maturity", 70), "benchmark": 80},
        {"dimension": "Domestic Supply Chain", "score": radar_scores.get("domestic_supply_chain", 80), "benchmark": 60},
        {"dimension": "Siting & Permitting", "score": radar_scores.get("siting_permitting_ease", 80), "benchmark": 70}
    ]

    trl_progression = [
        {"stage": "TRL 1-3: Basic Principles & Lab Feasibility", "active": tech_def["trl_current"] >= 3, "description": "Proof of concept demonstrated in lab."},
        {"stage": "TRL 4-6: Subsystem Validation & Pilot", "active": tech_def["trl_current"] >= 6, "description": "Engineered prototype tested in operational environment."},
        {"stage": "TRL 7-8: Full-Scale Field Demonstration", "active": tech_def["trl_current"] >= 8, "description": "Commercial-scale unit operating in utility/industrial setting."},
        {"stage": "TRL 9: Commercial Deployment", "active": tech_def["trl_current"] >= 9, "description": "Standardized serial factory manufacturing and global bankability."}
    ]

    return {
        **tech_def,
        "cost_performance": cost_performance,
        "radar_data": radar_data,
        "trl_progression": trl_progression,
        "evidence": evidence
    }

# ==============================================================================
# 5. OPENAI API TECHNICAL SPECIALIST & CACHING ENGINE
# ==============================================================================

def get_or_generate_tech_insights(
    db: Session,
    tech_id: str,
    custom_question: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """Generates on-demand technical diligence and frontier Q&A with disk caching."""
    dossier = get_technology_dossier(db, tech_id)
    if not dossier:
        raise ValueError(f"Technology ID '{tech_id}' not found in master registry.")

    key_to_use = api_key or getattr(settings, "openai_api_key", None) or os.environ.get("OPENAI_API_KEY", "")
    model_to_use = model_name or getattr(settings, "default_llm_model", "gpt-4o-mini")

    q_text = custom_question.strip() if custom_question else "Executive Technology Diligence & Frontier Synthesis"
    cache_key = hashlib.sha256(f"{tech_id}:{q_text}:{model_to_use}".encode("utf-8")).hexdigest()
    cache_file = CACHE_DIR / f"{cache_key}.json"

    if not force_refresh and cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
                cached["cached"] = True
                return cached
        except Exception as e:
            logger.warning(f"Error reading tech reference cache: {e}")

    if key_to_use and len(key_to_use.strip()) > 10:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key_to_use.strip())

            system_prompt = (
                "You are the Chief Scientist and Lead Technology Due Diligence Officer at Energy Innovation Terminal. "
                "Provide deep, rigorous, quantitative engineering evaluations for energy technologies. "
                "Always return strict JSON conforming to the requested schema."
            )

            user_prompt = f"""Analyze the following technology and answer the diligence inquiry.

TECHNOLOGY METADATA:
Name: {dossier['name']}
Sector: {dossier['category_name']}
Current TRL: {dossier['trl_current']} -> Target TRL: {dossier['trl_target']}
Headline: {dossier['headline']}

MECHANICAL PRINCIPLES:
What is it: {dossier['plain_english']['what_is_it']}
How it works: {dossier['plain_english']['how_it_works']}
Why it matters: {dossier['plain_english']['why_it_matters']}

INNOVATION FRONTIER:
Moonshot Goal: {dossier['frontier']['moonshot_goal']}
Critical Bottlenecks: {json.dumps(dossier['frontier']['bottlenecks'])}
Active Research Tracks: {json.dumps(dossier['frontier']['active_research_tracks'])}

DATABASE EVIDENCE:
Tracked Grant Capital: {dossier['evidence'].get('tracked_capital_fmt', '$0M')} across {dossier['evidence'].get('award_count', 0)} projects.
Active Solicitations: {dossier['evidence'].get('active_solicitations_count', 0)} open FOAs.

USER INQUIRY:
"{q_text}"

Return a JSON object with this exact structure:
{{
  "technology_id": "{tech_id}",
  "technology_name": "{dossier['name']}",
  "question": "{q_text}",
  "executive_synthesis": "Crisp 2-3 paragraph plain-English executive summary addressing the question.",
  "engineering_deep_dive": "Deep thermodynamic/materials/physics breakdown with specific performance numbers, degradation rates, and trade-offs.",
  "frontier_research_tracks": ["Research Track 1", "Research Track 2", "Research Track 3"],
  "strategic_recommendations": ["Recommendation for grant seekers", "Recommendation for program managers", "Recommendation for investors"],
  "model_used": "{model_to_use}"
}}"""

            response = client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2500
            )

            result_str = response.choices[0].message.content
            parsed = json.loads(result_str)
            parsed["cached"] = False
            parsed["model_used"] = model_to_use

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2)

            return parsed
        except Exception as e:
            logger.error(f"OpenAI API invocation failed for {tech_id}: {e}. Using deterministic synthesis.")

    # High-Fidelity Deterministic Fallback Synthesis
    fallback = {
        "technology_id": tech_id,
        "technology_name": dossier["name"],
        "question": q_text,
        "executive_synthesis": (
            f"{dossier['name']} represents a foundational clean tech capability within the {dossier['category_name']} sector. "
            f"Currently positioned at TRL {dossier['trl_current']}, it targets commercial scale at TRL {dossier['trl_target']}. "
            f"{dossier['plain_english']['why_it_matters']} The platform database tracks {dossier['evidence'].get('tracked_capital_fmt', '$0M')} "
            f"in verified grant commitments across {dossier['evidence'].get('award_count', 0)} competitive awards."
        ),
        "engineering_deep_dive": (
            f"Mechanically, {dossier['plain_english']['how_it_works']}\n\n"
            f"The primary engineering hurdle is addressing: {dossier['frontier']['bottlenecks'][0] if dossier['frontier']['bottlenecks'] else 'materials degradation'}. "
            f"Target milestones include reaching {dossier['frontier']['kpis'][0]['name']}: {dossier['frontier']['kpis'][0]['target_2030']}."
        ),
        "frontier_research_tracks": dossier["frontier"]["active_research_tracks"],
        "strategic_recommendations": [
            f"Grant Applicants: Align proposal milestone architectures with {dossier['frontier']['kpis'][0]['name']} targets.",
            "Program Directors: Structure stage-gated solicitations addressing materials durability under continuous cycling.",
            f"Capital Allocators: Benchmark unit CapEx against competing alternatives ({', '.join(dossier['trade_offs']['competing_technologies'][:2])})."
        ],
        "model_used": "Deterministic Diligence Engine",
        "cached": False
    }

    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(fallback, f, indent=2)

    return fallback


# ==============================================================================
# 6. CROSS-TECHNOLOGY COMPARATIVE, FUELS MATRIX & FRONTIER DATA SERVICES
# ==============================================================================

def get_technology_subsystems(db: Session, tech_id: str) -> List[Dict[str, Any]]:
    """Fetch subsystem architecture nodes for a given technology from PostgreSQL."""
    tech_row = db.query(Technology).filter(Technology.id == tech_id).first() if db else None
    if tech_row and tech_row.subsystems:
        return [
            {
                "id": s.node_id,
                "name": s.name,
                "category": s.category,
                "x": s.x,
                "y": s.y,
                "icon": s.icon,
                "summary": s.summary,
                "operatingValue": s.operating_value,
                "materials": s.materials,
                "failureMode": s.failure_mode,
                "frontierBottleneck": s.frontier_bottleneck,
                "activeResearch": s.active_research
            }
            for s in tech_row.subsystems
        ]
    return []


def get_comparative_technologies_matrix(db: Session, tech_ids: List[str]) -> Dict[str, Any]:
    """Builds a side-by-side multi-technology comparison matrix across 2-4 technologies."""
    items = []
    for tid in tech_ids[:4]:
        dossier = get_technology_dossier(db, tid)
        if dossier:
            items.append(dossier)
    return {
        "compared_count": len(items),
        "technologies": items
    }


def get_fuel_pathways_matrix(db: Session) -> List[Dict[str, Any]]:
    """Returns all zero-carbon fuels and molecular carriers with Carbon Intensity and density metrics."""
    results = []
    all_techs = db.query(Technology).all() if db else []
    if not all_techs:
        all_techs = [t for t in TECHNOLOGY_REGISTRY.values() if t.get("vector_type") == "fuel_carrier" or t.get("fuel_profile")]

    for t in all_techs:
        is_orm = hasattr(t, 'fuel_vector')
        t_id = t.id if is_orm else t['id']
        t_name = t.name if is_orm else t['name']
        t_vector = t.fuel_vector if is_orm else t.get('fuel_vector')
        v_type = getattr(t, 'vector_type', None) or (t.get('vector_type') if not is_orm else 'hardware')
        reg_t = TECHNOLOGY_REGISTRY.get(t_id, {})
        
        fp = None
        if is_orm and hasattr(t, 'fuel_profile_json') and t.fuel_profile_json:
            try:
                fp = json.loads(t.fuel_profile_json)
            except Exception:
                pass
        if not fp:
            fp = reg_t.get("fuel_profile")
        
        if v_type == 'fuel_carrier' or fp:
            cat_name = t.category.name if (is_orm and t.category) else reg_t.get('category_name', 'Clean Fuels')
            trl_cur = t.trl_current if is_orm else t.get('trl_current', 7)
            trl_tgt = t.trl_target if is_orm else t.get('trl_target', 9)
            results.append({
                "id": t_id,
                "name": t_name,
                "carrier_name": fp.get("carrier_name", t_vector) if fp else t_vector,
                "category_name": cat_name,
                "chemical_formula": fp.get("chemical_formula", "N/A") if fp else "N/A",
                "carbon_intensity_ci": fp.get("carbon_intensity_ci", "Low/Zero CI") if fp else "Low/Zero CI",
                "energy_density_gravimetric": fp.get("energy_density_gravimetric", "N/A") if fp else "N/A",
                "energy_density_volumetric": fp.get("energy_density_volumetric", "N/A") if fp else "N/A",
                "feedstock_pathway": fp.get("feedstock_pathway", "Renewable & Waste") if fp else "Renewable & Waste",
                "drop_in_compatibility": fp.get("drop_in_compatibility", "Standard") if fp else "Standard",
                "policy_incentives": fp.get("policy_incentives", "IRA 45V / 45Z / LCFS") if fp else "IRA 45V / 45Z / LCFS",
                "trl_current": trl_cur,
                "trl_target": trl_tgt,
                "headline": t.headline if is_orm else t.get('headline', '')
            })
    return results


_FRONTIER_MATRIX_CACHE: Optional[List[Dict[str, Any]]] = None

def get_frontier_matrix(db: Optional[Session] = None, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Returns all 36 technologies with normalized metrics for scatter/quadrant analysis."""
    global _FRONTIER_MATRIX_CACHE
    if _FRONTIER_MATRIX_CACHE is not None and not force_refresh:
        return _FRONTIER_MATRIX_CACHE

    matrix_file = CACHE_DIR / "frontier_matrix.json"
    if not force_refresh and matrix_file.exists():
        try:
            with open(matrix_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if cached:
                    _FRONTIER_MATRIX_CACHE = cached
                    return cached
        except Exception:
            pass

    results = []
    tech_rows = []
    if db:
        try:
            tech_rows = db.query(Technology).all()
        except Exception as e:
            logger.warning(f"Error querying Technology rows for frontier matrix: {e}")
            try:
                db.rollback()
            except Exception:
                pass

    if not tech_rows:
        tech_rows = [type('TechObj', (), {
            'id': k,
            'name': v['name'],
            'category_id': v['category_id'],
            'category': type('CatObj', (), {'name': v.get('category_name', v['category_id'])}),
            'sector': v.get('sector', 'Clean Tech'),
            'fuel_vector': v.get('fuel_vector', 'Electricity'),
            'vector_type': v.get('vector_type', 'hardware'),
            'trl_current': v.get('trl_current', 6),
            'trl_target': v.get('trl_target', 9),
            'bottlenecks_json': json.dumps(v.get('frontier', {}).get('bottlenecks', [])),
            'moonshot_goal': v.get('frontier', {}).get('moonshot_goal', '')
        })() for k, v in TECHNOLOGY_REGISTRY.items()]

    for t in tech_rows:
        reg_t = TECHNOLOGY_REGISTRY.get(t.id, {})
        cost_perf = synthesize_cost_performance(t.id, reg_t)
        cm = cost_perf.get("cost_metric", {})
        pm = cost_perf.get("performance_metric", {})
        
        red_str = str(cm.get("reduction_pct", "-50%")).replace("%", "").replace("-", "").replace("+", "").strip()
        try:
            red_pct_num = float(red_str)
        except Exception:
            red_pct_num = 50.0

        imp_str = str(pm.get("improvement_pct", "+50%")).replace("%", "").replace("-", "").replace("+", "").replace(",", "").strip()
        try:
            imp_pct_num = float(imp_str)
        except Exception:
            imp_pct_num = 50.0

        evidence = get_live_technology_evidence(db, t.id) if db else {}
        bottlenecks = json.loads(getattr(t, 'bottlenecks_json', None) or "[]")
        primary_bn = bottlenecks[0] if bottlenecks else "Materials durability"

        results.append({
            "id": t.id,
            "name": t.name,
            "category_id": t.category_id,
            "category_name": t.category.name if t.category else t.category_id,
            "sector": t.sector,
            "fuel_vector": t.fuel_vector,
            "vector_type": getattr(t, 'vector_type', None) or reg_t.get('vector_type', 'hardware'),
            "trl_current": t.trl_current,
            "trl_target": t.trl_target,
            "cost_metric_name": cm.get("name", "CapEx"),
            "cost_baseline_fmt": cm.get("baseline_fmt", "$1,000 / unit"),
            "cost_target_2030_fmt": cm.get("target_2030_fmt", "$350 / unit"),
            "cost_reduction_pct_num": red_pct_num,
            "cost_reduction_pct_str": cm.get("reduction_pct", "-50%"),
            "perf_metric_name": pm.get("name", "Efficiency"),
            "perf_baseline_fmt": pm.get("baseline_fmt", "65%"),
            "perf_target_2030_fmt": pm.get("target_2030_fmt", "88%"),
            "perf_improvement_pct_num": imp_pct_num,
            "perf_improvement_pct_str": pm.get("improvement_pct", "+50%"),
            "learning_rate": cost_perf.get("learning_rate", "15% per doubling"),
            "earthshot_goal": cost_perf.get("earthshot_goal", "DOE Decarbonization Earthshot"),
            "tracked_capital_usd": evidence.get("tracked_capital_usd", 0.0),
            "tracked_capital_fmt": evidence.get("tracked_capital_fmt", "$0M"),
            "award_count": evidence.get("award_count", 0),
            "active_solicitations_count": evidence.get("active_solicitations_count", 0),
            "primary_bottleneck": primary_bn,
            "moonshot_goal": t.moonshot_goal
        })
    if results:
        _FRONTIER_MATRIX_CACHE = results
        try:
            with open(matrix_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        except Exception:
            pass
    return results


# Public API Aliases
get_all_technologies_summary = get_technologies_list
synthesize_technology_insights = get_or_generate_tech_insights

