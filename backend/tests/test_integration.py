"""
GPT.R1 - Integration Tests
End-to-end testing of complete workflows and system integration
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app
from tests.conftest import (
    TestDataGenerator, MockAgenticService, MockOrchestrator,
    TestUtilities, async_test, integration_test
)

@pytest.mark.integration
class TestFullChatWorkflow:
    """Test complete chat workflow from API to database"""
    
    @integration_test
    async def test_complete_new_conversation_workflow(self):
        """Test complete workflow for new conversation"""
        # Mock all external services
        with patch('backend.app.services.chat_service.EnhancedChatService') as mock_chat_service, \
             patch('backend.app.crud.conversation_crud') as mock_conv_crud, \
             patch('backend.app.crud.message_crud') as mock_msg_crud:
            
            # Setup mocks
            mock_service_instance = AsyncMock()
            mock_chat_service.return_value = mock_service_instance
            
            # Mock conversation creation
            mock_conv = MagicMock()
            mock_conv.id = 1
            mock_conv.title = "New Conversation"
            mock_conv_crud.create.return_value = mock_conv
            
            # Mock message creation
            mock_user_msg = MagicMock()
            mock_user_msg.id = 1
            mock_assistant_msg = MagicMock()
            mock_assistant_msg.id = 2
            mock_msg_crud.create.side_effect = [mock_user_msg, mock_assistant_msg]
            
            # Mock streaming response
            async def mock_stream_response(*args, **kwargs):
                workflow_steps = [
                    '{"type": "workflow_start", "message": "Starting enhanced workflow..."}',
                    '{"type": "conversation_created", "conversation_id": 1, "title": "New Conversation"}',
                    '{"type": "workflow_progress", "step": "orchestrate", "message": "Orchestrating 4 specialized tools..."}',
                    '{"type": "orchestration_result", "tools_orchestrated": 4, "success": true}',
                    '{"type": "workflow_progress", "step": "analyze", "message": "Analyzing user query..."}',
                    '{"type": "analysis_complete", "analysis": "Query requires comprehensive response"}',
                    '{"type": "workflow_progress", "step": "search", "message": "Searching for relevant information..."}',
                    '{"type": "search_complete", "sources_found": 5}',
                    '{"type": "workflow_progress", "step": "synthesize", "message": "Synthesizing information..."}',
                    '{"type": "synthesis_complete", "insights_generated": 3}',
                    '{"type": "workflow_progress", "step": "validate", "message": "Validating response quality..."}',
                    '{"type": "validation_complete", "quality_score": 0.95}',
                    '{"type": "workflow_progress", "step": "respond", "message": "Generating final response..."}',
                    '{"type": "response_start"}',
                    '{"type": "content", "content": "This is a comprehensive response "}',
                    '{"type": "content", "content": "generated through our advanced "}',
                    '{"type": "content", "content": "agentic workflow with multi-tool "}',
                    '{"type": "content", "content": "orchestration. The system analyzed "}',
                    '{"type": "content", "content": "your query, searched for relevant "}',
                    '{"type": "content", "content": "information, and synthesized "}',
                    '{"type": "content", "content": "a high-quality response."}',
                    '{"type": "workflow_summary", "summary": {"total_time": 3.2, "steps_completed": 6, "tools_used": 4, "quality_score": 0.95}}',
                    '{"type": "complete"}'
                ]
                
                for step in workflow_steps:
                    yield f'data: {step}\n\n'
                    await asyncio.sleep(0.01)  # Simulate streaming delay
            
            mock_service_instance.stream_chat_response = mock_stream_response
            
            # Execute workflow
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat/stream",
                    json={
                        "message": "Tell me about the latest developments in artificial intelligence",
                        "conversation_id": None
                    }
                )
            
            # Verify response
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream"
            
            # Parse streaming response
            content = response.text
            TestUtilities.assert_streaming_response_format(content)
            
            messages = TestUtilities.parse_sse_messages(content)
            
            # Verify workflow steps
            message_types = [msg.get("type") for msg in messages]
            expected_types = [
                "workflow_start", "conversation_created", "workflow_progress",
                "orchestration_result", "response_start", "content", 
                "workflow_summary", "complete"
            ]
            
            for expected_type in expected_types:
                assert expected_type in message_types, f"Missing message type: {expected_type}"
            
            # Verify orchestration details
            orchestration_msg = next((msg for msg in messages if msg.get("type") == "orchestration_result"), None)
            assert orchestration_msg is not None
            assert orchestration_msg["tools_orchestrated"] == 4
            assert orchestration_msg["success"] is True
            
            # Verify workflow summary
            summary_msg = next((msg for msg in messages if msg.get("type") == "workflow_summary"), None)
            assert summary_msg is not None
            assert "total_time" in summary_msg["summary"]
            assert summary_msg["summary"]["steps_completed"] == 6
            assert summary_msg["summary"]["tools_used"] == 4
            assert summary_msg["summary"]["quality_score"] == 0.95
    
    @integration_test
    async def test_existing_conversation_workflow(self):
        """Test workflow with existing conversation"""
        with patch('backend.app.services.chat_service.EnhancedChatService') as mock_chat_service, \
             patch('backend.app.crud.conversation_crud') as mock_conv_crud, \
             patch('backend.app.crud.message_crud') as mock_msg_crud:
            
            # Mock existing conversation
            mock_conv = MagicMock()
            mock_conv.id = 1
            mock_conv.title = "Existing Conversation"
            mock_conv_crud.get.return_value = mock_conv
            
            # Mock conversation history
            mock_history = [
                MagicMock(role="user", content="Previous question", created_at=datetime.now()),
                MagicMock(role="assistant", content="Previous answer", created_at=datetime.now())
            ]
            mock_msg_crud.get_messages_by_conversation.return_value = mock_history
            
            # Setup chat service
            mock_service_instance = AsyncMock()
            mock_chat_service.return_value = mock_service_instance
            
            async def mock_stream_response(*args, **kwargs):
                yield 'data: {"type": "connected", "conversation_id": 1}\n\n'
                yield 'data: {"type": "history_loaded", "message_count": 2}\n\n'
                yield 'data: {"type": "workflow_start", "message": "Continuing conversation..."}\n\n'
                yield 'data: {"type": "content", "content": "Follow-up response based on history"}\n\n'
                yield 'data: {"type": "complete"}\n\n'
            
            mock_service_instance.stream_chat_response = mock_stream_response
            
            # Execute workflow
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat/stream",
                    json={
                        "message": "Follow-up question",
                        "conversation_id": 1
                    }
                )
            
            assert response.status_code == 200
            
            messages = TestUtilities.parse_sse_messages(response.text)
            
            # Verify conversation connection
            connected_msg = next((msg for msg in messages if msg.get("type") == "connected"), None)
            assert connected_msg is not None
            assert connected_msg["conversation_id"] == 1
            
            # Verify history loading
            history_msg = next((msg for msg in messages if msg.get("type") == "history_loaded"), None)
            assert history_msg is not None
            assert history_msg["message_count"] == 2

@pytest.mark.integration
class TestConversationManagementIntegration:
    """Test conversation management integration"""
    
    @integration_test
    async def test_full_conversation_lifecycle(self):
        """Test complete conversation lifecycle"""
        with patch('backend.app.crud.conversation_crud') as mock_conv_crud, \
             patch('backend.app.crud.message_crud') as mock_msg_crud:
            
            # Mock conversation creation
            mock_conv = MagicMock()
            mock_conv.id = 1
            mock_conv.title = "Test Conversation"
            mock_conv.created_at = datetime.now()
            mock_conv_crud.create.return_value = mock_conv
            mock_conv_crud.get.return_value = mock_conv
            
            # Mock conversation list
            mock_conv_crud.get_conversation_summaries.return_value = [
                {
                    "id": 1,
                    "title": "Test Conversation",
                    "created_at": datetime.now().isoformat(),
                    "message_count": 0
                }
            ]
            
            # Mock successful deletion
            mock_conv_crud.remove.return_value = True
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                # 1. Create conversation
                create_response = await client.post(
                    "/api/conversations",
                    json={"title": "Test Conversation"}
                )
                assert create_response.status_code == 200
                conv_data = create_response.json()
                assert conv_data["title"] == "Test Conversation"
                
                # 2. List conversations
                list_response = await client.get("/api/conversations")
                assert list_response.status_code == 200
                conversations = list_response.json()
                assert len(conversations) >= 1
                
                # 3. Get specific conversation
                get_response = await client.get("/api/conversations/1")
                assert get_response.status_code == 200
                
                # 4. Delete conversation
                delete_response = await client.delete("/api/conversations/1")
                assert delete_response.status_code == 200
    
    @integration_test
    async def test_conversation_with_messages_integration(self):
        """Test conversation with messages integration"""
        with patch('backend.app.crud.conversation_crud') as mock_conv_crud, \
             patch('backend.app.crud.message_crud') as mock_msg_crud:
            
            # Mock conversation
            mock_conv = MagicMock()
            mock_conv.id = 1
            mock_conv.title = "Conversation with Messages"
            mock_conv_crud.get.return_value = mock_conv
            
            # Mock messages
            mock_messages = [
                MagicMock(
                    id=1, role="user", content="Hello",
                    created_at=datetime.now(), conversation_id=1
                ),
                MagicMock(
                    id=2, role="assistant", content="Hi there!",
                    created_at=datetime.now(), conversation_id=1
                )
            ]
            mock_msg_crud.get_messages_by_conversation.return_value = mock_messages
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                # Get conversation with messages
                response = await client.get("/api/conversations/1")
                assert response.status_code == 200
                
                data = response.json()
                assert "conversation" in data
                assert "messages" in data
                assert len(data["messages"]) == 2
                assert data["messages"][0]["role"] == "user"
                assert data["messages"][1]["role"] == "assistant"

@pytest.mark.integration
class TestMultiToolOrchestrationIntegration:
    """Test multi-tool orchestration integration"""
    
    @integration_test
    async def test_orchestration_workflow_integration(self):
        """Test complete orchestration workflow integration"""
        with patch('backend.app.services.multi_tool_orchestrator.AdvancedToolOrchestrator') as mock_orch_class:
            # Setup mock orchestrator
            mock_orchestrator = AsyncMock()
            mock_orch_class.return_value = mock_orchestrator
            
            # Mock orchestration result
            mock_orchestrator.orchestrate_workflow.return_value = {
                "success": True,
                "workflow_id": "integration_test_workflow_123",
                "tools_orchestrated": 4,
                "execution_time": 2.8,
                "final_result": {
                    "integrated_insights": [
                        "AI technology is rapidly advancing",
                        "Machine learning applications are expanding",
                        "Ethical considerations are increasingly important"
                    ],
                    "synthesized_response": "Comprehensive AI analysis complete"
                },
                "quality_validation": {
                    "quality_score": 0.92,
                    "confidence_level": "high",
                    "validation_notes": "All tools executed successfully"
                },
                "tool_breakdown": {
                    "WebSearchTool": {
                        "success": True,
                        "execution_time": 0.8,
                        "sources_found": 15,
                        "confidence": 0.9
                    },
                    "AnalysisTool": {
                        "success": True,
                        "execution_time": 0.6,
                        "insights_generated": 8,
                        "confidence": 0.95
                    },
                    "SynthesisTool": {
                        "success": True,
                        "execution_time": 0.7,
                        "synthesis_quality": 0.88,
                        "confidence": 0.9
                    },
                    "ValidationTool": {
                        "success": True,
                        "execution_time": 0.3,
                        "validation_score": 0.92,
                        "confidence": 0.94
                    }
                }
            }
            
            # Mock tool statistics
            mock_orchestrator.get_orchestrator_statistics.return_value = {
                "total_workflows": 1,
                "tools_available": 4,
                "average_execution_time": 2.8,
                "success_rate": 1.0
            }
            
            # Test orchestration through agentic service
            from backend.app.services.agentic_service import AdvancedAgenticService
            
            with patch('backend.app.services.agentic_service.RAGService') as mock_rag, \
                 patch('backend.app.services.agentic_service.OpenAIService') as mock_openai:
                
                # Setup additional mocks
                mock_rag.return_value.get_context_from_search.return_value = "Relevant search context"
                mock_openai.return_value.generate_response.return_value = "Final orchestrated response"
                
                # Create service instance
                agentic_service = AdvancedAgenticService()
                agentic_service.orchestrator = mock_orchestrator
                
                # Execute workflow
                workflow = await agentic_service.execute_agentic_workflow(
                    "Tell me about the latest AI developments and their implications",
                    []
                )
                
                # Verify workflow execution
                assert workflow is not None
                assert workflow.success
                assert len(workflow.steps) >= 5
                
                # Verify orchestration step
                orchestrate_step = next(
                    (s for s in workflow.steps if s.step_type.value == "orchestrate"),
                    None
                )
                assert orchestrate_step is not None
                assert orchestrate_step.success
                assert orchestrate_step.output_data["orchestration_successful"]
                assert orchestrate_step.output_data["tools_orchestrated"] == 4
                
                # Verify tool breakdown in orchestration data
                tool_breakdown = orchestrate_step.output_data["tool_breakdown"]
                assert "WebSearchTool" in tool_breakdown
                assert "AnalysisTool" in tool_breakdown
                assert "SynthesisTool" in tool_breakdown
                assert "ValidationTool" in tool_breakdown
                
                # Verify all tools succeeded
                for tool_name, tool_result in tool_breakdown.items():
                    assert tool_result["success"] is True
                    assert tool_result["confidence"] > 0.8

@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling across system integration"""
    
    @integration_test
    async def test_database_error_integration(self):
        """Test database error handling integration"""
        with patch('backend.app.crud.conversation_crud.get_conversation_summaries') as mock_get:
            # Mock database error
            mock_get.side_effect = Exception("Database connection failed")
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/conversations")
                
                # Should handle error gracefully
                assert response.status_code == 500
    
    @integration_test
    async def test_service_error_integration(self):
        """Test service error handling integration"""
        with patch('backend.app.services.chat_service.EnhancedChatService') as mock_chat_service:
            # Mock service error
            mock_service_instance = AsyncMock()
            mock_chat_service.return_value = mock_service_instance
            mock_service_instance.stream_chat_response.side_effect = Exception("Service error")
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat/stream",
                    json={"message": "Test message", "conversation_id": None}
                )
                
                # Should handle error gracefully
                assert response.status_code == 500
    
    @integration_test
    async def test_validation_error_integration(self):
        """Test validation error integration"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test various validation errors
            test_cases = [
                # Empty message
                {"message": "", "conversation_id": None},
                # Invalid conversation ID type
                {"message": "Test", "conversation_id": "invalid"},
                # Missing required field
                {"conversation_id": None}
            ]
            
            for test_case in test_cases:
                response = await client.post("/api/chat/stream", json=test_case)
                assert response.status_code in [400, 422]  # Bad request or validation error

@pytest.mark.integration
class TestPerformanceIntegration:
    """Test performance across system integration"""
    
    @integration_test
    async def test_concurrent_requests_integration(self):
        """Test concurrent request handling"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create multiple concurrent requests
            tasks = []
            for i in range(10):
                task = client.get("/api/health")
                tasks.append(task)
            
            # Execute concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all requests succeeded
            for response in responses:
                if hasattr(response, 'status_code'):
                    assert response.status_code == 200
    
    @integration_test
    async def test_streaming_performance_integration(self):
        """Test streaming performance integration"""
        import time
        
        with patch('backend.app.services.chat_service.EnhancedChatService') as mock_chat_service:
            mock_service_instance = AsyncMock()
            mock_chat_service.return_value = mock_service_instance
            
            # Mock fast streaming response
            async def mock_fast_stream(*args, **kwargs):
                for i in range(5):
                    yield f'data: {{"type": "content", "content": "Chunk {i}"}}\n\n'
                yield 'data: {"type": "complete"}\n\n'
            
            mock_service_instance.stream_chat_response = mock_fast_stream
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                start_time = time.time()
                
                response = await client.post(
                    "/api/chat/stream",
                    json={"message": "Performance test", "conversation_id": None}
                )
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                assert response.status_code == 200
                assert execution_time < 5.0  # Should complete within 5 seconds

@pytest.mark.integration
class TestSecurityIntegration:
    """Test security across system integration"""
    
    @integration_test
    async def test_input_sanitization_integration(self):
        """Test input sanitization integration"""
        from backend.tests.conftest import SecurityTestUtils
        
        malicious_inputs = SecurityTestUtils.get_injection_payloads()
        
        with patch('backend.app.services.chat_service.EnhancedChatService') as mock_chat_service:
            mock_service_instance = AsyncMock()
            mock_chat_service.return_value = mock_service_instance
            
            async def mock_safe_stream(*args, **kwargs):
                yield 'data: {"type": "content", "content": "Safe response"}\n\n'
                yield 'data: {"type": "complete"}\n\n'
            
            mock_service_instance.stream_chat_response = mock_safe_stream
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                for malicious_input in malicious_inputs:
                    response = await client.post(
                        "/api/chat/stream",
                        json={"message": malicious_input, "conversation_id": None}
                    )
                    
                    # Should either process safely or reject
                    assert response.status_code in [200, 400, 422]
    
    @integration_test
    async def test_cors_integration(self):
        """Test CORS integration"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test CORS preflight
            response = await client.options("/api/chat/stream")
            assert response.status_code in [200, 204]
            
            # Test actual request
            response = await client.get("/api/health")
            assert response.status_code == 200

if __name__ == "__main__":
    print("🔗 Running Integration Tests...")
    pytest.main([__file__, "-v", "--tb=short"])