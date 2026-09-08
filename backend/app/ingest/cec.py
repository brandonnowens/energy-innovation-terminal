"""CEC (California Energy Commission) API adapter for funding opportunities.

Uses web scraping of the Drupal CMS pages to extract GFO opportunities.
"""

import json
import logging
import re
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
import httpx

from app.config import settings
from app.ingest.base import BaseAdapter
from app.models.opportunity import (
    Opportunity,
    OpportunityRound,
    OpportunityCategory,
)
from app.models.source import ChangeEvent, IngestionRun, Source

logger = logging.getLogger(__name__)


def _parse_date(date_str: str) -> Optional[datetime]:
    if not date_str or not date_str.strip():
        return None
    
    # Try various formats commonly found
    date_str = date_str.strip()
    # Format e.g., November 20, 2026, 11:59 pm
    # Or just November 20, 2026
    # Remove ordinal suffixes if any
    date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    
    formats = [
        "%B %d, %Y, %I:%M %p",
        "%B %d, %Y",
        "%b %d, %Y, %I:%M %p",
        "%b %d, %Y",
        "%m/%d/%Y",
        "%Y-%m-%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    # As a fallback, try to extract just the date part (Month DD, YYYY)
    match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', date_str)
    if match:
        try:
            return datetime.strptime(match.group(1), "%B %d, %Y")
        except ValueError:
            pass
            
    logger.warning(f"Could not parse date: {date_str}")
    return None


def _clean_html(html_str: str) -> str:
    """Strip HTML tags from a string."""
    if not html_str:
        return ""
    # Replace <br> and <p> with spaces to avoid joining words
    html_str = re.sub(r'<(br|p|div)[^>]*>', ' ', html_str, flags=re.IGNORECASE)
    # Remove all other tags
    html_str = re.sub(r'<[^>]+>', '', html_str)
    # Unescape some common HTML entities
    html_str = html_str.replace('&nbsp;', ' ').replace('&amp;', '&')
    html_str = html_str.replace('&#39;', "'").replace('&quot;', '"')
    html_str = html_str.replace('', "'") # Common encoding issue replacement
    # Clean up whitespace
    return re.sub(r'\s+', ' ', html_str).strip()


def _infer_categories(desc: str, name: str) -> list[dict]:
    """Infer technology/activity categories from description text."""
    categories = []
    combined = f"{name} {desc}".lower()

    tech_keywords = {
        "solar": "Solar",
        "wind": "Wind",
        "offshore wind": "Offshore Wind",
        "battery": "Energy Storage",
        "energy storage": "Energy Storage",
        "heat pump": "Building Electrification",
        "building electrification": "Building Electrification",
        "hvac": "Building Electrification",
        "grid": "Grid Modernization",
        "transmission": "Grid Modernization",
        "hydrogen": "Hydrogen & Alternative Fuels",
        "fuel cell": "Hydrogen & Alternative Fuels",
        "carbon capture": "Carbon Management",
        "ccus": "Carbon Management",
        "electric vehicle": "Clean Transportation",
        "ev charging": "Clean Transportation",
        "geothermal": "Thermal Energy Networks",
        "nuclear": "Nuclear",
        "advanced reactor": "Nuclear",
        "cybersecurity": "Cybersecurity",
        "water": "Water",
        "desalination": "Water",
        "air quality": "Environmental Research",
        "emissions": "Environmental Research",
        "wildfire": "Resilience",
        "climate resilient": "Resilience",
    }

    seen = set()
    for keyword, tech in tech_keywords.items():
        if keyword in combined and tech not in seen:
            categories.append({
                "category_type": "technology",
                "category_value": tech,
                "confidence": 0.8,
                "source": "description_inference",
            })
            seen.add(tech)

    activity_keywords = {
        "demonstration": "Demonstration",
        "research": "Research",
        "product development": "Product Development",
        "feasibility": "Feasibility Study",
        "training": "Training",
        "technical assistance": "Technical Assistance",
        "deployment": "Deployment",
        "scale-up": "Scale-up",
        "retrofit": "Retrofit",
    }

    for keyword, activity in activity_keywords.items():
        if keyword in combined:
            categories.append({
                "category_type": "activity",
                "category_value": activity,
                "confidence": 0.8,
                "source": "description_inference",
            })

    return categories


class CECAdapter(BaseAdapter):
    """Ingests current funding opportunities from California Energy Commission (CEC)."""

    source_name = "cec"
    source_url = "https://www.energy.ca.gov/funding-opportunities"
    source_type = "html"
    authority_rank = 2
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.energy.ca.gov"
        self.solicitations_url = f"{self.base_url}/funding-opportunities/solicitations"

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}

        # Record ingestion run
        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            # Fetch listing page
            response = self.fetch_url(self.solicitations_url)
            html = response.text
            content_hash = self.compute_hash(html)

            # Update source record
            source = db.query(Source).filter_by(name=self.source_name).first()
            if not source:
                source = Source(
                    name=self.source_name,
                    url=self.source_url,
                    source_type=self.source_type,
                    authority_rank=self.authority_rank,
                    description="California Energy Commission (CEC) Funding Opportunities",
                    update_frequency="daily",
                )
                db.add(source)

            source.last_fetched_at = self.now_utc()
            source.fetch_status = "success"
            
            # Extract solicitations from the HTML
            # Pattern: <a href="/solicitations/...">...<h3...>GFO-XX-XXX - Title</h3>
            pattern = r'<a href="(/solicitations/[^"]+)"[^>]*>(?:(?!</a>).)*?<h3[^>]*>(GFO-\d{2}-\d{3})\s*-\s*(.*?)</h3>'
            matches = re.findall(pattern, html, flags=re.DOTALL | re.IGNORECASE)
            
            seen_numbers = set()

            for match in matches:
                link_path, gfo_num, title = match
                detail_url = f"{self.base_url}{link_path}"
                
                try:
                    result = self._process_opportunity(db, detail_url, gfo_num, _clean_html(title))
                    stats[result] += 1
                    seen_numbers.add(gfo_num)
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error processing CEC opportunity {gfo_num}: {e}", exc_info=True)

            # Count totals
            source.record_count = len(seen_numbers)
            source.content_hash = content_hash
            db.commit()

            run.status = "success"
            run.records_added = stats["added"]
            run.records_updated = stats["updated"]
            run.records_unchanged = stats["unchanged"]
            run.errors = stats["errors"]
            run.completed_at = self.now_utc()
            db.commit()

            logger.info(
                f"[{self.source_name}] Ingestion complete: "
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

    def _process_opportunity(self, db: Session, detail_url: str, gfo_num: str, title: str) -> str:
        """Process a single CEC opportunity detail page."""
        
        # Fetch the detail page
        response = self.fetch_url(detail_url)
        detail_html = response.text
        
        # We need a robust hash for change detection, let's use the whole page body
        content_hash = self.compute_hash(detail_html)

        existing = db.query(Opportunity).filter_by(solicitation_number=gfo_num).first()

        if existing:
            if existing.content_hash == content_hash:
                existing.last_verified_at = self.now_utc()
                db.commit()
                return "unchanged"

        # Parse details
        desc, deadline_str, status = self._parse_detail_html(detail_html)
        
        # Build opportunity record
        opp_data = {
            "solicitation_number": gfo_num,
            "name": title,
            "solicitation_type": "GFO",
            "status": status,
            "short_description": desc,
            "detail_page_url": detail_url,
            "agency": "CEC",
            "agency_code": "CEC",
            "jurisdiction": "state_ca",
            "source_url": self.source_url,
            "source_name": self.source_name,
            "content_hash": content_hash,
            "enrollment_type": "Due Date" if deadline_str else "Unknown",
        }

        if existing:
            # Detect changes and update
            self._detect_changes(db, existing, opp_data)
            
            existing.name = title
            existing.status = status
            existing.short_description = desc
            existing.detail_page_url = detail_url
            existing.content_hash = content_hash
            existing.last_verified_at = self.now_utc()
            existing.enrollment_type = opp_data["enrollment_type"]
            
            # Update rounds
            db.query(OpportunityRound).filter_by(opportunity_id=existing.id).delete()
            if deadline_str:
                due_date = _parse_date(deadline_str)
                if due_date:
                    db.add(OpportunityRound(
                        opportunity_id=existing.id,
                        round_number="1",
                        status=status,
                        due_date=due_date,
                    ))
            
            db.commit()
            return "updated"

        # Create new
        opp = Opportunity(
            **opp_data,
            first_seen_at=self.now_utc(),
            last_verified_at=self.now_utc(),
        )
        db.add(opp)
        db.flush()

        # Add round if deadline exists
        if deadline_str:
            due_date = _parse_date(deadline_str)
            if due_date:
                db.add(OpportunityRound(
                    opportunity_id=opp.id,
                    round_number="1",
                    status=status,
                    due_date=due_date,
                ))

        # Infer categories
        for cat_data in _infer_categories(desc, title):
            db.add(OpportunityCategory(
                opportunity_id=opp.id,
                **cat_data,
            ))

        db.add(ChangeEvent(
            entity_type="opportunity",
            entity_id=gfo_num,
            entity_name=title,
            change_type="new",
            source_name=self.source_name,
        ))
        db.commit()
        return "added"

    def _parse_detail_html(self, html: str) -> tuple[str, str, str]:
        """Extract description, deadline, and status from detail HTML."""
        # 1. Description
        desc = ""
        # Try finding the Purpose field
        purpose_match = re.search(r'<div[^>]*class="[^"]*field--name-field-purpose[^"]*"[^>]*>.*?<div class="field__item">(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
        if purpose_match:
            desc = _clean_html(purpose_match.group(1))
        
        if not desc:
            # Fallback to meta description
            meta_match = re.search(r'<meta[^>]*name="description"[^>]*content="(.*?)"', html, re.IGNORECASE)
            if meta_match:
                desc = _clean_html(meta_match.group(1))
                
        # 2. Deadline - find text after "Submission Deadline" label
        deadline_str = ""
        dl_idx = html.find("Submission Deadline")
        if dl_idx > 0:
            chunk = html[dl_idx:dl_idx+300]
            dd_m = re.search(r'<dd[^>]*>(.*?)</dd>', chunk, re.DOTALL | re.IGNORECASE)
            if dd_m:
                raw = dd_m.group(1)
                deadline_str = re.sub(r'<[^>]+>', '', raw).strip()
                # Strip hidden Unicode characters (zero-width joiners, etc.)
                deadline_str = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff]', '', deadline_str)
            
        # 3. Status - find text after "Solicitation Status" label
        status = "closed"
        st_idx = html.find("Solicitation Status")
        if st_idx > 0:
            chunk = html[st_idx:st_idx+200]
            dd_m = re.search(r'<dd[^>]*>(.*?)</dd>', chunk, re.DOTALL | re.IGNORECASE)
            if dd_m:
                raw_status = re.sub(r'<[^>]+>', '', dd_m.group(1)).strip().lower()
                raw_status = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff]', '', raw_status)
                if "active" in raw_status or "open" in raw_status:
                    status = "open"
                elif "anticipated" in raw_status or "upcoming" in raw_status:
                    status = "draft"
                
        return desc, deadline_str, status

    def _detect_changes(self, db: Session, existing: Opportunity, new_data: dict):
        """Detect and record changes between existing and new data."""
        gfo_num = existing.solicitation_number

        if existing.status != new_data["status"]:
            db.add(ChangeEvent(
                entity_type="opportunity",
                entity_id=gfo_num,
                entity_name=existing.name,
                change_type="status_change",
                field_name="status",
                old_value=existing.status,
                new_value=new_data["status"],
                source_name=self.source_name,
            ))
            
        if existing.name != new_data["name"]:
            db.add(ChangeEvent(
                entity_type="opportunity",
                entity_id=gfo_num,
                entity_name=existing.name,
                change_type="field_change",
                field_name="name",
                old_value=existing.name,
                new_value=new_data["name"],
                source_name=self.source_name,
            ))
            
        db.commit()
