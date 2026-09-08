"""NSF Awards API adapter for historical funding opportunities."""

import json
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.ingest.base import BaseAdapter
from app.models.opportunity import Opportunity
from app.models.source import IngestionRun, Source, ChangeEvent
from app.engine.energy_filter import is_energy_innovation_relevant

logger = logging.getLogger(__name__)

KEYWORDS = (
    '"clean energy" OR "renewable energy" OR "solar energy" OR "wind energy" '
    'OR "energy storage" OR "battery storage" OR "grid modernization" OR "smart grid" '
    'OR "hydrogen fuel" OR "fuel cell" OR "carbon capture" OR "decarbonization" '
    'OR "building energy" OR "energy efficiency" OR "electric vehicle" '
    'OR "offshore wind" OR "geothermal" OR "nuclear energy" OR "energy innovation" '
    'OR "clean power" OR "power grid" OR "energy transition" OR "zero emission" '
    'OR "net zero" OR "photovoltaic" OR "building electrification" '
    'OR "heat pump" OR "carbon dioxide removal" OR "direct air capture" '
    'OR "sustainable aviation fuel" OR "long duration storage"'
)

class NSFAwardsAdapter(BaseAdapter):
    """Ingests historical NSF awards from public API."""

    source_name = "nsf_awards"
    source_url = "https://api.nsf.gov/services/v1/awards.json"
    source_type = "api"
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
                    description="NSF Historical Awards",
                    update_frequency="monthly",
                )
                db.add(source)
                db.commit()

            source.last_fetched_at = self.now_utc()

            params = {
                'keyword': KEYWORDS,
                'dateStart': '01/01/1994',
                'rpp': 25,
                'offset': 0,
                'printFields': 'id,title,agency,awardeeName,awardeeCity,awardeeStateCode,fundsObligatedAmt,estimatedTotalAmt,startDate,expDate,date,abstractText,piFirstName,piLastName,fundProgramName,primaryProgram,cfdaNumber'
            }

            seen_ids = set()
            batch_count = 0
            
            # Start pagination
            while True:
                logger.info(f"[{self.source_name}] Fetching offset {params['offset']}")
                resp = self.fetch_json(self.source_url, params=params)
                
                awards = resp.get("response", {}).get("award", [])
                if not awards:
                    break
                    
                for award in awards:
                    try:
                        ext_id = str(award.get("id"))
                        title = award.get("title", "")
                        abstract = award.get("abstractText", "")
                        
                        # Rigorous energy-innovation relevance and exclusion filter
                        is_valid, reason = is_energy_innovation_relevant(
                            title=title,
                            text_content=abstract,
                            agency="NSF"
                        )
                        if not is_valid:
                            continue
                        
                        amount = 0.0
                        amt_str = award.get("estimatedTotalAmt")
                        if amt_str:
                            try:
                                amount = float(amt_str)
                            except ValueError:
                                pass
                                
                        award_date = award.get("date", "")
                        year = None
                        if award_date:
                            try:
                                # format might be MM/DD/YYYY or similar, we can just grab the last 4 if it's year
                                parts = award_date.split("/")
                                if len(parts) == 3:
                                    year = int(parts[2])
                            except:
                                pass
                                
                        raw_data = json.dumps(award)
                        content_hash = self.compute_hash(raw_data)
                        
                        existing = db.query(Opportunity).filter_by(external_id=ext_id).first()
                        
                        if existing:
                            if existing.content_hash == content_hash:
                                existing.last_verified_at = self.now_utc()
                                stats["unchanged"] += 1
                            else:
                                existing.name = title[:500]
                                existing.short_description = abstract[:2000] if abstract else None
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
                                solicitation_number=ext_id,
                                name=title[:500],
                                short_description=abstract[:2000] if abstract else None,
                                agency="NSF",
                                jurisdiction="federal",
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
                                opp.org_type = "government"
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
                        
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"Error processing award {award.get('id')}: {e}")
                        
                if batch_count % 100 == 0:
                    db.commit()
                
                # Setup next page
                params['offset'] += params['rpp']
                
                # Avoid hammering indefinitely in development
                # if params['offset'] > 1000: break # Uncomment if you need a hard cap

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
