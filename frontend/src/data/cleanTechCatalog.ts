export interface CleanTechItem {
  id: string;
  name: string;
  shortLabel: string;
  sector: string;
  description: string;
  defaultTrlMin: number;
  defaultTrlMax: number;
  defaultBottlenecks: string;
}

export const CLEAN_ENERGY_SECTORS = [
  'Long-Duration Energy Storage (LDES) & Advanced Batteries',
  'Clean Hydrogen, Green Ammonia & Sustainable E-Fuels',
  'Advanced Nuclear, SMRs & Fusion Energy',
  'Industrial Decarbonization & Clean Process Heat',
  'Grid Modernization, Power Electronics & Transmission',
  'Carbon Management, Direct Air Capture & Point-Source CDR',
  'Clean Buildings, Thermal Energy Networks & Heat Pumps',
  'Heavy Transportation, Megawatt EV & Maritime / Aviation',
  'Advanced Renewable Generation: Solar & Wind',
  'Geothermal, Hydrokinetic & Ocean Energy',
  'Circular Economy, Battery Recycling & Critical Minerals',
  'Bioenergy, RNG & Methane Abatement'
] as const;

export const CLEAN_ENERGY_TECHNOLOGIES: CleanTechItem[] = [
  // 1. Long-Duration Energy Storage (LDES) & Advanced Batteries (10)
  {
    id: 'iron_air_battery',
    name: 'Iron-Air Long-Duration Battery (100-Hour Discharge)',
    shortLabel: 'Iron-Air Battery',
    sector: 'Long-Duration Energy Storage (LDES) & Advanced Batteries',
    description: 'Multi-day multi-diurnal iron-air redox storage chemistry for 100hr grid dispatch.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Air-breathing cathode degradation during multi-day continuous discharge; Parasitic hydrogen evolution reaction at iron anode; Balance-of-plant thermal management in sub-zero winter extremes'
  },
  {
    id: 'vanadium_flow_battery',
    name: 'Vanadium Redox Flow Battery (VRFB)',
    shortLabel: 'Vanadium Flow Battery',
    sector: 'Long-Duration Energy Storage (LDES) & Advanced Batteries',
    description: 'Decoupled energy-power liquid electrolyte flow storage for 8-24hr industrial microgrids.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Vanadium precipitation at elevated temperatures (>40°C); Membrane crossover of vanadium species; Stack pressure drop and shunt current losses'
  },
  {
    id: 'zinc_flow_battery',
    name: 'Zinc-Bromine & Zinc-Iron Flow Batteries',
    shortLabel: 'Zinc Flow Battery',
    sector: 'Long-Duration Energy Storage (LDES) & Advanced Batteries',
    description: 'Low-cost abundant transition metal flow batteries for long-duration bulk storage.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Zinc dendrite formation and uneven electrodeposition; Bromine vapor crossover and complexing agent stability; Reversible stack degradation under deep cycling'
  },
  {
    id: 'all_iron_flow_battery',
    name: 'All-Iron Flow Battery (Non-Toxic Electrolyte)',
    shortLabel: 'All-Iron Flow Battery',
    sector: 'Long-Duration Energy Storage (LDES) & Advanced Batteries',
    description: 'Zero-toxicity iron chloride flow chemistry for urban and environmentally sensitive sites.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Iron plating morphology control and edge buildup; Slurry handling and pump hydraulic parasitic losses; High round-trip efficiency optimization'
  },
  {
    id: 'solid_state_battery',
    name: 'Solid-State Lithium Metal Battery (Sulfide / Ceramic)',
    shortLabel: 'Solid-State Li Battery',
    sector: 'Long-Duration Energy Storage (LDES) & Advanced Batteries',
    description: 'High energy density solid electrolyte batteries eliminating flammable liquid solvents.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Solid electrolyte interphase (SEI) impedance growth; Dendrite penetration through ceramic grain boundaries; High-pressure stack packaging and cell volume expansion'
  },
  {
    id: 'sodium_ion_battery',
    name: 'Sodium-Ion Battery (Prussian White / Layered Oxide)',
    shortLabel: 'Sodium-Ion Battery',
    sector: 'Long-Duration Energy Storage (LDES) & Advanced Batteries',
    description: 'Lithium-free sodium chemistry for low-cost stationary storage and light mobility.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Cathode moisture sensitivity and transition metal dissolution; Hard carbon anode first-cycle coulombic efficiency; High-rate capacity retention at low temperatures'
  },
  {
    id: 'liquid_metal_battery',
    name: 'Liquid Metal Battery (High-Temperature Sb-Pb-Bi)',
    shortLabel: 'Liquid Metal Battery',
    sector: 'Long-Duration Energy Storage (LDES) & Advanced Batteries',
    description: 'Self-assembling molten metal-salt layers operating at 450°C with zero electrode degradation.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'High operating temperature thermal insulation (450°C+); Interfacial mass transfer resistance; Long-term corrosion of container ceramics and feedthrough seals'
  },
  {
    id: 'compressed_air_storage',
    name: 'Compressed Air Energy Storage (Adiabatic CAES)',
    shortLabel: 'Adiabatic CAES',
    sector: 'Long-Duration Energy Storage (LDES) & Advanced Batteries',
    description: 'Underground cavern isothermal/adiabatic pneumatic storage with thermal recovery.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Underground cavern geomechanical sealing under cyclic pressure; Thermal energy storage (TES) round-trip heat recovery efficiency; High-pressure expander turbo-machinery efficiency'
  },
  {
    id: 'liquid_air_storage',
    name: 'Liquid Air Energy Storage (Cryogenic LAES)',
    shortLabel: 'Cryogenic LAES',
    sector: 'Long-Duration Energy Storage (LDES) & Advanced Batteries',
    description: 'Cryogenic liquefaction and expansion of ambient air for locational unconstrained storage.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Cryogenic cold-recycle heat exchanger exergy losses; High-efficiency air liquefaction integration; Rapid transient startup time for grid ancillary support'
  },
  {
    id: 'pumped_hydro_closed_loop',
    name: 'Gravity & Pumped Storage Hydro (Closed-Loop / Underground)',
    shortLabel: 'Closed-Loop Pumped Hydro',
    sector: 'Long-Duration Energy Storage (LDES) & Advanced Batteries',
    description: 'Off-river closed-loop and modular civil gravity storage for decadal grid reliability.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Subsurface cavern excavation cost and geotechnical stability; High-head reversible pump-turbine cavitation; Civil engineering CapEx minimization'
  },

  // 2. Clean Hydrogen, Green Ammonia & Sustainable E-Fuels (10)
  {
    id: 'soec_electrolyzer',
    name: 'Solid Oxide Electrolyzer Cell (SOEC - High-Temp High-Efficiency)',
    shortLabel: 'SOEC Electrolyzer',
    sector: 'Clean Hydrogen, Green Ammonia & Sustainable E-Fuels',
    description: 'High-temperature (700-850°C) steam electrolysis for high electrical efficiency H2 synthesis.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Chromium poisoning at oxygen electrode under 750°C operation; Stack seal degradation and thermal cycling mechanical stresses; Catalyst coating manufacturing yield and balance-of-plant CapEx'
  },
  {
    id: 'pem_electrolyzer',
    name: 'Proton Exchange Membrane (PEM) Electrolyzer (Ir-Lean Catalyst)',
    shortLabel: 'PEM Electrolyzer',
    sector: 'Clean Hydrogen, Green Ammonia & Sustainable E-Fuels',
    description: 'Dynamic fast-responding water electrolysis operating at high current densities.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Iridium catalyst loading reduction without cell voltage penalty; Titanium bipolar plate protective coating cost; Membrane thinning gas crossover under high differential pressure (30+ bar)'
  },
  {
    id: 'aem_electrolyzer',
    name: 'Anion Exchange Membrane (AEM) Electrolyzer (Noble-Metal-Free)',
    shortLabel: 'AEM Electrolyzer',
    sector: 'Clean Hydrogen, Green Ammonia & Sustainable E-Fuels',
    description: 'Alkaline membrane electrolysis combining PEM flexibility with low-cost transition metal catalysts.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Polymer membrane alkaline chemical stability above 60°C; Non-precious metal catalyst (Ni-Fe) passivation; Carbonate poisoning from trace atmospheric CO2'
  },
  {
    id: 'alkaline_electrolyzer',
    name: 'Alkaline Water Electrolyzer (Advanced High-Pressure Zero-Gap)',
    shortLabel: 'Alkaline Electrolyzer',
    sector: 'Clean Hydrogen, Green Ammonia & Sustainable E-Fuels',
    description: 'Mature zero-gap pressurized alkaline electrolysis for gigawatt-scale hydrogen hubs.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Gas purity crossover at low turn-down ratios (<20%); Zero-gap separator durability under intermittent renewable power cycling; High current density operation without overheating'
  },
  {
    id: 'green_ammonia',
    name: 'Green Ammonia Synthesis (Low-Pressure / Electrocatalytic)',
    shortLabel: 'Green Ammonia',
    sector: 'Clean Hydrogen, Green Ammonia & Sustainable E-Fuels',
    description: 'Direct electrocatalytic or low-pressure Haber-Bosch green ammonia for maritime fuel & fertilizer.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Catalyst activity and N2 dissociation at moderate temperatures (<350°C); Ammonia separation and unreacted syngas loop recirculation; Integration with variable hydrogen feedstocks'
  },
  {
    id: 'sustainable_aviation_fuel',
    name: 'Sustainable Aviation Fuel (SAF - Alcohol-to-Jet / Fischer-Tropsch PtL)',
    shortLabel: 'Sustainable Aviation Fuel (SAF)',
    sector: 'Clean Hydrogen, Green Ammonia & Sustainable E-Fuels',
    description: 'Drop-in synthetic paraffinic kerosene from clean hydrogen, biogenic carbon, and alcohol.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Oligomerization and hydroprocessing catalyst selectivity to jet-range aromatics; Syngas clean-up and carbon monoxide conversion efficiency; ASTM D7566 certification and aromatics blending ratio'
  },
  {
    id: 'emethanol_efuels',
    name: 'E-Methanol & Synthetic E-Fuels Synthesis (CO2 + Green H2)',
    shortLabel: 'E-Methanol & E-Fuels',
    sector: 'Clean Hydrogen, Green Ammonia & Sustainable E-Fuels',
    description: 'Catalytic hydrogenation of captured CO2 into drop-in marine e-methanol and hydrocarbons.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Highly active and selective CO2 hydrogenation catalysts; Exothermic reactor heat management and steam generation; Byproduct water separation and catalyst sintering resistance'
  },
  {
    id: 'lohc_hydrogen_carriers',
    name: 'Liquid Organic Hydrogen Carriers (LOHC - Toluene/MCH & DBT)',
    shortLabel: 'LOHC Hydrogen Carriers',
    sector: 'Clean Hydrogen, Green Ammonia & Sustainable E-Fuels',
    description: 'Ambient liquid chemical hydrogen carriers for long-distance transport in existing petroleum assets.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Dehydrogenation endothermic heat delivery at dehydrogenator reactor; Catalyst deactivation and carrier thermal degradation; Round-trip energy efficiency penalty'
  },
  {
    id: 'geologic_hydrogen',
    name: 'Geologic / Natural Gold Hydrogen Exploration & Extraction',
    shortLabel: 'Geologic Gold Hydrogen',
    sector: 'Clean Hydrogen, Green Ammonia & Sustainable E-Fuels',
    description: 'Subsurface serpentinization-generated primary hydrogen extraction directly from geologic strata.',
    defaultTrlMin: 3,
    defaultTrlMax: 6,
    defaultBottlenecks: 'Subsurface sweet spot reservoir identification and seismic imaging; Hydrogen-permeable extraction wellbore completion metallurgy; Continuous downhole hydrogen flux characterization'
  },
  {
    id: 'methane_pyrolysis_turquoise_h2',
    name: 'Methane Pyrolysis & Turquoise Hydrogen (Solid Carbon Co-Product)',
    shortLabel: 'Methane Pyrolysis',
    sector: 'Clean Hydrogen, Green Ammonia & Sustainable E-Fuels',
    description: 'Molten metal thermal decomposition of methane into clean H2 and valuable solid carbon black.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Molten metal/salt reactor carbon buildup and clogging; Solid carbon black purity and morphological value for industrial off-take; Catalyst fouling and high-temperature heat transfer'
  },

  // 3. Advanced Nuclear, SMRs & Fusion Energy (8)
  {
    id: 'htgr_smr',
    name: 'High-Temperature Gas-Cooled Reactor (HTGR SMR for Industrial Heat)',
    shortLabel: 'HTGR Industrial SMR',
    sector: 'Advanced Nuclear, SMRs & Fusion Energy',
    description: 'High-temperature helium-cooled TRISO reactor generating 750-950°C process heat for industry.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'High-temperature intermediate heat exchanger alloy corrosion; Secondary steam loop integration with industrial chemical manufacturing; TRISO fuel manufacturing qualification and qualification data'
  },
  {
    id: 'molten_salt_reactor',
    name: 'Molten Salt Reactor (MSR - Liquid Fluoride / Chloride Fuel)',
    shortLabel: 'Molten Salt Reactor (MSR)',
    sector: 'Advanced Nuclear, SMRs & Fusion Energy',
    description: 'Liquid fueled reactor with walk-away passive safety and online fission product management.',
    defaultTrlMin: 3,
    defaultTrlMax: 6,
    defaultBottlenecks: 'High-temperature molten salt corrosion and structural nickel alloy embrittlement; Noble metal fission product extraction; Online fuel salt chemistry control and safeguards'
  },
  {
    id: 'sodium_fast_reactor',
    name: 'Sodium-Cooled Fast Reactor (SFR - High Burnup Waste Transmutation)',
    shortLabel: 'Sodium-Cooled Fast Reactor',
    sector: 'Advanced Nuclear, SMRs & Fusion Energy',
    description: 'Fast neutron liquid metal reactor for high fuel utilization and spent fuel recycling.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Liquid sodium-water steam generator leak detection and isolation; In-service inspection techniques in opaque liquid sodium; Fast neutron damage to core structural materials'
  },
  {
    id: 'integral_pwr_smr',
    name: 'Light Water Small Modular Reactor (Integral PWR SMR)',
    shortLabel: 'Integral PWR SMR',
    sector: 'Advanced Nuclear, SMRs & Fusion Energy',
    description: 'Factory-fabricated modular light water reactor for baseload utility peaker replacement.',
    defaultTrlMin: 6,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Integral steam generator flow-induced vibration; Natural circulation passive decay heat removal in compact vessel; Factory fabrication modular assembly tolerances'
  },
  {
    id: 'nuclear_microreactor',
    name: 'Microreactors for Remote & Defense Microgrids (1-20 MWe)',
    shortLabel: 'Nuclear Microreactor',
    sector: 'Advanced Nuclear, SMRs & Fusion Energy',
    description: 'Truck-transportable solid-core heat pipe microreactors for resilient islanded grids.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'High-temperature heat pipe core thermal transfer limits; Autonomous load-following control algorithms; Transportation package shock and vibration qualification'
  },
  {
    id: 'hts_tokamak_fusion',
    name: 'Magnetic Confinement Fusion (High-Field HTS Tokamak)',
    shortLabel: 'HTS Tokamak Fusion',
    sector: 'Advanced Nuclear, SMRs & Fusion Energy',
    description: 'Compact high-field fusion utilizing rare-earth barium copper oxide (REBCO) superconductors.',
    defaultTrlMin: 3,
    defaultTrlMax: 6,
    defaultBottlenecks: 'High-temperature superconducting (HTS) tape joint resistance under high magnetic field; Divertor plasma-facing component heat flux handling (>10 MW/m²); Tritium breeding and extraction ratio in blanket'
  },
  {
    id: 'magneto_inertial_fusion',
    name: 'Inertial Confinement & Magneto-Inertial Fusion Systems',
    shortLabel: 'Magneto-Inertial Fusion',
    sector: 'Advanced Nuclear, SMRs & Fusion Energy',
    description: 'Pulsed magnetic compression of magnetized plasma targets for commercial fusion power.',
    defaultTrlMin: 3,
    defaultTrlMax: 5,
    defaultBottlenecks: 'High-repetition pulsed power switch durability; Plasma compression stability and Rayleigh-Taylor instability mitigation; First-wall neutron damage and shielding'
  },
  {
    id: 'triso_fuel_fabrication',
    name: 'TRISO Coated Particle Nuclear Fuel Manufacturing',
    shortLabel: 'TRISO Fuel Manufacturing',
    sector: 'Advanced Nuclear, SMRs & Fusion Energy',
    description: 'Tri-structural isotropic particle fuel capable of withstanding temperatures >1600°C without melting.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Silicon carbide layer uniformity and defect minimization; Uranium kernel sol-gel manufacturing yield; Fission product retention verification under 1600°C accident conditions'
  },

  // 4. Industrial Decarbonization & Clean Process Heat (10)
  {
    id: 'industrial_heat_pump_steam',
    name: 'Industrial High-Temperature Heat Pump (Steam Generating 120-200°C)',
    shortLabel: 'Industrial Heat Pump (150C+)',
    sector: 'Industrial Decarbonization & Clean Process Heat',
    description: 'Electric heat pumps upgrading industrial low-grade waste heat into process steam.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'High-temperature refrigerant thermodynamic stability and low-GWP compliance; Compressor lubrication and seal integrity at 160°C+ discharge; Integration with variable batch industrial steam cycles'
  },
  {
    id: 'hydrogen_dri_steel',
    name: 'Hydrogen Direct Reduced Iron (H2-DRI for Green Steelmaking)',
    shortLabel: 'Green Steel H2-DRI',
    sector: 'Industrial Decarbonization & Clean Process Heat',
    description: '100% green hydrogen reduction of iron ore in shaft furnaces coupled to electric arc furnaces.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Shaft furnace gas flow aerodynamics with 100% H2; Pellets sticking and degradation in reduction zone; Highly endothermic reduction heat supply'
  },
  {
    id: 'molten_oxide_electrolysis_steel',
    name: 'Molten Oxide Electrolysis (MOE for Zero-Carbon Iron Ore Reduction)',
    shortLabel: 'Molten Oxide Electrolysis (MOE)',
    sector: 'Industrial Decarbonization & Clean Process Heat',
    description: 'Direct electrochemical reduction of iron ore at 1600°C producing pure liquid metal and O2.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Inert anode stability in 1600°C molten iron silicate electrolyte; Refractory lining corrosion from molten slag; Electrical busbar heat loss and current distribution'
  },
  {
    id: 'low_carbon_calcined_clay_cement',
    name: 'Low-Carbon Supplementary Cementitious Materials (SCMs) & Calcined Clays',
    shortLabel: 'Low-Carbon SCMs & Clays',
    sector: 'Industrial Decarbonization & Clean Process Heat',
    description: 'LC3 cement formulation substituting up to 50% clinker with calcined clay and limestone.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Calcined clay color and reactivity activation kinetics; Supplementary cementitious material rheological slump flow; Early-age compressive strength development in concrete'
  },
  {
    id: 'electrochemical_clinker_alternative',
    name: 'Electrochemical & Bio-Based Cement Clinker Replacement',
    shortLabel: 'Clinkerless Bio-Cement',
    sector: 'Industrial Decarbonization & Clean Process Heat',
    description: 'Zero-clinker structural binders synthesized through ambient mineral carbonation & bio-enzymes.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Low-temperature chemical activation kinetics; Long-term durability and carbonation resistance under ASTM C1157; Feedstock availability and regional supply chain logistics'
  },
  {
    id: 'high_temp_thermal_storage_battery',
    name: 'Thermal Energy Storage (Brick / Molten Salt Heat Battery 1000°C+)',
    shortLabel: 'Thermal Heat Battery (1000C+)',
    sector: 'Industrial Decarbonization & Clean Process Heat',
    description: 'Solid refractory bricks or molten metals storing low-cost electricity as 1000°C+ continuous heat.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'High-temperature radiant heat transfer modeling; Refractory ceramic block thermal stress cracking during fast cycling; High-efficiency steam generator integration'
  },
  {
    id: 'industrial_microwave_rf_heating',
    name: 'Industrial Microwave & Radiofrequency Dielectric Heating',
    shortLabel: 'Industrial Dielectric Heating',
    sector: 'Industrial Decarbonization & Clean Process Heat',
    description: 'Direct volumetric heating of materials via high-power electromagnetic radiation.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Electromagnetic field uniformity in heterogeneous materials; Applicator tuning during changing material dielectric properties; High-power magnetron/solid-state generator reliability'
  },
  {
    id: 'supercritical_co2_waste_heat',
    name: 'Waste Heat Recovery via Supercritical CO2 (sCO2) Brayton Cycles',
    shortLabel: 'sCO2 Waste Heat Power',
    sector: 'Industrial Decarbonization & Clean Process Heat',
    description: 'Compact high-efficiency power generation cycles driven by industrial flue gas and furnace heat.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Printed circuit heat exchanger (PCHE) fouling and thermal stress; High-pressure turbo-compressor aerodynamic efficiency near critical point; High-pressure dynamic seal leakage control'
  },
  {
    id: 'electric_lime_calciner',
    name: 'Zero-Emission Electric Calciner for Lime & Cement Manufacturing',
    shortLabel: 'Electric Calciner',
    sector: 'Industrial Decarbonization & Clean Process Heat',
    description: 'Electrified indirect-fired rotary kilns producing high-purity biogenic/mineral CO2 streams.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Indirect electric heating radiant tube lifespan under corrosive alkaline dust; Pure CO2 off-gas capture and particle separation; Continuous kiln throughput scaling'
  },
  {
    id: 'electrochemical_chlor_alkali_decarb',
    name: 'Electrochemical Bulk Chemical & Ethylene Decarbonization',
    shortLabel: 'Electrochemical Chemical Decarb',
    sector: 'Industrial Decarbonization & Clean Process Heat',
    description: 'Electrified membrane synthesis of olefins, aromatics, and chlor-alkali bulk chemicals.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Electrocatalyst selectivity for multi-carbon (C2+) products; Gas-diffusion electrode flooding and carbonate salt precipitation; Faradaic efficiency maintenance at high current densities'
  },

  // 5. Grid Modernization, Power Electronics & Transmission (10)
  {
    id: 'dynamic_line_rating_gets',
    name: 'Dynamic Line Rating (DLR) & Grid-Enhancing Technologies (GETs)',
    shortLabel: 'Dynamic Line Rating (DLR)',
    sector: 'Grid Modernization, Power Electronics & Transmission',
    description: 'Sensor-based real-time transmission capacity unlocking 20-40% extra renewable throughput.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Conductor temperature sensor telemetry latency and cybersecurity; Dynamic thermal rating algorithm integration with EMS/SCADA; Extreme weather ice-load sensing accuracy'
  },
  {
    id: 'grid_forming_inverters_virtual_inertia',
    name: 'Grid-Forming Inverters (GFM) with Virtual Synchronous Inertia',
    shortLabel: 'Grid-Forming Inverters (GFM)',
    sector: 'Grid Modernization, Power Electronics & Transmission',
    description: 'Inverter control algorithms establishing autonomous voltage and frequency without spinning mass.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Sub-synchronous control interaction (SSCI) damping in weak grids; Current limiting during severe symmetrical/asymmetrical grid faults; Multi-vendor interoperability and IEEE 2800 compliance'
  },
  {
    id: 'hvdc_modular_multilevel_converters',
    name: 'High-Voltage Direct Current (HVDC) Modular Multilevel Converters (MMC)',
    shortLabel: 'HVDC MMC Converters',
    sector: 'Grid Modernization, Power Electronics & Transmission',
    description: 'VSC-HVDC transmission enabling multi-gigawatt offshore wind and inter-regional wheeling.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Subsea/underground cable insulation breakdown under DC polarity reversals; High-speed DC circuit breaker interruption time (<5ms); Acoustic noise and valve hall cooling footprint'
  },
  {
    id: 'hts_superconducting_cables',
    name: 'High-Temperature Superconducting (HTS) Power Cables',
    shortLabel: 'HTS Power Cables',
    sector: 'Grid Modernization, Power Electronics & Transmission',
    description: 'Zero-resistance underground power transmission capable of carrying gigawatts in narrow rights-of-way.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Cryogenic liquid nitrogen circulation pressure drop in long cable runs; Thermal runaway quench detection and rapid protection; Cable termination cryostat heat in-leakage'
  },
  {
    id: 'derms_orchestration',
    name: 'Distributed Energy Resource Management Systems (DERMS Orchestration)',
    shortLabel: 'DERMS Orchestration',
    sector: 'Grid Modernization, Power Electronics & Transmission',
    description: 'Edge-to-cloud software orchestrating hundreds of thousands of BTM batteries, EVs, and solar assets.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Distributed multi-agent optimization under asynchronous communications; Low-voltage feeder observability and pseudo-measurement estimation; DER flexibility market clearing latency'
  },
  {
    id: 'solid_state_transformers_sst',
    name: 'Solid-State Transformers (SST for MV/LV Substations)',
    shortLabel: 'Solid-State Transformers (SST)',
    sector: 'Grid Modernization, Power Electronics & Transmission',
    description: 'Power electronic transformers enabling bi-directional AC/DC power routing with full power factor control.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'High-voltage silicon carbide (SiC) MOSFET switching losses; Medium-frequency transformer insulation partial discharge; Fault ride-through capability during transmission line surges'
  },
  {
    id: 'microgrid_islanding_controllers',
    name: 'Fault-Tolerant Microgrid Islanding & Black-Start Controllers',
    shortLabel: 'Microgrid Islanding & Black-Start',
    sector: 'Grid Modernization, Power Electronics & Transmission',
    description: 'Autonomous controllers executing seamless transition to island mode and black-starting 100% inverter grids.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Seamless grid-to-island transition without frequency deviation trip; Black-start coordination of 100% inverter-based resources; Dynamic reactive power balancing across unbundled phases'
  },
  {
    id: 'synchronous_condensers_flywheels',
    name: 'Synchronous Condensers with Flywheels for System Inertia',
    shortLabel: 'Sync Condensers + Flywheels',
    sector: 'Grid Modernization, Power Electronics & Transmission',
    description: 'De-energized rotating machines providing critical physical inertia, short-circuit ratio, and MVARs.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Heavy rotor bearing lubrication and vibration monitoring; Rapid excitation response during voltage depression; Substation civil foundation dynamic loading'
  },
  {
    id: 'power_flow_controllers_facts',
    name: 'Power Flow Control (Advanced FACTS & Variable Phase Shifters)',
    shortLabel: 'Power Flow Controllers (FACTS)',
    sector: 'Grid Modernization, Power Electronics & Transmission',
    description: 'Solid-state line impedance injectors diverting electrons away from overloaded transmission corridors.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'High-speed thyristor switch durability; Sub-transmission line impedance balancing without loop flows; Real-time congestion dispatch algorithm coupling'
  },
  {
    id: 'substation_edge_flisr',
    name: 'Substation Edge Computing & Autonomous Feeder Reconfiguration (FLISR)',
    shortLabel: 'Edge FLISR Grid Automation',
    sector: 'Grid Modernization, Power Electronics & Transmission',
    description: 'Sub-second autonomous distribution feeder fault isolation and restoration without central SCADA delay.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Deterministic edge computing loop latency (<10ms); Cybersecurity micro-segmentation per NERC CIP; Automated fault location, isolation, and service restoration (FLISR)'
  },

  // 6. Carbon Management, Direct Air Capture & Point-Source CDR (10)
  {
    id: 'solid_sorbent_dac',
    name: 'Direct Air Capture (Solid Sorbent Chemisorption DAC)',
    shortLabel: 'Solid Sorbent DAC',
    sector: 'Carbon Management, Direct Air Capture & Point-Source CDR',
    description: 'Amine-functionalized solid porous structures extracting ambient atmospheric CO2 via low-temp steam.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Desorption thermal energy penalty per ton CO2 captured; Sorbent degradation under ambient humidity and NOx/SOx impurities; Contactor pressure drop and parasitic air fan electricity consumption'
  },
  {
    id: 'liquid_solvent_dac',
    name: 'Direct Air Capture (Liquid Solvent Potassium Hydroxide DAC)',
    shortLabel: 'Liquid Solvent DAC',
    sector: 'Carbon Management, Direct Air Capture & Point-Source CDR',
    description: 'Aqueous KOH air contactor coupled to calcium loop calcination for megaton-scale CDR hubs.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'High-temperature calcination energy efficiency (>800°C); Water loss minimization in arid/semi-arid deployment zones; Pellet reactor precipitation kinetics and lime slaker scaling'
  },
  {
    id: 'point_source_sorbent_capture',
    name: 'Point-Source Flue Gas Carbon Capture (Amine-Free Solid Sorbents & Membranes)',
    shortLabel: 'Point-Source Membrane Capture',
    sector: 'Carbon Management, Direct Air Capture & Point-Source CDR',
    description: 'Low-energy non-amine membranes and metal-organic frameworks for cement and steel flue stacks.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Membrane selectivity drop in the presence of trace water vapor; Sorbent dust attrition in fluidized beds; Regeneration heat exchanger footprint in space-constrained industrial sites'
  },
  {
    id: 'class_vi_geologic_sequestration',
    name: 'Class VI Geologic CO2 Sequestration & Wellbore Integrity Monitoring',
    shortLabel: 'Class VI Geologic Storage',
    sector: 'Carbon Management, Direct Air Capture & Point-Source CDR',
    description: 'Permanent supercritical CO2 injection into deep saline aquifers with fiber-optic plume tracking.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Distributed fiber-optic acoustic and temperature sensing (DAS/DTS) resolution; Caprock micro-fracture geomechanical integrity; Downhole supercritical CO2 corrosive brine interactions'
  },
  {
    id: 'co2_mineralization_concrete',
    name: 'CO2 Mineralization in Concrete & Alkaline Waste Byproducts',
    shortLabel: 'CO2 Mineralization Concrete',
    sector: 'Carbon Management, Direct Air Capture & Point-Source CDR',
    description: 'Permanent sequestration of CO2 into calcium carbonate within ready-mix and precast concrete.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'CO2 penetration depth and curing cycle time in precast units; Compressive strength gain vs slump loss in ready-mix concrete; Automated CO2 dosing control based on moisture content'
  },
  {
    id: 'biochar_pyrolysis_cdr',
    name: 'Biochar Production & Carbon-Negative Pyrolysis with Heat Coproduct',
    shortLabel: 'Biochar CDR Pyrolysis',
    sector: 'Carbon Management, Direct Air Capture & Point-Source CDR',
    description: 'Thermochemical stabilization of biogenic waste into recalcitrant carbon biochar for agricultural soils.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Biochar fixed-carbon stability and recalcitrance index (H/C ratio); Syngas emissions cleanup and tar removal; Agricultural soil heavy metal bioavailability monitoring'
  },
  {
    id: 'enhanced_rock_weathering',
    name: 'Enhanced Rock Weathering (Basalt Application on Agricultural Soils)',
    shortLabel: 'Enhanced Rock Weathering',
    sector: 'Carbon Management, Direct Air Capture & Point-Source CDR',
    description: 'Spreading finely crushed silicate rock on croplands to capture atmospheric CO2 as bicarbonate ions.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Baseline soil cation exchange capacity and dissolution rate measurement; Secondary carbonate precipitation vs bicarbonate leaching monitoring, reporting, and verification (MRV); Trace nickel and chromium soil accumulation limits'
  },
  {
    id: 'ocean_alkalinity_enhancement',
    name: 'Ocean Alkalinity Enhancement & Direct Ocean CO2 Capture (DOC)',
    shortLabel: 'Ocean Alkalinity CDR',
    sector: 'Carbon Management, Direct Air Capture & Point-Source CDR',
    description: 'Electrochemical ocean water de-acidification and mineral dissolution to draw down oceanic carbon.',
    defaultTrlMin: 3,
    defaultTrlMax: 6,
    defaultBottlenecks: 'Regional ocean biogeochemical modeling and local pH buffering monitoring; Bicarbonate saturation and secondary precipitation risk; Electro-dialytic water splitting membrane durability in raw seawater'
  },
  {
    id: 'electrochemical_co2_reduction',
    name: 'Electrochemical CO2 Reduction to Syngas & Ethylene',
    shortLabel: 'Electrochemical CO2 Reduction',
    sector: 'Carbon Management, Direct Air Capture & Point-Source CDR',
    description: 'Low-temperature gas-diffusion electrolysis turning captured CO2 into green ethylene and formic acid.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Cathode electrocatalyst stability and degradation from electrolyte impurities; Zero-gap gas-diffusion electrolyzer cell lifetime (>5,000 hrs); Product separation and downstream purification CapEx'
  },
  {
    id: 'in_situ_basalt_mineralization',
    name: 'Subsurface Basalt Carbon Mineralization (In-Situ Rapid Reaction)',
    shortLabel: 'In-Situ Basalt Mineralization',
    sector: 'Carbon Management, Direct Air Capture & Point-Source CDR',
    description: 'Dissolving CO2 in water and injecting into basaltic formations to turn into solid stone within two years.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'In-situ mineral carbonation rate verification via isotopic tracers; Wellbore casing corrosion from carbonated water injection; Subsurface micro-seismic risk mitigation'
  },

  // 7. Clean Buildings, Thermal Energy Networks & Heat Pumps (10)
  {
    id: 'district_thermal_energy_networks',
    name: '5th Generation District Heating & Cooling Thermal Energy Networks (TENs)',
    shortLabel: 'Thermal Energy Networks (TENs)',
    sector: 'Clean Buildings, Thermal Energy Networks & Heat Pumps',
    description: 'Ambient-temperature bidirectional water loops sharing waste heat between urban buildings.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Right-of-way subsurface utility coordination and boring CapEx; Thermal balancing across mixed-use residential/commercial load profiles; Hydraulic pumping energy optimization'
  },
  {
    id: 'cold_climate_heat_pumps',
    name: 'Cold-Climate Air-Source Heat Pumps (Vapor Injection -20°F Operation)',
    shortLabel: 'Cold-Climate Heat Pumps',
    sector: 'Clean Buildings, Thermal Energy Networks & Heat Pumps',
    description: 'Enhanced vapor injection scroll compressors delivering full heating capacity in sub-zero climates.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Heating capacity retention at -20°F ambient temperature without electric resistance backup; Defrost cycle frequency and noise minimization; Low-GWP refrigerant flammability and charge limits (A2L)'
  },
  {
    id: 'geothermal_ground_source_heat_pumps',
    name: 'Geothermal Ground-Source Heat Pumps (Shared Ambient Loop District Systems)',
    shortLabel: 'Geothermal Ground Heat Pumps',
    sector: 'Clean Buildings, Thermal Energy Networks & Heat Pumps',
    description: 'Closed-loop vertical borehole fields utilizing stable ground temperatures for COP > 4.5 heating/cooling.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Deep borehole thermal fatigue and grout conductivity optimization; Long-term borehole field thermal imbalance; Drilling cost reduction in urban bedrock'
  },
  {
    id: 'solid_state_caloric_cooling',
    name: 'Acoustic / Thermoacoustic Heat Pumps & Solid-State Caloric Cooling',
    shortLabel: 'Solid-State Caloric Cooling',
    sector: 'Clean Buildings, Thermal Energy Networks & Heat Pumps',
    description: 'Refrigerant-free solid electrocaloric and acoustic cooling cycles with zero GWP footprint.',
    defaultTrlMin: 3,
    defaultTrlMax: 6,
    defaultBottlenecks: 'Piezoelectric/magnetocaloric material fatigue after billion-cycle actuation; Acoustic streaming heat transfer losses; Compact resonator packaging'
  },
  {
    id: 'vacuum_insulated_glass_aerogel',
    name: 'Ultra-Thin Aerogel & Vacuum Insulated Glass (VIG) Envelope Retrofits',
    shortLabel: 'Vacuum Insulated Glass & Aerogel',
    sector: 'Clean Buildings, Thermal Energy Networks & Heat Pumps',
    description: 'R-12+ ultra-thin architectural glazing and aerogel blankets for non-invasive historic building retrofits.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Vacuum glass edge seal hermetic durability over 25+ years; Aerogel blanket dust shedding during installation; Thermal bridging elimination in historic masonry facades'
  },
  {
    id: 'phase_change_material_envelope',
    name: 'Phase Change Material (PCM) Thermal Storage in Building Envelopes',
    shortLabel: 'PCM Thermal Envelope',
    sector: 'Clean Buildings, Thermal Energy Networks & Heat Pumps',
    description: 'Micro-encapsulated organic paraffin/salt hydrate PCMs shifting HVAC peak loads by hours.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'PCM phase separation and subcooling mitigation; Heat transfer enhancement using graphite matrices; Fire retardancy integration without loss of latent heat capacity'
  },
  {
    id: 'ai_hvac_predictive_digital_twins',
    name: 'Self-Optimizing Predictive HVAC Controls & Building Digital Twins',
    shortLabel: 'AI HVAC Digital Twins',
    sector: 'Clean Buildings, Thermal Energy Networks & Heat Pumps',
    description: 'Model predictive control optimizing chillers, boilers, and ventilation based on real-time weather and tariffs.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Occupancy sensor accuracy and privacy preservation; Model predictive control (MPC) stability under sudden weather swings; Legacy BACnet/Modbus integration and cybersecurity'
  },
  {
    id: 'sewer_wastewater_heat_recovery',
    name: 'Wastewater Heat Recovery (Sewer Thermal Energy Extraction)',
    shortLabel: 'Sewer Heat Recovery',
    sector: 'Clean Buildings, Thermal Energy Networks & Heat Pumps',
    description: 'Extracting thermal energy from municipal sewage trunk lines to feed central district heat pumps.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Wastewater solids fouling and biofilm buildup on heat exchanger surfaces; Bi-directional heat extraction and injection seasonal balancing; Corrosion resistance against hydrogen sulfide gas'
  },
  {
    id: 'natural_refrigerants_co2_propane',
    name: 'Commercial Refrigeration with Low-GWP Natural Refrigerants (CO2 / Propane)',
    shortLabel: 'Natural Refrigerants (CO2/R290)',
    sector: 'Clean Buildings, Thermal Energy Networks & Heat Pumps',
    description: 'Transcritical CO2 (R744) and hydrocarbon refrigeration systems eliminating hydrofluorocarbons.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Transcritical CO2 high-side operating pressure safety (120+ bar); R290 propane charge limit compliance in retail spaces; Adiabatic gas cooler efficiency during summer heatwaves'
  },
  {
    id: 'electrochromic_smart_windows',
    name: 'Smart Automated Window Glazing & Electrochromic Dynamic Envelopes',
    shortLabel: 'Electrochromic Smart Windows',
    sector: 'Clean Buildings, Thermal Energy Networks & Heat Pumps',
    description: 'Electronically tintable architectural glass dynamically modulating solar heat gain coefficient (SHGC).',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Switching speed and optical tint uniformity across large architectural glass panes; 30-year UV solar radiation durability; Low-voltage wiring integration in curtain wall frames'
  },

  // 8. Heavy Transportation, Megawatt EV & Maritime / Aviation (10)
  {
    id: 'megawatt_ev_charging_mcs',
    name: 'Megawatt EV Fast-Charging Systems (MCS for Class 8 Heavy Trucks)',
    shortLabel: 'Megawatt EV Charging (MCS)',
    sector: 'Heavy Transportation, Megawatt EV & Maritime / Aviation',
    description: 'High-power 3.75 MW DC conductive charging for commercial freight and fleet electrification.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Liquid-cooled cable thermal management under 3.75 MW continuous draw; Substation interconnect capacity and on-site buffer battery coordination; High-cycle connector contact pin durability'
  },
  {
    id: 'heavy_duty_fuel_cell_trucks',
    name: 'Heavy-Duty Fuel Cell Electric Truck Powertrains (350kW+ Fuel Cell)',
    shortLabel: 'Fuel Cell Heavy Trucks',
    sector: 'Heavy Transportation, Megawatt EV & Maritime / Aviation',
    description: 'Long-haul zero-emission hydrogen fuel cell powertrains offering 500+ mile range and fast fueling.',
    defaultTrlMin: 6,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Membrane electrode assembly (MEA) durability under highway heavy shock and vibration; Cathode air filtration in dirty freight highway environments; Fuel cell stack freezing and cold-start below -30°C'
  },
  {
    id: 'type_iv_700bar_composite_h2_tanks',
    name: 'High-Pressure 700-Bar Composite Hydrogen On-Board Storage Tanks',
    shortLabel: '700-Bar H2 Composite Tanks',
    sector: 'Heavy Transportation, Megawatt EV & Maritime / Aviation',
    description: 'Carbon fiber filament-wound Type-IV tanks with high gravimetric hydrogen storage density.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Carbon fiber winding optimization to reduce vessel weight; Fast-fill thermal heat dissipation during 15-minute 700-bar fueling; Permeation liner micro-cracking during rapid depressurization'
  },
  {
    id: 'cryogenic_liquid_h2_fueling',
    name: 'Cryogenic Liquid Hydrogen Fueling & Heavy-Duty Boil-Off Management',
    shortLabel: 'Cryo-Liquid H2 Fueling',
    sector: 'Heavy Transportation, Megawatt EV & Maritime / Aviation',
    description: 'Cryo-pumped liquid H2 infrastructure for long-distance maritime, heavy rail, and long-haul trucking.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Liquid hydrogen boil-off gas reliquefaction / recovery; Sub-cooled cryogenic pump cavitation and seal life; Vacuum-insulated pipe transfer decoupling safety'
  },
  {
    id: 'maritime_ammonia_dual_fuel_engines',
    name: 'Maritime Ammonia-Fueled Dual-Fuel Two-Stroke Marine Engines',
    shortLabel: 'Ammonia Maritime Engines',
    sector: 'Heavy Transportation, Megawatt EV & Maritime / Aviation',
    description: 'Large two-stroke marine internal combustion engines running on green ammonia with zero CO2.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Unburned ammonia slip and N2O greenhouse gas emissions abatement; Fuel injector corrosion from liquid anhydrous ammonia; Engine room double-walled safety piping and leak scrubbing'
  },
  {
    id: 'hybrid_electric_hydrogen_aviation',
    name: 'Hybrid-Electric & Fuel-Cell Commercial Regional Aviation Powertrains',
    shortLabel: 'Zero-Emission Aviation Powertrains',
    sector: 'Heavy Transportation, Megawatt EV & Maritime / Aviation',
    description: 'Megawatt-class electric propulsion and liquid hydrogen fuel cells for regional commuter aircraft.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'High-altitude dielectric breakdown and partial discharge in low atmospheric pressure; Megawatt motor power density (>15 kW/kg); In-flight cryogenic hydrogen fuel system safety'
  },
  {
    id: 'dynamic_wireless_roadway_charging',
    name: 'Pantograph & High-Power Inductive Dynamic Roadway Wireless Charging',
    shortLabel: 'Dynamic In-Road EV Charging',
    sector: 'Heavy Transportation, Megawatt EV & Maritime / Aviation',
    description: 'Electrified highway lanes transferring power wirelessly to heavy-duty trucks while in motion.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Transmitter-receiver coil alignment tolerance at highway speeds; Electromagnetic field (EMF) shielding for vehicle occupants; Pavement asphalt thermal stress and inductive coil durability'
  },
  {
    id: 'battery_electric_locomotives',
    name: 'Electric Locomotive Battery-Tender Propulsion Systems',
    shortLabel: 'Battery Freight Locomotives',
    sector: 'Heavy Transportation, Megawatt EV & Maritime / Aviation',
    description: 'Multi-megawatt-hour battery tender cars paired with diesel-electric locomotives to form heavy hybrid consists.',
    defaultTrlMin: 6,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Multi-megawatt-hour locomotive battery thermal runaway containment; Regenerative braking energy capture from heavy freight downhill runs; High-voltage DC link switching to traction inverters'
  },
  {
    id: 'port_cold_ironing_shore_power',
    name: 'Port Vessel Cold Ironing & Microgrid Shore Power Integration',
    shortLabel: 'Port Cold Ironing Shore Power',
    sector: 'Heavy Transportation, Megawatt EV & Maritime / Aviation',
    description: 'High-voltage shore-to-ship power enabling berthed ocean vessels to shut down auxiliary diesel generators.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Synchronizing shipboard generator with shore grid without vessel black-out; Cable management system flexibility with tidal elevation swings; High-voltage shore connection safety interlocks'
  },
  {
    id: 'electric_marine_ferries_swappable_battery',
    name: 'Electric Marine Ferries & Swappable Containerized Megawatt Batteries',
    shortLabel: 'Swappable Battery Marine Ferries',
    sector: 'Heavy Transportation, Megawatt EV & Maritime / Aviation',
    description: 'Fully electric passenger and vehicle ferries utilizing robotic battery container swapping at ports.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Automated marine robotic battery swap mechanism alignment in rough waters; Containerized battery seawater corrosion protection; High-power harbor charging turnaround (<10 min)'
  },

  // 9. Advanced Renewable Generation: Solar & Wind (10)
  {
    id: 'perovskite_silicon_tandem_pv',
    name: 'Perovskite-Silicon Tandem Photovoltaic Solar Modules (>30% Efficiency)',
    shortLabel: 'Perovskite Tandem Solar PV',
    sector: 'Advanced Renewable Generation: Solar & Wind',
    description: 'Two-terminal tandem solar cells breaking theoretical single-junction Shockley-Queisser limits.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Perovskite layer thermal and moisture degradation under continuous illumination; Large-area slot-die coating uniformity for 2m² modules; Lead encapsulation and non-toxic bismuth/tin alternatives'
  },
  {
    id: 'agrivoltaics_dual_use_trackers',
    name: 'Agrivoltaics & Dual-Use Agricultural Solar Trackers',
    shortLabel: 'Agrivoltaics Solar Trackers',
    sector: 'Advanced Renewable Generation: Solar & Wind',
    description: 'Elevated single-axis smart tracking solar arrays co-located with livestock grazing and specialty crops.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Single-axis tracker structural wind loading at elevated heights (10ft+ clearance); Crop microclimate optimization and PAR light transmission modeling; Agricultural farm machinery clearance'
  },
  {
    id: 'bifacial_heterojunction_pv',
    name: 'Bifacial Heterojunction (HJT) Solar PV with Advanced Metallization',
    shortLabel: 'Bifacial HJT Solar PV',
    sector: 'Advanced Renewable Generation: Solar & Wind',
    description: 'High-bifaciality solar cells with ultra-low temperature coefficients and copper plating metallization.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Thin-wafer bowing during module lamination; Low-temperature silver paste consumption reduction; Module rear-side albedo capture under snowy/sandy terrain'
  },
  {
    id: 'deepwater_floating_offshore_wind',
    name: 'Deepwater Floating Offshore Wind (Semi-Submersible / Tension Leg Platforms)',
    shortLabel: 'Floating Offshore Wind',
    sector: 'Advanced Renewable Generation: Solar & Wind',
    description: 'Floating substructures unlocking high-capacity ocean wind resources in waters deeper than 60 meters.',
    defaultTrlMin: 6,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Semi-submersible hull hydrodynamics and wave vortex-induced motions; Mooring line tension fatigue under 100-year storm surges; Dynamic subsea inter-array power cable flex fatigue'
  },
  {
    id: 'nextgen_15mw_offshore_wind_nacelles',
    name: '15MW+ Next-Gen Offshore Wind Turbine Nacelles & Carbon Blades',
    shortLabel: '15MW+ Offshore Wind Turbines',
    sector: 'Advanced Renewable Generation: Solar & Wind',
    description: 'Direct-drive permanent magnet generators with 115m+ aero-elastically tailored carbon blades.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Direct-drive permanent magnet generator structural deflection; 115m+ carbon fiber blade leading-edge rain erosion; Heavy-lift offshore installation vessel crane limits'
  },
  {
    id: 'airborne_wind_energy_kites',
    name: 'Airborne Wind Energy Systems (AWE Kites & Tethered Drones)',
    shortLabel: 'Airborne Wind Energy (AWE)',
    sector: 'Advanced Renewable Generation: Solar & Wind',
    description: 'Autonomous high-altitude tethered wings tapping strong, continuous crosswind high above traditional towers.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Autonomous launch, flight trajectory optimization, and recovery in turbulent wind gusts; High-cycle tether tensile fatigue and electrical power transmission; FAA airspace safety integration'
  },
  {
    id: 'autonomous_wind_blade_drone_repair',
    name: 'Autonomous Wind Turbine Blade Inspection & Laser Leading-Edge Repair',
    shortLabel: 'Autonomous Blade Drone Repair',
    sector: 'Advanced Renewable Generation: Solar & Wind',
    description: 'AI-guided climbing robotics and drones performing autonomous composite repair in the field.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Autonomous edge-AI crack detection on rotating/parked blades; In-situ robotic UV-curing epoxy application on leading-edge erosion; High-altitude wind gust station-keeping'
  },
  {
    id: 'building_integrated_pv_bipv',
    name: 'Building-Integrated Photovoltaics (BIPV Solar Facades & Shingles)',
    shortLabel: 'BIPV Solar Facades',
    sector: 'Advanced Renewable Generation: Solar & Wind',
    description: 'Aesthetic architectural glass, rainscreens, and shingles generating power directly from building envelopes.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Architectural color consistency without severe solar conversion efficiency penalty; Fire safety rating under ASTM E119 for building envelope integration; Cell mismatch compensation in complex shaded facades'
  },
  {
    id: 'concentrated_solar_power_particles',
    name: 'Concentrated Solar Thermal Power (CSP) with Particle Heat Receivers',
    shortLabel: 'CSP Particle Receiver Power',
    sector: 'Advanced Renewable Generation: Solar & Wind',
    description: 'Heliostat fields concentrating solar flux onto ceramic falling particles for 800°C+ thermal energy storage.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Solid ceramic particle attrition and thermal shock at 800°C; Particle receiver cavity heat loss and radiative emissivity; High-temperature particle-to-sCO2 heat exchanger'
  },
  {
    id: 'wake_steering_wind_farm_optimization',
    name: 'Repowering Optimization & Wake-Steering Array Control for Wind Farms',
    shortLabel: 'Wake-Steering Wind Control',
    sector: 'Advanced Renewable Generation: Solar & Wind',
    description: 'Coordinated yaw and pitch steering deflecting turbulent wakes away from downstream turbines to boost farm yield.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Real-time yaw misalignment control under shifting atmospheric turbulence; Blade fatigue load redistribution during intentional wake steering; LiDAR predictive wind measurement integration'
  },

  // 10. Geothermal, Hydrokinetic & Ocean Energy (8)
  {
    id: 'enhanced_geothermal_egs',
    name: 'Enhanced Geothermal Systems (EGS Hydraulic Shear Stimulation)',
    shortLabel: 'Enhanced Geothermal (EGS)',
    sector: 'Geothermal, Hydrokinetic & Ocean Energy',
    description: 'Creating engineered permeability in hot dry crystalline rock to extract continuous baseload clean power.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Hydraulic stimulation fracture network connectivity without induced seismicity; Downhole tool electronics durability at >200°C; Long-term reservoir thermal drawdown management'
  },
  {
    id: 'supercritical_deep_egs',
    name: 'Supercritical Deep EGS (>400°C Ultra-Deep Drilling)',
    shortLabel: 'Supercritical Deep EGS',
    sector: 'Geothermal, Hydrokinetic & Ocean Energy',
    description: 'Drilling to 5-10km depth to tap supercritical fluids with 10x higher energy density than conventional wells.',
    defaultTrlMin: 3,
    defaultTrlMax: 6,
    defaultBottlenecks: 'Drill bit and mud motor survivability in extreme super-hot rock; Supercritical geothermal fluid chemistry and silica scaling; Wellbore casing thermal expansion stresses'
  },
  {
    id: 'closed_loop_advanced_geothermal',
    name: 'Closed-Loop Advanced Geothermal Systems (AGS Radiator Wellbores)',
    shortLabel: 'Closed-Loop Geothermal (AGS)',
    sector: 'Geothermal, Hydrokinetic & Ocean Energy',
    description: 'Sealed subsurface radiator loops circulating working fluids without fracking or water consumption.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Deep horizontal multi-lateral wellbore drilling precision; Conductive heat transfer surface area limits; Working fluid circulation thermosiphon optimization'
  },
  {
    id: 'geothermal_lithium_mineral_extraction',
    name: 'Geothermal Lithium & Critical Mineral Co-Extraction from Brines',
    shortLabel: 'Geothermal Lithium Co-Extraction',
    sector: 'Geothermal, Hydrokinetic & Ocean Energy',
    description: 'Integrated direct lithium extraction (DLE) harvesting battery metals from geothermal brine streams.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Direct lithium extraction (DLE) adsorbent selectivity in high-salinity hot brines; Silica fouling removal prior to lithium adsorption; Reinjection well clogging prevention'
  },
  {
    id: 'tidal_stream_dual_rotor_turbines',
    name: 'Tidal Stream Turbines with Dual-Rotor Flow Optimization',
    shortLabel: 'Tidal Stream Turbines',
    sector: 'Geothermal, Hydrokinetic & Ocean Energy',
    description: 'Subsea hydrokinetic turbines capturing predictable astronomical ocean tidal current power.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Biofouling and marine growth on rotor hydrofoils; Dual-rotor counter-rotating torque balancing in high-velocity tidal channels; Subsea wet-mate connector durability'
  },
  {
    id: 'wave_energy_converters',
    name: 'Wave Energy Converters (Oscillating Water Column / Point Absorber)',
    shortLabel: 'Wave Energy Converters',
    sector: 'Geothermal, Hydrokinetic & Ocean Energy',
    description: 'Ocean surface buoys and air-column turbines converting wave kinematic energy into electricity.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Survivability during 50-year extreme rogue wave storm conditions; Power take-off (PTO) mechanical-to-electrical efficiency; Moorings and umbilical cable fatigue life'
  },
  {
    id: 'otec_ocean_thermal_energy',
    name: 'Ocean Thermal Energy Conversion (OTEC Deep Cold Water)',
    shortLabel: 'Ocean Thermal (OTEC)',
    sector: 'Geothermal, Hydrokinetic & Ocean Energy',
    description: 'Exploiting the temperature gradient between tropical surface water and deep 1000m cold ocean water.',
    defaultTrlMin: 4,
    defaultTrlMax: 6,
    defaultBottlenecks: 'Deep cold water pipe (1000m depth) structural hydrodynamics; Large-scale low-pressure ammonia turbine efficiency; Biological slime fouling on aluminum heat exchangers'
  },
  {
    id: 'low_head_conduit_micro_hydro',
    name: 'Low-Head & Conduit Hydropower In-Line Micro-Turbines',
    shortLabel: 'Conduit Micro-Hydropower',
    sector: 'Geothermal, Hydrokinetic & Ocean Energy',
    description: 'Generating clean electricity from existing municipal water conduits, irrigation canals, and low-head dams.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Fish-friendly turbine runner hydrodynamic design; Variable flow speed permanent magnet generator efficiency; Automated trash-rack cleaning and sediment bypass'
  },

  // 11. Circular Economy, Battery Recycling & Critical Minerals (8)
  {
    id: 'direct_cathode_recycling',
    name: 'Direct Cathode-to-Cathode Recycling for LFP and NMC Batteries',
    shortLabel: 'Direct Cathode Recycling',
    sector: 'Circular Economy, Battery Recycling & Critical Minerals',
    description: 'Re-lithiation and structural healing of degraded cathode powders without energy-intensive smelting.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Relithiation annealing uniformity of degraded cathode particles; Selective binder and carbon black delamination without toxic solvents; Recovered cathode electrochemical cycle life parity'
  },
  {
    id: 'hydrometallurgical_battery_refining',
    name: 'Hydrometallurgical Extraction of Lithium, Nickel & Cobalt from Black Mass',
    shortLabel: 'Hydrometallurgical Black Mass Refining',
    sector: 'Circular Economy, Battery Recycling & Critical Minerals',
    description: 'Low-temperature aqueous acid leaching achieving >98% recovery of battery-grade precursor salts.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Acid leaching chemical consumption and wastewater neutralization; High-purity separation of nickel and cobalt from manganese and iron; Reagent recycling loop closure'
  },
  {
    id: 'bioleaching_rare_earth_elements',
    name: 'Bioleaching of Rare Earth Elements (REE) from Electronic & Industrial Waste',
    shortLabel: 'Bioleaching Rare Earths',
    sector: 'Circular Economy, Battery Recycling & Critical Minerals',
    description: 'Microbial organism metabolic extraction of neodymium and dysprosium from magnets and e-waste.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Microbial leaching kinetics and strain adaptation in acidic ore slurries; Continuous bioreactor nutrient management; Selective solvent extraction of neodymium and dysprosium'
  },
  {
    id: 'synthetic_graphite_biocarbon',
    name: 'Synthetic Graphite Manufacturing from Non-Fossil Carbon Precursors',
    shortLabel: 'Biocarbon Synthetic Graphite',
    sector: 'Circular Economy, Battery Recycling & Critical Minerals',
    description: 'High-crystallinity battery anode graphite synthesized from renewable forestry lignin and bio-pitch.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Graphitization furnace energy consumption at 2800°C; Biocarbon precursor carbon yield and crystallinity; Anode slurry rheology and SEI formation stability'
  },
  {
    id: 'silicon_anode_nanomaterials',
    name: 'Silicon Anode Nanomaterial Production for Next-Gen High-Density Cells',
    shortLabel: 'Silicon Anode Nanomaterials',
    sector: 'Circular Economy, Battery Recycling & Critical Minerals',
    description: 'Nanostructured porous silicon-carbon composites boosting cell volumetric energy density by 30-50%.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Silicon particle 300% volume expansion pulverization mitigation; Carbon-coating nanostructure scalability; First-cycle irreversible capacity loss compensation'
  },
  {
    id: 'zero_liquid_discharge_dle',
    name: 'Zero-Liquid-Discharge (ZLD) Lithium Brine Direct Extraction (DLE)',
    shortLabel: 'Zero-Liquid Discharge DLE',
    sector: 'Circular Economy, Battery Recycling & Critical Minerals',
    description: 'Closed-loop DLE using selective adsorption membranes with 95% process water recycling.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Adsorbent elution water consumption and freshwater recovery; Resin capacity degradation over thousands of cycles; High-salinity brine reinjection pressure'
  },
  {
    id: 'composite_wind_blade_recycling',
    name: 'Composite Wind Turbine Blade Thermoset Resin Depolymerization',
    shortLabel: 'Composite Blade Recycling',
    sector: 'Circular Economy, Battery Recycling & Critical Minerals',
    description: 'Chemical solvolysis breaking down epoxy resins to recover virgin-grade carbon and glass fibers.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Mild chemical solvolysis reagent recyclability; Reclaimed carbon and glass fiber structural tensile strength retention; High-throughput blade shredding logistics'
  },
  {
    id: 'solar_pv_module_delamination_recycling',
    name: 'Solar PV Module Glass, Silicon & Silver Thermal Delamination & Recovery',
    shortLabel: 'Solar PV Module Recycling',
    sector: 'Circular Economy, Battery Recycling & Critical Minerals',
    description: 'Clean thermal separation and chemical refining recovering >95% of silver, silicon, and copper from decommissioned panels.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Delamination of EVA encapsulant without toxic fluoropolymer emissions; Silicon wafer etching and high-purity solar-grade silicon recovery; Silver hydrometallurgical recovery yield (>95%)'
  },

  // 12. Bioenergy, RNG & Methane Abatement (8)
  {
    id: 'anaerobic_digestion_biomethane_rng',
    name: 'High-Yield Anaerobic Digestion & Biomethane RNG Upgrading with Membranes',
    shortLabel: 'Biomethane RNG Upgrading',
    sector: 'Bioenergy, RNG & Methane Abatement',
    description: 'Thermophilic digestion of organic waste with multi-stage membrane separation into pipeline-spec RNG.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Multi-stage polymeric membrane CO2/CH4 selectivity; Trace siloxane and volatile organic sulfur removal to pipeline specs; Digester microbial community stability during feedstock changes'
  },
  {
    id: 'dairy_manure_methane_abatement',
    name: 'Dairy Manure Methane Abatement & Gas-to-Electricity Microgrids',
    shortLabel: 'Dairy Methane Microgrids',
    sector: 'Bioenergy, RNG & Methane Abatement',
    description: 'Covered lagoon biogas capture converting agricultural methane emissions into dispatchable local microgrid power.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Low-temperature psychrophilic digestion efficiency in cold winter climates; Hydrogen sulfide scrubbers for combined heat and power (CHP) engines; Digestate nutrient recovery (N & P)'
  },
  {
    id: 'hydrothermal_liquefaction_sludge',
    name: 'Hydrothermal Liquefaction (HTL) of Wet Sewage Sludge & Algae to Biocrude',
    shortLabel: 'Hydrothermal Biocrude (HTL)',
    sector: 'Bioenergy, RNG & Methane Abatement',
    description: 'Thermochemical pressure conversion of wet non-food biomass into drop-in synthetic crude oil.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Continuous high-pressure (200 bar) slurry pumping reliability; Biocrude hydro-deoxygenation and nitrogen removal; Aqueous phase carbon recovery and wastewater treatment'
  },
  {
    id: 'supercritical_water_gasification',
    name: 'Supercritical Water Gasification of High-Moisture Organic Waste',
    shortLabel: 'Supercritical Water Gasification',
    sector: 'Bioenergy, RNG & Methane Abatement',
    description: 'Complete tar-free conversion of wet organic feedstocks into hydrogen and syngas in supercritical water.',
    defaultTrlMin: 4,
    defaultTrlMax: 7,
    defaultBottlenecks: 'Salt precipitation and plugging at supercritical water conditions (374°C, 221 bar); Reactor alloy corrosion resistance; High-pressure clean syngas production without tar'
  },
  {
    id: 'biogenic_co2_purification',
    name: 'Biogenic CO2 Purification & High-Purity Synthetic Fuel Feedstock',
    shortLabel: 'Biogenic CO2 Purification',
    sector: 'Bioenergy, RNG & Methane Abatement',
    description: 'Cryogenic capture and purification of 100% biogenic CO2 from bioethanol and RNG facilities.',
    defaultTrlMin: 7,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Cryogenic CO2 purification to food/beverage and industrial E-fuel purity (>99.9%); Boil-off gas recovery during storage and transport; Low-energy refrigeration cycle'
  },
  {
    id: 'fast_pyrolysis_bio_oil',
    name: 'Fast Pyrolysis Bio-Oil with Hydrotreating for Drop-in Bio-Refinery',
    shortLabel: 'Fast Pyrolysis Bio-Oil',
    sector: 'Bioenergy, RNG & Methane Abatement',
    description: 'Rapid fluid-bed pyrolysis of agricultural and forestry residues into refined refinery co-processing feedstocks.',
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Pyrolysis vapor quenching and aerosol coalescing; Bio-oil acidity (low pH) and polymerization during storage; Catalytic deoxygenation hydrogen consumption'
  },
  {
    id: 'cellulosic_enzymatic_hydrolysis',
    name: 'Enzymatic Hydrolysis for Cellulosic Ethanol & Platform Biochemicals',
    shortLabel: 'Cellulosic Enzymatic Hydrolysis',
    sector: 'Bioenergy, RNG & Methane Abatement',
    description: 'Advanced enzyme cocktails deconstructing non-food lignocellulose into fermentable C5 and C6 sugars.',
    defaultTrlMin: 6,
    defaultTrlMax: 8,
    defaultBottlenecks: 'Pretreatment inhibitor generation minimization; Enzyme cocktail loading cost per dry ton biomass; Continuous fermentation productivity with high-solids loading'
  },
  {
    id: 'landfill_gas_cryogenic_siloxane_removal',
    name: 'Landfill Gas Enhanced Recovery & Siloxane Cryogenic Removal',
    shortLabel: 'Landfill Gas Siloxane Cleanup',
    sector: 'Bioenergy, RNG & Methane Abatement',
    description: 'Deep cryogenic condensation removing volatile organic silicon compounds from fugitive municipal landfill gas.',
    defaultTrlMin: 6,
    defaultTrlMax: 9,
    defaultBottlenecks: 'Multi-well vacuum header automation based on gas composition sensors; Cryogenic condensation of high-molecular-weight siloxanes; Nitrogen and oxygen deep rejection to meet pipeline standards'
  }
];

export function findCleanTech(identifier: string): CleanTechItem | undefined {
  if (!identifier) return undefined;
  const lower = identifier.toLowerCase().trim();
  return CLEAN_ENERGY_TECHNOLOGIES.find(
    t => t.id.toLowerCase() === lower ||
         t.name.toLowerCase() === lower ||
         t.shortLabel.toLowerCase() === lower ||
         t.name.toLowerCase().includes(lower) ||
         lower.includes(t.shortLabel.toLowerCase())
  );
}
