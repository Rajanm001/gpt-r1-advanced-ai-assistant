"""
Database models for GPT.R1 ChatGPT Clone
PostgreSQL-optimized models with proper relationships
Created by: Rajan Mishra
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    """
    Conversation model - represents a chat conversation
    Optimized for PostgreSQL with proper indexing
    """
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}')>"

class Message(Base):
    """
    Message model - represents individual messages in conversations
    Supports both user and assistant messages with metadata
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Optional metadata for advanced features
    token_count = Column(Integer, nullable=True)
    processing_time = Column(Integer, nullable=True)  # in milliseconds
    workflow_id = Column(String(100), nullable=True)  # Links to agentic workflow
    
    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"