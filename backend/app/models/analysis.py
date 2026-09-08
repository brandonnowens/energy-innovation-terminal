"""Project analysis models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProjectAnalysis(Base):
    """A user's project analysis."""

    __tablename__ = "project_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    input_text: Mapped[str] = mapped_column(Text)
    structured_profile: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    technology_areas: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    activity_types: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    estimated_trl: Mapped[Optional[int]] = mapped_column(Integer)
    applicant_type: Mapped[Optional[str]] = mapped_column(String(100))
    target_location: Mapped[Optional[str]] = mapped_column(String(200))
    target_agencies: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of agency names searched
    project_cost: Mapped[Optional[float]] = mapped_column(Float)
    project_timeline: Mapped[Optional[str]] = mapped_column(String(200))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    decomposition: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    funding_architecture: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class AnalysisMatch(Base):
    """A match between a project analysis and an opportunity."""

    __tablename__ = "analysis_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("project_analyses.id", ondelete="CASCADE"), index=True)
    opportunity_id: Mapped[Optional[int]] = mapped_column(ForeignKey("opportunities.id"), index=True)
    program_id: Mapped[Optional[int]] = mapped_column(ForeignKey("programs.id"))
    historical_opportunity_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("historical_opportunities.id")
    )

    match_type: Mapped[str] = mapped_column(String(30))
    # strong, conditional, component, commercialization, watchlist, no_match
    match_category: Mapped[Optional[str]] = mapped_column(String(50))
    # current_match, conditional_match, component_stack, ecosystem_support, historical_precedent
    fit_score: Mapped[Optional[float]] = mapped_column(Float)
    confidence: Mapped[Optional[str]] = mapped_column(String(20))  # high, medium, low

    applicable_component: Mapped[Optional[str]] = mapped_column(String(200))
    why_it_fits: Mapped[Optional[str]] = mapped_column(Text)
    eligibility_summary: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    blockers: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    unknowns: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    recommended_positioning: Mapped[Optional[str]] = mapped_column(Text)
    useful_partners: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    timing_notes: Mapped[Optional[str]] = mapped_column(Text)
    next_action: Mapped[Optional[str]] = mapped_column(Text)
    evidence: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of source references
    assessment_json: Mapped[Optional[str]] = mapped_column(Text)  # Full competitive assessment JSON
    timeline_json: Mapped[Optional[str]] = mapped_column(Text)  # Action timeline JSON
    reasoning_type: Mapped[Optional[str]] = mapped_column(String(30))
    # fact, inferred_fit, strategic_option, historical_precedent, watchlist
