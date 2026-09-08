"""Proposal and Grant Application Pursuit database models."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Proposal(Base):
    """A grant application pursuit or winning proposal dossier."""

    __tablename__ = "proposals"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)  # e.g. "prop-cec-epic-heat" or "prop-awd-1234"
    solicitation_number: Mapped[str] = mapped_column(String(255), index=True)
    opportunity_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("opportunities.id", ondelete="SET NULL"), index=True)
    award_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("awards.id", ondelete="SET NULL"), index=True)
    creator_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True)

    title: Mapped[str] = mapped_column(String(500))
    agency: Mapped[str] = mapped_column(String(255), index=True)
    agency_code: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    
    # Financials
    target_funding: Mapped[float] = mapped_column(Float, default=0.0)
    total_budget: Mapped[float] = mapped_column(Float, default=0.0)
    cost_share_pct: Mapped[float] = mapped_column(Float, default=0.0)
    cost_share_amount: Mapped[Optional[float]] = mapped_column(Float, default=0.0)

    # Timing & Status
    deadline: Mapped[Optional[str]] = mapped_column(String(50))
    days_remaining: Mapped[Optional[int]] = mapped_column(Integer)
    award_date: Mapped[Optional[str]] = mapped_column(String(50))
    year: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    stage: Mapped[str] = mapped_column(String(50), default="draft", index=True)  # draft, cbp_compliance, red_team, submitted, award_won
    stage_label: Mapped[Optional[str]] = mapped_column(String(100))
    is_won: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Audit & Scoring
    red_team_score: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    compliance_pct: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    # Team & Consortium
    lead_pi: Mapped[Optional[str]] = mapped_column(String(300))
    pi_email: Mapped[Optional[str]] = mapped_column(String(300))
    pi_institution: Mapped[Optional[str]] = mapped_column(String(500))
    recipient_name: Mapped[Optional[str]] = mapped_column(String(500), index=True)
    recipient_city: Mapped[Optional[str]] = mapped_column(String(200))
    recipient_state: Mapped[Optional[str]] = mapped_column(String(100))
    recipient_type: Mapped[Optional[str]] = mapped_column(String(100))
    partner_consortium_json: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Scope & Details
    tech_area: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    sopo_tasks_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON)
    rubric_scores_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON)
    raw_metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    opportunity: Mapped[Optional["Opportunity"]] = relationship("Opportunity")
    award: Mapped[Optional["Award"]] = relationship("Award")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "solicitation_number": self.solicitation_number,
            "opportunity_id": self.opportunity_id,
            "award_id": self.award_id,
            "title": self.title,
            "agency": self.agency,
            "agency_code": self.agency_code or (self.agency[:10] if self.agency else "AGY"),
            "target_funding": self.target_funding,
            "total_budget": self.total_budget,
            "cost_share_pct": self.cost_share_pct,
            "cost_share_amount": self.cost_share_amount or (self.total_budget - self.target_funding if self.total_budget > self.target_funding else 0.0),
            "deadline": self.deadline,
            "days_remaining": self.days_remaining,
            "award_date": self.award_date,
            "year": self.year,
            "stage": self.stage,
            "stage_label": self.stage_label or self.stage.replace("_", " ").title(),
            "is_won": self.is_won,
            "red_team_score": self.red_team_score or 0,
            "compliance_pct": self.compliance_pct or 0,
            "lead_pi": self.lead_pi,
            "pi_email": self.pi_email,
            "pi_institution": self.pi_institution,
            "recipient_name": self.recipient_name,
            "recipient_city": self.recipient_city,
            "recipient_state": self.recipient_state,
            "recipient_type": self.recipient_type,
            "partner_consortium": self.partner_consortium_json or [],
            "tech_area": self.tech_area,
            "description": self.description,
            "sopo_tasks": self.sopo_tasks_json or [],
            "rubric_scores": self.rubric_scores_json or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Proposal {self.id}: {self.title}>"


from app.models.opportunity import Opportunity  # noqa: E402
from app.models.award import Award  # noqa: E402
