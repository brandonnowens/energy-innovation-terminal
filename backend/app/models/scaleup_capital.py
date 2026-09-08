"""DOE Loan Programs Office (LPO) & IRA Section 48C Allocations Database Model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class FederalScaleupAllocation(Base):
    """DOE LPO (Title 17, ATVM, CIFIA) & IRA 48C Advanced Energy Project Allocations."""

    __tablename__ = "federal_scaleup_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("recipients.id", ondelete="SET NULL"), index=True)
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), index=True)
    
    # Program & Instrument
    program_category: Mapped[str] = mapped_column(String(64), index=True)  # DOE_LPO_TITLE_17, DOE_LPO_ATVM, IRA_48C_TAX_CREDIT, IRA_DIRECT_PAY
    support_type: Mapped[str] = mapped_column(String(64))  # Direct Loan, Loan Guarantee, Conditional Commitment, Tax Credit Allocation
    facility_name: Mapped[str] = mapped_column(String(255), index=True)
    
    # Financials
    allocation_amount_usd: Mapped[float] = mapped_column(Float, index=True)  # Federal debt or tax credit amount
    total_project_capex_usd: Mapped[Optional[float]] = mapped_column(Float)
    leverage_multiple: Mapped[Optional[float]] = mapped_column(Float)
    
    # Facility Location
    facility_city: Mapped[Optional[str]] = mapped_column(String(128))
    facility_state: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    energy_community_qualified: Mapped[bool] = mapped_column(Boolean, default=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    
    # Technology & Impact
    technology_vertical: Mapped[str] = mapped_column(String(128), index=True)
    annual_ghg_avoidance_metric_tons: Mapped[Optional[float]] = mapped_column(Float)
    permanent_jobs_created: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Milestone Status
    status: Mapped[str] = mapped_column(String(64), default="Allocated", index=True)  # Conditional Commitment, Financial Close, Allocated, Operational
    announcement_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    financial_close_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Provenance
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipient = relationship("Recipient", backref="scaleup_allocations")
    organization = relationship("Organization", backref="scaleup_allocations")
