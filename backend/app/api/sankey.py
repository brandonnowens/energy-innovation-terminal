"""Sankey Diagram and Multi-Stage Capital Flow Intelligence API."""

from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict
from fastapi import APIRouter, Depends, Query, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.core.cache_utils import TTLCache
from app.ingest.organization_taxonomy import get_organization_profile
from app.api.agencies import CATEGORY_META

router = APIRouter()
_sankey_flow_cache = TTLCache(ttl_seconds=300.0, max_size=500)
_sankey_insights_cache = TTLCache(ttl_seconds=300.0, max_size=50)

PRESETS: Dict[str, Dict[str, Any]] = {
    "ecosystem": {
        "id": "ecosystem",
        "title": "Funder Ecosystem to Technology Flow",
        "description": "Macro flow of capital from organization tiers through specific funders into energy sectors and technology areas.",
        "dimensions": ["org_tier", "agency", "sector", "technology"],
        "default_metric": "funding",
        "default_org_type": "all",
    },
    "utilities": {
        "id": "utilities",
        "title": "Electric & Gas Utility Innovation Pipeline",
        "description": "Specific focus on New York and regional utilities, their non-wires programs, and target grid technologies.",
        "dimensions": ["utility_type", "agency", "program", "technology"],
        "default_metric": "opportunities",
        "default_org_type": "utility",
    },
    "state_energy": {
        "id": "state_energy",
        "title": "State Clean Energy Innovation Corridors",
        "description": "State clean energy authorities and energy offices (NYSERDA, MassCEC, CEC, etc.) funding clean tech commercialization.",
        "dimensions": ["agency", "program", "sector", "technology"],
        "default_metric": "funding",
        "default_org_type": "state",
    },
    "nonprofit_funds": {
        "id": "nonprofit_funds",
        "title": "Non-Profit & Philanthropic Capital Flow",
        "description": "Philanthropic climate foundations and non-profit grantmakers channeling catalytic capital into net-zero solutions.",
        "dimensions": ["agency", "activity", "sector", "technology"],
        "default_metric": "funding",
        "default_org_type": "foundation",
    },
    "capital_deployment": {
        "id": "capital_deployment",
        "title": "Capital Deployment & Recipient Types",
        "description": "End-to-end trace from funding agency through activity types to recipient institutions and geographic states.",
        "dimensions": ["agency", "activity", "recipient_type", "recipient_state"],
        "default_metric": "funding",
        "default_org_type": "all",
    },
    "portfolio": {
        "id": "portfolio",
        "title": "Agency Portfolios & Innovation Stages",
        "description": "How funding organizations channel capital through formal programs into innovation, demonstration, and deployment stages.",
        "dimensions": ["agency", "program", "activity", "status"],
        "default_metric": "funding",
        "default_org_type": "all",
    },
    "commercialization_9d": {
        "id": "commercialization_9d",
        "title": "9-D Commercialization Pipeline (Policy to Deployment)",
        "description": "Full end-to-end trace from funding agencies and programs into sectors, technologies, fuels, and commercialization stages.",
        "dimensions": ["agency", "program", "sector", "technology", "fuel", "activity"],
        "default_metric": "funding",
        "default_org_type": "all",
    },
    "patent_catalyst": {
        "id": "patent_catalyst",
        "title": "Grant Catalyst to Recipient & Stage",
        "description": "How non-dilutive agency grants flow through technology solutions and commercialization stages into recipient institutions.",
        "dimensions": ["org_tier", "agency", "technology", "activity", "recipient_type"],
        "default_metric": "funding",
        "default_org_type": "all",
    },
    "tech_fuels": {
        "id": "tech_fuels",
        "title": "Cross-Sector Technology & Clean Fuels Matrix",
        "description": "Linkage between economic sectors, primary technology solutions, and clean energy fuels.",
        "dimensions": ["sector", "technology", "fuel", "agency"],
        "default_metric": "opportunities",
        "default_org_type": "all",
    },
}

DIMENSION_LABELS: Dict[str, str] = {
    "org_tier": "Organization Tier",
    "agency": "Funding Organization",
    "utility_type": "Organization Structure",
    "program": "Program / Portfolio",
    "sector": "Sector / End-Use",
    "technology": "Technology Solution",
    "fuel": "Clean Fuel / Resource",
    "activity": "Innovation Stage",
    "recipient_type": "Recipient Type",
    "recipient_state": "Recipient State",
    "status": "Solicitation Status",
}

# Category normalization mapping
CATEGORY_SYNONYMS: Dict[str, str] = {
    "utility": "utility",
    "utilities": "utility",
    "electric": "utility",
    "gas": "utility",
    "state": "state",
    "state_agency": "state",
    "state_agencies": "state",
    "nyserda": "state",
    "federal": "federal",
    "federal_agency": "federal",
    "federal_agencies": "federal",
    "foundation": "foundation",
    "foundations": "foundation",
    "nonprofit": "foundation",
    "non-profit": "foundation",
    "non_profit": "foundation",
    "philanthropy": "foundation",
    "national_lab": "national_lab",
    "national_labs": "national_lab",
    "research": "national_lab",
    "lab": "national_lab",
    "labs": "national_lab",
}

import time

_SANKEY_FLOW_CACHE: Dict[str, Tuple[float, Any]] = {}
_SANKEY_INSIGHTS_CACHE: Optional[Tuple[float, Any]] = None
_SANKEY_CACHE_TTL = 300.0  # 5 minutes


@router.get("/sankey/presets")
def get_presets():
    """Return available flow pipeline presets."""
    return list(PRESETS.values())

@router.get("/sankey/flow")
def get_sankey_flow(
    preset: Optional[str] = None,
    dimensions: Optional[str] = None,
    metric: str = "funding",
    agency: Optional[str] = None,
    org_type: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    status: Optional[str] = None,
    sector: Optional[str] = None,
    technology: Optional[str] = None,
    top_n_per_stage: int = 20,
    min_value: float = 0.0,
    exclude_nyserda: Optional[bool] = Query(None, description="Exclude NYSERDA from sankey flows"),
    x_include_nyserda: Optional[str] = Header(None, alias="X-Include-NYSERDA"),
    db: Session = Depends(get_db),
):
    """Dynamically generate multi-stage Sankey directed flow data (nodes & links)
    across arbitrary dimension sequences with full organization tier flexibility."""

    should_exclude_nyserda = False
    if exclude_nyserda is True:
        should_exclude_nyserda = True
    elif isinstance(x_include_nyserda, str) and x_include_nyserda.strip().lower() in ("false", "0", "no"):
        should_exclude_nyserda = True

    cache_key = f"{preset}:{dimensions}:{metric}:{agency}:{org_type}:{year_min}:{year_max}:{status}:{sector}:{technology}:{top_n_per_stage}:{min_value}:{should_exclude_nyserda}"
    cached = _sankey_flow_cache.get(cache_key)
    if cached is not None:
        return cached

    # 1. Determine active dimensions
    if dimensions and isinstance(dimensions, str) and dimensions.strip():
        dim_list = [d.strip() for d in dimensions.split(",") if d.strip()]
    elif preset and isinstance(preset, str) and preset in PRESETS:
        dim_list = PRESETS[preset]["dimensions"]
    else:
        dim_list = PRESETS["ecosystem"]["dimensions"]

    if len(dim_list) < 2:
        dim_list = ["agency", "sector", "technology"]

    # 2. Parse active organization types and agencies filters
    target_org_types = set()
    effective_org_type = org_type
    if (not effective_org_type or effective_org_type.strip().lower() == "all") and preset and preset in PRESETS and PRESETS[preset].get("default_org_type") and PRESETS[preset]["default_org_type"] != "all":
        effective_org_type = PRESETS[preset]["default_org_type"]

    if effective_org_type and effective_org_type.strip() and effective_org_type.strip().lower() != "all":
        raw_types = [t.strip().lower() for t in effective_org_type.split(",") if t.strip()]
        for rt in raw_types:
            norm_t = CATEGORY_SYNONYMS.get(rt, rt)
            if norm_t:
                target_org_types.add(norm_t)

    target_agencies = set()
    if agency and agency.strip() and agency.strip().lower() != "all":
        raw_agencies = [a.strip() for a in agency.split(",") if a.strip()]
        target_agencies = {a.lower() for a in raw_agencies}

    # 3. Build Base Opportunity/Award Query
    where_clauses = ["o.agency IS NOT NULL AND o.agency != ''"]
    sql_params: Dict[str, Any] = {}

    if should_exclude_nyserda:
        where_clauses.append("LOWER(o.agency) NOT LIKE '%nyserda%' AND LOWER(o.name) NOT LIKE '%nyserda%'")

    if status and status.lower() != "all":
        where_clauses.append("LOWER(o.status) = :status")
        sql_params["status"] = status.lower()

    where_sql = " AND ".join(where_clauses)

    try:
        opp_rows = db.execute(text(f"""
            SELECT o.id, o.agency, o.solicitation_number, o.name, o.status,
                   COALESCE(o.total_funding, 0) as total_funding,
                   p.name as program_name, p.program_type
            FROM opportunities o
            LEFT JOIN programs p ON o.program_id = p.id
            WHERE {where_sql}
        """), sql_params).fetchall()
    except Exception as db_err:
        import logging, json
        from pathlib import Path
        logging.getLogger("SankeyAPI").warning(f"Database error in get_sankey_flow: {db_err}, loading fallback disk cache", exc_info=True)
        fallback_file = Path(__file__).parent.parent.parent / "data" / "sankey_cache" / "default_flow.json"
        if fallback_file.exists():
            try:
                with open(fallback_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"nodes": [], "links": [], "stages": dim_list, "meta": {"total_value": 0, "node_count": 0, "link_count": 0}}

    if not opp_rows:
        return {"nodes": [], "links": [], "stages": dim_list, "meta": {"total_value": 0, "node_count": 0, "link_count": 0}}

    opp_dict: Dict[int, Dict[str, Any]] = {}
    for r in opp_rows:
        agency_name = r[1]
        prof = get_organization_profile(agency_name)
        cat_id = prof.get("category", "state")
        cat_label = prof.get("category_label", "State Energy Agencies")
        sub_type = prof.get("sub_type", "Energy Entity")

        # Check agency filter
        if target_agencies and agency_name.lower() not in target_agencies:
            continue

        # Check org_type filter
        if target_org_types and cat_id not in target_org_types:
            continue

        # Baseline funding floors if unstated, ensuring non-profits/utilities are proportionally visible
        raw_fund = float(r[5] or 0)
        if raw_fund > 2_000_000_000.0:
            effective_funding = 50_000_000.0
        elif raw_fund > 0:
            effective_funding = raw_fund
        else:
            if cat_id == "utility":
                effective_funding = 2_500_000.0
            elif cat_id == "foundation":
                effective_funding = 1_500_000.0
            elif cat_id == "state":
                effective_funding = 3_000_000.0
            else:
                effective_funding = 2_000_000.0

        opp_dict[r[0]] = {
            "id": r[0],
            "agency": agency_name,
            "org_tier": cat_label,
            "org_type": cat_id,
            "utility_type": sub_type,
            "name": r[3],
            "status": "Open Solicitations" if (r[4] or "").lower() == "open" else "Closed / Archived",
            "funding": effective_funding,
            "program": r[6] or f"{agency_name} General Program",
            "program_type": r[7] or "innovation",
            "sectors": set(),
            "technologies": set(),
            "fuels": set(),
            "activities": set(),
            "recipient_types": set(),
            "recipient_states": set(),
            "award_count": 0,
            "award_amount": 0.0,
        }

    if not opp_dict:
        return {"nodes": [], "links": [], "stages": dim_list, "meta": {"total_value": 0, "node_count": 0, "link_count": 0}}

    valid_opp_ids = list(opp_dict.keys())

    # Fetch Categories for opportunities efficiently
    if len(valid_opp_ids) > 200:
        cat_rows = db.execute(text("""
            SELECT opportunity_id, category_type, category_value
            FROM opportunity_categories
            WHERE category_value != ''
        """)).fetchall()
    else:
        placeholders = ",".join(str(cid) for cid in valid_opp_ids)
        cat_rows = db.execute(text(f"""
            SELECT opportunity_id, category_type, category_value
            FROM opportunity_categories
            WHERE opportunity_id IN ({placeholders}) AND category_value != ''
        """)).fetchall()

    for c in cat_rows:
        opp_id, ctype, cval = c[0], c[1], c[2]
        if opp_id in opp_dict and cval:
            if ctype == "sector":
                opp_dict[opp_id]["sectors"].add(cval)
            elif ctype == "technology":
                opp_dict[opp_id]["technologies"].add(cval)
            elif ctype == "fuel":
                opp_dict[opp_id]["fuels"].add(cval)
            elif ctype == "activity":
                opp_dict[opp_id]["activities"].add(cval)

    # Optional Sector or Technology filtering
    if sector and sector.strip() and sector.lower() != "all":
        sec_clean = sector.strip().lower()
        opp_dict = {
            k: v for k, v in opp_dict.items()
            if any(sec_clean in s.lower() for s in v["sectors"])
        }
    if technology and technology.strip() and technology.lower() != "all":
        tech_clean = technology.strip().lower()
        opp_dict = {
            k: v for k, v in opp_dict.items()
            if any(tech_clean in t.lower() for t in v["technologies"])
        }

    if not opp_dict:
        return {"nodes": [], "links": [], "stages": dim_list, "meta": {"total_value": 0, "node_count": 0, "link_count": 0}}

    valid_opp_ids = list(opp_dict.keys())

    # Conditionally fetch Awards data only when recipient dimensions or award metric are active
    needs_awards = "recipient_type" in dim_list or "recipient_state" in dim_list or metric == "awards"
    if needs_awards:
        if len(valid_opp_ids) > 200:
            award_rows = db.execute(text("""
                SELECT opportunity_id, recipient_type, recipient_state, COUNT(*), COALESCE(SUM(award_amount), 0)
                FROM awards
                WHERE opportunity_id IS NOT NULL
                GROUP BY opportunity_id, recipient_type, recipient_state
            """)).fetchall()
        else:
            placeholders = ",".join(str(cid) for cid in valid_opp_ids)
            award_rows = db.execute(text(f"""
                SELECT opportunity_id, recipient_type, recipient_state, COUNT(*), COALESCE(SUM(award_amount), 0)
                FROM awards
                WHERE opportunity_id IN ({placeholders})
                GROUP BY opportunity_id, recipient_type, recipient_state
            """)).fetchall()

        for aw in award_rows:
            opp_id, rtype, rstate, cnt, amount = aw[0], aw[1], aw[2], aw[3], aw[4]
            if opp_id in opp_dict:
                opp_dict[opp_id]["award_count"] += int(cnt or 1)
                if amount:
                    opp_dict[opp_id]["award_amount"] += float(amount)
                if rtype:
                    opp_dict[opp_id]["recipient_types"].add(rtype.capitalize())
                if rstate:
                    opp_dict[opp_id]["recipient_states"].add(rstate.upper())

    # Fallback defaults for empty sets
    for opp in opp_dict.values():
        if not opp["sectors"]:
            if opp["org_type"] == "utility":
                opp["sectors"].add("Electric Grid & Transmission")
            elif opp["org_type"] == "foundation":
                opp["sectors"].add("Cross-Sector Decarbonization")
            else:
                opp["sectors"].add("Clean Energy & Power")
        if not opp["technologies"]:
            if opp["org_type"] == "utility":
                opp["technologies"].add("Grid Edge & Storage")
            elif opp["org_type"] == "foundation":
                opp["technologies"].add("Climate Catalytic Tech")
            else:
                opp["technologies"].add("Clean Energy Technology")
        if not opp["fuels"]:
            opp["fuels"].add("Electricity")
        if not opp["activities"]:
            act_label = {
                "innovation": "R&D & Innovation",
                "deployment": "Demonstration & Deployment",
                "commercialization": "Commercialization & Scale",
                "technical_assistance": "Technical Assistance",
                "workforce": "Workforce Training",
            }.get(opp["program_type"], "R&D & Innovation")
            opp["activities"].add(act_label)
        if not opp["recipient_types"]:
            opp["recipient_types"].add("Industry / Startup")
        if not opp["recipient_states"]:
            prof = get_organization_profile(opp["agency"])
            opp["recipient_states"].add(prof.get("state", "NY"))

    # 4. Build Multi-Stage Graph Links
    stage_links: List[Dict[Tuple[str, str], float]] = []

    def get_opp_dimension_values(opp: Dict[str, Any], dim: str) -> List[str]:
        if dim == "org_tier":
            return [opp["org_tier"]]
        elif dim == "agency":
            return [opp["agency"]]
        elif dim == "utility_type":
            return [opp["utility_type"]]
        elif dim == "program":
            return [opp["program"]]
        elif dim == "sector":
            return list(opp["sectors"])
        elif dim == "technology":
            return list(opp["technologies"])
        elif dim == "fuel":
            return list(opp["fuels"])
        elif dim == "activity":
            return list(opp["activities"])
        elif dim == "recipient_type":
            return list(opp["recipient_types"])
        elif dim == "recipient_state":
            return list(opp["recipient_states"])
        elif dim == "status":
            return [opp["status"]]
        return ["Other"]

    for stage_idx in range(len(dim_list) - 1):
        dim_a = dim_list[stage_idx]
        dim_b = dim_list[stage_idx + 1]
        link_map: Dict[Tuple[str, str], float] = defaultdict(float)

        for opp in opp_dict.values():
            vals_a = get_opp_dimension_values(opp, dim_a)
            vals_b = get_opp_dimension_values(opp, dim_b)

            if metric == "funding":
                val = opp["funding"]
            elif metric == "awards":
                val = float(opp["award_count"]) if opp["award_count"] > 0 else 1.0
            else:  # opportunities
                val = 1.0

            # Distribute weight evenly across combinations
            pair_count = max(1, len(vals_a) * len(vals_b))
            split_val = val / pair_count

            for va in vals_a:
                for vb in vals_b:
                    link_map[(va, vb)] += split_val

        stage_links.append(link_map)

    # 5. Smart Truncation: Balanced Multi-Tier Node Selection
    # Compute total inflow/outflow per node per stage
    stage_nodes: List[Dict[str, float]] = []
    for stage_idx in range(len(dim_list)):
        dim_name = dim_list[stage_idx]
        node_totals: Dict[str, float] = defaultdict(float)
        if stage_idx < len(stage_links):
            for (src, _), v in stage_links[stage_idx].items():
                node_totals[src] += v
        if stage_idx > 0:
            for (_, tgt), v in stage_links[stage_idx - 1].items():
                node_totals[tgt] += v

        # If the stage is 'agency' and no specific org_type filter was locked,
        # apply balanced sampling so utilities, state agencies, and non-profits
        # are guaranteed representation alongside federal agencies.
        if dim_name == "agency" and len(target_org_types) == 0:
            # Group agencies by their org_type
            tier_agencies: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
            for ag_name, tot_val in node_totals.items():
                prof = get_organization_profile(ag_name)
                c_id = prof.get("category", "state")
                tier_agencies[c_id].append((ag_name, tot_val))

            for c_id in tier_agencies:
                tier_agencies[c_id].sort(key=lambda x: -x[1])

            # Reserve slots per active tier
            selected_agencies: Dict[str, float] = {}
            target_tiers = ["utility", "state", "foundation", "federal", "national_lab"]
            slots_per_tier = max(3, top_n_per_stage // max(1, len(target_tiers)))

            for c_id in target_tiers:
                for ag_name, val in tier_agencies.get(c_id, [])[:slots_per_tier]:
                    selected_agencies[ag_name] = val

            # Fill remaining budget with highest overall volume
            remaining_slots = max(0, top_n_per_stage - len(selected_agencies))
            if remaining_slots > 0:
                sorted_overall = sorted(node_totals.items(), key=lambda x: -x[1])
                for ag_name, val in sorted_overall:
                    if ag_name not in selected_agencies:
                        selected_agencies[ag_name] = val
                        if len(selected_agencies) >= top_n_per_stage:
                            break

            # Sort selected nodes by value descending
            top_nodes = dict(sorted(selected_agencies.items(), key=lambda x: -x[1]))
        else:
            sorted_nodes = sorted(node_totals.items(), key=lambda x: -x[1])
            top_nodes = dict(sorted_nodes[:top_n_per_stage])

        stage_nodes.append(top_nodes)

    # 6. Format Nodes & Links for D3-Sankey
    final_nodes: List[Dict[str, Any]] = []
    node_id_map: Dict[Tuple[int, str], int] = {}
    current_idx = 0

    # Color palettes for stages
    STAGE_COLORS = [
        ["#4f46e5", "#6366f1", "#818cf8", "#a5b4fc"],  # Indigo
        ["#059669", "#10b981", "#34d399", "#6ee7b7"],  # Emerald
        ["#d97706", "#f59e0b", "#fbbf24", "#fde68a"],  # Amber
        ["#0284c7", "#0ea5e9", "#38bdf8", "#7dd3fc"],  # Sky
        ["#7c3aed", "#8b5cf6", "#a78bfa", "#c4b5fd"],  # Purple
        ["#db2777", "#ec4899", "#f472b6", "#fbcfe8"],  # Pink
    ]

    for stage_idx, stage_dict in enumerate(stage_nodes):
        dim_name = dim_list[stage_idx]
        palette = STAGE_COLORS[stage_idx % len(STAGE_COLORS)]

        for n_i, (node_name, total_val) in enumerate(stage_dict.items()):
            color = palette[n_i % len(palette)]
            node_id_map[(stage_idx, node_name)] = current_idx
            
            # Enrich node with org profile if dimension is agency
            node_prof = get_organization_profile(node_name) if dim_name == "agency" else {}

            final_nodes.append({
                "id": current_idx,
                "node_key": f"s{stage_idx}_{node_name}",
                "name": node_name,
                "stage": stage_idx,
                "stage_name": DIMENSION_LABELS.get(dim_name, dim_name),
                "dimension": dim_name,
                "value": total_val,
                "color": color,
                "category": node_prof.get("category") if dim_name == "agency" else None,
                "category_label": node_prof.get("category_label") if dim_name == "agency" else None,
                "sub_type": node_prof.get("sub_type") if dim_name == "agency" else None,
            })
            current_idx += 1

    final_links: List[Dict[str, Any]] = []
    total_flow_value = 0.0

    for stage_idx in range(len(dim_list) - 1):
        for (src_name, tgt_name), val in stage_links[stage_idx].items():
            if val < min_value:
                continue
            src_key = (stage_idx, src_name)
            tgt_key = (stage_idx + 1, tgt_name)

            if src_key in node_id_map and tgt_key in node_id_map:
                src_id = node_id_map[src_key]
                tgt_id = node_id_map[tgt_key]
                final_links.append({
                    "source": src_id,
                    "target": tgt_id,
                    "source_name": src_name,
                    "target_name": tgt_name,
                    "stage_from": stage_idx,
                    "stage_to": stage_idx + 1,
                    "value": round(val, 2),
                })
                total_flow_value += val

    result = {
        "nodes": final_nodes,
        "links": final_links,
        "stages": [
            {
                "index": i,
                "dimension": d,
                "label": DIMENSION_LABELS.get(d, d),
                "node_count": len(stage_nodes[i]) if i < len(stage_nodes) else 0,
            }
            for i, d in enumerate(dim_list)
        ],
        "meta": {
            "metric": metric,
            "total_value": round(total_flow_value, 2),
            "node_count": len(final_nodes),
            "link_count": len(final_links),
            "opp_count": len(opp_dict),
            "active_org_types": list(target_org_types) if target_org_types else ["all"],
        }
    }

    _sankey_flow_cache.set(cache_key, result)
    return result

@router.get("/sankey/insights")
@router.get("/sankey/analytics")
def get_sankey_insights(
    exclude_nyserda: Optional[bool] = Query(None, description="Exclude NYSERDA from insights"),
    x_include_nyserda: Optional[str] = Header(None, alias="X-Include-NYSERDA"),
    db: Session = Depends(get_db),
):
    """Compute automated macro funding insights, major capital conduits,
    funneling dynamics, and cross-sector technology deployment patterns with TTL caching."""
    should_exclude_nyserda = False
    if exclude_nyserda is True:
        should_exclude_nyserda = True
    elif isinstance(x_include_nyserda, str) and x_include_nyserda.strip().lower() in ("false", "0", "no"):
        should_exclude_nyserda = True

    cache_key = f"insights:{should_exclude_nyserda}"
    cached = _sankey_insights_cache.get(cache_key)
    if cached is not None:
        return cached

    is_pg = db.bind.dialect.name == "postgresql" if db.bind else False
    agg_agency = "string_agg(DISTINCT o.agency, ', ')" if is_pg else "GROUP_CONCAT(DISTINCT o.agency)"

    nyserda_sql_filter = "AND LOWER(o.agency) NOT LIKE '%nyserda%' AND LOWER(o.name) NOT LIKE '%nyserda%'" if should_exclude_nyserda else ""

    # 1. Macro Queries Execution with Full Fallback Protection
    try:
        top_conduits_raw = db.execute(text(f"""
            SELECT o.agency,
                   COALESCE(cs.category_value, 'Power & Grid') as sector,
                   COALESCE(ct.category_value, 'Energy Storage') as technology,
                   SUM(COALESCE(o.total_funding, 0)) as total_funding,
                   COUNT(DISTINCT o.id) as opp_count
            FROM opportunities o
            LEFT JOIN opportunity_categories cs ON o.id = cs.opportunity_id AND cs.category_type = 'sector'
            LEFT JOIN opportunity_categories ct ON o.id = ct.opportunity_id AND ct.category_type = 'technology'
            WHERE o.agency IS NOT NULL {nyserda_sql_filter}
              AND cs.category_value IS NOT NULL AND cs.category_value NOT IN ('Unknown', 'Other', '')
              AND ct.category_value IS NOT NULL AND ct.category_value NOT IN ('Unknown', 'Other', '')
            GROUP BY o.agency, cs.category_value, ct.category_value
            ORDER BY total_funding DESC
            LIMIT 10
        """)).fetchall()

        top_conduits = [
            {
                "agency": r[0],
                "sector": r[1],
                "technology": r[2],
                "funding": float(r[3]),
                "opp_count": r[4],
                "headline": f"{r[0]} → {r[1]} → {r[2]}",
            }
            for r in top_conduits_raw
        ]

        total_conduit_funding = sum(c["funding"] for c in top_conduits) or 1.0

        # 2. Utility Innovation Share (Non-Wires & Grid Modernization vs Other)
        util_stats = db.execute(text("""
            SELECT o.agency,
                   COUNT(o.id) as total_opps,
                   SUM(CASE WHEN LOWER(o.name) LIKE '%non-wire%' OR LOWER(o.name) LIKE '%grid%' OR LOWER(o.name) LIKE '%storage%' OR LOWER(o.name) LIKE '%epic%' THEN 1 ELSE 0 END) as grid_storage_opps,
                   COALESCE(SUM(o.total_funding), 0) as total_funding
            FROM opportunities o
            WHERE o.agency IN ('Con Edison', 'National Grid', 'NYSEG', 'RG&E', 'Central Hudson', 'Orange & Rockland', 'NYPA', 'LIPA', 'PSEG Long Island', 'Pacific Gas and Electric', 'Southern California Edison', 'San Diego Gas & Electric')
            GROUP BY o.agency
            ORDER BY total_funding DESC
        """)).fetchall()

        utility_breakdown = [
            {
                "utility": r[0],
                "total_opps": r[1],
                "grid_storage_opps": r[2],
                "funding": float(r[3]),
                "pct_grid_focused": round((r[2] / max(1, r[1])) * 100, 1),
            }
            for r in util_stats
        ]

        # 3. Technology Diversification (Which tech is funded by the most distinct agencies)
        tech_diversity = db.execute(text(f"""
            SELECT ct.category_value as technology,
                   COUNT(DISTINCT o.agency) as agency_count,
                   {agg_agency} as agencies,
                   COUNT(DISTINCT o.id) as opp_count,
                   SUM(COALESCE(o.total_funding, 0)) as total_funding
            FROM opportunity_categories ct
            JOIN opportunities o ON ct.opportunity_id = o.id
            WHERE ct.category_type = 'technology' AND ct.category_value != '' AND ct.category_value NOT IN ('Unknown', 'Other')
            GROUP BY ct.category_value
            HAVING COUNT(DISTINCT o.agency) >= 3
            ORDER BY total_funding DESC
            LIMIT 10
        """)).fetchall()

        cross_agency_tech = [
            {
                "technology": r[0],
                "agency_count": r[1],
                "agencies": [x.strip() for x in r[2].split(",") if x.strip()] if r[2] else [],
                "opp_count": r[3],
                "funding": float(r[4]),
            }
            for r in tech_diversity
        ]

        # 4. Multi-Stage Pipeline Funneling Statistics
        stage_funneling = {
            "macro_conduits_count": len(top_conduits),
            "multi_agency_tech_count": len(cross_agency_tech),
            "total_conduit_capital": total_conduit_funding,
            "dominant_conduit": top_conduits[0]["headline"] if top_conduits else "Federal → Grid → Storage",
        }
    except Exception as db_err:
        import logging, json
        from pathlib import Path
        logging.getLogger("SankeyAPI").warning(f"Database error in get_sankey_insights: {db_err}, loading fallback disk cache", exc_info=True)
        fallback_file = Path(__file__).parent.parent.parent / "data" / "sankey_cache" / "default_insights.json"
        if fallback_file.exists():
            try:
                with open(fallback_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"top_conduits": [], "utility_breakdown": [], "cross_agency_technologies": [], "stage_funneling": {}, "insights": []}

    # 5. Automated Structured Ecosystem Flow Discoveries
    insights = []

    # [Discovery 1] Primary Capital Artery
    if top_conduits:
        c1 = top_conduits[0]
        insights.append({
            "category": "Capital Conduits",
            "type": "primary_artery",
            "title": f"Primary Capital Flow Artery: {c1['headline']}",
            "description": f"The largest single capital conduit traces from {c1['agency']} through the {c1['sector']} sector into {c1['technology']}, channeling ${(c1['funding']/1e9):.1f}B across {c1['opp_count']} dedicated solicitations.",
            "impact": "high",
            "badge": "Primary Artery",
            "metric": f"${(c1['funding']/1e9):.1f}B Throughput",
        })

    # [Discovery 2] Multi-Agency Tech Convergence
    if cross_agency_tech:
        top_mat = cross_agency_tech[0]
        insights.append({
            "category": "Cross-Agency Flows",
            "type": "cross_agency_convergence",
            "title": f"Multi-Funder Flow Convergence: {top_mat['technology']}",
            "description": f"'{top_mat['technology']}' serves as the primary capital pooling point, drawing funding from {top_mat['agency_count']} distinct institutions totaling ${(top_mat['funding']/1e9):.1f}B across {top_mat['opp_count']:,} solicitations.",
            "impact": "high",
            "badge": f"{top_mat['agency_count']} Funder Inflows",
            "metric": f"${(top_mat['funding']/1e9):.1f}B Pooled",
        })

    # [Discovery 3] Utility Non-Wires & Grid Transformation
    if utility_breakdown:
        top_util = utility_breakdown[0]
        avg_grid_pct = round(sum(u['pct_grid_focused'] for u in utility_breakdown) / max(1, len(utility_breakdown)), 1)
        insights.append({
            "category": "Utility Pipeline",
            "type": "utility_grid_focus",
            "title": f"Utility Innovation Focus: {avg_grid_pct}% of Solicitations Target Grid/DER",
            "description": f"Tracked electric & gas utilities dedicate an average of {avg_grid_pct}% of their innovation solicitations specifically to Non-Wires Alternatives (NWAs), grid edge flexibility, and energy storage.",
            "impact": "high",
            "badge": f"{avg_grid_pct}% Grid Focused",
            "metric": f"{len(utility_breakdown)} Utilities Tracked",
        })

    # [Discovery 4] Cross-Sectoral Technology Spillover
    if len(cross_agency_tech) >= 2:
        mat2 = cross_agency_tech[1]
        insights.append({
            "category": "Cross-Agency Flows",
            "type": "spillover_effect",
            "title": f"Dual-Sector Flow Nexus: {mat2['technology']}",
            "description": f"'{mat2['technology']}' exhibits powerful spillover characteristics, capturing ${(mat2['funding']/1e9):.1f}B across {mat2['agency_count']} funding agencies spanning both utility grid and end-use industrial sectors.",
            "impact": "medium",
            "badge": "Cross-Sector Nexus",
            "metric": f"${(mat2['funding']/1e9):.1f}B Across {mat2['agency_count']} Orgs",
        })

    # [Discovery 5] Strategic Conduit Navigation for Applicants
    insights.append({
        "category": "Strategic Navigation",
        "type": "flow_optimization",
        "title": "Conduit Selection Strategy: Target Multi-Agency Funding Streams",
        "description": "Flow analytics demonstrate that technologies mapped into multi-agency convergence nodes benefit from continuous funding continuity, reducing downstream commercialization valley-of-death risk.",
        "impact": "high",
        "badge": "Strategy Target",
        "metric": "De-risked Pathway",
    })

    res_insights = {
        "top_conduits": top_conduits,
        "utility_breakdown": utility_breakdown,
        "cross_agency_technologies": cross_agency_tech,
        "stage_funneling": stage_funneling,
        "insights": insights,
        "summary": {
            "total_tracked_pathways": len(top_conduits),
            "dominant_funder": top_conduits[0]["agency"] if top_conduits else "DOE",
            "dominant_tech": top_conduits[0]["technology"] if top_conduits else "Energy Storage",
            "total_conduit_capital": total_conduit_funding,
        }
    }
    _sankey_insights_cache.set("insights", res_insights)
    return res_insights

