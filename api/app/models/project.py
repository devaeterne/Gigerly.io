# app/models/project.py
from __future__ import annotations
import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Boolean, Numeric, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM, JSONB,JSON
from .base import Base, IDMixin, TimestampMixin, ReprMixin

# DB'deki enum değerleri lowercase olduğu için böyle tanımlıyoruz:
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

    # Zorunlular
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="NO ACTION"), nullable=False)

    # ENUM alanlar — mevcut PG enum tiplerine bağlanıyoruz (create_type=False)
    budget_type = Column(
        ENUM(ProjectBudgetType, name="projectbudgettype", create_type=False),
        nullable=False,
        server_default=text("'fixed'::projectbudgettype"),
    )
    status = Column(
        ENUM(ProjectStatus, name="projectstatus", create_type=False),
        nullable=False,
        server_default=text("'open'::projectstatus"),
    )
    complexity = Column(
        ENUM(ProjectComplexity, name="projectcomplexity", create_type=False),
        nullable=True,
    )

    # Sayısal alanlar
    budget_min = Column(Numeric(10, 2), nullable=True)
    budget_max = Column(Numeric(10, 2), nullable=True)
    hourly_rate_min = Column(Numeric(8, 2), nullable=True)
    hourly_rate_max = Column(Numeric(8, 2), nullable=True)

    # Diğerleri
    currency = Column(String(3), nullable=False, server_default=text("'USD'::varchar"))
    estimated_duration = Column(Integer, nullable=True)
    deadline = Column(Date, nullable=True)

    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)

    required_skills = mapped_column(
        JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb")
    )
    is_featured = Column(Boolean, nullable=False, server_default=text("false"))
    allows_proposals = Column(Boolean, nullable=False, server_default=text("true"))
    max_proposals = Column(Integer, nullable=False, server_default=text("50"))

    # Not: DDL'de kolon tipi JSON, default ise '[]'::jsonb yazıyor.
    # ORM tarafında default'u DB'ye bırakmak en güvenlisi:
    attachments = Column(JSON, nullable=False, server_default=text("'[]'::jsonb"))
    tags = Column(JSON, nullable=False, server_default=text("'[]'::jsonb"))

    slug = Column(String(250), unique=True, nullable=True)
    view_count = Column(Integer, nullable=False, server_default=text("0"))
    proposal_count = Column(Integer, nullable=False, server_default=text("0"))

    # İlişkiler
    customer = relationship(
        "User",
        back_populates="projects_posted",
        foreign_keys=[customer_id],
        lazy="joined",   # response'ta nested user için işimizi kolaylaştırır
    )
    proposals = relationship(
        "Proposal",
        back_populates="project",
        cascade="all, delete-orphan",
    )
