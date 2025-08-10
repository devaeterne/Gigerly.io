# app/models/project.py
from __future__ import annotations
import enum

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Boolean, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ENUM as PGEnum

from .base import Base, IDMixin, TimestampMixin, ReprMixin

# ENUM sınıfları (lowercase değerler)
class ProjectStatus(enum.Enum):
    draft = "draft"
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    closed = "closed"

class ProjectBudgetType(enum.Enum):
    fixed = "fixed"
    hourly = "hourly"

class ProjectComplexity(enum.Enum):
    simple = "simple"
    moderate = "moderate"
    complex = "complex"

class Project(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "projects"

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    # PG ENUM'ları mevcut isimlerle eşleştir (create_type=False -> mevcut tipleri kullan)
    budget_type = Column(
        PGEnum(ProjectBudgetType, name="projectbudgettype", create_type=False, validate_strings=True),
        nullable=False,
        server_default=ProjectBudgetType.fixed.value,
    )

    currency = Column(String(3), nullable=False, server_default="USD")

    customer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    complexity = Column(
        PGEnum(ProjectComplexity, name="projectcomplexity", create_type=False, validate_strings=True),
        nullable=True,
    )

    estimated_duration = Column(Integer, nullable=True)
    deadline = Column(Date, nullable=True)

    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)

    is_featured = Column(Boolean, nullable=False, server_default="false")
    allows_proposals = Column(Boolean, nullable=False, server_default="true")

    # 🔒 NULL'ü engelle + sağlam server default
    max_proposals = Column(Integer, nullable=False, server_default="50", default=50)

    # JSONB default'ları PG tarafında doğru vermek gerekir
    tags = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"), default=list)
    attachments = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"), default=list)

    status = Column(
        PGEnum(ProjectStatus, name="projectstatus", create_type=False, validate_strings=True),
        nullable=False,
        server_default=ProjectStatus.open.value,
    )

    slug = Column(String(255), nullable=True)
    view_count = Column(Integer, nullable=False, server_default="0", default=0)
    proposal_count = Column(Integer, nullable=False, server_default="0", default=0)

    # İlişkiler (User modelinde back_populates = "projects_posted" olmalı)
    customer = relationship("User", back_populates="projects_posted", foreign_keys=[customer_id])
    proposals = relationship("Proposal", back_populates="project", cascade="all, delete-orphan")
