"""State Distributed Energy Resource (DER) Deployments & Cost Benchmarks Model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    DateTime, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class DerMarketDeployment(Base):
    """Real-World DER Installations, Hardware Models, and Installed Cost Benchmarks."""

    __tablename__ = "der_market_deployments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    state_program: Mapped[str] = mapped_column(String(64), index=True)  # NY_SUN, NY_CLEAN_HEAT, CA_SGIP, MASSCEC_PTS
    sector: Mapped[str] = mapped_column(String(32), index=True)  # Residential, Commercial, Community Solar, Industrial
    technology_type: Mapped[str] = mapped_column(String(64), index=True)  # Solar PV, Storage BESS, Heat Pump Air Source, Geothermal Heat Pump
    
    # Hardware Specification
    equipment_manufacturer: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    equipment_model: Mapped[Optional[str]] = mapped_column(String(255))
    inverter_manufacturer: Mapped[Optional[str]] = mapped_column(String(128))
    
    # Entity Linkages
    installer_organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))
    recipient_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("recipients.id", ondelete="SET NULL"))
    
    # Capacity & Financials
    capacity_kw: Mapped[Optional[float]] = mapped_column(Float)
    storage_kwh: Mapped[Optional[float]] = mapped_column(Float)
    total_installed_cost_usd: Mapped[Optional[float]] = mapped_column(Float)
    incentive_paid_usd: Mapped[Optional[float]] = mapped_column(Float)
    cost_per_watt_or_kwh: Mapped[Optional[float]] = mapped_column(Float, index=True)  # $/W for PV or $/kWh for BESS
    
    # Location
    county: Mapped[Optional[str]] = mapped_column(String(128))
    state: Mapped[str] = mapped_column(String(32), index=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(10))
    utility_territory: Mapped[Optional[str]] = mapped_column(String(128))
    
    # Dates & Status
    interconnection_year: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    installed_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(32), default="Completed", index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    installer_organization = relationship("Organization", backref="der_installations")
    recipient = relationship("Recipient", backref="der_installations")
