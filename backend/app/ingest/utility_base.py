"""Base adapter class for NY utility innovation opportunities.

Provides shared logic for scraping utility innovation program pages,
inferring utility-specific categories, and adding service territory
eligibility rules.
"""

import json
import logging
import re
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.ingest.base import BaseAdapter
from app.models.opportunity import (
    Opportunity,
    OpportunityCategory,
    OpportunityDocument,
    OpportunityRound,
    EligibilityRule,
    OpportunityRestriction,
)
from app.models.source import ChangeEvent, IngestionRun, Source

logger = logging.getLogger(__name__)


def clean_html(html_str: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    if not html_str:
        return ""
    html_str = re.sub(r'<(br|p|div)[^>]*>', ' ', html_str, flags=re.IGNORECASE)
    html_str = re.sub(r'<[^>]+>', '', html_str)
    html_str = html_str.replace('&nbsp;', ' ').replace('&amp;', '&')
    html_str = html_str.replace('&#39;', "'").replace('&quot;', '"')
    return re.sub(r'\s+', ' ', html_str).strip()


def parse_date_flexible(date_str: str) -> Optional[datetime]:
    """Parse dates in various formats commonly found on utility sites."""
    if not date_str or not date_str.strip():
        return None
    date_str = date_str.strip()
    date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

    formats = [
        "%B %d, %Y, %I:%M %p",
        "%B %d, %Y",
        "%b %d, %Y, %I:%M %p",
        "%b %d, %Y",
        "%m/%d/%Y %I:%M %p",
        "%m/%d/%Y",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', date_str)
    if match:
        try:
            return datetime.strptime(match.group(1), "%B %d, %Y")
        except ValueError:
            pass

    logger.warning(f"Could not parse date: {date_str}")
    return None


# Utility-specific category keyword maps
UTILITY_PROGRAM_KEYWORDS = {
    "non-wires alternative": "NWA",
    "non-wires": "NWA",
    "nwa": "NWA",
    "non-pipe alternative": "NPA",
    "non-pipe": "NPA",
    "npa": "NPA",
    "dynamic load management": "DLM",
    "dlm": "DLM",
    "demand response": "Demand Response",
    "demand-side management": "DSM",
    "dsm": "DSM",
    "virtual power plant": "VPP",
    "vpp": "VPP",
    "pilot": "Pilot Program",
    "demonstration": "Demonstration",
    "innovation": "Innovation",
    "research and development": "R&D",
    "r&d": "R&D",
    "energy storage": "Energy Storage",
    "bulk storage": "Bulk Energy Storage",
    "grid modernization": "Grid Modernization",
    "grid-enhancing": "Grid-Enhancing Technologies",
    "thermal energy network": "Thermal Energy Network",
    "uten": "Thermal Energy Network",
    "electrification": "Building Electrification",
    "ev charging": "EV Charging",
    "electric vehicle": "EV Charging",
    "resilience": "Resilience",
    "microgrid": "Microgrid",
    "distributed energy": "Distributed Energy Resources",
    "der": "Distributed Energy Resources",
    "solar": "Solar",
    "wind": "Wind",
    "geothermal": "Geothermal",
    "hydrogen": "Hydrogen",
    "fuel cell": "Fuel Cells",
    "carbon capture": "Carbon Management",
    "advanced metering": "Advanced Metering",
    "smart grid": "Smart Grid",
    "cybersecurity": "Cybersecurity",
}

TECH_KEYWORDS = {
    "solar": "Solar",
    "wind": "Wind",
    "battery": "Energy Storage",
    "energy storage": "Energy Storage",
    "heat pump": "Building Electrification",
    "grid": "Grid Modernization",
    "hydrogen": "Hydrogen & Alternative Fuels",
    "fuel cell": "Fuel Cells",
    "carbon": "Carbon Management",
    "ev": "Clean Transportation",
    "electric vehicle": "Clean Transportation",
    "geothermal": "Geothermal",
    "resilience": "Resilience",
    "cybersecurity": "Cybersecurity",
    "nuclear": "Nuclear",
    "transmission": "Grid Modernization",
    "distribution": "Grid Modernization",
    "microgrid": "Microgrid",
    "der": "Distributed Energy Resources",
}

ACTIVITY_KEYWORDS = {
    "demonstration": "Demonstration",
    "pilot": "Pilot",
    "research": "Research",
    "product development": "Product Development",
    "feasibility": "Feasibility Study",
    "deployment": "Deployment",
    "scale-up": "Scale-up",
    "retrofit": "Retrofit",
    "testing": "Testing & Validation",
}


class UtilityBaseAdapter(BaseAdapter):
    """Base class for all NY utility innovation adapters.

    Subclasses must set:
        utility_name: str       — e.g. "Con Edison"
        service_territory: str  — e.g. "NYC, Westchester"
        source_name: str        — e.g. "coned_innovation"
        source_url: str         — public innovation page URL
    """

    utility_name: str = ""
    service_territory: str = ""
    parent_company: str = ""
    regulatory_body: str = "NY PSC"
    source_type = "html"
    authority_rank = 2

    def _build_opportunity_defaults(self) -> dict:
        """Common fields for all utility-sourced opportunities."""
        return {
            "agency": self.utility_name,
            "agency_code": self.source_name.upper(),
            "jurisdiction": "utility_ny",
            "org_type": "utility",
            "source_url": self.source_url,
            "source_name": self.source_name,
            "geographic_scope": self.service_territory,
            "data_provenance": "observed",
        }

    def _ensure_source(self, db: Session) -> Source:
        """Create or update the Source record for this adapter."""
        source = db.query(Source).filter_by(name=self.source_name).first()
        if not source:
            source = Source(
                name=self.source_name,
                url=self.source_url,
                source_type=self.source_type,
                authority_rank=self.authority_rank,
                description=f"{self.utility_name} innovation and procurement opportunities",
                update_frequency="daily",
            )
            db.add(source)
        source.last_fetched_at = self.now_utc()
        source.fetch_status = "success"
        db.commit()
        return source

    def _upsert_opportunity(
        self,
        db: Session,
        sol_num: str,
        opp_data: dict,
        categories: list[dict] | None = None,
        rules: list[dict] | None = None,
        restrictions: list[dict] | None = None,
        documents: list[dict] | None = None,
        rounds: list[dict] | None = None,
    ) -> str:
        """Create or update an opportunity. Returns 'added', 'updated', or 'unchanged'."""
        content_hash = self.compute_hash(json.dumps(opp_data, sort_keys=True, default=str))

        existing = db.query(Opportunity).filter_by(solicitation_number=sol_num).first()

        if existing:
            if existing.content_hash == content_hash:
                existing.last_verified_at = self.now_utc()
                db.commit()
                return "unchanged"
            # Detect status change
            if existing.status != opp_data.get("status", existing.status):
                db.add(ChangeEvent(
                    entity_type="opportunity",
                    entity_id=sol_num,
                    entity_name=existing.name,
                    change_type="status_change",
                    field_name="status",
                    old_value=existing.status,
                    new_value=opp_data.get("status"),
                    source_name=self.source_name,
                ))
            # Update fields
            for key, value in opp_data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.content_hash = content_hash
            existing.last_verified_at = self.now_utc()
            db.commit()
            return "updated"

        # Create new
        defaults = self._build_opportunity_defaults()
        defaults.update(opp_data)
        defaults["solicitation_number"] = sol_num
        defaults["content_hash"] = content_hash
        defaults["first_seen_at"] = self.now_utc()
        defaults["last_verified_at"] = self.now_utc()

        opp = Opportunity(**defaults)
        db.add(opp)
        db.flush()

        # Add categories
        if categories:
            for cat in categories:
                db.add(OpportunityCategory(opportunity_id=opp.id, **cat))

        # Add eligibility rules
        self._add_default_rules(db, opp.id)
        if rules:
            for rule in rules:
                db.add(EligibilityRule(opportunity_id=opp.id, **rule))

        # Add restrictions
        if restrictions:
            for r in restrictions:
                db.add(OpportunityRestriction(opportunity_id=opp.id, **r))

        # Add documents
        if documents:
            for doc in documents:
                db.add(OpportunityDocument(opportunity_id=opp.id, **doc))

        # Add rounds
        if rounds:
            for rnd in rounds:
                db.add(OpportunityRound(opportunity_id=opp.id, **rnd))

        # Record as new
        db.add(ChangeEvent(
            entity_type="opportunity",
            entity_id=sol_num,
            entity_name=opp_data.get("name", sol_num),
            change_type="new",
            source_name=self.source_name,
        ))
        db.commit()
        return "added"

    def _add_default_rules(self, db: Session, opp_id: int):
        """Add default eligibility rules for utility opportunities."""
        # Service territory rule
        db.add(EligibilityRule(
            opportunity_id=opp_id,
            rule_type="geography",
            rule_key="service_territory",
            rule_value=self.service_territory,
            rule_operator="in",
            is_hard_requirement=True,
            source=f"{self.utility_name} service territory",
            confidence=0.9,
        ))
        # State rule
        db.add(EligibilityRule(
            opportunity_id=opp_id,
            rule_type="geography",
            rule_key="state",
            rule_value="NY",
            rule_operator="equals",
            is_hard_requirement=True,
            source=f"{self.utility_name} is a New York utility",
            confidence=1.0,
        ))

    def infer_categories(self, text: str) -> list[dict]:
        """Infer technology, activity, and utility program type categories from text."""
        if not text:
            return []

        categories = []
        combined = text.lower()
        seen = set()

        # Utility program type
        for keyword, program_type in UTILITY_PROGRAM_KEYWORDS.items():
            if keyword in combined and program_type not in seen:
                categories.append({
                    "category_type": "utility_program",
                    "category_value": program_type,
                    "confidence": 0.85,
                    "source": "description_inference",
                })
                seen.add(program_type)

        # Technology areas
        for keyword, tech in TECH_KEYWORDS.items():
            if keyword in combined and tech not in seen:
                categories.append({
                    "category_type": "technology",
                    "category_value": tech,
                    "confidence": 0.8,
                    "source": "description_inference",
                })
                seen.add(tech)

        # Activity types
        for keyword, activity in ACTIVITY_KEYWORDS.items():
            if keyword in combined and activity not in seen:
                categories.append({
                    "category_type": "activity",
                    "category_value": activity,
                    "confidence": 0.8,
                    "source": "description_inference",
                })
                seen.add(activity)

        return categories

    def _extract_funding(self, text: str) -> tuple[Optional[float], Optional[float]]:
        """Extract total funding and max per award from description text."""
        total = None
        per_award = None
        if not text:
            return total, per_award

        money_pattern = r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|M|B))?'
        matches = re.findall(money_pattern, text, re.IGNORECASE)

        for match in matches:
            value = match.replace('$', '').replace(',', '').strip()
            multiplier = 1
            if 'million' in value.lower() or value.endswith('M'):
                value = re.sub(r'\s*(million|M)\s*', '', value, flags=re.IGNORECASE)
                multiplier = 1_000_000
            elif 'billion' in value.lower() or value.endswith('B'):
                value = re.sub(r'\s*(billion|B)\s*', '', value, flags=re.IGNORECASE)
                multiplier = 1_000_000_000
            try:
                num = float(value) * multiplier
                if total is None:
                    total = num
                elif per_award is None and num < total:
                    per_award = num
            except ValueError:
                continue

        return total, per_award

    def _infer_status(self, text: str) -> str:
        """Infer solicitation status from text."""
        lower = text.lower()
        if any(w in lower for w in ["closed", "expired", "past due", "no longer accepting"]):
            return "closed"
        if any(w in lower for w in ["upcoming", "anticipated", "forthcoming", "draft"]):
            return "draft"
        return "open"

    def _infer_solicitation_type(self, text: str) -> str:
        """Infer solicitation type (RFP, RFI, RFQ, etc.) from text."""
        lower = text.lower()
        if "request for information" in lower or "rfi" in lower:
            return "RFI"
        if "request for qualification" in lower or "rfq" in lower:
            return "RFQ"
        if "request for proposal" in lower or "rfp" in lower:
            return "RFP"
        if "request for offer" in lower or "rfo" in lower:
            return "RFO"
        return "RFP"  # Default to RFP for utility procurement

    def _run_ingestion(self, db: Session, fetch_fn) -> dict:
        """Standard ingestion wrapper with error handling and run tracking.

        Args:
            db: Database session
            fetch_fn: Callable(db) -> tuple[int, int] of (seen_count, error_count)
                      or uses stats dict internally
        """
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}
        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            source = self._ensure_source(db)
            stats = fetch_fn(db, stats)

            source.record_count = stats["added"] + stats["updated"] + stats["unchanged"]
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
