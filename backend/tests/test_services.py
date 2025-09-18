"""
GPT.R1 - Service Layer Tests
Comprehensive testing of all service layer components
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json

from app.services.chat_service import EnhancedChatService
from app.services.agentic_service import AdvancedAgenticService
from app.services.multi_tool_orchestrator import AdvancedToolOrchestrator
from app.services.openai_service import OpenAIService
from app.services.rag_service import RAGService

class TestChatService:
    """Test enhanced chat service functionality"""
    
    @pytest.fixture
    def chat_service(self):
        """Create chat service instance with mocked dependencies"""
        with patch('backend.app.services.chat_service.OpenAIService') as mock_openai, \
             patch('backend.app.services.chat_service.AdvancedAgenticService') as mock_agentic:
            
            service = EnhancedChatService()
            service.openai_service = mock_openai.return_value
            service.agentic_service = mock_agentic.return_value
            return service
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        session = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session
    
    async def test_stream_chat_response_new_conversation(self, chat_service, mock_db_session):
        """Test streaming chat response for new conversation"""
        # Mock agentic workflow
        mock_workflow = MagicMock()
        mock_workflow.workflow_id = "test_workflow_123"
        mock_workflow.success = True
        mock_workflow.steps = []
        mock_workflow.final_response = "Test response"
        mock_workflow.execution_time = 2.5
        
        chat_service.agentic_service.execute_agentic_workflow.return_value = mock_workflow
        
        # Mock message creation
        with patch('backend.app.crud.message_crud.create') as mock_create_message, \
             patch('backend.app.crud.conversation_crud.create') as mock_create_conv:
            
            mock_conv = MagicMock()
            mock_conv.id = 1
            mock_create_conv.return_value = mock_conv
            
            mock_msg = MagicMock()
            mock_msg.id = 1
            mock_create_message.return_value = mock_msg
            
            # Collect streaming responses
            responses = []
            async for response in chat_service.stream_chat_response(
                "Test message", None, mock_db_session
            ):
                responses.append(response)
            
            # Verify streaming format
            assert len(responses) > 0
            
            # Check for required message types
            response_text = ''.join(responses)
            assert 'data: {"type": "workflow_start"' in response_text
            assert 'data: {"type": "complete"}' in response_text
    
    async def test_stream_chat_response_existing_conversation(self, chat_service, mock_db_session):
        """Test streaming chat response for existing conversation"""
        # Mock conversation retrieval
        with patch('backend.app.crud.conversation_crud.get') as mock_get_conv:
            mock_conv = MagicMock()
            mock_conv.id = 1
            mock_get_conv.return_value = mock_conv
            
            # Mock workflow
            mock_workflow = MagicMock()
            mock_workflow.success = True
            mock_workflow.final_response = "Existing conv response"
            chat_service.agentic_service.execute_agentic_workflow.return_value = mock_workflow
            
            # Mock message creation
            with patch('backend.app.crud.message_crud.create'):
                responses = []
                async for response in chat_service.stream_chat_response(
                    "Follow-up message", 1, mock_db_session
                ):
                    responses.append(response)
                
                # Should include conversation connection message
                response_text = ''.join(responses)
                assert '"conversation_id": 1' in response_text
    
    async def test_conversation_history_retrieval(self, chat_service, mock_db_session):
        """Test conversation history retrieval"""
        # Mock message retrieval
        with patch('backend.app.crud.message_crud.get_messages_by_conversation') as mock_get_messages:
            mock_messages = [
                MagicMock(role="user", content="Hello", created_at=datetime.now()),
                MagicMock(role="assistant", content="Hi!", created_at=datetime.now())
            ]
            mock_get_messages.return_value = mock_messages
            
            history = await chat_service._get_conversation_history(1, mock_db_session)
            
            assert len(history) == 2
            assert history[0]["role"] == "user"
            assert history[0]["content"] == "Hello"
            assert history[1]["role"] == "assistant"
            assert history[1]["content"] == "Hi!"
    
    async def test_error_handling_in_streaming(self, chat_service, mock_db_session):
        """Test error handling during streaming"""
        # Mock workflow to raise exception
        chat_service.agentic_service.execute_agentic_workflow.side_effect = Exception("Workflow error")
        
        responses = []
        async for response in chat_service.stream_chat_response(
            "Test message", None, mock_db_session
        ):
            responses.append(response)
        
        # Should include error message
        response_text = ''.join(responses)
        assert 'error' in response_text.lower()

class TestAgenticService:
    """Test advanced agentic service functionality"""
    
    @pytest.fixture
    def agentic_service(self):
        """Create agentic service instance"""
        with patch('backend.app.services.agentic_service.AdvancedToolOrchestrator') as mock_orch, \
             patch('backend.app.services.agentic_service.RAGService') as mock_rag, \
             patch('backend.app.services.agentic_service.OpenAIService') as mock_openai:
            
            service = AdvancedAgenticService()
            service.orchestrator = mock_orch.return_value
            service.rag_service = mock_rag.return_value
            service.openai_service = mock_openai.return_value
            return service
    
    async def test_complete_agentic_workflow(self, agentic_service):
        """Test complete agentic workflow execution"""
        # Mock orchestrator
        agentic_service.orchestrator.orchestrate_workflow.return_value = {
            "success": True,
            "workflow_id": "orch_123",
            "tools_orchestrated": 4,
            "final_result": {"integrated_insights": ["Insight 1"]}
        }
        
        # Mock RAG service
        agentic_service.rag_service.get_context_from_search.return_value = "Search context"
        
        # Mock OpenAI service
        agentic_service.openai_service.generate_response.return_value = "Final response"
        
        workflow = await agentic_service.execute_agentic_workflow(
            "Test query about AI",
            []
        )
        
        assert workflow is not None
        assert workflow.success
        assert workflow.user_query == "Test query about AI"
        assert len(workflow.steps) >= 5  # Should have multiple steps
        
        # Check specific steps
        step_types = [step.step_type.value for step in workflow.steps]
        assert "orchestrate" in step_types
        assert "analyze" in step_types
        assert "search" in step_types
        assert "synthesize" in step_types
        assert "respond" in step_types
    
    async def test_workflow_with_orchestration_failure(self, agentic_service):
        """Test workflow when orchestration fails"""
        # Mock orchestrator failure
        agentic_service.orchestrator.orchestrate_workflow.return_value = {
            "success": False,
            "error": "Orchestration failed"
        }
        
        # Mock other services for fallback
        agentic_service.rag_service.get_context_from_search.return_value = "Fallback context"
        agentic_service.openai_service.generate_response.return_value = "Fallback response"
        
        workflow = await agentic_service.execute_agentic_workflow(
            "Test query",
            []
        )
        
        # Should still complete workflow with fallback
        assert workflow is not None
        assert workflow.success  # Should succeed with fallback
        
        # Check orchestration step failed but others succeeded
        orchestrate_step = next((s for s in workflow.steps if s.step_type.value == "orchestrate"), None)
        assert orchestrate_step is not None
        assert not orchestrate_step.success
    
    async def test_workflow_step_error_handling(self, agentic_service):
        """Test error handling in individual workflow steps"""
        # Mock RAG service to fail
        agentic_service.rag_service.get_context_from_search.side_effect = Exception("Search failed")
        
        # Mock other services
        agentic_service.orchestrator.orchestrate_workflow.return_value = {
            "success": True,
            "workflow_id": "test_123"
        }
        agentic_service.openai_service.generate_response.return_value = "Error response"
        
        workflow = await agentic_service.execute_agentic_workflow(
            "Test query",
            []
        )
        
        # Should handle error gracefully
        assert workflow is not None
        
        # Search step should have failed
        search_step = next((s for s in workflow.steps if s.step_type.value == "search"), None)
        assert search_step is not None
        assert not search_step.success
    
    async def test_conversation_history_integration(self, agentic_service):
        """Test workflow integration with conversation history"""
        conversation_history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"}
        ]
        
        # Mock services
        agentic_service.orchestrator.orchestrate_workflow.return_value = {
            "success": True,
            "workflow_id": "hist_123"
        }
        agentic_service.rag_service.get_context_from_search.return_value = "Context"
        agentic_service.openai_service.generate_response.return_value = "Response with history"
        
        workflow = await agentic_service.execute_agentic_workflow(
            "Follow-up question",
            conversation_history
        )
        
        assert workflow is not None
        assert workflow.success
        
        # Check that conversation history was used in analysis step
        analyze_step = next((s for s in workflow.steps if s.step_type.value == "analyze"), None)
        assert analyze_step is not None
        assert analyze_step.success

class TestMultiToolOrchestrator:
    """Test multi-tool orchestration system"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        return AdvancedToolOrchestrator()
    
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator.tools is not None
        assert len(orchestrator.tools) == 4
        
        expected_tools = ["WebSearchTool", "AnalysisTool", "SynthesisTool", "ValidationTool"]
        for tool_name in expected_tools:
            assert tool_name in orchestrator.tools
    
    async def test_workflow_orchestration_success(self, orchestrator):
        """Test successful workflow orchestration"""
        # Mock tool executions
        for tool in orchestrator.tools.values():
            mock_result = AsyncMock()
            mock_result.success = True
            mock_result.result = "Mock result"
            mock_result.confidence = 0.9
            mock_result.execution_time = 1.0
            tool.execute = AsyncMock(return_value=mock_result)
        
        result = await orchestrator.orchestrate_workflow(
            "Test query for orchestration",
            {"conversation_history": []}
        )
        
        assert result["success"]
        assert result["tools_orchestrated"] > 0
        assert "final_result" in result
        assert "quality_validation" in result
        assert result["quality_validation"]["quality_score"] > 0.8
    
    async def test_tool_selection_algorithm(self, orchestrator):
        """Test intelligent tool selection"""
        from backend.app.services.multi_tool_orchestrator import ToolRequest, ToolType, ToolPriority
        
        # Test different tool type selections
        test_cases = [
            (ToolType.SEARCH, "WebSearchTool"),
            (ToolType.ANALYSIS, "AnalysisTool"),
            (ToolType.SYNTHESIS, "SynthesisTool"),
            (ToolType.VALIDATION, "ValidationTool")
        ]
        
        for tool_type, expected_tool in test_cases:
            request = ToolRequest(
                tool_type=tool_type,
                input_data={"query": "test"},
                priority=ToolPriority.HIGH
            )
            
            selected_tool = orchestrator._select_best_tool(request)
            assert selected_tool is not None
            assert selected_tool.name == expected_tool
    
    async def test_tool_failure_handling(self, orchestrator):
        """Test handling of tool failures"""
        # Mock one tool to fail
        orchestrator.tools["WebSearchTool"].execute = AsyncMock(side_effect=Exception("Tool failed"))
        
        # Mock other tools to succeed
        for tool_name, tool in orchestrator.tools.items():
            if tool_name != "WebSearchTool":
                mock_result = AsyncMock()
                mock_result.success = True
                mock_result.result = "Success"
                mock_result.confidence = 0.8
                tool.execute = AsyncMock(return_value=mock_result)
        
        result = await orchestrator.orchestrate_workflow(
            "Test query",
            {"conversation_history": []}
        )
        
        # Should still succeed with degraded functionality
        assert result["success"]
        assert result["tools_orchestrated"] >= 3  # Other tools should work
    
    async def test_orchestrator_statistics(self, orchestrator):
        """Test orchestrator statistics collection"""
        stats = orchestrator.get_orchestrator_statistics()
        
        assert "total_workflows" in stats
        assert "tools_available" in stats
        assert "average_execution_time" in stats
        assert stats["tools_available"] == 4
    
    async def test_quality_validation(self, orchestrator):
        """Test quality validation system"""
        # Mock all tools to succeed with varying quality
        tool_results = {
            "WebSearchTool": {"confidence": 0.9, "result": "High quality result"},
            "AnalysisTool": {"confidence": 0.8, "result": "Good analysis"},
            "SynthesisTool": {"confidence": 0.85, "result": "Solid synthesis"},
            "ValidationTool": {"confidence": 0.95, "result": "Excellent validation"}
        }
        
        for tool_name, result_data in tool_results.items():
            mock_result = AsyncMock()
            mock_result.success = True
            mock_result.confidence = result_data["confidence"]
            mock_result.result = result_data["result"]
            orchestrator.tools[tool_name].execute = AsyncMock(return_value=mock_result)
        
        result = await orchestrator.orchestrate_workflow(
            "High quality test query",
            {"conversation_history": []}
        )
        
        assert result["success"]
        
        # Quality score should be high with good tool results
        quality_score = result["quality_validation"]["quality_score"]
        assert quality_score > 0.8

class TestOpenAIService:
    """Test OpenAI service functionality"""
    
    @pytest.fixture
    def openai_service(self):
        """Create OpenAI service instance"""
        with patch('openai.AsyncOpenAI'):
            return OpenAIService()
    
    async def test_generate_response_success(self, openai_service):
        """Test successful response generation"""
        # Mock OpenAI client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Test response from OpenAI"))
        ]
        
        openai_service.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        response = await openai_service.generate_response([
            {"role": "user", "content": "Test prompt"}
        ])
        
        assert response == "Test response from OpenAI"
    
    async def test_stream_chat_completion(self, openai_service):
        """Test streaming chat completion"""
        # Mock streaming response
        async def mock_stream():
            responses = [
                MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content=" world"))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content="!"))])
            ]
            for response in responses:
                yield response
        
        openai_service.client.chat.completions.create = AsyncMock(return_value=mock_stream())
        
        chunks = []
        async for chunk in openai_service.stream_chat_completion([
            {"role": "user", "content": "Test prompt"}
        ]):
            chunks.append(chunk)
        
        assert len(chunks) == 3
        assert chunks[0]["content"] == "Hello"
        assert chunks[1]["content"] == " world"
        assert chunks[2]["content"] == "!"
    
    async def test_error_handling(self, openai_service):
        """Test OpenAI service error handling"""
        # Mock OpenAI error
        openai_service.client.chat.completions.create = AsyncMock(
            side_effect=Exception("OpenAI API Error")
        )
        
        response = await openai_service.generate_response([
            {"role": "user", "content": "Test prompt"}
        ])
        
        # Should return error message
        assert "error" in response.lower() or "sorry" in response.lower()

class TestRAGService:
    """Test RAG (Retrieval-Augmented Generation) service"""
    
    @pytest.fixture
    def rag_service(self):
        """Create RAG service instance"""
        return RAGService()
    
    async def test_context_retrieval_from_search(self, rag_service):
        """Test context retrieval from search"""
        # Mock DuckDuckGo search
        with patch('backend.app.services.rag_service.DDGS') as mock_ddgs:
            mock_results = [
                {"title": "Result 1", "body": "Content 1", "href": "url1"},
                {"title": "Result 2", "body": "Content 2", "href": "url2"}
            ]
            
            mock_ddgs.return_value.text.return_value = mock_results
            
            context = await rag_service.get_context_from_search("test query")
            
            assert context is not None
            assert len(context) > 0
            assert "Result 1" in context or "Content 1" in context
    
    async def test_search_error_handling(self, rag_service):
        """Test search error handling"""
        # Mock search failure
        with patch('backend.app.services.rag_service.DDGS') as mock_ddgs:
            mock_ddgs.return_value.text.side_effect = Exception("Search failed")
            
            context = await rag_service.get_context_from_search("test query")
            
            # Should return fallback context or empty string
            assert isinstance(context, str)
    
    async def test_context_formatting(self, rag_service):
        """Test context formatting and cleaning"""
        # Mock search results with various formatting
        with patch('backend.app.services.rag_service.DDGS') as mock_ddgs:
            mock_results = [
                {
                    "title": "  Formatted Title  ",
                    "body": "Content with\nnewlines and    spaces",
                    "href": "https://example.com"
                }
            ]
            
            mock_ddgs.return_value.text.return_value = mock_results
            
            context = await rag_service.get_context_from_search("test query")
            
            # Should be properly formatted
            assert context is not None
            assert "Formatted Title" in context
            assert "Content with" in context

if __name__ == "__main__":
    print("🔧 Running Service Layer Tests...")
    pytest.main([__file__, "-v"])