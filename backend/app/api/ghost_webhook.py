"""Ghost.org Webhook and Member Verification API Router."""

from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, HTTPException, Depends, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.ghost_service import ghost_service
from app.core.security import create_access_token, hash_password, generate_random_token

router = APIRouter(prefix="/auth/ghost", tags=["Ghost Membership Integration"])


class VerifyGhostMemberRequest(BaseModel):
    """Payload to verify member via Ghost Admin API."""
    email: str


class GhostAuthResponse(BaseModel):
    """Response returned upon successful Ghost member authentication."""
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]
    ghost_tier: Optional[str] = None
    ghost_status: str


@router.get("/config")
def get_ghost_config():
    """Return public Ghost publication configuration for frontend membership portal links."""
    return {
        "ghost_api_url": getattr(settings, "ghost_api_url", ""),
        "configured": bool(getattr(settings, "ghost_admin_api_key", "")),
        "portal_signup_url": f"{getattr(settings, 'ghost_api_url', '').rstrip('/')}/#/portal/signup" if getattr(settings, "ghost_api_url", "") else ""
    }


@router.post("/verify-member", response_model=GhostAuthResponse)
async def verify_ghost_member(req: VerifyGhostMemberRequest, db: Session = Depends(get_db)):
    """
    Verify a Ghost subscriber by email, synchronize their tier, and issue a Terminal JWT access token.
    """
    clean_email = req.email.strip().lower()

    # Query Ghost Admin API
    member_profile = await ghost_service.get_member_by_email(clean_email)
    if not member_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active Ghost subscription found for this email address. Please subscribe at our publication first."
        )

    # Map Ghost subscription to Terminal tier
    mapped_tier = ghost_service.map_ghost_tier_to_terminal_tier(
        ghost_status=member_profile.status,
        tier_slug=member_profile.tier_slug
    )

    # Upsert user record in Supabase/PostgreSQL database
    user = db.query(User).filter(User.email == clean_email).first()
    if not user:
        user = User(
            email=clean_email,
            hashed_password=hash_password(generate_random_token(16)),
            full_name=member_profile.name or clean_email.split("@")[0],
            role="user",
            tier=mapped_tier,
            tier_status="active" if member_profile.status in ("paid", "comped", "free") else "past_due",
            ghost_member_id=member_profile.id,
            ghost_subscription_tier=member_profile.tier_name or member_profile.tier_slug,
            ghost_status=member_profile.status,
            is_active=True,
            is_verified=True,
            last_login_at=datetime.utcnow()
        )
        db.add(user)
    else:
        user.ghost_member_id = member_profile.id
        user.ghost_subscription_tier = member_profile.tier_name or member_profile.tier_slug
        user.ghost_status = member_profile.status
        user.tier = mapped_tier
        user.tier_status = "active" if member_profile.status in ("paid", "comped", "free") else "past_due"
        user.last_login_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    # Issue JWT token
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "role": user.role,
            "tier": user.tier
        }
    )

    return GhostAuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user.to_dict(public_benefit_active=getattr(settings, "public_benefit_mode", True)),
        ghost_tier=user.ghost_subscription_tier,
        ghost_status=user.ghost_status
    )


@router.post("/webhook")
async def ghost_webhook_receiver(
    request: Request,
    db: Session = Depends(get_db),
    x_ghost_signature: Optional[str] = Header(None)
):
    """
    Handle real-time webhooks from Ghost.org when members sign up, edit subscriptions, or cancel.
    """
    body_bytes = await request.body()

    # Validate HMAC signature
    if not ghost_service.verify_webhook_signature(body_bytes, x_ghost_signature or ""):
        raise HTTPException(status_code=401, detail="Invalid Ghost webhook signature")

    payload = await request.json()
    member_data = payload.get("member", {}) or payload.get("current", {})
    if not member_data and "members" in payload and payload["members"]:
        member_data = payload["members"][0]

    email = member_data.get("email", "").strip().lower()
    if not email:
        return {"status": "ignored", "reason": "no_email_in_payload"}

    ghost_status_val = member_data.get("status", "free")
    tiers = member_data.get("tiers", [])
    tier_slug = tiers[0].get("slug") if tiers else None
    tier_name = tiers[0].get("name") if tiers else None

    mapped_tier = ghost_service.map_ghost_tier_to_terminal_tier(
        ghost_status=ghost_status_val,
        tier_slug=tier_slug
    )

    user = db.query(User).filter(User.email == email).first()
    if user:
        user.ghost_member_id = member_data.get("id", user.ghost_member_id)
        user.ghost_subscription_tier = tier_name or tier_slug
        user.ghost_status = ghost_status_val
        user.tier = mapped_tier
        user.tier_status = "active" if ghost_status_val in ("paid", "comped", "free") else "past_due"
        user.updated_at = datetime.utcnow()
        db.commit()
        return {"status": "updated", "email": email, "tier": mapped_tier}
    else:
        new_user = User(
            email=email,
            hashed_password=hash_password(generate_random_token(16)),
            full_name=member_data.get("name") or email.split("@")[0],
            role="user",
            tier=mapped_tier,
            tier_status="active" if ghost_status_val in ("paid", "comped", "free") else "past_due",
            ghost_member_id=member_data.get("id"),
            ghost_subscription_tier=tier_name or tier_slug,
            ghost_status=ghost_status_val,
            is_active=True,
            is_verified=True,
            last_login_at=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        return {"status": "created", "email": email, "tier": mapped_tier}
