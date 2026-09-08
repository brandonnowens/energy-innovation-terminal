"""Community, strategy, report, chart, and moderation models."""
import secrets
import hashlib
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, JSON,
    Index,
)
from app.database import Base


def generate_token():
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class CreatorToken(Base):
    __tablename__ = "creator_tokens"

    id = Column(Integer, primary_key=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    recovery_key_hash = Column(String(64), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    generation_count = Column(Integer, default=0)
    is_banned = Column(Boolean, default=False)


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True)
    creator_hash = Column(String(64), nullable=False, index=True)
    mode = Column(String(30), nullable=False)  # project_sponsor, funding_organization
    title = Column(String(500))
    inputs_json = Column(JSON)
    results_json = Column(JSON)
    report_json = Column(JSON)
    status = Column(String(20), default="draft", index=True)  # draft, processing, complete, failed, archived
    is_public = Column(Boolean, default=False)
    visibility_confirmed = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    tags_json = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    delete_confirmed_at = Column(DateTime, nullable=True)


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    creator_hash = Column(String(64), nullable=False, index=True)
    title = Column(String(500))
    summary = Column(Text)
    prompt = Column(Text, nullable=False)
    plan_json = Column(JSON)
    results_json = Column(JSON)
    report_json = Column(JSON)
    status = Column(String(20), default="draft", index=True)
    is_public = Column(Boolean, default=False)
    visibility_confirmed = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    tags_json = Column(JSON, default=list)
    filters_json = Column(JSON)
    coverage_json = Column(JSON)
    methodology = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    delete_confirmed_at = Column(DateTime, nullable=True)


class SavedChart(Base):
    __tablename__ = "saved_charts"

    id = Column(Integer, primary_key=True)
    creator_hash = Column(String(64), nullable=False, index=True)
    title = Column(String(500))
    chart_type = Column(String(50))  # line, area, bar, scatter, heatmap, treemap, sankey, network
    config_json = Column(JSON)
    data_query = Column(Text)
    filters_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SavedView(Base):
    __tablename__ = "saved_views"

    id = Column(Integer, primary_key=True)
    creator_hash = Column(String(64), nullable=False, index=True)
    title = Column(String(500))
    view_type = Column(String(30))  # network, chart, strategy
    config_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AbuseReport(Base):
    __tablename__ = "abuse_reports"

    id = Column(Integer, primary_key=True)
    item_type = Column(String(30), nullable=False)  # strategy, report
    item_id = Column(Integer, nullable=False)
    reason = Column(Text)
    reporter_ip_hash = Column(String(64))
    status = Column(String(20), default="pending")  # pending, reviewed, dismissed, actioned
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)


Index("ix_strategy_public", Strategy.is_public, Strategy.status)
Index("ix_report_public", Report.is_public, Report.status)
