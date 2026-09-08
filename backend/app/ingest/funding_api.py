"""NYSERDA Funding Opportunities JSON API adapter.

This is the primary data source for current opportunities.
Uses the native JSON API discovered at:
https://www.nyserda.ny.gov/rapi/fundingopportunitiesapi/getfundingopportunities
"""

import json
import logging
import re
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.ingest.base import BaseAdapter
from app.models.opportunity import (
    Opportunity,
    OpportunityContact,
    OpportunityDocument,
    OpportunityRound,
    OpportunityCategory,
    EligibilityRule,
)
from app.models.source import ChangeEvent, IngestionRun, Source

logger = logging.getLogger(__name__)


def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string from NYSERDA API (e.g., '10/28/2026 3:00 PM')."""
    if not date_str or not date_str.strip():
        return None
    for fmt in ["%m/%d/%Y %I:%M %p", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    logger.warning(f"Could not parse date: {date_str}")
    return None


def _clean_html(html_str: str) -> str:
    """Strip HTML tags from a string."""
    if not html_str:
        return ""
    return re.sub(r"<[^>]+>", " ", html_str).strip()


def _extract_funding_from_description(desc: str) -> tuple[Optional[float], Optional[float]]:
    """Try to extract total funding and max per award from description text."""
    total = None
    per_award = None
    if not desc:
        return total, per_award

    # Match patterns like "$24,000,000" or "$3 million"
    money_pattern = r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion))?'
    matches = re.findall(money_pattern, desc, re.IGNORECASE)

    for match in matches:
        value = match.replace('$', '').replace(',', '').strip()
        multiplier = 1
        if 'million' in value.lower():
            value = re.sub(r'\s*million\s*', '', value, flags=re.IGNORECASE)
            multiplier = 1_000_000
        elif 'billion' in value.lower():
            value = re.sub(r'\s*billion\s*', '', value, flags=re.IGNORECASE)
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


def _infer_categories(opp_data: dict) -> list[dict]:
    """Infer technology/activity categories from opportunity data."""
    categories = []
    desc = (opp_data.get("ShortDescription") or "").lower()
    name = (opp_data.get("SolicitationName") or "").lower()
    combined = f"{name} {desc}"

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


def _infer_eligibility_rules(opp_data: dict) -> list[dict]:
    """Infer basic eligibility rules from opportunity data."""
    rules = []
    desc = (opp_data.get("ShortDescription") or "").lower()

    # All NYSERDA opportunities are NY-focused
    rules.append({
        "rule_type": "geography",
        "rule_key": "state",
        "rule_value": "NY",
        "rule_operator": "equals",
        "is_hard_requirement": True,
        "source": "NYSERDA program scope",
        "confidence": 1.0,
    })

    # Check for cost share mentions
    cost_share_match = re.search(r'(\d+)%\s*cost[- ]?share', desc)
    if cost_share_match:
        rules.append({
            "rule_type": "cost_share",
            "rule_key": "min_cost_share_pct",
            "rule_value": cost_share_match.group(1),
            "rule_operator": "gte",
            "is_hard_requirement": True,
            "source": "solicitation description",
            "source_text": cost_share_match.group(0),
            "confidence": 0.9,
        })

    # Check for applicant type restrictions
    if "public sector" in desc or "municipalities" in desc or "municipal" in desc:
        rules.append({
            "rule_type": "applicant",
            "rule_key": "applicant_type",
            "rule_value": "public_sector",
            "rule_operator": "in",
            "is_hard_requirement": True,
            "source": "solicitation description",
            "confidence": 0.8,
        })
    if "hospital" in desc:
        rules.append({
            "rule_type": "applicant",
            "rule_key": "applicant_type",
            "rule_value": "hospital",
            "rule_operator": "in",
            "is_hard_requirement": True,
            "source": "solicitation description",
            "confidence": 0.8,
        })
    if "labor organization" in desc or "apprenticeship" in desc:
        rules.append({
            "rule_type": "applicant",
            "rule_key": "applicant_type",
            "rule_value": "labor_organization",
            "rule_operator": "in",
            "is_hard_requirement": True,
            "source": "solicitation description",
            "confidence": 0.8,
        })
    if "retailer" in desc and "contractor" in desc:
        rules.append({
            "rule_type": "applicant",
            "rule_key": "applicant_type",
            "rule_value": "retailer_contractor",
            "rule_operator": "in",
            "is_hard_requirement": True,
            "source": "solicitation description",
            "confidence": 0.8,
        })

    return rules


class FundingAPIAdapter(BaseAdapter):
    """Ingests current funding opportunities from NYSERDA's native JSON API."""

    source_name = "nyserda_funding_api"
    source_url = settings.nyserda_funding_api_url
    source_type = "api"
    authority_rank = 2  # High authority, second only to formal solicitation docs

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}

        # Record ingestion run
        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            # Fetch from API
            data = self.fetch_json(self.source_url)
            raw_json = json.dumps(data)
            content_hash = self.compute_hash(raw_json)

            # Update source record
            source = db.query(Source).filter_by(name=self.source_name).first()
            if not source:
                source = Source(
                    name=self.source_name,
                    url=self.source_url,
                    source_type=self.source_type,
                    authority_rank=self.authority_rank,
                    description="NYSERDA native JSON API for current funding opportunities",
                    update_frequency="real-time",
                )
                db.add(source)

            source.last_fetched_at = self.now_utc()
            source.fetch_status = "success"
            source.content_hash = content_hash
            db.commit()

            # Parse opportunities from grouped sections
            sections = data.get("FundingOpportunities", [])
            seen_numbers = set()

            for section in sections:
                for opp_data in section.get("FundingOpportunities", []):
                    try:
                        result = self._process_opportunity(db, opp_data)
                        stats[result] += 1
                        sol_num = opp_data.get("SolicitationNumber", "")
                        seen_numbers.add(sol_num)
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"Error processing opportunity: {e}", exc_info=True)

            # Count totals
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
        """Process a single opportunity from the API. Returns 'added', 'updated', or 'unchanged'."""
        sol_num = data.get("SolicitationNumber", "").strip()
        if not sol_num:
            logger.warning("Skipping opportunity with no solicitation number")
            return "errors"

        content_hash = self.compute_hash(json.dumps(data, sort_keys=True))

        existing = db.query(Opportunity).filter_by(solicitation_number=sol_num).first()

        if existing:
            if existing.content_hash == content_hash:
                existing.last_verified_at = self.now_utc()
                db.commit()
                return "unchanged"
            # Detect changes
            self._detect_changes(db, existing, data)
            self._update_opportunity(db, existing, data, content_hash)
            return "updated"

        # New opportunity
        self._create_opportunity(db, data, content_hash)
        # Record as new
        db.add(ChangeEvent(
            entity_type="opportunity",
            entity_id=sol_num,
            entity_name=data.get("SolicitationName"),
            change_type="new",
            source_name=self.source_name,
        ))
        db.commit()
        return "added"

    def _create_opportunity(self, db: Session, data: dict, content_hash: str):
        """Create a new opportunity from API data."""
        sol_num = data["SolicitationNumber"].strip()
        total_funding, max_per_award = _extract_funding_from_description(
            data.get("ShortDescription", "")
        )

        # Determine overall status from rounds
        rounds = data.get("SolicitationRounds", [])
        has_open = any(r.get("Status") == "Open" for r in rounds)
        status = "open" if has_open else "closed"

        opp = Opportunity(
            solicitation_number=sol_num,
            name=data.get("SolicitationName", ""),
            solicitation_type=data.get("SolicitationCategory"),
            solicitation_category=data.get("SolicitationCategory"),
            status=status,
            enrollment_type=data.get("SolicitationType"),
            short_description=data.get("ShortDescription"),
            total_funding=total_funding,
            max_per_award=max_per_award,
            concept_paper_required=data.get("Conceptpaper", False),
            salesforce_id=data.get("SolicitationID"),
            detail_page_url=data.get("DetailPageLink"),
            portal_url=data.get("SalesforceLink"),
            revision_date=data.get("RevisedDate"),
            revision_notes=data.get("RevisedNotes"),
            due_date_display=_clean_html(data.get("DueDateString", "")),
            manual_submission_only=data.get("ManualSubmissionOnly", False),
            ny_green_bank=data.get("NYGreenBankRFP", False),
            source_url=self.source_url,
            source_name=self.source_name,
            content_hash=content_hash,
            first_seen_at=self.now_utc(),
            last_verified_at=self.now_utc(),
        )
        db.add(opp)
        db.flush()

        # Add rounds
        for round_data in rounds:
            db.add(OpportunityRound(
                opportunity_id=opp.id,
                round_number=round_data.get("Round", ""),
                status=round_data.get("Status", ""),
                due_date=_parse_date(round_data.get("DueDate", "")),
                concept_paper_due_date=_parse_date(round_data.get("ConceptPaperDueDate", "")),
            ))

        # Add contacts
        for contact_data in data.get("SolicitationContacts", []):
            db.add(OpportunityContact(
                opportunity_id=opp.id,
                name=contact_data.get("Name"),
                email=contact_data.get("Email"),
                phone=contact_data.get("Phone"),
                sequence=contact_data.get("Sequence"),
            ))

        # Add documents
        for doc_data in data.get("AssociatedDocuments", []):
            db.add(OpportunityDocument(
                opportunity_id=opp.id,
                document_name=doc_data.get("DocumentName", ""),
                document_url=doc_data.get("DocumentLink", ""),
                document_sequence=doc_data.get("DocumentSequence"),
            ))

        # Infer and add categories
        for cat_data in _infer_categories(data):
            db.add(OpportunityCategory(
                opportunity_id=opp.id,
                **cat_data,
            ))

        # Infer and add eligibility rules
        for rule_data in _infer_eligibility_rules(data):
            db.add(EligibilityRule(
                opportunity_id=opp.id,
                **rule_data,
            ))

        db.commit()

    def _update_opportunity(self, db: Session, opp: Opportunity, data: dict, content_hash: str):
        """Update an existing opportunity with new data."""
        total_funding, max_per_award = _extract_funding_from_description(
            data.get("ShortDescription", "")
        )

        rounds = data.get("SolicitationRounds", [])
        has_open = any(r.get("Status") == "Open" for r in rounds)

        opp.name = data.get("SolicitationName", opp.name)
        opp.enrollment_type = data.get("SolicitationType", opp.enrollment_type)
        opp.short_description = data.get("ShortDescription", opp.short_description)
        opp.status = "open" if has_open else "closed"
        opp.total_funding = total_funding or opp.total_funding
        opp.max_per_award = max_per_award or opp.max_per_award
        opp.concept_paper_required = data.get("Conceptpaper", opp.concept_paper_required)
        opp.revision_date = data.get("RevisedDate", opp.revision_date)
        opp.revision_notes = data.get("RevisedNotes", opp.revision_notes)
        opp.due_date_display = _clean_html(data.get("DueDateString", ""))
        opp.content_hash = content_hash
        opp.last_verified_at = self.now_utc()

        # Replace rounds
        db.query(OpportunityRound).filter_by(opportunity_id=opp.id).delete()
        for round_data in rounds:
            db.add(OpportunityRound(
                opportunity_id=opp.id,
                round_number=round_data.get("Round", ""),
                status=round_data.get("Status", ""),
                due_date=_parse_date(round_data.get("DueDate", "")),
                concept_paper_due_date=_parse_date(round_data.get("ConceptPaperDueDate", "")),
            ))

        # Replace contacts
        db.query(OpportunityContact).filter_by(opportunity_id=opp.id).delete()
        for contact_data in data.get("SolicitationContacts", []):
            db.add(OpportunityContact(
                opportunity_id=opp.id,
                name=contact_data.get("Name"),
                email=contact_data.get("Email"),
                phone=contact_data.get("Phone"),
                sequence=contact_data.get("Sequence"),
            ))

        # Replace documents
        db.query(OpportunityDocument).filter_by(opportunity_id=opp.id).delete()
        for doc_data in data.get("AssociatedDocuments", []):
            db.add(OpportunityDocument(
                opportunity_id=opp.id,
                document_name=doc_data.get("DocumentName", ""),
                document_url=doc_data.get("DocumentLink", ""),
                document_sequence=doc_data.get("DocumentSequence"),
            ))

        db.commit()

    def _detect_changes(self, db: Session, existing: Opportunity, new_data: dict):
        """Detect and record changes between existing and new data."""
        sol_num = existing.solicitation_number

        # Check status change
        rounds = new_data.get("SolicitationRounds", [])
        has_open = any(r.get("Status") == "Open" for r in rounds)
        new_status = "open" if has_open else "closed"
        if existing.status != new_status:
            db.add(ChangeEvent(
                entity_type="opportunity",
                entity_id=sol_num,
                entity_name=existing.name,
                change_type="status_change",
                field_name="status",
                old_value=existing.status,
                new_value=new_status,
                source_name=self.source_name,
            ))

        # Check revision date change
        new_rev = new_data.get("RevisedDate", "")
        if new_rev and new_rev != (existing.revision_date or ""):
            db.add(ChangeEvent(
                entity_type="opportunity",
                entity_id=sol_num,
                entity_name=existing.name,
                change_type="revision",
                field_name="revision_date",
                old_value=existing.revision_date,
                new_value=new_rev,
                source_name=self.source_name,
            ))

        # Check name change
        new_name = new_data.get("SolicitationName", "")
        if new_name and new_name != existing.name:
            db.add(ChangeEvent(
                entity_type="opportunity",
                entity_id=sol_num,
                entity_name=existing.name,
                change_type="field_change",
                field_name="name",
                old_value=existing.name,
                new_value=new_name,
                source_name=self.source_name,
            ))

        db.commit()
