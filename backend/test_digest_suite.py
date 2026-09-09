"""Comprehensive Verification Suite for Daily Clean Energy Intelligence Digest."""

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestDailyDigestSuite(unittest.TestCase):

    def test_01_get_latest_digest(self):
        resp = client.get("/api/v1/digest/latest")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("edition_date", data)
        self.assertIn("formatted_date", data)
        self.assertIn("macro_metrics", data)
        self.assertIn("new_solicitations", data)
        self.assertIn("urgent_deadlines", data)
        self.assertIn("award_wire", data)
        self.assertIn("editorial_narrative", data)
        print(f"[PASS] /api/v1/digest/latest returned valid briefing for {data.get('formatted_date')}")

    def test_02_get_digest_archive(self):
        resp = client.get("/api/v1/digest/archive")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertIn("date", data[0])
        self.assertIn("headline", data[0])
        print(f"[PASS] /api/v1/digest/archive returned {len(data)} editions.")

    def test_03_get_historical_digest(self):
        # Fetch today's date edition explicitly
        resp_archive = client.get("/api/v1/digest/archive")
        target_date = resp_archive.json()[0]["date"]

        resp = client.get(f"/api/v1/digest/{target_date}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["edition_date"], target_date)
        print(f"[PASS] /api/v1/digest/{target_date} successfully returned edition.")

    def test_04_force_regenerate_digest(self):
        resp = client.post("/api/v1/digest/generate")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("spotlight", data)
        print("[PASS] POST /api/v1/digest/generate successfully refreshed edition.")

if __name__ == "__main__":
    unittest.main()
