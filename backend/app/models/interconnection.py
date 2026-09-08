"""ISO/RTO Grid Interconnection Queue Projects Database Model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    DateTime, Float, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class InterconnectionQueueProject(Base):
    """Grid Interconnection Queue Project (NYISO, CAISO, PJM, ERCOT, MISO, SPP, ISO-NE)."""

    __tablename__ = "interconnection_queue_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    iso_rto: Mapped[str] = mapped_column(String(32), index=True)  # NYISO, CAISO, PJM, ERCOT, MISO, ISONE, SPP
    queue_id: Mapped[str] = mapped_column(String(64), index=True)
    project_name: Mapped[str] = mapped_column(String(255), index=True)
    developer_raw: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Entity Linkages
    recipient_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("recipients.id", ondelete="SET NULL"), index=True)
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), index=True)
    opportunity_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("opportunities.id", ondelete="SET NULL"), index=True)
    
    # Technical Specs
    technology_type: Mapped[str] = mapped_column(String(64), index=True)  # Storage, Solar+Storage, Geothermal, Offshore Wind, Clean Hydrogen, etc.
    capacity_mw: Mapped[Optional[float]] = mapped_column(Float)
    storage_mwh: Mapped[Optional[float]] = mapped_column(Float)
    
    # Geospatial & Grid POI
    county: Mapped[Optional[str]] = mapped_column(String(128))
    state: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    poi_substation: Mapped[Optional[str]] = mapped_column(String(255))
    utility_territory: Mapped[Optional[str]] = mapped_column(String(128))
    
    # Timeline & Milestones
    queue_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    study_phase: Mapped[Optional[str]] = mapped_column(String(128))  # Cluster Study, System Impact Study, IA Executed, Operational
    estimated_network_upgrade_cost_usd: Mapped[Optional[float]] = mapped_column(Float)
    expected_cod: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)  # active, completed, withdrawn
    
    # Metadata & Provenance
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    last_synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipient = relationship("Recipient", backref="interconnection_projects")
    organization = relationship("Organization", backref="interconnection_projects")
