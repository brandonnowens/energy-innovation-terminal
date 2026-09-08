"""
SQLAlchemy ORM models for the Master Clean Technology Reference & Innovation Frontier.
Stores sectors, technologies, standardized KPIs, cost/performance trajectories,
and explorable subsystem architectures as relational database tables.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship

from app.database import Base


class TechnologyCategory(Base):
    """Clean energy innovation sector vertical."""
    __tablename__ = "technology_categories"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    icon = Column(String(64), nullable=False, default="Zap")
    description = Column(Text, nullable=True)
    color = Column(String(64), nullable=True)
    accent = Column(String(32), nullable=True)
    sort_order = Column(Integer, default=0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    technologies = relationship("Technology", back_populates="category", cascade="all, delete-orphan")


class Technology(Base):
    """Detailed technology profile and innovation frontier knowledge base."""
    __tablename__ = "technologies"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category_id = Column(String(64), ForeignKey("technology_categories.id"), nullable=False, index=True)
    headline = Column(Text, nullable=False)
    trl_current = Column(Integer, default=5)
    trl_target = Column(Integer, default=9)
    sector = Column(String(128), nullable=True)
    fuel_vector = Column(String(128), nullable=True)
    vector_type = Column(String(32), default="hardware", index=True)  # hardware, fuel_carrier, hybrid
    fuel_profile_json = Column(Text, nullable=True)  # JSON object with CI, energy density, feedstock, etc.
    keywords_json = Column(Text, nullable=True)  # JSON array of search strings

    # Plain-English Executive Synthesis
    plain_what_is_it = Column(Text, nullable=True)
    plain_how_it_works = Column(Text, nullable=True)
    plain_why_it_matters = Column(Text, nullable=True)
    plain_macro_problem_solved = Column(Text, nullable=True)

    # Evolution Timeline
    evolution_past = Column(Text, nullable=True)
    evolution_present = Column(Text, nullable=True)
    evolution_future = Column(Text, nullable=True)

    # Innovation Frontier & Moonshot
    moonshot_goal = Column(Text, nullable=True)
    bottlenecks_json = Column(Text, nullable=True)  # JSON array
    active_research_json = Column(Text, nullable=True)  # JSON array

    # Trade-offs & Radar Scores
    tradeoffs_strengths_json = Column(Text, nullable=True)  # JSON array
    tradeoffs_weaknesses_json = Column(Text, nullable=True)  # JSON array
    competing_techs_json = Column(Text, nullable=True)  # JSON array
    radar_scores_json = Column(Text, nullable=True)  # JSON object

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("TechnologyCategory", back_populates="technologies")
    cost_performance = relationship("TechnologyCostPerformance", back_populates="technology", uselist=False, cascade="all, delete-orphan")
    kpis = relationship("TechnologyKPI", back_populates="technology", cascade="all, delete-orphan", order_by="TechnologyKPI.sort_order")
    subsystems = relationship("TechnologySubsystem", back_populates="technology", cascade="all, delete-orphan")


class TechnologyCostPerformance(Base):
    """Quantitative cost and performance baseline vs target trajectories."""
    __tablename__ = "technology_cost_performance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    technology_id = Column(String(64), ForeignKey("technologies.id"), nullable=False, unique=True, index=True)

    # Cost Metric
    cost_metric_name = Column(String(255), nullable=False)
    cost_unit = Column(String(64), nullable=False)
    cost_baseline_2024 = Column(Float, nullable=True)
    cost_baseline_fmt = Column(String(64), nullable=True)
    cost_target_2030 = Column(Float, nullable=True)
    cost_target_2030_fmt = Column(String(64), nullable=True)
    cost_target_2035 = Column(Float, nullable=True)
    cost_target_2035_fmt = Column(String(64), nullable=True)
    cost_reduction_pct = Column(String(32), nullable=True)
    cost_primary_driver = Column(Text, nullable=True)

    # Performance Metric
    perf_metric_name = Column(String(255), nullable=False)
    perf_unit = Column(String(64), nullable=False)
    perf_baseline_2024 = Column(Float, nullable=True)
    perf_baseline_fmt = Column(String(64), nullable=True)
    perf_target_2030 = Column(Float, nullable=True)
    perf_target_2030_fmt = Column(String(64), nullable=True)
    perf_target_2035 = Column(Float, nullable=True)
    perf_target_2035_fmt = Column(String(64), nullable=True)
    perf_improvement_pct = Column(String(32), nullable=True)
    perf_primary_driver = Column(Text, nullable=True)

    # Scale Elasticity & Federal Targets
    learning_rate = Column(String(255), nullable=True)
    earthshot_goal = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    technology = relationship("Technology", back_populates="cost_performance")


class TechnologyKPI(Base):
    """Key Performance Indicator milestones for technology development."""
    __tablename__ = "technology_kpis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    technology_id = Column(String(64), ForeignKey("technologies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    current_value = Column(String(128), nullable=False)
    target_2030 = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False, default="on_track")  # achieved, on_track, challenging
    sort_order = Column(Integer, default=0)

    # Relationships
    technology = relationship("Technology", back_populates="kpis")


class TechnologySubsystem(Base):
    """Explorable vector subsystem node definitions for interactive diagrams."""
    __tablename__ = "technology_subsystems"

    id = Column(String(128), primary_key=True)  # e.g. iron_air_battery:air_breathing_cathode
    technology_id = Column(String(64), ForeignKey("technologies.id"), nullable=False, index=True)
    node_id = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(128), nullable=True)
    x = Column(Integer, default=50)
    y = Column(Integer, default=50)
    icon = Column(String(64), default="Zap")
    summary = Column(Text, nullable=True)
    operating_value = Column(String(128), nullable=True)
    materials = Column(String(255), nullable=True)
    failure_mode = Column(Text, nullable=True)
    frontier_bottleneck = Column(Text, nullable=True)
    active_research = Column(Text, nullable=True)

    # Relationships
    technology = relationship("Technology", back_populates="subsystems")
