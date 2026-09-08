"""Federal Procurement & Commercial Offtake Contracts Database Model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class FederalProcurementContract(Base):
    """FPDS / SAM.gov Federal Contracts, DoD DIU Offtake & SBIR Phase III Sole-Source Contracts."""

    __tablename__ = "federal_procurement_contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("recipients.id", ondelete="SET NULL"), index=True)
    award_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("awards.id", ondelete="SET NULL"), index=True)
    
    # Contract Details
    contract_number: Mapped[str] = mapped_column(String(64), index=True)
    contracting_agency: Mapped[str] = mapped_column(String(128), index=True)  # DoD, Army, Navy, Air Force, GSA, DOE, NASA, EPA
    contracting_office: Mapped[Optional[str]] = mapped_column(String(255))
    award_type: Mapped[Optional[str]] = mapped_column(String(64))  # Definitive Contract, Delivery Order, BPA Call, Other Transaction Authority (OTA)
    
    # Commercialization & SBIR Phase III Classification
    is_sbir_phase_3: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_sole_source: Mapped[bool] = mapped_column(Boolean, default=False)
    psc_code: Mapped[Optional[str]] = mapped_column(String(16))  # Product Service Code
    naics_code: Mapped[Optional[str]] = mapped_column(String(16))
    
    # Financials
    obligated_amount_usd: Mapped[float] = mapped_column(Float, index=True)
    base_and_all_options_value_usd: Mapped[Optional[float]] = mapped_column(Float)
    
    # Performance & Timing
    signed_date: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    place_of_performance_state: Mapped[Optional[str]] = mapped_column(String(32))
    place_of_performance_city: Mapped[Optional[str]] = mapped_column(String(128))
    
    # Description & Provenance
    description_of_requirement: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipient = relationship("Recipient", backref="procurement_contracts")
    award = relationship("Award", backref="procurement_transitions")
