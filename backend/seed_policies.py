"""
Authoritative Seed Dataset for Clean Energy Innovation Policies, Regulations, Codes & Standards.
Grounds the Energy Innovation Terminal across:
1. Safety & Testing Codes (NFPA, UL, IEEE, ASME, SAE)
2. Grid Interconnection & Market Tariffs (FERC Orders, State SIR, CA Rule 21)
3. Federal Tax Credits & Statutory Mandates (IRA §45V, §45Q, §48C, §45X, Justice40, BABA)
4. State Climate Acts, Building Codes & Siting (NY CLCPA, CA SB 100, Title 24, NYC FDNY 3 RCNY §401-01)
5. Emissions, Low-Carbon Fuels & Materials Standards (EPA CAA §111, CA LCFS, EPA RFS2)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, init_db, init_fts
from app.models.policy import (
    PolicyStandard,
    PolicyTechnologyLink,
    PolicyFuelLink,
    PolicyOpportunityLink,
    PolicyOrganizationLink
)
from app.models.technology import Technology
from app.models.opportunity import Opportunity

# Master Policy & Standards Registry
SEED_POLICIES = [
    # =========================================================================
    # 1. SAFETY & TESTING STANDARDS
    # =========================================================================
    {
        "id": "nfpa_855_2023",
        "code_identifier": "NFPA 855",
        "title": "Standard for the Installation of Stationary Energy Storage Systems",
        "short_title": "NFPA 855 (BESS Safety & Siting)",
        "category": "safety_code",
        "jurisdiction_level": "international",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2020,
        "latest_revision": "2023 Edition",
        "executive_summary": "The premier international standard setting stringent fire protection, physical setbacks, ventilation, and maximum allowable energy capacities for stationary battery energy storage systems (BESS).",
        "statutory_intent": "Mitigate catastrophic thermal runaway propagation, deflagration hazards, and toxic gas emissions in lithium-ion and electrochemical energy storage installations.",
        "compliance_mandate": "Requires maximum unit sizing of 50 kWh for residential and 600 kWh for commercial groups with 3-foot clearance separation between units, continuous combustible gas detection, exhaust ventilation, and emergency operations planning.",
        "commercial_friction_points": "High balance-of-system (BOS) engineering costs; strict indoor setback requirements often restrict urban dense deployments unless accompanied by UL 9540A large-scale fire testing approvals.",
        "associated_incentives": "Prerequisite compliance gate for obtaining commercial project insurance, municipal building permits, and public grant disbursements across NY, CA, and MA.",
        "official_source_url": "https://www.nfpa.org/codes-and-standards/nfpa-855-standard-development/855",
        "tech_links": [
            {"tech_id": "iron_air_battery", "relevance_type": "safety_siting", "compliance_impact": "accelerator_tailwind", "impact_summary": "Iron-air aqueous chemistry is non-flammable and inherently avoids thermal runaway explosion risks under NFPA 855."},
            {"tech_id": "vanadium_redox_flow", "relevance_type": "safety_siting", "compliance_impact": "accelerator_tailwind", "impact_summary": "Non-combustible aqueous electrolyte simplifies NFPA 855 indoor spacing and fire suppression compliance."},
            {"tech_id": "solid_state_lithium_battery", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Must demonstrate that solid ceramic/polymer electrolytes eliminate dendritic short circuits and thermal runaway under abuse conditions."},
            {"tech_id": "sodium_ion_battery", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Requires full UL 9540A testing to certify safety clearances under NFPA 855 Section 4.3."},
            {"tech_id": "microgrid_black_start", "relevance_type": "safety_siting", "compliance_impact": "cost_driver", "impact_summary": "Enforces separation distances between co-located generation assets and battery enclosures."}
        ],
        "fuel_links": []
    },
    {
        "id": "ul_9540a_2023",
        "code_identifier": "UL 9540A",
        "title": "Test Method for Evaluating Thermal Runaway Fire Propagation in Battery Energy Storage Systems",
        "short_title": "UL 9540A (Thermal Runaway Testing Protocol)",
        "category": "safety_code",
        "jurisdiction_level": "international",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2018,
        "latest_revision": "4th Edition (2023)",
        "executive_summary": "The standardized four-tier testing methodology (Cell Level, Module Level, Unit Level, Installation Level) required by AHJs (Authorities Having Jurisdiction) to evaluate thermal runaway hazards and explosive gas composition.",
        "statutory_intent": "Provide quantitative empirical data on cell venting, heat release rates, flammable gas generation (H2, CO, CH4), and projectile risks during forced thermal runaway.",
        "compliance_mandate": "Energy storage OEMs must complete certified destructive test regimes across cell, module, and full rack configurations to waive the standard 3-foot / 50 kWh separation restrictions in NFPA 855 and International Fire Code (IFC).",
        "commercial_friction_points": "Testing costs $250,000 to $600,000+ per battery architecture; long test laboratory backlog (6 to 12 months) delays time-to-market for novel battery chemistries.",
        "associated_incentives": "Passing UL 9540A is mandatory for indoor urban energy storage siting in New York City (FDNY) and California major metros.",
        "official_source_url": "https://www.shopulstandards.com/ProductDetail.aspx?UniqueKey=42921",
        "tech_links": [
            {"tech_id": "sodium_ion_battery", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Must produce certified UL 9540A test reports before commercial deployment in US utility projects."},
            {"tech_id": "solid_state_lithium_battery", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Crucial for verifying that solid electrolytes eliminate flammable gas venting during nail penetration and overcharge."},
            {"tech_id": "iron_air_battery", "relevance_type": "mandatory_testing", "compliance_impact": "accelerator_tailwind", "impact_summary": "Inherently passes thermal runaway testing due to non-combustible water-based electrolyte."}
        ],
        "fuel_links": []
    },
    {
        "id": "ul_1741_sb_2022",
        "code_identifier": "UL 1741 SB",
        "title": "Inverters, Converters, Controllers and Interconnection System Equipment for Use With Distributed Energy Resources",
        "short_title": "UL 1741 SB (Smart & Grid-Forming Inverters)",
        "category": "safety_code",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2022,
        "latest_revision": "3rd Edition with Supplement SB",
        "executive_summary": "Manufacturing and testing standard that certifies inverters and power conversion systems for advanced grid-supportive functionality, frequency/voltage ride-through, and IEEE 1547-2018 compliance.",
        "statutory_intent": "Ensure distributed solar, wind, and storage inverters stabilize the grid during bulk power system disruptions rather than tripping offline simultaneously.",
        "compliance_mandate": "All utility-interconnected inverters installed in major US ISO/RTO territories must hold active UL 1741 SB certification verifying autonomous volt-var, frequency-watt, and active anti-islanding capabilities.",
        "commercial_friction_points": "Legacy inverter inventories must be recertified or phased out; firmware compliance complexity for emerging grid-forming (GFM) control topologies.",
        "associated_incentives": "Enables distributed resources to participate in high-value utility DERMS and ancillary services programs.",
        "official_source_url": "https://www.shopulstandards.com/ProductDetail.aspx?UniqueKey=39294",
        "tech_links": [
            {"tech_id": "grid_forming_inverters", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Standardized certification benchmark for black-start and synthetic inertia capabilities."},
            {"tech_id": "perovskite_tandem_solar", "relevance_type": "interconnection", "compliance_impact": "cost_driver", "impact_summary": "Balance-of-system inverter pairing must hold UL 1741 SB certification."},
            {"tech_id": "v2g_bidirectional_chargers", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Bidirectional EV chargers exporting to the grid are legally classified as inverters and must hold UL 1741 SB."}
        ],
        "fuel_links": []
    },
    {
        "id": "ieee_1547_2018",
        "code_identifier": "IEEE 1547-2018",
        "title": "Standard for Interconnection and Interoperability of Distributed Energy Resources with Associated Electric Power Systems Interfaces",
        "short_title": "IEEE 1547-2018 (DER Interconnection Standard)",
        "category": "interconnection_rule",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2018,
        "latest_revision": "IEEE 1547-2018 (Adopted 2023+)",
        "executive_summary": "The national engineering benchmark defining technical requirements for interconnecting solar, energy storage, fuel cells, and microgrids to the distribution system, mandating smart inverter capabilities and standardized communication protocols (IEEE 2030.5, SunSpec Modbus, DNP3).",
        "statutory_intent": "Establish uniform interoperability, power quality, reactive power control, and interoperable communications across all US electric utilities.",
        "compliance_mandate": "DER projects must provide continuous autonomous voltage regulation, ride through abnormal grid frequency/voltage excursions, and support standardized telemetry with utility distribution management systems (ADMS).",
        "commercial_friction_points": "Uneven state-by-state utility implementation timelines; utility interconnection study delays when testing custom communication gateways.",
        "associated_incentives": "Essential for obtaining fast-track interconnection screening under state utility tariffs.",
        "official_source_url": "https://standards.ieee.org/ieee/1547/5826/",
        "tech_links": [
            {"tech_id": "grid_forming_inverters", "relevance_type": "interconnection", "compliance_impact": "critical_gate", "impact_summary": "Defines the exact voltage/frequency trip thresholds and ride-through curves for inverter firmware."},
            {"tech_id": "derms_vpp_orchestration", "relevance_type": "mandatory_testing", "compliance_impact": "accelerator_tailwind", "impact_summary": "Mandates open communication protocols (IEEE 2030.5 / DNP3) that allow DERMS software to orchestrate multi-vendor assets."},
            {"tech_id": "agrivoltaics_bifacial_solar", "relevance_type": "interconnection", "compliance_impact": "cost_driver", "impact_summary": "Distribution feeder hosting capacity and anti-islanding coordination governed by IEEE 1547."}
        ],
        "fuel_links": []
    },
    {
        "id": "asme_b31_12_2019",
        "code_identifier": "ASME B31.12",
        "title": "Hydrogen Piping and Pipelines Code",
        "short_title": "ASME B31.12 (Hydrogen Pipelines & Piping)",
        "category": "safety_code",
        "jurisdiction_level": "international",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2019,
        "latest_revision": "2019 (Reaffirmed 2024)",
        "executive_summary": "Comprehensive safety and material engineering standard governing the design, construction, operation, and maintenance of high-pressure hydrogen pipelines, gaseous distribution piping, and refueling facility manifolds.",
        "statutory_intent": "Prevent hydrogen embrittlement, micro-cracking, and catastrophic leakage in metallic and composite materials exposed to pressurized H2 gas.",
        "compliance_mandate": "Specifies strict material selection guidelines (limiting carbon steel yield strengths, prescribing 316L stainless steel alloys or specialized polymer composite liners) and radiographic weld inspection protocols for any hydrogen system operating above 100 psig.",
        "commercial_friction_points": "High capital cost for hydrogen-rated metallurgy; retrofit blending into existing natural gas pipelines requires extensive material fracture toughness reassessments.",
        "associated_incentives": "Mandatory standard for all DOE Regional Clean Hydrogen Hubs (H2Hubs) and pipeline offtake infrastructure.",
        "official_source_url": "https://www.asme.org/codes-standards/find-codes-standards/b31-12-hydrogen-piping-pipelines",
        "tech_links": [
            {"tech_id": "pem_electrolyzer", "relevance_type": "safety_siting", "compliance_impact": "critical_gate", "impact_summary": "All balance-of-plant high-pressure gas manifolds (30-80 bar) must conform to ASME B31.12."},
            {"tech_id": "soec_solid_oxide_electrolyzer", "relevance_type": "safety_siting", "compliance_impact": "critical_gate", "impact_summary": "High-temperature steam and hydrogen effluent piping requires specialized nickel-alloy ASME compliance."},
            {"tech_id": "salt_cavern_h2_storage", "relevance_type": "safety_siting", "compliance_impact": "critical_gate", "impact_summary": "Wellhead piping and surface gathering lines must meet ASME B31.12 transmission pipeline rules."}
        ],
        "fuel_links": [
            {"fuel_vector": "green_hydrogen", "lifecycle_ci_threshold": "N/A", "impact_summary": "Governs pipeline transport and plant piping for pure hydrogen and hydrogen blends."}
        ]
    },
    {
        "id": "sae_j3271_mcs_2024",
        "code_identifier": "SAE J3271",
        "title": "Megawatt Charging System (MCS) for Heavy-Duty Electric Vehicles",
        "short_title": "SAE J3271 (Megawatt Charging Standard)",
        "category": "safety_code",
        "jurisdiction_level": "international",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2024,
        "latest_revision": "2024 Release",
        "executive_summary": "The ultra-high-power DC charging interface standard for Class 6–8 commercial heavy-duty trucks, electric buses, aerospace, and marine vessels, delivering up to 3.75 MW (3,000 Amps at 1,250 Volts DC).",
        "statutory_intent": "Establish a single interoperable global charging connector and liquid-cooled cable standard capable of fully recharging a 500 kWh heavy-duty truck battery in under 20 minutes.",
        "compliance_mandate": "Defines connector geometry, liquid-cooling thermal management, pin assignments, automated locking mechanisms, and ISO 15118-20 secure digital communication protocols.",
        "commercial_friction_points": "Massive grid interconnection demands (5–20 MW per truck stop) requiring dedicated on-site battery storage or substation upgrades.",
        "associated_incentives": "Required for participating in federal NEVI (National Electric Vehicle Infrastructure) freight corridor funding and state zero-emission truck incentive programs.",
        "official_source_url": "https://www.sae.org/standards/content/j3271_202404/",
        "tech_links": [
            {"tech_id": "megawatt_charging_systems", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Defines the fundamental mechanical and electrical connector architecture for all 1MW+ chargers."},
            {"tech_id": "silicon_anode_batteries", "relevance_type": "mandatory_testing", "compliance_impact": "accelerator_tailwind", "impact_summary": "Fast-charge cell validation relies on 4C+ continuous charge rates enabled by MCS protocols."}
        ],
        "fuel_links": []
    },

    # =========================================================================
    # 2. GRID INTERCONNECTION & MARKET TARIFFS
    # =========================================================================
    {
        "id": "ferc_order_2023",
        "code_identifier": "FERC Order 2023",
        "title": "Improvements to Generator Interconnection Procedures and Agreements",
        "short_title": "FERC Order 2023 (Interconnection Queue Reform)",
        "category": "interconnection_rule",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2023,
        "latest_revision": "Order 2023-A (2024)",
        "executive_summary": "Landmark federal regulatory order overhauling the generator interconnection process across all jurisdictional RTOs/ISOs and transmission providers, transitioning from a broken 'first-come, first-served' serial review to a 'first-ready, first-served' cluster study process.",
        "statutory_intent": "Clear the 2,600+ GW backlog of solar, wind, and storage projects stuck in US interconnection queues and impose financial penalties on speculative applications and slow transmission providers.",
        "compliance_mandate": "Imposes steep commercial readiness deposits (site control proof, $5M+ study deposits), strict withdrawal penalties for projects that drop out, and mandatory evaluation of Grid-Enhancing Technologies (DLR, advanced power flow control) in transmission studies.",
        "commercial_friction_points": "Developers must post non-refundable cash deposits and demonstrate 100% site control much earlier in the project development lifecycle.",
        "associated_incentives": "Dramatically compresses multi-year study timelines for shovel-ready clean energy and storage projects.",
        "official_source_url": "https://www.ferc.gov/news-events/news/ferc-issues-final-rule-generator-interconnection-reforms",
        "tech_links": [
            {"tech_id": "dynamic_line_rating_gets", "relevance_type": "interconnection", "compliance_impact": "accelerator_tailwind", "impact_summary": "Order 2023 explicitly mandates that transmission operators evaluate GETs and DLR in interconnection facility studies."},
            {"tech_id": "iron_air_battery", "relevance_type": "interconnection", "compliance_impact": "critical_gate", "impact_summary": "Governs the cluster study queue entry and deliverability studies for multi-day storage assets."},
            {"tech_id": "deepwater_floating_wind", "relevance_type": "interconnection", "compliance_impact": "critical_gate", "impact_summary": "Offshore wind interconnection points of interconnection (POIs) subject to cluster study milestones."},
            {"tech_id": "egs_geothermal", "relevance_type": "interconnection", "compliance_impact": "cost_driver", "impact_summary": "Baseload geothermal capacity must navigate firm transmission deliverability tests."}
        ],
        "fuel_links": []
    },
    {
        "id": "ferc_order_1920",
        "code_identifier": "FERC Order 1920",
        "title": "Building for the Future Through Electric Regional Transmission Planning and Cost Allocation",
        "short_title": "FERC Order 1920 (Long-Term Regional Transmission Planning)",
        "category": "interconnection_rule",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2024,
        "latest_revision": "Order 1920 (Issued May 2024)",
        "executive_summary": "Transformative federal rule requiring transmission providers to conduct forward-looking, 20-year regional transmission planning that explicitly accounts for state clean energy laws, utility resource plans, and extreme weather resilience.",
        "statutory_intent": "Proactively build high-voltage interstate and interregional transmission lines to integrate massive amounts of low-cost renewable energy and meet national decarbonization goals.",
        "compliance_mandate": "Transmission operators must develop 20-year plans revised every 5 years, evaluate economic and reliability benefits across 7 mandatory criteria, establish ex-ante cost allocation methodologies, and evaluate GETs (dynamic line ratings, advanced conductors).",
        "commercial_friction_points": "Interstate cost-sharing disputes between state utility commissions over who pays for multi-state transmission corridors.",
        "associated_incentives": "Unlocks multi-billion-dollar transmission corridors enabling large-scale offshore wind, remote solar, and regional clean energy trade.",
        "official_source_url": "https://www.ferc.gov/news-events/news/ferc-issues-landmark-transmission-rule",
        "tech_links": [
            {"tech_id": "hvdc_transmission_links", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Order 1920 mandates long-term planning for inter-regional high-capacity HVDC corridors."},
            {"tech_id": "dynamic_line_rating_gets", "relevance_type": "mandatory_testing", "compliance_impact": "accelerator_tailwind", "impact_summary": "Requires transmission planners to evaluate advanced conductor reconductoring and dynamic ratings in all 20-year plans."},
            {"tech_id": "deepwater_floating_wind", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Enables regional offshore transmission networks across Pacific and Atlantic coastlines."}
        ],
        "fuel_links": []
    },
    {
        "id": "ferc_order_2222",
        "code_identifier": "FERC Order 2222",
        "title": "Participation of Distributed Energy Resource Aggregations in Regional Wholesale Markets",
        "short_title": "FERC Order 2222 (DER & VPP Aggregation)",
        "category": "interconnection_rule",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2020,
        "latest_revision": "Implementation through 2026",
        "executive_summary": "Opens wholesale electric capacity, energy, and ancillary service markets to aggregated distributed energy resources (DERs)—including rooftop solar, residential batteries, smart thermostats, and EV chargers.",
        "statutory_intent": "Level the playing field for distributed clean technologies by allowing Virtual Power Plants (VPPs) to compete directly alongside conventional power plants in wholesale markets.",
        "compliance_mandate": "RTOs/ISOs must establish minimum aggregation thresholds of no higher than 100 kW, allow multi-technology heterogeneous aggregations, and create transparent coordination rules with local distribution utilities.",
        "commercial_friction_points": "Complex 'double-counting' dispute rules between retail utility net metering tariffs and wholesale capacity payments; telemetry integration costs for small aggregators.",
        "associated_incentives": "Creates multi-stream revenue stacking for distributed energy storage and smart EV charging aggregators.",
        "official_source_url": "https://www.ferc.gov/media/ferc-order-no-2222-fact-sheet",
        "tech_links": [
            {"tech_id": "derms_vpp_orchestration", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Provides the legal regulatory foundation for VPPs to monetize aggregated grid services in wholesale markets."},
            {"tech_id": "v2g_bidirectional_chargers", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Allows aggregated fleet and residential EV batteries to supply wholesale spinning reserve and frequency regulation."},
            {"tech_id": "district_thermal_energy_networks", "relevance_type": "market_incentive", "compliance_impact": "cost_driver", "impact_summary": "Thermal storage flexibility can be bid into wholesale demand response programs."}
        ],
        "fuel_links": []
    },
    {
        "id": "ny_sir_2023",
        "code_identifier": "NY PSC SIR",
        "title": "New York State Standardized Interconnection Requirements and Application Process",
        "short_title": "NY SIR (New York Interconnection Tariff)",
        "category": "interconnection_rule",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2023,
        "latest_revision": "2023 NYPSC Order",
        "executive_summary": "The definitive regulatory framework governing all distributed generation and energy storage systems up to 5 MW connecting to New York investor-owned utility distribution systems (ConEd, National Grid, NYSEG, RG&E, Central Hudson, O&R).",
        "statutory_intent": "Streamline application review, establish predictable Coordinated Electric System Interconnection Review (CESIR) timelines, and mandate standard technical interconnection screens.",
        "compliance_mandate": "Defines fast-track eligibility (<50 kW simplified, <5 MW standard), mandatory cost allocation rules for substation transformer upgrades, and smart inverter setting requirements.",
        "commercial_friction_points": "Substation saturation and high developer costs for dedicated distribution line extensions; CESIR study delays in high-penetration rural upstate areas.",
        "associated_incentives": "Clear statutory timelines and pre-application hosting capacity maps reduce upfront development uncertainty across NY State.",
        "official_source_url": "https://dps.ny.gov/standardized-interconnection-requirements-sir",
        "tech_links": [
            {"tech_id": "agrivoltaics_bifacial_solar", "relevance_type": "interconnection", "compliance_impact": "critical_gate", "impact_summary": "All community solar and agrivoltaic systems <5 MW in NY must obtain formal NY SIR / CESIR approval."},
            {"tech_id": "iron_air_battery", "relevance_type": "interconnection", "compliance_impact": "critical_gate", "impact_summary": "Governs distribution-connected long-duration energy storage installations in New York."},
            {"tech_id": "microgrid_black_start", "relevance_type": "interconnection", "compliance_impact": "critical_gate", "impact_summary": "Regulates islanding transfer switches and point of common coupling (PCC) protection."}
        ],
        "fuel_links": []
    },

    # =========================================================================
    # 3. FEDERAL TAX CREDITS & STATUTORY MANDATES (INFLATION REDUCTION ACT)
    # =========================================================================
    {
        "id": "ira_sec_45v_clean_h2",
        "code_identifier": "26 U.S.C. § 45V",
        "title": "Inflation Reduction Act Section 45V: Clean Hydrogen Production Tax Credit",
        "short_title": "IRA § 45V (Clean Hydrogen PTC)",
        "category": "tax_incentive",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2023,
        "sunset_year": 2033,
        "latest_revision": "Treasury Proposed Guidance (Dec 2023 / Final 2024)",
        "executive_summary": "Tiered 10-year production tax credit providing up to $3.00 per kilogram of clean hydrogen produced with lifecycle greenhouse gas emissions below 0.45 kg CO2e/kg H2, determined via the GREET model.",
        "statutory_intent": "Scale domestic production of zero-carbon green and clean hydrogen to cost-parity with conventional fossil-fuel steam methane reforming.",
        "compliance_mandate": "Requires compliance with the 'Three Pillars' framework: (1) Incrementality/Additionality (new clean power generated within 36 months), (2) Deliverability/Regionality (clean power sourced from the same balancing authority), and (3) Hourly Temporal Matching (transitioning from annual to hourly Energy Attribute Certificates).",
        "commercial_friction_points": "Hourly matching requirements raise the Levelized Cost of Hydrogen (LCOH) by requiring oversized renewable generation and on-site energy storage; strict additionality criteria restrict baseload nuclear-to-hydrogen pairing without new capacity additions.",
        "associated_incentives": "Up to $3.00/kg clean H2 (top tier), $1.00/kg (tier 2), $0.75/kg (tier 3), $0.60/kg (tier 4). Stackable with state incentives.",
        "official_source_url": "https://www.irs.gov/clean-hydrogen-production-credit",
        "tech_links": [
            {"tech_id": "pem_electrolyzer", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Primary economic engine for green hydrogen projects; enables sub-$2.00/kg levelized cost of hydrogen."},
            {"tech_id": "soec_solid_oxide_electrolyzer", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "High thermodynamic efficiency reduces electricity input per kg of H2, optimizing 45V credit value."},
            {"tech_id": "turquoise_h2_methane_pyrolysis", "relevance_type": "market_incentive", "compliance_impact": "critical_gate", "impact_summary": "Must prove low upstream methane leakage in 45V GREET lifecycle modeling to qualify for top-tier credit."}
        ],
        "fuel_links": [
            {"fuel_vector": "green_hydrogen", "lifecycle_ci_threshold": "< 0.45 kg CO2e / kg H2", "impact_summary": "Qualifies for maximum $3.00/kg 10-year production tax credit under 45V."},
            {"fuel_vector": "clean_ammonia", "lifecycle_ci_threshold": "< 0.45 kg CO2e / kg H2 eq", "impact_summary": "Synthesis feedstock benefits directly from upstream 45V credits."}
        ]
    },
    {
        "id": "ira_sec_45q_ccus",
        "code_identifier": "26 U.S.C. § 45Q",
        "title": "Inflation Reduction Act Section 45Q: Credit for Carbon Oxide Sequestration",
        "short_title": "IRA § 45Q (Carbon Sequestration Credit)",
        "category": "tax_incentive",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2023,
        "sunset_year": 2033,
        "latest_revision": "IRA 2022 Enhancement",
        "executive_summary": "Provides 12-year refundable production tax credits of up to $85 per metric ton for industrial point-source carbon capture stored in secure geologic formations, and up to $180 per metric ton for Direct Air Capture (DAC) with dedicated geologic storage.",
        "statutory_intent": "Catalyze the commercial deployment of point-source carbon scrubbers and atmospheric carbon dioxide removal across heavy industry, cement, and power generation.",
        "compliance_mandate": "Facilities must capture minimum thresholds (1,000 tons/yr for DAC; 12,500 tons/yr for industrial facilities; 18,750 tons/yr for power plants), secure EPA Class VI injection well permits, and maintain MRV (Monitoring, Reporting, and Verification) under 40 CFR Part 98 Subpart RR.",
        "commercial_friction_points": "Multi-year delays in EPA Class VI geologic injection well approvals (taking 3–6 years in states without primacy); high MRV and long-term liability insurance costs.",
        "associated_incentives": "Direct pay available for the first 5 years of operation for taxable and tax-exempt entities; transferable credits under Section 6418.",
        "official_source_url": "https://www.irs.gov/credits-deductions/clean-vehicle-and-energy-credits-under-the-inflation-reduction-act",
        "tech_links": [
            {"tech_id": "direct_air_capture_dac", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Receives up to $180/ton for dedicated geologic storage and $130/ton for carbon utilization."},
            {"tech_id": "post_combustion_carbon_capture", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Receives $85/ton for industrial point-source capture paired with saline aquifer storage."},
            {"tech_id": "concrete_co2_mineralization", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Qualifies for $60-$130/ton carbon utilization tax credit under Section 45Q(a)(4)."}
        ],
        "fuel_links": []
    },
    {
        "id": "ira_sec_48c_clean_mfg",
        "code_identifier": "26 U.S.C. § 48C",
        "title": "Inflation Reduction Act Section 48C: Qualifying Advanced Energy Project Credit",
        "short_title": "IRA § 48C (Clean Tech Manufacturing Credit)",
        "category": "tax_incentive",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2023,
        "sunset_year": 2026,
        "latest_revision": "$10 Billion Allocation Round",
        "executive_summary": "A competitive 30% investment tax credit administered jointly by the DOE and IRS to re-equip, expand, or establish domestic manufacturing facilities for clean energy hardware, critical minerals, electrolyzers, batteries, and carbon capture components.",
        "statutory_intent": "Re-shore critical clean tech supply chains, reduce dependence on foreign manufacturing, and revitalize historic energy communities.",
        "compliance_mandate": "Requires competitive application approval from the DOE (evaluating commercial viability, GHG reduction, and domestic supply chain impact) plus prevailing wage and apprenticeship requirements; $4B ring-fenced for designated Energy Communities.",
        "commercial_friction_points": "High application oversubscription (>7x oversubscribed); tight 2-year statutory construction milestone clock.",
        "associated_incentives": "Provides upfront 30% capital expenditure offset for clean tech factories and recycling facilities.",
        "official_source_url": "https://www.energy.gov/infrastructure/qualifying-advanced-energy-project-credit-48c-program",
        "tech_links": [
            {"tech_id": "perovskite_tandem_solar", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "30% CAPEX tax credit for establishing domestic tandem solar cell and wafer manufacturing lines."},
            {"tech_id": "battery_scrap_hydrometallurgy", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Directly subsidizes domestic critical mineral recycling and cathode active material refining plants."},
            {"tech_id": "iron_air_battery", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Offloaded factory scaling CAPEX for Form Energy's multi-day battery gigafactories."}
        ],
        "fuel_links": []
    },
    {
        "id": "ira_sec_45x_mfg_ptc",
        "code_identifier": "26 U.S.C. § 45X",
        "title": "Inflation Reduction Act Section 45X: Advanced Manufacturing Production Credit",
        "short_title": "IRA § 45X (Advanced Manufacturing PTC)",
        "category": "tax_incentive",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2023,
        "sunset_year": 2032,
        "latest_revision": "Treasury Final Rules (2024)",
        "executive_summary": "An uncapped, volume-based federal production tax credit paid per unit of eligible clean energy component produced in the United States, including battery cells ($35/kWh), battery modules ($10/kWh), solar wafers ($12/m²), solar cells ($0.04/W), and critical minerals (10% of production cost).",
        "statutory_intent": "Guarantee long-term operational profitability for domestic clean energy component manufacturers to compete with state-subsidized foreign producers.",
        "compliance_mandate": "Components must be produced in the United States and sold to an unrelated third party; producers must maintain detailed metallurgical and bill-of-materials traceability.",
        "commercial_friction_points": "Phases down by 25% annually beginning in 2030 (75% in 2030, 50% in 2031, 25% in 2032, 0% thereafter).",
        "associated_incentives": "Up to $45/kWh combined for domestic battery cell + module production; 10% production cost refund for refining critical minerals.",
        "official_source_url": "https://www.irs.gov/credits-deductions/advanced-manufacturing-production-credit",
        "tech_links": [
            {"tech_id": "solid_state_lithium_battery", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Provides $35/kWh cell credit + $10/kWh module credit for domestic solid-state production."},
            {"tech_id": "direct_lithium_extraction_dle", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "10% production cost credit for refining battery-grade lithium carbonate and hydroxide."},
            {"tech_id": "perovskite_tandem_solar", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Eligible for wafer, cell, and module production subsidies."}
        ],
        "fuel_links": []
    },
    {
        "id": "doe_justice40_mandate",
        "code_identifier": "EO 14008 / Justice40",
        "title": "Federal Justice40 Initiative Mandate for Clean Energy Programs",
        "short_title": "Justice40 Initiative (Community Benefits Mandate)",
        "category": "federal_mandate",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2021,
        "latest_revision": "DOE Community Benefits Plan (CBP) v3",
        "executive_summary": "Executive Order directing that at least 40% of the overall benefits of federal climate, clean energy, and environmental investments flow to disadvantaged communities (DACs) historically overburdened by pollution.",
        "statutory_intent": "Ensure equitable wealth building, local job creation, public health improvements, and environmental remediation in frontline communities.",
        "compliance_mandate": "All major DOE funding opportunities (FOAs), Regional Clean Hydrogen Hubs, DAC Hubs, and OCED grants mandate a scored Community Benefits Plan (CBP) accounting for 20% of the total merit evaluation score.",
        "commercial_friction_points": "Applicants must negotiate enforceable Community Project Agreements (CPAs) and project labor agreements (PLAs) with local labor unions and civic groups prior to award finalization.",
        "associated_incentives": "A strong Community Benefits Plan is mandatory for winning competitive multi-million-dollar federal clean energy grants.",
        "official_source_url": "https://www.energy.gov/diversity/justice40-initiative",
        "tech_links": [
            {"tech_id": "direct_air_capture_dac", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Regional DAC Hub proposals require comprehensive Justice40 air quality monitoring and community co-ownership."},
            {"tech_id": "microgrid_black_start", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Resilience microgrids deployed in disadvantaged communities receive prioritized federal scoring."},
            {"tech_id": "district_thermal_energy_networks", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Prioritizes thermal network deployment in low-to-moderate income (LMI) housing districts."}
        ],
        "fuel_links": []
    },
    {
        "id": "baba_build_america_2021",
        "code_identifier": "BABA / 2 CFR 184",
        "title": "Build America, Buy America Act Requirements for Federal Financial Assistance",
        "short_title": "BABA (Domestic Sourcing Mandate)",
        "category": "federal_mandate",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2022,
        "latest_revision": "OMB 2 CFR Part 184 (2023)",
        "executive_summary": "Statutory domestic procurement mandate requiring that all infrastructure projects funded by federal financial assistance use 100% domestic iron, steel, construction materials, and manufactured products produced in the United States.",
        "statutory_intent": "Strengthen national industrial manufacturing and prevent federal grant dollars from flowing to foreign component manufacturers.",
        "compliance_mandate": "Iron and steel must be melted and poured in the US; manufactured products must have >55% of the total component cost manufactured in the US, unless an explicit public interest or non-availability waiver is approved.",
        "commercial_friction_points": "High domestic supply chain constraints for specialized power transformers, high-voltage subsea cables, and advanced electrolyzer membranes; waiver approvals can take 6–12 months.",
        "associated_incentives": "Essential for federal grant disbursement compliance across DOE, EPA, DOT, and HUD.",
        "official_source_url": "https://www.whitehouse.gov/omb/management/made-in-america/build-america-buy-america-act-provisions/",
        "tech_links": [
            {"tech_id": "deepwater_floating_wind", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Steel hulls and mooring chains in federally funded port facilities must satisfy BABA rules."},
            {"tech_id": "hvdc_transmission_links", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Requires domestic sourcing for high-voltage DC converter transformers and steel towers."},
            {"tech_id": "megawatt_charging_systems", "relevance_type": "mandatory_testing", "compliance_impact": "cost_driver", "impact_summary": "NEVI-funded charging enclosures and power electronics must comply with FHWA Buy America waiver rules."}
        ],
        "fuel_links": []
    },

    # =========================================================================
    # 4. STATE CLIMATE ACTS, BUILDING CODES, SITING & LOCAL MUNICIPAL POLICIES
    # =========================================================================
    {
        "id": "ny_clcpa_2019",
        "code_identifier": "NY CLCPA / ECL Art. 75",
        "title": "New York Climate Leadership and Community Protection Act",
        "short_title": "NY CLCPA (New York Climate Act)",
        "category": "state_statute",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2019,
        "sunset_year": 2050,
        "latest_revision": "Chapter 106 of the Laws of 2019",
        "executive_summary": "New York State's landmark climate statute mandating 70% renewable electricity by 2030, 100% zero-emission electricity by 2040, 6,000 MW of energy storage by 2030, 10,000 MW of distributed solar by 2030, 9,000 MW of offshore wind by 2035, and an 85% economy-wide GHG reduction by 2050.",
        "statutory_intent": "Position New York as a national clean energy leader while directing at least 35% (goal of 40%) of clean energy investments to disadvantaged communities (ECL § 75-0117 / Justice40).",
        "compliance_mandate": "All state agency decisions, air permits, and grants (DEC, DPS, NYSERDA, NYPA, ESD) must comply with Section 7(2) and 7(3) consistency reviews to prove projects do not disproportionately burden disadvantaged communities.",
        "commercial_friction_points": "Aggressive 2030 targets require unprecedented deployment velocities for transmission, offshore wind, and building electrification amid supply chain inflation.",
        "associated_incentives": "Drives billions of dollars in state procurement through NYSERDA Tier 1, Tier 2, Tier 4 RECs, Offshore Wind OREC, and Energy Storage Index REC contracts.",
        "official_source_url": "https://climate.ny.gov/",
        "tech_links": [
            {"tech_id": "iron_air_battery", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Directly backed by NY's expanded 6 GW by 2030 energy storage target."},
            {"tech_id": "district_thermal_energy_networks", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Statutory driver for NY Utility Thermal Energy Networks and Jobs Act pilot programs."},
            {"tech_id": "deepwater_floating_wind", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Fuels NY's 9,000 MW offshore wind procurement mandates."},
            {"tech_id": "perovskite_tandem_solar", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Supported by NY 10 GW distributed solar mandate."}
        ],
        "fuel_links": []
    },
    {
        "id": "nyc_local_law_97_2019",
        "code_identifier": "NYC Local Law 97 / Admin Code Art. 320",
        "title": "New York City Local Law 97: Building Energy and Carbon Emissions Limits",
        "short_title": "NYC LL97 (Building Carbon Caps & Penalties)",
        "category": "emissions_standard",
        "jurisdiction_level": "municipal",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2019,
        "sunset_year": 2050,
        "latest_revision": "2024 Compliance Rules (1 RCNY 103-14)",
        "executive_summary": "NYC's flagship municipal building decarbonization statute setting strict carbon emissions caps on all commercial and multifamily buildings greater than 25,000 gross square feet across the five boroughs.",
        "statutory_intent": "Achieve a 40% reduction in NYC building emissions by 2030 and 80% by 2050, forcing the phaseout of fossil heating boilers in favor of heat pumps and deep efficiency.",
        "compliance_mandate": "Covered building owners must submit annual emissions reports stamped by a registered design professional. Buildings exceeding their statutory carbon limit face mandatory civil penalties of $268 per metric ton CO2e over the cap.",
        "commercial_friction_points": "High upfront capital costs for electrifying steam radiator infrastructure in pre-war residential and commercial towers; limited Tier 4 clean electricity transmission into Zone J until 2026-2027.",
        "associated_incentives": "Avoids civil penalties often exceeding $100,000 to $1,000,000/year; stacks with NYSERDA Buildings of Excellence (PON 4333), ConEd Clean Heat commercial incentives (up to $1,500/ton), and NYC C-PACE financing.",
        "official_source_url": "https://www.nyc.gov/site/sustainablebuildings/ll97/local-law-97.page",
        "tech_links": [
            {"tech_id": "cold_climate_heat_pumps", "relevance_type": "mandatory_testing", "compliance_impact": "accelerator_tailwind", "impact_summary": "Primary technological path to eliminate on-site natural gas combustion and avoid LL97 penalties."},
            {"tech_id": "thermal_energy_networks_tens", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Enables multi-building thermal loops to share waste heat and achieve collective LL97 compliance."},
            {"tech_id": "iron_air_battery", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Peak shaving and on-site storage reduce building peak demand and grid emissions intensity."}
        ],
        "fuel_links": []
    },
    {
        "id": "nyc_local_law_92_94_2019",
        "code_identifier": "NYC Local Laws 92 & 94 / Building Code § 1511.2",
        "title": "New York City Local Laws 92 and 94: Sustainable Green and Solar Roof Mandate",
        "short_title": "NYC LL92/94 (Solar & Green Roof Mandate)",
        "category": "building_code",
        "jurisdiction_level": "municipal",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2019,
        "latest_revision": "2022 NYC Construction Codes Update",
        "executive_summary": "Requires that 100% of available rooftop space on new buildings, building additions, or substantial roof deck replacements in NYC be fitted with solar photovoltaic electricity systems, green roof systems, or a combination of both.",
        "statutory_intent": "Maximize distributed urban solar generation and storm-water retention while mitigating the NYC urban heat island effect.",
        "compliance_mandate": "Solar PV installations must generate a minimum of 4 kW or cover the entire contiguous available rooftop zone after FDNY Fire Code access pathway setbacks (6-ft perimeter clear paths).",
        "commercial_friction_points": "Rooftop mechanical equipment (cooling towers, HVAC, elevator bulkheads) and FDNY rooftop fire ventilation clearances limit available contiguous solar area.",
        "associated_incentives": "Eligible for NYC Solar Property Tax Abatement (PTA - 30% over 4 years), NYSERDA NY-Sun MW Block rebates, and VDER Community Solar credits.",
        "official_source_url": "https://www.nyc.gov/site/buildings/industry/sustainable-roofs.page",
        "tech_links": [
            {"tech_id": "perovskite_tandem_solar", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "High-efficiency tandem solar maximizes kW generation on constrained NYC rooftop footprints."},
            {"tech_id": "iron_air_battery", "relevance_type": "safety_siting", "compliance_impact": "cost_driver", "impact_summary": "Paired battery storage must adhere to FDNY rooftop structural and setback codes."}
        ],
        "fuel_links": []
    },
    {
        "id": "nyc_local_law_154_2021",
        "code_identifier": "NYC Local Law 154 / Admin Code § 24-177.1",
        "title": "New York City Local Law 154: All-Electric New Construction Building Code",
        "short_title": "NYC LL154 (All-Electric Building Ban)",
        "category": "building_code",
        "jurisdiction_level": "municipal",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2021,
        "latest_revision": "Phase 1: Jan 1, 2024 (<=7 Stories); Phase 2: July 2, 2027 (All Buildings)",
        "executive_summary": "Groundbreaking municipal statute prohibiting the combustion of fossil fuels (natural gas, heating oil, propane) for space heating, hot water, and cooking in new building construction across New York City.",
        "statutory_intent": "Permanently halt the expansion of gas distribution infrastructure and eliminate indoor combustion pollutants in newly constructed NYC buildings.",
        "compliance_mandate": "Bans fuel combustion in new buildings under 7 stories permitted after Jan 1, 2024; expands to all commercial, institutional, and high-rise residential construction permitted after July 2, 2027.",
        "commercial_friction_points": "Substantial increase in electrical service entrance capacity required from Con Edison; peak winter electrical heating loads in high-density residential towers.",
        "associated_incentives": "Mandatory market demand driver for commercial heat pumps, heat pump water heaters, and thermal storage systems.",
        "official_source_url": "https://www.nyc.gov/site/buildings/industry/all-electric-new-buildings.page",
        "tech_links": [
            {"tech_id": "cold_climate_heat_pumps", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Sole compliant space heating solution for all new residential and commercial construction in NYC."},
            {"tech_id": "thermal_energy_networks_tens", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Provides centralized geothermal loop connectivity for new master-planned developments."}
        ],
        "fuel_links": []
    },
    {
        "id": "nyc_fdny_3rcny_608_01",
        "code_identifier": "FDNY 3 RCNY § 608-01",
        "title": "Fire Department of New York Rule 3 RCNY § 608-01: Outdoor and Indoor Stationary Battery Energy Storage Systems",
        "short_title": "FDNY 3 RCNY 608-01 (NYC BESS Fire Code)",
        "category": "safety_code",
        "jurisdiction_level": "municipal",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2019,
        "latest_revision": "2024 Revision (Rule 608-01)",
        "executive_summary": "The nation's most stringent municipal fire code governing the design, installation, operation, and emergency response planning for stationary battery energy storage systems (BESS) within the five boroughs of New York City.",
        "statutory_intent": "Protect firefighters, dense residential populations, and surrounding infrastructure from explosive off-gassing and catastrophic thermal runaway events.",
        "compliance_mandate": "Mandates certified UL 9540A large-scale fire testing review by the FDNY Technology Management Unit, dedicated dry-pipe water suppression, explosion deflagration venting (NFPA 68/69), continuous gas detection (CO, H2, Lower Flammable Limit), and a certified on-site Certificate of Fitness (COF B-29) supervisor.",
        "commercial_friction_points": "Approval timelines from the FDNY Bureau of Fire Prevention average 12 to 24 months; strict outdoor setback requirements (10 ft from lot lines, 20 ft from doors/windows) make rooftop and indoor urban siting difficult for traditional lithium-ion chemistries.",
        "associated_incentives": "Required to unlock the lucrative New York City capacity market and ConEd Value of Distributed Energy Resources (VDER) revenue streams.",
        "official_source_url": "https://www.nyc.gov/site/fdny/codes/fire-code/fire-code.page",
        "tech_links": [
            {"tech_id": "iron_air_battery", "relevance_type": "safety_siting", "compliance_impact": "accelerator_tailwind", "impact_summary": "Aqueous chemistry significantly accelerates FDNY safety approvals by avoiding flammable gas venting."},
            {"tech_id": "vanadium_redox_flow", "relevance_type": "safety_siting", "compliance_impact": "accelerator_tailwind", "impact_summary": "Non-flammable electrolyte eliminates thermal runaway risk under FDNY Rule § 608-01."},
            {"tech_id": "sodium_ion_battery", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Requires full FDNY TMU review and UL 9540A testing before NYC deployment."}
        ],
        "fuel_links": []
    },
    {
        "id": "nys_rptl_487_tax_exemption",
        "code_identifier": "NY RPTL § 487",
        "title": "New York State Real Property Tax Law § 487: Renewable Energy Systems Tax Exemption",
        "short_title": "NYS RPTL § 487 (15-Year Property Tax Exemption & PILOT)",
        "category": "tax_incentive",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 1977,
        "sunset_year": 2030,
        "latest_revision": "Amended 2022 (Extended to Jan 1, 2030)",
        "executive_summary": "Provides a statutory 15-year real property tax exemption for the value added by qualified solar, wind, battery energy storage, microgrid, geothermal, and fuel cell installations across New York State.",
        "statutory_intent": "Prevent prohibitive property tax assessments from rendering clean energy infrastructure projects economically unviable.",
        "compliance_mandate": "Applies automatically across NYS unless a local taxing jurisdiction (town, county, school district) proactively opts out by local law. If opted out, developers negotiate a standardized Payment in Lieu of Taxes (PILOT) with local Industrial Development Agencies (IDAs).",
        "commercial_friction_points": "Local upstate municipal opt-outs create fragmented county-by-county tax liability risks and extended IDA PILOT negotiations.",
        "associated_incentives": "Saves commercial clean energy projects $20,000 to $150,000/MW-year in municipal real property tax liabilities.",
        "official_source_url": "https://www.tax.ny.gov/research/property/assess/manuals/vol4/pt1/sec4_01/sec487.htm",
        "tech_links": [
            {"tech_id": "perovskite_tandem_solar", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Exempts commercial solar generation assets from local property tax assessment increases."},
            {"tech_id": "iron_air_battery", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Standalone and paired storage qualify for 15-year tax exemption or standardized PILOT."}
        ],
        "fuel_links": []
    },
    {
        "id": "nys_vder_value_stack_2017",
        "code_identifier": "NY PSC Case 15-E-0751",
        "title": "New York State Value of Distributed Energy Resources (VDER) Value Stack Tariff",
        "short_title": "NYS VDER (Value Stack Compensation Mechanism)",
        "category": "interconnection_rule",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2017,
        "latest_revision": "PSC VDER 2.0 Order 2023",
        "executive_summary": "New York's market-leading compensation methodology unbundling distributed energy values into granular hourly revenue components: Energy Value (LMP), Capacity Value (ICAP), Environmental Value (E-Value ~3.1¢/kWh), Demand Reduction Value (DRV), and Locational System Relief Value (LSRV).",
        "statutory_intent": "Transition distributed generation from flat net metering to location-specific, time-varying grid value compensation.",
        "compliance_mandate": "All commercial, industrial, and Community Distributed Generation (CDG) solar, storage, and fuel cell projects must interconnect under utility VDER tariff schedules (ConEd, National Grid, Central Hudson, NYSEG, RG&E, PSEG LI).",
        "commercial_friction_points": "ICAP capacity forecast volatility and complex monthly utility billing reconciliation; DRV revenue requires dispatching precisely during top 10 summer peak network hours.",
        "associated_incentives": "Provides guaranteed 25-year revenue stacking with fixed 20-year Environmental Value (E-Value) tranche lock-ins for community solar and storage.",
        "official_source_url": "https://www.nyserda.ny.gov/All-Programs/NY-Sun/Contractors/Value-of-Distributed-Energy-Resources",
        "tech_links": [
            {"tech_id": "perovskite_tandem_solar", "relevance_type": "interconnection", "compliance_impact": "accelerator_tailwind", "impact_summary": "Community solar projects monetize E-Value and ICAP capacity via VDER."},
            {"tech_id": "iron_air_battery", "relevance_type": "interconnection", "compliance_impact": "accelerator_tailwind", "impact_summary": "Dispatches during utility DRV/LSRV call windows to capture peak locational capacity premiums."}
        ],
        "fuel_links": []
    },
    {
        "id": "nys_clean_heat_program_2020",
        "code_identifier": "NY PSC Case 18-M-0084",
        "title": "New York State Clean Heat Statewide Heat Pump Incentive Framework",
        "short_title": "NYS Clean Heat (Statewide Heat Pump Incentives)",
        "category": "tax_incentive",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2020,
        "latest_revision": "2024 Program Implementation Manual",
        "executive_summary": "A multi-billion dollar statewide ratepayer-funded incentive program operated jointly by Con Edison, National Grid, Central Hudson, NYSEG, RG&E, and PSEG Long Island to rapidly scale clean electrified heating.",
        "statutory_intent": "Accelerate building electrification to meet the CLCPA mandate of 1 to 2 million electrified homes by 2030.",
        "compliance_mandate": "Participating contractors must be certified NYS Clean Heat Installers and install NEEP-listed cold-climate air-source heat pumps (ccASHP) or AHRI-certified ground-source heat pumps (GSHP) with full heating capacity down to 5°F.",
        "commercial_friction_points": "Upfront electrical service panel upgrade bottlenecks and contractor labor capacity constraints across downstate and upstate regions.",
        "associated_incentives": "Provides up to $10,000 per residential installation and up to $1,500/ton for commercial installations. Stacks with NYS 25% Residential Geothermal Tax Credit (Tax Law § 606(g-1)) and federal IRA 25C/179D tax deductions.",
        "official_source_url": "https://cleanheat.ny.gov/",
        "tech_links": [
            {"tech_id": "cold_climate_heat_pumps", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Primary point-of-sale rebate mechanism funding cold-climate air-source and geothermal heat pumps."},
            {"tech_id": "thermal_energy_networks_tens", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Large commercial geothermal loop heat pump installations qualify for customized multi-million dollar utility rebates."}
        ],
        "fuel_links": []
    },
    {
        "id": "nys_utility_thermal_energy_networks_2022",
        "code_identifier": "NY Ch. 375, L. 2022 / PSC Case 22-M-0149",
        "title": "New York Utility Thermal Energy Networks and Jobs Act",
        "short_title": "NY UTENJA (Utility Geothermal Thermal Networks Act)",
        "category": "state_statute",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2022,
        "latest_revision": "PSC Phase II Regulatory Framework 2024",
        "executive_summary": "Landmark legislation mandating that all seven major investor-owned gas and electric utilities in New York State develop and construct pilot Thermal Energy Networks (district geothermal heating and cooling loops).",
        "statutory_intent": "Provide a just transition for union gas utility pipefitters while decarbonizing entire neighborhood building blocks simultaneously through shared geothermal loops.",
        "compliance_mandate": "Requires each utility (ConEd, National Grid, Central Hudson, NYSEG, RG&E, O&R, Orange & Rockland) to submit detailed engineering proposals for 1 to 2 pilot thermal networks, with at least one in a Disadvantaged Community (DAC).",
        "commercial_friction_points": "Subsurface right-of-way congestion under urban streets (sewers, subways, electrical conduits) and multi-property easement negotiations.",
        "associated_incentives": "Utility rate-based capital expenditure framework with full cost-recovery approved by the NY PSC, unlocking hundreds of millions in infrastructure contracts.",
        "official_source_url": "https://dps.ny.gov/utility-thermal-energy-network-pilot-projects",
        "tech_links": [
            {"tech_id": "thermal_energy_networks_tens", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Direct statutory creation of the utility thermal energy network asset class in New York."},
            {"tech_id": "cold_climate_heat_pumps", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Water-to-water and water-to-air heat pumps serve as building-side interconnection nodes on the ambient loops."}
        ],
        "fuel_links": []
    },
    {
        "id": "nys_all_electric_building_act_2023",
        "code_identifier": "NY Ch. 56, L. 2023 / Energy Law § 11-104",
        "title": "New York State All-Electric Building Act",
        "short_title": "NYS All-Electric Building Act (Statewide Fossil Ban)",
        "category": "building_code",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2023,
        "latest_revision": "Effective Dec 31, 2025 (Low-Rise) / Dec 31, 2028 (High-Rise)",
        "executive_summary": "The first statewide statute in the United States prohibiting fossil-fuel equipment (gas boilers, furnaces, water heaters, stoves) in new building construction.",
        "statutory_intent": "Eliminate fossil fuel combustion infrastructure at the point of construction across all 62 New York counties.",
        "compliance_mandate": "State Uniform Code prohibits issuing building permits for new residential and commercial structures under 7 stories with fossil fuel infrastructure after Dec 31, 2025; extends to commercial/high-rise buildings over 7 stories after Dec 31, 2028.",
        "commercial_friction_points": "Requires all new building designs to incorporate all-electric heat pump systems and high-efficiency induction cooking; grid interconnection review timelines for new distribution capacity.",
        "associated_incentives": "Direct statutory accelerator for heat pump manufacturers, energy recovery ventilators (ERVs), and building envelope insulation suppliers.",
        "official_source_url": "https://www.nysenate.gov/legislation/laws/ENG/11-104",
        "tech_links": [
            {"tech_id": "cold_climate_heat_pumps", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Mandatory standard for all newly constructed buildings in New York State."}
        ],
        "fuel_links": []
    },
    {
        "id": "nys_zev_advanced_clean_cars_ii",
        "code_identifier": "6 NYCRR Part 218",
        "title": "New York Advanced Clean Cars II & Heavy-Duty Zero-Emission Vehicle Rules",
        "short_title": "NYS ACC II (100% ZEV Sales Mandate)",
        "category": "emissions_standard",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2023,
        "latest_revision": "Adopted by NYS DEC Dec 2022",
        "executive_summary": "Binding state regulation requiring automakers to deliver increasing percentages of zero-emission light-duty vehicles, reaching 100% of new passenger car and light truck sales in NYS by 2035, and 100% medium/heavy-duty zero-emission trucks by 2045.",
        "statutory_intent": "Eliminate tailpipe emissions from the transportation sector, which constitutes the second-largest source of greenhouse gases in New York.",
        "compliance_mandate": "Automakers face escalating zero-emission vehicle credit delivery thresholds: 35% by model year 2026, 68% by 2030, and 100% by 2035. Non-compliant manufacturers face financial penalties and loss of sales authorization.",
        "commercial_friction_points": "Requires massive buildout of public DC Fast Charging depots, megawatt fleet charging systems, and heavy-duty grid interconnection upgrades.",
        "associated_incentives": "Supported by NYSERDA Drive Clean Rebate ($2,000/vehicle), NYS Clean Truck Voucher Program (up to $185,000/truck), and ConEd PowerReady EV Make-Ready incentives.",
        "official_source_url": "https://dec.ny.gov/environmental-protection/air-quality/clean-transportation",
        "tech_links": [
            {"tech_id": "megawatt_charging_systems_mcs", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Essential for commercial fleet depots complying with NYS Heavy-Duty ZEV mandates."},
            {"tech_id": "solid_state_lithium", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Next-gen automotive battery chemistries required for long-range heavy EV compliance."}
        ],
        "fuel_links": []
    },
    {
        "id": "nyc_property_tax_abatement_solar_storage",
        "code_identifier": "NYC RPTL § 499-aaaa through 499-gggg",
        "title": "New York City Solar Electric Generating & Energy Storage System Property Tax Abatement",
        "short_title": "NYC PTA (Solar & Storage Property Tax Abatement)",
        "category": "tax_incentive",
        "jurisdiction_level": "municipal",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2008,
        "sunset_year": 2035,
        "latest_revision": "Extended to 2035 by NY State Legislature (Ch. 347, L. 2023)",
        "executive_summary": "Municipal tax incentive providing a 30% property tax abatement over 4 years (7.5% of total installed equipment cost per year) against New York City real property tax bills for building owners installing solar PV or paired battery energy storage.",
        "statutory_intent": "Encourage private property owners in NYC's dense urban core to invest in rooftop solar and flexible battery storage assets.",
        "compliance_mandate": "Must obtain approved DOB building permits, certified electrical sign-offs, and an approved Department of Finance (DOF) PTA4 application by March 15 of the tax year.",
        "commercial_friction_points": "Abatement is capped at $62,500/year or the total real property taxes due on the building in that tax year.",
        "associated_incentives": "Stacks with federal 30% IRA Investment Tax Credit (§ 48/§ 48E), NYSERDA NY-Sun rebates, and NYS Sales Tax exemption for equipment.",
        "official_source_url": "https://www.nyc.gov/site/finance/benefits/property-benefits-solar.page",
        "tech_links": [
            {"tech_id": "perovskite_tandem_solar", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "30% municipal tax abatement directly offsets installed rooftop solar capital costs in NYC."},
            {"tech_id": "iron_air_battery", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Paired storage systems qualify for the full 4-year 30% tax abatement."}
        ],
        "fuel_links": []
    },
    {
        "id": "coned_powerready_ev_charging",
        "code_identifier": "Con Edison PSC Case 18-E-0138",
        "title": "Con Edison PowerReady EV Infrastructure Make-Ready Program",
        "short_title": "ConEd PowerReady (EV Make-Ready Coverage)",
        "category": "tax_incentive",
        "jurisdiction_level": "state",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2020,
        "latest_revision": "Phase II Program Guidelines 2024",
        "executive_summary": "New York's premier utility EV make-ready incentive program, providing up to 100% coverage for utility-side electrical infrastructure (transformers, service lines) and up to 90%–100% coverage for customer-side electrical equipment (switchgear, conduit, panels) for Level 2 and DC Fast Charging stations in NYC and Westchester.",
        "statutory_intent": "Eliminate electrical interconnection and infrastructure cost barriers for public, commercial fleet, and multi-unit dwelling EV charger installations.",
        "compliance_mandate": "Chargers must be networked (OCPP compliant), metered, and installed by licensed electrical contractors. Projects located in Disadvantaged Communities (DAC) qualify for maximum 100% cost coverage.",
        "commercial_friction_points": "Transformer capacity constraints in congested NYC network distribution vaults can require extended utility engineering lead times.",
        "associated_incentives": "Can save commercial EV charging developers $50,000 to $500,000+ per charging site; stacks with federal 30C Alternative Fuel Refueling tax credit.",
        "official_source_url": "https://www.coned.com/en/our-energy-future/technology-innovation/electric-vehicles/powerready",
        "tech_links": [
            {"tech_id": "megawatt_charging_systems_mcs", "relevance_type": "interconnection", "compliance_impact": "accelerator_tailwind", "impact_summary": "Subsidizes high-power fleet charging electrical switchgear and transformer upgrades."}
        ],
        "fuel_links": []
    },
    {
        "id": "westchester_county_renewable_energy_code",
        "code_identifier": "Westchester County Code Ch. 277",
        "title": "Westchester County Model Solar & Sustainable Energy Ordinance",
        "short_title": "Westchester County Sustainable Energy Standard",
        "category": "building_code",
        "jurisdiction_level": "county",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2021,
        "latest_revision": "Unified Permitting & BESS Siting Update 2024",
        "executive_summary": "County-wide model code establishing unified permitting standards for rooftop solar, canopies, and commercial battery storage across Westchester's 48 municipal jurisdictions, coupled with the Westchester Power 100% renewable Community Choice Aggregation (CCA) default supply.",
        "statutory_intent": "Streamline clean energy deployment timelines and provide standardized local zoning across suburban municipal jurisdictions.",
        "compliance_mandate": "Adopting municipalities utilize the NYS Unified Solar Permit (USP) with guaranteed 14-day administrative review timelines for residential and small commercial systems.",
        "commercial_friction_points": "Local zoning variance requirements for ground-mounted solar arrays and standalone battery storage enclosures in residential-adjacent zones.",
        "associated_incentives": "Enables distributed clean generation to access Con Edison / NYSEG Westchester territory VDER locational relief values (LSRV).",
        "official_source_url": "https://planning.westchestergov.com/sustainability",
        "tech_links": [
            {"tech_id": "perovskite_tandem_solar", "relevance_type": "safety_siting", "compliance_impact": "accelerator_tailwind", "impact_summary": "Fast-track 14-day administrative permitting under Westchester unified code."}
        ],
        "fuel_links": []
    },
    {
        "id": "long_island_lipa_clean_energy_tariff",
        "code_identifier": "LIPA Tariff for Electric Service Schedule 2024",
        "title": "Long Island Power Authority Clean Energy & Storage Tariff",
        "short_title": "LIPA Clean Energy & Storage Tariff",
        "category": "interconnection_rule",
        "jurisdiction_level": "county",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2018,
        "latest_revision": "2024 LIPA Tariff",
        "executive_summary": "The regulatory tariff governing distributed solar, offshore wind interconnections, and commercial battery storage across Nassau and Suffolk Counties on Long Island.",
        "statutory_intent": "Meet Long Island's specific clean energy and grid resiliency targets while managing local sub-transmission capacity constraints.",
        "compliance_mandate": "Projects interconnecting to the PSEG Long Island grid receive VDER Value Stack compensation and must participate in LIPA's Smart Inverter and Dynamic Load Management (DLM) dispatch requirements.",
        "commercial_friction_points": "Substation interconnection headroom limitations in eastern Suffolk County; strict Nassau and Suffolk IDA PILOT negotiation schedules.",
        "associated_incentives": "Offers PSEG Long Island Super-Peak Energy Storage incentives (up to $250/kWh) and commercial solar incentives through NY-Sun Long Island region blocks.",
        "official_source_url": "https://www.lipower.org/about-us/tariff/",
        "tech_links": [
            {"tech_id": "iron_air_battery", "relevance_type": "interconnection", "compliance_impact": "accelerator_tailwind", "impact_summary": "Provides long-duration grid stabilization for Long Island eastern transmission bottlenecks."},
            {"tech_id": "deepwater_floating_wind", "relevance_type": "interconnection", "compliance_impact": "accelerator_tailwind", "impact_summary": "Governs offshore wind points of interconnection into Long Island substations."}
        ],
        "fuel_links": []
    },
    {
        "id": "buffalo_green_code_energy_standard",
        "code_identifier": "Buffalo Unified Development Ordinance § 511-1",
        "title": "City of Buffalo Green Code Energy & Climate Standard",
        "short_title": "Buffalo Green Code (Commercial Energy Standard)",
        "category": "building_code",
        "jurisdiction_level": "municipal",
        "jurisdiction_state": "NY",
        "status": "active",
        "effective_year": 2017,
        "latest_revision": "2023 Climate Action Update",
        "executive_summary": "Comprehensive municipal development code for the City of Buffalo requiring commercial building energy benchmarking, cold-climate heat pump installation standards, and renewable microgrid zoning in Western New York.",
        "statutory_intent": "Drive urban building efficiency, reduce winter heating energy burdens, and support clean tech manufacturing redevelopment along the Great Lakes industrial corridor.",
        "compliance_mandate": "Mandatory annual energy and water benchmarking reporting for commercial buildings over 50,000 sq ft via ENERGY STAR Portfolio Manager; zoning fast-tracks for rooftop solar and EV charging infrastructure.",
        "commercial_friction_points": "High thermal envelope retrofit costs in Buffalo's legacy architectural and industrial building stock experiencing extreme winter freeze events.",
        "associated_incentives": "Stacks with National Grid Upstate Clean Heat incentives, NYSERDA Empire Building Challenge grants, and Western New York Power Proceed allocations from NYPA hydro power.",
        "official_source_url": "https://www.buffalony.gov/1224/Buffalo-Green-Code",
        "tech_links": [
            {"tech_id": "cold_climate_heat_pumps", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Mandatory cold-climate performance standards tailored to Western NY winter sub-zero temperatures."}
        ],
        "fuel_links": []
    },
    {
        "id": "ca_sb_100_2018",
        "code_identifier": "CA SB 100",
        "title": "California 100 Percent Clean Energy Act of 2018",
        "short_title": "CA SB 100 (California Clean Grid Act)",
        "category": "state_statute",
        "jurisdiction_level": "state",
        "jurisdiction_state": "CA",
        "status": "active",
        "effective_year": 2018,
        "sunset_year": 2045,
        "latest_revision": "SB 100 Joint Agency Report",
        "executive_summary": "Statutory mandate requiring California to supply 60% of all retail electricity from eligible renewable energy resources by 2030, and 100% zero-carbon electricity to retail end-use customers by 2045.",
        "statutory_intent": "Accelerate the total decarbonization of California's electric grid while maintaining reliability and affordable consumer rates.",
        "compliance_mandate": "The California Public Utilities Commission (CPUC), California Energy Commission (CEC), and California Air Resources Board (CARB) must enforce compliance via utility Integrated Resource Plans (IRP) and Renewable Portfolio Standard (RPS) procurement mandates.",
        "commercial_friction_points": "Requires massive additions of long-duration energy storage (LDES) and firm clean power (geothermal, offshore wind) to maintain grid reliability during multi-day renewable lulls (dunkelflaute).",
        "associated_incentives": "Fuels multi-billion-dollar annual clean energy solicitations through the CEC Electric Program Investment Charge (EPIC) and CPUC 11.5 GW clean procurement orders.",
        "official_source_url": "https://www.energy.gov/sites/default/files/2021-03/2021_sb_100_joint_agency_report.pdf",
        "tech_links": [
            {"tech_id": "deepwater_floating_wind", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Key resource to achieve California's 25 GW by 2045 offshore wind planning goal under SB 100."},
            {"tech_id": "iron_air_battery", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Supported by CPUC mandates for multi-day long-duration energy storage."},
            {"tech_id": "egs_geothermal", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Provides firm baseload zero-carbon capacity required by CPUC Mid-Term Reliability orders."}
        ],
        "fuel_links": []
    },
    {
        "id": "ca_title_24_2022",
        "code_identifier": "CA Title 24, Part 6",
        "title": "California Building Energy Efficiency Standards",
        "short_title": "CA Title 24 (Building Energy Code)",
        "category": "state_statute",
        "jurisdiction_level": "state",
        "jurisdiction_state": "CA",
        "status": "active",
        "effective_year": 2023,
        "latest_revision": "2022 Standards (Enforced 2023–2026)",
        "executive_summary": "The nation's most progressive building energy code, establishing mandatory heat pump baselines for space and water heating in new residential and commercial construction, solar PV + storage readiness, and strict ventilation standards.",
        "statutory_intent": "Eliminate direct fossil fuel combustion in new buildings and maximize on-site solar generation and demand flexibility.",
        "compliance_mandate": "Establishes heat pumps as the prescriptive baseline for space heating or water heating in new homes; requires commercial buildings to install solar PV and battery storage sized to offset daytime electric loads.",
        "commercial_friction_points": "High upfront electrical panel and transformer upgrade costs in existing building retrofits.",
        "associated_incentives": "Creates guaranteed statewide demand for cold-climate heat pumps, building-integrated PV, and residential battery storage systems.",
        "official_source_url": "https://www.energy.ca.gov/programs-and-topics/programs/building-energy-efficiency-standards",
        "tech_links": [
            {"tech_id": "cold_climate_heat_pumps", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Title 24 establishes heat pumps as the prescriptive baseline for California building permits."},
            {"tech_id": "perovskite_tandem_solar", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Mandatory solar requirements on new commercial construction create a massive captive market."},
            {"tech_id": "aerogel_superinsulation", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "High R-value envelope requirements favor ultra-thin aerogel building insulation."}
        ],
        "fuel_links": []
    },

    # =========================================================================
    # 5. EMISSIONS, LOW-CARBON FUELS & WASTE STANDARDS
    # =========================================================================
    {
        "id": "ca_lcfs_carb_2024",
        "code_identifier": "CARB LCFS",
        "title": "California Low Carbon Fuel Standard",
        "short_title": "CA LCFS (Low Carbon Fuel Standard)",
        "category": "emissions_standard",
        "jurisdiction_level": "state",
        "jurisdiction_state": "CA",
        "status": "active",
        "effective_year": 2011,
        "sunset_year": 2045,
        "latest_revision": "2024 Amendments (30% CI reduction by 2030)",
        "executive_summary": "A market-based regulatory program administered by CARB designed to decrease the Carbon Intensity (CI) of California's transportation fuel pool by at least 30% by 2030 and 90% by 2045 compared to a 2010 baseline.",
        "statutory_intent": "Displace petroleum fuels by generating tradeable LCFS credits for low-carbon fuels (SAF, green hydrogen, renewable diesel, RNG, EV charging electricity).",
        "compliance_mandate": "Fuel producers and importers whose fuels exceed the annual CI benchmark must purchase LCFS deficit credits; clean fuel producers generate tradeable credits determined by CA-GREET 4.0 lifecycle carbon scoring.",
        "commercial_friction_points": "Credit price volatility ($60 to $200+/ton); CARB phaseout of avoided methane crediting for dairy biomethane by 2040.",
        "associated_incentives": "Generates substantial revenue premiums: e.g., negative CI fuels like dairy RNG and electrolytic hydrogen can earn $1.50 to $3.00+ per gallon equivalent in LCFS credits.",
        "official_source_url": "https://ww2.arb.ca.gov/our-work/programs/low-carbon-fuel-standard",
        "tech_links": [
            {"tech_id": "sustainable_aviation_fuel_saf", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "SAF qualifies for maximum LCFS credit generation and opt-in airline accounting."},
            {"tech_id": "anaerobic_digestion_rng", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Dairy RNG achieves negative Carbon Intensity (-150 to -350 gCO2e/MJ), yielding peak LCFS value."},
            {"tech_id": "pem_electrolyzer", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Electrolytic hydrogen dispensed to fuel cell EVs generates high-value LCFS credits."}
        ],
        "fuel_links": [
            {"fuel_vector": "saf", "lifecycle_ci_threshold": "< 50 gCO2e / MJ", "impact_summary": "Generates tradeable LCFS credits proportional to lifecycle CI reduction vs fossil jet fuel."},
            {"fuel_vector": "rng", "lifecycle_ci_threshold": "< 0 gCO2e / MJ (Negative CI)", "impact_summary": "Earns premium credit prices under CA-GREET avoided methane accounting."},
            {"fuel_vector": "green_hydrogen", "lifecycle_ci_threshold": "< 30 gCO2e / MJ", "impact_summary": "Eligible for transportation dispensing credits and zero-emission vehicle infrastructure capacity credits."}
        ]
    },
    {
        "id": "epa_caa_sec_111_ghg",
        "code_identifier": "EPA Clean Air Act § 111",
        "title": "EPA New Source Performance Standards and Emission Guidelines for Greenhouse Gases from Fossil Fuel-Fired Electric Generating Units",
        "short_title": "EPA CAA § 111 (Power Plant Carbon Rule)",
        "category": "emissions_standard",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2024,
        "sunset_year": 2040,
        "latest_revision": "Final Rule (April 2024)",
        "executive_summary": "Federal Clean Air Act regulations setting carbon dioxide emission limits for new and existing baseload natural gas and coal-fired power plants based on the Best System of Emission Reduction (BSER), identifying 90% Carbon Capture and Storage (CCS) and high-blend clean hydrogen co-firing as established control technologies.",
        "statutory_intent": "Reduce power sector greenhouse gas emissions by 1.38 billion metric tons through 2047 and force decarbonization of long-run baseload thermal generation.",
        "compliance_mandate": "Long-term baseload natural gas combined-cycle (NGCC) plants operating past 2039 must achieve a 90% CO2 capture rate via CCS by 2032, or retire early.",
        "commercial_friction_points": "High commercial CAPEX for utility-scale CCS retrofits; legal challenges from multi-state coalitions regarding BSER technological readiness.",
        "associated_incentives": "Massive market pull for commercial carbon capture scrubbers, deep geologic storage, and grid-scale hydrogen turbines.",
        "official_source_url": "https://www.epa.gov/stationary-sources-air-pollution/greenhouse-gas-standards-and-guidelines-fossil-fuel-fired-power",
        "tech_links": [
            {"tech_id": "post_combustion_carbon_capture", "relevance_type": "mandatory_testing", "compliance_impact": "critical_gate", "impact_summary": "Designated by EPA as the primary BSER technology for baseload fossil power plants."},
            {"tech_id": "pem_electrolyzer", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Clean hydrogen co-firing (>30% by volume) serves as a key compliance path."},
            {"tech_id": "salt_cavern_h2_storage", "relevance_type": "market_incentive", "compliance_impact": "accelerator_tailwind", "impact_summary": "Provides the seasonal fuel storage required to power hydrogen-fired peaking turbines."}
        ],
        "fuel_links": [
            {"fuel_vector": "green_hydrogen", "lifecycle_ci_threshold": "< 0.45 kg CO2e / kg H2", "impact_summary": "Co-firing compliance path for thermal power generation."}
        ]
    },
    {
        "id": "epa_class_vi_uic",
        "code_identifier": "EPA 40 CFR Part 146",
        "title": "EPA Underground Injection Control (UIC) Program: Class VI Geologic Sequestration Wells",
        "short_title": "EPA Class VI Well Permitting",
        "category": "environmental_permitting",
        "jurisdiction_level": "federal",
        "jurisdiction_state": "US",
        "status": "active",
        "effective_year": 2010,
        "latest_revision": "Guidance on Primacy & State Delegations (2023)",
        "executive_summary": "Federal environmental permitting standard under the Safe Drinking Water Act (SDWA) regulating the site characterization, construction, operation, testing, and post-injection site care of deep injection wells used to permanently sequester supercritical CO2 in deep saline formations.",
        "statutory_intent": "Ensure permanent carbon storage while preventing contamination of Underground Sources of Drinking Water (USDWs) and induced seismic events.",
        "compliance_mandate": "Operators must model an Area of Review (AoR), maintain continuous pressure monitoring, construct corrosion-resistant injection tubing, conduct seismic surveys, and maintain 50-year post-injection monitoring and financial assurance bonds.",
        "commercial_friction_points": "Lengthy federal EPA permit review timelines (averaging 36 to 60 months per well); high legal liability for long-term subsurface plume migration.",
        "associated_incentives": "A certified Class VI permit is legally required to claim the $85–$180/ton tax credits under Section 45Q.",
        "official_source_url": "https://www.epa.gov/uic/class-vi-wells-used-geologic-sequestration-carbon-dioxide",
        "tech_links": [
            {"tech_id": "direct_air_capture_dac", "relevance_type": "safety_siting", "compliance_impact": "critical_gate", "impact_summary": "All permanent DAC sequestration in saline aquifers requires a Class VI permit."},
            {"tech_id": "post_combustion_carbon_capture", "relevance_type": "safety_siting", "compliance_impact": "critical_gate", "impact_summary": "Class VI approval is the ultimate gating factor for point-source CCS project finance."}
        ],
        "fuel_links": []
    }
]


TECH_ID_ALIASES = {
    "solid_state_lithium_battery": "solid_state_lithium",
    "microgrid_black_start": "black_start_microgrids",
    "grid_forming_inverters": "advanced_inverters_grid_forming",
    "v2g_bidirectional_chargers": "megawatt_charging_systems_mcs",
    "derms_vpp_orchestration": "vpp_derms_orchestration",
    "pem_electrolyzer": "pem_soec_electrolyzers",
    "soec_solid_oxide_electrolyzer": "pem_soec_electrolyzers",
    "salt_cavern_h2_storage": "underground_hydrogen_storage",
    "megawatt_charging_systems": "megawatt_charging_systems_mcs",
    "megawatt_charging_system_mcs": "megawatt_charging_systems_mcs",
    "silicon_anode_batteries": "solid_state_lithium",
    "dynamic_line_rating_gets": "grid_enhancing_technologies",
    "deepwater_floating_wind": "floating_offshore_wind",
    "egs_geothermal": "enhanced_geothermal_egs",
    "hvdc_transmission_links": "hvdc_transmission_interconnects",
    "ccashp_cold_climate_heat_pumps": "cold_climate_heat_pumps",
    "tens_district_geothermal": "thermal_energy_networks_tens",
    "district_thermal_energy_networks": "thermal_energy_networks_tens",
    "direct_air_capture": "direct_air_capture_dac",
    "post_combustion_carbon_capture": "direct_air_capture_dac",
    "concrete_co2_mineralization": "direct_air_capture_dac",
    "h2_dri_green_steel": "green_steel_h2_dri",
    "direct_lithium_extraction": "direct_lithium_extraction_dle",
    "battery_scrap_hydrometallurgy": "closed_loop_battery_recycling",
    "smr_gen4_reactors": "smr_advanced_nuclear",
    "superhot_rock": "superhot_rock_geothermal",
    "advanced_biofuels_saf": "sustainable_aviation_fuels",
    "sustainable_aviation_fuel_saf": "sustainable_aviation_fuels",
    "rng_anaerobic_digestion": "anaerobic_digestion_biomethane",
    "anaerobic_digestion_rng": "anaerobic_digestion_biomethane",
    "turquoise_h2_methane_pyrolysis": "pyrolysis_biochar_biofuels",
    "aerogel_superinsulation": "cold_climate_heat_pumps",
}


def seed_policy_standards(db: SessionLocal):
    """Seed foundational policies, standards, codes, and relational linkages."""
    print("=== Seeding Policy, Regulatory, Codes & Standards Knowledge Base ===")
    
    total_added = 0
    total_updated = 0
    tech_links_count = 0
    fuel_links_count = 0

    valid_tech_ids = {r[0] for r in db.query(Technology.id).all()}

    for pol_data in SEED_POLICIES:
        pol_id = pol_data["id"]
        policy = db.query(PolicyStandard).filter(PolicyStandard.id == pol_id).first()

        if not policy:
            policy = PolicyStandard(
                id=pol_id,
                code_identifier=pol_data["code_identifier"],
                title=pol_data["title"],
                short_title=pol_data.get("short_title"),
                category=pol_data["category"],
                jurisdiction_level=pol_data["jurisdiction_level"],
                jurisdiction_state=pol_data.get("jurisdiction_state", "US"),
                status=pol_data.get("status", "active"),
                effective_year=pol_data.get("effective_year"),
                sunset_year=pol_data.get("sunset_year"),
                latest_revision=pol_data.get("latest_revision"),
                executive_summary=pol_data["executive_summary"],
                statutory_intent=pol_data.get("statutory_intent"),
                compliance_mandate=pol_data["compliance_mandate"],
                commercial_friction_points=pol_data.get("commercial_friction_points"),
                associated_incentives=pol_data.get("associated_incentives"),
                official_source_url=pol_data.get("official_source_url"),
                metadata_json={}
            )
            db.add(policy)
            db.flush()
            total_added += 1
        else:
            policy.code_identifier = pol_data["code_identifier"]
            policy.title = pol_data["title"]
            policy.short_title = pol_data.get("short_title")
            policy.category = pol_data["category"]
            policy.jurisdiction_level = pol_data["jurisdiction_level"]
            policy.jurisdiction_state = pol_data.get("jurisdiction_state", "US")
            policy.status = pol_data.get("status", "active")
            policy.effective_year = pol_data.get("effective_year")
            policy.sunset_year = pol_data.get("sunset_year")
            policy.latest_revision = pol_data.get("latest_revision")
            policy.executive_summary = pol_data["executive_summary"]
            policy.statutory_intent = pol_data.get("statutory_intent")
            policy.compliance_mandate = pol_data["compliance_mandate"]
            policy.commercial_friction_points = pol_data.get("commercial_friction_points")
            policy.associated_incentives = pol_data.get("associated_incentives")
            policy.official_source_url = pol_data.get("official_source_url")
            total_updated += 1

        # Seed Technology Linkages
        for tlink in pol_data.get("tech_links", []):
            raw_tech_id = tlink["tech_id"]
            canonical_tech_id = TECH_ID_ALIASES.get(raw_tech_id, raw_tech_id)
            if canonical_tech_id not in valid_tech_ids:
                continue

            existing_tlink = db.query(PolicyTechnologyLink).filter(
                PolicyTechnologyLink.policy_id == pol_id,
                PolicyTechnologyLink.technology_id == canonical_tech_id
            ).first()
            if not existing_tlink:
                new_tlink = PolicyTechnologyLink(
                    policy_id=pol_id,
                    technology_id=canonical_tech_id,
                    relevance_type=tlink["relevance_type"],
                    compliance_impact=tlink.get("compliance_impact", "critical_gate"),
                    impact_summary=tlink.get("impact_summary")
                )
                db.add(new_tlink)
                tech_links_count += 1
            else:
                existing_tlink.relevance_type = tlink["relevance_type"]
                existing_tlink.compliance_impact = tlink.get("compliance_impact", "critical_gate")
                existing_tlink.impact_summary = tlink.get("impact_summary")

        # Seed Fuel Linkages
        for flink in pol_data.get("fuel_links", []):
            existing_flink = db.query(PolicyFuelLink).filter(
                PolicyFuelLink.policy_id == pol_id,
                PolicyFuelLink.fuel_vector == flink["fuel_vector"]
            ).first()
            if not existing_flink:
                new_flink = PolicyFuelLink(
                    policy_id=pol_id,
                    fuel_vector=flink["fuel_vector"],
                    lifecycle_ci_threshold=flink.get("lifecycle_ci_threshold"),
                    impact_summary=flink.get("impact_summary")
                )
                db.add(new_flink)
                fuel_links_count += 1
            else:
                existing_flink.lifecycle_ci_threshold = flink.get("lifecycle_ci_threshold")
                existing_flink.impact_summary = flink.get("impact_summary")

    # Map sample opportunities to policies where matching keywords exist
    opp_links_count = 0
    try:
        sample_opps = db.query(Opportunity).all()
        for opp in sample_opps:
            opp_text = f"{opp.name or ''} {opp.short_description or ''} {opp.agency or ''}".lower()
            if "storage" in opp_text or "battery" in opp_text:
                for target_pol in ["nfpa_855_2023", "ny_clcpa_2019"]:
                    if not db.query(PolicyOpportunityLink).filter_by(policy_id=target_pol, opportunity_id=opp.id).first():
                        db.add(PolicyOpportunityLink(
                            policy_id=target_pol,
                            opportunity_id=opp.id,
                            link_reason="mandatory_standard" if "nfpa" in target_pol else "statutory_basis"
                        ))
                        opp_links_count += 1
            if "hydrogen" in opp_text or "electrolyzer" in opp_text:
                if not db.query(PolicyOpportunityLink).filter_by(policy_id="ira_sec_45v_clean_h2", opportunity_id=opp.id).first():
                    db.add(PolicyOpportunityLink(
                        policy_id="ira_sec_45v_clean_h2",
                        opportunity_id=opp.id,
                        link_reason="statutory_basis"
                    ))
                    opp_links_count += 1
            if "heat pump" in opp_text or "thermal" in opp_text or "building" in opp_text:
                if not db.query(PolicyOpportunityLink).filter_by(policy_id="ny_clcpa_2019", opportunity_id=opp.id).first():
                    db.add(PolicyOpportunityLink(
                        policy_id="ny_clcpa_2019",
                        opportunity_id=opp.id,
                        link_reason="statutory_basis"
                    ))
                    opp_links_count += 1
    except Exception as e:
        print(f"Opportunity linking note: {e}")

    db.commit()
    print(f"Policy standards seeded: {total_added} added, {total_updated} updated.")
    print(f"Technology links created: {tech_links_count}")
    print(f"Fuel links created: {fuel_links_count}")
    print(f"Opportunity links created: {opp_links_count}")
    return {
        "policies_added": total_added,
        "policies_updated": total_updated,
        "tech_links": tech_links_count,
        "fuel_links": fuel_links_count,
        "opp_links": opp_links_count
    }


if __name__ == "__main__":
    db = SessionLocal()
    try:
        init_db()
        init_fts()
        seed_policy_standards(db)
    finally:
        db.close()
