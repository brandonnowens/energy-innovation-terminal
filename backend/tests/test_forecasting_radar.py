"""
Unit and Integration Test Suite for the Predictive Solicitation Release Forecasting Engine.
"""

import pytest
from app.database import SessionLocal
from app.engine.profile import ProjectProfile
from app.engine.forecasting_radar import (
    get_predictive_solicitation_forecasts,
    match_project_against_forecasts,
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


def test_statutory_and_recurring_forecasts(db_session):
    """Verify predictive forecasts return known multi-year recurring and flagship solicitations."""
    forecasts = get_predictive_solicitation_forecasts(db_session)
    assert len(forecasts) >= 6
    
    # Check that high-confidence recurring solicitations exist
    program_names = [f["predicted_title"] for f in forecasts]
    assert any("PON 5482" in p or "Storage" in p for p in program_names)
    assert any("OPEN" in p or "ARPA-E" in p for p in program_names)
    assert any("IEDO" in p or "Industrial" in p for p in program_names)

    # Check that each forecast has complete pre-positioning actions
    for f in forecasts:
        assert f["confidence_score"] >= 50
        assert f["forecasted_release_window"] != ""
        assert len(f["pre_positioning_playbook"]) >= 2


def test_forecast_filters(db_session):
    """Verify filtering by agency and horizon."""
    doe_forecasts = get_predictive_solicitation_forecasts(db_session, agency="DOE")
    assert all(f["agency"] == "DOE" for f in doe_forecasts)

    nyserda_forecasts = get_predictive_solicitation_forecasts(db_session, agency="NYSERDA")
    assert all(f["agency"] == "NYSERDA" for f in nyserda_forecasts)


def test_match_project_against_forecasts(db_session):
    """Verify matching a clean energy project profile against forecasted pipeline."""
    profile = ProjectProfile(
        project_title="Industrial Thermal Heat Pump for Food Processing Decarbonization",
        summary="High-temperature industrial heat pump replacing gas boilers in manufacturing plant.",
        technology_areas=["Industrial Decarbonization", "Sustainable Materials & Circular Economy", "Clean Energy Manufacturing"],
        sectors=["Industrial & Manufacturing"],
        applicant_type="commercial",
        project_cost=6000000.0,
        estimated_trl=6,
        target_location="Buffalo, NY",
    )

    matches = match_project_against_forecasts(db_session, profile)
    assert len(matches) > 0
    top_match = matches[0]
    assert "predicted_title" in top_match
    assert "relevance_score_pct" in top_match
    assert "pre_positioning_playbook" in top_match
    assert top_match["relevance_score_pct"] > 50


def test_forecasting_api_endpoints(client):
    """Test GET /api/forecasting/radar and GET /api/forecasting/stats."""
    res_radar = client.get("/api/forecasting/radar")
    assert res_radar.status_code == 200
    data_radar = res_radar.json()
    assert "count" in data_radar
    assert "forecasts" in data_radar
    assert data_radar["count"] > 0

    res_stats = client.get("/api/forecasting/stats")
    assert res_stats.status_code == 200
    data_stats = res_stats.json()
    assert data_stats["total_forecasts"] > 0
    assert data_stats["total_projected_funding"] > 0
    assert "agency_distribution" in data_stats

    res_match = client.post("/api/forecasting/project-radar", json={
        "project_title": "Grid-Scale Long Duration Battery",
        "summary": "Long duration battery storage system for NYISO bulk power grid support.",
        "technology_areas": ["Energy Storage", "Battery Storage"],
        "project_cost": 15000000.0,
        "estimated_trl": 7,
    })
    assert res_match.status_code == 200
    data_match = res_match.json()
    assert data_match["match_count"] > 0
