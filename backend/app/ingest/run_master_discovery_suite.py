"""
Master Runner for Deep Discovery Suite (Patents, VC, and Relational Linking).
"""

import sys
import logging
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal, init_db
from app.ingest.deep_patent_discovery import DeepPatentDiscovery
from app.ingest.deep_vc_discovery import DeepVCDiscovery
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DeepDiscoveryRunner")


def run_master_suite():
    print("=================================================================")
    print("U.S. ENERGY INNOVATION DATABASE DEEP PATENT & VC DISCOVERY MASTER INGESTION SUITE")
    print("=================================================================")

    init_db()
    db = SessionLocal()

    try:
        # Step 1: Deep Patent Discovery
        print("\n[STEP 1/3] Executing Deep Patent Discovery & Ingestion...")
        pat_engine = DeepPatentDiscovery()
        pat_res = pat_engine.run(db)
        print(f"  --> Ingested {pat_res['patents_ingested']} deep-tech patents.")

        # Step 2: Deep VC Discovery
        print("\n[STEP 2/3] Executing Deep VC & Institutional Financing Discovery...")
        vc_engine = DeepVCDiscovery()
        vc_res = vc_engine.run(db)
        print(f"  --> Ingested {vc_res['rounds_ingested']} private financing rounds totaling ${vc_res['total_vc_volume']:,.0f} USD.")

        # Step 3: Link Patents to Opportunities via Award Solicitation Numbers
        print("\n[STEP 3/3] Cross-linking Patents & VC directly to Solicitations & Programs...")
        db.execute(text("""
            UPDATE recipient_patents
            SET award_id = (
                SELECT id FROM awards
                WHERE awards.external_award_id LIKE '%' || recipient_patents.grant_contract_id || '%'
                   OR awards.solicitation_number LIKE '%' || recipient_patents.grant_contract_id || '%'
                LIMIT 1
            )
            WHERE award_id IS NULL AND grant_contract_id IS NOT NULL;
        """))
        db.commit()

        # Auditing Metrics
        total_pats = db.execute(text("SELECT COUNT(*) FROM recipient_patents")).scalar()
        total_vcs = db.execute(text("SELECT COUNT(*), SUM(amount_usd) FROM recipient_investments")).fetchone()
        distinct_orgs = db.execute(text("SELECT COUNT(DISTINCT recipient_id) FROM recipient_patents")).scalar()
        vc_orgs = db.execute(text("SELECT COUNT(DISTINCT recipient_id) FROM recipient_investments")).scalar()

        print("\n=================================================================")
        print("MASTER ASSET INVENTORY:")
        print(f"  • Verified USPTO Bayh-Dole Patents:     {total_pats}")
        print(f"  • Organizations with Granted Patents:   {distinct_orgs}")
        print(f"  • Private VC Financing Rounds:          {total_vcs[0]}")
        print(f"  • Total Private VC Leveraged Tracked:   ${total_vcs[1]:,.2f} ({total_vcs[1]/1e9:.2f}B USD)")
        print(f"  • Organizations with Tracked VC Rounds: {vc_orgs}")
        print("=================================================================")

    except Exception as e:
        db.rollback()
        logger.error(f"Error during deep discovery: {e}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_master_suite()
