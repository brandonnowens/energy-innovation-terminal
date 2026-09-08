from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
payload = {
    "text": "Grid-scale battery energy storage system and non-wires alternative pilot for distribution substation deferral and peak load management",
    "location": "California",
    "technology_areas": ["Energy Storage", "Grid Modernization"],
    "activity_types": ["Demonstration", "Pilot & Demonstration"],
    "sectors": ["Utility / Grid"],
    "fuel_types": ["Electricity", "Battery Storage"],
    "agencies": ["Pacific Gas and Electric", "Southern California Edison", "San Diego Gas & Electric"]
}

res = client.post('/api/analyze', json=payload)
print("Match Status Code:", res.status_code)
if res.status_code == 200:
    data = res.json()
    strong = data.get("matches", {}).get("strong_matches", [])
    conditional = data.get("matches", {}).get("conditional_matches", [])
    print(f"Strong matches: {len(strong)}")
    for m in strong:
        print(f"  [{m.get('agency')}] {m.get('solicitation_number')}: {m.get('name')} (Fit: {m.get('fit_score')})")
    print(f"Conditional matches: {len(conditional)}")
    for m in conditional:
        print(f"  [{m.get('agency')}] {m.get('solicitation_number')}: {m.get('name')} (Fit: {m.get('fit_score')})")
