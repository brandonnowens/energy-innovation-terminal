"""Database models for Venture & Patent Attributions."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RecipientPatent(Base):
    """USPTO Patent assigned to a recipient, citing federal or state grant awards (Bayh-Dole Act)."""

    __tablename__ = "recipient_patents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipients.id"), index=True)
    award_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("awards.id"), index=True)
    
    # Patent Information
    patent_number: Mapped[str] = mapped_column(String(50), index=True)  # e.g., US11456789B2
    title: Mapped[str] = mapped_column(String(500), index=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text)
    filing_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    grant_date: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    
    # Classification & Provenance
    cpc_class: Mapped[Optional[str]] = mapped_column(String(50))  # e.g., H01M 10/052 (Batteries)
    technology_area: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    bayh_dole_citation: Mapped[Optional[str]] = mapped_column(Text)  # e.g. "This invention was made with government support under DE-AR0000850 awarded by DOE."
    grant_contract_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Assignee & Inventors
    assignee_name: Mapped[Optional[str]] = mapped_column(String(500), index=True)
    inventors: Mapped[Optional[str]] = mapped_column(Text)  # JSON or comma-separated
    cited_by_count: Mapped[int] = mapped_column(Integer, default=0)  # Citations by downstream corporate patents
    patent_url: Mapped[Optional[str]] = mapped_column(String(500))  # Google Patents / USPTO link
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class RecipientInvestment(Base):
    """Private venture capital / equity financing round raised by a recipient organization."""

    __tablename__ = "recipient_investments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipients.id"), index=True)
    
    # Funding Round Details
    round_type: Mapped[str] = mapped_column(String(100), index=True)  # Seed, Series A, Series B, Series C, Growth, Private Equity, IPO
    round_date: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    amount_usd: Mapped[Optional[float]] = mapped_column(Float, index=True)
    valuation_usd: Mapped[Optional[float]] = mapped_column(Float)
    
    # Syndicate & Investors
    lead_investor: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    participating_investors_json: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of investor names
    investor_count: Mapped[int] = mapped_column(Integer, default=1)
    
    # Context
    post_grant_months: Mapped[Optional[int]] = mapped_column(Integer)  # Number of months after first public grant
    is_climate_fund_backed: Mapped[bool] = mapped_column(Boolean, default=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
