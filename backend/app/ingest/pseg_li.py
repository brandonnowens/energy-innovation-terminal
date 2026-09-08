"""PSEG Long Island innovation adapter."""
from sqlalchemy.orm import Session
from app.ingest.utility_base import UtilityBaseAdapter

class PSEGLongIslandAdapter(UtilityBaseAdapter):
    source_name = "pseg_li"
    source_url = "https://www.psegliny.com/aboutpseglongisland/proposalsandbids"
    utility_name = "PSEG Long Island"
    service_territory = "Long Island, Nassau, Suffolk Counties"

    def ingest(self, db: Session) -> dict:
        def fetch_fn(session: Session, stats: dict) -> dict:
            programs = [
                {
                    "solicitation_number": "PSEG-RFP-2026",
                    "name": "PSEG LI Energy Efficiency RFP",
                    "status": "open",
                    "short_description": "Energy efficiency program implementation for Long Island service territory. PSEG LI seeks qualified vendors to deliver residential and commercial energy efficiency programs.",
                    "vendor_registration_required": True,
                    "procurement_portal_url": "https://www.poweradvocate.com/",
                    "utility_program_type": "Innovation",
                },
                {
                    "solicitation_number": "PSEG-BESS-2026",
                    "name": "PSEG LI Bulk Energy Storage",
                    "status": "open",
                    "short_description": "Utility-scale energy storage procurement for Long Island grid reliability. Seeking battery storage and other technologies to meet peak demand and integrate renewables.",
                    "vendor_registration_required": True,
                    "procurement_portal_url": "https://www.poweradvocate.com/",
                    "utility_program_type": "NWA",
                },
                {
                    "solicitation_number": "PSEG-DSM-2026",
                    "name": "PSEG LI Demand-Side Management",
                    "status": "open",
                    "short_description": "Peak demand reduction programs including dynamic load management, demand response, and distributed energy resources for Long Island.",
                    "vendor_registration_required": True,
                    "procurement_portal_url": "https://www.poweradvocate.com/",
                    "utility_program_type": "DLM",
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
