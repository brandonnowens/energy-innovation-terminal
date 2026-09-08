"""Purge non-energy-innovation records from the database using raw SQL."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.database import engine
from sqlalchemy import text

ENERGY_TERMS = [
    "clean energy", "renewable energy", "solar", "wind", "photovoltaic", "geothermal",
    "battery", "energy storage", "grid", "smart grid", "microgrid",
    "hydrogen", "fuel cell", "electrolysis", "electrolyzer",
    "carbon capture", "carbon sequestration", "ccs", "ccus", "direct air capture",
    "decarbonization", "decarbonize", "net zero", "zero emission", "low carbon",
    "building energy", "energy efficiency", "heat pump", "weatherization", "hvac",
    "electric vehicle", "ev charging", "electrification",
    "offshore wind", "onshore wind", "wind turbine", "wind power",
    "nuclear", "fusion", "fission", "small modular reactor", "advanced reactor",
    "biofuel", "bioenergy", "biomass", "biogas", "sustainable fuel", "sustainable aviation",
    "power grid", "power system", "electricity", "transmission",
    "greenhouse gas", "ghg", "climate change", "climate mitigation",
    "energy innovation", "clean technology", "cleantech", "energy transition",
    "long duration storage", "pumped hydro", "compressed air",
    "industrial decarbonization", "industrial emissions", "process heat",
    "combined heat and power", "chp", "cogeneration",
    "distributed energy", "demand response", "energy management",
]

# Agencies inherently energy-focused (keep all records)
KEEP_AGENCIES = ("DOE", "ARPA-E", "NYSERDA", "CEC", "MassCEC")

with engine.connect() as conn:
    # Count before
    total_before = conn.execute(text("SELECT COUNT(*) FROM opportunities")).scalar()
    print(f"Before purge: {total_before} opportunities")

    # Build the energy relevance SQL condition
    # An opportunity is energy-relevant if its name+description contains any energy term
    energy_conditions = " OR ".join(
        f"(LOWER(COALESCE(name,'') || ' ' || COALESCE(short_description,'')) LIKE '%{term}%')"
        for term in ENERGY_TERMS
    )

    # Find IDs to delete: non-energy-focused agencies where content doesn't match any energy term
    placeholders = ",".join(f"'{a}'" for a in KEEP_AGENCIES)
    delete_sql = f"""
        SELECT id FROM opportunities
        WHERE agency NOT IN ({placeholders})
        AND NOT ({energy_conditions})
    """

    ids_to_delete = [row[0] for row in conn.execute(text(delete_sql)).fetchall()]
    print(f"Found {len(ids_to_delete)} non-energy records to purge")

    if ids_to_delete:
        # Delete related records first (FK constraints)
        for table in ["opportunity_rounds", "opportunity_contacts", "opportunity_documents",
                       "opportunity_categories", "eligibility_rules", "analysis_matches",
                       "opportunity_relationships"]:
            try:
                batch_size = 500
                for i in range(0, len(ids_to_delete), batch_size):
                    batch = ids_to_delete[i:i+batch_size]
                    id_list = ",".join(str(x) for x in batch)
                    
                    # Different FK column names per table
                    if table == "opportunity_relationships":
                        conn.execute(text(f"DELETE FROM {table} WHERE source_opp_id IN ({id_list}) OR target_opp_id IN ({id_list})"))
                    elif table == "analysis_matches":
                        conn.execute(text(f"DELETE FROM {table} WHERE opportunity_id IN ({id_list})"))
                    else:
                        conn.execute(text(f"DELETE FROM {table} WHERE opportunity_id IN ({id_list})"))
            except Exception as e:
                print(f"  Note: {table} - {e}")

        # Now delete the opportunities themselves
        for i in range(0, len(ids_to_delete), 500):
            batch = ids_to_delete[i:i+500]
            id_list = ",".join(str(x) for x in batch)
            conn.execute(text(f"DELETE FROM opportunities WHERE id IN ({id_list})"))

        conn.commit()

    total_after = conn.execute(text("SELECT COUNT(*) FROM opportunities")).scalar()
    print(f"After purge: {total_after} opportunities")
    print(f"Removed: {total_before - total_after}")

    # Show breakdown
    rows = conn.execute(text(
        "SELECT agency, COUNT(*) as cnt FROM opportunities GROUP BY agency ORDER BY cnt DESC"
    )).fetchall()
    print("\nBy Agency:")
    for agency, count in rows:
        print(f"  {agency}: {count}")
