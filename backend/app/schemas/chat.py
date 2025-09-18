"""
Pydantic schemas for GPT.R1 ChatGPT Clone
Request/Response models with validation
Created by: Rajan Mishra
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"

# Base schemas
class MessageBase(BaseModel):
    """Base message schema"""
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    role: MessageRole = Field(..., description="Message role")

class MessageCreate(MessageBase):
    """Schema for creating new messages"""
    conversation_id: int = Field(..., description="ID of the conversation")
    workflow_id: Optional[str] = Field(None, description="Associated workflow ID")

class MessageUpdate(BaseModel):
    """Schema for updating messages"""
    content: Optional[str] = Field(None, min_length=1, max_length=10000)

class MessageInDB(MessageBase):
    """Message schema as stored in database"""
    id: int
    conversation_id: int
    created_at: datetime
    token_count: Optional[int] = None
    processing_time: Optional[int] = None
    workflow_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class Message(MessageInDB):
    """Public message schema"""
    pass

# Conversation schemas
class ConversationBase(BaseModel):
    """Base conversation schema"""
    title: str = Field(default="New Conversation", max_length=255)

class ConversationCreate(ConversationBase):
    """Schema for creating conversations"""
    pass

class ConversationUpdate(BaseModel):
    """Schema for updating conversations"""
    title: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

class ConversationInDB(ConversationBase):
    """Conversation schema as stored in database"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True

class Conversation(ConversationInDB):
    """Public conversation schema"""
    messages: List[Message] = []

class ConversationSummary(BaseModel):
    """Conversation summary schema"""
    id: int
    title: str
    message_count: int
    last_message_at: Optional[datetime] = None
    created_at: datetime

class ConversationResponse(ConversationInDB):
    """Response schema for conversation operations"""
    messages: List[Message] = []
    
    class Config:
        from_attributes = True

# Chat-specific schemas
class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[int] = None
    
    @validator('message')
    def validate_message(cls, v):
        """Validate message content"""
        if not v.strip():
            raise ValueError('Message cannot be empty or whitespace only')
        return v.strip()

class ChatResponse(BaseModel):
    """Chat response schema"""
    message: str
    conversation_id: int
    message_id: int
    workflow_metadata: Optional[dict] = None

class StreamingChatChunk(BaseModel):
    """Schema for streaming chat chunks"""
    type: str = Field(..., description="Chunk type: content, workflow_start, workflow_summary, complete, error")
    content: Optional[str] = Field(None, description="Chunk content")
    message: Optional[str] = Field(None, description="Status message")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[dict] = Field(None, description="Additional metadata")

# Workflow schemas
class WorkflowStepSchema(BaseModel):
    """Schema for agentic workflow steps"""
    step_type: str
    description: str
    success: bool
    execution_time: float
    error: Optional[str] = None

class WorkflowSchema(BaseModel):
    """Schema for complete agentic workflow"""
    workflow_id: str
    user_query: str
    steps: List[WorkflowStepSchema]
    final_response: str
    total_execution_time: float
    success: bool

class WorkflowStatistics(BaseModel):
    """Schema for workflow statistics"""
    total_workflows: int
    success_rate: float
    average_execution_time: float
    last_workflow_success: Optional[bool] = None