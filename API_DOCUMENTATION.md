# 📡 GPT.R1 API Documentation & Examples

## 🔧 API Base Configuration

**Base URL**: `http://localhost:8000`  
**API Version**: `v1`  
**Full API Path**: `http://localhost:8000/api/v1`

---

## 🔐 Authentication System

### 1. User Registration

**Endpoint**: `POST /api/v1/auth/register`

**Request Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePassword123!",
    "full_name": "Test User"
  }'
```

**Response (Success - 201)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-09-18T10:30:00Z",
  "message": "User registered successfully"
}
```

**Error Responses**:
```json
// 400 - Email already exists
{
  "detail": "Email already registered",
  "error_code": "EMAIL_EXISTS",
  "timestamp": "2025-09-18T10:30:00Z"
}

// 422 - Validation Error
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "error_code": "VALIDATION_ERROR"
}
```

### 2. User Login

**Endpoint**: `POST /api/v1/auth/login`

**Request Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response (Success - 200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1440,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User"
  }
}
```

**Error Responses**:
```json
// 401 - Invalid credentials
{
  "detail": "Invalid email or password",
  "error_code": "INVALID_CREDENTIALS",
  "timestamp": "2025-09-18T10:30:00Z"
}

// 422 - Missing fields
{
  "detail": "Email and password are required",
  "error_code": "MISSING_CREDENTIALS"
}
```

---

## 💬 Chat & Streaming API

### 1. Real-time Streaming Chat

**Endpoint**: `POST /api/v1/chat/stream`

**Request Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "message": "Explain quantum computing in simple terms",
    "conversation_id": 1,
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
  }'
```

**Streaming Response (Server-Sent Events)**:
```
data: {"type": "start_streaming", "conversation_id": 1, "message_id": 15, "timestamp": "2025-09-18T10:30:00Z"}

data: {"type": "chunk", "content": "Quantum", "timestamp": "2025-09-18T10:30:00.100Z"}

data: {"type": "chunk", "content": " computing", "timestamp": "2025-09-18T10:30:00.150Z"}

data: {"type": "chunk", "content": " is like", "timestamp": "2025-09-18T10:30:00.200Z"}

data: {"type": "rag_searching", "query": "quantum computing 2025", "timestamp": "2025-09-18T10:30:01.000Z"}

data: {"type": "chunk", "content": " having a", "timestamp": "2025-09-18T10:30:01.250Z"}

data: {"type": "complete", "conversation_id": 1, "message_id": 15, "total_tokens": 245, "timestamp": "2025-09-18T10:30:05.000Z"}
```

**Error Responses**:
```json
// 401 - Authentication required
{
  "detail": "Authentication credentials required",
  "error_code": "AUTH_REQUIRED",
  "timestamp": "2025-09-18T10:30:00Z"
}

// 429 - Rate limit exceeded
{
  "detail": "Too many requests. Please wait before sending another message.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60,
  "timestamp": "2025-09-18T10:30:00Z"
}

// 503 - OpenAI API unavailable
{
  "detail": "AI service temporarily unavailable. Please try again in a few moments.",
  "error_code": "AI_SERVICE_UNAVAILABLE",
  "timestamp": "2025-09-18T10:30:00Z"
}

// 400 - Message too long
{
  "detail": "Message exceeds maximum length of 4000 characters",
  "error_code": "MESSAGE_TOO_LONG",
  "max_length": 4000,
  "current_length": 4500
}
```

---

## 📋 Conversation Management

### 1. List All Conversations

**Endpoint**: `GET /api/v1/conversations`

**Request Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/conversations?page=1&limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (Success - 200)**:
```json
{
  "conversations": [
    {
      "id": 1,
      "title": "Quantum Computing Discussion",
      "created_at": "2025-09-18T09:00:00Z",
      "updated_at": "2025-09-18T10:30:00Z",
      "message_count": 8,
      "is_archived": false,
      "last_message": {
        "id": 15,
        "content": "Quantum computing is like having a...",
        "role": "assistant",
        "timestamp": "2025-09-18T10:30:00Z"
      }
    },
    {
      "id": 2,
      "title": "Python Programming Help",
      "created_at": "2025-09-18T08:00:00Z", 
      "updated_at": "2025-09-18T08:45:00Z",
      "message_count": 12,
      "is_archived": false,
      "last_message": {
        "id": 28,
        "content": "Thanks for the code examples!",
        "role": "user",
        "timestamp": "2025-09-18T08:45:00Z"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 2,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### 2. Create New Conversation

**Endpoint**: `POST /api/v1/conversations`

**Request Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/conversations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "title": "Machine Learning Questions",
    "first_message": "Can you help me understand neural networks?"
  }'
```

**Response (Success - 201)**:
```json
{
  "id": 3,
  "title": "Machine Learning Questions",
  "created_at": "2025-09-18T11:00:00Z",
  "updated_at": "2025-09-18T11:00:00Z",
  "message_count": 1,
  "is_archived": false,
  "messages": [
    {
      "id": 29,
      "content": "Can you help me understand neural networks?",
      "role": "user",
      "timestamp": "2025-09-18T11:00:00Z"
    }
  ]
}
```

### 3. Get Specific Conversation

**Endpoint**: `GET /api/v1/conversations/{conversation_id}`

**Request Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (Success - 200)**:
```json
{
  "id": 1,
  "title": "Quantum Computing Discussion",
  "created_at": "2025-09-18T09:00:00Z",
  "updated_at": "2025-09-18T10:30:00Z",
  "message_count": 8,
  "is_archived": false,
  "messages": [
    {
      "id": 10,
      "content": "What is quantum computing?",
      "role": "user",
      "timestamp": "2025-09-18T09:00:00Z",
      "token_count": 5
    },
    {
      "id": 11,
      "content": "Quantum computing is a revolutionary technology...",
      "role": "assistant", 
      "timestamp": "2025-09-18T09:00:15Z",
      "token_count": 150,
      "model_used": "gpt-3.5-turbo"
    }
  ]
}
```

**Error Response**:
```json
// 404 - Conversation not found
{
  "detail": "Conversation not found or access denied",
  "error_code": "CONVERSATION_NOT_FOUND",
  "conversation_id": 999
}
```

### 4. Continue Existing Conversation

**Endpoint**: `POST /api/v1/chat/stream` (with conversation_id)

**Request Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "message": "Can you give me a practical example of quantum supremacy?",
    "conversation_id": 1,
    "model": "gpt-3.5-turbo"
  }'
```

**Streaming Response**:
```
data: {"type": "start_streaming", "conversation_id": 1, "message_id": 16, "timestamp": "2025-09-18T11:15:00Z"}

data: {"type": "chunk", "content": "A great", "timestamp": "2025-09-18T11:15:00.100Z"}

data: {"type": "chunk", "content": " example", "timestamp": "2025-09-18T11:15:00.150Z"}

data: {"type": "rag_searching", "query": "quantum supremacy examples 2025", "timestamp": "2025-09-18T11:15:01.000Z"}

data: {"type": "chunk", "content": " of quantum", "timestamp": "2025-09-18T11:15:01.200Z"}

data: {"type": "complete", "conversation_id": 1, "message_id": 16, "total_tokens": 320, "timestamp": "2025-09-18T11:15:08.000Z"}
```

### 5. Delete Conversation

**Endpoint**: `DELETE /api/v1/conversations/{conversation_id}`

**Request Example**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/conversations/2" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (Success - 200)**:
```json
{
  "message": "Conversation deleted successfully",
  "conversation_id": 2,
  "deleted_messages": 12,
  "timestamp": "2025-09-18T11:20:00Z"
}
```

---

## 🛠️ System & Monitoring

### 1. Health Check

**Endpoint**: `GET /api/v1/health`

**Request Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

**Response (Success - 200)**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-18T11:25:00Z",
  "version": "2.0.0",
  "database": {
    "status": "connected",
    "type": "PostgreSQL",
    "host": "localhost:5432"
  },
  "openai": {
    "status": "available", 
    "model": "gpt-3.5-turbo"
  },
  "rag": {
    "status": "enabled",
    "search_provider": "DuckDuckGo"
  },
  "uptime": "2h 45m 30s"
}
```

**Error Response (Service Down)**:
```json
// 503 - Service unavailable
{
  "status": "unhealthy",
  "timestamp": "2025-09-18T11:25:00Z",
  "errors": [
    {
      "service": "database",
      "status": "disconnected",
      "error": "Connection timeout to PostgreSQL server"
    },
    {
      "service": "openai",
      "status": "unavailable", 
      "error": "API key invalid or quota exceeded"
    }
  ]
}
```

### 2. Get Current User

**Endpoint**: `GET /api/v1/auth/me`

**Request Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (Success - 200)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-09-18T10:30:00Z",
  "last_login": "2025-09-18T11:00:00Z",
  "preferences": {
    "theme": "dark",
    "language": "en",
    "notifications": true
  },
  "usage_stats": {
    "total_conversations": 15,
    "total_messages": 145,
    "last_active": "2025-09-18T11:25:00Z"
  }
}
```

---

## 🚨 Common Error Scenarios & Handling

### 1. Database Connection Issues

**Error Response**:
```json
{
  "detail": "Database connection failed. Please try again in a few moments.",
  "error_code": "DATABASE_CONNECTION_ERROR",
  "timestamp": "2025-09-18T11:30:00Z",
  "retry_after": 30
}
```

**Troubleshooting**:
```bash
# Check PostgreSQL status
curl -X GET "http://localhost:8000/api/v1/health"

# Verify database connection
psql "postgresql://username:password@localhost:5432/gpt_r1_db" -c "SELECT 1;"
```

### 2. OpenAI API Timeout

**Error Response**:
```json
{
  "detail": "AI response timeout. The request took too long to process.",
  "error_code": "OPENAI_TIMEOUT",
  "timeout_duration": 30,
  "timestamp": "2025-09-18T11:30:00Z"
}
```

### 3. Rate Limiting

**Error Response**:
```json
{
  "detail": "Rate limit exceeded. Maximum 60 requests per minute.",
  "error_code": "RATE_LIMIT_EXCEEDED", 
  "limit": 60,
  "window": "1 minute",
  "retry_after": 45,
  "timestamp": "2025-09-18T11:30:00Z"
}
```

### 4. Invalid Token

**Error Response**:
```json
{
  "detail": "Token has expired. Please refresh your authentication.",
  "error_code": "TOKEN_EXPIRED",
  "expired_at": "2025-09-18T10:30:00Z",
  "timestamp": "2025-09-18T11:30:00Z"
}
```

---

## 🔧 cURL Demo: Complete Streaming Example

Here's a complete example showing real chunked SSE output:

```bash
# 1. Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "username": "demo", "password": "Demo123!", "full_name": "Demo User"}'

# 2. Login and get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "Demo123!"}' | jq -r '.access_token')

# 3. Create new conversation  
CONV_ID=$(curl -s -X POST "http://localhost:8000/api/v1/conversations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Streaming Demo", "first_message": "Hello!"}' | jq -r '.id')

# 4. Stream a message with real-time output
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"message\": \"Explain machine learning in 3 sentences\", \"conversation_id\": $CONV_ID}" \
  --no-buffer
```

**Expected Output**:
```
data: {"type": "start_streaming", "conversation_id": 1, "message_id": 2, "timestamp": "2025-09-18T12:00:00Z"}

data: {"type": "chunk", "content": "Machine", "timestamp": "2025-09-18T12:00:00.100Z"}

data: {"type": "chunk", "content": " learning", "timestamp": "2025-09-18T12:00:00.150Z"}

data: {"type": "chunk", "content": " is a", "timestamp": "2025-09-18T12:00:00.200Z"}

data: {"type": "chunk", "content": " subset of", "timestamp": "2025-09-18T12:00:00.250Z"}

data: {"type": "chunk", "content": " artificial", "timestamp": "2025-09-18T12:00:00.300Z"}

data: {"type": "complete", "conversation_id": 1, "message_id": 2, "total_tokens": 95, "timestamp": "2025-09-18T12:00:03.000Z"}
```

---

## 📊 API Status Codes Reference

| Code | Status | Description |
|------|--------|-------------|
| `200` | OK | Request successful |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Invalid request data |
| `401` | Unauthorized | Authentication required |
| `403` | Forbidden | Access denied |
| `404` | Not Found | Resource not found |
| `422` | Unprocessable Entity | Validation error |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server error |
| `503` | Service Unavailable | External service down |

---

## 🔍 Interactive API Testing

**Swagger UI**: http://localhost:8000/docs  
**ReDoc**: http://localhost:8000/redoc

These interactive interfaces provide:
- Live API testing
- Schema validation
- Response examples  
- Authentication setup
- Request builders

---

<div align="center">

**📡 GPT.R1 API Documentation**  
*Complete API Reference with Real Examples*

For more details, visit the [Interactive Documentation](http://localhost:8000/docs)

</div>