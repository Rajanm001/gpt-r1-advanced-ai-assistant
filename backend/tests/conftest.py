"""
GPT.R1 - Test Fixtures and Utilities
Shared test fixtures and utility functions
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
import uuid
from typing import List, Dict, Any

# Test data generators
class TestDataGenerator:
    """Generate test data for various scenarios"""
    
    @staticmethod
    def generate_conversation_data(title: str = None) -> Dict[str, Any]:
        """Generate conversation test data"""
        return {
            "id": 1,
            "title": title or f"Test Conversation {uuid.uuid4().hex[:8]}",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    
    @staticmethod
    def generate_message_data(conversation_id: int = 1, role: str = "user", content: str = None) -> Dict[str, Any]:
        """Generate message test data"""
        return {
            "id": 1,
            "conversation_id": conversation_id,
            "role": role,
            "content": content or f"Test message {uuid.uuid4().hex[:8]}",
            "created_at": datetime.now()
        }
    
    @staticmethod
    def generate_workflow_data() -> Dict[str, Any]:
        """Generate workflow test data"""
        return {
            "workflow_id": f"workflow_{uuid.uuid4().hex[:8]}",
            "user_query": "Test query",
            "steps": [
                {
                    "step_type": "orchestrate",
                    "success": True,
                    "output_data": {"tools_orchestrated": 4}
                },
                {
                    "step_type": "analyze",
                    "success": True,
                    "output_data": {"analysis": "Test analysis"}
                }
            ],
            "success": True,
            "final_response": "Test response",
            "execution_time": 2.5
        }

# Mock services
class MockOpenAIService:
    """Mock OpenAI service for testing"""
    
    async def stream_chat_completion(self, messages: List[Dict], **kwargs):
        """Mock streaming chat completion"""
        responses = [
            {"type": "content", "content": "This "},
            {"type": "content", "content": "is "},
            {"type": "content", "content": "a "},
            {"type": "content", "content": "test "},
            {"type": "content", "content": "response."},
            {"type": "complete"}
        ]
        
        for response in responses:
            yield response
            await asyncio.sleep(0.01)  # Simulate streaming delay

class MockRAGService:
    """Mock RAG service for testing"""
    
    async def get_context_from_search(self, query: str) -> str:
        """Mock context retrieval"""
        return f"Mocked context for query: {query}"

class MockAgenticService:
    """Mock agentic service for testing"""
    
    def __init__(self):
        self.orchestrator = MockOrchestrator()
    
    async def execute_agentic_workflow(self, user_query: str, conversation_history: List[Dict]) -> Any:
        """Mock workflow execution"""
        from backend.app.schemas.workflow import WorkflowExecution, WorkflowStep, StepType
        
        workflow = WorkflowExecution(
            workflow_id=f"test_workflow_{uuid.uuid4().hex[:8]}",
            user_query=user_query,
            steps=[
                WorkflowStep(
                    step_type=StepType.ORCHESTRATE,
                    success=True,
                    output_data={"tools_orchestrated": 4}
                ),
                WorkflowStep(
                    step_type=StepType.ANALYZE,
                    success=True,
                    output_data={"analysis": "Mock analysis"}
                )
            ],
            success=True,
            final_response="Mock agentic response",
            execution_time=1.5
        )
        
        return workflow

class MockOrchestrator:
    """Mock orchestrator for testing"""
    
    async def orchestrate_workflow(self, query: str, context: Dict) -> Dict[str, Any]:
        """Mock orchestration"""
        return {
            "success": True,
            "workflow_id": f"orch_workflow_{uuid.uuid4().hex[:8]}",
            "tools_orchestrated": 4,
            "execution_time": 2.0,
            "final_result": {"integrated_insights": ["Insight 1", "Insight 2"]},
            "quality_validation": {"quality_score": 0.95},
            "tool_breakdown": {
                "WebSearchTool": {"success": True, "execution_time": 0.5},
                "AnalysisTool": {"success": True, "execution_time": 0.3},
                "SynthesisTool": {"success": True, "execution_time": 0.4},
                "ValidationTool": {"success": True, "execution_time": 0.2}
            }
        }

# Test utilities
class TestUtilities:
    """Utility functions for testing"""
    
    @staticmethod
    def assert_streaming_response_format(response_data: str):
        """Assert that response follows SSE format"""
        lines = response_data.split('\n')
        
        # Should have data: prefix for SSE
        data_lines = [line for line in lines if line.startswith('data: ')]
        assert len(data_lines) > 0, "No SSE data lines found"
        
        # Should end with double newline
        assert response_data.endswith('\n\n'), "SSE response should end with double newline"
    
    @staticmethod
    def parse_sse_messages(response_data: str) -> List[Dict[str, Any]]:
        """Parse SSE messages from response"""
        import json
        
        messages = []
        lines = response_data.split('\n')
        
        for line in lines:
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    messages.append(data)
                except json.JSONDecodeError:
                    continue
        
        return messages
    
    @staticmethod
    def create_mock_database_session():
        """Create mock database session"""
        session = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.close = AsyncMock()
        return session

# Performance testing utilities
class PerformanceTestUtils:
    """Utilities for performance testing"""
    
    @staticmethod
    def measure_execution_time(func):
        """Decorator to measure function execution time"""
        import time
        
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            return result, execution_time
        
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            return result, execution_time
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    @staticmethod
    def assert_response_time(execution_time: float, max_time: float):
        """Assert that execution time is within acceptable limits"""
        assert execution_time < max_time, f"Execution time {execution_time:.2f}s exceeded limit {max_time}s"

# Security testing utilities
class SecurityTestUtils:
    """Utilities for security testing"""
    
    @staticmethod
    def get_injection_payloads() -> List[str]:
        """Get common injection attack payloads"""
        return [
            "'; DROP TABLE conversations; --",
            "' OR '1'='1",
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "../../etc/passwd",
            "../../../windows/system32/drivers/etc/hosts",
            "{{7*7}}",
            "${7*7}",
            "#{7*7}",
            "%{7*7}",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>"
        ]
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """Sanitize input for testing purposes"""
        import html
        import re
        
        # HTML escape
        sanitized = html.escape(input_string)
        
        # Remove potential script tags
        sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove SQL injection patterns
        sql_patterns = [r';\s*DROP\s+TABLE', r';\s*DELETE\s+FROM', r';\s*INSERT\s+INTO']
        for pattern in sql_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized

# Error simulation utilities
class ErrorSimulationUtils:
    """Utilities for simulating various error conditions"""
    
    @staticmethod
    def create_database_error():
        """Create a database connection error"""
        from sqlalchemy.exc import OperationalError
        return OperationalError("Connection failed", None, None)
    
    @staticmethod
    def create_openai_error():
        """Create an OpenAI API error"""
        class MockOpenAIError(Exception):
            def __init__(self, message="OpenAI API Error"):
                self.message = message
                super().__init__(self.message)
        
        return MockOpenAIError("Rate limit exceeded")
    
    @staticmethod
    def create_timeout_error():
        """Create a timeout error"""
        import asyncio
        return asyncio.TimeoutError("Operation timed out")

# Test environment setup
class TestEnvironment:
    """Test environment configuration and setup"""
    
    @staticmethod
    def setup_test_environment():
        """Set up test environment variables"""
        import os
        
        test_env_vars = {
            "OPENAI_API_KEY": "test-key-123",
            "DATABASE_URL": "postgresql+asyncpg://postgres:admin@localhost:5432/test_gpt_r1_db",
            "ENVIRONMENT": "test",
            "LOG_LEVEL": "DEBUG"
        }
        
        for key, value in test_env_vars.items():
            os.environ[key] = value
    
    @staticmethod
    def cleanup_test_environment():
        """Clean up test environment"""
        import os
        
        test_env_vars = [
            "OPENAI_API_KEY",
            "DATABASE_URL", 
            "ENVIRONMENT",
            "LOG_LEVEL"
        ]
        
        for key in test_env_vars:
            if key in os.environ:
                del os.environ[key]

# Test decorators
def async_test(func):
    """Decorator for async test functions"""
    return pytest.mark.asyncio(func)

def performance_test(max_time: float = 5.0):
    """Decorator for performance tests"""
    def decorator(func):
        @pytest.mark.asyncio
        async def wrapper(*args, **kwargs):
            result, execution_time = await PerformanceTestUtils.measure_execution_time(func)(*args, **kwargs)
            PerformanceTestUtils.assert_response_time(execution_time, max_time)
            return result
        return wrapper
    return decorator

def integration_test(func):
    """Decorator for integration tests"""
    return pytest.mark.integration(func)

def security_test(func):
    """Decorator for security tests"""
    return pytest.mark.security(func)