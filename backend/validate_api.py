import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api(path, desc):
    try:
        r = client.get(path)
        assert r.status_code == 200, f"Status code: {r.status_code}"
        data = r.json()
        if isinstance(data, list):
            print(f"  OK  {desc}: {len(data)} items")
        elif isinstance(data, dict) and 'items' in data:
            print(f"  OK  {desc}: {len(data['items'])} items, {data.get('total', '?')} total")
        elif isinstance(data, dict):
            keys = list(data.keys())[:5]
            print(f"  OK  {desc}: keys={keys}")
        else:
            print(f"  OK  {desc}: {type(data)}")
        return True
    except Exception as e:
        print(f"  FAIL {desc}: {e}")
        return False


print("=== API ENDPOINT TESTS ===")
results = []
results.append(test_api("/api/health", "Health"))
results.append(test_api("/api/opportunities?page_size=5", "Opportunities"))
results.append(test_api("/api/programs?organization=NYSERDA", "Programs (NYSERDA)"))
results.append(test_api("/api/programs?organization=DOE", "Programs (DOE)"))
results.append(test_api("/api/programs?organization=NSF", "Programs (NSF)"))
results.append(test_api("/api/programs/1/opportunities?organization=NYSERDA", "Program Opps"))
results.append(test_api("/api/organizations?page_size=5", "Organizations"))
results.append(test_api("/api/awards?page_size=5", "Awards"))
results.append(test_api("/api/awards/stats", "Award Stats"))
results.append(test_api("/api/awards/map?limit=100", "Award Map"))
results.append(test_api("/api/awards/recipients?page_size=5", "Award Recipients"))
results.append(test_api("/api/trends/overview", "Trends Overview"))
results.append(test_api("/api/trends/by-agency", "Trends by Agency"))
results.append(test_api("/api/trends/by-technology", "Trends by Tech"))
results.append(test_api("/api/trends/by-sector", "Trends by Sector"))
results.append(test_api("/api/trends/by-fuel", "Trends by Fuel"))
results.append(test_api("/api/trends/amounts", "Trends Amounts"))
results.append(test_api("/api/trends/heatmap", "Trends Heatmap"))
results.append(test_api("/api/network/graph?limit=50", "Network Graph"))
results.append(test_api("/api/agencies", "Agencies"))
results.append(test_api("/api/system/sources", "Sources"))

passed = sum(results)
total = len(results)
print(f"\nAPI: {passed}/{total} passed")

from sqlalchemy import text
from app.database import engine

print("\n=== HIERARCHY INTEGRITY ===")
with engine.begin() as conn:
    orphan_progs = conn.execute(text(
        "SELECT COUNT(*) FROM programs p WHERE p.id NOT IN (SELECT DISTINCT program_id FROM opportunities WHERE program_id IS NOT NULL)"
    )).scalar() or 0
    print(f"  Orphan programs (no opps): {orphan_progs}" + (" OK" if orphan_progs == 0 else " FAIL"))

    unlinked_opps = conn.execute(text("SELECT COUNT(*) FROM opportunities WHERE program_id IS NULL")).scalar() or 0
    print(f"  Opps without program: {unlinked_opps}" + (" OK" if unlinked_opps == 0 else " FAIL"))

    total_progs = conn.execute(text("SELECT COUNT(*) FROM programs")).scalar() or 0
    total_opps = conn.execute(text("SELECT COUNT(*) FROM opportunities")).scalar() or 0
    total_awards = conn.execute(text("SELECT COUNT(*) FROM awards")).scalar() or 0
    print(f"  Programs: {total_progs}")
    print(f"  Opportunities: {total_opps}")
    print(f"  Awards: {total_awards}")

    # Geocoding coverage
    nyserda_geo = conn.execute(text("""
        SELECT COUNT(*) as total, SUM(CASE WHEN latitude IS NOT NULL THEN 1 ELSE 0 END) as geo
        FROM awards WHERE agency = 'NYSERDA'
    """)).fetchone()
    ny_tot = nyserda_geo[0] or 1
    ny_geo = nyserda_geo[1] or 0
    print(f"  NYSERDA geocoded: {ny_geo}/{ny_tot} ({ny_geo*100//ny_tot}%)")

    all_geo = conn.execute(text("""
        SELECT COUNT(*) as total, SUM(CASE WHEN latitude IS NOT NULL THEN 1 ELSE 0 END) as geo FROM awards
    """)).fetchone()
    all_tot = all_geo[0] or 1
    all_g = all_geo[1] or 0
    print(f"  Overall geocoded: {all_g}/{all_tot} ({all_g*100//all_tot}%)")

    # Cross-agency programs
    cross = conn.execute(text("""
        SELECT COUNT(*) FROM (
            SELECT p.id FROM programs p JOIN opportunities o ON o.program_id = p.id 
            GROUP BY p.id HAVING COUNT(DISTINCT o.agency) > 1
        ) sub
    """)).scalar() or 0
    print(f"  Cross-agency programs: {cross}" + (" OK" if cross == 0 else f" (found {cross})"))

all_ok = passed == total and orphan_progs == 0 and unlinked_opps == 0
print(f"\n{'ALL CHECKS PASSED' if all_ok else 'SOME CHECKS FAILED'}")
sys.exit(0 if all_ok else 1)

