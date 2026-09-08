"""Historical opportunity and project models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HistoricalOpportunity(Base):
    """A closed/past NYSERDA funding opportunity."""

    __tablename__ = "historical_opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agency: Mapped[str] = mapped_column(String(100), default="NYSERDA", index=True)
    solicitation_number: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(500))
    solicitation_type: Mapped[Optional[str]] = mapped_column(String(50))
    closed_date: Mapped[Optional[str]] = mapped_column(String(50))
    year: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    funding_amount: Mapped[Optional[float]] = mapped_column(Float)
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    detail_url: Mapped[Optional[str]] = mapped_column(String(500))
    org_type: Mapped[Optional[str]] = mapped_column(String(30))
    funding_type: Mapped[Optional[str]] = mapped_column(String(50))
    total_funding: Mapped[Optional[float]] = mapped_column(Float)
    max_per_award: Mapped[Optional[float]] = mapped_column(Float)
    objectives: Mapped[Optional[str]] = mapped_column(Text)
    raw_source_data: Mapped[Optional[str]] = mapped_column(Text)
    data_provenance: Mapped[Optional[str]] = mapped_column(String(50), default="observed")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class HistoricalProject(Base):
    """A historically funded NYSERDA R&D project (from Open NY)."""

    __tablename__ = "historical_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agency: Mapped[str] = mapped_column(String(100), default="NYSERDA", index=True)
    application_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    project_title: Mapped[str] = mapped_column(String(500))
    contractor_name: Mapped[Optional[str]] = mapped_column(String(300))
    contractor_type: Mapped[Optional[str]] = mapped_column(String(100))
    project_type: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    technology_1: Mapped[Optional[str]] = mapped_column(String(200))
    technology_2: Mapped[Optional[str]] = mapped_column(String(200))
    technology_3: Mapped[Optional[str]] = mapped_column(String(200))
    project_description: Mapped[Optional[str]] = mapped_column(Text)
    award_date: Mapped[Optional[str]] = mapped_column(String(50))
    award_amount: Mapped[Optional[float]] = mapped_column(Float)
    contractor_city: Mapped[Optional[str]] = mapped_column(String(100))
    contractor_state: Mapped[Optional[str]] = mapped_column(String(50))
    contractor_zip: Mapped[Optional[str]] = mapped_column(String(20))
    contractor_website: Mapped[Optional[str]] = mapped_column(String(500))
    data_as_of: Mapped[Optional[str]] = mapped_column(String(50))

    source_dataset: Mapped[str] = mapped_column(String(50), default="7xzk-zyk5")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
