import logging
import re
import uuid
from typing import Optional

from sqlalchemy.orm import Session
import httpx

from app.ingest.base import BaseAdapter
from app.models.opportunity import Opportunity, OpportunityCategory
from app.models.source import ChangeEvent, IngestionRun, Source

logger = logging.getLogger(__name__)

def _clean_html(html_str: str) -> str:
    if not html_str:
        return ""
    html_str = re.sub(r'<(br|p|div)[^>]*>', ' ', html_str, flags=re.IGNORECASE)
    html_str = re.sub(r'<[^>]+>', '', html_str)
    html_str = html_str.replace('&nbsp;', ' ').replace('&amp;', '&')
    return re.sub(r'\s+', ' ', html_str).strip()

class NMEMNRDAdapter(BaseAdapter):
    source_name = "newmexico_emnrd"
    source_url = "https://www.emnrd.nm.gov/ecmd/"
    source_type = "html"
    authority_rank = 3
    
    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}
        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            try:
                response = self.fetch_url(self.source_url)
                html = response.text
            except httpx.HTTPError as e:
                logger.error(f"[{self.source_name}] Failed to fetch: {e}")
                run.status = "error"
                run.error_details = str(e)
                run.completed_at = self.now_utc()
                db.commit()
                return stats

            content_hash = self.compute_hash(html)
            source = db.query(Source).filter_by(name=self.source_name).first()
            if not source:
                source = Source(
                    name=self.source_name,
                    url=self.source_url,
                    source_type=self.source_type,
                    authority_rank=self.authority_rank,
                    description="NM EMNRD Funding Opportunities",
                    update_frequency="weekly",
                )
                db.add(source)

            source.last_fetched_at = self.now_utc()
            source.fetch_status = "success"

            # Simple regex to find links that might be opportunities
            pattern = r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, flags=re.IGNORECASE)
            
            seen_ids = set()
            
            for link, title in matches:
                title = _clean_html(title)
                if not title or len(title) < 10:
                    continue
                    
                title_lower = title.lower()
                # Check topics
                topics = ['grant', 'modernization', 'innovation', 'renewables', 'storage', 'concept paper']
                if not any(t.lower() in title_lower for t in topics):
                    continue
                    
                # Generate a stable ID based on URL or title
                ext_id = self.compute_hash(link + title)[:20]
                
                if ext_id in seen_ids:
                    continue
                seen_ids.add(ext_id)
                
                try:
                    result = self._process_opportunity(db, link, ext_id, title)
                    stats[result] += 1
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"[{self.source_name}] Error processing {ext_id}: {e}", exc_info=True)

            source.record_count = len(seen_ids)
            source.content_hash = content_hash
            db.commit()

            run.status = "success"
            run.records_added = stats["added"]
            run.records_updated = stats["updated"]
            run.records_unchanged = stats["unchanged"]
            run.errors = stats["errors"]
            run.completed_at = self.now_utc()
            db.commit()
        except Exception as e:
            run.status = "error"
            run.error_details = str(e)
            run.completed_at = self.now_utc()
            db.commit()
            logger.error(f"[{self.source_name}] Ingestion failed: {e}", exc_info=True)
            raise

        return stats

    def _process_opportunity(self, db: Session, link: str, ext_id: str, title: str) -> str:
        if not link.startswith("http"):
            if link.startswith("/"):
                link = self.source_url.rstrip("/") + link
            else:
                link = self.source_url.rstrip("/") + "/" + link
                
        content_hash = self.compute_hash(title + link)
        existing = db.query(Opportunity).filter_by(external_id=ext_id, source_name=self.source_name).first()

        if existing:
            if existing.content_hash == content_hash:
                existing.last_verified_at = self.now_utc()
                db.commit()
                return "unchanged"

        opp_data = {
            "external_id": ext_id,
            "solicitation_number": ext_id, # Fallback
            "name": title,
            "status": "open",
            "detail_page_url": link,
            "agency": "NM EMNRD",
            "jurisdiction": "state_nm",
            "source_url": self.source_url,
            "source_name": self.source_name,
            "content_hash": content_hash,
            "org_type": "government",
            "data_provenance": "observed",
        }

        if existing:
            existing.name = title
            existing.detail_page_url = link
            existing.content_hash = content_hash
            existing.last_verified_at = self.now_utc()
            db.commit()
            return "updated"

        opp = Opportunity(
            **opp_data,
            first_seen_at=self.now_utc(),
            last_verified_at=self.now_utc(),
        )
        db.add(opp)
        db.flush()

        db.add(ChangeEvent(
            entity_type="opportunity",
            entity_id=ext_id,
            entity_name=title,
            change_type="new",
            source_name=self.source_name,
        ))
        db.commit()
        return "added"
