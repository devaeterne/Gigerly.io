# api/app/models/proposal.py
from __future__ import annotations

import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, IDMixin, TimestampMixin, ReprMixin

# ========== ENUMS ==========
class ProposalStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

# ========== MODELS ==========

class Proposal(Base, IDMixin, TimestampMixin, ReprMixin):
    # DÜZELTME: Migration'da 'proposals' (çoğul) olarak yaratılmış
    __tablename__ = "proposals"  # ✅ 'proposal' yerine 'proposals'

    # --- FKs ---
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    freelancer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # --- fields ---
    bid_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, server_default="USD")
    cover_letter = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, server_default="PENDING")
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Ek alanlar (migration'da mevcut)
    estimated_delivery_days = Column(Integer, nullable=True)

    # --- relationships ---
    project = relationship(
        "Project",
        back_populates="proposals",
        foreign_keys=[project_id],
    )

    freelancer = relationship(
        "User",
        back_populates="proposals",
        foreign_keys=[freelancer_id],
    )