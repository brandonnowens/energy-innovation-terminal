"""Enrich awards database: add lat/lng, expand schema, fix ARPA-E, geocode."""
import json
import logging
import hashlib
from pathlib import Path

from sqlalchemy import text
from app.database import engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# US state coordinates for geocoding (centroid of each state)
STATE_COORDS = {
    "AL": (32.806671, -86.791130), "AK": (61.370716, -152.404419), "AZ": (33.729759, -111.431221),
    "AR": (34.969704, -92.373123), "CA": (36.116203, -119.681564), "CO": (39.059811, -105.311104),
    "CT": (41.597782, -72.755371), "DE": (39.318523, -75.507141), "FL": (27.766279, -81.686783),
    "GA": (33.040619, -83.643074), "HI": (21.094318, -157.498337), "ID": (44.240459, -114.478828),
    "IL": (40.349457, -88.986137), "IN": (39.849426, -86.258278), "IA": (42.011539, -93.210526),
    "KS": (38.526600, -96.726486), "KY": (37.668140, -84.670067), "LA": (31.169546, -91.867805),
    "ME": (44.693947, -69.381927), "MD": (39.063946, -76.802101), "MA": (42.230171, -71.530106),
    "MI": (43.326618, -84.536095), "MN": (45.694454, -93.900192), "MS": (32.741646, -89.678696),
    "MO": (38.456085, -92.288368), "MT": (46.921925, -110.454353), "NE": (41.125370, -98.268082),
    "NV": (38.313515, -117.055374), "NH": (43.452492, -71.563896), "NJ": (40.298904, -74.521011),
    "NM": (34.840515, -106.248482), "NY": (42.165726, -74.948051), "NC": (35.630066, -79.806419),
    "ND": (47.528912, -99.784012), "OH": (40.388783, -82.764915), "OK": (35.565342, -96.928917),
    "OR": (44.572021, -122.070938), "PA": (40.590752, -77.209755), "RI": (41.680893, -71.511780),
    "SC": (33.856892, -80.945007), "SD": (44.299782, -99.438828), "TN": (35.747845, -86.692345),
    "TX": (31.054487, -97.563461), "UT": (40.150032, -111.862434), "VT": (44.045876, -72.710686),
    "VA": (37.769337, -78.169968), "WA": (47.400902, -121.490494), "WV": (38.491226, -80.954456),
    "WI": (44.268543, -89.616508), "WY": (42.755966, -107.302490), "DC": (38.897438, -77.026817),
    "PR": (18.220833, -66.590149), "VI": (18.335765, -64.896335), "GU": (13.444304, 144.793731),
}

# Major city coordinates for more precise geocoding
CITY_COORDS = {
    ("WEST LAFAYETTE", "IN"): (40.4259, -86.9081), ("CAMBRIDGE", "MA"): (42.3736, -71.1097),
    ("STANFORD", "CA"): (37.4275, -122.1697), ("BERKELEY", "CA"): (37.8716, -122.2727),
    ("ANN ARBOR", "MI"): (42.2808, -83.7430), ("ITHACA", "NY"): (42.4440, -76.5019),
    ("COLLEGE PARK", "MD"): (38.9897, -76.9378), ("AUSTIN", "TX"): (30.2672, -97.7431),
    ("BOULDER", "CO"): (40.0150, -105.2705), ("MADISON", "WI"): (43.0731, -89.4012),
    ("UNIVERSITY PARK", "PA"): (40.8148, -77.8653), ("TEMPE", "AZ"): (33.4255, -111.9400),
    ("ATLANTA", "GA"): (33.7490, -84.3880), ("SEATTLE", "WA"): (47.6062, -122.3321),
    ("CHICAGO", "IL"): (41.8781, -87.6298), ("NEW YORK", "NY"): (40.7128, -74.0060),
    ("BOSTON", "MA"): (42.3601, -71.0589), ("SAN FRANCISCO", "CA"): (37.7749, -122.4194),
    ("LOS ANGELES", "CA"): (34.0522, -118.2437), ("HOUSTON", "TX"): (29.7604, -95.3698),
    ("PITTSBURGH", "PA"): (40.4406, -79.9959), ("PHILADELPHIA", "PA"): (39.9526, -75.1652),
    ("RALEIGH", "NC"): (35.7796, -78.6382), ("DURHAM", "NC"): (35.9940, -78.8986),
    ("PASADENA", "CA"): (34.1478, -118.1445), ("GOLDEN", "CO"): (39.7555, -105.2211),
    ("OAK RIDGE", "TN"): (36.0103, -84.2697), ("ALBUQUERQUE", "NM"): (35.0844, -106.6504),
    ("SAN DIEGO", "CA"): (32.7157, -117.1611), ("DENVER", "CO"): (39.7392, -104.9903),
    ("PORTLAND", "OR"): (45.5152, -122.6784), ("MINNEAPOLIS", "MN"): (44.9778, -93.2650),
    ("SALT LAKE CITY", "UT"): (40.7608, -111.8910), ("ALBANY", "NY"): (42.6526, -73.7562),
    ("ARLINGTON", "VA"): (38.8816, -77.0910), ("TUCSON", "AZ"): (32.2226, -110.9747),
    ("LEXINGTON", "MA"): (42.4473, -71.2256), ("DAYTON", "OH"): (39.7589, -84.1916),
    ("PRINCETON", "NJ"): (40.3573, -74.6672), ("NEW HAVEN", "CT"): (41.3083, -72.9279),
    ("CHAMPAIGN", "IL"): (40.1164, -88.2434), ("COLUMBUS", "OH"): (39.9612, -82.9988),
    ("BLACKSBURG", "VA"): (37.2296, -80.4139), ("GAINESVILLE", "FL"): (29.6516, -82.3248),
    ("DAVIS", "CA"): (38.5449, -121.7405), ("AMES", "IA"): (42.0308, -93.6319),
    ("LIVERMORE", "CA"): (37.6819, -121.7680), ("RICHLAND", "WA"): (46.2856, -119.2845),
    ("KNOXVILLE", "TN"): (35.9606, -83.9207), ("UPTON", "NY"): (40.8687, -72.8868),
    ("MENLO PARK", "CA"): (37.4530, -122.1817), ("PALO ALTO", "CA"): (37.4419, -122.1430),
    ("DETROIT", "MI"): (42.3314, -83.0458), ("INDIANAPOLIS", "IN"): (39.7684, -86.1581),
    ("NASHVILLE", "TN"): (36.1627, -86.7816), ("OKLAHOMA CITY", "OK"): (35.4676, -97.5164),
    ("BALTIMORE", "MD"): (39.2904, -76.6122), ("WASHINGTON", "DC"): (38.9072, -77.0369),
    ("SACRAMENTO", "CA"): (38.5816, -121.4944), ("CHARLOTTESVILLE", "VA"): (38.0293, -78.4767),
    ("STONY BROOK", "NY"): (40.9257, -73.1409), ("TROY", "NY"): (42.7284, -73.6918),
    ("HANOVER", "NH"): (43.7022, -72.2896), ("STORRS", "CT"): (41.8084, -72.2495),
    ("BATON ROUGE", "LA"): (30.4515, -91.1871), ("IOWA CITY", "IA"): (41.6611, -91.5302),
    ("LINCOLN", "NE"): (40.8136, -96.7026), ("LARAMIE", "WY"): (41.3114, -105.5911),
    ("MISSOULA", "MT"): (46.8721, -113.9940), ("MOSCOW", "ID"): (46.7324, -117.0002),
    ("COLUMBIA", "MO"): (38.9517, -92.3341), ("MANHATTAN", "KS"): (39.1836, -96.5717),
}


def add_columns(conn):
    """PostgreSQL schema columns are managed via SQLAlchemy models."""
    pass


def geocode_awards(conn):
    """Add lat/lng to all awards based on city+state."""
    need_geo = conn.execute(text("SELECT COUNT(*) FROM awards WHERE latitude IS NULL AND recipient_state IS NOT NULL")).scalar() or 0
    logger.info(f"Awards needing geocoding: {need_geo:,}")

    # First pass: exact city+state matches
    updated = 0
    city_sql = text("""
        UPDATE awards SET latitude = :lat, longitude = :lng 
        WHERE latitude IS NULL AND UPPER(recipient_city) = :city AND UPPER(recipient_state) = :state
    """)
    for (city, state), (lat, lng) in CITY_COORDS.items():
        r = conn.execute(city_sql, {"lat": lat, "lng": lng, "city": city, "state": state})
        updated += r.rowcount

    logger.info(f"Geocoded by city: {updated:,}")

    # Second pass: state centroid for the rest
    updated2 = 0
    state_sql = text("""
        UPDATE awards SET latitude = :lat, longitude = :lng 
        WHERE latitude IS NULL AND UPPER(recipient_state) = :state
    """)
    for state, (lat, lng) in STATE_COORDS.items():
        r = conn.execute(state_sql, {"lat": lat, "lng": lng, "state": state})
        updated2 += r.rowcount

    logger.info(f"Geocoded by state centroid: {updated2:,}")

    # Check coverage
    geocoded = conn.execute(text("SELECT COUNT(*) FROM awards WHERE latitude IS NOT NULL")).scalar() or 0
    total = conn.execute(text("SELECT COUNT(*) FROM awards")).scalar() or 0
    logger.info(f"Total geocoded: {geocoded:,} / {total:,} ({geocoded/total*100:.1f}%)")


def enrich_sbir_data(conn):
    """Re-read SBIR CSV data to enrich with website, employee count, DUNS, PI details."""
    import csv
    import tempfile
    import requests

    # Check if already enriched
    already_cnt = conn.execute(text("SELECT COUNT(*) FROM awards WHERE source_name='sbir_gov' AND recipient_website IS NOT NULL")).scalar() or 0
    if already_cnt > 1000:
        logger.info("SBIR data already enriched -- skipping download")
        return

    logger.info("Downloading SBIR CSV for enrichment...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get("https://data.www.sbir.gov/awarddatapublic/award_data.csv",
                          headers=headers, timeout=300, stream=True)
        resp.raise_for_status()
    except Exception as e:
        logger.warning(f"SBIR download failed: {e}")
        return

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="wb")
    for chunk in resp.iter_content(chunk_size=1024*1024):
        tmp.write(chunk)
    tmp.close()

    csv.field_size_limit(2**30)
    updated = 0
    batch = []
    batch_size = 1000

    update_sbir_sql = text("""
        UPDATE awards SET
            recipient_website = COALESCE(recipient_website, :website),
            employee_count = COALESCE(employee_count, :employee_count),
            duns_number = COALESCE(duns_number, :duns_number),
            hubzone = COALESCE(hubzone, :hubzone),
            women_owned = COALESCE(women_owned, :women_owned),
            disadvantaged = COALESCE(disadvantaged, :disadvantaged),
            pi_title = COALESCE(pi_title, :pi_title),
            pi_phone = COALESCE(pi_phone, :pi_phone),
            solicitation_number = COALESCE(solicitation_number, :solicitation_number),
            award_phase = COALESCE(award_phase, :award_phase)
        WHERE external_award_id = :ext_id AND source_name = 'sbir_gov'
    """)

    with open(tmp.name, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tracking = row.get("Agency Tracking Number", "")
            contract = row.get("Contract", "")
            ext_id = tracking or contract
            if not ext_id:
                continue

            website = row.get("Company Website", "").strip() or None
            employees = None
            emp_str = row.get("Number Employees", "").strip()
            if emp_str:
                try:
                    employees = int(emp_str)
                except ValueError:
                    pass
            duns = row.get("Duns", "").strip() or None
            hubzone = row.get("HUBZone Owned", "").strip() or None
            women = row.get("Women Owned", "").strip() or None
            disadvantaged = row.get("Socially and Economically Disadvantaged", "").strip() or None
            pi_title = row.get("PI Title", "").strip() or None
            pi_phone = row.get("PI Phone", "").strip() or None
            sol_num = row.get("Solicitation Number", "").strip() or None
            phase = row.get("Phase", "").strip() or None

            if website or employees or duns:
                batch.append({
                    "website": website,
                    "employee_count": employees,
                    "duns_number": duns,
                    "hubzone": hubzone,
                    "women_owned": women,
                    "disadvantaged": disadvantaged,
                    "pi_title": pi_title,
                    "pi_phone": pi_phone,
                    "solicitation_number": sol_num,
                    "award_phase": phase,
                    "ext_id": ext_id
                })
                updated += 1

            if len(batch) >= batch_size:
                conn.execute(update_sbir_sql, batch)
                batch.clear()

        if batch:
            conn.execute(update_sbir_sql, batch)
            batch.clear()

    Path(tmp.name).unlink(missing_ok=True)
    logger.info(f"SBIR enrichment: updated {updated:,} awards with website/employees/DUNS/PI details")


def fix_arpa_e(conn):
    """Map ARPA-E awards from DOE USASpending data."""
    # USASpending DOE awards that mention ARPA-E in program_office
    r = conn.execute(text("""
        UPDATE awards SET agency='ARPA-E'
        WHERE agency IN ('DOE', 'DOE-EERE', 'DOE-SC', 'DOE-OCED')
        AND (program_office LIKE '%ARPA%' OR program_office LIKE '%Advanced Research%'
             OR project_title LIKE '%ARPA-E%' OR project_abstract LIKE '%ARPA-E%')
    """))
    logger.info(f"Remapped {r.rowcount} awards to ARPA-E")

    # Also check for ARPA-E in SBIR
    r2 = conn.execute(text("""
        UPDATE awards SET agency='ARPA-E'
        WHERE source_name='sbir_gov' AND agency='DOE'
        AND (program_name LIKE '%ARPA%' OR project_title LIKE '%ARPA-E%')
    """))
    logger.info(f"Remapped {r2.rowcount} SBIR awards to ARPA-E")


def main():
    with engine.begin() as conn:
        logger.info("Step 1: Checking columns...")
        add_columns(conn)

        logger.info("\nStep 2: Fixing ARPA-E mapping...")
        fix_arpa_e(conn)

        logger.info("\nStep 3: Geocoding awards...")
        geocode_awards(conn)

        logger.info("\nStep 4: Enriching SBIR data...")
        enrich_sbir_data(conn)

        # Final summary
        total = conn.execute(text("SELECT COUNT(*) FROM awards")).scalar() or 0
        geocoded = conn.execute(text("SELECT COUNT(*) FROM awards WHERE latitude IS NOT NULL")).scalar() or 0
        with_website = conn.execute(text("SELECT COUNT(*) FROM awards WHERE recipient_website IS NOT NULL")).scalar() or 0
        with_employees = conn.execute(text("SELECT COUNT(*) FROM awards WHERE employee_count IS NOT NULL")).scalar() or 0
        arpa_e = conn.execute(text("SELECT COUNT(*) FROM awards WHERE agency='ARPA-E'")).scalar() or 0

        logger.info(f"\n{'='*60}")
        logger.info(f"ENRICHMENT COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total awards: {total:,}")
        logger.info(f"Geocoded (lat/lng): {geocoded:,} ({geocoded/total*100:.1f}%)")
        logger.info(f"With website: {with_website:,}")
        logger.info(f"With employee count: {with_employees:,}")
        logger.info(f"ARPA-E awards: {arpa_e:,}")


if __name__ == "__main__":
    main()

