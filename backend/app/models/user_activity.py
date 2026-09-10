"""User activity and telemetry models for usage analytics."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Index
)
from app.database import Base


class UserActivityLog(Base):
    """Logs individual user interactions, page views, and API executions for usage analytics."""
    __tablename__ = "user_activity_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True, index=True)
    ip_hash = Column(String(64), nullable=False, index=True)
    session_id = Column(String(64), nullable=True, index=True)
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), default="GET", nullable=False)
    action_type = Column(String(50), default="api_request", nullable=False, index=True)
    status_code = Column(Integer, default=200, nullable=False)
    duration_ms = Column(Float, default=0.0, nullable=False)
    user_agent = Column(String(255), nullable=True)
    device_type = Column(String(50), default="desktop", nullable=True)
    referrer = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index("idx_user_activity_created_action", "created_at", "action_type"),
        Index("idx_user_activity_ip_created", "ip_hash", "created_at"),
    )
