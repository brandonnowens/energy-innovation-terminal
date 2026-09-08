"""Massachusetts Clean Energy Center (MassCEC) funding opportunities adapter."""

import json
import logging
import re
import time
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.ingest.base import BaseAdapter
from app.models.opportunity import (
    Opportunity,
    OpportunityCategory,
)
from app.models.source import ChangeEvent, IngestionRun, Source

logger = logging.getLogger(__name__)


def _clean_html(html_str: str) -> str:
    """Strip HTML tags from a string and normalize whitespace."""
    if not html_str:
        return ""
    # Replace <br> and </p> with space before stripping tags
    html_str = re.sub(r'<(br|/p|/div|/li)[^>]*>', ' ', html_str, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", html_str)
    # Replace HTML entities
    text = text.replace("&amp;", "&").replace("&nbsp;", " ").replace("&quot;", '"')
    text = text.replace("&#39;", "'").replace("&rsquo;", "'").replace("&ndash;", "-")
    return re.sub(r"\s+", " ", text).strip()


def _extract_funding_from_text(desc: str) -> tuple[Optional[float], Optional[float]]:
    """Try to extract total funding and max per award from text."""
    total = None
    per_award = None
    if not desc:
        return total, per_award

    money_pattern = r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|[kKMmBb]))?'
    matches = re.findall(money_pattern, desc, re.IGNORECASE)

    for match in matches:
        value = match.replace('$', '').replace(',', '').strip()
        multiplier = 1
        val_lower = value.lower()
        if 'million' in val_lower or 'm' in val_lower.split()[-1] or val_lower.endswith('m'):
            value = re.sub(r'\s*million\s*|m$', '', val_lower, flags=re.IGNORECASE)
            multiplier = 1_000_000
        elif 'billion' in val_lower or 'b' in val_lower.split()[-1] or val_lower.endswith('b'):
            value = re.sub(r'\s*billion\s*|b$', '', val_lower, flags=re.IGNORECASE)
            multiplier = 1_000_000_000
        elif 'k' in val_lower.split()[-1] or val_lower.endswith('k'):
            value = re.sub(r'k$', '', val_lower, flags=re.IGNORECASE)
            multiplier = 1_000

        try:
            num = float(value.strip()) * multiplier
            if total is None:
                total = num
            elif per_award is None and num < total:
                per_award = num
        except ValueError:
            continue

    return total, per_award


def _infer_categories(desc: str, title: str) -> list[dict]:
    """Infer technology/activity categories from opportunity data."""
    categories = []
    combined = f"{title} {desc}".lower()

    tech_keywords = {
        "grid": "Grid Modernization",
        "solar": "Solar",
        "wind": "Wind",
        "storage": "Energy Storage",
        "battery": "Energy Storage",
        "hydrogen": "Hydrogen & Alternative Fuels",
        "heat pump": "Building Electrification",
        "electrification": "Building Electrification",
        "building": "Buildings",
        "ev": "Clean Transportation",
        "electric vehicle": "Clean Transportation",
        "charging": "Clean Transportation",
        "transportation": "Clean Transportation",
        "manufacturing": "Manufacturing",
        "workforce": "Workforce Development",
        "air quality": "Environmental Research",
        "methane": "Environmental Research",
        "fuel cell": "Fuel Cells",
        "carbon": "Carbon Management",
        "offshore wind": "Offshore Wind",
        "geothermal": "Geothermal",
        "thermal": "Thermal Energy",
        "resilience": "Resilience",
        "cybersecurity": "Cybersecurity",
        "multifamily": "Multifamily Buildings",
        "climatetech": "Climatetech",
    }

    for keyword, category in tech_keywords.items():
        if keyword in combined:
            categories.append({
                "category_type": "technology",
                "category_value": category,
                "confidence": 0.8,
                "source": "description_inference",
            })

    activity_keywords = {
        "demonstration": "Demonstration",
        "research": "Research",
        "product development": "Product Development",
        "feasibility": "Feasibility Study",
        "training": "Training",
        "technical assistance": "Technical Assistance",
        "deployment": "Deployment",
        "scale-up": "Scale-up",
        "incentive": "Incentive Program",
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


class MassCECAdapter(BaseAdapter):
    """Ingests current funding opportunities from MassCEC website."""

    source_name = "masscec"
    source_url = "https://www.masscec.com/funding"
    source_type = "html"
    authority_rank = 2
    base_url = "https://www.masscec.com"

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}

        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            response = self.fetch_url(self.source_url)
            html = response.text
            
            # Simple content hash based on raw html
            content_hash = self.compute_hash(html)

            source = db.query(Source).filter_by(name=self.source_name).first()
            if not source:
                source = Source(
                    name=self.source_name,
                    url=self.source_url,
                    source_type=self.source_type,
                    authority_rank=self.authority_rank,
                    description="Massachusetts Clean Energy Center funding opportunities",
                    update_frequency="daily",
                )
                db.add(source)

            source.last_fetched_at = self.now_utc()
            source.fetch_status = "success"
            source.content_hash = content_hash
            db.commit()

            # Find all opportunity blocks
            blocks = re.findall(r'<div class="views-row">(.*?)(?=<div class="views-row">|</div>\s*</div>\s*</div>)', html, re.DOTALL)
            seen_numbers = set()

            for block in blocks:
                try:
                    # Extract title and link
                    title_match = re.search(r'<span class="field-content"><a href="([^"]+)"[^>]*>(.*?)</a></span>', block)
                    if not title_match:
                        continue
                        
                    link = title_match.group(1)
                    title = _clean_html(title_match.group(2))
                    
                    sol_num = f"MassCEC-{link.strip('/').split('/')[-1]}"
                    seen_numbers.add(sol_num)
                    
                    # Extract status
                    status = "open"
                    status_match = re.search(r'<div class="field-content status-([^"]+)">', block)
                    if status_match:
                        status = status_match.group(1).lower()
                        
                    # Extract type
                    opp_type = None
                    type_match = re.search(r'<span class="views-label views-label-field-funding-type">.*?</span>\s*<div class="field-content">(.*?)</div>', block, re.DOTALL)
                    if type_match:
                        opp_type = _clean_html(type_match.group(1))
                        
                    # Extract deadline
                    deadline = None
                    deadline_match = re.search(r'<span class="views-label views-label-field-application-deadline">.*?</span>\s*<div class="field-content">(.*?)</div>', block, re.DOTALL)
                    if deadline_match:
                        deadline = _clean_html(deadline_match.group(1))
                        
                    # Extract award limit
                    award_limit = None
                    award_match = re.search(r'<span class="views-label views-label-field-award-limit">.*?</span>\s*<div class="field-content">(.*?)</div>', block, re.DOTALL)
                    if award_match:
                        award_limit = _clean_html(award_match.group(1))

                    # Fetch detail page
                    detail_url = self.base_url + link if link.startswith('/') else link
                    time.sleep(1) # Explicit rate limit
                    
                    try:
                        detail_resp = self.fetch_url(detail_url)
                        detail_html = detail_resp.text
                        
                        # Extract description from detail page
                        desc_match = re.search(r'<div class="clearfix text-formatted field field--name-body[^>]*>(.*?)</div>\s*</article>', detail_html, re.DOTALL)
                        if not desc_match:
                            desc_match = re.search(r'<div class="clearfix text-formatted field field--name-body[^>]*>(.*?)(?:</div>\s*</div>|</article>)', detail_html, re.DOTALL)
                        
                        if desc_match:
                            desc = _clean_html(desc_match.group(1))
                        else:
                            desc = ""
                    except Exception as e:
                        logger.warning(f"Failed to fetch detail page {detail_url}: {e}")
                        desc = ""

                    total_funding, max_per_award = _extract_funding_from_text(award_limit or desc)

                    opp_data = {
                        "solicitation_number": sol_num,
                        "name": title,
                        "status": status,
                        "detail_page_url": detail_url,
                        "short_description": desc,
                        "due_date_display": deadline,
                        "solicitation_type": opp_type or "Program",
                        "total_funding": total_funding,
                        "max_per_award": max_per_award,
                    }

                    result = self._process_opportunity(db, opp_data)
                    stats[result] += 1

                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error processing MassCEC block: {e}", exc_info=True)

            source.record_count = len(seen_numbers)
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

    def _process_opportunity(self, db: Session, data: dict) -> str:
        sol_num = data["solicitation_number"]
        content_hash = self.compute_hash(json.dumps(data, sort_keys=True))

        existing = db.query(Opportunity).filter_by(solicitation_number=sol_num).first()

        if existing:
            if existing.content_hash == content_hash:
                existing.last_verified_at = self.now_utc()
                db.commit()
                return "unchanged"
            self._update_opportunity(db, existing, data, content_hash)
            return "updated"

        self._create_opportunity(db, data, content_hash)
        db.add(ChangeEvent(
            entity_type="opportunity",
            entity_id=sol_num,
            entity_name=data["name"],
            change_type="new",
            source_name=self.source_name,
        ))
        db.commit()
        return "added"

    def _create_opportunity(self, db: Session, data: dict, content_hash: str):
        opp = Opportunity(
            solicitation_number=data["solicitation_number"],
            name=data["name"],
            solicitation_type=data["solicitation_type"],
            status=data["status"],
            short_description=data["short_description"],
            total_funding=data["total_funding"],
            max_per_award=data["max_per_award"],
            detail_page_url=data["detail_page_url"],
            due_date_display=data["due_date_display"],
            source_url=self.source_url,
            source_name=self.source_name,
            content_hash=content_hash,
            first_seen_at=self.now_utc(),
            last_verified_at=self.now_utc(),
            agency="MassCEC",
            agency_code="MassCEC",
            jurisdiction="state_ma",
        )
        db.add(opp)
        db.flush()

        for cat_data in _infer_categories(data["short_description"], data["name"]):
            db.add(OpportunityCategory(
                opportunity_id=opp.id,
                **cat_data,
            ))
        db.commit()

    def _update_opportunity(self, db: Session, opp: Opportunity, data: dict, content_hash: str):
        opp.name = data["name"]
        opp.solicitation_type = data["solicitation_type"]
        opp.status = data["status"]
        opp.short_description = data["short_description"]
        opp.total_funding = data["total_funding"]
        opp.max_per_award = data["max_per_award"]
        opp.detail_page_url = data["detail_page_url"]
        opp.due_date_display = data["due_date_display"]
        opp.content_hash = content_hash
        opp.last_verified_at = self.now_utc()

        # Update categories by replacing them
        db.query(OpportunityCategory).filter_by(opportunity_id=opp.id).delete()
        for cat_data in _infer_categories(data["short_description"], data["name"]):
            db.add(OpportunityCategory(
                opportunity_id=opp.id,
                **cat_data,
            ))
            
        db.commit()
