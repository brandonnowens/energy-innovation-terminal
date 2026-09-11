"""
Telemetry and Anonymous Visitor Event Ingestion Router.

Provides high-throughput, non-blocking telemetry event recording and
real-time usage statistics aggregation across anonymous and authenticated users.
"""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Request, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.middleware.observability import (
    enqueue_telemetry_event,
    parse_user_agent_details
)

router = APIRouter(prefix="/telemetry", tags=["Telemetry & Anonymous Analytics"])


class TelemetryEventPayload(BaseModel):
    anon_id: Optional[str] = None
    session_id: Optional[str] = None
    action_type: str = "page_view"
    endpoint: Optional[str] = None
    page_title: Optional[str] = None
    referrer: Optional[str] = None
    initial_referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None
    screen_resolution: Optional[str] = None
    viewport_size: Optional[str] = None
    client_timezone: Optional[str] = None
    language: Optional[str] = None
    duration_ms: Optional[float] = 0.0
    event_data: Optional[Any] = None


def _get_client_ip_hash(request: Request) -> str:
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        raw_ip = cf_ip.strip()
    else:
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            raw_ip = x_forwarded_for.split(",")[0].strip()
        else:
            x_real_ip = request.headers.get("X-Real-IP")
            if x_real_ip:
                raw_ip = x_real_ip.strip()
            else:
                raw_ip = request.client.host if request.client else "unknown"
    return hashlib.sha256(raw_ip.encode()).hexdigest()[:16]


@router.post("/event")
async def record_telemetry_event(payload: TelemetryEventPayload, request: Request):
    """
    Non-blocking endpoint to ingest client-side telemetry events.
    Captures full anonymous user behavior, pageviews, and interaction metadata.
    """
    user_agent = request.headers.get("user-agent") or ""
    browser, os_name, device_type = parse_user_agent_details(user_agent)
    ip_hash = _get_client_ip_hash(request)

    # Cloudflare Edge Geolocation
    country = request.headers.get("CF-IPCountry")
    region = request.headers.get("CF-Region") or request.headers.get("CF-Region-Code")
    city = request.headers.get("CF-IPCity")
    postal_code = request.headers.get("CF-Postal-Code")
    latitude = request.headers.get("CF-IPLatitude")
    longitude = request.headers.get("CF-IPLongitude")
    cf_ray = request.headers.get("CF-RAY")

    # Serialize event_data
    event_data_str = None
    if payload.event_data is not None:
        if isinstance(payload.event_data, str):
            event_data_str = payload.event_data
        else:
            try:
                event_data_str = json.dumps(payload.event_data)
            except Exception:
                event_data_str = str(payload.event_data)

    item = {
        "ip_hash": ip_hash,
        "anon_id": payload.anon_id or request.headers.get("X-Anonymous-ID"),
        "session_id": payload.session_id or request.headers.get("X-Session-ID"),
        "country": country,
        "region": region,
        "city": city,
        "postal_code": postal_code,
        "latitude": latitude,
        "longitude": longitude,
        "cf_ray": cf_ray,
        "endpoint": (payload.endpoint or request.url.path)[:255],
        "method": "CLIENT_EVENT",
        "action_type": payload.action_type[:50],
        "status_code": 200,
        "duration_ms": float(payload.duration_ms or 0.0),
        "user_agent": user_agent[:250],
        "device_type": device_type,
        "browser": browser,
        "os": os_name,
        "screen_resolution": (payload.screen_resolution or request.headers.get("X-Screen-Resolution"))[:50] if (payload.screen_resolution or request.headers.get("X-Screen-Resolution")) else None,
        "viewport_size": (payload.viewport_size or request.headers.get("X-Viewport-Size"))[:50] if (payload.viewport_size or request.headers.get("X-Viewport-Size")) else None,
        "client_timezone": (payload.client_timezone or request.headers.get("X-Client-Timezone"))[:100] if (payload.client_timezone or request.headers.get("X-Client-Timezone")) else None,
        "language": (payload.language or (request.headers.get("accept-language") or "").split(",")[0].strip())[:50],
        "referrer": (payload.referrer or request.headers.get("referer") or "")[:250],
        "initial_referrer": (payload.initial_referrer or request.headers.get("X-Initial-Referrer"))[:250] if (payload.initial_referrer or request.headers.get("X-Initial-Referrer")) else None,
        "utm_source": payload.utm_source or request.headers.get("X-UTM-Source"),
        "utm_medium": payload.utm_medium or request.headers.get("X-UTM-Medium"),
        "utm_campaign": payload.utm_campaign or request.headers.get("X-UTM-Campaign"),
        "utm_term": payload.utm_term or request.headers.get("X-UTM-Term"),
        "utm_content": payload.utm_content or request.headers.get("X-UTM-Content"),
        "page_title": payload.page_title[:255] if payload.page_title else None,
        "event_data": event_data_str,
        "created_at": datetime.utcnow()
    }

    enqueue_telemetry_event(item)
    return {"status": "ok", "recorded": True}


@router.get("/stats")
def get_telemetry_stats(
    days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Retrieve summarized telemetry metrics for administrative oversight."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        total_events = db.execute(text("SELECT COUNT(*) FROM user_activity_logs WHERE created_at >= :c"), {"c": cutoff}).scalar() or 0
        today_events = db.execute(text("SELECT COUNT(*) FROM user_activity_logs WHERE created_at >= :t"), {"t": today_start}).scalar() or 0

        unique_anon_period = db.execute(text(
            "SELECT COUNT(DISTINCT COALESCE(anon_id, ip_hash)) FROM user_activity_logs WHERE created_at >= :c"
        ), {"c": cutoff}).scalar() or 0

        unique_anon_today = db.execute(text(
            "SELECT COUNT(DISTINCT COALESCE(anon_id, ip_hash)) FROM user_activity_logs WHERE created_at >= :t"
        ), {"t": today_start}).scalar() or 0

        sessions_period = db.execute(text(
            "SELECT COUNT(DISTINCT session_id) FROM user_activity_logs WHERE session_id IS NOT NULL AND created_at >= :c"
        ), {"c": cutoff}).scalar() or 0

        regions_raw = db.execute(text(
            "SELECT COALESCE(region, 'Unknown') as reg, COUNT(*) as cnt "
            "FROM user_activity_logs WHERE created_at >= :c GROUP BY reg ORDER BY cnt DESC LIMIT 10"
        ), {"c": cutoff}).fetchall()
        top_regions = [{"region": r[0], "count": r[1]} for r in regions_raw]

        cities_raw = db.execute(text(
            "SELECT COALESCE(city, 'Unknown') as cty, COALESCE(region, '') as reg, COUNT(*) as cnt "
            "FROM user_activity_logs WHERE city IS NOT NULL AND created_at >= :c GROUP BY cty, reg ORDER BY cnt DESC LIMIT 10"
        ), {"c": cutoff}).fetchall()
        top_cities = [{"city": f"{r[0]}, {r[1]}" if r[1] else r[0], "count": r[2]} for r in cities_raw]

        actions_raw = db.execute(text(
            "SELECT action_type, COUNT(*) as cnt "
            "FROM user_activity_logs WHERE created_at >= :c GROUP BY action_type ORDER BY cnt DESC LIMIT 10"
        ), {"c": cutoff}).fetchall()
        top_actions = [{"action": r[0], "count": r[1]} for r in actions_raw]

        devices_raw = db.execute(text(
            "SELECT COALESCE(device_type, 'desktop') as dev, COUNT(*) as cnt "
            "FROM user_activity_logs WHERE created_at >= :c GROUP BY dev ORDER BY cnt DESC"
        ), {"c": cutoff}).fetchall()
        devices = [{"device": r[0], "count": r[1]} for r in devices_raw]

        browsers_raw = db.execute(text(
            "SELECT COALESCE(browser, 'Other') as brw, COUNT(*) as cnt "
            "FROM user_activity_logs WHERE created_at >= :c GROUP BY brw ORDER BY cnt DESC LIMIT 6"
        ), {"c": cutoff}).fetchall()
        browsers = [{"browser": r[0], "count": r[1]} for r in browsers_raw]

        utm_raw = db.execute(text(
            "SELECT COALESCE(utm_source, 'direct/organic') as src, COUNT(*) as cnt "
            "FROM user_activity_logs WHERE created_at >= :c GROUP BY src ORDER BY cnt DESC LIMIT 6"
        ), {"c": cutoff}).fetchall()
        top_sources = [{"source": r[0], "count": r[1]} for r in utm_raw]

        return {
            "time_window_days": days,
            "total_events": total_events,
            "today_events": today_events,
            "unique_visitors_period": unique_anon_period,
            "unique_visitors_today": unique_anon_today,
            "total_sessions_period": sessions_period,
            "top_regions": top_regions,
            "top_cities": top_cities,
            "top_actions": top_actions,
            "devices": devices,
            "browsers": browsers,
            "top_sources": top_sources
        }
    except Exception as e:
        return {
            "error": str(e),
            "time_window_days": days,
            "total_events": 0,
            "unique_visitors_today": 0
        }
