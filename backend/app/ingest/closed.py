"""Closed opportunities HTML scraper.

Scrapes the NYSERDA closed opportunities archive pages.
"""

import logging
import re
from typing import Optional

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.config import settings
from app.ingest.base import BaseAdapter
from app.models.project import HistoricalOpportunity
from app.models.source import IngestionRun, Source

logger = logging.getLogger(__name__)

# Years to scrape
ARCHIVE_YEARS = [2026, 2025, 2024, 2023, 2022, 2021]


class ClosedOpportunitiesAdapter(BaseAdapter):
    """Scrapes closed/past NYSERDA funding opportunities from archive pages."""

    source_name = "nyserda_closed_opportunities"
    source_type = "html"
    authority_rank = 4

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}

        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            for year in ARCHIVE_YEARS:
                url = (
                    f"{settings.nyserda_base_url}/All-Opportunities/"
                    f"Closed-Funding-Opportunities/{year}-Closed-Opportunities"
                )
                try:
                    year_stats = self._scrape_year(db, url, year)
                    for key in stats:
                        stats[key] += year_stats[key]
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error scraping year {year}: {e}")

            # Update source
            source = db.query(Source).filter_by(name=self.source_name).first()
            if not source:
                source = Source(
                    name=self.source_name,
                    url=f"{settings.nyserda_base_url}/All-Opportunities/Closed-Funding-Opportunities",
                    source_type=self.source_type,
                    authority_rank=self.authority_rank,
                    description="NYSERDA closed opportunities archive (HTML scrape)",
                    update_frequency="monthly",
                )
                db.add(source)

            source.last_fetched_at = self.now_utc()
            source.fetch_status = "success"

            run.status = "success"
            run.records_added = stats["added"]
            run.records_updated = stats["updated"]
            run.records_unchanged = stats["unchanged"]
            run.errors = stats["errors"]
            run.completed_at = self.now_utc()
            db.commit()

            logger.info(
                f"[{self.source_name}] Ingestion complete: "
                f"{stats['added']} added, {stats['errors']} errors"
            )

        except Exception as e:
            run.status = "error"
            run.error_details = str(e)
            run.completed_at = self.now_utc()
            db.commit()
            logger.error(f"[{self.source_name}] Ingestion failed: {e}", exc_info=True)
            raise

        return stats

    def _scrape_year(self, db: Session, url: str, year: int) -> dict:
        """Scrape a single year's closed opportunities page."""
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}

        try:
            response = self.fetch_url(url)
            soup = BeautifulSoup(response.text, "lxml")
        except Exception as e:
            logger.warning(f"Could not fetch {url}: {e}")
            stats["errors"] += 1
            return stats

        # Find opportunity listings - look for common patterns
        # NYSERDA pages typically list opportunities in various HTML structures
        content = soup.find("div", class_="field-content") or soup.find("main") or soup.find("article") or soup.body

        if not content:
            logger.warning(f"No content found on {url}")
            stats["errors"] += 1
            return stats

        # Try to find solicitation numbers and names from text content
        text = content.get_text(separator="\n")
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Pattern: PON/RFP/RFQ/RFI/RFQL followed by a number
        sol_pattern = re.compile(
            r'((?:PON|RFP|RFQ|RFI|RFQL)\s*\d{3,5})\s*[-–:]\s*(.+)',
            re.IGNORECASE
        )

        for line in lines:
            match = sol_pattern.search(line)
            if match:
                sol_num = match.group(1).strip().upper()
                # Normalize spacing
                sol_num = re.sub(r'\s+', ' ', sol_num)
                name = match.group(2).strip()
                # Clean up name - remove trailing dates/info
                name = re.split(r'\s*(?:Due|Closed|Posted)\s*:', name, flags=re.IGNORECASE)[0].strip()

                try:
                    existing = db.query(HistoricalOpportunity).filter_by(
                        solicitation_number=sol_num, year=year
                    ).first()

                    if existing:
                        stats["unchanged"] += 1
                        continue

                    sol_type = sol_num.split()[0] if " " in sol_num else None

                    opp = HistoricalOpportunity(
                        solicitation_number=sol_num,
                        name=name[:500],
                        solicitation_type=sol_type,
                        year=year,
                        source_url=url,
                    )
                    db.add(opp)
                    db.commit()
                    stats["added"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error adding closed opp {sol_num}: {e}")
                    db.rollback()

        # Also try to find links with solicitation info
        for link in content.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            match = sol_pattern.search(link_text)
            if match:
                sol_num = re.sub(r'\s+', ' ', match.group(1).strip().upper())
                name = match.group(2).strip()

                existing = db.query(HistoricalOpportunity).filter_by(
                    solicitation_number=sol_num, year=year
                ).first()

                if not existing:
                    href = link.get("href", "")
                    if href and not href.startswith("http"):
                        href = f"{settings.nyserda_base_url}{href}"

                    try:
                        opp = HistoricalOpportunity(
                            solicitation_number=sol_num,
                            name=name[:500],
                            solicitation_type=sol_num.split()[0] if " " in sol_num else None,
                            year=year,
                            source_url=url,
                            detail_url=href if href.startswith("http") else None,
                        )
                        db.add(opp)
                        db.commit()
                        stats["added"] += 1
                    except Exception as e:
                        stats["errors"] += 1
                        db.rollback()

        return stats
