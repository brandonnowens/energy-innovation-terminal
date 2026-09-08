"""Real-Time Alerts & Watchlist Radar API Router."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func, or_
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models.alert import AlertSubscription, AlertTriggerLog
from app.models.opportunity import Opportunity

router = APIRouter(prefix="/alerts", tags=["Real-Time Alerts & Radar"])


class CreateAlertRequest(BaseModel):
    name: str
    keywords: Optional[str] = ""
    target_agencies: Optional[List[str]] = []
    target_states: Optional[List[str]] = []
    trl_min: Optional[int] = 1
    trl_max: Optional[int] = 9
    min_funding: Optional[float] = 0.0
    email_destination: Optional[str] = "In-Terminal Radar"
    frequency: Optional[str] = "in_terminal_daily"


@router.get("/triggers")
def list_alert_triggers(db: Session = Depends(get_db)):
    """List all configured in-terminal smart radar watchlists."""
    triggers = db.query(AlertSubscription).order_by(AlertSubscription.created_at.desc()).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "keywords": t.keywords,
            "target_agencies": t.target_agencies or [],
            "target_states": t.target_states or [],
            "trl_min": t.trl_min,
            "trl_max": t.trl_max,
            "min_funding": t.min_funding,
            "email_destination": "In-Terminal Daily Feed",
            "frequency": "In-Terminal",
            "is_active": t.is_active,
            "matches_count": t.matches_count,
            "last_triggered_at": t.last_triggered_at.isoformat() if t.last_triggered_at else None,
            "created_at": t.created_at.isoformat() if t.created_at else None
        }
        for t in triggers
    ]


@router.post("/triggers")
def create_alert_trigger(req: CreateAlertRequest, db: Session = Depends(get_db)):
    """Create a new in-terminal opportunity radar watchlist trigger."""
    sub = AlertSubscription(
        name=req.name.strip(),
        keywords=req.keywords.strip() if req.keywords else "",
        target_agencies=req.target_agencies or [],
        target_states=req.target_states or [],
        trl_min=req.trl_min or 1,
        trl_max=req.trl_max or 9,
        min_funding=req.min_funding or 0.0,
        email_destination=(req.email_destination or "In-Terminal Radar").strip(),
        frequency="in_terminal_daily",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Calculate immediate matches
    q = db.query(Opportunity)
    if sub.keywords:
        kw = f"%{sub.keywords.lower()}%"
        q = q.filter(func.lower(Opportunity.name).like(kw) | func.lower(Opportunity.short_description).like(kw))
    if sub.target_agencies:
        q = q.filter(Opportunity.agency.in_(sub.target_agencies))
    if sub.min_funding and sub.min_funding > 0:
        q = q.filter(Opportunity.total_funding >= sub.min_funding)
    
    sub.matches_count = q.count()
    sub.last_triggered_at = datetime.utcnow()
    
    db.add(sub)
    db.commit()
    db.refresh(sub)
    
    return {
        "id": sub.id,
        "name": sub.name,
        "matches_count": sub.matches_count,
        "message": f"In-Terminal Watchlist '{sub.name}' activated! Monitoring 5,741 opportunities in real time on your dashboard."
    }


@router.delete("/triggers/{trigger_id}")
def delete_alert_trigger(trigger_id: int, db: Session = Depends(get_db)):
    """Delete an existing alert trigger."""
    sub = db.query(AlertSubscription).filter(AlertSubscription.id == trigger_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Alert trigger not found")
    db.delete(sub)
    db.commit()
    return {"status": "deleted", "id": trigger_id}


@router.get("/live-matches")
def get_live_radar_matches(keywords: Optional[str] = None, agency: Optional[str] = None, min_funding: Optional[float] = None, db: Session = Depends(get_db)):
    """Live radar query testing matches across live opportunities."""
    q = db.query(Opportunity).filter(Opportunity.status.ilike("%open%"))
    if keywords:
        kw = f"%{keywords.lower()}%"
        q = q.filter(func.lower(Opportunity.name).like(kw) | func.lower(Opportunity.short_description).like(kw))
    if agency:
        q = q.filter(Opportunity.agency.ilike(f"%{agency}%"))
    if min_funding and min_funding > 0:
        q = q.filter(Opportunity.total_funding >= min_funding)
        
    opps = q.order_by(Opportunity.total_funding.desc().nulls_last()).limit(15).all()
    return [
        {
            "id": o.id,
            "solicitation_number": o.solicitation_number,
            "name": o.name,
            "agency": o.agency,
            "total_funding": o.total_funding,
            "due_date_display": o.due_date_display,
            "status": o.status
        }
        for o in opps
    ]
