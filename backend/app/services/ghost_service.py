"""Ghost.org Members and Subscriptions Integration Service."""

import time
import hmac
import hashlib
from typing import Optional, Dict, Any
import httpx
import jwt
from pydantic import BaseModel

from app.config import settings


class GhostMemberProfile(BaseModel):
    """Normalized Ghost member subscription profile."""
    id: str
    email: str
    name: Optional[str] = None
    status: str = "free"  # free, paid, comped
    tier_slug: Optional[str] = None
    tier_name: Optional[str] = None
    subscriptions: list[Dict[str, Any]] = []
    created_at: Optional[str] = None


class GhostService:
    """Service client for Ghost Admin API and webhook subscription synchronization."""

    def __init__(
        self,
        api_url: Optional[str] = None,
        admin_api_key: Optional[str] = None,
        webhook_secret: Optional[str] = None
    ):
        self.api_url = (api_url or getattr(settings, "ghost_api_url", "")).rstrip("/")
        self.admin_api_key = admin_api_key or getattr(settings, "ghost_admin_api_key", "")
        self.webhook_secret = webhook_secret or getattr(settings, "ghost_webhook_secret", "")

    def _generate_admin_jwt(self) -> Optional[str]:
        """Generate short-lived HS256 JWT for Ghost Admin API authentication."""
        if not self.admin_api_key or ":" not in self.admin_api_key:
            return None

        key_id, secret = self.admin_api_key.split(":")
        try:
            secret_bytes = bytes.fromhex(secret)
        except ValueError:
            return None

        now = int(time.time())
        payload = {
            "iat": now,
            "exp": now + 300,  # 5 minutes
            "aud": "/admin/"
        }
        token = jwt.encode(payload, secret_bytes, algorithm="HS256", headers={"kid": key_id})
        return token

    async def get_member_by_email(self, email: str) -> Optional[GhostMemberProfile]:
        """Fetch member subscription and tier details directly from Ghost Admin API."""
        if not self.api_url or not self.admin_api_key:
            return None

        token = self._generate_admin_jwt()
        if not token:
            return None

        endpoint = f"{self.api_url}/ghost/api/admin/members/"
        headers = {
            "Authorization": f"Ghost {token}",
            "Accept-Version": "v5.0"
        }
        params = {"filter": f"email:'{email.strip().lower()}'", "include": "tiers,subscriptions"}

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                res = await client.get(endpoint, headers=headers, params=params)
                if res.status_code != 200:
                    return None

                data = res.json()
                members = data.get("members", [])
                if not members:
                    return None

                m = members[0]
                tiers = m.get("tiers", [])
                tier_slug = tiers[0].get("slug") if tiers else None
                tier_name = tiers[0].get("name") if tiers else None

                return GhostMemberProfile(
                    id=m.get("id"),
                    email=m.get("email"),
                    name=m.get("name"),
                    status=m.get("status", "free"),
                    tier_slug=tier_slug,
                    tier_name=tier_name,
                    subscriptions=m.get("subscriptions", []),
                    created_at=m.get("created_at")
                )
        except Exception:
            return None

    def verify_webhook_signature(self, body_bytes: bytes, signature_header: str) -> bool:
        """Verify HMAC-SHA256 signature from Ghost webhook requests."""
        if not self.webhook_secret:
            return True  # If no secret configured, allow in development

        if not signature_header:
            return False

        try:
            # Ghost webhook signature format: sha256={hash}
            expected_prefix = "sha256="
            clean_sig = signature_header[len(expected_prefix):] if signature_header.startswith(expected_prefix) else signature_header
            computed = hmac.new(
                self.webhook_secret.encode("utf-8"),
                body_bytes,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(computed, clean_sig)
        except Exception:
            return False

    def map_ghost_tier_to_terminal_tier(self, ghost_status: str, tier_slug: Optional[str] = None) -> str:
        """Map Ghost subscription status and tier slug to Terminal tier enum."""
        if ghost_status in ("comped", "paid"):
            slug = (tier_slug or "").lower()
            if any(k in slug for k in ["enterprise", "institution", "corporate", "team"]):
                return "enterprise"
            return "pro"

        # Default free tier
        return "free_public_benefit"


ghost_service = GhostService()
