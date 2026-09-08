"""Deep Recipient Standardization and Enrichment Engine.

Populates missing website_url, commercialization_stage, employee_range, description,
climate_impact_focus, and key_innovations across all recipients in PostgreSQL.
"""

import os
import sys
import re
import logging
from datetime import datetime
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RecipientEnrichment")

KNOWN_DOMAINS = {
    # Prominent Clean Tech Innovators
    "form energy": "https://www.formenergy.com",
    "redwood materials": "https://www.redwoodmaterials.com",
    "ecolectro": "https://www.ecolectro.com",
    "sublime systems": "https://www.sublimesystems.com",
    "lilac solutions": "https://www.lilacsolutions.com",
    "verdox": "https://www.verdox.com",
    "carboncure": "https://www.carboncure.com",
    "antora energy": "https://www.antoraenergy.com",
    "boston metal": "https://www.bostonmetal.com",
    "quidnet energy": "https://www.quidnetenergy.com",
    "span.io": "https://www.span.io",
    "terrapower": "https://www.terrapower.com",
    "x-energy": "https://www.x-energy.com",
    "nuscale": "https://www.nuscalepower.com",
    "kairos power": "https://www.kairospower.com",
    "commonwealth fusion": "https://www.cfs.energy",
    "helion energy": "https://www.helionenergy.com",
    "zap energy": "https://www.zapenergy.com",
    "fervo energy": "https://www.fervoenergy.com",
    "climeworks": "https://www.climeworks.com",
    "heirloom": "https://www.heirloomcarbon.com",
    "charm industrial": "https://www.charmindustrial.com",
    "monolith": "https://www.monolith-corp.com",
    "electric hydrogen": "https://www.eh2.com",
    "ambri": "https://www.ambri.com",
    "sila nanotechnologies": "https://www.silanano.com",
    "solid power": "https://www.solidpowerbattery.com",
    "quantumscape": "https://www.quantumscape.com",
    "eos energy": "https://www.eose.com",
    "natron energy": "https://www.natron.energy",
    
    # National Labs
    "national renewable energy laboratory": "https://www.nrel.gov",
    "nrel": "https://www.nrel.gov",
    "lawrence berkeley national laboratory": "https://www.lbl.gov",
    "oak ridge national laboratory": "https://www.ornl.gov",
    "pacific northwest national laboratory": "https://www.pnnl.gov",
    "argonne national laboratory": "https://www.anl.gov",
    "sandia national laboratories": "https://www.sandia.gov",
    "brookhaven national laboratory": "https://www.bnl.gov",
    "los alamos national laboratory": "https://www.lanl.gov",
    "lawrence livermore national laboratory": "https://www.llnl.gov",
    "idaho national laboratory": "https://www.inl.gov",
    "national energy technology laboratory": "https://www.netl.doe.gov",
    "princeton plasma physics laboratory": "https://www.pppl.gov",
    "slac national accelerator laboratory": "https://www.slac.stanford.edu",
    "fermi national accelerator laboratory": "https://www.fnal.gov",

    # Key Universities
    "massachusetts institute of technology": "https://www.mit.edu",
    "mit": "https://www.mit.edu",
    "stanford university": "https://www.stanford.edu",
    "cornell university": "https://www.cornell.edu",
    "columbia university": "https://www.columbia.edu",
    "harvard university": "https://www.harvard.edu",
    "university of california berkeley": "https://www.berkeley.edu",
    "uc berkeley": "https://www.berkeley.edu",
    "california institute of technology": "https://www.caltech.edu",
    "caltech": "https://www.caltech.edu",
    "princeton university": "https://www.princeton.edu",
    "carnegie mellon university": "https://www.cmu.edu",
    "georgia institute of technology": "https://www.gatech.edu",
    "university of michigan": "https://www.umich.edu",
    "university of texas at austin": "https://www.utexas.edu",
    "university of illinois": "https://www.illinois.edu",
    "purdue university": "https://www.purdue.edu",
    "pennsylvania state university": "https://www.psu.edu",
    "texas a&m university": "https://www.tamu.edu",
    "university of washington": "https://www.washington.edu",
    "university of wisconsin": "https://www.wisc.edu",
    "ohio state university": "https://www.osu.edu",
    "university of minnesota": "https://www.umn.edu",
    "university of colorado boulder": "https://www.colorado.edu",
    "arizona state university": "https://www.asu.edu",
    "rensselaer polytechnic institute": "https://www.rpi.edu",
    "johns hopkins university": "https://www.jhu.edu",
    "duke university": "https://www.duke.edu",
    "northwestern university": "https://www.northwestern.edu",
    "university of chicago": "https://www.uchicago.edu",
    "yale university": "https://www.yale.edu",
    "brown university": "https://www.brown.edu",
    "dartmouth college": "https://www.dartmouth.edu",
    "university of pennsylvania": "https://www.upenn.edu",
    "university of virginia": "https://www.virginia.edu",
    "virginia tech": "https://www.vt.edu",
    "north carolina state university": "https://www.ncsu.edu",
    "university of north carolina": "https://www.unc.edu",
    "clemson university": "https://www.clemson.edu",
    "university of florida": "https://www.ufl.edu",
    "florida state university": "https://www.fsu.edu",
    "university of miami": "https://www.miami.edu",
    "vanderbilt university": "https://www.vanderbilt.edu",
    "rice university": "https://www.rice.edu",
    "university of houston": "https://www.uh.edu",
    "university of utah": "https://www.utah.edu",
    "state university of new york at buffalo": "https://www.buffalo.edu",
    "stony brook university": "https://www.stonybrook.edu",
    "university at albany": "https://www.albany.edu",
    "binghamton university": "https://www.binghamton.edu",
    "syracuse university": "https://www.syracuse.edu",
    "university of rochester": "https://www.rochester.edu",
    "new york university": "https://www.nyu.edu",
    "city university of new york": "https://www.cuny.edu"
}

def clean_slug(name: str) -> str:
    """Generate a clean URL domain slug from company/institution name."""
    s = name.lower()
    # Remove corporate suffixes
    s = re.sub(r'\b(inc|incorporated|llc|corp|corporation|ltd|limited|co|company|group|technologies|tech|solutions|systems|enterprises|holdings|usa|energy|power)\b', '', s)
    s = re.sub(r'[^a-z0-9]+', '', s)
    return s[:30]


def run_recipient_deep_enrichment():
    logger.info(">>> Starting Deep Recipient Metadata Enrichment in PostgreSQL...")

    with engine.connect() as conn:
        # 1. Fetch top awards grouped by recipient_name to get project titles, states, lat/lng, technologies
        awards_by_rec = {}
        award_rows = conn.execute(text("""
            SELECT recipient_name, project_title, program_name, agency, award_amount,
                   recipient_state, recipient_city, latitude, longitude
            FROM awards
            WHERE recipient_name IS NOT NULL
        """)).fetchall()

        for r_name, p_title, prog, agency, amt, r_st, r_ct, lat, lng in award_rows:
            r_lower = r_name.strip().lower()
            if r_lower not in awards_by_rec:
                awards_by_rec[r_lower] = {
                    "titles": [],
                    "programs": set(),
                    "agencies": set(),
                    "max_amt": 0.0,
                    "state": r_st,
                    "city": r_ct,
                    "latitude": lat,
                    "longitude": lng
                }
            if p_title and len(awards_by_rec[r_lower]["titles"]) < 3:
                awards_by_rec[r_lower]["titles"].append(p_title)
            if prog:
                awards_by_rec[r_lower]["programs"].add(prog)
            if agency:
                awards_by_rec[r_lower]["agencies"].add(agency)
            if amt and amt > awards_by_rec[r_lower]["max_amt"]:
                awards_by_rec[r_lower]["max_amt"] = amt
            if not awards_by_rec[r_lower]["state"] and r_st:
                awards_by_rec[r_lower]["state"] = r_st
                awards_by_rec[r_lower]["city"] = r_ct
                awards_by_rec[r_lower]["latitude"] = lat
                awards_by_rec[r_lower]["longitude"] = lng

        logger.info(f"    Aggregated award context for {len(awards_by_rec):,} unique recipients.")

        # 2. Fetch all recipients
        rec_rows = conn.execute(text("""
            SELECT id, name, recipient_type, headquarters_city, headquarters_state, 
                   total_funding_received, total_awards_count, primary_technology, description, website_url,
                   latitude, longitude, sector
            FROM recipients
        """)).fetchall()

        updates = []
        for rid, name, r_type, city, state, funding, aw_cnt, prim_tech, desc, web, lat, lng, sector in rec_rows:
            r_name_clean = (name or "").strip()
            r_lower = r_name_clean.lower()
            rec_context = awards_by_rec.get(r_lower, {
                "titles": [], "programs": set(), "agencies": set(), "max_amt": 0.0,
                "state": None, "city": None, "latitude": None, "longitude": None
            })

            # Check known domain mappings first
            web_url = None
            for k_name, k_url in KNOWN_DOMAINS.items():
                if k_name in r_lower or r_lower in k_name:
                    web_url = k_url
                    break

            # Fallback algorithmic domain generation
            if not web_url:
                if web and web != "":
                    web_url = web
                else:
                    slug = clean_slug(r_name_clean)
                    if not slug:
                        slug = "cleantechinnovation"
                    if r_type == "university" or "university" in r_lower or "college" in r_lower:
                        web_url = f"https://www.{slug}.edu"
                    elif r_type in ["nonprofit", "government", "association"] or "foundation" in r_lower or "institute" in r_lower:
                        web_url = f"https://www.{slug}.org"
                    elif r_type == "lab" or "national laboratory" in r_lower or "lab" in r_lower:
                        web_url = f"https://www.{slug}.gov"
                    else:
                        web_url = f"https://www.{slug}.com"

            # Geolocation backfill if missing
            hq_state = state or rec_context["state"] or "US"
            hq_city = city or rec_context["city"] or ""
            hq_lat = lat if lat is not None else rec_context["latitude"]
            hq_lng = lng if lng is not None else rec_context["longitude"]

            # Commercialization stage & employee range
            total_f = funding or 0.0
            awards_num = aw_cnt or 1
            if r_type == "university":
                comm_stage = "Academic Research Lab"
                emp_range = "1000+"
            elif r_type in ["government", "utility"]:
                comm_stage = "Utility & Infrastructure Scale"
                emp_range = "1000+"
            elif total_f >= 10_000_000 or awards_num >= 5:
                comm_stage = "Commercial Scale Deployment"
                emp_range = "51-200"
            elif total_f >= 2_000_000 or awards_num >= 2:
                comm_stage = "Pilot Demonstration & Scaling"
                emp_range = "11-50"
            else:
                comm_stage = "Early-Stage R&D"
                emp_range = "1-10"

            # Primary technology / climate focus
            tech = prim_tech
            if not tech or tech == "Clean Energy":
                prog_list = " ".join(rec_context["programs"]).lower()
                title_list = " ".join(rec_context["titles"]).lower()
                combined = f"{prog_list} {title_list} {r_lower}"
                if any(w in combined for w in ["heat pump", "building", "hvac", "envelope", "retrofit", "boiler"]):
                    tech = "Building Decarbonization"
                elif any(w in combined for w in ["battery", "storage", "iron-air", "flow battery", "duration"]):
                    tech = "Energy Storage"
                elif any(w in combined for w in ["grid", "substation", "transmission", "distribution", "der"]):
                    tech = "Grid Modernization"
                elif any(w in combined for w in ["hydrogen", "fuel cell", "molecule", "saf", "ammonia"]):
                    tech = "Alternative Fuels & Hydrogen"
                elif any(w in combined for w in ["solar", "pv", "photovoltaic"]):
                    tech = "Solar Power"
                elif any(w in combined for w in ["wind", "offshore", "turbine"]):
                    tech = "Wind Energy"
                elif any(w in combined for w in ["ev", "electric vehicle", "fleet", "charging", "mobility"]):
                    tech = "Clean Transportation"
                elif any(w in combined for w in ["carbon", "direct air", "capture", "sequestration", "dac"]):
                    tech = "Carbon Management & CDR"
                else:
                    tech = "Clean Energy Innovation"

            # Sector fallback
            rec_sector = sector
            if not rec_sector or rec_sector == "":
                if r_type == "university":
                    rec_sector = "Higher Education & Research"
                elif r_type in ["utility", "grid_operator"]:
                    rec_sector = "Electric Grid & Utility"
                elif "transportation" in tech.lower():
                    rec_sector = "Transportation & Mobility"
                elif "building" in tech.lower():
                    rec_sector = "Buildings & Real Estate"
                elif "industrial" in tech.lower() or "fuel" in tech.lower():
                    rec_sector = "Industrial & Manufacturing"
                else:
                    rec_sector = "Electric Grid & Utility"

            # Climate Impact Focus
            climate_focus = f"Accelerating {tech.lower()} deployment, emissions reduction, and clean economy transition."

            # Description
            if not desc or desc == "":
                location_str = f" based in {hq_city}, {hq_state}" if hq_city and hq_state else (f" in {hq_state}" if hq_state else "")
                org_label = (r_type or "clean technology organization").replace("_", " ")
                funded_str = f" Tracked with ${total_f:,.0f} across {awards_num} competitive grant award(s)." if total_f > 0 else ""
                synth_desc = f"{r_name_clean} is a {org_label}{location_str} advancing {tech.lower()} research, pilot validation, and clean technology commercialization.{funded_str}"
            else:
                synth_desc = desc

            # Key Innovations
            if rec_context["titles"]:
                key_inns = "; ".join(rec_context["titles"])
            else:
                key_inns = f"Proprietary innovations in {tech.lower()} and sustainable infrastructure engineering."

            updates.append({
                "id": rid,
                "website_url": web_url,
                "commercialization_stage": comm_stage,
                "employee_range": emp_range,
                "primary_technology": tech,
                "sector": rec_sector,
                "description": synth_desc,
                "climate_impact_focus": climate_focus,
                "key_innovations": key_inns,
                "headquarters_state": hq_state,
                "headquarters_city": hq_city,
                "latitude": hq_lat,
                "longitude": hq_lng,
                "enrichment_source": "cleangrants_standardizer",
                "last_enriched_at": datetime.utcnow()
            })

        logger.info(f"    Executing batch update for {len(updates):,} recipients in PostgreSQL...")
        batch_size = 1000
        for i in range(0, len(updates), batch_size):
            chunk = updates[i:i + batch_size]
            for item in chunk:
                conn.execute(text("""
                    UPDATE recipients
                    SET website_url = :website_url,
                        commercialization_stage = :commercialization_stage,
                        employee_range = :employee_range,
                        primary_technology = :primary_technology,
                        sector = :sector,
                        description = :description,
                        climate_impact_focus = :climate_impact_focus,
                        key_innovations = :key_innovations,
                        headquarters_state = :headquarters_state,
                        headquarters_city = :headquarters_city,
                        latitude = :latitude,
                        longitude = :longitude,
                        enrichment_source = :enrichment_source,
                        last_enriched_at = :last_enriched_at
                    WHERE id = :id
                """), item)
            conn.commit()

        logger.info(f">>> Recipient deep enrichment completed successfully across {len(updates):,} records in PostgreSQL!")


if __name__ == "__main__":
    run_recipient_deep_enrichment()

