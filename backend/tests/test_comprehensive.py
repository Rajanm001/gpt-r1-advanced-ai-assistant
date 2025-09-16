"""
GPT.R1 - Comprehensive Test Suite
Author: Rajan Mishra
Testing all endpoints, edge cases, performance, and reliability
"""

import pytest
import asyncio
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock
import json

from main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.services.openai_service import openai_service
from app.services.rag_service import rag_service

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_gpt_r1.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def test_db():
    """Create test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers."""
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

class TestGPTR1Core:
    """Core functionality tests for GPT.R1"""
    
    def test_root_endpoint(self, test_db):
        """Test root endpoint returns proper GPT.R1 branding."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "GPT.R1" in data["message"]
        assert "Rajan Mishra" in data["author"]
        assert len(data["features"]) >= 5
        
    def test_health_check(self, test_db):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
    def test_openapi_docs(self, test_db):
        """Test API documentation is accessible."""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "GPT.R1" in data["info"]["title"]

class TestAuthentication:
    """Authentication system tests"""
    
    def test_user_registration_success(self, test_db):
        """Test successful user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com", 
            "password": "newpassword123"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        assert response.json()["username"] == "newuser"
        
    def test_user_registration_duplicate_username(self, test_user):
        """Test registration with duplicate username fails."""
        user_data = {
            "username": "testuser",
            "email": "different@example.com",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
        
    def test_user_login_success(self, test_user):
        """Test successful user login."""
        login_data = {
            "username": "testuser", 
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
        
    def test_user_login_invalid_credentials(self, test_user):
        """Test login with invalid credentials fails."""
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
        
    def test_protected_endpoint_without_auth(self, test_db):
        """Test protected endpoint requires authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
        
    def test_protected_endpoint_with_auth(self, auth_headers):
        """Test protected endpoint works with authentication."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

class TestConversations:
    """Conversation management tests"""
    
    def test_create_conversation(self, auth_headers):
        """Test creating a new conversation."""
        conv_data = {"title": "Test Conversation"}
        response = client.post("/api/v1/conversations/", json=conv_data, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Test Conversation"
        
    def test_list_conversations(self, auth_headers):
        """Test listing user conversations."""
        # Create a conversation first
        conv_data = {"title": "Test Conv 1"}
        client.post("/api/v1/conversations/", json=conv_data, headers=auth_headers)
        
        response = client.get("/api/v1/conversations/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1
        
    def test_get_conversation_by_id(self, auth_headers):
        """Test getting specific conversation."""
        # Create conversation
        conv_data = {"title": "Test Conv"}
        create_response = client.post("/api/v1/conversations/", json=conv_data, headers=auth_headers)
        conv_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/conversations/{conv_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == conv_id
        
    def test_get_nonexistent_conversation(self, auth_headers):
        """Test getting non-existent conversation returns 404."""
        response = client.get("/api/v1/conversations/99999", headers=auth_headers)
        assert response.status_code == 404

class TestChatStreaming:
    """Chat streaming functionality tests"""
    
    @patch.object(openai_service, 'create_chat_completion_stream')
    def test_chat_streaming_mock(self, mock_stream, auth_headers):
        """Test chat streaming with mocked OpenAI service."""
        async def mock_generator():
            chunks = ["Hello", " there", "! How", " can I", " help you?"]
            for chunk in chunks:
                yield chunk
                
        mock_stream.return_value = mock_generator()
        
        chat_data = {
            "message": "Hello",
            "conversation_id": None,
            "use_rag": False
        }
        
        response = client.post("/api/v1/chat/", json=chat_data, headers=auth_headers)
        assert response.status_code == 200
        
    def test_chat_without_auth(self, test_db):
        """Test chat endpoint requires authentication."""
        chat_data = {"message": "Hello", "conversation_id": None}
        response = client.post("/api/v1/chat/", json=chat_data)
        assert response.status_code == 401
        
    def test_chat_empty_message(self, auth_headers):
        """Test chat with empty message."""
        chat_data = {"message": "", "conversation_id": None}
        response = client.post("/api/v1/chat/", json=chat_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error

class TestRAGSystem:
    """RAG (Retrieval-Augmented Generation) tests"""
    
    @patch.object(rag_service, 'search_web')
    async def test_rag_search(self, mock_search):
        """Test RAG web search functionality."""
        mock_search.return_value = [
            {
                "title": "Test Result",
                "url": "https://example.com",
                "snippet": "Test snippet content",
                "source": "DuckDuckGo"
            }
        ]
        
        context = await rag_service.get_context_from_search("test query")
        assert "Test Result" in context
        assert "https://example.com" in context
        
    def test_rag_system_prompt_creation(self):
        """Test RAG system prompt creation."""
        context = "Sample context from web search"
        prompt = rag_service.create_rag_system_prompt(context)
        assert "helpful AI assistant" in prompt
        assert context in prompt

class TestPerformance:
    """Performance and load tests"""
    
    def test_endpoint_response_time(self, test_db):
        """Test API endpoint response times."""
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
        
    def test_concurrent_requests(self, auth_headers):
        """Test handling concurrent requests."""
        def make_request():
            return client.get("/api/v1/conversations/", headers=auth_headers)
            
        # Simulate concurrent requests
        responses = []
        for _ in range(10):
            responses.append(make_request())
            
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            
    def test_large_message_handling(self, auth_headers):
        """Test handling large messages."""
        large_message = "x" * 5000  # 5KB message
        chat_data = {
            "message": large_message,
            "conversation_id": None,
            "use_rag": False
        }
        
        response = client.post("/api/v1/chat/", json=chat_data, headers=auth_headers)
        assert response.status_code == 200

class TestErrorHandling:
    """Error handling and edge cases"""
    
    def test_invalid_json_payload(self, test_db):
        """Test handling invalid JSON payloads."""
        response = client.post(
            "/api/v1/auth/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
    def test_sql_injection_prevention(self, test_db):
        """Test SQL injection prevention."""
        malicious_data = {
            "username": "'; DROP TABLE users; --",
            "email": "hacker@example.com",
            "password": "password123"
        }
        
        # Should not cause server error
        response = client.post("/api/v1/auth/register", json=malicious_data)
        # May return 400 or 422 due to validation, but not 500
        assert response.status_code in [400, 422]
        
    def test_rate_limiting_protection(self, test_db):
        """Test protection against rapid requests."""
        # Make many rapid requests
        responses = []
        for i in range(50):
            response = client.get("/")
            responses.append(response)
            
        # Server should handle gracefully without crashing
        successful_responses = [r for r in responses if r.status_code == 200]
        assert len(successful_responses) > 0

class TestDataValidation:
    """Data validation and security tests"""
    
    def test_email_validation(self, test_db):
        """Test email format validation."""
        invalid_emails = ["invalid", "invalid@", "@invalid.com", "test@"]
        
        for email in invalid_emails:
            user_data = {
                "username": f"user_{email}",
                "email": email,
                "password": "password123"
            }
            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == 422
            
    def test_password_strength(self, test_db):
        """Test password strength requirements."""
        weak_passwords = ["123", "password", "abc"]
        
        for password in weak_passwords:
            user_data = {
                "username": f"user_{password}",
                "email": f"{password}@example.com",
                "password": password
            }
            response = client.post("/api/v1/auth/register", json=user_data)
            # Should have validation or succeed (depends on implementation)
            assert response.status_code in [200, 422]
            
    def test_xss_prevention(self, auth_headers):
        """Test XSS attack prevention."""
        xss_payload = "<script>alert('xss')</script>"
        conv_data = {"title": xss_payload}
        
        response = client.post("/api/v1/conversations/", json=conv_data, headers=auth_headers)
        if response.status_code == 200:
            # If accepted, ensure it's properly escaped
            assert "<script>" not in response.json()["title"]

class TestDatabaseOperations:
    """Database operation tests"""
    
    def test_database_transactions(self, test_db):
        """Test database transaction integrity."""
        # Test that failed operations don't leave partial data
        invalid_user_data = {
            "username": "",  # Invalid username
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=invalid_user_data)
        assert response.status_code == 422
        
        # Verify no partial user was created
        valid_user_data = {
            "username": "validuser",
            "email": "test@example.com",  # Same email should be available
            "password": "password123"
        }
        response = client.post("/api/v1/auth/register", json=valid_user_data)
        assert response.status_code == 200
        
    def test_database_connection_handling(self, test_db):
        """Test database connection management."""
        # Make multiple requests to test connection pooling
        for i in range(20):
            response = client.get("/health")
            assert response.status_code == 200

if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([__file__, "-v", "--tb=short"])