"""NY PSC innovation adapter."""
from sqlalchemy.orm import Session
from app.ingest.utility_base import UtilityBaseAdapter

class NYPSCAdapter(UtilityBaseAdapter):
    source_name = "ny_psc"
    source_url = "https://www3.dps.ny.gov/W/PSCWeb.nsf/All/C4A2E16B51D2F68985257687006F396B"
    utility_name = "NY PSC"
    service_territory = "Statewide (Regulatory)"
    regulatory_body = "NY PSC"

    def _build_opportunity_defaults(self) -> dict:
        defaults = super()._build_opportunity_defaults()
        defaults["org_type"] = "government"
        defaults["jurisdiction"] = "state_ny"
        return defaults

    def ingest(self, db: Session) -> dict:
        def fetch_fn(session: Session, stats: dict) -> dict:
            programs = [
                {
                    "solicitation_number": "NYPSC-REV-2026",
                    "name": "REV Demonstration Projects",
                    "status": "open",
                    "short_description": "Reforming the Energy Vision mandated utility demonstrations",
                },
                {
                    "solicitation_number": "NYPSC-DSIP-2026",
                    "name": "Distributed System Implementation Plans",
                    "status": "open",
                    "short_description": "Utility grid modernization and DER integration",
                },
                {
                    "solicitation_number": "NYPSC-VDER-2026",
                    "name": "Value of DER (VDER) Proceedings",
                    "status": "open",
                    "short_description": "Value stack compensation for distributed energy",
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
