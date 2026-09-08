"""
SQLAlchemy ORM models for Energy Innovation News Items and explicit polymorphic database linkages.
Persists cumulative clean tech news intelligence in PostgreSQL with strict deduplication.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Index, func
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base


class NewsItem(Base):
    """
    Daily Energy Innovation News Item ingested from federal, state, utility, and clean tech media feeds.
    Strictly filtered for relevance to energy innovation technologies, funding, and database entities.
    Automatically de-duplicated via canonical URL hashing and title content fingerprinting.
    """
    __tablename__ = "news_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    canonical_url: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    content_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    raw_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # LLM-Generated Executive Synthesis
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[str] = mapped_column(
        String(50),
        default="neutral",
        index=True
    )  # breakthrough, commercial, regulatory, grant_awarded, funding_round, milestone, neutral
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0)
    category_tag: Mapped[str] = mapped_column(
        String(100),
        default="Clean Energy Innovation",
        index=True
    )  # Long-Duration Storage, Grid Modernization, Clean Hydrogen, Nuclear SMR, Industrial Heat, FOA & Grants, Policy & Codes, etc.
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Explicit Database Linkages (Polymorphic one-to-many relationship)
    links: Mapped[List["NewsItemLink"]] = relationship(
        "NewsItemLink",
        back_populates="news_item",
        cascade="all, delete-orphan",
        order_by="desc(NewsItemLink.confidence_score)"
    )

    def __repr__(self):
        return f"<NewsItem {self.id}: [{self.source_name}] {self.title[:40]}>"


class NewsItemLink(Base):
    """
    Explicit relational link connecting a news item to a specific database element in PostgreSQL.
    Supported element types:
      - 'opportunity': Funding solicitation / PON / FOA
      - 'organization': Funder, agency, utility, commercial developer
      - 'program': Funding portfolio / initiative
      - 'award': Specific grant disbursement / project comp
      - 'technology': Master clean tech taxonomy / subsystem
      - 'policy': Statutory standard / code / mandate (e.g. NFPA 855, FERC Order 1920)
      - 'proceeding': Regulatory PUC/FERC docket
      - 'sector': Macro end-use vertical (Grid, Buildings, Transport, Industry)
      - 'recipient': Awardee startup, scale-up, national lab, university
    """
    __tablename__ = "news_item_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    element_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    element_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    element_title: Mapped[str] = mapped_column(String(500), nullable=False)
    element_url_path: Mapped[str] = mapped_column(String(500), nullable=False)
    link_rationale: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationship back to parent news item
    news_item: Mapped["NewsItem"] = relationship("NewsItem", back_populates="links")

    def __repr__(self):
        return f"<NewsItemLink {self.id}: News #{self.news_item_id} -> {self.element_type}:{self.element_id}>"
