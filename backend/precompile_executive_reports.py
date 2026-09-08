"""
Pre-compilation and verification script for all Executive Strategic Monographs.
Compiles all 17 publication dossiers into backend/data/reports_archive/ using
empirical database queries, ReportLab vector graphics, and the Master Technology Reference Database.
"""

import os
import io
import sys
import datetime
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal
from app.engine.specialized_generators.dispatcher import GENERATORS_MAP

ARCHIVE_DIR = Path("backend/data/reports_archive")
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# Preset ID to output filename mapping
PRESET_FILENAME_MAP = {
    # 0. Core Technical Architecture & Database Reference
    "cleangrid_database_docs": "executive-report-cleangrid-database-docs",

    # 1. Macro & Policy Strategy
    "state_partnership_ecosystem": "executive-report-state-partnership-ecosystem",
    "future_research_pathways_flagship": "executive-report-future-research-pathways-flagship",
    "us_energy_innovation_landscape_flagship": "executive-report-us-energy-innovation-landscape",
    "programmatic_outcomes_roi_scorecard": "executive-report-programmatic-outcomes-roi-scorecard",
    "federal_state_synergy": "executive-report-federal-state-synergy",
    "climate_justice_equity": "executive-report-climate-justice-equity",
    "regional_hubs_atlas": "executive-report-regional-hubs-atlas",
    "state_innovation_evolution": "executive-report-state-innovation-evolution",

    # 2. Commercialization & Capital Markets
    "state_commercialization_strategies": "executive-report-state-commercialization-strategies",
    "clean_tech_ip_patent_atlas": "executive-report-clean-tech-ip-patent-atlas",
    "venture_capital_syndication_report": "executive-report-venture-capital-syndication",
    "private_capital_catalyst": "executive-report-private-capital-catalyst",
    "multistage_sankey_flow": "executive-report-multistage-sankey-flow",
    "awardee_due_diligence": "executive-report-awardee-due-diligence",
    "workforce_transition_report": "executive-report-workforce-transition",

    # 3. Project Strategy & Consortia
    "winning_proposals_meta_strategy": "executive-report-winning-proposals-strategy",
    "grant_stacking_consortia": "executive-report-grant-stacking-consortia",
    "opportunity_lineage_forecaster": "executive-report-opportunity-lineage-forecaster",
    "pi_academic_leadership_benchmark": "executive-report-pi-academic-leadership-benchmark",
    "utility_modernization": "executive-report-utility-modernization",
    "knowledge_graph_atlas": "executive-report-knowledge-graph-atlas",

    # 4. Technology Domains
    "clean_gen_dossier": "executive-report-clean-gen-dossier",
    "energy_storage_dossier": "executive-report-energy-storage-dossier",
    "alt_fuels_dossier": "executive-report-alt-fuels-dossier",
    "advanced_nuclear_smr": "executive-report-advanced-nuclear-smr",
    "grid_modernization_dossier": "executive-report-grid-modernization-dossier",
    "buildings_thermal_dossier": "executive-report-buildings-thermal-dossier",
    "industrial_decarb_dossier": "executive-report-industrial-decarb-dossier",
    "critical_minerals_dossier": "executive-report-critical-minerals-dossier",
    "ai_critical_minerals_supply_chain": "executive-report-ai-critical-minerals-supply-chain",
    "ai_datacenter_dossier": "executive-report-ai-datacenter-dossier",
    "transportation_ev_dossier": "executive-report-transportation-ev",
}

def precompile_all_executive_reports():
    print("=" * 75)
    print("PRE-COMPILING ALL EXECUTIVE STRATEGIC MONOGRAPHS WITH TECH DATABASE")
    print("=" * 75)

    db = SessionLocal()
    today_str = datetime.date.today().isoformat()
    compiled_count = 0
    errors = []

    try:
        for preset_id, filename_base in PRESET_FILENAME_MAP.items():
            generator_func = GENERATORS_MAP.get(preset_id)
            if not generator_func:
                print(f" [SKIP] No generator mapped for preset: {preset_id}")
                continue

            print(f"\n--> Compiling: {preset_id}...")
            buf = io.BytesIO()
            try:
                generator_func(db, buf)
                pdf_bytes = buf.getvalue()

                # Write date-stamped file and latest canonical file
                out_path_dated = ARCHIVE_DIR / f"{filename_base}-{today_str}.pdf"
                out_path_latest = ARCHIVE_DIR / f"{filename_base}.pdf"

                with open(out_path_dated, "wb") as f:
                    f.write(pdf_bytes)
                with open(out_path_latest, "wb") as f:
                    f.write(pdf_bytes)

                size_kb = len(pdf_bytes) / 1024.0
                print(f"    [OK] Successfully compiled: {out_path_dated.name} ({size_kb:.1f} KB)")
                compiled_count += 1
            except Exception as e:
                print(f"    [ERROR] Failed compiling {preset_id}: {e}")
                errors.append((preset_id, str(e)))

        print("\n" + "=" * 75)
        print("PRE-COMPILATION SUMMARY")
        print("=" * 75)
        print(f"Total Monographs Compiled: {compiled_count} / {len(PRESET_FILENAME_MAP)}")
        if errors:
            print(f"Errors ({len(errors)}):")
            for p, err in errors:
                print(f" - {p}: {err}")
        else:
            print("Status: ALL EXECUTIVE MONOGRAPHS COMPILED WITH ZERO ERRORS.")
        print("=" * 75)

    finally:
        db.close()

if __name__ == "__main__":
    precompile_all_executive_reports()
