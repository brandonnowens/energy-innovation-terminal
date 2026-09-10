"""
High-Performance Concurrent Batch Rerun of All U.S. Energy Innovation Database Strategic Reports.
Extracts verified database context (including technology profiles, cost curves,
fuel vectors, policy standards, and regulatory matrices), generates executive
narratives, updates PostgreSQL reports table, and verifies PDF monograph generation.
"""

import os
import sys
import io
import json
import shutil
import logging
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from app.database import SessionLocal
from app.models.community import Report
from app.engine.report_aggregator import ReportContextAggregator, PRESET_REFERENCE_MAPPINGS
from app.engine.ai_report_author import author_report_with_openai
from app.engine.specialized_generators.dispatcher import generate_specialized_monograph, GENERATORS_MAP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("rerun_reports")

def process_preset(preset_id: str):
    db = SessionLocal()
    agg = ReportContextAggregator(db)
    result = {"preset_id": preset_id, "success": False, "pdf_success": False, "error": None}

    try:
        # 1. Aggregate context with technology, fuel, policy, and regulatory matrices
        context = agg.aggregate_by_preset(preset_id)
        tech_count = len(context.get("technology_reference", []))
        pol_count = len(context.get("policy_standards", []))
        fuel_count = len(context.get("fuel_vectors", []))
        reg_gates = len(context.get("regulatory_matrix", {}).get("critical_gates", []))

        # 2. Author executive strategic narrative
        narrative = author_report_with_openai(preset_id, context, force_refresh=True)
        report_title = narrative.get("title") or context.get("report_title") or preset_id

        # 3. Update or Insert into PostgreSQL reports table
        existing_report = db.query(Report).filter(Report.prompt == preset_id).first()
        if not existing_report:
            existing_report = db.query(Report).filter(Report.title == report_title).first()

        now = datetime.now(timezone.utc)
        if existing_report:
            existing_report.title = report_title
            existing_report.prompt = preset_id
            existing_report.results_json = json.dumps(context)
            existing_report.report_json = json.dumps(narrative)
            existing_report.status = "completed"
            existing_report.error_message = None
            existing_report.updated_at = now
            logger.info(f"[{preset_id}] Updated existing Report ID: {existing_report.id} ({tech_count}T / {pol_count}P / {fuel_count}F / {reg_gates}G)")
        else:
            new_report = Report(
                title=report_title,
                prompt=preset_id,
                status="completed",
                results_json=json.dumps(context),
                report_json=json.dumps(narrative),
                creator_hash="system_canonical_seed",
                is_public=True,
                created_at=now,
                updated_at=now
            )
            db.add(new_report)
            db.flush()
            logger.info(f"[{preset_id}] Created new Report ID: {new_report.id} ({tech_count}T / {pol_count}P / {fuel_count}F / {reg_gates}G)")

        db.commit()
        result["success"] = True

        # 4. Verify Specialized PDF Generation if a generator exists for this preset
        if preset_id in GENERATORS_MAP:
            try:
                buf = io.BytesIO()
                generate_specialized_monograph(preset_id, db, buf)
                pdf_bytes = buf.getvalue()
                if len(pdf_bytes) > 1000:
                    result["pdf_success"] = True
                    logger.info(f"[{preset_id}] PDF Monograph verified: {len(pdf_bytes):,} bytes")
            except Exception as pe:
                logger.warning(f"[{preset_id}] PDF verification warning: {pe}")

    except Exception as e:
        logger.error(f"[{preset_id}] FAILED: {e}", exc_info=True)
        result["error"] = str(e)
        db.rollback()
    finally:
        db.close()

    return result

def rerun_all():
    # 1. Clear narrative disk cache if present
    cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "reports_cache"))
    if os.path.exists(cache_dir):
        logger.info(f"Clearing reports cache directory at {cache_dir}")
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)

    all_presets = list(PRESET_REFERENCE_MAPPINGS.keys())

    logger.info("============================================================")
    logger.info(f"STARTING CONCURRENT REPORT GENERATION ACROSS {len(all_presets)} PRESETS (8 Workers)")
    logger.info("============================================================")

    success_count = 0
    failed_count = 0
    pdf_success_count = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_preset, p): p for p in all_presets}
        for future in as_completed(futures):
            res = future.result()
            if res["success"]:
                success_count += 1
            else:
                failed_count += 1
            if res["pdf_success"]:
                pdf_success_count += 1

    logger.info("\n============================================================")
    logger.info("BATCH REPORT GENERATION COMPLETED")
    logger.info(f"Success: {success_count} / {len(all_presets)}")
    logger.info(f"Specialized PDFs Verified: {pdf_success_count}")
    logger.info(f"Failures: {failed_count}")
    logger.info("============================================================")

if __name__ == "__main__":
    rerun_all()
