"""Verification test suite for Venture & Patent Attributions and Multi-State Expansion."""

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAttributionsAndMultiState(unittest.TestCase):

    def test_attributions_overview(self):
        response = client.get("/api/attributions/overview")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_patents", data)
        self.assertIn("total_vc_raised_usd", data)
        self.assertIn("leverage_multiplier", data)
        self.assertIn("top_investors", data)
        print(f"\n[TEST PASS] Overview: {data['total_patents']} patents, ${data['total_vc_raised_usd']:,.0f} VC raised, {data['leverage_multiplier']}x leverage.")

    def test_attributions_recipients(self):
        response = client.get("/api/attributions/recipients?sort_by=leverage_ratio")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertGreater(len(data["items"]), 0)
        first = data["items"][0]
        print(f"[TEST PASS] Top recipient by leverage: {first['name']} ({first['leverage_ratio']}x, ${first['total_vc_raised_usd']:,.0f} VC, {first['patent_count']} patents)")

    def test_recipient_dossier_and_ego_graph(self):
        # Get first recipient ID
        list_resp = client.get("/api/attributions/recipients")
        rec_id = list_resp.json()["items"][0]["id"]
        
        response = client.get(f"/api/attributions/recipients/{rec_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("recipient", data)
        self.assertIn("patents", data)
        self.assertIn("investments", data)
        self.assertIn("ego_graph", data)
        print(f"[TEST PASS] Dossier for {data['recipient']['name']}: {len(data['patents'])} patents, {len(data['investments'])} VC rounds, {len(data['ego_graph']['nodes'])} ego nodes.")

    def test_attributions_graph(self):
        response = client.get("/api/attributions/graph")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        print(f"[TEST PASS] Lineage Graph: {len(data['nodes'])} nodes, {len(data['edges'])} edges.")

    def test_syndicates(self):
        response = client.get("/api/attributions/syndicates")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("syndicates", data)
        self.assertGreater(len(data["syndicates"]), 0)
        print(f"[TEST PASS] Investor Syndicates: {len(data['syndicates'])} VC funds tracked.")

    def test_multistate_opportunities_filtering(self):
        # Filter California CEC
        ca_resp = client.get("/api/opportunities?jurisdiction=CA")
        self.assertEqual(ca_resp.status_code, 200)
        ca_data = ca_resp.json()
        self.assertGreater(ca_data["total"], 0)
        print(f"[TEST PASS] Multi-State CA: {ca_data['total']} California opportunities.")

        # Filter Massachusetts MassCEC
        ma_resp = client.get("/api/opportunities?jurisdiction=MA")
        self.assertEqual(ma_resp.status_code, 200)
        ma_data = ma_resp.json()
        self.assertGreater(ma_data["total"], 0)
        print(f"[TEST PASS] Multi-State MA: {ma_data['total']} Massachusetts opportunities.")


if __name__ == "__main__":
    unittest.main()
