"""Contact and opportunity-contact junction models."""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    name_first = Column(String(200))
    name_last = Column(String(200))
    name_display = Column(String(400), nullable=False)
    title = Column(String(300))
    department = Column(String(300))
    role_type = Column(String(50), index=True)  # program_officer, pi, technical_expert, director, solicitation_lead, institutional_gateway, utility_lead
    email = Column(String(300))
    phone = Column(String(50))
    source_url = Column(String(500))
    source_document = Column(String(500))
    retrieval_date = Column(DateTime)
    effective_from = Column(DateTime)
    effective_to = Column(DateTime)
    verification_status = Column(String(30), default="source_reported")  # verified, source_reported, stale, unverified
    confidence = Column(Float, default=0.8)
    data_provenance = Column(String(100), default="observed")
    is_current = Column(Boolean, default=True)

    # Enhanced directory & physical mailing address fields
    institution_name = Column(String(500), index=True)
    technology_area = Column(String(200), index=True)
    sector = Column(String(200), index=True)
    fuel_type = Column(String(200))
    entity_contact_url = Column(String(500))
    address_line1 = Column(String(300))
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(200))
    state = Column(String(100), index=True)
    postal_code = Column(String(30), index=True)
    country = Column(String(100), default="US")
    formatted_address = Column(String(500))
    address_verification_status = Column(String(50), default="verified")
    awards_count = Column(Integer, default=0)
    total_funding = Column(Float, default=0.0)
    keywords = Column(Text)

    # Email Verification & Deliverability
    email_status = Column(String(50), default="unverified", index=True)  # verified_valid, syntax_valid, gateway_required, invalid_format
    email_deliverable = Column(Boolean, default=False, index=True)
    email_domain = Column(String(200), index=True)
    email_score = Column(Float, default=0.0)
    email_verified_at = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="contacts")
    opportunity_links = relationship("OpportunityContactLink", back_populates="contact")


class OpportunityContactLink(Base):
    """Junction between opportunities and contacts (distinct from existing OpportunityContact)."""
    __tablename__ = "opportunity_contact_links"

    id = Column(Integer, primary_key=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    role = Column(String(50))  # technical, program, contracting, pi
    source_url = Column(String(500))
    effective_from = Column(DateTime)
    effective_to = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    contact = relationship("Contact", back_populates="opportunity_links")


Index("ix_contact_name", Contact.name_last, Contact.name_first)
Index("ix_contact_email", Contact.email)
Index("ix_contact_display", Contact.name_display)
Index("ix_opp_contact_link", OpportunityContactLink.opportunity_id, OpportunityContactLink.contact_id, unique=True)
