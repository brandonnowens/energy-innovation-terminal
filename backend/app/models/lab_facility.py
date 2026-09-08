"""National Laboratory User Facilities & Testbeds Database Models."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    DateTime, Float, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class NationalLabFacility(Base):
    """DOE National Lab User Facilities, Specialized Testbeds, and Scientific Instruments."""

    __tablename__ = "national_lab_facilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lab_name: Mapped[str] = mapped_column(String(64), index=True)  # NREL, ORNL, PNNL, LBNL, INL, SLAC, NETL, ANL, Sandia
    facility_name: Mapped[str] = mapped_column(String(255), index=True)
    facility_slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    facility_type: Mapped[Optional[str]] = mapped_column(String(64), index=True)  # User Facility, Testbed, Supercomputing, Pilot Line, Characterization
    summary: Mapped[str] = mapped_column(Text)
    
    # Detailed Catalogs
    capabilities_json: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of test capabilities
    instruments_catalog_json: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of specific hardware specs
    primary_sectors_json: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of sector keys
    
    # TRL & Access
    trl_focus_min: Mapped[int] = mapped_column(Integer, default=2)
    trl_focus_max: Mapped[int] = mapped_column(Integer, default=7)
    access_mechanisms_json: Mapped[Optional[str]] = mapped_column(Text)  # ['User Call', 'CRADA', 'SPP', 'Technical Voucher']
    proposal_deadline_cycles: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Liaison & Contact
    lab_liaison_contact_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"))
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    official_url: Mapped[Optional[str]] = mapped_column(Text)
    
    # Location
    city: Mapped[Optional[str]] = mapped_column(String(128))
    state: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    liaison_contact = relationship("Contact", backref="managed_lab_facilities")
    technology_links = relationship("FacilityTechnologyLink", back_populates="facility", cascade="all, delete-orphan")


class FacilityTechnologyLink(Base):
    """Junction linking National Lab Facilities to Core Technology Taxonomies."""

    __tablename__ = "facility_technology_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    facility_id: Mapped[int] = mapped_column(Integer, ForeignKey("national_lab_facilities.id", ondelete="CASCADE"), index=True)
    technology_id: Mapped[str] = mapped_column(String(128), ForeignKey("technologies.id", ondelete="CASCADE"), index=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0)
    derisking_role: Mapped[Optional[str]] = mapped_column(String(255))  # e.g. "Megawatt-scale inverter grid fault simulation"

    facility = relationship("NationalLabFacility", back_populates="technology_links")
    technology = relationship("Technology", backref="lab_facility_links")
