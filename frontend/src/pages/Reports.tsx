import React, { useState, useEffect, useMemo } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  FileText, Search, Download, Layers, MapPin, Share2, Activity,
  Zap, Scale, TrendingUp, Globe, Loader2, Play,
  CheckCheck, X, Flame, Sun, BatteryCharging, Cpu, Home,
  Compass, Eye, EyeOff, Building, Target, Users, Key, Sparkles, ShieldCheck,
  RotateCw, RefreshCw, Database, Check, AlertCircle, Info, ExternalLink, Settings
} from 'lucide-react';
import { saveAs } from 'file-saver';
import { api, ReportPreset, ReportGenerateRequest } from '../api/client';
import { OrgLogo } from '../components/OrgLogo';
import { useNyserda } from '../context/NyserdaContext';

const CATEGORIES = [
  'All Categories',
  'Macro & Policy Strategy',
  'Project Strategy',
  'Technology Domains',
  'Commercialization'
];

// Normalizes any category variant from API to the canonical 4 categories
export function normalizeCategory(cat?: string): string {
  if (!cat) return 'Macro & Policy Strategy';
  const lower = cat.toLowerCase().trim();
  if (lower.includes('macro') || lower.includes('policy')) return 'Macro & Policy Strategy';
  if (lower.includes('project') || lower.includes('network') || lower.includes('geospatial') || lower.includes('consorti')) return 'Project Strategy';
  if (lower.includes('tech') || lower.includes('domain') || lower.includes('vertical')) return 'Technology Domains';
  if (lower.includes('commerc') || lower.includes('market') || lower.includes('capital') || lower.includes('due diligence') || lower.includes('workforce') || lower.includes('labor')) return 'Commercialization';
  return 'Macro & Policy Strategy';
}

const DEFAULT_PRESETS: ReportPreset[] = [
  // 0. Core Technical Architecture & Database Reference Manual (Hidden for now)
  // {
  //   "id": "cleangrid_database_docs",
  //   "title": "CleanGrid IQ Database",
  //   "subtitle": "Comprehensive Technical Data Architecture, Source Provenance, Vintage Specifications, Relational Graph Topology, and Stakeholder Decision Utility Reference Manual",
  //   "category": "Macro & Policy Strategy",
  //   "target_audience": "State Energy Directors, Federal Program Managers, Clean Tech Project Sponsors, Climate Tech VCs, Regulated Utilities, University Research VPs, and Community Consortia",
  //   "badge": "Database Architecture & Reference",
  //   "icon": "Database",
  //   "pages": 24,
  //   "capital_tracked": "$98.98B Tracked",
  //   "awards_count": "54,305 Awards (35-Yr Arc)",
  //   "key_focus": "Exhaustive technical documentation of all 10 data layers, 31+ public source connectors, 35-year longitudinal vintage (1991–2026), 3-tier credibility framework, relational knowledge graph topology, and 7-persona stakeholder decision-maker utility matrix."
  // },

  // 1. Macro & Policy Strategy (Flagship Strategic Briefings & Institutional Blueprints)
  {
    "id": "state_partnership_ecosystem",
    "title": "State Innovation Program Partnership & Ecosystem Expansion Lessons Learned and Future Strategies",
    "subtitle": "The Definitive Retrospective and Forward Blueprint: Analyzing 25 Years of State-Level Clean Energy Consortia, Multi-Jurisdictional Coalitions, Hardtech Incubators, Regulated Utility Alignment, and Frontline Equity Co-Design (2000–2026 Empirical Arc and 2026–2035 Strategic Roadmap)",
    "category": "Macro & Policy Strategy",
    "target_audience": "State Energy Leadership, Governors' Energy Cabinets, Incubator Directors, Utility Innovation Officers, Community Consortia Leads, National Labs",
    "badge": "Ecosystem Blueprint",
    "icon": "Share2",
    "pages": 21,
    "capital_tracked": "$98.98B Tracked",
    "awards_count": "54,313 Awards (25-Yr Arc)",
    "key_focus": "25-year empirical retrospective of state clean energy consortia, incubator networks (NYSERDA CEI, MassCEC Greentown, CalSEED, ESD NY Ventures), 3.8x federal co-funding multiplier, utility regulatory sandboxes, Justice40 equity co-design, and 2026-2035 strategic blueprints."
  },
  {
    "id": "future_research_pathways_flagship",
    "title": "Future Research Pathways for Funding Institutions Across Technology & Fuel Domains",
    "subtitle": "The Definitive Programmatic Blueprint for State & Federal Energy Agencies, National Laboratories, Philanthropies, and Utility R&D Directors: Designing High-Impact Solicitations, Stage-Gated Milestone Architectures, and Multi-Tiered Capital Stacks for the 2026–2035 Horizon",
    "category": "Macro & Policy Strategy",
    "target_audience": "State Energy Directors (NYSERDA, CEC, MassCEC, ESD), Federal Program Leads (DOE ARPA-E, EERE, OCED, FECM), Philanthropies (Rockefeller, Bloomberg, Bezos), Utility R&D VPs",
    "badge": "Institutional Blueprint",
    "icon": "Layers",
    "pages": 21,
    "capital_tracked": "$98.98B Tracked",
    "awards_count": "54,313 Awards (All Sectors)",
    "key_focus": "Optimal programmatic funding strategies by institution type (Federal, State, Labs, Philanthropy, Utility), high-yield research pathways vs. stranded risks across 8 technology domains, open enrollment vs. phased RFP mechanics, 4-stage Go/No-Go contracting gates, and 2026–2035 institutional execution playbooks."
  },
  {
    "id": "us_energy_innovation_landscape_flagship",
    "title": "Understanding the U.S. Energy Innovation Landscape: Past, Present and Future",
    "subtitle": "The Definitive Nationwide Meta-Synthesis: Evaluating 54,313 Project Awards, 5,741 Solicitations, 174 Programs, and 13,781 Institutions Across 50 Years of Policy, Physical Deployment Friction, and 2026–2035 Horizon Realities",
    "category": "Macro & Policy Strategy",
    "target_audience": "Cabinet Secretaries, Governors' Energy Cabinets, Corporate C-Suite Leadership, Infrastructure Funds, Utility Executives",
    "badge": "Flagship Meta-Report",
    "icon": "Compass",
    "pages": 21,
    "capital_tracked": "$98.98B Tracked",
    "awards_count": "54,313 Awards (50-Yr Arc)",
    "key_focus": "Comprehensive meta-synthesis integrating findings across all strategic monographs: 50-year policy evolution, cross-sector capital stacks, TRL 4-7 Valley of Death bottlenecks, institutional broker centrality, and 2026-2035 executive roadmaps."
  },
  {
    "id": "programmatic_outcomes_roi_scorecard",
    "title": "Clean Energy Outcomes, GHG Abatement & Programmatic ROI Scorecard",
    "subtitle": "Comprehensive Programmatic Evaluation Across 5,741 Solicitations: Return on Public Grant Dollar, Carbon Abatement Efficiency, Job Creation Multipliers, and Commercialization Rates",
    "category": "Macro & Policy Strategy",
    "target_audience": "Legislative Oversight Committees, Agency Evaluation Directors, Philanthropic Trustees, State Energy Officials",
    "badge": "Program ROI Scorecard",
    "icon": "Target",
    "pages": 21,
    "capital_tracked": "$98.98B Evaluated",
    "awards_count": "5,741 Solicitations",
    "key_focus": "Standardized return on public grant dollar metrics: Metric Tons CO2e Avoided / $10k Awarded, FTE Jobs / $1M, Private Capital Leverage multiples (1.5x - 8.3x), and Technology Readiness Level (TRL) advancement rates."
  },
  {
    "id": "federal_state_synergy",
    "title": "Federal vs. State Energy Agency Synergies & Co-Funding Matrix",
    "subtitle": "Intergovernmental policy analysis quantifying the catalytic multiplier effect of state seed funding in winning federal awards.",
    "category": "Macro & Policy Strategy",
    "target_audience": "State Energy Leadership, DOE OCED Directors, Policy Advisors",
    "badge": "Synergy Matrix",
    "icon": "Scale",
    "pages": 21,
    "capital_tracked": "3.8x Multiplier",
    "awards_count": "Dual-Funded Ledgers",
    "key_focus": "State due diligence multiplier, federal matching win rates, and intergovernmental co-investment."
  },
  {
    "id": "climate_justice_equity",
    "title": "Climate Justice, Disadvantaged Communities & Equitable Capital Deployment Atlas",
    "subtitle": "Empirical analysis of statutory 35-40% Disadvantaged Communities (DAC) capital deployment mandates, Community Benefits Plans (CBPs), and frontline workforce equity.",
    "category": "Macro & Policy Strategy",
    "target_audience": "Chief Sustainability Officers, State Environmental Justice Directors, Municipal Leaders, Community Consortia",
    "badge": "Justice40 & Equity",
    "icon": "Scale",
    "pages": 21,
    "capital_tracked": "$18.70B",
    "awards_count": "6,412 Awards",
    "key_focus": "Federal Justice40 compliance, state DAC investment targets (CLCPA 35-40%), community benefits plan (CBP) scoring dynamics, and municipal equitable deployment."
  },
  {
    "id": "regional_hubs_atlas",
    "title": "Regional Clean Tech Innovation Hubs & Geospatial Capital Atlas",
    "subtitle": "High-resolution geospatial intelligence mapping clean tech capital concentration, state competitiveness rankings, and regional manufacturing corridors.",
    "category": "Macro & Policy Strategy",
    "target_audience": "State Economic Development Councils, Regional Hub Directors, Site Selectors, Infrastructure Funds",
    "badge": "Regional Hubs",
    "icon": "MapPin",
    "pages": 21,
    "capital_tracked": "$98.98B",
    "awards_count": "50 States & Hubs",
    "key_focus": "Metropolitan cluster agglomeration, interstate supply chain specialization (Northeast R&D vs Southeast Battery Belt), and secondary market grant capture disparities."
  },
  {
    "id": "state_innovation_evolution",
    "title": "The Evolution of State Clean Energy Innovation: Governance, SBC Tariffs & 2035 Horizon",
    "subtitle": "Institutional history, statutory policy milestones, and 10-year forward strategic roadmaps for state energy authorities.",
    "category": "Macro & Policy Strategy",
    "target_audience": "Governors' Policy Advisors, State Energy Directors, Legislative Energy Chairs",
    "badge": "State Evolution",
    "icon": "Layers",
    "pages": 21,
    "capital_tracked": "$98.98B",
    "awards_count": "50-Year Arc",
    "key_focus": "Historical policy mandates (1975-2026), institutional governance models, ratepayer SBC funding mechanisms, and 2026-2035 zero-emission milestones."
  },

  // 2. Commercialization & Capital Markets (Actionable Diagnostics & Strategies)
  {
    "id": "state_commercialization_strategies",
    "title": "State Innovation Program Commercialization Strategies to Maximize Results",
    "subtitle": "The Definitive Strategic Framework for State Clean Energy Agencies, Green Banks, and Regional Accelerators: Overcoming the Mid-TRL Valley of Death, Optimizing Stage-Gated Non-Dilutive Capital Stacks, Mobilizing Private Co-Investment, and Scaling Clean Technologies from Lab to Market",
    "category": "Commercialization",
    "target_audience": "State Energy Directors (NYSERDA, CEC, MassCEC, NJEDA, ESD), Green Bank Investment Officers, Climate VCs, Accelerators, Clean Tech Project Developers",
    "badge": "Commercialization Strategy",
    "icon": "TrendingUp",
    "pages": 21,
    "capital_tracked": "$98.98B Tracked",
    "awards_count": "13,781 Scale-Ups",
    "key_focus": "Overcoming the TRL 4-7 Valley of Death, 4-stage milestone-contingent contracting, 5.2x private capital syndication, pre-negotiated utility testbed access, university tech transfer reform, and MRL 1-10 manufacturing escalators."
  },
  {
    "id": "clean_tech_ip_patent_atlas",
    "title": "Clean Tech Intellectual Property, Bayh-Dole Citations & Patent Commercialization Atlas",
    "subtitle": "National Assessment of Government-Backed Patents, CPC Classification Velocity, Corporate Citation Networks, and Technology Transfer Moats",
    "category": "Commercialization",
    "target_audience": "Corporate M&A, VC Technical Partners, University Tech Transfer Offices, USPTO Counsel",
    "badge": "Patent & IP Atlas",
    "icon": "ShieldCheck",
    "pages": 21,
    "capital_tracked": "182 USPTO Patents",
    "awards_count": "12 Tech Domains",
    "key_focus": "Bayh-Dole compliance, downstream corporate citations of government patents, solid-state battery moats, electrochemical cement IP, and patent valuation multiples across 182 verified USPTO patents."
  },
  {
    "id": "venture_capital_syndication_report",
    "title": "Private Capital Syndication, Venture Backing & FOAK Valuation Benchmark",
    "subtitle": "Empirical Analysis of Non-Dilutive Grant Leverage Across 173 Institutional Venture Capital Rounds ($20.01B USD Private Equity Deployed), FOAK Valuation Trajectories, and Post-Grant Equity Acceleration",
    "category": "Commercialization",
    "target_audience": "Climate Tech VCs, Private Equity, Growth Infrastructure Funds, Green Banks, Corporate Venture (CVC)",
    "badge": "Venture Syndication",
    "icon": "TrendingUp",
    "pages": 21,
    "capital_tracked": "$20.01B VC Syndicated",
    "awards_count": "173 Equity Rounds",
    "key_focus": "Grant-to-venture timelines (average 38 months), post-grant valuation step-ups (4.2x from Series A to B), lead climate fund syndication networks, and FOAK blended debt-equity stacks."
  },

  {
    "id": "private_capital_catalyst",
    "title": "First-of-a-Kind (FOAK) Deployment & Private Capital Syndication Intelligence",
    "subtitle": "Strategic analysis of private match ratios, venture capital co-investment dynamics, and FOAK de-risking mechanisms across 13,700+ clean tech companies.",
    "category": "Commercialization",
    "target_audience": "Climate Tech VCs, Infrastructure Private Equity, Corporate Venture (CVC), Green Bank Investment Officers",
    "badge": "FOAK & Capital Stack",
    "icon": "TrendingUp",
    "pages": 21,
    "capital_tracked": "$38.50B Match",
    "awards_count": "13,706 Companies",
    "key_focus": "FOAK project financing structures, private matching leverage (1.5x - 5.2x across sectors), commercialization stage transitions (Seed/Lab -> Pilot -> FOAK Commercial -> Bankable Scale), debt-equity blended finance, and corporate off-take agreements."
  },
  {
    "id": "multistage_sankey_flow",
    "title": "Multi-Stage Capital Flow & 'Valley of Death' Pipeline Intelligence",
    "subtitle": "Stage-gate progression analysis tracking capital conduits from basic R&D through demonstration and commercial scale.",
    "category": "Commercialization",
    "target_audience": "Program Managers, ARPA-E / DOE Directors, Venture Capitalists",
    "badge": "Pipeline Diagnostics",
    "icon": "Layers",
    "pages": 21,
    "capital_tracked": "TRL 1-9 Conduits",
    "awards_count": "78% Attrition Diagnostic",
    "key_focus": "TRL 4-7 demonstration funding cliff, catalytic FOAK blended finance, and milestone tranche structures."
  },
  {
    "id": "awardee_due_diligence",
    "title": "Clean Tech Awardee & Market Frontier Due Diligence Briefing",
    "subtitle": "Due diligence dossier on high-growth venture-ready recipients with repeat grant track records.",
    "category": "Commercialization",
    "target_audience": "Climate Tech Investors, Corporate Strategy, Prime Contractors",
    "badge": "Venture Diligence",
    "icon": "TrendingUp",
    "pages": 21,
    "capital_tracked": "Top Growth Cohort",
    "awards_count": "Multi-Award Firms",
    "key_focus": "Repeat award track records, commercialization milestones, private match leverage, and venture readiness."
  },
  {
    "id": "workforce_transition_report",
    "title": "Clean Energy Workforce Transition & Green Labor Economics Briefing",
    "subtitle": "Comprehensive Strategic Assessment of 1.2M Worker Demand, Union Registered Apprenticeships, and Gas Utility Labor Transition.",
    "category": "Commercialization",
    "target_audience": "Building Trade Unions, Community College Leadership, Workforce Policy Directors",
    "badge": "Labor & Workforce",
    "icon": "Layers",
    "pages": 21,
    "capital_tracked": "$14.10B",
    "awards_count": "Union & Non-Union",
    "key_focus": "1.2M clean energy worker demand, union registered apprenticeships, prevailing wage multipliers, and gas utility labor transition."
  },

  // 3. Project Strategy & Consortia (4 Actionable Playbooks)
  {
    "id": "winning_proposals_meta_strategy",
    "title": "Winning Proposal Architectures & Scoring Criteria: Nationwide Meta-Analysis",
    "subtitle": "Data-driven cross-sector meta-analysis of winning proposals across 54,305 awards and 5,699 opportunities spanning 100-point scoring mechanics, concept papers, cost-share splits, and submission timing.",
    "category": "Project Strategy",
    "target_audience": "Project Sponsors, Energy Transition Developers, Proposal Directors, Infrastructure Funds, Clean Tech Primes",
    "badge": "Winning Proposals Meta-Analysis",
    "icon": "Target",
    "pages": 21,
    "capital_tracked": "$98.98B Tracked",
    "awards_count": "54,305 Winning Awards",
    "key_focus": "Empirical win-rate factors, 100-point scoring rubric mechanics, open vs rolling enrollment capture timing, 20-50% cost-share syndication, concept paper de-risking, and actionable C-Suite execution playbooks."
  },
  {
    "id": "grant_stacking_consortia",
    "title": "Consortia Formation & Multi-Agency Grant Stacking Playbook",
    "subtitle": "Empirical blueprint for assembling winning prime-sub teaming structures, utility partnerships, and multi-agency sequential capital stacking (State -> Federal -> Green Bank).",
    "category": "Project Strategy",
    "target_audience": "Consortia Leads, Prime Contractors, Utility Innovation Officers, Energy Developers",
    "badge": "Consortia & Stacking",
    "icon": "Share2",
    "pages": 21,
    "capital_tracked": "3.8x Co-Funding",
    "awards_count": "146 Utility & Funder Orgs",
    "key_focus": "Sequential capital stacking pathways (State Seed -> Federal Pilot -> FOAK Infrastructure -> Concessionary Green Bank Debt), high-win consortia topology (Developer + Lab/University + Utility + Community Partner), utility interconnection channels, and 2026-2035 funding trend pivots."
  },
  {
    "id": "opportunity_lineage_forecaster",
    "title": "Opportunity Lineage, Predecessor-Successor Dynamics & Reauthorization Forecaster",
    "subtitle": "Predictive Intelligence Mapping 2,751 Funding Opportunity Lineages, Recurring Solicitation Cadences, Predecessor-Successor Sequences, and 12-Month Forward Funding Calendars",
    "category": "Project Strategy",
    "target_audience": "Project Developers, Consortia Directors, Grants Officers, Government Affairs SVPs, Clean Tech Primes",
    "badge": "Lineage Forecaster",
    "icon": "Compass",
    "pages": 21,
    "capital_tracked": "5,708 Solicitations Mapped",
    "awards_count": "2,751 Relational Linkages",
    "key_focus": "Predecessor-successor evolution, recurring annual RFP cadences (USDA, EPA, DOE), statutory appropriations lifecycles (BIL, IRA), and 12-month advance concept paper engineering."
  },
  {
    "id": "pi_academic_leadership_benchmark",
    "title": "Principal Investigator (PI) & Academic Innovation Leadership Benchmark",
    "subtitle": "National Assessment of 42,378 Awarded Principal Investigators (PIs), University Research Centers, National Laboratory Leads, and Cross-Institutional Teaming Consortia",
    "category": "Project Strategy",
    "target_audience": "University VPs of Research, Prime Contractors, National Lab Directors, Corporate R&D SVPs",
    "badge": "PI Leadership Benchmark",
    "icon": "Users",
    "pages": 21,
    "capital_tracked": "$13.5B Academic Capital",
    "awards_count": "42,378 PI-Led Awards",
    "key_focus": "Top-decile academic Principal Investigators, university research system rankings (UC System, MIT, Stanford, Cornell), national lab leadership, and prime-sub teaming structures for large federal solicitations."
  },

  // 4. Technology Domain Strategic Deep-Dives (10 Vertical Market Dossiers)
  {
    "id": "alt_fuels_dossier",
    "title": "Alternative Fuels & Clean Molecules Strategic Dossier",
    "subtitle": "Comprehensive vertical intelligence across Clean Hydrogen (Electrolysis), SAF, Bioenergy, CCUS, and IRA 45V/45Q compliance.",
    "category": "Technology Domains",
    "target_audience": "Chief Technology Officers, Hydrogen Hub Consortia, Chemical Industry VPs",
    "badge": "Clean Molecules",
    "icon": "Flame",
    "pages": 21,
    "capital_tracked": "$17.06B",
    "awards_count": "1,944 Orgs",
    "key_focus": "Electrolyzer Capex curves, IRA 45V 3-pillars guidance, SAF blending mandates, point-source CCUS, and verified patent holdings."
  },
  {
    "id": "clean_gen_dossier",
    "title": "Clean Energy Generation & Offshore Systems Strategic Dossier",
    "subtitle": "Strategic analysis of 9 GW offshore wind staging, advanced agrivoltaics, perovskite tandem solar, and deep geothermal EGS.",
    "category": "Technology Domains",
    "target_audience": "Power Generation SVPs, Offshore Wind Developers, Solar Consortium Leads",
    "badge": "Generation & OSW",
    "icon": "Sun",
    "pages": 21,
    "capital_tracked": "$6.51B",
    "awards_count": "2,442 Orgs",
    "key_focus": "Offshore wind port staging, supply chain bottlenecks, bifacial solar density, tandem cell patents, and Small Modular Reactors (SMRs)."
  },
  {
    "id": "energy_storage_dossier",
    "title": "Energy Storage & Advanced Battery Chemistries Strategic Dossier",
    "subtitle": "Deep-dive on 6 GW storage mandates, 10-100hr Long-Duration Energy Storage (LDES), NFPA 855 safety, and battery recycling.",
    "category": "Technology Domains",
    "target_audience": "BESS Developers, Battery Tech VCs, Utility Grid Planners",
    "badge": "Energy Storage",
    "icon": "BatteryCharging",
    "pages": 21,
    "capital_tracked": "$19.64B",
    "awards_count": "2,169 Orgs",
    "key_focus": "Iron-air & flow chemistries, thermal runaway safety standards, solid-state garnet patents, and domestic gigafactory investments."
  },
  {
    "id": "grid_modernization_dossier",
    "title": "Grid Modernization & Transmission Infrastructure Strategic Dossier",
    "subtitle": "High-Voltage Direct Current (HVDC) corridors, FERC Order 1920 planning, Dynamic Line Rating (DLR), and IEEE 2030.5 DERMS.",
    "category": "Technology Domains",
    "target_audience": "Electric Utility Planners, Transmission Operators, Grid Hardware OEMs",
    "badge": "Grid & Transmission",
    "icon": "Activity",
    "pages": 21,
    "capital_tracked": "$10.57B",
    "awards_count": "2,781 Orgs",
    "key_focus": "HVDC subsea cables, Dynamic Line Rating (DLR) sensors, ADMS automation, and substation digital twins."
  },
  {
    "id": "buildings_thermal_dossier",
    "title": "Building Decarbonization & Thermal Energy Networks Strategic Dossier",
    "subtitle": "District geothermal Utility Thermal Energy Networks (TENs), cold-climate heat pump scale, and municipal building performance standards.",
    "category": "Technology Domains",
    "target_audience": "Real Estate Executives, Municipal Sustainability Directors, HVAC OEMs",
    "badge": "Thermal Networks",
    "icon": "Home",
    "pages": 21,
    "capital_tracked": "$24.51B",
    "awards_count": "949 Orgs",
    "key_focus": "District geothermal loops, 60% winter peak electric reduction, building envelope retrofits, and carbon caps."
  },
  {
    "id": "ai_datacenter_dossier",
    "title": "Emerging AI & Data Center Energy Innovation Strategic Dossier",
    "subtitle": "Gigawatt-scale AI compute load balancing, behind-the-meter clean microgrids, direct-to-chip liquid cooling, and waste heat export.",
    "category": "Technology Domains",
    "target_audience": "Hyperscale Operators (Cloud/AI), Data Center Developers, Energy Software CTOs",
    "badge": "AI & Compute Power",
    "icon": "Cpu",
    "pages": 21,
    "capital_tracked": "$3.95B",
    "awards_count": "933 Orgs",
    "key_focus": "Behind-the-meter SMR/geothermal co-location, 150-200% load growth by 2030, and liquid immersion cooling."
  },
  {
    "id": "transportation_ev_dossier",
    "title": "Transportation Electrification & Heavy-Duty Fleet Decarbonization Strategic Dossier",
    "subtitle": "Comprehensive Strategic Assessment of Medium- & Heavy-Duty Trucks, Megawatt Charging Systems (MCS), Transit Depots, and V2G Integration.",
    "category": "Technology Domains",
    "target_audience": "Fleet Directors, Heavy Truck OEMs, Transit Authorities, Utility Planners",
    "badge": "Fleet Electrification",
    "icon": "Activity",
    "pages": 21,
    "capital_tracked": "$22.40B",
    "awards_count": "2,488 Orgs",
    "key_focus": "MHDV total cost of ownership (TCO), SAE J3271 Megawatt Charging, depot smart load balancing, and V2G peak shaving."
  },
  {
    "id": "industrial_decarb_dossier",
    "title": "Industrial Decarbonization & Clean Process Heat Strategic Dossier",
    "subtitle": "High-temperature thermal energy storage (1,500°C), industrial high-lift heat pumps (150-200°C steam), green steel, and low-carbon cement.",
    "category": "Technology Domains",
    "target_audience": "Plant Operations VPs, Heavy Industry OEMs, Chemical Engineering Leaders",
    "badge": "Industrial Heat",
    "icon": "Flame",
    "pages": 21,
    "capital_tracked": "$20.60B",
    "awards_count": "2,914 Orgs",
    "key_focus": "High-temperature thermal batteries (crushed rock/molten salt), industrial heat pumps, H2-DRI steelmaking, and electrochemical cement patents."
  },
  {
    "id": "critical_minerals_dossier",
    "title": "Critical Minerals, Rare Earth Elements & Supply Chain Security Strategic Dossier",
    "subtitle": "National Assessment of Lithium, Nickel, Cobalt, Graphite, Neodymium Magnets, Geothermal Brine Extraction, and Defense Production Act Mandates.",
    "category": "Technology Domains",
    "target_audience": "Battery Gigafactory Executives, Mining & Refining Officers, Defense Supply Chain Directors, Hyperscale Hardware Leads",
    "badge": "Critical Minerals",
    "icon": "Layers",
    "pages": 21,
    "capital_tracked": "$20.40B",
    "awards_count": "2,140 Orgs",
    "key_focus": "Direct Lithium Extraction (DLE), synthetic graphite, permanent magnet sintered manufacturing, WBG gallium/germanium semiconductors, and IRA 30D/45X FEOC compliance."
  },
  {
    "id": "ai_critical_minerals_supply_chain",
    "title": "AI Infrastructure & Critical Minerals: The Role, Limits, and Frontiers of Energy Innovation",
    "subtitle": "An Empirical Investigation Using The CleanGrants Database: Quantifying Hyperscale Material Intensities ($3.55B in Tracked Grants), Upstream Refining Realities, and What Clean Tech Innovation CAN vs. CANNOT Alleviate",
    "category": "Technology Domains",
    "target_audience": "Hyperscale Infrastructure Leaders, Energy & Minerals Policymakers, Climate Tech Investors, Semiconductor & Balance-of-Plant OEMs",
    "badge": "AI & Minerals Frontier",
    "icon": "Cpu",
    "pages": 21,
    "capital_tracked": "$3.55B Tracked",
    "awards_count": "2,623 Awards",
    "key_focus": "Empirical quantification of 100 MW hyperscale material intensities (copper, rare earths, gallium/germanium, lithium, HALEU), what clean tech CAN alleviate (380V DC, reluctance motors, closed-loop hydrometallurgy) vs. CANNOT alleviate (transformer physical mass, thermodynamics, 7-12 yr mine lead times)."
  },
  {
    "id": "advanced_nuclear_smr",
    "title": "Advanced Nuclear Energy & Small Modular Reactors (SMRs) Strategic Dossier",
    "subtitle": "National Assessment of Gen IV Reactor Architectures, HALEU Fuel Supply Chains, NRC Part 53 Licensing, and Hyperscale Data Center Power.",
    "category": "Technology Domains",
    "target_audience": "Utility Generation SVPs, Hyperscale Tech Planners, Nuclear Regulatory Counsel",
    "badge": "Advanced Nuclear",
    "icon": "Zap",
    "pages": 21,
    "capital_tracked": "$18.90B",
    "awards_count": "1,820 Orgs",
    "key_focus": "Sodium Fast Reactors, HTGR industrial steam, HALEU centrifuge enrichment, coal-to-nuclear repowering, and 24/7/365 AI data center microgrids."
  },
  {
    "id": "nuclear_fusion_dossier",
    "title": "Nuclear Fusion Energy & Advanced Plasma Architectures Strategic Dossier",
    "subtitle": "National Assessment of Magnetic Confinement (Tokamaks, Stellarators, FRCs), Inertial Fusion, High-Temperature Superconductors (HTS), NRC 10 CFR Part 30 Licensing, and Hyperscale AI Power Off-take.",
    "category": "Technology Domains",
    "target_audience": "Hyperscale Compute Executives, Plasma Physicists, Climate VCs, Utility Resource Planners, Defense & Energy Policy Directors",
    "badge": "Commercial Fusion",
    "icon": "Sun",
    "pages": 21,
    "capital_tracked": "$9.40B Private/Public",
    "awards_count": "1,060+ Orgs",
    "key_focus": "High-Field HTS Tokamaks (SPARC/ARC), Stellarators, FRCs, Sheared-Flow Z-Pinch, Laser ICF, REBCO tape scaling, 2035 Tritium supply cliff, NRC Part 30 materials licensing, and behind-the-meter AI compute microgrids."
  }
];

export default function Reports() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  
  // OpenAI API Key Configuration
  const [openaiApiKey, setOpenaiApiKey] = useState<string>(() => localStorage.getItem('energysignal_openai_api_key') || localStorage.getItem('openai_api_key') || localStorage.getItem('cleangrants_openai_api_key') || '');
  const [tempApiKey, setTempApiKey] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('gpt-4o-mini');
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [showKeyVisibility, setShowKeyVisibility] = useState(false);
  const [isClearingCache, setIsClearingCache] = useState(false);
  const [keySavedToast, setKeySavedToast] = useState<string | null>(null);
  const [isBackendConfigured, setIsBackendConfigured] = useState(false);

  // Preview Drawer Modal
  const [previewPreset, setPreviewPreset] = useState<any>(null);
  const [previewData, setPreviewData] = useState<any>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  // Pipeline execution modal
  const [showPipelineModal, setShowPipelineModal] = useState(false);
  const [pipelineResult, setPipelineResult] = useState<any>(null);

  // Check backend OpenAI status on mount
  useEffect(() => {
    fetch('/api/chat/status')
      .then((res) => res.json())
      .then((data) => {
        if (data.openai_configured) {
          setIsBackendConfigured(true);
          if (!openaiApiKey) {
            setOpenaiApiKey('backend-configured');
          }
        }
      })
      .catch(() => {});
  }, []);

  const { includeNyserda, isNyserda } = useNyserda();

  // Fetch presets catalog
  const { data: presetsData } = useQuery({
    queryKey: ['report-presets-library', includeNyserda],
    queryFn: () => api.getReportPresets(),
    staleTime: 0,
    refetchOnMount: true,
  });

  const rawReportsList: any[] = (presetsData?.presets && presetsData.presets.length > 0) ? presetsData.presets : DEFAULT_PRESETS;
  const reportsList: any[] = useMemo(() => {
    if (includeNyserda) return rawReportsList;
    return rawReportsList.filter((r: any) => {
      if (r.id && (r.id.toLowerCase().includes('nyserda') || isNyserda(r.id))) return false;
      return true;
    });
  }, [rawReportsList, includeNyserda, isNyserda]);

  const handleSaveApiKey = async (andRegenerate: boolean = false) => {
    const trimmed = tempApiKey.trim();
    setOpenaiApiKey(trimmed);
    if (trimmed && trimmed !== 'backend-configured') {
      localStorage.setItem('energysignal_openai_api_key', trimmed);
      localStorage.setItem('openai_api_key', trimmed);
      try {
        await fetch('/api/chat/set-api-key', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ api_key: trimmed }),
        });
      } catch (e) {
        console.error('Failed to sync API key with backend:', e);
      }
      setKeySavedToast('OpenAI API key saved. Reports will synthesize using live LLM.');
      setTimeout(() => setKeySavedToast(null), 4000);
    } else if (!trimmed) {
      localStorage.removeItem('energysignal_openai_api_key');
      localStorage.removeItem('openai_api_key');
      localStorage.removeItem('cleangrants_openai_api_key');
      try {
        await fetch('/api/chat/set-api-key', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ api_key: '' }),
        });
      } catch (e) {}
      setKeySavedToast('OpenAI API key cleared. Reports will use deterministic strategy engine.');
      setTimeout(() => setKeySavedToast(null), 4000);
    }
    setShowApiKeyModal(false);

    if (andRegenerate) {
      try {
        await api.clearReportCache();
      } catch (e) {
        console.error('Failed to clear report cache:', e);
      }
      if (previewPreset) {
        handlePreviewReport(previewPreset, true, trimmed || undefined);
      } else {
        setShowPipelineModal(true);
        pipelineMutation.mutate();
      }
    }
  };

  const handleClearCache = async () => {
    setIsClearingCache(true);
    try {
      const res = await api.clearReportCache();
      setKeySavedToast(`Cleared ${res.cleared_count} cached report narratives. Next generation will author live.`);
      setTimeout(() => setKeySavedToast(null), 4000);
      if (previewPreset) {
        handlePreviewReport(previewPreset, true);
      }
    } catch (e) {
      console.error('Failed to clear report cache:', e);
    } finally {
      setIsClearingCache(false);
    }
  };

  // Pipeline Execution Mutation
  const pipelineMutation = useMutation({
    mutationFn: async () => {
      const effectiveKey = (openaiApiKey && openaiApiKey !== 'backend-configured') ? openaiApiKey.trim() : undefined;
      return await api.runPipelineUpdate({
        openai_api_key: effectiveKey,
        model_name: selectedModel,
      });
    },
    onSuccess: (data) => {
      setPipelineResult(data);
    },
  });

  const handleRegenerateAllReports = () => {
    if (!openaiApiKey.trim()) {
      setTempApiKey('');
      setShowApiKeyModal(true);
      return;
    }
    setShowPipelineModal(true);
    pipelineMutation.mutate();
  };

  // Direct PDF Download Handler
  const handleDownloadReportPdf = async (report: any) => {
    setDownloadingId(report.id);
    try {
      const effectiveKey = (openaiApiKey && openaiApiKey.trim() !== 'backend-configured') ? openaiApiKey.trim() : undefined;
      const req: ReportGenerateRequest = {
        preset_id: report.id,
        openai_api_key: effectiveKey,
        model_name: selectedModel,
        force_refresh: true,
      };
      const blob = await api.exportExecutiveReportPdf(req);
      const timestamp = new Date().toISOString().slice(0, 10);
      saveAs(blob, `clean-energy-publication-${report.id}-${timestamp}.pdf`);
    } catch (e) {
      console.error('Failed to export PDF:', e);
    } finally {
      setDownloadingId(null);
    }
  };

  // Preview Report Handler (with optional forceRefresh to bypass cache and author live)
  const handlePreviewReport = async (report: any, forceRefresh: boolean = false, overrideKey?: string) => {
    const rawKey = overrideKey !== undefined ? overrideKey : openaiApiKey.trim();
    const effectiveKey = (rawKey && rawKey !== 'backend-configured') ? rawKey : undefined;

    if (forceRefresh && !rawKey) {
      setTempApiKey('');
      setShowApiKeyModal(true);
      return;
    }

    setPreviewPreset(report);
    setIsPreviewLoading(true);
    try {
      const req: ReportGenerateRequest = {
        preset_id: report.id,
        openai_api_key: effectiveKey,
        model_name: selectedModel,
        force_refresh: forceRefresh,
      };
      const res = await api.generateExecutiveReport(req);
      setPreviewData(res);
    } catch (e) {
      console.error('Failed to load report preview:', e);
    } finally {
      setIsPreviewLoading(false);
    }
  };

  // Count reports in each category
  const getCategoryCount = (cat: string) => {
    if (cat === 'All Categories') return reportsList.length;
    const targetNorm = normalizeCategory(cat);
    return reportsList.filter((r) => normalizeCategory(r.category) === targetNorm).length;
  };

  // Filtered reports list
  const filteredReports = reportsList.filter((r) => {
    const reportNorm = normalizeCategory(r.category);
    const selectedNorm = normalizeCategory(selectedCategory);
    const matchesCategory = selectedCategory === 'All Categories' || reportNorm === selectedNorm;
    const matchesSearch =
      searchQuery.trim() === '' ||
      r.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.subtitle?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.target_audience?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.category?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.badge?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.key_focus?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getReportIcon = (iconName: string) => {
    switch (iconName) {
      case 'Database': return <Database size={20} className="text-indigo-600" />;
      case 'Globe': return <Globe size={20} className="text-indigo-600" />;
      case 'Scale': return <Scale size={20} className="text-indigo-600" />;
      case 'Flame': return <Flame size={20} className="text-amber-500" />;
      case 'Sun': return <Sun size={20} className="text-amber-500" />;
      case 'BatteryCharging': return <BatteryCharging size={20} className="text-emerald-500" />;
      case 'Home': return <Home size={20} className="text-indigo-500" />;
      case 'Cpu': return <Cpu size={20} className="text-purple-500" />;
      case 'Share2': return <Share2 size={20} className="text-blue-500" />;
      case 'MapPin': return <MapPin size={20} className="text-emerald-500" />;
      case 'Layers': return <Layers size={20} className="text-amber-600" />;
      case 'Activity': return <Activity size={20} className="text-blue-600" />;
      case 'Zap': return <Zap size={20} className="text-amber-500" />;
      case 'TrendingUp': return <TrendingUp size={20} className="text-purple-600" />;
      case 'Building': return <Building size={20} className="text-indigo-600" />;
      case 'Compass': return <Compass size={20} className="text-sky-600" />;
      case 'Target': return <Target size={20} className="text-rose-600" />;
      case 'Users': return <Users size={20} className="text-teal-600" />;
      case 'ShieldCheck': return <ShieldCheck size={20} className="text-emerald-600" />;
      default: return <FileText size={20} className="text-indigo-600" />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Toast Notification */}
      {keySavedToast && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium flex items-center justify-between shadow-xs animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="flex items-center gap-2">
            <CheckCheck size={16} className="text-emerald-600 shrink-0" />
            <span>{keySavedToast}</span>
          </div>
          <button
            onClick={() => setKeySavedToast(null)}
            className="p-1 text-emerald-600 hover:text-emerald-800 rounded-lg cursor-pointer"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Hero Banner */}
      <div className="p-6 sm:p-8 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white shadow-xl border border-slate-800 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="max-w-3xl">
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="px-3 py-1 rounded-full text-[11px] font-bold tracking-wider uppercase bg-indigo-500/20 text-indigo-200 border border-indigo-500/30">
                {reportsList.length} Strategic Monographs
              </span>
              <span className="px-3 py-1 rounded-full text-[11px] font-bold tracking-wider uppercase bg-slate-700/50 text-slate-300 border border-slate-600">
                Executive Publication Series
              </span>
              {openaiApiKey ? (
                <span className="px-3 py-1 rounded-full text-[11px] font-bold tracking-wider uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5">
                  <Sparkles size={12} className="text-emerald-300 animate-pulse" />
                  <span>OpenAI Live AI Active ({selectedModel})</span>
                </span>
              ) : (
                <span className="px-3 py-1 rounded-full text-[11px] font-bold tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1.5">
                  <Info size={12} className="text-amber-300" />
                  <span>Deterministic Fallback Active</span>
                </span>
              )}
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              Executive Report Library
            </h1>
            <p className="text-sm text-slate-300 mt-2 max-w-3xl leading-relaxed">
              Download publication-grade strategic monographs synthesizing <strong>54,305 verified energy innovation awards</strong>, 
              <strong> 13,706 nationwide recipient institutions</strong>, deep domain analyses across all energy vectors and industrial technologies, and forward-looking horizon roadmaps (2026–2035).
            </p>
          </div>

          {/* Action / Configuration Controls */}
          <div className="flex flex-col sm:flex-row lg:flex-col xl:flex-row items-stretch sm:items-center gap-3 shrink-0">
            {/* Configure OpenAI API Key Button */}
            <button
              onClick={() => {
                setTempApiKey(openaiApiKey === 'backend-configured' ? '' : openaiApiKey);
                setShowApiKeyModal(true);
              }}
              className={`px-4 py-3 rounded-xl text-xs font-bold transition-all flex items-center gap-3 cursor-pointer shadow-md hover:scale-[1.02] active:scale-[0.98] ${
                openaiApiKey
                  ? 'bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-white border border-emerald-400/40'
                  : 'bg-gradient-to-r from-indigo-600 to-violet-700 hover:from-indigo-500 hover:to-violet-600 text-white border border-indigo-400/40 ring-2 ring-indigo-400/20'
              }`}
              title="Add or edit your OpenAI API Key for customized AI report synthesis"
            >
              <div className={`p-2 rounded-lg ${openaiApiKey ? 'bg-emerald-500/30 text-emerald-200' : 'bg-white/20 text-white'}`}>
                <Key size={16} />
              </div>
              <div className="text-left">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-extrabold tracking-tight">
                    {openaiApiKey ? 'OpenAI API Connected' : 'Add OpenAI API Key'}
                  </span>
                  <span className={`w-2 h-2 rounded-full ${openaiApiKey ? 'bg-emerald-300 animate-ping' : 'bg-amber-400'}`} />
                </div>
                <span className="text-[10px] text-white/80 font-normal block mt-0.5">
                  {openaiApiKey ? `Synthesizing with ${selectedModel}` : 'Click to add key & unlock live LLM'}
                </span>
              </div>
            </button>

            {/* Clear Cache Button */}
            <button
              onClick={handleClearCache}
              disabled={isClearingCache}
              className="px-3.5 py-3 rounded-xl text-xs font-bold bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
              title="Clear all cached report narratives to force live re-synthesis"
            >
              <RefreshCw size={14} className={isClearingCache ? 'animate-spin text-cyan-400' : 'text-slate-400'} />
              <span>{isClearingCache ? 'Clearing...' : 'Clear Cache'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="space-y-4 mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          {/* Category Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
            {CATEGORIES.map((cat) => {
              const isSelected = selectedCategory === cat;
              const count = getCategoryCount(cat);
              return (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all cursor-pointer flex items-center gap-2 ${
                    isSelected
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
                  }`}
                >
                  <span>{cat}</span>
                  <span
                    className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold ${
                      isSelected
                        ? 'bg-white/20 text-white'
                        : 'bg-slate-100 text-slate-500'
                    }`}
                  >
                    {count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Search Input */}
          <div className="relative w-full sm:w-72 shrink-0">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search reports by topic, title..."
              className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-indigo-500 outline-none text-slate-800"
            />
          </div>
        </div>
      </div>

      {/* Reports Catalog Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredReports.map((report) => {
          const isDownloading = downloadingId === report.id;
          return (
            <div
              key={report.id}
              className="bg-white rounded-2xl border border-slate-200 shadow-xs hover:shadow-md transition-all p-6 flex flex-col justify-between space-y-4 relative group"
            >
              <div>
                {/* Top Badge & Category */}
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-100 flex items-center gap-1.5">
                    {getReportIcon(report.icon)}
                    <span>{report.badge}</span>
                  </span>
                  <span className="text-[11px] font-semibold text-slate-400 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                    Vector Publication · 300 DPI
                  </span>
                </div>

                {/* Title and Subtitle */}
                <h3 className="text-base font-bold text-slate-900 font-serif leading-snug group-hover:text-indigo-600 transition-colors">
                  {report.title}
                </h3>
                <p className="text-xs text-slate-500 mt-2 leading-relaxed line-clamp-2 font-sans">
                  {report.subtitle}
                </p>

                {/* Quantitative Metric Pill */}
                {report.capital_tracked && (
                  <div className="mt-3.5 p-2.5 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-between text-xs">
                    <div>
                      <span className="text-[10px] uppercase font-bold text-slate-400 block">Volume Tracked</span>
                      <span className="font-extrabold text-indigo-700 font-serif">{report.capital_tracked}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] uppercase font-bold text-slate-400 block">Entities</span>
                      <span className="font-bold text-slate-800">{report.awards_count}</span>
                    </div>
                  </div>
                )}

                {/* Target Audience & Target Funders */}
                <div className="mt-3 space-y-1.5">
                  <div className="text-[11px] text-slate-400 flex items-center gap-1">
                    <span className="font-semibold text-slate-600">Target:</span>
                    <span className="truncate">{report.target_audience}</span>
                  </div>
                  <div className="flex items-center gap-1.5 flex-wrap pt-0.5">
                    {['NYSERDA', 'DOE', 'CEC', 'MassCEC', 'EPA', 'ARPA-E', 'NSF', 'NASA', 'USDA', 'DOD'].filter(
                      (a) => (report.target_audience && report.target_audience.includes(a)) || report.title.includes(a) || (report.subtitle && report.subtitle.includes(a))
                    ).slice(0, 4).map((a) => (
                      <div key={a} className="flex items-center gap-1 bg-slate-50 border border-slate-200/60 rounded px-1.5 py-0.5" title={`Target Agency: ${a}`}>
                        <OrgLogo org={a} size="xs" />
                        <span className="text-[9.5px] font-bold text-slate-600">{a}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 border-t border-slate-100 flex items-center gap-2">
                <button
                  onClick={() => handlePreviewReport(report)}
                  className="flex-1 py-2 px-3 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
                  title="View Executive Summary & Key Insights Preview"
                >
                  <Eye size={14} className="text-slate-600" />
                  <span>Preview</span>
                </button>

                <button
                  onClick={() => handleDownloadReportPdf(report)}
                  disabled={isDownloading}
                  className="flex-1 py-2 px-3 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-sm hover:shadow-md transition-all flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50"
                  title="Download Publication PDF"
                >
                  {isDownloading ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Download size={14} />
                  )}
                  <span>Download PDF</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {filteredReports.length === 0 && (
        <div className="text-center py-16 text-slate-400 bg-white rounded-2xl border border-slate-200">
          <FileText size={36} className="mx-auto mb-2 text-slate-300" />
          <p className="text-sm font-semibold text-slate-700">No reports matched your search criteria.</p>
          <p className="text-xs text-slate-400 mt-1">Try searching for a different keyword or selecting "All Categories".</p>
        </div>
      )}

      {/* Slide-over Preview Modal */}
      {previewPreset && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-3xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 border border-indigo-200">
                  {previewPreset.badge}
                </span>
                <span className="text-xs text-slate-500">Executive Strategic Monograph</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setTempApiKey(openaiApiKey === 'backend-configured' ? '' : openaiApiKey);
                    setShowApiKeyModal(true);
                  }}
                  className="px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-700 bg-white hover:bg-slate-100 border border-slate-200 shadow-xs transition-all flex items-center gap-1.5 cursor-pointer"
                  title="Configure OpenAI API Key or Model"
                >
                  <Key size={13} className="text-slate-500" />
                  <span>{openaiApiKey ? 'Key Configured' : 'Add OpenAI Key'}</span>
                </button>
                <button
                  onClick={() => handlePreviewReport(previewPreset, true)}
                  disabled={isPreviewLoading}
                  className="px-3 py-1.5 rounded-xl text-xs font-bold text-indigo-700 bg-white hover:bg-indigo-50 border border-indigo-200 shadow-xs transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  title="Re-author this report live using OpenAI"
                >
                  <RotateCw size={13} className={isPreviewLoading ? 'animate-spin text-indigo-600' : 'text-indigo-600'} />
                  <span>{isPreviewLoading ? 'Synthesizing...' : 'Regenerate'}</span>
                </button>
                <button
                  onClick={() => {
                    setPreviewPreset(null);
                    setPreviewData(null);
                  }}
                  className="p-1 text-slate-400 hover:text-slate-600 rounded-lg cursor-pointer"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Modal Scrollable Body */}
            <div className="p-6 overflow-y-auto space-y-6">
              <div>
                <span className="text-[11px] font-bold text-amber-700 uppercase tracking-widest block mb-1">
                  STRATEGIC PUBLICATION PREVIEW
                </span>
                <h2 className="text-xl font-extrabold font-serif text-slate-900 leading-snug">
                  {previewPreset.title}
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  {previewPreset.subtitle}
                </p>
              </div>

              {/* Status Banner with Quick Key / Model Configuration */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-50 border border-slate-200">
                <div className="flex items-center gap-2.5 text-xs text-slate-700">
                  <div className={`p-2 rounded-lg ${openaiApiKey ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                    <Sparkles size={16} />
                  </div>
                  <div>
                    <div className="flex items-center gap-1.5 font-bold">
                      {openaiApiKey ? (
                        <span className="text-emerald-900">Authoring Engine: Live OpenAI ({selectedModel})</span>
                      ) : (
                        <span className="text-slate-900">Authoring Engine: Deterministic Strategy Engine</span>
                      )}
                    </div>
                    <span className="text-[11px] text-slate-500 font-normal block mt-0.5">
                      {openaiApiKey 
                        ? 'Synthesizes tailored McKinsey-standard executive briefs using verified database context.'
                        : 'Using pre-computed template. Connect an OpenAI API key to author dynamic narratives.'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => {
                      setTempApiKey(openaiApiKey === 'backend-configured' ? '' : openaiApiKey);
                      setShowApiKeyModal(true);
                    }}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 bg-white hover:bg-slate-100 border border-slate-200 shadow-xs transition-all flex items-center gap-1.5 cursor-pointer"
                  >
                    <Key size={13} className="text-slate-500" />
                    <span>{openaiApiKey ? 'Settings' : 'Connect Key'}</span>
                  </button>

                  <button
                    onClick={() => handlePreviewReport(previewPreset, true)}
                    disabled={isPreviewLoading}
                    className={`px-3.5 py-1.5 rounded-lg text-xs font-bold text-white transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50 shadow-xs ${
                      openaiApiKey ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-gradient-to-r from-amber-600 to-indigo-600 hover:from-amber-500 hover:to-indigo-500'
                    }`}
                  >
                    <RotateCw size={12} className={isPreviewLoading ? 'animate-spin' : ''} />
                    <span>{isPreviewLoading ? 'Synthesizing...' : 'Regenerate Narrative'}</span>
                  </button>
                </div>
              </div>

              {isPreviewLoading ? (
                <div className="py-16 flex flex-col items-center justify-center gap-3 text-slate-400">
                  <Loader2 size={36} className="animate-spin text-indigo-600" />
                  <span className="text-xs font-semibold text-slate-700">
                    {openaiApiKey ? `Authoring live McKinsey synthesis with OpenAI (${selectedModel})...` : 'Generating publication preview...'}
                  </span>
                </div>
              ) : previewData?.narrative ? (
                <div className="space-y-5">
                  {/* Core Takeaway Box */}
                  {previewData.narrative.executive_takeaway && (
                    <div className="p-4 rounded-xl bg-amber-50 border border-amber-200">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-amber-800 block mb-1">
                        Core Strategic Thesis // Executive Insight
                      </span>
                      <p className="text-xs font-serif italic text-slate-900 leading-relaxed">
                        "{previewData.narrative.executive_takeaway}"
                      </p>
                    </div>
                  )}

                  {/* Executive Summary (House Voice) */}
                  {previewData.narrative.executive_summary && (
                    <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2.5">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-slate-900 font-serif uppercase tracking-wider flex items-center gap-1.5">
                          <Sparkles size={14} className="text-indigo-600" />
                          <span>Executive Summary // Strategic Synthesis &amp; Market Dynamics</span>
                        </h4>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                          Executive Synthesis
                        </span>
                      </div>
                      <div 
                        className="text-xs text-slate-700 leading-relaxed space-y-2 font-sans whitespace-pre-line"
                        dangerouslySetInnerHTML={{ __html: previewData.narrative.executive_summary }}
                      />
                    </div>
                  )}

                  {/* Macro Context if available */}
                  {previewData.narrative.macro_context && (
                    <div className="p-4 rounded-xl bg-indigo-50/40 border border-indigo-100 space-y-2">
                      <h4 className="text-xs font-bold text-slate-900 font-serif uppercase tracking-wider">
                        Macroeconomic Architecture &amp; Statutory Framework
                      </h4>
                      <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-line">
                        {previewData.narrative.macro_context}
                      </p>
                    </div>
                  )}

                  {/* Key Findings */}
                  {previewData.narrative.key_findings && previewData.narrative.key_findings.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-slate-900 font-serif uppercase tracking-wider">
                        Core Strategic Insights &amp; Market Dynamics
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {previewData.narrative.key_findings.map((f: any, idx: number) => (
                          <div key={idx} className="p-3.5 rounded-xl bg-white border border-slate-200 text-xs space-y-2 shadow-xs">
                            <div className="flex items-start justify-between gap-2">
                              <h5 className="font-bold text-slate-900 font-serif text-xs leading-snug">{idx + 1}. {f.title}</h5>
                              <span className="inline-block text-[10px] font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100 shrink-0">
                                {f.metric_highlight}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-600 leading-relaxed">{f.narrative}</p>
                            {f.strategic_implication && (
                              <div className="pt-2 border-t border-slate-100 text-[10px] text-indigo-900 bg-indigo-50/50 p-1.5 rounded">
                                <span className="font-bold">Key Takeaway: </span>{f.strategic_implication}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 10-Year Horizon Outlook */}
                  {previewData.narrative.future_outlook?.inflection_points && (
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-slate-900 font-serif uppercase tracking-wider flex items-center gap-1.5">
                        <Compass size={14} className="text-indigo-600" />
                        <span>Strategic Future Outlook &amp; Horizon Roadmap (2026–2035)</span>
                      </h4>
                      <div className="space-y-2">
                        {previewData.narrative.future_outlook.inflection_points.map((item: any, idx: number) => (
                          <div key={idx} className="p-3 rounded-lg bg-indigo-50/50 border border-indigo-100 text-xs">
                            <div className="flex items-center justify-between gap-2 mb-1">
                              <span className="font-bold text-slate-900">{item.title}</span>
                              <span className="text-[10px] font-bold text-indigo-700 uppercase">{item.horizon}</span>
                            </div>
                            <p className="text-[11px] text-slate-600 leading-relaxed">{item.outlook}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Strategic Conclusion & Implementation Framework */}
                  {previewData.narrative.conclusion && (
                    <div className="p-5 rounded-xl bg-gradient-to-br from-slate-900 to-indigo-950 text-white border border-indigo-800/50 space-y-3 shadow-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] uppercase font-bold tracking-widest text-cyan-400">
                          IMPLEMENTATION &amp; RISK GOVERNANCE ROADMAP
                        </span>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-300 bg-emerald-500/20 px-2.5 py-0.5 rounded border border-emerald-500/30">
                          2026–2035 Horizon
                        </span>
                      </div>
                      <h4 className="text-sm font-bold text-white font-serif">
                        Strategic Conclusion // 2026–2035 Horizon Trajectory &amp; Execution Framework
                      </h4>
                      <div 
                        className="text-xs text-slate-300 leading-relaxed space-y-2.5 font-sans whitespace-pre-line"
                        dangerouslySetInnerHTML={{ __html: previewData.narrative.conclusion }}
                      />
                    </div>
                  )}

                  {/* Strategic Recommendations Matrix */}
                  {previewData.narrative.strategic_recommendations && previewData.narrative.strategic_recommendations.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-slate-900 font-serif uppercase tracking-wider">
                        Stakeholder Strategic Action Directives
                      </h4>
                      <div className="space-y-2">
                        {previewData.narrative.strategic_recommendations.map((rec: any, idx: number) => (
                          <div key={idx} className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                            <span className="font-bold text-indigo-900 shrink-0 sm:w-1/3">{rec.target}</span>
                            <span className="text-slate-600 sm:w-2/3 text-[11px]">{rec.action}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-xs text-slate-500">Preview details currently unavailable.</div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">
                Source: <strong>U.S. Energy Innovation Database by Brandon N. Owens</strong>
              </span>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={() => {
                    setPreviewPreset(null);
                    setPreviewData(null);
                  }}
                  className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-100 transition-colors cursor-pointer"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    setTempApiKey(openaiApiKey === 'backend-configured' ? '' : openaiApiKey);
                    setShowApiKeyModal(true);
                  }}
                  className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-100 border border-slate-200 rounded-xl shadow-xs transition-all flex items-center gap-1.5 cursor-pointer"
                  title="Configure OpenAI API Key"
                >
                  <Key size={13} className="text-slate-500" />
                  <span>{openaiApiKey ? 'Key Configured' : 'Add API Key'}</span>
                </button>
                <button
                  onClick={() => handlePreviewReport(previewPreset, true)}
                  disabled={isPreviewLoading}
                  className="px-4 py-2 text-xs font-bold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 rounded-xl shadow-xs transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  title="Re-run OpenAI synthesis to author fresh narrative"
                >
                  <RotateCw size={13} className={isPreviewLoading ? 'animate-spin text-indigo-600' : 'text-indigo-600'} />
                  <span>Regenerate Narrative</span>
                </button>
                <button
                  onClick={() => handleDownloadReportPdf(previewPreset)}
                  disabled={downloadingId === previewPreset.id}
                  className="px-5 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-md transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  {downloadingId === previewPreset.id ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Download size={14} />
                  )}
                  <span>Download Executive Publication (PDF)</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Automated Pipeline Modal */}
      {showPipelineModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-md">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-2xl w-full p-6 space-y-5 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-amber-100 text-amber-800 font-bold">
                  <Play size={16} className="fill-amber-600 text-amber-600" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    Automated Ingestion &amp; Pre-Compilation Pipeline
                  </h3>
                  <p className="text-[11px] text-slate-500">
                    Refreshes nationwide database geocoding, updates taxonomies, and pre-compiles all executive PDF monographs.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowPipelineModal(false)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            {pipelineMutation.isPending ? (
              <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-500">
                <Loader2 size={36} className="animate-spin text-indigo-600" />
                <span className="text-xs font-bold text-slate-800">
                  Executing Pipeline Routine in Background...
                </span>
                <span className="text-[11px] text-slate-400 max-w-md text-center">
                  Geocoding 54K awards, refreshing recipient taxonomies, and compiling publication monographs.
                </span>
              </div>
            ) : pipelineResult ? (
              <div className="space-y-4">
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-2 text-xs text-emerald-800 font-medium">
                  <CheckCheck size={16} className="text-emerald-600 shrink-0" />
                  <span>Pipeline finished in {pipelineResult.total_duration_sec}s! All executive monographs compiled.</span>
                </div>

                <div className="max-h-60 overflow-y-auto space-y-2 divide-y divide-slate-100 text-xs">
                  {pipelineResult.generated_reports?.map((r: any, idx: number) => (
                    <div key={idx} className="pt-2 flex items-center justify-between text-xs">
                      <div>
                        <span className="font-bold text-slate-800 block">{r.title}</span>
                        <span className="text-[10px] text-slate-400">{r.pdf_filename} · {(r.size_bytes / 1024).toFixed(0)} KB</span>
                      </div>
                      <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono text-[10px]">
                        {r.duration_sec}s
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-xs text-slate-500">
                Click below to start the automated update routine.
              </div>
            )}

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                onClick={() => setShowPipelineModal(false)}
                className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors cursor-pointer"
              >
                Close
              </button>
              <button
                onClick={() => pipelineMutation.mutate()}
                disabled={pipelineMutation.isPending}
                className="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-md transition-all flex items-center gap-1.5 disabled:opacity-50 cursor-pointer"
              >
                {pipelineMutation.isPending ? <Loader2 size={13} className="animate-spin" /> : <Play size={13} className="fill-white" />}
                <span>Run Pipeline Now</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* OpenAI API Key & Model Configuration Modal */}
      {showApiKeyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-md animate-in fade-in duration-150">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 space-y-5 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2.5 rounded-xl bg-indigo-100 text-indigo-800 font-bold">
                  <Key size={18} className="text-indigo-600" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    OpenAI Intelligence Configuration
                  </h3>
                  <p className="text-[11px] text-slate-500">
                    Enable live McKinsey-level AI synthesis for Executive Reports &amp; PDF Monographs.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowApiKeyModal(false)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5 flex items-center justify-between">
                  <span>OpenAI API Key</span>
                  <span className="text-[10px] text-slate-400 font-normal">Stored securely in browser localStorage</span>
                </label>
                <div className="relative">
                  <input
                    type={showKeyVisibility ? "text" : "password"}
                    value={tempApiKey}
                    onChange={(e) => setTempApiKey(e.target.value)}
                    placeholder="sk-proj-..."
                    className="w-full pl-3.5 pr-10 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono focus:ring-2 focus:ring-indigo-500 outline-none text-slate-900"
                  />
                  <button
                    type="button"
                    onClick={() => setShowKeyVisibility(!showKeyVisibility)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
                  >
                    {showKeyVisibility ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
                <p className="text-[10px] text-slate-400 mt-1.5 leading-relaxed">
                  Provide your key to generate custom, non-deterministic AI executive narratives. If empty, the engine uses the verified deterministic house analysis.
                </p>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  LLM Model Selection
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setSelectedModel('gpt-4o-mini')}
                    className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                      selectedModel === 'gpt-4o-mini'
                        ? 'border-indigo-600 bg-indigo-50/50 text-indigo-950 ring-1 ring-indigo-500'
                        : 'border-slate-200 bg-white hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="block text-xs font-bold font-mono">gpt-4o-mini</span>
                      <span className="text-[9px] font-bold text-indigo-700 bg-indigo-100 px-1.5 py-0.2 rounded">Default</span>
                    </div>
                    <span className="block text-[10px] text-slate-500 mt-0.5">Fast, high-throughput &amp; cost-efficient</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSelectedModel('gpt-4o')}
                    className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                      selectedModel === 'gpt-4o'
                        ? 'border-indigo-600 bg-indigo-50/50 text-indigo-950 ring-1 ring-indigo-500'
                        : 'border-slate-200 bg-white hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="block text-xs font-bold font-mono">gpt-4o</span>
                      <span className="text-[9px] font-bold text-emerald-700 bg-emerald-100 px-1.5 py-0.2 rounded">Flagship</span>
                    </div>
                    <span className="block text-[10px] text-slate-500 mt-0.5">Deep analytical reasoning &amp; strategy</span>
                  </button>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => {
                  setTempApiKey('');
                  setOpenaiApiKey('');
                  localStorage.removeItem('energysignal_openai_api_key');
                  localStorage.removeItem('openai_api_key');
                  localStorage.removeItem('cleangrants_openai_api_key');
                  fetch('/api/chat/set-api-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: '' }),
                  }).catch(() => {});
                  setShowApiKeyModal(false);
                  setKeySavedToast('OpenAI API key cleared.');
                  setTimeout(() => setKeySavedToast(null), 3000);
                }}
                className="px-3 py-1.5 text-xs text-rose-600 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer"
              >
                Clear Key
              </button>

              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={() => setShowApiKeyModal(false)}
                  className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => handleSaveApiKey(false)}
                  className="px-4 py-2 text-xs font-bold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl shadow-xs transition-all cursor-pointer"
                >
                  Save Key
                </button>
                <button
                  type="button"
                  onClick={() => handleSaveApiKey(true)}
                  className="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-md transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <RotateCw size={13} className="text-cyan-300" />
                  <span>Save &amp; Regenerate</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
