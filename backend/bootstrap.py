"""Initialize the database and FTS tables, then run full ingestion."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, init_db
from sqlalchemy import text

print("Creating tables...")
init_db()

print("Creating FTS virtual tables...")
with engine.connect() as conn:
    conn.execute(text(
        "CREATE VIRTUAL TABLE IF NOT EXISTS opportunities_fts "
        "USING fts5(solicitation_number, name, short_description, "
        "tokenize='porter unicode61')"
    ))
    conn.execute(text(
        "CREATE VIRTUAL TABLE IF NOT EXISTS historical_projects_fts "
        "USING fts5(project_title, contractor_name, project_description, "
        "technology_1, technology_2, technology_3, "
        "tokenize='porter unicode61')"
    ))
    conn.execute(text(
        "CREATE VIRTUAL TABLE IF NOT EXISTS programs_fts "
        "USING fts5(name, description, "
        "tokenize='porter unicode61')"
    ))
    conn.commit()
print("Database initialized successfully!")

# Run ingestion
print("\n=== Running full ingestion ===\n")

from app.database import SessionLocal
db = SessionLocal()

def run_adapter(label, adapter_cls):
    """Run a single adapter with error isolation."""
    try:
        print(f"Ingesting {label}...")
        with adapter_cls() as adapter:
            stats = adapter.ingest(db)
            print(f"  {label}: {stats}")
            return stats
    except Exception as e:
        print(f"  {label}: FAILED - {e}")
        db.rollback()
        return {"added": 0, "updated": 0, "unchanged": 0, "errors": 1}

try:
    from app.ingest.funding_api import FundingAPIAdapter
    run_adapter("NYSERDA Current", FundingAPIAdapter)

    from app.ingest.programs import ProgramsAdapter
    run_adapter("NYSERDA Programs", ProgramsAdapter)

    from app.ingest.socrata import SocrataAdapter
    run_adapter("Historical R&D Projects", SocrataAdapter)

    from app.ingest.closed import ClosedOpportunitiesAdapter
    run_adapter("Closed Opportunities", ClosedOpportunitiesAdapter)

    from app.ingest.grants_gov import GrantsGovAdapter
    run_adapter("Grants.gov Federal", GrantsGovAdapter)

    from app.ingest.doe_labs import DOELabsAdapter
    run_adapter("DOE Labs", DOELabsAdapter)

    from app.ingest.cec import CECAdapter
    run_adapter("CEC (California)", CECAdapter)

    from app.ingest.masscec import MassCECAdapter
    run_adapter("MassCEC", MassCECAdapter)

    from app.ingest.maine_efficiency import MaineEfficiencyAdapter
    run_adapter("Maine Efficiency", MaineEfficiencyAdapter)

    from app.ingest.maryland_mea import MarylandMEAAdapter
    run_adapter("Maryland MEA", MarylandMEAAdapter)

    from app.ingest.pennsylvania_dep import PADEPAdapter
    run_adapter("Pennsylvania DEP", PADEPAdapter)

    from app.ingest.virginia_energy import VAEnergyAdapter
    run_adapter("Virginia Energy", VAEnergyAdapter)

    from app.ingest.colorado_ceo import ColoradoCEOAdapter
    run_adapter("Colorado CEO", ColoradoCEOAdapter)

    from app.ingest.njeda import NJEDAAdapter
    run_adapter("NJEDA", NJEDAAdapter)

    from app.ingest.washington_commerce import WACommerceAdapter
    run_adapter("WA Commerce", WACommerceAdapter)

    from app.ingest.illinois_dceo import ILDCEOAdapter
    run_adapter("IL DCEO", ILDCEOAdapter)

    from app.ingest.minnesota_commerce import MNCommerceAdapter
    run_adapter("MN Commerce", MNCommerceAdapter)

    from app.ingest.gates import GatesAdapter
    run_adapter("Gates Foundation", GatesAdapter)

    from app.ingest.nsf_awards import NSFAwardsAdapter
    run_adapter("NSF Awards (Historical)", NSFAwardsAdapter)

    from app.ingest.grants_gov_historical import GrantsGovHistoricalAdapter
    run_adapter("Grants.gov Historical", GrantsGovHistoricalAdapter)

    from app.ingest.hewlett import HewlettAdapter
    run_adapter("Hewlett Foundation", HewlettAdapter)

    from app.ingest.macarthur import MacArthurAdapter
    run_adapter("MacArthur Foundation", MacArthurAdapter)

    from app.ingest.kresge import KresgeAdapter
    run_adapter("Kresge Foundation", KresgeAdapter)

    from app.ingest.barr import BarrAdapter
    run_adapter("Barr Foundation", BarrAdapter)

    from app.ingest.bezos import BezosAdapter
    run_adapter("Bezos Earth Fund", BezosAdapter)

    from app.ingest.breakthrough import BreakthroughAdapter
    run_adapter("Breakthrough Energy", BreakthroughAdapter)

    from app.ingest.propublica_990 import ProPublica990Adapter
    run_adapter("ProPublica 990-PF", ProPublica990Adapter)

    from app.ingest.newmexico_emnrd import NMEMNRDAdapter
    run_adapter("NM EMNRD", NMEMNRDAdapter)

    from app.ingest.texas_seco import TXSECOAdapter
    run_adapter("TX SECO", TXSECOAdapter)

    from app.ingest.wisconsin_oei import WIOEIAdapter
    run_adapter("WI OEI", WIOEIAdapter)

    from app.ingest.iowa_ieda import IAIEDAAdapter
    run_adapter("IA IEDA", IAIEDAAdapter)

    # NY Utility Innovation Adapters
    from app.ingest.coned import ConEdInnovationAdapter
    run_adapter("Con Edison", ConEdInnovationAdapter)

    from app.ingest.orange_rockland import OrangeRocklandAdapter
    run_adapter("Orange & Rockland", OrangeRocklandAdapter)

    from app.ingest.national_grid_ny import NationalGridNYAdapter
    run_adapter("National Grid NY", NationalGridNYAdapter)

    from app.ingest.nyseg import NYSEGAdapter
    run_adapter("NYSEG", NYSEGAdapter)

    from app.ingest.rge import RGEAdapter
    run_adapter("RG&E", RGEAdapter)

    from app.ingest.central_hudson import CentralHudsonAdapter
    run_adapter("Central Hudson", CentralHudsonAdapter)

    from app.ingest.pseg_li import PSEGLongIslandAdapter
    run_adapter("PSEG Long Island", PSEGLongIslandAdapter)

    from app.ingest.lipa import LIPAAdapter
    run_adapter("LIPA", LIPAAdapter)

    from app.ingest.nypa import NYPAAdapter
    run_adapter("NYPA", NYPAAdapter)

    from app.ingest.joint_utilities_ny import JointUtilitiesNYAdapter
    run_adapter("Joint Utilities NY", JointUtilitiesNYAdapter)

    from app.ingest.ny_psc import NYPSCAdapter
    run_adapter("NY PSC", NYPSCAdapter)

    # Post-ingestion backfills
    print("\nBackfilling years...")
    from app.ingest.backfill_years import backfill_years
    year_stats = backfill_years(db)
    print(f"  Year backfill: {year_stats}")

    print("Backfilling categories (technology/fuel/sector)...")
    from app.ingest.backfill_categories import backfill_all_categories
    cat_stats = backfill_all_categories(db)
    print(f"  Category backfill: {cat_stats}")

    # Seed Policy Standards & Regulatory Proceedings
    print("\nSeeding Standards, Codes & Regulatory Proceedings...")
    try:
        from seed_policies import seed_policies
        seed_policies(db)
    except Exception as e:
        print(f"  Policy seeding note: {e}")

    try:
        from seed_proceedings import seed_proceedings
        seed_proceedings(db)
    except Exception as e:
        print(f"  Proceeding seeding note: {e}")

    # Rebuild FTS indexes
    print("\nRebuilding FTS indexes...")
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM opportunities_fts"))
        conn.execute(text(
            "INSERT INTO opportunities_fts(rowid, solicitation_number, name, short_description) "
            "SELECT id, solicitation_number, name, COALESCE(short_description, '') FROM opportunities"
        ))
        conn.execute(text("DELETE FROM historical_projects_fts"))
        conn.execute(text(
            "INSERT INTO historical_projects_fts(rowid, project_title, contractor_name, project_description, technology_1, technology_2, technology_3) "
            "SELECT id, project_title, COALESCE(contractor_name, ''), COALESCE(project_description, ''), "
            "COALESCE(technology_1, ''), COALESCE(technology_2, ''), COALESCE(technology_3, '') FROM historical_projects"
        ))
        conn.execute(text("DELETE FROM programs_fts"))
        conn.execute(text(
            "INSERT INTO programs_fts(rowid, name, description) "
            "SELECT id, name, COALESCE(description, '') FROM programs"
        ))
        conn.commit()
    print("FTS indexes rebuilt successfully!")

    # Quick stats
    from app.models.opportunity import Opportunity
    from app.models.project import HistoricalProject, HistoricalOpportunity
    from app.models.program import Program
    from sqlalchemy import func

    opp_count = db.query(Opportunity).count()
    hist_count = db.query(Opportunity).filter(Opportunity.is_historical == True).count()
    curr_count = opp_count - hist_count
    proj_count = db.query(HistoricalProject).count()
    prog_count = db.query(Program).count()

    agency_counts = db.query(Opportunity.agency, func.count()).group_by(Opportunity.agency).order_by(func.count().desc()).all()

    print(f"\n{'='*50}")
    print(f"  DATABASE SUMMARY")
    print(f"{'='*50}")
    print(f"  Total opportunities:    {opp_count}")
    print(f"    Current:              {curr_count}")
    print(f"    Historical:           {hist_count}")
    print(f"  Historical R&D projects: {proj_count}")
    print(f"  Programs:               {prog_count}")
    print(f"\n  By Agency:")
    for agency, count in agency_counts:
        print(f"    {agency:<25} {count:>5}")
    print(f"{'='*50}\n")

finally:
    db.close()
