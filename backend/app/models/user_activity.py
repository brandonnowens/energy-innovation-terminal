"""User activity and telemetry models for usage analytics."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Index, Text
)
from app.database import Base


class UserActivityLog(Base):
    """Logs individual user interactions, page views, and API executions for usage analytics."""
    __tablename__ = "user_activity_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True, index=True)
    anon_id = Column(String(64), nullable=True, index=True)
    session_id = Column(String(64), nullable=True, index=True)
    ip_hash = Column(String(64), nullable=False, index=True)
    
    # Geolocation metadata (from Cloudflare edge headers)
    country = Column(String(10), nullable=True, index=True)
    region = Column(String(50), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    cf_ray = Column(String(50), nullable=True)
    
    # Request & Action Details
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), default="GET", nullable=False)
    action_type = Column(String(50), default="api_request", nullable=False, index=True)
    status_code = Column(Integer, default=200, nullable=False)
    duration_ms = Column(Float, default=0.0, nullable=False)
    
    # Client & Hardware Demographics
    user_agent = Column(String(255), nullable=True)
    device_type = Column(String(50), default="desktop", nullable=True, index=True)
    browser = Column(String(50), nullable=True, index=True)
    os = Column(String(50), nullable=True, index=True)
    screen_resolution = Column(String(50), nullable=True)
    viewport_size = Column(String(50), nullable=True)
    client_timezone = Column(String(100), nullable=True)
    language = Column(String(50), nullable=True)
    
    # Acquisition & Attribution
    referrer = Column(String(255), nullable=True)
    initial_referrer = Column(String(255), nullable=True)
    utm_source = Column(String(100), nullable=True, index=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    utm_term = Column(String(100), nullable=True)
    utm_content = Column(String(100), nullable=True)
    
    # Event Context
    page_title = Column(String(255), nullable=True)
    event_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index("idx_user_activity_created_action", "created_at", "action_type"),
        Index("idx_user_activity_ip_created", "ip_hash", "created_at"),
        Index("idx_user_activity_anon_created", "anon_id", "created_at"),
        Index("idx_user_activity_region_created", "region", "created_at"),
    )

