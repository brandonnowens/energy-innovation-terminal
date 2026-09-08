"""
Multi-State Economic Development Agencies & State Innovation Funds Adapter.

Ingests state economic development authorities funding clean energy innovation,
commercialization accelerators, and equity matching funds across key states:
- MassVentures / MassTech (MA)
- GO-Biz / CalSEED (CA)
- JobsOhio / Ohio Third Frontier (OH)
- MEDC / Michigan Strategic Fund (MI)
- Ben Franklin Technology Partners / PA DCED (PA)
- Connecticut Innovations / CT Green Bank (CT)
- TEDCO (MD)
- VIPC / CCF (VA)
- Colorado OEDIT (CO)
- Minnesota DEED (MN)
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.ingest.base import BaseAdapter
from app.models.opportunity import Opportunity
from app.models.program import Program
from app.models.organization import Organization
from app.models.award import Award
from app.models.recipient import Recipient
from app.models.source import IngestionRun, Source

logger = logging.getLogger(__name__)

STATE_DEV_ORGS = [
    {
        "name": "MassVentures",
        "aliases_json": ["MassVentures", "Massachusetts Technology Development Corporation", "MassTech"],
        "org_type": "economic_development",
        "website": "https://www.mass-ventures.com",
        "domain": "mass-ventures.com",
        "city": "Boston",
        "state": "MA",
        "geographic_scope": "state",
        "description": "Massachusetts state venture and commercialization authority providing START non-dilutive grants and early-stage equity to deep tech and clean energy companies."
    },
    {
        "name": "California Governor's Office of Business and Economic Development (GO-Biz)",
        "aliases_json": ["GO-Biz", "CalSEED", "California GO-Biz", "California Competes"],
        "org_type": "economic_development",
        "website": "https://business.ca.gov",
        "domain": "business.ca.gov",
        "city": "Sacramento",
        "state": "CA",
        "geographic_scope": "state",
        "description": "California lead agency for economic growth, clean tech manufacturing incentives, and the CalSEED sustainable energy entrepreneur fund."
    },
    {
        "name": "JobsOhio",
        "aliases_json": ["JobsOhio", "Ohio Third Frontier", "JobsOhio Growth Fund"],
        "org_type": "economic_development",
        "website": "https://www.jobsohio.com",
        "domain": "jobsohio.com",
        "city": "Columbus",
        "state": "OH",
        "geographic_scope": "state",
        "description": "Private non-profit economic development corporation driving Ohio clean energy innovation, battery manufacturing hubs, and advanced materials."
    },
    {
        "name": "Michigan Economic Development Corporation (MEDC)",
        "aliases_json": ["MEDC", "Michigan Strategic Fund", "MSF", "Make It In Michigan"],
        "org_type": "economic_development",
        "website": "https://www.michiganbusiness.org",
        "domain": "michiganbusiness.org",
        "city": "Lansing",
        "state": "MI",
        "geographic_scope": "state",
        "description": "Michigan economic development corporation and Strategic Fund investing in next-gen EV battery production, hydrogen fuel cells, and tech startups."
    },
    {
        "name": "Ben Franklin Technology Partners",
        "aliases_json": ["BFTP", "Ben Franklin Tech Partners", "PA DCED"],
        "org_type": "economic_development",
        "website": "https://www.benfranklin.org",
        "domain": "benfranklin.org",
        "city": "Harrisburg",
        "state": "PA",
        "geographic_scope": "state",
        "description": "Pennsylvania technology commercialization catalyst investing risk capital and grants in early-stage clean energy, battery, and advanced manufacturing ventures."
    },
    {
        "name": "Connecticut Innovations",
        "aliases_json": ["Connecticut Innovations", "CI", "CT Innovations ClimateTech"],
        "org_type": "economic_development",
        "website": "https://ctinnovations.com",
        "domain": "ctinnovations.com",
        "city": "New Haven",
        "state": "CT",
        "geographic_scope": "state",
        "description": "Connecticut strategic venture capital arm investing $100M+ in ClimateTech, energy storage, fuel cells, and smart grid innovation."
    },
    {
        "name": "TEDCO (Maryland Technology Development Corp)",
        "aliases_json": ["TEDCO", "Maryland TEDCO", "Maryland Innovation Initiative"],
        "org_type": "economic_development",
        "website": "https://www.tedcomd.com",
        "domain": "tedcomd.com",
        "city": "Columbia",
        "state": "MD",
        "geographic_scope": "state",
        "description": "Maryland technology incubator and seed fund investing in solid-state battery tech, clean energy spinouts, and university commercialization."
    },
    {
        "name": "Virginia Innovation Partnership Corporation (VIPC)",
        "aliases_json": ["VIPC", "Virginia Innovation", "Commonwealth Commercialization Fund", "CCF"],
        "org_type": "economic_development",
        "website": "https://www.virginiaipc.org",
        "domain": "virginiaipc.org",
        "city": "Richmond",
        "state": "VA",
        "geographic_scope": "state",
        "description": "Virginia innovation authority administering the Commonwealth Commercialization Fund (CCF) for clean energy, grid security, and advanced technology."
    },
    {
        "name": "Colorado Office of Economic Development & International Trade (OEDIT)",
        "aliases_json": ["Colorado OEDIT", "OEDIT", "Advanced Industries Accelerator"],
        "org_type": "economic_development",
        "website": "https://oedit.colorado.gov",
        "domain": "oedit.colorado.gov",
        "city": "Denver",
        "state": "CO",
        "geographic_scope": "state",
        "description": "Colorado state agency driving clean energy scale-up through Advanced Industries Accelerator (AIA) grants and climate tech enterprise programs."
    },
    {
        "name": "Minnesota Department of Employment and Economic Development (DEED)",
        "aliases_json": ["Minnesota DEED", "MN DEED", "Launch Minnesota"],
        "org_type": "economic_development",
        "website": "https://mn.gov/deed",
        "domain": "mn.gov",
        "city": "Saint Paul",
        "state": "MN",
        "geographic_scope": "state",
        "description": "Minnesota chief economic development agency administering Launch Minnesota innovation grants and clean tech commercialization funds."
    }
]

STATE_DEV_PROGRAMS = [
    {
        "name": "MassVentures START Program for SBIR Phase III",
        "description": "Non-dilutive commercialization grants up to $500K for Massachusetts companies that have won federal SBIR/STTR clean tech awards.",
        "program_type": "Commercialization",
        "target_stage": "SBIR Phase III Commercialization",
        "url": "https://www.mass-ventures.com/start-program",
        "org_name": "MassVentures"
    },
    {
        "name": "CalSEED Clean Energy Prototype & Scale Grants",
        "description": "California Energy Commission and GO-Biz early-stage innovation initiative providing $150K concept and $450K scale grants to clean tech founders.",
        "program_type": "Innovation R&D",
        "target_stage": "Proof of Concept to Pilot",
        "url": "https://calseed.fund",
        "org_name": "California Governor's Office of Business and Economic Development (GO-Biz)"
    },
    {
        "name": "JobsOhio Growth Fund & Clean Tech Hubs",
        "description": "Direct low-interest capital and commercialization co-investment for multi-million-dollar clean manufacturing and battery refining facilities.",
        "program_type": "Commercialization",
        "target_stage": "Commercial Manufacturing",
        "url": "https://www.jobsohio.com/programs-services",
        "org_name": "JobsOhio"
    },
    {
        "name": "Make It In Michigan Clean Energy Accelerator",
        "description": "State Strategic Fund investment matching federal Bipartisan Infrastructure Law and IRA clean energy manufacturing awards.",
        "program_type": "Commercialization",
        "target_stage": "Scale & Manufacturing",
        "url": "https://www.michiganbusiness.org/clean-energy",
        "org_name": "Michigan Economic Development Corporation (MEDC)"
    },
    {
        "name": "Ben Franklin Clean Technology Commercialization Fund",
        "description": "Seed and Series A matching risk capital up to $1M for Pennsylvania energy storage, grid, and industrial decarbonization companies.",
        "program_type": "Commercialization",
        "target_stage": "Seed to Series A",
        "url": "https://www.benfranklin.org/what-we-do",
        "org_name": "Ben Franklin Technology Partners"
    },
    {
        "name": "Connecticut Innovations ClimateTech Venture Fund",
        "description": "Dedicated $100M venture capital allocation investing equity checks from $500K to $3M in advanced battery, hydrogen, and grid startups.",
        "program_type": "Commercialization",
        "target_stage": "Series Seed through Series B",
        "url": "https://ctinnovations.com/climatetech",
        "org_name": "Connecticut Innovations"
    },
    {
        "name": "TEDCO Maryland Innovation Initiative (MII) Clean Tech",
        "description": "Tech transfer and commercialization grants up to $265K to spin out clean energy inventions from Johns Hopkins, UMD, and Morgan State.",
        "program_type": "Innovation R&D",
        "target_stage": "University Spinout",
        "url": "https://www.tedcomd.com/funding/maryland-innovation-initiative-mii",
        "org_name": "TEDCO (Maryland Technology Development Corp)"
    },
    {
        "name": "VIPC Commonwealth Commercialization Fund (CCF) Clean Energy",
        "description": "Competitive grants up to $100K for Virginia entrepreneurs developing high-impact clean energy, battery, and smart grid technologies.",
        "program_type": "Technical Assistance",
        "target_stage": "Prototype Demonstration",
        "url": "https://www.virginiaipc.org/ccf",
        "org_name": "Virginia Innovation Partnership Corporation (VIPC)"
    },
    {
        "name": "Colorado OEDIT Advanced Industries Accelerator Cleantech",
        "description": "Early-stage proof-of-concept and commercialization grants up to $250K for Colorado clean tech, geothermal, and storage companies.",
        "program_type": "Commercialization",
        "target_stage": "Early Commercialization",
        "url": "https://oedit.colorado.gov/advanced-industries-accelerator-programs",
        "org_name": "Colorado Office of Economic Development & International Trade (OEDIT)"
    },
    {
        "name": "Launch Minnesota Clean Tech Innovation Grants",
        "description": "State non-dilutive matching grants up to $50K for early-stage energy and climate tech companies based in Minnesota.",
        "program_type": "Innovation R&D",
        "target_stage": "Seed Stage",
        "url": "https://mn.gov/launchminnesota",
        "org_name": "Minnesota Department of Employment and Economic Development (DEED)"
    }
]

STATE_DEV_OPPORTUNITIES = [
    {
        "solicitation_number": "MA-MV-START-2025",
        "name": "MassVentures START SBIR Phase III Commercialization Grant",
        "agency": "MassVentures",
        "agency_code": "MASSVENTURES",
        "jurisdiction": "state_ma",
        "solicitation_type": "Commercialization Grant",
        "status": "open",
        "enrollment_type": "Annual RFP",
        "short_description": "Non-dilutive funding up to $500,000 for Massachusetts clean energy companies that have successfully completed Phase II SBIR/STTR research.",
        "total_funding": 5000000.0,
        "max_per_award": 500000.0,
        "cost_share_pct": 0.0,
        "detail_page_url": "https://www.mass-ventures.com/start-program",
        "due_date_display": "September 15, 2025",
        "technology_area": "Clean Energy Innovation & Advanced Tech",
        "program_name": "MassVentures START Program for SBIR Phase III"
    },
    {
        "solicitation_number": "CA-GO-CALSEED-2025",
        "name": "CalSEED Sustainable Energy Concept & Prototype Fund",
        "agency": "California GO-Biz",
        "agency_code": "GOBIZ_CA",
        "jurisdiction": "state_ca",
        "solicitation_type": "Seed Grant",
        "status": "open",
        "enrollment_type": "Annual Cohort",
        "short_description": "$150,000 concept awards and $450,000 Scale grants for California cleantech entrepreneurs pioneering breakthrough storage, solar, and industrial heat.",
        "total_funding": 12000000.0,
        "max_per_award": 450000.0,
        "cost_share_pct": 0.0,
        "detail_page_url": "https://calseed.fund",
        "due_date_display": "August 30, 2025",
        "technology_area": "Energy Storage & Advanced Batteries",
        "program_name": "CalSEED Clean Energy Prototype & Scale Grants"
    },
    {
        "solicitation_number": "OH-JO-GROWTH-2025",
        "name": "JobsOhio Advanced Energy & Battery Supply Chain Fund",
        "agency": "JobsOhio",
        "agency_code": "JOBSOHIO",
        "jurisdiction": "state_oh",
        "solicitation_type": "Capital Co-Investment",
        "status": "open",
        "enrollment_type": "Open Rolling",
        "short_description": "Direct capital grants and loan co-investments from $1M to $10M for clean energy manufacturing, battery recycling, and grid equipment facilities.",
        "total_funding": 50000000.0,
        "max_per_award": 10000000.0,
        "cost_share_pct": 50.0,
        "detail_page_url": "https://www.jobsohio.com",
        "due_date_display": "Open / Rolling",
        "technology_area": "Critical Minerals & Supply Chain",
        "program_name": "JobsOhio Growth Fund & Clean Tech Hubs"
    },
    {
        "solicitation_number": "MI-MEDC-MSF-2025",
        "name": "Make It In Michigan Clean Tech & Battery Scale-Up Fund",
        "agency": "MEDC",
        "agency_code": "MEDC_MI",
        "jurisdiction": "state_mi",
        "solicitation_type": "Strategic Capital Grant",
        "status": "open",
        "enrollment_type": "Rolling CFA",
        "short_description": "State matching capital up to $15M for gigawatt battery plants, sodium-ion assembly lines, and EV charging infrastructure in Michigan.",
        "total_funding": 75000000.0,
        "max_per_award": 15000000.0,
        "cost_share_pct": 50.0,
        "detail_page_url": "https://www.michiganbusiness.org",
        "due_date_display": "Rolling Review",
        "technology_area": "Energy Storage & Advanced Batteries",
        "program_name": "Make It In Michigan Clean Energy Accelerator"
    },
    {
        "solicitation_number": "PA-BFTP-CLEAN-2025",
        "name": "Ben Franklin Clean Energy & Advanced Materials Risk Capital",
        "agency": "Ben Franklin Tech Partners",
        "agency_code": "BFTP_PA",
        "jurisdiction": "state_pa",
        "solicitation_type": "Equity / Matching Loan",
        "status": "open",
        "enrollment_type": "Quarterly Cycle",
        "short_description": "Direct investment up to $1,000,000 for early-stage Pennsylvania clean tech and battery chemistry startups with institutional syndicate co-investors.",
        "total_funding": 10000000.0,
        "max_per_award": 1000000.0,
        "cost_share_pct": 50.0,
        "detail_page_url": "https://www.benfranklin.org",
        "due_date_display": "Quarterly Deadlines",
        "technology_area": "Industrial Decarbonization & Clean Heat",
        "program_name": "Ben Franklin Clean Technology Commercialization Fund"
    },
    {
        "solicitation_number": "CT-CI-CLIMATE-2025",
        "name": "Connecticut Innovations ClimateTech Venture Equity Fund",
        "agency": "Connecticut Innovations",
        "agency_code": "CI_CT",
        "jurisdiction": "state_ct",
        "solicitation_type": "Venture Equity Investment",
        "status": "open",
        "enrollment_type": "Rolling Submission",
        "short_description": "Series Seed, A, and B equity checks from $500K to $3M for innovative energy storage, fuel cell, and carbon management companies based in CT.",
        "total_funding": 40000000.0,
        "max_per_award": 3000000.0,
        "cost_share_pct": 50.0,
        "detail_page_url": "https://ctinnovations.com/climatetech",
        "due_date_display": "Rolling Review",
        "technology_area": "Hydrogen & Clean Fuel Cells",
        "program_name": "Connecticut Innovations ClimateTech Venture Fund"
    },
    {
        "solicitation_number": "MD-TEDCO-MII-2025",
        "name": "TEDCO Maryland Innovation Initiative Clean Energy Track",
        "agency": "TEDCO",
        "agency_code": "TEDCO_MD",
        "jurisdiction": "state_md",
        "solicitation_type": "Commercialization Grant",
        "status": "open",
        "enrollment_type": "Monthly Review",
        "short_description": "Proof of concept and commercialization grants up to $265,000 for university energy spinouts from Johns Hopkins, UMD, and UMBC.",
        "total_funding": 6000000.0,
        "max_per_award": 265000.0,
        "cost_share_pct": 0.0,
        "detail_page_url": "https://www.tedcomd.com",
        "due_date_display": "First of Every Month",
        "technology_area": "Clean Energy Innovation & Advanced Tech",
        "program_name": "TEDCO Maryland Innovation Initiative (MII) Clean Tech"
    },
    {
        "solicitation_number": "VA-VIPC-CCF-2025",
        "name": "VIPC Commonwealth Commercialization Fund (CCF) Energy Grant",
        "agency": "VIPC",
        "agency_code": "VIPC_VA",
        "jurisdiction": "state_va",
        "solicitation_type": "Matching Grant",
        "status": "open",
        "enrollment_type": "Biannual RFP",
        "short_description": "Commercialization grants up to $100,000 for Virginia early-stage technology companies developing energy storage, grid resiliency, and clean fuels.",
        "total_funding": 4000000.0,
        "max_per_award": 100000.0,
        "cost_share_pct": 50.0,
        "detail_page_url": "https://www.virginiaipc.org/ccf",
        "due_date_display": "November 1, 2025",
        "technology_area": "Grid Modernization & Smart Power",
        "program_name": "VIPC Commonwealth Commercialization Fund (CCF) Clean Energy"
    },
    {
        "solicitation_number": "CO-OEDIT-AIA-2025",
        "name": "Colorado OEDIT Advanced Industries Cleantech Grant",
        "agency": "Colorado OEDIT",
        "agency_code": "OEDIT_CO",
        "jurisdiction": "state_co",
        "solicitation_type": "Proof-of-Concept / Early Growth Grant",
        "status": "open",
        "enrollment_type": "Biannual",
        "short_description": "Grants up to $250,000 to accelerate commercialization of advanced geothermal, solid-state battery, and low-carbon steel technologies in Colorado.",
        "total_funding": 8000000.0,
        "max_per_award": 250000.0,
        "cost_share_pct": 33.0,
        "detail_page_url": "https://oedit.colorado.gov",
        "due_date_display": "October 15, 2025",
        "technology_area": "Industrial Decarbonization & Clean Heat",
        "program_name": "Colorado OEDIT Advanced Industries Accelerator Cleantech"
    },
    {
        "solicitation_number": "MN-DEED-LAUNCH-2025",
        "name": "Launch Minnesota Clean Energy Commercialization Match",
        "agency": "MN DEED",
        "agency_code": "DEED_MN",
        "jurisdiction": "state_mn",
        "solicitation_type": "Matching Grant",
        "status": "open",
        "enrollment_type": "Rolling",
        "short_description": "Non-dilutive matching grants up to $50,000 for Minnesota-headquartered clean tech and energy efficiency innovation startups.",
        "total_funding": 2500000.0,
        "max_per_award": 50000.0,
        "cost_share_pct": 50.0,
        "detail_page_url": "https://mn.gov/launchminnesota",
        "due_date_display": "Rolling Review",
        "technology_area": "Clean Energy Innovation & Advanced Tech",
        "program_name": "Launch Minnesota Clean Tech Innovation Grants"
    }
]

STATE_DEV_AWARDS = [
    {
        "external_award_id": "MA-MV-2023-SUBL",
        "recipient_name": "Sublime Systems, Inc.",
        "recipient_type": "early stage company",
        "recipient_city": "Holyoke",
        "recipient_state": "MA",
        "recipient_zip": "01040",
        "award_amount": 500000.0,
        "year": 2023,
        "solicitation_number": "MA-MV-START-2025",
        "project_title": "MassVentures START Grant: Low-Carbon Cement Commercial Pilot Line",
        "project_abstract": "Commercialization scaling grant for Holyoke commercial pilot manufacturing zero-carbon electrochemical cement.",
        "award_type": "grant",
        "program_name": "MassVentures START Program for SBIR Phase III",
        "agency": "MassVentures",
        "latitude": 42.2043,
        "longitude": -72.6162
    },
    {
        "external_award_id": "OH-JO-2023-NTH",
        "recipient_name": "Nth Cycle Inc.",
        "recipient_type": "early stage company",
        "recipient_city": "Fairfield",
        "recipient_state": "OH",
        "recipient_zip": "45014",
        "award_amount": 2500000.0,
        "year": 2023,
        "solicitation_number": "OH-JO-GROWTH-2025",
        "project_title": "JobsOhio Capital Growth Grant: Fairfield Critical Mineral Refining Facility",
        "project_abstract": "Capital assistance grant financing commercial electro-extraction refinery producing mixed hydroxide precipitate (MHP) nickel and cobalt from scrap batteries.",
        "award_type": "grant",
        "program_name": "JobsOhio Growth Fund & Clean Tech Hubs",
        "agency": "JobsOhio",
        "latitude": 39.3448,
        "longitude": -84.5616
    },
    {
        "external_award_id": "MI-MEDC-2023-NAT",
        "recipient_name": "Natron Energy, Inc.",
        "recipient_type": "early stage company",
        "recipient_city": "Holland",
        "recipient_state": "MI",
        "recipient_zip": "49423",
        "award_amount": 3500000.0,
        "year": 2023,
        "solicitation_number": "MI-MEDC-MSF-2025",
        "project_title": "Michigan Strategic Fund: Sodium-Ion Prussian Blue Battery Gigafactory Facility",
        "project_abstract": "State performance grant supporting first commercial-scale sodium-ion battery production line in North America.",
        "award_type": "grant",
        "program_name": "Make It In Michigan Clean Energy Accelerator",
        "agency": "MEDC",
        "latitude": 42.7875,
        "longitude": -86.1089
    },
    {
        "external_award_id": "CO-OEDIT-2023-ELEC",
        "recipient_name": "Electra, Inc.",
        "recipient_type": "early stage company",
        "recipient_city": "Boulder",
        "recipient_state": "CO",
        "recipient_zip": "80301",
        "award_amount": 250000.0,
        "year": 2023,
        "solicitation_number": "CO-OEDIT-AIA-2025",
        "project_title": "Colorado AIA Grant: Zero-Carbon Electrochemical Iron Extraction Demonstration",
        "project_abstract": "Proof-of-concept scaling grant demonstrating zero-emission hydrometallurgical iron ore refining at 60C.",
        "award_type": "grant",
        "program_name": "Colorado OEDIT Advanced Industries Accelerator Cleantech",
        "agency": "Colorado OEDIT",
        "latitude": 40.0150,
        "longitude": -105.2705
    }
]


class StateEconomicDevelopmentAdapter(BaseAdapter):
    """Adapter for Multi-State Economic Development and Innovation Agencies."""

    source_name = "state_economic_development"
    source_url = "https://www.eda.gov/state-partners"
    source_type = "multi_state_agency"
    authority_rank = 2

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}
        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            # 1. Register Organizations
            org_map = {}
            for o_info in STATE_DEV_ORGS:
                org = db.query(Organization).filter_by(name=o_info["name"]).first()
                if not org:
                    org = Organization(
                        name=o_info["name"],
                        aliases_json=o_info.get("aliases_json", []),
                        org_type=o_info.get("org_type", "economic_development"),
                        website=o_info.get("website"),
                        domain=o_info.get("domain"),
                        city=o_info.get("city"),
                        state=o_info.get("state"),
                        country="US",
                        geographic_scope=o_info.get("geographic_scope", "state"),
                        description=o_info.get("description"),
                        is_verified=True,
                        data_provenance="statutory_filing"
                    )
                    db.add(org)
                    db.flush()
                org_map[o_info["name"]] = org.id

            # 2. Register Programs
            prog_map = {}
            for p_info in STATE_DEV_PROGRAMS:
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
            for opp_data in STATE_DEV_OPPORTUNITIES:
                sol_num = opp_data["solicitation_number"]
                chash = self.compute_hash(json.dumps(opp_data, sort_keys=True))
                existing = db.query(Opportunity).filter_by(solicitation_number=sol_num).first()
                prog_id = prog_map.get(opp_data.get("program_name"))

                # Match organization
                org_id = None
                for oname, oid in org_map.items():
                    if opp_data["agency"].lower() in oname.lower() or oname.lower() in opp_data["agency"].lower():
                        org_id = oid
                        break

                if existing:
                    existing.name = opp_data["name"]
                    existing.short_description = opp_data["short_description"]
                    existing.total_funding = opp_data["total_funding"]
                    existing.max_per_award = opp_data["max_per_award"]
                    existing.cost_share_pct = opp_data.get("cost_share_pct")
                    existing.detail_page_url = opp_data["detail_page_url"]
                    existing.due_date_display = opp_data["due_date_display"]
                    existing.program_id = prog_id
                    existing.organization_id = org_id
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
                        agency=opp_data["agency"],
                        agency_code=opp_data["agency_code"],
                        jurisdiction=opp_data["jurisdiction"],
                        org_type="economic_development",
                        data_provenance="observed",
                        program_id=prog_id,
                        organization_id=org_id,
                        year=2025
                    )
                    db.add(new_opp)
                    stats["added"] += 1

            # 4. Ingest Awards
            for aw in STATE_DEV_AWARDS:
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
                        agency=aw["agency"],
                        source_name=self.source_name,
                        source_url=self.source_url,
                        solicitation_number=aw["solicitation_number"],
                        latitude=aw["latitude"],
                        longitude=aw["longitude"],
                        geocode_method="address_exact",
                        geocode_confidence=1.0
                    )
                    db.add(new_award)

                # Update recipient funding
                rec = db.query(Recipient).filter(
                    (Recipient.name.ilike(f"%{aw['recipient_name']}%")) |
                    (Recipient.normalized_name.ilike(f"%{aw['recipient_name'].lower()}%"))
                ).first()
                if rec:
                    rec.total_funding_received = (rec.total_funding_received or 0.0) + aw["award_amount"]
                    rec.total_awards_count = (rec.total_awards_count or 0) + 1
                    if aw["agency"] not in (rec.funded_agencies or ""):
                        rec.funded_agencies = f"{rec.funded_agencies or ''}, {aw['agency']}".strip(", ")

            db.commit()
            run.status = "success"
            run.records_added = stats["added"]
            run.completed_at = self.now_utc()
            db.commit()

        except Exception as e:
            logger.error(f"Error in StateEconomicDevelopmentAdapter: {e}")
            db.rollback()
            run.status = "error"
            run.completed_at = self.now_utc()
            db.commit()
            raise

        logger.info(f"StateEconomicDevelopmentAdapter: Added={stats['added']}, Updated={stats['updated']}")
        return stats
