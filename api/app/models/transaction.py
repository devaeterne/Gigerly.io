# api/app/models/transaction.py
from __future__ import annotations

import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, IDMixin, TimestampMixin, ReprMixin

# ========== ENUMS ==========
class TransactionType(enum.Enum):
    fund = "fund"
    release = "release"
    payout = "payout"
    refund = "refund"
    fee = "fee"
    escrow = "escrow"
    withdrawal = "withdrawal"

class TransactionStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"
    refunded = "refunded"

class PaymentProvider(enum.Enum):
    payoneer = "payoneer"
    stripe = "stripe"
    paypal = "paypal"
    bank_transfer = "bank_transfer"
    interval = "interval"

# ========== MODELS ==========

class Transaction(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "transactions"

    # Foreign Keys
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Transaction Details
    type = Column(String(20), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, server_default="USD")
    
    # Provider Info
    provider = Column(String(30), nullable=False)
    provider_transaction_id = Column(String(255), nullable=True)
    provider_reference = Column(String(255), nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, server_default="pending")
    description = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)
    
    # Fees
    platform_fee = Column(Numeric(10, 2), nullable=False, server_default="0")
    payment_processor_fee = Column(Numeric(10, 2), nullable=False, server_default="0")
    net_amount = Column(Numeric(10, 2), nullable=False)
    
    # Timeline
    initiated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error Handling
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, server_default="0")

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    contract = relationship("Contract", foreign_keys=[contract_id])
    milestone = relationship("Milestone", foreign_keys=[milestone_id])