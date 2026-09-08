"""Base Ingestion Worker Interface and Database Sink."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.opportunity import Opportunity, OpportunityCategory, EligibilityRule
from app.models.source import Source, IngestionRun
from app.models.alert import AlertSubscription, AlertTriggerLog

logger = logging.getLogger("IngestionPipeline")


class BaseIngestionWorker(ABC):
    """Abstract base worker for external grant & docket scrapers."""

    source_code: str = "generic"
    source_name: str = "Generic Ingestion Worker"
    agency_name: str = "Federal/State Agency"
    jurisdiction: str = "US_FED"

    @abstractmethod
    def fetch_records(self) -> List[Dict[str, Any]]:
        """Fetch raw records from API, RSS feed, or docket portal."""
        pass

    def run_sync(self, db: Session, user_initiated: bool = False) -> Dict[str, Any]:
        """Executes the ingestion run, inserts/updates PostgreSQL, and triggers alert checks."""
        start_time = datetime.utcnow()
        run_record = IngestionRun(
            source_name=self.source_name,
            started_at=start_time,
            status="running",
            records_added=0,
            records_updated=0,
            records_unchanged=0,
            errors=0
        )
        db.add(run_record)
        db.commit()
        db.refresh(run_record)

        try:
            raw_records = self.fetch_records()
            inserted = 0
            updated = 0
            unchanged = 0
            new_opportunities = []

            for item in raw_records:
                sol_num = item.get("solicitation_number")
                if not sol_num:
                    continue

                existing = db.query(Opportunity).filter(
                    Opportunity.solicitation_number == sol_num
                ).first()

                if existing:
                    # Update status, funding, or close date if changed
                    existing.status = item.get("status", existing.status)
                    if item.get("total_funding"):
                        existing.total_funding = item.get("total_funding")
                    if item.get("due_date_display"):
                        existing.due_date_display = item.get("due_date_display")
                    existing.last_verified_at = datetime.utcnow()
                    updated += 1
                else:
                    new_opp = Opportunity(
                        solicitation_number=sol_num,
                        agency=item.get("agency", self.agency_name),
                        agency_code=item.get("agency_code", self.source_code.upper()),
                        jurisdiction=item.get("jurisdiction", self.jurisdiction),
                        name=item.get("name", "Clean Energy Solicitation"),
                        solicitation_type=item.get("solicitation_type", "RFP / Grant"),
                        solicitation_category=item.get("solicitation_category", "Clean Energy & Grid"),
                        status=item.get("status", "open"),
                        short_description=item.get("short_description", ""),
                        total_funding=item.get("total_funding"),
                        max_per_award=item.get("max_per_award"),
                        cost_share_pct=item.get("cost_share_pct", 20.0),
                        due_date_display=item.get("due_date_display", "Open Enrollment"),
                        detail_page_url=item.get("detail_page_url"),
                        portal_url=item.get("portal_url"),
                        source_name=self.source_name,
                        first_seen_at=datetime.utcnow(),
                        last_verified_at=datetime.utcnow(),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(new_opp)
                    db.flush()
                    new_opportunities.append(new_opp)
                    inserted += 1

            run_record.records_added = inserted
            run_record.records_updated = updated
            run_record.records_unchanged = unchanged
            run_record.status = "success"
            run_record.completed_at = datetime.utcnow()

            # Update Source heartbeat
            src = db.query(Source).filter(Source.name == self.source_name).first()
            if not src:
                src = Source(
                    name=self.source_name,
                    url=self.source_code,
                    source_type="automated_worker",
                    authority_rank=1,
                    update_frequency="hourly"
                )
                db.add(src)
            src.last_fetched_at = datetime.utcnow()
            src.fetch_status = "success"
            src.record_count = (src.record_count or 0) + inserted

            db.commit()

            # Dispatch Alerts for newly discovered opportunities
            alerts_dispatched = self._check_and_dispatch_alerts(db, new_opportunities)

            return {
                "source": self.source_name,
                "status": "success",
                "records_fetched": len(raw_records),
                "inserted": inserted,
                "updated": updated,
                "alerts_dispatched": alerts_dispatched,
                "duration_seconds": round((datetime.utcnow() - start_time).total_seconds(), 2)
            }

        except Exception as e:
            logger.error(f"Error in {self.source_name}: {e}", exc_info=True)
            run_record.status = "error"
            run_record.errors = 1
            run_record.error_details = str(e)
            run_record.completed_at = datetime.utcnow()
            db.commit()
            return {
                "source": self.source_name,
                "status": "error",
                "error": str(e)
            }

    def _check_and_dispatch_alerts(self, db: Session, new_opps: List[Opportunity]) -> int:
        """Evaluates newly ingested opportunities against active in-terminal radar watchlist rules."""
        if not new_opps:
            return 0

        dispatched = 0
        active_subs = db.query(AlertSubscription).filter(AlertSubscription.is_active == True).all()

        for opp in new_opps:
            for sub in active_subs:
                match = True
                if sub.keywords:
                    kw = sub.keywords.lower()
                    if kw not in (opp.name or "").lower() and kw not in (opp.short_description or "").lower():
                        match = False
                if sub.target_agencies and opp.agency not in sub.target_agencies:
                    match = False
                if sub.min_funding and (opp.total_funding or 0) < sub.min_funding:
                    match = False

                if match:
                    log = AlertTriggerLog(
                        subscription_id=sub.id,
                        opportunity_id=opp.id,
                        matched_reason=f"In-Terminal {self.source_name} radar match on '{sub.keywords or 'all'}'",
                        delivered_to="In-Terminal Daily Feed",
                        delivered_at=datetime.utcnow()
                    )
                    db.add(log)
                    sub.matches_count = (sub.matches_count or 0) + 1
                    sub.last_triggered_at = datetime.utcnow()
                    dispatched += 1

        db.commit()
        return dispatched
