from sqlalchemy import Column, String, Text, Integer, ForeignKey, DECIMAL, Boolean, JSON, DateTime
from sqlalchemy.orm import relationship

from .base import Base

class Review(Base):
    """Reviews and ratings between users after contract completion"""
    
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    rater_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ratee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    overall_rating = Column(DECIMAL(2, 1), nullable=False)
    communication_rating = Column(DECIMAL(2, 1), nullable=True)
    quality_rating = Column(DECIMAL(2, 1), nullable=True)
    timeliness_rating = Column(DECIMAL(2, 1), nullable=True)
    professionalism_rating = Column(DECIMAL(2, 1), nullable=True)
    
    title = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)
    
    is_public = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    skills_mentioned = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    
    response = Column(Text, nullable=True)
    response_created_at = Column(DateTime(timezone=True), nullable=True)
    
    is_flagged = Column(Boolean, default=False, nullable=False)
    moderation_notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Review {self.overall_rating}⭐ from {self.rater_id} to {self.ratee_id}>"