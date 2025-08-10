# api/app/models/contract.py
from __future__ import annotations

import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric, Date, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship

from .base import Base, IDMixin, TimestampMixin, ReprMixin

# ========== ENUMS ==========
class ContractStatus(enum.Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"
    cancelled = "cancelled"
    disputed = "disputed"

class ContractType(enum.Enum):
    fixed_price = "fixed_price"
    hourly = "hourly"

# ========== MODELS ==========

class Contract(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "contracts"

    # Foreign Keys
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    freelancer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    winning_proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=True)

    # Contract Details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    contract_type = Column(String(20), nullable=False, server_default="fixed_price")
    
    # Financial
    total_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, server_default="USD")
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    
    # Timeline
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, server_default="draft")
    
    # Contract Data
    terms = Column(JSON, nullable=False, server_default="{}")
    deliverables = Column(JSON, nullable=False, server_default="[]")
    payment_schedule = Column(JSON, nullable=True)
    
    # Signatures
    signed_by_customer_at = Column(DateTime(timezone=True), nullable=True)
    signed_by_freelancer_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metrics
    approved_hours = Column(Numeric(10, 2), nullable=False, server_default="0")
    billed_amount = Column(Numeric(12, 2), nullable=False, server_default="0")
    paid_amount = Column(Numeric(12, 2), nullable=False, server_default="0")

    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    customer = relationship("User", foreign_keys=[customer_id])
    freelancer = relationship("User", foreign_keys=[freelancer_id])