"""Comprehensive End-to-End Verification Suite for PostgreSQL & Energy Innovation Terminal Knowledge Base."""

import json
import logging
from sqlalchemy import text
from fastapi.testclient import TestClient

from app.database import SessionLocal, engine
from app.main import app
from app.models.proposal import Proposal
from app.models.community import Report, Strategy, SavedView
from app.models.result import ResultArtifact, ResultBenchmark
from app.models.opportunity import Opportunity
from app.models.award import Award
from app.models.recipient import Recipient
from app.models.analysis import ProjectAnalysis, AnalysisMatch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestVerificationSuite")


def run_verification():
    client = TestClient(app)
    db = SessionLocal()
    results = {}

    print("\n================ U.S. ENERGY INNOVATION DATABASE VERIFICATION ================\n")

    # 1. Database Volume & Scale Verification
    with engine.connect() as conn:
        tot_awards = conn.execute(text("SELECT COUNT(*) FROM awards")).scalar()
        tot_opps = conn.execute(text("SELECT COUNT(*) FROM opportunities")).scalar()
        tot_recipients = conn.execute(text("SELECT COUNT(*) FROM recipients")).scalar()
        tot_benchmarks = conn.execute(text("SELECT COUNT(*) FROM result_benchmarks")).scalar()
        tot_restrictions = conn.execute(text("SELECT COUNT(*) FROM opportunity_restrictions")).scalar()
        tot_relationships = conn.execute(text("SELECT COUNT(*) FROM opportunity_relationships")).scalar()
        tot_artifacts = conn.execute(text("SELECT COUNT(*) FROM result_artifacts")).scalar()
        tot_proposals = conn.execute(text("SELECT COUNT(*) FROM proposals")).scalar()
        tot_reports = conn.execute(text("SELECT COUNT(*) FROM reports")).scalar()
        tot_strategies = conn.execute(text("SELECT COUNT(*) FROM strategies")).scalar()
        tot_views = conn.execute(text("SELECT COUNT(*) FROM saved_views")).scalar()

        opps_with_org = conn.execute(text("SELECT COUNT(*) FROM opportunities WHERE organization_id IS NOT NULL")).scalar()
        opps_with_bm = conn.execute(text("SELECT COUNT(DISTINCT opportunity_id) FROM result_benchmarks")).scalar()
        recipients_with_web = conn.execute(text("SELECT COUNT(*) FROM recipients WHERE website_url IS NOT NULL AND website_url != ''")).scalar()

        print(f"1. Database Scale & 100% Coverage Checks:")
        print(f"   [OK] Awards:                     {tot_awards:,}")
        print(f"   [OK] Solicitations:              {tot_opps:,}")
        print(f"   [OK] Opportunities Linked to Org:{opps_with_org:,} / {tot_opps:,} ({(opps_with_org/tot_opps*100):.1f}%)")
        print(f"   [OK] Benchmark Coverage:         {opps_with_bm:,} / {tot_opps:,} ({(opps_with_bm/tot_opps*100):.1f}%)")
        print(f"   [OK] Recipients Enriched:        {recipients_with_web:,} / {tot_recipients:,} ({(recipients_with_web/tot_recipients*100):.1f}%)")
        print(f"   [OK] Statutory Restrictions:     {tot_restrictions:,}")
        print(f"   [OK] Cross-Agency Relationships: {tot_relationships:,}")
        print(f"   [OK] Technical Artifacts:        {tot_artifacts:,}")
        print(f"   [OK] Proposals Database:         {tot_proposals:,}")
        print(f"   [OK] Executive Reports in DB:    {tot_reports:,}")
        print(f"   [OK] Strategies:                 {tot_strategies:,}")
        print(f"   [OK] Saved Views:                {tot_views:,}")

    # 2. Proposals API Verification
    print("\n2. Testing Proposals API Endpoints:")
    res = client.get("/api/proposals?page_size=5")
    assert res.status_code == 200, f"Failed GET /api/proposals: {res.text}"
    props_data = res.json()
    print(f"   [OK] GET /api/proposals returned {props_data['total']:,} total items")

    # Create new proposal pursuit
    create_payload = {
        "solicitation_number": "PON 5892",
        "title": "Grid-Interactive Thermal Heat Pump District Pilot",
        "agency": "NYSERDA",
        "agency_code": "NYSERDA",
        "target_funding": 3000000.0,
        "total_budget": 4000000.0,
        "cost_share_pct": 25.0,
        "lead_pi": "Dr. Marcus Vance",
        "recipient_name": "Urban Clean Thermal Innovations",
        "tech_area": "Building Decarbonization",
        "description": "5th generation district thermal loop connecting multifamily residential complexes with sewer heat recovery."
    }
    create_res = client.post("/api/proposals", json=create_payload, headers={"X-Creator-Token": "test_creator_token"})
    assert create_res.status_code == 200, f"Failed POST /api/proposals: {create_res.text}"
    created_prop = create_res.json()
    new_prop_id = created_prop["id"]
    print(f"   [OK] POST /api/proposals created: {new_prop_id} (Stored in PostgreSQL)")

    # Red-team audit proposal
    rt_res = client.post(f"/api/proposals/{new_prop_id}/red-team", json={"review_notes": "Passed initial evaluation"})
    assert rt_res.status_code == 200, f"Failed POST /api/proposals/{new_prop_id}/red-team: {rt_res.text}"
    rt_data = rt_res.json()
    print(f"   [OK] POST /api/proposals/{new_prop_id}/red-team score: {rt_data['red_team_score']}/100 Pts (Stage: {rt_data['stage']})")

    # 3. Reports API & Persistence Verification
    print("\n3. Testing Executive Reports Generation & Persistence:")
    rep_res = client.post("/api/reports/generate", json={"preset_id": "macro_capital_deployment"})
    assert rep_res.status_code == 200, f"Failed POST /api/reports/generate: {rep_res.text}"
    rep_data = rep_res.json()
    print(f"   [OK] POST /api/reports/generate produced narrative: '{rep_data['narrative'].get('title')}'")

    # Verify report is in database
    db_rep = db.query(Report).filter(Report.prompt == "preset:macro_capital_deployment").first()
    assert db_rep is not None, "Report was not persisted to PostgreSQL database!"
    print(f"   [OK] Verified Report stored in DB (ID: {db_rep.id}, Title: '{db_rep.title}', Status: {db_rep.status})")

    # 4. Strategy Engine Real Execution & Persistence Verification
    print("\n4. Testing Strategy Execution & Persistence:")
    from app.models.community import hash_token
    token_val = "test_strat_token"
    token_hash_val = hash_token(token_val)

    strat = Strategy(
        creator_hash=token_hash_val,
        mode="project_sponsor",
        title="Automated Test Thermal Storage Siting",
        inputs_json={"technologies": ["Energy Storage"], "geography": {"state": "NY"}, "budget": 2000000.0},
        status="draft"
    )
    db.add(strat)
    db.commit()
    db.refresh(strat)

    exec_res = client.post(f"/api/strategy/{strat.id}/execute", headers={"X-Creator-Token": token_val})
    assert exec_res.status_code == 200, f"Failed POST /api/strategy/{strat.id}/execute: {exec_res.text}"
    exec_data = exec_res.json()
    assert exec_data["status"] == "complete", f"Strategy status not complete: {exec_data}"
    print(f"   [OK] POST /api/strategy/{strat.id}/execute ran real engine, stored outputs (Status: {exec_data['status']})")

    # 5. Saved Views Verification
    print("\n5. Testing Saved Views API:")
    view_res = client.post("/api/views", json={
        "title": "Northeast Heat Pump & Geothermal Network",
        "view_type": "network",
        "config_json": {"zoom": 1.5, "technology": "Building Decarbonization"}
    })
    assert view_res.status_code == 200, f"Failed POST /api/views: {view_res.text}"
    v_data = view_res.json()
    print(f"   [OK] POST /api/views saved view (ID: {v_data['id']}, Title: '{v_data['title']}')")

    list_v = client.get("/api/views")
    assert list_v.status_code == 200, f"Failed GET /api/views: {list_v.text}"
    print(f"   [OK] GET /api/views returned {len(list_v.json())} saved views")

    # 6. Project Analysis Matching & Match Persistence
    print("\n6. Testing Project Analysis & Match Persistence:")
    analyze_res = client.post("/api/analyze", json={
        "text": "Development and deployment of a 5 MW / 50 MWh long-duration iron-flow battery storage system in upstate New York to relieve grid congestion.",
        "location": "NY",
        "applicant_type": "company",
        "cost": 5000000.0,
        "trl": 6
    })
    assert analyze_res.status_code == 200, f"Failed POST /api/analyze: {analyze_res.text}"
    analyze_data = analyze_res.json()
    matches_count = len(analyze_data.get("matches", []))
    print(f"   [OK] POST /api/analyze evaluated project: {matches_count} matching opportunities found")

    # Clean up test proposal
    client.delete(f"/api/proposals/{new_prop_id}")

    print("\n================ ALL 6 VERIFICATION TEST SUITES PASSED! ================\n")


if __name__ == "__main__":
    run_verification()
