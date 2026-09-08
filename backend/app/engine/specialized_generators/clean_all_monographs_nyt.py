"""
Cleanly standardizes the imports and NYT graphics hooks across all specialized generator files.
"""

import os
import re

GEN_DIR = os.path.dirname(os.path.abspath(__file__))

FILES_TO_FIX = [
    ("gen_clean_gen.py", "clean_gen_dossier"),
    ("gen_energy_storage.py", "energy_storage_dossier"),
    ("gen_alt_fuels.py", "alt_fuels_dossier"),
    ("gen_advanced_nuclear.py", "advanced_nuclear_smr"),
    ("gen_grid_modernization.py", "grid_modernization_dossier"),
    ("gen_buildings_thermal.py", "buildings_thermal_dossier"),
    ("gen_industrial_decarb.py", "industrial_decarb_dossier"),
    ("gen_critical_minerals.py", "critical_minerals_dossier"),
    ("gen_ai_datacenter.py", "ai_datacenter_dossier"),
    ("gen_transportation_ev.py", "transportation_ev_dossier"),
]

def clean_file(filename: str, preset_id: str):
    filepath = os.path.join(GEN_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Clean up imports
    if "from .nyt_graphics_registry import get_nyt_graphics_for_preset" not in content:
        content = re.sub(
            r'from \.base import \(',
            'from .nyt_graphics_registry import get_nyt_graphics_for_preset\nfrom .base (',
            content
        )

    # 2. Strip broken NYT injection fragments
    content = re.sub(r'# Fetch NYT-Grade Customized Geospatial.*?\)\n', '', content, flags=re.DOTALL)
    content = re.sub(r'# \(Replaced by NYT.*?\n', '', content)

    # 3. Cleanly insert NYT graphics generation right after bar_chart definition
    nyt_block = f"""
    # Fetch NYT-Grade Customized Geospatial & Knowledge Graph Registry Data
    nyt_meta = get_nyt_graphics_for_preset("{preset_id}")
    us_map = render_geospatial_us_map(
        title=nyt_meta.get("map_title", "Geospatial Capital Deployment Atlas"),
        custom_clusters=nyt_meta.get("clusters"),
        callout_boxes=nyt_meta.get("callouts")
    )
    network_diag = render_network_graph_diagram(
        title=nyt_meta.get("network_title", "Institutional Knowledge Graph"),
        custom_nodes=nyt_meta.get("nodes"),
        custom_edges=nyt_meta.get("edges")
    )
"""

    # If us_map = ... or network_diag = ... exists, remove them
    content = re.sub(r'us_map\s*=\s*render_geospatial_us_map\([^)]*\)\n?', '', content)
    content = re.sub(r'network_diag\s*=\s*render_network_graph_diagram\([^)]*\)\n?', '', content)

    # Inject clean nyt_block after bar_chart = ...
    if "bar_chart = render_vector_bar_chart(" in content:
        content = re.sub(
            r'(bar_chart\s*=\s*render_vector_bar_chart\([^)]*\)\n)',
            r'\1' + nyt_block,
            content
        )
    else:
        content = content.replace(
            "pages_content = [",
            f"{nyt_block}\n    pages_content = ["
        )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    for fn, pid in FILES_TO_FIX:
        clean_file(fn, pid)
    print("[OK] All files cleaned.")
