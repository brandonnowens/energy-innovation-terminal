import csv
import io
import logging
import tempfile
from pathlib import Path

import requests
from sqlalchemy import text
from app.database import engine
from app.engine.energy_filter import is_energy_innovation_relevant

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BULK_URL = "https://data.www.sbir.gov/awarddatapublic/award_data.csv"

ENERGY_AGENCIES = {
    "Department of Energy": "DOE",
    "National Science Foundation": "NSF",
    "Environmental Protection Agency": "EPA",
    "National Aeronautics and Space Administration": "NASA",
    "Department of Transportation": "DOT",
    "Department of Agriculture": "USDA",
    "Department of Defense": "DOD",
}


def classify_company(name: str) -> str:
    nl = name.lower()
    if any(t in nl for t in ["university", "college", "institute"]):
        return "university"
    if any(t in nl for t in ["national lab", "laboratory"]):
        return "lab"
    return "company"


def main():
    logger.info("Connecting to PostgreSQL for SBIR ingestion...")
    with engine.begin() as conn:
        existing = conn.execute(text("SELECT COUNT(*) FROM awards WHERE source_name='sbir_gov'")).scalar() or 0
        if existing > 0:
            logger.info(f"SBIR awards already ingested ({existing}) -- clearing for re-ingest")
            conn.execute(text("DELETE FROM awards WHERE source_name='sbir_gov'"))

    logger.info("Downloading SBIR bulk CSV (367MB)... this will take a minute")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    # Download to temp file to avoid memory issues
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="wb")
    try:
        resp = requests.get(BULK_URL, headers=headers, timeout=300, stream=True)
        resp.raise_for_status()
        downloaded = 0
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            tmp.write(chunk)
            downloaded += len(chunk)
            if downloaded % (50 * 1024 * 1024) == 0:
                logger.info(f"  Downloaded {downloaded // (1024*1024)}MB...")
        tmp.close()
        logger.info(f"  Download complete: {downloaded // (1024*1024)}MB")
    except Exception as e:
        logger.error(f"Download failed: {e}")
        tmp.close()
        Path(tmp.name).unlink(missing_ok=True)
        return

    # Parse CSV
    logger.info("Parsing CSV and filtering energy-innovation awards...")
    count = 0
    skipped = 0
    total_rows = 0

    csv.field_size_limit(2**30)

    insert_sql = text("""
        INSERT INTO awards (
            external_award_id,
            recipient_name, recipient_type,
            recipient_city, recipient_state, recipient_zip,
            pi_name, pi_email,
            award_amount,
            project_title, project_abstract,
            award_type, program_name, agency,
            source_name, source_url, year
        ) VALUES (
            :external_award_id,
            :recipient_name, :recipient_type,
            :recipient_city, :recipient_state, :recipient_zip,
            :pi_name, :pi_email,
            :award_amount,
            :project_title, :project_abstract,
            :award_type, :program_name, :agency,
            :source_name, :source_url, :year
        )
    """)

    batch = []
    batch_size = 1000

    with open(tmp.name, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        logger.info(f"CSV columns: {reader.fieldnames}")

        with engine.begin() as conn:
            for row in reader:
                total_rows += 1

                try:
                    agency = row.get("Agency", "")
                    if agency not in ENERGY_AGENCIES:
                        skipped += 1
                        continue

                    mapped_agency = ENERGY_AGENCIES[agency]

                    title = row.get("Award Title", "")
                    abstract = row.get("Abstract", "")
                    company = row.get("Company", "")

                    if not company:
                        continue

                    is_valid, _ = is_energy_innovation_relevant(
                        title=title,
                        text_content=abstract,
                        agency=mapped_agency
                    )
                    if not is_valid:
                        skipped += 1
                        continue

                    tracking = row.get("Agency Tracking Number", "")
                    contract = row.get("Contract", "")
                    ext_id = tracking or contract or f"SBIR-{total_rows}"

                    amount = None
                    amt_str = row.get("Award Amount", "")
                    if amt_str:
                        try:
                            amount = float(amt_str.replace(",", "").replace("$", "").strip())
                        except (ValueError, TypeError):
                            pass

                    year = None
                    award_year = row.get("Award Year", "")
                    if award_year:
                        try:
                            year = int(str(award_year).strip()[:4])
                        except (ValueError, IndexError):
                            pass

                    phase = row.get("Phase", "").strip()
                    award_type = f"sbir_{phase.lower().replace(' ', '')}" if phase else "sbir"

                    pi_name = row.get("PI Name", "").strip() or row.get("Contact Name", "").strip() or None
                    pi_email = row.get("PI Email", "").strip() or row.get("Contact Email", "").strip() or None

                    batch.append({
                        "external_award_id": ext_id,
                        "recipient_name": company,
                        "recipient_type": classify_company(company),
                        "recipient_city": row.get("City", "").strip() or None,
                        "recipient_state": row.get("State", "").strip() or None,
                        "recipient_zip": row.get("Zip", "").strip() or None,
                        "pi_name": pi_name,
                        "pi_email": pi_email,
                        "award_amount": amount,
                        "project_title": title[:500] if title else None,
                        "project_abstract": abstract[:5000] if abstract else None,
                        "award_type": award_type,
                        "program_name": row.get("Program", "").strip() or row.get("Topic Code", "").strip() or None,
                        "agency": mapped_agency,
                        "source_name": "sbir_gov",
                        "source_url": f"https://www.sbir.gov/node/{ext_id}",
                        "year": year,
                    })
                    count += 1

                    if len(batch) >= batch_size:
                        conn.execute(insert_sql, batch)
                        batch.clear()
                        logger.info(f"  {count} energy SBIR awards ingested (scanned {total_rows} rows)...")

                except Exception as e:
                    if count < 5:
                        logger.warning(f"Error row {total_rows}: {e}")
                    continue

            if batch:
                conn.execute(insert_sql, batch)
                batch.clear()

    Path(tmp.name).unlink(missing_ok=True)

    logger.info(f"\n{'='*60}")
    logger.info(f"SBIR INGESTION COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Total CSV rows scanned: {total_rows:,}")
    logger.info(f"Energy-innovation awards ingested: {count:,}")
    logger.info(f"Skipped (non-energy/non-target agency): {skipped:,}")

    # Summary by agency
    with engine.connect() as conn:
        summary = conn.execute(text("SELECT agency, COUNT(*), COALESCE(SUM(award_amount),0) FROM awards WHERE source_name='sbir_gov' GROUP BY agency ORDER BY COUNT(*) DESC")).fetchall()
        for ag, cnt, funding in summary:
            logger.info(f"  {ag}: {cnt} awards, ${funding:,.0f}")


if __name__ == "__main__":
    main()

