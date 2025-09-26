from sqlalchemy.orm import Session
from app.models.models import Conversation, Message
from app.models.schemas import ConversationCreate, MessageCreate
from typing import List, Optional, cast

class ConversationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_conversation(self, conversation: ConversationCreate) -> Conversation:
        """Create a new conversation"""
        db_conversation = Conversation(**conversation.dict())
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        return db_conversation
    
    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def get_conversations(self, skip: int = 0, limit: int = 50) -> List[Conversation]:
        """Get all conversations"""
        return self.db.query(Conversation).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
            return True
        return False
    
    def add_message(self, message: MessageCreate) -> Message:
        """Add a message to a conversation"""
        db_message = Message(**message.dict())
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        
        # Update conversation timestamp
        conversation_id_from_msg = getattr(db_message, 'conversation_id', None)
        if conversation_id_from_msg is not None:
            conversation_id_int = cast(int, conversation_id_from_msg)
            conversation = self.get_conversation(conversation_id_int)
            if conversation:
                self.db.commit()
        
        return db_message
    
    def get_conversation_messages(self, conversation_id: int) -> List[Message]:
        """Get all messages for a conversation"""
        return self.db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.timestamp.asc()).all()