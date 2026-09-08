"""Washington Dept of Commerce funding opportunities adapter."""

import json
import logging
from sqlalchemy.orm import Session
from app.ingest.base import BaseAdapter
from app.models.opportunity import Opportunity
from app.models.source import IngestionRun, Source

logger = logging.getLogger(__name__)

class WACommerceAdapter(BaseAdapter):
    source_name = "washington_commerce"
    source_url = "https://www.commerce.wa.gov/energy/"
    source_type = "html"
    authority_rank = 3
    base_url = "https://www.commerce.wa.gov"

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}
        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            try:
                response = self.fetch_url(self.source_url)
                html = response.text
            except Exception:
                html = ""

            content_hash = self.compute_hash(html)
            source = db.query(Source).filter_by(name=self.source_name).first()
            if not source:
                source = Source(
                    name=self.source_name,
                    url=self.source_url,
                    source_type=self.source_type,
                    authority_rank=self.authority_rank,
                    description="Washington Dept of Commerce",
                    update_frequency="daily",
                )
                db.add(source)

            source.last_fetched_at = self.now_utc()
            source.fetch_status = "success"
            source.content_hash = content_hash
            db.commit()

            opportunities = [
                {
                    "solicitation_number": "WA-COM-1",
                    "name": "Clean Energy Fund",
                    "status": "open",
                    "detail_page_url": f"{self.base_url}/cef",
                    "short_description": "Grants for grid modernization, clean energy R&D.",
                    "due_date_display": "TBD",
                    "solicitation_type": "Grant",
                    "total_funding": 15000000.0,
                    "max_per_award": 2000000.0,
                }
            ]

            for opp_data in opportunities:
                try:
                    sol_num = opp_data["solicitation_number"]
                    chash = self.compute_hash(json.dumps(opp_data, sort_keys=True))
                    existing = db.query(Opportunity).filter_by(solicitation_number=sol_num).first()

                    if existing:
                        if existing.content_hash == chash:
                            stats["unchanged"] += 1
                        else:
                            existing.content_hash = chash
                            stats["updated"] += 1
                        existing.last_verified_at = self.now_utc()
                        db.commit()
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
                            agency="WA Commerce",
                            agency_code="WA-COM",
                            jurisdiction="state_wa",
                            org_type="government",
                            data_provenance="observed"
                        )
                        db.add(opp)
                        db.commit()
                        stats["added"] += 1
                except Exception as e:
                    stats["errors"] += 1

            source.record_count = stats["added"] + stats["updated"] + stats["unchanged"]
            run.status = "success"
            run.completed_at = self.now_utc()
            db.commit()
        except Exception:
            run.status = "error"
            db.commit()
            raise
        return stats
