# api/app/models/project.py
from __future__ import annotations

import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from .base import Base, IDMixin, TimestampMixin, ReprMixin

# ========== ENUMS ==========
class ProjectStatus(enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS" 
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    CLOSED = "CLOSED"

class ProjectBudgetType(enum.Enum):
    FIXED = "FIXED"
    HOURLY = "HOURLY"

class ProjectComplexity(enum.Enum):
    SIMPLE = "SIMPLE"
    MODERATE = "MODERATE"
    COMPLEX = "COMPLEX"

# ========== MODELS ==========

class Project(Base, IDMixin, TimestampMixin, ReprMixin):
    # DÜZELTME: Migration'da 'projects' (çoğul) olarak yaratılmış
    __tablename__ = "projects"  # ✅ 'project' yerine 'projects'

    # --- core fields ---
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    # budget / currency
    budget_type = Column(String(20), nullable=False, server_default="FIXED")
    currency = Column(String(3), nullable=False, server_default="USD")

    # müşteri -> users.id
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # opsiyonel alanlar
    complexity = Column(String(20), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # days
    deadline = Column(Date, nullable=True)
    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)
    is_featured = Column(Boolean, nullable=False, server_default="false")
    allows_proposals = Column(Boolean, nullable=False, server_default="true")
    max_proposals = Column(Integer, nullable=False, server_default="50")
    tags = Column(JSONB, nullable=False, server_default="[]")
    attachments = Column(JSONB, nullable=False, server_default="[]")
    status = Column(String(20), nullable=False, server_default="OPEN")
    slug = Column(String(255), nullable=True)
    view_count = Column(Integer, nullable=False, server_default="0")
    proposal_count = Column(Integer, nullable=False, server_default="0")

    # --- relationships ---
    # USER tarafındaki 'projects_posted' ile eşleşiyor
    customer = relationship(
        "User",
        back_populates="projects_posted",
        foreign_keys=[customer_id],
    )

    proposals = relationship(
        "Proposal",
        back_populates="project",
        cascade="all, delete-orphan",
    )