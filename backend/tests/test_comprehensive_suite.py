"""
GPT.R1 - Comprehensive Test Suite
Tests all functionality including streaming, orchestration, and database operations
Created by: Rajan Mishra
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

# Import our application
from backend.main import app
from backend.app.core.database import get_db, Base
from backend.app.services.chat_service import EnhancedChatService
from backend.app.services.agentic_service import AdvancedAgenticService
from backend.app.services.multi_tool_orchestrator import AdvancedToolOrchestrator
from backend.app.schemas.chat import ChatRequest, MessageCreate
from backend.app.crud import conversation_crud, message_crud

# Test database setup
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5432/test_gpt_r1_db"

class TestConfig:
    """Test configuration"""
    DATABASE_URL = SQLALCHEMY_DATABASE_URL
    OPENAI_API_KEY = "test-key"
    TEST_MODE = True

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_engine():
    """Create test database engine"""
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=False,
        future=True
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
async def async_session(async_engine):
    """Create test database session"""
    async_session_maker = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session

@pytest.fixture
async def override_get_db(async_session):
    """Override database dependency for testing"""
    def _override_get_db():
        yield async_session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

class TestHealthEndpoint:
    """Test health check functionality"""
    
    def test_health_check(self, client):
        """Test basic health check"""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "GPT.R1 Enhanced Chat API"
        assert data["agentic_workflow"] == "active"
        assert data["postgresql"] == "connected"

class TestDatabaseOperations:
    """Test database CRUD operations"""
    
    async def test_conversation_creation(self, async_session, override_get_db):
        """Test conversation creation"""
        from backend.app.schemas.chat import ConversationCreate
        
        conversation_data = ConversationCreate(title="Test Conversation")
        conversation = await conversation_crud.create(async_session, obj_in=conversation_data)
        
        assert conversation.id is not None
        assert conversation.title == "Test Conversation"
        assert conversation.created_at is not None
    
    async def test_message_creation(self, async_session, override_get_db):
        """Test message creation"""
        from backend.app.schemas.chat import ConversationCreate
        
        # Create conversation first
        conversation_data = ConversationCreate(title="Test Conversation")
        conversation = await conversation_crud.create(async_session, obj_in=conversation_data)
        
        # Create message
        message_data = MessageCreate(
            conversation_id=conversation.id,
            content="Test message",
            role="user"
        )
        message = await message_crud.create(async_session, obj_in=message_data)
        
        assert message.id is not None
        assert message.content == "Test message"
        assert message.role == "user"
        assert message.conversation_id == conversation.id
    
    async def test_conversation_history_retrieval(self, async_session, override_get_db):
        """Test conversation history retrieval"""
        from backend.app.schemas.chat import ConversationCreate
        
        # Create conversation
        conversation_data = ConversationCreate(title="Test Conversation")
        conversation = await conversation_crud.create(async_session, obj_in=conversation_data)
        
        # Create multiple messages
        messages_data = [
            MessageCreate(conversation_id=conversation.id, content="Hello", role="user"),
            MessageCreate(conversation_id=conversation.id, content="Hi there!", role="assistant"),
            MessageCreate(conversation_id=conversation.id, content="How are you?", role="user")
        ]
        
        for msg_data in messages_data:
            await message_crud.create(async_session, obj_in=msg_data)
        
        # Retrieve messages
        messages = await message_crud.get_messages_by_conversation(
            async_session, conversation_id=conversation.id
        )
        
        assert len(messages) == 3
        assert messages[0].content == "Hello"
        assert messages[1].content == "Hi there!"
        assert messages[2].content == "How are you?"

class TestAgenticService:
    """Test advanced agentic service functionality"""
    
    @pytest.fixture
    def agentic_service(self):
        """Create agentic service instance"""
        return AdvancedAgenticService()
    
    async def test_agentic_workflow_execution(self, agentic_service):
        """Test complete agentic workflow execution"""
        with patch.object(agentic_service.rag_service, 'get_context_from_search') as mock_search:
            mock_search.return_value = "Mocked search results about testing"
            
            workflow = await agentic_service.execute_agentic_workflow(
                user_query="Tell me about software testing",
                conversation_history=[]
            )
            
            assert workflow is not None
            assert workflow.workflow_id is not None
            assert len(workflow.steps) >= 5  # Should have all workflow steps
            assert workflow.user_query == "Tell me about software testing"
    
    async def test_workflow_with_orchestration(self, agentic_service):
        """Test workflow with multi-tool orchestration"""
        with patch.object(agentic_service.orchestrator, 'orchestrate_workflow') as mock_orchestrate:
            mock_orchestrate.return_value = {
                "success": True,
                "workflow_id": "test_workflow_123",
                "tools_orchestrated": 4,
                "execution_time": 2.5,
                "final_result": {"integrated_insights": ["Insight 1", "Insight 2"]},
                "quality_validation": {"quality_score": 0.9},
                "tool_breakdown": {"WebSearchTool": {"success": True}, "AnalysisTool": {"success": True}}
            }
            
            workflow = await agentic_service.execute_agentic_workflow(
                user_query="Complex query requiring orchestration",
                conversation_history=[]
            )
            
            # Check orchestration step
            orchestrate_step = next((s for s in workflow.steps if s.step_type.value == "orchestrate"), None)
            assert orchestrate_step is not None
            assert orchestrate_step.success
            assert orchestrate_step.output_data["orchestration_successful"]
            assert orchestrate_step.output_data["tools_orchestrated"] == 4
    
    async def test_workflow_error_handling(self, agentic_service):
        """Test workflow error handling"""
        with patch.object(agentic_service, '_step_analyze_query') as mock_analyze:
            mock_analyze.side_effect = Exception("Test error")
            
            workflow = await agentic_service.execute_agentic_workflow(
                user_query="Test query",
                conversation_history=[]
            )
            
            assert not workflow.success
            assert "error" in workflow.final_response.lower()

class TestMultiToolOrchestrator:
    """Test multi-tool orchestration system"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        return AdvancedToolOrchestrator()
    
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert len(orchestrator.tools) == 4  # Should have 4 tools
        assert "WebSearchTool" in orchestrator.tools
        assert "AnalysisTool" in orchestrator.tools
        assert "SynthesisTool" in orchestrator.tools
        assert "ValidationTool" in orchestrator.tools
    
    async def test_tool_orchestration_workflow(self, orchestrator):
        """Test complete tool orchestration workflow"""
        with patch.object(orchestrator.tools["WebSearchTool"], 'execute') as mock_search:
            mock_search.return_value = AsyncMock(
                success=True,
                result="Search results",
                confidence=0.9,
                execution_time=1.0
            )
            
            result = await orchestrator.orchestrate_workflow(
                "Tell me about artificial intelligence",
                {"conversation_history": [], "sources": []}
            )
            
            assert result["success"]
            assert result["tools_orchestrated"] > 0
            assert "final_result" in result
            assert "quality_validation" in result
    
    async def test_tool_selection_algorithm(self, orchestrator):
        """Test intelligent tool selection"""
        from backend.app.services.multi_tool_orchestrator import ToolRequest, ToolType, ToolPriority
        
        request = ToolRequest(
            tool_type=ToolType.SEARCH,
            input_data={"query": "current news about AI"},
            priority=ToolPriority.HIGH
        )
        
        selected_tool = orchestrator._select_best_tool(request)
        assert selected_tool is not None
        assert selected_tool.name == "WebSearchTool"
    
    async def test_orchestrator_statistics(self, orchestrator):
        """Test orchestrator statistics"""
        stats = orchestrator.get_orchestrator_statistics()
        assert "total_workflows" in stats
        assert "tools_available" in stats
        assert stats["tools_available"] == 4

class TestChatService:
    """Test enhanced chat service"""
    
    @pytest.fixture
    def chat_service(self):
        """Create chat service instance"""
        return EnhancedChatService()
    
    async def test_chat_service_initialization(self, chat_service):
        """Test chat service initialization"""
        assert chat_service.openai_service is not None
        assert chat_service.agentic_service is not None
    
    async def test_conversation_history_retrieval(self, chat_service, async_session):
        """Test conversation history retrieval"""
        # Mock database session
        with patch.object(message_crud, 'get_messages_by_conversation') as mock_get_messages:
            mock_messages = [
                MagicMock(role="user", content="Hello", created_at=datetime.now()),
                MagicMock(role="assistant", content="Hi!", created_at=datetime.now())
            ]
            mock_get_messages.return_value = mock_messages
            
            history = await chat_service._get_conversation_history(1, async_session)
            
            assert len(history) == 2
            assert history[0]["role"] == "user"
            assert history[0]["content"] == "Hello"
            assert history[1]["role"] == "assistant"
            assert history[1]["content"] == "Hi!"

class TestStreamingAPI:
    """Test streaming API functionality"""
    
    async def test_streaming_endpoint_basic(self, async_client, override_get_db):
        """Test basic streaming endpoint functionality"""
        # Mock the services to avoid external API calls
        with patch('backend.app.services.chat_service.EnhancedChatService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            # Mock streaming response
            async def mock_stream_response(*args, **kwargs):
                yield 'data: {"type": "workflow_start", "message": "Starting..."}\n\n'
                yield 'data: {"type": "content", "content": "Hello"}\n\n'
                yield 'data: {"type": "complete"}\n\n'
            
            mock_service.stream_chat_response = mock_stream_response
            
            response = await async_client.post(
                "/api/chat/stream",
                json={"message": "Hello, world!", "conversation_id": None}
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream"
    
    async def test_streaming_with_conversation_id(self, async_client, override_get_db):
        """Test streaming with existing conversation"""
        # Create a conversation first
        with patch('backend.app.crud.conversation_crud.get') as mock_get_conv:
            mock_conv = MagicMock()
            mock_conv.id = 1
            mock_get_conv.return_value = mock_conv
            
            with patch('backend.app.services.chat_service.EnhancedChatService') as mock_service_class:
                mock_service = AsyncMock()
                mock_service_class.return_value = mock_service
                
                async def mock_stream_response(*args, **kwargs):
                    yield 'data: {"type": "connected", "conversation_id": 1}\n\n'
                    yield 'data: {"type": "content", "content": "Response"}\n\n'
                
                mock_service.stream_chat_response = mock_stream_response
                
                response = await async_client.post(
                    "/api/chat/stream",
                    json={"message": "Test message", "conversation_id": 1}
                )
                
                assert response.status_code == 200
    
    async def test_streaming_error_handling(self, async_client, override_get_db):
        """Test streaming error handling"""
        response = await async_client.post(
            "/api/chat/stream",
            json={"message": "", "conversation_id": None}  # Empty message should fail
        )
        
        assert response.status_code == 400

class TestConversationAPI:
    """Test conversation management API"""
    
    async def test_create_conversation(self, async_client, override_get_db):
        """Test conversation creation endpoint"""
        with patch('backend.app.crud.conversation_crud.create') as mock_create:
            mock_conv = MagicMock()
            mock_conv.id = 1
            mock_conv.title = "Test Conversation"
            mock_create.return_value = mock_conv
            
            response = await async_client.post(
                "/api/conversations",
                json={"title": "Test Conversation"}
            )
            
            assert response.status_code == 200
    
    async def test_get_conversations(self, async_client, override_get_db):
        """Test conversation list endpoint"""
        with patch('backend.app.crud.conversation_crud.get_conversation_summaries') as mock_get:
            mock_conversations = [
                {"id": 1, "title": "Conv 1", "created_at": datetime.now().isoformat()},
                {"id": 2, "title": "Conv 2", "created_at": datetime.now().isoformat()}
            ]
            mock_get.return_value = mock_conversations
            
            response = await async_client.get("/api/conversations")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2

class TestIntegrationScenarios:
    """Test complex integration scenarios"""
    
    async def test_full_chat_workflow(self, async_client, override_get_db):
        """Test complete chat workflow from start to finish"""
        # 1. Create conversation
        with patch('backend.app.crud.conversation_crud.create') as mock_create_conv:
            mock_conv = MagicMock()
            mock_conv.id = 1
            mock_create_conv.return_value = mock_conv
            
            conv_response = await async_client.post(
                "/api/conversations",
                json={"title": "Integration Test"}
            )
            assert conv_response.status_code == 200
        
        # 2. Send message and test streaming
        with patch('backend.app.services.chat_service.EnhancedChatService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            async def mock_stream_response(*args, **kwargs):
                yield 'data: {"type": "workflow_start"}\n\n'
                yield 'data: {"type": "workflow_progress", "step": "orchestrate"}\n\n'
                yield 'data: {"type": "workflow_progress", "step": "analyze"}\n\n'
                yield 'data: {"type": "response_start"}\n\n'
                yield 'data: {"type": "content", "content": "This is a test response"}\n\n'
                yield 'data: {"type": "workflow_summary"}\n\n'
                yield 'data: {"type": "complete"}\n\n'
            
            mock_service.stream_chat_response = mock_stream_response
            
            chat_response = await async_client.post(
                "/api/chat/stream",
                json={"message": "Tell me about AI", "conversation_id": 1}
            )
            
            assert chat_response.status_code == 200
    
    async def test_error_recovery_scenarios(self, async_client, override_get_db):
        """Test various error recovery scenarios"""
        # Test invalid conversation ID
        response = await async_client.post(
            "/api/chat/stream",
            json={"message": "Test", "conversation_id": 99999}
        )
        assert response.status_code == 404
        
        # Test malformed request
        response = await async_client.post(
            "/api/chat/stream",
            json={"invalid": "data"}
        )
        assert response.status_code == 422  # Validation error

class TestPerformanceScenarios:
    """Test performance-related scenarios"""
    
    async def test_concurrent_requests(self, async_client, override_get_db):
        """Test handling of concurrent requests"""
        with patch('backend.app.services.chat_service.EnhancedChatService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            async def mock_stream_response(*args, **kwargs):
                yield 'data: {"type": "content", "content": "Response"}\n\n'
                yield 'data: {"type": "complete"}\n\n'
            
            mock_service.stream_chat_response = mock_stream_response
            
            # Send multiple concurrent requests
            tasks = []
            for i in range(5):
                task = async_client.post(
                    "/api/chat/stream",
                    json={"message": f"Test message {i}", "conversation_id": None}
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
    
    async def test_large_message_handling(self, async_client, override_get_db):
        """Test handling of large messages"""
        large_message = "A" * 10000  # 10KB message
        
        with patch('backend.app.services.chat_service.EnhancedChatService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            async def mock_stream_response(*args, **kwargs):
                yield 'data: {"type": "content", "content": "Processed large message"}\n\n'
                yield 'data: {"type": "complete"}\n\n'
            
            mock_service.stream_chat_response = mock_stream_response
            
            response = await async_client.post(
                "/api/chat/stream",
                json={"message": large_message, "conversation_id": None}
            )
            
            assert response.status_code == 200

class TestSecurityScenarios:
    """Test security-related scenarios"""
    
    async def test_injection_prevention(self, async_client, override_get_db):
        """Test prevention of injection attacks"""
        malicious_inputs = [
            "'; DROP TABLE conversations; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "{{7*7}}"  # Template injection
        ]
        
        with patch('backend.app.services.chat_service.EnhancedChatService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            async def mock_stream_response(*args, **kwargs):
                yield 'data: {"type": "content", "content": "Safe response"}\n\n'
                yield 'data: {"type": "complete"}\n\n'
            
            mock_service.stream_chat_response = mock_stream_response
            
            for malicious_input in malicious_inputs:
                response = await async_client.post(
                    "/api/chat/stream",
                    json={"message": malicious_input, "conversation_id": None}
                )
                
                # Should still process but safely
                assert response.status_code in [200, 400]  # Either process safely or reject

# Test runner functions
def run_basic_tests():
    """Run basic functionality tests"""
    print("🧪 Running basic functionality tests...")
    pytest.main([
        __file__ + "::TestHealthEndpoint",
        __file__ + "::TestDatabaseOperations",
        "-v"
    ])

def run_advanced_tests():
    """Run advanced feature tests"""
    print("🚀 Running advanced feature tests...")
    pytest.main([
        __file__ + "::TestAgenticService",
        __file__ + "::TestMultiToolOrchestrator",
        __file__ + "::TestChatService",
        "-v"
    ])

def run_integration_tests():
    """Run integration tests"""
    print("🔗 Running integration tests...")
    pytest.main([
        __file__ + "::TestStreamingAPI",
        __file__ + "::TestConversationAPI",
        __file__ + "::TestIntegrationScenarios",
        "-v"
    ])

def run_performance_tests():
    """Run performance tests"""
    print("⚡ Running performance tests...")
    pytest.main([
        __file__ + "::TestPerformanceScenarios",
        "-v"
    ])

def run_security_tests():
    """Run security tests"""
    print("🔒 Running security tests...")
    pytest.main([
        __file__ + "::TestSecurityScenarios",
        "-v"
    ])

def run_all_tests():
    """Run complete test suite"""
    print("🎯 Running complete test suite...")
    pytest.main([__file__, "-v", "--tb=short"])

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 GPT.R1 Comprehensive Test Suite")
    print("=" * 60)
    
    # Run all tests
    run_all_tests()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)