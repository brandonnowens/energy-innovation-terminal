"""
Master Pipeline Runner for Venture, Patent, ESD, and Multi-State Expansion.

Executes all discovery adapters, reconciles entity linkages, recomputes macro
leverage ratios, and audits database completeness.
"""

import sys
import logging
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal, init_db
from app.ingest.empire_state_development import EmpireStateDevelopmentAdapter
from app.ingest.state_economic_development import StateEconomicDevelopmentAdapter
from app.ingest.foundations_adapter import FoundationsAdapter
from app.ingest.patents_adapter import PatentsAdapter
from app.ingest.venture_adapter import VentureAdapter
from sqlalchemy import text


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PipelineRunner")


def run_pipeline():
    print("=================================================================")
    print("MASTER ATTRIBUTIONS, ESD & MULTI-STATE INGESTION PIPELINE")
    print("=================================================================")

    init_db()
    db = SessionLocal()

    try:
        # 1. Ingest Empire State Development (ESD) & NY Ventures
        print("\n[STEP 1/5] Running Empire State Development (ESD & NY Ventures) Adapter...")
        with EmpireStateDevelopmentAdapter() as esd_adapter:
            esd_res = esd_adapter.ingest(db)
            print(f"  --> ESD Ingestion: Added={esd_res.get('added', 0)}, Updated={esd_res.get('updated', 0)}")

        # 2. Ingest Multi-State Economic Development Agencies
        print("\n[STEP 2/6] Running Multi-State Economic Development Agencies Adapter...")
        with StateEconomicDevelopmentAdapter() as state_adapter:
            state_res = state_adapter.ingest(db)
            print(f"  --> State Economic Development Ingestion: Added={state_res.get('added', 0)}, Updated={state_res.get('updated', 0)}")

        # 3. Ingest Philanthropic Foundations & Climate Non-Profits
        print("\n[STEP 3/6] Running Philanthropic Foundations & Non-Profits Adapter...")
        with FoundationsAdapter() as found_adapter:
            found_res = found_adapter.ingest(db)
            print(f"  --> Foundations Ingestion: Orgs Added={found_res.get('organizations_added', 0)}, Opps Added={found_res.get('opportunities_added', 0)}")

        # 4. Ingest USPTO Bayh-Dole Patents across 12 domains
        print("\n[STEP 4/6] Running USPTO Bayh-Dole Clean Energy Patents Adapter...")
        pat_adapter = PatentsAdapter()
        pat_res = pat_adapter.run(db)
        print(f"  --> Ingested {pat_res['patents_ingested']} patents across {pat_res['linked_awards']} awards.")


        # 4. Ingest Venture Capital Financing & Institutional Syndicates
        print("\n[STEP 4/5] Running Venture Capital & Institutional Equity Adapter...")
        vc_adapter = VentureAdapter()
        vc_res = vc_adapter.run(db)
        print(f"  --> Ingested {vc_res['rounds_ingested']} VC rounds totaling ${vc_res['total_vc_volume']:,.0f} USD.")

        # 5. Multi-State Jurisdiction Normalization & Coverage
        print("\n[STEP 5/5] Running Multi-State Jurisdiction Enforcer...")
        db.execute(text("""
            UPDATE opportunities SET jurisdiction = 'state_ny' WHERE (agency IN ('NYSERDA', 'Empire State Development', 'ESD') OR agency LIKE '%NY%') AND (jurisdiction IS NULL OR jurisdiction = '' OR jurisdiction = 'NY');
        """))
        db.execute(text("""
            UPDATE opportunities SET jurisdiction = 'state_ca' WHERE (agency IN ('CEC', 'California GO-Biz', 'CalSEED') OR agency LIKE '%California%') AND (jurisdiction IS NULL OR jurisdiction = '' OR jurisdiction = 'CA');
        """))
        db.execute(text("""
            UPDATE opportunities SET jurisdiction = 'state_ma' WHERE (agency IN ('MassCEC', 'MassVentures') OR agency LIKE '%Mass%') AND (jurisdiction IS NULL OR jurisdiction = '' OR jurisdiction = 'MA');
        """))
        db.execute(text("""
            UPDATE opportunities SET jurisdiction = 'state_oh' WHERE agency = 'JobsOhio';
        """))
        db.execute(text("""
            UPDATE opportunities SET jurisdiction = 'state_mi' WHERE agency = 'MEDC';
        """))
        db.execute(text("""
            UPDATE opportunities SET jurisdiction = 'state_pa' WHERE agency = 'Ben Franklin Tech Partners';
        """))
        db.execute(text("""
            UPDATE opportunities SET jurisdiction = 'state_ct' WHERE agency = 'Connecticut Innovations';
        """))
        db.execute(text("""
            UPDATE opportunities SET jurisdiction = 'state_md' WHERE agency = 'TEDCO';
        """))
        db.execute(text("""
            UPDATE opportunities SET jurisdiction = 'state_va' WHERE agency = 'VIPC';
        """))
        db.execute(text("""
            UPDATE opportunities SET jurisdiction = 'state_co' WHERE agency = 'Colorado OEDIT';
        """))
        db.execute(text("""
            UPDATE opportunities SET jurisdiction = 'state_mn' WHERE agency = 'MN DEED';
        """))
        db.execute(text("""
            UPDATE opportunities SET jurisdiction = 'federal' WHERE agency IN ('DOE', 'NSF', 'DOD', 'NASA', 'EPA', 'USDA', 'ARPA-E', 'DOT') AND (jurisdiction IS NULL OR jurisdiction = '' OR jurisdiction = 'US_FED');
        """))
        db.commit()
        print("  --> Enforced jurisdiction metadata across federal and state records.")

        # Reconcile counts
        total_pats = db.execute(text("SELECT COUNT(*) FROM recipient_patents")).scalar()
        total_vcs = db.execute(text("SELECT COUNT(*), SUM(amount_usd) FROM recipient_investments")).fetchone()
        esd_opps = db.execute(text("SELECT COUNT(*) FROM opportunities WHERE agency = 'Empire State Development'")).scalar()
        state_opps = db.execute(text("SELECT COUNT(*) FROM opportunities WHERE org_type = 'economic_development'")).scalar()
        org_count = db.execute(text("SELECT COUNT(*) FROM organizations")).scalar()

        print("\n=================================================================")
        print("FINAL ASSET INGESTION SUMMARY:")
        print(f"  • Total Organizations in Database:        {org_count}")
        print(f"  • Verified USPTO Bayh-Dole Patents:       {total_pats}")
        print(f"  • Institutional VC Funding Rounds:        {total_vcs[0]} (${total_vcs[1]:,.0f} USD)")
        print(f"  • Empire State Development (ESD) Opps:    {esd_opps}")
        print(f"  • State Economic Development Opps:        {state_opps}")
        print("=================================================================")

    except Exception as e:
        db.rollback()
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_pipeline()
