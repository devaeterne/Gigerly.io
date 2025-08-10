from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, JSON, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base

class MessageType(str, enum.Enum):
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    SYSTEM = "system"

class ThreadType(str, enum.Enum):
    PROJECT_DISCUSSION = "project_discussion"
    CONTRACT_COMMUNICATION = "contract_communication"
    SUPPORT_TICKET = "support_ticket"
    DISPUTE = "dispute"

class Thread(Base):
    """Message threads for organizing conversations"""
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    
    type = Column(Enum(ThreadType), nullable=False)
    title = Column(String(200), nullable=True)
    participants = Column(JSON, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    message_count = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<Thread {self.type} - {self.title or 'Untitled'}>"

class Message(Base):
    """Individual messages within threads"""
    
    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    type = Column(Enum(MessageType), default=MessageType.TEXT, nullable=False)
    content = Column(Text, nullable=False)
    attachments = Column(JSON, nullable=True)
    
    is_edited = Column(Boolean, default=False, nullable=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    is_system_message = Column(Boolean, default=False, nullable=False)
    read_by = Column(JSON, nullable=True)
    reply_to_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    
    def __repr__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message from {self.sender_id}: {content_preview}>"