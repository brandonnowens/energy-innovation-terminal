"""Relationships API - single opportunity lookups and network graph data."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional

from app.database import get_db
from app.models.opportunity import Opportunity
from app.models.relationship import OpportunityRelationship

router = APIRouter()


@router.get("/relationships")
def get_relationships(
    opportunity_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Get relationships for a specific opportunity."""
    rels = db.query(OpportunityRelationship).filter(
        or_(
            OpportunityRelationship.source_opp_id == opportunity_id,
            OpportunityRelationship.target_opp_id == opportunity_id,
        )
    ).all()

    result = []
    for r in rels:
        is_source = r.source_opp_id == opportunity_id
        other_id = r.target_opp_id if is_source else r.source_opp_id
        other_opp = db.query(Opportunity).get(other_id)
        if not other_opp:
            continue
        result.append({
            "relationship_id": r.id,
            "relationship_type": r.relationship_type,
            "confidence": r.confidence,
            "rationale": r.rationale,
            "evidence": r.evidence,
            "is_inferred": r.is_inferred,
            "direction": "outbound" if is_source else "inbound",
            "related_opportunity": {
                "id": other_opp.id,
                "solicitation_number": other_opp.solicitation_number,
                "name": other_opp.name,
                "agency": other_opp.agency,
                "status": other_opp.status,
                "year": getattr(other_opp, "year", None),
                "keywords": getattr(other_opp, "keywords", None),
            },
        })
    return result


@router.get("/relationships/network")
def get_relationship_network(
    relationship_type: Optional[str] = None,
    agency: Optional[str] = None,
    min_confidence: float = 0.0,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    is_historical: Optional[bool] = None,
    limit: int = Query(500, le=2000),
    db: Session = Depends(get_db),
):
    """Get relationship network data for visualization (nodes + edges).

    Returns a graph structure suitable for network diagrams:
    - nodes: unique opportunities with agency, name, status, year, keywords
    - edges: relationships with type, confidence, rationale
    - summary: aggregate counts by type, agency connectivity
    """
    query = db.query(OpportunityRelationship).filter(
        OpportunityRelationship.confidence >= min_confidence
    )
    if relationship_type:
        query = query.filter(OpportunityRelationship.relationship_type == relationship_type)

    # If filtering by agency, only include relationships where at least one side is that agency
    if agency:
        agency_ids = [
            o.id
            for o in db.query(Opportunity.id).filter(Opportunity.agency == agency).all()
        ]
        if not agency_ids:
            return {"nodes": [], "edges": [], "summary": {}}
        query = query.filter(
            or_(
                OpportunityRelationship.source_opp_id.in_(agency_ids),
                OpportunityRelationship.target_opp_id.in_(agency_ids),
            )
        )

    # Year and historical filters - restrict to relationships where at least one node matches
    if year_min is not None or year_max is not None or is_historical is not None:
        opp_filter = db.query(Opportunity.id)
        if year_min is not None:
            opp_filter = opp_filter.filter(Opportunity.year >= year_min)
        if year_max is not None:
            opp_filter = opp_filter.filter(Opportunity.year <= year_max)
        if is_historical is not None:
            opp_filter = opp_filter.filter(Opportunity.is_historical == is_historical)
        filtered_ids = [o.id for o in opp_filter.all()]
        if not filtered_ids:
            return {"nodes": [], "edges": [], "summary": {"total_nodes": 0, "total_edges": 0, "by_type": {}, "top_cross_agency_connections": []}}
        query = query.filter(
            or_(
                OpportunityRelationship.source_opp_id.in_(filtered_ids),
                OpportunityRelationship.target_opp_id.in_(filtered_ids),
            )
        )

    rels = query.order_by(OpportunityRelationship.confidence.desc()).limit(limit).all()

    # Collect unique node IDs
    node_ids = set()
    edges = []
    for r in rels:
        node_ids.add(r.source_opp_id)
        node_ids.add(r.target_opp_id)
        edges.append({
            "id": r.id,
            "source": r.source_opp_id,
            "target": r.target_opp_id,
            "type": r.relationship_type,
            "confidence": r.confidence,
            "rationale": r.rationale,
            "evidence": r.evidence,
        })

    # Load node details
    nodes = []
    if node_ids:
        opps = db.query(Opportunity).filter(Opportunity.id.in_(node_ids)).all()
        for o in opps:
            nodes.append({
                "id": o.id,
                "name": o.name,
                "agency": o.agency,
                "status": o.status,
                "year": getattr(o, "year", None),
                "keywords": getattr(o, "keywords", None),
                "is_historical": getattr(o, "is_historical", False),
                "solicitation_number": o.solicitation_number,
            })

    # Summary stats
    type_counts = {}
    agency_connections = {}
    for e in edges:
        t = e["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    node_map = {n["id"]: n for n in nodes}
    for e in edges:
        src = node_map.get(e["source"], {})
        tgt = node_map.get(e["target"], {})
        a1, a2 = src.get("agency", "?"), tgt.get("agency", "?")
        if a1 != a2:
            pair = tuple(sorted([a1, a2]))
            agency_connections[pair] = agency_connections.get(pair, 0) + 1

    # Top cross-agency connections
    top_connections = sorted(agency_connections.items(), key=lambda x: -x[1])[:20]

    return {
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "by_type": type_counts,
            "top_cross_agency_connections": [
                {"agencies": list(pair), "count": cnt}
                for pair, cnt in top_connections
            ],
        },
    }


@router.get("/relationships/stats")
def get_relationship_stats(db: Session = Depends(get_db)):
    """Get aggregate relationship statistics."""
    total = db.query(func.count(OpportunityRelationship.id)).scalar()

    by_type = db.query(
        OpportunityRelationship.relationship_type,
        func.count(),
        func.avg(OpportunityRelationship.confidence),
    ).group_by(OpportunityRelationship.relationship_type).all()

    return {
        "total_relationships": total,
        "by_type": [
            {
                "type": t,
                "count": c,
                "avg_confidence": round(float(avg), 2) if avg else 0,
            }
            for t, c, avg in by_type
        ],
    }
