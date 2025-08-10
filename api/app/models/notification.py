from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, JSON, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from .base import Base

class NotificationType(str, enum.Enum):
    NEW_PROJECT_POSTED = "new_project_posted"
    PROJECT_UPDATED = "project_updated"
    PROJECT_CANCELLED = "project_cancelled"
    PROPOSAL_RECEIVED = "proposal_received"
    PROPOSAL_ACCEPTED = "proposal_accepted"
    PROPOSAL_REJECTED = "proposal_rejected"
    CONTRACT_CREATED = "contract_created"
    CONTRACT_SIGNED = "contract_signed"
    CONTRACT_STARTED = "contract_started"
    CONTRACT_COMPLETED = "contract_completed"
    CONTRACT_CANCELLED = "contract_cancelled"
    MILESTONE_FUNDED = "milestone_funded"
    MILESTONE_SUBMITTED = "milestone_submitted"
    MILESTONE_APPROVED = "milestone_approved"
    MILESTONE_RELEASED = "milestone_released"
    MILESTONE_OVERDUE = "milestone_overdue"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_RELEASED = "payment_released"
    PAYOUT_PROCESSED = "payout_processed"
    PAYMENT_FAILED = "payment_failed"
    NEW_MESSAGE = "new_message"
    REVIEW_RECEIVED = "review_received"
    ACCOUNT_VERIFIED = "account_verified"
    PROFILE_UPDATED = "profile_updated"
    SYSTEM_MAINTENANCE = "system_maintenance"

class NotificationPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Notification(Base):
    """User notifications for various platform events"""
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.NORMAL, nullable=False)
    
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True)
    
    is_read = Column(Boolean, default=False, nullable=False)
    is_sent_push = Column(Boolean, default=False, nullable=False)
    is_sent_email = Column(Boolean, default=False, nullable=False)
    
    read_at = Column(DateTime(timezone=True), nullable=True)
    sent_push_at = Column(DateTime(timezone=True), nullable=True)
    sent_email_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Notification {self.type} for User {self.user_id}>"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()