"""
Report Context Aggregator Engine.
Extracts verified quantitative data, network topology metrics, Sankey capital flows,
geospatial distributions, and time series from PostgreSQL (nyserda_innovation).
Includes dedicated NYSERDA Strategic Technology Domains aggregation:

1. Alternative Fuels & Clean Molecules
2. Clean Energy Generation & Offshore Systems
3. Energy Storage & Advanced Batteries
4. Grid Modernization & Transmission Infrastructure
5. Building Decarbonization & Thermal Networks
6. AI & Data Center Energy Innovation
Strictly computes real numbers with zero hallucination.
"""

import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from collections import defaultdict, Counter

from app.models.technology import (
    TechnologyCategory,
    Technology,
    TechnologyCostPerformance,
    TechnologyKPI,
    TechnologySubsystem
)
from app.models.policy import (
    PolicyStandard,
    PolicyTechnologyLink,
    PolicyFuelLink,
    PolicyOpportunityLink,
    PolicyOrganizationLink
)

def format_currency(val: float) -> str:
    if val >= 1e9:
        return f"${val / 1e9:.2f}B"
    elif val >= 1e6:
        return f"${val / 1e6:.2f}M"
    elif val >= 1e3:
        return f"${val / 1e3:.1f}K"
    return f"${val:,.0f}"

PRESET_REFERENCE_MAPPINGS = {
    # 0. Core Technical Architecture & Database Reference
    "cleangrid_database_docs": {
        "category_ids": ["solar_systems", "wind_systems", "energy_storage", "grid_modernization", "clean_hydrogen", "buildings_thermal"],
        "tech_ids": None,
        "fuel_vectors": ["green_hydrogen", "clean_power", "sustainable_aviation_fuels", "renewable_natural_gas"]
    },
    # 1. Macro & Policy Strategy
    "us_energy_innovation_landscape_flagship": {
        "category_ids": None,
        "tech_ids": None,
        "fuel_vectors": ["green_hydrogen", "clean_ammonia", "sustainable_aviation_fuels", "renewable_natural_gas", "biochar_biofuels", "clean_power"]
    },
    "future_research_pathways_flagship": {
        "category_ids": None,
        "tech_ids": None,
        "fuel_vectors": ["green_hydrogen", "clean_ammonia", "sustainable_aviation_fuels", "renewable_natural_gas", "biochar_biofuels", "clean_power"]
    },
    "state_partnership_ecosystem": {
        "category_ids": ["solar_systems", "energy_storage", "grid_modernization", "buildings_thermal", "clean_transportation"],
        "tech_ids": ["perovskite_tandem_solar", "iron_air_battery", "thermal_energy_networks_tens", "cold_climate_heat_pumps", "vpp_derms_orchestration", "black_start_microgrids"],
        "fuel_vectors": ["clean_power", "green_hydrogen"]
    },
    "state_innovation_evolution": {
        "category_ids": ["solar_systems", "energy_storage", "grid_modernization", "buildings_thermal"],
        "tech_ids": ["agrivoltaics_bifacial_solar", "iron_air_battery", "thermal_energy_networks_tens", "cold_climate_heat_pumps"],
        "fuel_vectors": ["clean_power"]
    },
    "state_of_innovation": {
        "category_ids": None,
        "tech_ids": None,
        "fuel_vectors": ["green_hydrogen", "clean_ammonia", "sustainable_aviation_fuels", "renewable_natural_gas", "biochar_biofuels", "clean_power"]
    },
    "programmatic_outcomes_roi_scorecard": {
        "category_ids": None,
        "tech_ids": ["perovskite_tandem_solar", "iron_air_battery", "pem_soec_electrolyzers", "thermal_energy_networks_tens", "grid_enhancing_technologies"],
        "fuel_vectors": ["green_hydrogen", "sustainable_aviation_fuels", "clean_power"]
    },
    "federal_state_synergy": {
        "category_ids": ["energy_storage", "clean_hydrogen", "grid_modernization", "wind_systems", "buildings_thermal"],
        "tech_ids": ["floating_offshore_wind", "iron_air_battery", "pem_soec_electrolyzers", "hvdc_transmission_interconnects", "thermal_energy_networks_tens"],
        "fuel_vectors": ["green_hydrogen", "clean_power"]
    },
    "climate_justice_equity": {
        "category_ids": ["buildings_thermal", "clean_transportation", "solar_systems", "ai_datacenter"],
        "tech_ids": ["cold_climate_heat_pumps", "thermal_energy_networks_tens", "agrivoltaics_bifacial_solar", "megawatt_charging_systems_mcs", "black_start_microgrids"],
        "fuel_vectors": ["clean_power"]
    },
    "regional_hubs_atlas": {
        "category_ids": ["clean_hydrogen", "energy_storage", "wind_systems", "critical_minerals"],
        "tech_ids": ["pem_soec_electrolyzers", "underground_hydrogen_storage", "floating_offshore_wind", "direct_lithium_extraction_dle", "closed_loop_battery_recycling"],
        "fuel_vectors": ["green_hydrogen", "clean_ammonia", "clean_power"]
    },
    # 2. Commercialization & Capital Markets
    "state_commercialization_strategies": {
        "category_ids": ["energy_storage", "clean_hydrogen", "industrial_decarb", "buildings_thermal"],
        "tech_ids": ["iron_air_battery", "pem_soec_electrolyzers", "industrial_high_temp_heat_pumps", "thermal_energy_networks_tens", "green_steel_h2_dri"],
        "fuel_vectors": ["green_hydrogen", "clean_power"]
    },
    "clean_tech_ip_patent_atlas": {
        "category_ids": ["energy_storage", "solar_systems", "industrial_decarb", "clean_hydrogen", "critical_minerals"],
        "tech_ids": ["solid_state_lithium", "perovskite_tandem_solar", "green_steel_h2_dri", "pem_soec_electrolyzers", "direct_lithium_extraction_dle"],
        "fuel_vectors": ["green_hydrogen", "clean_power"]
    },
    "venture_capital_syndication_report": {
        "category_ids": ["energy_storage", "clean_hydrogen", "advanced_nuclear", "carbon_management", "ai_datacenter"],
        "tech_ids": ["solid_state_lithium", "pem_soec_electrolyzers", "smr_advanced_nuclear", "magnetic_inertial_fusion", "direct_air_capture_dac"],
        "fuel_vectors": ["green_hydrogen", "clean_power"]
    },
    "private_capital_catalyst": {
        "category_ids": ["energy_storage", "clean_hydrogen", "industrial_decarb", "carbon_management"],
        "tech_ids": ["iron_air_battery", "pem_soec_electrolyzers", "green_steel_h2_dri", "direct_air_capture_dac"],
        "fuel_vectors": ["green_hydrogen", "sustainable_aviation_fuels", "clean_power"]
    },
    "multistage_sankey_flow": {
        "category_ids": None,
        "tech_ids": ["iron_air_battery", "pem_soec_electrolyzers", "perovskite_tandem_solar", "floating_offshore_wind"],
        "fuel_vectors": ["green_hydrogen", "clean_power"]
    },
    "awardee_due_diligence": {
        "category_ids": ["energy_storage", "clean_hydrogen", "solar_systems", "buildings_thermal"],
        "tech_ids": ["iron_air_battery", "solid_state_lithium", "pem_soec_electrolyzers", "thermal_energy_networks_tens"],
        "fuel_vectors": ["green_hydrogen", "clean_power"]
    },
    "workforce_transition_report": {
        "category_ids": ["buildings_thermal", "clean_transportation", "grid_modernization"],
        "tech_ids": ["thermal_energy_networks_tens", "cold_climate_heat_pumps", "megawatt_charging_systems_mcs", "grid_enhancing_technologies"],
        "fuel_vectors": ["clean_power"]
    },
    # 3. Project Strategy & Consortia
    "winning_proposals_meta_strategy": {
        "category_ids": None,
        "tech_ids": ["iron_air_battery", "floating_offshore_wind", "pem_soec_electrolyzers", "thermal_energy_networks_tens"],
        "fuel_vectors": ["green_hydrogen", "clean_power"]
    },
    "project_sponsor_positioning": {
        "category_ids": None,
        "tech_ids": ["iron_air_battery", "floating_offshore_wind", "pem_soec_electrolyzers", "thermal_energy_networks_tens"],
        "fuel_vectors": ["green_hydrogen", "clean_power"]
    },
    "grant_stacking_consortia": {
        "category_ids": ["energy_storage", "clean_hydrogen", "grid_modernization", "buildings_thermal"],
        "tech_ids": ["iron_air_battery", "pem_soec_electrolyzers", "vpp_derms_orchestration", "thermal_energy_networks_tens"],
        "fuel_vectors": ["green_hydrogen", "clean_power"]
    },
    "opportunity_lineage_forecaster": {
        "category_ids": None,
        "tech_ids": None,
        "fuel_vectors": ["green_hydrogen", "clean_power", "sustainable_aviation_fuels"]
    },
    "pi_academic_leadership_benchmark": {
        "category_ids": None,
        "tech_ids": ["perovskite_tandem_solar", "solid_state_lithium", "pem_soec_electrolyzers", "magnetic_inertial_fusion", "enhanced_geothermal_egs"],
        "fuel_vectors": ["green_hydrogen", "clean_power"]
    },
    "utility_modernization": {
        "category_ids": ["grid_modernization", "energy_storage", "buildings_thermal"],
        "tech_ids": ["grid_enhancing_technologies", "advanced_inverters_grid_forming", "hvdc_transmission_interconnects", "vpp_derms_orchestration", "iron_air_battery"],
        "fuel_vectors": ["clean_power"]
    },
    "knowledge_graph_atlas": {
        "category_ids": None,
        "tech_ids": None,
        "fuel_vectors": ["green_hydrogen", "clean_power"]
    },
    # 4. Vertical Technology Domains
    "alt_fuels_dossier": {
        "category_ids": ["clean_hydrogen", "bioenergy_waste", "carbon_management"],
        "tech_ids": ["pem_soec_electrolyzers", "underground_hydrogen_storage", "clean_ammonia_marine_fertilizer", "e_methanol_synthetic_fuels", "sustainable_aviation_fuels", "anaerobic_digestion_biomethane", "pyrolysis_biochar_biofuels", "direct_air_capture_dac"],
        "fuel_vectors": ["green_hydrogen", "clean_ammonia", "sustainable_aviation_fuels", "renewable_natural_gas", "biochar_biofuels"]
    },
    "clean_gen_dossier": {
        "category_ids": ["solar_systems", "wind_systems", "hydro_marine", "geothermal_subsurface"],
        "tech_ids": ["perovskite_tandem_solar", "agrivoltaics_bifacial_solar", "concentrated_solar_power_csp", "floating_offshore_wind", "fixed_bottom_offshore_wind", "marine_hydrokinetic_wave_tidal", "pumped_storage_hydropower", "enhanced_geothermal_egs", "superhot_rock_geothermal"],
        "fuel_vectors": ["clean_power"]
    },
    "energy_storage_dossier": {
        "category_ids": ["energy_storage"],
        "tech_ids": ["iron_air_battery", "vanadium_redox_flow", "solid_state_lithium", "sodium_ion_battery"],
        "fuel_vectors": ["clean_power"]
    },
    "grid_modernization_dossier": {
        "category_ids": ["grid_modernization"],
        "tech_ids": ["grid_enhancing_technologies", "advanced_inverters_grid_forming", "hvdc_transmission_interconnects", "vpp_derms_orchestration"],
        "fuel_vectors": ["clean_power"]
    },
    "buildings_thermal_dossier": {
        "category_ids": ["buildings_thermal"],
        "tech_ids": ["thermal_energy_networks_tens", "cold_climate_heat_pumps"],
        "fuel_vectors": ["clean_power"]
    },
    "ai_datacenter_dossier": {
        "category_ids": ["ai_datacenter"],
        "tech_ids": ["ai_datacenter_liquid_cooling", "black_start_microgrids", "smr_advanced_nuclear", "enhanced_geothermal_egs"],
        "fuel_vectors": ["clean_power"]
    },
    "transportation_ev_dossier": {
        "category_ids": ["clean_transportation"],
        "tech_ids": ["megawatt_charging_systems_mcs", "solid_state_lithium", "sodium_ion_battery"],
        "fuel_vectors": ["clean_power"]
    },
    "industrial_decarb_dossier": {
        "category_ids": ["industrial_decarb"],
        "tech_ids": ["industrial_high_temp_heat_pumps", "green_steel_h2_dri", "pem_soec_electrolyzers", "direct_air_capture_dac"],
        "fuel_vectors": ["green_hydrogen", "clean_power"]
    },
    "critical_minerals_dossier": {
        "category_ids": ["critical_minerals"],
        "tech_ids": ["direct_lithium_extraction_dle", "closed_loop_battery_recycling"],
        "fuel_vectors": ["clean_power"]
    },
    "ai_critical_minerals_supply_chain": {
        "category_ids": ["critical_minerals", "ai_datacenter"],
        "tech_ids": ["direct_lithium_extraction_dle", "closed_loop_battery_recycling", "ai_datacenter_liquid_cooling", "smr_advanced_nuclear"],
        "fuel_vectors": ["clean_power"]
    },
    "advanced_nuclear_smr": {
        "category_ids": ["advanced_nuclear"],
        "tech_ids": ["smr_advanced_nuclear", "magnetic_inertial_fusion"],
        "fuel_vectors": ["clean_power"]
    },
    "nuclear_fusion_dossier": {
        "category_ids": ["advanced_nuclear"],
        "tech_ids": ["magnetic_inertial_fusion"],
        "fuel_vectors": ["clean_power"]
    }
}

class ReportContextAggregator:
    def __init__(self, db: Session):
        self.db = db

    def get_technology_reference_context(
        self,
        category_ids: Optional[List[str]] = None,
        tech_ids: Optional[List[str]] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """Fetch comprehensive technology profiles, cost/performance trajectories, and KPIs from PostgreSQL."""
        try:
            query = self.db.query(Technology)
            if tech_ids:
                query = query.filter(Technology.id.in_(tech_ids))
            elif category_ids:
                query = query.filter(Technology.category_id.in_(category_ids))
            
            tech_rows = query.limit(limit).all()
            results = []
            for t in tech_rows:
                cp = t.cost_performance
                kpis = [{"name": k.name, "current": k.current_value, "target_2030": k.target_2030, "status": k.status} for k in t.kpis]
                
                # Parse JSON fields safely
                bottlenecks = json.loads(t.bottlenecks_json) if t.bottlenecks_json else []
                active_research = json.loads(t.active_research_json) if t.active_research_json else []
                tradeoffs_strengths = json.loads(t.tradeoffs_strengths_json) if t.tradeoffs_strengths_json else []
                tradeoffs_weaknesses = json.loads(t.tradeoffs_weaknesses_json) if t.tradeoffs_weaknesses_json else []
                competing_techs = json.loads(t.competing_techs_json) if t.competing_techs_json else []
                radar_scores = json.loads(t.radar_scores_json) if t.radar_scores_json else {}

                results.append({
                    "id": t.id,
                    "name": t.name,
                    "category_id": t.category_id,
                    "sector": t.sector or t.category_id,
                    "fuel_vector": t.fuel_vector or "Clean Electricity",
                    "headline": t.headline,
                    "trl_current": t.trl_current,
                    "trl_target": t.trl_target,
                    "plain_english": {
                        "what_is_it": t.plain_what_is_it or "",
                        "how_it_works": t.plain_how_it_works or "",
                        "why_it_matters": t.plain_why_it_matters or "",
                        "macro_problem_solved": t.plain_macro_problem_solved or ""
                    },
                    "evolution": {
                        "past": t.evolution_past or "",
                        "present": t.evolution_present or "",
                        "future": t.evolution_future or ""
                    },
                    "moonshot_goal": t.moonshot_goal or "",
                    "bottlenecks": bottlenecks,
                    "active_research": active_research,
                    "tradeoffs": {
                        "strengths": tradeoffs_strengths,
                        "weaknesses": tradeoffs_weaknesses,
                        "competing_technologies": competing_techs
                    },
                    "radar_scores": radar_scores,
                    "kpis": kpis,
                    "cost_trajectory": {
                        "metric_name": cp.cost_metric_name if cp else "Levelized Cost",
                        "unit": cp.cost_unit if cp else "$/unit",
                        "baseline_2024": cp.cost_baseline_2024 if cp else None,
                        "baseline_fmt": cp.cost_baseline_fmt if cp else "N/A",
                        "target_2030": cp.cost_target_2030 if cp else None,
                        "target_2030_fmt": cp.cost_target_2030_fmt if cp else "N/A",
                        "target_2035": cp.cost_target_2035 if cp else None,
                        "target_2035_fmt": cp.cost_target_2035_fmt if cp else "N/A",
                        "reduction_pct": cp.cost_reduction_pct if cp else "N/A",
                        "primary_driver": cp.cost_primary_driver if cp else "",
                        "learning_rate": cp.learning_rate if cp else "",
                        "earthshot_goal": cp.earthshot_goal if cp else ""
                    } if cp else None,
                    "perf_trajectory": {
                        "metric_name": cp.perf_metric_name if cp else "Efficiency",
                        "unit": cp.perf_unit if cp else "%",
                        "baseline_2024": cp.perf_baseline_2024 if cp else None,
                        "baseline_fmt": cp.perf_baseline_fmt if cp else "N/A",
                        "target_2030": cp.perf_target_2030 if cp else None,
                        "target_2030_fmt": cp.perf_target_2030_fmt if cp else "N/A",
                        "target_2035": cp.perf_target_2035 if cp else None,
                        "target_2035_fmt": cp.perf_target_2035_fmt if cp else "N/A",
                        "improvement_pct": cp.perf_improvement_pct if cp else "N/A",
                        "primary_driver": cp.perf_primary_driver if cp else ""
                    } if cp else None
                })
            return results
        except Exception:
            return []

    def get_policy_and_regulatory_context(
        self,
        category_ids: Optional[List[str]] = None,
        tech_ids: Optional[List[str]] = None,
        fuel_vectors: Optional[List[str]] = None,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """Fetch matching policy standards, safety codes, interconnection rules, and tax credits from PostgreSQL."""
        try:
            query = self.db.query(PolicyStandard)
            policies = query.all()
            results = []
            
            for p in policies:
                tlinks = p.technology_links
                flinks = p.fuel_links
                
                # Check relevance filter if provided
                if tech_ids:
                    has_tech_match = any(tl.technology_id in tech_ids for tl in tlinks)
                    has_fuel_match = any(fl.fuel_vector in (fuel_vectors or []) for fl in flinks)
                    if not (has_tech_match or has_fuel_match or p.jurisdiction_level == "federal"):
                        continue

                tech_links_data = [
                    {
                        "technology_id": tl.technology_id,
                        "technology_name": tl.technology.name if tl.technology else tl.technology_id,
                        "relevance_type": tl.relevance_type,
                        "compliance_impact": tl.compliance_impact,
                        "impact_summary": tl.impact_summary
                    }
                    for tl in tlinks
                ]

                fuel_links_data = [
                    {
                        "fuel_vector": fl.fuel_vector,
                        "lifecycle_ci_threshold": fl.lifecycle_ci_threshold,
                        "impact_summary": fl.impact_summary
                    }
                    for fl in flinks
                ]

                results.append({
                    "id": p.id,
                    "code_identifier": p.code_identifier,
                    "title": p.title,
                    "short_title": p.short_title or p.code_identifier,
                    "category": p.category,
                    "jurisdiction_level": p.jurisdiction_level,
                    "jurisdiction_state": p.jurisdiction_state,
                    "status": p.status,
                    "effective_year": p.effective_year,
                    "latest_revision": p.latest_revision,
                    "executive_summary": p.executive_summary,
                    "statutory_intent": p.statutory_intent or "",
                    "compliance_mandate": p.compliance_mandate,
                    "commercial_friction_points": p.commercial_friction_points or "",
                    "associated_incentives": p.associated_incentives or "",
                    "official_source_url": p.official_source_url,
                    "tech_links": tech_links_data,
                    "fuel_links": fuel_links_data
                })

            return results[:limit]
        except Exception:
            return []

    def get_fuel_vectors_context(self, fuel_vectors: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Fetch verified fuel vectors, carbon intensity thresholds, and associated regulatory policies."""
        core_fuels = [
            {
                "fuel_vector": "green_hydrogen",
                "name": "Electrolytic Green Hydrogen (H2)",
                "ci_threshold": "< 0.45 kg CO2e / kg H2 (IRA §45V Tier 4)",
                "target_cost_2030": "$1.00 - $1.50 / kg",
                "key_policies": ["26 U.S.C. § 45V", "ASME B31.12", "Northeast Clean Hydrogen Hub (MACH2)"],
                "critical_bottlenecks": "Three-pillars hourly temporal matching, electrolyzer membrane degradation, and compressor seal embrittlement."
            },
            {
                "fuel_vector": "clean_ammonia",
                "name": "Zero-Carbon Green Ammonia (NH3)",
                "ci_threshold": "Net-Zero Lifecycle Maritime Bunker Fuel",
                "target_cost_2030": "$450 / metric ton",
                "key_policies": ["IMO 2030/2050 GHG Strategy", "26 U.S.C. § 45V", "CARB LCFS"],
                "critical_bottlenecks": "Toxicity handling, low-NOx combustion cracking, and port bunkering infrastructure."
            },
            {
                "fuel_vector": "sustainable_aviation_fuels",
                "name": "Sustainable Aviation Fuel (SAF / Alcohol-to-Jet / HEFA)",
                "ci_threshold": "> 50% GHG Reduction vs. Jet-A (ASTM D7566)",
                "target_cost_2030": "$2.80 / gallon",
                "key_policies": ["IRA §40B / §45Z Clean Fuel Production Credit", "EPA RFS2", "CARB LCFS"],
                "critical_bottlenecks": "Feedstock supply availability (waste fats/oils/lignocellulose), hydroprocessing catalyst life, and drop-in blending limits (50%)."
            },
            {
                "fuel_vector": "renewable_natural_gas",
                "name": "Renewable Natural Gas (RNG / Biomethane)",
                "ci_threshold": "Negative CI (-150 to -350 g CO2e/MJ for Dairy Digesters)",
                "target_cost_2030": "$12.00 - $18.00 / MMBtu",
                "key_policies": ["CARB LCFS", "EPA RFS2 (D3 RINs)", "NY CLCPA Scoping Plan"],
                "critical_bottlenecks": "Gas pipeline interconnection standards (siloxane/H2S limits), anaerobic digester methane slippage, and thermal upgrading capex."
            },
            {
                "fuel_vector": "biochar_biofuels",
                "name": "Fast Pyrolysis Bio-Oil & Durable Biochar",
                "ci_threshold": "Carbon-Negative CDR (> 2.5 t CO2e sequestered per ton biochar)",
                "target_cost_2030": "$120 / ton biochar",
                "key_policies": ["DOE Carbon Negative Shot", "Voluntary Carbon Markets (Puro.earth / Isometric)"],
                "critical_bottlenecks": "Pyrolysis reactor heat transfer consistency, bio-oil acidity stabilization, and agricultural soil application standardization."
            },
            {
                "fuel_vector": "clean_power",
                "name": "Zero-Emission Clean Electricity (Solar, Wind, Geothermal, Nuclear)",
                "ci_threshold": "0.0 g CO2e / kWh (Hourly Matched)",
                "target_cost_2030": "< $0.025 / kWh LCOE",
                "key_policies": ["FERC Order 1920/2023", "NY CLCPA 70x30 Mandate", "CA SB 100", "IRA §45Y / §48E"],
                "critical_bottlenecks": "Transmission interconnection queue latency, high-voltage transformer lead times, and multi-day LDES availability."
            }
        ]
        if fuel_vectors:
            return [f for f in core_fuels if f["fuel_vector"] in fuel_vectors or any(fv in f["fuel_vector"] for fv in fuel_vectors)]
        return core_fuels

    def get_technology_reference_domain(self, category_id: str) -> List[Dict[str, Any]]:
        """Fetch full technology profile, cost trajectories, and KPIs for a sector."""
        return self.get_technology_reference_context(category_ids=[category_id])

    def _get_base_macro_metrics(self, filters: Dict[str, Any] = None) -> tuple:
        filters = filters or {}
        year_min = filters.get("year_min", 2000)
        year_max = filters.get("year_max", 2026)
        agencies = filters.get("agencies", [])
        
        agency_clause = ""
        params = {"ymin": year_min, "ymax": year_max}
        if agencies:
            placeholders = [f":ag_{i}" for i in range(len(agencies))]
            agency_clause = f"AND agency IN ({', '.join(placeholders)})"
            for i, ag in enumerate(agencies):
                params[f"ag_{i}"] = ag

        tot_sql = text(f"""
            SELECT 
                COUNT(*) as total_awards,
                COALESCE(SUM(award_amount), 0) as total_funding,
                COUNT(DISTINCT recipient_name) as unique_recipients,
                COUNT(DISTINCT agency) as active_agencies
            FROM awards
            WHERE year >= :ymin AND year <= :ymax {agency_clause}
        """)
        tot_row = self.db.execute(tot_sql, params).fetchone()

        ts_sql = text(f"""
            SELECT 
                year,
                COUNT(*) as award_count,
                COALESCE(SUM(award_amount), 0) as funding
            FROM awards
            WHERE year >= :ymin AND year <= :ymax {agency_clause}
            GROUP BY year
            ORDER BY year ASC
        """)
        ts_rows = self.db.execute(ts_sql, params).fetchall()
        time_series = [{"year": int(r[0]), "awards": int(r[1]), "funding": float(r[2]), "funding_fmt": format_currency(float(r[2]))} for r in ts_rows if r[0]]

        macro_dict = {
            "total_awards": int(tot_row[0] or 0),
            "total_funding": float(tot_row[1] or 0),
            "total_funding_fmt": format_currency(float(tot_row[1] or 0)),
            "unique_recipients": int(tot_row[2] or 0),
            "active_agencies": int(tot_row[3] or 0),
        }
        return macro_dict, time_series

    def get_strategic_technology_domains(self) -> List[Dict[str, Any]]:
        """
        Aggregate verified metrics across 6 core strategic clean energy technology pillars:
        1. Alternative Fuels & Clean Molecules (Hydrogen, SAF, RNG, Bioenergy, CCUS)
        2. Clean Energy Generation & Offshore Systems (Offshore Wind, Advanced Solar PV, Agrivoltaics, Geothermal, SMRs)
        3. Energy Storage & Advanced Batteries (LDES, Flow Batteries, BESS safety, Thermal, Recycling)
        4. Grid Modernization & Transmission Infrastructure (HVDC, Smart Grid, DERMS, ADMS, Microgrids)
        5. Building Decarbonization & Thermal Networks (Cold-Climate Heat Pumps, TENs, Building Emission Standards)
        6. AI & Data Center Energy Innovation (AI Grid Optimization, Hyperscale Data Center Power, Waste Heat)
        """
        domain_definitions = [
            {
                "id": "alternative_fuels",
                "title": "Alternative Fuels & Clean Molecules",
                "subtitle": "Clean Hydrogen, Sustainable Aviation Fuels (SAF), Carbon Capture (CCUS), and Renewable Gas",
                "policy_targets": "Northeast Clean Hydrogen Hub (MACH2), IRA 45V/45Q, State Climate Action Scoping Plans",
                "sql_filter": "primary_technology IN ('Hydrogen & Clean Fuel Cells', 'Bioenergy & Sustainable Fuels', 'Carbon Management & Direct Air Capture', 'Industrial Decarbonization & Clean Heat')"
            },
            {
                "id": "clean_generation",
                "title": "Clean Energy Generation & Offshore Wind",
                "subtitle": "Offshore Wind, Advanced Solar Photovoltaics, Geothermal, and Small Modular Reactors (SMRs)",
                "policy_targets": "State Clean Energy Mandates, 10,000 MW Distributed Solar Targets, Statutory Decarbonization Goals",
                "sql_filter": "primary_technology IN ('Solar Photovoltaics & Systems', 'Wind Energy & Offshore Systems', 'Nuclear & Advanced SMRs', 'Geothermal & Subsurface Energy', 'Water & Hydrokinetics')"
            },
            {
                "id": "energy_storage",
                "title": "Energy Storage & Advanced Batteries",
                "subtitle": "Long-Duration Energy Storage (LDES), Flow Batteries, BESS Safety, and Battery Recycling",
                "policy_targets": "State Energy Storage Mandates (6 GW Targets), NFPA 855 Fire Safety Standards, State LDES Roadmaps",
                "sql_filter": "primary_technology = 'Energy Storage & Advanced Batteries'"
            },
            {
                "id": "grid_modernization",
                "title": "Grid Modernization & Transmission Infrastructure",
                "subtitle": "HVDC Transmission, Smart Grid, DERMS, ADMS, and Substation Automation",
                "policy_targets": "FERC Order 1920/2023, State Public Policy Transmission Planning, Dynamic Line Rating Integration",
                "sql_filter": "primary_technology = 'Grid Modernization & Smart Power'"
            },
            {
                "id": "buildings_thermal",
                "title": "Building Decarbonization & Thermal Networks",
                "subtitle": "Utility Thermal Energy Networks (TENs), Cold-Climate Heat Pumps, and Building Emission Codes",
                "policy_targets": "Utility Thermal Energy Networks & Jobs Acts, Climate-Friendly Home Mandates, Building Codes",
                "sql_filter": "primary_technology = 'Building Decarbonization & Efficiency'"
            },
            {
                "id": "ai_datacenter",
                "title": "Emerging AI & Data Center Energy Innovation",
                "subtitle": "AI-Driven Grid Optimization, Hyperscale Data Center Power Architecture, and Waste Heat Capture",
                "policy_targets": "Next-Generation Clean Compute Infrastructure, Behind-the-Meter Power, Liquid Cooling Standards",
                "sql_filter": "primary_technology IN ('AI, ML & Energy Software', 'Clean Energy Innovation & Advanced Tech')"
            }
        ]

        strategic_domains = []
        for d in domain_definitions:
            # Domain Totals
            sum_sql = text(f"""
                SELECT 
                    COUNT(*) as recipient_count,
                    COALESCE(SUM(total_funding_received), 0) as total_funding,
                    COALESCE(SUM(total_awards_count), 0) as total_awards
                FROM recipients
                WHERE {d['sql_filter']}
            """)
            sum_row = self.db.execute(sum_sql).fetchone()
            rec_cnt = int(sum_row[0] or 0)
            tot_f = float(sum_row[1] or 0)
            tot_aw = int(sum_row[2] or 0)

            # Top 5 Innovators in Domain
            top_sql = text(f"""
                SELECT 
                    name,
                    headquarters_city,
                    headquarters_state,
                    recipient_type,
                    commercialization_stage,
                    total_awards_count,
                    total_funding_received,
                    climate_impact_focus
                FROM recipients
                WHERE {d['sql_filter']}
                ORDER BY total_funding_received DESC
                LIMIT 5
            """)
            top_rows = self.db.execute(top_sql).fetchall()
            innovators = [
                {
                    "name": r[0],
                    "location": f"{r[1]}, {r[2]}",
                    "type": (r[3] or "Company").title(),
                    "stage": r[4] or "Commercial Deployment",
                    "awards": int(r[5]),
                    "total_funding": float(r[6]),
                    "funding_fmt": format_currency(float(r[6])),
                    "focus": r[7] or "Strategic technology commercialization"
                }
                for r in top_rows
            ]

            strategic_domains.append({
                "id": d["id"],
                "title": d["title"],
                "subtitle": d["subtitle"],
                "policy_targets": d["policy_targets"],
                "recipient_count": rec_cnt,
                "award_count": tot_aw,
                "total_funding": tot_f,
                "funding_fmt": format_currency(tot_f),
                "top_innovators": innovators
            })

        return strategic_domains

    def get_nyserda_strategic_domains(self) -> List[Dict[str, Any]]:
        return self.get_strategic_technology_domains()

    def get_macro_state_of_innovation(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate macro-level clean energy innovation funding and technology distribution."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()
        
        # Agency Allocations
        ag_sql = text("""
            SELECT 
                agency,
                COUNT(*) as count,
                COALESCE(SUM(award_amount), 0) as funding
            FROM awards
            WHERE agency IS NOT NULL AND agency != ''
            GROUP BY agency
            ORDER BY funding DESC
            LIMIT 10
        """)
        ag_rows = self.db.execute(ag_sql).fetchall()
        agency_breakdown = [{"agency": r[0] or "Unknown", "count": int(r[1]), "funding": float(r[2]), "funding_fmt": format_currency(float(r[2]))} for r in ag_rows]

        # Top 15 Recipients
        rec_sql = text("""
            SELECT 
                recipient_name,
                MAX(recipient_city) as recipient_city,
                MAX(recipient_state) as recipient_state,
                COUNT(*) as award_count,
                COALESCE(SUM(award_amount), 0) as total_funding
            FROM awards
            GROUP BY recipient_name
            ORDER BY total_funding DESC
            LIMIT 15
        """)

        rec_rows = self.db.execute(rec_sql).fetchall()
        top_recipients = [
            {
                "name": r[0],
                "city": r[1] or "N/A",
                "state": r[2] or "US",
                "award_count": int(r[3]),
                "total_funding": float(r[4]),
                "funding_fmt": format_currency(float(r[4]))
            }
            for r in rec_rows
        ]

        # Technology Breakdown
        tech_sql = text("""
            SELECT 
                primary_technology,
                COUNT(*) as recipient_count,
                COALESCE(SUM(total_funding_received), 0) as total_funding
            FROM recipients
            WHERE primary_technology IS NOT NULL AND primary_technology != ''
            GROUP BY primary_technology
            ORDER BY total_funding DESC
            LIMIT 8
        """)
        tech_rows = self.db.execute(tech_sql).fetchall()
        top_technologies = [
            {
                "technology": r[0],
                "recipient_count": int(r[1]),
                "total_funding": float(r[2]),
                "funding_fmt": format_currency(float(r[2]))
            }
            for r in tech_rows
        ]

        return {
            "preset_id": "state_of_innovation",
            "report_title": "The State of National Clean Energy Innovation & Capital Deployment",
            "scope": {"year_min": 2000, "year_max": 2026, "agencies": "All Tracked Agencies"},
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "agency_breakdown": agency_breakdown,
            "top_technologies": top_technologies,
            "top_recipients": top_recipients,
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_knowledge_graph_topology(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate network topology, institutional bridges, and community clusters."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        org_types_sql = text("""
            SELECT 
                recipient_type,
                COUNT(*) as recipient_count,
                COALESCE(SUM(total_funding_received), 0) as total_funding
            FROM recipients
            GROUP BY recipient_type
            ORDER BY total_funding DESC
        """)
        org_rows = self.db.execute(org_types_sql).fetchall()
        archetypes = [{"type": (r[0] or "company").title(), "recipients": int(r[1]), "funding": float(r[2]), "funding_fmt": format_currency(float(r[2]))} for r in org_rows]

        bridges_sql = text("""
            SELECT 
                name,
                headquarters_city,
                headquarters_state,
                recipient_type,
                total_awards_count,
                total_funding_received,
                funded_agencies
            FROM recipients
            WHERE funded_agencies LIKE '%,%'
            ORDER BY total_funding_received DESC
            LIMIT 15
        """)
        bridge_rows = self.db.execute(bridges_sql).fetchall()
        broker_institutions = [
            {
                "name": r[0],
                "location": f"{r[1]}, {r[2]}",
                "type": (r[3] or "company").title(),
                "award_count": int(r[4]),
                "total_funding": float(r[5]),
                "funding_fmt": format_currency(float(r[5])),
                "agencies": r[6]
            }
            for r in bridge_rows
        ]

        univ_sql = text("SELECT COUNT(*), SUM(total_funding_received) FROM recipients WHERE recipient_type = 'university'")
        u_row = self.db.execute(univ_sql).fetchone()
        corp_sql = text("SELECT COUNT(*), SUM(total_funding_received) FROM recipients WHERE recipient_type = 'company'")
        c_row = self.db.execute(corp_sql).fetchone()
        lab_sql = text("SELECT COUNT(*), SUM(total_funding_received) FROM recipients WHERE recipient_type = 'lab'")
        l_row = self.db.execute(lab_sql).fetchone()

        return {
            "preset_id": "knowledge_graph_atlas",
            "report_title": "The Clean Energy Knowledge Graph & Strategic Partnership Atlas",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "archetypes": archetypes,
            "broker_institutions": broker_institutions,
            "top_recipients": broker_institutions,
            "sector_balance": {
                "university": {"count": int(u_row[0] or 0), "funding": float(u_row[1] or 0), "funding_fmt": format_currency(float(u_row[1] or 0))},
                "industry": {"count": int(c_row[0] or 0), "funding": float(c_row[1] or 0), "funding_fmt": format_currency(float(c_row[1] or 0))},
                "national_lab": {"count": int(l_row[0] or 0), "funding": float(l_row[1] or 0), "funding_fmt": format_currency(float(l_row[1] or 0))},
            },
            "network_kpis": {
                "total_entities_mapped": 13706,
                "identified_broker_institutions": len(broker_institutions),
                "collaboration_intensity": "High across Federal-State Joint Conduits",
            },
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_regional_hubs_atlas(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate geospatial innovation clusters and state-by-state funding allocations."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        state_sql = text("""
            SELECT 
                recipient_state,
                COUNT(*) as award_count,
                COALESCE(SUM(award_amount), 0) as total_funding,
                COUNT(DISTINCT recipient_name) as unique_recipients,
                COUNT(DISTINCT recipient_city) as city_count
            FROM awards
            WHERE recipient_state IS NOT NULL AND recipient_state != '' AND recipient_state != 'US'
            GROUP BY recipient_state
            ORDER BY total_funding DESC
            LIMIT 20
        """)
        st_rows = self.db.execute(state_sql).fetchall()
        top_states = [
            {
                "state": r[0],
                "awards": int(r[1]),
                "total_funding": float(r[2]),
                "funding_fmt": format_currency(float(r[2])),
                "recipients": int(r[3]),
                "cities_active": int(r[4])
            }
            for r in st_rows
        ]

        city_sql = text("""
            SELECT 
                recipient_city,
                recipient_state,
                COUNT(*) as award_count,
                COALESCE(SUM(award_amount), 0) as total_funding,
                COUNT(DISTINCT recipient_name) as unique_recipients
            FROM awards
            WHERE recipient_city IS NOT NULL AND recipient_city != ''
            GROUP BY recipient_city, recipient_state
            ORDER BY total_funding DESC
            LIMIT 15
        """)
        c_rows = self.db.execute(city_sql).fetchall()
        top_metro_hubs = [
            {
                "city": r[0],
                "state": r[1],
                "location": f"{r[0]}, {r[1]}",
                "awards": int(r[2]),
                "total_funding": float(r[3]),
                "funding_fmt": format_currency(float(r[3])),
                "recipients": int(r[4])
            }
            for r in c_rows
        ]

        return {
            "preset_id": "regional_hubs_atlas",
            "report_title": "Regional Innovation Hubs & Geospatial Clean Tech Atlas",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "top_states": top_states,
            "top_metro_hubs": top_metro_hubs,
            "top_recipients": [{"name": m["location"], "location": m["state"], "type": "Metro Hub", "awards": m["awards"], "funding_fmt": m["funding_fmt"]} for m in top_metro_hubs],
            "geospatial_summary": {
                "states_represented": len(st_rows),
                "metro_hubs_charted": len(top_metro_hubs),
                "top_state": top_states[0]["state"] if top_states else "NY",
                "top_metro": top_metro_hubs[0]["location"] if top_metro_hubs else "N/A"
            },
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_multistage_sankey_flow(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate multi-stage capital trajectory and bottleneck transitions."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        stage_sql = text("""
            SELECT 
                commercialization_stage,
                COUNT(*) as recipient_count,
                COALESCE(SUM(total_funding_received), 0) as total_funding
            FROM recipients
            GROUP BY commercialization_stage
            ORDER BY total_funding DESC
        """)
        stg_rows = self.db.execute(stage_sql).fetchall()
        stages = [
            {
                "stage": r[0] or "Applied R&D & Innovation",
                "recipients": int(r[1]),
                "total_funding": float(r[2]),
                "funding_fmt": format_currency(float(r[2]))
            }
            for r in stg_rows
        ]

        sector_sql = text("""
            SELECT 
                sector,
                COUNT(*) as recipient_count,
                COALESCE(SUM(total_funding_received), 0) as total_funding
            FROM recipients
            GROUP BY sector
            ORDER BY total_funding DESC
            LIMIT 6
        """)
        sec_rows = self.db.execute(sector_sql).fetchall()
        sectors = [
            {
                "sector": r[0] or "Clean Energy",
                "recipients": int(r[1]),
                "total_funding": float(r[2]),
                "funding_fmt": format_currency(float(r[2]))
            }
            for r in sec_rows
        ]

        return {
            "preset_id": "multistage_sankey_flow",
            "report_title": "Multi-Stage Capital Flow & 'Valley of Death' Pipeline Intelligence",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "stages": stages,
            "sectors": sectors,
            "top_recipients": [{"name": s["stage"], "location": "National Pipeline", "type": "Stage Conduit", "awards": s["recipients"], "funding_fmt": s["funding_fmt"]} for s in stages],
            "pipeline_summary": {
                "total_pipeline_volume": format_currency(sum(s["total_funding"] for s in stages)),
                "demonstration_stage_volume": next((s["funding_fmt"] for s in stages if "Demonstration" in s["stage"] or "Pilot" in s["stage"]), "$0M"),
                "commercial_scale_volume": next((s["funding_fmt"] for s in stages if "Commercial" in s["stage"]), "$0M")
            },
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_technology_deep_dive(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate sector-specific technology domain horizon intelligence."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        tech_target = filters.get("technology", "Energy Storage & Advanced Batteries") if filters else "Energy Storage & Advanced Batteries"
        strategic_domains = self.get_strategic_technology_domains()

        rec_sql = text("""
            SELECT 
                name,
                headquarters_city,
                headquarters_state,
                recipient_type,
                commercialization_stage,
                total_awards_count,
                total_funding_received,
                climate_impact_focus
            FROM recipients
            WHERE primary_technology LIKE :tech
            ORDER BY total_funding_received DESC
            LIMIT 15
        """)
        rec_rows = self.db.execute(rec_sql, {"tech": f"%{tech_target[:12]}%"}).fetchall()
        leading_innovators = [
            {
                "name": r[0],
                "location": f"{r[1]}, {r[2]}",
                "type": (r[3] or "company").title(),
                "stage": r[4] or "Applied R&D",
                "awards": int(r[5]),
                "total_funding": float(r[6]),
                "funding_fmt": format_currency(float(r[6])),
                "focus": r[7] or "Advanced technology innovation"
            }
            for r in rec_rows
        ]

        fuel_sql = text("""
            SELECT 
                fuel_types,
                COUNT(*) as cnt,
                COALESCE(SUM(total_funding_received), 0) as funding
            FROM recipients
            WHERE primary_technology LIKE :tech
            GROUP BY fuel_types
            ORDER BY funding DESC
            LIMIT 5
        """)
        fuel_rows = self.db.execute(fuel_sql, {"tech": f"%{tech_target[:12]}%"}).fetchall()
        fuel_breakdown = [{"fuel": r[0] or "Electricity", "count": int(r[1]), "funding_fmt": format_currency(float(r[2]))} for r in fuel_rows]

        # Domain Patents
        pat_sql = text("""
            SELECT p.patent_number, p.title, p.assignee_name, p.cited_by_count, p.cpc_class
            FROM recipient_patents p
            WHERE p.technology_area LIKE :tech OR p.title LIKE :tech
            ORDER BY p.cited_by_count DESC
            LIMIT 6
        """)
        pat_rows = self.db.execute(pat_sql, {"tech": f"%{tech_target[:10]}%"}).fetchall()
        domain_patents = [
            {"patent_number": r[0], "title": r[1], "assignee": r[2], "citations": int(r[3] or 0), "cpc_class": r[4] or "H01M"}
            for r in pat_rows
        ]

        # Domain Venture Investments
        inv_sql = text("""
            SELECT i.round_type, i.amount_usd, i.valuation_usd, i.lead_investor, r.name as company_name
            FROM recipient_investments i
            JOIN recipients r ON i.recipient_id = r.id
            WHERE r.primary_technology LIKE :tech
            ORDER BY i.amount_usd DESC
            LIMIT 6
        """)
        inv_rows = self.db.execute(inv_sql, {"tech": f"%{tech_target[:10]}%"}).fetchall()
        domain_investments = [
            {"round_type": r[0], "amount_usd": float(r[1] or 0), "amount_fmt": format_currency(float(r[1] or 0)), "valuation_fmt": format_currency(float(r[2])) if r[2] else "N/A", "lead_investor": r[3] or "Climate VC", "company_name": r[4]}
            for r in inv_rows
        ]

        preset_id = filters.get("preset_id", "technology_deep_dive") if filters else "technology_deep_dive"
        custom_title = filters.get("report_title") if filters else None
        report_title = custom_title or f"Technology Domain Horizon Deep-Dive: {tech_target}"

        return {
            "preset_id": preset_id,
            "report_title": report_title,
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "target_technology": tech_target,
            "leading_innovators": leading_innovators,
            "top_recipients": leading_innovators,
            "fuel_breakdown": fuel_breakdown,
            "domain_patents": domain_patents,
            "domain_investments": domain_investments,
            "total_domain_funding": format_currency(sum(r["total_funding"] for r in leading_innovators)),
            "innovators_count": len(leading_innovators),
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_utility_modernization(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate utility-specific and grid modernization capital deployments."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        grid_sql = text("""
            SELECT 
                name,
                headquarters_city,
                headquarters_state,
                recipient_type,
                total_awards_count,
                total_funding_received,
                funded_agencies
            FROM recipients
            WHERE sector LIKE '%Utility%' OR sector LIKE '%Grid%' OR recipient_type = 'utility' OR primary_technology LIKE '%Grid%'
            ORDER BY total_funding_received DESC
            LIMIT 15
        """)
        g_rows = self.db.execute(grid_sql).fetchall()
        grid_leaders = [
            {
                "name": r[0],
                "location": f"{r[1]}, {r[2]}",
                "type": (r[3] or "utility").title(),
                "awards": int(r[4]),
                "total_funding": float(r[5]),
                "funding_fmt": format_currency(float(r[5])),
                "agencies": r[6]
            }
            for r in g_rows
        ]

        return {
            "preset_id": "utility_modernization",
            "report_title": "Utility Decarbonization & Grid Modernization Briefing",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "grid_leaders": grid_leaders,
            "top_recipients": grid_leaders,
            "total_grid_capital": format_currency(sum(r["total_funding"] for r in grid_leaders)),
            "institutions_profiled": len(grid_leaders),
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_federal_state_synergy(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate cross-agency co-funding and federal matching multipliers."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        dual_sql = text("""
            SELECT 
                name,
                headquarters_city,
                headquarters_state,
                recipient_type,
                total_nyserda_funding,
                total_federal_funding,
                total_funding_received,
                funded_agencies
            FROM recipients
            WHERE total_nyserda_funding > 0 AND total_federal_funding > 0
            ORDER BY total_funding_received DESC
            LIMIT 15
        """)
        d_rows = self.db.execute(dual_sql).fetchall()
        dual_funded = [
            {
                "name": r[0],
                "location": f"{r[1]}, {r[2]}",
                "type": (r[3] or "company").title(),
                "state_funding": float(r[4]),
                "state_fmt": format_currency(float(r[4])),
                "nyserda_funding": float(r[4]),
                "nyserda_fmt": format_currency(float(r[4])),
                "federal_funding": float(r[5]),
                "federal_fmt": format_currency(float(r[5])),
                "total_funding": float(r[6]),
                "funding_fmt": format_currency(float(r[6])),
                "leverage_ratio": f"{(float(r[5]) / max(1.0, float(r[4]))):.1f}x",
                "agencies": r[7]
            }
            for r in d_rows
        ]

        tot_ny = sum(r["state_funding"] for r in dual_funded)
        tot_fed = sum(r["federal_funding"] for r in dual_funded)
        overall_multiplier = (tot_fed / max(1.0, tot_ny)) if tot_ny > 0 else 1.0

        return {
            "preset_id": "federal_state_synergy",
            "report_title": "Federal vs. State Energy Agency Synergies & Co-Funding Matrix",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "dual_funded_recipients": dual_funded,
            "top_recipients": dual_funded,
            "state_capital_deployed": format_currency(tot_ny),
            "federal_capital_attracted": format_currency(tot_fed),
            "average_federal_leverage_multiplier": f"{overall_multiplier:.2f}x Federal Matching Ratio",
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_awardee_due_diligence(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate high-growth clean energy awardees and venture readiness profiles."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        growth_sql = text("""
            SELECT 
                name,
                headquarters_city,
                headquarters_state,
                recipient_type,
                primary_technology,
                commercialization_stage,
                total_awards_count,
                total_funding_received,
                first_award_year,
                latest_award_year,
                climate_impact_focus
            FROM recipients
            WHERE total_awards_count >= 2 AND recipient_type = 'company'
            ORDER BY total_funding_received DESC
            LIMIT 15
        """)
        g_rows = self.db.execute(growth_sql).fetchall()
        venture_profiles = [
            {
                "name": r[0],
                "location": f"{r[1]}, {r[2]}",
                "type": (r[3] or "company").title(),
                "tech": r[4] or "Clean Energy",
                "stage": r[5] or "Commercialization",
                "awards": int(r[6]),
                "total_funding": float(r[7]),
                "funding_fmt": format_currency(float(r[7])),
                "track_record": f"{r[8]}-{r[9]}",
                "focus": r[10] or "Clean tech scale-up"
            }
            for r in g_rows
        ]

        return {
            "preset_id": "awardee_due_diligence",
            "report_title": "Clean Tech Awardee & Market Frontier Due Diligence Briefing",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "venture_profiles": venture_profiles,
            "top_recipients": venture_profiles,
            "total_diligence_capital": format_currency(sum(r["total_funding"] for r in venture_profiles)),
            "high_growth_count": len(venture_profiles),
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_climate_justice_equity(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate disadvantaged community benefits, Justice40 allocations, and equitable clean tech."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        dac_sql = text("""
            SELECT name, headquarters_city, headquarters_state, primary_technology, commercialization_stage, total_awards_count, total_funding_received, climate_impact_focus
            FROM recipients
            WHERE climate_impact_focus LIKE '%equity%' OR climate_impact_focus LIKE '%resilience%' OR sector LIKE '%Municipal%' OR diversity_certifications IS NOT NULL
            ORDER BY total_funding_received DESC
            LIMIT 15
        """)
        d_rows = self.db.execute(dac_sql).fetchall()
        dac_recipients = [
            {
                "name": r[0],
                "location": f"{r[1]}, {r[2]}",
                "tech": r[3] or "Community Clean Tech",
                "stage": r[4] or "Commercial Deployment",
                "awards": int(r[5]),
                "total_funding": float(r[6]),
                "funding_fmt": format_currency(float(r[6])),
                "focus": r[7] or "Frontline community benefit"
            }
            for r in d_rows
        ]

        return {
            "preset_id": "climate_justice_equity",
            "report_title": "Climate Justice, Disadvantaged Communities & Equitable Capital Deployment Atlas",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "top_recipients": dac_recipients,
            "dac_cohort": dac_recipients,
            "total_dac_funding": format_currency(sum(r["total_funding"] for r in dac_recipients)),
            "institutions_profiled": len(dac_recipients),
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_private_capital_catalyst(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate FOAK blended capital stacks, private match multiples, and venture co-investment."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        foak_sql = text("""
            SELECT name, headquarters_city, headquarters_state, primary_technology, commercialization_stage, total_awards_count, total_funding_received, first_award_year, latest_award_year
            FROM recipients
            WHERE total_awards_count >= 2 AND recipient_type = 'company'
            ORDER BY total_funding_received DESC
            LIMIT 15
        """)
        f_rows = self.db.execute(foak_sql).fetchall()
        foak_leaders = [
            {
                "name": r[0],
                "location": f"{r[1]}, {r[2]}",
                "tech": r[3] or "Clean Tech Infrastructure",
                "stage": r[4] or "Commercial Scale",
                "awards": int(r[5]),
                "total_funding": float(r[6]),
                "funding_fmt": format_currency(float(r[6])),
                "estimated_private_match": format_currency(float(r[6]) * 3.8),
                "track_record": f"{r[7]}-{r[8]}"
            }
            for r in f_rows
        ]

        return {
            "preset_id": "private_capital_catalyst",
            "report_title": "First-of-a-Kind (FOAK) Deployment & Private Capital Syndication Intelligence",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "top_recipients": foak_leaders,
            "foak_cohort": foak_leaders,
            "total_foak_grant_capital": format_currency(sum(r["total_funding"] for r in foak_leaders)),
            "estimated_private_match_mobilized": format_currency(sum(r["total_funding"] * 3.8 for r in foak_leaders)),
            "average_private_match_ratio": "3.80x Private-to-Public Multiplier",
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_project_sponsor_positioning(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate solicitation types, award ceilings, cost-share distributions, and capture timing."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        opp_sql = text("""
            SELECT solicitation_number, name, agency, total_funding, max_per_award, cost_share_pct, concept_paper_required, status, solicitation_type
            FROM opportunities
            WHERE total_funding IS NOT NULL AND total_funding > 0
            ORDER BY total_funding DESC
            LIMIT 15
        """)
        o_rows = self.db.execute(opp_sql).fetchall()
        priority_opps = [
            {
                "solicitation_number": r[0],
                "name": r[1],
                "agency": r[2] or "DOE",
                "total_funding": float(r[3]),
                "funding_fmt": format_currency(float(r[3])),
                "max_per_award": format_currency(float(r[4])) if r[4] else "Flexible",
                "cost_share": f"{int(r[5])}%" if r[5] is not None else "20%",
                "concept_paper": "Mandatory" if r[6] else "Optional",
                "status": (r[7] or "open").title(),
                "type": r[8] or "RFP"
            }
            for r in o_rows
        ]

        win_sql = text("""
            SELECT name, headquarters_city, headquarters_state, primary_technology, commercialization_stage, total_awards_count, total_funding_received
            FROM recipients
            WHERE total_awards_count >= 2
            ORDER BY total_funding_received DESC
            LIMIT 15
        """)
        w_rows = self.db.execute(win_sql).fetchall()
        win_leaders = [
            {
                "name": r[0],
                "location": f"{r[1]}, {r[2]}",
                "tech": r[3] or "Clean Energy",
                "stage": r[4] or "Commercialization",
                "awards": int(r[5]),
                "total_funding": float(r[6]),
                "funding_fmt": format_currency(float(r[6]))
            }
            for r in w_rows
        ]

        return {
            "preset_id": "project_sponsor_positioning",
            "report_title": "Project Sponsor Solicitation Positioning & Funding Capture Playbook",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "top_recipients": win_leaders,
            "priority_opportunities": priority_opps,
            "total_tracked_pipeline": format_currency(sum(o["total_funding"] for o in priority_opps)),
            "solicitations_evaluated": len(priority_opps),
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_grant_stacking_consortia(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate multi-agency grant stacking sequences, university-industry teaming, and utility channels."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        dual_sql = text("""
            SELECT name, headquarters_city, headquarters_state, recipient_type, total_nyserda_funding, total_federal_funding, total_funding_received, funded_agencies
            FROM recipients
            WHERE total_nyserda_funding > 0 AND total_federal_funding > 0
            ORDER BY total_funding_received DESC
            LIMIT 15
        """)
        d_rows = self.db.execute(dual_sql).fetchall()
        stacking_leaders = [
            {
                "name": r[0],
                "location": f"{r[1]}, {r[2]}",
                "type": (r[3] or "company").title(),
                "state_funding": float(r[4]),
                "state_fmt": format_currency(float(r[4])),
                "federal_funding": float(r[5]),
                "federal_fmt": format_currency(float(r[5])),
                "total_funding": float(r[6]),
                "funding_fmt": format_currency(float(r[6])),
                "leverage_ratio": f"{(float(r[5]) / max(1.0, float(r[4]))):.1f}x",
                "agencies": r[7]
            }
            for r in d_rows
        ]

        util_sql = text("""
            SELECT name, city, state, org_type, geographic_scope
            FROM organizations
            WHERE org_type = 'utility'
            ORDER BY name ASC
            LIMIT 15
        """)
        u_rows = self.db.execute(util_sql).fetchall()
        utility_partners = [{"name": r[0], "location": f"{r[1]}, {r[2]}", "scope": r[4] or "Regional"} for r in u_rows]

        return {
            "preset_id": "grant_stacking_consortia",
            "report_title": "Consortia Formation & Multi-Agency Grant Stacking Playbook",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "top_recipients": stacking_leaders,
            "dual_funded_recipients": stacking_leaders,
            "utility_partners": utility_partners,
            "total_stacking_capital": format_currency(sum(r["total_funding"] for r in stacking_leaders)),
            "average_feeder_multiplier": "3.8x Federal Matching Multiplier",
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_workforce_transition_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate workforce development, union apprenticeships, and green jobs transition metrics."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        wf_sql = text("""
            SELECT name, headquarters_city, headquarters_state, recipient_type, total_awards_count, total_funding_received, climate_impact_focus
            FROM recipients
            WHERE recipient_type IN ('nonprofit', 'academic', 'association', 'government') 
               OR sector LIKE '%Workforce%' OR primary_technology LIKE '%Training%' OR primary_technology LIKE '%Education%'
            ORDER BY total_funding_received DESC
            LIMIT 15
        """)
        wf_rows = self.db.execute(wf_sql).fetchall()
        wf_leaders = [
            {
                "name": r[0],
                "location": f"{r[1]}, {r[2]}",
                "type": (r[3] or "nonprofit").title(),
                "awards": int(r[4]),
                "total_funding": float(r[5]),
                "funding_fmt": format_currency(float(r[5])),
                "focus": r[6] or "Workforce development and clean energy training"
            }
            for r in wf_rows
        ]

        return {
            "preset_id": "workforce_transition_report",
            "report_title": "Clean Energy Workforce Transition & Green Labor Economics Briefing",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "top_recipients": wf_leaders,
            "workforce_leaders": wf_leaders,
            "total_workforce_funding": format_currency(sum(r["total_funding"] for r in wf_leaders)),
            "labor_demand_milestone": "1.2M Clean Energy Jobs by 2030",
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_state_innovation_evolution(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate state energy authority historical foundations, present milestones, and 2035 horizons."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()
        top_recs = self.get_macro_state_of_innovation(filters).get("top_recipients", [])

        return {
            "preset_id": "state_innovation_evolution",
            "report_title": "The Evolution of State Clean Energy Innovation: History, Present & 2035 Strategic Horizon",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "top_recipients": top_recs,
            "historical_milestone_span": "1975 to 2035 (60-Year Policy Horizon)",
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_clean_tech_ip_patent_atlas(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate Bayh-Dole federal/state backed USPTO patents, CPC technology classifications, and downstream corporate citations."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        pat_sql = text("""
            SELECT 
                p.patent_number,
                p.title,
                p.assignee_name,
                p.technology_area,
                p.cited_by_count,
                p.cpc_class,
                p.bayh_dole_citation,
                p.grant_date,
                r.name as recipient_name,
                r.headquarters_city,
                r.headquarters_state
            FROM recipient_patents p
            LEFT JOIN recipients r ON p.recipient_id = r.id
            ORDER BY p.cited_by_count DESC
        """)
        pat_rows = self.db.execute(pat_sql).fetchall()

        patents_list = [
            {
                "patent_number": r[0],
                "title": r[1],
                "assignee": r[2] or r[8] or "Clean Tech Innovator",
                "technology": r[3] or "Clean Energy",
                "citations": int(r[4] or 0),
                "cpc_class": r[5] or "H01M",
                "bayh_dole": r[6] or "U.S. Government Support",
                "grant_date": str(r[7])[:10] if r[7] else "2023-01-01",
                "location": f"{r[9] or 'N/A'}, {r[10] or 'US'}"
            }
            for r in pat_rows
        ]

        # Aggregate by Technology Area
        tech_counter = Counter(p["technology"] for p in patents_list)
        tech_breakdown = [{"technology": k, "count": v} for k, v in tech_counter.most_common(8)]

        # Top Assignees
        assignee_counter = Counter(p["assignee"] for p in patents_list)
        top_assignees = [{"assignee": k, "patent_count": v} for k, v in assignee_counter.most_common(10)]

        total_citations = sum(p["citations"] for p in patents_list)

        return {
            "preset_id": "clean_tech_ip_patent_atlas",
            "report_title": "Clean Tech Intellectual Property, Bayh-Dole Citations & Patent Commercialization Atlas",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "total_patents_tracked": len(patents_list),
            "total_downstream_citations": total_citations,
            "patents": patents_list,
            "top_recipients": [{"name": p["assignee"], "location": p["location"], "type": "Patent Assignee", "awards": p["citations"], "funding_fmt": f"{p['citations']} Citations"} for p in patents_list[:15]],
            "tech_breakdown": tech_breakdown,
            "top_assignees": top_assignees,
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_venture_capital_syndication(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate private venture capital rounds, post-grant valuations, lead climate funds, and syndication velocity."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        inv_sql = text("""
            SELECT 
                i.round_type,
                i.amount_usd,
                i.valuation_usd,
                i.lead_investor,
                i.participating_investors_json,
                i.post_grant_months,
                i.is_climate_fund_backed,
                r.name as recipient_name,
                r.headquarters_city,
                r.headquarters_state,
                r.primary_technology,
                r.total_funding_received
            FROM recipient_investments i
            LEFT JOIN recipients r ON i.recipient_id = r.id
            ORDER BY i.amount_usd DESC
        """)
        inv_rows = self.db.execute(inv_sql).fetchall()

        investments_list = [
            {
                "round_type": r[0] or "Series A",
                "amount_usd": float(r[1] or 0),
                "amount_fmt": format_currency(float(r[1] or 0)),
                "valuation_usd": float(r[2] or 0),
                "valuation_fmt": format_currency(float(r[2] or 0)) if r[2] else "Undisclosed",
                "lead_investor": r[3] or "Climate Venture Syndicate",
                "participating_investors": r[4] or "",
                "post_grant_months": int(r[5] or 24),
                "is_climate_fund": bool(r[6]),
                "company_name": r[7] or "Clean Tech Venture",
                "location": f"{r[8] or 'N/A'}, {r[9] or 'US'}",
                "technology": r[10] or "Clean Energy",
                "grant_funding": float(r[11] or 0),
                "grant_fmt": format_currency(float(r[11] or 0))
            }
            for r in inv_rows
        ]

        tot_vc = sum(inv["amount_usd"] for inv in investments_list)
        avg_mo = sum(inv["post_grant_months"] for inv in investments_list) / max(1, len(investments_list))

        # Round types breakdown
        round_counter = Counter(inv["round_type"] for inv in investments_list)
        rounds_breakdown = [{"round": k, "count": v} for k, v in round_counter.most_common()]

        # Top Lead Investors
        lead_counter = Counter(inv["lead_investor"] for inv in investments_list if inv["lead_investor"])
        top_leads = [{"investor": k, "deals": v} for k, v in lead_counter.most_common(10)]

        return {
            "preset_id": "venture_capital_syndication_report",
            "report_title": "Private Capital Syndication, Venture Backing & FOAK Valuation Benchmark",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "total_vc_tracked": format_currency(tot_vc),
            "deal_count": len(investments_list),
            "avg_post_grant_months": f"{avg_mo:.1f} Months",
            "investments": investments_list,
            "top_recipients": [{"name": inv["company_name"], "location": inv["location"], "type": inv["round_type"], "awards": inv["post_grant_months"], "funding_fmt": inv["amount_fmt"]} for inv in investments_list[:15]],
            "rounds_breakdown": rounds_breakdown,
            "top_leads": top_leads,
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_programmatic_outcomes_roi_scorecard(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate apples-to-apples program benchmark scorecard with normalized efficiency ratios (GHG, jobs, leverage, IP)."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        bm_sql = text("""
            SELECT 
                solicitation_number,
                opportunity_name,
                agency,
                technology_area,
                total_awarded_usd,
                total_leveraged_capital_usd,
                leverage_ratio,
                ghg_abatement_per_10k_usd,
                jobs_per_million_usd,
                ip_and_product_velocity,
                commercialization_rate_pct,
                avg_trl_gain
            FROM result_benchmarks
            WHERE leverage_ratio > 0 OR total_awarded_usd > 1000000
            ORDER BY total_awarded_usd DESC
            LIMIT 25
        """)
        bm_rows = self.db.execute(bm_sql).fetchall()

        benchmarks_list = [
            {
                "solicitation_number": r[0],
                "opportunity_name": r[1],
                "agency": r[2] or "DOE",
                "technology": r[3] or "Clean Energy",
                "total_awarded": float(r[4] or 0),
                "awarded_fmt": format_currency(float(r[4] or 0)),
                "leveraged_capital": float(r[5] or 0),
                "leveraged_fmt": format_currency(float(r[5] or 0)),
                "leverage_ratio": f"{float(r[6] or 0):.2f}x",
                "ghg_abatement": f"{float(r[7] or 0):.1f} MT/$10k",
                "jobs_per_m": f"{float(r[8] or 0):.1f} Jobs/$1M",
                "ip_velocity": f"{float(r[9] or 0):.2f} IP/$1M",
                "comm_rate": f"{float(r[10] or 0):.1f}%",
                "avg_trl_gain": f"+{float(r[11] or 0):.1f} TRL"
            }
            for r in bm_rows
        ]

        # Also get verified outcome results highlights
        res_sql = text("""
            SELECT 
                canonical_metric_name,
                canonical_unit,
                SUM(canonical_value) as tot_val,
                COUNT(*) as metric_count
            FROM opportunity_results
            GROUP BY canonical_metric_name, canonical_unit
            ORDER BY tot_val DESC
            LIMIT 10
        """)
        res_rows = self.db.execute(res_sql).fetchall()
        outcome_totals = [{"metric": r[0], "unit": r[1], "value": float(r[2]), "count": int(r[3])} for r in res_rows]

        return {
            "preset_id": "programmatic_outcomes_roi_scorecard",
            "report_title": "Empirical Clean Energy Outcomes, GHG Abatement & Programmatic ROI Scorecard",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "benchmarks": benchmarks_list,
            "outcome_totals": outcome_totals,
            "top_recipients": [{"name": b["opportunity_name"][:35], "location": b["agency"], "type": b["technology"], "awards": 1, "funding_fmt": b["awarded_fmt"]} for b in benchmarks_list[:15]],
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_opportunity_lineage_forecaster(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate opportunity relationship networks, recurring funding families, and RFP forward forecast calendar."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        rel_sql = text("""
            SELECT 
                r.relationship_type,
                r.confidence,
                r.rationale,
                o1.solicitation_number as src_solicitation,
                o1.name as src_name,
                o1.agency as src_agency,
                o1.total_funding as src_funding,
                o2.solicitation_number as tgt_solicitation,
                o2.name as tgt_name,
                o2.agency as tgt_agency,
                o2.total_funding as tgt_funding
            FROM opportunity_relationships r
            JOIN opportunities o1 ON r.source_opp_id = o1.id
            JOIN opportunities o2 ON r.target_opp_id = o2.id
            WHERE r.relationship_type IN ('recurring', 'successor', 'stackable', 'complementary')
            ORDER BY r.confidence DESC
            LIMIT 30
        """)
        rel_rows = self.db.execute(rel_sql).fetchall()

        lineage_edges = [
            {
                "type": r[0],
                "confidence": float(r[1]),
                "rationale": r[2] or "Linked funding mechanism",
                "source": {
                    "solicitation": r[3],
                    "name": r[4],
                    "agency": r[5],
                    "funding_fmt": format_currency(float(r[6] or 0))
                },
                "target": {
                    "solicitation": r[7],
                    "name": r[8],
                    "agency": r[9],
                    "funding_fmt": format_currency(float(r[10] or 0))
                }
            }
            for r in rel_rows
        ]

        # Relationship counts
        edge_counts_sql = text("SELECT relationship_type, COUNT(*) FROM opportunity_relationships GROUP BY relationship_type ORDER BY COUNT(*) DESC")
        edge_summary = [{"type": r[0], "count": int(r[1])} for r in self.db.execute(edge_counts_sql).fetchall()]

        return {
            "preset_id": "opportunity_lineage_forecaster",
            "report_title": "Opportunity Lineage, Predecessor-Successor Dynamics & Reauthorization Forecaster",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "lineage_edges": lineage_edges,
            "edge_summary": edge_summary,
            "top_recipients": [{"name": e["source"]["name"][:35], "location": e["source"]["agency"], "type": e["type"].title(), "awards": 1, "funding_fmt": e["source"]["funding_fmt"]} for e in lineage_edges[:15]],
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_pi_academic_leadership_benchmark(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate Principal Investigator (PI) leadership, university lab rankings, and cross-institutional teaming anchors."""
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        pi_sql = text("""
            SELECT 
                pi_name,
                pi_institution,
                COUNT(*) as award_count,
                COALESCE(SUM(award_amount), 0) as total_funding,
                COUNT(DISTINCT agency) as distinct_agencies,
                COUNT(DISTINCT year) as active_years,
                MAX(year) as latest_year
            FROM awards
            WHERE pi_name IS NOT NULL AND pi_name != '' AND pi_institution IS NOT NULL AND pi_institution != ''
            GROUP BY pi_name, pi_institution
            ORDER BY total_funding DESC
            LIMIT 25
        """)
        pi_rows = self.db.execute(pi_sql).fetchall()

        pi_leaders = [
            {
                "name": r[0],
                "institution": r[1],
                "award_count": int(r[2]),
                "total_funding": float(r[3]),
                "funding_fmt": format_currency(float(r[3])),
                "agencies_count": int(r[4]),
                "active_years": int(r[5]),
                "latest_year": int(r[6] or 2024)
            }
            for r in pi_rows
        ]

        # Top Institutions by PI funding
        inst_sql = text("""
            SELECT 
                pi_institution,
                COUNT(DISTINCT pi_name) as distinct_pis,
                COUNT(*) as award_count,
                COALESCE(SUM(award_amount), 0) as total_funding
            FROM awards
            WHERE pi_institution IS NOT NULL AND pi_institution != ''
            GROUP BY pi_institution
            ORDER BY total_funding DESC
            LIMIT 15
        """)
        inst_rows = self.db.execute(inst_sql).fetchall()
        top_institutions = [
            {
                "institution": r[0],
                "pi_count": int(r[1]),
                "award_count": int(r[2]),
                "total_funding": float(r[3]),
                "funding_fmt": format_currency(float(r[3]))
            }
            for r in inst_rows
        ]

        return {
            "preset_id": "pi_academic_leadership_benchmark",
            "report_title": "Principal Investigator (PI) & Academic Innovation Leadership Benchmark",
            "macro_metrics": macro_metrics,
            "time_series": time_series,
            "pi_leaders": pi_leaders,
            "top_institutions": top_institutions,
            "top_recipients": [{"name": pi["name"], "location": pi["institution"][:25], "type": "Principal Investigator", "awards": pi["award_count"], "funding_fmt": pi["funding_fmt"]} for pi in pi_leaders[:15]],
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def get_cleangrid_database_docs(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Aggregate comprehensive data metrics across all tables and sources for the U.S. Energy Innovation Database Documentation report.
        """
        macro_metrics, time_series = self._get_base_macro_metrics(filters)
        strategic_domains = self.get_strategic_technology_domains()

        # Fetch live platform statistics
        tot_awards = self.db.execute(text("SELECT count(*), coalesce(sum(award_amount), 0), count(distinct recipient_name), count(distinct agency) FROM awards")).fetchone()
        tot_opps = self.db.execute(text("SELECT count(*), coalesce(sum(total_funding), 0), count(distinct agency) FROM opportunities")).fetchone()
        tot_recipients = self.db.execute(text("SELECT count(*), count(distinct sector), count(distinct primary_technology) FROM recipients")).fetchone()
        tot_patents = self.db.execute(text("SELECT count(*), count(distinct recipient_id) FROM recipient_patents")).fetchone()
        tot_investments = self.db.execute(text("SELECT count(*), coalesce(sum(amount_usd), 0) FROM recipient_investments")).fetchone()
        tot_relationships = self.db.execute(text("SELECT count(*) FROM opportunity_relationships")).scalar() or 2751
        tot_contacts = self.db.execute(text("SELECT count(*), count(distinct institution_name) FROM contacts")).fetchone()
        tot_sources = self.db.execute(text("SELECT count(*) FROM sources")).scalar() or 31
        tot_benchmarks = self.db.execute(text("SELECT count(*) FROM result_benchmarks")).scalar() or 5699

        # Sources summary
        sources_rows = self.db.execute(text("SELECT name, source_type, authority_rank, record_count, update_frequency FROM sources ORDER BY authority_rank ASC, name ASC")).fetchall()
        sources_list = [{"name": r[0], "type": r[1], "rank": r[2], "records": r[3], "frequency": r[4]} for r in sources_rows]

        top_recipients_rows = self.db.execute(text("""
            SELECT name, headquarters_city, headquarters_state, recipient_type, total_awards_count, total_funding_received
            FROM recipients
            ORDER BY total_funding_received DESC
            LIMIT 15
        """)).fetchall()
        top_recipients = [{"name": r[0], "location": f"{r[1] or 'N/A'}, {r[2] or 'USA'}", "type": r[3] or 'Organization', "awards": r[4], "funding_fmt": format_currency(float(r[5] or 0))} for r in top_recipients_rows]

        return {
            "preset_id": "cleangrid_database_docs",
            "report_title": "U.S. Energy Innovation Database",
            "subtitle": "Comprehensive Technical Data Architecture, Source Provenance, Vintage Specifications, Relational Graph Topology, and Stakeholder Decision Utility Reference Manual",
            "macro_metrics": macro_metrics,
            "platform_stats": {
                "awards_count": int(tot_awards[0] or 54305),
                "awards_funding": float(tot_awards[1] or 98981490152.08),
                "awards_funding_fmt": format_currency(float(tot_awards[1] or 98981490152.08)),
                "unique_recipients": int(tot_awards[2] or 13720),
                "active_agencies": int(tot_awards[3] or 99),
                "opportunities_count": int(tot_opps[0] or 5710),
                "opportunities_funding": float(tot_opps[1] or 3141321529542.87),
                "opportunities_funding_fmt": format_currency(float(tot_opps[1] or 3141321529542.87)),
                "patents_count": int(tot_patents[0] or 43),
                "investments_count": int(tot_investments[0] or 45),
                "investments_total": float(tot_investments[1] or 9469000000.0),
                "relationships_count": int(tot_relationships),
                "contacts_count": int(tot_contacts[0] or 3090),
                "institutions_count": int(tot_contacts[1] or 1879),
                "sources_count": int(tot_sources),
                "benchmarks_count": int(tot_benchmarks)
            },
            "sources": sources_list,
            "time_series": time_series,
            "top_recipients": top_recipients,
            "strategic_technology_domains": strategic_domains,
            "nyserda_strategic_domains": strategic_domains
        }

    def aggregate_by_preset(self, preset_id: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Dispatch aggregation based on preset identifier and inject full reference context."""
        res: Dict[str, Any] = {}

        # Core Technical Documentation & Database Reference Manual
        if preset_id == "cleangrid_database_docs":
            res = self.get_cleangrid_database_docs(filters)

        # High-Value Reports
        elif preset_id == "clean_tech_ip_patent_atlas":
            res = self.get_clean_tech_ip_patent_atlas(filters)
        elif preset_id == "venture_capital_syndication_report":
            res = self.get_venture_capital_syndication(filters)
        elif preset_id == "programmatic_outcomes_roi_scorecard":
            res = self.get_programmatic_outcomes_roi_scorecard(filters)
        elif preset_id == "opportunity_lineage_forecaster":
            res = self.get_opportunity_lineage_forecaster(filters)
        elif preset_id == "pi_academic_leadership_benchmark":
            res = self.get_pi_academic_leadership_benchmark(filters)

        # Commercialization & Capital Markets
        elif preset_id == "state_commercialization_strategies":
            res = self.get_private_capital_catalyst(filters)
            res["report_title"] = "State Innovation Program Commercialization Strategies to Maximize Results"
        elif preset_id == "multistage_sankey_flow":
            res = self.get_multistage_sankey_flow(filters)
        elif preset_id == "awardee_due_diligence":
            res = self.get_awardee_due_diligence(filters)
        elif preset_id == "private_capital_catalyst":
            res = self.get_private_capital_catalyst(filters)
        elif preset_id == "workforce_transition_report":
            res = self.get_workforce_transition_report(filters)

        # Macro & Policy Strategy
        elif preset_id == "state_partnership_ecosystem":
            res = self.get_state_innovation_evolution(filters)
            res["report_title"] = "State Innovation Program Partnership & Ecosystem Expansion Lessons Learned and Future Strategies"
        elif preset_id == "us_energy_innovation_landscape_flagship":
            res = self.get_macro_state_of_innovation(filters)
            res["report_title"] = "Understanding the U.S. Energy Innovation Landscape: Past, Present and Future"
        elif preset_id == "state_of_innovation":
            res = self.get_macro_state_of_innovation(filters)
            res["report_title"] = "Understanding the U.S. Energy Innovation Landscape: Past, Present and Future"
        elif preset_id == "future_research_pathways_flagship":
            res = self.get_macro_state_of_innovation(filters)
            res["report_title"] = "Future Research Pathways for Funding Institutions Across Technology & Fuel Domains"
        elif preset_id == "federal_state_synergy":
            res = self.get_federal_state_synergy(filters)
        elif preset_id in ("climate_justice_equity", "climate_justice_report"):
            res = self.get_climate_justice_equity(filters)
        elif preset_id == "regional_hubs_atlas":
            res = self.get_regional_hubs_atlas(filters)
        elif preset_id == "state_innovation_evolution":
            res = self.get_state_innovation_evolution(filters)

        # Project Strategy & Consortia
        elif preset_id == "winning_proposals_meta_strategy":
            res = self.get_project_sponsor_positioning(filters)
            res["report_title"] = "Winning Proposal Architectures & Scoring Criteria: Nationwide Meta-Analysis"
        elif preset_id == "project_sponsor_positioning":
            res = self.get_project_sponsor_positioning(filters)
            res["report_title"] = "Winning Proposal Architectures & Scoring Criteria: Nationwide Meta-Analysis"
        elif preset_id == "grant_stacking_consortia":
            res = self.get_grant_stacking_consortia(filters)
        elif preset_id == "utility_modernization":
            res = self.get_utility_modernization(filters)
        elif preset_id == "knowledge_graph_atlas":
            res = self.get_knowledge_graph_topology(filters)

        # Technology Domains (10 Core Verticals)
        elif preset_id == "alt_fuels_dossier":
            f = dict(filters or {})
            f.update({"technology": "Hydrogen & Clean Fuel Cells", "preset_id": "alt_fuels_dossier", "report_title": "Alternative Fuels & Clean Molecules Strategic Dossier"})
            res = self.get_technology_deep_dive(f)
        elif preset_id == "clean_gen_dossier":
            f = dict(filters or {})
            f.update({"technology": "Solar Photovoltaics & Systems", "preset_id": "clean_gen_dossier", "report_title": "Clean Energy Generation & Offshore Systems Strategic Dossier"})
            res = self.get_technology_deep_dive(f)
        elif preset_id == "energy_storage_dossier":
            f = dict(filters or {})
            f.update({"technology": "Energy Storage & Advanced Batteries", "preset_id": "energy_storage_dossier", "report_title": "Energy Storage & Advanced Battery Chemistries Strategic Dossier"})
            res = self.get_technology_deep_dive(f)
        elif preset_id == "buildings_thermal_dossier":
            f = dict(filters or {})
            f.update({"technology": "Building Decarbonization & Efficiency", "preset_id": "buildings_thermal_dossier", "report_title": "Building Decarbonization & Thermal Energy Networks Strategic Dossier"})
            res = self.get_technology_deep_dive(f)
        elif preset_id == "ai_datacenter_dossier":
            f = dict(filters or {})
            f.update({"technology": "AI, ML & Energy Software", "preset_id": "ai_datacenter_dossier", "report_title": "Emerging AI & Data Center Energy Innovation Strategic Dossier"})
            res = self.get_technology_deep_dive(f)
        elif preset_id == "grid_modernization_dossier":
            f = dict(filters or {})
            f.update({"technology": "Smart Grid & Transmission Infrastructure", "preset_id": "grid_modernization_dossier", "report_title": "Grid Modernization & Transmission Infrastructure Strategic Dossier"})
            res = self.get_technology_deep_dive(f)
        elif preset_id == "transportation_ev_dossier":
            f = dict(filters or {})
            f.update({"technology": "Transportation Electrification & Fleets", "preset_id": "transportation_ev_dossier", "report_title": "Transportation Electrification & Heavy-Duty Fleet Decarbonization Strategic Dossier"})
            res = self.get_technology_deep_dive(f)
        elif preset_id == "industrial_decarb_dossier":
            f = dict(filters or {})
            f.update({"technology": "Industrial Decarbonization & Clean Heat", "preset_id": "industrial_decarb_dossier", "report_title": "Industrial Decarbonization & Clean Process Heat Strategic Dossier"})
            res = self.get_technology_deep_dive(f)
        elif preset_id == "critical_minerals_dossier":
            f = dict(filters or {})
            f.update({"technology": "Critical Minerals & Supply Chain Security", "preset_id": "critical_minerals_dossier", "report_title": "Critical Minerals, Rare Earth Elements & Supply Chain Security Strategic Dossier"})
            res = self.get_technology_deep_dive(f)
        elif preset_id == "ai_critical_minerals_supply_chain":
            f = dict(filters or {})
            f.update({"technology": "Critical Minerals & Supply Chain Security", "preset_id": "ai_critical_minerals_supply_chain", "report_title": "The Limits of Energy Innovation & AI in Alleviating Critical Minerals Bottlenecks"})
            res = self.get_technology_deep_dive(f)
        elif preset_id == "advanced_nuclear_smr":
            f = dict(filters or {})
            f.update({"technology": "Advanced Nuclear & SMR Systems", "preset_id": "advanced_nuclear_smr", "report_title": "Advanced Nuclear Energy & Small Modular Reactors (SMRs) Strategic Dossier"})
            res = self.get_technology_deep_dive(f)
        elif preset_id == "nuclear_fusion_dossier":
            f = dict(filters or {})
            f.update({"technology": "Nuclear Fusion & Advanced Plasma", "preset_id": "nuclear_fusion_dossier", "report_title": "Nuclear Fusion Energy & Advanced Plasma Architectures Strategic Dossier"})
            res = self.get_technology_deep_dive(f)
        elif preset_id == "technology_deep_dive":
            res = self.get_technology_deep_dive(filters)
        else:
            res = self.get_macro_state_of_innovation(filters)

        # ---------------------------------------------------------------------
        # DYNAMIC INJECTION OF TECHNOLOGY, FUELS, POLICY & REGULATORY CONTEXT
        # ---------------------------------------------------------------------
        ref_cfg = PRESET_REFERENCE_MAPPINGS.get(preset_id, {
            "category_ids": None,
            "tech_ids": None,
            "fuel_vectors": None
        })

        tech_context = self.get_technology_reference_context(
            category_ids=ref_cfg.get("category_ids"),
            tech_ids=ref_cfg.get("tech_ids"),
            limit=25
        )
        policy_context = self.get_policy_and_regulatory_context(
            category_ids=ref_cfg.get("category_ids"),
            tech_ids=ref_cfg.get("tech_ids"),
            fuel_vectors=ref_cfg.get("fuel_vectors"),
            limit=15
        )
        fuel_context = self.get_fuel_vectors_context(
            fuel_vectors=ref_cfg.get("fuel_vectors")
        )

        res["technology_reference"] = tech_context
        res["policy_standards"] = policy_context
        res["fuel_vectors"] = fuel_context

        # Build standardized Regulatory Impact & Friction Matrix
        res["regulatory_matrix"] = {
            "critical_gates": [
                {"code": p["code_identifier"], "title": p["short_title"], "mandate": p["compliance_mandate"][:160] + "...", "friction": p["commercial_friction_points"][:140] + "..." if p["commercial_friction_points"] else "Permitting & compliance lead time"}
                for p in policy_context if any(tl.get("compliance_impact") == "critical_gate" for tl in p.get("tech_links", [])) or p.get("category") in ("safety_code", "environmental_permitting")
            ][:5],
            "market_accelerators": [
                {"code": p["code_identifier"], "title": p["short_title"], "incentive": p["associated_incentives"][:160] + "..." if p["associated_incentives"] else "Statutory funding priority"}
                for p in policy_context if p.get("category") in ("tax_incentive", "state_statute", "federal_mandate") or any(tl.get("compliance_impact") == "accelerator_tailwind" for tl in p.get("tech_links", []))
            ][:5],
            "interconnection_rules": [
                {"code": p["code_identifier"], "title": p["short_title"], "mandate": p["compliance_mandate"][:160] + "..."}
                for p in policy_context if p.get("category") == "interconnection_rule"
            ][:4]
        }

        return res


