"""Capital Intelligence & Innovation Layer REST APIs.

Endpoints for:
- ISO/RTO Interconnection Queue Projects & Telemetry
- DOE National Lab User Facilities, Instruments & Testbeds
- SEC Form D Clean Tech Regulatory Offerings
- DOE LPO Commitments & IRA Section 48C Allocations
- Federal Procurement & SBIR Phase III Offtake Contracts
- State DER Real-World Market Deployments & Cost Curves
- University Licensable Clean Tech Portals & Spinout IP
- End-to-End Multi-Stage Capital Continuum by Recipient
"""

import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func, desc, or_

from app.database import get_db
from app.models.interconnection import InterconnectionQueueProject
from app.models.lab_facility import NationalLabFacility, FacilityTechnologyLink
from app.models.sec_form_d import SecFormDFiling
from app.models.scaleup_capital import FederalScaleupAllocation
from app.models.procurement import FederalProcurementContract
from app.models.der_market import DerMarketDeployment
from app.models.university_ip import UniversityLicensableTechnology
from app.models.recipient import Recipient
from app.models.award import Award
from app.models.attribution import RecipientInvestment, RecipientPatent

router = APIRouter()


# ── 1. ISO/RTO INTERCONNECTION QUEUE ENDPOINTS ──

@router.get("/interconnection-queues")
def get_interconnection_queues(
    iso_rto: Optional[str] = None,
    technology_type: Optional[str] = None,
    state: Optional[str] = None,
    status: Optional[str] = None,
    recipient_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve filtered ISO/RTO grid interconnection queue projects."""
    q = db.query(InterconnectionQueueProject)

    if iso_rto and iso_rto != "ALL":
        q = q.filter(InterconnectionQueueProject.iso_rto.ilike(iso_rto))
    if technology_type and technology_type != "ALL":
        q = q.filter(InterconnectionQueueProject.technology_type.ilike(f"%{technology_type}%"))
    if state and state != "ALL":
        q = q.filter(InterconnectionQueueProject.state == state.upper())
    if status and status != "ALL":
        q = q.filter(InterconnectionQueueProject.status.ilike(status))
    if recipient_id:
        q = q.filter(InterconnectionQueueProject.recipient_id == recipient_id)
    if search:
        s = f"%{search.strip()}%"
        q = q.filter(
            or_(
                InterconnectionQueueProject.project_name.ilike(s),
                InterconnectionQueueProject.developer_raw.ilike(s),
                InterconnectionQueueProject.poi_substation.ilike(s),
                InterconnectionQueueProject.queue_id.ilike(s),
                InterconnectionQueueProject.county.ilike(s)
            )
        )

    total = q.count()
    items = q.order_by(desc(InterconnectionQueueProject.capacity_mw)).offset((page - 1) * page_size).limit(page_size).all()

    # Aggregate statistics in a single query
    totals_row = db.query(
        func.sum(InterconnectionQueueProject.capacity_mw),
        func.sum(InterconnectionQueueProject.storage_mwh)
    ).first()
    total_capacity_mw = (totals_row[0] or 0.0) if totals_row else 0.0
    total_storage_mwh = (totals_row[1] or 0.0) if totals_row else 0.0

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_capacity_mw": round(total_capacity_mw, 1),
        "total_storage_mwh": round(total_storage_mwh, 1),
        "items": [
            {
                "id": p.id,
                "iso_rto": p.iso_rto,
                "queue_id": p.queue_id,
                "project_name": p.project_name,
                "developer_raw": p.developer_raw,
                "recipient_id": p.recipient_id,
                "technology_type": p.technology_type,
                "capacity_mw": p.capacity_mw,
                "storage_mwh": p.storage_mwh,
                "county": p.county,
                "state": p.state,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "poi_substation": p.poi_substation,
                "utility_territory": p.utility_territory,
                "queue_date": p.queue_date.isoformat() if p.queue_date else None,
                "study_phase": p.study_phase,
                "estimated_network_upgrade_cost_usd": p.estimated_network_upgrade_cost_usd,
                "expected_cod": p.expected_cod.isoformat() if p.expected_cod else None,
                "status": p.status,
                "source_url": p.source_url,
                "notes": p.notes
            }
            for p in items
        ]
    }


@router.get("/interconnection-queues/geojson")
def get_interconnection_queues_geojson(
    iso_rto: Optional[str] = None,
    technology_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """GeoJSON endpoint for GIS Map Studio interconnection layer."""
    q = db.query(InterconnectionQueueProject).filter(
        InterconnectionQueueProject.latitude != None,
        InterconnectionQueueProject.longitude != None
    )
    if iso_rto and iso_rto != "ALL":
        q = q.filter(InterconnectionQueueProject.iso_rto.ilike(iso_rto))
    if technology_type and technology_type != "ALL":
        q = q.filter(InterconnectionQueueProject.technology_type.ilike(f"%{technology_type}%"))

    projects = q.limit(500).all()

    features = []
    for p in projects:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [p.longitude, p.latitude]
            },
            "properties": {
                "id": p.id,
                "queue_id": p.queue_id,
                "iso_rto": p.iso_rto,
                "name": p.project_name,
                "developer": p.developer_raw,
                "capacity_mw": p.capacity_mw,
                "storage_mwh": p.storage_mwh,
                "tech": p.technology_type,
                "substation": p.poi_substation,
                "phase": p.study_phase,
                "upgrade_cost": p.estimated_network_upgrade_cost_usd,
                "cod": p.expected_cod.strftime("%b %Y") if p.expected_cod else None,
                "state": p.state
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


# ── 2. DOE NATIONAL LAB USER FACILITIES ENDPOINTS ──

@router.get("/lab-facilities")
def get_lab_facilities(
    lab_name: Optional[str] = None,
    sector: Optional[str] = None,
    technology_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve DOE National Lab User Facilities & Specialized Testbeds."""
    q = db.query(NationalLabFacility)

    if lab_name and lab_name != "ALL":
        q = q.filter(NationalLabFacility.lab_name.ilike(lab_name))
    if sector and sector != "ALL":
        q = q.filter(NationalLabFacility.primary_sectors_json.ilike(f"%{sector}%"))
    if technology_id:
        q = q.join(FacilityTechnologyLink).filter(FacilityTechnologyLink.technology_id == technology_id)
    if search:
        s = f"%{search.strip()}%"
        q = q.filter(
            or_(
                NationalLabFacility.facility_name.ilike(s),
                NationalLabFacility.summary.ilike(s),
                NationalLabFacility.lab_name.ilike(s),
                NationalLabFacility.capabilities_json.ilike(s)
            )
        )

    facilities = q.order_by(NationalLabFacility.lab_name, NationalLabFacility.facility_name).all()

    result = []
    for f in facilities:
        caps = json.loads(f.capabilities_json) if f.capabilities_json else []
        insts = json.loads(f.instruments_catalog_json) if f.instruments_catalog_json else []
        mechs = json.loads(f.access_mechanisms_json) if f.access_mechanisms_json else []
        sectors = json.loads(f.primary_sectors_json) if f.primary_sectors_json else []

        result.append({
            "id": f.id,
            "lab_name": f.lab_name,
            "facility_name": f.facility_name,
            "facility_slug": f.facility_slug,
            "facility_type": f.facility_type,
            "summary": f.summary,
            "capabilities": caps,
            "instruments": insts,
            "primary_sectors": sectors,
            "trl_focus_min": f.trl_focus_min,
            "trl_focus_max": f.trl_focus_max,
            "access_mechanisms": mechs,
            "proposal_deadline_cycles": f.proposal_deadline_cycles,
            "contact_email": f.contact_email,
            "official_url": f.official_url,
            "city": f.city,
            "state": f.state,
            "latitude": f.latitude,
            "longitude": f.longitude,
            "linked_technologies": [link.technology_id for link in f.technology_links]
        })

    return {"total": len(result), "items": result}


# ── 3. SEC FORM D REGULATORY FILINGS ENDPOINTS ──

@router.get("/sec-form-d")
def get_sec_form_d_filings(
    recipient_id: Optional[int] = None,
    state: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve SEC Form D Regulation D exempt private offerings."""
    q = db.query(SecFormDFiling)

    if recipient_id:
        q = q.filter(SecFormDFiling.recipient_id == recipient_id)
    if state and state != "ALL":
        q = q.filter(SecFormDFiling.jurisdiction_state == state.upper())
    if search:
        s = f"%{search.strip()}%"
        q = q.filter(
            or_(
                SecFormDFiling.entity_legal_name.ilike(s),
                SecFormDFiling.cik_number.ilike(s),
                SecFormDFiling.primary_industry.ilike(s)
            )
        )

    total = q.count()
    items = q.order_by(desc(SecFormDFiling.filing_date)).offset((page - 1) * page_size).limit(page_size).all()
    total_capital_raised = db.query(func.sum(SecFormDFiling.total_amount_sold_usd)).scalar() or 0.0

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_capital_raised_usd": round(total_capital_raised, 2),
        "items": [
            {
                "id": f.id,
                "recipient_id": f.recipient_id,
                "cik_number": f.cik_number,
                "accession_number": f.accession_number,
                "filing_date": f.filing_date.strftime("%Y-%m-%d") if f.filing_date else None,
                "date_of_first_sale": f.date_of_first_sale.strftime("%Y-%m-%d") if f.date_of_first_sale else None,
                "entity_legal_name": f.entity_legal_name,
                "jurisdiction_state": f.jurisdiction_state,
                "primary_industry": f.primary_industry,
                "total_offering_amount_usd": f.total_offering_amount_usd,
                "total_amount_sold_usd": f.total_amount_sold_usd,
                "total_remaining_usd": f.total_remaining_usd,
                "is_equity": f.is_equity,
                "is_debt": f.is_debt,
                "num_investors": f.num_investors,
                "minimum_investment_accepted_usd": f.minimum_investment_accepted_usd,
                "executive_officers": json.loads(f.executive_officers_json) if f.executive_officers_json else [],
                "sec_html_url": f.sec_html_url
            }
            for f in items
        ]
    }


# ── 4. DOE LPO & IRA 48C SCALE-UP ALLOCATIONS ENDPOINTS ──

@router.get("/scaleup-allocations")
def get_scaleup_allocations(
    program_category: Optional[str] = None,
    state: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve DOE Loan Programs Office commitments and IRA Section 48C allocations."""
    q = db.query(FederalScaleupAllocation)

    if program_category and program_category != "ALL":
        q = q.filter(FederalScaleupAllocation.program_category.ilike(program_category))
    if state and state != "ALL":
        q = q.filter(FederalScaleupAllocation.facility_state == state.upper())
    if search:
        s = f"%{search.strip()}%"
        q = q.filter(
            or_(
                FederalScaleupAllocation.facility_name.ilike(s),
                FederalScaleupAllocation.technology_vertical.ilike(s),
                FederalScaleupAllocation.facility_city.ilike(s)
            )
        )

    allocations = q.order_by(desc(FederalScaleupAllocation.allocation_amount_usd)).all()
    total_allocated = sum(a.allocation_amount_usd for a in allocations)
    total_capex = sum(a.total_project_capex_usd or 0 for a in allocations)

    return {
        "total": len(allocations),
        "total_allocated_usd": round(total_allocated, 2),
        "total_capex_usd": round(total_capex, 2),
        "items": [
            {
                "id": a.id,
                "recipient_id": a.recipient_id,
                "facility_name": a.facility_name,
                "program_category": a.program_category,
                "support_type": a.support_type,
                "allocation_amount_usd": a.allocation_amount_usd,
                "total_project_capex_usd": a.total_project_capex_usd,
                "leverage_multiple": a.leverage_multiple,
                "facility_city": a.facility_city,
                "facility_state": a.facility_state,
                "energy_community_qualified": a.energy_community_qualified,
                "latitude": a.latitude,
                "longitude": a.longitude,
                "technology_vertical": a.technology_vertical,
                "annual_ghg_avoidance_metric_tons": a.annual_ghg_avoidance_metric_tons,
                "permanent_jobs_created": a.permanent_jobs_created,
                "status": a.status,
                "announcement_date": a.announcement_date.strftime("%Y-%m-%d") if a.announcement_date else None,
                "source_url": a.source_url,
                "summary": a.summary
            }
            for a in allocations
        ]
    }


# ── 5. FEDERAL PROCUREMENT CONTRACTS ENDPOINTS ──

@router.get("/procurement-contracts")
def get_procurement_contracts(
    recipient_id: Optional[int] = None,
    agency: Optional[str] = None,
    is_sbir_phase_3: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve federal commercial offtake and SBIR Phase III contracts."""
    q = db.query(FederalProcurementContract)

    if recipient_id:
        q = q.filter(FederalProcurementContract.recipient_id == recipient_id)
    if agency and agency != "ALL":
        q = q.filter(FederalProcurementContract.contracting_agency.ilike(f"%{agency}%"))
    if is_sbir_phase_3 is not None:
        q = q.filter(FederalProcurementContract.is_sbir_phase_3 == is_sbir_phase_3)
    if search:
        s = f"%{search.strip()}%"
        q = q.filter(
            or_(
                FederalProcurementContract.contract_number.ilike(s),
                FederalProcurementContract.contracting_agency.ilike(s),
                FederalProcurementContract.description_of_requirement.ilike(s)
            )
        )

    contracts = q.order_by(desc(FederalProcurementContract.obligated_amount_usd)).all()
    total_obligated = sum(c.obligated_amount_usd for c in contracts)

    return {
        "total": len(contracts),
        "total_obligated_usd": round(total_obligated, 2),
        "items": [
            {
                "id": c.id,
                "recipient_id": c.recipient_id,
                "contract_number": c.contract_number,
                "contracting_agency": c.contracting_agency,
                "contracting_office": c.contracting_office,
                "award_type": c.award_type,
                "is_sbir_phase_3": c.is_sbir_phase_3,
                "is_sole_source": c.is_sole_source,
                "obligated_amount_usd": c.obligated_amount_usd,
                "base_and_all_options_value_usd": c.base_and_all_options_value_usd,
                "signed_date": c.signed_date.strftime("%Y-%m-%d") if c.signed_date else None,
                "completion_date": c.completion_date.strftime("%Y-%m-%d") if c.completion_date else None,
                "place_of_performance_state": c.place_of_performance_state,
                "place_of_performance_city": c.place_of_performance_city,
                "description_of_requirement": c.description_of_requirement,
                "source_url": c.source_url
            }
            for c in contracts
        ]
    }


# ── 6. STATE DER MARKET BENCHMARKS ENDPOINTS ──

@router.get("/der-deployments/benchmarks")
def get_der_benchmarks(
    technology_type: Optional[str] = None,
    state_program: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Empirical installed cost curves ($/W & $/kWh) by year and technology."""
    q = db.query(
        DerMarketDeployment.interconnection_year,
        DerMarketDeployment.technology_type,
        DerMarketDeployment.sector,
        func.avg(DerMarketDeployment.cost_per_watt_or_kwh).label("avg_unit_cost"),
        func.count(DerMarketDeployment.id).label("total_installs"),
        func.sum(DerMarketDeployment.capacity_kw).label("total_kw")
    ).filter(DerMarketDeployment.interconnection_year != None)

    if technology_type and technology_type != "ALL":
        q = q.filter(DerMarketDeployment.technology_type.ilike(f"%{technology_type}%"))
    if state_program and state_program != "ALL":
        q = q.filter(DerMarketDeployment.state_program == state_program)

    results = q.group_by(
        DerMarketDeployment.interconnection_year,
        DerMarketDeployment.technology_type,
        DerMarketDeployment.sector
    ).order_by(DerMarketDeployment.interconnection_year).all()

    # Hardware Manufacturer Market Share
    mfg_share = db.query(
        DerMarketDeployment.equipment_manufacturer,
        func.count(DerMarketDeployment.id).label("installs_count"),
        func.sum(DerMarketDeployment.capacity_kw).label("total_mw")
    ).filter(DerMarketDeployment.equipment_manufacturer != None).group_by(
        DerMarketDeployment.equipment_manufacturer
    ).order_by(desc(func.count(DerMarketDeployment.id))).limit(10).all()

    return {
        "cost_curves": [
            {
                "year": r.interconnection_year,
                "technology_type": r.technology_type,
                "sector": r.sector,
                "avg_unit_cost": round(r.avg_unit_cost or 0.0, 2),
                "total_installs": r.total_installs,
                "total_kw": round(r.total_kw or 0.0, 1)
            }
            for r in results
        ],
        "top_manufacturers": [
            {
                "manufacturer": m.equipment_manufacturer,
                "installs_count": m.installs_count,
                "total_mw": round((m.total_mw or 0.0) / 1000.0, 2)
            }
            for m in mfg_share
        ]
    }


# ── 7. UNIVERSITY LICENSABLE IP ENDPOINTS ──

@router.get("/university-ip")
def get_university_ip(
    tech_domain: Optional[str] = None,
    technology_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve university clean tech IP licensable portfolios."""
    q = db.query(UniversityLicensableTechnology)

    if tech_domain and tech_domain != "ALL":
        q = q.filter(UniversityLicensableTechnology.tech_domain.ilike(f"%{tech_domain}%"))
    if technology_id:
        q = q.filter(UniversityLicensableTechnology.technology_id == technology_id)
    if search:
        s = f"%{search.strip()}%"
        q = q.filter(
            or_(
                UniversityLicensableTechnology.title.ilike(s),
                UniversityLicensableTechnology.abstract.ilike(s),
                UniversityLicensableTechnology.case_number.ilike(s)
            )
        )

    items = q.order_by(UniversityLicensableTechnology.title).all()

    return {
        "total": len(items),
        "items": [
            {
                "id": u.id,
                "university_id": u.university_org_id,
                "university_name": u.university.name if u.university else "University Research Office",
                "title": u.title,
                "abstract": u.abstract,
                "tech_domain": u.tech_domain,
                "technology_id": u.technology_id,
                "licensing_status": u.licensing_status,
                "trl_estimated": u.trl_estimated,
                "patent_application_number": u.patent_application_number,
                "licensing_contact_email": u.licensing_contact_email,
                "portal_url": u.portal_url,
                "case_number": u.case_number
            }
            for u in items
        ]
    }


# ── 8. UNIFIED CAPITAL STACK CONTINUUM BY RECIPIENT ──

@router.get("/recipients/{recipient_id}/capital-continuum")
def get_recipient_capital_continuum(recipient_id: int, db: Session = Depends(get_db)):
    """Full-spectrum capital progression ledger for a recipient."""
    recipient = db.get(Recipient, recipient_id)
    if not recipient:
        raise HTTPException(404, "Recipient not found")

    # 1. Non-Dilutive Grants
    awards = db.query(Award).filter(Award.recipient_name.ilike(recipient.name)).order_by(Award.award_date.asc()).all()
    
    # 2. SEC Form D Offerings
    sec_filings = db.query(SecFormDFiling).filter(SecFormDFiling.recipient_id == recipient_id).order_by(SecFormDFiling.filing_date.asc()).all()

    # 3. Climate VC Rounds
    vc_rounds = db.query(RecipientInvestment).filter(RecipientInvestment.recipient_id == recipient_id).order_by(RecipientInvestment.round_date.asc()).all()

    # 4. Patents
    patents = db.query(RecipientPatent).filter(RecipientPatent.recipient_id == recipient_id).order_by(RecipientPatent.grant_date.asc()).all()

    # 5. Federal Scale-Up Allocations (LPO & 48C)
    scaleups = db.query(FederalScaleupAllocation).filter(FederalScaleupAllocation.recipient_id == recipient_id).all()

    # 6. Federal Procurement Contracts
    contracts = db.query(FederalProcurementContract).filter(FederalProcurementContract.recipient_id == recipient_id).all()

    # 7. Grid Interconnection Queues
    queues = db.query(InterconnectionQueueProject).filter(InterconnectionQueueProject.recipient_id == recipient_id).all()

    # Summary Totals
    total_grants = sum(a.award_amount or 0 for a in awards)
    total_sec_d = sum(s.total_amount_sold_usd or 0 for s in sec_filings)
    total_vc = sum(v.amount_usd or 0 for v in vc_rounds)
    total_scaleup = sum(sc.allocation_amount_usd for sc in scaleups)
    total_procurement = sum(c.obligated_amount_usd for c in contracts)

    return {
        "recipient_id": recipient.id,
        "name": recipient.name,
        "primary_technology": recipient.primary_technology,
        "headquarters_city": recipient.headquarters_city,
        "headquarters_state": recipient.headquarters_state,
        "financial_aggregates": {
            "total_public_grants_usd": total_grants,
            "total_sec_form_d_usd": total_sec_d,
            "total_vc_investments_usd": total_vc,
            "total_scaleup_allocations_usd": total_scaleup,
            "total_procurement_offtake_usd": total_procurement,
            "grand_total_capital_usd": total_grants + total_sec_d + total_vc + total_scaleup + total_procurement
        },
        "grants": [
            {
                "id": a.id,
                "agency": a.agency,
                "award_amount": a.award_amount,
                "award_date": a.award_date.strftime("%Y-%m-%d") if a.award_date else None,
                "project_title": a.project_title,
                "solicitation_number": a.external_award_id or a.source_name
            }
            for a in awards[:15]
        ],
        "sec_form_d_filings": [
            {
                "id": s.id,
                "cik": s.cik_number,
                "filing_date": s.filing_date.strftime("%Y-%m-%d") if s.filing_date else None,
                "amount_sold_usd": s.total_amount_sold_usd,
                "num_investors": s.num_investors,
                "is_equity": s.is_equity,
                "sec_url": s.sec_html_url
            }
            for s in sec_filings
        ],
        "vc_rounds": [
            {
                "id": v.id,
                "round_type": v.round_type,
                "round_date": v.round_date.strftime("%Y-%m-%d") if v.round_date else None,
                "amount_usd": v.amount_usd,
                "lead_investor": v.lead_investor,
                "investors": json.loads(v.participating_investors_json) if v.participating_investors_json else []
            }
            for v in vc_rounds
        ],
        "patents": [
            {
                "id": p.id,
                "patent_number": p.patent_number,
                "title": p.title,
                "grant_date": p.grant_date.strftime("%Y-%m-%d") if p.grant_date else None,
                "bayh_dole_citation": p.bayh_dole_citation,
                "cited_by_count": p.cited_by_count
            }
            for p in patents
        ],
        "scaleup_allocations": [
            {
                "id": sc.id,
                "program_category": sc.program_category,
                "facility_name": sc.facility_name,
                "allocation_amount_usd": sc.allocation_amount_usd,
                "total_capex_usd": sc.total_project_capex_usd,
                "status": sc.status,
                "jobs": sc.permanent_jobs_created
            }
            for sc in scaleups
        ],
        "procurement_contracts": [
            {
                "id": pr.id,
                "contract_number": pr.contract_number,
                "agency": pr.contracting_agency,
                "obligated_amount_usd": pr.obligated_amount_usd,
                "is_sbir_phase_3": pr.is_sbir_phase_3,
                "signed_date": pr.signed_date.strftime("%Y-%m-%d") if pr.signed_date else None
            }
            for pr in contracts
        ],
        "interconnection_queues": [
            {
                "id": q.id,
                "iso_rto": q.iso_rto,
                "queue_id": q.queue_id,
                "project_name": q.project_name,
                "capacity_mw": q.capacity_mw,
                "storage_mwh": q.storage_mwh,
                "poi_substation": q.poi_substation,
                "study_phase": q.study_phase,
                "status": q.status,
                "expected_cod": q.expected_cod.strftime("%b %Y") if q.expected_cod else None
            }
            for q in queues
        ]
    }
