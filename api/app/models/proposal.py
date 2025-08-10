from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, IDMixin, TimestampMixin, ReprMixin

class Proposal(Base, IDMixin, TimestampMixin, ReprMixin):
    # HATA: __tablename__ eksikti -> eklendi
    __tablename__ = "proposal"

    # --- FKs ---
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    freelancer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # --- fields ---
    # amount / currency vb. alanları minimal tuttum; istersen genişletiriz
    bid_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, server_default="USD")
    cover_letter = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, server_default="PENDING")
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

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
