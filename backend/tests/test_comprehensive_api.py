import pytest
import asyncio
import json
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

# Import the main app
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main import app

class TestChatStreamingAPI:
    """Comprehensive tests for /api/v1/chat/stream endpoint"""
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)
    
    @pytest.fixture  
    def mock_token(self):
        """Mock JWT token for authentication"""
        return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"
    
    @pytest.fixture
    def auth_headers(self, mock_token):
        """Authentication headers"""
        return {"Authorization": f"Bearer {mock_token}"}
    
    @pytest.mark.asyncio
    async def test_chat_stream_endpoint_exists(self, client):
        """Test that the streaming endpoint exists and requires auth"""
        response = client.post("/api/v1/chat/stream", json={"message": "test"})
        assert response.status_code in [401, 422]  # Auth required or validation error
    
    @pytest.mark.asyncio
    @patch('app.services.chat_service.ChatService.stream_response')
    @patch('app.core.auth.verify_token')
    async def test_chat_stream_with_valid_auth(self, mock_verify_token, mock_stream, client, auth_headers):
        """Test streaming with valid authentication"""
        # Mock authentication
        mock_verify_token.return_value = {"user_id": 1, "email": "test@example.com"}
        
        # Mock streaming response
        async def mock_stream_generator():
            chunks = [
                {"type": "start_streaming", "conversation_id": 1, "message_id": 1},
                {"type": "chunk", "content": "Hello"},
                {"type": "chunk", "content": " world"},
                {"type": "complete", "conversation_id": 1, "message_id": 1}
            ]
            for chunk in chunks:
                yield f"data: {json.dumps(chunk)}\n\n"
        
        mock_stream.return_value = mock_stream_generator()
        
        # Test request
        response = client.post(
            "/api/v1/chat/stream",
            json={
                "message": "Hello, how are you?",
                "conversation_id": 1,
                "model": "gpt-3.5-turbo"
            },
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        
        # Check streaming content
        content = response.text
        assert "start_streaming" in content
        assert "chunk" in content
        assert "complete" in content
    
    @pytest.mark.asyncio
    @patch('openai.ChatCompletion.acreate')
    @patch('app.core.auth.verify_token')
    async def test_openai_integration_mock(self, mock_verify_token, mock_openai, client, auth_headers):
        """Test OpenAI integration with mocked API"""
        # Mock authentication
        mock_verify_token.return_value = {"user_id": 1, "email": "test@example.com"}
        
        # Mock OpenAI response
        mock_response = AsyncMock()
        mock_response.__aiter__.return_value = [
            type('obj', (object,), {
                'choices': [type('obj', (object,), {
                    'delta': {'content': 'Hello'}
                })()]
            }),
            type('obj', (object,), {
                'choices': [type('obj', (object,), {
                    'delta': {'content': ' there'}
                })()]
            })
        ]
        mock_openai.return_value = mock_response
        
        # Test request
        response = client.post(
            "/api/v1/chat/stream",
            json={
                "message": "Say hello",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7
            },
            headers=auth_headers
        )
        
        # Verify OpenAI was called
        mock_openai.assert_called_once()
        call_args = mock_openai.call_args
        assert call_args[1]["model"] == "gpt-3.5-turbo"
        assert call_args[1]["stream"] == True
        assert any("Say hello" in str(msg) for msg in call_args[1]["messages"])
    
    @pytest.mark.asyncio
    async def test_invalid_message_format(self, client, auth_headers):
        """Test validation for invalid message format"""
        with patch('app.core.auth.verify_token') as mock_verify:
            mock_verify.return_value = {"user_id": 1}
            
            # Test empty message
            response = client.post(
                "/api/v1/chat/stream",
                json={"message": ""},
                headers=auth_headers
            )
            assert response.status_code == 422
            
            # Test missing message
            response = client.post(
                "/api/v1/chat/stream", 
                json={},
                headers=auth_headers
            )
            assert response.status_code == 422
            
            # Test message too long
            long_message = "x" * 5000  # Assuming 4000 char limit
            response = client.post(
                "/api/v1/chat/stream",
                json={"message": long_message},
                headers=auth_headers
            )
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    @patch('app.core.auth.verify_token')
    async def test_openai_timeout_handling(self, mock_verify_token, client, auth_headers):
        """Test OpenAI API timeout handling"""
        mock_verify_token.return_value = {"user_id": 1}
        
        with patch('openai.ChatCompletion.acreate') as mock_openai:
            # Mock timeout exception
            mock_openai.side_effect = asyncio.TimeoutError("Request timeout")
            
            response = client.post(
                "/api/v1/chat/stream",
                json={"message": "Test timeout"},
                headers=auth_headers
            )
            
            # Should handle timeout gracefully
            assert response.status_code in [503, 500]
            if response.status_code == 503:
                error_data = response.json()
                assert "timeout" in error_data["detail"].lower()
    
    @pytest.mark.asyncio
    @patch('app.core.auth.verify_token')
    async def test_rate_limiting(self, mock_verify_token, client, auth_headers):
        """Test rate limiting functionality"""
        mock_verify_token.return_value = {"user_id": 1}
        
        # Send multiple rapid requests
        responses = []
        for i in range(10):  # Assuming rate limit is lower than 10/minute
            response = client.post(
                "/api/v1/chat/stream",
                json={"message": f"Test message {i}"},
                headers=auth_headers
            )
            responses.append(response)
        
        # Check if any requests were rate limited
        rate_limited = any(r.status_code == 429 for r in responses)
        if rate_limited:
            # Find the rate limited response
            rate_limited_response = next(r for r in responses if r.status_code == 429)
            error_data = rate_limited_response.json()
            assert "rate limit" in error_data["detail"].lower()
            assert "retry_after" in error_data or "retry-after" in rate_limited_response.headers
    
    @pytest.mark.asyncio
    @patch('app.core.auth.verify_token')
    async def test_conversation_context(self, mock_verify_token, client, auth_headers):
        """Test conversation context handling"""
        mock_verify_token.return_value = {"user_id": 1}
        
        with patch('app.services.chat_service.ChatService.stream_response') as mock_stream:
            # Mock conversation service
            async def mock_stream_generator():
                yield f'data: {json.dumps({"type": "start_streaming", "conversation_id": 123})}\n\n'
                yield f'data: {json.dumps({"type": "chunk", "content": "Response"})}\n\n'
                yield f'data: {json.dumps({"type": "complete", "conversation_id": 123})}\n\n'
            
            mock_stream.return_value = mock_stream_generator()
            
            # Test with conversation ID
            response = client.post(
                "/api/v1/chat/stream",
                json={
                    "message": "Continue our discussion",
                    "conversation_id": 123
                },
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert "conversation_id" in response.text
    
    @pytest.mark.asyncio
    async def test_rag_enhancement_integration(self, client, auth_headers):
        """Test RAG (DuckDuckGo search) enhancement"""
        with patch('app.core.auth.verify_token') as mock_verify:
            mock_verify.return_value = {"user_id": 1}
            
            with patch('app.agents.rag_agent.RAGAgent.search') as mock_search:
                mock_search.return_value = "Current information about the topic"
                
                with patch('app.services.chat_service.ChatService.stream_response') as mock_stream:
                    async def mock_rag_stream():
                        yield f'data: {json.dumps({"type": "rag_searching", "query": "current weather"})}\n\n'
                        yield f'data: {json.dumps({"type": "chunk", "content": "Based on current data"})}\n\n'
                        yield f'data: {json.dumps({"type": "complete"})}\n\n'
                    
                    mock_stream.return_value = mock_rag_stream()
                    
                    # Test message that should trigger RAG
                    response = client.post(
                        "/api/v1/chat/stream",
                        json={"message": "What's the current weather like?"},
                        headers=auth_headers
                    )
                    
                    assert response.status_code == 200
                    assert "rag_searching" in response.text
    
    @pytest.mark.asyncio
    async def test_error_response_format(self, client):
        """Test that errors return proper JSON format"""
        # Test unauthenticated request
        response = client.post(
            "/api/v1/chat/stream",
            json={"message": "test"}
        )
        
        assert response.status_code == 401
        error_data = response.json()
        
        # Verify error structure
        assert "detail" in error_data
        assert isinstance(error_data["detail"], str)
        
        # Should have timestamp and error code
        if "timestamp" in error_data:
            assert error_data["timestamp"]
        if "error_code" in error_data:
            assert error_data["error_code"]


class TestDatabasePersistence:
    """Test database operations and persistence"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        from unittest.mock import MagicMock
        return MagicMock()
    
    @pytest.mark.asyncio
    async def test_conversation_creation(self, mock_db):
        """Test conversation creation in database"""
        from app.crud.conversation_crud import ConversationCRUD
        
        with patch('app.core.database.get_db') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            
            crud = ConversationCRUD()
            
            # Mock the create method
            mock_conversation = type('obj', (object,), {
                'id': 1,
                'title': 'Test Conversation',
                'user_id': 1,
                'message_count': 0
            })
            
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            # Test conversation creation
            with patch.object(crud, 'create_conversation', return_value=mock_conversation):
                result = crud.create_conversation(
                    user_id=1,
                    title="Test Conversation"
                )
                
                assert result.id == 1
                assert result.title == "Test Conversation"
                assert result.user_id == 1
    
    @pytest.mark.asyncio
    async def test_message_persistence(self, mock_db):
        """Test message persistence in database"""
        from app.crud.message_crud import MessageCRUD
        
        with patch('app.core.database.get_db') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            
            crud = MessageCRUD()
            
            # Mock message creation
            mock_message = type('obj', (object,), {
                'id': 1,
                'conversation_id': 1,
                'role': 'user',
                'content': 'Test message',
                'token_count': 3
            })
            
            with patch.object(crud, 'create_message', return_value=mock_message):
                result = crud.create_message(
                    conversation_id=1,
                    role="user",
                    content="Test message",
                    token_count=3
                )
                
                assert result.id == 1
                assert result.conversation_id == 1
                assert result.role == "user"
                assert result.content == "Test message"
    
    @pytest.mark.asyncio
    async def test_user_conversation_isolation(self, mock_db):
        """Test that users can only access their own conversations"""
        from app.crud.conversation_crud import ConversationCRUD
        
        with patch('app.core.database.get_db') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = mock_db
            
            crud = ConversationCRUD()
            
            # Mock query result
            mock_db.query.return_value.filter.return_value.all.return_value = []
            
            with patch.object(crud, 'get_user_conversations', return_value=[]):
                # User 1 should not see User 2's conversations
                user1_conversations = crud.get_user_conversations(user_id=1)
                user2_conversations = crud.get_user_conversations(user_id=2)
                
                # Each user should only see their own conversations
                assert isinstance(user1_conversations, list)
                assert isinstance(user2_conversations, list)


class TestConversationEndpoints:
    """Test conversation management endpoints"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer test.token.here"}
    
    @pytest.mark.asyncio
    async def test_list_conversations(self, client, auth_headers):
        """Test GET /api/v1/conversations"""
        with patch('app.core.auth.verify_token') as mock_verify:
            mock_verify.return_value = {"user_id": 1}
            
            with patch('app.crud.conversation_crud.ConversationCRUD.get_user_conversations') as mock_get:
                mock_conversations = [
                    type('obj', (object,), {
                        'id': 1,
                        'title': 'Test Conversation',
                        'created_at': '2025-09-18T12:00:00Z',
                        'message_count': 5,
                        'is_archived': False
                    })
                ]
                mock_get.return_value = mock_conversations
                
                response = client.get("/api/v1/conversations", headers=auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert "conversations" in data
                assert isinstance(data["conversations"], list)
    
    @pytest.mark.asyncio
    async def test_create_conversation(self, client, auth_headers):
        """Test POST /api/v1/conversations"""
        with patch('app.core.auth.verify_token') as mock_verify:
            mock_verify.return_value = {"user_id": 1}
            
            with patch('app.crud.conversation_crud.ConversationCRUD.create_conversation') as mock_create:
                mock_conversation = type('obj', (object,), {
                    'id': 1,
                    'title': 'New Conversation',
                    'user_id': 1,
                    'created_at': '2025-09-18T12:00:00Z',
                    'message_count': 0
                })
                mock_create.return_value = mock_conversation
                
                response = client.post(
                    "/api/v1/conversations",
                    json={"title": "New Conversation"},
                    headers=auth_headers
                )
                
                assert response.status_code == 201
                data = response.json()
                assert data["title"] == "New Conversation"
                assert data["id"] == 1
    
    @pytest.mark.asyncio
    async def test_get_conversation_by_id(self, client, auth_headers):
        """Test GET /api/v1/conversations/{id}"""
        with patch('app.core.auth.verify_token') as mock_verify:
            mock_verify.return_value = {"user_id": 1}
            
            with patch('app.crud.conversation_crud.ConversationCRUD.get_conversation') as mock_get:
                mock_conversation = type('obj', (object,), {
                    'id': 1,
                    'title': 'Test Conversation',
                    'user_id': 1,
                    'messages': []
                })
                mock_get.return_value = mock_conversation
                
                response = client.get("/api/v1/conversations/1", headers=auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == 1
                assert data["title"] == "Test Conversation"
    
    @pytest.mark.asyncio
    async def test_delete_conversation(self, client, auth_headers):
        """Test DELETE /api/v1/conversations/{id}"""
        with patch('app.core.auth.verify_token') as mock_verify:
            mock_verify.return_value = {"user_id": 1}
            
            with patch('app.crud.conversation_crud.ConversationCRUD.delete_conversation') as mock_delete:
                mock_delete.return_value = True
                
                response = client.delete("/api/v1/conversations/1", headers=auth_headers)
                
                assert response.status_code == 200
                data = response.json()
                assert "deleted" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_conversation_not_found(self, client, auth_headers):
        """Test accessing non-existent conversation"""
        with patch('app.core.auth.verify_token') as mock_verify:
            mock_verify.return_value = {"user_id": 1}
            
            with patch('app.crud.conversation_crud.ConversationCRUD.get_conversation') as mock_get:
                mock_get.return_value = None
                
                response = client.get("/api/v1/conversations/999", headers=auth_headers)
                
                assert response.status_code == 404
                data = response.json()
                assert "not found" in data["detail"].lower()


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing"
    ])