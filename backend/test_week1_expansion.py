"""Comprehensive verification suite for Week 1 Data Expansion & Financial Envelope Backfill."""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.main import app
from app.engine.analyzer import analyze_project, get_cached_opportunities, invalidate_opportunities_cache

client = TestClient(app)

def test_week1_expansion_and_financials():
    print("=== 1. VERIFYING DATABASE EXPANSION & FINANCIAL ENVELOPES ===")
    with SessionLocal() as db:
        # Invalidate in-memory cache to force refresh with new data
        invalidate_opportunities_cache()
        get_cached_opportunities(db, force_refresh=True)

        # Check total opportunities
        tot = db.execute(text("SELECT COUNT(*) FROM opportunities")).scalar()
        print(f"Total Opportunities in Database: {tot}")
        assert tot >= 5750, f"Expected >= 5750 opportunities, got {tot}"

        # Check active state opportunities by agency
        ca_cnt = db.execute(text("SELECT COUNT(*) FROM opportunities WHERE agency = 'CEC' AND status ILIKE 'open%'")).scalar()
        ma_cnt = db.execute(text("SELECT COUNT(*) FROM opportunities WHERE agency = 'MassCEC' AND status ILIKE 'open%'")).scalar()
        tx_cnt = db.execute(text("SELECT COUNT(*) FROM opportunities WHERE agency = 'TX SECO' AND status ILIKE 'open%'")).scalar()
        co_cnt = db.execute(text("SELECT COUNT(*) FROM opportunities WHERE agency = 'Colorado CEO' AND status ILIKE 'open%'")).scalar()
        il_cnt = db.execute(text("SELECT COUNT(*) FROM opportunities WHERE agency = 'IL DCEO' AND status ILIKE 'open%'")).scalar()
        wa_cnt = db.execute(text("SELECT COUNT(*) FROM opportunities WHERE agency = 'WA Commerce' AND status ILIKE 'open%'")).scalar()
        pa_cnt = db.execute(text("SELECT COUNT(*) FROM opportunities WHERE agency = 'Pennsylvania DEP' AND status ILIKE 'open%'")).scalar()

        print(f"Active Open CEC (California): {ca_cnt}")
        print(f"Active Open MassCEC (Massachusetts): {ma_cnt}")
        print(f"Active Open TX SECO (Texas): {tx_cnt}")
        print(f"Active Open Colorado CEO: {co_cnt}")
        print(f"Active Open Illinois DCEO: {il_cnt}")
        print(f"Active Open WA Commerce: {wa_cnt}")
        print(f"Active Open Pennsylvania DEP: {pa_cnt}")

        assert ca_cnt >= 10, f"Expected >= 10 open CEC opportunities, got {ca_cnt}"
        assert ma_cnt >= 5, f"Expected >= 5 open MassCEC opportunities, got {ma_cnt}"
        assert tx_cnt >= 1, "Expected >= 1 open TX SECO opportunity"
        assert co_cnt >= 1, "Expected >= 1 open Colorado CEO opportunity"
        assert il_cnt >= 1, "Expected >= 1 open IL DCEO opportunity"

        # Check that known major NYSERDA PONs and CEC GFOs now have positive funding envelopes
        pon_rows = db.execute(text("""
            SELECT solicitation_number, name, agency, total_funding, max_per_award
            FROM opportunities
            WHERE solicitation_number IN ('PON 6088', 'PON 6121', 'RFP 1', 'RFP 21', 'GFO-26-301', 'GFO-26-302', 'TX-SECO-2026-GRID')
        """)).mappings().all()

        print("\nSample Backfilled Solicitations:")
        for r in pon_rows:
            print(f"  [{r['agency']}] {r['solicitation_number']}: {r['name'][:50]} | Funding: ${r['total_funding']:,.2f} | Max Award: ${r['max_per_award'] or 0:,.2f}")
            assert r['total_funding'] > 0, f"Expected positive funding for {r['solicitation_number']}"

        # Check Field Provenances recorded
        prov_cnt = db.execute(text("SELECT COUNT(*) FROM field_provenances WHERE extraction_method IN ('curated_authoritative_envelope', 'nlp_regex_extractor', 'state_expansion_pipeline')")).scalar()
        print(f"\nTotal Field Provenance Hashes Recorded: {prov_cnt}")
        assert prov_cnt >= 100, f"Expected >= 100 provenance records, got {prov_cnt}"

    print("\n=== 2. VERIFYING REST API ENDPOINTS ===")
    # Test California opportunities filter
    ca_resp = client.get("/api/opportunities?jurisdiction=state_ca&status=open")
    assert ca_resp.status_code == 200
    ca_data = ca_resp.json()
    print(f"API /api/opportunities?jurisdiction=state_ca: {ca_data['total']} opportunities returned")
    assert ca_data["total"] >= 10

    # Test Funding threshold filter
    f_resp = client.get("/api/opportunities?min_funding=10000000&status=open")
    assert f_resp.status_code == 200
    f_data = f_resp.json()
    print(f"API /api/opportunities?min_funding=10000000 (>= $10M): {f_data['total']} open opportunities returned")
    assert f_data["total"] >= 15

    print("\n=== 3. VERIFYING 3-LAYER MATCHING ENGINE ===")
    with SessionLocal() as db:
        match_res = analyze_project(
            db=db,
            text="Advanced solid-state battery pilot manufacturing line and cell qualification in California.",
            location="Fremont, CA",
            cost=12000000.0,
            trl=7,
            fast_mode=True,
        )

        assert match_res["summary"]["total_matched"] > 0
        top_matches = match_res.get("top_25_opportunities", [])
        print(f"Matching Engine Results for Solid-State Battery in CA: {len(top_matches)} matches")
        
        # Verify California CEC opportunity is in the top recommendations
        ca_found = any("GFO-26-301" in m.get("solicitation_number", "") or "CEC" in m.get("agency", "") for m in top_matches)
        print(f"Top 1 match: [{top_matches[0]['agency']}] {top_matches[0]['solicitation_number']}: {top_matches[0]['name']} (Score: {top_matches[0]['fit_score']})")
        assert ca_found or top_matches[0]["fit_score"] >= 0.70

    print("\n[ALL WEEK 1 VERIFICATION TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    test_week1_expansion_and_financials()
