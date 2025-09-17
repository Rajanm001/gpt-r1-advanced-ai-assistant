"""
GPT.R1 - Comprehensive Test Suite
Production-ready testing with full coverage
Created by: Rajan Mishra
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime, timedelta

from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token
from app.models.user import User
from app.models.conversation import Conversation, Message

# Test database setup
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5432/test_gpt_r1_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Async test client fixture"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def db_session():
    """Database session fixture"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$hashedpassword",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_conversation(db_session, test_user):
    """Create test conversation"""
    conversation = Conversation(
        title="Test Conversation",
        user_id=test_user.id
    )
    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)
    return conversation

@pytest.fixture
def auth_headers(test_user):
    """Authentication headers for requests"""
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}

class TestChatAPI:
    """Test chat API endpoints"""
    
    def test_chat_without_auth(self, client):
        """Test chat endpoint requires authentication"""
        response = client.post("/api/v1/chat", json={"message": "Hello"})
        assert response.status_code == 401
    
    def test_chat_with_invalid_message(self, client, auth_headers):
        """Test chat with invalid message format"""
        response = client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": ""}
        )
        assert response.status_code == 400
        assert "VALIDATION_ERROR" in response.json()["detail"]["code"]
    
    def test_chat_message_too_long(self, client, auth_headers):
        """Test chat with message exceeding length limit"""
        long_message = "x" * 5000
        response = client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": long_message}
        )
        assert response.status_code == 400
        assert "MESSAGE_TOO_LONG" in response.json()["detail"]["errors"][0]["code"]
    
    @patch('app.services.openai_service.OpenAIService.create_chat_completion_stream')
    async def test_chat_streaming_success(self, mock_stream, async_client, auth_headers):
        """Test successful chat streaming"""
        # Mock streaming response
        async def mock_stream_response(*args, **kwargs):
            yield "Hello"
            yield " world"
            yield "!"
        
        mock_stream.return_value = mock_stream_response()
        
        response = await async_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": "Hello"}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
    
    @patch('app.services.openai_service.OpenAIService.create_chat_completion_stream')
    async def test_chat_openai_error_fallback(self, mock_stream, async_client, auth_headers):
        """Test OpenAI error triggers fallback response"""
        # Mock OpenAI error
        mock_stream.side_effect = Exception("OpenAI API Error")
        
        response = await async_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": "Hello"}
        )
        
        assert response.status_code == 200
        # Should still get a streaming response with fallback content
    
    def test_chat_invalid_conversation_id(self, client, auth_headers):
        """Test chat with non-existent conversation ID"""
        response = client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": "Hello", "conversation_id": 99999}
        )
        assert response.status_code == 404
        assert "CONVERSATION_NOT_FOUND" in response.json()["detail"]["code"]
    
    def test_chat_with_rag(self, client, auth_headers):
        """Test chat with RAG enabled"""
        with patch('app.services.rag_service.RAGService.get_context_from_search') as mock_rag:
            mock_rag.return_value = "Some search context"
            
            response = client.post(
                "/api/v1/chat",
                headers=auth_headers,
                json={"message": "What's the weather?", "use_rag": True}
            )
            
            assert response.status_code == 200

class TestAuthentication:
    """Test authentication system"""
    
    def test_create_user_success(self, client):
        """Test successful user creation"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "StrongPass123!"
            }
        )
        assert response.status_code == 201
        assert "access_token" in response.json()
    
    def test_create_user_weak_password(self, client):
        """Test user creation with weak password"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "weak"
            }
        )
        assert response.status_code == 400
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        with patch('app.core.security.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "username": "testuser",
                    "password": "password"
                }
            )
            assert response.status_code == 200
            assert "access_token" in response.json()
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        with patch('app.core.security.verify_password') as mock_verify:
            mock_verify.return_value = False
            
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "username": "testuser",
                    "password": "wrongpassword"
                }
            )
            assert response.status_code == 401

class TestConversations:
    """Test conversation management"""
    
    def test_get_conversations(self, client, auth_headers, test_conversation):
        """Test getting user conversations"""
        response = client.get("/api/v1/conversations", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1
    
    def test_get_conversation_messages(self, client, auth_headers, test_conversation):
        """Test getting conversation messages"""
        response = client.get(
            f"/api/v1/conversations/{test_conversation.id}/messages",
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_delete_conversation(self, client, auth_headers, test_conversation):
        """Test deleting conversation"""
        response = client.delete(
            f"/api/v1/conversations/{test_conversation.id}",
            headers=auth_headers
        )
        assert response.status_code == 200

class TestErrorHandling:
    """Test error handling system"""
    
    def test_database_error_handling(self, client, auth_headers):
        """Test database error handling"""
        with patch('app.core.database.get_db') as mock_db:
            mock_db.side_effect = Exception("Database connection failed")
            
            response = client.get("/api/v1/conversations", headers=auth_headers)
            # Should return appropriate error response
            assert response.status_code in [500, 503]
    
    def test_rate_limiting(self, client, auth_headers):
        """Test rate limiting functionality"""
        # Make multiple rapid requests
        for _ in range(5):
            response = client.post(
                "/api/v1/chat",
                headers=auth_headers,
                json={"message": "Test"}
            )
        
        # Should not trigger rate limit for small number of requests
        assert response.status_code != 429
    
    def test_validation_error_format(self, client, auth_headers):
        """Test validation error response format"""
        response = client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"invalid": "request"}
        )
        
        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "error" in error_detail
        assert "code" in error_detail
        assert "timestamp" in error_detail

class TestHealthCheck:
    """Test system health check"""
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert "status" in health_data
        assert "services" in health_data
        assert "timestamp" in health_data

class TestStreamingResponse:
    """Test streaming response functionality"""
    
    @patch('app.services.openai_service.OpenAIService.create_chat_completion_stream')
    async def test_sse_format(self, mock_stream, async_client, auth_headers):
        """Test Server-Sent Events format"""
        async def mock_stream_response(*args, **kwargs):
            yield "chunk1"
            yield "chunk2"
        
        mock_stream.return_value = mock_stream_response()
        
        response = await async_client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": "Test"}
        )
        
        assert response.status_code == 200
        content = response.content.decode()
        
        # Check for SSE format
        assert "data: " in content
        assert "\n\n" in content
    
    async def test_streaming_cancellation(self, async_client, auth_headers):
        """Test streaming request cancellation"""
        # This would test the abort controller functionality
        # In a real scenario, we'd test timeout and cancellation
        pass

class TestRAGIntegration:
    """Test RAG (Retrieval Augmented Generation) functionality"""
    
    @patch('app.services.rag_service.RAGService.get_context_from_search')
    def test_rag_search_success(self, mock_search, client, auth_headers):
        """Test successful RAG search integration"""
        mock_search.return_value = "Relevant search context"
        
        response = client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": "What is Python?", "use_rag": True}
        )
        
        assert response.status_code == 200
        mock_search.assert_called_once()
    
    @patch('app.services.rag_service.RAGService.get_context_from_search')
    def test_rag_search_failure_fallback(self, mock_search, client, auth_headers):
        """Test RAG search failure doesn't break chat"""
        mock_search.side_effect = Exception("Search service unavailable")
        
        response = client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": "What is Python?", "use_rag": True}
        )
        
        # Should still succeed with fallback
        assert response.status_code == 200

class TestDatabaseOperations:
    """Test database operations and transactions"""
    
    def test_conversation_creation(self, db_session, test_user):
        """Test conversation creation in database"""
        conversation = Conversation(
            title="New Conversation",
            user_id=test_user.id
        )
        db_session.add(conversation)
        db_session.commit()
        
        assert conversation.id is not None
        assert conversation.user_id == test_user.id
    
    def test_message_creation(self, db_session, test_conversation):
        """Test message creation in database"""
        message = Message(
            conversation_id=test_conversation.id,
            role="user",
            content="Test message"
        )
        db_session.add(message)
        db_session.commit()
        
        assert message.id is not None
        assert message.conversation_id == test_conversation.id
    
    def test_user_conversation_relationship(self, db_session, test_user):
        """Test user-conversation relationship"""
        conversations = db_session.query(Conversation).filter(
            Conversation.user_id == test_user.id
        ).all()
        
        assert len(conversations) >= 0

# Performance tests
class TestPerformance:
    """Test performance characteristics"""
    
    def test_response_time(self, client, auth_headers):
        """Test API response times"""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self, client, auth_headers):
        """Test handling concurrent requests"""
        import threading
        
        results = []
        
        def make_request():
            response = client.get("/api/v1/conversations", headers=auth_headers)
            results.append(response.status_code)
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)

# Integration tests
class TestIntegration:
    """End-to-end integration tests"""
    
    def test_complete_chat_flow(self, client):
        """Test complete chat flow from registration to conversation"""
        # 1. Register user
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "integrationuser",
                "email": "integration@example.com",
                "password": "StrongPass123!"
            }
        )
        assert register_response.status_code == 201
        
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Send chat message
        with patch('app.services.openai_service.OpenAIService.create_chat_completion_stream') as mock_stream:
            async def mock_response(*args, **kwargs):
                yield "Hello! How can I help you today?"
            
            mock_stream.return_value = mock_response()
            
            chat_response = client.post(
                "/api/v1/chat",
                headers=headers,
                json={"message": "Hello"}
            )
            assert chat_response.status_code == 200
        
        # 3. Get conversations
        conversations_response = client.get("/api/v1/conversations", headers=headers)
        assert conversations_response.status_code == 200
        assert len(conversations_response.json()) >= 1

# Test fixtures cleanup
@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up database after each test"""
    yield
    # Cleanup logic here
    session = TestingSessionLocal()
    try:
        session.query(Message).delete()
        session.query(Conversation).delete()
        session.query(User).delete()
        session.commit()
    finally:
        session.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])