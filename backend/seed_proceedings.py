"""
Authoritative Seed Dataset for Energy Innovation Regulatory Proceedings & PUC Dockets.
Grounds the Energy Innovation Terminal across:
1. Large Load & AI Data Center Interconnection (NY PSC 24-E-0314, FERC AD24-11, PUCT 55999)
2. State Clean Energy & Energy Storage Procurement (NY PSC 18-E-0130, CPUC R.20-05-003)
3. Utility Thermal Energy Networks - TENs (NY PSC 22-M-0149, Mass DPU 20-80)
4. Grid Interconnection Modernization & High-DER (NY SIR 19-E-0735, CPUC Rule 21 R.21-06-017, PJM ER24-99)
5. Federal Transmission Planning & Wholesale VPPs (FERC Orders 2023, 1920, 2222)
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, init_db
from app.models.policy import (
    RegulatoryProceeding,
    ProceedingTechnologyLink,
    ProceedingOrganizationLink,
    ProceedingOpportunityLink
)
from app.models.technology import Technology
from app.models.organization import Organization
from app.models.opportunity import Opportunity

# Master Regulatory Proceedings Registry
SEED_PROCEEDINGS = [
    # =========================================================================
    # 1. LARGE LOAD & AI DATA CENTER INTERCONNECTION
    # =========================================================================
    {
        "id": "ny_psc_24_e_0314_large_load",
        "docket_number": "Case 24-E-0314",
        "commission": "NYPSC",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "title": "Proceeding on Motion of the Commission Regarding Large Load Interconnection and System Reliability",
        "short_title": "NY PSC Large Load & Data Center Proceeding (Case 24-E-0314)",
        "topic_category": "large_load_interconnection",
        "status": "active",
        "open_date": datetime(2024, 5, 16),
        "comment_deadline": datetime(2025, 3, 31),
        "expected_order_date": datetime(2025, 6, 30),
        "executive_summary": "High-profile New York Public Service Commission proceeding examining the unprecedented surge of massive electric load requests (50 MW to 1+ GW per facility) from artificial intelligence data centers, clean hydrogen electrolyzers, semiconductor fabs (Micron in Clay, NY), and industrial electrification across Upstate and Downstate territories.",
        "innovation_impact": "Directly catalyzes market demand for behind-the-meter clean firm generation (SMR nuclear, enhanced geothermal), on-site multi-day long-duration energy storage (iron-air, redox flow), and Grid-Enhancing Technologies (GETs) like Dynamic Line Rating (DLR) to unlock latent transmission capacity without triggering multi-year substation upgrade moratoriums.",
        "commercial_tailwinds": "Establishes expedited interconnection fast-tracks for loads offering automated demand flexibility or pairing with co-located zero-emission generation; creates specialized dynamic rate tariffs that compensate large loads for automated shedding during peak grid stress.",
        "commercial_friction_points": "Developers face risk of transmission upgrade cost-allocation rules, long utility study queues, and potential standby charges for behind-the-meter generation if not designed with true islanding capability.",
        "key_filings_summary": "Joint Utilities of New York (ConEd, National Grid, NYSEG, RG&E, Central Hudson, O&R) proposed standardized Large Load Interconnection Procedures (LLIP) with upfront non-refundable milestone deposits. Clean energy innovators advocate for flexible interconnection agreements and co-located storage credits.",
        "official_docket_url": "https://documents.dps.ny.gov/public/MatterManagement/CaseMaster.aspx?MatterCaseNo=24-E-0314",
        "tech_links": [
            {"tech_id": "iron_air_battery", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "Co-locating multi-day storage with large loads avoids transmission peak demand charges and provides islanded resilience."},
            {"tech_id": "smr_gen4_reactors", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "SMR co-location is a leading candidate for 24/7 carbon-free data center power under PSC review."},
            {"tech_id": "egs_geothermal", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Provides firm baseload zero-carbon power directly adjacent to industrial large loads."},
            {"tech_id": "dynamic_line_rating_gets", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "Utilities evaluated DLR to rapidly increase feeder hosting capacity for Upstate large loads."},
            {"tech_id": "pem_electrolyzer", "impact_level": "critical_gate", "commercial_vector": "tariff_revenue", "impact_summary": "Electrolyzers need flexible rate structures and rapid ramping credit to operate economically under NY PSC tariffs."}
        ],
        "org_names": ["Consolidated Edison", "National Grid", "New York Power Authority", "NYSEG"]
    },
    {
        "id": "ferc_ad24_11_large_load_colocation",
        "docket_number": "Docket AD24-11-000 / RM24-15",
        "commission": "FERC",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "title": "Inquiry Concerning Large Loads Co-Located at Generating Facilities",
        "short_title": "FERC Large Load Co-Location Inquiry (Docket AD24-11)",
        "topic_category": "large_load_interconnection",
        "status": "public_comment",
        "open_date": datetime(2024, 6, 28),
        "comment_deadline": datetime(2025, 4, 15),
        "expected_order_date": datetime(2025, 9, 30),
        "executive_summary": "Federal Energy Regulatory Commission nationwide proceeding and technical conference examining the legal, reliability, and cost-allocation rules for hyperscale AI data centers co-locating directly behind-the-meter at existing and new nuclear, natural gas, and clean energy generating stations (sparked by the Talen Energy Susquehanna nuclear data center dispute).",
        "innovation_impact": "Determines the commercial model for behind-the-meter clean tech deployment across the entire US. A favorable ruling unlocks hundreds of gigawatts of dedicated SMR, advanced geothermal, and clean hydrogen co-location without triggering federal transmission network upgrade fees.",
        "commercial_tailwinds": "Accelerates time-to-power for AI data centers from 5–7 years down to 12–24 months by avoiding the regional transmission interconnection queue.",
        "commercial_friction_points": "Incumbent utilities and consumer advocates argue co-located loads must pay transmission network service charges and ancillary service fees to prevent cost-shifting to retail ratepayers.",
        "key_filings_summary": "Tech hyperscalers (Amazon, Microsoft, Google, Meta) and clean energy developers advocate for clear co-location rights with proportional cost responsibility; PJM, AEP, and Exelon filed protests urging full transmission rate assessments.",
        "official_docket_url": "https://elibrary.ferc.gov/eLibrary/search",
        "tech_links": [
            {"tech_id": "smr_gen4_reactors", "impact_level": "high_catalyst", "commercial_vector": "siting_clarity", "impact_summary": "Directly governs the legal framework for dedicated SMR-to-data-center off-grid power sales."},
            {"tech_id": "egs_geothermal", "impact_level": "high_catalyst", "commercial_vector": "siting_clarity", "impact_summary": "Allows deep geothermal developers to sell direct behind-the-meter power contracts without FERC transmission tariff overhead."},
            {"tech_id": "microgrid_black_start", "impact_level": "critical_gate", "commercial_vector": "interconnection_access", "impact_summary": "Microgrid isolation switches and protection schemes must satisfy FERC safety and reliability criteria."}
        ],
        "org_names": ["US Department of Energy (DOE)"]
    },
    {
        "id": "puct_project_55999_large_flexible_loads",
        "docket_number": "Project No. 55999",
        "commission": "PUCT",
        "jurisdiction_level": "state",
        "jurisdiction_state": "TX",
        "title": "Review of Rules Regarding the Interconnection of Large Flexible Loads in the ERCOT Region",
        "short_title": "PUCT Large Flexible Load Rules (Project 55999)",
        "topic_category": "large_load_interconnection",
        "status": "active",
        "open_date": datetime(2023, 12, 1),
        "expected_order_date": datetime(2025, 5, 30),
        "executive_summary": "Public Utility Commission of Texas proceeding establishing standardized registration, operational telemetry, and mandatory curtailment requirements for large flexible loads (≥75 MW) connecting to the ERCOT grid, specifically addressing AI data centers, clean hydrogen electrolyzers, and industrial facilities.",
        "innovation_impact": "Creates high-value revenue streams for industrial loads equipped with fast-ramping controls and on-site batteries capable of curtailing power within seconds during ERCOT Energy Emergency Alerts (EEA).",
        "commercial_tailwinds": "Enables fast-track interconnection in ERCOT for loads willing to enter into voluntary interruptible service tariffs.",
        "commercial_friction_points": "Mandates real-time telemetry integration with ERCOT dispatch and strict non-compliance financial penalties for failing to curtail during grid emergencies.",
        "key_filings_summary": "ERCOT proposed mandatory 10-second telemetry updates and ride-through performance requirements; clean hydrogen and data center coalitions requested flexible participation tiers.",
        "official_docket_url": "https://interchange.puc.texas.gov/Search/SearchPost",
        "tech_links": [
            {"tech_id": "pem_electrolyzer", "impact_level": "high_catalyst", "commercial_vector": "tariff_revenue", "impact_summary": "Electrolyzers can monetize rapid curtailment as high-value ERCOT Responsive Reserve Service (RRS)."},
            {"tech_id": "derms_vpp_orchestration", "impact_level": "high_catalyst", "commercial_vector": "tariff_revenue", "impact_summary": "Provides automated orchestration software required for multi-site large load compliance."},
            {"tech_id": "iron_air_battery", "impact_level": "market_expansion", "commercial_vector": "interconnection_access", "impact_summary": "Provides backup power when large industrial loads are instructed by ERCOT to curtail."}
        ],
        "org_names": ["Texas State Energy Conservation Office (SECO)"]
    },

    # =========================================================================
    # 2. STATE STORAGE & CLEAN FIRM PROCUREMENT MANDATES
    # =========================================================================
    {
        "id": "ny_psc_18_e_0130_storage",
        "docket_number": "Case 18-E-0130",
        "commission": "NYPSC",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "title": "In the Matter of Energy Storage Deployment Program (6 GW Energy Storage Roadmap)",
        "short_title": "NY PSC 6 GW Storage Roadmap (Case 18-E-0130)",
        "topic_category": "storage_procurement",
        "status": "order_issued",
        "open_date": datetime(2018, 3, 1),
        "expected_order_date": datetime(2024, 7, 18),
        "executive_summary": "New York Public Service Commission landmark order adopting the updated New York Energy Storage Roadmap, establishing competitive procurement mechanisms for 6,000 MW of energy storage by 2030 (including 3,000 MW bulk storage, 1,500 MW retail storage, and 200 MW residential), backed by the Index Storage Credit (ISC) incentive framework.",
        "innovation_impact": "Directly underwrites multi-billion dollar state procurement for both 4-hour lithium systems and 10-100+ hour Long-Duration Energy Storage (LDES); sets dedicated 20% program carve-out for disadvantaged communities (DACs).",
        "commercial_tailwinds": "NYSERDA bulk and retail storage solicitations totaling over $1.5B in public ratepayer incentives; 15-year revenue certainty insulating project developers from wholesale capacity price volatility.",
        "commercial_friction_points": "NYISO interconnection study queue delays; strict New York City FDNY 3 RCNY §401-01 fire safety approvals for urban dense siting.",
        "key_filings_summary": "NYSERDA and DPS staff whitepaper established the Index Storage Credit (ISC) structure; approved by Commission Order in July 2024 with first competitive NYSERDA procurement launched in late 2024.",
        "official_docket_url": "https://documents.dps.ny.gov/public/MatterManagement/CaseMaster.aspx?MatterCaseNo=18-E-0130",
        "tech_links": [
            {"tech_id": "iron_air_battery", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Directly benefits from NY's long-duration storage carve-outs and NYSERDA multi-day pilot solicitations."},
            {"tech_id": "vanadium_redox_flow", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Eligible for 8-hour+ bulk storage ISC awards with zero thermal runaway degradation risk."},
            {"tech_id": "solid_state_lithium_battery", "impact_level": "market_expansion", "commercial_vector": "direct_procurement", "impact_summary": "Next-gen chemistry targeting retail commercial and municipal storage allocations."},
            {"tech_id": "sodium_ion_battery", "impact_level": "market_expansion", "commercial_vector": "direct_procurement", "impact_summary": "Cost-competitive candidate for distribution-connected retail storage programs."}
        ],
        "org_names": ["NYSERDA", "Consolidated Edison", "National Grid", "New York Power Authority"]
    },
    {
        "id": "cpuc_r20_05_003_irp",
        "docket_number": "Rulemaking R.20-05-003",
        "commission": "CPUC",
        "jurisdiction_level": "state",
        "jurisdiction_state": "CA",
        "title": "Order Instituting Rulemaking to Continue Electric Integrated Resource Planning and Related Procurement Processes",
        "short_title": "CPUC Clean Firm & LDES Procurement Mandates (R.20-05-003)",
        "topic_category": "clean_firm_procurement",
        "status": "active",
        "open_date": datetime(2020, 5, 28),
        "expected_order_date": datetime(2025, 8, 30),
        "executive_summary": "California Public Utilities Commission flagship proceeding directing load-serving entities (IOUs, CCAs, POUs) to procure over 11,500 MW of new net qualifying capacity, including mandatory statutory carve-outs for Long-Duration Energy Storage (LDES: 1,000+ MW, 8+ hours duration) and Clean Firm Zero-Emitting Generation (1,000+ MW geothermal, advanced nuclear, offshore wind).",
        "innovation_impact": "The single largest commercial procurement driver in the Western United States for multi-day storage (iron-air, vanadium flow), enhanced geothermal systems (EGS), and floating offshore wind.",
        "commercial_tailwinds": "Creates multi-year binding utility power purchase agreements (PPAs) that enable project finance for first-of-a-kind commercial clean firm plants.",
        "commercial_friction_points": "Tight commercial online date milestones (2026–2028) with steep failure penalties for developers facing CAISO transmission interconnection delays.",
        "key_filings_summary": "CPUC Decision D.21-06-035 and D.23-02-040 established binding 2030 and 2035 greenhouse gas targets and ordered joint CCA/IOU solicitations for long-lead-time clean firm technologies.",
        "official_docket_url": "https://apps.cpuc.ca.gov/apex/f?p=401:56:0::NO:RP,56:P56_PROCEEDING_SELECT:R2005003",
        "tech_links": [
            {"tech_id": "iron_air_battery", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Primary technology selected by California CCAs (Central Coast Community Energy, Silicon Valley Clean Energy) for 8-100 hr storage."},
            {"tech_id": "vanadium_redox_flow", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Captures 8-12 hour mid-duration storage contracts across California CCAs."},
            {"tech_id": "egs_geothermal", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Fulfills CPUC 1,000 MW clean firm capacity mandate (backed by Fervo Energy / Southern California Edison PPA)."},
            {"tech_id": "deepwater_floating_wind", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Directly integrated into CPUC 2035 transmission planning and offshore procurement targets."}
        ],
        "org_names": ["California Energy Commission (CEC)"]
    },

    # =========================================================================
    # 3. UTILITY THERMAL ENERGY NETWORKS (TENs) & BUILDING DECARBONIZATION
    # =========================================================================
    {
        "id": "ny_psc_22_m_0149_tens",
        "docket_number": "Case 22-M-0149",
        "commission": "NYPSC",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "title": "Proceeding on Motion of the Commission to Implement the Utility Thermal Energy Networks and Jobs Act",
        "short_title": "NY PSC Utility Thermal Networks (Case 22-M-0149)",
        "topic_category": "thermal_networks",
        "status": "implementation",
        "open_date": datetime(2022, 7, 22),
        "expected_order_date": datetime(2024, 12, 19),
        "executive_summary": "Proceeding implementing New York's Utility Thermal Energy Networks and Jobs Act, mandating all 7 major gas and electric utilities to design, engineer, and deploy 1 to 5 commercial pilot Thermal Energy Networks (TENs) connecting multiple commercial, residential, and institutional buildings to shared ambient water loops and geothermal borefields.",
        "innovation_impact": "Establishes utility rate-basing for district heating infrastructure, sewer heat recovery, industrial waste heat integration, and geothermal loop systems; protects union jobs by transitioning utility pipefitters from gas to water systems.",
        "commercial_tailwinds": "Utilities have over $250M in authorized pilot project capital expenditures; drives high-volume procurement for commercial water-source heat pumps, advanced drilling equipment, and thermal metering.",
        "commercial_friction_points": "Subsurface right-of-way congestion in NYC and older urban metros; thermal tariff rate design complexities between anchor institutional customers and residential tenants.",
        "key_filings_summary": "Utilities filed Stage 1 and Stage 2 engineering plans for 13+ pilot sites across NY (including ConEd Chelsea/Rockefeller, National Grid Brooklyn/Syracuse, NYSEG Ithaca); Commission issued Phase 1 pilot approvals in 2024.",
        "official_docket_url": "https://documents.dps.ny.gov/public/MatterManagement/CaseMaster.aspx?MatterCaseNo=22-M-0149",
        "tech_links": [
            {"tech_id": "district_thermal_energy_networks", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "The definitive regulatory authorization creating the utility thermal network sector in New York."},
            {"tech_id": "cold_climate_heat_pumps", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Large water-to-water heat pumps serve as the central plant workhorses for utility TENs."},
            {"tech_id": "egs_geothermal", "impact_level": "market_expansion", "commercial_vector": "siting_clarity", "impact_summary": "Deep borefield drilling innovations directly lower CAPEX for network geothermal loops."}
        ],
        "org_names": ["Consolidated Edison", "National Grid", "NYSEG", "NYSERDA"]
    },
    {
        "id": "mass_dpu_20_80_clean_heat",
        "docket_number": "DPU Docket 20-80",
        "commission": "Mass DPU",
        "jurisdiction_level": "state",
        "jurisdiction_state": "MA",
        "title": "Investigation by the Department of Public Utilities on its own Motion into the Role of Gas Local Distribution Companies in Achieving the 2050 Net Zero Emissions Target",
        "short_title": "Mass DPU 20-80 (Gas Utility Decarbonization Order)",
        "topic_category": "thermal_networks",
        "status": "order_issued",
        "open_date": datetime(2020, 10, 29),
        "expected_order_date": datetime(2023, 12, 6),
        "executive_summary": "Historic regulatory order issued by the Massachusetts Department of Public Utilities directing gas utilities (National Grid, Eversource) to phase out fossil gas pipeline expansion, prioritize networked geothermal micro-districts, and accelerate building electrification to meet the Commonwealth's 2050 Net Zero emissions mandate.",
        "innovation_impact": "Establishes the national blueprint for gas utility transition; requires gas utilities to submit clean energy transition plans and authorizes commercial rate recovery for geothermal micro-district pilots (such as Eversource's Framingham networked geothermal project).",
        "commercial_tailwinds": "Opens utility capital budgets to geothermal network technology, industrial heat pump systems, and thermal storage developers across New England.",
        "commercial_friction_points": "Strict gas infrastructure cost-recovery restrictions; regulatory scrutiny over gas utility alternative fuel proposals (RNG and hydrogen blending).",
        "key_filings_summary": "Final Order 20-80 rejected broad hydrogen blending for residential heating and mandated utility transition to networked geothermal and building electrification.",
        "official_docket_url": "https://eeaonline.eea.state.ma.us/DPU/Fileroom/dockets/bynumber/20-80",
        "tech_links": [
            {"tech_id": "district_thermal_energy_networks", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Directly authorized Eversource Framingham and National Grid Lowell networked geothermal pilots."},
            {"tech_id": "cold_climate_heat_pumps", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Core technology driving Massachusetts Clean Heat Standard compliance."}
        ],
        "org_names": ["Massachusetts Clean Energy Center (MassCEC)"]
    },

    # =========================================================================
    # 4. GRID INTERCONNECTION REFORM & HIGH-DER INTEGRATION
    # =========================================================================
    {
        "id": "ny_psc_19_e_0735_sir",
        "docket_number": "Case 19-E-0735",
        "commission": "NYPSC",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "title": "Proceeding on Motion of the Commission as to the Standardized Interconnection Requirements (SIR) and Application Process",
        "short_title": "NY PSC SIR Interconnection Modernization (Case 19-E-0735)",
        "topic_category": "interconnection_reform",
        "status": "active",
        "open_date": datetime(2019, 11, 15),
        "expected_order_date": datetime(2025, 4, 30),
        "executive_summary": "Continuous regulatory proceeding updating New York's Standardized Interconnection Requirements (SIR) for distributed generation, solar, and energy storage systems up to 5 MW connecting to utility distribution networks.",
        "innovation_impact": "Mandates smart inverter certification (IEEE 1547-2018 / UL 1741 SB), establishes standard cost-sharing formulas for substation transformer upgrades, and implements pre-application hosting capacity maps to streamline developer siting.",
        "commercial_tailwinds": "Expedited fast-track screening reduces interconnection review timelines from 12+ months down to 45 business days for compliant solar+storage assets.",
        "commercial_friction_points": "High developer upgrade costs in saturated Upstate rural circuits; utility study backlog in high-penetration community solar territories.",
        "key_filings_summary": "Interconnection Technical Working Group (ITWG) proposed automated screening rules and streamlined Energy Storage System (ESS) charging evaluation criteria.",
        "official_docket_url": "https://documents.dps.ny.gov/public/MatterManagement/CaseMaster.aspx?MatterCaseNo=19-E-0735",
        "tech_links": [
            {"tech_id": "grid_forming_inverters", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "Governs the autonomous volt-var and ride-through settings required for NY SIR approval."},
            {"tech_id": "agrivoltaics_bifacial_solar", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "All community solar and agrivoltaic projects in NY must navigate the SIR / CESIR process."},
            {"tech_id": "derms_vpp_orchestration", "impact_level": "market_expansion", "commercial_vector": "interconnection_access", "impact_summary": "Enables distribution utilities to monitor and dynamically control DER output under SIR rules."}
        ],
        "org_names": ["Consolidated Edison", "National Grid", "NYSEG"]
    },
    {
        "id": "cpuc_r21_06_017_rule21",
        "docket_number": "Rulemaking R.21-06-017",
        "commission": "CPUC",
        "jurisdiction_level": "state",
        "jurisdiction_state": "CA",
        "title": "Order Instituting Rulemaking to Modernize the Electric Grid for a High Distributed Energy Resources Future (Rule 21 & Interconnection)",
        "short_title": "CPUC High-DER & Rule 21 Modernization (R.21-06-017)",
        "topic_category": "interconnection_reform",
        "status": "active",
        "open_date": datetime(2021, 6, 24),
        "expected_order_date": datetime(2025, 7, 30),
        "executive_summary": "CPUC rulemaking reforming California's Rule 21 interconnection tariff to accommodate massive growth in distributed solar, storage, EV fast charging, and microgrids, pioneering dynamic and flexible interconnection based on real-time distribution grid hosting capacity.",
        "innovation_impact": "Establishes 'Flexible Interconnection Agreements' where DERs and commercial EV fleets interconnect rapidly without expensive distribution upgrades by agreeing to automated output throttling via DERMS during rare circuit constraint hours.",
        "commercial_tailwinds": "Dramatically cuts interconnection timelines and upgrade costs for commercial EV charging depots, community solar, and industrial microgrids.",
        "commercial_friction_points": "Requires sophisticated on-site DERMS gateways and communication reliability complying with IEEE 2030.5 protocols.",
        "key_filings_summary": "CPUC Decision D.24-03-004 adopted Phase 1 reforms establishing the standard flexible interconnection option and distribution investment deferral framework.",
        "official_docket_url": "https://apps.cpuc.ca.gov/apex/f?p=401:56:0::NO:RP,56:P56_PROCEEDING_SELECT:R2106017",
        "tech_links": [
            {"tech_id": "derms_vpp_orchestration", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "Provides the automated control software required for Rule 21 flexible interconnection compliance."},
            {"tech_id": "megawatt_charging_systems", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "Allows heavy-duty truck charging depots to connect without waiting for 3-year substation rebuilds."},
            {"tech_id": "grid_forming_inverters", "impact_level": "critical_gate", "commercial_vector": "interconnection_access", "impact_summary": "Rule 21 mandates advanced inverter autonomous ride-through and telemetry."}
        ],
        "org_names": ["California Energy Commission (CEC)"]
    },
    {
        "id": "pjm_er24_99_queue_reform",
        "docket_number": "Docket ER24-99",
        "commission": "FERC / PJM",
        "jurisdiction_level": "rto_iso",
        "jurisdiction_state": "US",
        "title": "PJM Interconnection Queue Cluster Study Reform & Fast-Track Capacity Transition",
        "short_title": "PJM Interconnection Queue Reform (Docket ER24-99)",
        "topic_category": "interconnection_reform",
        "status": "implementation",
        "open_date": datetime(2023, 10, 15),
        "expected_order_date": datetime(2024, 8, 1),
        "executive_summary": "PJM Interconnection tariff filing overhauling its 250+ GW generation and storage interconnection queue, transitioning to first-ready cluster reviews and creating expedited fast-track evaluation for clean generation and battery storage projects in critical data center load pockets across Northern Virginia, Pennsylvania, and Ohio.",
        "innovation_impact": "Accelerates commercial approvals for solar, battery storage, SMR nuclear, and hybrid plants in the world's highest-density data center region (PJM Dominion / PJM East).",
        "commercial_tailwinds": "Fast-track review processes shave 2 to 3 years off development timelines for shovel-ready clean energy and storage projects.",
        "commercial_friction_points": "Steep financial readiness deposits ($5M+) and non-refundable withdrawal penalties for speculative project applications.",
        "key_filings_summary": "FERC approved PJM's cluster study transition rules with implementation active through 2026 across Cycle 1 and Cycle 2 clusters.",
        "official_docket_url": "https://elibrary.ferc.gov/eLibrary/search",
        "tech_links": [
            {"tech_id": "smr_gen4_reactors", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "Governs grid-connected SMR capacity injection studies in the PJM market."},
            {"tech_id": "iron_air_battery", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "Multi-day storage projects in PJM queue evaluated under new cluster reliability metrics."},
            {"tech_id": "dynamic_line_rating_gets", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "PJM evaluating GETs to clear constrained transmission lines into Northern Virginia data centers."}
        ],
        "org_names": ["US Department of Energy (DOE)"]
    },

    # =========================================================================
    # 5. FEDERAL TRANSMISSION PLANNING & VIRTUAL POWER PLANTS (VPPs)
    # =========================================================================
    {
        "id": "ferc_order_2023_interconnection",
        "docket_number": "Docket RM22-14 / Order 2023",
        "commission": "FERC",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "title": "Improvements to Generator Interconnection Procedures and Agreements (Order 2023 / Order 2023-A)",
        "short_title": "FERC Order 2023 (Interconnection Queue Overhaul)",
        "topic_category": "interconnection_reform",
        "status": "implementation",
        "open_date": datetime(2022, 6, 16),
        "expected_order_date": datetime(2024, 3, 21),
        "executive_summary": "Landmark federal regulatory order overhauling the generator interconnection process across all jurisdictional RTOs/ISOs (PJM, NYISO, CAISO, MISO, SPP, ISO-NE) and transmission providers, mandating a cluster study process and requiring transmission operators to explicitly evaluate Grid-Enhancing Technologies (GETs).",
        "innovation_impact": "Mandates that transmission planners explicitly model Dynamic Line Rating (DLR), Advanced Power Flow Control, and Topology Optimization in all cluster facility studies, creating a massive captive market for grid hardware and software startups.",
        "commercial_tailwinds": "Replaces speculative queues with transparent cluster timelines; forces utilities to consider low-cost GETs alternatives before assigning expensive transmission reconductoring costs to developers.",
        "commercial_friction_points": "Developers must demonstrate 100% site control and post significant cash milestone deposits to enter the cluster study.",
        "key_filings_summary": "Order 2023-A reaffirmed core cluster rules and mandatory GETs evaluation in response to rehearing requests from major transmission owner coalitions.",
        "official_docket_url": "https://www.ferc.gov/news-events/news/ferc-issues-final-rule-generator-interconnection-reforms",
        "tech_links": [
            {"tech_id": "dynamic_line_rating_gets", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Explicitly named in Order 2023 as mandatory technology for transmission interconnection study evaluation."},
            {"tech_id": "iron_air_battery", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "Cluster study deliverability rules govern multi-day storage grid injection rights."},
            {"tech_id": "deepwater_floating_wind", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "Offshore wind POIs evaluated in coordinated cluster studies under Order 2023."}
        ],
        "org_names": ["US Department of Energy (DOE)"]
    },
    {
        "id": "ferc_order_1920_tx_planning",
        "docket_number": "Docket RM21-17 / Order 1920",
        "commission": "FERC",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "title": "Building for the Future Through Electric Regional Transmission Planning and Cost Allocation",
        "short_title": "FERC Order 1920 (20-Year Long-Term Transmission Planning)",
        "topic_category": "transmission_planning",
        "status": "implementation",
        "open_date": datetime(2021, 7, 15),
        "expected_order_date": datetime(2024, 5, 13),
        "executive_summary": "Transformative federal rule mandating all transmission providers to conduct forward-looking, 20-year regional transmission planning that explicitly accounts for state clean energy laws, utility resource plans, and extreme weather resilience, establishing transparent ex-ante cost allocation methodologies.",
        "innovation_impact": "Unlocks multi-billion-dollar interstate high-voltage DC (HVDC) transmission corridors and mandates that regional planners evaluate advanced conductors (carbon-core reconductoring) and GETs in all 20-year plans.",
        "commercial_tailwinds": "Enables large-scale remote renewables, deepwater floating offshore wind, and enhanced geothermal to access high-value coastal and metro load centers.",
        "commercial_friction_points": "Interstate cost-sharing disputes between state utility commissions over who pays for multi-state transmission lines.",
        "key_filings_summary": "Order 1920 established 7 mandatory economic and reliability benefit metrics that transmission planners must evaluate when justifying long-term grid expansions.",
        "official_docket_url": "https://www.ferc.gov/news-events/news/ferc-issues-landmark-transmission-rule",
        "tech_links": [
            {"tech_id": "hvdc_transmission_links", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Order 1920 creates the planning mandate for inter-regional high-capacity HVDC transmission."},
            {"tech_id": "dynamic_line_rating_gets", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Mandates evaluation of advanced conductors and dynamic ratings across all regional transmission plans."},
            {"tech_id": "deepwater_floating_wind", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "Provides transmission planning framework for Pacific and Atlantic offshore wind networks."}
        ],
        "org_names": ["US Department of Energy (DOE)"]
    },
    {
        "id": "ferc_order_2222_der_aggregation",
        "docket_number": "Docket RM18-9 / Order 2222",
        "commission": "FERC",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "title": "Participation of Distributed Energy Resource Aggregations in Regional Wholesale Markets",
        "short_title": "FERC Order 2222 (Wholesale VPP & DER Aggregation)",
        "topic_category": "vpp_rate_design",
        "status": "implementation",
        "open_date": datetime(2018, 2, 15),
        "expected_order_date": datetime(2024, 6, 1),
        "executive_summary": "Federal rule opening wholesale electric energy, capacity, and ancillary services markets in all RTO/ISO territories to aggregated distributed energy resources (solar, batteries, EV chargers, smart heat pumps) with minimum aggregation thresholds of no higher than 100 kW.",
        "innovation_impact": "Provides the legal regulatory foundation for Virtual Power Plants (VPPs) and DERMS orchestration software to aggregate thousands of residential and commercial devices and bid them into wholesale power markets.",
        "commercial_tailwinds": "Enables multi-stream revenue stacking: aggregators earn wholesale capacity revenues on top of retail utility bill savings and state incentives.",
        "commercial_friction_points": "Complex multi-jurisdictional rules preventing double-compensation between retail utility programs and wholesale markets; telemetry integration costs for small aggregators.",
        "key_filings_summary": "RTOs/ISOs (NYISO, CAISO, PJM, ISO-NE, MISO) filed compliance tariffs establishing DERA participation models and utility distribution coordination protocols.",
        "official_docket_url": "https://www.ferc.gov/media/ferc-order-no-2222-fact-sheet",
        "tech_links": [
            {"tech_id": "derms_vpp_orchestration", "impact_level": "high_catalyst", "commercial_vector": "tariff_revenue", "impact_summary": "The fundamental legal framework enabling commercial DERMS and VPP market participation."},
            {"tech_id": "v2g_bidirectional_chargers", "impact_level": "high_catalyst", "commercial_vector": "tariff_revenue", "impact_summary": "Allows aggregated fleet and residential EV batteries to supply wholesale spinning reserve and regulation."}
        ],
        "org_names": ["US Department of Energy (DOE)"]
    },
    {
        "id": "cpuc_r22_07_005_demand_flex",
        "docket_number": "Rulemaking R.22-07-005",
        "commission": "CPUC",
        "jurisdiction_level": "state",
        "jurisdiction_state": "CA",
        "title": "Order Instituting Rulemaking to Advance Demand Flexibility Through Electric Rates",
        "short_title": "CPUC Demand Flexibility & VPP Rates (R.22-07-005)",
        "topic_category": "vpp_rate_design",
        "status": "active",
        "open_date": datetime(2022, 7, 14),
        "expected_order_date": datetime(2025, 6, 15),
        "executive_summary": "California Public Utilities Commission proceeding overhauling retail electricity rate design to establish dynamic, real-time rates and universal automated price signals (CalFUSE framework) enabling automated Virtual Power Plants (VPPs) and smart EV chargers to automatically optimize charging against wholesale locational marginal prices.",
        "innovation_impact": "Provides machine-readable, dynamic price APIs that smart thermostats, residential batteries, and commercial EV fleets can ingest to automate peak-demand shedding and charge during solar curtailment hours.",
        "commercial_tailwinds": "Creates guaranteed consumer cost savings for deploying smart energy management systems; expands the addressable market for VPP software aggregators.",
        "commercial_friction_points": "Consumer pushback regarding income-graduated fixed charges (IGFC) and complex time-varying billing structures.",
        "key_filings_summary": "CPUC Decision D.24-05-028 adopted income-graduated fixed charges and authorized dynamic rate pilots for residential and commercial customers across PG&E, SCE, and SDG&E.",
        "official_docket_url": "https://apps.cpuc.ca.gov/apex/f?p=401:56:0::NO:RP,56:P56_PROCEEDING_SELECT:R2207005",
        "tech_links": [
            {"tech_id": "derms_vpp_orchestration", "impact_level": "high_catalyst", "commercial_vector": "tariff_revenue", "impact_summary": "Directly enables automated demand response software to monetize real-time price signals."},
            {"tech_id": "v2g_bidirectional_chargers", "impact_level": "high_catalyst", "commercial_vector": "tariff_revenue", "impact_summary": "EV fleet orchestration software uses dynamic rates to optimize smart charging windows."}
        ],
        "org_names": ["California Energy Commission (CEC)"]
    },
    {
        "id": "ny_psc_15_e_0302_ces",
        "docket_number": "Case 15-E-0302",
        "commission": "NYPSC",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "title": "Proceeding on Motion of the Commission to Implement a Large-Scale Clean Energy Standard",
        "short_title": "NY PSC Clean Energy Standard (Case 15-E-0302 / Tier 4)",
        "topic_category": "clean_firm_procurement",
        "status": "implementation",
        "open_date": datetime(2015, 6, 18),
        "expected_order_date": datetime(2025, 12, 31),
        "executive_summary": "The flagship regulatory proceeding structuring New York's Clean Energy Standard (CES), mandating compliance mechanisms for 70% renewable electricity by 2030 and 100% zero-emission electricity by 2040 across Tier 1 (large-scale solar/wind), Tier 2 (upstate hydro/wind maintenance), Tier 4 (direct clean electricity delivery into NYC / Zone J), and Zero-Emission Credits (ZECs).",
        "innovation_impact": "Directly authorizes over $10B in long-term renewable contracts and unlocks major HVDC transmission links (Champlain Hudson Power Express and Clean Path NY) delivering Canadian hydro, upstate wind, and solar directly into New York City.",
        "commercial_tailwinds": "Provides 20-year fixed REC/OREC revenue contracts that enable commercial project finance for multi-hundred-megawatt clean energy projects.",
        "commercial_friction_points": "Supply chain cost inflation required 2023-2024 expedited re-solicitations (NYSERDA ORECRF23-1 and Tier 1 RESRFP23-1).",
        "key_filings_summary": "Commission approved Tier 4 contracts with CHPE and Clean Path NY; ongoing biennial reviews calibrate compliance obligations for Load Serving Entities.",
        "official_docket_url": "https://documents.dps.ny.gov/public/MatterManagement/CaseMaster.aspx?MatterCaseNo=15-E-0302",
        "tech_links": [
            {"tech_id": "hvdc_transmission_interconnects", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Tier 4 contracts underwrite the 1,250 MW Champlain Hudson Power Express HVDC cable."},
            {"tech_id": "deepwater_floating_wind", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "Large-scale offshore wind procurement structured under CES Tier 1 and OREC frameworks."},
            {"tech_id": "iron_air_battery", "impact_level": "high_catalyst", "commercial_vector": "interconnection_access", "impact_summary": "Co-located long-duration storage qualifies for Tier 1 paired capacity value."}
        ],
        "org_names": ["NYSERDA", "Consolidated Edison", "New York Power Authority"]
    },
    {
        "id": "ny_psc_18_e_0138_ev_make_ready",
        "docket_number": "Case 18-E-0138",
        "commission": "NYPSC",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "title": "Proceeding on Motion of the Commission Regarding Electric Vehicle Supply Equipment and Infrastructure",
        "short_title": "NY PSC EV Make-Ready & Fleet Infrastructure (Case 18-E-0138)",
        "topic_category": "interconnection_reform",
        "status": "implementation",
        "open_date": datetime(2018, 4, 19),
        "expected_order_date": datetime(2025, 10, 30),
        "executive_summary": "Comprehensive regulatory proceeding establishing New York's statewide $700M+ EV Make-Ready Program across all investor-owned utilities (ConEd, National Grid, Central Hudson, NYSEG, RG&E, O&R), funding utility-side and customer-side electrical infrastructure for 50,000+ Level 2 and DC Fast Chargers.",
        "innovation_impact": "Directly subsidizes the high-voltage switchgear, step-down transformers, and civil trenching required for commercial fleet depots, municipal bus electrification, and public megawatt charging corridors.",
        "commercial_tailwinds": "Covers up to 100% of electrical make-ready infrastructure costs for EV charging sites in Disadvantaged Communities (DACs).",
        "commercial_friction_points": "Distribution vault capacity limits in NYC and extended utility transformer manufacturing delivery lead times.",
        "key_filings_summary": "PSC Order in 2023 expanded the program with dedicated Medium- and Heavy-Duty (MHD) Fleet Make-Ready incentives and managed charging requirements.",
        "official_docket_url": "https://documents.dps.ny.gov/public/MatterManagement/CaseMaster.aspx?MatterCaseNo=18-E-0138",
        "tech_links": [
            {"tech_id": "megawatt_charging_systems_mcs", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "MHD fleet make-ready funding pays for high-power megawatt depot electrical infrastructure."},
            {"tech_id": "v2g_bidirectional_chargers", "impact_level": "high_catalyst", "commercial_vector": "tariff_revenue", "impact_summary": "Managed charging rules reward V2G and smart bidirectional charging."}
        ],
        "org_names": ["Consolidated Edison", "National Grid", "NYSEG", "NYSERDA"]
    },
    {
        "id": "illinois_icc_23_0072_ceja_grid",
        "docket_number": "Docket 23-0072",
        "commission": "ICC",
        "jurisdiction_level": "state",
        "jurisdiction_state": "IL",
        "title": "Investigation into Multi-Year Integrated Grid Plans Pursuant to the Climate and Equitable Jobs Act (CEJA)",
        "short_title": "Illinois ICC CEJA Multi-Year Grid Plan (Docket 23-0072)",
        "topic_category": "interconnection_reform",
        "status": "active",
        "open_date": datetime(2023, 1, 20),
        "expected_order_date": datetime(2025, 4, 15),
        "executive_summary": "Illinois Commerce Commission proceeding reviewing ComEd and Ameren Illinois multi-billion-dollar Multi-Year Integrated Grid Plans under the landmark Climate and Equitable Jobs Act (CEJA), establishing strict equity mandates, non-wires alternatives (NWAs), and distribution hosting capacity transparency.",
        "innovation_impact": "Requires utilities to formally solicit Non-Wires Alternatives (distributed energy storage, VPPs, energy efficiency) before approving traditional capital expenditures for new distribution substations and feeders.",
        "commercial_tailwinds": "Creates dedicated utility NWA procurement opportunities and funding for clean tech startups deploying commercial microgrids and distributed batteries in Illinois.",
        "commercial_friction_points": "ICC rejection of initial utility capital expenditure plans due to insufficient affordability and equity justifications, requiring revised utility filings.",
        "key_filings_summary": "ICC issued historic December 2023 orders rejecting initial utility rate plans; utilities filed revised grid plans incorporating expanded NWA pilots and DER integration in 2024.",
        "official_docket_url": "https://www.icc.illinois.gov/docket/P2023-0072",
        "tech_links": [
            {"tech_id": "derms_vpp_orchestration", "impact_level": "high_catalyst", "commercial_vector": "direct_procurement", "impact_summary": "NWA mandates create direct utility procurement for software-orchestrated DER aggregations."},
            {"tech_id": "iron_air_battery", "impact_level": "market_expansion", "commercial_vector": "direct_procurement", "impact_summary": "Utility NWA solicitations evaluate grid-scale long-duration batteries for substation deferral."}
        ],
        "org_names": ["Illinois Department of Commerce and Economic Opportunity (DCEO)"]
    }
]


TECH_ID_ALIASES = {
    "iron_air_battery": "iron_air_battery",
    "vanadium_redox_flow": "vanadium_redox_flow",
    "solid_state_lithium_battery": "solid_state_lithium",
    "solid_state_lithium": "solid_state_lithium",
    "sodium_ion_battery": "sodium_ion_battery",
    "smr_gen4_reactors": "smr_advanced_nuclear",
    "smr_advanced_nuclear": "smr_advanced_nuclear",
    "egs_geothermal": "enhanced_geothermal_egs",
    "enhanced_geothermal_egs": "enhanced_geothermal_egs",
    "dynamic_line_rating_gets": "grid_enhancing_technologies",
    "grid_enhancing_technologies": "grid_enhancing_technologies",
    "pem_electrolyzer": "pem_soec_electrolyzers",
    "pem_soec_electrolyzers": "pem_soec_electrolyzers",
    "microgrid_black_start": "black_start_microgrids",
    "black_start_microgrids": "black_start_microgrids",
    "derms_vpp_orchestration": "vpp_derms_orchestration",
    "vpp_derms_orchestration": "vpp_derms_orchestration",
    "grid_forming_inverters": "advanced_inverters_grid_forming",
    "advanced_inverters_grid_forming": "advanced_inverters_grid_forming",
    "deepwater_floating_wind": "floating_offshore_wind",
    "floating_offshore_wind": "floating_offshore_wind",
    "district_thermal_energy_networks": "thermal_energy_networks_tens",
    "thermal_energy_networks_tens": "thermal_energy_networks_tens",
    "cold_climate_heat_pumps": "cold_climate_heat_pumps",
    "megawatt_charging_systems": "megawatt_charging_systems_mcs",
    "megawatt_charging_systems_mcs": "megawatt_charging_systems_mcs",
    "v2g_bidirectional_chargers": "megawatt_charging_systems_mcs",
    "hvdc_transmission_links": "hvdc_transmission_interconnects",
    "hvdc_transmission_interconnects": "hvdc_transmission_interconnects",
    "agrivoltaics_bifacial_solar": "agrivoltaics_bifacial_solar",
    "ai_datacenter_liquid_cooling": "ai_datacenter_liquid_cooling"
}


def seed_proceedings(db=None):
    """Seed regulatory proceedings and linkage records into PostgreSQL / SQLite database."""
    should_close = False
    if db is None:
        init_db()
        db = SessionLocal()
        should_close = True

    try:
        print(f"[*] Seeding {len(SEED_PROCEEDINGS)} authoritative regulatory proceedings and PUC dockets...")
        
        # Cache technology IDs for linking
        existing_tech_ids = {t.id for t in db.query(Technology.id).all()}
        # Cache organization IDs for linking
        orgs = db.query(Organization.name, Organization.id).all()
        org_map = {o.name.lower(): o.id for o in orgs}

        created_count = 0
        updated_count = 0
        tech_links_count = 0
        org_links_count = 0

        for p_data in SEED_PROCEEDINGS:
            p_id = p_data["id"]
            existing = db.query(RegulatoryProceeding).filter(RegulatoryProceeding.id == p_id).first()

            if not existing:
                existing = RegulatoryProceeding(id=p_id)
                db.add(existing)
                created_count += 1
            else:
                updated_count += 1

            existing.docket_number = p_data["docket_number"]
            existing.commission = p_data["commission"]
            existing.jurisdiction_level = p_data.get("jurisdiction_level", "state")
            existing.jurisdiction_state = p_data.get("jurisdiction_state", "US")
            existing.title = p_data["title"]
            existing.short_title = p_data.get("short_title")
            existing.topic_category = p_data["topic_category"]
            existing.status = p_data.get("status", "active")
            existing.open_date = p_data.get("open_date")
            existing.comment_deadline = p_data.get("comment_deadline")
            existing.expected_order_date = p_data.get("expected_order_date")
            existing.executive_summary = p_data["executive_summary"]
            existing.innovation_impact = p_data["innovation_impact"]
            existing.commercial_tailwinds = p_data.get("commercial_tailwinds")
            existing.commercial_friction_points = p_data.get("commercial_friction_points")
            existing.key_filings_summary = p_data.get("key_filings_summary")
            existing.official_docket_url = p_data.get("official_docket_url")

            db.flush()

            # Technology links
            db.query(ProceedingTechnologyLink).filter(ProceedingTechnologyLink.proceeding_id == p_id).delete()
            seen_tech = set()
            for tlink in p_data.get("tech_links", []):
                raw_tech_id = tlink["tech_id"]
                resolved_tech_id = TECH_ID_ALIASES.get(raw_tech_id, raw_tech_id)
                if resolved_tech_id in existing_tech_ids and resolved_tech_id not in seen_tech:
                    seen_tech.add(resolved_tech_id)
                    link_obj = ProceedingTechnologyLink(
                        proceeding_id=p_id,
                        technology_id=resolved_tech_id,
                        impact_level=tlink.get("impact_level", "high_catalyst"),
                        commercial_vector=tlink.get("commercial_vector", "interconnection_access"),
                        impact_summary=tlink.get("impact_summary")
                    )
                    db.add(link_obj)
                    tech_links_count += 1

            # Organization links
            db.query(ProceedingOrganizationLink).filter(ProceedingOrganizationLink.proceeding_id == p_id).delete()
            seen_org = set()
            for org_query in p_data.get("org_names", []):
                q_lower = org_query.lower()
                matched_id = org_map.get(q_lower)
                if not matched_id:
                    for name_key, oid in org_map.items():
                        if q_lower in name_key or name_key in q_lower:
                            matched_id = oid
                            break
                if matched_id and matched_id not in seen_org:
                    seen_org.add(matched_id)
                    olink_obj = ProceedingOrganizationLink(
                        proceeding_id=p_id,
                        organization_id=matched_id,
                        role="affected_utility"
                    )
                    db.add(olink_obj)
                    org_links_count += 1

        db.commit()
        print(f"[+] Successfully seeded {created_count} new and {updated_count} updated proceedings.")
        print(f"[+] Created {tech_links_count} technology linkages and {org_links_count} utility linkages.")
        return True
    except Exception as e:
        db.rollback()
        print(f"[-] Error seeding regulatory proceedings: {e}")
        return False
    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    seed_proceedings()
