from __future__ import annotations

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, IDMixin, TimestampMixin, ReprMixin

class User(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
    )

    # --- fields ---
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=True)
    google_sub = Column(String(255), nullable=True)
    google_email_verified = Column(Boolean, server_default="false", nullable=False)

    role = Column(String(50), nullable=False, server_default="CUSTOMER")
    status = Column(String(50), nullable=False, server_default="ACTIVE")

    is_active = Column(Boolean, nullable=False, server_default="true")
    is_verified = Column(Boolean, nullable=False, server_default="false")

    last_login_at = Column(DateTime(timezone=True), nullable=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)

    # --- relationships ---
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # ÖNEMLİ: Project tarafında 'customer' isimli ilişki var.
    projects_posted = relationship(
        "Project",
        back_populates="customer",
        foreign_keys="Project.customer_id",
        cascade="all, delete-orphan",
    )

    # Proposal tarafında 'freelancer' ilişki adı var.
    proposals = relationship(
        "Proposal",
        back_populates="freelancer",
        foreign_keys="Proposal.freelancer_id",
        cascade="all, delete-orphan",
    )
