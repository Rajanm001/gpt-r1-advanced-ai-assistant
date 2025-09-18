"""
GPT.R1 Test Configuration and Utilities
=======================================

This module provides test configuration, fixtures, and utilities
for the comprehensive test suite.
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, AsyncMock
from typing import AsyncGenerator

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


@pytest.fixture(scope="session")
def event_loop():
    """Provide event loop for async tests"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def mock_database_session():
    """Mock database session for testing"""
    session = Mock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock() 
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "choices": [{
            "message": {
                "content": "This is a mocked AI response for testing purposes."
            }
        }]
    }


@pytest.fixture
def test_user_data():
    """Test user data for registration/login tests"""
    return {
        "username": "test_user_123",
        "email": "test@example.com",
        "password": "secure_test_password_123"
    }


@pytest.fixture  
def test_conversation_data():
    """Test conversation data"""
    return {
        "title": "Test Conversation",
        "user_id": "test-user-uuid-123"
    }


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for authentication tests"""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"


@pytest.fixture
def authenticated_headers(mock_jwt_token):
    """Headers with authentication token"""
    return {
        "Authorization": f"Bearer {mock_jwt_token}",
        "Content-Type": "application/json"
    }


# Test markers for categorizing tests
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"  
    )
    config.addinivalue_line(
        "markers", "asyncio: marks tests as async tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )