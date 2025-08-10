# api/app/models/user.py
from __future__ import annotations

import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Enum
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, IDMixin, TimestampMixin, ReprMixin

# ========== ENUMS ==========
# Migration'daki enum değerleriyle tam uyumlu olmalı
class UserRole(enum.Enum):
    admin = "admin"           # Migration: 'admin'
    moderator = "moderator"   # Migration: 'moderator' 
    helpdesk = "helpdesk"     # Migration: 'helpdesk'
    freelancer = "freelancer" # Migration: 'freelancer'
    customer = "customer"     # Migration: 'customer'

class UserStatus(enum.Enum):
    active = "active"         # Migration: 'active'
    inactive = "inactive"     # Migration: 'inactive'
    suspended = "suspended"   # Migration: 'suspended'
    banned = "banned"         # Migration: 'banned'

# ========== MODELS ==========

class User(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
    )

    # --- fields ---
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=True)
    google_sub = Column(String(255), nullable=True)
    google_email_verified = Column(Boolean, nullable=True)  # Migration'da nullable=True

    # ✅ ENUM türlerini kullan (String değil!)
    role = Column(Enum(UserRole), nullable=False, server_default="customer")
    status = Column(Enum(UserStatus), nullable=False, server_default="active")

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

    projects_posted = relationship(
        "Project",
        back_populates="customer",
        foreign_keys="Project.customer_id",
        cascade="all, delete-orphan",
    )

    proposals = relationship(
        "Proposal",
        back_populates="freelancer",
        foreign_keys="Proposal.freelancer_id",
        cascade="all, delete-orphan",
    )

    device_tokens = relationship(
        "DeviceToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserProfile(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "user_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_profiles_user_id"),
    )

    # --- Foreign Key ---
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # --- Profile Fields ---
    display_name = Column(String(100), nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    title = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Financial info
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), nullable=False, server_default="USD")
    
    # Location
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)
    
    # Links
    website = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    
    # Images
    avatar_url = Column(String(500), nullable=True)
    cover_image_url = Column(String(500), nullable=True)
    
    # Stats
    total_earnings = Column(Numeric(12, 2), nullable=False, server_default="0")
    completed_projects = Column(Integer, nullable=False, server_default="0")
    average_rating = Column(Numeric(3, 2), nullable=True)
    total_reviews = Column(Integer, nullable=False, server_default="0")
    
    # Settings
    is_available = Column(Boolean, nullable=False, server_default="false")
    is_profile_public = Column(Boolean, nullable=False, server_default="true")

    # --- relationships ---
    user = relationship(
        "User",
        back_populates="profile",
        foreign_keys=[user_id],
    )


class DeviceToken(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "device_tokens"

    # --- Foreign Key ---
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # --- Token Info ---
    fcm_token = Column(String(500), nullable=False, unique=True)
    platform = Column(String(20), nullable=False)  # ios, android, web, desktop
    device_id = Column(String(200), nullable=True)
    
    # --- Status ---
    is_active = Column(Boolean, nullable=False, server_default="true")
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # --- relationships ---
    user = relationship(
        "User",
        back_populates="device_tokens",
        foreign_keys=[user_id],
    )