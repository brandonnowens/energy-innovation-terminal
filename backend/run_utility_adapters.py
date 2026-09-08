"""Run only the new utility innovation adapters."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
# Import all models to ensure mapper relationships are resolved
from app.models import opportunity, award, source, program, project, analysis  # noqa: F401

db = SessionLocal()

def run_adapter(label, adapter_cls):
    try:
        print(f"Ingesting {label}...")
        with adapter_cls() as adapter:
            stats = adapter.ingest(db)
            print(f"  {label}: {stats}")
    except Exception as e:
        print(f"  {label}: FAILED - {e}")
        db.rollback()

try:
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

    # Summary
    from app.models.opportunity import Opportunity
    from sqlalchemy import func
    total = db.query(Opportunity).count()
    counts = db.query(Opportunity.agency, func.count()).group_by(Opportunity.agency).order_by(func.count().desc()).all()
    print(f"\n{'='*50}")
    print(f"  Total opportunities: {total}")
    print(f"\n  By Agency:")
    for agency, count in counts:
        print(f"    {agency:<25} {count:>5}")
    print(f"{'='*50}")

finally:
    db.close()
