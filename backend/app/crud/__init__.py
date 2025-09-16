from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import User, Conversation, Message
from app.schemas import UserCreate, ConversationCreate, MessageCreate
from app.core.security import get_password_hash, verify_password


class UserCRUD:
    """CRUD operations for User model."""
    
    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    def create_user(self, db: Session, user: UserCreate) -> User:
        """Create new user."""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user."""
        user = self.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


class ConversationCRUD:
    """CRUD operations for Conversation model."""
    
    def get_conversation(self, db: Session, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID."""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def get_conversations(self, db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Conversation]:
        """Get conversations with optional user filter."""
        query = db.query(Conversation)
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        return query.offset(skip).limit(limit).all()
    
    def create_conversation(self, db: Session, conversation: ConversationCreate, user_id: Optional[int] = None) -> Conversation:
        """Create new conversation."""
        db_conversation = Conversation(
            title=conversation.title,
            user_id=user_id
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation
    
    def update_conversation_title(self, db: Session, conversation_id: int, title: str) -> Optional[Conversation]:
        """Update conversation title."""
        conversation = self.get_conversation(db, conversation_id)
        if conversation:
            conversation.title = title
            db.commit()
            db.refresh(conversation)
        return conversation


class MessageCRUD:
    """CRUD operations for Message model."""
    
    def get_message(self, db: Session, message_id: int) -> Optional[Message]:
        """Get message by ID."""
        return db.query(Message).filter(Message.id == message_id).first()
    
    def get_messages_by_conversation(self, db: Session, conversation_id: int) -> List[Message]:
        """Get all messages for a conversation."""
        return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.timestamp).all()
    
    def create_message(self, db: Session, message: MessageCreate, conversation_id: int) -> Message:
        """Create new message."""
        db_message = Message(
            conversation_id=conversation_id,
            role=message.role,
            content=message.content
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message


# Create instances
user_crud = UserCRUD()
conversation_crud = ConversationCRUD()
message_crud = MessageCRUD()