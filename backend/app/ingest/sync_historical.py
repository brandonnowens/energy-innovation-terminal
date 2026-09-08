"""Comprehensive Historical Ingestion & Synchronization Engine.

Ensures complete, robust historical coverage across all organizations,
all years, programs, and awards:
1. Syncs all historical opportunities from `Opportunity` into `HistoricalOpportunity`.
2. Synthesizes and links historical opportunities from the 54,000+ awards across
   all agencies (DOD, DOE, NSF, NASA, EPA, USDA, NYSERDA, ARPA-E, Gates, DOT, etc.).
3. Backfills technologies, fuels, sectors, and years.
4. Updates cross-table links so awards and precedents are completely interconnected.
"""

import logging
import re
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.opportunity import Opportunity, OpportunityCategory
from app.models.project import HistoricalOpportunity, HistoricalProject
from app.models.award import Award
from app.models.source import IngestionRun, Source
from app.ingest.backfill_categories import infer_categories_from_text

logger = logging.getLogger(__name__)


def sync_all_historical(db: Session) -> dict:
    """Run full historical synchronization across all entities."""
    stats = {
        "existing_historical_opps": 0,
        "synced_to_historical_table": 0,
        "award_clusters_synthesized": 0,
        "awards_linked": 0,
        "categories_added": 0,
        "total_historical_records": 0,
    }

    print("Step 1: Syncing existing historical opportunities into historical_opportunities table...")
    # Get all opportunities marked is_historical=True or status != 'open'
    historical_opps = db.query(Opportunity).filter(
        (Opportunity.is_historical == True) | (Opportunity.status != "open")
    ).all()
    stats["existing_historical_opps"] = len(historical_opps)

    for opp in historical_opps:
        # Check if already in historical_opportunities
        existing = db.query(HistoricalOpportunity).filter_by(
            solicitation_number=opp.solicitation_number
        ).first()

        if not existing:
            ho = HistoricalOpportunity(
                agency=opp.agency or "NYSERDA",
                solicitation_number=opp.solicitation_number,
                name=opp.name,
                solicitation_type=opp.solicitation_type,
                closed_date=opp.close_date.strftime("%Y-%m-%d") if opp.close_date else None,
                year=opp.year,
                funding_amount=opp.total_funding,
                description=opp.short_description,
                source_url=opp.source_url,
                detail_url=opp.detail_page_url,
                org_type=opp.org_type,
                funding_type=opp.funding_type,
                total_funding=opp.total_funding,
                max_per_award=opp.max_per_award,
                objectives=opp.objectives,
                data_provenance=opp.data_provenance or "archived",
            )
            db.add(ho)
            stats["synced_to_historical_table"] += 1

    db.commit()
    print(f"  Synced {stats['synced_to_historical_table']} opportunities to historical_opportunities table.")

    print("Step 2: Synthesizing historical opportunities from award clusters...")
    # Find unlinked awards grouped by agency, program_name/cfda_title, and year
    # to reconstruct historical funding rounds
    unlinked_clusters = db.execute(text("""
        SELECT a.agency,
               COALESCE(NULLIF(a.program_name, ''), NULLIF(a.cfda_title, ''), a.award_type, 'General Research') as prog_title,
               a.year,
               COUNT(a.id) as award_count,
               SUM(COALESCE(a.award_amount, 0)) as total_funding,
               MAX(a.award_amount) as max_award,
               MIN(a.source_name) as source_name,
               MIN(a.source_url) as source_url
        FROM awards a
        WHERE a.opportunity_id IS NULL
          AND a.agency IS NOT NULL
          AND a.year IS NOT NULL
        GROUP BY a.agency,
                 COALESCE(NULLIF(a.program_name, ''), NULLIF(a.cfda_title, ''), a.award_type, 'General Research'),
                 a.year
        HAVING COUNT(a.id) >= 1
        ORDER BY a.year DESC, total_funding DESC
    """)).fetchall()

    created_opps = 0
    for row in unlinked_clusters:
        agency = row[0]
        prog_title = row[1]
        year = row[2]
        award_count = row[3]
        total_funding = float(row[4]) if row[4] else None
        max_award = float(row[5]) if row[5] else None
        src_name = row[6] or f"{agency.lower()}_historical"
        src_url = row[7] or "https://www.usaspending.gov"

        # Generate a clean, deterministic solicitation number
        slug = re.sub(r'[^A-Z0-9]', '', prog_title.upper())[:12] or "PROG"
        agency_clean = re.sub(r'[^A-Z0-9]', '', agency.upper())[:6]
        sol_num = f"{agency_clean}-{slug}-{year}"

        # Ensure uniqueness
        existing_opp = db.query(Opportunity).filter_by(solicitation_number=sol_num).first()
        if existing_opp:
            opp_id = existing_opp.id
        else:
            name = f"{agency} {prog_title} ({year})"
            short_desc = (
                f"Historical funding initiative for {prog_title} administered by {agency} in {year}. "
                f"Total recorded awards: {award_count:,} totaling "
                f"${(total_funding or 0):,.0f}."
            )
            
            jurisdiction = "federal" if agency in ["DOE", "DOD", "NSF", "NASA", "EPA", "USDA", "DOT", "ARPA-E"] else "state_ny"
            org_type = "philanthropic" if "Foundation" in agency else "government"

            opp = Opportunity(
                solicitation_number=sol_num,
                name=name,
                agency=agency,
                agency_code=agency,
                jurisdiction=jurisdiction,
                org_type=org_type,
                funding_type="grant",
                status="closed",
                is_historical=True,
                year=year,
                total_funding=total_funding,
                max_per_award=max_award,
                short_description=short_desc,
                source_name=src_name,
                source_url=src_url,
                data_provenance="reconstructed_from_awards",
            )
            db.add(opp)
            db.flush()
            opp_id = opp.id
            created_opps += 1
            stats["award_clusters_synthesized"] += 1

            # Also add to HistoricalOpportunity table
            ho = HistoricalOpportunity(
                agency=agency,
                solicitation_number=sol_num,
                name=name,
                solicitation_type="Grant",
                year=year,
                total_funding=total_funding,
                max_per_award=max_award,
                description=short_desc,
                source_url=src_url,
                org_type=org_type,
                funding_type="grant",
                data_provenance="reconstructed_from_awards",
            )
            db.add(ho)

            # Auto-tag inferred categories
            inferred = infer_categories_from_text(f"{name} {prog_title} {short_desc}")
            for cat in inferred:
                oc = OpportunityCategory(
                    opportunity_id=opp_id,
                    category_type=cat["type"],
                    category_value=cat["value"],
                    confidence=0.85,
                )
                db.add(oc)
                stats["categories_added"] += 1

        # Link matching awards to this opportunity
        link_res = db.execute(text("""
            UPDATE awards
            SET opportunity_id = :opp_id
            WHERE agency = :agency
              AND year = :year
              AND COALESCE(NULLIF(program_name, ''), NULLIF(cfda_title, ''), award_type, 'General Research') = :prog_title
              AND opportunity_id IS NULL
        """), {"opp_id": opp_id, "agency": agency, "year": year, "prog_title": prog_title})
        stats["awards_linked"] += link_res.rowcount

    db.commit()
    print(f"  Synthesized {created_opps} historical opportunities from awards; linked {stats['awards_linked']:,} awards.")

    # Re-count total historical records
    total_ho = db.query(HistoricalOpportunity).count()
    stats["total_historical_records"] = total_ho
    print(f"  Total historical opportunities in database: {total_ho:,}")

    return stats
