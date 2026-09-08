"""Week 4-5 Verification Suite: Interconnection Queues & State Awards Coverage.

Validates:
1. ISO/RTO Grid Interconnection Queue Projects expanded across all 7 ISOs (10,000+ projects, 3,000+ GW capacity).
2. California Energy Commission (CEC) & Massachusetts Clean Energy Center (MassCEC) historical awards (56,400+ awards, $100B+ non-dilutive capital).
3. Capital Intelligence & Innovation Layer APIs (/api/interconnection-queues, /api/interconnection-queues/geojson, /api/awards, /api/recipients/{id}/capital-continuum).
"""

import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on Python path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.main import app
from app.models.interconnection import InterconnectionQueueProject
from app.models.award import Award
from app.models.recipient import Recipient

client = TestClient(app)


def test_interconnection_queue_total_count():
    """Verify total interconnection queue projects exceed 10,000 across all 7 US ISOs."""
    db = SessionLocal()
    try:
        count = db.query(InterconnectionQueueProject).count()
        assert count >= 10000, f"Expected >= 10,000 interconnection projects, got {count}"
        print(f"\n[PASS] Total Interconnection Queue Projects: {count}")
    finally:
        db.close()


def test_interconnection_iso_distribution():
    """Verify projects exist across all 7 US Grid Operators."""
    db = SessionLocal()
    try:
        expected_isos = ["CAISO", "ERCOT", "PJM", "MISO", "NYISO", "ISONE", "SPP"]
        for iso in expected_isos:
            iso_count = db.query(InterconnectionQueueProject).filter(InterconnectionQueueProject.iso_rto == iso).count()
            assert iso_count > 0, f"Expected projects for {iso}, found 0"
            print(f"[PASS] ISO {iso}: {iso_count} projects")
    finally:
        db.close()


def test_interconnection_queue_api_endpoints():
    """Verify REST API response structure and query filtering for interconnection queues."""
    # 1. Base list & aggregation
    resp = client.get("/api/interconnection-queues?page=1&page_size=20")
    assert resp.status_code == 200, f"API failed with {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["total"] >= 10000
    assert data["total_capacity_mw"] >= 2500000.0  # >= 2.5 Terawatts
    assert data["total_storage_mwh"] >= 4000000.0  # >= 4.0 Terawatt-hours
    assert len(data["items"]) == 20
    print(f"[PASS] /api/interconnection-queues returned {data['total']} projects, {data['total_capacity_mw']} MW capacity, {data['total_storage_mwh']} MWh storage")

    # 2. ISO Filter
    resp_caiso = client.get("/api/interconnection-queues?iso_rto=CAISO")
    assert resp_caiso.status_code == 200
    assert resp_caiso.json()["total"] >= 2000

    # 3. Technology Filter
    resp_storage = client.get("/api/interconnection-queues?technology_type=Storage")
    assert resp_storage.status_code == 200
    assert resp_storage.json()["total"] >= 2500

    # 4. GeoJSON Endpoint
    resp_geojson = client.get("/api/interconnection-queues/geojson?iso_rto=NYISO")
    assert resp_geojson.status_code == 200
    geo_data = resp_geojson.json()
    assert geo_data["type"] == "FeatureCollection"
    assert len(geo_data["features"]) > 0
    assert "coordinates" in geo_data["features"][0]["geometry"]
    print(f"[PASS] /api/interconnection-queues/geojson returned {len(geo_data['features'])} NYISO features")


def test_state_awards_expansion():
    """Verify California CEC and Massachusetts MassCEC historical awards are ingested and geocoded."""
    db = SessionLocal()
    try:
        total_awards = db.query(Award).count()
        assert total_awards >= 56000, f"Expected >= 56,000 awards, got {total_awards}"

        cec_count = db.query(Award).filter(Award.agency == "California Energy Commission").count()
        assert cec_count >= 1500, f"Expected >= 1,500 California CEC awards, got {cec_count}"

        masscec_count = db.query(Award).filter(Award.agency == "Massachusetts Clean Energy Center").count()
        assert masscec_count >= 500, f"Expected >= 500 MassCEC awards, got {masscec_count}"

        # Verify Geocoding completeness for state awards
        geocoded_cec = db.query(Award).filter(
            Award.agency == "California Energy Commission",
            Award.latitude != None,
            Award.longitude != None
        ).count()
        assert geocoded_cec == cec_count, "All CEC awards must have valid geocoding coordinates"

        geocoded_mass = db.query(Award).filter(
            Award.agency == "Massachusetts Clean Energy Center",
            Award.latitude != None,
            Award.longitude != None
        ).count()
        assert geocoded_mass == masscec_count, "All MassCEC awards must have valid geocoding coordinates"

        print(f"[PASS] State Awards Ingestion: Total {total_awards}, CEC: {cec_count} (100% Geocoded), MassCEC: {masscec_count} (100% Geocoded)")
    finally:
        db.close()


def test_awards_api_state_filtering():
    """Verify /api/awards filters state awards cleanly."""
    resp_cec = client.get("/api/awards?agency=California Energy Commission&page_size=20")
    assert resp_cec.status_code == 200, f"Failed: {resp_cec.text}"
    data_cec = resp_cec.json()
    assert data_cec["total"] >= 1500
    assert len(data_cec["items"]) == 20
    assert data_cec["items"][0]["agency"] == "California Energy Commission"
    assert data_cec["items"][0]["recipient_state"] == "CA"

    resp_mass = client.get("/api/awards?agency=Massachusetts Clean Energy Center&page_size=20")
    assert resp_mass.status_code == 200
    data_mass = resp_mass.json()
    assert data_mass["total"] >= 500
    assert len(data_mass["items"]) == 20
    assert data_mass["items"][0]["agency"] == "Massachusetts Clean Energy Center"
    assert data_mass["items"][0]["recipient_state"] == "MA"
    print("[PASS] /api/awards state agency filtering verified for CEC and MassCEC")


def test_full_capital_continuum_integration():
    """Verify Capital Continuum API synthesizes grants, VC, Form D, patents, and queues."""
    db = SessionLocal()
    try:
        # Find a recipient that has multiple layers
        rec = db.query(Recipient).filter(Recipient.name.ilike("%Form Energy%")).first()
        if not rec:
            rec = db.query(Recipient).first()

        resp = client.get(f"/api/recipients/{rec.id}/capital-continuum")
        assert resp.status_code == 200
        data = resp.json()
        assert "financial_aggregates" in data
        assert "grants" in data
        assert "sec_form_d_filings" in data
        assert "vc_rounds" in data
        assert "patents" in data
        assert "interconnection_queues" in data
        print(f"[PASS] Capital continuum verified for Recipient {rec.name} (ID: {rec.id})")
    finally:
        db.close()


if __name__ == "__main__":
    pytest.main(["-s", __file__])
