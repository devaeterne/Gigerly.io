# api/app/models/notification.py
from __future__ import annotations

import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, IDMixin, TimestampMixin, ReprMixin

# ========== ENUMS ==========
class NotificationType(str, enum.Enum):
    new_project_posted = "new_project_posted"
    project_updated = "project_updated"
    project_cancelled = "project_cancelled"
    proposal_received = "proposal_received"
    proposal_accepted = "proposal_accepted"
    proposal_rejected = "proposal_rejected"
    contract_created = "contract_created"
    contract_signed = "contract_signed"
    contract_started = "contract_started"
    contract_completed = "contract_completed"
    contract_cancelled = "contract_cancelled"
    milestone_funded = "milestone_funded"
    milestone_submitted = "milestone_submitted"
    milestone_approved = "milestone_approved"
    milestone_released = "milestone_released"
    milestone_overdue = "milestone_overdue"
    payment_received = "payment_received"
    payment_released = "payment_released"
    payout_processed = "payout_processed"
    payment_failed = "payment_failed"
    new_message = "new_message"
    review_received = "review_received"
    account_verified = "account_verified"
    profile_updated = "profile_updated"
    system_maintenance = "system_maintenance"


class NotificationPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"

# ========== MODELS ==========

class Notification(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "notifications"

    # --- Foreign Key ---
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # --- Notification Details ---
    type = Column(String(50), nullable=False)
    priority = Column(String(10), nullable=False, server_default="normal")
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True)
    
    # --- Status ---
    is_read = Column(Boolean, nullable=False, server_default="false")
    is_sent_push = Column(Boolean, nullable=False, server_default="false")
    is_sent_email = Column(Boolean, nullable=False, server_default="false")
    
    # --- Timeline ---
    read_at = Column(DateTime(timezone=True), nullable=True)
    sent_push_at = Column(DateTime(timezone=True), nullable=True)
    sent_email_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # --- relationships ---
    user = relationship("User", foreign_keys=[user_id])
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = func.now()