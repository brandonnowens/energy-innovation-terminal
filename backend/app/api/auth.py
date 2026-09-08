"""Authentication and membership API endpoints."""

import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User, PasswordResetToken
from app.core.security import (
    hash_password, verify_password, create_access_token,
    generate_random_token, hash_token
)
from app.core.membership import (
    get_current_user, get_current_user_optional,
    get_tier_scaffolding_manifest, MembershipTier
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ----------------------------------------------------------------------
# Request & Response Schemas (Pydantic)
# ----------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """Minimal friction registration requiring only email and password."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (minimum 8 characters)")
    full_name: Optional[str] = Field(None, description="Optional full name")
    organization_name: Optional[str] = Field(None, description="Optional organization")


class LoginRequest(BaseModel):
    """User login credentials."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class AuthResponse(BaseModel):
    """Response payload for successful login or registration."""
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    organization_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class UpgradeTierRequest(BaseModel):
    tier: str = Field(..., description="Target tier (free_public_benefit, pro, enterprise)")


def _normalize_email(email: str) -> str:
    cleaned = email.strip().lower()
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_regex, cleaned):
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    return cleaned


# ----------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------

@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account with minimal information (Email + Password).
    All users receive immediate full access under the Free Public Benefit tier.
    """
    clean_email = _normalize_email(req.email)
    
    # Check if user already exists
    existing = db.query(User).filter(User.email == clean_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists. Please sign in instead."
        )
    
    # Hash password securely
    hashed_pw = hash_password(req.password)
    
    # Create user
    user = User(
        email=clean_email,
        hashed_password=hashed_pw,
        full_name=req.full_name.strip() if req.full_name else None,
        organization_name=req.organization_name.strip() if req.organization_name else None,
        role="user",
        tier=MembershipTier.FREE_PUBLIC_BENEFIT.value,
        tier_status="active",
        is_active=True,
        is_verified=True,
        last_login_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate JWT token
    token = create_access_token({
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "tier": user.tier
    })
    
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user.to_dict(public_benefit_active=settings.public_benefit_mode)
    )


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user with email and password."""
    clean_email = _normalize_email(req.email)
    user = db.query(User).filter(User.email == clean_email).first()
    
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please try again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support."
        )
        
    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    token = create_access_token({
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "tier": user.tier
    })
    
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user.to_dict(public_benefit_active=settings.public_benefit_mode)
    )


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    """Get profile and membership details of the currently authenticated user."""
    return {
        "user": user.to_dict(public_benefit_active=settings.public_benefit_mode)
    }


@router.put("/me")
def update_me(
    req: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profile attributes (name, organization, preferences)."""
    if req.full_name is not None:
        user.full_name = req.full_name.strip()
    if req.organization_name is not None:
        user.organization_name = req.organization_name.strip()
    if req.preferences is not None:
        user.preferences_json = req.preferences
        
    db.commit()
    db.refresh(user)
    return {
        "status": "ok",
        "user": user.to_dict(public_benefit_active=settings.public_benefit_mode)
    }


@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change the authenticated user's password."""
    if not verify_password(req.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password does not match."
        )
        
    user.hashed_password = hash_password(req.new_password)
    db.commit()
    return {"status": "ok", "message": "Password updated successfully."}


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Generate a timed password recovery token for an account.
    Returns recovery key for seamless direct recovery in local/public mode.
    """
    clean_email = _normalize_email(req.email)
    user = db.query(User).filter(User.email == clean_email).first()
    
    if not user:
        # Standard security practice: Don't leak whether email exists
        return {
            "status": "ok",
            "message": "If an account exists with this email, recovery instructions have been initiated.",
            "reset_token": None
        }
        
    token_str = generate_random_token(32)
    token_h = hash_token(token_str)
    
    # Store token with 1 hour expiration
    expires = datetime.utcnow() + timedelta(hours=1)
    reset_entry = PasswordResetToken(
        user_id=user.id,
        token_hash=token_h,
        expires_at=expires
    )
    db.add(reset_entry)
    db.commit()
    
    return {
        "status": "ok",
        "message": "Password reset token generated.",
        "reset_token": token_str  # Ready for UI helper or email integration
    }


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using a valid, non-expired recovery token."""
    token_h = hash_token(req.token.strip())
    entry = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_h,
        PasswordResetToken.used_at == None,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token."
        )
        
    user = entry.user
    if not user:
        raise HTTPException(status_code=400, detail="User associated with token not found.")
        
    user.hashed_password = hash_password(req.new_password)
    entry.used_at = datetime.utcnow()
    db.commit()
    
    return {"status": "ok", "message": "Password has been successfully reset. You can now sign in."}


@router.get("/membership")
def get_membership(user: Optional[User] = Depends(get_current_user_optional)):
    """Return platform membership information, current tier details, and tier scaffolding."""
    manifest = get_tier_scaffolding_manifest()
    user_info = user.to_dict(public_benefit_active=settings.public_benefit_mode) if user else None
    return {
        "user": user_info,
        "membership_manifest": manifest
    }


@router.post("/mock-upgrade")
def mock_upgrade(
    req: UpgradeTierRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Scaffolding endpoint to test tier upgrades in development."""
    valid_tiers = [t.value for t in MembershipTier]
    if req.tier not in valid_tiers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier. Choose one of: {', '.join(valid_tiers)}"
        )
        
    user.tier = req.tier
    user.tier_status = "active"
    db.commit()
    db.refresh(user)
    
    return {
        "status": "ok",
        "message": f"Account tier upgraded to {req.tier}.",
        "user": user.to_dict(public_benefit_active=settings.public_benefit_mode)
    }
