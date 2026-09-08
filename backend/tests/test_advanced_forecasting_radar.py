"""
Advanced Integration & Verification Test Suite for the Early-Warning Forecasting Radar.

Validates:
1. Probabilistic opportunity release projections across all 250 database organizations.
2. Empirical cadence analytics (mean inter-release interval, standard deviation, regularity index).
3. Statutory appropriations and policy mandate alignment.
4. Probabilistic forecast and public information disclaimer presence across all outputs.
5. Organization briefing and project radar matching endpoints.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.organization import Organization
from app.engine.profile import ProjectProfile
from app.engine.forecasting_radar import (
    get_forecasting_organization_directory,
    get_predictive_solicitation_forecasts,
    match_project_against_forecasts,
    synthesize_llm_projection_briefing,
    _calculate_cadence_stats,
    PROBABILISTIC_DISCLAIMER,
)


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_full_database_organization_coverage(db: Session):
    """Verify that forecasting directory covers ALL organizations present in PostgreSQL."""
    total_db_orgs = db.query(Organization).count()
    directory = get_forecasting_organization_directory(db)
    
    assert len(directory) == total_db_orgs
    assert len(directory) >= 150

    # Verify every directory entry has complete probabilistic metadata
    for org in directory:
        assert "organization_id" in org
        assert "organization_code" in org
        assert "category" in org
        assert "total_pipeline_funding" in org
        assert "cadence_regularity_score" in org
        assert "next_release_horizon" in org
        assert org["disclaimer"] == PROBABILISTIC_DISCLAIMER
        assert org["is_probabilistic_forecast"] is True


def test_cadence_statistical_metrics():
    """Verify mathematical calculation of cadence interval, variance, and regularity index."""
    # Test case 1: Regular annual releases (12 months interval)
    dates_annual = [
        datetime(2021, 10, 15, tzinfo=timezone.utc),
        datetime(2022, 10, 12, tzinfo=timezone.utc),
        datetime(2023, 10, 18, tzinfo=timezone.utc),
        datetime(2024, 10, 14, tzinfo=timezone.utc),
    ]
    cadence_annual = _calculate_cadence_stats(dates_annual, [2021, 2022, 2023, 2024], "state")
    assert 11.0 <= cadence_annual["mean_interval_months"] <= 13.0
    assert cadence_annual["std_dev_months"] < 1.0
    assert cadence_annual["regularity_score"] >= 90
    assert cadence_annual["peak_quarter"] == "Q4"

    # Test case 2: Semi-annual releases (6 months interval)
    dates_semiannual = [
        datetime(2023, 4, 1, tzinfo=timezone.utc),
        datetime(2023, 10, 1, tzinfo=timezone.utc),
        datetime(2024, 4, 1, tzinfo=timezone.utc),
        datetime(2024, 10, 1, tzinfo=timezone.utc),
    ]
    cadence_semi = _calculate_cadence_stats(dates_semiannual, [2023, 2024], "state")
    assert 5.0 <= cadence_semi["mean_interval_months"] <= 7.0
    assert cadence_semi["regularity_score"] >= 88


def test_predictive_solicitation_forecasts_breadth(db: Session):
    """Verify generation of forecasts across all database organizations."""
    forecasts = get_predictive_solicitation_forecasts(db)
    assert len(forecasts) >= 150

    # Verify categories represented
    categories = {f["organization_category"] for f in forecasts}
    assert "state" in categories
    assert "federal" in categories
    assert "utility" in categories
    assert "foundation" in categories

    # Verify required analytical attributes on all forecasts
    for fc in forecasts:
        assert "predicted_title" in fc
        assert "forecasted_release_window" in fc
        assert "days_until_release" in fc
        assert "confidence_score" in fc
        assert "confidence_tier" in fc
        assert "projected_funding_envelope" in fc
        assert "projected_funding_range" in fc
        assert "statutory_driver" in fc
        assert len(fc["pre_positioning_playbook"]) >= 2
        assert fc["disclaimer"] == PROBABILISTIC_DISCLAIMER
        assert fc["is_probabilistic_forecast"] is True


def test_forecasting_api_endpoints_disclaimer_and_filtering(client: TestClient):
    """Verify API endpoints return structured metadata and probabilistic disclaimers."""
    # 1. GET /api/forecasting/organizations
    res_orgs = client.get("/api/forecasting/organizations")
    assert res_orgs.status_code == 200
    data_orgs = res_orgs.json()
    assert data_orgs["count"] >= 150
    assert data_orgs["disclaimer"] == PROBABILISTIC_DISCLAIMER
    assert data_orgs["total_tracked_pipeline"] > 1_000_000_000

    # 2. GET /api/forecasting/radar with category filter
    res_radar_util = client.get("/api/forecasting/radar?category=utility")
    assert res_radar_util.status_code == 200
    data_radar_util = res_radar_util.json()
    assert data_radar_util["count"] > 0
    assert all(f["organization_category"] == "utility" for f in data_radar_util["forecasts"])
    assert data_radar_util["disclaimer"] == PROBABILISTIC_DISCLAIMER

    # 3. GET /api/forecasting/stats
    res_stats = client.get("/api/forecasting/stats")
    assert res_stats.status_code == 200
    data_stats = res_stats.json()
    assert data_stats["total_organizations"] >= 150
    assert data_stats["total_forecasts"] >= 150
    assert "category_distribution" in data_stats
    assert data_stats["disclaimer"] == PROBABILISTIC_DISCLAIMER


def test_organization_briefing_endpoint(client: TestClient):
    """Verify on-demand probabilistic briefing synthesis endpoint for organizations."""
    res_briefing = client.get("/api/forecasting/briefing/NYSERDA")
    assert res_briefing.status_code == 200
    data_b = res_briefing.json()
    assert data_b["status"] == "success"
    assert "briefing" in data_b
    assert "cadence_regularity_score" in data_b
    assert data_b["disclaimer"] == PROBABILISTIC_DISCLAIMER


def test_project_radar_matching(client: TestClient):
    """Verify project matching against upcoming probabilistic forecasts."""
    req_body = {
        "project_title": "Advanced Geothermal District Energy Network",
        "summary": "Demonstration of utility-scale thermal energy network in upstate NY.",
        "technology_areas": ["Thermal Energy Networks", "Geothermal Energy", "Heat Pumps"],
        "sectors": ["Commercial Real Estate", "Electric Power"],
        "target_location": "Albany, NY",
        "project_cost": 12000000.0,
        "estimated_trl": 6,
    }
    res_match = client.post("/api/forecasting/project-radar", json=req_body)
    assert res_match.status_code == 200
    data_match = res_match.json()
    assert data_match["match_count"] > 0
    assert data_match["disclaimer"] == PROBABILISTIC_DISCLAIMER
    top = data_match["matched_forecasts"][0]
    assert "relevance_score_pct" in top
    assert top["relevance_score_pct"] >= 50
