"""Central Hudson innovation adapter."""
from sqlalchemy.orm import Session
from app.ingest.utility_base import UtilityBaseAdapter

class CentralHudsonAdapter(UtilityBaseAdapter):
    source_name = "central_hudson"
    source_url = "https://www.cenhud.com/en/my-energy/non-wires-alternatives/"
    utility_name = "Central Hudson"
    service_territory = "Mid-Hudson Valley, Dutchess, Ulster, Greene, Columbia Counties"
    parent_company = "Fortis Inc."

    def ingest(self, db: Session) -> dict:
        def fetch_fn(session: Session, stats: dict) -> dict:
            programs = [
                {
                    "solicitation_number": "CENHUD-NWA-2026",
                    "name": "Central Hudson NWA Program",
                    "status": "open",
                    "short_description": "Non-wires alternatives for Mid-Hudson",
                },
                {
                    "solicitation_number": "CENHUD-UTEN-2026",
                    "name": "Utility Thermal Energy Network",
                    "status": "open",
                    "short_description": "District thermal energy network pilot",
                },
                {
                    "solicitation_number": "CENHUD-BESS-2026",
                    "name": "Bulk Energy Storage RFP",
                    "status": "open",
                    "short_description": "Grid-scale energy storage",
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
