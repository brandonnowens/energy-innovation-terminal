"""Program and commercialization models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Program(Base):
    """A NYSERDA program (Innovation, commercialization, workforce, etc.)."""

    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(300), unique=True)
    program_type: Mapped[str] = mapped_column(String(50))
    # innovation, commercialization, workforce, market_development, deployment, technical_assistance
    description: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(String(500))
    contact_email: Mapped[Optional[str]] = mapped_column(String(200))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_program: Mapped[Optional[str]] = mapped_column(String(200))
    target_stage: Mapped[Optional[str]] = mapped_column(String(100))  # early-stage, growth, scale-up
    target_applicant: Mapped[Optional[str]] = mapped_column(String(200))
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), index=True)

    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    last_verified_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="programs")

    focus_areas: Mapped[list["ProgramFocusArea"]] = relationship(
        back_populates="program", cascade="all, delete-orphan"
    )


class ProgramFocusArea(Base):
    """A focus area within a program."""

    __tablename__ = "program_focus_areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"), index=True)
    focus_area: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    keywords: Mapped[Optional[str]] = mapped_column(Text)  # Comma-separated keywords

    program: Mapped["Program"] = relationship(back_populates="focus_areas")
