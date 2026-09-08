"""Opportunity-Organization junction model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class OpportunityOrganization(Base):
    __tablename__ = "opportunity_organizations"

    id = Column(Integer, primary_key=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # funder, administrator, program_office, partner, recipient, awardee
    source_url = Column(String(500))
    effective_from = Column(DateTime)
    effective_to = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization")


Index("ix_opp_org_unique", OpportunityOrganization.opportunity_id, OpportunityOrganization.organization_id, OpportunityOrganization.role, unique=True)
