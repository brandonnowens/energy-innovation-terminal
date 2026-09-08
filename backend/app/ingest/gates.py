"""Gates Foundation CSV adapter for philanthropic funding opportunities."""

import csv
import io
import json
import logging
import sys
from typing import Optional

csv.field_size_limit(2**30)

from sqlalchemy.orm import Session

from app.ingest.base import BaseAdapter
from app.models.opportunity import Opportunity
from app.models.source import IngestionRun, Source, ChangeEvent
from app.engine.energy_filter import is_energy_innovation_relevant

logger = logging.getLogger(__name__)

class GatesAdapter(BaseAdapter):
    """Ingests Gates Foundation grants from CSV."""

    source_name = "gates_foundation"
    source_url = "https://www.gatesfoundation.org/-/media/files/bmgf-grants.csv"
    source_type = "csv"
    authority_rank = 3

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
                    description="Gates Foundation Committed Grants",
                    update_frequency="monthly",
                )
                db.add(source)
                db.commit()

            source.last_fetched_at = self.now_utc()

            logger.info(f"[{self.source_name}] Downloading CSV...")
            response = self.fetch_url(self.source_url)
            
            # The CSV might have a BOM
            text = response.text
            if text.startswith("\ufeff"):
                text = text[1:]

            # Skip metadata header lines until actual CSV columns
            lines = text.split("\n")
            header_idx = 0
            for i, line in enumerate(lines):
                if "GRANT ID" in line.upper() or "GRANTEE" in line.upper():
                    header_idx = i
                    break
            text = "\n".join(lines[header_idx:])

            reader = csv.DictReader(io.StringIO(text))
            
            seen_ids = set()
            batch_count = 0

            for row in reader:
                try:
                    # 'GRANT ID', 'GRANTEE', 'PURPOSE', 'DIVISION', 'DATE COMMITTED', 'DURATION (MONTHS)', 'AMOUNT COMMITTED', 'GRANTEE WEBSITE', 'GRANTEE CITY', 'GRANTEE STATE', 'GRANTEE COUNTRY', 'REGION SERVED', 'TOPIC'
                    grantee = row.get("GRANTEE", "").strip()
                    purpose = row.get("PURPOSE", "").strip()
                    topic = row.get("TOPIC", "").strip()
                    amount_str = row.get("AMOUNT COMMITTED", "").strip()
                    date_committed = row.get("DATE COMMITTED", "").strip() # e.g. 2021-02
                    
                    if not grantee or not purpose:
                        continue
                        
                    # Filter by energy innovation relevance and exclusions
                    is_valid, reason = is_energy_innovation_relevant(
                        title=purpose,
                        text_content=topic,
                        agency="Gates Foundation"
                    )
                    if not is_valid:
                        continue

                    amount = 0.0
                    if amount_str:
                        try:
                            amount = float(amount_str.replace(",", ""))
                        except ValueError:
                            pass
                            
                    year = None
                    if date_committed and "-" in date_committed:
                        try:
                            year = int(date_committed.split("-")[0])
                        except:
                            pass

                    # Generate unique hash for deduplication
                    ext_id = self.compute_hash(f"{grantee}_{date_committed}_{amount_str}")
                    
                    sol_num = f"GATES-{self.compute_hash(grantee + date_committed)[:10].upper()}"
                    
                    raw_data = json.dumps(row)
                    content_hash = self.compute_hash(raw_data)

                    existing = db.query(Opportunity).filter_by(external_id=ext_id).first()

                    if existing:
                        if existing.content_hash == content_hash:
                            existing.last_verified_at = self.now_utc()
                            stats["unchanged"] += 1
                        else:
                            existing.name = purpose[:500]
                            existing.short_description = purpose
                            existing.max_per_award = amount
                            existing.content_hash = content_hash
                            existing.last_verified_at = self.now_utc()
                            
                            if hasattr(existing, "raw_source_data"):
                                existing.raw_source_data = raw_data
                            if hasattr(existing, "year") and year:
                                existing.year = year
                                
                            stats["updated"] += 1
                    else:
                        opp = Opportunity(
                            solicitation_number=sol_num,
                            name=purpose[:500],
                            short_description=purpose,
                            agency="Gates Foundation",
                            jurisdiction="national",
                            status="awarded",
                            max_per_award=amount,
                            external_id=ext_id,
                            source_url=self.source_url,
                            source_name=self.source_name,
                            content_hash=content_hash,
                            first_seen_at=self.now_utc(),
                            last_verified_at=self.now_utc()
                        )
                        
                        if hasattr(opp, "org_type"):
                            opp.org_type = "philanthropic"
                        if hasattr(opp, "is_historical"):
                            opp.is_historical = True
                        if hasattr(opp, "data_provenance"):
                            opp.data_provenance = "observed"
                        if hasattr(opp, "year") and year:
                            opp.year = year
                        if hasattr(opp, "raw_source_data"):
                            opp.raw_source_data = raw_data
                            
                        db.add(opp)
                        stats["added"] += 1
                        
                    seen_ids.add(ext_id)
                    batch_count += 1
                    
                    if batch_count % 100 == 0:
                        db.commit()

                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error processing row: {e}")

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
