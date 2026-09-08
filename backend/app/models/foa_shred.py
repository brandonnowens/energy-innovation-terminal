"""SQLAlchemy model for AI FOA Shredder results."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from app.database import Base


class FoaShredResult(Base):
    """Stores shredded FOA evaluation rubrics, compliance gates, and document checklists."""
    __tablename__ = "foa_shred_results"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    solicitation_number = Column(String(100), index=True)
    agency = Column(String(100), index=True)
    title = Column(String(500), nullable=False)
    
    executive_summary = Column(Text)
    cost_share_required_pct = Column(Float, default=0.0)
    cost_share_rule_explanation = Column(Text)
    trl_min = Column(Integer, default=1)
    trl_max = Column(Integer, default=9)
    eligible_applicant_types = Column(JSON, default=list)
    domestic_manufacturing_clause = Column(Boolean, default=False)
    justice40_cbp_required = Column(Boolean, default=False)
    
    scoring_rubric_json = Column(JSON, default=list)
    submission_checklist_json = Column(JSON, default=list)

    concept_paper_deadline = Column(DateTime, nullable=True)
    full_application_deadline = Column(DateTime, nullable=True)
    qa_cutoff_date = Column(DateTime, nullable=True)
    estimated_award_date = Column(DateTime, nullable=True)
    
    key_win_themes = Column(JSON, default=list)
    red_team_fatal_flaws_to_avoid = Column(JSON, default=list)
    
    shredded_by = Column(String(100), default="AI FOA Engine v3.5")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
