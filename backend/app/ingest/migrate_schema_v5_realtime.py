'''Migration Schema v5: Real-time ingestion tables (webhooks & RSS)'''

import logging
from sqlalchemy import text
from app.database import engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MigrateSchemaV5Realtime")


def migrate_schema_v5_realtime() -> None:
    """Create additive tables to support webhook endpoints and RSS feed sources.

    Tables:
        webhook_endpoints – stores configuration for incoming webhooks (shared secret, enabled flag, provenance).
        rss_feed_sources   – stores RSS/Atom feed URLs, fetch metadata, poll interval, and provenance.
    """
    logger.info("Executing Schema v5 additive migration for real-time ingestion (webhooks & RSS)...")

    with engine.begin() as conn:
        # 1. webhook_endpoints table
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS webhook_endpoints (
                    id SERIAL PRIMARY KEY,
                    source_code VARCHAR(100) NOT NULL UNIQUE,
                    endpoint_url VARCHAR(1000) NOT NULL,
                    secret_token VARCHAR(255) NOT NULL,
                    enabled BOOLEAN DEFAULT TRUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_webhook_source ON webhook_endpoints(source_code);
                CREATE INDEX IF NOT EXISTS idx_webhook_enabled ON webhook_endpoints(enabled);
                """
            )
        )

        # 2. rss_feed_sources table
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS rss_feed_sources (
                    id SERIAL PRIMARY KEY,
                    source_code VARCHAR(100) NOT NULL UNIQUE,
                    feed_url VARCHAR(1000) NOT NULL,
                    poll_interval_minutes INTEGER DEFAULT 15,
                    last_fetched TIMESTAMP,
                    enabled BOOLEAN DEFAULT TRUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_rss_source ON rss_feed_sources(source_code);
                CREATE INDEX IF NOT EXISTS idx_rss_enabled ON rss_feed_sources(enabled);
                """
            )
        )

    logger.info("Schema v5 realtime ingestion migration completed successfully!")


if __name__ == "__main__":
    migrate_schema_v5_realtime()
