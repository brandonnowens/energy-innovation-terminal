"""NYPA innovation adapter."""
from sqlalchemy.orm import Session
from app.ingest.utility_base import UtilityBaseAdapter

class NYPAAdapter(UtilityBaseAdapter):
    source_name = "nypa"
    source_url = "https://www.nypa.gov/procurement"
    utility_name = "NYPA"
    service_territory = "Statewide (NY Power Authority)"

    def ingest(self, db: Session) -> dict:
        def fetch_fn(session: Session, stats: dict) -> dict:
            programs = [
                {
                    "solicitation_number": "NYPA-AGILE-2026",
                    "name": "NYPA AGILe Innovation Testbed",
                    "status": "open",
                    "short_description": "Advanced Grid Innovation Laboratory for Energy",
                    "vendor_registration_required": True,
                    "procurement_portal_url": "https://www.ariba.com/",
                },
                {
                    "solicitation_number": "NYPA-VISION-2026",
                    "name": "VISION2030 Technology Partnerships",
                    "status": "open",
                    "short_description": "Strategic innovation partnerships",
                    "vendor_registration_required": True,
                    "procurement_portal_url": "https://www.ariba.com/",
                },
                {
                    "solicitation_number": "NYPA-TRANS-2026",
                    "name": "Transmission Modernization RFP",
                    "status": "open",
                    "short_description": "Grid transmission upgrade projects",
                    "vendor_registration_required": True,
                    "procurement_portal_url": "https://www.ariba.com/",
                },
                {
                    "solicitation_number": "NYPA-EV-2026",
                    "name": "EVolve NY Charging Infrastructure",
                    "status": "open",
                    "short_description": "EV fast-charging network expansion",
                    "vendor_registration_required": True,
                    "procurement_portal_url": "https://www.ariba.com/",
                },
            ]
            for p in programs:
                res = self._upsert_opportunity(
                    db=session,
                    sol_num=p["solicitation_number"],
                    opp_data=p,
                    categories=self.infer_categories(p["short_description"])
                )
                stats[res] += 1
            return stats

        return self._run_ingestion(db, fetch_fn)
