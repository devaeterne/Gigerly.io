# api/app/models/notification.py
from __future__ import annotations

import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, IDMixin, TimestampMixin, ReprMixin

class NotificationType(enum.Enum):
    NEW_PROJECT_POSTED = "NEW_PROJECT_POSTED"
    PROJECT_UPDATED = "PROJECT_UPDATED"
    PROJECT_CANCELLED = "PROJECT_CANCELLED"
    PROPOSAL_RECEIVED = "PROPOSAL_RECEIVED"
    PROPOSAL_ACCEPTED = "PROPOSAL_ACCEPTED"
    PROPOSAL_REJECTED = "PROPOSAL_REJECTED"
    CONTRACT_CREATED = "CONTRACT_CREATED"
    CONTRACT_SIGNED = "CONTRACT_SIGNED"
    CONTRACT_STARTED = "CONTRACT_STARTED"
    CONTRACT_COMPLETED = "CONTRACT_COMPLETED"
    CONTRACT_CANCELLED = "CONTRACT_CANCELLED"
    MILESTONE_FUNDED = "MILESTONE_FUNDED"
    MILESTONE_SUBMITTED = "MILESTONE_SUBMITTED"
    MILESTONE_APPROVED = "MILESTONE_APPROVED"
    MILESTONE_RELEASED = "MILESTONE_RELEASED"
    MILESTONE_OVERDUE = "MILESTONE_OVERDUE"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
    PAYMENT_RELEASED = "PAYMENT_RELEASED"
    PAYOUT_PROCESSED = "PAYOUT_PROCESSED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    NEW_MESSAGE = "NEW_MESSAGE"
    REVIEW_RECEIVED = "REVIEW_RECEIVED"
    ACCOUNT_VERIFIED = "ACCOUNT_VERIFIED"
    PROFILE_UPDATED = "PROFILE_UPDATED"
    SYSTEM_MAINTENANCE = "SYSTEM_MAINTENANCE"

class NotificationPriority(enum.Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"

class Notification(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "notifications"

    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Notification Details
    type = Column(String(50), nullable=False)
    priority = Column(String(10), nullable=False, server_default="NORMAL")
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True)
    
    # Status
    is_read = Column(Boolean, nullable=False, server_default="false")
    is_sent_push = Column(Boolean, nullable=False, server_default="false")
    is_sent_email = Column(Boolean, nullable=False, server_default="false")
    
    # Timeline
    read_at = Column(DateTime(timezone=True), nullable=True)
    sent_push_at = Column(DateTime(timezone=True), nullable=True)
    sent_email_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])