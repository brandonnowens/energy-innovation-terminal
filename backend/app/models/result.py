"""Results, Outcomes, Success Stories, and Benchmark database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OpportunityResult(Base):
    """An individual verified outcome metric or research output from an opportunity or award.
    
    Contains both the raw reported metric and the canonical standardized metric for
    apples-to-apples comparability across opportunities and agencies.
    """

    __tablename__ = "opportunity_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    award_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("awards.id", ondelete="SET NULL"), index=True)
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), index=True)

    # Entity / Recipient context
    recipient_name: Mapped[Optional[str]] = mapped_column(String(500), index=True)
    agency: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, index=True)

    # Metric Categorization & Canonical Standard
    # Categories: environmental_ghg, energy_generation, energy_efficiency, commercialization,
    #             capital_leverage, economic_jobs, intellectual_property, trl_advancement
    metric_category: Mapped[str] = mapped_column(String(100), index=True)
    
    # Canonical key (e.g., ghg_avoided_annual_mt, private_capital_leveraged_usd, jobs_created_direct, patents_issued)
    canonical_metric_name: Mapped[str] = mapped_column(String(150), index=True)
    canonical_unit: Mapped[str] = mapped_column(String(50))  # MT_CO2e_yr, USD, FTE_jobs, MWh_yr, patents, products, TRL_steps
    canonical_value: Mapped[float] = mapped_column(Float, index=True)

    # Original Raw Reported Metric
    reported_metric_name: Mapped[Optional[str]] = mapped_column(String(255))
    reported_unit: Mapped[Optional[str]] = mapped_column(String(100))
    raw_metric_value_str: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Context & Timeframe
    timeframe_years: Mapped[Optional[float]] = mapped_column(Float)  # Performance timeframe in years (e.g. 1.0, 3.0, lifetime)
    is_projected_or_actual: Mapped[str] = mapped_column(String(20), default="actual")  # actual, verified_post_install, projected_ex_ante
    
    # Provenance & Citation
    # Provenance tiers: agency_verified, statutory_filing, osti_technical_report, curated_case_study, model_standardized
    data_provenance: Mapped[str] = mapped_column(String(50), default="agency_verified")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    source_artifact_title: Mapped[Optional[str]] = mapped_column(String(500))
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    source_artifact_type: Mapped[Optional[str]] = mapped_column(String(50))  # pdf_report, regulatory_filing, technical_deliverable, case_study
    notes_and_context: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    opportunity: Mapped[Optional["Opportunity"]] = relationship(back_populates="results")
    award: Mapped[Optional["Award"]] = relationship("Award")

    def __repr__(self):
        return f"<OpportunityResult {self.id}: {self.canonical_metric_name}={self.canonical_value} {self.canonical_unit}>"


class SuccessStory(Base):
    """Structured impact case study and organizational success story linked to opportunities."""

    __tablename__ = "success_stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    award_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("awards.id", ondelete="SET NULL"), index=True)
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), index=True)

    recipient_name: Mapped[str] = mapped_column(String(500), index=True)
    agency: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(Text)
    
    # Structured Case Study Sections
    challenge: Mapped[Optional[str]] = mapped_column(Text)
    solution_technology: Mapped[Optional[str]] = mapped_column(Text)
    outcome_impact: Mapped[Optional[str]] = mapped_column(Text)
    customer_market: Mapped[Optional[str]] = mapped_column(Text)
    
    # Quotes & Stakeholder Voice
    quote_text: Mapped[Optional[str]] = mapped_column(Text)
    quote_author: Mapped[Optional[str]] = mapped_column(String(300))
    
    # Metadata & Categorization
    technology_area: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    trl_advancement: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "TRL 3 -> TRL 7"
    featured_metrics_json: Mapped[Optional[dict]] = mapped_column(JSON)  # Key highlight numbers
    
    # Artifact Linkages
    artifact_url: Mapped[Optional[str]] = mapped_column(String(1000))
    artifact_title: Mapped[Optional[str]] = mapped_column(String(500))
    image_url: Mapped[Optional[str]] = mapped_column(String(1000))
    publication_date: Mapped[Optional[str]] = mapped_column(String(50))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    opportunity: Mapped[Optional["Opportunity"]] = relationship(back_populates="success_stories")
    award: Mapped[Optional["Award"]] = relationship("Award")

    def __repr__(self):
        return f"<SuccessStory {self.id}: {self.title}>"


class ResultBenchmark(Base):
    """Apples-to-apples opportunity & program benchmark scorecard with normalized efficiency ratios."""

    __tablename__ = "result_benchmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), unique=True, index=True)
    
    solicitation_number: Mapped[str] = mapped_column(String(255), index=True)
    opportunity_name: Mapped[str] = mapped_column(String(500))
    agency: Mapped[str] = mapped_column(String(100), index=True)
    technology_area: Mapped[Optional[str]] = mapped_column(String(200), index=True)

    # Core Quantities
    total_awards_tracked: Mapped[int] = mapped_column(Integer, default=0)
    total_awarded_usd: Mapped[float] = mapped_column(Float, default=0.0)
    total_leveraged_capital_usd: Mapped[float] = mapped_column(Float, default=0.0)
    total_ghg_avoided_annual_mt: Mapped[float] = mapped_column(Float, default=0.0)
    total_clean_energy_mwh_yr: Mapped[float] = mapped_column(Float, default=0.0)
    total_jobs_created: Mapped[float] = mapped_column(Float, default=0.0)
    total_patents_issued: Mapped[int] = mapped_column(Integer, default=0)
    total_commercial_products: Mapped[int] = mapped_column(Integer, default=0)
    total_startups_spun_out: Mapped[int] = mapped_column(Integer, default=0)
    
    # Normalized Apples-to-Apples Ratios (Return on Public Grant Dollar)
    leverage_ratio: Mapped[float] = mapped_column(Float, default=0.0)  # Follow-on Private $ / Grant $
    ghg_abatement_per_10k_usd: Mapped[float] = mapped_column(Float, default=0.0)  # Metric tons CO2e avoided / $10k awarded
    jobs_per_million_usd: Mapped[float] = mapped_column(Float, default=0.0)  # FTE Jobs / $1M awarded
    ip_and_product_velocity: Mapped[float] = mapped_column(Float, default=0.0)  # (Patents + Products) / $1M awarded
    commercialization_rate_pct: Mapped[float] = mapped_column(Float, default=0.0)  # % of projects achieving commercial deployment
    avg_trl_gain: Mapped[float] = mapped_column(Float, default=0.0)  # Average TRL increase
    
    # Metadata & Quality
    comparability_index: Mapped[float] = mapped_column(Float, default=1.0)  # 0.0 - 1.0 completeness & comparability score
    last_computed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship(back_populates="benchmark")

    def __repr__(self):
        return f"<ResultBenchmark {self.solicitation_number}: Leverage={self.leverage_ratio:.2f}x>"


class ResultArtifact(Base):
    """Scraped or referenced PDF report, OSTI deliverable, agency filing, or technical document."""

    __tablename__ = "result_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("opportunities.id", ondelete="SET NULL"), index=True)
    award_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("awards.id", ondelete="SET NULL"), index=True)
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), index=True)
    recipient_name: Mapped[Optional[str]] = mapped_column(String(500), index=True)
    
    title: Mapped[str] = mapped_column(String(500))
    artifact_type: Mapped[str] = mapped_column(String(50), index=True)  # evaluation_report, osti_technical_report, case_study, filing, fact_sheet
    agency: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    source_url: Mapped[str] = mapped_column(String(1000))
    doi: Mapped[Optional[str]] = mapped_column(String(200))
    publication_date: Mapped[Optional[str]] = mapped_column(String(50))
    page_count: Mapped[Optional[int]] = mapped_column(Integer)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    key_findings_json: Mapped[Optional[list]] = mapped_column(JSON)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    local_cache_path: Mapped[Optional[str]] = mapped_column(String(500))
    data_provenance: Mapped[str] = mapped_column(String(50), default="agency_verified")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    def __repr__(self):
        return f"<ResultArtifact {self.id}: {self.title}>"


# Import Opportunity and Award at end to avoid circular imports
from app.models.opportunity import Opportunity  # noqa: E402
from app.models.award import Award  # noqa: E402
