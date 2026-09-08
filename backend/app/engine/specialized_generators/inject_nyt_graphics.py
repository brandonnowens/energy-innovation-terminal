"""
Script to wire each Specialized Monograph Generator to use the NYT Graphics Registry:
1. Ingests topic-specific custom clusters, callout boxes, and coordinates into render_geospatial_us_map.
2. Ingests topic-specific institutional nodes and collaborative edges into render_network_graph_diagram.
3. Completely replaces generic maps and generic networks with custom publication-grade graphics.
"""

import os
import re

GEN_DIR = os.path.dirname(os.path.abspath(__file__))

PRESET_TO_FILE_MAP = {
    "clean_gen_dossier": "gen_clean_gen.py",
    "energy_storage_dossier": "gen_energy_storage.py",
    "alt_fuels_dossier": "gen_alt_fuels.py",
    "advanced_nuclear_smr": "gen_advanced_nuclear.py",
    "grid_modernization_dossier": "gen_grid_modernization.py",
    "buildings_thermal_dossier": "gen_buildings_thermal.py",
    "industrial_decarb_dossier": "gen_industrial_decarb.py",
    "critical_minerals_dossier": "gen_critical_minerals.py",
    "ai_datacenter_dossier": "gen_ai_datacenter.py",
    "transportation_ev_dossier": "gen_transportation_ev.py",
}

def inject_all_nyt_graphics():
    print("=" * 70)
    print("INJECTING NYT GRAPHICS REGISTRY INTO SPECIALIZED MONOGRAPHS")
    print("=" * 70)

    for preset_id, filename in PRESET_TO_FILE_MAP.items():
        filepath = os.path.join(GEN_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Skipping {filename} (not found)")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Ensure import of get_nyt_graphics_for_preset
        if "get_nyt_graphics_for_preset" not in content:
            content = content.replace(
                "from .base import (",
                "from .nyt_graphics_registry import get_nyt_graphics_for_preset\nfrom .base import ("
            )

        # 2. Add NYT graphics extraction code at beginning of generator function
        fetch_code = f"""
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

        # Replace existing generic us_map = ... and network_diag = ...
        # Regex to find existing us_map and network_diag definitions
        content = re.sub(
            r'us_map\s*=\s*render_geospatial_us_map\([^)]*\)',
            '# (Replaced by NYT Geospatial Map below)',
            content
        )
        content = re.sub(
            r'network_diag\s*=\s*render_network_graph_diagram\([^)]*\)',
            '# (Replaced by NYT Knowledge Graph below)',
            content
        )

        # Inject the fetch code right after radar_chart or ts_chart
        if "nyt_meta = get_nyt_graphics_for_preset" not in content:
            if "radar_chart = render_technology_radar_chart(" in content:
                content = re.sub(
                    r'(radar_chart\s*=\s*render_technology_radar_chart\([^)]*\))',
                    r'\1\n' + fetch_code,
                    content
                )
            else:
                content = content.replace(
                    "pages_content = [",
                    f"{fetch_code}\n    pages_content = ["
                )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f" [OK] Successfully injected NYT graphics into {filename}")

    print("=" * 70)
    print("ALL SPECIALIZED MONOGRAPHS UPGRADED WITH NYT GRAPHICS")
    print("=" * 70)

if __name__ == "__main__":
    inject_all_nyt_graphics()
