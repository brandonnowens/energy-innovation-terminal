"""Grants.gov Historical API adapter for archived/closed federal funding opportunities."""

import json
import logging
import re
from typing import Optional

from sqlalchemy.orm import Session

from app.ingest.base import BaseAdapter
from app.ingest.grants_gov import (
    AGENCY_MAP,
    GRANTS_GOV_AGENCIES,
    ENERGY_FOCUSED_AGENCIES,
    ENERGY_RELEVANCE_TERMS,
    _clean_html,
    _parse_date,
    _infer_categories
)
from app.models.opportunity import Opportunity
from app.models.source import IngestionRun, Source, ChangeEvent
from app.engine.energy_filter import is_energy_innovation_relevant

logger = logging.getLogger(__name__)

class GrantsGovHistoricalAdapter(BaseAdapter):
    """Ingests closed/archived federal funding opportunities from Grants.gov."""

    source_name = "grants_gov_historical"
    source_url = "https://api.grants.gov/v1/api"
    source_type = "api"
    authority_rank = 3

    def _post_json(self, url: str, payload: dict) -> dict:
        self._rate_limit()
        response = self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}

        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            source = db.query(Source).filter_by(name=self.source_name).first()
            if not source:
                source = Source(
                    name=self.source_name, url=self.source_url,
                    source_type=self.source_type, authority_rank=self.authority_rank,
                    description="Grants.gov Historical Funding Opportunities",
                    update_frequency="monthly",
                )
                db.add(source)
                db.commit()

            source.last_fetched_at = self.now_utc()

            search_url = f"{self.source_url}/search2"
            detail_url = f"{self.source_url}/fetchOpportunity"
            seen_ids = set()
            batch_count = 0

            # Search each agency
            for agency_code in GRANTS_GOV_AGENCIES:
                logger.info(f"[{self.source_name}] Searching agency: {agency_code}")
                start = 0

                while True:
                    payload = {
                        "agencies": agency_code,
                        "oppStatuses": "closed|archived",
                        "rows": 100,  # larger page sizes
                        "startRecordNum": start,
                        "sortBy": "openDate|desc",
                    }

                    resp = self._post_json(search_url, payload)
                    data = resp.get("data", resp)
                    total = data.get("hitCount", 0)
                    hits = data.get("oppHits", [])

                    if not hits:
                        break

                    for hit in hits:
                        try:
                            result = self._process_hit(db, hit, detail_url)
                            stats[result] += 1
                            seen_ids.add(hit.get("id"))
                            
                            batch_count += 1
                            if batch_count % 100 == 0:
                                db.commit()
                                
                        except Exception as e:
                            stats["errors"] += 1
                            logger.error(f"Error processing hit {hit.get('id')}: {e}")

                    start += len(hits)
                    if start >= total:
                        break

                logger.info(f"[{self.source_name}] {agency_code}: processed {start} of {total}")

            db.commit()
            
            source.record_count = len(seen_ids)
            source.fetch_status = "success"
            db.commit()

            run.status = "success"
            run.records_added = stats["added"]
            run.records_updated = stats["updated"]
            run.records_unchanged = stats["unchanged"]
            run.errors = stats["errors"]
            run.completed_at = self.now_utc()
            db.commit()

            logger.info(
                f"[{self.source_name}] Done: "
                f"{stats['added']} added, {stats['updated']} updated, "
                f"{stats['unchanged']} unchanged, {stats['errors']} errors"
            )

        except Exception as e:
            run.status = "error"
            run.error_details = str(e)
            run.completed_at = self.now_utc()
            db.commit()
            logger.error(f"[{self.source_name}] Ingestion failed: {e}", exc_info=True)
            raise

        return stats

    def _process_hit(self, db: Session, hit: dict, detail_url: str) -> str:
        grants_id = str(hit["id"])
        sol_num = hit.get("number", "") or ""
        hit_title = hit.get("title", "") or ""
        hit_agency_code = hit.get("agencyCode", "") or ""
        
        hit_hash = self.compute_hash(json.dumps(hit, sort_keys=True))

        existing = db.query(Opportunity).filter(
            (Opportunity.external_id == grants_id) |
            (Opportunity.solicitation_number == sol_num)
        ).first()

        if existing and existing.content_hash == hit_hash:
            existing.last_verified_at = self.now_utc()
            return "unchanged"

        # Fetch details
        try:
            resp = self._post_json(detail_url, {"opportunityId": int(hit["id"])})
            detail = resp.get("data", resp)
        except Exception as e:
            logger.warning(f"Failed to fetch detail for {grants_id}: {e}")
            detail = {}

        synopsis = detail.get("synopsis", {}) or {}
        
        status = "closed"
        agency = AGENCY_MAP.get(hit_agency_code, hit_agency_code.split("-")[0] if "-" in hit_agency_code else hit_agency_code)

        desc = _clean_html(synopsis.get("synopsisDesc", ""))

        # Energy-innovation relevance and negative exclusion filter
        is_valid, _ = is_energy_innovation_relevant(
            title=title if 'title' in locals() and title else hit_title,
            text_content=desc,
            agency=agency
        )
        if not is_valid:
            return "unchanged"  # Skip non-energy opportunities

        total_funding = synopsis.get("estimatedTotalProgramFunding")
        max_award = synopsis.get("awardCeiling")
        if isinstance(total_funding, str):
            try: total_funding = float(total_funding.replace(",", ""))
            except: total_funding = None
        if isinstance(max_award, str):
            try: max_award = float(max_award.replace(",", ""))
            except: max_award = None

        title = detail.get("opportunityTitle") or detail.get("title") or hit_title
        
        close_date_raw = hit.get("closeDate", "") or synopsis.get("responseDate", "")
        close_date = _parse_date(close_date_raw)
        
        year = None
        if close_date:
            year = close_date.year
            
        raw_data = json.dumps(detail)

        if existing:
            existing.name = title or existing.name
            existing.short_description = desc or existing.short_description
            existing.total_funding = total_funding or existing.total_funding
            existing.max_per_award = max_award or existing.max_per_award
            existing.content_hash = hit_hash
            existing.last_verified_at = self.now_utc()
            
            if hasattr(existing, "year") and year:
                existing.year = year
            if hasattr(existing, "raw_source_data"):
                existing.raw_source_data = raw_data
                
            return "updated"

        opp = Opportunity(
            solicitation_number=sol_num or f"GRANTS-{grants_id}",
            name=title,
            status=status,
            short_description=desc[:5000] if desc else "",
            total_funding=total_funding,
            max_per_award=max_award,
            agency=agency,
            agency_code=hit_agency_code,
            jurisdiction="federal",
            external_id=grants_id,
            source_url=self.source_url,
            source_name=self.source_name,
            content_hash=hit_hash,
            first_seen_at=self.now_utc(),
            last_verified_at=self.now_utc(),
        )
        
        if hasattr(opp, "is_historical"):
            opp.is_historical = True
        if hasattr(opp, "year") and year:
            opp.year = year
        if hasattr(opp, "raw_source_data"):
            opp.raw_source_data = raw_data
            
        db.add(opp)
        return "added"
