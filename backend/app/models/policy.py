"""
SQLAlchemy ORM models for Policy, Regulatory, Codes & Standards Knowledge Base.
Supports safety codes (NFPA, UL, IEEE), federal regulations and tax credits (IRA, EPA, FERC),
state climate statutes (NY CLCPA, CA SB 100, Title 24), and utility interconnection rules.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Index, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


class PolicyStandard(Base):
    """
    Master Policy, Regulatory, Codes & Standards entity.
    Stores federal/state statutes, testing standards, market rules, and tax credit frameworks.
    """
    __tablename__ = "policy_standards"

    id = Column(String(128), primary_key=True, index=True)  # e.g. "nfpa_855_2023", "ferc_order_2023"
    code_identifier = Column(String(150), nullable=False, index=True)  # e.g. "NFPA 855", "FERC Order 2023"
    title = Column(String(500), nullable=False)
    short_title = Column(String(255), nullable=True)
    category = Column(String(128), nullable=False, index=True)  # safety_code, interconnection_rule, tax_incentive, state_statute, emissions_standard
    jurisdiction_level = Column(String(128), nullable=False, index=True)  # federal, state, rto_iso, municipal, international
    jurisdiction_state = Column(String(64), nullable=True, index=True)  # NY, CA, MA, US, PJM, NYISO, etc.
    issuing_org_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(64), default="active", index=True)  # active, proposed, under_revision, superseded
    effective_year = Column(Integer, nullable=True)
    sunset_year = Column(Integer, nullable=True)
    latest_revision = Column(String(255), nullable=True)  # e.g. "2023 Edition", "Rev 4"

    # Plain English & Strategic Syntheses
    executive_summary = Column(Text, nullable=False)
    statutory_intent = Column(Text, nullable=True)
    compliance_mandate = Column(Text, nullable=False)
    commercial_friction_points = Column(Text, nullable=True)  # Siting roadblocks, interconnection backlog, testing cost
    associated_incentives = Column(Text, nullable=True)  # e.g. "$3.00/kg clean H2 production tax credit"
    official_source_url = Column(String(1000), nullable=True)
    
    # Structured JSON metadata
    metadata_json = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    issuing_organization = relationship("Organization", foreign_keys=[issuing_org_id])
    technology_links = relationship("PolicyTechnologyLink", back_populates="policy", cascade="all, delete-orphan")
    fuel_links = relationship("PolicyFuelLink", back_populates="policy", cascade="all, delete-orphan")
    opportunity_links = relationship("PolicyOpportunityLink", back_populates="policy", cascade="all, delete-orphan")
    organization_links = relationship("PolicyOrganizationLink", back_populates="policy", cascade="all, delete-orphan")


class PolicyTechnologyLink(Base):
    """M:N Relational linkage between Policies/Standards and Clean Technologies."""
    __tablename__ = "policy_technology_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(128), ForeignKey("policy_standards.id", ondelete="CASCADE"), nullable=False, index=True)
    technology_id = Column(String(128), ForeignKey("technologies.id", ondelete="CASCADE"), nullable=False, index=True)
    relevance_type = Column(String(128), nullable=False)  # mandatory_testing, safety_siting, market_incentive, interconnection
    compliance_impact = Column(String(64), default="critical_gate", index=True)  # critical_gate, cost_driver, accelerator_tailwind
    impact_summary = Column(Text, nullable=True)  # Explains why this rule specifically matters to this technology
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("policy_id", "technology_id", name="uq_policy_tech"),
    )

    # Relationships
    policy = relationship("PolicyStandard", back_populates="technology_links")
    technology = relationship("Technology")


class PolicyFuelLink(Base):
    """M:N Relational linkage between Policies/Standards and Fuel / Energy Carriers."""
    __tablename__ = "policy_fuel_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(128), ForeignKey("policy_standards.id", ondelete="CASCADE"), nullable=False, index=True)
    fuel_vector = Column(String(128), nullable=False, index=True)  # green_hydrogen, saf, rng, ammonia, clean_power
    lifecycle_ci_threshold = Column(String(128), nullable=True)  # e.g. "< 0.45 kg CO2e/kg H2"
    impact_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("policy_id", "fuel_vector", name="uq_policy_fuel"),
    )

    # Relationships
    policy = relationship("PolicyStandard", back_populates="fuel_links")


class PolicyOpportunityLink(Base):
    """M:N Relational linkage between Policies/Standards and Funding Solicitations."""
    __tablename__ = "policy_opportunity_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(128), ForeignKey("policy_standards.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    link_reason = Column(String(128), default="statutory_basis")  # statutory_basis, mandatory_standard, eligibility_criterion
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("policy_id", "opportunity_id", name="uq_policy_opp"),
    )

    # Relationships
    policy = relationship("PolicyStandard", back_populates="opportunity_links")
    opportunity = relationship("Opportunity")


class PolicyOrganizationLink(Base):
    """M:N Relational linkage between Policies/Standards and affected Organizations / Regulators."""
    __tablename__ = "policy_organization_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(128), ForeignKey("policy_standards.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type = Column(String(128), default="regulated_entity")  # issuing_regulator, compliant_developer, utility_operator
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("policy_id", "organization_id", "relation_type", name="uq_policy_org_rel"),
    )

    # Relationships
    policy = relationship("PolicyStandard", back_populates="organization_links")
    organization = relationship("Organization")


class RegulatoryProceeding(Base):
    """
    Master Regulatory & Public Utility Commission (PUC/PSC/FERC) Proceeding entity.
    Tracks active dockets, rate cases, large load inquiries, and market rulemakings.
    """
    __tablename__ = "regulatory_proceedings"

    id = Column(String(128), primary_key=True, index=True)  # e.g. "ny_psc_24_e_0314_large_load"
    docket_number = Column(String(150), nullable=False, index=True)  # e.g. "Case 24-E-0314", "Docket RM22-14"
    commission = Column(String(128), nullable=False, index=True)  # e.g. "NYPSC", "CPUC", "PUCT", "FERC", "Mass DPU", "ICC"
    jurisdiction_level = Column(String(64), default="state", index=True)  # state, federal, rto_iso
    jurisdiction_state = Column(String(64), nullable=True, index=True)  # NY, CA, TX, US, MA, IL
    title = Column(String(500), nullable=False)
    short_title = Column(String(255), nullable=True)
    topic_category = Column(String(128), nullable=False, index=True)  # large_load_interconnection, storage_procurement, thermal_networks, interconnection_reform, vpp_rate_design, transmission_planning, clean_firm_procurement
    status = Column(String(64), default="active", index=True)  # active, staff_whitepaper, public_comment, order_issued, implementation
    
    open_date = Column(DateTime, nullable=True)
    comment_deadline = Column(DateTime, nullable=True)
    expected_order_date = Column(DateTime, nullable=True)

    # Plain English & Strategic Syntheses
    executive_summary = Column(Text, nullable=False)
    innovation_impact = Column(Text, nullable=False)  # Specific direct implications for energy tech & startups
    commercial_tailwinds = Column(Text, nullable=True)  # Market growth accelerators
    commercial_friction_points = Column(Text, nullable=True)  # Siting bottlenecks, queue delays, standby fees
    key_filings_summary = Column(Text, nullable=True)  # Key intervenor and staff proposals
    official_docket_url = Column(String(1000), nullable=True)  # Link to NY DMM, CPUC e-filing, FERC eLibrary
    
    # Structured JSON metadata
    metadata_json = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    technology_links = relationship("ProceedingTechnologyLink", back_populates="proceeding", cascade="all, delete-orphan")
    organization_links = relationship("ProceedingOrganizationLink", back_populates="proceeding", cascade="all, delete-orphan")
    opportunity_links = relationship("ProceedingOpportunityLink", back_populates="proceeding", cascade="all, delete-orphan")


class ProceedingTechnologyLink(Base):
    """M:N Relational linkage between Regulatory Proceedings and Clean Technologies."""
    __tablename__ = "proceeding_technology_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proceeding_id = Column(String(128), ForeignKey("regulatory_proceedings.id", ondelete="CASCADE"), nullable=False, index=True)
    technology_id = Column(String(128), ForeignKey("technologies.id", ondelete="CASCADE"), nullable=False, index=True)
    impact_level = Column(String(64), default="high_catalyst", index=True)  # high_catalyst, critical_gate, cost_driver, market_expansion
    commercial_vector = Column(String(128), nullable=True)  # direct_procurement, interconnection_access, tariff_revenue, siting_clarity
    impact_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("proceeding_id", "technology_id", name="uq_proceeding_tech"),
    )

    # Relationships
    proceeding = relationship("RegulatoryProceeding", back_populates="technology_links")
    technology = relationship("Technology")


class ProceedingOrganizationLink(Base):
    """M:N Relational linkage between Regulatory Proceedings and affected Organizations / Utilities."""
    __tablename__ = "proceeding_organization_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proceeding_id = Column(String(128), ForeignKey("regulatory_proceedings.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(128), default="affected_utility")  # lead_commission, affected_utility, intervenor, rto_operator
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("proceeding_id", "organization_id", "role", name="uq_proceeding_org_role"),
    )

    # Relationships
    proceeding = relationship("RegulatoryProceeding", back_populates="organization_links")
    organization = relationship("Organization")


class ProceedingOpportunityLink(Base):
    """M:N Relational linkage between Regulatory Proceedings and Funding Solicitations."""
    __tablename__ = "proceeding_opportunity_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proceeding_id = Column(String(128), ForeignKey("regulatory_proceedings.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    link_reason = Column(String(128), default="statutory_authorization")  # statutory_authorization, program_creation, tariff_pilot
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("proceeding_id", "opportunity_id", name="uq_proceeding_opp"),
    )

    # Relationships
    proceeding = relationship("RegulatoryProceeding", back_populates="opportunity_links")
    opportunity = relationship("Opportunity")

