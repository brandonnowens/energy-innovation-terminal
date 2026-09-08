"""Award and AwardResult database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Award(Base):
    """A specific award/grant made under a funding opportunity."""

    __tablename__ = "awards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("opportunities.id"), index=True)
    external_award_id: Mapped[Optional[str]] = mapped_column(String(200), index=True)

    # Recipient
    recipient_name: Mapped[Optional[str]] = mapped_column(String(500), index=True)
    recipient_type: Mapped[Optional[str]] = mapped_column(String(100), index=True)  # university, company, nonprofit, lab, government, individual
    recipient_city: Mapped[Optional[str]] = mapped_column(String(200))
    recipient_state: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    recipient_zip: Mapped[Optional[str]] = mapped_column(String(50))
    recipient_country: Mapped[Optional[str]] = mapped_column(String(100), default="US")
    recipient_uei: Mapped[Optional[str]] = mapped_column(String(100))  # Unique Entity ID

    # Principal Investigator
    pi_name: Mapped[Optional[str]] = mapped_column(String(500))
    pi_email: Mapped[Optional[str]] = mapped_column(String(500))
    pi_institution: Mapped[Optional[str]] = mapped_column(String(500))

    # Financials
    award_amount: Mapped[Optional[float]] = mapped_column(Float, index=True)
    total_estimated: Mapped[Optional[float]] = mapped_column(Float)
    cost_share_amount: Mapped[Optional[float]] = mapped_column(Float)

    # Dates
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    award_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Project
    project_title: Mapped[Optional[str]] = mapped_column(Text)
    project_abstract: Mapped[Optional[str]] = mapped_column(Text)
    award_type: Mapped[Optional[str]] = mapped_column(String(100))  # grant, cooperative_agreement, contract, fellowship, sbir_phase1, sbir_phase2
    cfda_number: Mapped[Optional[str]] = mapped_column(String(50))
    cfda_title: Mapped[Optional[str]] = mapped_column(String(500))

    # Program
    program_name: Mapped[Optional[str]] = mapped_column(String(500))
    program_office: Mapped[Optional[str]] = mapped_column(String(500))
    agency: Mapped[Optional[str]] = mapped_column(String(255), index=True)

    # Provenance & Geocoding
    source_name: Mapped[Optional[str]] = mapped_column(String(255))
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    raw_data: Mapped[Optional[str]] = mapped_column(Text)
    year: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    solicitation_number: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, index=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, index=True)
    geocode_method: Mapped[Optional[str]] = mapped_column(String(100))
    geocode_confidence: Mapped[Optional[float]] = mapped_column(Float)


    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    opportunity: Mapped[Optional["Opportunity"]] = relationship(back_populates="awards")
    results: Mapped[list["AwardResult"]] = relationship(back_populates="award", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Award {self.id}: {self.recipient_name} - {self.project_title}>"


class AwardResult(Base):
    """A result/output of an award (publication, patent, report, etc.)."""

    __tablename__ = "award_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    award_id: Mapped[int] = mapped_column(Integer, ForeignKey("awards.id"), index=True)

    result_type: Mapped[str] = mapped_column(String(50))  # publication, patent, report, dataset, product, deployment, startup
    title: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    doi: Mapped[Optional[str]] = mapped_column(String(200))
    patent_number: Mapped[Optional[str]] = mapped_column(String(100))
    url: Mapped[Optional[str]] = mapped_column(String(500))
    authors: Mapped[Optional[str]] = mapped_column(Text)
    date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    source_name: Mapped[Optional[str]] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    award: Mapped["Award"] = relationship(back_populates="results")

    def __repr__(self):
        return f"<AwardResult {self.id}: {self.result_type} - {self.title}>"


# Import Opportunity here to avoid circular imports - the relationship is set up in opportunity.py
from app.models.opportunity import Opportunity  # noqa: E402
