import React, { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useNyserda } from '../context/NyserdaContext';
import {
  Compass, Zap, Building2, Download, Sparkles, Layers,
  TrendingUp, Award, Users, ShieldCheck, FileText, ArrowRight,
  CheckCircle2, AlertTriangle, FileDown, Loader2, ArrowUpRight,
  Bookmark, BarChart3, Cpu, Check, Info, Calendar, DollarSign,
  Clock, Target, RefreshCw, ChevronRight, Sliders, ChevronDown,
  ExternalLink, HelpCircle
} from 'lucide-react';
import { OrgLogo } from '../components/OrgLogo';
import { EditableComboBox, ComboBoxOption } from '../components/EditableComboBox';
import {
  quickExecuteStrategy,
  fetchStrategyTemplates,
  downloadStrategyPdf,
  StrategyResultPayload,
  StrategyTemplatesResponse
} from '../api/client';
import {
  CLEAN_ENERGY_TECHNOLOGIES,
  CleanTechItem,
  findCleanTech,
  CLEAN_ENERGY_SECTORS
} from '../data/cleanTechCatalog';

// ============================================================================
// 1. POPULAR TARGET ORGANIZATIONS & CASCADING CONFIGURATIONS
// ============================================================================
export interface OrgConfig {
  id: string;
  name: string;
  shortName: string;
  orgType: string;
  defaultMandate: string;
  defaultPool: string;
  defaultAwardCap: string;
  defaultInstrument: string;
  defaultProgramLength: string;
  defaultAwardDistribution: string;
}

const POPULAR_ORGANIZATIONS: OrgConfig[] = [
  {
    id: 'doe',
    name: 'US Department of Energy (DOE)',
    shortName: 'US DOE',
    orgType: 'Federal Advanced Research Agency (DOE, ARPA-E, NSF)',
    defaultMandate: 'Federal Energy Earthshots: $1/kg clean hydrogen, $20/kWh 10hr+ storage, and <$100/ton DAC by 2030',
    defaultPool: '$50,000,000',
    defaultAwardCap: '$10,000,000',
    defaultInstrument: 'Milestone-Driven Project Call with National Lab User Facility Integration',
    defaultProgramLength: '5 Years (Standard Multi-Phase Pathway)',
    defaultAwardDistribution: 'Ramped: 10 Phase-1 feasibility -> 4 Phase-2 pilot -> 2 Phase-3 host demos/yr'
  },
  {
    id: 'arpa-e',
    name: 'ARPA-E',
    shortName: 'ARPA-E',
    orgType: 'Federal Advanced Research Agency (DOE, ARPA-E, NSF)',
    defaultMandate: 'High-risk, transformational hardtech innovations capable of paradigm shifts in US energy security and emissions reduction',
    defaultPool: '$35,000,000',
    defaultAwardCap: '$5,000,000',
    defaultInstrument: 'Accelerated Open FOA with Stage-Gated Down-Selection',
    defaultProgramLength: '3 Years (Accelerated Pilot & Feasibility Pathway)',
    defaultAwardDistribution: 'Cohort Model: 8 Seed Grants/Year with 50% down-selection to Phase 2'
  },
  {
    id: 'cec',
    name: 'California Energy Commission (CEC)',
    shortName: 'CEC',
    orgType: 'State Energy Office (CEC, MassCEC, NYSERDA)',
    defaultMandate: 'California SB 100 & EPIC IV: 100% clean electricity by 2045 and aggressive clean transportation targets',
    defaultPool: '$30,000,000',
    defaultAwardCap: '$5,000,000',
    defaultInstrument: 'EPIC Competitive Grant Funding Opportunity (GFO)',
    defaultProgramLength: '5 Years (Standard Multi-Phase Pathway)',
    defaultAwardDistribution: '5 Awards/Year (25 Total Awards across 5-Year Pathway)'
  },
  {
    id: 'nyserda',
    name: 'NYSERDA (New York State)',
    shortName: 'NYSERDA',
    orgType: 'State Energy Office (CEC, MassCEC, NYSERDA)',
    defaultMandate: 'NY CLCPA: 6 GW storage by 2030, 70% renewable electricity by 2030, and 100% zero-emission electricity by 2040',
    defaultPool: '$25,000,000',
    defaultAwardCap: '$4,000,000',
    defaultInstrument: '3-Stage Competitive RFP with Go/No-Go Milestone Gates',
    defaultProgramLength: '5 Years (Standard Multi-Phase Pathway)',
    defaultAwardDistribution: '5 Awards/Year (25 Total Awards across 5-Year Pathway)'
  },
  {
    id: 'masscec',
    name: 'Massachusetts Clean Energy Center (MassCEC)',
    shortName: 'MassCEC',
    orgType: 'State Energy Office (NYSERDA, CEC, MassCEC)',
    defaultMandate: 'Massachusetts Clean Energy and Climate Plan for 2030: Offshore wind, clean heat, and grid equity',
    defaultPool: '$15,000,000',
    defaultAwardCap: '$2,500,000',
    defaultInstrument: 'Targeted Innovation Challenge & Demonstration Grant',
    defaultProgramLength: '3 Years (Accelerated Pilot & Feasibility Pathway)',
    defaultAwardDistribution: 'Even Cadence: 4 High-Cap Anchor Awards/Year ($2M-$5M each)'
  },
  {
    id: 'utility',
    name: 'Regulated Electric & Gas Utility (ConEd / National Grid)',
    shortName: 'Regulated Utility',
    orgType: 'Regulated Electric & Gas Utility (ConEd, National Grid)',
    defaultMandate: 'Utility Grid Modernization: Substation CapEx deferral, EV peak shaving, and feeder hosting capacity',
    defaultPool: '$12,000,000',
    defaultAwardCap: '$2,000,000',
    defaultInstrument: 'Utility Sandbox Demonstration & Behind-the-Meter Pilot Program',
    defaultProgramLength: '5 Years (Decadal Reliability Blueprint)',
    defaultAwardDistribution: 'Even Cadence: 4 High-Cap Anchor Awards/Year ($2M-$5M each)'
  },
  {
    id: 'ge_vernova',
    name: 'GE Vernova / Corporate OEM',
    shortName: 'GE Vernova',
    orgType: 'Corporate R&D / Corporate Venture (GE Vernova, Siemens Energy)',
    defaultMandate: 'Commercial First-of-a-Kind (FOAK) technology scaling, supply chain localization, and OEM margin expansion',
    defaultPool: '$20,000,000',
    defaultAwardCap: '$3,500,000',
    defaultInstrument: 'Corporate Co-Development & Strategic Supplier Partnership Call',
    defaultProgramLength: '5 Years (Standard Multi-Phase Pathway)',
    defaultAwardDistribution: 'Ramped: 10 Phase-1 feasibility -> 4 Phase-2 pilot -> 2 Phase-3 host demos/yr'
  },
  {
    id: 'nypa',
    name: 'New York Power Authority (NYPA)',
    shortName: 'NYPA',
    orgType: 'Municipal Power Authority / Regional Transmission Org (NYPA, NYISO)',
    defaultMandate: 'Public power decarbonization, transmission optimization, and zero-emission peaker replacement by 2035',
    defaultPool: '$15,000,000',
    defaultAwardCap: '$3,000,000',
    defaultInstrument: 'Public Power Demonstration Call with Direct Asset Integration',
    defaultProgramLength: '5 Years (Standard Multi-Phase Pathway)',
    defaultAwardDistribution: 'Even Cadence: 4 High-Cap Anchor Awards/Year ($2M-$5M each)'
  }
];

// ============================================================================
// 2. BROAD TECHNOLOGY & FUEL DOMAINS (UNIFIED - INCLUDES FUELS & HARDWARE)
// ============================================================================
export interface BroadDomainConfig {
  id: string;
  name: string;
  shortLabel: string;
  description: string;
  defaultPhilosophy: (org: string) => string;
  defaultTrlMin: number;
  defaultTrlMax: number;
  sponsorDefaultTech: string;
  sponsorDefaultFuel: string;
  sponsorDefaultBottlenecks: string;
}

const BROAD_TECH_DOMAINS: BroadDomainConfig[] = [
  {
    id: 'clean_gen_solar_wind',
    name: 'Advanced Renewable Generation: Solar & Wind Power',
    shortLabel: 'Solar & Wind Generation',
    description: 'Perovskite-silicon tandem PV, floating offshore wind, agrivoltaics, airborne wind & BIPV',
    defaultPhilosophy: (org) => `Accelerate next-generation utility-scale and distributed renewable generation under ${org} programs, proving 30%+ tandem PV efficiency and deepwater floating wind foundations in harsh marine environments.`,
    defaultTrlMin: 3,
    defaultTrlMax: 7,
    sponsorDefaultTech: 'Perovskite-Silicon Tandem Solar Cells',
    sponsorDefaultFuel: 'Clean Electricity / Renewable Generation',
    sponsorDefaultBottlenecks: 'Halide phase segregation under continuous illumination and thermal bias; Moisture and oxygen ingress through edge seal barrier materials; Deepwater dynamic mooring and inter-array cable fatigue in floating offshore wind'
  },
  {
    id: 'geothermal_hydrokinetic_ocean',
    name: 'Geothermal, Hydrokinetic & Ocean Marine Energy',
    shortLabel: 'Geothermal, Wave & Ocean',
    description: 'Enhanced Geothermal Systems (EGS), closed-loop deep geothermal, wave converters, tidal/river hydrokinetics & OTEC',
    defaultPhilosophy: (org) => `De-risk 24/7 firm baseload renewable power through ${org} sandbox programs, demonstrating high-temperature subsurface drilling, multi-stage hydraulic stimulation, and corrosion-resistant marine hydrokinetic turbines.`,
    defaultTrlMin: 3,
    defaultTrlMax: 7,
    sponsorDefaultTech: 'Enhanced Geothermal Systems (EGS)',
    sponsorDefaultFuel: 'Subsurface High-Enthalpy Geothermal Steam',
    sponsorDefaultBottlenecks: 'Subsurface fracture network short-circuiting and thermal drawdown; Downhole logging tool electronics survival at >250°C; Biofouling and seal degradation in marine wave/tidal generators'
  },
  {
    id: 'advanced_nuclear_fusion',
    name: 'Advanced Nuclear, SMRs & Fusion Energy',
    shortLabel: 'Nuclear SMRs & Fusion',
    description: 'High-temperature gas SMRs, molten salt reactors (MSR), fast sodium microreactors, magnetic & inertial fusion energy pilot plants',
    defaultPhilosophy: (org) => `Establish regulatory demonstration pathways, passive safety architectures, high-temperature industrial steam integration, and modular factory fabrication for Gen-IV SMRs and commercial fusion under ${org} funding.`,
    defaultTrlMin: 3,
    defaultTrlMax: 7,
    sponsorDefaultTech: 'High-Temperature Gas-Cooled SMR',
    sponsorDefaultFuel: 'High-Grade Thermal Steam / Process Heat',
    sponsorDefaultBottlenecks: 'High-temperature intermediate heat exchanger alloy corrosion; Secondary steam loop integration with industrial facilities; First-wall plasma-facing material neutron embrittlement in fusion systems'
  },
  {
    id: 'storage_ldes',
    name: 'Energy Storage & Long-Duration Chemistries (LDES)',
    shortLabel: 'Energy Storage & LDES',
    description: 'Iron-air, flow batteries (vanadium/zinc), sodium-ion, thermal energy storage (TES), compressed air CAES, gravity & flywheels',
    defaultPhilosophy: (org) => `De-risk 10-100hr multi-day energy storage chemistries through ${org} testbeds, validating degradation curves, round-trip efficiency, and cost parity with fossil peaker plants.`,
    defaultTrlMin: 4,
    defaultTrlMax: 8,
    sponsorDefaultTech: 'Iron-Air Battery',
    sponsorDefaultFuel: 'Clean Electricity / Storage Carrier',
    sponsorDefaultBottlenecks: 'Air-breathing cathode degradation during multi-day continuous discharge; Parasitic hydrogen evolution reaction at iron anode; Balance-of-plant thermal management in sub-zero winter extremes'
  },
  {
    id: 'hydrogen_efuels',
    name: 'Clean Hydrogen, Green Ammonia & Sustainable E-Fuels',
    shortLabel: 'Hydrogen, Ammonia & E-Fuels',
    description: 'Electrolyzers (SOEC/PEM/AEM), green ammonia synthesis, e-methanol, power-to-liquids (PtL), SAF & biomethane',
    defaultPhilosophy: (org) => `Accelerate low-cost electrolytic hydrogen (<$1/kg), modular green ammonia synthesis, and sustainable aviation fuels (SAF) with industrial off-taker integration under ${org} standards.`,
    defaultTrlMin: 3,
    defaultTrlMax: 7,
    sponsorDefaultTech: 'Solid Oxide Electrolyzer (SOEC)',
    sponsorDefaultFuel: 'Green Hydrogen (H2) & Derivatives',
    sponsorDefaultBottlenecks: 'Chromium poisoning at oxygen electrode under 750°C operation; Stack seal degradation and thermal cycling stresses; Catalyst coating manufacturing yield and balance-of-plant CapEx'
  },
  {
    id: 'industrial_decarb',
    name: 'Industrial Decarbonization & Clean Process Heat',
    shortLabel: 'Industrial Decarbonization',
    description: 'Industrial heat pumps (150°C-250°C+), green steel H2-DRI, low-carbon cement calcination, electrified chemicals & waste heat ORC',
    defaultPhilosophy: (org) => `Electrify heavy industrial process heat and eliminate fossil reliance in steel, cement, glass, and chemical manufacturing via thermal heat pumps, plasma torches, and hydrogen reduction.`,
    defaultTrlMin: 4,
    defaultTrlMax: 8,
    sponsorDefaultTech: 'Industrial High-Temperature Heat Pump (150C+)',
    sponsorDefaultFuel: 'High-Grade Thermal Steam / Process Heat',
    sponsorDefaultBottlenecks: 'High-temperature refrigerant thermodynamic stability; Compressor lubrication at 160°C+ discharge; Integration with variable batch industrial steam cycles'
  },
  {
    id: 'grid_transmission',
    name: 'Grid Modernization, Power Electronics & Transmission',
    shortLabel: 'Grid Modernization & GETs',
    description: 'Grid-enhancing technologies (GETs), Dynamic Line Rating (DLR), grid-forming inverters, solid-state transformers & HVDC converters',
    defaultPhilosophy: (org) => `Unlock transmission line capacity and substation hosting capacity through grid-enhancing technologies (GETs), dynamic line ratings, and autonomous DERMS orchestration under ${org} rules.`,
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    sponsorDefaultTech: 'Dynamic Line Rating (DLR) & GETs',
    sponsorDefaultFuel: 'Pure Hardware Electron Focus / Grid Carrier',
    sponsorDefaultBottlenecks: 'Dynamic line rating sensor telemetry latency; Grid-forming inverter harmonic resonance; Substation DERMS communication and anti-islanding validation'
  },
  {
    id: 'carbon_management',
    name: 'Carbon Management, Direct Air Capture & Point-Source CDR',
    shortLabel: 'Carbon Removal & DAC',
    description: 'Solid sorbent DAC, liquid solvent DAC, point-source capture, Class VI geologic sequestration & carbon mineralization',
    defaultPhilosophy: (org) => `Scale permanent carbon dioxide removal (CDR) and point-source flue capture below $100/ton through advanced solid sorbents, low-thermal desorption cycles, and Class VI mineralization.`,
    defaultTrlMin: 3,
    defaultTrlMax: 7,
    sponsorDefaultTech: 'Direct Air Capture (Solid Sorbent DAC)',
    sponsorDefaultFuel: 'Direct Air Capture (DAC) CO2 / Carbon Carrier',
    sponsorDefaultBottlenecks: 'Desorption thermal energy penalty per ton CO2; Sorbent degradation under ambient humidity and NOx/SOx impurities; Contactor pressure drop optimization'
  },
  {
    id: 'buildings_thermal_networks',
    name: 'Clean Buildings, Thermal Energy Networks (TENs) & Heat Pumps',
    shortLabel: 'Clean Buildings & TENs',
    description: '5G Thermal Energy Networks, district geothermal loops, cold-climate air/water-source heat pumps & smart envelope retrofits',
    defaultPhilosophy: (org) => `Deploy scalable thermal energy networks (TENs) and cold-climate heat pumps to decarbonize dense urban building envelopes and alleviate peak winter electric heating loads.`,
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    sponsorDefaultTech: 'Utility Thermal Energy Networks (TENs)',
    sponsorDefaultFuel: 'High-Grade Thermal Steam / Ambient Heat',
    sponsorDefaultBottlenecks: 'Right-of-way subsurface utility coordination; Thermal balancing across mixed-use residential/commercial load profiles; Hydraulic pumping energy optimization'
  },
  {
    id: 'heavy_mobility_transport',
    name: 'Heavy Transportation, Megawatt EV & Maritime / Aviation',
    shortLabel: 'Heavy Mobility & Megawatt EV',
    description: 'Megawatt charging systems (MCS), heavy-duty Class-8 fuel cell trucks, liquid H2 aircraft tanks, ammonia bunkering & rail',
    defaultPhilosophy: (org) => `Deploy high-power megawatt charging infrastructure (MCS) and heavy-duty fuel cell/e-fuel powertrains to decarbonize commercial freight corridors, transit fleets, and maritime ports.`,
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    sponsorDefaultTech: 'Megawatt EV Charging Systems (MCS)',
    sponsorDefaultFuel: 'Clean Electricity / Storage Carrier',
    sponsorDefaultBottlenecks: 'Liquid-cooled cable thermal management under 3.75 MW continuous draw; Substation interconnect capacity and on-site buffer battery coordination; High-cycle connector durability'
  },
  {
    id: 'circular_economy_recycling',
    name: 'Circular Economy, Battery Recycling & Critical Minerals',
    shortLabel: 'Battery Recycling & Minerals',
    description: 'Hydrometallurgical cathode recovery, direct lithium extraction (DLE) from brines, rare earth magnet recycling & precursor synthesis',
    defaultPhilosophy: (org) => `Establish domestic closed-loop supply chains for critical energy minerals (lithium, cobalt, nickel, rare earths) through low-emission hydrometallurgical recovery and direct brine extraction under ${org} programs.`,
    defaultTrlMin: 4,
    defaultTrlMax: 8,
    sponsorDefaultTech: 'Hydrometallurgical Battery Cathode Recycling',
    sponsorDefaultFuel: 'Recycled Critical Mineral Precursors',
    sponsorDefaultBottlenecks: 'Cross-contamination of mixed cathode chemistries (NMC/LFP); Reagent chemical consumption and wastewater effluent treatment; Purity verification for battery-grade cathode precursor re-synthesis'
  },
  {
    id: 'bioenergy_rng_methane',
    name: 'Bioenergy, Biomethane (RNG), Biochar & Methane Abatement',
    shortLabel: 'Bioenergy, RNG & Biochar',
    description: 'Anaerobic digestion RNG upgrading, biomass pyrolysis & gasification with biochar CDR, agricultural manure capture & landfill oxidation',
    defaultPhilosophy: (org) => `Monetize agricultural and organic waste streams through high-purity RNG biomethane production, permanent biochar carbon sequestration, and point-source fugitive methane abatement.`,
    defaultTrlMin: 5,
    defaultTrlMax: 8,
    sponsorDefaultTech: 'Anaerobic Digestion to Renewable Natural Gas (RNG)',
    sponsorDefaultFuel: 'Biomethane / Renewable Natural Gas (RNG)',
    sponsorDefaultBottlenecks: 'Siloxane and volatile organic sulfur compound (VOSC) poisoning of biogas upgrading membranes; Thermal efficiency of digestate drying; Pipeline interconnect gas quality certification'
  },
  {
    id: 'ders_microgrids_vpp',
    name: 'Distributed Energy Resources (DERs), Microgrids & Virtual Power Plants (VPPs)',
    shortLabel: 'DERs, Microgrids & VPPs',
    description: 'Commercial microgrids, AI-driven VPP aggregation, bidirectional vehicle-to-grid (V2G) power electronics & community solar+storage',
    defaultPhilosophy: (org) => `Aggregate distributed rooftop solar, behind-the-meter storage, and smart EV chargers into dynamic virtual power plants (VPPs) to provide sub-second frequency regulation and feeder capacity relief.`,
    defaultTrlMin: 5,
    defaultTrlMax: 9,
    sponsorDefaultTech: 'Virtual Power Plant (VPP) Aggregation Platform',
    sponsorDefaultFuel: 'Distributed Flexible Electrons / DER Carrier',
    sponsorDefaultBottlenecks: 'IEEE 2030.5 / OpenADR communication latency across tens of thousands of distributed endpoints; Multi-asset dispatch co-optimization under dynamic LMP pricing; Customer churn and baseline counterfactual verification'
  },
  {
    id: 'water_energy_nexus',
    name: 'Clean Water-Energy Nexus, Desalination & Resource Recovery',
    shortLabel: 'Water-Energy & Desalination',
    description: 'Zero Liquid Discharge (ZLD), low-energy reverse osmosis with energy recovery, waste-heat / solar membrane distillation & brine mineral harvesting',
    defaultPhilosophy: (org) => `Optimize the water-energy nexus by reducing the specific energy consumption of industrial wastewater treatment, desalination, and critical mineral extraction from reject brines.`,
    defaultTrlMin: 4,
    defaultTrlMax: 8,
    sponsorDefaultTech: 'Zero Liquid Discharge (ZLD) Low-Energy Desalination',
    sponsorDefaultFuel: 'Thermal Waste Heat / Low-Carbon Electricity',
    sponsorDefaultBottlenecks: 'High-salinity membrane fouling and mineral scaling; Specific thermal and electric energy consumption per cubic meter of clean distillate; Selective extraction of battery-grade minerals from hypersaline brines'
  },
  {
    id: 'agriculture_soil_carbon',
    name: 'Agriculture Decarbonization, Precision Ag & Soil Carbon',
    shortLabel: 'Agriculture & Soil Carbon',
    description: 'Electrified agricultural equipment, low-carbon green nitrogen fertilizers, enhanced rock weathering on croplands & enteric methane reduction',
    defaultPhilosophy: (org) => `Decarbonize agricultural operations and food supply chains through electrified field equipment, green ammonia fertilizer application, and MRV-verified soil carbon sequestration.`,
    defaultTrlMin: 3,
    defaultTrlMax: 7,
    sponsorDefaultTech: 'Enhanced Rock Weathering for Agricultural Soil Carbon',
    sponsorDefaultFuel: 'Soil Carbon Sequestration / Bio-Nutrient Carrier',
    sponsorDefaultBottlenecks: 'Empirical Measurement, Reporting & Verification (MRV) of dissolved inorganic carbon weathering rates; Basalt grain size milling energy penalty; Soil pH and heavy metal trace accumulation monitoring'
  }
];

// Curated Helper Lists
const SPONSOR_TYPES = [
  'Early-Stage Startup / Small Business (SBIR-Eligible)',
  'Established Commercial Hardtech OEM',
  'Academic Institution / University Research Lab',
  'National Laboratory / FFRDC Partner',
  'Multi-Stakeholder Regional Clean Energy Consortium',
  'Project Developer / Independent Power Producer (IPP)'
];

const FUNDER_TYPES = [
  'Federal Advanced Research Agency (DOE, ARPA-E, NSF)',
  'State Energy Office (CEC, MassCEC, NYSERDA)',
  'Regulated Electric & Gas Utility (ConEd, National Grid)',
  'Corporate R&D / Corporate Venture (GE Vernova, Siemens Energy)',
  'Municipal Power Authority / Regional Transmission Org (NYPA, NYISO)'
];

const PROGRAM_LENGTH_OPTIONS = [
  '3 Years (Accelerated Pilot & Feasibility Pathway)',
  '5 Years (Standard Multi-Phase Stage-Gated Pathway)',
  '7 Years (Deep Commercialization & Scaling Roadmap)',
  '10 Years (Decadal Industrial Transformation Blueprint)',
  '2 Years (Fast-Track SBIR/STTR Innovation Cohort)'
];

const AWARD_DISTRIBUTION_OPTIONS = [
  '5 Awards/Year (25 Total Awards across 5-Year Pathway)',
  'Ramped: 10 Phase-1 feasibility -> 4 Phase-2 pilot -> 2 Phase-3 host demos/yr',
  'Front-Loaded: 12 seed awards in Y1-Y2 tapering to 4 scale-up demos in Y3-Y5',
  'Even Cadence: 4 High-Cap Anchor Awards/Year ($2M-$5M each)',
  'Cohort Model: 8 Seed Grants/Year with 50% down-selection to Phase 2 after 18 months'
];

const SOLICITATION_INSTRUMENTS = [
  '3-Stage Competitive RFP with Go/No-Go Milestone Gates',
  'Continuous Open PON with Rolling Quarterly Evaluation Rounds',
  'Milestone-Driven Challenge Prize + Utility Sandbox Demonstration',
  'Accelerated Open FOA with Stage-Gated Down-Selection',
  'Utility Sandbox Demonstration & Behind-the-Meter Pilot Program',
  'Corporate Co-Development & Strategic Supplier Partnership Call'
];

const BUDGET_OPTIONS = ['$2,500,000', '$5,000,000', '$10,000,000', '$15,000,000', '$25,000,000', '$50,000,000'];
const COST_SHARE_OPTIONS = ['0% (Academic / SBIR Tier 1 Waiver)', '10% (Small Business Cost Share)', '20% (Standard Federal/State Match)', '35% (Commercial Host-Site Co-Funding)', '50% (OCED / Large Demo Match)'];
const PROGRAM_POOL_OPTIONS = ['$10,000,000', '$15,000,000', '$25,000,000', '$35,000,000', '$50,000,000', '$100,000,000'];
const AWARD_CAP_OPTIONS = ['$1,000,000', '$2,000,000', '$2,500,000', '$4,000,000', '$5,000,000', '$10,000,000'];

export default function Strategy() {
  const navigate = useNavigate();
  const { includeNyserda, isNyserda } = useNyserda();

  const popularOrgs = useMemo(() => {
    return POPULAR_ORGANIZATIONS.filter(o => includeNyserda || o.id !== 'nyserda');
  }, [includeNyserda]);

  const funderTypes = FUNDER_TYPES;

  const [mode, setMode] = useState<'project_sponsor' | 'funding_organization'>('project_sponsor');
  const [activeTab, setActiveTab] = useState<'thesis' | 'pathway' | 'workstreams' | 'capital_stack' | 'awards_comps'>('thesis');
  const [isExecuting, setIsExecuting] = useState(false);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  // --------------------------------------------------------------------------
  // Project Sponsor Form State (Auto-Grounded to 112+ Master Technologies)
  // --------------------------------------------------------------------------
  const [sponsorTech, setSponsorTech] = useState(CLEAN_ENERGY_TECHNOLOGIES[0].name);
  const [sponsorCurrentTrl, setSponsorCurrentTrl] = useState(CLEAN_ENERGY_TECHNOLOGIES[0].defaultTrlMin);
  const [sponsorTargetTrl, setSponsorTargetTrl] = useState(CLEAN_ENERGY_TECHNOLOGIES[0].defaultTrlMax);
  const [sponsorType, setSponsorType] = useState(SPONSOR_TYPES[0]);
  const [sponsorState, setSponsorState] = useState('New York');
  const [sponsorAgency, setSponsorAgency] = useState('DOE');
  const [sponsorBudget, setSponsorBudget] = useState('$10,000,000');
  const [sponsorCostShare, setSponsorCostShare] = useState('20% (Standard Federal/State Match)');
  const [sponsorBottlenecks, setSponsorBottlenecks] = useState(CLEAN_ENERGY_TECHNOLOGIES[0].defaultBottlenecks);

  // --------------------------------------------------------------------------
  // Funding Organization Form State (Clean & Streamlined - No Separate Fuel Box)
  // --------------------------------------------------------------------------
  const [funderOrgName, setFunderOrgName] = useState(popularOrgs[0].name);
  const [funderOrgType, setFunderOrgType] = useState(popularOrgs[0].orgType);
  const [funderMandate, setFunderMandate] = useState(popularOrgs[0].defaultMandate);
  const [funderTechFocus, setFunderTechFocus] = useState(BROAD_TECH_DOMAINS[0].name);
  const [funderProgramLength, setFunderProgramLength] = useState(popularOrgs[0].defaultProgramLength);
  const [funderAwardDistribution, setFunderAwardDistribution] = useState(popularOrgs[0].defaultAwardDistribution);
  const [funderProgramPhilosophy, setFunderProgramPhilosophy] = useState(
    BROAD_TECH_DOMAINS[0].defaultPhilosophy(popularOrgs[0].shortName)
  );
  const [funderProgramPool, setFunderProgramPool] = useState(popularOrgs[0].defaultPool);
  const [funderAwardCap, setFunderAwardCap] = useState(popularOrgs[0].defaultAwardCap);
  const [funderTrlMin, setFunderTrlMin] = useState(BROAD_TECH_DOMAINS[0].defaultTrlMin);
  const [funderTrlMax, setFunderTrlMax] = useState(BROAD_TECH_DOMAINS[0].defaultTrlMax);
  const [funderInstrument, setFunderInstrument] = useState(popularOrgs[0].defaultInstrument);

  // Automatically adjust selected agency and organization when NYSERDA is excluded
  useEffect(() => {
    if (!includeNyserda) {
      if (isNyserda(sponsorAgency) || sponsorAgency === 'NYSERDA') {
        setSponsorAgency('DOE');
      }
      if (isNyserda(funderOrgName) || funderOrgName === 'NYSERDA') {
        const fallback = popularOrgs[0] || POPULAR_ORGANIZATIONS[1];
        setFunderOrgName(fallback.name);
        setFunderOrgType(fallback.orgType);
        setFunderMandate(fallback.defaultMandate);
        setFunderProgramLength(fallback.defaultProgramLength);
        setFunderAwardDistribution(fallback.defaultAwardDistribution);
        setFunderProgramPool(fallback.defaultPool);
        setFunderAwardCap(fallback.defaultAwardCap);
        setFunderInstrument(fallback.defaultInstrument);
      }
    }
  }, [includeNyserda, sponsorAgency, funderOrgName, popularOrgs, isNyserda]);

  // Strategy Execution Results
  const [strategyResults, setStrategyResults] = useState<StrategyResultPayload | null>(null);

  // Fetch Pre-Configured Templates
  const { data: templatesData } = useQuery<StrategyTemplatesResponse>({
    queryKey: ['strategy_templates'],
    queryFn: fetchStrategyTemplates,
    staleTime: 60 * 60 * 1000
  });

  // --------------------------------------------------------------------------
  // Dynamic Cascading Selection Handlers
  // --------------------------------------------------------------------------
  const handleSelectOrg = (orgNameOrConfig: string | OrgConfig) => {
    const cfg = typeof orgNameOrConfig === 'string'
      ? popularOrgs.find(o => o.name === orgNameOrConfig || o.shortName === orgNameOrConfig || o.id === orgNameOrConfig)
      : orgNameOrConfig;
    if (cfg) {
      setFunderOrgName(cfg.name);
      setFunderOrgType(cfg.orgType);
      setFunderMandate(cfg.defaultMandate);
      setFunderProgramLength(cfg.defaultProgramLength);
      setFunderAwardDistribution(cfg.defaultAwardDistribution);
      setFunderProgramPool(cfg.defaultPool);
      setFunderAwardCap(cfg.defaultAwardCap);
      setFunderInstrument(cfg.defaultInstrument);
      
      const currentDomain = BROAD_TECH_DOMAINS.find(d => d.name === funderTechFocus);
      if (currentDomain) {
        setFunderProgramPhilosophy(currentDomain.defaultPhilosophy(cfg.shortName));
      }
    } else if (typeof orgNameOrConfig === 'string') {
      setFunderOrgName(orgNameOrConfig);
    }
  };

  const handleSelectDomain = (domain: BroadDomainConfig) => {
    setFunderTechFocus(domain.name);
    setFunderTrlMin(domain.defaultTrlMin);
    setFunderTrlMax(domain.defaultTrlMax);

    const activeOrg = POPULAR_ORGANIZATIONS.find(o => o.name === funderOrgName || o.shortName === funderOrgName);
    const orgLabel = activeOrg?.shortName || funderOrgName || 'Agency';
    setFunderProgramPhilosophy(domain.defaultPhilosophy(orgLabel));
  };

  const handleSelectCleanTech = (val: string) => {
    setSponsorTech(val);
    const matched = findCleanTech(val);
    if (matched) {
      setSponsorBottlenecks(matched.defaultBottlenecks);
      setSponsorCurrentTrl(matched.defaultTrlMin);
      setSponsorTargetTrl(matched.defaultTrlMax);
    }
  };

  // Load Template Handler
  const handleLoadTemplate = (templateId: string) => {
    setSelectedTemplateId(templateId);
    if (mode === 'project_sponsor' && templatesData?.project_sponsor_templates) {
      const t = templatesData.project_sponsor_templates.find(item => item.id === templateId);
      if (t) {
        setSponsorTech(t.technology || '');
        setSponsorCurrentTrl(t.current_trl);
        setSponsorTargetTrl(t.target_trl);
        setSponsorType(t.sponsor_type);
        setSponsorState(t.state);
        setSponsorAgency(t.target_agency);
        setSponsorBudget(t.budget);
        setSponsorCostShare(t.cost_share_pct);
        setSponsorBottlenecks((t.technical_bottlenecks || []).join('; '));
      }
    } else if (mode === 'funding_organization' && templatesData?.funding_org_templates) {
      const t = templatesData.funding_org_templates.find(item => item.id === templateId);
      if (t) {
        setFunderOrgName(t.org_name);
        setFunderOrgType(t.org_type);
        setFunderMandate(t.mandate);
        setFunderTechFocus((t.tech_focus || []).join(', '));
        if (t.program_length_years) setFunderProgramLength(t.program_length_years);
        if (t.annual_award_distribution) setFunderAwardDistribution(t.annual_award_distribution);
        if (t.program_philosophy) setFunderProgramPhilosophy(t.program_philosophy);
        setFunderProgramPool(t.program_pool);
        setFunderAwardCap(t.award_cap);
        setFunderTrlMin(t.target_trl_min);
        setFunderTrlMax(t.target_trl_max);
        setFunderInstrument(t.solicitation_instrument);
      }
    }
  };

  // Execution Handler
  const handleExecuteStrategy = async () => {
    setIsExecuting(true);
    try {
      const payload = {
        mode,
        title: mode === 'project_sponsor'
          ? `${sponsorTech || 'Clean Energy'} Research Strategy & Capital Architecture`
          : `${funderOrgName} Program Strategy & Solicitation Architecture`,
        inputs: mode === 'project_sponsor'
          ? {
              technologies: sponsorTech ? [sponsorTech.trim()] : [],
              current_trl: sponsorCurrentTrl,
              target_trl: sponsorTargetTrl,
              sponsor_type: sponsorType,
              state: sponsorState,
              target_agency: sponsorAgency,
              budget: sponsorBudget,
              cost_share_pct: sponsorCostShare,
              technical_bottlenecks: sponsorBottlenecks.split(';').map(s => s.trim()).filter(Boolean)
            }
          : {
              org_name: funderOrgName,
              org_type: funderOrgType,
              mandate: funderMandate,
              tech_focus: funderTechFocus.split(',').map(s => s.trim()).filter(Boolean),
              program_length_years: funderProgramLength,
              annual_award_distribution: funderAwardDistribution,
              program_philosophy: funderProgramPhilosophy,
              program_pool: funderProgramPool,
              award_cap: funderAwardCap,
              target_trl_min: funderTrlMin,
              target_trl_max: funderTrlMax,
              solicitation_instrument: funderInstrument
            }
      };

      const response = await quickExecuteStrategy(payload);
      setStrategyResults(response.results);
      setActiveTab('thesis');
    } catch (err: any) {
      console.error('Execution error:', err);
      alert(err.message || 'Strategy analysis error. Please try again.');
    } finally {
      setIsExecuting(false);
    }
  };

  // Download PDF Handler
  const handleDownloadPdf = async () => {
    if (!strategyResults) return;
    setIsDownloadingPdf(true);
    try {
      await downloadStrategyPdf(
        strategyResults,
        strategyResults.title || 'Strategic_Research_Plan',
        mode
      );
    } catch (err: any) {
      console.error('PDF error:', err);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  // Push to Proposal Copilot
  const handlePushToProposalCopilot = () => {
    if (!strategyResults) return;
    const proposalPayload = {
      project_title: strategyResults.title,
      technology: sponsorTech,
      target_agency: sponsorAgency,
      trl: sponsorCurrentTrl,
      budget: sponsorBudget,
      workstreams: strategyResults.workstream_decomposition,
      executive_summary: strategyResults.executive_thesis,
      capital_stack: strategyResults.capital_stacking_strategy
    };
    navigate('/proposals', { state: { strategyPayload: proposalPayload } });
  };

  const activeOrgObj = POPULAR_ORGANIZATIONS.find(o => o.name === funderOrgName || o.shortName === funderOrgName);

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-16 px-4">
      {/* Header & Mode Switcher */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
              <Compass size={12} className="text-indigo-600" />
              <span>Strategy Intelligence Terminal</span>
            </span>
            <span className="text-xs text-slate-300">|</span>
            <span className="text-xs font-medium text-slate-500">Long-Term Innovation Pathways</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            {mode === 'project_sponsor' ? 'Project Sponsor Strategy' : 'Funding Organization Strategy'}
          </h1>
          <p className="text-xs text-slate-600 max-w-3xl mt-1">
            {mode === 'project_sponsor'
              ? 'Select your clean technology and target agency to formulate an optimized research approach, capital stacking plan, and high-win teaming.'
              : 'Select your funding organization and technology & fuels domain to generate a multi-year RFP solicitation architecture, Go/No-Go milestones, and scoring rubrics.'}
          </p>
        </div>

        {/* Mode Toggle Switch */}
        <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 shrink-0">
          <button
            onClick={() => {
              setMode('project_sponsor');
              setStrategyResults(null);
            }}
            className={`px-4 py-2 text-xs font-bold rounded-lg transition-all cursor-pointer flex items-center gap-1.5 ${
              mode === 'project_sponsor'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Zap size={14} className={mode === 'project_sponsor' ? 'text-amber-500' : 'text-slate-400'} />
            <span>Project Sponsor</span>
          </button>
          <button
            onClick={() => {
              setMode('funding_organization');
              setStrategyResults(null);
            }}
            className={`px-4 py-2 text-xs font-bold rounded-lg transition-all cursor-pointer flex items-center gap-1.5 ${
              mode === 'funding_organization'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Building2 size={14} className={mode === 'funding_organization' ? 'text-blue-500' : 'text-slate-400'} />
            <span>Funding Organization</span>
          </button>
        </div>
      </div>

      {/* Preset Blueprints Quick Load Bar */}
      <div className="flex items-center gap-2 flex-wrap text-xs bg-slate-50 p-2.5 rounded-xl border border-slate-200">
        <span className="text-slate-600 font-semibold flex items-center gap-1">
          <Bookmark size={13} className="text-indigo-600" />
          <span>Institutional Blueprints:</span>
        </span>
        {mode === 'project_sponsor' ? (
          templatesData?.project_sponsor_templates?.map(tpl => (
            <button
              key={tpl.id}
              onClick={() => handleLoadTemplate(tpl.id)}
              className={`px-2.5 py-1 rounded-lg border text-xs transition cursor-pointer ${
                selectedTemplateId === tpl.id
                  ? 'bg-indigo-600 border-indigo-600 text-white font-semibold shadow-xs'
                  : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-100'
              }`}
            >
              {tpl.name}
            </button>
          ))
        ) : (
          templatesData?.funding_org_templates?.map(tpl => (
            <button
              key={tpl.id}
              onClick={() => handleLoadTemplate(tpl.id)}
              className={`px-2.5 py-1 rounded-lg border text-xs transition cursor-pointer ${
                selectedTemplateId === tpl.id
                  ? 'bg-indigo-600 border-indigo-600 text-white font-semibold shadow-xs'
                  : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-100'
              }`}
            >
              {tpl.name}
            </button>
          ))
        )}
      </div>

      {/* =========================================================================
         ORGANIZATIONAL MODE: 2-STEP CASCADING FLOW
         ========================================================================= */}
      {mode === 'funding_organization' ? (
        <>
          {/* STEP 1: VISUAL 1-CLICK QUICK SELECTION (EFFORTLESS CLICK-THROUGH) */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600">Step 1</span>
                <h2 className="text-sm font-bold text-slate-900">
                  Select Funding Organization &amp; Technology / Fuels Domain
                </h2>
              </div>
              <span className="text-xs text-slate-500 italic">
                1-Click auto-configures all strategic parameters
              </span>
            </div>

            <div className="space-y-4">
              {/* 1-Click Popular Organization Pills */}
              <div className="space-y-1.5">
                <label className="block text-xs font-semibold text-slate-700">
                  1. Target Funding Organization:
                </label>
                <div className="flex items-center gap-2 flex-wrap">
                  {POPULAR_ORGANIZATIONS.map(org => {
                    const isSelected = funderOrgName === org.name || funderOrgName === org.shortName;
                    return (
                      <button
                        key={org.id}
                        type="button"
                        onClick={() => handleSelectOrg(org)}
                        className={`px-3 py-1.5 text-xs rounded-xl font-semibold border transition cursor-pointer flex items-center gap-1.5 ${
                          isSelected
                            ? 'bg-slate-900 text-white border-slate-900 shadow-xs ring-2 ring-slate-900/10'
                            : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                        }`}
                      >
                        <OrgLogo org={org.shortName} size="xs" />
                        <span>{org.name}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* 1-Click Broad Technology & Fuels Domains (Unified) */}
              <div className="space-y-1.5 pt-1">
                <label className="block text-xs font-semibold text-slate-700 flex items-center gap-1">
                  <span>2. Technology &amp; Fuels Domain Target (Broad Scope):</span>
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
                  {BROAD_TECH_DOMAINS.map(dom => {
                    const isSelected = funderTechFocus === dom.name || funderTechFocus.includes(dom.shortLabel);
                    return (
                      <button
                        key={dom.id}
                        type="button"
                        onClick={() => handleSelectDomain(dom)}
                        className={`p-2.5 text-left rounded-xl border transition cursor-pointer flex flex-col justify-between ${
                          isSelected
                            ? 'bg-indigo-50/80 border-indigo-600 ring-2 ring-indigo-600/20 shadow-xs'
                            : 'bg-white border-slate-200 hover:border-indigo-300 hover:bg-slate-50'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className={`text-xs font-bold ${isSelected ? 'text-indigo-900' : 'text-slate-900'}`}>
                            {dom.shortLabel}
                          </span>
                          {isSelected && <Check size={14} className="text-indigo-600 shrink-0" />}
                        </div>
                        <span className="text-[10px] text-slate-500 mt-1 line-clamp-2 leading-tight">
                          {dom.description}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* STEP 2: AUTO-CONFIGURED STRATEGIC PARAMETERS CARD */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-600">Step 2</span>
                <h2 className="text-sm font-bold text-slate-900">
                  Auto-Configured Strategic Specifications
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold flex items-center gap-1 cursor-pointer"
              >
                <Sliders size={13} />
                <span>{showAdvanced ? 'Hide Fine-Tuning' : 'Customize All Fields'}</span>
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Funding Organization */}
                <EditableComboBox
                  label="Funding Organization Name"
                  value={funderOrgName}
                  onChange={handleSelectOrg}
                  options={popularOrgs.map(o => o.name)}
                  placeholder="e.g. US Department of Energy (DOE), California Energy Commission (CEC), NYSERDA..."
                />

                {/* Institution Type */}
                <EditableComboBox
                  label="Institution Classification"
                  value={funderOrgType}
                  onChange={setFunderOrgType}
                  options={funderTypes}
                  placeholder="Select institution type..."
                />

                {/* Broad Technology & Fuel Domain Target (Single Field) */}
                <EditableComboBox
                  label="Technology &amp; Fuels Domain Target"
                  subLabel="Broad domain encompassing hardware, fuels, and systems"
                  value={funderTechFocus}
                  onChange={val => {
                    setFunderTechFocus(val);
                    const matched = BROAD_TECH_DOMAINS.find(d => d.name === val || d.shortLabel === val);
                    if (matched) handleSelectDomain(matched);
                  }}
                  options={BROAD_TECH_DOMAINS.map(d => ({ value: d.name, label: d.shortLabel, description: d.description }))}
                  placeholder="Select or enter domain target..."
                  badge="Broad Domain"
                />
              </div>

              {/* Strategic Philosophy & Program Description */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="block text-xs font-semibold text-slate-700">
                    Program Philosophy &amp; Strategic Thesis (Interpreted by LLM):
                  </label>
                  <span className="text-[11px] text-emerald-600 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                    Auto-Grounded to Selection
                  </span>
                </div>
                <textarea
                  rows={2}
                  value={funderProgramPhilosophy}
                  onChange={e => setFunderProgramPhilosophy(e.target.value)}
                  className="w-full text-xs p-2.5 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-slate-800 bg-slate-50/50"
                  placeholder="Strategic thesis interpreted by the LLM to design the stage-gated RFP architecture, scoring criteria, and Go/No-Go milestones..."
                />
              </div>

              {/* Collapsible / Advanced Details */}
              {showAdvanced && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-2 border-t border-slate-100">
                  {/* Policy Mandate */}
                  <div className="md:col-span-2">
                    <EditableComboBox
                      label="Statutory / Strategic Policy Mandate"
                      value={funderMandate}
                      onChange={setFunderMandate}
                      options={POPULAR_ORGANIZATIONS.map(o => o.defaultMandate)}
                      placeholder="e.g. NY CLCPA 6 GW storage by 2030..."
                    />
                  </div>

                  {/* Solicitation Instrument */}
                  <EditableComboBox
                    label="Solicitation Mechanism &amp; Format"
                    value={funderInstrument}
                    onChange={setFunderInstrument}
                    options={SOLICITATION_INSTRUMENTS}
                    placeholder="e.g. 3-Stage Competitive RFP..."
                  />

                  {/* Program Pool & Award Cap */}
                  <EditableComboBox
                    label="Total Program Pool"
                    value={funderProgramPool}
                    onChange={setFunderProgramPool}
                    options={PROGRAM_POOL_OPTIONS}
                    placeholder="$25,000,000"
                  />

                  <EditableComboBox
                    label="Max Award Cap"
                    value={funderAwardCap}
                    onChange={setFunderAwardCap}
                    options={AWARD_CAP_OPTIONS}
                    placeholder="$4,000,000"
                  />

                  {/* Program Length & Award Cadence */}
                  <EditableComboBox
                    label="Program Horizon (Years)"
                    value={funderProgramLength}
                    onChange={setFunderProgramLength}
                    options={PROGRAM_LENGTH_OPTIONS}
                    placeholder="5 Years..."
                  />

                  <div className="md:col-span-2">
                    <EditableComboBox
                      label="Annual Award Distribution Cadence"
                      value={funderAwardDistribution}
                      onChange={setFunderAwardDistribution}
                      options={AWARD_DISTRIBUTION_OPTIONS}
                      placeholder="e.g. 5 Awards/Year..."
                    />
                  </div>

                  {/* TRL Range */}
                  <div className="grid grid-cols-2 gap-2 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                    <div>
                      <label className="block text-[11px] font-semibold text-slate-600">Target Min TRL</label>
                      <input
                        type="number"
                        min={1}
                        max={funderTrlMax}
                        value={funderTrlMin}
                        onChange={e => setFunderTrlMin(Number(e.target.value))}
                        className="w-full text-xs p-1.5 rounded border border-slate-300 mt-1 bg-white"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-slate-600">Target Max TRL</label>
                      <input
                        type="number"
                        min={funderTrlMin}
                        max={9}
                        value={funderTrlMax}
                        onChange={e => setFunderTrlMax(Number(e.target.value))}
                        className="w-full text-xs p-1.5 rounded border border-slate-300 mt-1 bg-white"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Primary Execute Button */}
              <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-100">
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <ShieldCheck size={16} className="text-emerald-600 shrink-0" />
                  <span>Grounded in <b>54,000+ historical awards</b> &amp; master clean technology models.</span>
                </div>

                <button
                  type="button"
                  onClick={handleExecuteStrategy}
                  disabled={isExecuting}
                  className="w-full sm:w-auto px-6 py-3 rounded-xl font-bold text-sm bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isExecuting ? (
                    <>
                      <Loader2 size={18} className="animate-spin text-white" />
                      <span>Synthesizing Strategy via OpenAI GPT-4o...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles size={18} className="text-amber-300" />
                      <span>Generate {activeOrgObj?.shortName || funderOrgName} Program Architecture</span>
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </>
      ) : (
        /* =========================================================================
           PROJECT SPONSOR MODE: UNIFIED SINGLE WORKSPACE (NO STEP 1 DUPLICATION)
           ========================================================================= */
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-amber-600 flex items-center gap-1">
                <Zap size={13} className="text-amber-500" />
                <span>Project Formulation &amp; Award Capture Blueprint</span>
              </span>
              <h2 className="text-sm font-bold text-slate-900">
                Clean Technology &amp; Research Approach Specifications
              </h2>
            </div>
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold flex items-center gap-1 cursor-pointer"
            >
              <Sliders size={13} />
              <span>{showAdvanced ? 'Hide Fine-Tuning' : 'Customize All Fields'}</span>
            </button>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* 112+ Clean Energy Technologies Combobox */}
              <div>
                <EditableComboBox
                  label="Primary Clean Energy Technology &amp; Carrier Vector"
                  subLabel="Select or search across 112+ expansive clean technologies, carriers, and decarbonization systems"
                  value={sponsorTech}
                  onChange={handleSelectCleanTech}
                  options={CLEAN_ENERGY_TECHNOLOGIES.map(t => ({
                    value: t.name,
                    label: t.name,
                    group: t.sector,
                    description: t.description
                  }))}
                  placeholder="Type or search 112+ technologies (e.g. Iron-Air, SOEC, SMR, Heat Pump, DAC, HJT...)"
                  badge="112+ Clean Technologies"
                />
              </div>

              {/* Target Funding Agency */}
              <div className="space-y-1.5">
                <EditableComboBox
                  label="Target Funding Agency"
                  subLabel="Target institutional funder for solicitation alignment &amp; win-rate optimization"
                  value={sponsorAgency}
                  onChange={setSponsorAgency}
                  options={['DOE', 'ARPA-E', 'CEC', 'NYSERDA', 'MassCEC', 'Regulated Electric & Gas Utility (ConEd / National Grid)', 'GE Vernova / Corporate OEM', 'New York Power Authority (NYPA)', 'National Science Foundation (NSF)', 'DOD / ESTCP / DARPA']}
                  placeholder="e.g. DOE, ARPA-E, CEC, NYSERDA, MassCEC..."
                />
                {/* 1-Click Popular Agency Quick Selectors */}
                <div className="flex items-center gap-1.5 flex-wrap pt-0.5">
                  <span className="text-[10px] text-slate-500 font-semibold">Quick select:</span>
                  {['DOE', 'ARPA-E', 'CEC', 'NYSERDA', 'MassCEC', 'Con Edison', 'National Grid', 'GE Vernova'].map(ag => (
                    <button
                      key={ag}
                      type="button"
                      onClick={() => setSponsorAgency(ag)}
                      className={`px-2 py-0.5 text-[11px] rounded-md font-semibold border transition cursor-pointer flex items-center gap-1 ${
                        sponsorAgency === ag
                          ? 'bg-slate-900 text-white border-slate-900 shadow-2xs'
                          : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                      }`}
                    >
                      <OrgLogo org={ag} size="xs" />
                      <span>{ag}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Core Engineering Bottlenecks (Auto-Grounded to Selected Technology) */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="block text-xs font-semibold text-slate-700">
                  Core Engineering Bottlenecks (Auto-Grounded to Technology; Semicolon-Separated):
                </label>
                <span className="text-[11px] text-emerald-600 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                  Auto-Grounded to Selection
                </span>
              </div>
              <textarea
                rows={2}
                value={sponsorBottlenecks}
                onChange={e => setSponsorBottlenecks(e.target.value)}
                className="w-full text-xs p-2.5 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-slate-800 bg-slate-50/50"
                placeholder="e.g. Air-breathing cathode degradation; Parasitic hydrogen evolution; Balance of plant thermal management..."
              />
            </div>

            {/* Specifications / Fine-Tuning */}
            {showAdvanced && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-2 border-t border-slate-100">
                <EditableComboBox
                  label="Applicant / Sponsor Type"
                  value={sponsorType}
                  onChange={setSponsorType}
                  options={SPONSOR_TYPES}
                  placeholder="Select type..."
                />

                <EditableComboBox
                  label="Total Project Budget"
                  value={sponsorBudget}
                  onChange={setSponsorBudget}
                  options={BUDGET_OPTIONS}
                  placeholder="$10,000,000"
                />

                <EditableComboBox
                  label="Cost Match Capacity"
                  value={sponsorCostShare}
                  onChange={setSponsorCostShare}
                  options={COST_SHARE_OPTIONS}
                  placeholder="20% Match"
                />

                {/* TRL Sliders */}
                <div className="grid grid-cols-2 gap-3 bg-slate-50 p-2.5 rounded-lg border border-slate-200 md:col-span-2">
                  <div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-semibold text-slate-700">Current TRL</span>
                      <span className="font-bold text-indigo-700">TRL {sponsorCurrentTrl}</span>
                    </div>
                    <input
                      type="range"
                      min={1}
                      max={8}
                      value={sponsorCurrentTrl}
                      onChange={e => setSponsorCurrentTrl(Number(e.target.value))}
                      className="w-full accent-indigo-600 mt-1 cursor-pointer"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-semibold text-slate-700">Target TRL</span>
                      <span className="font-bold text-emerald-700">TRL {sponsorTargetTrl}</span>
                    </div>
                    <input
                      type="range"
                      min={sponsorCurrentTrl}
                      max={9}
                      value={sponsorTargetTrl}
                      onChange={e => setSponsorTargetTrl(Number(e.target.value))}
                      className="w-full accent-emerald-600 mt-1 cursor-pointer"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Primary Execute Button */}
            <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-100">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <ShieldCheck size={16} className="text-emerald-600 shrink-0" />
                <span>Grounded in <b>54,000+ historical awards</b> &amp; 112+ master clean technology models.</span>
              </div>

              <button
                type="button"
                onClick={handleExecuteStrategy}
                disabled={isExecuting}
                className="w-full sm:w-auto px-6 py-3 rounded-xl font-bold text-sm bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isExecuting ? (
                  <>
                    <Loader2 size={18} className="animate-spin text-white" />
                    <span>Synthesizing Strategy via OpenAI GPT-4o...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={18} className="text-amber-300" />
                    <span>Run Strategy Analysis</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
         RESULTS OUTPUT STUDIO
         ========================================================================= */}
      {strategyResults && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden space-y-6">
          {/* Results Header Bar */}
          <div className="p-5 bg-gradient-to-r from-slate-900 to-indigo-950 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  OpenAI GPT-4o Grounded Synthesis Complete
                </span>
                <span className="text-xs text-slate-400">|</span>
                <span className="text-xs text-slate-300">{strategyResults.llm_engine}</span>
              </div>
              <h2 className="text-lg font-bold tracking-tight">
                {strategyResults.title}
              </h2>
            </div>

            {/* PDF & Proposal Copilot Actions */}
            <div className="flex items-center gap-2.5 shrink-0">
              <button
                onClick={handleDownloadPdf}
                disabled={isDownloadingPdf}
                className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-bold border border-white/20 transition flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
              >
                {isDownloadingPdf ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <FileDown size={14} className="text-indigo-300" />
                )}
                <span>Download PDF Strategic Report</span>
              </button>

              {mode === 'project_sponsor' && (
                <button
                  onClick={handlePushToProposalCopilot}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition flex items-center gap-1.5 cursor-pointer shadow-xs"
                >
                  <span>Send to Proposal Copilot</span>
                  <ArrowUpRight size={14} />
                </button>
              )}
            </div>
          </div>

          {/* Results Tabs Bar */}
          <div className="px-5 border-b border-slate-200 flex items-center gap-4 overflow-x-auto text-xs font-semibold">
            <button
              onClick={() => setActiveTab('thesis')}
              className={`py-3 border-b-2 transition cursor-pointer flex items-center gap-1.5 ${
                activeTab === 'thesis'
                  ? 'border-indigo-600 text-indigo-600 font-bold'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <FileText size={15} />
              <span>Executive Strategic Plan</span>
            </button>

            {mode === 'funding_organization' && strategyResults.program_pathway_timeline && (
              <button
                onClick={() => setActiveTab('pathway')}
                className={`py-3 border-b-2 transition cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'pathway'
                    ? 'border-indigo-600 text-indigo-600 font-bold'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <Calendar size={15} />
                <span>Multi-Year Pathway &amp; Cadence</span>
              </button>
            )}

            <button
              onClick={() => setActiveTab('workstreams')}
              className={`py-3 border-b-2 transition cursor-pointer flex items-center gap-1.5 ${
                activeTab === 'workstreams'
                  ? 'border-indigo-600 text-indigo-600 font-bold'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Layers size={15} />
              <span>{mode === 'project_sponsor' ? 'R&D Workstreams & Milestones' : 'Stage-Gated Solicitation Design'}</span>
            </button>

            <button
              onClick={() => setActiveTab('capital_stack')}
              className={`py-3 border-b-2 transition cursor-pointer flex items-center gap-1.5 ${
                activeTab === 'capital_stack'
                  ? 'border-indigo-600 text-indigo-600 font-bold'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <TrendingUp size={15} />
              <span>{mode === 'project_sponsor' ? 'Capital Stacking & Tax Credits' : 'Market Whitespace & Gaps'}</span>
            </button>

            <button
              onClick={() => setActiveTab('awards_comps')}
              className={`py-3 border-b-2 transition cursor-pointer flex items-center gap-1.5 ${
                activeTab === 'awards_comps'
                  ? 'border-indigo-600 text-indigo-600 font-bold'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Award size={15} />
              <span>{mode === 'project_sponsor' ? 'Historical Awards & Teaming' : 'Scoring Rubric & Draft Topics'}</span>
            </button>
          </div>

          {/* ================= TAB 1: EXECUTIVE STRATEGIC PLAN ================= */}
          {activeTab === 'thesis' && (
            <div className="p-6 space-y-6">
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <Sparkles size={16} className="text-indigo-600" />
                    <span>Executive Strategic Thesis &amp; Positioning Narrative</span>
                  </h3>
                  <span className="text-[11px] text-slate-500 font-medium">
                    Synthesized from 54,000+ Database Records
                  </span>
                </div>
                <div className="prose prose-sm max-w-none text-slate-700 text-xs leading-relaxed space-y-2 whitespace-pre-line">
                  {strategyResults.executive_thesis || (strategyResults as any).program_blueprint_narrative}
                </div>
              </div>

              {/* Sponsor Specific: Win Rate Optimizations & Red Flag Mitigations */}
              {mode === 'project_sponsor' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-3">
                    <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <CheckCircle2 size={15} className="text-emerald-600" />
                      <span>Win-Rate Maximization Directives</span>
                    </h4>
                    <ul className="space-y-2 text-xs text-slate-600">
                      {strategyResults.win_rate_optimizations?.map((opt, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-indigo-600 font-bold">•</span>
                          <span>{opt}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-3">
                    <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <AlertTriangle size={15} className="text-amber-600" />
                      <span>Reviewer Red Flags &amp; Proactive Mitigations</span>
                    </h4>
                    <div className="space-y-2.5">
                      {strategyResults.reviewer_red_flags_and_mitigation?.map((item, i) => (
                        <div key={i} className="p-2.5 bg-amber-50/60 rounded-lg border border-amber-200/60 text-xs space-y-1">
                          <div className="font-semibold text-amber-900 flex items-center gap-1">
                            <span>Risk:</span>
                            <span>{item.risk}</span>
                          </div>
                          <div className="text-amber-800 text-[11px]">
                            <span className="font-medium text-emerald-800">Mitigation: </span>
                            {item.mitigation}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Funder Specific: Strategic Recommendations */}
              {mode === 'funding_organization' && strategyResults.strategic_recommendations && (
                <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-3">
                  <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                    <CheckCircle2 size={15} className="text-emerald-600" />
                    <span>Programmatic Implementation Recommendations</span>
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-slate-700">
                    {strategyResults.strategic_recommendations.map((rec, i) => (
                      <div key={i} className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-start gap-2">
                        <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center shrink-0">
                          {i + 1}
                        </span>
                        <span>{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ================= TAB 2: MULTI-YEAR PATHWAY (FUNDER ONLY) ================= */}
          {activeTab === 'pathway' && mode === 'funding_organization' && (
            <div className="p-6 space-y-6">
              {strategyResults.program_pathway_timeline && (
                <div className="space-y-4">
                  <div className="bg-indigo-50/60 border border-indigo-200 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
                    <div>
                      <span className="font-bold text-indigo-900 block text-sm">
                        {strategyResults.program_pathway_timeline.total_years} Strategic Innovation Horizon
                      </span>
                      <span className="text-indigo-700 text-[11px]">
                        Target Cadence: {strategyResults.program_pathway_timeline.annual_distribution_summary}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-3 py-1 rounded-full bg-white text-indigo-800 font-bold border border-indigo-200 text-xs shadow-2xs">
                        {funderProgramPool} Total Pool
                      </span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {strategyResults.program_pathway_timeline.milestone_roadmap?.map((rm, idx) => (
                      <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-white space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900 text-xs flex items-center gap-2">
                            <span className="w-6 h-6 rounded-full bg-slate-900 text-white text-[11px] font-bold flex items-center justify-center">
                              {idx + 1}
                            </span>
                            <span>{rm.timeframe}</span>
                          </span>
                          <span className="text-[11px] font-semibold text-indigo-700 bg-indigo-50 px-2.5 py-0.5 rounded-full border border-indigo-100">
                            {rm.awards_target}
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 pl-8">
                          <b>Strategic Focus:</b> {rm.focus}
                        </p>
                        <div className="ml-8 p-2.5 bg-emerald-50/70 border border-emerald-200 rounded-lg text-xs text-emerald-900">
                          <b>Go/No-Go Milestone Gate:</b> {rm.gate_criterion}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ================= TAB 3: WORKSTREAMS / SOLICITATION ================= */}
          {activeTab === 'workstreams' && (
            <div className="p-6 space-y-6">
              {mode === 'project_sponsor' ? (
                /* Sponsor Workstreams */
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <Layers size={16} className="text-indigo-600" />
                      <span>Milestone-Gated R&amp;D Workstream Decomposition</span>
                    </h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {strategyResults.workstream_decomposition?.map((ws, i) => (
                      <div key={i} className="p-4 rounded-xl border border-slate-200 bg-white flex flex-col justify-between space-y-3">
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-bold text-slate-900 text-xs">{ws.phase}</span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-100">
                              {ws.trl_progression}
                            </span>
                          </div>
                          <p className="text-xs text-slate-600">{ws.objective}</p>
                        </div>
                        <div className="space-y-2 pt-2 border-t border-slate-100">
                          <div className="text-[11px] font-semibold text-slate-700">Deliverables:</div>
                          <ul className="space-y-1 text-[11px] text-slate-600">
                            {ws.deliverables?.map((d, di) => (
                              <li key={di} className="flex items-start gap-1.5">
                                <span className="text-emerald-600 font-bold">✓</span>
                                <span>{d}</span>
                              </li>
                            ))}
                          </ul>
                          <div className="pt-2 flex items-center justify-between text-[11px]">
                            <span className="text-slate-500">Est. Budget:</span>
                            <span className="font-bold text-slate-900">{ws.estimated_budget}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                /* Funder Stage-Gated RFP Structure */
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <Layers size={16} className="text-indigo-600" />
                      <span>Stage-Gated Solicitation Structure &amp; Go/No-Go Milestone Gates</span>
                    </h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {strategyResults.solicitation_structure?.phases?.map((ph, i) => (
                      <div key={i} className="p-4 rounded-xl border border-slate-200 bg-white flex flex-col justify-between space-y-3">
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-bold text-slate-900 text-xs">{ph.phase_name}</span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700">
                              {ph.duration}
                            </span>
                          </div>
                          <div className="text-xs font-semibold text-indigo-700 mb-2">
                            Award Range: {ph.award_range}
                          </div>
                        </div>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-1">
                          <span className="font-bold text-slate-800 text-[11px] block">Go/No-Go Milestone Gate:</span>
                          <span className="text-slate-600 text-[11px]">{ph.go_no_go_milestone}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ================= TAB 4: CAPITAL STACK / WHITESPACE ================= */}
          {activeTab === 'capital_stack' && (
            <div className="p-6 space-y-6">
              {mode === 'project_sponsor' ? (
                /* Sponsor Capital Stack */
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <TrendingUp size={16} className="text-indigo-600" />
                      <span>Multi-Agency Non-Dilutive Capital Stacking Waterfall</span>
                    </h3>
                  </div>
                  <div className="space-y-3">
                    {strategyResults.capital_stacking_strategy?.map((layer, i) => (
                      <div key={i} className="p-4 rounded-xl border border-slate-200 bg-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-100">
                              {layer.layer}
                            </span>
                            <span className="font-bold text-xs text-slate-900">{layer.target_program}</span>
                          </div>
                          <p className="text-xs text-slate-600">{layer.strategic_utility}</p>
                        </div>
                        <div className="text-right shrink-0">
                          <div className="font-bold text-sm text-emerald-600">{layer.estimated_amount}</div>
                          <div className="text-[10px] text-slate-500">Match: {layer.cost_share_required}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                /* Funder Whitespace & Market Saturation Analysis */
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <TrendingUp size={16} className="text-indigo-600" />
                      <span>Market Saturation vs. Critical Whitespace Analysis (54k+ Awards Evaluated)</span>
                    </h3>
                  </div>
                  <div className="space-y-3">
                    {strategyResults.whitespace_analysis?.map((ws, i) => (
                      <div key={i} className="p-4 rounded-xl border border-slate-200 bg-white space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-xs text-slate-900">{ws.technology_area}</span>
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
                            {ws.saturation_status}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-xs text-slate-500">
                          <span>Historical Grants: <b>{ws.historical_awards_count} awards</b></span>
                          <span>Tracked Capital: <b>{ws.historical_funding_tracked}</b></span>
                        </div>
                        <div className="p-2.5 bg-slate-50 rounded-lg text-xs text-slate-700">
                          <b>Programmatic Opportunity:</b> {ws.programmatic_gap_recommendation}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ================= TAB 5: AWARDS COMPS & TEAMING / RUBRIC ================= */}
          {activeTab === 'awards_comps' && (
            <div className="p-6 space-y-6">
              {mode === 'project_sponsor' ? (
                /* Historical Comps & Teaming Partners */
                <div className="space-y-6">
                  {/* Historical Award Comps */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <Award size={16} className="text-indigo-600" />
                      <span>Empirical Peer Award Comps (U.S. Energy Innovation Database)</span>
                    </h3>
                    <div className="space-y-2">
                      {strategyResults.historical_award_comps?.slice(0, 5).map((comp, i) => (
                        <div key={i} className="p-3 bg-white border border-slate-200 rounded-lg flex items-center justify-between text-xs">
                          <div>
                            <span className="font-bold text-slate-900 block">{comp.project_title}</span>
                            <span className="text-slate-500 text-[11px]">
                              {comp.recipient_name} ({comp.recipient_type}) • {comp.agency} ({comp.year})
                            </span>
                          </div>
                          <span className="font-bold text-emerald-600 shrink-0">{comp.award_amount_fmt}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Teaming Ecosystem */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <Users size={16} className="text-indigo-600" />
                      <span>Recommended Consortia &amp; Teaming Partners</span>
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {strategyResults.teaming_ecosystem?.slice(0, 6).map((partner, i) => (
                        <div key={i} className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1 text-xs">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-900">{partner.name}</span>
                            <span className="text-[10px] text-slate-500 font-medium">{partner.type}</span>
                          </div>
                          <p className="text-[11px] text-slate-600">{partner.recommendation_rationale}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                /* Scoring Rubric & Draft FOA Topics */
                <div className="space-y-6">
                  {/* Weighted Scoring Rubric */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <Award size={16} className="text-indigo-600" />
                      <span>Weighted Evaluation &amp; Scoring Rubric</span>
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {strategyResults.scoring_rubric?.map((rubric, i) => (
                        <div key={i} className="p-3.5 bg-white border border-slate-200 rounded-xl space-y-1">
                          <span className="font-bold text-xs text-indigo-900 block">{rubric.criterion}</span>
                          <p className="text-xs text-slate-600">{rubric.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Draft FOA Topics */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <FileText size={16} className="text-indigo-600" />
                      <span>Ready-to-Issue Draft FOA Solicitation Topics</span>
                    </h3>
                    <div className="space-y-3">
                      {strategyResults.draft_foa_topics?.map((topic, i) => (
                        <div key={i} className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-xs">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-900">{topic.topic_id}</span>
                            <span className="text-emerald-700 font-semibold text-[11px]">{topic.cost_share_rule}</span>
                          </div>
                          <p className="text-slate-600">{topic.scope}</p>
                          <div className="pt-1">
                            <span className="font-semibold text-slate-700 block mb-1">Technical Targets:</span>
                            <ul className="space-y-0.5 text-slate-600 text-[11px]">
                              {topic.technical_targets?.map((target, ti) => (
                                <li key={ti} className="flex items-center gap-1.5">
                                  <span className="text-indigo-600">•</span>
                                  <span>{target}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
