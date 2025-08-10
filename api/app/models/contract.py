from sqlalchemy import Column, String, Text, Enum, DECIMAL, Integer, ForeignKey, Boolean, Date, JSON, DateTime
from sqlalchemy.orm import relationship
import enum

from .base import Base

class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class ContractType(str, enum.Enum):
    FIXED_PRICE = "fixed_price"
    HOURLY = "hourly"

class Contract(Base):
    """Contract between customer and freelancer"""
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    freelancer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    winning_proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=True)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    contract_type = Column(Enum(ContractType), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    hourly_rate = Column(DECIMAL(8, 2), nullable=True)
    
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT, nullable=False)
    terms = Column(JSON, nullable=True)
    deliverables = Column(JSON, nullable=True)
    payment_schedule = Column(JSON, nullable=True)
    
    approved_hours = Column(DECIMAL(8, 2), default=0, nullable=False)
    billed_amount = Column(DECIMAL(10, 2), default=0, nullable=False)
    paid_amount = Column(DECIMAL(10, 2), default=0, nullable=False)
    
    signed_by_customer_at = Column(DateTime(timezone=True), nullable=True)
    signed_by_freelancer_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Contract {self.id}: {self.title[:30]}>"