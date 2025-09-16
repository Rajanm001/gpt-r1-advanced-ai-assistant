from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserLogin(BaseModel):
    """User login schema."""
    username: str
    password: str


class User(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str


class MessageBase(BaseModel):
    """Base message schema."""
    role: str
    content: str


class MessageCreate(MessageBase):
    """Message creation schema."""
    conversation_id: Optional[int] = None


class Message(MessageBase):
    """Message response schema."""
    id: int
    conversation_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """Base conversation schema."""
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    """Conversation creation schema."""
    pass


class Conversation(ConversationBase):
    """Conversation response schema."""
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[Message] = []
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str
    conversation_id: Optional[int] = None
    use_rag: bool = False


class ChatResponse(BaseModel):
    """Chat response schema."""
    conversation_id: int
    message: Message