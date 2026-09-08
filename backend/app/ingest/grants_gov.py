"""Grants.gov API adapter for federal funding opportunities.

Uses the legacy public API at api.grants.gov which requires NO authentication.
Field names verified against actual API responses (2026-08):
  Search hits: id, number, title, agencyCode, agency, openDate, closeDate, oppStatus, docType, cfdaList
  Response wrapper: {"data": {"hitCount": N, "oppHits": [...]}}
  Detail wrapper: {"data": {..., "synopsis": {...}}}
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
    OpportunityRound,
    OpportunityCategory,
    EligibilityRule,
)
from app.models.source import ChangeEvent, IngestionRun, Source
from app.engine.energy_filter import is_energy_innovation_relevant

logger = logging.getLogger(__name__)

# Map Grants.gov agencyCode to our display names
AGENCY_MAP = {
    # DOE sub-agencies
    "DOE": "DOE", "DOE-GFO": "DOE", "DOE-EERE": "DOE",
    "DOE-ARPAE": "ARPA-E", "DOE-NETL": "DOE", "DOE-SC": "DOE",
    "DOE-ID": "DOE", "DOE-OE": "DOE", "DOE-HQ": "DOE",
    "DOE-NNSA": "DOE", "DOE-EM": "DOE", "DOE-OCED": "DOE",
    "DOE-MESC": "DOE", "DOE-01": "DOE",
    "PAMS": "DOE", "PAMS-SC": "DOE",  # Office of Science uses PAMS
    # Other federal
    "EPA": "EPA", "NSF": "NSF", "NASA": "NASA",
    "USDA": "USDA", "USDA-NIFA": "USDA", "USDA-RBCS": "USDA",
    "USDA-RUS": "USDA", "USDA-FS": "USDA",
    "DOT": "DOT", "DOT-FHWA": "DOT", "DOT-FTA": "DOT",
    "DOT-FRA": "DOT", "DOT-MA": "DOT",
    "DOD": "DOD", "DOD-AFRL": "DOD", "DOD-ONR": "DOD", "DOD-DARPA-DSO": "DOD",
    "DOC-EDA": "EDA", "DOC": "DOC", "DOC-NIST": "NIST",
    "SBA": "SBA",
}

# Grants.gov agency codes to search - many agencies require sub-agency codes!
# Verified: parent codes often return 0, but sub-agencies return results.
GRANTS_GOV_AGENCIES = [
    # DOE sub-agencies (EERE/GFO, ARPA-E, NETL, Idaho/Nuclear, Office of Science, HQ)
    "DOE-GFO", "DOE-ARPAE", "DOE-NETL", "DOE-ID", "DOE-OE",
    "DOE-HQ", "DOE-NNSA", "DOE-EM", "DOE-01", "DOE-SC",
    "PAMS", "PAMS-SC",  # DOE Office of Science uses PAMS parent code
    # EPA, NSF work with parent codes
    "EPA", "NSF",
    # USDA sub-agencies (parent code returns 0)
    "USDA-NIFA", "USDA-RBCS", "USDA-RUS", "USDA-FS",
    # DOT sub-agencies (parent code returns 0)
    "DOT-FHWA", "DOT-FTA", "DOT-FRA", "DOT-MA", "DOT-OSDBU", "DOT-RITA",
    # DOC and SBA work with parent codes
    "DOC",   # EDA tech hubs, NIST
    "SBA",   # SBIR aggregation
]

# Agencies whose mandates are inherently energy-focused (no secondary filter needed)
ENERGY_FOCUSED_AGENCIES = {"DOE", "ARPA-E"}

# Energy-innovation terms for filtering non-energy-focused agency results
ENERGY_RELEVANCE_TERMS = {
    "clean energy", "renewable energy", "solar energy", "wind energy", "solar",
    "photovoltaic", "geothermal", "battery", "energy storage", "grid",
    "smart grid", "microgrid", "hydrogen", "fuel cell", "electrolysis",
    "carbon capture", "carbon sequestration", "ccs", "ccus", "direct air capture",
    "decarbonization", "net zero", "zero emission", "low carbon",
    "building energy", "energy efficiency", "heat pump", "weatherization",
    "electric vehicle", "ev charging", "electrification",
    "offshore wind", "wind turbine", "wind power",
    "nuclear", "advanced reactor", "small modular reactor",
    "biofuel", "bioenergy", "biomass", "biogas", "renewable natural gas",
    "sustainable fuel", "sustainable aviation fuel",
    "power grid", "power system", "electricity", "transmission",
    "greenhouse gas", "ghg", "climate change", "climate mitigation",
    "energy innovation", "clean technology", "cleantech", "energy transition",
    "long duration storage", "pumped hydro", "compressed air energy",
    "industrial decarbonization", "industrial emissions", "process heat",
    "combined heat and power", "chp", "cogeneration",
    "distributed energy", "demand response", "energy management",
}



def _parse_date(date_str: str) -> Optional[datetime]:
    if not date_str or not date_str.strip():
        return None
    for fmt in ["%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def _clean_html(html_str: str) -> str:
    if not html_str:
        return ""
    return re.sub(r"<[^>]+>", " ", html_str).strip()


def _infer_categories(desc: str, name: str) -> list[dict]:
    """Infer technology/activity categories from description text."""
    categories = []
    combined = f"{name} {desc}".lower()

    tech_keywords = {
        "solar": "Solar", "photovoltaic": "Solar", "pv ": "Solar",
        "wind": "Wind", "offshore wind": "Offshore Wind",
        "battery": "Energy Storage", "energy storage": "Energy Storage",
        "heat pump": "Building Electrification", "building electrification": "Building Electrification",
        "hvac": "Building Electrification", "building envelope": "Building Electrification",
        "grid": "Grid Modernization", "transmission": "Grid Modernization",
        "hydrogen": "Hydrogen & Alternative Fuels", "fuel cell": "Hydrogen & Alternative Fuels",
        "carbon capture": "Carbon Management", "ccus": "Carbon Management",
        "electric vehicle": "Clean Transportation", "ev charging": "Clean Transportation",
        "geothermal": "Thermal Energy Networks",
        "nuclear": "Nuclear", "advanced reactor": "Nuclear",
        "cybersecurity": "Cybersecurity",
        "water": "Water", "desalination": "Water",
        "air quality": "Environmental Research", "emissions": "Environmental Research",
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
        "demonstration": "Demonstration", "research": "Research",
        "product development": "Product Development", "feasibility": "Feasibility Study",
        "training": "Training", "technical assistance": "Technical Assistance",
        "deployment": "Deployment", "scale-up": "Scale-up",
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


class GrantsGovAdapter(BaseAdapter):
    """Ingests federal funding opportunities from Grants.gov public API."""

    source_name = "grants_gov"
    source_url = "https://api.grants.gov/v1/api"
    source_type = "api"
    authority_rank = 2

    def _post_json(self, url: str, payload: dict) -> dict:
        self._rate_limit()
        response = self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}

        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            # Register source
            source = db.query(Source).filter_by(name=self.source_name).first()
            if not source:
                source = Source(
                    name=self.source_name, url=self.source_url,
                    source_type=self.source_type, authority_rank=self.authority_rank,
                    description="Grants.gov federal funding opportunities",
                    update_frequency="daily",
                )
                db.add(source)
                db.commit()

            source.last_fetched_at = self.now_utc()

            search_url = f"{self.source_url}/search2"
            detail_url = f"{self.source_url}/fetchOpportunity"
            seen_ids = set()

            # Search each agency separately (Grants.gov uses top-level codes)
            for agency_code in GRANTS_GOV_AGENCIES:
                logger.info(f"[{self.source_name}] Searching agency: {agency_code}")
                start = 0

                while True:
                    payload = {
                        "agencies": agency_code,
                        "oppStatuses": "posted|forecasted",
                        "rows": 25,
                        "startRecordNum": start,
                        "sortBy": "openDate|desc",
                    }

                    resp = self._post_json(search_url, payload)
                    # Response is wrapped: {"data": {"hitCount": N, "oppHits": [...]}}
                    data = resp.get("data", resp)
                    total = data.get("hitCount", 0)
                    hits = data.get("oppHits", [])

                    if not hits:
                        logger.info(f"[{self.source_name}] {agency_code}: {total} total, page empty at {start}")
                        break

                    for hit in hits:
                        try:
                            result = self._process_hit(db, hit, detail_url)
                            stats[result] += 1
                            seen_ids.add(hit.get("id"))
                        except Exception as e:
                            stats["errors"] += 1
                            logger.error(f"Error processing hit {hit.get('id')}: {e}")

                    start += len(hits)
                    if start >= total:
                        break

                logger.info(f"[{self.source_name}] {agency_code}: processed {start} of {total}")

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

    def _process_hit(self, db: Session, hit: dict, detail_url: str) -> str:
        """Process a single search hit. Returns 'added', 'updated', or 'unchanged'."""
        # Actual field names from Grants.gov API (verified):
        #   id, number, title, agencyCode, agency, openDate, closeDate, oppStatus, cfdaList
        grants_id = str(hit["id"])
        sol_num = hit.get("number", "") or ""
        hit_title = hit.get("title", "") or ""
        hit_agency_code = hit.get("agencyCode", "") or ""
        hit_status_raw = (hit.get("oppStatus", "") or "").upper()

        # Compute hash from search hit for quick change detection
        hit_hash = self.compute_hash(json.dumps(hit, sort_keys=True))

        # Check if already exists
        existing = db.query(Opportunity).filter(
            (Opportunity.external_id == grants_id) |
            (Opportunity.solicitation_number == sol_num)
        ).first()

        if existing and existing.content_hash == hit_hash:
            existing.last_verified_at = self.now_utc()
            db.commit()
            return "unchanged"

        # Fetch full details
        try:
            resp = self._post_json(detail_url, {"opportunityId": int(hit["id"])})
            detail = resp.get("data", resp)
        except Exception as e:
            logger.warning(f"Failed to fetch detail for {grants_id}: {e}, using search data only")
            detail = {}

        synopsis = detail.get("synopsis", {}) or {}

        # Map status
        status_map = {"POSTED": "open", "FORECASTED": "draft", "CLOSED": "closed", "ARCHIVED": "closed"}
        status = status_map.get(hit_status_raw, "closed")

        # Map agency
        agency = AGENCY_MAP.get(hit_agency_code, hit_agency_code.split("-")[0] if "-" in hit_agency_code else hit_agency_code)

        # Solicitation type from funding instrument
        instr = synopsis.get("fundingInstrumentCodes", "") or ""
        if "G" in instr:
            sol_type = "Grant"
        elif "CA" in instr:
            sol_type = "Cooperative Agreement"
        else:
            sol_type = "NOFO"

        # Description
        desc = _clean_html(synopsis.get("synopsisDesc", ""))

        # Energy-innovation relevance and negative exclusion filter
        is_valid, _ = is_energy_innovation_relevant(
            title=hit_title,
            text_content=desc,
            agency=agency
        )
        if not is_valid:
            return "unchanged"  # Skip non-energy opportunities

        # Cost share
        cost_share_pct = None
        cs_desc = synopsis.get("costSharingDescription", "") or ""
        if cs_desc:
            m = re.search(r"(\d+)\s*%", cs_desc)
            if m:
                cost_share_pct = float(m.group(1))

        # Funding amounts
        total_funding = synopsis.get("estimatedTotalProgramFunding")
        max_award = synopsis.get("awardCeiling")
        # These can come as strings or ints
        if isinstance(total_funding, str):
            try: total_funding = float(total_funding.replace(",", ""))
            except: total_funding = None
        if isinstance(max_award, str):
            try: max_award = float(max_award.replace(",", ""))
            except: max_award = None

        # Build detail URL
        detail_page = f"https://www.grants.gov/search-results-detail/{hit['id']}"

        # Title from detail or search hit
        title = detail.get("opportunityTitle") or detail.get("title") or hit_title

        if existing:
            # Update existing record
            if existing.status != status:
                db.add(ChangeEvent(
                    entity_type="opportunity", entity_id=existing.solicitation_number,
                    entity_name=existing.name, change_type="status_change",
                    field_name="status", old_value=existing.status, new_value=status,
                    source_name=self.source_name,
                ))
                existing.status = status

            existing.name = title or existing.name
            existing.short_description = desc or existing.short_description
            existing.total_funding = total_funding or existing.total_funding
            existing.max_per_award = max_award or existing.max_per_award
            existing.content_hash = hit_hash
            existing.last_verified_at = self.now_utc()
            db.commit()
            return "updated"

        # Create new record
        opp = Opportunity(
            solicitation_number=sol_num or f"GRANTS-{grants_id}",
            name=title,
            solicitation_type=sol_type,
            status=status,
            enrollment_type="Due Date",
            short_description=desc[:5000] if desc else "",
            total_funding=total_funding,
            max_per_award=max_award,
            cost_share_pct=cost_share_pct,
            detail_page_url=detail_page,
            agency=agency,
            agency_code=hit_agency_code,
            jurisdiction="federal",
            external_id=grants_id,
            source_url=self.source_url,
            source_name=self.source_name,
            content_hash=hit_hash,
            first_seen_at=self.now_utc(),
            last_verified_at=self.now_utc(),
        )
        db.add(opp)
        db.flush()

        # Round with deadline
        close_date = _parse_date(hit.get("closeDate", "")) or _parse_date(synopsis.get("responseDate", ""))
        if close_date:
            db.add(OpportunityRound(
                opportunity_id=opp.id, round_number="1",
                status=status, due_date=close_date,
            ))

        # Contact
        c_name = synopsis.get("agencyContactName")
        c_email = synopsis.get("agencyContactEmail")
        c_phone = synopsis.get("agencyContactPhone")
        if c_name or c_email:
            db.add(OpportunityContact(
                opportunity_id=opp.id, name=c_name or "", email=c_email or "", phone=c_phone or "",
            ))

        # Categories from description inference
        for cat in _infer_categories(desc, title):
            db.add(OpportunityCategory(opportunity_id=opp.id, **cat))

        # Eligibility rules
        elig_desc = (synopsis.get("applicantEligibilityDesc", "") or "").lower()
        if "sbir" in elig_desc or "sttr" in elig_desc or "small business" in elig_desc:
            db.add(EligibilityRule(
                opportunity_id=opp.id, rule_type="applicant",
                rule_key="applicant_type", rule_value="small_business",
                rule_operator="in", is_hard_requirement=True,
                source="grants.gov eligibility desc",
            ))

        db.add(ChangeEvent(
            entity_type="opportunity", entity_id=opp.solicitation_number,
            entity_name=title, change_type="new", source_name=self.source_name,
        ))
        db.commit()
        return "added"
