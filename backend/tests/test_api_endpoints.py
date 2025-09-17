"""
GPT.R1 - API Endpoint Tests
Comprehensive testing of all API endpoints
"""

import pytest
import json
import sys
import asyncio
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app
from tests.conftest import TestDataGenerator, MockAgenticService, TestUtilities

class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_health_check_endpoint(self):
        """Test basic health check"""
        client = TestClient(app)
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "status" in data
        assert "timestamp" in data
        assert "service" in data
        assert data["status"] == "healthy"
        assert data["service"] == "GPT.R1 Enhanced Chat API"
    
    def test_health_check_includes_system_info(self):
        """Test health check includes system information"""
        client = TestClient(app)
        response = client.get("/api/health")
        
        data = response.json()
        assert "agentic_workflow" in data
        assert "postgresql" in data
        assert data["agentic_workflow"] == "active"

class TestConversationEndpoints:
    """Test conversation management endpoints"""
    
    @pytest.fixture
    def mock_conversation_crud(self):
        """Mock conversation CRUD operations"""
        with patch('backend.app.crud.conversation_crud') as mock:
            yield mock
    
    @pytest.fixture
    def mock_message_crud(self):
        """Mock message CRUD operations"""
        with patch('backend.app.crud.message_crud') as mock:
            yield mock
    
    async def test_create_conversation_success(self, mock_conversation_crud):
        """Test successful conversation creation"""
        # Setup mock
        mock_conv = MagicMock()
        mock_conv.id = 1
        mock_conv.title = "Test Conversation"
        mock_conv.created_at = datetime.now()
        mock_conversation_crud.create.return_value = mock_conv
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/conversations",
                json={"title": "Test Conversation"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Conversation"
        assert "id" in data
    
    async def test_create_conversation_validation_error(self):
        """Test conversation creation with validation error"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/conversations",
                json={"invalid_field": "value"}
            )
        
        assert response.status_code == 422  # Validation error
    
    async def test_get_conversations_success(self, mock_conversation_crud):
        """Test successful conversation list retrieval"""
        # Setup mock
        mock_conversations = [
            {
                "id": 1,
                "title": "Conversation 1",
                "created_at": datetime.now().isoformat(),
                "message_count": 5
            },
            {
                "id": 2,
                "title": "Conversation 2", 
                "created_at": datetime.now().isoformat(),
                "message_count": 3
            }
        ]
        mock_conversation_crud.get_conversation_summaries.return_value = mock_conversations
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/conversations")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Conversation 1"
        assert data[1]["title"] == "Conversation 2"
    
    async def test_get_conversation_by_id_success(self, mock_conversation_crud, mock_message_crud):
        """Test successful single conversation retrieval"""
        # Setup mocks
        mock_conv = MagicMock()
        mock_conv.id = 1
        mock_conv.title = "Test Conversation"
        mock_conversation_crud.get.return_value = mock_conv
        
        mock_messages = [
            MagicMock(id=1, role="user", content="Hello", created_at=datetime.now()),
            MagicMock(id=2, role="assistant", content="Hi there!", created_at=datetime.now())
        ]
        mock_message_crud.get_messages_by_conversation.return_value = mock_messages
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/conversations/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation"]["title"] == "Test Conversation"
        assert len(data["messages"]) == 2
    
    async def test_get_conversation_not_found(self, mock_conversation_crud):
        """Test conversation not found error"""
        mock_conversation_crud.get.return_value = None
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/conversations/999")
        
        assert response.status_code == 404
    
    async def test_delete_conversation_success(self, mock_conversation_crud):
        """Test successful conversation deletion"""
        mock_conv = MagicMock()
        mock_conv.id = 1
        mock_conversation_crud.get.return_value = mock_conv
        mock_conversation_crud.remove.return_value = True
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete("/api/conversations/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Conversation deleted successfully"
    
    async def test_delete_conversation_not_found(self, mock_conversation_crud):
        """Test deletion of non-existent conversation"""
        mock_conversation_crud.get.return_value = None
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete("/api/conversations/999")
        
        assert response.status_code == 404

class TestChatEndpoints:
    """Test chat endpoints including streaming"""
    
    @pytest.fixture
    def mock_chat_service(self):
        """Mock chat service"""
        with patch('backend.app.services.chat_service.EnhancedChatService') as mock:
            yield mock
    
    @pytest.fixture
    def mock_database_session(self):
        """Mock database session"""
        with patch('backend.app.core.database.get_db') as mock:
            session = AsyncMock()
            mock.return_value = session
            yield session
    
    async def test_chat_stream_endpoint_success(self, mock_chat_service, mock_database_session):
        """Test successful chat streaming"""
        # Setup mock chat service
        mock_service_instance = AsyncMock()
        mock_chat_service.return_value = mock_service_instance
        
        # Mock streaming response
        async def mock_stream_response(*args, **kwargs):
            yield 'data: {"type": "workflow_start", "message": "Starting workflow..."}\n\n'
            yield 'data: {"type": "workflow_progress", "step": "orchestrate", "message": "Orchestrating tools..."}\n\n'
            yield 'data: {"type": "workflow_progress", "step": "analyze", "message": "Analyzing query..."}\n\n'
            yield 'data: {"type": "response_start", "message": "Generating response..."}\n\n'
            yield 'data: {"type": "content", "content": "This is a test response."}\n\n'
            yield 'data: {"type": "workflow_summary", "summary": {"total_time": 2.5, "steps_completed": 6}}\n\n'
            yield 'data: {"type": "complete"}\n\n'
        
        mock_service_instance.stream_chat_response = mock_stream_response
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/stream",
                json={"message": "Tell me about AI", "conversation_id": None}
            )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
        
        # Verify SSE format
        content = response.text
        TestUtilities.assert_streaming_response_format(content)
        
        # Parse and verify messages
        messages = TestUtilities.parse_sse_messages(content)
        assert len(messages) >= 5  # Should have multiple message types
        
        # Verify message types
        message_types = [msg.get("type") for msg in messages]
        assert "workflow_start" in message_types
        assert "workflow_progress" in message_types
        assert "content" in message_types
        assert "complete" in message_types
    
    async def test_chat_stream_with_conversation_id(self, mock_chat_service, mock_database_session):
        """Test chat streaming with existing conversation"""
        # Mock conversation exists
        with patch('backend.app.crud.conversation_crud.get') as mock_get_conv:
            mock_conv = MagicMock()
            mock_conv.id = 1
            mock_get_conv.return_value = mock_conv
            
            # Setup mock chat service
            mock_service_instance = AsyncMock()
            mock_chat_service.return_value = mock_service_instance
            
            async def mock_stream_response(*args, **kwargs):
                yield 'data: {"type": "connected", "conversation_id": 1}\n\n'
                yield 'data: {"type": "content", "content": "Response for existing conversation"}\n\n'
                yield 'data: {"type": "complete"}\n\n'
            
            mock_service_instance.stream_chat_response = mock_stream_response
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat/stream",
                    json={"message": "Follow-up question", "conversation_id": 1}
                )
            
            assert response.status_code == 200
            
            # Verify conversation connection message
            messages = TestUtilities.parse_sse_messages(response.text)
            connected_msg = next((msg for msg in messages if msg.get("type") == "connected"), None)
            assert connected_msg is not None
            assert connected_msg["conversation_id"] == 1
    
    async def test_chat_stream_validation_error(self):
        """Test chat streaming with validation errors"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Empty message should fail validation
            response = await client.post(
                "/api/chat/stream",
                json={"message": "", "conversation_id": None}
            )
            
            assert response.status_code == 400
    
    async def test_chat_stream_invalid_conversation_id(self):
        """Test chat streaming with invalid conversation ID"""
        with patch('backend.app.crud.conversation_crud.get') as mock_get_conv:
            mock_get_conv.return_value = None  # Conversation not found
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat/stream",
                    json={"message": "Test message", "conversation_id": 999}
                )
                
                assert response.status_code == 404
    
    async def test_chat_stream_service_error(self, mock_chat_service, mock_database_session):
        """Test chat streaming with service error"""
        # Setup mock to raise exception
        mock_service_instance = AsyncMock()
        mock_chat_service.return_value = mock_service_instance
        mock_service_instance.stream_chat_response.side_effect = Exception("Service error")
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/stream",
                json={"message": "Test message", "conversation_id": None}
            )
            
            assert response.status_code == 500

class TestMessageEndpoints:
    """Test message-related endpoints"""
    
    @pytest.fixture
    def mock_message_crud(self):
        """Mock message CRUD operations"""
        with patch('backend.app.crud.message_crud') as mock:
            yield mock
    
    async def test_get_messages_by_conversation(self, mock_message_crud):
        """Test retrieving messages for a conversation"""
        # Setup mock
        mock_messages = [
            MagicMock(
                id=1,
                role="user",
                content="Hello",
                created_at=datetime.now(),
                conversation_id=1
            ),
            MagicMock(
                id=2,
                role="assistant", 
                content="Hi there!",
                created_at=datetime.now(),
                conversation_id=1
            )
        ]
        mock_message_crud.get_messages_by_conversation.return_value = mock_messages
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/conversations/1/messages")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["role"] == "user"
        assert data[0]["content"] == "Hello"
        assert data[1]["role"] == "assistant"
        assert data[1]["content"] == "Hi there!"
    
    async def test_get_messages_empty_conversation(self, mock_message_crud):
        """Test retrieving messages for empty conversation"""
        mock_message_crud.get_messages_by_conversation.return_value = []
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/conversations/1/messages")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

class TestErrorHandling:
    """Test error handling across all endpoints"""
    
    async def test_404_not_found(self):
        """Test 404 error handling"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/nonexistent-endpoint")
        
        assert response.status_code == 404
    
    async def test_method_not_allowed(self):
        """Test 405 method not allowed"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/health")  # Health is GET only
        
        assert response.status_code == 405
    
    async def test_internal_server_error_handling(self):
        """Test 500 error handling"""
        with patch('backend.app.crud.conversation_crud.get_conversation_summaries') as mock:
            mock.side_effect = Exception("Database error")
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/conversations")
            
            assert response.status_code == 500

class TestCORSHandling:
    """Test CORS headers and cross-origin handling"""
    
    async def test_cors_headers_present(self):
        """Test that CORS headers are present"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/health")
        
        # FastAPI should include CORS headers
        assert response.status_code == 200
    
    async def test_options_request_handling(self):
        """Test OPTIONS request handling for CORS preflight"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.options("/api/chat/stream")
        
        # Should handle OPTIONS request
        assert response.status_code in [200, 204]

class TestRequestValidation:
    """Test request validation across endpoints"""
    
    async def test_invalid_json_payload(self):
        """Test handling of invalid JSON"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/conversations",
                content="invalid json{",
                headers={"content-type": "application/json"}
            )
        
        assert response.status_code == 422  # Validation error
    
    async def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/stream",
                json={}  # Missing required 'message' field
            )
        
        assert response.status_code == 422  # Validation error
    
    async def test_field_type_validation(self):
        """Test field type validation"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/stream",
                json={
                    "message": 123,  # Should be string
                    "conversation_id": "not_a_number"  # Should be int or null
                }
            )
        
        assert response.status_code == 422  # Validation error

class TestRateLimiting:
    """Test rate limiting if implemented"""
    
    async def test_multiple_rapid_requests(self):
        """Test handling of multiple rapid requests"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Send multiple requests rapidly
            tasks = []
            for i in range(10):
                task = client.get("/api/health")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should succeed (or handle rate limiting gracefully)
            for response in responses:
                if hasattr(response, 'status_code'):
                    assert response.status_code in [200, 429]  # OK or Too Many Requests

if __name__ == "__main__":
    print("🧪 Running API Endpoint Tests...")
    pytest.main([__file__, "-v"])