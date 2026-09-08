"""Pennsylvania DEP Energy API adapter."""

import logging
import re
import time
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.ingest.base import BaseAdapter
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)

class PADEPAdapter(BaseAdapter):
    """Adapter for PA DEP opportunities."""

    source_name = "pennsylvania_dep"
    source_url = "https://www.dep.pa.gov/"
    source_type = "html"
    authority_rank = 2
    agency = "PA DEP"

    def _rate_limit(self):
        super()._rate_limit()
        time.sleep(1)

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}
        
        try:
            response = self.fetch_url(self.source_url)
            html = response.text
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (403, 404):
                logger.warning(f"[{self.source_name}] Gracefully handling {e.response.status_code}: {e}")
                return stats
            stats["errors"] += 1
            logger.error(f"[{self.source_name}] HTTP Error: {e}")
            return stats
        except Exception as e:
            stats["errors"] += 1
            logger.error(f"[{self.source_name}] Request Error: {e}")
            return stats

        matches = re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', html, re.IGNORECASE)
        seen = set()
        topics = ["rise", "industrial decarb", "small business advantage", "energy", "agricultural"]

        for href, link_text in matches:
            if href.startswith('#') or href.startswith('javascript:'):
                continue
            
            link_text = re.sub(r'<[^>]+>', '', link_text).strip()
            if not link_text:
                continue

            is_relevant = any(topic in link_text.lower() for topic in topics)
            if not is_relevant:
                continue
                
            solicitation_number = self.compute_hash(href)[:15]
            if solicitation_number in seen:
                continue
            seen.add(solicitation_number)
            
            detail_url = href if href.startswith('http') else f"https://www.dep.pa.gov{href if href.startswith('/') else '/' + href}"
            
            try:
                result = self._process_opportunity(db, detail_url, solicitation_number, link_text)
                stats[result] += 1
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (403, 404):
                    logger.warning(f"[{self.source_name}] Gracefully handling {e.response.status_code} for {detail_url}: {e}")
                    continue
                stats["errors"] += 1
            except Exception as e:
                stats["errors"] += 1
                logger.error(f"Error processing {solicitation_number}: {e}")
                
        return stats

    def _process_opportunity(self, db: Session, detail_url: str, sol_num: str, title: str) -> str:
        existing = db.query(Opportunity).filter(
            (Opportunity.solicitation_number == sol_num) | 
            (Opportunity.external_id == sol_num)
        ).first()
        
        if existing:
            return "unchanged"
            
        try:
            resp = self.fetch_url(detail_url)
            html = resp.text
        except httpx.HTTPStatusError as e:
            raise e
            
        opp_data = {
            "solicitation_number": sol_num,
            "external_id": sol_num,
            "name": title,
            "status": "open",
            "short_description": title,
            "detail_page_url": detail_url,
            "agency": self.agency,
            "jurisdiction": "state",
            "source_url": self.source_url,
            "source_name": self.source_name,
            "content_hash": self.compute_hash(html),
        }
        
        opp = Opportunity(**opp_data)
        if hasattr(opp, "org_type"):
            opp.org_type = "government"
        if hasattr(opp, "data_provenance"):
            opp.data_provenance = "observed"
            
        db.add(opp)
        db.commit()
        return "added"
