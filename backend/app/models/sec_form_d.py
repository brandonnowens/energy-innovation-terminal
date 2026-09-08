"""SEC Form D Regulatory Private Offerings Database Model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class SecFormDFiling(Base):
    """SEC EDGAR Form D (Regulation D Exempt Private Offerings)."""

    __tablename__ = "sec_form_d_filings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("recipients.id", ondelete="SET NULL"), index=True)
    
    # SEC Identifiers
    cik_number: Mapped[str] = mapped_column(String(16), index=True)
    accession_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    filing_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    date_of_first_sale: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Legal Entity
    entity_legal_name: Mapped[str] = mapped_column(String(255), index=True)
    jurisdiction_state: Mapped[Optional[str]] = mapped_column(String(64))
    primary_industry: Mapped[Optional[str]] = mapped_column(String(128))  # Energy, Cleantech, Advanced Manufacturing, etc.
    
    # Offering Financials
    total_offering_amount_usd: Mapped[Optional[float]] = mapped_column(Float)
    total_amount_sold_usd: Mapped[Optional[float]] = mapped_column(Float, index=True)
    total_remaining_usd: Mapped[Optional[float]] = mapped_column(Float)
    
    # Securities Details
    is_equity: Mapped[bool] = mapped_column(Boolean, default=True)
    is_debt: Mapped[bool] = mapped_column(Boolean, default=False)
    is_option_or_warrant: Mapped[bool] = mapped_column(Boolean, default=False)
    num_investors: Mapped[Optional[int]] = mapped_column(Integer)
    minimum_investment_accepted_usd: Mapped[Optional[float]] = mapped_column(Float)
    
    # Leadership & Officers
    executive_officers_json: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of directors and executive officers
    
    # Provenance
    sec_html_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipient = relationship("Recipient", backref="sec_filings")
