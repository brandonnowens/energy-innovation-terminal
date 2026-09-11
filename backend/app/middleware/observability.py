"""
Observability and User Activity Telemetry Middleware.

Measures endpoint latency, attaches `X-Response-Time-Ms` header,
logs slow queries/responses, and asynchronously records rich user/anonymous telemetry
into `user_activity_logs`.
"""

import time
import hashlib
import logging
import threading
import queue
import re
from datetime import datetime
from typing import Dict, Any, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("Observability")
SLOW_REQUEST_THRESHOLD_MS = 1500.0

# Asynchronous background worker queue for non-blocking telemetry logging
_ACTIVITY_QUEUE: queue.Queue = queue.Queue(maxsize=20000)
_WORKER_THREAD: threading.Thread | None = None
_WORKER_RUNNING = False


def parse_user_agent_details(user_agent: str) -> Tuple[str, str, str]:
    """Parse User-Agent into (browser, os, device_type)."""
    if not user_agent:
        return ("Unknown", "Unknown", "desktop")

    ua = user_agent.lower()
    
    # 1. Device Type
    if any(bot in ua for bot in ["bot", "spider", "crawl", "curl", "wget", "headless", "postman", "python", "http"]):
        device_type = "bot"
    elif any(tab in ua for tab in ["ipad", "tablet", "playbook", "silk"]):
        device_type = "tablet"
    elif any(mob in ua for mob in ["mobi", "iphone", "android", "touch", "windows phone"]):
        device_type = "mobile"
    else:
        device_type = "desktop"

    # 2. Operating System
    if "windows nt 10.0" in ua:
        os_name = "Windows 10/11"
    elif "windows nt 6.3" in ua:
        os_name = "Windows 8.1"
    elif "windows nt 6.1" in ua:
        os_name = "Windows 7"
    elif "mac os x" in ua:
        os_name = "macOS"
    elif "iphone" in ua or "ipad" in ua or "ipod" in ua:
        os_name = "iOS"
    elif "android" in ua:
        os_name = "Android"
    elif "linux" in ua:
        os_name = "Linux"
    elif "cros" in ua:
        os_name = "Chrome OS"
    else:
        os_name = "Other OS"

    # 3. Browser
    if "edg/" in ua or "edge/" in ua:
        browser = "Microsoft Edge"
    elif "chrome/" in ua and "safari/" in ua and "edg/" not in ua and "opr/" not in ua:
        browser = "Google Chrome"
    elif "safari/" in ua and "chrome/" not in ua and "android" not in ua:
        browser = "Apple Safari"
    elif "firefox/" in ua:
        browser = "Mozilla Firefox"
    elif "opr/" in ua or "opera/" in ua:
        browser = "Opera"
    elif "trident/" in ua or "msie" in ua:
        browser = "Internet Explorer"
    else:
        browser = "Other Browser"

    return (browser, os_name, device_type)


def _categorize_action(path: str, method: str) -> str:
    p = path.lower()
    if "/analyze" in p:
        return "grant_match_analysis"
    elif "/chat" in p:
        return "copilot_chat"
    elif "/foa-shred" in p or "/foa_shred" in p:
        return "foa_shred"
    elif "/proposals" in p:
        return "proposal_generator"
    elif "/reports" in p and method == "POST":
        return "report_create"
    elif "/strategies" in p and method == "POST":
        return "strategy_create"
    elif "/search" in p:
        return "search"
    elif "/pdf" in p or "/export" in p:
        return "export_download"
    elif "/auth/login" in p:
        return "user_login"
    elif "/auth/register" in p:
        return "user_register"
    elif "/telemetry" in p:
        return "client_telemetry"
    elif p.startswith("/api/"):
        return "api_request"
    elif p in ("/", "/index.html") or not p.startswith("/api"):
        return "page_view"
    return "general_request"


def enqueue_telemetry_event(payload: Dict[str, Any]):
    """Public helper to enqueue a telemetry event safely into the background batch worker."""
    _ensure_worker_started()
    try:
        _ACTIVITY_QUEUE.put_nowait(payload)
    except queue.Full:
        pass


def _telemetry_worker():
    """Background worker that flushes queued activity logs to PostgreSQL in batches."""
    from app.database import SessionLocal
    from app.models.user_activity import UserActivityLog

    while _WORKER_RUNNING:
        batch = []
        try:
            # Wait for at least one item
            item = _ACTIVITY_QUEUE.get(timeout=2.0)
            batch.append(item)
            _ACTIVITY_QUEUE.task_done()
            
            # Drain up to 100 more items from the queue
            while len(batch) < 100:
                try:
                    next_item = _ACTIVITY_QUEUE.get_nowait()
                    batch.append(next_item)
                    _ACTIVITY_QUEUE.task_done()
                except queue.Empty:
                    break
        except queue.Empty:
            continue
        except Exception as e:
            logger.debug(f"Telemetry worker queue get error: {e}")
            continue

        if batch:
            try:
                with SessionLocal() as db:
                    objs = []
                    for b in batch:
                        lat = b.get("latitude")
                        lon = b.get("longitude")
                        try:
                            lat = float(lat) if lat is not None else None
                        except Exception:
                            lat = None
                        try:
                            lon = float(lon) if lon is not None else None
                        except Exception:
                            lon = None

                        objs.append(UserActivityLog(
                            user_id=b.get("user_id"),
                            user_email=b.get("user_email"),
                            anon_id=b.get("anon_id"),
                            session_id=b.get("session_id"),
                            ip_hash=b.get("ip_hash", "unknown"),
                            
                            # Geolocation
                            country=b.get("country"),
                            region=b.get("region"),
                            city=b.get("city"),
                            postal_code=b.get("postal_code"),
                            latitude=lat,
                            longitude=lon,
                            cf_ray=b.get("cf_ray"),
                            
                            # Request Details
                            endpoint=b.get("endpoint", "")[:255],
                            method=b.get("method", "GET")[:10],
                            action_type=b.get("action_type", "api_request")[:50],
                            status_code=b.get("status_code", 200),
                            duration_ms=b.get("duration_ms", 0.0),
                            
                            # Client Demographics
                            user_agent=b.get("user_agent", "")[:255],
                            device_type=b.get("device_type", "desktop")[:50],
                            browser=b.get("browser")[:50] if b.get("browser") else None,
                            os=b.get("os")[:50] if b.get("os") else None,
                            screen_resolution=b.get("screen_resolution")[:50] if b.get("screen_resolution") else None,
                            viewport_size=b.get("viewport_size")[:50] if b.get("viewport_size") else None,
                            client_timezone=b.get("client_timezone")[:100] if b.get("client_timezone") else None,
                            language=b.get("language")[:50] if b.get("language") else None,
                            
                            # Attribution
                            referrer=b.get("referrer", "")[:255],
                            initial_referrer=b.get("initial_referrer", "")[:255] if b.get("initial_referrer") else None,
                            utm_source=b.get("utm_source")[:100] if b.get("utm_source") else None,
                            utm_medium=b.get("utm_medium")[:100] if b.get("utm_medium") else None,
                            utm_campaign=b.get("utm_campaign")[:100] if b.get("utm_campaign") else None,
                            utm_term=b.get("utm_term")[:100] if b.get("utm_term") else None,
                            utm_content=b.get("utm_content")[:100] if b.get("utm_content") else None,
                            
                            # Event Details
                            page_title=b.get("page_title")[:255] if b.get("page_title") else None,
                            event_data=b.get("event_data"),
                            created_at=b.get("created_at", datetime.utcnow())
                        ))
                    db.add_all(objs)
                    db.commit()
            except Exception as e:
                logger.debug(f"Telemetry batch write failed: {e}")


def _ensure_worker_started():
    global _WORKER_THREAD, _WORKER_RUNNING
    if not _WORKER_RUNNING or _WORKER_THREAD is None or not _WORKER_THREAD.is_alive():
        _WORKER_RUNNING = True
        _WORKER_THREAD = threading.Thread(target=_telemetry_worker, daemon=True, name="TelemetryWorker")
        _WORKER_THREAD.start()


class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        _ensure_worker_started()

    def _get_client_ip(self, request: Request) -> str:
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

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        
        response: Response = await call_next(request)
        
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"
        
        path = request.url.path

        # Log slow requests
        if duration_ms > SLOW_REQUEST_THRESHOLD_MS:
            logger.warning(
                f"Slow Request: {request.method} {path} "
                f"took {duration_ms:.2f}ms (status: {response.status_code})"
            )

        # Skip noise: health probes, static assets, and telemetry beacon itself (telemetry endpoint logs itself)
        if not (
            path in ("/health", "/api/health", "/favicon.ico", "/favicon.png", "/favicon.svg")
            or path.startswith("/assets/")
            or path.startswith("/logos/")
            or path.startswith("/api/telemetry/event")
            or request.method == "OPTIONS"
        ):
            user_agent = request.headers.get("user-agent") or ""
            ip_hash = self._get_ip_hash(request)
            browser, os_name, device_type = parse_user_agent_details(user_agent)
            action_type = _categorize_action(path, request.method)
            
            # Extract anonymous and session identifiers
            anon_id = request.headers.get("X-Anonymous-ID") or request.query_params.get("anon_id")
            session_id = request.headers.get("X-Session-ID") or request.cookies.get("session_id")
            
            # Extract Cloudflare edge geolocation headers
            country = request.headers.get("CF-IPCountry")
            region = request.headers.get("CF-Region") or request.headers.get("CF-Region-Code")
            city = request.headers.get("CF-IPCity")
            postal_code = request.headers.get("CF-Postal-Code")
            latitude = request.headers.get("CF-IPLatitude")
            longitude = request.headers.get("CF-IPLongitude")
            cf_ray = request.headers.get("CF-RAY")
            
            # Extract client dimensions and locale
            screen_resolution = request.headers.get("X-Screen-Resolution")
            viewport_size = request.headers.get("X-Viewport-Size")
            client_timezone = request.headers.get("X-Client-Timezone")
            language = (request.headers.get("accept-language") or "").split(",")[0].strip()
            
            # Extract attribution
            referrer = request.headers.get("referer") or ""
            initial_referrer = request.headers.get("X-Initial-Referrer")
            utm_source = request.query_params.get("utm_source") or request.headers.get("X-UTM-Source")
            utm_medium = request.query_params.get("utm_medium") or request.headers.get("X-UTM-Medium")
            utm_campaign = request.query_params.get("utm_campaign") or request.headers.get("X-UTM-Campaign")
            utm_term = request.query_params.get("utm_term") or request.headers.get("X-UTM-Term")
            utm_content = request.query_params.get("utm_content") or request.headers.get("X-UTM-Content")

            payload = {
                "ip_hash": ip_hash,
                "anon_id": anon_id,
                "session_id": session_id,
                "country": country,
                "region": region,
                "city": city,
                "postal_code": postal_code,
                "latitude": latitude,
                "longitude": longitude,
                "cf_ray": cf_ray,
                "endpoint": path,
                "method": request.method,
                "action_type": action_type,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "user_agent": user_agent[:250],
                "device_type": device_type,
                "browser": browser,
                "os": os_name,
                "screen_resolution": screen_resolution,
                "viewport_size": viewport_size,
                "client_timezone": client_timezone,
                "language": language,
                "referrer": referrer[:250],
                "initial_referrer": initial_referrer[:250] if initial_referrer else None,
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
                "utm_term": utm_term,
                "utm_content": utm_content,
                "created_at": datetime.utcnow()
            }
            enqueue_telemetry_event(payload)
            
        return response

