"""Membership tiers, feature gating scaffolding, and authentication dependencies."""

from enum import Enum
from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.core.security import decode_access_token, hash_token

# Bearer security scheme (auto_error=False to allow custom error handling and optional auth)
http_bearer = HTTPBearer(auto_error=False)


class MembershipTier(str, Enum):
    """Platform membership tiers."""
    FREE_PUBLIC_BENEFIT = "free_public_benefit"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class FeaturePermission(str, Enum):
    """Granular feature permissions for future-ready tier scaffolding."""
    OPPORTUNITY_MATCHING = "opportunity_matching"
    AWARD_EXPLORER = "award_explorer"
    SANKEY_FLOWS = "sankey_flows"
    NETWORK_GRAPH = "network_graph"
    MARKET_TRENDS = "market_trends"
    EXECUTIVE_DOSSIERS = "executive_dossiers"
    PDF_EXPORT = "pdf_export"
    CSV_EXPORT = "csv_export"
    CUSTOM_STRATEGIES = "custom_strategies"
    API_ACCESS = "api_access"
    PIPELINE_TRIGGER = "pipeline_trigger"


# Future permission mappings per tier
TIER_PERMISSIONS: Dict[str, List[str]] = {
    MembershipTier.FREE_PUBLIC_BENEFIT.value: [
        FeaturePermission.OPPORTUNITY_MATCHING.value,
        FeaturePermission.AWARD_EXPLORER.value,
        FeaturePermission.SANKEY_FLOWS.value,
        FeaturePermission.NETWORK_GRAPH.value,
        FeaturePermission.MARKET_TRENDS.value,
        FeaturePermission.EXECUTIVE_DOSSIERS.value,
        FeaturePermission.PDF_EXPORT.value,
        FeaturePermission.CSV_EXPORT.value,
        FeaturePermission.CUSTOM_STRATEGIES.value,
        FeaturePermission.API_ACCESS.value,
        FeaturePermission.PIPELINE_TRIGGER.value,
    ],
    MembershipTier.PRO.value: [
        FeaturePermission.OPPORTUNITY_MATCHING.value,
        FeaturePermission.AWARD_EXPLORER.value,
        FeaturePermission.SANKEY_FLOWS.value,
        FeaturePermission.NETWORK_GRAPH.value,
        FeaturePermission.MARKET_TRENDS.value,
        FeaturePermission.EXECUTIVE_DOSSIERS.value,
        FeaturePermission.PDF_EXPORT.value,
        FeaturePermission.CSV_EXPORT.value,
        FeaturePermission.CUSTOM_STRATEGIES.value,
        FeaturePermission.API_ACCESS.value,
        FeaturePermission.PIPELINE_TRIGGER.value,
    ],
    MembershipTier.ENTERPRISE.value: [
        FeaturePermission.OPPORTUNITY_MATCHING.value,
        FeaturePermission.AWARD_EXPLORER.value,
        FeaturePermission.SANKEY_FLOWS.value,
        FeaturePermission.NETWORK_GRAPH.value,
        FeaturePermission.MARKET_TRENDS.value,
        FeaturePermission.EXECUTIVE_DOSSIERS.value,
        FeaturePermission.PDF_EXPORT.value,
        FeaturePermission.CSV_EXPORT.value,
        FeaturePermission.CUSTOM_STRATEGIES.value,
        FeaturePermission.API_ACCESS.value,
        FeaturePermission.PIPELINE_TRIGGER.value,
    ],
}


def get_current_user_optional(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: Session = Depends(get_db),
    x_creator_token: Optional[str] = Header(None)
) -> Optional[User]:
    """Extract and validate the current user from Bearer token, if present."""
    if not auth or not auth.credentials:
        return None
    
    payload = decode_access_token(auth.credentials)
    if not payload or "sub" not in payload:
        return None
    
    user_id = payload.get("user_id")
    email = payload.get("sub")
    
    query = db.query(User)
    if user_id:
        user = query.filter(User.id == user_id).first()
    elif email:
        user = query.filter(User.email == email.lower()).first()
    else:
        return None
        
    if not user or not user.is_active:
        return None
        
    return user


def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """Dependency that requires a valid authenticated user."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials are required or invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_admin_user_or_default(
    user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
) -> User:
    """Returns authenticated admin user, or the primary system administrator user for open preview mode."""
    if user:
        return user
    admin_email_addr = (settings.admin_primary_email or "bowens@aixenergy.io").strip().lower()
    admin_user = db.query(User).filter(User.email == admin_email_addr).first()
    if not admin_user:
        admin_user = db.query(User).filter(User.role == "admin").first()
    if not admin_user:
        admin_user = User(
            id=1,
            email=admin_email_addr,
            full_name=settings.admin_primary_name or "Brandon Owens",
            organization_name="AIxEnergy / Energy Innovation Terminal",
            role="admin",
            tier="enterprise",
            tier_status="active",
            is_active=True,
            is_verified=True
        )
    return admin_user


def require_role(allowed_roles: List[str]):
    """Enforce specific user roles (e.g. admin, analyst)."""
    def role_checker(user: User = Depends(get_current_user)) -> User:
        is_primary_admin = (
            user.email and settings.admin_primary_email and
            user.email.strip().lower() == settings.admin_primary_email.strip().lower()
        )
        if "admin" in allowed_roles and is_primary_admin:
            return user
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action requires one of the following roles: {', '.join(allowed_roles)}"
            )
        return user
    return role_checker


def require_permission(permission: FeaturePermission):
    """Enforce feature-level access with Public Benefit mode bypass."""
    def permission_checker(user: User = Depends(get_current_user)) -> User:
        # Public Benefit mode: All active users get 100% full access
        if settings.public_benefit_mode:
            return user
        
        user_tier = user.tier or MembershipTier.FREE_PUBLIC_BENEFIT.value
        allowed_perms = TIER_PERMISSIONS.get(user_tier, [])
        if permission.value not in allowed_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Your current tier ({user_tier}) does not include permission: {permission.value}. Upgrade to Pro for access."
            )
        return user
    return permission_checker


def get_tier_scaffolding_manifest() -> Dict[str, Any]:
    """Metadata describing the sovereign enterprise licensing structure and institutional tiers."""
    return {
        "public_benefit_mode": settings.public_benefit_mode,
        "active_message": "Energy Innovation Terminal by AIxEnergy — Full Enterprise Seat Active.",
        "tiers": [
            {
                "id": MembershipTier.FREE_PUBLIC_BENEFIT.value,
                "name": "Community & Academic Pilot",
                "tagline": "Standard multi-agency database search for university labs and academic researchers",
                "price": "$0 / month (Pilot)",
                "is_current_default": True,
                "badge": "Research Pilot",
                "features": [
                    "Multi-Agency Solicitations Index (5,757+ Active & Historical Grants)",
                    "Historical Awards & Recipient Ledger (56,413 Awards · $104.16B Tracked)",
                    "Basic Technology & Fuels Reference Profiles",
                    "Public Domain Citation & Standard Data Views",
                    "Community Support & Online Documentation"
                ]
            },
            {
                "id": MembershipTier.PRO.value,
                "name": "Energy Innovation Terminal Seat",
                "tagline": "Full institutional license: AI FOA Shredder, 56,400+ Teaming Network, Decision-Maker Say-Yes Matrix & Vector PDFs",
                "price": "$1,500 / seat / month (Flat Rate)",
                "is_current_default": False,
                "badge": "Institutional ($1,500/mo)",
                "features": [
                    "Instant AI FOA Shredder & 4-Part Proposal Blueprint Engine",
                    "56,413 Awardee & Multi-Agency Consortia Teaming Network",
                    "Decision-Maker Say-Yes Matrix & Program Manager Intelligence",
                    "5-Stage Non-Dilutive Capital Stack & Precedent Continuum Solver",
                    "Predictive Solicitation Release Forecasting Radar",
                    "DOE National Lab Testbed & User Facility Directory",
                    "Policy, Codes, Standards & PUC Regulatory Dockets",
                    "University Licensable IP & Spinout Portal",
                    "IRA Section 48C / 45X Direct Pay & Tax Credit Calculator",
                    "Publication-Grade 1-Click Vector PDF Report Exports"
                ]
            },
            {
                "id": MembershipTier.ENTERPRISE.value,
                "name": "Consultancy & Practice Group License",
                "tagline": "Multi-seat practice group license for clean energy consultancies, VCs, and advisory firms",
                "price": "$1,500 / seat / month (Team Packages Available)",
                "is_current_default": False,
                "badge": "Practice Group",
                "features": [
                    "Everything in Energy Innovation Terminal Seat",
                    "Multi-Seat Centralized Account & Billing Management",
                    "Dedicated Onboarding & Winning Strategy Review",
                    "High-Throughput REST API Access & Custom Ingestion Feeds",
                    "Custom Agency Watchlist Feeds & Webhook Alerts",
                    "Client-Ready White-Label Vector PDF Export Rights",
                    "Priority Technical Support & Dedicated SLA"
                ]
            }
        ]
    }
