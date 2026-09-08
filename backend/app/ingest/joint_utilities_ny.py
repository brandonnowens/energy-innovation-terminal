"""Joint Utilities NY innovation adapter."""
from sqlalchemy.orm import Session
from app.ingest.utility_base import UtilityBaseAdapter

class JointUtilitiesNYAdapter(UtilityBaseAdapter):
    source_name = "joint_utilities_ny"
    source_url = "https://jointutilitiesofny.org/"
    utility_name = "Joint Utilities of NY"
    service_territory = "Statewide (Coordinated NY Utility Programs)"

    def ingest(self, db: Session) -> dict:
        def fetch_fn(session: Session, stats: dict) -> dict:
            programs = [
                {
                    "solicitation_number": "JUNY-NWA-2026",
                    "name": "Joint Utilities NWA Coordination",
                    "status": "open",
                    "short_description": "Coordinated non-wires alternatives across NY utilities",
                },
                {
                    "solicitation_number": "JUNY-DSIP-2026",
                    "name": "Distributed System Implementation Plan",
                    "status": "open",
                    "short_description": "Coordinated DER integration planning",
                },
                {
                    "solicitation_number": "JUNY-DATA-2026",
                    "name": "System Data Portal",
                    "status": "open",
                    "short_description": "Utility system data access for third-party developers",
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
