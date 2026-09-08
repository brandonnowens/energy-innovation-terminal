"""Tests for Ghost.org membership integration, tier mapping, and webhook verification."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.services.ghost_service import ghost_service


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_ghost_config_endpoint(client: TestClient):
    """Verify Ghost configuration public endpoint."""
    res = client.get("/api/auth/ghost/config")
    assert res.status_code == 200
    data = res.json()
    assert "ghost_api_url" in data
    assert "configured" in data
    assert "portal_signup_url" in data


def test_ghost_tier_mapping():
    """Verify tier translation logic between Ghost and Terminal."""
    assert ghost_service.map_ghost_tier_to_terminal_tier("paid", "pro-annual") == "pro"
    assert ghost_service.map_ghost_tier_to_terminal_tier("paid", "enterprise-tier") == "enterprise"
    assert ghost_service.map_ghost_tier_to_terminal_tier("free", "free-tier") == "free_public_benefit"
    assert ghost_service.map_ghost_tier_to_terminal_tier("comped", "partner-access") == "pro"


def test_ghost_webhook_lifecycle(client: TestClient, db: Session):
    """Test webhook ingestion of member creation and tier update."""
    test_email = "test-ghost-member@aixenergy.io"

    # Clean up existing test user
    existing = db.query(User).filter(User.email == test_email).first()
    if existing:
        db.delete(existing)
        db.commit()

    # 1. Simulate member.added webhook from Ghost
    payload = {
        "member": {
            "id": "ghost_mem_12345",
            "email": test_email,
            "name": "Ghost Test User",
            "status": "paid",
            "tiers": [{"slug": "pro-monthly", "name": "Pro Member"}]
        }
    }

    res = client.post("/api/auth/ghost/webhook", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "created"
    assert data["tier"] == "pro"

    # Verify user in database
    user = db.query(User).filter(User.email == test_email).first()
    assert user is not None
    assert user.tier == "pro"
    assert user.ghost_member_id == "ghost_mem_12345"
    assert user.ghost_status == "paid"

    # 2. Simulate member.edited (upgrade to enterprise)
    payload_upgrade = {
        "member": {
            "id": "ghost_mem_12345",
            "email": test_email,
            "name": "Ghost Test User",
            "status": "paid",
            "tiers": [{"slug": "enterprise-tier", "name": "Institutional Partner"}]
        }
    }

    res_upgrade = client.post("/api/auth/ghost/webhook", json=payload_upgrade)
    assert res_upgrade.status_code == 200
    data_up = res_upgrade.json()
    assert data_up["status"] == "updated"
    assert data_up["tier"] == "enterprise"

    db.refresh(user)
    assert user.tier == "enterprise"

    # Clean up
    db.delete(user)
    db.commit()
