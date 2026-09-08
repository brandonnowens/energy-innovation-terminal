"""Backfill general programs for organizations that have opportunities but no programs.

Ensures that every organization with funding opportunities has at least one general
innovation program holding all its historical and current opportunities.
Also assigns any unassigned opportunities (program_id IS NULL) to their agency's general program.
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.program import Program, ProgramFocusArea
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)

# Specialized program descriptions and metadata per agency/utility
ORG_PROGRAM_METADATA = {
    "DOD": {
        "name": "DOD Defense Energy & Innovation Program",
        "type": "innovation",
        "desc": "Department of Defense energy resilience, operational energy, advanced materials, and technological innovation initiatives.",
        "url": "https://www.acq.osd.mil/eie/eer/",
        "focus_areas": [
            ("Operational Energy & Resilience", "Advanced power systems, tactical microgrids, and mobile power generation."),
            ("Advanced Materials & Defense Tech", "Next-generation energy storage, thermal management, and power electronics."),
        ],
    },
    "NASA": {
        "name": "NASA Space Power & Energy Storage Program",
        "type": "innovation",
        "desc": "NASA extreme environment power, high-density energy storage, photovoltaic, and advanced propulsion technologies.",
        "url": "https://www.nasa.gov/directorates/stmd/",
        "focus_areas": [
            ("Extreme Environment Power", "Batteries, solar arrays, and thermal energy conversion for aerospace and harsh conditions."),
            ("Advanced Energy Conversion", "Fuel cells, power management, and regenerative energy systems."),
        ],
    },
    "DOT": {
        "name": "DOT Clean Transportation & Infrastructure Innovation",
        "type": "deployment",
        "desc": "Department of Transportation clean transit, EV charging infrastructure, smart mobility, and emissions reduction programs.",
        "url": "https://www.transportation.gov/sustainability",
        "focus_areas": [
            ("Electric Mobility & Charging", "EV deployment, fleet electrification, and public charging network optimization."),
            ("Smart Grid Integration & Transit", "Vehicle-to-grid integration and low-emission multi-modal transit systems."),
        ],
    },
    "Con Edison": {
        "name": "Con Edison Non-Wires & Clean Innovation Program",
        "type": "deployment",
        "desc": "Con Edison utility innovation programs, Non-Wires Solutions (NWS), distributed energy integration, and battery storage pilots in NYC and Westchester.",
        "url": "https://www.coned.com/en/business-partners/business-opportunities/non-wires-solutions",
        "focus_areas": [
            ("Non-Wires Solutions (NWS)", "Targeted energy efficiency, storage, and demand management to defer substation upgrades."),
            ("Urban Grid Modernization", "High-density network resilience, smart metering, and distributed storage."),
        ],
    },
    "Orange & Rockland": {
        "name": "Orange & Rockland Utility Innovation & NWA Program",
        "type": "deployment",
        "desc": "Orange & Rockland Non-Wires Alternatives (NWA) and clean energy demonstration projects across Rockland, Orange, and Sullivan counties.",
        "url": "https://www.oru.com/en/business-partners/business-opportunities/non-wires-alternatives",
        "focus_areas": [
            ("Non-Wires Alternatives (NWA)", "Grid relief and capacity enhancement through distributed solar, storage, and efficiency."),
        ],
    },
    "National Grid": {
        "name": "National Grid NY Clean Energy & Grid Innovation",
        "type": "deployment",
        "desc": "National Grid New York innovation initiatives, Non-Wires Alternatives, hydrogen blending, RNG, and EV infrastructure programs.",
        "url": "https://www.nationalgridus.com/upstate-ny-business/energy-initiatives/",
        "focus_areas": [
            ("Clean Heat & Gas Decarbonization", "Hydrogen blending, renewable natural gas (RNG), and network geothermal pilots."),
            ("Upstate Grid Modernization", "Distributed energy integration, hosting capacity enhancement, and storage pilots."),
        ],
    },
    "NYSEG": {
        "name": "NYSEG Non-Wires Alternatives & Grid Innovation",
        "type": "deployment",
        "desc": "New York State Electric & Gas innovation procurements, Non-Wires Alternatives, and smart grid modernization across upstate NY.",
        "url": "https://www.nyseg.com/wps/portal/nyseg/suppliersandpartners/businesspartners/nwa",
        "focus_areas": [
            ("Non-Wires Alternatives", "Locational capacity relief and load reduction via energy storage and DERs."),
        ],
    },
    "RG&E": {
        "name": "RG&E Clean Grid & Non-Wires Program",
        "type": "deployment",
        "desc": "Rochester Gas & Electric Non-Wires Alternatives, smart grid upgrades, and distributed energy demonstration programs in the Rochester region.",
        "url": "https://www.rge.com/wps/portal/rge/suppliersandpartners/businesspartners/nwa",
        "focus_areas": [
            ("Rochester Grid Modernization", "Targeted load management, distribution automation, and battery storage demonstrations."),
        ],
    },
    "Central Hudson": {
        "name": "Central Hudson Targeted Demand Response & NWA",
        "type": "deployment",
        "desc": "Central Hudson Gas & Electric Targeted Demand Response, Non-Wires Alternatives, and grid modernization in the Mid-Hudson Valley.",
        "url": "https://www.cenhud.com/nwa",
        "focus_areas": [
            ("Targeted Demand Management", "Peak load reduction, smart inverters, and battery storage integration."),
        ],
    },
    "PSEG Long Island": {
        "name": "PSEG Long Island Utility 2.0 & Innovation Program",
        "type": "deployment",
        "desc": "PSEG Long Island Utility 2.0 clean energy transition, non-wires solutions, battery storage, and dynamic load management on Long Island.",
        "url": "https://www.psegliny.com/businesspartners/nwa",
        "focus_areas": [
            ("Long Island Grid Resilience", "Substation load relief, energy storage integration, and coastal grid hardening."),
        ],
    },
    "LIPA": {
        "name": "LIPA Clean Energy & Resource Procurement Program",
        "type": "innovation",
        "desc": "Long Island Power Authority bulk energy storage, offshore wind integration, clean energy RFPs, and grid resilience initiatives.",
        "url": "https://www.lipower.org/clean-energy-initiatives/",
        "focus_areas": [
            ("Bulk Energy Storage & Offshore Wind", "Grid-scale battery systems and transmission interconnection for offshore wind."),
        ],
    },
    "NYPA": {
        "name": "NYPA Clean Energy Technology & Demonstration Program",
        "type": "innovation",
        "desc": "New York Power Authority advanced energy pilots, thermal storage, hydrogen demonstrations, and high-voltage transmission innovation.",
        "url": "https://www.nypa.gov/innovation",
        "focus_areas": [
            ("High-Voltage Grid & Storage", "Large-scale battery storage, digital substations, and green hydrogen turbines."),
        ],
    },
    "Joint Utilities of NY": {
        "name": "Joint Utilities of NY Collaborative R&D Program",
        "type": "innovation",
        "desc": "Collaborative research, dynamic load management, hosting capacity maps, and EV integration across all 6 NY investor-owned utilities.",
        "url": "https://jointutilitiesofny.org/",
        "focus_areas": [
            ("Joint Grid Integration & EV", "Statewide EV rate design, interconnection standards, and DER hosting capacity."),
        ],
    },
    "NY PSC": {
        "name": "NY PSC Clean Energy Innovation & Pilot Initiatives",
        "type": "innovation",
        "desc": "New York Public Service Commission regulatory sandboxes, REV demonstration projects, and clean energy innovation proceedings.",
        "url": "https://dps.ny.gov/",
        "focus_areas": [
            ("Regulatory Sandboxes & REV Demonstrations", "New utility business models, shared savings, and clean energy innovation filings."),
        ],
    },
    "USDA": {
        "name": "USDA Rural Energy & Bioeconomy Innovation Program",
        "type": "deployment",
        "desc": "USDA Rural Energy for America Program (REAP), bioeconomy research, and agricultural clean energy deployment.",
        "url": "https://www.rd.usda.gov/programs-services/energy-programs",
        "focus_areas": [
            ("Rural & Agricultural Clean Energy", "On-farm solar, anaerobic digesters, and rural energy efficiency."),
        ],
    },
}


def backfill_general_programs(db: Session) -> dict:
    """Create general programs for organizations without programs and link all opportunities."""
    stats = {
        "programs_created": 0,
        "focus_areas_created": 0,
        "opportunities_assigned": 0,
    }

    # 1. Find all distinct agencies in opportunities
    agencies_rows = db.execute(text("""
        SELECT DISTINCT agency
        FROM opportunities
        WHERE agency IS NOT NULL AND agency != ''
    """)).fetchall()
    agencies = [r[0] for r in agencies_rows]

    for agency in agencies:
        # Check if agency has any programs linked to its opportunities
        linked_prog_count = db.execute(text("""
            SELECT COUNT(DISTINCT program_id)
            FROM opportunities
            WHERE agency = :agency AND program_id IS NOT NULL
        """), {"agency": agency}).scalar() or 0

        # Check existing programs by name matching agency
        existing_prog = db.query(Program).filter(
            (Program.name.ilike(f"{agency} %")) | (Program.name.ilike(f"%{agency}%"))
        ).first()

        prog_id = existing_prog.id if existing_prog else None

        # If no program exists for this agency, create one
        if not prog_id:
            meta = ORG_PROGRAM_METADATA.get(agency, {
                "name": f"{agency} General Innovation & Energy Program",
                "type": "innovation",
                "desc": f"General funding, innovation, and clean energy programs administered by {agency}.",
                "url": f"https://www.google.com/search?q={agency}+clean+energy+funding",
                "focus_areas": [
                    ("Clean Energy Innovation", f"Core research and development programs supported by {agency}."),
                ],
            })

            # Check if name is already taken, if so append Agency
            prog_name = meta["name"]
            existing_by_name = db.query(Program).filter_by(name=prog_name).first()
            if existing_by_name:
                prog_id = existing_by_name.id
            else:
                new_prog = Program(
                    name=prog_name,
                    program_type=meta.get("type", "innovation"),
                    description=meta.get("desc", f"General innovation initiatives by {agency}."),
                    url=meta.get("url"),
                    active=True,
                    target_stage="all-stages",
                    target_applicant="business, university, utility, municipality",
                    source_url=meta.get("url"),
                )
                db.add(new_prog)
                db.flush()
                prog_id = new_prog.id
                stats["programs_created"] += 1

                # Add focus areas
                for fa_title, fa_desc in meta.get("focus_areas", []):
                    fa = ProgramFocusArea(
                        program_id=prog_id,
                        focus_area=fa_title,
                        description=fa_desc,
                        keywords=f"{agency}, clean energy, innovation, {fa_title}",
                    )
                    db.add(fa)
                    stats["focus_areas_created"] += 1

                db.commit()
                print(f"  Created program for {agency}: '{prog_name}' (ID {prog_id})")

        # 2. Assign all opportunities for this agency where program_id IS NULL to this program
        if prog_id:
            assign_res = db.execute(text("""
                UPDATE opportunities
                SET program_id = :prog_id
                WHERE agency = :agency AND program_id IS NULL
            """), {"prog_id": prog_id, "agency": agency})
            assigned_count = assign_res.rowcount
            if assigned_count > 0:
                stats["opportunities_assigned"] += assigned_count
                print(f"  Assigned {assigned_count} opportunities for {agency} to program ID {prog_id}.")

    db.commit()
    return stats
