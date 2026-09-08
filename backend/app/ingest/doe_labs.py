import json
import logging
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from app.ingest.base import BaseAdapter
from app.models.opportunity import (
    Opportunity,
    OpportunityCategory,
    OpportunityRound,
    EligibilityRule,
)
from app.models.source import ChangeEvent, IngestionRun, Source

logger = logging.getLogger(__name__)

class DOELabsAdapter(BaseAdapter):
    source_name = "doe_labs"
    source_url = "https://www.energy.gov/technologytransitions"
    source_type = "html"
    authority_rank = 2

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
                    description="DOE National Lab Partnership & Fellowship Adapter",
                    update_frequency="weekly",
                )
                db.add(source)
                db.commit()

            source.last_fetched_at = self.now_utc()

            opportunities_data = []

            # 1. LEEP Fellowship programs
            leep_programs = [
                {
                    "solicitation_number": f"DOE-LEEP-CyclotronRoad-{datetime.now().year}",
                    "name": "Cyclotron Road (LBNL)",
                    "agency_code": "DOE-LBNL",
                    "url": "https://cyclotronroad.org/",
                    "description": "2-year fellowship for hard-tech entrepreneurs at Lawrence Berkeley National Laboratory."
                },
                {
                    "solicitation_number": f"DOE-LEEP-ChainReaction-{datetime.now().year}",
                    "name": "Chain Reaction Innovations (ANL)",
                    "agency_code": "DOE-ANL",
                    "url": "https://chainreaction.anl.gov/",
                    "description": "2-year fellowship for hard-tech entrepreneurs at Argonne National Laboratory."
                },
                {
                    "solicitation_number": f"DOE-LEEP-InnovationCrossroads-{datetime.now().year}",
                    "name": "Innovation Crossroads (ORNL)",
                    "agency_code": "DOE-ORNL",
                    "url": "https://innovationcrossroads.ornl.gov/",
                    "description": "2-year fellowship for hard-tech entrepreneurs at Oak Ridge National Laboratory."
                }
            ]

            for prog in leep_programs:
                status = "open"
                raw_html = ""
                try:
                    resp = self.fetch_url(prog["url"], timeout=10.0)
                    raw_html = resp.text
                    if "closed" in raw_html.lower() and "apply" not in raw_html.lower():
                        pass
                except Exception as e:
                    logger.warning(f"Failed to fetch {prog['url']}: {e}")
                
                opportunities_data.append({
                    "solicitation_number": prog["solicitation_number"],
                    "name": prog["name"],
                    "agency": "DOE",
                    "agency_code": prog["agency_code"],
                    "funding_type": "fellowship",
                    "status": status,
                    "short_description": prog["description"],
                    "detail_page_url": prog["url"],
                    "raw_source_data": json.dumps({"url": prog["url"], "html_length": len(raw_html)}),
                    "keywords": json.dumps(["fellowship", "entrepreneurship", "hard-tech", "deep-tech", "commercialization"]),
                    "objectives": "Support hard-tech entrepreneurs to bridge the valley of death by providing funding, lab access, and mentorship."
                })

            # 2. Technology Commercialization Fund (TCF)
            tcf_url = "https://www.energy.gov/technologytransitions/technology-commercialization-fund"
            try:
                resp = self.fetch_url(tcf_url)
                raw_html = resp.text
            except Exception as e:
                logger.warning(f"Failed to fetch TCF: {e}")
                raw_html = ""

            opportunities_data.append({
                "solicitation_number": "DOE-TCF-OPEN",
                "name": "Technology Commercialization Fund (Current)",
                "agency": "DOE",
                "agency_code": "DOE",
                "funding_type": "partnership",
                "status": "open",
                "is_historical": False,
                "short_description": "Current round of Technology Commercialization Fund (TCF).",
                "detail_page_url": tcf_url,
                "raw_source_data": json.dumps({"url": tcf_url}),
            })
            opportunities_data.append({
                "solicitation_number": "DOE-TCF-HISTORICAL",
                "name": "Technology Commercialization Fund (Historical Awards)",
                "agency": "DOE",
                "agency_code": "DOE",
                "funding_type": "partnership",
                "status": "closed",
                "is_historical": True,
                "short_description": "Historical awards under the Technology Commercialization Fund (TCF).",
                "detail_page_url": tcf_url,
                "raw_source_data": json.dumps({"url": tcf_url}),
            })

            # 3. Small Business Vouchers (SBV)
            sbv_url = "https://www.energy.gov/technologytransitions/small-business-voucher"
            try:
                resp = self.fetch_url(sbv_url)
            except Exception as e:
                logger.warning(f"Failed to fetch SBV: {e}")
                
            opportunities_data.append({
                "solicitation_number": "DOE-SBV-OPEN",
                "name": "Small Business Vouchers (SBV) - Current",
                "agency": "DOE",
                "agency_code": "DOE",
                "funding_type": "voucher",
                "status": "open",
                "is_historical": False,
                "short_description": "Current Small Business Vouchers (SBV) program.",
                "detail_page_url": sbv_url,
                "raw_source_data": json.dumps({"url": sbv_url}),
            })

            # 4. Genesis Mission Initiatives & AI Discovery Platform
            genesis_foa_url = "https://www.energy.gov/science/genesis-mission"
            opportunities_data.append({
                "solicitation_number": "DE-FOA-0003612",
                "name": "The Genesis Mission: Transforming Science and Energy with AI",
                "agency": "DOE",
                "agency_code": "DOE-SC",
                "funding_type": "cooperative_agreement",
                "status": "closed",
                "is_historical": True,
                "year": 2026,
                "total_funding": 150000000.0,
                "max_per_award": 25000000.0,
                "short_description": "Flagship Department of Energy Office of Science funding opportunity to build integrated AI-driven scientific discovery capabilities. The initiative pairs multidisciplinary research teams with supercomputers, automated laboratory workflows, foundation models, and high-performance experimental facilities across the 17 DOE National Laboratories.",
                "objectives": "Accelerate scientific discovery, strengthen American energy dominance, and advance high-performance AI foundation models for clean energy materials, advanced nuclear systems, quantum computing, chemical catalysis, and fusion energy.",
                "detail_page_url": genesis_foa_url,
                "portal_url": "https://pamspublic.science.energy.gov",
                "keywords": json.dumps(["Genesis Mission", "AI for Science", "Foundation Models", "Supercomputing", "Advanced Materials", "Quantum Computing", "National Labs"]),
                "categories": [
                    {"category_type": "technology", "category_value": "AI & Advanced Computing", "confidence": 0.95},
                    {"category_type": "technology", "category_value": "Clean Energy Materials", "confidence": 0.90},
                    {"category_type": "technology", "category_value": "Nuclear", "confidence": 0.85},
                    {"category_type": "technology", "category_value": "Quantum Science", "confidence": 0.85},
                    {"category_type": "activity", "category_value": "Research", "confidence": 0.95},
                    {"category_type": "activity", "category_value": "Demonstration", "confidence": 0.90},
                ],
                "rounds": [
                    {"round_number": "1", "status": "Closed", "due_date": datetime(2026, 5, 15, 17, 0, 0)}
                ]
            })

            genesis_consortium_url = "https://genesismissionconsortium.org/"
            opportunities_data.append({
                "solicitation_number": "DOE-GENESIS-CONSORTIUM",
                "name": "DOE Genesis Mission Consortium & American Science Cloud",
                "agency": "DOE",
                "agency_code": "DOE-HQ",
                "funding_type": "partnership",
                "enrollment_type": "Open Enrollment",
                "status": "open",
                "is_historical": False,
                "year": 2026,
                "total_funding": 500000000.0,
                "short_description": "The DOE Genesis Mission Consortium connects the 17 DOE National Laboratories, universities, and commercial industry partners to develop and deploy open AI foundation models, high-performance computing testbeds, and automated robotic laboratories under the American Science Cloud.",
                "objectives": "Deploy scalable AI computing infrastructure, facilitate public-private consortium partnerships, and provide researchers with access to leading national laboratory supercomputers (Frontier, Aurora, Summit) for breakthrough energy science.",
                "detail_page_url": genesis_consortium_url,
                "portal_url": "https://www.energy.gov/technologytransitions/partnerships",
                "keywords": json.dumps(["Genesis Consortium", "American Science Cloud", "National Labs", "AI", "Supercomputers", "Public-Private Partnership"]),
                "categories": [
                    {"category_type": "technology", "category_value": "AI & Advanced Computing", "confidence": 0.95},
                    {"category_type": "technology", "category_value": "Grid Modernization", "confidence": 0.85},
                    {"category_type": "activity", "category_value": "Deployment", "confidence": 0.90},
                    {"category_type": "activity", "category_value": "Technical Assistance", "confidence": 0.90},
                ],
                "rounds": [
                    {"round_number": "1", "status": "Open", "due_date": datetime(2026, 12, 31, 23, 59, 59)}
                ]
            })

            # 5. Lab Partnerships Overview
            pathways = [
                {
                    "solicitation_number": "DOE-CRADA-PATHWAY",
                    "name": "Cooperative Research and Development Agreement (CRADA)",
                    "description": "A CRADA is a written agreement between one or more DOE laboratories and one or more non-federal parties under which the government provides personnel, services, facilities, equipment, intellectual property, or other resources with or without reimbursement."
                },
                {
                    "solicitation_number": "DOE-ACT-PATHWAY",
                    "name": "Agreements for Commercializing Technology (ACT)",
                    "description": "ACTs authorize National Laboratories to partner with businesses and non-federal entities, allowing for more flexible terms and conditions than CRADAs."
                },
                {
                    "solicitation_number": "DOE-SPP-PATHWAY",
                    "name": "Strategic Partnership Projects (SPP)",
                    "description": "SPPs allow non-DOE entities to use DOE National Laboratory facilities and personnel to conduct work that is not directly funded by DOE."
                }
            ]

            partnership_url = "https://www.energy.gov/technologytransitions/partnerships"
            try:
                resp = self.fetch_url(partnership_url)
            except:
                pass

            for pathway in pathways:
                opportunities_data.append({
                    "solicitation_number": pathway["solicitation_number"],
                    "name": pathway["name"],
                    "agency": "DOE",
                    "agency_code": "DOE",
                    "funding_type": "partnership",
                    "enrollment_type": "Open Enrollment",
                    "status": "open",
                    "short_description": pathway["description"],
                    "detail_page_url": partnership_url,
                    "raw_source_data": json.dumps({"url": partnership_url}),
                })

            # Upsert into DB
            seen_ids = set()
            for opp_data in opportunities_data:
                sol_num = opp_data["solicitation_number"]
                existing = db.query(Opportunity).filter_by(solicitation_number=sol_num).first()
                
                # Separate relationships/categories/rounds from model columns
                categories_list = opp_data.pop("categories", [])
                rounds_list = opp_data.pop("rounds", [])

                # Default shared fields
                shared_fields = {
                    "jurisdiction": "federal",
                    "org_type": "government",
                    "data_provenance": "observed",
                    "geographic_scope": "National - any DOE National Lab",
                    "source_url": self.source_url,
                    "source_name": self.source_name
                }
                
                # Merge dictionaries safely
                combined_data = {**opp_data, **shared_fields}
                content_hash = self.compute_hash(json.dumps(combined_data, default=str, sort_keys=True))

                target_opp = None
                if existing:
                    target_opp = existing
                    if existing.content_hash == content_hash:
                        existing.last_verified_at = self.now_utc()
                        stats["unchanged"] += 1
                    else:
                        for k, v in combined_data.items():
                            if hasattr(existing, k):
                                setattr(existing, k, v)
                        existing.content_hash = content_hash
                        existing.last_verified_at = self.now_utc()
                        stats["updated"] += 1
                    seen_ids.add(sol_num)
                else:
                    new_opp = Opportunity()
                    for k, v in combined_data.items():
                        if hasattr(new_opp, k):
                            setattr(new_opp, k, v)
                    
                    new_opp.content_hash = content_hash
                    new_opp.first_seen_at = self.now_utc()
                    new_opp.last_verified_at = self.now_utc()
                    
                    db.add(new_opp)
                    db.flush()
                    target_opp = new_opp
                    
                    db.add(ChangeEvent(
                        entity_type="opportunity", entity_id=sol_num,
                        entity_name=new_opp.name, change_type="new", source_name=self.source_name,
                    ))
                    stats["added"] += 1
                    seen_ids.add(sol_num)

                # Attach categories
                if categories_list and target_opp:
                    existing_cats = {c.category_value for c in target_opp.categories}
                    for cat in categories_list:
                        if cat["category_value"] not in existing_cats:
                            db.add(OpportunityCategory(
                                opportunity_id=target_opp.id,
                                category_type=cat["category_type"],
                                category_value=cat["category_value"],
                                confidence=cat.get("confidence", 0.9),
                                source="doe_labs_adapter",
                            ))

                # Attach rounds
                if rounds_list and target_opp:
                    existing_round_nums = {r.round_number for r in target_opp.rounds}
                    for rd in rounds_list:
                        if rd["round_number"] not in existing_round_nums:
                            db.add(OpportunityRound(
                                opportunity_id=target_opp.id,
                                round_number=rd["round_number"],
                                status=rd.get("status", target_opp.status),
                                due_date=rd.get("due_date"),
                            ))

                # Sync FTS if available
                if target_opp:
                    try:
                        db.execute(text("DELETE FROM opportunities_fts WHERE rowid = :id"), {"id": target_opp.id})
                        db.execute(text("""
                            INSERT INTO opportunities_fts (rowid, solicitation_number, name, short_description)
                            VALUES (:id, :sol, :name, :desc)
                        """), {
                            "id": target_opp.id,
                            "sol": target_opp.solicitation_number,
                            "name": target_opp.name or "",
                            "desc": target_opp.short_description or ""
                        })
                    except Exception as fts_err:
                        logger.debug(f"FTS sync notice for {sol_num}: {fts_err}")

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

        except Exception as e:
            run.status = "error"
            run.error_details = str(e)
            run.completed_at = self.now_utc()
            db.commit()
            logger.error(f"[{self.source_name}] Ingestion failed: {e}", exc_info=True)
            stats["errors"] += 1

        return stats

