"""Community API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.community import CreatorToken, generate_token, hash_token, AbuseReport
from pydantic import BaseModel

router = APIRouter()

def get_creator_hash(x_creator_token: str = Header(None)):
    if not x_creator_token:
        return None
    return hash_token(x_creator_token)

def require_creator_hash(x_creator_token: str = Header(None)) -> str:
    h = get_creator_hash(x_creator_token)
    if not h:
        raise HTTPException(status_code=401, detail="X-Creator-Token header required")
    return h

class ReportRequest(BaseModel):
    item_type: str
    item_id: int
    reason: str

@router.post("/community/token")
def create_token(db: Session = Depends(get_db)):
    token = generate_token()
    recovery_key = generate_token()
    
    t_hash = hash_token(token)
    r_hash = hash_token(recovery_key)
    
    ct = CreatorToken(token_hash=t_hash, recovery_key_hash=r_hash)
    db.add(ct)
    db.commit()
    
    return {
        "token": token,
        "recovery_key": recovery_key
    }

@router.post("/community/verify")
def verify_token(creator_hash: str = Depends(require_creator_hash), db: Session = Depends(get_db)):
    ct = db.query(CreatorToken).filter_by(token_hash=creator_hash).first()
    if not ct or ct.is_banned:
        return {"valid": False}
    
    return {
        "valid": True,
        "generation_count": ct.generation_count,
        "created_at": ct.created_at
    }

class RecoverRequest(BaseModel):
    recovery_key: str

@router.post("/community/recover")
def recover_token(req: RecoverRequest, db: Session = Depends(get_db)):
    r_hash = hash_token(req.recovery_key)
    ct = db.query(CreatorToken).filter_by(recovery_key_hash=r_hash).first()
    if not ct or ct.is_banned:
        raise HTTPException(status_code=400, detail="Invalid recovery key")
        
    new_token = generate_token()
    new_recovery = generate_token()
    
    ct.token_hash = hash_token(new_token)
    ct.recovery_key_hash = hash_token(new_recovery)
    db.commit()
    
    return {
        "token": new_token,
        "recovery_key": new_recovery
    }

@router.post("/community/report")
def report_abuse(req: ReportRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = hash_token(client_ip)
    
    # Rate limit check
    # Max 10 per hour logic could be implemented here
    
    report = AbuseReport(
        item_type=req.item_type,
        item_id=req.item_id,
        reason=req.reason,
        reporter_ip_hash=ip_hash
    )
    db.add(report)
    db.commit()
    
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Saved Views Persistence Endpoints
# ---------------------------------------------------------------------------

from typing import Optional, Dict, Any, List
from app.models.community import SavedView


class ViewSaveRequest(BaseModel):
    title: str
    view_type: str  # network, chart, strategy, map, sankey
    config_json: Dict[str, Any]


@router.post("/views")
@router.post("/community/views")
def save_view(
    req: ViewSaveRequest,
    creator_hash: Optional[str] = Depends(get_creator_hash),
    db: Session = Depends(get_db)
):
    """Save an interactive view layout or filter configuration to PostgreSQL."""
    h = creator_hash or "anonymous_view"
    v = SavedView(
        creator_hash=h,
        title=req.title,
        view_type=req.view_type,
        config_json=req.config_json
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return {
        "id": v.id,
        "title": v.title,
        "view_type": v.view_type,
        "config_json": v.config_json,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    }


@router.get("/views")
@router.get("/community/views")
def list_saved_views(
    view_type: Optional[str] = None,
    creator_hash: Optional[str] = Depends(get_creator_hash),
    db: Session = Depends(get_db)
):
    """List saved interactive views and filter states."""
    q = db.query(SavedView)
    if creator_hash:
        q = q.filter(or_(SavedView.creator_hash == creator_hash, SavedView.creator_hash == "system_executive"))
    if view_type:
        q = q.filter(SavedView.view_type == view_type)

    views = q.order_by(SavedView.created_at.desc()).all()
    return [
        {
            "id": v.id,
            "title": v.title,
            "view_type": v.view_type,
            "config_json": v.config_json,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in views
    ]


@router.get("/views/{view_id}")
@router.get("/community/views/{view_id}")
def get_saved_view(view_id: int, db: Session = Depends(get_db)):
    """Retrieve single saved view configuration."""
    v = db.query(SavedView).filter_by(id=view_id).first()
    if not v:
        raise HTTPException(404, "Saved view not found")
    return {
        "id": v.id,
        "title": v.title,
        "view_type": v.view_type,
        "config_json": v.config_json,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    }


@router.delete("/views/{view_id}")
@router.delete("/community/views/{view_id}")
def delete_saved_view(
    view_id: int,
    creator_hash: Optional[str] = Depends(require_creator_hash),
    db: Session = Depends(get_db)
):
    """Delete a saved view."""
    v = db.query(SavedView).filter_by(id=view_id).first()
    if not v:
        raise HTTPException(404, "Saved view not found")
    if creator_hash and v.creator_hash != creator_hash and v.creator_hash != "system_executive":
        raise HTTPException(403, "Access denied")
    db.delete(v)
    db.commit()
    return {"status": "deleted"}
