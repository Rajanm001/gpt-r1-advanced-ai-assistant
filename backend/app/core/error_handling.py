"""
GPT.R1 - Production Error Handling System
Comprehensive error handling with proper status codes and recovery
Created by: Rajan Mishra
"""

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from openai import APIError, RateLimitError, APITimeoutError
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class GPTError(Exception):
    """Base exception class for GPT.R1 application"""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class DatabaseError(GPTError):
    """Database-related errors"""
    def __init__(self, message: str, original_error: Exception = None):
        self.original_error = original_error
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class OpenAIError(GPTError):
    """OpenAI API-related errors"""
    def __init__(self, message: str, original_error: Exception = None):
        self.original_error = original_error
        super().__init__(
            message=message,
            code="OPENAI_API_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

class ValidationError(GPTError):
    """Input validation errors"""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )

class AuthenticationError(GPTError):
    """Authentication-related errors"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class AuthorizationError(GPTError):
    """Authorization-related errors"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN
        )

class RateLimitError(GPTError):
    """Rate limiting errors"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

def handle_database_error(error: SQLAlchemyError, operation: str = "database operation") -> HTTPException:
    """Handle SQLAlchemy database errors with proper categorization"""
    
    logger.error(f"Database error during {operation}: {str(error)}")
    
    if isinstance(error, IntegrityError):
        # Handle constraint violations
        if "duplicate key" in str(error).lower():
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "Duplicate entry",
                    "code": "DUPLICATE_ENTRY",
                    "message": "This entry already exists",
                    "operation": operation,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        elif "foreign key" in str(error).lower():
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid reference",
                    "code": "FOREIGN_KEY_ERROR",
                    "message": "Referenced item does not exist",
                    "operation": operation,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    elif isinstance(error, OperationalError):
        # Handle connection/operational errors
        if "connection" in str(error).lower():
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "Database connection error",
                    "code": "DB_CONNECTION_ERROR",
                    "message": "Database is temporarily unavailable",
                    "operation": operation,
                    "timestamp": datetime.utcnow().isoformat(),
                    "retry_after": 30
                }
            )
    
    # Generic database error
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": "Database error",
            "code": "DATABASE_ERROR",
            "message": f"An error occurred during {operation}",
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

def handle_openai_error(error: Exception, fallback_available: bool = True) -> Dict[str, Any]:
    """Handle OpenAI API errors with fallback information"""
    
    logger.error(f"OpenAI API error: {str(error)}")
    
    error_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "fallback_available": fallback_available
    }
    
    if isinstance(error, RateLimitError):
        error_info.update({
            "error": "Rate limit exceeded",
            "code": "RATE_LIMIT_EXCEEDED",
            "message": "Too many requests to OpenAI API",
            "retry_after": 60,
            "suggestion": "Please wait a moment before sending another message"
        })
    
    elif isinstance(error, APITimeoutError):
        error_info.update({
            "error": "API timeout",
            "code": "API_TIMEOUT",
            "message": "OpenAI API request timed out",
            "suggestion": "The request took too long. Please try again."
        })
    
    elif isinstance(error, APIError):
        if "insufficient_quota" in str(error).lower():
            error_info.update({
                "error": "API quota exceeded",
                "code": "QUOTA_EXCEEDED",
                "message": "OpenAI API quota has been exceeded",
                "suggestion": "Using intelligent fallback responses"
            })
        else:
            error_info.update({
                "error": "API error",
                "code": "OPENAI_API_ERROR",
                "message": "OpenAI API returned an error",
                "suggestion": "Using intelligent fallback responses"
            })
    
    else:
        error_info.update({
            "error": "Service unavailable",
            "code": "SERVICE_UNAVAILABLE",
            "message": "AI service is temporarily unavailable",
            "suggestion": "Using intelligent fallback responses"
        })
    
    return error_info

def validate_chat_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Validate chat request with detailed error messages"""
    
    errors = []
    
    # Check if request is valid dictionary
    if not isinstance(request, dict):
        raise ValidationError("Request must be a valid JSON object")
    
    # Validate message
    message = request.get("message")
    if not message:
        errors.append({
            "field": "message",
            "error": "Message is required",
            "code": "MISSING_MESSAGE"
        })
    elif not isinstance(message, str):
        errors.append({
            "field": "message",
            "error": "Message must be a string",
            "code": "INVALID_MESSAGE_TYPE"
        })
    elif not message.strip():
        errors.append({
            "field": "message",
            "error": "Message cannot be empty",
            "code": "EMPTY_MESSAGE"
        })
    elif len(message) > 4000:
        errors.append({
            "field": "message",
            "error": "Message too long (max 4000 characters)",
            "code": "MESSAGE_TOO_LONG",
            "max_length": 4000,
            "current_length": len(message)
        })
    
    # Validate conversation_id if provided
    conversation_id = request.get("conversation_id")
    if conversation_id is not None:
        if not isinstance(conversation_id, int) or conversation_id <= 0:
            errors.append({
                "field": "conversation_id",
                "error": "Conversation ID must be a positive integer",
                "code": "INVALID_CONVERSATION_ID"
            })
    
    # Validate use_rag if provided
    use_rag = request.get("use_rag")
    if use_rag is not None and not isinstance(use_rag, bool):
        errors.append({
            "field": "use_rag",
            "error": "use_rag must be a boolean",
            "code": "INVALID_RAG_FLAG"
        })
    
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation failed",
                "code": "VALIDATION_ERROR",
                "message": "Request contains invalid data",
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    return {
        "message": message.strip(),
        "conversation_id": conversation_id,
        "use_rag": use_rag or False
    }

def create_error_response(error: Exception, operation: str = "operation") -> Dict[str, Any]:
    """Create standardized error response"""
    
    error_response = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation
    }
    
    if isinstance(error, GPTError):
        error_response.update({
            "error": error.message,
            "code": error.code,
            "status_code": error.status_code
        })
    
    elif isinstance(error, HTTPException):
        error_response.update({
            "error": error.detail,
            "code": "HTTP_ERROR",
            "status_code": error.status_code
        })
    
    else:
        error_response.update({
            "error": "An unexpected error occurred",
            "code": "UNEXPECTED_ERROR",
            "status_code": 500,
            "message": str(error)
        })
    
    return error_response

class ErrorRecoveryService:
    """Service for handling error recovery and fallback mechanisms"""
    
    @staticmethod
    async def recover_from_openai_error(error: Exception, user_message: str) -> str:
        """Recover from OpenAI API errors with intelligent fallback"""
        
        logger.warning(f"Recovering from OpenAI error: {error}")
        
        # Import here to avoid circular imports
        from ..services.openai_service import OpenAIService
        
        openai_service = OpenAIService()
        return openai_service._create_intelligent_response(user_message)
    
    @staticmethod
    async def recover_from_database_error(error: SQLAlchemyError, operation: str) -> Dict[str, Any]:
        """Attempt to recover from database errors"""
        
        logger.warning(f"Attempting database error recovery for: {operation}")
        
        recovery_info = {
            "recovered": False,
            "fallback_used": False,
            "error_type": type(error).__name__,
            "operation": operation
        }
        
        # For connection errors, suggest retry
        if isinstance(error, OperationalError) and "connection" in str(error).lower():
            recovery_info.update({
                "suggestion": "retry",
                "retry_after": 30,
                "message": "Database connection issue detected. Please retry in 30 seconds."
            })
        
        # For integrity errors, provide specific guidance
        elif isinstance(error, IntegrityError):
            recovery_info.update({
                "suggestion": "modify_request",
                "message": "Data conflict detected. Please modify your request."
            })
        
        return recovery_info

# Middleware for global error handling
async def global_error_handler(request, call_next):
    """Global error handling middleware"""
    try:
        response = await call_next(request)
        return response
    except Exception as error:
        logger.error(f"Unhandled error in {request.url.path}: {error}")
        
        # Create standardized error response
        error_detail = create_error_response(error, f"request to {request.url.path}")
        
        return HTTPException(
            status_code=500,
            detail=error_detail
        )

# Health check with error detection
async def system_health_check() -> Dict[str, Any]:
    """Comprehensive system health check"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check database
    try:
        from ..core.database import engine
        connection = engine.connect()
        connection.close()
        health_status["services"]["database"] = {
            "status": "healthy",
            "response_time_ms": 0  # Could measure actual response time
        }
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "error_code": "DB_CONNECTION_FAILED"
        }
        health_status["status"] = "degraded"
    
    # Check OpenAI service
    try:
        from ..services.openai_service import OpenAIService
        openai_service = OpenAIService()
        if openai_service.is_configured:
            health_status["services"]["openai"] = {
                "status": "healthy",
                "fallback_available": True
            }
        else:
            health_status["services"]["openai"] = {
                "status": "fallback_mode",
                "fallback_available": True,
                "message": "Using intelligent fallback responses"
            }
    except Exception as e:
        health_status["services"]["openai"] = {
            "status": "unhealthy",
            "error": str(e),
            "fallback_available": True
        }
    
    return health_status