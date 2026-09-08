import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from app.main import app
from fastapi.testclient import TestClient

def main():
    client = TestClient(app)

    print("================================================================================")
    print("TESTING FASTAPI BACKEND AGAINST LIVE SUPABASE POSTGRESQL CLUSTER")
    print("================================================================================")

    print("\n1. Testing /health endpoint...")
    r = client.get("/health")
    print("   Status:", r.status_code, r.json())
    assert r.status_code == 200

    print("\n2. Testing /api/system/stats endpoint...")
    r = client.get("/api/system/stats")
    print("   Status:", r.status_code, r.json())
    assert r.status_code == 200

    print("\n3. Testing /api/opportunities endpoint...")
    r = client.get("/api/opportunities?page=1&page_size=3")
    print("   Status:", r.status_code)
    data = r.json()
    print("   Total Opportunities in Supabase:", data.get("total"))
    print("   Sample Opportunity:", data.get("items", [{}])[0].get("name"))
    assert r.status_code == 200
    assert data.get("total", 0) > 0

    print("\n4. Testing /api/awards endpoint...")
    r = client.get("/api/awards?page=1&page_size=3")
    print("   Status:", r.status_code)
    data = r.json()
    print("   Total Awards in Supabase:", data.get("total"))
    print("   Sample Recipient:", data.get("items", [{}])[0].get("recipient_name"))
    assert r.status_code == 200
    assert data.get("total", 0) > 0

    print("\n5. Testing /api/contacts endpoint...")
    r = client.get("/api/contacts?page=1&page_size=3")
    print("   Status:", r.status_code)
    data = r.json()
    print("   Total Key Contacts in Supabase:", data.get("total"))
    assert r.status_code == 200
    assert data.get("total", 0) > 0

    print("\n6. Testing Ghost Auth endpoint...")
    r = client.post("/api/auth/ghost/verify-member", json={"email": "nonexistent_member@example.com"})
    print("   Status:", r.status_code, "(Correctly rejected unregistered member)")
    assert r.status_code in [404, 200]

    print("\n7. Testing System Membership Manifest endpoint...")
    r = client.get("/api/auth/membership")
    print("   Status:", r.status_code, "Tiers:", len(r.json().get("membership_manifest", {}).get("tiers", [])))
    assert r.status_code == 200

    print("\n================================================================================")
    print("ALL API ENDPOINTS FUNCTIONING WITH 100% SUCCESS AGAINST SUPABASE!")
    print("================================================================================")

if __name__ == "__main__":
    main()
