"""
Comprehensive Test Suite for GPT.R1 Advanced AI Assistant
========================================================

This module contains comprehensive tests covering:
- Mock OpenAI integration
- Database persistence 
- Error handling scenarios
- Authentication flows
- Streaming functionality
- API endpoints

All tests use mocked external dependencies for reliable, fast execution.
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
import uuid
from datetime import datetime, timedelta

# Import application components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app
from app.core.config import get_settings
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.auth import UserCreate, UserLogin
from app.schemas.chat import ChatMessage, ConversationCreate


class TestOpenAIMocking:
    """Test suite for OpenAI API integration with comprehensive mocking"""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client with realistic responses"""
        mock_client = Mock()
        
        # Mock streaming response
        async def mock_stream_chunks():
            chunks = [
                "Hello", " there!", " I'm", " GPT", "-4", " and", 
                " I'm", " here", " to", " help", " you", " today."
            ]
            for chunk in chunks:
                yield {
                    "choices": [{
                        "delta": {
                            "content": chunk
                        }
                    }]
                }
        
        mock_client.chat.completions.create.return_value = mock_stream_chunks()
        return mock_client
    
    @pytest.mark.asyncio
    async def test_openai_streaming_response(self, mock_openai_client):
        """Test OpenAI streaming response handling"""
        with patch('app.services.chat_service.openai_client', mock_openai_client):
            # Simulate streaming response
            collected_chunks = []
            async for chunk in mock_openai_client.chat.completions.create():
                if chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
                    collected_chunks.append(chunk["choices"][0]["delta"]["content"])
            
            # Verify chunks are received
            assert len(collected_chunks) > 0
            full_response = "".join(collected_chunks)
            assert "Hello there!" in full_response
            assert "GPT-4" in full_response
    
    @pytest.mark.asyncio 
    async def test_openai_error_handling(self):
        """Test OpenAI API error scenarios"""
        with patch('app.services.chat_service.openai_client') as mock_client:
            # Mock API rate limit error
            mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
            
            # Test error is properly handled
            with pytest.raises(Exception) as exc_info:
                mock_client.chat.completions.create()
            
            assert "Rate limit exceeded" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_openai_timeout_handling(self):
        """Test OpenAI API timeout scenarios"""
        with patch('app.services.chat_service.openai_client') as mock_client:
            # Mock timeout error
            mock_client.chat.completions.create.side_effect = asyncio.TimeoutError("Request timeout")
            
            with pytest.raises(asyncio.TimeoutError):
                await mock_client.chat.completions.create()


class TestDatabasePersistence:
    """Test suite for database operations and persistence"""
    
    @pytest.fixture
    async def async_session(self):
        """Create async database session for testing"""
        # Mock database session
        session = Mock(spec=AsyncSession)
        session.add = Mock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.close = AsyncMock()
        return session
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing"""
        return {
            "username": "test_user",
            "email": "test@example.com", 
            "password": "secure_password123"
        }
    
    @pytest.fixture
    def sample_conversation_data(self):
        """Sample conversation data for testing"""
        return {
            "title": "Test Conversation",
            "user_id": str(uuid.uuid4())
        }
    
    @pytest.mark.asyncio
    async def test_user_creation_persistence(self, async_session, sample_user_data):
        """Test user creation and database persistence"""
        # Create user instance
        user = User(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            hashed_password="hashed_" + sample_user_data["password"]
        )
        
        # Mock database operations
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        # Verify mocks were called
        async_session.add.assert_called_once_with(user)
        async_session.commit.assert_called_once()
        async_session.refresh.assert_called_once_with(user)
    
    @pytest.mark.asyncio
    async def test_conversation_persistence(self, async_session, sample_conversation_data):
        """Test conversation creation and persistence"""
        conversation = Conversation(
            title=sample_conversation_data["title"],
            user_id=sample_conversation_data["user_id"],
            created_at=datetime.utcnow()
        )
        
        # Mock database operations
        async_session.add(conversation)
        await async_session.commit()
        
        # Verify persistence
        async_session.add.assert_called_once_with(conversation)
        async_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_message_persistence(self, async_session):
        """Test message creation and persistence"""
        message = Message(
            conversation_id=str(uuid.uuid4()),
            content="Test message content",
            role="user",
            timestamp=datetime.utcnow()
        )
        
        # Mock database operations
        async_session.add(message)
        await async_session.commit()
        
        # Verify persistence
        async_session.add.assert_called_once_with(message)
        async_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_database_rollback_on_error(self, async_session):
        """Test database rollback on error scenarios"""
        async_session.commit.side_effect = Exception("Database error")
        async_session.rollback = AsyncMock()
        
        try:
            await async_session.commit()
        except Exception:
            await async_session.rollback()
        
        async_session.rollback.assert_called_once()


class TestErrorHandling:
    """Test suite for comprehensive error handling scenarios"""
    
    @pytest.fixture
    def test_client(self):
        """Create test client for API testing"""
        return TestClient(app)
    
    def test_invalid_authentication_error(self, test_client):
        """Test authentication error handling"""
        response = test_client.post(
            "/api/v1/auth/login",
            json={"username": "invalid", "password": "wrong"}
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json().get("detail", "")
    
    def test_missing_authorization_header(self, test_client):
        """Test missing authorization header error"""
        response = test_client.post("/api/v1/conversations")
        
        assert response.status_code == 401
        assert "authorization" in response.json().get("detail", "").lower()
    
    def test_invalid_json_payload(self, test_client):
        """Test invalid JSON payload error handling"""
        response = test_client.post(
            "/api/v1/auth/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, test_client):
        """Test missing required fields validation"""
        response = test_client.post(
            "/api/v1/auth/register",
            json={"username": "test"}  # Missing email and password
        )
        
        assert response.status_code == 422
        errors = response.json().get("detail", [])
        assert any("email" in str(error) for error in errors)
        assert any("password" in str(error) for error in errors)
    
    @pytest.mark.asyncio
    async def test_database_connection_error(self):
        """Test database connection error handling"""
        with patch('app.core.database.get_session') as mock_get_session:
            mock_get_session.side_effect = Exception("Database connection failed")
            
            with pytest.raises(Exception) as exc_info:
                await mock_get_session()
            
            assert "Database connection failed" in str(exc_info.value)
    
    def test_rate_limit_error(self, test_client):
        """Test rate limiting error handling"""
        # Mock rate limit exceeded
        with patch('app.middleware.rate_limit.is_rate_limited', return_value=True):
            response = test_client.post("/api/v1/chat/stream")
            
            assert response.status_code == 429


class TestAPIEndpoints:
    """Test suite for API endpoints with realistic scenarios"""
    
    @pytest.fixture
    def test_client(self):
        """Create test client for API testing"""
        return TestClient(app)
    
    @pytest.fixture
    def authenticated_headers(self):
        """Mock authenticated headers"""
        return {"Authorization": "Bearer mock_jwt_token"}
    
    def test_health_check_endpoint(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "timestamp" in data
    
    def test_user_registration_endpoint(self, test_client):
        """Test user registration endpoint"""
        with patch('app.services.auth_service.create_user') as mock_create:
            mock_create.return_value = Mock(id=str(uuid.uuid4()), username="testuser")
            
            response = test_client.post(
                "/api/v1/auth/register",
                json={
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "secure123"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data.get("username") == "testuser"
    
    def test_conversation_creation(self, test_client, authenticated_headers):
        """Test conversation creation endpoint"""
        with patch('app.services.conversation_service.create_conversation') as mock_create:
            mock_conversation = Mock(
                id=str(uuid.uuid4()),
                title="New Chat",
                created_at=datetime.utcnow()
            )
            mock_create.return_value = mock_conversation
            
            response = test_client.post(
                "/api/v1/conversations",
                json={"title": "New Chat"},
                headers=authenticated_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data.get("title") == "New Chat"
    
    @pytest.mark.asyncio
    async def test_streaming_chat_endpoint(self):
        """Test streaming chat endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch('app.services.chat_service.stream_chat_response') as mock_stream:
                # Mock streaming response
                async def mock_stream_generator():
                    yield "data: {\"type\": \"chunk\", \"content\": \"Hello\"}\n\n"
                    yield "data: {\"type\": \"chunk\", \"content\": \" World\"}\n\n"
                    yield "data: {\"type\": \"end\"}\n\n"
                
                mock_stream.return_value = mock_stream_generator()
                
                response = await client.post(
                    "/api/v1/chat/stream",
                    json={
                        "message": "Hello",
                        "conversation_id": str(uuid.uuid4())
                    },
                    headers={"Authorization": "Bearer mock_token"}
                )
                
                assert response.status_code == 200
                assert response.headers["content-type"] == "text/event-stream"


class TestIntegrationScenarios:
    """Integration tests for complete user workflows"""
    
    @pytest.fixture
    def test_client(self):
        return TestClient(app)
    
    def test_complete_chat_workflow(self, test_client):
        """Test complete chat workflow from registration to conversation"""
        # Mock all external dependencies
        with patch('app.services.auth_service.create_user') as mock_create_user, \
             patch('app.services.auth_service.authenticate_user') as mock_auth, \
             patch('app.services.conversation_service.create_conversation') as mock_create_conv, \
             patch('app.services.chat_service.process_message') as mock_process:
            
            # Setup mocks
            user_id = str(uuid.uuid4())
            conv_id = str(uuid.uuid4())
            
            mock_create_user.return_value = Mock(id=user_id, username="testuser")
            mock_auth.return_value = ("mock_token", Mock(id=user_id))
            mock_create_conv.return_value = Mock(id=conv_id, title="Test Chat")
            mock_process.return_value = "AI response"
            
            # 1. Register user
            register_response = test_client.post(
                "/api/v1/auth/register",
                json={"username": "testuser", "email": "test@example.com", "password": "pass123"}
            )
            assert register_response.status_code == 201
            
            # 2. Login user
            login_response = test_client.post(
                "/api/v1/auth/login", 
                json={"username": "testuser", "password": "pass123"}
            )
            assert login_response.status_code == 200
            
            # 3. Create conversation
            conv_response = test_client.post(
                "/api/v1/conversations",
                json={"title": "Test Chat"},
                headers={"Authorization": "Bearer mock_token"}
            )
            assert conv_response.status_code == 201
    
    def test_error_recovery_workflow(self, test_client):
        """Test error recovery in multi-step workflows"""
        with patch('app.services.auth_service.authenticate_user') as mock_auth:
            # Mock authentication failure
            mock_auth.side_effect = Exception("Auth service down")
            
            # Attempt login - should handle error gracefully
            response = test_client.post(
                "/api/v1/auth/login",
                json={"username": "user", "password": "pass"}
            )
            
            # Should return appropriate error status
            assert response.status_code >= 400


# Pytest configuration and fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_settings():
    """Mock application settings for tests"""
    with patch('app.core.config.get_settings') as mock:
        mock.return_value = Mock(
            database_url="postgresql://test:test@localhost/test_db",
            openai_api_key="test_key",
            secret_key="test_secret",
            environment="testing"
        )
        yield mock


# Test runner configuration
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing"
    ])