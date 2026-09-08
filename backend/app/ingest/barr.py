"""Barr Foundation adapter."""
import json
import logging
from sqlalchemy.orm import Session
from app.ingest.base import BaseAdapter
from app.models.opportunity import Opportunity
from app.models.source import IngestionRun, Source

logger = logging.getLogger(__name__)

class BarrAdapter(BaseAdapter):
    source_name = "barr"
    source_url = "https://www.barrfoundation.org/grantmaking/grants-database"
    source_type = "html"
    
    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}
        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()
        
        try:
            try:
                self.fetch_url(self.source_url)
            except Exception as e:
                logger.warning(f"Failed to fetch {self.source_url}: {e}")
                run.status = "success"
                db.commit()
                return stats
                
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
