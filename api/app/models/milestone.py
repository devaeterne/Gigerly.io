from sqlalchemy import Column, String, Text, Enum, DECIMAL, Integer, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import date

from .base import Base

class MilestoneStatus(str, enum.Enum):
    PENDING = "pending"
    FUNDED = "funded"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    RELEASED = "released"
    DISPUTED = "disputed"

class Milestone(Base):
    """Project milestones for payment tracking"""
    
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    due_date = Column(Date, nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    
    status = Column(Enum(MilestoneStatus), default=MilestoneStatus.PENDING, nullable=False)
    
    funded_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    released_at = Column(DateTime(timezone=True), nullable=True)
    
    deliverable_url = Column(String(500), nullable=True)
    submission_notes = Column(Text, nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Milestone {self.title[:30]}>"