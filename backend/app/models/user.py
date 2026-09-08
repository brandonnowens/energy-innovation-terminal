"""User authentication and membership models."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """User account model supporting minimal friction login and tiered membership scaffolding."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    organization_name = Column(String(255), nullable=True)
    
    # Permissions & Roles
    role = Column(String(50), default="user", nullable=False)  # "user", "analyst", "admin"
    
    # Membership Tier Scaffolding
    tier = Column(String(50), default="free_public_benefit", nullable=False)  # "free_public_benefit", "pro", "enterprise"
    tier_status = Column(String(50), default="active", nullable=False)  # "active", "trialing", "past_due", "canceled"
    tier_expires_at = Column(DateTime, nullable=True)
    
    # Payment Provider & Ghost.org Scaffolding
    stripe_customer_id = Column(String(100), nullable=True, index=True)
    stripe_subscription_id = Column(String(100), nullable=True, index=True)
    ghost_member_id = Column(String(100), nullable=True, index=True)
    ghost_subscription_tier = Column(String(100), nullable=True)
    ghost_status = Column(String(50), default="free", nullable=True)
    
    # Account status & metadata
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    preferences_json = Column(JSON, default=dict, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self, public_benefit_active: bool = True):
        """Serialize user for client consumption."""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name or "",
            "organization_name": self.organization_name or "",
            "role": self.role,
            "tier": self.tier,
            "tier_status": self.tier_status,
            "tier_expires_at": self.tier_expires_at.isoformat() if self.tier_expires_at else None,
            "ghost_member_id": self.ghost_member_id,
            "ghost_subscription_tier": self.ghost_subscription_tier,
            "ghost_status": self.ghost_status or "free",
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "public_benefit_access": public_benefit_active or self.tier in ["free_public_benefit", "pro", "enterprise"],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }


class PasswordResetToken(Base):
    """Secure, timed, single-use token for password recovery."""
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="reset_tokens")
