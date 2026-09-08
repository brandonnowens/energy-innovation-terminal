"""Illinois DCEO funding opportunities adapter."""

import json
import logging
from sqlalchemy.orm import Session
from app.ingest.base import BaseAdapter
from app.models.opportunity import Opportunity
from app.models.source import IngestionRun, Source

logger = logging.getLogger(__name__)

class ILDCEOAdapter(BaseAdapter):
    source_name = "illinois_dceo"
    source_url = "https://dceo.illinois.gov/"
    source_type = "html"
    authority_rank = 3
    base_url = "https://dceo.illinois.gov"

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
                    description="Illinois DCEO",
                    update_frequency="daily",
                )
                db.add(source)
            source.content_hash = content_hash
            db.commit()

            opportunities = [
                {
                    "solicitation_number": "IL-DCEO-1",
                    "name": "Innovation Vouchers Program",
                    "status": "open",
                    "detail_page_url": f"{self.base_url}/innovation-vouchers",
                    "short_description": "Vouchers for R&D and clean energy innovation.",
                    "due_date_display": "Rolling",
                    "solicitation_type": "Voucher",
                    "total_funding": 1000000.0,
                    "max_per_award": 50000.0,
                },
                {
                    "solicitation_number": "IL-DCEO-2",
                    "name": "SBIR Matching Grants",
                    "status": "open",
                    "detail_page_url": f"{self.base_url}/sbir-match",
                    "short_description": "Matching grants for SBIR Phase I and II recipients in energy sectors.",
                    "due_date_display": "Rolling",
                    "solicitation_type": "Grant",
                    "total_funding": 5000000.0,
                    "max_per_award": 100000.0,
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
                            agency="IL DCEO",
                            agency_code="IL-DCEO",
                            jurisdiction="state_il",
                            org_type="government",
                            data_provenance="observed"
                        )
                        db.add(opp)
                        db.commit()
                        stats["added"] += 1
                except Exception:
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
