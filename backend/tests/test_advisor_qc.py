"""
Unit and Integration Test Suite for the Final LLM Advisor QC Layer.

Verifies:
1. Domain mismatch screening: Sustainable clothing / garment manufacturing projects
   screen out battery cell manufacturing, EV charging, and marine energy opportunities.
2. Domain alignment approval: Sustainable clothing / garment projects approve
   industrial decarbonization and clean manufacturing solicitations.
3. Residential vs heavy industrial exclusion.
4. Batch multi-threaded screening with metadata enrichment.
5. End-to-end integration into `analyze_project` orchestrator.
"""

import pytest
from app.database import SessionLocal
from app.models.opportunity import Opportunity
from app.engine.profile import ProjectProfile, extract_profile
from app.engine.analyzer import analyze_project, get_cached_opportunities
from app.engine.advisor_qc import (
    AdvisorQCVerdict,
    evaluate_deterministic_advisor_qc,
    evaluate_opportunity_with_advisor_qc,
    screen_matched_opportunities_with_advisor,
)


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    get_cached_opportunities(db)
    yield db
    db.close()


def test_sustainable_clothing_vs_battery_mismatch():
    """Verify that a sustainable clothing manufacturing project screens out battery manufacturing."""
    profile = ProjectProfile(
        project_title="Circular Textile & Sustainable Garment Production Plant",
        summary="Commercial facility for sustainable clothing and circular textile manufacturing from recycled post-consumer fibers in Brooklyn, NY.",
        technology_areas=["Industrial Decarbonization", "Clean Energy Manufacturing"],
        sectors=["Industrial", "Commercial"],
        applicant_type="business",
        project_cost=2000000.0,
        estimated_trl=7,
        target_location="Brooklyn, NY",
    )

    # Battery manufacturing opportunity
    opp_battery = Opportunity(
        id=9001,
        solicitation_number="DE-FOA-0002800",
        name="Advanced Battery Cell Manufacturing and Cathode Active Materials Processing",
        short_description="Funding for commercial-scale manufacturing of lithium-ion battery cells, solid-state electrolytes, and advanced battery packs.",
        objectives="Expand domestic manufacturing capacity for electric vehicle and grid-scale lithium battery energy storage systems.",
        agency="DOE",
    )

    verdict = evaluate_deterministic_advisor_qc(profile, opp_battery)
    assert verdict.makes_sense is False
    assert verdict.decision == "SCREENED_OUT"
    assert verdict.domain_alignment == "mismatch"
    assert "clothing" in verdict.reason.lower() or "garment" in verdict.reason.lower() or "battery" in verdict.reason.lower()


def test_sustainable_clothing_vs_clean_manufacturing_approval():
    """Verify that a sustainable clothing manufacturing project approves clean industrial manufacturing."""
    profile = ProjectProfile(
        project_title="Circular Textile & Sustainable Garment Production Plant",
        summary="Commercial facility for sustainable clothing and circular textile manufacturing from recycled post-consumer fibers in Brooklyn, NY.",
        technology_areas=["Industrial Decarbonization", "Clean Energy Manufacturing"],
        sectors=["Industrial"],
        applicant_type="business",
        project_cost=2000000.0,
        estimated_trl=7,
        target_location="Brooklyn, NY",
    )

    # Clean manufacturing opportunity
    opp_manufacturing = Opportunity(
        id=9002,
        solicitation_number="PON 4000",
        name="Industrial Decarbonization and Clean Energy Manufacturing Innovation Program",
        short_description="Incentives and grants for industrial facilities to adopt low-carbon manufacturing processes, waste heat recovery, and circular materials.",
        objectives="Support New York manufacturers in reducing embodied emissions and implementing innovative sustainable production technologies.",
        agency="NYSERDA",
    )

    verdict = evaluate_deterministic_advisor_qc(profile, opp_manufacturing)
    assert verdict.makes_sense is True
    assert verdict.decision == "APPROVED"
    assert verdict.domain_alignment == "aligned"
    assert verdict.confidence >= 0.80


def test_residential_vs_heavy_industry_screening():
    """Verify that a single-family residential heat pump project screens out heavy industrial cement/steel solicitations."""
    profile = ProjectProfile(
        project_title="Residential Air-Source Heat Pump Retrofit",
        summary="Installation of residential clean heat air source heat pumps for a single-family home in Syracuse, NY.",
        technology_areas=["Building Electrification", "Heat Pumps"],
        sectors=["Residential"],
        applicant_type="homeowner",
        project_cost=15000.0,
        estimated_trl=9,
        target_location="Syracuse, NY",
    )

    opp_heavy_industry = Opportunity(
        id=9003,
        solicitation_number="DE-FOA-0003100",
        name="Heavy Industry Decarbonization: Green Steel and Cement Kiln Conversion",
        short_description="Large-scale demonstration of low-carbon blast furnaces, direct reduced iron (DRI), and cement plant clinker electrification.",
        objectives="Demonstrate deep decarbonization of energy-intensive heavy manufacturing plants.",
        agency="DOE",
    )

    verdict = evaluate_deterministic_advisor_qc(profile, opp_heavy_industry)
    assert verdict.makes_sense is False
    assert verdict.decision == "SCREENED_OUT"
    assert "residential" in verdict.reason.lower() or "industrial" in verdict.reason.lower()


def test_commercial_vs_residential_rebate_screening():
    """Verify that a commercial clean tech enterprise screens out residential homeowner rebates."""
    profile = ProjectProfile(
        project_title="Commercial Microgrid & Megawatt Battery Facility",
        summary="Development of a 5 MW microgrid with commercial battery storage for an industrial park in Queens, NY.",
        technology_areas=["Microgrids & Resilience", "Energy Storage"],
        sectors=["Commercial", "Industrial"],
        applicant_type="business",
        project_cost=8000000.0,
        estimated_trl=7,
        target_location="Queens, NY",
    )

    opp_res_rebate = Opportunity(
        id=9004,
        solicitation_number="PON 1001",
        name="Residential Wood Heater Replacement and Single-Family Homeowner Rebates",
        short_description="Rebates for homeowners to replace inefficient wood stoves with clean heating appliances.",
        objectives="Reduce residential particulate emissions for single-family residences.",
        agency="NYSERDA",
    )

    verdict = evaluate_deterministic_advisor_qc(profile, opp_res_rebate)
    assert verdict.makes_sense is False
    assert verdict.decision == "SCREENED_OUT"


def test_screen_matched_opportunities_batch_filtering():
    """Verify batch multi-threaded screening filters out mismatched opportunities and enriches valid ones."""
    profile = ProjectProfile(
        project_title="Sustainable Garment Manufacturing & Textile Circularity Hub",
        summary="Sustainable clothing and apparel manufacturing plant utilizing low-emission cutting, waterless dyeing, and fiber recycling.",
        technology_areas=["Industrial Decarbonization", "Clean Energy Manufacturing"],
        sectors=["Industrial"],
        applicant_type="business",
        project_cost=3000000.0,
        estimated_trl=7,
        target_location="New York, NY",
    )

    opp1 = Opportunity(
        id=101,
        solicitation_number="PON-CLEAN-MFG",
        name="Clean Manufacturing & Industrial Circularity",
        short_description="Grants for clean industrial production and circular material processing.",
        agency="NYSERDA",
    )
    opp2 = Opportunity(
        id=102,
        solicitation_number="FOA-BATTERY-CELL",
        name="Lithium-Ion Battery Cell Manufacturing Scale-Up",
        short_description="Capital grants for lithium battery cell manufacturing lines and cathode processing.",
        agency="DOE",
    )
    opp3 = Opportunity(
        id=103,
        solicitation_number="FOA-EV-CHARGING",
        name="Electric Vehicle Fleet Charging Infrastructure",
        short_description="Deployment of fast DC chargers for commercial vehicle fleets.",
        agency="DOT",
    )

    opps_by_id = {101: opp1, 102: opp2, 103: opp3}
    matches = [
        {"opportunity_id": 101, "fit_score": 0.88, "name": opp1.name},
        {"opportunity_id": 102, "fit_score": 0.82, "name": opp2.name},
        {"opportunity_id": 103, "fit_score": 0.80, "name": opp3.name},
    ]

    approved, screened_out = screen_matched_opportunities_with_advisor(
        profile=profile,
        matches=matches,
        opportunities_by_id=opps_by_id,
        fast_mode=True,
    )

    assert len(approved) == 1
    assert approved[0]["opportunity_id"] == 101
    assert approved[0]["advisor_qc"]["makes_sense"] is True
    assert approved[0]["advisor_qc"]["decision"] == "APPROVED"

    assert len(screened_out) == 2
    screened_ids = [m["opportunity_id"] for m in screened_out]
    assert 102 in screened_ids
    assert 103 in screened_ids


def test_analyze_project_with_advisor_qc_integration(db_session):
    """Verify that analyze_project runs the Advisor QC screening and filters out battery solicitations for garment project."""
    res = analyze_project(
        db=db_session,
        text="Sustainable garment manufacturing and recycled textile circularity plant in Brooklyn, NY. Budget $2.5M.",
        location="Brooklyn, NY",
        applicant_type="business",
        cost=2500000.0,
        trl=7,
        fast_mode=True,
    )

    assert "advisor_qc_screened_count" in res["summary"]
    assert "advisor_qc_verified_count" in res["summary"]
    assert res["summary"]["advisor_qc_verified_count"] > 0

    top_matches = res.get("top_20_opportunities", [])
    for m in top_matches:
        name_lower = (m.get("name") or "").lower()
        # Ensure no battery manufacturing opportunities slipped through
        assert "battery cell manufacturing" not in name_lower
        assert "lithium-ion battery" not in name_lower
        assert "advanced battery chemistry" not in name_lower
        if "advisor_qc" in m:
            assert m["advisor_qc"]["makes_sense"] is True
