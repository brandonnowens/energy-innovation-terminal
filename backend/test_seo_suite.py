"""Comprehensive Verification Suite for Viral SEO, Sitemaps, GEO, and RSS Engine."""

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestSeoEngine(unittest.TestCase):

    def test_01_robots_txt(self):
        resp = client.get("/robots.txt")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/plain", resp.headers["content-type"])
        self.assertIn("Sitemap: https://energyinnovation.terminal/sitemap.xml", resp.text)
        self.assertIn("User-agent: PerplexityBot", resp.text)
        self.assertIn("User-agent: ChatGPT-User", resp.text)
        print("[PASS] /robots.txt serves valid directives and sitemap links.")

    def test_02_llms_txt_and_ai_txt(self):
        resp_llms = client.get("/llms.txt")
        self.assertEqual(resp_llms.status_code, 200)
        self.assertIn("Energy Innovation Terminal", resp_llms.text)
        self.assertIn("54,313 competitive grant awards", resp_llms.text)
        self.assertIn("Source: Energy Innovation Terminal", resp_llms.text)

        resp_ai = client.get("/ai.txt")
        self.assertEqual(resp_ai.status_code, 200)
        self.assertIn("LLMs-File:", resp_ai.text)
        print("[PASS] /llms.txt and /ai.txt serve Generative Engine Optimization (GEO) context.")

    def test_03_master_sitemap_index(self):
        resp = client.get("/sitemap.xml")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("application/xml", resp.headers["content-type"])
        self.assertIn("<sitemapindex", resp.text)
        self.assertIn("sitemap-opportunities.xml", resp.text)
        self.assertIn("sitemap-recipients.xml", resp.text)
        self.assertIn("sitemap-technologies.xml", resp.text)
        print("[PASS] /sitemap.xml serves valid sitemap index.")

    def test_04_sub_sitemaps(self):
        # Opportunities sitemap
        resp_opps = client.get("/sitemap-opportunities.xml")
        self.assertEqual(resp_opps.status_code, 200)
        self.assertIn("<urlset", resp_opps.text)
        self.assertIn("/opportunities/", resp_opps.text)

        # Recipients sitemap
        resp_rec = client.get("/sitemap-recipients.xml")
        self.assertEqual(resp_rec.status_code, 200)
        self.assertIn("<urlset", resp_rec.text)
        self.assertIn("/recipients/", resp_rec.text)

        # Technologies sitemap
        resp_tech = client.get("/sitemap-technologies.xml")
        self.assertEqual(resp_tech.status_code, 200)
        self.assertIn("<urlset", resp_tech.text)
        self.assertIn("/technologies/", resp_tech.text)
        print("[PASS] All segmented XML sitemaps generate valid URL sets.")

    def test_05_rss_syndication_feed(self):
        resp = client.get("/feed/rss/opportunities.xml")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("application/rss+xml", resp.headers["content-type"])
        self.assertIn('<rss version="2.0"', resp.text)
        self.assertIn("<item>", resp.text)
        print("[PASS] /feed/rss/opportunities.xml serves active grants syndication.")

    def test_06_dynamic_social_cards_and_badges(self):
        # Test opportunity OG SVG image
        resp_og = client.get("/api/seo/og-image/opportunity/1.svg")
        self.assertEqual(resp_og.status_code, 200)
        self.assertIn("image/svg+xml", resp_og.headers["content-type"])
        self.assertIn("<svg", resp_og.text)
        self.assertIn("ENERGY INNOVATION TERMINAL", resp_og.text)

        # Test recipient badge
        resp_badge = client.get("/api/seo/badge/1.svg")
        self.assertEqual(resp_badge.status_code, 200)
        self.assertIn("image/svg+xml", resp_badge.headers["content-type"])
        self.assertIn("<svg", resp_badge.text)
        self.assertIn("TRACKED ON ENERGY INNOVATION TERMINAL", resp_badge.text)
        print("[PASS] Dynamic social card preview banners and embeddable badges render valid SVG.")

    def test_07_crawler_prerender_middleware(self):
        # Send request with Googlebot User-Agent
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        resp = client.get("/opportunities/1", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.headers["content-type"])
        self.assertIn('<script type="application/ld+json">', resp.text)
        self.assertIn("GovernmentService", resp.text)
        self.assertIn("MonetaryGrant", resp.text)
        self.assertIn("og:image", resp.text)
        self.assertIn("twitter:card", resp.text)
        print("[PASS] Googlebot crawler receives pre-rendered HTML with JSON-LD Schema & OG tags.")

if __name__ == "__main__":
    unittest.main()
