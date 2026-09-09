"""Security middleware: rate limiting, headers, input sanitization."""
import hashlib
import re
import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Production-grade in-memory rate limiter per client IP with reverse-proxy support and anti-scraping defenses."""

    SCRAPER_USER_AGENTS = (
        "bytespider", "ccbot", "diffbot", "dataforseobot", "scrapy",
        "ahrefsbot", "semrushbot", "mj12bot", "dotbot", "petalbot", "zoominfobot"
    )

    def __init__(self, app, default_rpm: int = 120, contact_rpm: int = 10, export_rpm: int = 20, ai_rpm: int = 30):
        super().__init__(app)
        self.default_rpm = default_rpm
        self.contact_rpm = contact_rpm
        self.export_rpm = export_rpm
        self.ai_rpm = ai_rpm
        self.requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        """Extract real client IP considering Cloudflare, AWS ALB, and reverse proxies."""
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip:
            return cf_ip.strip()
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip.strip()
        return request.client.host if request.client else "unknown"

    def _get_ip_hash(self, request: Request) -> str:
        ip = self._get_client_ip(request)
        return hashlib.sha256(ip.encode()).hexdigest()[:16]

    def _check_rate(self, key: str, limit: int) -> bool:
        now = time.time()
        window = self.requests[key]
        # Prune old entries (older than 60s)
        window[:] = [t for t in window if now - t < 60]
        if len(window) >= limit:
            return False
        window.append(now)
        return True

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # 1. Block aggressive bulk scrapers targeting raw API endpoints
        user_agent = (request.headers.get("user-agent") or "").lower()
        if any(bot in user_agent for bot in self.SCRAPER_USER_AGENTS) and path.startswith("/api/"):
            return Response(
                content='{"detail": "Automated scraping of API endpoints is prohibited."}',
                status_code=403,
                media_type="application/json",
            )

        # Bypass rate limiting for health probes, CORS preflights, static assets, and SEO meta files
        if (
            request.method == "OPTIONS"
            or path in ("/health", "/api/health", "/robots.txt", "/sitemap.xml", "/llms.txt", "/ai.txt", "/favicon.ico", "/favicon.png", "/favicon.svg")
            or path.startswith("/assets/")
            or path.startswith("/logos/")
            or path.startswith("/sitemap-")
        ):
            return await call_next(request)

        ip_hash = self._get_ip_hash(request)

        # Determine rate limit tier
        if "/contacts" in path:
            limit = self.contact_rpm
            key = f"contact:{ip_hash}"
        elif "/export" in path or path.endswith("/pdf") or path.endswith("/csv"):
            limit = self.export_rpm
            key = f"export:{ip_hash}"
        elif "/analyze" in path or "/chat" in path or "/winning-angle" in path or "/foa-shred" in path:
            limit = self.ai_rpm
            key = f"ai:{ip_hash}"
        else:
            limit = self.default_rpm
            key = f"default:{ip_hash}"

        if not self._check_rate(key, limit):
            return Response(
                content='{"detail": "Rate limit exceeded. Please try again later."}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"},
            )

        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add anti-reverse-engineering and defensive security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=*, microphone=*, display-capture=*, autoplay=*, clipboard-write=*"
        response.headers["Server"] = "Energy-Innovation-Terminal"
        response.headers["X-Robots-Tag"] = "noindex, nofollow" if request.url.path.startswith("/api/") else "index, follow"
        from app.config import settings
        if getattr(settings, "environment", "") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class HttpCacheControlMiddleware(BaseHTTPMiddleware):
    """Add Cache-Control headers to cacheable read-only GET endpoints."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        if request.method == "GET" and response.status_code == 200:
            path = request.url.path
            if "Cache-Control" not in response.headers:
                if any(path.startswith(p) for p in [
                    "/api/agencies",
                    "/api/sankey/presets",
                    "/api/technologies",
                    "/api/tech_reference",
                    "/api/policies",
                    "/api/linkages",
                    "/api/charts",
                    "/api/results/benchmarks",
                    "/api/system"
                ]):
                    response.headers["Cache-Control"] = "public, max-age=120, stale-while-revalidate=600"
                elif any(path.startswith(p) for p in [
                    "/api/awards/stats",
                    "/api/trends",
                    "/api/sankey/insights",
                    "/api/contacts/stats",
                    "/api/attributions/overview"
                ]):
                    response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=300"
        return response


# ============================================================
# Input sanitization utilities
# ============================================================

# Patterns that suggest prompt injection
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+a",
    r"system\s*:\s*",
    r"<\s*script",
    r"javascript\s*:",
    r"on(load|error|click|mouseover)\s*=",
    r"data\s*:\s*text/html",
]
_injection_re = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)


def sanitize_prompt(text: str, max_length: int = 10000) -> str:
    """Sanitize user prompts for LLM input."""
    if not text:
        return ""
    # Truncate
    text = text[:max_length]
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Check for injection patterns (log but don't block - just strip)
    text = _injection_re.sub("[filtered]", text)
    return text.strip()


def sanitize_filename(name: str) -> str:
    """Make a string safe for use as a filename."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r"\s+", "_", name)
    name = name[:100]  # Limit length
    return name or "export"


def generate_unguessable_id() -> str:
    """Generate an unguessable ID for public-facing resources."""
    import secrets
    return secrets.token_urlsafe(16)
