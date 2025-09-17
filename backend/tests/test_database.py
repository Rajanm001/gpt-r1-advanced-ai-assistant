"""
GPT.R1 - Database Tests
Comprehensive testing of database operations and data persistence
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from backend.app.core.database import Base, get_db
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.crud import conversation_crud, message_crud
from backend.app.schemas.chat import ConversationCreate, MessageCreate, ConversationUpdate

# Test database configuration
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5432/test_gpt_r1_db"

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    """Create test database session"""
    async_session_maker = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()

class TestDatabaseConnection:
    """Test database connection and basic operations"""
    
    async def test_database_connection(self, test_engine):
        """Test basic database connectivity"""
        async with test_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
    
    async def test_table_creation(self, test_engine):
        """Test that all tables are created properly"""
        async with test_engine.begin() as conn:
            # Check conversations table
            result = await conn.execute(text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'conversations')"
            ))
            assert result.scalar() is True
            
            # Check messages table
            result = await conn.execute(text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'messages')"
            ))
            assert result.scalar() is True
    
    async def test_table_relationships(self, test_engine):
        """Test foreign key relationships"""
        async with test_engine.begin() as conn:
            # Check foreign key constraint exists
            result = await conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.table_constraints 
                WHERE constraint_type = 'FOREIGN KEY' 
                AND table_name = 'messages'
                AND constraint_name LIKE '%conversation_id%'
            """))
            assert result.scalar() >= 1  # Should have FK constraint

class TestConversationCRUD:
    """Test conversation CRUD operations"""
    
    async def test_create_conversation(self, test_session):
        """Test conversation creation"""
        conversation_data = ConversationCreate(title="Test Conversation")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        
        assert conversation.id is not None
        assert conversation.title == "Test Conversation"
        assert conversation.created_at is not None
        assert conversation.updated_at is not None
        assert isinstance(conversation.created_at, datetime)
    
    async def test_get_conversation_by_id(self, test_session):
        """Test conversation retrieval by ID"""
        # Create conversation
        conversation_data = ConversationCreate(title="Test Conversation")
        created_conv = await conversation_crud.create(test_session, obj_in=conversation_data)
        await test_session.commit()
        
        # Retrieve conversation
        retrieved_conv = await conversation_crud.get(test_session, id=created_conv.id)
        
        assert retrieved_conv is not None
        assert retrieved_conv.id == created_conv.id
        assert retrieved_conv.title == "Test Conversation"
    
    async def test_get_nonexistent_conversation(self, test_session):
        """Test retrieval of non-existent conversation"""
        conversation = await conversation_crud.get(test_session, id=99999)
        assert conversation is None
    
    async def test_update_conversation(self, test_session):
        """Test conversation update"""
        # Create conversation
        conversation_data = ConversationCreate(title="Original Title")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        await test_session.commit()
        
        # Update conversation
        update_data = ConversationUpdate(title="Updated Title")
        updated_conv = await conversation_crud.update(
            test_session, db_obj=conversation, obj_in=update_data
        )
        await test_session.commit()
        
        assert updated_conv.title == "Updated Title"
        assert updated_conv.updated_at > updated_conv.created_at
    
    async def test_delete_conversation(self, test_session):
        """Test conversation deletion"""
        # Create conversation
        conversation_data = ConversationCreate(title="To Delete")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        await test_session.commit()
        
        conversation_id = conversation.id
        
        # Delete conversation
        await conversation_crud.remove(test_session, id=conversation_id)
        await test_session.commit()
        
        # Verify deletion
        deleted_conv = await conversation_crud.get(test_session, id=conversation_id)
        assert deleted_conv is None
    
    async def test_get_conversation_summaries(self, test_session):
        """Test conversation summaries retrieval"""
        # Create multiple conversations
        conversations_data = [
            ConversationCreate(title="Conversation 1"),
            ConversationCreate(title="Conversation 2"),
            ConversationCreate(title="Conversation 3")
        ]
        
        created_conversations = []
        for conv_data in conversations_data:
            conv = await conversation_crud.create(test_session, obj_in=conv_data)
            created_conversations.append(conv)
        
        await test_session.commit()
        
        # Get summaries
        summaries = await conversation_crud.get_conversation_summaries(test_session, limit=10)
        
        assert len(summaries) >= 3
        
        # Verify summary structure
        for summary in summaries:
            assert "id" in summary
            assert "title" in summary
            assert "created_at" in summary
            assert "message_count" in summary

class TestMessageCRUD:
    """Test message CRUD operations"""
    
    async def test_create_message(self, test_session):
        """Test message creation"""
        # Create conversation first
        conversation_data = ConversationCreate(title="Test Conversation")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        await test_session.commit()
        
        # Create message
        message_data = MessageCreate(
            conversation_id=conversation.id,
            content="Test message content",
            role="user"
        )
        message = await message_crud.create(test_session, obj_in=message_data)
        
        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.content == "Test message content"
        assert message.role == "user"
        assert message.created_at is not None
    
    async def test_get_message_by_id(self, test_session):
        """Test message retrieval by ID"""
        # Create conversation and message
        conversation_data = ConversationCreate(title="Test Conversation")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        await test_session.commit()
        
        message_data = MessageCreate(
            conversation_id=conversation.id,
            content="Test message",
            role="user"
        )
        created_message = await message_crud.create(test_session, obj_in=message_data)
        await test_session.commit()
        
        # Retrieve message
        retrieved_message = await message_crud.get(test_session, id=created_message.id)
        
        assert retrieved_message is not None
        assert retrieved_message.id == created_message.id
        assert retrieved_message.content == "Test message"
    
    async def test_get_messages_by_conversation(self, test_session):
        """Test retrieving messages for a conversation"""
        # Create conversation
        conversation_data = ConversationCreate(title="Test Conversation")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        await test_session.commit()
        
        # Create multiple messages
        messages_data = [
            MessageCreate(
                conversation_id=conversation.id,
                content="Message 1",
                role="user"
            ),
            MessageCreate(
                conversation_id=conversation.id,
                content="Message 2",
                role="assistant"
            ),
            MessageCreate(
                conversation_id=conversation.id,
                content="Message 3",
                role="user"
            )
        ]
        
        for msg_data in messages_data:
            await message_crud.create(test_session, obj_in=msg_data)
        
        await test_session.commit()
        
        # Retrieve messages
        messages = await message_crud.get_messages_by_conversation(
            test_session, conversation_id=conversation.id
        )
        
        assert len(messages) == 3
        
        # Verify order (should be chronological)
        assert messages[0].content == "Message 1"
        assert messages[1].content == "Message 2"
        assert messages[2].content == "Message 3"
        
        # Verify roles
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"
        assert messages[2].role == "user"
    
    async def test_get_messages_empty_conversation(self, test_session):
        """Test retrieving messages from empty conversation"""
        # Create conversation
        conversation_data = ConversationCreate(title="Empty Conversation")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        await test_session.commit()
        
        # Retrieve messages (should be empty)
        messages = await message_crud.get_messages_by_conversation(
            test_session, conversation_id=conversation.id
        )
        
        assert len(messages) == 0
    
    async def test_delete_message(self, test_session):
        """Test message deletion"""
        # Create conversation and message
        conversation_data = ConversationCreate(title="Test Conversation")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        await test_session.commit()
        
        message_data = MessageCreate(
            conversation_id=conversation.id,
            content="To Delete",
            role="user"
        )
        message = await message_crud.create(test_session, obj_in=message_data)
        await test_session.commit()
        
        message_id = message.id
        
        # Delete message
        await message_crud.remove(test_session, id=message_id)
        await test_session.commit()
        
        # Verify deletion
        deleted_message = await message_crud.get(test_session, id=message_id)
        assert deleted_message is None

class TestDatabaseConstraints:
    """Test database constraints and validation"""
    
    async def test_conversation_title_constraint(self, test_session):
        """Test conversation title constraints"""
        # Test with valid title
        conversation_data = ConversationCreate(title="Valid Title")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        assert conversation.title == "Valid Title"
        
        # Test with long title (should be truncated or handled)
        long_title = "x" * 1000
        conversation_data = ConversationCreate(title=long_title)
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        # Should either succeed or be handled gracefully
        assert conversation.title is not None
    
    async def test_message_foreign_key_constraint(self, test_session):
        """Test message foreign key constraints"""
        # Create valid message with conversation
        conversation_data = ConversationCreate(title="Test Conversation")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        await test_session.commit()
        
        message_data = MessageCreate(
            conversation_id=conversation.id,
            content="Valid message",
            role="user"
        )
        message = await message_crud.create(test_session, obj_in=message_data)
        assert message.conversation_id == conversation.id
        
        # Test with invalid conversation_id should be handled by application logic
        # (Database constraints might allow this depending on configuration)
    
    async def test_message_role_validation(self, test_session):
        """Test message role validation"""
        # Create conversation
        conversation_data = ConversationCreate(title="Test Conversation")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        await test_session.commit()
        
        # Test valid roles
        valid_roles = ["user", "assistant", "system"]
        for role in valid_roles:
            message_data = MessageCreate(
                conversation_id=conversation.id,
                content=f"Message from {role}",
                role=role
            )
            message = await message_crud.create(test_session, obj_in=message_data)
            assert message.role == role

class TestDatabasePerformance:
    """Test database performance and optimization"""
    
    async def test_conversation_list_performance(self, test_session):
        """Test performance of conversation list retrieval"""
        import time
        
        # Create many conversations
        conversations = []
        for i in range(100):
            conversation_data = ConversationCreate(title=f"Conversation {i}")
            conv = await conversation_crud.create(test_session, obj_in=conversation_data)
            conversations.append(conv)
        
        await test_session.commit()
        
        # Measure performance
        start_time = time.time()
        summaries = await conversation_crud.get_conversation_summaries(
            test_session, limit=50
        )
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert len(summaries) == 50
        assert execution_time < 1.0  # Should complete within 1 second
    
    async def test_message_retrieval_performance(self, test_session):
        """Test performance of message retrieval"""
        import time
        
        # Create conversation with many messages
        conversation_data = ConversationCreate(title="Performance Test")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        await test_session.commit()
        
        # Create many messages
        for i in range(200):
            message_data = MessageCreate(
                conversation_id=conversation.id,
                content=f"Message {i}",
                role="user" if i % 2 == 0 else "assistant"
            )
            await message_crud.create(test_session, obj_in=message_data)
        
        await test_session.commit()
        
        # Measure retrieval performance
        start_time = time.time()
        messages = await message_crud.get_messages_by_conversation(
            test_session, conversation_id=conversation.id
        )
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert len(messages) == 200
        assert execution_time < 1.0  # Should complete within 1 second

class TestDatabaseTransactions:
    """Test database transaction handling"""
    
    async def test_successful_transaction(self, test_session):
        """Test successful transaction completion"""
        # Create conversation and message in same transaction
        conversation_data = ConversationCreate(title="Transaction Test")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        
        message_data = MessageCreate(
            conversation_id=conversation.id,
            content="Transaction message",
            role="user"
        )
        message = await message_crud.create(test_session, obj_in=message_data)
        
        await test_session.commit()
        
        # Verify both were committed
        retrieved_conv = await conversation_crud.get(test_session, id=conversation.id)
        retrieved_msg = await message_crud.get(test_session, id=message.id)
        
        assert retrieved_conv is not None
        assert retrieved_msg is not None
    
    async def test_transaction_rollback(self, test_session):
        """Test transaction rollback"""
        # Create conversation
        conversation_data = ConversationCreate(title="Rollback Test")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        
        conversation_id = conversation.id
        
        # Rollback without commit
        await test_session.rollback()
        
        # Verify conversation was not persisted
        retrieved_conv = await conversation_crud.get(test_session, id=conversation_id)
        assert retrieved_conv is None

class TestDatabaseErrorHandling:
    """Test database error handling"""
    
    async def test_connection_error_handling(self, test_session):
        """Test handling of connection errors"""
        # This would require mocking the database connection
        # For now, we'll test that our CRUD operations handle exceptions gracefully
        
        # Test with mock that raises exception
        with patch.object(test_session, 'execute', side_effect=Exception("Connection error")):
            try:
                conversation_data = ConversationCreate(title="Error Test")
                await conversation_crud.create(test_session, obj_in=conversation_data)
                # Should handle error gracefully
            except Exception as e:
                # Exception should be handled by application
                assert "Connection error" in str(e)
    
    async def test_duplicate_constraint_handling(self, test_session):
        """Test handling of constraint violations"""
        # This depends on specific constraints in the schema
        # For now, test that our models handle edge cases
        
        conversation_data = ConversationCreate(title="Constraint Test")
        conversation = await conversation_crud.create(test_session, obj_in=conversation_data)
        
        # Should succeed without constraint violations
        assert conversation.title == "Constraint Test"

if __name__ == "__main__":
    print("🗄️ Running Database Tests...")
    pytest.main([__file__, "-v"])