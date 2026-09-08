"""ProPublica 990-PF adapter."""
import json
import logging
from sqlalchemy.orm import Session
from app.ingest.base import BaseAdapter
from app.models.opportunity import Opportunity
from app.models.source import IngestionRun, Source

logger = logging.getLogger(__name__)

FOUNDATIONS = [
    {'ein': '94-3136956', 'name': 'Energy Foundation', 'agency': 'Energy Foundation'},
    {'ein': '95-4682601', 'name': 'ClimateWorks Foundation', 'agency': 'ClimateWorks'},
    {'ein': '20-4368045', 'name': 'Heising-Simons Foundation', 'agency': 'Heising-Simons'},
    {'ein': '20-5765826', 'name': 'Bloomberg Philanthropies', 'agency': 'Bloomberg Philanthropies'},
]

class ProPublica990Adapter(BaseAdapter):
    source_name = "propublica_990"
    source_url = "https://projects.propublica.org/nonprofits/api/v2/organizations/{EIN}.json"
    source_type = "api"
    
    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}
        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()
        
        try:
            for fd in FOUNDATIONS:
                url = self.source_url.replace("{EIN}", fd['ein'].replace("-", ""))
                try:
                    data = self.fetch_json(url)
                    # mock process
                except Exception as e:
                    logger.warning(f"Failed to fetch {url}: {e}")
                    continue
                
            db.commit()
            run.status = "success"
            run.completed_at = self.now_utc()
            db.commit()
        except Exception as e:
            run.status = "error"
            run.error_details = str(e)
            run.completed_at = self.now_utc()
            db.commit()
            logger.error(e)
        return stats
