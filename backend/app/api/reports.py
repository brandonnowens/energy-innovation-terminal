"""Reports API endpoints & Executive AI Dossier Generator."""

import io
import os
import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.community import Report
from app.api.community import require_creator_hash, get_creator_hash
from app.engine.report_aggregator import ReportContextAggregator
from app.engine.ai_report_author import author_report_with_openai
from app.engine.pdf_report_builder import build_executive_pdf
from app.engine.specialized_generators.dispatcher import GENERATORS_MAP, generate_specialized_monograph

router = APIRouter()

class ReportGenerateRequest(BaseModel):
    preset_id: str = "state_of_innovation"
    filters: Optional[Dict[str, Any]] = None
    custom_prompt: Optional[str] = None
    openai_api_key: Optional[str] = None
    model_name: Optional[str] = "gpt-4o-mini"
    title: Optional[str] = None
    force_refresh: Optional[bool] = False

class ReportCreate(BaseModel):
    title: str
    prompt: Optional[str] = None
    filters_json: Optional[str] = None

REPORT_PRESETS = [
    # 0. Core Technical Architecture & Database Reference (Hidden for now)
    # {
    #     "id": "cleangrid_database_docs",
    #     "title": "CleanGrid IQ Database",
    #     "subtitle": "Comprehensive Technical Data Architecture, Source Provenance, Vintage Specifications, Relational Graph Topology, and Stakeholder Decision Utility Reference Manual",
    #     "category": "Macro & Policy Strategy",
    #     "target_audience": "State Energy Directors, Federal Program Managers, Clean Tech Project Sponsors, Climate Tech VCs, Regulated Utilities, University Research VPs, and Community Consortia",
    #     "badge": "Database Architecture & Reference",
    #     "icon": "Database",
    #     "pages": 24,
    #     "capital_tracked": "$98.98B Tracked",
    #     "awards_count": "54,305 Awards (35-Yr Arc)",
    #     "key_focus": "Exhaustive technical documentation of all 10 data layers, 31+ public source connectors, 35-year longitudinal vintage (1991–2026), 3-tier credibility framework, relational knowledge graph topology, and 7-persona stakeholder decision-maker utility matrix."
    # },

    # 1. Macro & Policy Strategy (Flagship Strategic Briefings & Institutional Blueprints)
    {

        "id": "state_partnership_ecosystem",
        "title": "State Innovation Program Partnership & Ecosystem Expansion Lessons Learned and Future Strategies",
        "subtitle": "The Definitive Retrospective and Forward Blueprint: Analyzing 25 Years of State-Level Clean Energy Consortia, Multi-Jurisdictional Coalitions, Hardtech Incubators, Regulated Utility Alignment, and Frontline Equity Co-Design (2000-2026 Empirical Arc and 2026-2035 Strategic Roadmap)",
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

    # 2. Commercialization & Capital Markets (Actionable Diagnostics & Strategies)
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

    # 3. Project Strategy & Consortia (4 Actionable Playbooks)
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

    # 4. Technology Domain Strategic Deep-Dives (10 Vertical Market Dossiers)
    {
        "id": "alt_fuels_dossier",
        "title": "Alternative Fuels, Clean Molecules & Synthetic Carriers Strategic Dossier",
        "subtitle": "Comprehensive vertical intelligence across Clean Hydrogen, Green Ammonia, E-Methanol, SAF, RNG, Biochar & Pyrolysis, and IRA 45V/45Z/40B compliance.",
        "category": "Technology Domains",
        "target_audience": "Chief Technology Officers, Maritime Fleet Operators, Sustainable Aviation Developers, Chemical Industry VPs",
        "badge": "Clean Fuels & Molecules",
        "icon": "Flame",
        "pages": 21,
        "capital_tracked": "$17.06B",
        "awards_count": "1,944 Orgs",
        "key_focus": "Electrolyzer Capex curves, IRA 45V 3-pillars guidance, SAF blending mandates, green ammonia/e-methanol synthetic molecules, fast pyrolysis biochar, point-source CCUS, and verified patent holdings."
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
]

@router.get("/reports/presets")
def get_report_presets():
    """Return list of all 15 Executive Report Presets in the Library."""
    return {"presets": REPORT_PRESETS}

@router.post("/reports/generate")
def generate_executive_report(req: ReportGenerateRequest, db: Session = Depends(get_db)):
    """
    Executes context aggregation from the database and runs OpenAI LLM authorship.
    Returns structured JSON with data context and authored executive narrative.
    """
    aggregator = ReportContextAggregator(db)
    context_data = aggregator.aggregate_by_preset(req.preset_id, req.filters)
    
    if req.title:
        context_data["report_title"] = req.title

    narrative = author_report_with_openai(
        preset_id=req.preset_id,
        context=context_data,
        custom_prompt=req.custom_prompt,
        api_key=req.openai_api_key,
        model_name=req.model_name or "gpt-4o-mini",
        force_refresh=bool(req.force_refresh)
    )

    # Persist report into PostgreSQL knowledge base
    try:
        from app.models.result import ResultArtifact
        prompt_key = f"preset:{req.preset_id}"
        report_row = db.query(Report).filter(Report.prompt == prompt_key).first()
        report_title = req.title or context_data.get("report_title") or narrative.get("title") or "Executive Strategic Report"
        report_summary = narrative.get("executive_takeaway") or narrative.get("subtitle") or "Executive strategic briefing"

        if not report_row:
            report_row = Report(
                creator_hash="system_editorial_board",
                title=report_title,
                summary=report_summary,
                prompt=prompt_key,
                plan_json={"preset_id": req.preset_id, "filters": req.filters},
                results_json=context_data,
                report_json=narrative,
                status="complete",
                is_public=True,
                visibility_confirmed=True,
                version=1,
                tags_json=[req.preset_id, "Executive Strategic Publication"],
                methodology="Empirical transaction aggregation across Energy Innovation Terminal platform and strategic synthesis."
            )
            db.add(report_row)
        else:
            report_row.title = report_title
            report_row.summary = report_summary
            report_row.results_json = context_data
            report_row.report_json = narrative
            report_row.status = "complete"
            report_row.is_public = True
            report_row.updated_at = datetime.datetime.utcnow()

        db.flush()

        # Also register or update ResultArtifact in knowledge base
        art = db.query(ResultArtifact).filter(ResultArtifact.title == report_title).first()
        if not art:
            art = ResultArtifact(
                title=report_title,
                artifact_type="evaluation_report",
                agency="Energy Innovation Terminal",
                source_url=f"/api/reports/{report_row.id}",
                publication_date=datetime.date.today().strftime("%Y-%m-%d"),
                page_count=21,
                summary=report_summary,
                key_findings_json=[f["title"] for f in narrative.get("key_findings", [])] if isinstance(narrative.get("key_findings"), list) else [],
                data_provenance="agency_verified"
            )
            db.add(art)

        db.commit()
    except Exception as e:
        db.rollback()

    return {
        "preset_id": req.preset_id,
        "context_data": context_data,
        "narrative": narrative,
        "generated_at": datetime.datetime.utcnow().isoformat()
    }

@router.post("/reports/clear-cache")
def clear_report_cache():
    """
    Clears all cached AI report narrative files to force live re-generation.
    """
    from app.engine.ai_report_author import clear_all_report_caches
    cleared_count = clear_all_report_caches()
    return {"status": "success", "cleared_count": cleared_count}

@router.get("/reports/clear-cache", include_in_schema=False)
def clear_report_cache_get():
    return clear_report_cache()

@router.post("/reports/export-pdf")
def export_executive_report_pdf(req: ReportGenerateRequest, db: Session = Depends(get_db)):
    """
    Generates and streams high-resolution multi-page PDF executive monograph.
    Always forces cache refresh and live AI synthesis when users download.
    """
    pdf_buffer = io.BytesIO()

    if req.preset_id in GENERATORS_MAP:
        generate_specialized_monograph(
            preset_id=req.preset_id,
            db=db,
            output_stream=pdf_buffer,
            openai_api_key=req.openai_api_key,
            model_name=req.model_name,
            custom_prompt=req.custom_prompt,
            force_refresh=True
        )
    else:
        aggregator = ReportContextAggregator(db)
        context_data = aggregator.aggregate_by_preset(req.preset_id, req.filters)
        
        if req.title:
            context_data["report_title"] = req.title

        narrative = author_report_with_openai(
            preset_id=req.preset_id,
            context=context_data,
            custom_prompt=req.custom_prompt,
            api_key=req.openai_api_key,
            model_name=req.model_name or "gpt-4o-mini",
            force_refresh=True
        )
        build_executive_pdf(context_data, narrative, pdf_buffer)

    pdf_buffer.seek(0)
    filename_slug = req.preset_id.replace("_", "-")
    timestamp_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"clean-energy-publication-{filename_slug}-{timestamp_str}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

class PipelineRunRequest(BaseModel):
    openai_api_key: Optional[str] = None
    model_name: Optional[str] = "gpt-4o-mini"

@router.post("/reports/run-pipeline")
def trigger_pipeline_update(req: Optional[PipelineRunRequest] = None):
    """
    Triggers the automated data refresh, nationwide geocoding, and 8 executive report updates.
    """
    from app.ingest.pipeline_runner import run_data_refresh_and_report_pipeline
    key = req.openai_api_key if req else None
    model = (req.model_name if req and req.model_name else "gpt-4o-mini")
    manifest = run_data_refresh_and_report_pipeline(openai_api_key=key, model_name=model)
    return manifest

@router.post("/reports")
def create_report(req: ReportCreate, creator_hash: str = Depends(require_creator_hash), db: Session = Depends(get_db)):
    r = Report(
        creator_hash=creator_hash,
        prompt=req.prompt,
        title=req.title,
        filters_json=req.filters_json,
        status="draft"
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.get("/reports/{report_id}")
def get_report(report_id: int, creator_hash: Optional[str] = Depends(get_creator_hash), db: Session = Depends(get_db)):
    r = db.query(Report).filter_by(id=report_id).first()
    if not r or r.deleted_at:
        raise HTTPException(404, "Report not found")
        
    if r.creator_hash != creator_hash:
        if not r.is_public or r.status != "complete":
            raise HTTPException(403, "Access denied")
            
    return r

@router.get("/reports")
def list_reports(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    from sqlalchemy.orm import defer
    query = db.query(Report).options(
        defer(Report.report_json),
        defer(Report.results_json),
        defer(Report.plan_json),
        defer(Report.filters_json),
        defer(Report.coverage_json),
        defer(Report.prompt)
    ).filter(Report.status == "complete", Report.is_public == True, Report.deleted_at == None)
    
    if search:
        query = query.filter(Report.title.ilike(f"%{search}%"))
        
    total = query.count()
    items = query.order_by(Report.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.delete("/reports/{report_id}")
def delete_report(report_id: int, creator_hash: str = Depends(require_creator_hash), db: Session = Depends(get_db)):
    r = db.query(Report).filter_by(id=report_id).first()
    if not r:
        raise HTTPException(404, "Report not found")
    if r.creator_hash != creator_hash:
        raise HTTPException(403, "Access denied")
        
    r.deleted_at = datetime.datetime.utcnow()
    db.commit()
    return {"status": "deleted"}
