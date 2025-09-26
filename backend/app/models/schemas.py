from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    conversation_id: Optional[int] = None

class Message(MessageBase):
    id: int
    conversation_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationBase(BaseModel):
    title: Optional[str] = "New Conversation"

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []

    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    conversation_history: Optional[List[MessageBase]] = []

class ChatResponse(BaseModel):
    message: str
    conversation_id: int