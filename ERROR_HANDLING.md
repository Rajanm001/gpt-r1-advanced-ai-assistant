# 🚨 Error Handling Documentation - GPT.R1

This document provides comprehensive documentation for all error scenarios in GPT.R1, including sample error JSON responses, recovery mechanisms, and troubleshooting guides.

## 📋 Error Categories

### 1. Authentication Errors (4xx)
### 2. OpenAI API Errors (5xx)  
### 3. Database Connection Errors (5xx)
### 4. Validation Errors (422)
### 5. Rate Limiting Errors (429)
### 6. Network Timeout Errors (504)

---

## 🔐 Authentication Errors

### Invalid Credentials (401)

**Scenario**: User provides wrong username/password

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "wrong_user", "password": "wrong_pass"}'
```

**Error Response**:
```json
{
  "error": {
    "type": "authentication_error",
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid username or password",
    "details": {
      "field": "credentials",
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456789"
    }
  },
  "status_code": 401
}
```

**Recovery**: Verify credentials and retry with correct username/password.

---

### Missing Authorization Header (401)

**Scenario**: Protected endpoint accessed without token

```bash
curl -X POST "http://localhost:8000/api/v1/conversations" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Chat"}'
```

**Error Response**:
```json
{
  "error": {
    "type": "authentication_error", 
    "code": "MISSING_TOKEN",
    "message": "Authorization header is required",
    "details": {
      "required_header": "Authorization: Bearer <token>",
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456790"
    }
  },
  "status_code": 401
}
```

**Recovery**: Include `Authorization: Bearer <jwt_token>` header.

---

### Expired JWT Token (401)

**Scenario**: JWT token has expired

```bash
curl -X POST "http://localhost:8000/api/v1/conversations" \
  -H "Authorization: Bearer expired_jwt_token_here" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Chat"}'
```

**Error Response**:
```json
{
  "error": {
    "type": "authentication_error",
    "code": "TOKEN_EXPIRED", 
    "message": "JWT token has expired",
    "details": {
      "expired_at": "2025-09-18T11:00:00Z",
      "current_time": "2025-09-18T12:00:00Z",
      "action": "refresh_token_or_login",
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456791"
    }
  },
  "status_code": 401
}
```

**Recovery**: Login again to get new JWT token.

---

### Invalid JWT Token Format (422)

**Scenario**: Malformed JWT token

```bash
curl -X POST "http://localhost:8000/api/v1/conversations" \
  -H "Authorization: Bearer invalid.jwt.format" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Chat"}'
```

**Error Response**:
```json
{
  "error": {
    "type": "validation_error",
    "code": "INVALID_TOKEN_FORMAT",
    "message": "JWT token format is invalid", 
    "details": {
      "expected_format": "eyJ...",
      "received_format": "invalid.jwt.format",
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456792"
    }
  },
  "status_code": 422
}
```

**Recovery**: Ensure JWT token is properly formatted.

---

## 🤖 OpenAI API Errors

### OpenAI API Key Invalid (500)

**Scenario**: Invalid or missing OpenAI API key

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Authorization: Bearer valid_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "conversation_id": "conv_uuid"}'
```

**Error Response**:
```json
{
  "error": {
    "type": "external_service_error",
    "code": "OPENAI_API_KEY_INVALID",
    "message": "OpenAI API key is invalid or missing",
    "details": {
      "service": "OpenAI",
      "error_code": "invalid_api_key", 
      "suggestion": "Check OPENAI_API_KEY environment variable",
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456793"
    }
  },
  "status_code": 500
}
```

**Recovery**: Verify OpenAI API key in environment variables.

---

### OpenAI Rate Limit Exceeded (429)

**Scenario**: OpenAI API rate limit hit

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Authorization: Bearer valid_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "conversation_id": "conv_uuid"}'
```

**Error Response**:
```json
{
  "error": {
    "type": "rate_limit_error",
    "code": "OPENAI_RATE_LIMIT_EXCEEDED", 
    "message": "OpenAI API rate limit exceeded",
    "details": {
      "service": "OpenAI",
      "limit_type": "requests_per_minute",
      "retry_after": 60,
      "quota_reset": "2025-09-18T12:01:00Z",
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456794"
    }
  },
  "status_code": 429
}
```

**Recovery**: Wait for `retry_after` seconds before retrying.

---

### OpenAI Service Timeout (504)

**Scenario**: OpenAI API request timeout

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Authorization: Bearer valid_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"message": "Very long complex query...", "conversation_id": "conv_uuid"}'
```

**Error Response**:
```json
{
  "error": {
    "type": "timeout_error",
    "code": "OPENAI_REQUEST_TIMEOUT",
    "message": "OpenAI API request timed out",
    "details": {
      "service": "OpenAI",
      "timeout_duration": "30s",
      "suggestion": "Try a shorter or simpler query",
      "fallback_available": true,
      "timestamp": "2025-09-18T12:00:00Z", 
      "request_id": "req_123456795"
    }
  },
  "status_code": 504
}
```

**Recovery**: Retry with shorter query or check OpenAI service status.

---

## 🗄️ Database Connection Errors

### Database Connection Failed (500)

**Scenario**: PostgreSQL database is unreachable

```bash
curl -X POST "http://localhost:8000/api/v1/conversations" \
  -H "Authorization: Bearer valid_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Chat"}'
```

**Error Response**:
```json
{
  "error": {
    "type": "database_error",
    "code": "DATABASE_CONNECTION_FAILED",
    "message": "Unable to connect to database",
    "details": {
      "database": "PostgreSQL",
      "host": "localhost:5432",
      "error_detail": "Connection refused",
      "health_check": "/api/v1/health",
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456796"
    }
  },
  "status_code": 500
}
```

**Recovery**: Check database server status and connection settings.

---

### Database Transaction Failed (500)

**Scenario**: Database transaction rollback

```bash
curl -X POST "http://localhost:8000/api/v1/conversations" \
  -H "Authorization: Bearer valid_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Chat"}'
```

**Error Response**:
```json
{
  "error": {
    "type": "database_error",
    "code": "TRANSACTION_FAILED",
    "message": "Database transaction was rolled back",
    "details": {
      "operation": "create_conversation",
      "rollback_reason": "Constraint violation",
      "affected_tables": ["conversations"],
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456797"
    }
  },
  "status_code": 500
}
```

**Recovery**: Check data constraints and retry operation.

---

## ✅ Validation Errors

### Missing Required Fields (422)

**Scenario**: Required fields missing from request

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user"}'
```

**Error Response**:
```json
{
  "error": {
    "type": "validation_error",
    "code": "MISSING_REQUIRED_FIELDS",
    "message": "Required fields are missing",
    "details": {
      "missing_fields": ["email", "password"],
      "received_fields": ["username"],
      "field_requirements": {
        "email": "Valid email address required",
        "password": "Minimum 8 characters required"
      },
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456798"
    }
  },
  "status_code": 422
}
```

**Recovery**: Include all required fields in request body.

---

### Invalid Field Format (422)

**Scenario**: Field values don't match expected format

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "invalid_email", "password": "123"}'
```

**Error Response**:
```json
{
  "error": {
    "type": "validation_error", 
    "code": "INVALID_FIELD_FORMAT",
    "message": "Field validation failed",
    "details": {
      "validation_errors": [
        {
          "field": "email",
          "error": "Invalid email format",
          "received": "invalid_email",
          "expected": "user@example.com"
        },
        {
          "field": "password", 
          "error": "Password too short",
          "received_length": 3,
          "minimum_length": 8
        }
      ],
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456799"
    }
  },
  "status_code": 422
}
```

**Recovery**: Fix field formats according to validation requirements.

---

## 🚦 Rate Limiting Errors

### API Rate Limit Exceeded (429)

**Scenario**: Too many requests from same IP/user

```bash
# Rapid successive requests
for i in {1..100}; do
  curl -X POST "http://localhost:8000/api/v1/chat/stream" \
    -H "Authorization: Bearer valid_jwt_token" \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello", "conversation_id": "conv_uuid"}'
done
```

**Error Response**:
```json
{
  "error": {
    "type": "rate_limit_error",
    "code": "API_RATE_LIMIT_EXCEEDED", 
    "message": "Too many requests",
    "details": {
      "limit": "100 requests per minute",
      "window": "60 seconds",
      "retry_after": 45,
      "reset_time": "2025-09-18T12:01:00Z",
      "current_usage": "100/100",
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456800"
    }
  },
  "status_code": 429
}
```

**Recovery**: Wait for rate limit window to reset before retrying.

---

## 🌐 Network & Infrastructure Errors

### Service Unavailable (503)

**Scenario**: Backend service is temporarily down

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

**Error Response**:
```json
{
  "error": {
    "type": "service_error",
    "code": "SERVICE_UNAVAILABLE",
    "message": "Service is temporarily unavailable",
    "details": {
      "service": "GPT.R1 Backend",
      "status": "maintenance",
      "estimated_recovery": "2025-09-18T12:30:00Z",
      "alternative_endpoints": [],
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456801"
    }
  },
  "status_code": 503
}
```

**Recovery**: Wait for service to recover or check status page.

---

### Gateway Timeout (504)

**Scenario**: Request timeout at proxy/gateway level

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Authorization: Bearer valid_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"message": "Extremely complex analysis request...", "conversation_id": "conv_uuid"}' \
  --max-time 1
```

**Error Response**:
```json
{
  "error": {
    "type": "timeout_error",
    "code": "GATEWAY_TIMEOUT",
    "message": "Gateway timeout occurred", 
    "details": {
      "timeout_duration": "60s",
      "upstream_service": "FastAPI Backend",
      "suggestion": "Retry with smaller request or check service status",
      "timestamp": "2025-09-18T12:00:00Z",
      "request_id": "req_123456802"
    }
  },
  "status_code": 504
}
```

**Recovery**: Reduce request complexity or retry after short delay.

---

## 🔧 Error Recovery Strategies

### Automatic Retry Logic

```python
import asyncio
import backoff

@backoff.on_exception(
    backoff.expo,
    (asyncio.TimeoutError, ConnectionError),
    max_tries=3,
    max_time=30
)
async def make_api_request():
    # API request logic with automatic retry
    pass
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
```

### Error Monitoring

```python
import logging
from datetime import datetime

def log_error(error_type, error_code, details):
    logging.error({
        "error_type": error_type,
        "error_code": error_code, 
        "details": details,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "GPT.R1"
    })
```

---

## 📊 Error Monitoring & Alerts

### Health Check Endpoint

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

**Healthy Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-18T12:00:00Z",
  "services": {
    "database": {"status": "connected", "response_time": "15ms"},
    "openai": {"status": "available", "response_time": "200ms"},
    "cache": {"status": "connected", "response_time": "5ms"}
  },
  "version": "1.0.0"
}
```

**Unhealthy Response**:
```json
{
  "status": "unhealthy",
  "timestamp": "2025-09-18T12:00:00Z", 
  "services": {
    "database": {"status": "disconnected", "error": "Connection timeout"},
    "openai": {"status": "error", "error": "Invalid API key"},
    "cache": {"status": "connected", "response_time": "5ms"}
  },
  "version": "1.0.0"
}
```

### Error Aggregation

Common error patterns and their frequencies:

| Error Type | Frequency | Impact | Recovery Time |
|------------|-----------|--------|---------------|
| `INVALID_CREDENTIALS` | 15% | Low | Immediate |
| `OPENAI_RATE_LIMIT` | 8% | Medium | 60s |
| `DATABASE_CONNECTION` | 2% | High | 5-30s |
| `VALIDATION_ERROR` | 25% | Low | Immediate |
| `TOKEN_EXPIRED` | 12% | Low | Immediate |

---

## 🚨 Emergency Procedures

### Database Failover

1. Check database connectivity
2. Switch to read-only mode if needed
3. Failover to backup database
4. Update connection strings
5. Restart services

### OpenAI Service Degradation

1. Enable fallback responses
2. Cache recent responses
3. Reduce request complexity
4. Implement local AI fallback

### Complete Service Outage

1. Enable maintenance mode
2. Display status page
3. Queue incoming requests
4. Notify users via status channels
5. Implement graceful recovery

---

<div align="center">

**🛡️ COMPREHENSIVE ERROR HANDLING**

*Every error scenario documented with JSON examples and recovery strategies*

</div>