"""Run only the new state energy adapters."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.database import SessionLocal

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

    from app.ingest.maine_efficiency import MaineEfficiencyAdapter
    run_adapter("Efficiency Maine", MaineEfficiencyAdapter)

    from app.ingest.maryland_mea import MarylandMEAAdapter
    run_adapter("Maryland MEA", MarylandMEAAdapter)

    from app.ingest.pennsylvania_dep import PADEPAdapter
    run_adapter("Pennsylvania DEP", PADEPAdapter)

    from app.ingest.virginia_energy import VAEnergyAdapter
    run_adapter("Virginia Energy", VAEnergyAdapter)

    from app.ingest.newmexico_emnrd import NMEMNRDAdapter
    run_adapter("NM EMNRD", NMEMNRDAdapter)

    from app.ingest.texas_seco import TXSECOAdapter
    run_adapter("TX SECO", TXSECOAdapter)

    from app.ingest.wisconsin_oei import WIOEIAdapter
    run_adapter("WI OEI", WIOEIAdapter)

    from app.ingest.iowa_ieda import IAIEDAAdapter
    run_adapter("IA IEDA", IAIEDAAdapter)

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
