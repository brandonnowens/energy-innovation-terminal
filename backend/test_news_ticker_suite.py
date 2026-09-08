"""
Test Suite for Bloomberg Energy Innovation News Ticker & Entity Linkage Engine.
Verifies:
1. Database tables (news_items and news_item_links).
2. Deduplication using canonical URL & content fingerprinting.
3. Multi-source ingestion & strict energy innovation relevance filtering.
4. Polymorphic explicit database entity resolution (opportunities, orgs, techs, policies).
5. API endpoints (/api/news/ticker, /api/news/{id}, /api/news/element/..., /api/news/stats).
"""

import os
import unittest
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db, engine
from app.models.news import NewsItem, NewsItemLink
from app.engine.news_linker import (
    normalize_canonical_url,
    compute_content_fingerprint,
    check_energy_innovation_relevance,
    classify_news_sentiment,
    resolve_database_linkages
)
from app.ingest.news_adapter import ingest_daily_energy_news
from app.services.news_service import (
    get_news_ticker_items,
    get_news_item_detail,
    get_news_for_element,
    get_news_telemetry,
    run_news_ingestion_sync
)


class TestNewsTickerSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_url_normalization_and_fingerprinting(self):
        """Test canonical URL cleaning, UTM removal, and SHA-256 fingerprinting."""
        url1 = "https://www.CanaryMedia.com/articles/long-duration-storage/form-energy-iron-air/?utm_source=twitter&utm_medium=social#section1"
        url2 = "https://canarymedia.com/articles/long-duration-storage/form-energy-iron-air"
        
        canon1 = normalize_canonical_url(url1)
        canon2 = normalize_canonical_url(url2)
        self.assertEqual(canon1, canon2)
        
        title = "Form Energy Commissioning 100-Hour Multi-Day Storage Facility"
        fp1 = compute_content_fingerprint(title, url1)
        fp2 = compute_content_fingerprint(title, url2)
        self.assertEqual(fp1, fp2)
        self.assertTrue(len(fp1) >= 16)

    def test_02_relevance_filter(self):
        """Test strict clean energy innovation relevance filtering."""
        # Relevant news items
        rel1, score1, cat1 = check_energy_innovation_relevance("ARPA-E awards $100M for Grid-Forming Inverters", "FOA for superconducting transmission")
        self.assertTrue(rel1)
        self.assertGreater(score1, 0.7)
        self.assertEqual(cat1, "Grid Modernization & Transmission")

        rel2, score2, cat2 = check_energy_innovation_relevance("Form Energy iron-air battery commissioning for multi-day storage", "100-hour LDES installation")
        self.assertTrue(rel2)
        self.assertEqual(cat2, "Long-Duration Energy Storage")

        # Irrelevant non-energy / celebrity news items
        rel3, score3, cat3 = check_energy_innovation_relevance("Hollywood celebrity wins award at film festival", "Movie premier in Los Angeles")
        self.assertFalse(rel3)

    def test_03_sentiment_classification(self):
        """Test sentiment and commercial maturity classification."""
        self.assertEqual(classify_news_sentiment("DOE Announces $50M Grant Awarded to Storage Consortium"), "grant_awarded")
        self.assertEqual(classify_news_sentiment("Eos Energy Closes $65M Series C Funding Round"), "funding_round")
        self.assertEqual(classify_news_sentiment("FERC Finalizes Order 1920 Rule for Regional Transmission"), "regulatory")
        self.assertEqual(classify_news_sentiment("World Record 34% Perovskite Solar Efficiency Breakthrough"), "breakthrough")

    def test_04_entity_resolution_and_explicit_linkages(self):
        """Test explicit linking to opportunities, organizations, policies, technologies."""
        title = "Form Energy Deploys 100-Hour Iron-Air Storage under NYSERDA PON 6141 and NFPA 855 Standard"
        content = "Form Energy in collaboration with Consolidated Edison is deploying a long-duration storage battery meeting NFPA 855."
        
        links = resolve_database_linkages(title, content, self.db)
        self.assertGreaterEqual(len(links), 3)

        elem_types = [l["element_type"] for l in links]
        self.assertIn("technology", elem_types)
        self.assertIn("organization", elem_types)
        self.assertIn("policy", elem_types)

        # Verify all links have required fields
        for l in links:
            self.assertTrue(l["element_title"])
            self.assertTrue(l["element_url_path"])
            self.assertTrue(l["link_rationale"])
            self.assertGreater(l["confidence_score"], 0.5)

    def test_05_ingestion_and_deduplication(self):
        """Test end-to-end ingestion and verify second run deduplicates items."""
        # 1st run: ingest baseline and live feeds
        stats1 = run_news_ingestion_sync(self.db, force_seed=True)
        self.assertIn("new_items_persisted", stats1)
        initial_count = self.db.query(NewsItem).count()
        self.assertGreater(initial_count, 0)

        # 2nd run: should recognize identical fingerprints and skip duplicates
        stats2 = run_news_ingestion_sync(self.db, force_seed=True)
        self.assertGreater(stats2.get("duplicates_skipped", 0), 0)
        self.assertEqual(stats2.get("new_items_persisted", 0), 0)

    def test_06_ticker_and_detail_queries(self):
        """Test ticker retrieval and detail view with linkages."""
        ticker_items = get_news_ticker_items(self.db, limit=10)
        self.assertGreater(len(ticker_items), 0)
        
        first_item = ticker_items[0]
        self.assertIn("id", first_item)
        self.assertIn("title", first_item)
        self.assertIn("summary", first_item)
        self.assertIn("sentiment", first_item)
        self.assertIn("category_tag", first_item)
        self.assertIn("primary_link", first_item)

        # Query detail
        detail = get_news_item_detail(self.db, first_item["id"])
        self.assertIsNotNone(detail)
        self.assertEqual(detail["id"], first_item["id"])
        self.assertIsInstance(detail["links"], list)
        self.assertGreater(len(detail["links"]), 0)

    def test_07_element_specific_news(self):
        """Test querying news explicitly linked to an entity."""
        tech_news = get_news_for_element(self.db, "technology", "iron_air_battery")
        self.assertIsInstance(tech_news, list)

        telemetry = get_news_telemetry(self.db)
        self.assertGreater(telemetry["total_news_items"], 0)
        self.assertGreater(telemetry["total_explicit_links"], 0)


if __name__ == "__main__":
    unittest.main()
