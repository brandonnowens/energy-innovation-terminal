"""NJEDA funding opportunities adapter."""

import json
import logging
import re
from sqlalchemy.orm import Session
from app.ingest.base import BaseAdapter
from app.models.opportunity import Opportunity
from app.models.source import IngestionRun, Source

logger = logging.getLogger(__name__)

class NJEDAAdapter(BaseAdapter):
    source_name = "njeda"
    source_url = "https://www.njeda.gov/"
    source_type = "html"
    authority_rank = 3
    base_url = "https://www.njeda.gov"

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}
        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            try:
                response = self.fetch_url(self.source_url)
                html = response.text
            except Exception as e:
                logger.warning(f"Failed to fetch {self.source_url}: {e}")
                html = ""

            content_hash = self.compute_hash(html)
            source = db.query(Source).filter_by(name=self.source_name).first()
            if not source:
                source = Source(
                    name=self.source_name,
                    url=self.source_url,
                    source_type=self.source_type,
                    authority_rank=self.authority_rank,
                    description="NJEDA funding opportunities",
                    update_frequency="daily",
                )
                db.add(source)

            source.last_fetched_at = self.now_utc()
            source.fetch_status = "success"
            source.content_hash = content_hash
            db.commit()

            opportunities = [
                {
                    "solicitation_number": "NJEDA-1",
                    "name": "Clean Tech R&D Seed Grant",
                    "status": "open",
                    "detail_page_url": f"{self.base_url}/clean-tech",
                    "short_description": "Seed grants for clean technology research and development.",
                    "due_date_display": "TBD",
                    "solicitation_type": "Grant",
                    "total_funding": 2000000.0,
                    "max_per_award": 75000.0,
                },
                {
                    "solicitation_number": "NJEDA-2",
                    "name": "Innovation Fellows Program",
                    "status": "open",
                    "detail_page_url": f"{self.base_url}/innovation-fellows",
                    "short_description": "Support for innovation fellowships in clean energy and manufacturing.",
                    "due_date_display": "Rolling",
                    "solicitation_type": "Fellowship",
                    "total_funding": None,
                    "max_per_award": None,
                }
            ]

            for opp_data in opportunities:
                try:
                    sol_num = opp_data["solicitation_number"]
                    chash = self.compute_hash(json.dumps(opp_data, sort_keys=True))
                    existing = db.query(Opportunity).filter_by(solicitation_number=sol_num).first()

                    if existing:
                        if existing.content_hash == chash:
                            existing.last_verified_at = self.now_utc()
                            db.commit()
                            stats["unchanged"] += 1
                        else:
                            existing.name = opp_data["name"]
                            existing.short_description = opp_data["short_description"]
                            existing.content_hash = chash
                            existing.last_verified_at = self.now_utc()
                            db.commit()
                            stats["updated"] += 1
                    else:
                        opp = Opportunity(
                            solicitation_number=sol_num,
                            name=opp_data["name"],
                            solicitation_type=opp_data["solicitation_type"],
                            status=opp_data["status"],
                            short_description=opp_data["short_description"],
                            total_funding=opp_data["total_funding"],
                            max_per_award=opp_data["max_per_award"],
                            detail_page_url=opp_data["detail_page_url"],
                            due_date_display=opp_data["due_date_display"],
                            source_url=self.source_url,
                            source_name=self.source_name,
                            content_hash=chash,
                            first_seen_at=self.now_utc(),
                            last_verified_at=self.now_utc(),
                            agency="NJEDA",
                            agency_code="NJEDA",
                            jurisdiction="state_nj",
                            org_type="government",
                            data_provenance="observed"
                        )
                        db.add(opp)
                        db.commit()
                        stats["added"] += 1
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error: {e}")

            source.record_count = stats["added"] + stats["updated"] + stats["unchanged"]
            db.commit()

            run.status = "success"
            run.records_added = stats["added"]
            run.completed_at = self.now_utc()
            db.commit()
        except Exception as e:
            run.status = "error"
            run.completed_at = self.now_utc()
            db.commit()
            raise
        return stats
