"""Organization and related entity models."""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON,
    Index,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False, index=True)
    aliases_json = Column(JSON, default=list)  # ["DOE", "Dept of Energy"]
    org_type = Column(String(50), index=True)  # funder, program_office, lab, company, university, nonprofit
    parent_org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    website = Column(String(500))
    domain = Column(String(200))
    address_line = Column(String(500))
    city = Column(String(200))
    state = Column(String(100))
    zip_code = Column(String(20))
    country = Column(String(100), default="US")
    geographic_scope = Column(String(100))  # national, state, regional, local
    description = Column(Text)
    logo_url = Column(String(500))
    founded_year = Column(Integer)
    source_url = Column(String(500))
    data_provenance = Column(String(50), default="observed")  # observed, inferred, reported
    confidence = Column(Float, default=1.0)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("Organization", remote_side="Organization.id", backref="subsidiaries")
    aliases = relationship("OrganizationAlias", back_populates="organization", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="organization", cascade="all, delete-orphan")
    programs = relationship("Program", back_populates="organization")
    opportunity_links = relationship("OpportunityOrganization", back_populates="organization")


class OrganizationAlias(Base):
    __tablename__ = "organization_aliases"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    alias_name = Column(String(500), nullable=False)
    alias_type = Column(String(50))  # legal, dba, former, abbreviation, acronym
    effective_from = Column(DateTime)
    effective_to = Column(DateTime)
    source_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="aliases")


Index("ix_org_name_type", Organization.name, Organization.org_type)
Index("ix_org_domain", Organization.domain)
