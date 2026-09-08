"""Fix NYSERDA program assignments.

Creates missing curated NYSERDA programs and re-assigns all NYSERDA
opportunities to their correct programs based on keyword matching rules.
"""
from datetime import datetime
from sqlalchemy import text
from app.database import engine


# Curated NYSERDA programs with their matching keywords
# Each entry: (program_name, program_type, description, target_stage, keywords_list)
NYSERDA_PROGRAMS = [
    # Innovation Programs (from programs.py seed)
    ("Grid Modernization", "innovation",
     "Grid Enhancing Technologies, AI/ML Grid Analytics, DER Integration, Grid Cybersecurity",
     "early-stage",
     ["grid modernization", "grid enhancing", "smart grid", "grid cyber", "der integration"]),

    ("End-Use Energy Innovation (Buildings)", "innovation",
     "Heat Pump Innovation, Thermal Energy Storage, Building Envelope, Building Energy Management",
     "early-stage",
     ["heat pump", "building envelope", "building energy", "window heat pump",
      "through wall heat pump", "appliance upgrade", "hvac", "end-use"]),

    ("Advanced Fuels & Thermal Energy Networks", "innovation",
     "Clean Hydrogen & Electrolyzers, Thermal Energy Networks, Alternative Fuels",
     "early-stage",
     ["hydrogen", "thermal energy network", "alternative fuel", "electrolyz",
      "fuel production", "large scale non-drop-in"]),

    ("Power Generation & Storage", "innovation",
     "Long-Duration Energy Storage, Advanced Battery Chemistries, Offshore Wind, Solar",
     "early-stage",
     ["energy storage", "battery", "offshore wind", "solar", "ny-sun",
      "renewables", "build-ready", "power generation"]),

    ("Clean Transportation", "innovation",
     "Commercial Fleet Electrification, Smart Charging, Vehicle-to-Grid",
     "early-stage",
     ["clean transport", "charge ready", "ev ", "electric vehicle", "truck voucher",
      "school bus", "fleet electrification", "charging"]),

    ("Carbon Management & Industrial Decarbonization", "innovation",
     "Embodied Carbon, Industrial Process Heat Electrification, CCUS, Direct Air Capture",
     "early-stage",
     ["carbon management", "industrial decarboniz", "ccus", "direct air capture",
      "embodied carbon", "carbon capture"]),

    # Commercialization & Support Programs
    ("Empire Building Challenge", "deployment",
     "Decarbonization demonstration partnership with large commercial/hospital building owners",
     "deployment",
     ["empire building challenge"]),

    ("FlexTech Program", "technical_assistance",
     "Technical assistance cost-share for energy studies/audits for SBC ratepayers",
     "any",
     ["flextech", "flex tech", "flexible energy technical"]),

    # Additional NYSERDA programs needed for current opportunities
    ("Solar (NY-Sun)", "deployment",
     "NY-Sun incentive programs for residential, commercial, and industrial solar installations",
     "deployment",
     ["ny-sun", "solar incentive", "solar predevelopment"]),

    ("Multifamily & Affordable Housing", "deployment",
     "Energy efficiency, electrification, and retrofits for multifamily and affordable housing",
     "deployment",
     ["multifamily", "affordable multifamily", "affordable housing", "high-performance affordable",
      "owner's representative", "multifamily contractor"]),

    ("Workforce Development", "workforce",
     "Clean energy job training, apprenticeships, internships, and career pathways",
     "any",
     ["apprentice", "pre-apprentice", "training", "career pathway", "internship",
      "workforce", "on-the-job", "upskilling", "technical skills"]),

    ("Community & Municipal Programs", "market_development",
     "Community decarbonization, municipal permitting, energy economy planning, DAC consultant services",
     "any",
     ["community decarboni", "municipal permit", "energy economy planning",
      "disadvantaged communities", "dac consultant", "revolving loan fund",
      "community energy"]),

    ("Green Bank & Finance", "market_development",
     "NY Green Bank financing arrangements, clean energy financing, and eligible purchaser programs",
     "any",
     ["green bank", "financing arrangement", "eligible purchaser", "clean energy financing"]),

    ("Environmental & Health Research", "innovation",
     "Energy-focused air quality, health effects research, and environmental studies",
     "early-stage",
     ["air quality", "health effects", "environmental research", "energy-focused air"]),

    ("Port & Infrastructure", "deployment",
     "Port infrastructure for clean energy supply chain and offshore wind",
     "deployment",
     ["port infrastructure"]),

    ("Advanced Nuclear", "innovation",
     "Advanced nuclear energy research and development",
     "early-stage",
     ["nuclear", "advanced nuclear"]),
]


def main():
    with engine.begin() as conn:
        now = datetime.now().isoformat()

        # 1. Get existing programs
        cur_progs = conn.execute(text("SELECT id, name FROM programs"))
        existing = {row[1]: row[0] for row in cur_progs.fetchall()}
        print(f"Existing programs: {len(existing)}")

        # 2. Create missing programs
        prog_map = {}
        for name, ptype, desc, target, _ in NYSERDA_PROGRAMS:
            if name in existing:
                prog_map[name] = existing[name]
                print(f"  [OK] Program exists: [{existing[name]}] {name}")
            else:
                res = conn.execute(
                    text("""
                        INSERT INTO programs (name, program_type, description, target_stage,
                                       parent_program, active, last_verified_at, created_at, updated_at)
                        VALUES (:name, :ptype, :desc, :target, 'Technology & Business Innovation', true, NOW(), NOW(), NOW())
                        RETURNING id
                    """),
                    {"name": name, "ptype": ptype, "desc": desc, "target": target}
                )
                pid = res.scalar()
                prog_map[name] = pid
                print(f"  + Created program: [{pid}] {name} ({ptype})")

        # 3. Re-assign all NYSERDA opportunities
        cur_opps = conn.execute(
            text("SELECT id, solicitation_number, name, program_id FROM opportunities WHERE agency = 'NYSERDA'")
        )
        nyserda_opps = [dict(r._mapping) for r in cur_opps.fetchall()]
        print(f"\nRe-assigning {len(nyserda_opps)} NYSERDA opportunities:")

        assigned = 0
        for opp in nyserda_opps:
            opp_id = opp['id']
            opp_name = (opp['name'] or '').lower()
            opp_sol = (opp['solicitation_number'] or '').lower()
            text_blob = opp_name + " " + opp_sol
            old_prog = opp['program_id']

            matched_prog = None
            matched_prog_name = None

            # Try matching against program keywords (most specific first)
            for prog_name, _, _, _, keywords in NYSERDA_PROGRAMS:
                for kw in keywords:
                    if kw.lower() in text_blob:
                        matched_prog = prog_map[prog_name]
                        matched_prog_name = prog_name
                        break
                if matched_prog:
                    break

            if matched_prog:
                conn.execute(
                    text("UPDATE opportunities SET program_id = :matched_prog WHERE id = :opp_id"),
                    {"matched_prog": matched_prog, "opp_id": opp_id}
                )
                marker = "->" if matched_prog != old_prog else "="
                print(f"  {marker} {opp['solicitation_number'] or '':20s} -> [{matched_prog:3d}] {matched_prog_name:40s} | {(opp['name'] or '')[:50]}")
                assigned += 1
            else:
                # Fallback: create/use NYSERDA General
                if "NYSERDA General" not in prog_map:
                    res = conn.execute(
                        text("""
                            INSERT INTO programs (name, program_type, description, active,
                                           last_verified_at, created_at, updated_at)
                            VALUES ('NYSERDA General', 'inferred',
                                   'General NYSERDA programs not yet categorized', true, NOW(), NOW(), NOW())
                            RETURNING id
                        """)
                    )
                    prog_map["NYSERDA General"] = res.scalar()
                    print(f"  + Created fallback: NYSERDA General [{prog_map['NYSERDA General']}]")

                conn.execute(
                    text("UPDATE opportunities SET program_id = :prog_id WHERE id = :opp_id"),
                    {"prog_id": prog_map["NYSERDA General"], "opp_id": opp_id}
                )
                print(f"  ? {opp['solicitation_number'] or '':20s} -> NYSERDA General (no match)  | {(opp['name'] or '')[:50]}")
                assigned += 1

        # 4. Verify
        print("\n--- Verification ---")
        null_cnt = conn.execute(
            text("SELECT COUNT(*) FROM opportunities WHERE agency='NYSERDA' AND program_id IS NULL")
        ).scalar() or 0
        print(f"NYSERDA opps with null program_id: {null_cnt}")

        dist = conn.execute(text("""
            SELECT p.name, p.program_type, COUNT(o.id) as opp_count
            FROM programs p
            LEFT JOIN opportunities o ON o.program_id = p.id AND o.agency = 'NYSERDA'
            WHERE p.program_type != 'inferred' OR p.name LIKE '%NYSERDA%'
            GROUP BY p.id, p.name, p.program_type
            HAVING COUNT(o.id) > 0
            ORDER BY COUNT(o.id) DESC
        """)).fetchall()
        print("\nNYSERDA program distribution:")
        for row in dist:
            print(f"  {row[0]:45s} ({row[1]:20s}) -- {row[2]} opps")

        # Clean up orphan programs
        orphans = conn.execute(text("""
            SELECT p.id, p.name FROM programs p
            WHERE p.id NOT IN (SELECT DISTINCT program_id FROM opportunities WHERE program_id IS NOT NULL)
        """)).fetchall()
        if orphans:
            print(f"\nCleaning {len(orphans)} orphan programs:")
            for row in orphans:
                print(f"  Removing [{row[0]}] {row[1]}")
                conn.execute(text("DELETE FROM program_focus_areas WHERE program_id = :pid"), {"pid": row[0]})
                conn.execute(text("DELETE FROM programs WHERE id = :pid"), {"pid": row[0]})

    print(f"\nDone. {assigned} NYSERDA opportunities assigned.")


if __name__ == '__main__':
    main()

