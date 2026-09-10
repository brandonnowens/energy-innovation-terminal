"""
Observability and User Activity Telemetry Middleware.

Measures endpoint latency, attaches `X-Response-Time-Ms` header,
logs slow queries/responses, and logs user usage events into `user_activity_logs`.
"""

import time
import hashlib
import logging
import threading
import queue
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("Observability")
SLOW_REQUEST_THRESHOLD_MS = 1500.0

# Asynchronous background worker queue for non-blocking telemetry logging
_ACTIVITY_QUEUE: queue.Queue = queue.Queue(maxsize=10000)
_WORKER_THREAD: threading.Thread | None = None
_WORKER_RUNNING = False


def _detect_device_type(user_agent: str) -> str:
    ua = user_agent.lower()
    if any(bot in ua for bot in ["bot", "spider", "crawl", "curl", "wget", "headless"]):
        return "bot"
    if any(m in ua for m in ["mobi", "iphone", "android", "ipad", "tablet"]):
        return "mobile"
    return "desktop"


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
    elif p.startswith("/api/"):
        return "api_request"
    elif p in ("/", "/index.html") or not p.startswith("/api"):
        return "page_view"
    return "general_request"


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
            
            # Drain up to 50 more items from the queue
            while len(batch) < 50:
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
                    objs = [
                        UserActivityLog(
                            user_id=b.get("user_id"),
                            user_email=b.get("user_email"),
                            ip_hash=b.get("ip_hash", "unknown"),
                            session_id=b.get("session_id"),
                            endpoint=b.get("endpoint", "")[:255],
                            method=b.get("method", "GET")[:10],
                            action_type=b.get("action_type", "api_request")[:50],
                            status_code=b.get("status_code", 200),
                            duration_ms=b.get("duration_ms", 0.0),
                            user_agent=b.get("user_agent", "")[:255],
                            device_type=b.get("device_type", "desktop")[:50],
                            referrer=b.get("referrer", "")[:255],
                            created_at=b.get("created_at", datetime.utcnow())
                        )
                        for b in batch
                    ]
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

        # Skip noise: health probes and favicon/assets
        if not (
            path in ("/health", "/api/health", "/favicon.ico", "/favicon.png", "/favicon.svg")
            or path.startswith("/assets/")
            or path.startswith("/logos/")
            or request.method == "OPTIONS"
        ):
            user_agent = request.headers.get("user-agent") or ""
            ip_hash = self._get_ip_hash(request)
            device_type = _detect_device_type(user_agent)
            action_type = _categorize_action(path, request.method)
            session_id = request.headers.get("X-Session-ID") or request.cookies.get("session_id")
            
            payload = {
                "ip_hash": ip_hash,
                "session_id": session_id,
                "endpoint": path,
                "method": request.method,
                "action_type": action_type,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "user_agent": user_agent[:250],
                "device_type": device_type,
                "referrer": (request.headers.get("referer") or "")[:250],
                "created_at": datetime.utcnow()
            }
            try:
                _ACTIVITY_QUEUE.put_nowait(payload)
            except queue.Full:
                pass
            
        return response
