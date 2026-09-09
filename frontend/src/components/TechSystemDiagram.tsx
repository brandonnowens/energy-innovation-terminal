import React, { useState, useMemo } from 'react';
import {
  Zap, Play, Pause, RotateCw, Info, AlertTriangle, Sparkles,
  Layers, Sliders, ChevronRight, Activity, Eye, ShieldCheck,
  CheckCircle2, Gauge, Thermometer, Wind, Droplets, BatteryCharging,
  Cpu, Atom, Flame, ArrowRight, RefreshCw, ZoomIn, Sun
} from 'lucide-react';

export interface DiagramNode {
  id: string;
  name: string;
  category: string;
  x: number; // 0 to 100 percentage
  y: number; // 0 to 100 percentage
  icon: string;
  summary: string;
  operatingValue: string;
  materials: string;
  failureMode: string;
  frontierBottleneck: string;
  activeResearch: string;
}

export interface DiagramConduit {
  from: string;
  to: string;
  label: string;
  type: 'electricity' | 'matter' | 'heat' | 'fluid' | 'photons';
  bidirectional?: boolean;
}

export interface DiagramMode {
  id: string;
  label: string;
  description: string;
  efficiencyIndicator: string;
  activeFlows: string[];
}

export interface TechDiagramConfig {
  technologyId: string;
  title: string;
  subtitle: string;
  modes: DiagramMode[];
  nodes: DiagramNode[];
  conduits: DiagramConduit[];
}

// ==============================================================================
// 1. BESPOKE SYSTEM ARCHITECTURE SCHEMAS FOR CLEAN TECH DOMAINS
// ==============================================================================

const DIAGRAM_CONFIGS: Record<string, TechDiagramConfig> = {
  // ── 1. IRON-AIR BATTERY ──────────────────────────────────────────────────
  iron_air_battery: {
    technologyId: 'iron_air_battery',
    title: 'Iron-Air Electrochemical Rust Cell Architecture',
    subtitle: 'Reversible multi-day iron oxidation & reduction with alkaline water electrolyte and breathing air cathode.',
    modes: [
      {
        id: 'discharge',
        label: 'Discharge Mode (Iron Oxidation / Rusting)',
        description: 'Cathode inhales atmospheric oxygen; iron anode oxidizes into iron rust, pumping electrons (e-) out to the power grid for up to 100 continuous hours.',
        efficiencyIndicator: '48% Round-Trip Efficiency · 100-Hour Output',
        activeFlows: ['air_to_cathode', 'anode_to_inverter', 'inverter_to_grid']
      },
      {
        id: 'charge',
        label: 'Charge Mode (Rust Reduction / Breathing Out)',
        description: 'Surplus renewable electricity applies reverse voltage, stripping oxygen from rust back into metallic iron and expelling pure O2 gas into the air.',
        efficiencyIndicator: 'Input: Surplus Solar/Wind · Regeneration State',
        activeFlows: ['grid_to_inverter', 'inverter_to_anode', 'cathode_to_air']
      }
    ],
    nodes: [
      {
        id: 'air_breathing_cathode',
        name: 'Air-Breathing Gas Diffusion Cathode',
        category: 'Catalytic Reaction Interface',
        x: 18,
        y: 45,
        icon: 'Wind',
        summary: 'Porous carbon gas diffusion layer with bifunctional oxygen reduction (ORR) and oxygen evolution (OER) catalysts.',
        operatingValue: 'Ambient Air Inflow / Pure O2 Vent',
        materials: 'Nickel-Manganese Spinel & Carbon Nanotubes',
        failureMode: 'Carbonate crust scaling from atmospheric CO2 poisoning catalyst pores.',
        frontierBottleneck: 'Bifunctional catalyst degradation under repeated high-voltage charging cycles.',
        activeResearch: 'Hydrophobic gas-selective membranes that reject CO2 while admitting O2 (DOE ARPA-E / PNNL).'
      },
      {
        id: 'alkaline_electrolyte',
        name: 'Water-Based Alkaline Electrolyte',
        category: 'Ionic Transport Medium',
        x: 50,
        y: 45,
        icon: 'Droplets',
        summary: 'Non-flammable liquid potassium hydroxide (KOH) solution transporting hydroxide ions (OH-) between electrodes.',
        operatingValue: '6 Molar KOH Solution · 25°C to 40°C',
        materials: 'Water, Potassium Hydroxide, Corrosion Inhibitors',
        failureMode: 'Electrolyte dry-out and dendrite precipitation under severe multi-day cycling.',
        frontierBottleneck: 'Parasitic Hydrogen Evolution Reaction (HER) side-reaction stealing charging energy.',
        activeResearch: 'Bismuth and stannate liquid additives suppressing hydrogen bubble formation on iron pellets.'
      },
      {
        id: 'iron_metal_anode',
        name: 'Sintered Iron Pellet Anode Bed',
        category: 'Electrochemical Energy Storage',
        x: 82,
        y: 45,
        icon: 'BatteryCharging',
        summary: 'Packed bed of high-surface-area sintered iron pellets that reversibly transform between metallic iron (Fe) and iron rust (Fe(OH)2).',
        operatingValue: 'Fe <-> Fe(OH)2 + 2e- (E0 = -0.88V)',
        materials: 'Abundant Domestic Sintered Iron Powder',
        failureMode: 'Iron passivation layer forming prematurely, choking discharge before full capacity is extracted.',
        frontierBottleneck: 'Electrode density limits and slow iron dissolution kinetics during sub-zero winter temperatures.',
        activeResearch: 'Engineered multi-scale porous iron scaffolds with sulfur dopants preventing iron passivation.'
      },
      {
        id: 'bidirectional_inverter',
        name: 'Grid Inverter & Thermal Balance Unit',
        category: 'Power Electronics Interface',
        x: 50,
        y: 85,
        icon: 'Zap',
        summary: 'Bi-directional DC/AC inverter and water cooling management regulating multi-day power injection to local transmission lines.',
        operatingValue: '480V AC to 600V DC · >96% Conversion',
        materials: 'Silicon Carbide (SiC) Power Semiconductors',
        failureMode: 'Thermal management pump wear during sustained 100-hour continuous dispatch.',
        frontierBottleneck: 'Balance-of-plant parasitics cutting into low round-trip efficiency.',
        activeResearch: 'Integrated solid-state power blocks with autonomous sub-station islanding controllers.'
      }
    ],
    conduits: [
      { from: 'air_breathing_cathode', to: 'alkaline_electrolyte', label: 'Hydroxide (OH-) Ionic Flow', type: 'fluid', bidirectional: true },
      { from: 'alkaline_electrolyte', to: 'iron_metal_anode', label: 'Oxidation / Reduction Reaction', type: 'matter', bidirectional: true },
      { from: 'iron_metal_anode', to: 'bidirectional_inverter', label: 'Electron (e-) Current Flow', type: 'electricity', bidirectional: true },
      { from: 'air_breathing_cathode', to: 'bidirectional_inverter', label: 'Circuit Return Conduit', type: 'electricity', bidirectional: true }
    ]
  },

  // ── 2. PEROVSKITE TANDEM SOLAR ───────────────────────────────────────────
  perovskite_tandem_solar: {
    technologyId: 'perovskite_tandem_solar',
    title: 'Monolithic Perovskite-Silicon Tandem Architecture',
    subtitle: 'Dual-bandgap photonic stack capturing blue and infrared wavelengths with >30% commercial module efficiency.',
    modes: [
      {
        id: 'full_sun',
        label: 'Full Spectrum Sunlight (32% Efficiency Peak)',
        description: 'Perovskite top layer absorbs high-energy blue/green photons; Silicon bottom layer absorbs remaining red/infrared photons.',
        efficiencyIndicator: '32.4% Tandem Efficiency vs 22% Standard Silicon',
        activeFlows: ['blue_photons', 'infrared_photons', 'tunnel_electrons']
      },
      {
        id: 'diffuse_light',
        label: 'Cloudy / Low-Light Diffuse Response',
        description: 'Perovskite thin-film maintains high open-circuit voltage under low light, generating 25% more morning and winter energy.',
        efficiencyIndicator: 'Superior Low-Angle & Diffuse Light Capture',
        activeFlows: ['diffuse_photons', 'tunnel_electrons']
      }
    ],
    nodes: [
      {
        id: 'antireflective_coating',
        name: 'Textured Anti-Reflective & Barrier Layer',
        category: 'Optical & Environmental Barrier',
        x: 18,
        y: 20,
        icon: 'Eye',
        summary: 'Nanotextured magnesium fluoride and atomic-layer-deposited metal oxide hermetically sealing the cell against moisture and oxygen.',
        operatingValue: '< 1.5% Optical Reflection · 10^-4 g/m2/day WVTR',
        materials: 'MgF2, Al2O3 ALD Barrier Coating',
        failureMode: 'Micro-crack ingress of humidity causing rapid lead-halide crystal decomposition.',
        frontierBottleneck: 'Achieving 25-year moisture impermeability on flexible and large-area glass.',
        activeResearch: 'Inorganic-organic hybrid molecular sealants with self-healing elastic polymers (NREL).'
      },
      {
        id: 'perovskite_top_cell',
        name: 'Wide-Bandgap Perovskite Top Absorber (1.7 eV)',
        category: 'High-Energy Photonic Absorber',
        x: 50,
        y: 20,
        icon: 'Sun',
        summary: 'Synthetic organometal halide crystal (CsFAPbIBr) absorbing high-energy ultraviolet, blue, and green photons with near-zero thermal loss.',
        operatingValue: 'Voc = 1.32V · Absorbs 300nm - 750nm Spectrum',
        materials: 'Cesium Formamidinium Lead Halide Crystals',
        failureMode: 'Phase segregation into iodide-rich and bromide-rich domains under heat and intense light.',
        frontierBottleneck: 'Intrinsic ion migration under continuous operating electric field.',
        activeResearch: 'Self-assembled monolayers (SAMs) and 2D/3D perovskite heterostructures passivating crystal defects.'
      },
      {
        id: 'recombination_tunnel_junction',
        name: 'Transparent Recombination Tunnel Layer',
        category: 'Inter-Cell Electronic Conduit',
        x: 50,
        y: 55,
        icon: 'Layers',
        summary: 'Ultra-thin transparent conductive oxide (ITO/IZO) electrically connecting the top and bottom cells with zero optical absorption loss.',
        operatingValue: 'Sheet Resistance < 30 Ohm/sq · >95% Optical Transmittance',
        materials: 'Indium Zinc Oxide (IZO) / Nanocrystalline Silicon',
        failureMode: 'Sputtering damage to delicate perovskite underneath during industrial deposition.',
        frontierBottleneck: 'Minimizing parasitic series resistance without using scarce Indium metal.',
        activeResearch: 'Atomic-layer-deposited transparent conducting oxides and conductive polymer interlayers.'
      },
      {
        id: 'silicon_bottom_cell',
        name: 'Narrow-Bandgap Silicon Bottom Cell (1.1 eV)',
        category: 'Infrared Photonic Absorber',
        x: 50,
        y: 85,
        icon: 'Cpu',
        summary: 'Industrial n-type TOPCon or Heterojunction (HJT) silicon wafer absorbing transmitted red and near-infrared photons.',
        operatingValue: 'Voc = 0.74V · Absorbs 750nm - 1,150nm Photons',
        materials: 'Monocrystalline Silicon Wafer + Passivated Contacts',
        failureMode: 'Mechanical thermal expansion mismatch with top perovskite layer under desert cycling.',
        frontierBottleneck: 'Compatible wafer texturing matching liquid perovskite wet-coating processes.',
        activeResearch: 'Sub-micron conformal vapor-phase slot-die perovskite deposition on pyramid-textured silicon.'
      }
    ],
    conduits: [
      { from: 'antireflective_coating', to: 'perovskite_top_cell', label: 'Filtered Solar Radiance', type: 'photons' },
      { from: 'perovskite_top_cell', to: 'recombination_tunnel_junction', label: 'High-Energy Photoelectrons', type: 'electricity' },
      { from: 'recombination_tunnel_junction', to: 'silicon_bottom_cell', label: 'Infrared Photons & Electron Exchange', type: 'photons' }
    ]
  },

  // ── 3. ENHANCED GEOTHERMAL EGS ───────────────────────────────────────────
  enhanced_geothermal_egs: {
    technologyId: 'enhanced_geothermal_egs',
    title: 'Closed-Loop Enhanced Geothermal (EGS) Reservoir',
    subtitle: 'Deep horizontal multi-stage stimulated fracture radiator generating 24/7 firm clean baseload steam.',
    modes: [
      {
        id: 'baseload',
        label: '24/7 Firm Baseload Generation (95% Capacity Factor)',
        description: 'Cold fluid pumped down 3.5 km injection well; fluid superheats to 420°F through fracture network and returns up production well.',
        efficiencyIndicator: '10 MW Electric Output · Zero Intermittency',
        activeFlows: ['cold_injection', 'fracture_superheat', 'steam_turbine']
      },
      {
        id: 'load_following',
        label: 'Flexible Grid Peaking Mode',
        description: 'Subsurface reservoir acts as an underground thermal battery, modulating flow to deliver peak power during evening grid surges.',
        efficiencyIndicator: 'Flexible Dispatch Shaving Evening Grid Peaker Spikes',
        activeFlows: ['pressurized_storage', 'peaking_discharge']
      }
    ],
    nodes: [
      {
        id: 'injection_wellhead',
        name: 'High-Pressure Injection Wellhead',
        category: 'Surface Pumping Station',
        x: 18,
        y: 20,
        icon: 'Droplets',
        summary: 'High-pressure multi-stage pumps injecting filtered working fluid down 10,000+ feet into impermeable crystalline granite rock.',
        operatingValue: '60°F Fluid · 2,500 psi Pumping Pressure',
        materials: 'High-Strength Corrosion-Resistant Casing Steel',
        failureMode: 'Silica scale and mineral precipitation plugging wellhead perforations.',
        frontierBottleneck: 'High pumping parasitic power consumption if subsurface impedance is high.',
        activeResearch: 'Supercritical CO2 working fluid loops with zero freshwater consumption (DOE GTO).'
      },
      {
        id: 'subsurface_fracture_network',
        name: 'Multi-Stage Stimulated Granite Radiator',
        category: 'Subsurface Heat Exchanger (3.5 km Depth)',
        x: 50,
        y: 60,
        icon: 'Flame',
        summary: 'Engineered horizontal fracture fairway in 420°F (215°C) basement granite acting as an enormous underground thermal radiator.',
        operatingValue: '420°F (215°C) Hot Dry Granite · 3.5 km Depth',
        materials: 'Natural Crystalline Basement Granite + Proppants',
        failureMode: 'Thermal short-circuiting where fluid channels through a single fracture, rapidly cooling the path.',
        frontierBottleneck: 'Seismic slip monitoring and ensuring uniform fluid distribution across hundreds of fractures.',
        activeResearch: 'Fiber-optic Distributed Acoustic Sensing (DAS) mapping micro-fracture thermal drawdown in real time.'
      },
      {
        id: 'production_wellhead',
        name: 'High-Enthalpy Production Wellhead',
        category: 'Thermal Extraction Lateral',
        x: 82,
        y: 20,
        icon: 'Gauge',
        summary: 'Horizontal collection lateral capturing superheated brine at high flow rates and transporting it to the surface binary power plant.',
        operatingValue: '390°F - 415°F Superheated Liquid Brine',
        materials: 'Insulated Vacuum Casing Tubing',
        failureMode: 'Casing shearing and elastomer pack-off degradation from thermal shock expansion.',
        frontierBottleneck: 'Drilling rate-of-penetration (ROP) in ultra-hard abrasive granite.',
        activeResearch: 'Polycrystalline Diamond Compact (PDC) hybrid drill bits and particle impact drilling.'
      },
      {
        id: 'binary_orc_power_plant',
        name: 'Binary Organic Rankine Cycle (ORC) Generator',
        category: 'Surface Power Conversion',
        x: 50,
        y: 15,
        icon: 'Zap',
        summary: 'Closed-loop heat exchanger transferring geothermal brine heat to vaporize isopentane, driving an electric turbine generator.',
        operatingValue: '10 - 20 MW Electric Generation · >95% Uptime',
        materials: 'Titanium Shell-and-Tube Heat Exchangers',
        failureMode: 'Organic working fluid thermal cracking and condenser vacuum leaks.',
        frontierBottleneck: 'Thermodynamic Carnot efficiency limits on medium-temperature (150C-200C) fluids.',
        activeResearch: 'Supercritical CO2 Brayton power turbines delivering 50% higher thermodynamic efficiency than steam.'
      }
    ],
    conduits: [
      { from: 'injection_wellhead', to: 'subsurface_fracture_network', label: 'High-Pressure Cold Fluid (3.5 km Deep)', type: 'fluid' },
      { from: 'subsurface_fracture_network', to: 'production_wellhead', label: 'Superheated Geothermal Brine (420°F)', type: 'heat' },
      { from: 'production_wellhead', to: 'binary_orc_power_plant', label: 'High-Enthalpy Thermal Transfer', type: 'heat' },
      { from: 'binary_orc_power_plant', to: 'injection_wellhead', label: 'Closed-Loop Cooled Fluid Return', type: 'fluid' }
    ]
  },

  // ── 4. DIRECT AIR CAPTURE ────────────────────────────────────────────────
  direct_air_capture_dac: {
    technologyId: 'direct_air_capture_dac',
    title: 'Direct Air Capture & Geologic Mineralization Loop',
    subtitle: 'Chemical sorbent air contactors removing ambient CO2 with permanent Class VI basalt mineralization.',
    modes: [
      {
        id: 'capture_phase',
        label: 'Adsorption Phase (Atmospheric CO2 Trapping)',
        description: 'Massive axial fans push 420 ppm ambient air across chemical solid sorbent monoliths, chemically binding CO2 molecules.',
        efficiencyIndicator: '75-85% Capture Fraction from Ambient Air',
        activeFlows: ['air_inflow', 'co2_binding', 'purified_air_vent']
      },
      {
        id: 'desorption_phase',
        label: 'Desorption & Mineralization Phase',
        description: 'Chamber is sealed and heated to 100°C; pure CO2 gas is stripped, compressed to 150 bar, and injected into deep basalt rock to turn to stone.',
        efficiencyIndicator: 'Permanent >10,000 Year Solid Mineral Sequestration',
        activeFlows: ['steam_heat', 'co2_compression', 'basalt_injection']
      }
    ],
    nodes: [
      {
        id: 'air_contactor_fans',
        name: 'High-Volume Air Contactor Array',
        category: 'Atmospheric Inflow Interface',
        x: 18,
        y: 45,
        icon: 'Wind',
        summary: 'Low-energy industrial fan banks moving thousands of cubic meters of ambient atmospheric air across chemical filter arrays.',
        operatingValue: '420 ppm Ambient CO2 Concentration · Low Pressure Drop',
        materials: 'Composite Fan Blades & Aerodynamic Cowlings',
        failureMode: 'Fan motor energy consumption if aerodynamic pressure drop is too high.',
        frontierBottleneck: 'Moving 2.5 million cubic meters of air per ton of CO2 captured with minimal fan wattage.',
        activeResearch: 'Passive wind-driven aerodynamic contactor towers eliminating electric fan motors entirely.'
      },
      {
        id: 'solid_sorbent_matrix',
        name: 'Structured Solid Amine / MOF Filter Matrix',
        category: 'Chemical Molecular Sieve',
        x: 50,
        y: 45,
        icon: 'Layers',
        summary: 'Nanoporous Metal-Organic Frameworks (MOFs) or amine-impregnated silica honeycombs that selectively grab CO2 molecules.',
        operatingValue: '2.0 - 4.5 mmol CO2 / gram sorbent capacity',
        materials: 'Branched Polyethyleneimine (PEI) on Silica Honeycomb',
        failureMode: 'Oxidative degradation of amine groups and competitive moisture co-adsorption.',
        frontierBottleneck: 'Thermal energy required to regenerate the sorbent (1,500-2,500 kWh/ton).',
        activeResearch: 'Moisture-swing and electrochemical pH-swing sorbents releasing CO2 with zero thermal heat.'
      },
      {
        id: 'steam_desorption_compressor',
        name: 'Low-Temperature Desorption & 150-Bar Compressor',
        category: 'Thermal Stripping & Gas Compression',
        x: 82,
        y: 45,
        icon: 'Gauge',
        summary: 'Vacuum steam heating module (100°C) releasing 98% pure CO2 gas, feeding a multi-stage compressor converting gas to supercritical fluid.',
        operatingValue: '100°C Low-Grade Heat · 150-bar Supercritical CO2',
        materials: 'Corrosion-Resistant Stainless Steel Stages',
        failureMode: 'High energy consumption of multi-stage compressors and steam boiler inefficiencies.',
        frontierBottleneck: 'Integrating cheap geothermal or nuclear waste heat to avoid grid electricity competition.',
        activeResearch: 'Direct electrochemical CO2 compressors with zero moving mechanical pistons.'
      },
      {
        id: 'subsurface_basalt_injection',
        name: 'Class VI Deep Basalt Mineralization Well',
        category: 'Permanent Geologic Storage (1-2 km)',
        x: 82,
        y: 85,
        icon: 'ShieldCheck',
        summary: 'Subterranean injection well dissolving CO2 in water and pumping it into reactive basalt volcanic rock where it turns into solid limestone in 24 months.',
        operatingValue: '1,500m Depth · Rapid Solid Carbonate Mineralization',
        materials: 'Class VI Corrosion-Resistant Casing',
        failureMode: 'Wellbore micro-annulus leaks and mineral scaling prematurely clogging injection pore space.',
        frontierBottleneck: 'EPA Class VI permit review timelines (typically 3-5 years per well).',
        activeResearch: 'In-situ acoustic monitoring verifying rock mineralization permanence without tracer gases.'
      }
    ],
    conduits: [
      { from: 'air_contactor_fans', to: 'solid_sorbent_matrix', label: 'Ambient Air (420 ppm CO2)', type: 'fluid' },
      { from: 'solid_sorbent_matrix', to: 'steam_desorption_compressor', label: 'Desorbed 98% Pure CO2 Stream', type: 'matter' },
      { from: 'steam_desorption_compressor', to: 'subsurface_basalt_injection', label: 'Supercritical CO2 (150 bar) to Rock', type: 'matter' }
    ]
  },

  // ── 5. MEGAWATT CHARGING SYSTEMS (MCS) ──────────────────────────────────
  megawatt_charging_systems_mcs: {
    technologyId: 'megawatt_charging_systems_mcs',
    title: 'Megawatt Charging System (MCS 3.75 MW) Architecture',
    subtitle: 'Medium-voltage utility interconnect with buffer battery, SiC converters, and liquid-cooled conductive handle.',
    modes: [
      {
        id: 'peak_charge',
        label: 'Ultra-Fast Peak Charge (3,000A / 1,250V)',
        description: 'BESS buffer delivers 2 MW while grid supplies 1.75 MW; active dielectric coolant circulates through the charging pin to hold temperature under 60°C.',
        efficiencyIndicator: '3.75 MW Peak Throughput · 20-30 Min Full Charge',
        activeFlows: ['grid_feed', 'bess_discharge', 'liquid_cable_flow']
      },
      {
        id: 'depot_trickle',
        label: 'Depot Fleet Balancing & V2G Mode',
        description: 'Multi-truck depot throttles power down during grid congestion and provides bidirectional grid stabilization.',
        efficiencyIndicator: 'Bi-Directional V2G Fleet Grid Support',
        activeFlows: ['v2g_return', 'grid_support']
      }
    ],
    nodes: [
      {
        id: 'mv_substation_tie',
        name: 'Medium-Voltage (13.8 kV) Grid Tie',
        category: 'Grid Interconnection Stage',
        x: 18,
        y: 45,
        icon: 'Zap',
        summary: 'Direct connection to utility distribution circuit with dedicated step-down transformer.',
        operatingValue: '13.8 kV AC Input · 4.5 MVA Rating',
        materials: 'Copper Windings & FR3 Biodegradable Dielectric Oil',
        failureMode: 'Substation thermal overload during multi-truck simultaneous charging.',
        frontierBottleneck: 'Multi-year utility interconnection queues for 10+ MW depot requests.',
        activeResearch: 'Solid-State Transformers (SST) reducing substation footprint by 60%.'
      },
      {
        id: 'bess_buffer_station',
        name: 'Behind-the-Meter 2 MWh BESS Buffer',
        category: 'Peak Demand Shaving',
        x: 50,
        y: 20,
        icon: 'BatteryCharging',
        summary: 'Lithium Iron Phosphate (LFP) stationary storage buffering instantaneous 3.75 MW spikes to avoid utility demand charges.',
        operatingValue: '2 MWh Capacity · 2C Peak Discharge Rate',
        materials: 'LFP Prismatic Cells + Liquid Glycol Thermal Loop',
        failureMode: 'Cell degradation from high C-rate micro-cycling.',
        frontierBottleneck: 'Balancing buffer battery CapEx against utility demand tariff savings.',
        activeResearch: 'Sodium-ion high-rate stationary buffers with zero critical minerals.'
      },
      {
        id: 'sic_power_converters',
        name: 'Silicon Carbide (SiC) 1,250V Power Converter',
        category: 'High-Frequency DC Conversion',
        x: 50,
        y: 70,
        icon: 'Cpu',
        summary: 'High-voltage SiC MOSFET power blocks converting AC to DC with >98.5% efficiency and microsecond short-circuit protection.',
        operatingValue: '1,250V DC · 3,000A Output · >98.5% Efficiency',
        materials: 'Silicon Carbide (SiC) Power Semiconductor Modules',
        failureMode: 'High-temperature gate oxide breakdown under repetitive high-amperage transients.',
        frontierBottleneck: 'SiC wafer supply constraints and thermal dissipation at 50 kW waste heat.',
        activeResearch: 'Direct substrate liquid impingement cooling on SiC power dies.'
      },
      {
        id: 'liquid_cooled_connector',
        name: 'Active Liquid-Cooled MCS Handle & Cable',
        category: 'High-Current Conductive Interface',
        x: 82,
        y: 45,
        icon: 'Droplets',
        summary: 'Ergonomic CharIN-compliant MCS connector with internal dielectric fluid cooling channels preventing contact pin melting.',
        operatingValue: 'Max 3,000A DC Continuous · < 60°C Pin Temp',
        materials: 'Silver-Plated Copper Pins + Dielectric Coolant Tube',
        failureMode: 'Micro-arcing and pin mechanical wear after 10,000 insertion cycles.',
        frontierBottleneck: 'Cable ergonomics and weight for human drivers without robotic assist.',
        activeResearch: 'Automated robotic underbody conductive charging plates with zero manual handling.'
      }
    ],
    conduits: [
      { from: 'mv_substation_tie', to: 'bess_buffer_station', label: '13.8 kV Grid Energy Intake', type: 'electricity' },
      { from: 'mv_substation_tie', to: 'sic_power_converters', label: 'Medium-Voltage AC Feed', type: 'electricity' },
      { from: 'bess_buffer_station', to: 'sic_power_converters', label: 'Instantaneous High-Power Discharge', type: 'electricity' },
      { from: 'sic_power_converters', to: 'liquid_cooled_connector', label: '3.75 MW Direct Current Bus (1,250V / 3,000A)', type: 'electricity' }
    ]
  },

  // ── 6. SMALL MODULAR REACTORS (SMR) ──────────────────────────────────────
  smr_advanced_nuclear: {
    technologyId: 'smr_advanced_nuclear',
    title: 'High-Temperature Gas SMR & Microreactor Architecture',
    subtitle: 'TRISO pebble-bed core with passive gravity-driven safety and 750°C clean steam co-generation.',
    modes: [
      {
        id: 'power_heat',
        label: 'Combined Electric & Clean Industrial Heat (750°C)',
        description: 'Helium primary coolant extracts 750°C heat from TRISO core, splitting energy between sCO2 turbine (80 MWe) and clean hydrogen/steam export.',
        efficiencyIndicator: '80 MWe Power + 750°C Clean Process Heat',
        activeFlows: ['helium_loop', 'sco2_turbine', 'industrial_steam']
      },
      {
        id: 'passive_shutdown',
        label: 'Walk-Away Passive Safety Mode',
        description: 'Zero operator action or backup diesel required; natural decay heat radiates passively into atmospheric air through reactor vessel wall.',
        efficiencyIndicator: '100% Inherent Meltdown-Proof Physics',
        activeFlows: ['passive_radiation', 'natural_air_draft']
      }
    ],
    nodes: [
      {
        id: 'triso_fuel_core',
        name: 'TRISO Pebble-Bed Reactor Core',
        category: 'Nuclear Fission Core',
        x: 18,
        y: 45,
        icon: 'Atom',
        summary: 'Spherical fuel pebbles containing microscopic uranium oxycarbide kernels encased in triple silicon carbide shells that cannot melt below 1,600°C.',
        operatingValue: '750°C - 850°C Helium Coolant Temp · 200 MWth',
        materials: 'TRISO Fuel (SiC + Pyrolytic Carbon) in Graphite Matrix',
        failureMode: 'Neutron irradiation embrittlement of graphite moderator blocks over 60 years.',
        frontierBottleneck: 'Domestic High-Assay Low-Enriched Uranium (HALEU 19.75% U-235) enrichment supply.',
        activeResearch: 'Centrifuge enrichment facilities and alternative thorium-fueled pebble cycles (DOE NE).'
      },
      {
        id: 'helium_gas_loop',
        name: 'Primary Helium Closed Loop',
        category: 'Primary Thermal Transport',
        x: 50,
        y: 20,
        icon: 'Wind',
        summary: 'Inert helium gas circulated under 50 bar pressure transferring nuclear core heat to the secondary heat exchanger with zero corrosion.',
        operatingValue: '50 bar Helium · 750°C Outlet / 350°C Return',
        materials: 'Inconel 617 High-Temperature Nickel Superalloy',
        failureMode: 'Helium micro-leakage through rotating blower seals.',
        frontierBottleneck: 'Magnetic bearing durability and helium gas purification from graphite dust.',
        activeResearch: 'Supercritical helium circulators with hermetic canned magnetic bearings.'
      },
      {
        id: 'intermediate_heat_exchanger',
        name: 'Printed-Circuit Heat Exchanger (PCHE)',
        category: 'Thermal Barrier & Isolation',
        x: 50,
        y: 70,
        icon: 'Flame',
        summary: 'Diffusion-bonded micro-channel heat exchanger completely isolating the nuclear primary loop from commercial process steam.',
        operatingValue: '98% Thermal Effectiveness · High Delta-T',
        materials: 'Diffusion-Bonded Haynes 230 Superalloy',
        failureMode: 'Creep fatigue at micro-channel header junctions under thermal transients.',
        frontierBottleneck: 'ASME Section III nuclear code qualification for additive manufactured micro-channels.',
        activeResearch: 'Laser-welded ceramic and silicon carbide compact heat exchangers.'
      },
      {
        id: 'sco2_turbine_generator',
        name: 'Supercritical CO2 (sCO2) Power Block',
        category: 'High-Efficiency Generation',
        x: 82,
        y: 45,
        icon: 'Zap',
        summary: 'Compact closed-loop sCO2 Brayton cycle turbine providing 48% thermal-to-electric efficiency at 1/10th the size of a steam turbine.',
        operatingValue: '80 MWe Output · 48% Thermal Efficiency',
        materials: 'High-Nickel Rotor Alloys & sCO2 Turbomachinery',
        failureMode: 'Rotor tip seal leakage and aerodynamic thrust load imbalances.',
        frontierBottleneck: 'High capital cost of high-pressure sCO2 turbomachinery manufacturing.',
        activeResearch: 'Standardized factory-fabricated skid-mounted sCO2 power blocks.'
      }
    ],
    conduits: [
      { from: 'triso_fuel_core', to: 'helium_gas_loop', label: '750°C Superheated Helium Gas', type: 'heat' },
      { from: 'helium_gas_loop', to: 'intermediate_heat_exchanger', label: 'High-Temperature Heat Exchange', type: 'heat' },
      { from: 'intermediate_heat_exchanger', to: 'sco2_turbine_generator', label: 'Isolated Secondary Working Fluid', type: 'matter' },
      { from: 'intermediate_heat_exchanger', to: 'triso_fuel_core', label: 'Cooled Helium Return (350°C)', type: 'fluid' }
    ]
  },

  // ── 7. GRID-ENHANCING TECHNOLOGIES (GETS) ────────────────────────────────
  grid_enhancing_technologies: {
    technologyId: 'grid_enhancing_technologies',
    title: 'Grid-Enhancing Technologies (GETs) & Dynamic Rating',
    subtitle: 'Conductor telemetry, modular power flow controllers, and topology optimization unlocking 10-40% transmission headroom.',
    modes: [
      {
        id: 'windy_event',
        label: 'High-Wind Dynamic Surge (+35% Capacity)',
        description: 'Strong ambient wind cools overhead conductor lines, dynamically elevating transmission ampacity from 1,000A to 1,350A in real time.',
        efficiencyIndicator: '+35% Capacity Unlocked with $0 New Steel Towers',
        activeFlows: ['wind_cooling', 'telemetry_stream', 'power_surge']
      },
      {
        id: 'flow_redirection',
        label: 'Modular Power Flow Injection Mode',
        description: 'Series reactance controllers inject virtual impedance, pushing bottlenecked power away from overloaded lines onto underutilized paths.',
        efficiencyIndicator: 'Autonomous Interconnection Bottleneck Relief',
        activeFlows: ['impedance_shift', 'load_balance']
      }
    ],
    nodes: [
      {
        id: 'dynamic_line_sensors',
        name: 'Conductor Dynamic Line Rating (DLR) Sensors',
        category: 'Real-Time Physics Telemetry',
        x: 18,
        y: 45,
        icon: 'Activity',
        summary: 'Clamped autonomous optical/acoustic sensors measuring conductor sag, core temperature, solar radiation, and local wind vectors.',
        operatingValue: 'Real-Time Conductor Temp & Clearance Telemetry',
        materials: 'Solar-Powered Sensor Pod with Cellular/Mesh Uplink',
        failureMode: 'Sensor battery failure and line ice accumulation blocking optical sensors.',
        frontierBottleneck: 'Sensor density calibration across variable terrain and microclimates.',
        activeResearch: 'Satellite SAR interferometry and drone LiDAR validating ground clearances.'
      },
      {
        id: 'modular_power_flow_controller',
        name: 'Modular Static Synchronous Series Compensator (m-SSSC)',
        category: 'Active Impedance Injection',
        x: 50,
        y: 20,
        icon: 'Sliders',
        summary: 'Series-injected single-phase inverter modules hung directly on high-voltage transmission lines that inject inductive/capacitive voltage.',
        operatingValue: '0 - 5 Ohm Dynamic Variable Reactance Injection',
        materials: 'Insulated High-Voltage IGBT Valve Assembly',
        failureMode: 'Bypass switch failure during severe lightning fault currents.',
        frontierBottleneck: 'Grid protection coordination and anti-resonance dampening.',
        activeResearch: 'Autonomous peer-to-peer decentralized impedance routing algorithms.'
      },
      {
        id: 'dynamic_ems_engine',
        name: 'Real-Time Dynamic ACCC & EMS Orchestrator',
        category: 'ISO Market Telemetry Engine',
        x: 50,
        y: 75,
        icon: 'Cpu',
        summary: 'High-frequency control software ingesting DLR physics and updating 5-minute ISO dispatch limits in market engines (FERC Order 881).',
        operatingValue: '5-Minute Ahead Lookahead Transmission Ratings',
        materials: 'Cloud / On-Premise High-Assurance Compute',
        failureMode: 'Cyber-security communication dropouts defaulting line back to conservative static ratings.',
        frontierBottleneck: 'Legacy SCADA system software latency and utility risk aversion.',
        activeResearch: 'AI contingency lookahead models predicting conductor thermal limits 24 hours in advance.'
      },
      {
        id: 'transmission_substation_node',
        name: '345 kV Bulk Power Interconnection Substation',
        category: 'Bulk Grid Export',
        x: 82,
        y: 45,
        icon: 'Zap',
        summary: 'Major grid interchange delivering renewable power from remote wind/solar farms directly into urban load centers without curtailment.',
        operatingValue: '345 kV / 2,000 MVA Flow Capacity',
        materials: 'Gas-Insulated Switchgear (GIS) with SF6-Free Gas',
        failureMode: 'Transformer hotspot degradation during prolonged elevated ampacity.',
        frontierBottleneck: 'Substation terminal equipment (breakers, disconnects) becoming the new rating bottleneck.',
        activeResearch: 'Substation terminal equipment uprating and dynamic transformer thermal monitors.'
      }
    ],
    conduits: [
      { from: 'dynamic_line_sensors', to: 'dynamic_ems_engine', label: 'Real-Time Wind/Temp Physics Telemetry', type: 'electricity' },
      { from: 'dynamic_ems_engine', to: 'modular_power_flow_controller', label: 'Impedance Dispatch Commands', type: 'electricity' },
      { from: 'modular_power_flow_controller', to: 'transmission_substation_node', label: 'Optimized 345 kV Power Routing', type: 'electricity' }
    ]
  },

  // ── 8. LIQUID COOLING FOR AI DATA CENTERS ────────────────────────────────
  ai_datacenter_liquid_cooling: {
    technologyId: 'ai_datacenter_liquid_cooling',
    title: 'Direct-to-Chip & Immersion AI Thermal Architecture',
    subtitle: 'Micro-channel cold plates, dielectric fluid loops, CDUs, and municipal district heat integration.',
    modes: [
      {
        id: 'high_workload',
        label: '100 kW/Rack AI Training Workload (1,000W GPUs)',
        description: 'Dielectric fluid pumped directly across micro-channel copper cold plates on 1,000W GPU dies; warm water exits at 60°C for district heating.',
        efficiencyIndicator: '1.03 PUE · 100 kW/Rack Density · Zero Evaporative Water',
        activeFlows: ['cold_fluid_in', 'gpu_heat_pick', 'district_heat_export']
      },
      {
        id: 'low_power_idle',
        label: 'Low-Power Idle & Free Cooling Mode',
        description: 'Variable speed pumps ramp down to 20% power; ambient outdoor dry coolers reject remaining heat without chillers.',
        efficiencyIndicator: 'Sub-Watt Pump Parasitics',
        activeFlows: ['dry_cooler_loop']
      }
    ],
    nodes: [
      {
        id: 'gpu_cold_plate',
        name: 'Micro-Channel Copper GPU Cold Plate',
        category: 'Die-Level Heat Transduction',
        x: 18,
        y: 45,
        icon: 'Cpu',
        summary: 'Directly mounted precision micro-machined copper cold plate with sub-50-micron fins extracting 1,000+ Watts from AI silicon dies.',
        operatingValue: '1,000W / GPU · 0.03 °C-cm2/W Thermal Resistance',
        materials: 'Oxygen-Free High-Conductivity (OFHC) Copper & Nickel Plating',
        failureMode: 'Micro-channel clogging from coolant particulate and galvanic corrosion.',
        frontierBottleneck: 'Thermal interface material (TIM) pump-out and dry-out under 90°C thermal cycles.',
        activeResearch: 'Liquid metal (gallium-indium) and diamond-composite thermal interface layers.'
      },
      {
        id: 'rack_manifold_cdu',
        name: 'Coolant Distribution Unit (CDU) & Pumping Station',
        category: 'Hydronic Flow Management',
        x: 50,
        y: 20,
        icon: 'Droplets',
        summary: 'Redundant variable-speed pump skids, particle de-ionizers, and liquid-to-liquid heat exchangers managing 40-rack server clusters.',
        operatingValue: '50 gpm Liquid Flow · N+1 Pump Redundancy',
        materials: '316L Stainless Steel Manifolds & Dripless Quick Connects',
        failureMode: 'Seal degradation and quick-disconnect fitting micro-leaks.',
        frontierBottleneck: 'Pumping parasitic power consumption when scaling to 100,000 GPU mega-clusters.',
        activeResearch: 'Two-phase evaporative cold plates utilizing dielectric refrigerants with near-zero pumping work.'
      },
      {
        id: 'district_heat_recovery',
        name: 'Municipal District Thermal Exchanger',
        category: 'Waste Heat Circularity',
        x: 82,
        y: 20,
        icon: 'Flame',
        summary: 'Industrial plate heat exchanger exporting 60°C (140°F) hot water to municipal district heating networks or commercial greenhouses.',
        operatingValue: '60°C (140°F) Clean Hot Water Export',
        materials: 'Titanium Brazed Plate Heat Exchanger',
        failureMode: 'Seasonal mismatch where district heat demand drops during summer months.',
        frontierBottleneck: 'Proximity of data centers to municipal heat customers.',
        activeResearch: 'Seasonal borehole thermal energy storage (BTES) storing data center summer heat for winter heating.'
      },
      {
        id: 'dry_cooler_array',
        name: 'Zero-Water Atmospheric Dry Cooler Array',
        category: 'Atmospheric Heat Rejection',
        x: 82,
        y: 75,
        icon: 'Wind',
        summary: 'Roof-mounted closed-loop fin-fan coolers rejecting heat directly to ambient air with zero potable water consumption.',
        operatingValue: 'Zero Evaporative Water Consumption (WUE = 0.0)',
        materials: 'Micro-Channel Aluminum Coils & EC Fans',
        failureMode: 'Fan motor power consumption during 105°F summer heatwaves.',
        frontierBottleneck: 'Maintaining 45°C supply water when ambient desert air reaches 45°C.',
        activeResearch: 'Adiabatic assist misting nozzles that activate only above 100°F outdoor ambient temperatures.'
      }
    ],
    conduits: [
      { from: 'gpu_cold_plate', to: 'rack_manifold_cdu', label: '60°C Warm Liquid Return', type: 'heat' },
      { from: 'rack_manifold_cdu', to: 'district_heat_recovery', label: 'High-Grade Thermal Export', type: 'heat' },
      { from: 'rack_manifold_cdu', to: 'dry_cooler_array', label: 'Atmospheric Heat Rejection', type: 'heat' },
      { from: 'rack_manifold_cdu', to: 'gpu_cold_plate', label: '40°C Conditioned Coolant Supply', type: 'fluid' }
    ]
  }
};

// ==============================================================================
// 2. FALLBACK PROCEDURAL GENERATOR FOR ALL REMAINING TECHNOLOGIES
// ==============================================================================

function generateProceduralDiagram(techId: string, techName: string, categoryName: string, dbSubsystems?: any[]): TechDiagramConfig {
  let nodes: DiagramNode[] = [
    {
      id: 'subsystem_input',
      name: 'Primary Energy / Feedstock Ingestion Interface',
      category: 'Input Stage',
      x: 18,
      y: 50,
      icon: 'Droplets',
      summary: `Primary conversion interface ingesting raw energy vectors, fuel precursors, or power inputs for ${techName}.`,
      operatingValue: 'Nominal Input Rating · High Selectivity',
      materials: 'High-Purity Corrosion-Resistant Alloys',
      failureMode: 'Interface fouling and mechanical friction under continuous duty.',
      frontierBottleneck: 'Minimizing parasitic ingestion and conversion resistance losses.',
      activeResearch: 'Nanoscale surface coatings and autonomous algorithmic flow control.'
    },
    {
      id: 'subsystem_core',
      name: 'Active Reaction Core / Transduction Stage',
      category: 'Core Physics Stage',
      x: 50,
      y: 50,
      icon: 'Atom',
      summary: `The central thermodynamic, chemical, or electromagnetic core executing the primary energy transformation.`,
      operatingValue: 'Peak Conversion Efficiency Stage',
      materials: 'Advanced Engineered Composite / Semiconductor',
      failureMode: 'Thermal fatigue and micro-structural degradation under cyclic stress.',
      frontierBottleneck: 'Overcoming fundamental physics Carnot / Coulombic / Shockley-Queisser limits.',
      activeResearch: 'Quantum-simulated materials, high-entropy alloys, and defect passivation.'
    },
    {
      id: 'subsystem_output',
      name: 'Power / Product Export & Grid Interface',
      category: 'Output Stage',
      x: 82,
      y: 50,
      icon: 'Zap',
      summary: `Conditioning, compression, or power electronics stage delivering energy innovation or materials to the grid/off-taker.`,
      operatingValue: 'Standardized Commercial Output Spec',
      materials: 'Silicon Carbide / High-Voltage Power Components',
      failureMode: 'Grid interconnection transients and thermal overheating during peak export.',
      frontierBottleneck: 'Interconnection compliance (IEEE 2800 / FERC) and balance-of-plant CapEx.',
      activeResearch: 'Modular plug-and-play power electronics with integrated microgrid telemetry.'
    }
  ];

  if (dbSubsystems && dbSubsystems.length >= 3) {
    nodes = dbSubsystems.map((s, idx) => ({
      id: s.id || `node_${idx}`,
      name: s.name,
      category: s.category,
      x: s.x || (idx === 0 ? 18 : idx === 1 ? 50 : 82),
      y: s.y || 50,
      icon: s.icon || (idx === 0 ? 'Droplets' : idx === 1 ? 'Atom' : 'Zap'),
      summary: s.summary,
      operatingValue: s.operatingValue || 'Nominal Subsystem Rating',
      materials: s.materials || 'Advanced Engineered Alloys & Polymers',
      failureMode: s.failureMode || 'Thermal degradation and cycle wear',
      frontierBottleneck: s.frontierBottleneck || 'Minimizing conversion losses',
      activeResearch: s.activeResearch || 'Materials optimization'
    }));
  }

  const conduits = [
    { from: nodes[0].id, to: nodes[1].id, label: 'Primary Energy Vector Conduit', type: 'matter' as const },
    { from: nodes[1].id, to: nodes[nodes.length - 1].id, label: 'Conditioned Power / Product Flow', type: 'electricity' as const }
  ];

  return {
    technologyId: techId,
    title: `${techName} System Topology`,
    subtitle: `Subsystem interaction architecture and energy flow dynamics for ${categoryName}.`,
    modes: [
      {
        id: 'primary_operation',
        label: 'Active Nominal Operation (100% Rated Output)',
        description: `Nominal operating cycle optimizing conversion efficiency, subsystem throughput, and thermal equilibrium for ${techName}.`,
        efficiencyIndicator: 'Continuous Nominal Performance Mode',
        activeFlows: ['primary_flow', 'conversion_flow', 'output_flow']
      },
      {
        id: 'transient_peaking',
        label: 'Frontier High-Stress / Peaking Dispatch',
        description: `High-load operational state testing materials durability, thermal tolerance limits, and sub-second control response.`,
        efficiencyIndicator: 'Stress Testing Materials & Dynamic Response',
        activeFlows: ['stress_flow', 'feedback_loop']
      }
    ],
    nodes,
    conduits
  };
}

// ==============================================================================
// 3. MAIN COMPONENT: INTERACTIVE EXPLORABLE DIAGRAM
// ==============================================================================

interface TechSystemDiagramProps {
  technologyId: string;
  technologyName: string;
  categoryName: string;
  subsystems?: any[];
}

export function TechSystemDiagram({ technologyId, technologyName, categoryName, subsystems }: TechSystemDiagramProps) {
  const config = useMemo(() => {
    return DIAGRAM_CONFIGS[technologyId] || generateProceduralDiagram(technologyId, technologyName, categoryName, subsystems);
  }, [technologyId, technologyName, categoryName, subsystems]);

  const [activeModeId, setActiveModeId] = useState<string>(config.modes[0]?.id || 'default');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(config.nodes[0]?.id || null);
  const [isSimulating, setIsSimulating] = useState<boolean>(true);
  const [highlightLayer, setHighlightLayer] = useState<'all' | 'bottlenecks' | 'materials' | 'flows'>('all');

  const activeMode = useMemo(() => {
    return config.modes.find(m => m.id === activeModeId) || config.modes[0];
  }, [config, activeModeId]);

  const selectedNode = useMemo(() => {
    return config.nodes.find(n => n.id === selectedNodeId) || config.nodes[0];
  }, [config, selectedNodeId]);

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xs overflow-hidden flex flex-col">
      {/* ── DIAGRAM HEADER & SIMULATION TOOLBAR ────────────────────────────── */}
      <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/70 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-cyan-100 text-cyan-800 border border-cyan-200">
              <Sparkles size={11} className="text-cyan-600" />
              Explorable Subsystem Architecture
            </span>
            <span className="text-xs text-slate-400 font-mono">Interactive Vector Model</span>
          </div>
          <h3 className="text-base font-extrabold text-slate-900 mt-1">
            {config.title}
          </h3>
          <p className="text-xs text-slate-500 max-w-2xl">
            {config.subtitle}
          </p>
        </div>

        {/* Mode Toggles & Simulation Play/Pause */}
        <div className="flex items-center gap-2 shrink-0">
          <div className="bg-slate-200/70 p-1 rounded-xl flex items-center gap-1">
            {config.modes.map((mode) => (
              <button
                key={mode.id}
                onClick={() => setActiveModeId(mode.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  activeModeId === mode.id
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {mode.label.split('(')[0].trim()}
              </button>
            ))}
          </div>

          <button
            onClick={() => setIsSimulating(!isSimulating)}
            title={isSimulating ? 'Pause Particle Flow' : 'Play Flow Animation'}
            className="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-100 text-slate-700 transition-all cursor-pointer"
          >
            {isSimulating ? <Pause size={14} className="text-cyan-600" /> : <Play size={14} className="text-emerald-600" />}
          </button>
        </div>
      </div>

      {/* Mode Operational Summary Banner */}
      <div className="px-6 py-2.5 bg-gradient-to-r from-cyan-50/70 via-blue-50/50 to-slate-50 border-b border-cyan-100 flex items-center justify-between text-xs text-cyan-950 font-medium">
        <div className="flex items-center gap-2">
          <Activity size={14} className="text-cyan-600 animate-pulse" />
          <span><strong>Active State:</strong> {activeMode.description}</span>
        </div>
        <span className="font-mono text-[11px] font-bold px-2 py-0.5 rounded bg-cyan-200/60 text-cyan-900 shrink-0">
          {activeMode.efficiencyIndicator}
        </span>
      </div>

      {/* ── MAIN INTERACTIVE CANVAS & SPLIT INSPECTOR ────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 min-h-[380px]">
        {/* ── LEFT CANVAS AREA (7 COLS) ─────────────────────────────────── */}
        <div className="lg:col-span-8 p-6 relative bg-slate-900 text-white overflow-hidden flex flex-col justify-between select-none">
          {/* Background grid markings */}
          <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#94a3b8_1px,transparent_1px)] [background-size:16px_16px] pointer-events-none" />

          {/* Canvas Layer Filters */}
          <div className="relative z-10 flex items-center justify-between text-[11px]">
            <span className="text-slate-400 font-mono flex items-center gap-1.5">
              <ZoomIn size={12} className="text-slate-400" /> Click any node to inspect physical parameters
            </span>

            <div className="flex items-center gap-1 bg-white/10 p-0.5 rounded-lg">
              {[
                { id: 'all', label: 'All Subsystems' },
                { id: 'bottlenecks', label: 'Bottlenecks' },
                { id: 'materials', label: 'Materials' }
              ].map((layer) => (
                <button
                  key={layer.id}
                  onClick={() => setHighlightLayer(layer.id as any)}
                  className={`px-2 py-0.5 rounded text-[10px] font-medium transition-all cursor-pointer ${
                    highlightLayer === layer.id
                      ? 'bg-slate-100 text-slate-900 font-semibold'
                      : 'text-slate-300 hover:text-white'
                  }`}
                >
                  {layer.label}
                </button>
              ))}
            </div>
          </div>

          {/* SVG Conduits & Flow Lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
            <defs>
              <linearGradient id="flowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.7" />
                <stop offset="100%" stopColor="#10b981" stopOpacity="0.7" />
              </linearGradient>
            </defs>

            {config.conduits.map((conduit, idx) => {
              const sourceNode = config.nodes.find(n => n.id === conduit.from);
              const targetNode = config.nodes.find(n => n.id === conduit.to);
              if (!sourceNode || !targetNode) return null;

              return (
                <g key={idx}>
                  {/* Base track line */}
                  <line
                    x1={`${sourceNode.x}%`}
                    y1={`${sourceNode.y}%`}
                    x2={`${targetNode.x}%`}
                    y2={`${targetNode.y}%`}
                    stroke="#1e293b"
                    strokeWidth="4"
                    strokeDasharray="4 4"
                  />
                  {/* Active animated flow line */}
                  {isSimulating && (
                    <line
                      x1={`${sourceNode.x}%`}
                      y1={`${sourceNode.y}%`}
                      x2={`${targetNode.x}%`}
                      y2={`${targetNode.y}%`}
                      stroke="url(#flowGradient)"
                      strokeWidth="2.5"
                      strokeDasharray="6 8"
                      className="animate-[dash_1.5s_linear_infinite]"
                    />
                  )}
                </g>
              );
            })}
          </svg>

          {/* Interactive Subsystem Node Badges */}
          <div className="relative z-10 w-full h-full min-h-[260px] flex items-center justify-around my-auto">
            {config.nodes.map((node) => {
              const isSelected = selectedNodeId === node.id;
              const isBottleneckFocus = highlightLayer === 'bottlenecks';

              return (
                <button
                  key={node.id}
                  onClick={() => setSelectedNodeId(node.id)}
                  className={`group relative p-3 rounded-2xl border transition-all flex flex-col items-center gap-1.5 cursor-pointer max-w-[150px] text-center ${
                    isSelected
                      ? 'bg-cyan-500/20 border-cyan-400 shadow-lg shadow-cyan-500/30 scale-105 ring-2 ring-cyan-400'
                      : isBottleneckFocus
                      ? 'bg-amber-500/20 border-amber-400/80 animate-pulse'
                      : 'bg-slate-800/80 hover:bg-slate-800 border-white/10 hover:border-cyan-400/50'
                  }`}
                >
                  {/* Active Pulse Ring */}
                  {isSelected && (
                    <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-cyan-400 animate-ping" />
                  )}

                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${
                    isSelected ? 'bg-cyan-400 text-slate-950 font-bold' : 'bg-white/10 text-cyan-300 group-hover:bg-cyan-400 group-hover:text-slate-950'
                  }`}>
                    {node.icon === 'Wind' && <Wind size={20} />}
                    {node.icon === 'Droplets' && <Droplets size={20} />}
                    {node.icon === 'BatteryCharging' && <BatteryCharging size={20} />}
                    {node.icon === 'Zap' && <Zap size={20} />}
                    {node.icon === 'Sun' && <Sun size={20} />}
                    {node.icon === 'Layers' && <Layers size={20} />}
                    {node.icon === 'Cpu' && <Cpu size={20} />}
                    {node.icon === 'Flame' && <Flame size={20} />}
                    {node.icon === 'Atom' && <Atom size={20} />}
                    {node.icon === 'Gauge' && <Gauge size={20} />}
                    {node.icon === 'ShieldCheck' && <ShieldCheck size={20} />}
                    {node.icon === 'Eye' && <Eye size={20} />}
                  </div>

                  <span className="text-[11px] font-bold text-white line-clamp-2 leading-tight">
                    {node.name}
                  </span>

                  <span className="text-[9px] font-mono text-cyan-300 font-semibold px-1.5 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/60 truncate max-w-[130px]">
                    {node.operatingValue.split('·')[0]}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Bottom Conduit Flow Legend */}
          <div className="relative z-10 pt-2 border-t border-white/10 flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-400">
            <span className="font-mono">Energy & Matter Vector Conduits</span>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-cyan-400" /> Active Vector Flow
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-amber-400" /> Physics Bottleneck
              </span>
            </div>
          </div>
        </div>

        {/* ── RIGHT INSPECTOR DRAWER (5 COLS) ────────────────────────────── */}
        <div className="lg:col-span-4 p-5 bg-slate-50 border-t lg:border-t-0 lg:border-l border-slate-200 flex flex-col justify-between gap-4">
          <div>
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-200">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  Subsystem Inspector
                </span>
                <h4 className="text-sm font-black text-slate-900 mt-0.5">
                  {selectedNode.name}
                </h4>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-100 text-cyan-800 border border-cyan-200">
                {selectedNode.category}
              </span>
            </div>

            <div className="mt-3 space-y-3 text-xs">
              {/* Function Summary */}
              <div>
                <span className="text-[10px] font-bold uppercase text-slate-400 block mb-0.5">
                  Operating Physics & Function
                </span>
                <p className="text-slate-700 leading-relaxed font-medium">
                  {selectedNode.summary}
                </p>
              </div>

              {/* Operating Metrics */}
              <div className="p-2.5 rounded-xl bg-white border border-slate-200">
                <span className="text-[10px] font-bold uppercase text-cyan-700 flex items-center gap-1 mb-1">
                  <Gauge size={12} /> Live Operating Parameters
                </span>
                <div className="font-mono text-xs font-bold text-slate-800">
                  {selectedNode.operatingValue}
                </div>
              </div>

              {/* Materials & Chemistry */}
              <div>
                <span className="text-[10px] font-bold uppercase text-slate-400 block mb-0.5">
                  Active Materials & Metallurgy
                </span>
                <span className="text-xs text-slate-800 font-semibold">
                  {selectedNode.materials}
                </span>
              </div>

              {/* Critical Frontier Bottleneck */}
              <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-950">
                <span className="text-[10px] font-bold uppercase text-amber-700 flex items-center gap-1 mb-0.5">
                  <AlertTriangle size={12} /> Frontier Engineering Bottleneck
                </span>
                <p className="text-[11px] leading-relaxed">
                  {selectedNode.frontierBottleneck}
                </p>
              </div>

              {/* Active Research Vanguard */}
              <div className="p-2.5 rounded-xl bg-violet-50 border border-violet-200 text-violet-950">
                <span className="text-[10px] font-bold uppercase text-violet-700 flex items-center gap-1 mb-0.5">
                  <Sparkles size={12} /> Active Research Track
                </span>
                <p className="text-[11px] leading-relaxed">
                  {selectedNode.activeResearch}
                </p>
              </div>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-200 text-[10px] text-slate-400 flex items-center justify-between">
            <span>Energy Innovation Terminal Vector Model</span>
            <span className="font-mono">Node ID: {selectedNode.id}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
