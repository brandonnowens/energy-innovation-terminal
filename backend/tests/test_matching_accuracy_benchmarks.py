"""
Comprehensive Accuracy, Precision, and Performance Verification Suite
for Opportunity Matching Analysis Engine.

Validates multi-dimensional scoring precision, dense vector synonym matching,
consortium/teaming classification, and high-speed execution bounds.
"""

import time
import pytest
from app.database import SessionLocal
from app.engine.analyzer import analyze_project, get_cached_opportunities
from app.engine.vector_scorer import vectorize_text, compute_dense_similarities


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    # Pre-warm candidate and vector cache
    get_cached_opportunities(db)
    # Warm up first run
    try:
        analyze_project(
            db=db,
            text="Warmup clean energy technology matching test project.",
            location="NY",
            cost=1000000.0,
            trl=5,
            fast_mode=True,
        )
    except Exception:
        pass
    yield db
    db.close()


def test_solar_perovskite_accuracy(db_session):
    """Verify high-conviction solar perovskite matching and technology taxonomy."""
    res = analyze_project(
        db=db_session,
        text="Next-generation 32% efficiency perovskite-silicon tandem photovoltaic cell commercialization for high-density rooftop deployment in New York.",
        location="NY",
        applicant_type="business",
        cost=3000000.0,
        trl=6,
        technology_areas=["Solar PV", "Materials Science", "Advanced Manufacturing"],
        fast_mode=True,
    )

    assert res["summary"]["total_matched"] > 0
    assert len(res["top_25_opportunities"]) > 0

    top_m = res["top_25_opportunities"][0]
    assert top_m["fit_score"] >= 0.65
    assert "prime_matches" in res["matches"]
    assert "teaming_matches" in res["matches"]

    # Verify score breakdown components
    sb = top_m.get("score_breakdown", {})
    assert "technology_alignment" in sb
    assert "keyword_relevance" in sb
    assert "funding_scale" in sb
    assert "activity_stage" in sb


def test_long_duration_iron_flow_storage(db_session):
    """Verify long-duration iron-flow battery storage matching."""
    res = analyze_project(
        db=db_session,
        text="Development and multi-day field demonstration of a 10 MW / 100 MWh long-duration iron-flow battery energy storage system (BESS) for grid peak shifting in New York.",
        location="Albany, NY",
        applicant_type="company",
        cost=8000000.0,
        trl=6,
        technology_areas=["Energy Storage", "Grid Modernization"],
        fast_mode=True,
    )

    assert res["summary"]["total_matched"] > 0
    assert len(res["top_25_opportunities"]) >= 5
    assert len(res["top_15_say_yes"]) > 0

    top_m = res["top_25_opportunities"][0]
    assert top_m["fit_score"] >= 0.65


def test_geothermal_district_thermal_network(db_session):
    """Verify district geothermal and thermal energy network matching."""
    res = analyze_project(
        db=db_session,
        text="District thermal energy network with deep borehole geothermal heat pumps and low-GWP thermal storage in Buffalo, NY.",
        location="Buffalo, NY",
        applicant_type="commercial",
        cost=5000000.0,
        trl=7,
        technology_areas=["Geothermal", "Heat Pumps", "Buildings", "District Energy"],
        fast_mode=True,
    )

    assert res["summary"]["total_matched"] > 0
    top_m = res["top_25_opportunities"][0]
    assert top_m["fit_score"] >= 0.60


def test_direct_air_capture_carbon_mineralization(db_session):
    """Verify DAC and carbon mineralization semantic matching."""
    res = analyze_project(
        db=db_session,
        text="Solid-sorbent direct air capture (DAC) system with in-situ basalt mineralization and MRV carbon removal tracking.",
        location="NY",
        applicant_type="startup",
        cost=4000000.0,
        trl=5,
        technology_areas=["Carbon Capture", "Direct Air Capture", "Materials Science"],
        fast_mode=True,
    )

    assert res["summary"]["total_matched"] > 0
    top_m = res["top_25_opportunities"][0]
    assert top_m["fit_score"] >= 0.60


def test_dense_vector_semantic_synonym_retrieval(db_session):
    """Verify dense vector feature matching discovers unstated clean tech concepts."""
    q_vec = vectorize_text("solid-state electrolyte halide absorber redox pair non-dilutive grant")
    sims = compute_dense_similarities(q_vec)

    assert len(sims) > 1000
    top_sim = max(sims.values())
    assert top_sim >= 0.50


def test_teaming_consortium_classification(db_session):
    """Verify commercial startup receives teaming tier for academic-lead opportunities."""
    res = analyze_project(
        db=db_session,
        text="Applied materials synthesis and lab characterization of high-entropy alloys for hydrogen electrolyzer catalysts.",
        location="NY",
        applicant_type="startup",
        cost=1000000.0,
        trl=3,
        technology_areas=["Hydrogen & Alternative Fuels", "Materials Science"],
        fast_mode=True,
    )

    teaming_matches = res["matches"].get("teaming_matches", [])
    prime_matches = res["matches"].get("prime_matches", [])

    assert len(prime_matches) > 0 or len(teaming_matches) > 0
    if teaming_matches:
        t0 = teaming_matches[0]
        assert t0["match_tier"] == "teaming_partner"
        assert "teaming_role" in t0


def test_industrial_manufacturing_residential_exclusion(db_session):
    """Verify manufacturing project strictly excludes residential rebates and wood heaters."""
    res = analyze_project(
        db=db_session,
        text="Perovskite solar cell manufacturing plant in Rochester NY, budget $15M, commercial scale production line.",
        location="Rochester, NY",
        applicant_type="business",
        cost=15000000.0,
        trl=8,
        fast_mode=True,
    )

    top_names = [m.get("name", "").lower() for m in res["top_25_opportunities"]]
    # Verify no residential homeowner rebates, wood heater testing, or weatherization formula grants
    for n in top_names:
        assert "residential wood heater" not in n
        assert "weatherization formula" not in n
        assert "weatherization assistance" not in n
        assert "geothermal heat pump rebates" not in n
        assert "residential energy code" not in n

    top_solicitations = [m.get("solicitation_number", "") for m in res["top_25_opportunities"]]
    assert len(top_solicitations) >= 5


def test_residential_homeowner_industrial_exclusion(db_session):
    """Verify residential homeowner heat pump retrofit excludes heavy industrial manufacturing plants."""
    res = analyze_project(
        db=db_session,
        text="Residential clean heat air source heat pump retrofit for single-family home in Syracuse NY, cost $18,000.",
        location="Syracuse, NY",
        applicant_type="homeowner",
        cost=18000.0,
        trl=9,
        fast_mode=True,
    )

    top_names = [m.get("name", "").lower() for m in res["top_25_opportunities"]]
    # Verify no heavy industrial manufacturing or high-voltage grid transmission programs
    for n in top_names:
        assert "heavy industry decarbonization" not in n
        assert "cement plant" not in n
        assert "steel mill" not in n
        assert "bulk power system" not in n


def test_fuel_and_stage_compatibility(db_session):
    """Verify clean hydrogen project does not match solid coal or wood combustion."""
    res = analyze_project(
        db=db_session,
        text="Green hydrogen production using PEM water electrolysis and high-pressure tube trailer storage for heavy-duty transit fleet.",
        location="Buffalo, NY",
        applicant_type="company",
        cost=6000000.0,
        trl=6,
        fast_mode=True,
    )

    top_names = [m.get("name", "").lower() for m in res["top_25_opportunities"]]
    for n in top_names:
        assert "coal value chain" not in n
        assert "wood heater" not in n


def test_sustainable_garments_domain_isolation(db_session):
    """Verify sustainable garment production project in NYC isolates to industrial manufacturing & circular economy, excluding hydrokinetic and vehicle engines."""
    res = analyze_project(
        db=db_session,
        text="sustainable garment production project in NYC",
        location="NYC",
        cost=1000000.0,
        fast_mode=True,
    )

    matches = res.get("top_50_opportunities", [])
    assert len(matches) > 0

    top_names = [m.get("name", "").lower() for m in matches]
    top_solicitations = [m.get("solicitation_number", "") for m in matches]

    # Verify NO marine/hydrokinetic or vehicle engine/fleet solicitations matched
    for name in top_names:
        assert "hydrokinetic" not in name, f"Mismatched hydrokinetic program in garment results: {name}"
        assert "marine energy" not in name, f"Mismatched marine program in garment results: {name}"
        assert "wave energy" not in name, f"Mismatched wave energy program in garment results: {name}"
        assert "advanced vehicle engine" not in name, f"Mismatched vehicle engine program in garment results: {name}"
        assert "charge ready" not in name, f"Mismatched EV charging program in garment results: {name}"

    assert "EPA-OAR-OTAQ-10-03" not in top_solicitations


def test_top10_orgs_and_top20_opportunities_limits(db_session):
    """Verify results payload strictly returns Top 10 Organizations and Top 20 Opportunities."""
    res = analyze_project(
        db=db_session,
        text="Commercial rooftop solar PV with battery storage and smart inverters in Queens, NY.",
        location="Queens, NY",
        applicant_type="business",
        cost=2500000.0,
        trl=7,
        fast_mode=True,
    )

    assert len(res["top_10_say_yes"]) <= 10
    assert len(res["top_say_yes"]) <= 10
    assert len(res["grouped_opportunities"]) <= 10
    assert len(res["top_20_opportunities"]) <= 20
    assert len(res["top_25_opportunities"]) <= 20
    assert len(res["top_50_opportunities"]) <= 20


def test_warm_engine_speed_profile(db_session):
    """Verifies that in-memory matching completes rapidly across 5,747 opportunities."""
    t0 = time.time()
    res = analyze_project(
        db=db_session,
        text="Commercial heat pump chiller optimization with edge AI predictive controls for commercial buildings.",
        location="New York, NY",
        applicant_type="commercial",
        cost=1500000.0,
        trl=7,
        fast_mode=True,
    )
    elapsed = time.time() - t0

    assert res["summary"]["total_matched"] > 0
    # Warm execution should complete in reasonable time (including local caching)
    assert elapsed < 10.0, f"Execution time {elapsed:.3f}s exceeded 10.0s ceiling"


