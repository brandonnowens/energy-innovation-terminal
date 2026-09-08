"""
Technology & Fuels Reference & Innovation Frontier API endpoints.
Provides structured dossiers, fuel carrier profiles, live database evidence, and on-demand AI specialist insights.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.engine.tech_reference import (
    CATEGORIES,
    TECHNOLOGY_REGISTRY,
    get_technology_categories,
    get_technologies_list,
    get_technology_dossier,
    get_technology_subsystems,
    get_comparative_technologies_matrix,
    get_fuel_pathways_matrix,
    get_frontier_matrix,
    synthesize_technology_insights
)

router = APIRouter(prefix="/tech-reference", tags=["Technology & Fuels Reference"])


class TechInsightRequest(BaseModel):
    custom_question: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = "gpt-4o-mini"
    force_refresh: Optional[bool] = False


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Returns all 15 major clean tech & fuels innovation sectors from the database."""
    return get_technology_categories(db)


@router.get("/technologies")
def list_technologies(
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search by technology/fuel name or keyword"),
    vector_type: Optional[str] = Query(None, description="Filter by innovation vector: hardware, fuel_carrier, or all"),
    db: Session = Depends(get_db)
):
    """Returns a list of all technology & fuels reference records from the database."""
    return get_technologies_list(db, category_id=category_id, search=search, vector_type=vector_type)


@router.get("/compare")
def compare_technologies(
    ids: str = Query(..., description="Comma-separated list of technology IDs to compare (e.g. iron_air_battery,vanadium_redox_flow)"),
    db: Session = Depends(get_db)
):
    """Returns structured side-by-side comparative matrices for 2 to 4 technologies."""
    tech_ids = [t.strip() for t in ids.split(",") if t.strip()]
    if not tech_ids:
        raise HTTPException(status_code=400, detail="Please provide at least one valid technology ID in 'ids' query parameter.")
    return get_comparative_technologies_matrix(db, tech_ids)


@router.get("/fuels-matrix")
def get_fuels_matrix(db: Session = Depends(get_db)):
    """Returns structured Carbon Intensity, energy density, and policy incentive data for all zero-carbon fuel carriers."""
    return get_fuel_pathways_matrix(db)


@router.get("/frontier-matrix")
def get_frontier_matrix_endpoint(db: Session = Depends(get_db)):
    """Returns all 36 technologies with normalized metrics for scatter/quadrant analysis."""
    return get_frontier_matrix(db)


@router.get("/technologies/{tech_id}")
def get_technology(
    tech_id: str,
    db: Session = Depends(get_db)
):
    """Returns full structured technology & fuels dossier with fuel carrier metrics, real-time database facts, and radar metrics."""
    dossier = get_technology_dossier(db, tech_id)
    if not dossier:
        raise HTTPException(status_code=404, detail=f"Technology/Fuel '{tech_id}' not found.")
    
    # Enrich with Brandon Owens Technology Bankability Rating (TBR)
    from app.engine.bankability_engine import calculate_technology_bankability
    bankability = calculate_technology_bankability(db, tech_id, dossier.get("name"))
    dossier["bankability"] = bankability
    return dossier


@router.get("/technologies/{tech_id}/bankability")
def get_technology_bankability_endpoint(
    tech_id: str,
    db: Session = Depends(get_db)
):
    """Returns the Brandon Owens Technology Bankability Rating (TBR) scorecard and Causal Lineage."""
    from app.engine.bankability_engine import calculate_technology_bankability
    return calculate_technology_bankability(db, tech_id)


@router.get("/technologies/{tech_id}/subsystems")
def get_subsystems(
    tech_id: str,
    db: Session = Depends(get_db)
):
    """Returns subsystem architecture nodes and materials science specs for a technology."""
    subsystems = get_technology_subsystems(db, tech_id)
    return {"technology_id": tech_id, "subsystems": subsystems}


@router.post("/technologies/{tech_id}/ai-insights")
def get_ai_technology_insights(
    tech_id: str,
    req: TechInsightRequest,
    authorization: Optional[str] = Header(None)
):
    """
    On-demand AI technical & fuel specialist Q&A and frontier synthesis.
    Queries OpenAI API with prompt optimization, SHA-256 disk caching, and clean deterministic fallback.
    """
    api_key = req.api_key
    if not api_key and authorization and authorization.startswith("Bearer "):
        candidate = authorization.replace("Bearer ", "").strip()
        if candidate.startswith("sk-"):
            api_key = candidate

    insights = synthesize_technology_insights(
        tech_id=tech_id,
        custom_question=req.custom_question,
        api_key=api_key,
        model_name=req.model_name or "gpt-4o-mini",
        force_refresh=req.force_refresh or False
    )
    if "error" in insights:
        raise HTTPException(status_code=404, detail=insights["error"])
    return insights


@router.get("/stats")
def get_tech_reference_macro_stats(db: Session = Depends(get_db)):
    """Returns macro summary metrics across the entire technology & fuels reference knowledge base."""
    total_technologies = len(TECHNOLOGY_REGISTRY)
    total_categories = len(CATEGORIES)
    return {
        "total_technologies": total_technologies,
        "total_categories": total_categories,
        "trl_range": "TRL 4 – TRL 9",
        "sectors_covered": 15,
        "standards_reference": "Energy Innovation Terminal Master Technology & Fuels Taxonomy (2026–2035 Horizon)"
    }


