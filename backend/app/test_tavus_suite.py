"""Unit and integration test suite for Tavus.io Video Advisory endpoints."""

import os
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.api.tavus import get_role_greeting, build_tavus_conversational_context

client = TestClient(app)

def test_tavus_greetings():
    """Verify role-tailored verbal greetings."""
    roles = [
        "institutional_leader",
        "startup_entrepreneur",
        "developer",
        "investor",
        "researcher",
        "utility",
        "policy",
        "grant_writer"
    ]
    for r in roles:
        greeting = get_role_greeting(r)
        assert greeting and len(greeting) > 20, f"Greeting for {r} should be substantial"
        assert "Advisor" in greeting or "Partner" in greeting

    print("[PASS] Role greetings test passed for all 8 roles.")


def test_tavus_context_builder():
    """Verify conversational context generation."""
    ctx = build_tavus_conversational_context("institutional_leader", "Focus on $50M regional hydrogen hub.")
    assert "54,305" in ctx
    assert "Institutional Leader" in ctx
    assert "hydrogen hub" in ctx
    print("[PASS] Conversational context builder test passed.")


def test_tavus_status_endpoint():
    """Verify /api/tavus/status response structure."""
    res = client.get("/api/tavus/status")
    assert res.status_code == 200
    data = res.json()
    assert "tavus_configured" in data
    assert "supported_features" in data
    assert "realtime_video_conversation" in data["supported_features"]
    print(f"[PASS] /api/tavus/status returned: {data}")


def test_tavus_set_api_key_endpoint():
    """Verify /api/tavus/set-api-key endpoint."""
    res = client.post("/api/tavus/set-api-key", json={
        "api_key": "test_tav_key_123",
        "persona_id": "p_test_123",
        "replica_id": "r_test_123"
    })
    assert res.status_code == 200
    data = res.json()
    assert data.get("success") is True

    # Check status again
    status_res = client.get("/api/tavus/status")
    assert status_res.status_code == 200
    s_data = status_res.json()
    assert s_data["tavus_configured"] is True
    assert s_data["persona_id"] == "p_test_123"
    assert s_data["replica_id"] == "r_test_123"

    # Reset
    client.post("/api/tavus/set-api-key", json={"api_key": ""})
    print("[PASS] /api/tavus/set-api-key test passed.")


def test_tavus_create_conversation_validation():
    """Verify /api/tavus/conversations/create validation when no key is set."""
    settings.tavus_api_key = ""
    os.environ.pop("TAVUS_API_KEY", None)

    res = client.post("/api/tavus/conversations/create", json={
        "user_role": "institutional_leader"
    })
    assert res.status_code == 400
    assert "Tavus API key is not configured" in res.json()["detail"]
    print("[PASS] /api/tavus/conversations/create validation check passed.")


if __name__ == "__main__":
    test_tavus_greetings()
    test_tavus_context_builder()
    test_tavus_status_endpoint()
    test_tavus_set_api_key_endpoint()
    test_tavus_create_conversation_validation()
    print("\n ALL TAVUS VIDEO ADVISORY BACKEND TESTS PASSED SUCCESSFULLY!")
