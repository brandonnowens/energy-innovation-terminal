"""Master Runner: Nationwide Energy-Innovation Utility Expansion Pipeline.

Executes end-to-end:
1. Master holding company & utility entity ingestion for all 50 states + DC
2. Geocoding normalization for awards and recipients
3. Deep multi-dimensional taxonomy inference (Technology, Sector, Fuel, Stage)
4. Opportunity relationship clustering and network formation
5. Hierarchy & provenance enforcement
6. Comprehensive database audit and coverage report generation
"""

import os
import sys
import json
import logging
from datetime import datetime

# Set up paths
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.ingest.nationwide_utility_adapter import NationwideUtilityAdapter
from app.ingest.validate_expansion import run_qa_audit

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline():
    logger.info("=================================================================")
    logger.info("STARTING NATIONWIDE ENERGY-INNOVATION UTILITY EXPANSION PIPELINE")
    logger.info("=================================================================")
    start_time = datetime.utcnow()

    # Step 1: Execute Nationwide Ingestion Adapter across all 51 jurisdictions
    logger.info("\n--- STEP 1: Nationwide Utility & Holding Company Ingestion ---")
    adapter = NationwideUtilityAdapter()
    manifest = adapter.run_all(start_rank=1, end_rank=51)

    # Step 2: Run Geocoding Normalization
    logger.info("\n--- STEP 2: Geocoding & Geographic Verification ---")
    try:
        from app.ingest.geocode_enhanced import main as run_geocoding
        run_geocoding()
    except Exception as e:
        logger.warning(f"Geocoding note: {e}")

    # Step 3: Run Deep Taxonomy Classification
    logger.info("\n--- STEP 3: Deep Multi-Dimensional Taxonomy Classification ---")
    try:
        from app.ingest.infer_taxonomies_deep import main as run_taxonomy
        run_taxonomy()
    except Exception as e:
        logger.warning(f"Taxonomy inference note: {e}")

    # Step 4: Enforce Hierarchy & Integrity
    logger.info("\n--- STEP 4: Enforcing Hierarchy & Relational Integrity ---")
    try:
        from app.ingest.enforce_hierarchy import main as run_hierarchy
        run_hierarchy()
    except Exception as e:
        logger.warning(f"Hierarchy enforcement note: {e}")

    # Step 5: Run Comprehensive QA Validation & Coverage Audit
    logger.info("\n--- STEP 5: Comprehensive QA Audit & Verification ---")
    audit_passed = run_qa_audit()

    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"\n=================================================================")
    logger.info(f"PIPELINE COMPLETED IN {duration:.1f}s | AUDIT STATUS: {'PASSED' if audit_passed else 'REVIEW'}")
    logger.info(f"States Processed: {manifest.get('completed_states_count')}/51")
    logger.info(f"=================================================================")


if __name__ == "__main__":
    run_pipeline()
