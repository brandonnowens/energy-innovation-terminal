"""
Unit and Integration Test Suite for the Winning Angle & Hidden Rubric Reverse-Engineering Engine.
"""

import pytest
from app.database import SessionLocal
from app.models.opportunity import Opportunity
from app.engine.profile import ProjectProfile
from app.engine.winning_angle_engine import (
    generate_grounded_winning_angle,
    generate_winning_angle_with_llm,
    WinningAngleReport,
)
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_grounded_winning_angle_nyserda(db_session):
    """Verify that a NYSERDA opportunity generates NY-specific rubric and narrative hooks."""
    profile = ProjectProfile(
        project_title="Brooklyn Industrial Microgrid & Battery Storage",
        summary="Commercial microgrid with thermal and battery storage to relieve grid congestion in Brooklyn, NY.",
        technology_areas=["Energy Storage", "Microgrids", "Grid Modernization"],
        sectors=["Industrial", "Commercial"],
        applicant_type="business",
        project_cost=3500000.0,
        estimated_trl=7,
        target_location="Brooklyn, NY",
    )

    opp = Opportunity(
        id=9901,
        solicitation_number="PON 5482",
        name="Commercial and Industrial Carbon Challenge",
        short_description="Funding for large C&I clean energy, energy storage, and electrification projects in NY State.",
        agency="NYSERDA",
        total_funding=15000000.0,
    )

    report = generate_grounded_winning_angle(db_session, profile, opp, match_score=0.92)
    assert isinstance(report, WinningAngleReport)
    assert report.opportunity_id == 9901
    assert "NY" in report.winning_hook or "CLCPA" in report.winning_hook or "NYSERDA" in report.strategic_framing or "New York" in report.winning_hook
    assert len(report.hidden_rubric_breakdown) >= 4
    # Weights should sum to 100%
    total_weight = sum(c["weight_pct"] for c in report.hidden_rubric_breakdown)
    assert total_weight == 100
    # Mandatory keywords should be populated
    assert len(report.mandatory_reviewer_keywords) >= 8
    # Teaming recommendations present
    assert len(report.optimal_teaming_strategy) >= 2
    # Landmines present
    assert len(report.red_flag_landmines) >= 2


def test_grounded_winning_angle_doe(db_session):
    """Verify that a DOE opportunity generates federal rubric emphasizing domestic supply chain and TRL."""
    profile = ProjectProfile(
        project_title="Next-Gen Solid State Electrolyte Pilot Line",
        summary="Pilot manufacturing facility for solid-state battery electrolytes.",
        technology_areas=["Advanced Materials", "Batteries", "Clean Manufacturing"],
        sectors=["Industrial"],
        applicant_type="commercial",
        project_cost=12000000.0,
        estimated_trl=5,
        target_location="Upstate New York",
    )

    opp = Opportunity(
        id=9902,
        solicitation_number="DE-FOA-0003200",
        name="Advanced Energy Manufacturing and Industrial Decarbonization FOA",
        short_description="DOE MESC funding for domestic clean energy supply chains.",
        agency="DOE",
        total_funding=50000000.0,
    )

    report = generate_grounded_winning_angle(db_session, profile, opp, match_score=0.88)
    assert isinstance(report, WinningAngleReport)
    assert "supply chain" in report.winning_hook.lower() or "manufacturing" in report.winning_hook.lower() or "us" in report.strategic_framing.lower()
    assert len(report.mandatory_reviewer_keywords) >= 5


def test_winning_angle_api_endpoint(client, db_session):
    """Test the POST /api/analyze/winning-angle API endpoint with real DB opportunity."""
    first_opp = db_session.query(Opportunity).first()
    if not first_opp:
        pytest.skip("No opportunities in database to test endpoint.")

    payload = {
        "opportunity_id": first_opp.id,
        "project_profile": {
            "project_title": "Thermal Energy Storage for Industrial Decarbonization",
            "summary": "High temperature phase change material thermal storage system for manufacturing facilities.",
            "technology_areas": ["Energy Storage", "Thermal Energy", "Industrial Decarbonization"],
            "trl": 6,
            "cost": 5000000.0,
            "location": "New York",
        },
        "match_score": 0.91,
        "force_live": False,
    }

    response = client.post("/api/analyze/winning-angle", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["opportunity_id"] == first_opp.id
    assert "winning_hook" in data
    assert "hidden_rubric_breakdown" in data
    assert len(data["hidden_rubric_breakdown"]) >= 4
    assert "mandatory_reviewer_keywords" in data
    assert len(data["mandatory_reviewer_keywords"]) >= 5
