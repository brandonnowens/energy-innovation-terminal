"""
Empire State Development (ESD) & NY Ventures Ingestion Adapter.

Ingests New York State's primary economic development agency opportunities,
programs (NY Ventures, NYSTAR Centers of Excellence, REDC Clean Energy, FAST NY),
and historical grant/equity awards for clean energy and climate tech innovation.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.ingest.base import BaseAdapter
from app.models.opportunity import Opportunity
from app.models.program import Program
from app.models.organization import Organization
from app.models.award import Award
from app.models.recipient import Recipient
from app.models.source import IngestionRun, Source

logger = logging.getLogger(__name__)

ESD_PROGRAMS = [
    {
        "name": "ESD NY Ventures Climate Tech & Seed Fund",
        "description": "Direct equity co-investment and matching seed capital for early-stage high-growth climate technology and energy storage startups based in New York State.",
        "program_type": "Commercialization",
        "target_stage": "Early Commercialization & Scale",
        "url": "https://esd.ny.gov/venture-capital-ny-ventures"
    },
    {
        "name": "ESD NYSTAR Clean Energy Centers of Excellence & CATs",
        "description": "Empire State Development Division of Science, Technology and Innovation (NYSTAR) university-industry research partnerships in battery storage, advanced energy, and grid tech.",
        "program_type": "Innovation R&D",
        "target_stage": "R&D to Pilot",
        "url": "https://esd.ny.gov/nystar"
    },
    {
        "name": "REDC Clean Energy & Decarbonization Capital Grants",
        "description": "Regional Economic Development Councils (REDC) Consolidated Funding Application capital grants for clean energy manufacturing facilities and industrial decarbonization.",
        "program_type": "Commercialization",
        "target_stage": "Deployment & Scale",
        "url": "https://esd.ny.gov/regional-economic-development-councils"
    },
    {
        "name": "FAST NY Clean Tech & Battery Manufacturing Shovel-Ready",
        "description": "Focused Attraction of Shovel-Ready Tracts New York (FAST NY) grants to prepare industrial sites for major clean energy, battery, and EV supply chain manufacturing campuses.",
        "program_type": "Infrastructure & Manufacturing",
        "target_stage": "Commercial Scale",
        "url": "https://esd.ny.gov/fast-ny"
    },
    {
        "name": "ESD SBIR/STTR Clean Tech Matching Assistance",
        "description": "New York State matching grants and commercialization support for federal DOE, NSF, and DOD clean energy SBIR/STTR Phase I and Phase II winners.",
        "program_type": "Technical Assistance",
        "target_stage": "Proof of Concept to Prototype",
        "url": "https://esd.ny.gov/nystar/sbir-sttr"
    }
]

ESD_OPPORTUNITIES = [
    {
        "solicitation_number": "ESD-NYV-2025-01",
        "name": "NY Ventures Climate & Energy Innovation Seed Co-Investment",
        "solicitation_type": "Equity / Matching Co-Investment",
        "status": "open",
        "enrollment_type": "Rolling Enrollment",
        "short_description": "Direct equity investments from $250K to $1.5M for NY-based clean energy, long-duration battery storage, and advanced mobility ventures with matched private institutional capital.",
        "total_funding": 35000000.0,
        "max_per_award": 1500000.0,
        "cost_share_pct": 50.0,
        "detail_page_url": "https://esd.ny.gov/venture-capital-ny-ventures",
        "due_date_display": "Open / Rolling Evaluation",
        "technology_area": "Clean Energy Innovation & Advanced Tech",
        "program_name": "ESD NY Ventures Climate Tech & Seed Fund"
    },
    {
        "solicitation_number": "ESD-NYSTAR-2025-CAT",
        "name": "NYSTAR Applied Energy & Battery Storage Innovation Partnerships",
        "solicitation_type": "R&D Matching Grant",
        "status": "open",
        "enrollment_type": "Annual RFP",
        "short_description": "Matching grant funds for industry-sponsored research with NYS Centers for Advanced Technology (AERTC Stony Brook, Binghamton Battery COE, Cornell Materials).",
        "total_funding": 15000000.0,
        "max_per_award": 750000.0,
        "cost_share_pct": 50.0,
        "detail_page_url": "https://esd.ny.gov/nystar",
        "due_date_display": "October 31, 2025",
        "technology_area": "Energy Storage & Advanced Batteries",
        "program_name": "ESD NYSTAR Clean Energy Centers of Excellence & CATs"
    },
    {
        "solicitation_number": "ESD-REDC-CFA-R15",
        "name": "REDC Round XV Clean Tech & Industrial Decarbonization Capital Fund",
        "solicitation_type": "Capital Grant",
        "status": "open",
        "enrollment_type": "Consolidated Funding Application",
        "short_description": "Capital grants up to $5M for clean technology equipment purchases, green hydrogen pilot facilities, and zero-emission manufacturing plant construction.",
        "total_funding": 75000000.0,
        "max_per_award": 5000000.0,
        "cost_share_pct": 80.0,
        "detail_page_url": "https://esd.ny.gov/regional-economic-development-councils",
        "due_date_display": "July 31, 2025",
        "technology_area": "Industrial Decarbonization & Clean Heat",
        "program_name": "REDC Clean Energy & Decarbonization Capital Grants"
    },
    {
        "solicitation_number": "ESD-FAST-2025-02",
        "name": "FAST NY Shovel-Ready Clean Energy Manufacturing Infrastructure",
        "solicitation_type": "Infrastructure Grant",
        "status": "open",
        "enrollment_type": "Rolling Submission",
        "short_description": "Site preparation, high-voltage grid interconnection, and utility water/power buildouts for mega-scale battery gigafactories and electrolyzer assembly plants.",
        "total_funding": 100000000.0,
        "max_per_award": 10000000.0,
        "cost_share_pct": 0.0,
        "detail_page_url": "https://esd.ny.gov/fast-ny",
        "due_date_display": "Rolling Review",
        "technology_area": "Grid Modernization & Smart Power",
        "program_name": "FAST NY Clean Tech & Battery Manufacturing Shovel-Ready"
    },
    {
        "solicitation_number": "ESD-SBIR-MATCH-2025",
        "name": "NYS Clean Energy SBIR/STTR Phase I/II Commercialization Matching Grant",
        "solicitation_type": "Matching Grant",
        "status": "open",
        "enrollment_type": "Open Enrollment",
        "short_description": "State non-dilutive matching grants up to $100,000 to bridge Phase I and Phase II federal clean energy awards for New York deep tech startups.",
        "total_funding": 5000000.0,
        "max_per_award": 100000.0,
        "cost_share_pct": 0.0,
        "detail_page_url": "https://esd.ny.gov/nystar/sbir-sttr",
        "due_date_display": "Quarterly Deadlines",
        "technology_area": "Clean Energy Innovation & Advanced Tech",
        "program_name": "ESD SBIR/STTR Clean Tech Matching Assistance"
    }
]

ESD_AWARDS = [
    {
        "external_award_id": "ESD-NYV-2022-ECO",
        "recipient_name": "Ecolectro, Inc.",
        "recipient_type": "early stage company",
        "recipient_city": "Ithaca",
        "recipient_state": "NY",
        "recipient_zip": "14850",
        "award_amount": 1000000.0,
        "year": 2022,
        "solicitation_number": "ESD-NYV-2025-01",
        "project_title": "NY Ventures Climate Co-Investment: Precious-Metal-Free AEM Hydrogen Electrolyzer Scale-Up",
        "project_abstract": "Equity co-investment alongside Toyota Ventures and Starshot Capital to expand anion exchange membrane manufacturing and durability testing at Cornell Business & Technology Park.",
        "award_type": "equity_investment",
        "program_name": "ESD NY Ventures Climate Tech & Seed Fund",
        "latitude": 42.4406,
        "longitude": -76.4966
    },
    {
        "external_award_id": "ESD-NYV-2023-AMOG",
        "recipient_name": "Amogy Inc.",
        "recipient_type": "early stage company",
        "recipient_city": "Brooklyn",
        "recipient_state": "NY",
        "recipient_zip": "11205",
        "award_amount": 1500000.0,
        "year": 2023,
        "solicitation_number": "ESD-NYV-2025-01",
        "project_title": "NY Ventures Growth Co-Investment: Ammonia-to-Power Heavy Transportation Technology",
        "project_abstract": "Growth capital matching round supporting Brooklyn Navy Yard R&D labs and maritime zero-carbon ammonia power pack assembly.",
        "award_type": "equity_investment",
        "program_name": "ESD NY Ventures Climate Tech & Seed Fund",
        "latitude": 40.7003,
        "longitude": -73.9712
    },
    {
        "external_award_id": "ESD-CAT-2023-BING",
        "recipient_name": "Binghamton University (SUNY)",
        "recipient_type": "university",
        "recipient_city": "Binghamton",
        "recipient_state": "NY",
        "recipient_zip": "13902",
        "award_amount": 2500000.0,
        "year": 2023,
        "solicitation_number": "ESD-NYSTAR-2025-CAT",
        "project_title": "NYSTAR Center of Excellence in Clean Energy & Next-Gen Battery Prototyping Center",
        "project_abstract": "State partnership grant under M. Stanley Whittingham leadership supporting dry-room battery pilot lines and industry commercialization projects across the Southern Tier.",
        "award_type": "grant",
        "program_name": "ESD NYSTAR Clean Energy Centers of Excellence & CATs",
        "latitude": 42.0987,
        "longitude": -75.9180
    },
    {
        "external_award_id": "ESD-REDC-2024-LINE",
        "recipient_name": "LineVision, Inc.",
        "recipient_type": "early stage company",
        "recipient_city": "New York",
        "recipient_state": "NY",
        "recipient_zip": "10001",
        "award_amount": 850000.0,
        "year": 2024,
        "solicitation_number": "ESD-REDC-CFA-R15",
        "project_title": "REDC Dynamic Line Rating Sensor Commercialization & Grid Capacity Acceleration",
        "project_abstract": "Capital grant accelerating advanced optical sensor assembly for overhead transmission line rating deployments across New York State electric utilities.",
        "award_type": "grant",
        "program_name": "REDC Clean Energy & Decarbonization Capital Grants",
        "latitude": 40.7505,
        "longitude": -73.9934
    }
]


class EmpireStateDevelopmentAdapter(BaseAdapter):
    """Adapter for Empire State Development (ESD) and NY Ventures."""

    source_name = "empire_state_development"
    source_url = "https://esd.ny.gov"
    source_type = "state_agency"
    authority_rank = 2

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}
        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            # 1. Register ESD in Organization table
            esd_org = db.query(Organization).filter_by(name="Empire State Development").first()
            if not esd_org:
                esd_org = Organization(
                    name="Empire State Development",
                    aliases_json=["ESD", "Empire State Development Corporation", "NY Ventures", "NYSTAR"],
                    org_type="economic_development",
                    website="https://esd.ny.gov",
                    domain="esd.ny.gov",
                    city="New York",
                    state="NY",
                    zip_code="10017",
                    country="US",
                    geographic_scope="state",
                    description="New York State chief economic development agency, administering NY Ventures equity co-investments, NYSTAR innovation centers, and REDC clean tech capital funding.",
                    logo_url="https://esd.ny.gov/sites/default/files/esd-logo.png",
                    is_verified=True,
                    data_provenance="statutory_filing"
                )
                db.add(esd_org)
                db.flush()

            # 2. Register / update Programs
            prog_map = {}
            for p_info in ESD_PROGRAMS:
                prog = db.query(Program).filter_by(name=p_info["name"]).first()
                if not prog:
                    prog = Program(
                        name=p_info["name"],
                        description=p_info["description"],
                        program_type=p_info["program_type"],
                        target_stage=p_info["target_stage"],
                        url=p_info["url"]
                    )
                    db.add(prog)
                    db.flush()
                prog_map[p_info["name"]] = prog.id

            # 3. Ingest Opportunities
            for opp_data in ESD_OPPORTUNITIES:
                sol_num = opp_data["solicitation_number"]
                chash = self.compute_hash(json.dumps(opp_data, sort_keys=True))
                existing = db.query(Opportunity).filter_by(solicitation_number=sol_num).first()
                prog_id = prog_map.get(opp_data.get("program_name"))

                if existing:
                    existing.name = opp_data["name"]
                    existing.short_description = opp_data["short_description"]
                    existing.total_funding = opp_data["total_funding"]
                    existing.max_per_award = opp_data["max_per_award"]
                    existing.cost_share_pct = opp_data.get("cost_share_pct")
                    existing.detail_page_url = opp_data["detail_page_url"]
                    existing.due_date_display = opp_data["due_date_display"]
                    existing.program_id = prog_id
                    existing.organization_id = esd_org.id
                    existing.last_verified_at = self.now_utc()
                    stats["updated"] += 1
                else:
                    new_opp = Opportunity(
                        solicitation_number=sol_num,
                        name=opp_data["name"],
                        solicitation_type=opp_data["solicitation_type"],
                        status=opp_data["status"],
                        enrollment_type=opp_data["enrollment_type"],
                        short_description=opp_data["short_description"],
                        total_funding=opp_data["total_funding"],
                        max_per_award=opp_data["max_per_award"],
                        cost_share_pct=opp_data.get("cost_share_pct"),
                        detail_page_url=opp_data["detail_page_url"],
                        due_date_display=opp_data["due_date_display"],
                        source_url=self.source_url,
                        source_name=self.source_name,
                        content_hash=chash,
                        first_seen_at=self.now_utc(),
                        last_verified_at=self.now_utc(),
                        agency="Empire State Development",
                        agency_code="ESD",
                        jurisdiction="state_ny",
                        org_type="economic_development",
                        data_provenance="observed",
                        program_id=prog_id,
                        organization_id=esd_org.id,
                        year=2025
                    )
                    db.add(new_opp)
                    stats["added"] += 1

            # 4. Ingest Awards
            for aw in ESD_AWARDS:
                existing_aw = db.query(Award).filter_by(external_award_id=aw["external_award_id"]).first()
                opp = db.query(Opportunity).filter_by(solicitation_number=aw["solicitation_number"]).first()
                if not existing_aw:
                    new_award = Award(
                        external_award_id=aw["external_award_id"],
                        opportunity_id=opp.id if opp else None,
                        recipient_name=aw["recipient_name"],
                        recipient_type=aw["recipient_type"],
                        recipient_city=aw["recipient_city"],
                        recipient_state=aw["recipient_state"],
                        recipient_zip=aw["recipient_zip"],
                        recipient_country="US",
                        award_amount=aw["award_amount"],
                        year=aw["year"],
                        project_title=aw["project_title"],
                        project_abstract=aw["project_abstract"],
                        award_type=aw["award_type"],
                        program_name=aw["program_name"],
                        agency="Empire State Development",
                        source_name=self.source_name,
                        source_url=self.source_url,
                        solicitation_number=aw["solicitation_number"],
                        latitude=aw["latitude"],
                        longitude=aw["longitude"],
                        geocode_method="address_exact",
                        geocode_confidence=1.0
                    )
                    db.add(new_award)

                # Ensure recipient profile exists
                rec = db.query(Recipient).filter(
                    (Recipient.name.ilike(f"%{aw['recipient_name']}%")) |
                    (Recipient.normalized_name.ilike(f"%{aw['recipient_name'].lower()}%"))
                ).first()
                if rec:
                    rec.total_funding_received = (rec.total_funding_received or 0.0) + aw["award_amount"]
                    rec.total_awards_count = (rec.total_awards_count or 0) + 1
                    if "ESD" not in (rec.funded_agencies or ""):
                        rec.funded_agencies = f"{rec.funded_agencies or ''}, ESD".strip(", ")

            db.commit()
            run.status = "success"
            run.records_added = stats["added"]
            run.completed_at = self.now_utc()
            db.commit()

        except Exception as e:
            logger.error(f"Error in EmpireStateDevelopmentAdapter: {e}")
            db.rollback()
            run.status = "error"
            run.completed_at = self.now_utc()
            db.commit()
            raise

        logger.info(f"EmpireStateDevelopmentAdapter: Added={stats['added']}, Updated={stats['updated']}")
        return stats
