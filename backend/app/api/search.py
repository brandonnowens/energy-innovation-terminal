"""Universal Database Search API Engine.
Exhaustively queries across all 12 database domains with case-insensitive token and substring matching.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, text, desc

from app.database import get_db
from app.models.award import Award
from app.models.opportunity import Opportunity
from app.models.organization import Organization
from app.models.contact import Contact
from app.models.recipient import Recipient
from app.models.attribution import RecipientPatent, RecipientInvestment
from app.models.policy import PolicyStandard, RegulatoryProceeding
from app.models.technology import Technology
from app.models.interconnection import InterconnectionQueueProject
from app.models.lab_facility import NationalLabFacility
from app.models.sec_form_d import SecFormDFiling
from app.models.news import NewsItem

router = APIRouter(tags=["Universal Search"])


@router.get("/search")
def universal_search(
    q: str = Query(..., min_length=1, description="Keyword search query across the entire clean energy innovation database"),
    domain: Optional[str] = Query("all", description="Domain filter: all, awards, opportunities, organizations, contacts, patents, venture, technologies, policies, dockets, interconnections, labs, news"),
    limit_per_domain: int = Query(15, ge=1, le=100, description="Max results to return per entity category"),
    exclude_nyserda: Optional[bool] = Query(None),
    x_include_nyserda: Optional[str] = Header(None, alias="X-Include-NYSERDA"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Comprehensive, case-insensitive universal search across all clean energy database entities:
    - Awards & Past Precedents ($104.16B capital tracked)
    - Funding Opportunities & Solicitations (5,757 FOAs)
    - Organizations & Ecosystem Partners (140+ agencies, state offices, utilities)
    - Key Contacts & Principal Investigators (3,090+ experts)
    - Bayh-Dole Act Patents & IP Citations
    - Private Venture Capital Rounds & SEC Form D Filings
    - Technology Reference Architectures
    - Policies, Tax Credits & Safety Codes (IRA §45/§48, NFPA/UL)
    - Public Utility Commission Regulatory Dockets
    - Grid Interconnection Queues (10,250 projects)
    - National Lab Facilities & Testbeds (NREL, EPRI, etc.)
    - Clean Tech News Wire
    """
    term = q.strip()
    pattern = f"%{term}%"

    should_exclude_nyserda = False
    if exclude_nyserda is True:
        should_exclude_nyserda = True
    elif isinstance(x_include_nyserda, str) and x_include_nyserda.lower() in ("false", "0", "no"):
        should_exclude_nyserda = True

    results: Dict[str, List[Dict[str, Any]]] = {
        "awards": [],
        "recipients": [],
        "opportunities": [],
        "organizations": [],
        "contacts": [],
        "patents": [],
        "venture": [],
        "technologies": [],
        "policies": [],
        "dockets": [],
        "interconnections": [],
        "labs": [],
        "news": []
    }

    counts: Dict[str, int] = {}
    domain_str = domain if isinstance(domain, str) else "all"
    target_domains = [domain_str] if domain_str != "all" else list(results.keys())
    limit_val = limit_per_domain if isinstance(limit_per_domain, int) else 15

    # 1. Awards Search (Past Precedents & Disbursements)
    if "awards" in target_domains:
        aw_q = db.query(Award).filter(
            or_(
                Award.recipient_name.ilike(pattern),
                Award.project_title.ilike(pattern),
                Award.project_abstract.ilike(pattern),
                Award.pi_name.ilike(pattern),
                Award.external_award_id.ilike(pattern),
                Award.agency.ilike(pattern),
                Award.program_name.ilike(pattern),
                Award.recipient_city.ilike(pattern),
                Award.solicitation_number.ilike(pattern),
                Award.cfda_title.ilike(pattern)
            )
        )
        if should_exclude_nyserda:
            aw_q = aw_q.filter(
                ~Award.agency.ilike("%nyserda%"),
                ~Award.source_name.ilike("%nyserda%")
            )
        counts["awards"] = aw_q.count()
        aw_rows = aw_q.order_by(desc(Award.award_amount)).limit(limit_val).all()
        results["awards"] = [{
            "id": a.id,
            "recipient_name": a.recipient_name or "Advanced Innovator",
            "project_title": a.project_title or "Clean Energy Technology Project",
            "agency": a.agency or "Public Funder",
            "award_amount": a.award_amount,
            "award_amount_formatted": f"${a.award_amount:,.2f}" if a.award_amount else "$0",
            "year": a.year,
            "state": a.recipient_state or a.recipient_country or "US",
            "city": a.recipient_city,
            "pi_name": a.pi_name,
            "solicitation_number": a.solicitation_number,
            "external_award_id": a.external_award_id,
            "to": f"/awards?search={term}"
        } for a in aw_rows]

    # 2. Awardee Companies & Scaleups (Recipients Profile)
    if "recipients" in target_domains:
        rec_q = db.query(Recipient).filter(
            or_(
                Recipient.name.ilike(pattern),
                Recipient.normalized_name.ilike(pattern),
                Recipient.description.ilike(pattern),
                Recipient.primary_technology.ilike(pattern),
                Recipient.technology_tags.ilike(pattern),
                Recipient.sector.ilike(pattern),
                Recipient.headquarters_city.ilike(pattern),
                Recipient.headquarters_state.ilike(pattern),
                Recipient.key_innovations.ilike(pattern)
            )
        )
        if should_exclude_nyserda:
            rec_q = rec_q.filter(
                ~Recipient.name.ilike("%nyserda%")
            )
        counts["recipients"] = rec_q.count()
        rec_rows = rec_q.order_by(desc(Recipient.total_funding_received)).limit(limit_val).all()
        results["recipients"] = [{
            "id": r.id,
            "name": r.name,
            "recipient_type": r.recipient_type or "Clean Tech Company",
            "primary_technology": r.primary_technology,
            "total_funding_received": r.total_funding_received,
            "total_funding_formatted": f"${r.total_funding_received:,.0f}" if r.total_funding_received else "$0",
            "city": r.headquarters_city,
            "state": r.headquarters_state,
            "website_url": r.website_url,
            "description": r.description or r.key_innovations,
            "to": f"/awards?search={term}"
        } for r in rec_rows]

    # 3. Solicitations & Funding Opportunities
    if "opportunities" in target_domains:
        opp_q = db.query(Opportunity).filter(
            or_(
                Opportunity.name.ilike(pattern),
                Opportunity.short_description.ilike(pattern),
                Opportunity.solicitation_number.ilike(pattern),
                Opportunity.agency.ilike(pattern),
                Opportunity.solicitation_type.ilike(pattern),
                Opportunity.funding_type.ilike(pattern)
            )
        )
        if should_exclude_nyserda:
            opp_q = opp_q.filter(
                ~Opportunity.agency.ilike("%nyserda%"),
                ~Opportunity.source_name.ilike("%nyserda%")
            )
        counts["opportunities"] = opp_q.count()
        opp_rows = opp_q.order_by(desc(Opportunity.total_funding)).limit(limit_val).all()
        results["opportunities"] = [{
            "id": o.id,
            "solicitation_number": o.solicitation_number or f"OPP-{o.id}",
            "name": o.name,
            "agency": o.agency,
            "total_funding": o.total_funding,
            "total_funding_formatted": f"${o.total_funding:,.0f}" if o.total_funding else "Variable",
            "max_per_award": o.max_per_award,
            "status": o.status or "Active",
            "deadline": o.deadline.strftime("%Y-%m-%d") if o.deadline else "Open",
            "short_description": o.short_description,
            "to": f"/opportunities/{o.id}"
        } for o in opp_rows]

    # 4. Organizations & Government Agencies
    if "organizations" in target_domains:
        org_q = db.query(Organization).filter(
            or_(
                Organization.name.ilike(pattern),
                Organization.description.ilike(pattern),
                Organization.city.ilike(pattern),
                Organization.state.ilike(pattern),
                Organization.org_type.ilike(pattern),
                Organization.domain.ilike(pattern)
            )
        )
        if should_exclude_nyserda:
            org_q = org_q.filter(
                ~Organization.name.ilike("%nyserda%"),
                ~Organization.domain.ilike("%nyserda%")
            )
        counts["organizations"] = org_q.count()
        org_rows = org_q.limit(limit_val).all()
        results["organizations"] = [{
            "id": org.id,
            "name": org.name,
            "org_type": org.org_type,
            "state": org.state,
            "city": org.city,
            "domain": org.domain,
            "website": org.website,
            "description": org.description,
            "to": f"/organizations"
        } for org in org_rows]

    # 5. Contacts & Principal Investigators
    if "contacts" in target_domains:
        con_q = db.query(Contact).filter(
            or_(
                Contact.name_display.ilike(pattern),
                Contact.institution_name.ilike(pattern),
                Contact.title.ilike(pattern),
                Contact.email.ilike(pattern),
                Contact.department.ilike(pattern),
                Contact.technology_area.ilike(pattern),
                Contact.sector.ilike(pattern),
                Contact.city.ilike(pattern),
                Contact.state.ilike(pattern),
                Contact.keywords.ilike(pattern)
            )
        )
        if should_exclude_nyserda:
            con_q = con_q.filter(
                ~Contact.institution_name.ilike("%nyserda%"),
                ~Contact.data_provenance.ilike("%nyserda%"),
                ~Contact.email.ilike("%nyserda%")
            )
        counts["contacts"] = con_q.count()
        con_rows = con_q.limit(limit_val).all()
        results["contacts"] = [{
            "id": c.id,
            "name_display": c.name_display,
            "title": c.title,
            "institution_name": c.institution_name,
            "email": c.email,
            "email_status": c.email_status,
            "role_type": c.role_type,
            "technology_area": c.technology_area,
            "state": c.state,
            "to": f"/contacts?search={term}"
        } for c in con_rows]

    # 6. Patents & Bayh-Dole IP Citations
    if "patents" in target_domains:
        pat_q = db.query(RecipientPatent).filter(
            or_(
                RecipientPatent.title.ilike(pattern),
                RecipientPatent.assignee_name.ilike(pattern),
                RecipientPatent.patent_number.ilike(pattern),
                RecipientPatent.bayh_dole_citation.ilike(pattern),
                RecipientPatent.abstract.ilike(pattern),
                RecipientPatent.technology_area.ilike(pattern)
            )
        )
        counts["patents"] = pat_q.count()
        pat_rows = pat_q.limit(limit_val).all()
        results["patents"] = [{
            "id": p.id,
            "patent_number": p.patent_number,
            "title": p.title,
            "assignee_name": p.assignee_name,
            "technology_area": p.technology_area,
            "grant_date": p.grant_date.strftime("%Y-%m-%d") if p.grant_date else None,
            "bayh_dole_citation": p.bayh_dole_citation,
            "to": f"/venture-patents"
        } for p in pat_rows]

    # 7. Venture Capital Deals & SEC Form D
    if "venture" in target_domains:
        sec_q = db.query(SecFormDFiling).filter(
            or_(
                SecFormDFiling.entity_legal_name.ilike(pattern),
                SecFormDFiling.primary_industry.ilike(pattern),
                SecFormDFiling.jurisdiction_state.ilike(pattern)
            )
        )
        counts["venture"] = sec_q.count()
        sec_rows = sec_q.order_by(desc(SecFormDFiling.total_offering_amount_usd)).limit(limit_val).all()
        results["venture"] = [{
            "id": s.id,
            "company_name": s.entity_legal_name,
            "total_offering_usd": s.total_offering_amount_usd,
            "total_offering_formatted": f"${s.total_offering_amount_usd:,.0f}" if s.total_offering_amount_usd else "$0",
            "total_amount_sold_usd": s.total_amount_sold_usd,
            "filing_date": s.filing_date.strftime("%Y-%m-%d") if s.filing_date else None,
            "primary_industry": s.primary_industry,
            "state": s.jurisdiction_state,
            "to": f"/venture-patents"
        } for s in sec_rows]

    # 8. Technologies Reference
    if "technologies" in target_domains:
        tech_q = db.query(Technology).filter(
            or_(
                Technology.name.ilike(pattern),
                Technology.headline.ilike(pattern),
                Technology.sector.ilike(pattern),
                Technology.fuel_vector.ilike(pattern),
                Technology.plain_what_is_it.ilike(pattern),
                Technology.keywords_json.ilike(pattern)
            )
        )
        counts["technologies"] = tech_q.count()
        tech_rows = tech_q.limit(limit_val).all()
        results["technologies"] = [{
            "id": t.id,
            "name": t.name,
            "category": t.sector or "Energy Technology",
            "description": t.headline,
            "to": f"/technologies"
        } for t in tech_rows]

    # 9. Policies, Codes & Tax Credits
    if "policies" in target_domains:
        pol_q = db.query(PolicyStandard).filter(
            or_(
                PolicyStandard.title.ilike(pattern),
                PolicyStandard.code_identifier.ilike(pattern),
                PolicyStandard.compliance_mandate.ilike(pattern),
                PolicyStandard.executive_summary.ilike(pattern),
                PolicyStandard.category.ilike(pattern),
                PolicyStandard.jurisdiction_state.ilike(pattern)
            )
        )
        counts["policies"] = pol_q.count()
        pol_rows = pol_q.limit(limit_val).all()
        results["policies"] = [{
            "id": pol.id,
            "code_identifier": pol.code_identifier,
            "title": pol.title,
            "category": pol.category,
            "jurisdiction_state": pol.jurisdiction_state,
            "executive_summary": pol.executive_summary,
            "to": f"/policies"
        } for pol in pol_rows]

    # 10. Public Utility Commission Dockets
    if "dockets" in target_domains:
        doc_q = db.query(RegulatoryProceeding).filter(
            or_(
                RegulatoryProceeding.docket_number.ilike(pattern),
                RegulatoryProceeding.title.ilike(pattern),
                RegulatoryProceeding.commission.ilike(pattern),
                RegulatoryProceeding.topic_category.ilike(pattern),
                RegulatoryProceeding.jurisdiction_state.ilike(pattern),
                RegulatoryProceeding.executive_summary.ilike(pattern),
                RegulatoryProceeding.innovation_impact.ilike(pattern)
            )
        )
        counts["dockets"] = doc_q.count()
        doc_rows = doc_q.limit(limit_val).all()
        results["dockets"] = [{
            "id": d.id,
            "docket_number": d.docket_number,
            "title": d.title,
            "commission": d.commission,
            "topic_category": d.topic_category,
            "jurisdiction_state": d.jurisdiction_state,
            "to": f"/dockets"
        } for d in doc_rows]

    # 11. Interconnection Queues
    if "interconnections" in target_domains:
        iq_q = db.query(InterconnectionQueueProject).filter(
            or_(
                InterconnectionQueueProject.project_name.ilike(pattern),
                InterconnectionQueueProject.developer_raw.ilike(pattern),
                InterconnectionQueueProject.county.ilike(pattern),
                InterconnectionQueueProject.utility_territory.ilike(pattern),
                InterconnectionQueueProject.technology_type.ilike(pattern),
                InterconnectionQueueProject.iso_rto.ilike(pattern)
            )
        )
        counts["interconnections"] = iq_q.count()
        iq_rows = iq_q.limit(limit_val).all()
        results["interconnections"] = [{
            "id": i.id,
            "project_name": i.project_name,
            "developer": i.developer_raw,
            "capacity_mw": i.capacity_mw,
            "fuel_type": i.technology_type,
            "iso_rto": i.iso_rto,
            "utility": i.utility_territory,
            "county": i.county,
            "state": i.state,
            "to": f"/awards"
        } for i in iq_rows]

    # 12. National Lab Facilities
    if "labs" in target_domains:
        lab_q = db.query(NationalLabFacility).filter(
            or_(
                NationalLabFacility.facility_name.ilike(pattern),
                NationalLabFacility.lab_name.ilike(pattern),
                NationalLabFacility.facility_type.ilike(pattern),
                NationalLabFacility.summary.ilike(pattern),
                NationalLabFacility.capabilities_json.ilike(pattern),
                NationalLabFacility.city.ilike(pattern),
                NationalLabFacility.state.ilike(pattern)
            )
        )
        counts["labs"] = lab_q.count()
        lab_rows = lab_q.limit(limit_val).all()
        results["labs"] = [{
            "id": l.id,
            "name": l.facility_name,
            "parent_lab": l.lab_name,
            "facility_type": l.facility_type,
            "focus_areas": l.summary,
            "city": l.city,
            "state": l.state,
            "to": f"/network"
        } for l in lab_rows]

    # 13. Clean Tech News Wire
    if "news" in target_domains:
        news_q = db.query(NewsItem).filter(
            or_(
                NewsItem.title.ilike(pattern),
                NewsItem.summary.ilike(pattern),
                NewsItem.source_name.ilike(pattern),
                NewsItem.source_domain.ilike(pattern)
            )
        )
        counts["news"] = news_q.count()
        news_rows = news_q.order_by(desc(NewsItem.published_at)).limit(limit_val).all()
        results["news"] = [{
            "id": n.id,
            "title": n.title,
            "summary": n.summary,
            "category": "Clean Tech News",
            "source_domain": n.source_domain or n.source_name,
            "published_at": n.published_at.strftime("%Y-%m-%d") if n.published_at else None,
            "to": f"/updates"
        } for n in news_rows]

    total_matches = sum(counts.values())

    return {
        "query": term,
        "total_matches": total_matches,
        "counts": counts,
        "results": results
    }
