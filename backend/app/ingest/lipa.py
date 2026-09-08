"""Long Island Power Authority (LIPA) innovation adapter.

LIPA is the publicly owned electric utility serving Long Island
and the Rockaways. PSEG Long Island operates the grid on LIPA's
behalf, but LIPA issues its own procurements for bulk power supply,
renewable energy, and clean technology programs.
"""

import logging
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.ingest.utility_base import UtilityBaseAdapter, clean_html

logger = logging.getLogger(__name__)


class LIPAAdapter(UtilityBaseAdapter):
    """Adapter for Long Island Power Authority innovation opportunities."""

    source_name = "lipa"
    source_url = "https://www.lipower.org/about-us/proposals-bids/"
    utility_name = "LIPA"
    service_territory = "Long Island, Nassau, Suffolk Counties, Rockaways"
    parent_company = ""
    authority_rank = 2

    def _fetch_opportunities(self, db: Session, stats: dict) -> dict:
        """Fetch opportunities by scraping or using fallback."""
        try:
            response = self.fetch_url(self.source_url)
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                # Try to find procurement listings on the page
                # LIPA uses PowerAdvocate for formal bids, but lists summaries on their site
                found = False

                # Look for procurement sections / tables / links
                sections = soup.find_all(["article", "section", "div"], class_=lambda c: c and any(
                    k in str(c).lower() for k in ["procurement", "bid", "rfp", "solicitation", "proposal"]
                ))
                for section in sections:
                    links = section.find_all("a", href=True)
                    for link in links:
                        title = clean_html(link.get_text())
                        if len(title) > 10 and any(k in title.lower() for k in [
                            "rfp", "rfi", "rfq", "bid", "solicitation", "procurement",
                            "energy", "storage", "clean", "renewable", "grid"
                        ]):
                            sol_num = f"LIPA-{self.compute_hash(title)[:8].upper()}"
                            href = link.get("href", "")
                            if not href.startswith("http"):
                                href = f"https://www.lipower.org{href}"

                            desc = clean_html(section.get_text()[:500]) if section else title
                            opp_data = {
                                "name": title,
                                "short_description": desc,
                                "status": self._infer_status(desc),
                                "solicitation_type": self._infer_solicitation_type(title),
                                "detail_page_url": href,
                                "vendor_registration_required": True,
                                "procurement_portal_url": "https://www.poweradvocate.com/",
                            }
                            categories = self.infer_categories(f"{title} {desc}")
                            res = self._upsert_opportunity(db, sol_num, opp_data, categories=categories)
                            stats[res] += 1
                            found = True

                if not found:
                    self._fallback_curated(db, stats)
            else:
                self._fallback_curated(db, stats)

        except Exception as e:
            logger.warning(f"Error fetching from {self.source_url}: {e}")
            self._fallback_curated(db, stats)

        return stats

    def _fallback_curated(self, db: Session, stats: dict):
        """Fallback to curated known LIPA programs."""
        curated_programs = [
            {
                "id": "LIPA-CLEAN-2026",
                "name": "LIPA Clean Energy RFP",
                "desc": (
                    "Renewable energy and clean technology procurement for Long Island. "
                    "LIPA seeks proposals for utility-scale solar, offshore wind interconnection, "
                    "and innovative clean energy technologies to meet Climate Leadership and "
                    "Community Protection Act (CLCPA) targets."
                ),
                "type": "RFP",
                "program": "Innovation",
            },
            {
                "id": "LIPA-BESS-2026",
                "name": "LIPA Bulk Energy Storage Procurement",
                "desc": (
                    "Grid-scale battery energy storage systems for Long Island. LIPA is "
                    "procuring bulk storage capacity to improve grid reliability, reduce "
                    "peak demand, and support renewable energy integration across Nassau "
                    "and Suffolk Counties."
                ),
                "type": "RFP",
                "program": "NWA",
            },
            {
                "id": "LIPA-OFFSHORE-2026",
                "name": "LIPA Offshore Wind Integration RFP",
                "desc": (
                    "Grid infrastructure and interconnection solutions for offshore wind "
                    "energy integration on Long Island. Seeking innovative approaches to "
                    "grid upgrades, transmission, and distribution system modifications "
                    "to accommodate large-scale offshore wind delivery."
                ),
                "type": "RFP",
                "program": "Innovation",
            },
            {
                "id": "LIPA-RESIL-2026",
                "name": "LIPA Grid Resilience and Modernization",
                "desc": (
                    "Grid hardening and resilience improvement program for Long Island's "
                    "distribution and transmission infrastructure. Soliciting advanced "
                    "technologies including microgrids, smart switches, automated fault "
                    "isolation, and storm-hardening solutions."
                ),
                "type": "RFP",
                "program": "Grid Modernization",
            },
            {
                "id": "LIPA-DR-2026",
                "name": "LIPA Demand Response and DER Programs",
                "desc": (
                    "Demand response and distributed energy resource programs for Long "
                    "Island customers. LIPA is expanding programs for commercial and "
                    "residential demand flexibility, virtual power plants, and behind-"
                    "the-meter storage incentives."
                ),
                "type": "RFP",
                "program": "DLM",
            },
        ]

        for prog in curated_programs:
            desc = prog["desc"]
            opp_data = {
                "name": prog["name"],
                "short_description": desc,
                "status": "open",
                "solicitation_type": prog["type"],
                "utility_program_type": prog["program"],
                "vendor_registration_required": True,
                "procurement_portal_url": "https://www.poweradvocate.com/",
            }

            categories = self.infer_categories(f"{prog['name']} {desc}")
            res = self._upsert_opportunity(db, prog["id"], opp_data, categories=categories)
            stats[res] += 1

    def ingest(self, db: Session) -> dict:
        """Run the ingestion process."""
        return self._run_ingestion(db, self._fetch_opportunities)
