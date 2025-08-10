# api/app/models/review.py
from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship

from .base import Base, IDMixin, TimestampMixin, ReprMixin

class Review(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "reviews"

    # Foreign Keys
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    rater_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ratee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Review Details
    rating = Column(Numeric(2, 1), nullable=False)  # 0.0 to 5.0
    title = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)
    
    # Categories (freelancer skills)
    communication_rating = Column(Numeric(2, 1), nullable=True)
    quality_rating = Column(Numeric(2, 1), nullable=True)
    timeliness_rating = Column(Numeric(2, 1), nullable=True)
    professionalism_rating = Column(Numeric(2, 1), nullable=True)
    
    # Status
    is_public = Column(Boolean, nullable=False, server_default="true")
    is_verified = Column(Boolean, nullable=False, server_default="false")

    # Relationships
    contract = relationship("Contract", foreign_keys=[contract_id])
    rater = relationship("User", foreign_keys=[rater_id])
    ratee = relationship("User", foreign_keys=[ratee_id])