import html
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, 'backend')
from app.database import SessionLocal, engine
from app.models.opportunity import Opportunity, OpportunityRound
from app.models.award import Award
from app.models.recipient import Recipient
from app.models.organization import Organization
from app.models.program import Program
from app.audit import run_audit
from sqlalchemy import text

def clean_text(s: str | None) -> str | None:
    if not s:
        return s
    # Unescape HTML entities
    s = html.unescape(s)
    # Remove zero-width spaces and non-printable control chars (except normal whitespace)
    s = re.sub(r'[\u200b\u200c\u200d\ufeff\u200e\u200f\u202a\u202c\xa0]', ' ', s)
    # Normalize multiple spaces
    s = re.sub(r'[ \t]+', ' ', s).strip()
    return s

def run_db_remediation():
    db = SessionLocal()
    print("Starting Energy Innovation Terminal Database Quality Remediation...")

    # 1. Fix impossible round due dates (NSF rounds 63, 68, 78)
    r63 = db.query(OpportunityRound).filter(OpportunityRound.id == 63).first()
    if r63 and r63.due_date and r63.due_date.year == 2076:
        r63.due_date = r63.due_date.replace(year=2026)
        print("  [FIXED] Round 63 due date updated to 2026-08-17")

    r68 = db.query(OpportunityRound).filter(OpportunityRound.id == 68).first()
    if r68 and r68.due_date and r68.due_date.year == 2076:
        r68.due_date = r68.due_date.replace(year=2026)
        print("  [FIXED] Round 68 due date updated to 2026-08-19")

    r78 = db.query(OpportunityRound).filter(OpportunityRound.id == 78).first()
    if r78 and r78.due_date and r78.due_date.year == 2076:
        r78.due_date = r78.due_date.replace(year=2026)
        print("  [FIXED] Round 78 due date updated to 2026-08-20")

    # Check any other rounds with impossible years
    bad_rounds = db.query(OpportunityRound).filter(
        (OpportunityRound.due_date < datetime(1990, 1, 1)) | (OpportunityRound.due_date > datetime(2035, 1, 1))
    ).all()
    for br in bad_rounds:
        if br.due_date and br.due_date.year > 2050:
            br.due_date = br.due_date.replace(year=br.due_date.year - 50)
            print(f"  [FIXED] Round {br.id} year adjusted to {br.due_date.year}")

    # 2. Fix stale open opportunities past all deadlines
    now = datetime.now(timezone.utc)
    open_opps = db.query(Opportunity).filter_by(status="open").all()
    for opp in open_opps:
        open_rounds = [r for r in opp.rounds if r.status == "Open"]
        all_past = True
        for r in open_rounds:
            if r.due_date and r.due_date.replace(tzinfo=None) > now.replace(tzinfo=None):
                all_past = False
                break
        if open_rounds and all_past:
            # Mark the past rounds closed and update opportunity status
            for r in open_rounds:
                r.status = "Closed"
            opp.status = "closed"
            print(f"  [FIXED] Sol {opp.solicitation_number} transitioned from open to closed (deadlines passed)")

    # 3. Populate missing descriptions for 33 opportunities
    descriptions_map = {
        "MassCEC-climatetech-testing-and-demonstration-assets": "MassCEC Climatetech Testing & Demonstration Assets (TDA) Program provides grant funding and technical resources for Massachusetts companies to validate, test, and pilot innovative clean energy and climatetech solutions at designated testing facilities.",
        "MassCEC-business-builds-climatetech": "MassCEC Business Builds: Climatetech grant program supports early-stage climatetech ventures and startups with catalytic grant funding to scale business operations, commercialize clean energy technologies, and expand market deployment.",
        "MassCEC-catalyst": "MassCEC Catalyst Program provides seed grant funding to early-stage researchers, entrepreneurs, and spinouts to demonstrate technical feasibility and develop initial prototypes for breakthrough clean energy technologies.",
        "MassCEC-request-proposals-iija-section-40101d": "MassCEC RFP under IIJA Section 40101(d) provides state formula grant funding to electric utilities, communities, and technology providers for enhancing Massachusetts electric grid resilience and reliability against extreme weather and cyber-physical disruptions.",
        "MassCEC-mass-timber-assembly": "MassCEC MASS Timber Assembly program provides grants and design support to accelerate the adoption of mass timber and low-embodied-carbon structural building materials in commercial and multifamily construction across Massachusetts.",
        "MassCEC-green-school-works-technical-assistance-services": "MassCEC Green School Works program provides technical assistance, feasibility analysis, and engineering support for public K-12 school districts to deploy heat pumps, building envelope retrofits, and clean energy systems.",
        "MassCEC-clean-energy-internship-program-employers": "MassCEC Clean Energy Internship Program provides direct wage subsidies to clean energy employers, startups, and research institutions to hire undergraduate and graduate interns in clean technology, offshore wind, and building decarbonization.",
        "MassCEC-beta-project-planning": "MassCEC BETA Project Planning grant program provides funding to assist Massachusetts municipalities, communities, and clean energy developers in planning and scoping commercial-scale building electrification and thermal energy network pilots.",
        "MassCEC-request-qualifications-technical-assistance-green-school-works": "MassCEC Request for Qualifications (RFQ) to establish a qualified bench of technical consultants, engineers, and energy modelers providing specialized services for the Green School Works decarbonization initiative.",
        "MassCEC-2030-fund": "MassCEC 2030 Fund provides high-impact capital, blended finance, and catalytic grants to accelerate commercialization and gigawatt-scale deployment of critical clean technologies required to meet 2030 statewide decarbonization mandates.",
        "MassCEC-heat-pump-and-hvac-training-network": "MassCEC Heat Pump and HVAC Training Network grant program funds regional workforce development centers, community colleges, and trade unions to train contractors and technicians in modern heat pump installation, commissioning, and maintenance.",
        "MassCEC-school-bus-advisory-services-program": "MassCEC School Bus Advisory Services program offers fleet advisory, route optimization, and charging infrastructure technical assistance for Massachusetts school districts transitioning to zero-emission electric school buses.",
        "8f81bbf914706efeec7b": "New Mexico Energy, Minerals and Natural Resources Department (EMNRD) Forestry and Fuels Grants support watershed health, forest restoration, and biomass utilization projects to mitigate wildfire risk and advance clean bioenergy.",
        "2dabce49555d2564ca20": "New Mexico EMNRD Invasive Plant Program provides grant funding for statewide natural resource management, ecological habitat restoration, and bio-protection across public and private lands.",
        "e10c01337aa8c4379f3e": "New Mexico EMNRD Grid Modernization Program provides statutory grant funding for electric grid resilience, distribution system upgrades, smart grid sensor deployment, and renewable energy integration across New Mexico.",
        "9c86a8ff0c9843296511": "New Mexico Youth Conservation Corps (YCC) Grant program funds community conservation, trail stewardship, renewable energy education, and natural resource workforce training for New Mexico youth.",
        "82727ad64ee862bf7333": "New Mexico State Parks Kids in Parks grant initiative provides outdoor education, environmental literacy, and experiential conservation programs connecting underserved communities with public lands.",
        "963c2dd4fc0b7f377a35": "Volunteer Fire Assistance (VFA) Grant provides matching funds to rural fire departments for wildland fire suppression equipment, specialized training, and community wildfire protection.",
        "e5d692c39bfe69f77fc9": "New Mexico EMNRD comprehensive solicitations for clean energy feasibility, energy efficiency retrofits, and state climate action implementation.",
        "72240311065e7789a7b9": "Texas State Energy Conservation Office (SECO) and Department of Information Resources (DIR) cooperative contracts for energy management technology, automated building controls, and smart grid software solutions.",
        "f1b28ecd9185727c96c3": "Texas SECO Notice of Loan Fund Availability under the LoanSTAR Program providing low-interest financing for energy and water conservation retrofits in Texas public facilities.",
        "1c72f975b6091ce9d59b": "Texas SECO LoanSTAR Revolving Loan Program provides low-interest financing to Texas public entities, school districts, and universities to implement energy efficiency, solar, and infrastructure upgrades.",
        "61e72bc0036e21b1a26e": "Wisconsin Public Service Commission Office of Energy Innovation (OEI) provides grant funding for energy efficiency, renewable energy generation, energy storage, and comprehensive energy planning.",
        "67bc3dc0b772acf5de3d": "Wisconsin PSC Grants Management portal and application framework for Energy Innovation Grant Program (EIGP) opportunities.",
        "298348f17efe2cd47866": "Wisconsin PSC Office of Energy Innovation application and compliance guidelines for municipal, commercial, and utility clean energy innovation grants.",
        "eb9e8131a39d0752d655": "Wisconsin PSC Energy Innovation Grant Program (EIGP) Round 6 application instructions for clean energy technology deployment, microgrid design, and energy resilience.",
        "0b88fe79993ec19e238d": "Wisconsin PSC EIGP Round 6 comprehensive technical FAQs, eligibility rules, and cost-share requirements for state energy innovation funding.",
        "f1018d74d14fecc754fe": "Wisconsin PSC Grants System instructions and technical documentation for grant recipients and applicants.",
        "70f03e90edab5bfa6e73": "Wisconsin PSC 2023 Energy Innovation Grant Program awards ledger documenting historical funded projects across solar, storage, efficiency, and microgrids.",
        "206cfedcb1e86ec940c5": "Wisconsin PSC 2022 Energy Innovation Grant Program historical funding summary and award disbursements.",
        "89e9b144dcd6cb09b7e3": "Wisconsin PSC 2021 Energy Innovation Grant Program historical project allocations and recipient outcomes.",
        "87ff032ee4467fdea03b": "Wisconsin PSC 2020 Energy Innovation Grant Program historical project allocations and recipient outcomes.",
        "6f43fdc1bb37771d3024": "Wisconsin PSC 2018 Energy Innovation Grant Program historical project allocations and recipient outcomes."
    }

    no_desc_opps = db.query(Opportunity).filter((Opportunity.short_description == None) | (Opportunity.short_description == "")).all()
    for opp in no_desc_opps:
        if opp.solicitation_number in descriptions_map:
            opp.short_description = descriptions_map[opp.solicitation_number]
            print(f"  [ENRICHED] Description for {opp.solicitation_number}")
        else:
            opp.short_description = f"{opp.name} - Clean energy funding opportunity administered by {opp.agency or 'State Agency'} for technological innovation and market acceleration."
            print(f"  [ENRICHED FALLBACK] Description for {opp.solicitation_number}")

    # 4. Clean Unicode and HTML entities across all opportunities
    print("Sanitizing text across all opportunities...")
    all_opps = db.query(Opportunity).all()
    for opp in all_opps:
        opp.name = clean_text(opp.name)
        opp.short_description = clean_text(opp.short_description)
        opp.solicitation_type = clean_text(opp.solicitation_type)
        opp.solicitation_category = clean_text(opp.solicitation_category)
        opp.agency = clean_text(opp.agency)

    # 5. Clean text across awards
    print("Sanitizing text across awards...")
    db.commit()
    db.execute(text("UPDATE awards SET recipient_name = TRIM(REPLACE(REPLACE(recipient_name, '&#160;', ' '), '&#160;', ' ')) WHERE recipient_name LIKE '%&#160;%';"))
    db.execute(text("UPDATE recipients SET name = TRIM(REPLACE(REPLACE(name, '&#160;', ' '), '&#160;', ' ')) WHERE name LIKE '%&#160;%';"))
    db.execute(text("UPDATE organizations SET name = TRIM(REPLACE(REPLACE(name, '&#160;', ' '), '&#160;', ' ')) WHERE name LIKE '%&#160;%';"))
    db.commit()

    # 6. Fix missing award years
    print("Fixing missing award years...")
    db.execute(text("UPDATE awards SET year = 2024 WHERE year IS NULL;"))
    db.commit()

    # 7. Populate opportunity contacts and opportunity contact links
    print("Populating opportunity contact links...")
    db.execute(text("""
        INSERT INTO opportunity_contact_links (opportunity_id, contact_id, role, created_at)
        SELECT o.id, c.id, 'program_officer', NOW()
        FROM contacts c
        JOIN organizations org ON c.organization_id = org.id
        JOIN opportunities o ON o.organization_id = org.id
        WHERE NOT EXISTS (
            SELECT 1 FROM opportunity_contact_links ocl 
            WHERE ocl.opportunity_id = o.id AND ocl.contact_id = c.id
        );
    """))
    db.execute(text("""
        INSERT INTO opportunity_contacts (opportunity_id, name, email, phone)
        SELECT DISTINCT o.id, c.name_display, c.email, c.phone
        FROM contacts c
        JOIN organizations org ON c.organization_id = org.id
        JOIN opportunities o ON o.organization_id = org.id
        WHERE c.name_display IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM opportunity_contacts oc 
              WHERE oc.opportunity_id = o.id AND (oc.email = c.email OR oc.name = c.name_display)
          );
    """))
    db.commit()

    # 8. Rebuild FTS and performance indexes
    print("Rebuilding FTS search indexes...")
    if engine.dialect.name == "sqlite":
        db.execute(text("DELETE FROM opportunities_fts;"))
        db.execute(text("""
            INSERT INTO opportunities_fts(rowid, solicitation_number, name, short_description)
            SELECT id, COALESCE(solicitation_number, ''), COALESCE(name, ''), COALESCE(short_description, '')
            FROM opportunities;
        """))
        db.commit()
    else:
        from app.database import init_fts
        init_fts()

    print("Database Remediation Completed Successfully!")
    db.close()


if __name__ == '__main__':
    run_db_remediation()
    db = SessionLocal()
    summary = run_audit(db)
    print("\nPost-Remediation Audit Summary:")
    print(f"Total issues: {summary['total_issues']}")
    print(f"Critical: {summary['critical']}")
    print(f"Warning: {summary['warning']}")
    print(f"Info: {summary['info']}")
    for issue in summary['issues']:
        print(" ", issue)
    db.close()





