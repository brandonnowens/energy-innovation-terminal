"""
Dispatcher for Specialized executive strategic monograph Generators.
Maps each of the 17 preset IDs to its dedicated Python generator module.
"""

import io
from typing import Callable, Dict, Optional, Any
from sqlalchemy.orm import Session

from .gen_macro_state_of_innovation import generate_macro_state_of_innovation_monograph
from .gen_federal_state_synergy import generate_federal_state_synergy_monograph
from .gen_state_innovation_evolution import generate_state_innovation_evolution_monograph
from .gen_alt_fuels import generate_alt_fuels_monograph
from .gen_clean_gen import generate_clean_gen_monograph
from .gen_energy_storage import generate_energy_storage_monograph
from .gen_grid_modernization import generate_grid_modernization_monograph
from .gen_buildings_thermal import generate_buildings_thermal_monograph
from .gen_ai_datacenter import generate_ai_datacenter_monograph
from .gen_transportation_ev import generate_transportation_ev_monograph
from .gen_industrial_decarb import generate_industrial_decarb_monograph
from .gen_critical_minerals import generate_critical_minerals_monograph
from .gen_advanced_nuclear import generate_advanced_nuclear_monograph
from .gen_knowledge_graph import generate_knowledge_graph_monograph
from .gen_regional_hubs import generate_regional_hubs_monograph
from .gen_climate_justice import generate_climate_justice_monograph
from .gen_multistage_sankey import generate_multistage_sankey_monograph
from .gen_utility_modernization import generate_utility_modernization_monograph
from .gen_awardee_due_diligence import generate_awardee_due_diligence_monograph
from .gen_workforce_transition import generate_workforce_transition_monograph
from .gen_private_capital_catalyst import generate_private_capital_catalyst_monograph
from .gen_project_sponsor_positioning import generate_project_sponsor_positioning_monograph
from .gen_grant_stacking_consortia import generate_grant_stacking_consortia_monograph
from .gen_winning_proposals_strategy import generate_winning_proposals_strategy_monograph
from .gen_us_energy_innovation_landscape import generate_us_energy_innovation_landscape_monograph
from .gen_future_research_pathways import generate_future_research_pathways_monograph
from .gen_ai_critical_minerals_supply_chain import generate_ai_critical_minerals_supply_chain_monograph
from .gen_clean_tech_ip_patent_atlas import generate_clean_tech_ip_patent_atlas_monograph
from .gen_venture_capital_syndication import generate_venture_capital_syndication_monograph
from .gen_programmatic_outcomes_roi_scorecard import generate_programmatic_outcomes_roi_scorecard_monograph
from .gen_opportunity_lineage_forecaster import generate_opportunity_lineage_forecaster_monograph
from .gen_pi_academic_leadership_benchmark import generate_pi_academic_leadership_benchmark_monograph
from .gen_state_commercialization_strategies import generate_state_commercialization_strategies_monograph
from .gen_state_partnership_ecosystem import generate_state_partnership_ecosystem_monograph
from .gen_cleangrid_database_docs import generate_cleangrid_database_docs_monograph
from .gen_nuclear_fusion import generate_nuclear_fusion_monograph
from .gen_top5_breakthrough_innovations import generate_top5_breakthrough_innovations_monograph

GENERATORS_MAP: Dict[str, Callable[[Session, io.BytesIO], None]] = {
    # 0. Core Technical Architecture & Database Reference
    "cleangrid_database_docs": generate_cleangrid_database_docs_monograph,

    # 1. Macro & Policy Strategy (Flagship Strategic Briefings & Institutional Blueprints)
    "top5_breakthrough_innovations": generate_top5_breakthrough_innovations_monograph,
    "state_partnership_ecosystem": generate_state_partnership_ecosystem_monograph,
    "future_research_pathways_flagship": generate_future_research_pathways_monograph,
    "us_energy_innovation_landscape_flagship": generate_us_energy_innovation_landscape_monograph,
    "programmatic_outcomes_roi_scorecard": generate_programmatic_outcomes_roi_scorecard_monograph,
    "federal_state_synergy": generate_federal_state_synergy_monograph,
    "climate_justice_equity": generate_climate_justice_monograph,
    "regional_hubs_atlas": generate_regional_hubs_monograph,
    "state_innovation_evolution": generate_state_innovation_evolution_monograph,
    "state_of_innovation": generate_us_energy_innovation_landscape_monograph,  # Consolidated into Flagship

    # 2. Commercialization & Capital Markets (Actionable Diagnostics & Strategies)
    "state_commercialization_strategies": generate_state_commercialization_strategies_monograph,
    "clean_tech_ip_patent_atlas": generate_clean_tech_ip_patent_atlas_monograph,
    "venture_capital_syndication_report": generate_venture_capital_syndication_monograph,
    "private_capital_catalyst": generate_private_capital_catalyst_monograph,
    "multistage_sankey_flow": generate_multistage_sankey_monograph,
    "awardee_due_diligence": generate_awardee_due_diligence_monograph,
    "workforce_transition_report": generate_workforce_transition_monograph,

    # 3. Project Strategy & Consortia (4 Actionable Playbooks)
    "winning_proposals_meta_strategy": generate_winning_proposals_strategy_monograph,
    "grant_stacking_consortia": generate_grant_stacking_consortia_monograph,
    "opportunity_lineage_forecaster": generate_opportunity_lineage_forecaster_monograph,
    "pi_academic_leadership_benchmark": generate_pi_academic_leadership_benchmark_monograph,
    "project_sponsor_positioning": generate_winning_proposals_strategy_monograph,  # Consolidated into Winning Proposals
    "utility_modernization": generate_utility_modernization_monograph,
    "knowledge_graph_atlas": generate_knowledge_graph_monograph,

    # 4. Technology Domains (Core Vertical Deep-Dives)
    "alt_fuels_dossier": generate_alt_fuels_monograph,
    "clean_gen_dossier": generate_clean_gen_monograph,
    "energy_storage_dossier": generate_energy_storage_monograph,
    "grid_modernization_dossier": generate_grid_modernization_monograph,
    "buildings_thermal_dossier": generate_buildings_thermal_monograph,
    "ai_datacenter_dossier": generate_ai_datacenter_monograph,
    "transportation_ev_dossier": generate_transportation_ev_monograph,
    "industrial_decarb_dossier": generate_industrial_decarb_monograph,
    "critical_minerals_dossier": generate_critical_minerals_monograph,
    "ai_critical_minerals_supply_chain": generate_ai_critical_minerals_supply_chain_monograph,
    "advanced_nuclear_smr": generate_advanced_nuclear_monograph,
    "nuclear_fusion_dossier": generate_nuclear_fusion_monograph,
}

from app.engine.ai_report_author import author_report_with_openai, generate_deterministic_narrative
from app.engine.report_aggregator import ReportContextAggregator

def generate_specialized_monograph(
    preset_id: str,
    db: Session,
    output_stream: io.BytesIO,
    openai_api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    force_refresh: bool = False
) -> None:
    """Routes generation request to the dedicated generator function with live or bespoke narrative injection."""
    generator = GENERATORS_MAP.get(preset_id, generate_macro_state_of_innovation_monograph)
    
    # 1. Author or retrieve narrative
    narrative = None
    if custom_prompt or (force_refresh and openai_api_key):
        try:
            aggregator = ReportContextAggregator(db)
            context = aggregator.aggregate_by_preset(preset_id)
            narrative = author_report_with_openai(
                preset_id=preset_id,
                context=context,
                custom_prompt=custom_prompt,
                api_key=openai_api_key,
                model_name=model_name or "gpt-4o",
                force_refresh=force_refresh
            )
        except Exception as e:
            import logging
            logging.getLogger("Dispatcher").warning(f"Error pre-authoring narrative for {preset_id}: {e}")
            narrative = generate_deterministic_narrative(preset_id, {})
    else:
        # Fast path: instant bespoke domain-specific deterministic narrative (0.000s execution)
        narrative = generate_deterministic_narrative(preset_id, {})

    # 2. Invoke generator passing narrative
    try:
        import inspect
        sig = inspect.signature(generator)
        if 'narrative' in sig.parameters:
            generator(db, output_stream, narrative=narrative)
        elif 'openai_api_key' in sig.parameters:
            generator(db, output_stream, openai_api_key=openai_api_key, model_name=model_name, custom_prompt=custom_prompt)
        else:
            generator(db, output_stream)
    except Exception as e:
        import logging
        logging.getLogger("Dispatcher").error(f"Generator execution failed for {preset_id} with narrative: {e}. Retrying with default fallback.")
        generator(db, output_stream)

