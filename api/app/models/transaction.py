from sqlalchemy import Column, String, Text, Enum, DECIMAL, Integer, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship
import enum

from .base import Base

class TransactionType(str, enum.Enum):
    FUND = "fund"
    RELEASE = "release"
    PAYOUT = "payout"
    REFUND = "refund"
    FEE = "fee"
    ESCROW = "escrow"
    WITHDRAWAL = "withdrawal"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentProvider(str, enum.Enum):
    PAYONEER = "payoneer"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    INTERNAL = "internal"

class Transaction(Base):
    """Financial transactions and payment tracking"""
    
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    provider = Column(Enum(PaymentProvider), nullable=False)
    provider_transaction_id = Column(String(255), nullable=True)
    provider_reference = Column(String(255), nullable=True)
    
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    description = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)  # metadata yerine extra_data
    
    platform_fee = Column(DECIMAL(10, 2), default=0, nullable=False)
    payment_processor_fee = Column(DECIMAL(10, 2), default=0, nullable=False)
    net_amount = Column(DECIMAL(10, 2), nullable=False)
    
    initiated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<Transaction {self.type} {self.amount} {self.currency}>"