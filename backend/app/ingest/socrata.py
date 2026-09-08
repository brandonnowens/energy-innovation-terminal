"""Socrata SODA API adapter for Open NY NYSERDA datasets.

Primary dataset: NYSERDA Supported Clean Energy R&D Projects (7xzk-zyk5)
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.ingest.base import BaseAdapter
from app.models.project import HistoricalProject
from app.models.source import IngestionRun, Source

logger = logging.getLogger(__name__)


class SocrataAdapter(BaseAdapter):
    """Ingests historical project data from Open NY Socrata datasets."""

    source_name = "open_ny_rd_projects"
    source_type = "api"
    authority_rank = 3

    def __init__(self, dataset_id: str = None):
        super().__init__()
        self.dataset_id = dataset_id or settings.socrata_rd_dataset
        self.source_url = f"{settings.socrata_base_url}/resource/{self.dataset_id}.json"
        self.source_name = f"open_ny_{self.dataset_id}"

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}

        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            # Paginate through all records
            offset = 0
            total_fetched = 0

            while True:
                params = {
                    "$limit": settings.socrata_page_size,
                    "$offset": offset,
                    "$order": "application_id",
                }
                if settings.socrata_app_token:
                    params["$$app_token"] = settings.socrata_app_token

                records = self.fetch_json(self.source_url, params=params)

                if not records:
                    break

                for record in records:
                    try:
                        result = self._process_record(db, record)
                        stats[result] += 1
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"Error processing record: {e}")

                total_fetched += len(records)
                offset += settings.socrata_page_size

                if len(records) < settings.socrata_page_size:
                    break

            # Update source
            source = db.query(Source).filter_by(name=self.source_name).first()
            if not source:
                source = Source(
                    name=self.source_name,
                    url=self.source_url,
                    source_type=self.source_type,
                    authority_rank=self.authority_rank,
                    description=f"Open NY Socrata dataset {self.dataset_id}",
                    update_frequency="quarterly",
                )
                db.add(source)

            source.last_fetched_at = self.now_utc()
            source.fetch_status = "success"
            source.record_count = total_fetched

            run.status = "success"
            run.records_added = stats["added"]
            run.records_updated = stats["updated"]
            run.records_unchanged = stats["unchanged"]
            run.errors = stats["errors"]
            run.completed_at = self.now_utc()
            db.commit()

            logger.info(
                f"[{self.source_name}] Ingestion complete: {total_fetched} fetched, "
                f"{stats['added']} added, {stats['updated']} updated"
            )

        except Exception as e:
            run.status = "error"
            run.error_details = str(e)
            run.completed_at = self.now_utc()
            db.commit()
            logger.error(f"[{self.source_name}] Ingestion failed: {e}", exc_info=True)
            raise

        return stats

    def _process_record(self, db: Session, record: dict) -> str:
        app_id = record.get("application_id", "").strip()
        if not app_id:
            return "errors"

        existing = db.query(HistoricalProject).filter_by(application_id=app_id).first()

        award_amount = None
        raw_amount = record.get("award_amount_us_dollars")
        if raw_amount:
            try:
                award_amount = float(raw_amount)
            except (ValueError, TypeError):
                pass

        website = record.get("contractor_website")
        if isinstance(website, dict):
            website = website.get("url", "")

        if existing:
            # Update if data_as_of changed
            new_as_of = record.get("data_current_as_of_date", "")
            if existing.data_as_of == new_as_of:
                return "unchanged"
            existing.project_title = record.get("project_title", existing.project_title)
            existing.contractor_name = record.get("primary_contractor_name")
            existing.contractor_type = record.get("contractor_type")
            existing.project_type = record.get("project_type")
            existing.technology_1 = record.get("technology_1")
            existing.technology_2 = record.get("technology_2")
            existing.technology_3 = record.get("technology_3")
            existing.award_date = record.get("award_date")
            existing.award_amount = award_amount
            existing.contractor_city = record.get("contractor_city")
            existing.contractor_state = record.get("contractor_state_province")
            existing.contractor_zip = record.get("contractor_zip_postal_code")
            existing.contractor_website = website
            existing.data_as_of = new_as_of
            db.commit()
            return "updated"

        project = HistoricalProject(
            application_id=app_id,
            project_title=record.get("project_title", "Unknown"),
            contractor_name=record.get("primary_contractor_name"),
            contractor_type=record.get("contractor_type"),
            project_type=record.get("project_type"),
            technology_1=record.get("technology_1"),
            technology_2=record.get("technology_2"),
            technology_3=record.get("technology_3"),
            project_description=record.get("project_description"),
            award_date=record.get("award_date"),
            award_amount=award_amount,
            contractor_city=record.get("contractor_city"),
            contractor_state=record.get("contractor_state_province"),
            contractor_zip=record.get("contractor_zip_postal_code"),
            contractor_website=website,
            data_as_of=record.get("data_current_as_of_date"),
            source_dataset=self.dataset_id,
        )
        db.add(project)
        db.commit()
        return "added"
