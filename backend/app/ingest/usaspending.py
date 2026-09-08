"""USASpending.gov API adapter for federal award data (DOE, ARPA-E, EPA)."""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

import requests
from sqlalchemy import text
from app.database import engine
from app.engine.energy_filter import is_energy_innovation_relevant

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# Agency codes in USASpending
AGENCIES = {
    "DOE": {"name": "Department of Energy", "toptier_code": "089"},
    "EPA": {"name": "Environmental Protection Agency", "toptier_code": "068"},
    "NSF": {"name": "National Science Foundation", "toptier_code": "049"},
}

# Energy innovation keyword filter for API query
ENERGY_KEYWORDS = [
    "clean energy", "renewable energy", "solar energy", "wind energy",
    "energy storage", "battery storage", "grid modernization", "smart grid",
    "hydrogen fuel", "fuel cell", "carbon capture", "decarbonization",
    "energy efficiency", "electric vehicle", "offshore wind", "geothermal",
    "nuclear energy", "energy innovation", "photovoltaic", "electrification",
    "heat pump", "direct air capture", "sustainable aviation fuel",
    "long duration storage", "building energy", "net zero",
]

BASE_URL = "https://api.usaspending.gov/api/v2"


def classify_recipient(name: str) -> str:
    """Classify recipient type from name."""
    name_lower = name.lower()
    if any(t in name_lower for t in ["university", "college", "institute of technology", "polytechnic", "regents"]):
        return "university"
    if any(t in name_lower for t in ["national lab", "national laboratory", "argonne", "sandia", "oak ridge", "nrel", "pnnl"]):
        return "lab"
    if any(t in name_lower for t in ["inc", "llc", "corp", "ltd", "co.", "company", "technologies"]):
        return "company"
    if any(t in name_lower for t in ["foundation", "association", "society", "council"]):
        return "nonprofit"
    if any(t in name_lower for t in ["city of", "state of", "county", "department"]):
        return "government"
    return "other"


def fetch_awards_for_agency(agency_code: str, agency_name: str, conn: Any) -> int:
    """Fetch awards from USASpending for a specific agency."""
    count = 0

    page = 1

    while True:
        payload = {
            "filters": {
                "agencies": [
                    {"type": "awarding", "tier": "toptier", "name": AGENCIES[agency_name]["name"]}
                ],
                "award_type_codes": ["02", "03", "04", "05"],
                "keywords": ENERGY_KEYWORDS,
                "time_period": [{"start_date": "2010-01-01", "end_date": "2026-12-31"}],
            },
            "fields": [
                "Award ID", "Recipient Name", "Description", "Award Amount",
                "Start Date", "End Date", "Awarding Agency",
                "Awarding Sub Agency", "generated_internal_id",
                "CFDA Number", "Award Type",
            ],
            "page": page,
            "limit": 100,
            "sort": "Award Amount",
            "order": "desc",
        }

        try:
            resp = requests.post(
                f"{BASE_URL}/search/spending_by_award/",
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning(f"USASpending API error for {agency_name} page {page}: {e}")
            break

        results = data.get("results", [])
        if not results:
            break

        for award in results:
            try:
                description = award.get("Description", "")
                recipient = award.get("Recipient Name", "")

                if not recipient:
                    continue

                is_valid, _ = is_energy_innovation_relevant(
                    title=description[:200],
                    text_content=description,
                    agency=agency_code
                )
                if not is_valid:
                    continue

                ext_id = award.get("generated_internal_id") or award.get("Award ID", "")

                # Check for existing
                cur.execute("SELECT id FROM awards WHERE external_award_id=? AND source_name='usaspending'", (str(ext_id),))
                if cur.fetchone():
                    continue

                amount = None
                if award.get("Award Amount"):
                    try:
                        amount = float(award["Award Amount"])
                    except (ValueError, TypeError):
                        pass

                start_date = award.get("Start Date")
                end_date = award.get("End Date")
                year = None
                if start_date:
                    try:
                        year = int(start_date[:4])
                    except (ValueError, IndexError):
                        pass

                # Map agency name
                sub_agency = award.get("Awarding Sub Agency", "")
                if "ARPA-E" in sub_agency or "Advanced Research" in sub_agency:
                    mapped_agency = "ARPA-E"
                elif "EERE" in sub_agency or "Energy Efficiency" in sub_agency:
                    mapped_agency = "DOE-EERE"
                elif "Office of Science" in sub_agency:
                    mapped_agency = "DOE-SC"
                elif "OCED" in sub_agency or "Clean Energy Demonstrations" in sub_agency:
                    mapped_agency = "DOE-OCED"
                else:
                    mapped_agency = agency_name

                cur.execute("""
                    INSERT INTO awards (
                        external_award_id,
                        recipient_name, recipient_type,
                        award_amount,
                        start_date, end_date,
                        project_title, project_abstract,
                        award_type, cfda_number,
                        program_office, agency,
                        source_name, source_url, year
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(ext_id),
                    recipient, classify_recipient(recipient),
                    amount,
                    start_date, end_date,
                    description[:500] if description else None,
                    description,
                    award.get("Award Type", "grant"),
                    award.get("CFDA Number"),
                    sub_agency,
                    mapped_agency,
                    "usaspending",
                    f"https://www.usaspending.gov/award/{ext_id}",
                    year,
                ))
                count += 1

            except Exception as e:
                logger.warning(f"Error processing USASpending award: {e}")
                continue

        if count % 200 == 0 and count > 0:
            conn.commit()
            logger.info(f"  {agency_name}: {count} awards ingested...")

        page += 1
        has_next = data.get("page_metadata", {}).get("hasNext", False)
        if not has_next or page > 50:  # Cap at 5000 awards per agency
            break

        time.sleep(0.3)  # Rate limiting

    conn.commit()
    return count


def main():
    logger.info("Connecting to PostgreSQL")
    with engine.begin() as conn:
        # Check existing
        existing = conn.execute(text("SELECT COUNT(*) FROM awards WHERE source_name='usaspending'")).scalar() or 0
        if existing > 0:
            logger.info(f"USASpending awards already exist ({existing}) — skipping full re-ingest")
            return

        total = 0
        for agency_key, info in AGENCIES.items():
            logger.info(f"Fetching {agency_key} awards from USASpending...")
            count = fetch_awards_for_agency(info["toptier_code"], agency_key, conn)
            logger.info(f"  {agency_key}: {count} energy-related awards")
            total += count

        logger.info(f"\nUSASpending total: {total} awards ingested")


if __name__ == "__main__":
    main()

