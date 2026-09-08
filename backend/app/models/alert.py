"""SQLAlchemy models for Real-Time Alerts and Watchlist Triggers."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from app.database import Base


class AlertSubscription(Base):
    """Stores user-configured opportunity triggers, keyword watchlists, and regulatory radars."""
    __tablename__ = "alert_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(200), nullable=False)
    
    keywords = Column(String(300), default="")
    target_agencies = Column(JSON, default=list)
    target_states = Column(JSON, default=list)
    trl_min = Column(Integer, default=1)
    trl_max = Column(Integer, default=9)
    min_funding = Column(Float, default=0.0)
    include_regulatory_proceedings = Column(Boolean, default=True)
    
    email_destination = Column(String(200), nullable=False)
    frequency = Column(String(50), default="instant")
    is_active = Column(Boolean, default=True, index=True)
    
    last_triggered_at = Column(DateTime, nullable=True)
    matches_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AlertTriggerLog(Base):
    """Log of dispatched alert notifications and matching opportunities."""
    __tablename__ = "alert_trigger_logs"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("alert_subscriptions.id", ondelete="CASCADE"), index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=True, index=True)
    
    matched_reason = Column(String(300))
    delivered_to = Column(String(200))
    delivered_at = Column(DateTime, default=datetime.utcnow)
