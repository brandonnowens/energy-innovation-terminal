"""Migration v4: Create awards and award_results tables, then extract award data from existing raw_source_data."""

import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "nyserda.db"


def create_tables(conn: sqlite3.Connection):
    """Create awards and award_results tables."""
    cur = conn.cursor()

    # Check if already exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='awards'")
    if cur.fetchone():
        logger.info("awards table already exists — skipping CREATE")
    else:
        cur.execute("""
            CREATE TABLE awards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id INTEGER REFERENCES opportunities(id),
                external_award_id TEXT,
                recipient_name TEXT,
                recipient_type TEXT,
                recipient_city TEXT,
                recipient_state TEXT,
                recipient_zip TEXT,
                recipient_country TEXT DEFAULT 'US',
                recipient_uei TEXT,
                pi_name TEXT,
                pi_email TEXT,
                pi_institution TEXT,
                award_amount REAL,
                total_estimated REAL,
                cost_share_amount REAL,
                start_date TEXT,
                end_date TEXT,
                award_date TEXT,
                project_title TEXT,
                project_abstract TEXT,
                award_type TEXT,
                cfda_number TEXT,
                cfda_title TEXT,
                program_name TEXT,
                program_office TEXT,
                agency TEXT,
                source_name TEXT,
                source_url TEXT,
                raw_data TEXT,
                year INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_awards_opp_id ON awards(opportunity_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_awards_recipient ON awards(recipient_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_awards_agency ON awards(agency)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_awards_year ON awards(year)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_awards_ext_id ON awards(external_award_id)")
        logger.info("Created awards table with indexes")

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='award_results'")
    if cur.fetchone():
        logger.info("award_results table already exists — skipping CREATE")
    else:
        cur.execute("""
            CREATE TABLE award_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                award_id INTEGER REFERENCES awards(id),
                result_type TEXT NOT NULL,
                title TEXT,
                description TEXT,
                doi TEXT,
                patent_number TEXT,
                url TEXT,
                authors TEXT,
                date TEXT,
                source_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_award_results_award ON award_results(award_id)")
        logger.info("Created award_results table with indexes")

    conn.commit()


def parse_date(date_str: str) -> str | None:
    """Parse various date formats to ISO."""
    if not date_str:
        return None
    # NSF format: MM/DD/YYYY
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%Y-%m", "%m/%d/%y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).isoformat()
        except ValueError:
            continue
    return None


def classify_institution(name: str) -> str:
    """Classify institution type from name."""
    name_lower = name.lower()
    if any(t in name_lower for t in ["university", "college", "institute of technology", "polytechnic", "school of"]):
        return "university"
    if any(t in name_lower for t in ["national lab", "national laboratory", "argonne", "sandia", "oak ridge", "nrel", "pnnl", "bnl", "lbnl", "inl"]):
        return "lab"
    if any(t in name_lower for t in ["inc", "llc", "corp", "ltd", "co.", "company", "technologies", "systems"]):
        return "company"
    if any(t in name_lower for t in ["foundation", "association", "society", "council", "coalition"]):
        return "nonprofit"
    if any(t in name_lower for t in ["city of", "state of", "county", "department", "agency", "authority"]):
        return "government"
    return "other"


def extract_nsf_awards(conn: sqlite3.Connection) -> int:
    """Extract award data from NSF raw_source_data JSON."""
    cur = conn.cursor()

    # Check how many NSF awards already exist
    cur.execute("SELECT COUNT(*) FROM awards WHERE source_name='nsf_awards'")
    existing = cur.fetchone()[0]
    if existing > 0:
        logger.info(f"NSF awards already extracted ({existing} records) — skipping")
        return 0

    cur.execute("""
        SELECT id, raw_source_data, solicitation_number
        FROM opportunities
        WHERE agency='NSF' AND raw_source_data IS NOT NULL
    """)
    rows = cur.fetchall()
    count = 0

    for opp_id, raw, sol_num in rows:
        try:
            data = json.loads(raw)

            recipient_name = data.get("awardeeName", "")
            if not recipient_name:
                continue

            pi_first = data.get("piFirstName", "")
            pi_last = data.get("piLastName", "")
            pi_name = f"{pi_first} {pi_last}".strip() or None

            amount = None
            amt_str = data.get("fundsObligatedAmt") or data.get("estimatedTotalAmt")
            if amt_str:
                try:
                    amount = float(amt_str)
                except (ValueError, TypeError):
                    pass

            total_est = None
            est_str = data.get("estimatedTotalAmt")
            if est_str:
                try:
                    total_est = float(est_str)
                except (ValueError, TypeError):
                    pass

            year = None
            award_date_str = data.get("date", "")
            award_date = parse_date(award_date_str)
            if award_date_str:
                try:
                    parts = award_date_str.split("/")
                    if len(parts) == 3:
                        year = int(parts[2])
                except (ValueError, IndexError):
                    pass

            cur.execute("""
                INSERT INTO awards (
                    opportunity_id, external_award_id,
                    recipient_name, recipient_type, recipient_city, recipient_state, recipient_zip, recipient_country,
                    pi_name, pi_email, pi_institution,
                    award_amount, total_estimated,
                    start_date, end_date, award_date,
                    project_title, project_abstract,
                    award_type, cfda_number,
                    program_name, program_office, agency,
                    source_name, source_url, year
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opp_id, str(data.get("id", sol_num)),
                recipient_name, classify_institution(recipient_name),
                data.get("awardeeCity"), data.get("awardeeStateCode"),
                data.get("awardeeZipCode"), data.get("awardeeCountryCode", "US"),
                pi_name, data.get("piEmail"),
                recipient_name,  # PI institution = awardee for NSF
                amount, total_est,
                parse_date(data.get("startDate", "")),
                parse_date(data.get("expDate", "")),
                award_date,
                data.get("title", "")[:500],
                data.get("abstractText", ""),
                "grant",
                data.get("cfdaNumber"),
                data.get("fundProgramName") or data.get("primaryProgram"),
                data.get("orgLongName"),
                "NSF",
                "nsf_awards", "https://api.nsf.gov/services/v1/awards.json",
                year,
            ))
            count += 1

            if count % 500 == 0:
                conn.commit()
                logger.info(f"  NSF: {count} awards extracted...")

        except Exception as e:
            logger.warning(f"Error extracting NSF award {opp_id}: {e}")
            continue

    conn.commit()
    logger.info(f"NSF: Extracted {count} awards")
    return count


def extract_gates_awards(conn: sqlite3.Connection) -> int:
    """Extract award data from Gates Foundation raw_source_data JSON."""
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM awards WHERE source_name='gates_foundation'")
    existing = cur.fetchone()[0]
    if existing > 0:
        logger.info(f"Gates awards already extracted ({existing} records) — skipping")
        return 0

    cur.execute("""
        SELECT id, raw_source_data, solicitation_number
        FROM opportunities
        WHERE agency='Gates Foundation' AND raw_source_data IS NOT NULL
    """)
    rows = cur.fetchall()
    count = 0

    for opp_id, raw, sol_num in rows:
        try:
            data = json.loads(raw)

            grantee = data.get("GRANTEE", "")
            if not grantee:
                continue

            amount = None
            amt_val = data.get("AMOUNT COMMITTED")
            if amt_val:
                try:
                    amount = float(str(amt_val).replace(",", "").replace("$", ""))
                except (ValueError, TypeError):
                    pass

            year = None
            date_str = data.get("DATE COMMITTED", "")
            award_date = None
            if date_str:
                try:
                    if "-" in date_str:
                        parts = date_str.split("-")
                        year = int(parts[0])
                        award_date = f"{date_str}-01"  # Approximate to 1st of month
                except (ValueError, IndexError):
                    pass

            cur.execute("""
                INSERT INTO awards (
                    opportunity_id, external_award_id,
                    recipient_name, recipient_type, recipient_city, recipient_state, recipient_country,
                    award_amount,
                    award_date,
                    project_title, project_abstract,
                    award_type, program_name, agency,
                    source_name, source_url, year
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opp_id, data.get("GRANT ID", sol_num),
                grantee, classify_institution(grantee),
                data.get("GRANTEE CITY"), data.get("GRANTEE STATE"),
                data.get("GRANTEE COUNTRY", "US"),
                amount,
                award_date,
                data.get("PURPOSE", "")[:500],
                data.get("PURPOSE", ""),
                "grant",
                data.get("TOPIC") or data.get("DIVISION"),
                "Gates Foundation",
                "gates_foundation", "https://www.gatesfoundation.org/about/committed-grants",
                year,
            ))
            count += 1

        except Exception as e:
            logger.warning(f"Error extracting Gates award {opp_id}: {e}")
            continue

    conn.commit()
    logger.info(f"Gates: Extracted {count} awards")
    return count


def extract_nyserda_historical(conn: sqlite3.Connection) -> int:
    """Extract award data from NYSERDA historical_projects table."""
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM awards WHERE source_name='nyserda_socrata'")
    existing = cur.fetchone()[0]
    if existing > 0:
        logger.info(f"NYSERDA historical awards already extracted ({existing} records) — skipping")
        return 0

    # Check if historical_projects table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historical_projects'")
    if not cur.fetchone():
        logger.info("No historical_projects table found — skipping NYSERDA extraction")
        return 0

    cur.execute("SELECT * FROM historical_projects")
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    count = 0

    for row in rows:
        try:
            r = dict(zip(cols, row))
            contractor = r.get("contractor_name", "")
            if not contractor:
                continue

            amount = None
            if r.get("award_amount"):
                try:
                    amount = float(r["award_amount"])
                except (ValueError, TypeError):
                    pass

            year = None
            award_date = None
            if r.get("award_date"):
                try:
                    award_date = str(r["award_date"])
                    year = int(award_date[:4]) if len(award_date) >= 4 else None
                except (ValueError, TypeError):
                    pass

            # Try to find linked opportunity
            opp_id = None
            app_id = r.get("application_id")
            if app_id:
                cur.execute("SELECT id FROM opportunities WHERE solicitation_number=? OR external_id=?", (str(app_id), str(app_id)))
                opp_row = cur.fetchone()
                if opp_row:
                    opp_id = opp_row[0]

            techs = " | ".join(filter(None, [r.get("technology_1"), r.get("technology_2"), r.get("technology_3")]))

            cur.execute("""
                INSERT INTO awards (
                    opportunity_id, external_award_id,
                    recipient_name, recipient_type, recipient_city, recipient_state, recipient_zip,
                    award_amount,
                    award_date,
                    project_title, project_abstract,
                    award_type, program_name, agency,
                    source_name, source_url, year
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opp_id, str(app_id) if app_id else None,
                contractor, r.get("contractor_type") or classify_institution(contractor),
                r.get("contractor_city"), r.get("contractor_state"), r.get("contractor_zip"),
                amount,
                award_date,
                r.get("project_title", "")[:500],
                f"{r.get('project_description', '')} Technologies: {techs}".strip() if r.get("project_description") else techs,
                "grant",
                r.get("project_type"),
                "NYSERDA",
                "nyserda_socrata", "https://data.ny.gov/resource/7xzk-zyk5.json",
                year,
            ))
            count += 1

            if count % 500 == 0:
                conn.commit()

        except Exception as e:
            logger.warning(f"Error extracting NYSERDA historical award: {e}")
            continue

    conn.commit()
    logger.info(f"NYSERDA Historical: Extracted {count} awards")
    return count


def main():
    logger.info(f"Connecting to {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")

    # Step 1: Create tables
    create_tables(conn)

    # Step 2: Extract from existing data
    nsf = extract_nsf_awards(conn)
    gates = extract_gates_awards(conn)
    nyserda = extract_nyserda_historical(conn)

    # Summary
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM awards")
    total = cur.fetchone()[0]

    cur.execute("SELECT agency, COUNT(*), ROUND(SUM(COALESCE(award_amount, 0)), 0) FROM awards GROUP BY agency ORDER BY COUNT(*) DESC")
    by_agency = cur.fetchall()

    cur.execute("SELECT COUNT(DISTINCT recipient_name) FROM awards")
    unique_recipients = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT pi_name) FROM awards WHERE pi_name IS NOT NULL")
    unique_pis = cur.fetchone()[0]

    logger.info(f"\n{'='*60}")
    logger.info(f"AWARDS DATABASE SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total awards: {total}")
    logger.info(f"Unique recipients: {unique_recipients}")
    logger.info(f"Unique PIs: {unique_pis}")
    logger.info(f"New this run: NSF={nsf}, Gates={gates}, NYSERDA={nyserda}")
    for agency, cnt, funding in by_agency:
        logger.info(f"  {agency}: {cnt} awards, ${funding:,.0f}")

    conn.close()


if __name__ == "__main__":
    main()
