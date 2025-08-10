# api/app/models/proposal.py
from __future__ import annotations

import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, IDMixin, TimestampMixin, ReprMixin

class ProposalStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    withdrawn = "withdrawn"

class Proposal(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "proposals"  # ✅ 'proposal' yerine 'proposals'

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    freelancer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    bid_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, server_default="USD")
    cover_letter = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, server_default="pending")
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    estimated_delivery_days = Column(Integer, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="proposals", foreign_keys=[project_id])
    freelancer = relationship("User", back_populates="proposals", foreign_keys=[freelancer_id])