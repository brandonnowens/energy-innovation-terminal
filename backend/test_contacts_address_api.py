import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, text, init_db

init_db()

def test_contacts_api():
    client = TestClient(app)

    print("--- Testing /api/contacts endpoint ---")
    resp = client.get("/api/contacts?page=1&page_size=10")
    assert resp.status_code == 200, f"Status code {resp.status_code}: {resp.text}"
    data = resp.json()
    print(f"Total contacts: {data['total']}")
    print(f"Returned items: {len(data['items'])}")

    for item in data['items'][:3]:
        print(f"ID {item['id']}: {item['name_display']}")
        print(f"   Institution: {item['institution_name']}")
        print(f"   Address Line 1: {item['address_line1']}")
        print(f"   City, State, Zip: {item['city']}, {item['state']} {item['postal_code']}")
        print(f"   Formatted Address: {item['formatted_address']}")
        print(f"   Verification Status: {item['address_verification_status']}")
        print("---")

    print("\n--- Testing /api/contacts/{id} endpoint ---")
    c_id = data['items'][0]['id']
    resp_detail = client.get(f"/api/contacts/{c_id}")
    assert resp_detail.status_code == 200, f"Detail status {resp_detail.status_code}"
    detail = resp_detail.json()
    print(f"Detail ID {detail['id']}: {detail['name_display']}")
    print(f"   Formatted Address: {detail['formatted_address']}")
    assert detail['formatted_address'] is not None
    assert detail['address_line1'] is not None
    assert detail['city'] is not None
    assert detail['state'] is not None
    assert detail['postal_code'] is not None
def test_admin_email_api():
    client = TestClient(app)

    print("\n--- Testing /api/admin/email/status (open access) ---")
    resp = client.get("/api/admin/email/status")
    assert resp.status_code == 200, f"Status code {resp.status_code}: {resp.text}"
    status = resp.json()
    print("Admin Email:", status["admin_email"])
    print("Telemetry:", status["telemetry"])
    assert status["admin_email"] == "bowens@aixenergy.io"

    print("\n--- Testing /api/admin/email/templates (open access) ---")
    resp_tpl = client.get("/api/admin/email/templates")
    assert resp_tpl.status_code == 200, f"Templates status {resp_tpl.status_code}"
    tpls = resp_tpl.json()
    print(f"Loaded {len(tpls['templates'])} templates")
    assert len(tpls["templates"]) >= 4

    print("\n--- Testing /api/admin/email/threads (open access) ---")
    resp_threads = client.get("/api/admin/email/threads")
    assert resp_threads.status_code == 200, f"Threads status {resp_threads.status_code}"
    threads = resp_threads.json()
    print(f"Total threads: {threads['total']}")

    print("\n>>> ALL BACKEND TESTS PASSED WITH 0 ERRORS! <<<")

if __name__ == "__main__":
    test_contacts_api()
    test_admin_email_api()

