"""Opportunity relationship model."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Float, Text, Boolean, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class OpportunityRelationship(Base):
    __tablename__ = "opportunity_relationships"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_opp_id: Mapped[int] = mapped_column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    target_opp_id: Mapped[int] = mapped_column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(50))  # predecessor, successor, recurring, renamed, complementary, stackable, overlapping, cost_share_match
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    rationale: Mapped[Optional[str]] = mapped_column(Text)
    evidence: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    is_inferred: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    source_opportunity = relationship("Opportunity", foreign_keys=[source_opp_id])
    target_opportunity = relationship("Opportunity", foreign_keys=[target_opp_id])
    
    __table_args__ = (
        Index("ix_rel_type", "relationship_type"),
        Index("ix_rel_pair", "source_opp_id", "target_opp_id", unique=True),
    )
