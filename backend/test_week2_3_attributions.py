"""Comprehensive verification suite for Week 2-3 Venture Capital & Patent Attributions Expansion."""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.main import app

client = TestClient(app)

def test_week2_3_attributions_expansion():
    print("=== 1. VERIFYING DATABASE ATTRIBUTIONS EXPANSION ===")
    with SessionLocal() as db:
        tot_vc_rounds = db.execute(text("SELECT COUNT(*) FROM recipient_investments")).scalar()
        tot_vc_dollars = db.execute(text("SELECT SUM(amount_usd) FROM recipient_investments")).scalar() or 0.0
        tot_vc_recips = db.execute(text("SELECT COUNT(DISTINCT recipient_id) FROM recipient_investments")).scalar()

        tot_patents = db.execute(text("SELECT COUNT(*) FROM recipient_patents")).scalar()
        tot_pat_recips = db.execute(text("SELECT COUNT(DISTINCT recipient_id) FROM recipient_patents")).scalar()
        tot_pat_awards_linked = db.execute(text("SELECT COUNT(DISTINCT award_id) FROM recipient_patents WHERE award_id IS NOT NULL")).scalar()

        print(f"Total VC & Private Equity Rounds: {tot_vc_rounds}")
        print(f"Total Private Capital Tracked: ${tot_vc_dollars:,.2f}")
        print(f"Recipients with Private Financing: {tot_vc_recips}")
        print(f"Total Clean Tech Patents: {tot_patents}")
        print(f"Recipients with Patents: {tot_pat_recips}")
        print(f"Patents Linked to Public Awards: {tot_pat_awards_linked}")

        assert tot_vc_rounds >= 500, f"Expected >= 500 VC rounds, got {tot_vc_rounds}"
        assert tot_vc_dollars >= 30000000000.0, f"Expected >= $30B VC capital, got ${tot_vc_dollars:,.2f}"
        assert tot_patents >= 1000, f"Expected >= 1000 patents, got {tot_patents}"
        assert tot_pat_awards_linked >= 500, f"Expected >= 500 award-linked patents, got {tot_pat_awards_linked}"

    print("\n=== 2. VERIFYING REST API ENDPOINTS ===")
    
    # 1. Overview KPI Endpoint
    ov_resp = client.get("/api/attributions/overview")
    assert ov_resp.status_code == 200
    ov_data = ov_resp.json()
    print(f"Overview API: {ov_data['total_patents']} patents, ${ov_data['total_vc_raised_usd']:,.0f} VC raised, {ov_data['leverage_multiplier']}x leverage.")
    assert ov_data["total_patents"] >= 1000
    assert ov_data["total_vc_raised_usd"] >= 30000000000.0
    assert len(ov_data["top_investors"]) >= 5
    assert len(ov_data["tech_distribution"]) >= 5

    # 2. Recipients Leaderboard Endpoint
    rec_resp = client.get("/api/attributions/recipients?page=1&page_size=25&sort_by=vc_raised")
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    print(f"Recipients API: {rec_data['total']} backed commercialization pioneers indexed across {rec_data['total_pages']} pages.")
    assert rec_data["total"] >= 1000
    top_company = rec_data["items"][0]
    print(f"Top 1 Company by VC: {top_company['name']} (${top_company['total_vc_raised_usd']:,.0f} VC, {top_company['patent_count']} patents)")

    # 3. Interactive Lineage Graph Endpoint
    graph_resp = client.get("/api/attributions/graph?limit=150")
    assert graph_resp.status_code == 200
    graph_data = graph_resp.json()
    print(f"Lineage Graph API: {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} capital/IP channels delivered.")
    assert len(graph_data["nodes"]) >= 50
    assert len(graph_data["edges"]) >= 50

    # 4. Investor Syndicates Endpoint
    syn_resp = client.get("/api/attributions/syndicates")
    assert syn_resp.status_code == 200
    syn_data = syn_resp.json()
    print(f"Investor Syndicates API: {len(syn_data['syndicates'])} institutional climate VC syndicates tracked.")
    assert len(syn_data["syndicates"]) >= 10
    top_syndicate = syn_data["syndicates"][0]
    print(f"Top Syndicate: {top_syndicate['name']} (${top_syndicate['total_capital_deployed_usd']:,.0f} capital, {top_syndicate['rounds_count']} rounds)")

    # 5. Organization Dossier & Ego Graph
    first_id = rec_data["items"][0]["id"]
    dossier_resp = client.get(f"/api/attributions/recipients/{first_id}")
    assert dossier_resp.status_code == 200
    dossier_data = dossier_resp.json()
    print(f"Dossier API for {dossier_data['recipient']['name']}: {len(dossier_data['patents'])} patents, {len(dossier_data['investments'])} VC rounds, {len(dossier_data['ego_graph']['nodes'])} ego-network nodes.")
    assert len(dossier_data["ego_graph"]["nodes"]) >= 2

    print("\n[ALL WEEK 2-3 ATTRIBUTIONS VERIFICATION TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    test_week2_3_attributions_expansion()
