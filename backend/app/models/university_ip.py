"""University Licensable Clean Tech & Spinout Portals Database Model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    DateTime, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UniversityLicensableTechnology(Base):
    """University Licensable Clean Tech IP (AUTM, MIT TLO, Stanford OTL, UC Berkeley, Cornell CTL)."""

    __tablename__ = "university_licensable_technologies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    university_org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # IP & Innovation Details
    title: Mapped[str] = mapped_column(String(255), index=True)
    abstract: Mapped[str] = mapped_column(Text)
    tech_domain: Mapped[str] = mapped_column(String(128), index=True)
    technology_id: Mapped[Optional[str]] = mapped_column(String(128), ForeignKey("technologies.id", ondelete="SET NULL"), index=True)
    
    # Inventor & Contact Linkage
    lead_inventor_contact_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"))
    inventors_names_json: Mapped[Optional[str]] = mapped_column(Text)
    licensing_contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Patent & Legal Status
    patent_application_number: Mapped[Optional[str]] = mapped_column(String(64))
    licensing_status: Mapped[str] = mapped_column(String(64), default="Available for License", index=True)  # Exclusive, Non-Exclusive, Optioned
    trl_estimated: Mapped[int] = mapped_column(Integer, default=3)
    
    # Provenance
    portal_url: Mapped[Optional[str]] = mapped_column(Text)
    case_number: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    university = relationship("Organization", backref="licensable_technologies")
    lead_inventor = relationship("Contact", backref="licensable_inventions")
    technology = relationship("Technology", backref="university_licensable_links")
