# api/app/models/milestone.py  
from __future__ import annotations

import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric, Date, DateTime
from sqlalchemy.orm import relationship

from .base import Base, IDMixin, TimestampMixin, ReprMixin

# ========== ENUMS ==========
class MilestoneStatus(enum.Enum):
    pending = "pending"
    funded = "funded"
    in_progress = "in_progress"
    submitted = "submitted"
    approved = "approved"
    released = "released"
    disputed = "disputed"

# ========== MODELS ==========

class Milestone(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "milestones"

    # Foreign Keys
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    
    # Milestone Details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, server_default="0")
    
    # Financial
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, server_default="USD")
    
    # Timeline
    due_date = Column(Date, nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, server_default="pending")
    
    # Milestone Workflow
    funded_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    released_at = Column(DateTime(timezone=True), nullable=True)
    
    # Deliverables
    deliverable_url = Column(String(500), nullable=True)
    submission_notes = Column(Text, nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Relationships
    contract = relationship("Contract", foreign_keys=[contract_id])