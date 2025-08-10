# api/app/models/message.py
from __future__ import annotations

import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, IDMixin, TimestampMixin, ReprMixin

# ========== ENUMS ==========
class ThreadType(enum.Enum):
    PROJECT_DISCUSSION = "PROJECT_DISCUSSION"
    CONTRACT_COMMUNICATION = "CONTRACT_COMMUNICATION"
    SUPPORT_TICKET = "SUPPORT_TICKET"
    DISPUTE = "DISPUTE"

class MessageType(enum.Enum):
    TEXT = "TEXT"
    FILE = "FILE"
    IMAGE = "IMAGE"
    SYSTEM = "SYSTEM"

# ========== MODELS ==========

class Thread(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "threads"

    # Foreign Keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    
    # Thread Details
    type = Column(String(30), nullable=False)
    title = Column(String(200), nullable=True)
    participants = Column(JSON, nullable=False, server_default="[]")
    
    # Status
    is_archived = Column(Boolean, nullable=False, server_default="false")
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    message_count = Column(Integer, nullable=False, server_default="0")

    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    contract = relationship("Contract", foreign_keys=[contract_id])
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")


class Message(Base, IDMixin, TimestampMixin, ReprMixin):
    __tablename__ = "messages"

    # Foreign Keys
    thread_id = Column(Integer, ForeignKey("threads.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reply_to_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    
    # Message Details
    type = Column(String(20), nullable=False, server_default="TEXT")
    content = Column(Text, nullable=False)
    attachments = Column(JSON, nullable=True)
    
    # Status
    is_edited = Column(Boolean, nullable=False, server_default="false")
    is_system_message = Column(Boolean, nullable=False, server_default="false")
    edited_at = Column(DateTime(timezone=True), nullable=True)
    read_by = Column(JSON, nullable=True)

    # Relationships
    thread = relationship("Thread", back_populates="messages", foreign_keys=[thread_id])
    sender = relationship("User", foreign_keys=[sender_id])
    
    # ✅ DÜZELTME: Self-referential relationship için remote_side gerekli
    reply_to = relationship(
        "Message", 
        foreign_keys=[reply_to_message_id], 
        remote_side="id"  # String olarak column adı
    )