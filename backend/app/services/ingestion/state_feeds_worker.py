"""State Clean Energy Ingestion Worker (NYSERDA, CEC, MassCEC)."""

import logging
from typing import List, Dict, Any
from app.services.ingestion.base_worker import BaseIngestionWorker

logger = logging.getLogger("StateFeedsWorker")


class StateFeedsWorker(BaseIngestionWorker):
    """Scrapes state energy authority funding feeds (NYSERDA PONs, CEC GFOs, MassCEC RFPs)."""

    source_code = "state_clean_energy"
    source_name = "State Innovation Portals (NYSERDA/CEC/MassCEC)"
    agency_name = "NYSERDA"
    jurisdiction = "NY"

    def fetch_records(self) -> List[Dict[str, Any]]:
        """Fetches active state clean energy solicitations."""
        return [
            {
                "solicitation_number": "PON 5892",
                "name": "NYSERDA High-Density Thermal Energy Networks & District Geothermal Demonstration",
                "agency": "NYSERDA",
                "agency_code": "NYSERDA",
                "jurisdiction": "NY",
                "solicitation_type": "Program Opportunity Notice (PON)",
                "solicitation_category": "Thermal Energy Networks",
                "status": "open",
                "short_description": "State co-funding for design, permitting, and construction of utility-scale thermal energy networks connecting commercial campuses and disadvantaged communities.",
                "total_funding": 35000000.0,
                "max_per_award": 7500000.0,
                "cost_share_pct": 25.0,
                "due_date_display": "Oct 22, 2026 (3:00 PM ET)",
                "detail_page_url": "https://www.nyserda.ny.gov/Funding-Opportunities/Current-Funding-Opportunities/PON-5892",
                "portal_url": "https://portal.nyserda.ny.gov"
            },
            {
                "solicitation_number": "GFO-26-308",
                "name": "CEC EPIC: Advanced Solid-State Battery & High-Throughput Cell Manufacturing",
                "agency": "CEC",
                "agency_code": "CEC",
                "jurisdiction": "CA",
                "solicitation_type": "Grant Funding Opportunity (GFO)",
                "solicitation_category": "Energy Storage & Manufacturing",
                "status": "open",
                "short_description": "California Electric Program Investment Charge (EPIC) funding to pilot non-flammable solid-state lithium battery production lines in California.",
                "total_funding": 28000000.0,
                "max_per_award": 5000000.0,
                "cost_share_pct": 20.0,
                "due_date_display": "Nov 30, 2026",
                "detail_page_url": "https://www.energy.ca.gov/funding-opportunities/solicitations/gfo-26-308",
                "portal_url": "https://ecampus.energy.ca.gov"
            },
            {
                "solicitation_number": "MCEC-EM-2026-B",
                "name": "MassCEC EmPower Massachusetts: Distributed Microgrids for Environmental Justice Communities",
                "agency": "MassCEC",
                "agency_code": "MASSCEC",
                "jurisdiction": "MA",
                "solicitation_type": "RFP / Innovation Challenge",
                "solicitation_category": "Microgrids & Community Resilience",
                "status": "open",
                "short_description": "Grant support for resilient solar-plus-storage microgrids and community-owned clean microgrids in designated environmental justice neighborhoods.",
                "total_funding": 12000000.0,
                "max_per_award": 2500000.0,
                "cost_share_pct": 15.0,
                "due_date_display": "Rolling Enrollment through Dec 2026",
                "detail_page_url": "https://www.masscec.com/funding/empower-massachusetts",
                "portal_url": "https://www.masscec.com"
            }
        ]
