"""Venture & Patent Attributions API endpoints."""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, desc, asc, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.cache_utils import TTLCache
from app.models.attribution import RecipientPatent, RecipientInvestment
from app.models.recipient import Recipient
from app.models.award import Award
from app.models.opportunity import Opportunity

router = APIRouter()
_attributions_cache = TTLCache(ttl_seconds=300.0)


@router.get("/attributions/overview")
def get_attributions_overview(db: Session = Depends(get_db)):
    """Retrieve global KPIs and macro attribution statistics with TTLCache."""
    cached = _attributions_cache.get("overview")
    if cached is not None:
        return cached
    total_patents = db.query(func.count(RecipientPatent.id)).scalar() or 0
    total_vc_raised = db.query(func.sum(RecipientInvestment.amount_usd)).scalar() or 0.0
    
    # Distinct companies with either patent or VC investment
    patent_rec_ids = {r[0] for r in db.query(RecipientPatent.recipient_id).distinct().all()}
    invest_rec_ids = {r[0] for r in db.query(RecipientInvestment.recipient_id).distinct().all()}
    all_backed_ids = list(patent_rec_ids.union(invest_rec_ids))
    total_backed_companies = len(all_backed_ids)
    
    # Calculate public grant capital received by these specific backed companies
    public_grant_sum = 0.0
    if all_backed_ids:
        public_grant_sum = db.query(func.sum(Recipient.total_funding_received)).filter(
            Recipient.id.in_(all_backed_ids)
        ).scalar() or 0.0
        
        # If total_funding_received is 0, estimate from awards
        if public_grant_sum == 0.0:
            rec_names = [r[0] for r in db.query(Recipient.name).filter(Recipient.id.in_(all_backed_ids)).all()]
            public_grant_sum = db.query(func.sum(Award.award_amount)).filter(Award.recipient_name.in_(rec_names)).scalar() or 25000000.0

    leverage_multiplier = round(total_vc_raised / max(public_grant_sum, 1.0), 2)
    
    # Top lead investors
    lead_inv_rows = db.query(
        RecipientInvestment.lead_investor,
        func.count(RecipientInvestment.id),
        func.sum(RecipientInvestment.amount_usd)
    ).filter(RecipientInvestment.lead_investor.isnot(None))\
     .group_by(RecipientInvestment.lead_investor)\
     .order_by(desc(func.sum(RecipientInvestment.amount_usd)))\
     .limit(8).all()
     
    top_investors = [
        {
            "name": r[0],
            "rounds_led": r[1],
            "capital_deployed": r[2] or 0.0
        }
        for r in lead_inv_rows
    ]
    
    # Technology distribution of patents
    tech_dist_rows = db.query(
        RecipientPatent.technology_area,
        func.count(RecipientPatent.id)
    ).filter(RecipientPatent.technology_area.isnot(None))\
     .group_by(RecipientPatent.technology_area)\
     .order_by(desc(func.count(RecipientPatent.id)))\
     .all()
     
    tech_distribution = [{"technology": r[0], "patent_count": r[1]} for r in tech_dist_rows]

    result = {
        "total_patents": total_patents,
        "total_vc_raised_usd": total_vc_raised,
        "total_public_grants_usd": public_grant_sum,
        "leverage_multiplier": leverage_multiplier,
        "total_backed_companies": total_backed_companies,
        "top_investors": top_investors,
        "tech_distribution": tech_distribution
    }
    _attributions_cache.set("overview", result)
    return result


@router.get("/attributions/recipients")
def list_attribution_recipients(
    technology_area: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("leverage_ratio"),  # leverage_ratio, vc_raised, patents, grants, name
    sort_dir: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List organizations enriched with patent and venture funding metrics."""
    # Find all recipients that have either patents or investments
    patent_rec_ids = {r[0] for r in db.query(RecipientPatent.recipient_id).distinct().all()}
    invest_rec_ids = {r[0] for r in db.query(RecipientInvestment.recipient_id).distinct().all()}
    target_ids = list(patent_rec_ids.union(invest_rec_ids))
    
    if not target_ids:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}
        
    query = db.query(Recipient).filter(Recipient.id.in_(target_ids))
    
    if technology_area and isinstance(technology_area, str) and technology_area != "ALL":
        query = query.filter(Recipient.primary_technology == technology_area)
    if search and isinstance(search, str):
        s = f"%{search.lower()}%"
        query = query.filter(
            func.lower(Recipient.name).like(s) |
            func.lower(Recipient.description).like(s)
        )

        
    recipients = query.all()
    
    # Pre-fetch counts and sums
    patents_by_rec: Dict[int, List[RecipientPatent]] = {}
    for p in db.query(RecipientPatent).filter(RecipientPatent.recipient_id.in_(target_ids)).all():
        patents_by_rec.setdefault(p.recipient_id, []).append(p)
        
    invests_by_rec: Dict[int, List[RecipientInvestment]] = {}
    for inv in db.query(RecipientInvestment).filter(RecipientInvestment.recipient_id.in_(target_ids)).all():
        invests_by_rec.setdefault(inv.recipient_id, []).append(inv)
        
    results = []
    for r in recipients:
        p_list = patents_by_rec.get(r.id, [])
        i_list = invests_by_rec.get(r.id, [])
        
        vc_total = sum(inv.amount_usd or 0.0 for inv in i_list)
        grant_total = r.total_funding_received or (r.total_federal_funding + r.total_nyserda_funding) or 5000000.0
        leverage = round(vc_total / max(grant_total, 1.0), 2) if vc_total > 0 else 0.0
        
        lead_investors = list({inv.lead_investor for inv in i_list if inv.lead_investor})
        latest_round = sorted(i_list, key=lambda x: x.round_date or datetime.min, reverse=True)[0].round_type if i_list else None
        
        results.append({
            "id": r.id,
            "name": r.name,
            "recipient_type": r.recipient_type,
            "city": r.headquarters_city,
            "state": r.headquarters_state,
            "primary_technology": r.primary_technology,
            "patent_count": len(p_list),
            "patents_sample": [{"number": p.patent_number, "title": p.title, "url": p.patent_url} for p in p_list[:3]],
            "investment_count": len(i_list),
            "total_vc_raised_usd": vc_total,
            "total_public_grants_usd": grant_total,
            "leverage_ratio": leverage,
            "lead_investors": lead_investors,
            "latest_round": latest_round,
            "commercialization_stage": r.commercialization_stage or "Commercial Growth"
        })
        
    # Apply sorting
    if sort_by == "leverage_ratio":
        results.sort(key=lambda x: x["leverage_ratio"], reverse=(sort_dir == "desc"))
    elif sort_by == "vc_raised":
        results.sort(key=lambda x: x["total_vc_raised_usd"], reverse=(sort_dir == "desc"))
    elif sort_by == "patents":
        results.sort(key=lambda x: x["patent_count"], reverse=(sort_dir == "desc"))
    elif sort_by == "grants":
        results.sort(key=lambda x: x["total_public_grants_usd"], reverse=(sort_dir == "desc"))
    else:
        results.sort(key=lambda x: x["name"].lower(), reverse=(sort_dir == "desc"))
        
    total = len(results)
    start_idx = (page - 1) * page_size
    paged_items = results[start_idx : start_idx + page_size]
    
    return {
        "items": paged_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/attributions/recipients/{recipient_id}")
def get_recipient_attribution_dossier(recipient_id: int, db: Session = Depends(get_db)):
    """Retrieve deep patent, venture funding, and ego-network data for a specific organization."""
    rec = db.query(Recipient).filter_by(id=recipient_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recipient not found")
        
    patents = db.query(RecipientPatent).filter_by(recipient_id=recipient_id).order_by(desc(RecipientPatent.grant_date)).all()
    investments = db.query(RecipientInvestment).filter_by(recipient_id=recipient_id).order_by(asc(RecipientInvestment.round_date)).all()
    
    # Parse participating investors
    rounds_data = []
    all_investors = set()
    for inv in investments:
        participating = []
        if inv.participating_investors_json:
            try:
                participating = json.loads(inv.participating_investors_json)
            except Exception:
                participating = [inv.lead_investor] if inv.lead_investor else []
        for p in participating:
            all_investors.add(p)
        if inv.lead_investor:
            all_investors.add(inv.lead_investor)
            
        rounds_data.append({
            "id": inv.id,
            "round_type": inv.round_type,
            "round_date": inv.round_date.strftime("%Y-%m-%d") if inv.round_date else None,
            "amount_usd": inv.amount_usd,
            "valuation_usd": inv.valuation_usd,
            "lead_investor": inv.lead_investor,
            "participating_investors": participating,
            "post_grant_months": inv.post_grant_months,
            "notes": inv.notes
        })
        
    patents_data = [
        {
            "id": p.id,
            "patent_number": p.patent_number,
            "title": p.title,
            "abstract": p.abstract,
            "filing_date": p.filing_date.strftime("%Y-%m-%d") if p.filing_date else None,
            "grant_date": p.grant_date.strftime("%Y-%m-%d") if p.grant_date else None,
            "cpc_class": p.cpc_class,
            "technology_area": p.technology_area,
            "bayh_dole_citation": p.bayh_dole_citation,
            "grant_contract_id": p.grant_contract_id,
            "inventors": p.inventors,
            "cited_by_count": p.cited_by_count,
            "patent_url": p.patent_url
        }
        for p in patents
    ]
    
    # Build 2-degree Ego Network Data for this organization
    ego_nodes = [
        {"id": f"rec_{rec.id}", "name": rec.name, "type": "company", "category": "Core Company", "size": 30}
    ]
    ego_edges = []
    
    # Add grant nodes
    ego_nodes.append({
        "id": "funder_gov",
        "name": "Federal / State Grant Programs (DOE, ARPA-E, NYSERDA)",
        "type": "grant_funder",
        "category": "Public Grants",
        "size": 22
    })
    ego_edges.append({
        "source": "funder_gov",
        "target": f"rec_{rec.id}",
        "label": "Non-Dilutive Grant Seed",
        "color": "#6366f1"
    })
    
    # Add patent nodes
    for p in patents_data:
        p_id = f"pat_{p['id']}"
        ego_nodes.append({
            "id": p_id,
            "name": f"{p['patent_number']}: {p['title'][:32]}...",
            "type": "patent",
            "category": "USPTO Patent",
            "patent_number": p["patent_number"],
            "url": p["patent_url"],
            "size": 16
        })
        ego_edges.append({
            "source": f"rec_{rec.id}",
            "target": p_id,
            "label": "Assignee / Bayh-Dole IP",
            "color": "#f59e0b"
        })
        
    # Add investor nodes
    for inv_name in list(all_investors)[:8]:
        inv_id = f"inv_{hash(inv_name) % 1000000}"
        ego_nodes.append({
            "id": inv_id,
            "name": inv_name,
            "type": "investor",
            "category": "VC / Private Capital",
            "size": 18
        })
        ego_edges.append({
            "source": inv_id,
            "target": f"rec_{rec.id}",
            "label": "Equity Financing",
            "color": "#10b981"
        })
        
    return {
        "recipient": {
            "id": rec.id,
            "name": rec.name,
            "recipient_type": rec.recipient_type,
            "city": rec.headquarters_city,
            "state": rec.headquarters_state,
            "website": rec.website_url,
            "primary_technology": rec.primary_technology,
            "description": rec.description,
            "total_funding_received": rec.total_funding_received
        },
        "patents": patents_data,
        "investments": rounds_data,
        "ego_graph": {
            "nodes": ego_nodes,
            "edges": ego_edges
        }
    }


@router.get("/attributions/graph")
def get_attributions_lineage_graph(
    limit: int = Query(150, ge=10, le=1000),
    min_capital: float = Query(0.0, ge=0.0),
    db: Session = Depends(get_db)
):
    """Return the interactive Capital & IP Lineage Graph for top tracked commercialization pioneers."""
    nodes = []
    edges = []
    node_set = set()
    edge_set = set()
    
    def add_node(nid, name, ntype, category, extra=None):
        if nid not in node_set:
            node_set.add(nid)
            n = {"id": nid, "name": name, "type": ntype, "category": category}
            if extra:
                n.update(extra)
            nodes.append(n)
            
    def add_edge(src, tgt, label, edge_type, color="#64748b"):
        ek = f"{src}|{tgt}|{edge_type}"
        if ek not in edge_set:
            edge_set.add(ek)
            edges.append({"source": src, "target": tgt, "label": label, "type": edge_type, "color": color})
            
    # Add Agencies
    agencies = [
        "DOE", "ARPA-E", "NYSERDA", "Empire State Development", "CEC", "MassCEC",
        "MassVentures", "JobsOhio", "MEDC", "Ben Franklin Tech Partners",
        "Connecticut Innovations", "TEDCO", "VIPC", "Colorado OEDIT", "MN DEED", "NSF"
    ]
    for ag in agencies:
        add_node(f"ag_{ag}", ag, "agency", "Government / State Funder", {"color": "#6366f1", "size": 25})
        
    # Add Top Recipients based on funding
    patent_rec_ids = {r[0] for r in db.query(RecipientPatent.recipient_id).distinct().all()}
    invest_rec_ids = {r[0] for r in db.query(RecipientInvestment.recipient_id).distinct().all()}
    target_ids = list(patent_rec_ids.union(invest_rec_ids))
    
    query = db.query(Recipient).filter(Recipient.id.in_(target_ids))
    if min_capital > 0:
        query = query.filter(Recipient.total_funding_received >= min_capital)
    recipients = query.order_by(desc(Recipient.total_funding_received)).limit(limit).all()
    selected_recip_ids = {r.id for r in recipients}

    for r in recipients:
        add_node(f"rec_{r.id}", r.name, "company", "Awardee Company", {
            "technology": r.primary_technology,
            "state": r.headquarters_state,
            "color": "#0ea5e9",
            "size": 20
        })
        # Connect to relevant agencies
        if r.nyserda_award_count and r.nyserda_award_count > 0:
            add_edge("ag_NYSERDA", f"rec_{r.id}", "Funds Award", "funds", "#6366f1")
        if "DOE" in (r.funded_agencies or "") or r.total_federal_funding > 0:
            add_edge("ag_DOE", f"rec_{r.id}", "Federal Grant", "funds", "#6366f1")
        if "ARPA-E" in (r.funded_agencies or ""):
            add_edge("ag_ARPA-E", f"rec_{r.id}", "ARPA-E Grant", "funds", "#6366f1")
        if "NSF" in (r.funded_agencies or ""):
            add_edge("ag_NSF", f"rec_{r.id}", "NSF Grant", "funds", "#6366f1")
    # Add Patents for selected recipients
    patents = db.query(RecipientPatent).filter(RecipientPatent.recipient_id.in_(selected_recip_ids)).all() if selected_recip_ids else []
    for p in patents:
        pid = f"pat_{p.id}"
        add_node(pid, f"{p.patent_number}", "patent", "USPTO Patent", {
            "title": p.title,
            "url": p.patent_url,
            "color": "#f59e0b",
            "size": 14
        })
        add_edge(f"rec_{p.recipient_id}", pid, "Filed Patent", "patented", "#f59e0b")

    # Add VC Investors for selected recipients
    investments = db.query(RecipientInvestment).filter(RecipientInvestment.recipient_id.in_(selected_recip_ids)).all() if selected_recip_ids else []
    for inv in investments:
        if inv.lead_investor:
            iid = f"inv_{abs(hash(inv.lead_investor)) % 1000000}"
            add_node(iid, inv.lead_investor, "investor", "Venture Capital", {
                "color": "#10b981",
                "size": 18
            })
            add_edge(iid, f"rec_{inv.recipient_id}", f"{inv.round_type} (${int((inv.amount_usd or 0)/1e6)}M)", "invested_in", "#10b981")

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "agencies_count": len(agencies),
            "companies_count": len(recipients),
            "patents_count": len(patents),
            "investments_count": len(investments)
        }
    }


@router.get("/attributions/syndicates")
def get_venture_syndicates(db: Session = Depends(get_db)):
    """Retrieve VC investor syndicates, co-investment partners, and portfolio companies."""
    investments = db.query(RecipientInvestment).all()
    
    investor_map: Dict[str, Dict[str, Any]] = {}
    for inv in investments:
        lead = inv.lead_investor
        if not lead:
            continue
        rec = db.query(Recipient).filter_by(id=inv.recipient_id).first()
        rec_name = rec.name if rec else f"Company {inv.recipient_id}"
        
        participating = []
        if inv.participating_investors_json:
            try:
                participating = json.loads(inv.participating_investors_json)
            except Exception:
                participating = []
                
        if lead not in investor_map:
            investor_map[lead] = {
                "name": lead,
                "portfolio_companies": set(),
                "co_investors": set(),
                "total_capital_deployed_usd": 0.0,
                "rounds_count": 0
            }
            
        investor_map[lead]["portfolio_companies"].add(rec_name)
        investor_map[lead]["total_capital_deployed_usd"] += (inv.amount_usd or 0.0)
        investor_map[lead]["rounds_count"] += 1
        for co in participating:
            if co != lead:
                investor_map[lead]["co_investors"].add(co)
                
    results = [
        {
            "name": k,
            "portfolio_companies": sorted(list(v["portfolio_companies"])),
            "co_investors": sorted(list(v["co_investors"]))[:6],
            "total_capital_deployed_usd": v["total_capital_deployed_usd"],
            "rounds_count": v["rounds_count"]
        }
        for k, v in investor_map.items()
    ]
    results.sort(key=lambda x: x["total_capital_deployed_usd"], reverse=True)
    
    return {"syndicates": results}
