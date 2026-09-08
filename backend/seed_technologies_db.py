"""
Database Seeder & Migration Pipeline for Technology & Fuels Reference Knowledge Base.
Creates tables and seeds all 15 sectors, 36 technologies, KPIs, cost/performance metrics,
and fuel vectors directly into PostgreSQL.
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import engine, SessionLocal, Base
from app.models.technology import (
    TechnologyCategory,
    Technology,
    TechnologyCostPerformance,
    TechnologyKPI,
    TechnologySubsystem
)
from app.engine.tech_reference import (
    CATEGORIES,
    TECHNOLOGY_REGISTRY,
    synthesize_cost_performance
)

def run_technology_database_migration():
    """Idempotently creates tables and seeds complete master technology reference."""
    print("=" * 70)
    print("MIGRATING CLEAN ENERGY TECHNOLOGY & FUELS KNOWLEDGE BASE INTO POSTGRESQL")
    print("=" * 70)

    # 1. Create Tables
    print("\n1. Ensuring database tables exist in PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("   [OK] Tables 'technology_categories', 'technologies', 'technology_cost_performance', 'technology_kpis', 'technology_subsystems' verified.")


    db = SessionLocal()
    try:
        # 2. Seed Technology Categories
        print("\n2. Seeding 15 Clean Energy Innovation Sectors...")
        cat_count = 0
        for idx, cat in enumerate(CATEGORIES):
            existing_cat = db.query(TechnologyCategory).filter_by(id=cat["id"]).first()
            if not existing_cat:
                new_cat = TechnologyCategory(
                    id=cat["id"],
                    name=cat["name"],
                    icon=cat["icon"],
                    description=cat.get("description", ""),
                    color=cat.get("color", ""),
                    accent=cat.get("accent", ""),
                    sort_order=idx + 1,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_cat)
            else:
                existing_cat.name = cat["name"]
                existing_cat.icon = cat["icon"]
                existing_cat.description = cat.get("description", "")
                existing_cat.color = cat.get("color", "")
                existing_cat.accent = cat.get("accent", "")
                existing_cat.sort_order = idx + 1
                existing_cat.updated_at = datetime.utcnow()
            cat_count += 1
        db.commit()
        print(f"   [OK] Successfully seeded {cat_count} categories.")

        # 3. Seed Technologies & Associated Child Entities
        print("\n3. Seeding Technologies, KPIs, Cost/Performance, and Subsystems...")
        tech_count = 0
        kpi_count = 0
        cp_count = 0

        # 1b. Schema Patch: Ensure new columns exist on SQLite or PostgreSQL
        try:
            from sqlalchemy import inspect, text
            insp = inspect(engine)
            existing_cols = [c['name'] for c in insp.get_columns('technologies')]
            with engine.connect() as conn:
                if 'vector_type' not in existing_cols:
                    conn.execute(text("ALTER TABLE technologies ADD COLUMN vector_type VARCHAR(32) DEFAULT 'hardware';"))
                    conn.commit()
                    print("   [OK] Column 'vector_type' added to technologies.")
                if 'fuel_profile_json' not in existing_cols:
                    conn.execute(text("ALTER TABLE technologies ADD COLUMN fuel_profile_json TEXT;"))
                    conn.commit()
                    print("   [OK] Column 'fuel_profile_json' added to technologies.")
        except Exception as e:
            print(f"   [WARN] Column patch note: {e}")

        for tech_id, t in TECHNOLOGY_REGISTRY.items():
            cost_perf = synthesize_cost_performance(tech_id, t)

            # Upsert Technology
            existing_tech = db.query(Technology).filter_by(id=tech_id).first()
            if not existing_tech:
                existing_tech = Technology(id=tech_id)
                db.add(existing_tech)

            existing_tech.name = t["name"]
            existing_tech.category_id = t["category_id"]
            existing_tech.headline = t["headline"]
            existing_tech.trl_current = t.get("trl_current", 5)
            existing_tech.trl_target = t.get("trl_target", 9)
            existing_tech.sector = t.get("sector", "")
            existing_tech.fuel_vector = t.get("fuel_vector", "")
            existing_tech.vector_type = t.get("vector_type", "hardware")
            existing_tech.fuel_profile_json = json.dumps(t.get("fuel_profile")) if t.get("fuel_profile") else None
            existing_tech.keywords_json = json.dumps(t.get("keywords", []))

            # Plain English
            plain = t.get("plain_english", {})
            existing_tech.plain_what_is_it = plain.get("what_is_it", "")
            existing_tech.plain_how_it_works = plain.get("how_it_works", "")
            existing_tech.plain_why_it_matters = plain.get("why_it_matters", "")
            existing_tech.plain_macro_problem_solved = plain.get("macro_problem_solved", "")

            # Evolution
            evo = t.get("evolution", {})
            existing_tech.evolution_past = evo.get("past", "")
            existing_tech.evolution_present = evo.get("present", "")
            existing_tech.evolution_future = evo.get("future", "")

            # Frontier & Research
            frontier = t.get("frontier", {})
            existing_tech.moonshot_goal = frontier.get("moonshot_goal", "")
            existing_tech.bottlenecks_json = json.dumps(frontier.get("bottlenecks", []))
            existing_tech.active_research_json = json.dumps(frontier.get("active_research_tracks", []))

            # Trade-offs & Radar
            tradeoffs = t.get("trade_offs", {})
            existing_tech.tradeoffs_strengths_json = json.dumps(tradeoffs.get("strengths", []))
            existing_tech.tradeoffs_weaknesses_json = json.dumps(tradeoffs.get("weaknesses", []))
            existing_tech.competing_techs_json = json.dumps(tradeoffs.get("competing_technologies", []))
            existing_tech.radar_scores_json = json.dumps(t.get("radar_scores", {}))
            existing_tech.updated_at = datetime.utcnow()

            db.flush()

            # Upsert Cost & Performance
            if cost_perf:
                cm = cost_perf.get("cost_metric", {})
                pm = cost_perf.get("performance_metric", {})

                existing_cp = db.query(TechnologyCostPerformance).filter_by(technology_id=tech_id).first()
                if not existing_cp:
                    existing_cp = TechnologyCostPerformance(technology_id=tech_id)
                    db.add(existing_cp)

                existing_cp.cost_metric_name = cm.get("name", "Capital Cost")
                existing_cp.cost_unit = cm.get("unit", "$/unit")
                existing_cp.cost_baseline_2024 = cm.get("baseline_2024")
                existing_cp.cost_baseline_fmt = cm.get("baseline_fmt", "$1,000 / unit")
                existing_cp.cost_target_2030 = cm.get("target_2030")
                existing_cp.cost_target_2030_fmt = cm.get("target_2030_fmt", "$350 / unit")
                existing_cp.cost_target_2035 = cm.get("target_2035")
                existing_cp.cost_target_2035_fmt = cm.get("target_2035_fmt", "$200 / unit")
                existing_cp.cost_reduction_pct = cm.get("reduction_pct", "-80%")
                existing_cp.cost_primary_driver = cm.get("primary_driver", "")

                existing_cp.perf_metric_name = pm.get("name", "Conversion Efficiency")
                existing_cp.perf_unit = pm.get("unit", "%")
                existing_cp.perf_baseline_2024 = pm.get("baseline_2024")
                existing_cp.perf_baseline_fmt = pm.get("baseline_fmt", "65%")
                existing_cp.perf_target_2030 = pm.get("target_2030")
                existing_cp.perf_target_2030_fmt = pm.get("target_2030_fmt", "88%")
                existing_cp.perf_target_2035 = pm.get("target_2035")
                existing_cp.perf_target_2035_fmt = pm.get("target_2035_fmt", "95%")
                existing_cp.perf_improvement_pct = pm.get("improvement_pct", "+46%")
                existing_cp.perf_primary_driver = pm.get("primary_driver", "")

                existing_cp.learning_rate = cost_perf.get("learning_rate", "")
                existing_cp.earthshot_goal = cost_perf.get("earthshot_goal", "")
                cp_count += 1

            # Seed KPIs
            kpis = frontier.get("kpis", [])
            db.query(TechnologyKPI).filter_by(technology_id=tech_id).delete()
            for k_idx, k in enumerate(kpis):
                new_kpi = TechnologyKPI(
                    technology_id=tech_id,
                    name=k.get("name", "KPI"),
                    current_value=k.get("current", "N/A"),
                    target_2030=k.get("target_2030", "Target"),
                    status=k.get("status", "on_track"),
                    sort_order=k_idx + 1
                )
                db.add(new_kpi)
                kpi_count += 1

            # Seed Relational Subsystems
            db.query(TechnologySubsystem).filter_by(technology_id=tech_id).delete()
            subsystems_data = [
                {
                    "node_id": "input_interface",
                    "name": f"{t['name'].split(':')[0]} Primary Ingestion Interface",
                    "category": "Feedstock / Energy Intake Stage",
                    "x": 18,
                    "y": 45,
                    "icon": "Droplets" if t.get("vector_type") == "fuel_carrier" else "Zap",
                    "summary": f"Primary ingestion and conditioning interface for {t['fuel_vector']}.",
                    "operating_value": "Nominal Continuous Duty Input Rating",
                    "materials": "High-Durability Corrosion-Resistant Superalloys & Polymers",
                    "failure_mode": "Interface mechanical wear and parasitic resistance losses.",
                    "frontier_bottleneck": frontier.get("bottlenecks", ["Thermal and mechanical stress"])[0] if frontier.get("bottlenecks") else "Materials endurance",
                    "active_research": frontier.get("active_research_tracks", ["Surface passivation coatings"])[0] if frontier.get("active_research_tracks") else "Advanced materials testing"
                },
                {
                    "node_id": "reaction_core",
                    "name": f"{t['name'].split(':')[0]} Conversion Core & Reaction Cell",
                    "category": "Thermodynamic / Electrochemical Core",
                    "x": 50,
                    "y": 45,
                    "icon": "Atom",
                    "summary": f"Active conversion core executing primary clean energy transduction for {t['name']}.",
                    "operatingValue": "Peak System Efficiency Stage",
                    "materials": "Nanostructured Catalyst / Semiconductor Lattice / Advanced Sorbent",
                    "failure_mode": "Micro-structural defect propagation and thermal cycling degradation.",
                    "frontier_bottleneck": frontier.get("bottlenecks", ["Conversion efficiency ceiling"])[-1] if frontier.get("bottlenecks") else "Thermodynamic limits",
                    "active_research": frontier.get("active_research_tracks", ["Quantum-simulated catalytic pathways"])[-1] if frontier.get("active_research_tracks") else "Catalytic scaling"
                },
                {
                    "node_id": "power_export_balance",
                    "name": f"{t['name'].split(':')[0]} Balance of Plant & Output Stage",
                    "category": "Grid Integration & Product Conditioning",
                    "x": 82,
                    "y": 45,
                    "icon": "Zap",
                    "summary": f"High-voltage conditioning, compression, or power electronics delivering clean output to the off-taker.",
                    "operatingValue": "Standardized Commercial Interconnection Spec",
                    "materials": "Silicon Carbide Power Electronics / Cryogenic Compressor Stages",
                    "failure_mode": "Interconnection transient surges and balance-of-plant parasitics.",
                    "frontier_bottleneck": "Balance-of-system capital expenditure and siting permit friction.",
                    "active_research": "Autonomous microgrid telemetry and modular plug-and-play balance-of-plant skids."
                }
            ]
            for s in subsystems_data:
                sub_entity = TechnologySubsystem(
                    id=f"{tech_id}:{s['node_id']}",
                    technology_id=tech_id,
                    node_id=s["node_id"],
                    name=s["name"],
                    category=s["category"],
                    x=s["x"],
                    y=s["y"],
                    icon=s["icon"],
                    summary=s["summary"],
                    operating_value=s.get("operatingValue") or s.get("operating_value"),
                    materials=s["materials"],
                    failure_mode=s["failure_mode"],
                    frontier_bottleneck=s["frontier_bottleneck"],
                    active_research=s["active_research"]
                )
                db.add(sub_entity)

            tech_count += 1

        db.commit()
        print(f"   [OK] Successfully seeded {tech_count} technologies, {cp_count} cost/performance records, {kpi_count} KPIs, and {db.query(TechnologySubsystem).count()} subsystems.")

        # 4. Print Summary Verification
        print("\n" + "=" * 70)
        print("DATABASE MIGRATION AND SEEDING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"Categories Table:       {db.query(TechnologyCategory).count()} sectors")
        print(f"Technologies Table:     {db.query(Technology).count()} technologies")
        print(f"Cost/Performance Table: {db.query(TechnologyCostPerformance).count()} records")
        print(f"KPIs Table:             {db.query(TechnologyKPI).count()} records")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error during database seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_technology_database_migration()
