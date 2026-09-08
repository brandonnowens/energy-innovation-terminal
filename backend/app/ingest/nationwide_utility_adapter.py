"""Nationwide Energy-Innovation Utility Expansion Ingestion Adapter.

Ingests all 50 U.S. states + DC ranked sequentially by latest available GSP/GDP,
orchestrating complete entity ingestion:
Organization (Holding Companies & Operating Utilities) -> Program -> Opportunity -> Award -> Recipient
Maintains persistent resumable manifest at backend/data/utility_expansion_manifest.json.
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy import create_engine, select, func, and_
from sqlalchemy.orm import sessionmaker, Session

from app.database import SessionLocal
import app.models  # Register all models for SQLAlchemy
from app.models.organization import Organization
from app.models.opportunity_organization import OpportunityOrganization
from app.models.program import Program
from app.models.opportunity import (
    Opportunity, OpportunityCategory, EligibilityRule, OpportunityRestriction
)
from app.models.award import Award
from app.models.recipient import Recipient


from app.ingest.state_utility_registry import (
    STATE_GDP_RANKING, STATE_UTILITY_DATA, HOLDING_COMPANIES, get_ordered_states
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MANIFEST_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "utility_expansion_manifest.json")


class NationwideUtilityAdapter:
    """End-to-end autonomous ingestion adapter for nationwide utility expansion."""

    def __init__(self, db_session: Optional[Session] = None):
        if db_session:
            self.session = db_session
        else:
            self.session = SessionLocal()

        self.manifest = self._load_manifest()


    def _load_manifest(self) -> Dict[str, Any]:
        """Load or initialize the JSON progress manifest."""
        if os.path.exists(MANIFEST_PATH):
            try:
                with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading manifest: {e}, initializing new manifest")
        return {
            "version": "1.0.0",
            "last_updated": datetime.utcnow().isoformat(),
            "total_states": len(STATE_GDP_RANKING),
            "completed_states_count": 0,
            "states": {},
            "holding_companies_ingested": False,
            "summary_metrics": {
                "total_utilities_ingested": 0,
                "total_programs_ingested": 0,
                "total_opportunities_ingested": 0,
                "total_awards_ingested": 0,
                "total_recipients_ingested": 0,
            }
        }

    def _save_manifest(self):
        """Persist the manifest to disk."""
        self.manifest["last_updated"] = datetime.utcnow().isoformat()
        self.manifest["completed_states_count"] = sum(
            1 for s in self.manifest["states"].values() if s.get("status") == "completed"
        )
        os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=2)

    def ingest_holding_companies(self) -> Dict[str, int]:
        """Ingest master holding companies as parent organizations."""
        logger.info("Ingesting Master Holding Companies...")
        holding_map = {}
        for key, info in HOLDING_COMPANIES.items():
            existing = self.session.execute(
                select(Organization).where(Organization.name == info["name"])
            ).scalar_one_or_none()

            if not existing:
                org = Organization(
                    name=info["name"],
                    org_type="holding_company",
                    domain=info.get("domain"),
                    website=f"https://www.{info.get('domain')}" if info.get("domain") else None,
                    state=info.get("state"),
                    city=info.get("city"),
                    country="US",
                    geographic_scope="National / Multi-State",
                    data_provenance="observed",
                    is_verified=True,
                    description=f"Electric and natural gas utility holding company headquartered in {info.get('city')}, {info.get('state')}."
                )
                self.session.add(org)
                self.session.flush()
                holding_map[key] = org.id
            else:
                holding_map[key] = existing.id

        self.session.commit()
        self.manifest["holding_companies_ingested"] = True
        self._save_manifest()
        return holding_map

    def ingest_state(self, state_code: str, holding_map: Dict[str, int]) -> Dict[str, Any]:
        """Ingest a single state's utilities, programs, opportunities, awards, and awardees."""
        state_info = STATE_UTILITY_DATA.get(state_code)
        if not state_info:
            logger.warning(f"No state data found for {state_code}")
            return {"status": "skipped", "error": "No data"}

        state_name = state_info.get("state_name", state_code)
        gdp_rank = state_info.get("rank", 99)
        gdp_billions = state_info.get("gdp_billions", 0)

        logger.info(f"=== Processing Rank {gdp_rank:2d}: {state_code} - {state_name} (${gdp_billions}B GSP) ===")

        utils_ingested = 0
        programs_ingested = 0
        opps_ingested = 0
        awards_ingested = 0
        recipients_ingested = 0

        for u in state_info.get("utilities", []):
            u_name = u["name"]
            parent_key = u.get("parent_holding_company")
            parent_id = holding_map.get(parent_key) if parent_key else None

            # 1. Organization
            org = self.session.execute(
                select(Organization).where(Organization.name == u_name)
            ).scalar_one_or_none()

            if not org:
                org = Organization(
                    name=u_name,
                    org_type=u.get("org_type", "utility"),
                    parent_org_id=parent_id,
                    website=u.get("website"),
                    domain=u.get("domain"),
                    city=u.get("city"),
                    state=u.get("state", state_code),
                    zip_code=u.get("zip_code"),
                    country="US",
                    geographic_scope="State / Regional",
                    description=u.get("description"),
                    logo_url=f"https://logo.clearbit.com/{u.get('logo_domain')}" if u.get("logo_domain") else None,
                    founded_year=u.get("founded_year"),
                    data_provenance="observed",
                    is_verified=True,
                )
                self.session.add(org)
                self.session.flush()
                utils_ingested += 1
            else:
                # Update parent if missing
                if parent_id and not org.parent_org_id:
                    org.parent_org_id = parent_id
                    self.session.flush()

            # 2. Programs
            program_id_map = {}
            for prog_data in u.get("programs", []):
                prog_name = prog_data["name"]
                prog = self.session.execute(
                    select(Program).where(Program.name == prog_name)
                ).scalar_one_or_none()

                if not prog:
                    prog = Program(
                        name=prog_name,
                        program_type=prog_data.get("program_type", "innovation"),
                        description=prog_data.get("description"),
                        url=prog_data.get("url"),
                        active=prog_data.get("active", True),
                        target_stage=prog_data.get("target_stage", "demonstration"),
                    )
                    self.session.add(prog)
                    self.session.flush()
                    programs_ingested += 1
                program_id_map[prog_name] = prog.id

            default_program_id = list(program_id_map.values())[0] if program_id_map else None

            # 3. Opportunities
            opp_id_map = {}
            for opp_data in u.get("opportunities", []):
                sol_num = opp_data["solicitation_number"]
                opp = self.session.execute(
                    select(Opportunity).where(Opportunity.solicitation_number == sol_num)
                ).scalar_one_or_none()

                if not opp:
                    opp = Opportunity(
                        solicitation_number=sol_num,
                        name=opp_data["name"],
                        solicitation_type=opp_data.get("solicitation_type", "RFP"),
                        status=opp_data.get("status", "open"),
                        funding_type=opp_data.get("funding_type", "grant"),
                        total_funding=opp_data.get("total_funding", 0.0),
                        max_per_award=opp_data.get("max_per_award", 0.0),
                        short_description=opp_data.get("short_description"),
                        service_territory=opp_data.get("service_territory"),
                        utility_program_type=opp_data.get("utility_program_type", "Innovation RFP"),
                        procurement_portal_url=opp_data.get("procurement_portal_url"),
                        program_id=default_program_id,
                        agency=u_name,
                        agency_code=u.get("short_name", u_name[:10]),
                        jurisdiction=state_code,
                        org_type="utility",
                        year=opp_data.get("year", 2026),
                        keywords=opp_data.get("keywords"),
                        data_provenance="observed",
                        funding_provenance="ratepayer_innovation_fund",
                        geographic_scope="Statewide / Regional",
                    )
                    self.session.add(opp)
                    self.session.flush()
                    opps_ingested += 1

                    # OpportunityOrganization link
                    opp_org = OpportunityOrganization(
                        opportunity_id=opp.id,
                        organization_id=org.id,
                        role="sponsor"
                    )
                    self.session.add(opp_org)

                    # OpportunityCategory tags
                    for tech in opp_data.get("technologies", []):
                        cat = OpportunityCategory(
                            opportunity_id=opp.id,
                            category_type="technology",
                            category_value=tech,
                            source="observed",
                            confidence=1.0
                        )
                        self.session.add(cat)

                    for sec in opp_data.get("sectors", []):
                        cat = OpportunityCategory(
                            opportunity_id=opp.id,
                            category_type="sector",
                            category_value=sec,
                            source="observed",
                            confidence=1.0
                        )
                        self.session.add(cat)

                    for f_type in opp_data.get("fuels", []):
                        cat = OpportunityCategory(
                            opportunity_id=opp.id,
                            category_type="fuel_type",
                            category_value=f_type,
                            source="observed",
                            confidence=1.0
                        )
                        self.session.add(cat)

                opp_id_map[sol_num] = opp.id

            # 4. Awards & Recipients
            for awd_data in u.get("awards", []):
                ext_id = awd_data["external_award_id"]
                sol_num = awd_data.get("opportunity_sol_num")
                matched_opp_id = opp_id_map.get(sol_num)

                # Upsert Recipient
                rec_name = awd_data["recipient_name"]
                rec = self.session.execute(
                    select(Recipient).where(Recipient.name == rec_name)
                ).scalar_one_or_none()

                if not rec:
                    rec = Recipient(
                        name=rec_name,
                        recipient_type=awd_data.get("recipient_type", "company"),
                        headquarters_city=awd_data.get("recipient_city"),
                        headquarters_state=awd_data.get("recipient_state", state_code),
                        headquarters_country="US",
                        latitude=awd_data.get("latitude"),
                        longitude=awd_data.get("longitude"),
                        geocode_precision="city_verified",
                        total_funding_received=awd_data.get("award_amount", 0.0),
                        total_awards_count=1,
                        latest_award_year=awd_data.get("year", 2025)
                    )
                    self.session.add(rec)
                    self.session.flush()
                    recipients_ingested += 1
                else:
                    rec.total_funding_received = (rec.total_funding_received or 0.0) + (awd_data.get("award_amount") or 0.0)
                    rec.total_awards_count = (rec.total_awards_count or 0) + 1
                    if not rec.latitude and awd_data.get("latitude"):
                        rec.latitude = awd_data.get("latitude")
                        rec.longitude = awd_data.get("longitude")

                # Upsert Award
                awd = self.session.execute(
                    select(Award).where(Award.external_award_id == ext_id)
                ).scalar_one_or_none()

                if not awd:
                    awd = Award(
                        external_award_id=ext_id,
                        opportunity_id=matched_opp_id,
                        recipient_name=rec_name,
                        recipient_type=awd_data.get("recipient_type", "company"),
                        recipient_city=awd_data.get("recipient_city"),
                        recipient_state=awd_data.get("recipient_state", state_code),
                        recipient_country="US",
                        award_amount=awd_data.get("award_amount"),
                        project_title=awd_data.get("project_title"),
                        pi_name=awd_data.get("pi_name"),
                        year=awd_data.get("year", 2025),
                        agency=u_name,
                        solicitation_number=sol_num,
                        latitude=awd_data.get("latitude"),
                        longitude=awd_data.get("longitude"),
                        geocode_method="verified",
                        source_name=u_name,
                        award_type="grant" if "grant" in u_name.lower() else "contract",
                    )
                    self.session.add(awd)
                    awards_ingested += 1

        self.session.commit()

        # Update manifest for this state
        state_manifest_entry = {
            "state_code": state_code,
            "state_name": state_name,
            "rank": gdp_rank,
            "gdp_billions": gdp_billions,
            "utilities_count": len(state_info.get("utilities", [])),
            "new_utilities_added": utils_ingested,
            "new_programs_added": programs_ingested,
            "new_opportunities_added": opps_ingested,
            "new_awards_added": awards_ingested,
            "new_recipients_added": recipients_ingested,
            "completed_at": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        self.manifest["states"][state_code] = state_manifest_entry
        self.manifest["summary_metrics"]["total_utilities_ingested"] += utils_ingested
        self.manifest["summary_metrics"]["total_programs_ingested"] += programs_ingested
        self.manifest["summary_metrics"]["total_opportunities_ingested"] += opps_ingested
        self.manifest["summary_metrics"]["total_awards_ingested"] += awards_ingested
        self.manifest["summary_metrics"]["total_recipients_ingested"] += recipients_ingested
        self._save_manifest()

        logger.info(
            f"State {state_code} Complete: +{utils_ingested} orgs, +{programs_ingested} progs, "
            f"+{opps_ingested} opps, +{awards_ingested} awards, +{recipients_ingested} recipients"
        )
        return state_manifest_entry

    def run_all(self, start_rank: int = 1, end_rank: int = 51) -> Dict[str, Any]:
        """Execute nationwide expansion across all 51 jurisdictions sequentially."""
        logger.info(f"Starting Nationwide Energy-Innovation Utility Expansion (Ranks {start_rank} to {end_rank})...")
        holding_map = self.ingest_holding_companies()

        ordered_states = get_ordered_states()
        for s in ordered_states:
            rank = s["rank"]
            code = s["state_code"]
            if rank < start_rank or rank > end_rank:
                continue

            try:
                self.ingest_state(code, holding_map)
            except Exception as e:
                logger.error(f"Error processing state {code} (Rank {rank}): {e}", exc_info=True)
                self.manifest["states"][code] = {
                    "state_code": code,
                    "rank": rank,
                    "status": "error",
                    "error_message": str(e),
                    "failed_at": datetime.utcnow().isoformat()
                }
                self._save_manifest()

        logger.info("=== Nationwide Energy-Innovation Utility Ingestion Completed! ===")
        return self.manifest
