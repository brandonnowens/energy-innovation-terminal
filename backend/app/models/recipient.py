"""Recipient / Awardee organization database model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, DateTime, Float, Integer, String, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Recipient(Base):
    """Enriched awardee / recipient organization profile with LLM research & geocoding."""

    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    normalized_name: Mapped[Optional[str]] = mapped_column(String(500), index=True)
    
    # Classification
    recipient_type: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    primary_technology: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    technology_tags: Mapped[Optional[str]] = mapped_column(Text)
    sector: Mapped[Optional[str]] = mapped_column(String(200))
    fuel_types: Mapped[Optional[str]] = mapped_column(String(200))
    commercialization_stage: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Headquarters Location
    headquarters_city: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    headquarters_state: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    headquarters_country: Mapped[Optional[str]] = mapped_column(String(100), default="US")
    headquarters_address: Mapped[Optional[str]] = mapped_column(String(500))
    latitude: Mapped[Optional[float]] = mapped_column(Float, index=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, index=True)
    geocode_precision: Mapped[Optional[str]] = mapped_column(String(50))
    is_ny_based: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, index=True)
    
    # Organization Profile & Team
    website_url: Mapped[Optional[str]] = mapped_column(String(500))
    founded_year: Mapped[Optional[int]] = mapped_column(Integer)
    employee_range: Mapped[Optional[str]] = mapped_column(String(50))
    leadership_team: Mapped[Optional[str]] = mapped_column(Text)
    key_innovations: Mapped[Optional[str]] = mapped_column(Text)
    diversity_certifications: Mapped[Optional[str]] = mapped_column(String(200))
    climate_impact_focus: Mapped[Optional[str]] = mapped_column(Text)
    
    # Financials & Award Aggregates
    total_awards_count: Mapped[int] = mapped_column(Integer, default=0, index=True)
    total_funding_received: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    total_nyserda_funding: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    nyserda_award_count: Mapped[int] = mapped_column(Integer, default=0, index=True)
    total_federal_funding: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    federal_award_count: Mapped[int] = mapped_column(Integer, default=0)
    funded_agencies: Mapped[Optional[str]] = mapped_column(Text)
    first_award_year: Mapped[Optional[int]] = mapped_column(Integer)
    latest_award_year: Mapped[Optional[int]] = mapped_column(Integer)
    enrichment_source: Mapped[Optional[str]] = mapped_column(String(200), default="model_standardized")
    last_enriched_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    
    @property
    def total_state_funding(self) -> float:
        return self.total_nyserda_funding

    @property
    def state_award_count(self) -> int:
        return self.nyserda_award_count

    def __repr__(self):
        return f"<Recipient {self.id}: {self.name} ({self.headquarters_city}, {self.headquarters_state}) - ${self.total_funding_received:,.0f}>"
