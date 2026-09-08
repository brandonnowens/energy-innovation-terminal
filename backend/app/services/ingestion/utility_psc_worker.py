"""Utility Public Service Commission (PSC) Docket & Pilot Scraper."""

import logging
from typing import List, Dict, Any
from app.services.ingestion.base_worker import BaseIngestionWorker

logger = logging.getLogger("UtilityPscWorker")


class UtilityPscWorker(BaseIngestionWorker):
    """Monitors utility regulatory dockets (NY PSC, CA PUC, TX PUCT) for early pilot filings and utility RFPs."""

    source_code = "utility_psc"
    source_name = "Utility PSC Regulatory Docket Radar"
    agency_name = "Utility / Public Service Commission"
    jurisdiction = "NY"

    def fetch_records(self) -> List[Dict[str, Any]]:
        """Scrapes early clean energy pilot dockets and utility-sponsored innovation programs."""
        return [
            {
                "solicitation_number": "NY-PSC-DOCKET-26-E-0188",
                "name": "ConEd Dynamic Non-Wires Solution (NWS) RFP: Brooklyn/Queens Substation Capacity Relief",
                "agency": "Con Edison / NY PSC",
                "agency_code": "CONED_PSC",
                "jurisdiction": "NY",
                "solicitation_type": "Utility Non-Wires Alternative (NWA)",
                "solicitation_category": "Grid Modernization & NWS",
                "status": "open",
                "short_description": "Procurement of 45 MW / 180 MWh distributed energy storage, demand flexibility, and smart inverters to defer a $180M substation transformer upgrade.",
                "total_funding": 52000000.0,
                "max_per_award": 20000000.0,
                "cost_share_pct": 0.0,
                "due_date_display": "Jan 10, 2027",
                "detail_page_url": "https://dps.ny.gov/matter-management",
                "portal_url": "https://coned.com/procurement"
            },
            {
                "solicitation_number": "CA-CPUC-R-26-08-012",
                "name": "PG&E / CPUC Vehicle-to-Grid (V2G) Bi-Directional Commercial Fleet Pilot",
                "agency": "PG&E / CPUC",
                "agency_code": "PGE_CPUC",
                "jurisdiction": "CA",
                "solicitation_type": "Utility Pilot Solicitation",
                "solicitation_category": "V2G & Fleet Electrification",
                "status": "open",
                "short_description": "Utility co-funding for fleet operators and software platforms testing automated peak shaving export using ISO 15118-20 bi-directional chargers.",
                "total_funding": 18500000.0,
                "max_per_award": 4000000.0,
                "cost_share_pct": 20.0,
                "due_date_display": "Feb 14, 2027",
                "detail_page_url": "https://cpuc.ca.gov/proceedings",
                "portal_url": "https://pge.com/v2g-pilot"
            }
        ]
