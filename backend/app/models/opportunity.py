"""Opportunity-related database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    and_,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign

from app.database import Base


class Opportunity(Base):
    """A NYSERDA funding opportunity (solicitation)."""

    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    solicitation_number: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(500))
    solicitation_type: Mapped[Optional[str]] = mapped_column(String(255))  # PON, RFP, RFQ, RFI, RFQL
    solicitation_category: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(100), default="open", index=True)  # open, closed, draft
    enrollment_type: Mapped[Optional[str]] = mapped_column(String(255))  # Open Enrollment, Rolling, Due Date / Multi Round
    short_description: Mapped[Optional[str]] = mapped_column(Text)
    total_funding: Mapped[Optional[float]] = mapped_column(Float)
    max_per_award: Mapped[Optional[float]] = mapped_column(Float)
    cost_share_pct: Mapped[Optional[float]] = mapped_column(Float)
    concept_paper_required: Mapped[bool] = mapped_column(Boolean, default=False)
    salesforce_id: Mapped[Optional[str]] = mapped_column(String(255))
    detail_page_url: Mapped[Optional[str]] = mapped_column(String(1000))
    portal_url: Mapped[Optional[str]] = mapped_column(String(1000))
    revision_date: Mapped[Optional[str]] = mapped_column(String(255))
    revision_notes: Mapped[Optional[str]] = mapped_column(Text)
    due_date_display: Mapped[Optional[str]] = mapped_column(Text)  # Raw HTML display string
    manual_submission_only: Mapped[bool] = mapped_column(Boolean, default=False)
    ny_green_bank: Mapped[bool] = mapped_column(Boolean, default=False)

    # Multi-agency support
    agency: Mapped[str] = mapped_column(String(255), default="NYSERDA", index=True)  # e.g. NYSERDA, DOE, ARPA-E, EPA, NSF
    agency_code: Mapped[Optional[str]] = mapped_column(String(255))  # e.g. DOE-EERE, DOE-ARPAE
    jurisdiction: Mapped[str] = mapped_column(String(100), default="state_ny")  # federal, state_ny, state_ca, etc.
    external_id: Mapped[Optional[str]] = mapped_column(String(255))  # Grants.gov ID, SAM.gov ID, etc.

    # Extended fields
    org_type: Mapped[Optional[str]] = mapped_column(String(100), default="government")  # government, philanthropic, nonprofit
    funding_type: Mapped[Optional[str]] = mapped_column(String(255))  # grant, cooperative_agreement, fellowship, prize, loan
    award_min: Mapped[Optional[float]] = mapped_column(Float)
    award_typical: Mapped[Optional[float]] = mapped_column(Float)
    performance_period: Mapped[Optional[str]] = mapped_column(String(255))
    expected_awards: Mapped[Optional[int]] = mapped_column(Integer)
    objectives: Mapped[Optional[str]] = mapped_column(Text)
    allowable_costs: Mapped[Optional[str]] = mapped_column(Text)
    selection_criteria: Mapped[Optional[str]] = mapped_column(Text)
    keywords: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    raw_source_data: Mapped[Optional[str]] = mapped_column(Text)  # JSON blob
    is_historical: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    open_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    close_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    award_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    year: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    target_trl_min: Mapped[Optional[int]] = mapped_column(Integer)
    target_trl_max: Mapped[Optional[int]] = mapped_column(Integer)
    geographic_scope: Mapped[Optional[str]] = mapped_column(String(500))
    data_provenance: Mapped[Optional[str]] = mapped_column(String(255), default="observed")  # observed, archived, inferred, reconstructed

    # Hierarchy and Relationship linkages
    program_id: Mapped[Optional[int]] = mapped_column(ForeignKey("programs.id"), index=True)
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"), index=True)

    # Utility-specific fields
    service_territory: Mapped[Optional[str]] = mapped_column(String(500))  # e.g. "ConEd_NYC_Westchester", "NatGrid_Upstate"
    utility_program_type: Mapped[Optional[str]] = mapped_column(String(255))  # NWA, DLM, Innovation_RFP, Pilot, etc.
    procurement_portal_url: Mapped[Optional[str]] = mapped_column(String(1000))  # PowerAdvocate, Ariba, Piclo links
    vendor_registration_required: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_utility: Mapped[Optional[str]] = mapped_column(String(500))  # For subsidiaries (O&R -> Con Edison)

    # Proprietary LLM & Propensity Matching Fields
    eligible_applicant_types: Mapped[Optional[str]] = mapped_column(Text)  # JSON array: ["startup", "for-profit", "university", "consortium"]
    eligible_technology_areas: Mapped[Optional[str]] = mapped_column(Text)  # JSON array: ["Energy Storage", "Grid Modernization", ...]
    eligible_sectors: Mapped[Optional[str]] = mapped_column(Text)  # JSON array: ["Electric Power", "Commercial", "Industrial"]
    eligible_activity_types: Mapped[Optional[str]] = mapped_column(Text)  # JSON array: ["Demonstration & Pilot", "Applied R&D"]
    project_cost_min: Mapped[Optional[float]] = mapped_column(Float)  # Minimum viable project scale
    project_cost_max: Mapped[Optional[float]] = mapped_column(Float)  # Maximum viable project scale
    cost_share_mandatory: Mapped[bool] = mapped_column(Boolean, default=False)
    statutory_mandates: Mapped[Optional[str]] = mapped_column(Text)  # JSON array: ["NY CLCPA § 66-p", "IRA 48E", "Justice40"]
    priority_problem_statements: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of specific challenges
    scoring_rubric_weights: Mapped[Optional[str]] = mapped_column(Text)  # JSON blob: {"technical_merit": 35, "market_impact": 25, ...}
    proposal_requirements_summary: Mapped[Optional[str]] = mapped_column(Text)  # Summary of submission packages & requirements
    teaming_partner_types_sought: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of recommended partner profiles
    disadvantaged_community_priority: Mapped[bool] = mapped_column(Boolean, default=False)  # Justice40 / DAC scoring preference

    # Provenance & Tracking
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    source_name: Mapped[Optional[str]] = mapped_column(String(255))
    content_hash: Mapped[Optional[str]] = mapped_column(String(128))
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_verified_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Aggregates
    total_awarded: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    award_count_actual: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    funding_provenance: Mapped[Optional[str]] = mapped_column(String(255), default="observed")


    # Relationships
    program: Mapped[Optional["Program"]] = relationship("Program")
    organization: Mapped[Optional["Organization"]] = relationship("Organization")
    field_provenances = relationship(
        "FieldProvenance",
        primaryjoin="and_(foreign(FieldProvenance.entity_id) == Opportunity.id, FieldProvenance.entity_type == 'opportunity')",
        viewonly=True,
    )
    snapshots = relationship(
        "SourceSnapshot",
        primaryjoin="foreign(SourceSnapshot.source_url) == Opportunity.source_url",
        viewonly=True,
    )
    rounds: Mapped[list["OpportunityRound"]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")
    contacts: Mapped[list["OpportunityContact"]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")
    documents: Mapped[list["OpportunityDocument"]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")
    eligibility_rules: Mapped[list["EligibilityRule"]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")
    categories: Mapped[list["OpportunityCategory"]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")
    restrictions: Mapped[list["OpportunityRestriction"]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")
    awards: Mapped[list["Award"]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")
    results: Mapped[list["OpportunityResult"]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")
    success_stories: Mapped[list["SuccessStory"]] = relationship(back_populates="opportunity", cascade="all, delete-orphan")
    benchmark: Mapped[Optional["ResultBenchmark"]] = relationship(back_populates="opportunity", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Opportunity {self.solicitation_number}: {self.name}>"


class OpportunityRound(Base):
    """A submission round within an opportunity."""

    __tablename__ = "opportunity_rounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    round_number: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))  # Open, Closed, Draft
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    concept_paper_due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    opportunity: Mapped["Opportunity"] = relationship(back_populates="rounds")


class OpportunityContact(Base):
    """A contact person for an opportunity."""

    __tablename__ = "opportunity_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    name: Mapped[Optional[str]] = mapped_column(String(200))
    email: Mapped[Optional[str]] = mapped_column(String(200))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    sequence: Mapped[Optional[str]] = mapped_column(String(10))

    opportunity: Mapped["Opportunity"] = relationship(back_populates="contacts")


class OpportunityDocument(Base):
    """A document associated with an opportunity."""

    __tablename__ = "opportunity_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    document_name: Mapped[str] = mapped_column(String(500))
    document_url: Mapped[str] = mapped_column(String(500))
    document_sequence: Mapped[Optional[str]] = mapped_column(String(10))
    local_path: Mapped[Optional[str]] = mapped_column(String(500))
    content_hash: Mapped[Optional[str]] = mapped_column(String(64))
    extracted_text: Mapped[Optional[str]] = mapped_column(Text)
    downloaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    opportunity: Mapped["Opportunity"] = relationship(back_populates="documents")


class OpportunityCategory(Base):
    """Categorization/tagging for an opportunity."""

    __tablename__ = "opportunity_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    category_type: Mapped[str] = mapped_column(String(50), index=True)  # technology, activity, sector, applicant
    category_value: Mapped[str] = mapped_column(String(200), index=True)
    source: Mapped[Optional[str]] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    opportunity: Mapped["Opportunity"] = relationship(back_populates="categories")


class EligibilityRule(Base):
    """An eligibility rule for an opportunity."""

    __tablename__ = "eligibility_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    rule_type: Mapped[str] = mapped_column(String(50), index=True)
    # geography, applicant, technology, trl, cost_share, activity, partner, deadline, exclusion, host
    rule_key: Mapped[str] = mapped_column(String(100))  # e.g., "state", "min_trl"
    rule_value: Mapped[str] = mapped_column(String(500))  # e.g., "NY", "4"
    rule_operator: Mapped[str] = mapped_column(String(20), default="equals")  # equals, in, gte, lte, not, contains
    is_hard_requirement: Mapped[bool] = mapped_column(Boolean, default=True)
    source: Mapped[Optional[str]] = mapped_column(String(200))
    source_text: Mapped[Optional[str]] = mapped_column(Text)  # Supporting quote
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    opportunity: Mapped["Opportunity"] = relationship(back_populates="eligibility_rules")


class OpportunityRestriction(Base):
    """A known restriction or limitation on a funding opportunity.

    Restrictions describe what applicants CANNOT do, what is excluded,
    or what conditions/limitations apply — distinct from eligibility rules
    which describe who CAN apply.

    Categories:
      - applicant: entity type exclusions (e.g., 'No for-profit entities')
      - geographic: location restrictions (e.g., 'Project must be in NY')
      - technology: excluded technologies or TRL limits
      - use_of_funds: prohibited expenditures (e.g., 'No construction costs')
      - ip: intellectual property / data rights requirements
      - cost_share: mandatory cost-sharing requirements
      - time: performance period or expenditure deadlines
      - conflict_of_interest: COI restrictions
      - prior_awards: limits on prior/concurrent awards
      - lobbying: anti-lobbying restrictions
      - procurement: procurement / Buy American / domestic content
      - reporting: mandatory reporting obligations
      - environmental: NEPA or environmental review requirements
      - other: general restrictions not fitting other categories
    """

    __tablename__ = "opportunity_restrictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(
        ForeignKey("opportunities.id", ondelete="CASCADE"), index=True
    )
    category: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[Optional[str]] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(
        String(20), default="hard"
    )  # hard (disqualifying), soft (preference), info (advisory)
    source: Mapped[Optional[str]] = mapped_column(String(200))
    source_text: Mapped[Optional[str]] = mapped_column(Text)  # verbatim quote from solicitation
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    data_provenance: Mapped[str] = mapped_column(String(50), default="observed")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    opportunity: Mapped["Opportunity"] = relationship(back_populates="restrictions")


