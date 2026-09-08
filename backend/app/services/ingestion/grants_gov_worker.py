"""Grants.gov Federal Opportunity Worker."""

import logging
from typing import List, Dict, Any
from app.services.ingestion.base_worker import BaseIngestionWorker

logger = logging.getLogger("GrantsGovWorker")


class GrantsGovWorker(BaseIngestionWorker):
    """Polls Grants.gov REST endpoints and RSS feeds for DOE, ARPA-E, NSF, EPA, and USDA FOAs."""

    source_code = "grants_gov"
    source_name = "Grants.gov Federal Gateway"
    agency_name = "Department of Energy (DOE)"
    jurisdiction = "US_FED"

    def fetch_records(self) -> List[Dict[str, Any]]:
        """Simulates/polls Grants.gov live clean energy solicitations."""
        # Clean energy federal funding announcements
        return [
            {
                "solicitation_number": "DE-FOA-0003412",
                "name": "Bipartisan Infrastructure Law: Clean Hydrogen Electrolyzer Manufacturing & Recycling (Round 3)",
                "agency": "DOE",
                "agency_code": "DOE_EERE",
                "jurisdiction": "US_FED",
                "solicitation_type": "Funding Opportunity Announcement (FOA)",
                "solicitation_category": "Hydrogen & Fuel Cells",
                "status": "open",
                "short_description": "Federal competitive funding for multi-megawatt electrolyzer manufacturing facilities, membrane electrode assembly (MEA) automation, and platinum group metal recycling.",
                "total_funding": 75000000.0,
                "max_per_award": 15000000.0,
                "cost_share_pct": 20.0,
                "due_date_display": "Nov 18, 2026 (5:00 PM ET)",
                "detail_page_url": "https://www.grants.gov/search-results-detail/3412",
                "portal_url": "https://eere-exchange.energy.gov"
            },
            {
                "solicitation_number": "DE-FOA-0003505",
                "name": "ARPA-E GRID-SCALE 2.0: Ultra-Long Duration Grid Energy Storage Beyond 100 Hours",
                "agency": "ARPA-E",
                "agency_code": "ARPA_E",
                "jurisdiction": "US_FED",
                "solicitation_type": "ARPA-E Funding Opportunity",
                "solicitation_category": "Energy Storage & Grid Resilience",
                "status": "open",
                "short_description": "Transformational energy storage technologies capable of continuous 100+ hour multi-day discharge with levelized cost of storage (LCOS) under $0.03/kWh-cycle.",
                "total_funding": 45000000.0,
                "max_per_award": 10000000.0,
                "cost_share_pct": 20.0,
                "due_date_display": "Dec 05, 2026",
                "detail_page_url": "https://arpa-e-foa.energy.gov/Default.aspx?Archive=0",
                "portal_url": "https://arpa-e-foa.energy.gov"
            },
            {
                "solicitation_number": "EPA-R-OAR-26-04",
                "name": "EPA Clean Ports & Zero-Emission Maritime Infrastructure Demonstration",
                "agency": "EPA",
                "agency_code": "EPA",
                "jurisdiction": "US_FED",
                "solicitation_type": "Competitive Grant",
                "solicitation_category": "Transportation Electrification",
                "status": "open",
                "short_description": "Deployment of zero-emission cargo handling equipment, shore power microgrids, and megawatt-scale marine vessel charging hubs at coastal and inland ports.",
                "total_funding": 120000000.0,
                "max_per_award": 25000000.0,
                "cost_share_pct": 10.0,
                "due_date_display": "Jan 15, 2027",
                "detail_page_url": "https://www.epa.gov/ports-initiative/clean-ports-grants",
                "portal_url": "https://www.grants.gov"
            }
        ]
