# 🚀 GPT.R1 API Documentation

This document provides comprehensive API documentation for GPT.R1 Advanced AI Assistant with **real request/response examples**.

## 🌐 Base URL
```
Production: https://gpt-r1-api.example.com/api/v1
Development: http://localhost:8000/api/v1
```

## 🔐 Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

---

## 📚 Real API Examples

### 1. 🔐 Authentication Endpoints

#### Register New User

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user_2025",
    "email": "demo@gpt-r1.com",
    "password": "SecurePass123!"
  }'
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "demo_user_2025",
  "email": "demo@gpt-r1.com",
  "is_active": true,
  "created_at": "2025-09-18T12:00:00.000Z",
  "updated_at": "2025-09-18T12:00:00.000Z"
}
```

#### User Login

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user_2025",
    "password": "SecurePass123!"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MjY3NTMyMDB9.example_jwt_signature",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "demo_user_2025",
    "email": "demo@gpt-r1.com"
  }
}
```

---

### 2. 💬 Conversation Management

#### Create New Conversation

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/conversations" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Assistant Discussion"
  }'
```

**Response (201 Created):**
```json
{
  "id": "conv_123e4567-e89b-12d3-a456-426614174000",
  "title": "AI Assistant Discussion",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-09-18T12:05:00.000Z",
  "updated_at": "2025-09-18T12:05:00.000Z",
  "message_count": 0,
  "last_message_at": null
}
```

#### List All Conversations

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/conversations" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "conversations": [
    {
      "id": "conv_123e4567-e89b-12d3-a456-426614174000",
      "title": "AI Assistant Discussion",
      "created_at": "2025-09-18T12:05:00.000Z",
      "updated_at": "2025-09-18T12:15:00.000Z",
      "message_count": 6,
      "last_message_at": "2025-09-18T12:15:00.000Z",
      "last_message_preview": "That's a great question about artificial intelligence..."
    },
    {
      "id": "conv_987f6543-e21a-12d3-a456-426614174001", 
      "title": "Python Programming Help",
      "created_at": "2025-09-18T11:30:00.000Z",
      "updated_at": "2025-09-18T11:45:00.000Z",
      "message_count": 4,
      "last_message_at": "2025-09-18T11:45:00.000Z",
      "last_message_preview": "Here's a Python function that solves your problem..."
    }
  ],
  "total_count": 2,
  "page": 1,
  "per_page": 10
}
```

#### Get Conversation Details

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/conv_123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "id": "conv_123e4567-e89b-12d3-a456-426614174000",
  "title": "AI Assistant Discussion",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-09-18T12:05:00.000Z",
  "updated_at": "2025-09-18T12:15:00.000Z",
  "messages": [
    {
      "id": "msg_111a2222-b333-4444-c555-666666666666",
      "role": "user",
      "content": "What is artificial intelligence and how does it work?",
      "timestamp": "2025-09-18T12:05:30.000Z"
    },
    {
      "id": "msg_222b3333-c444-5555-d666-777777777777",
      "role": "assistant", 
      "content": "Artificial intelligence (AI) is a broad field of computer science focused on creating systems that can perform tasks typically requiring human intelligence. AI works through various approaches including machine learning, neural networks, and natural language processing...",
      "timestamp": "2025-09-18T12:05:45.000Z"
    },
    {
      "id": "msg_333c4444-d555-6666-e777-888888888888",
      "role": "user",
      "content": "Can you explain machine learning in simple terms?",
      "timestamp": "2025-09-18T12:10:00.000Z"
    },
    {
      "id": "msg_444d5555-e666-7777-f888-999999999999",
      "role": "assistant",
      "content": "Machine learning is like teaching a computer to recognize patterns and make predictions based on examples. Imagine showing a child thousands of photos of cats and dogs...",
      "timestamp": "2025-09-18T12:10:15.000Z"
    }
  ],
  "message_count": 4
}
```

---

### 3. 🔄 Real-Time Chat Streaming

#### Stream Chat Response

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Explain quantum computing in simple terms",
    "conversation_id": "conv_123e4567-e89b-12d3-a456-426614174000"
  }' \
  --no-buffer
```

**Response (200 OK - Server-Sent Events):**
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"type": "start", "message_id": "msg_555e6666-f777-8888-g999-aaaaaaaaaa", "timestamp": "2025-09-18T12:20:00.000Z"}

data: {"type": "chunk", "content": "Quantum"}

data: {"type": "chunk", "content": " computing"}

data: {"type": "chunk", "content": " is"}

data: {"type": "chunk", "content": " like"}

data: {"type": "chunk", "content": " having"}

data: {"type": "chunk", "content": " a"}

data: {"type": "chunk", "content": " super"}

data: {"type": "chunk", "content": " powerful"}

data: {"type": "chunk", "content": " computer"}

data: {"type": "chunk", "content": " that"}

data: {"type": "chunk", "content": " can"}

data: {"type": "chunk", "content": " process"}

data: {"type": "chunk", "content": " multiple"}

data: {"type": "chunk", "content": " possibilities"}

data: {"type": "chunk", "content": " simultaneously."}

data: {"type": "chunk", "content": " Instead"}

data: {"type": "chunk", "content": " of"}

data: {"type": "chunk", "content": " traditional"}

data: {"type": "chunk", "content": " bits"}

data: {"type": "chunk", "content": " that"}

data: {"type": "chunk", "content": " are"}

data: {"type": "chunk", "content": " either"}

data: {"type": "chunk", "content": " 0"}

data: {"type": "chunk", "content": " or"}

data: {"type": "chunk", "content": " 1,"}

data: {"type": "chunk", "content": " quantum"}

data: {"type": "chunk", "content": " computers"}

data: {"type": "chunk", "content": " use"}

data: {"type": "chunk", "content": " quantum"}

data: {"type": "chunk", "content": " bits"}

data: {"type": "chunk", "content": " (qubits)"}

data: {"type": "chunk", "content": " that"}

data: {"type": "chunk", "content": " can"}

data: {"type": "chunk", "content": " exist"}

data: {"type": "chunk", "content": " in"}

data: {"type": "chunk", "content": " multiple"}

data: {"type": "chunk", "content": " states"}

data: {"type": "chunk", "content": " at"}

data: {"type": "chunk", "content": " once."}

data: {"type": "end", "message_id": "msg_555e6666-f777-8888-g999-aaaaaaaaaa", "conversation_id": "conv_123e4567-e89b-12d3-a456-426614174000", "timestamp": "2025-09-18T12:20:15.000Z"}
```

#### Continue Existing Conversation

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "What are the practical applications of quantum computing?",
    "conversation_id": "conv_123e4567-e89b-12d3-a456-426614174000",
    "include_history": true
  }' \
  --no-buffer
```

**Response (200 OK):**
```
data: {"type": "start", "message_id": "msg_666f7777-g888-9999-h000-bbbbbbbbbb", "context": "continuing_conversation", "timestamp": "2025-09-18T12:25:00.000Z"}

data: {"type": "chunk", "content": "Great"}

data: {"type": "chunk", "content": " question!"}

data: {"type": "chunk", "content": " Quantum"}

data: {"type": "chunk", "content": " computing"}

data: {"type": "chunk", "content": " has"}

data: {"type": "chunk", "content": " several"}

data: {"type": "chunk", "content": " exciting"}

data: {"type": "chunk", "content": " practical"}

data: {"type": "chunk", "content": " applications:"}

data: {"type": "chunk", "content": "\n\n1."}

data: {"type": "chunk", "content": " **Cryptography"}

data: {"type": "chunk", "content": " and"}

data: {"type": "chunk", "content": " Security**:"}

data: {"type": "chunk", "content": " Breaking"}

data: {"type": "chunk", "content": " current"}

data: {"type": "chunk", "content": " encryption"}

data: {"type": "chunk", "content": " methods"}

data: {"type": "chunk", "content": " and"}

data: {"type": "chunk", "content": " creating"}

data: {"type": "chunk", "content": " quantum-safe"}

data: {"type": "chunk", "content": " alternatives."}

data: {"type": "end", "message_id": "msg_666f7777-g888-9999-h000-bbbbbbbbbb", "conversation_id": "conv_123e4567-e89b-12d3-a456-426614174000", "timestamp": "2025-09-18T12:25:30.000Z"}
```

---

### 4. 👤 User Management

#### Get User Profile

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "demo_user_2025",
  "email": "demo@gpt-r1.com",
  "is_active": true,
  "created_at": "2025-09-18T12:00:00.000Z",
  "updated_at": "2025-09-18T12:00:00.000Z",
  "profile": {
    "preferred_language": "en",
    "timezone": "UTC",
    "conversation_count": 5,
    "total_messages": 47,
    "last_active": "2025-09-18T12:25:30.000Z"
  }
}
```

#### Update User Profile

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "email": "updated_email@gpt-r1.com",
    "profile": {
      "preferred_language": "en",
      "timezone": "America/New_York"
    }
  }'
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000", 
  "username": "demo_user_2025",
  "email": "updated_email@gpt-r1.com",
  "is_active": true,
  "updated_at": "2025-09-18T12:30:00.000Z",
  "profile": {
    "preferred_language": "en",
    "timezone": "America/New_York",
    "conversation_count": 5,
    "total_messages": 47
  }
}
```

---

### 5. 🏥 Health & Status

#### Health Check

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/health" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-18T12:35:00.000Z",
  "version": "1.0.0",
  "services": {
    "database": {
      "status": "connected",
      "response_time": "15ms",
      "connection_pool": "8/20 active"
    },
    "openai": {
      "status": "available", 
      "response_time": "200ms",
      "quota_remaining": "85%"
    },
    "cache": {
      "status": "connected",
      "response_time": "5ms",
      "memory_usage": "45%"
    }
  },
  "performance": {
    "uptime": "72h 15m 30s",
    "cpu_usage": "12%",
    "memory_usage": "340MB",
    "active_connections": 23
  }
}
```

---

## 📊 Response Status Codes

| Status Code | Meaning | Example Use Case |
|------------|---------|------------------|
| `200` | OK | Successful GET, PUT requests |
| `201` | Created | User registration, conversation creation |
| `204` | No Content | Successful DELETE requests |
| `400` | Bad Request | Invalid request format |
| `401` | Unauthorized | Missing or invalid JWT token |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource doesn't exist |
| `422` | Unprocessable Entity | Validation errors |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server-side errors |
| `502` | Bad Gateway | Upstream service error |
| `503` | Service Unavailable | Maintenance mode |
| `504` | Gateway Timeout | Request timeout |

---

## 🔄 Pagination

For endpoints that return lists (conversations, messages), pagination is supported:

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/conversations?page=2&per_page=5" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "conversations": [...],
  "pagination": {
    "page": 2,
    "per_page": 5, 
    "total_pages": 8,
    "total_count": 37,
    "has_next": true,
    "has_prev": true,
    "next_page": 3,
    "prev_page": 1
  }
}
```

---

## 🔍 Filtering & Searching

### Search Conversations

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/conversations?search=quantum&sort=updated_at&order=desc" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "conversations": [
    {
      "id": "conv_123e4567-e89b-12d3-a456-426614174000",
      "title": "Quantum Computing Discussion",
      "created_at": "2025-09-18T12:05:00.000Z",
      "match_score": 0.95,
      "match_highlights": ["<mark>Quantum</mark> Computing Discussion"]
    }
  ],
  "search_metadata": {
    "query": "quantum",
    "total_matches": 1,
    "search_time": "12ms"
  }
}
```

---

## 🛡️ Security Features

### Rate Limiting Headers

All responses include rate limiting information:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1726753320
X-RateLimit-Window: 60
```

### CORS Headers

```http
Access-Control-Allow-Origin: https://gpt-r1.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400
```

---

## 🧪 Testing the API

### Complete Workflow Test Script

```bash
#!/bin/bash

API_BASE="http://localhost:8000/api/v1"

echo "🧪 Testing GPT.R1 API Complete Workflow"
echo "======================================="

# 1. Register User
echo "📝 Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"api_test_user","email":"test@api.com","password":"TestPass123!"}')

echo "✅ Registration: $(echo $REGISTER_RESPONSE | jq -r '.username')"

# 2. Login
echo "🔐 Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"api_test_user","password":"TestPass123!"}')

JWT_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "✅ JWT Token: ${JWT_TOKEN:0:20}..."

# 3. Create Conversation
echo "💬 Creating conversation..."
CONV_RESPONSE=$(curl -s -X POST "$API_BASE/conversations" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"API Test Conversation"}')

CONV_ID=$(echo $CONV_RESPONSE | jq -r '.id')
echo "✅ Conversation ID: $CONV_ID"

# 4. Send Message
echo "🤖 Sending message..."
curl -X POST "$API_BASE/chat/stream" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Hello, this is an API test\",\"conversation_id\":\"$CONV_ID\"}" \
  --no-buffer

echo ""
echo "✅ API workflow test completed successfully!"
```

---

<div align="center">

**📚 COMPLETE API DOCUMENTATION**

*Real examples for every endpoint with actual request/response samples*

[🔗 Interactive API Docs](http://localhost:8000/docs) • [📊 OpenAPI Schema](http://localhost:8000/openapi.json)

</div>

**Request Body (Form Data):**
```
username: string
password: string
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2025-09-16T10:00:00Z"
}
```

### Conversations

#### List Conversations
```http
GET /conversations
```

**Query Parameters:**
- `skip` (integer): Number of records to skip (default: 0)
- `limit` (integer): Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Chat about AI",
    "user_id": 1,
    "created_at": "2025-09-16T10:00:00Z",
    "updated_at": "2025-09-16T10:30:00Z",
    "messages": []
  }
]
```

#### Get Conversation
```http
GET /conversations/{id}
```

**Response:**
```json
{
  "id": 1,
  "title": "Chat about AI",
  "user_id": 1,
  "created_at": "2025-09-16T10:00:00Z",
  "updated_at": "2025-09-16T10:30:00Z",
  "messages": [
    {
      "id": 1,
      "conversation_id": 1,
      "role": "user",
      "content": "Hello, how are you?",
      "timestamp": "2025-09-16T10:00:00Z"
    },
    {
      "id": 2,
      "conversation_id": 1,
      "role": "assistant",
      "content": "Hello! I'm doing well, thank you for asking. How can I help you today?",
      "timestamp": "2025-09-16T10:00:30Z"
    }
  ]
}
```

#### Create Conversation
```http
POST /conversations
```

**Request Body:**
```json
{
  "title": "New Chat"
}
```

**Response:**
```json
{
  "id": 2,
  "title": "New Chat",
  "user_id": 1,
  "created_at": "2025-09-16T11:00:00Z",
  "updated_at": null,
  "messages": []
}
```

#### Update Conversation Title
```http
PUT /conversations/{id}/title
```

**Request Body:**
```json
{
  "title": "Updated Chat Title"
}
```

### Chat

#### Streaming Chat (Server-Sent Events)
```http
POST /chat
```

**Request Body:**
```json
{
  "message": "What is artificial intelligence?",
  "conversation_id": 1,
  "use_rag": true
}
```

**Response:** Server-Sent Events stream

**Event Types:**
```javascript
// Conversation ID event
data: {"type": "conversation_id", "conversation_id": 1}

// Context search event
data: {"type": "context", "content": "Searching the web for relevant information..."}

// Content chunk events
data: {"type": "content", "content": "Artificial"}
data: {"type": "content", "content": " intelligence"}
data: {"type": "content", "content": " is..."}

// Completion event
data: {"type": "done", "message_id": 5}

// Error event
data: {"type": "error", "content": "Error message"}
```

#### Simple Chat (Non-streaming)
```http
POST /chat/simple
```

**Request Body:**
```json
{
  "message": "What is artificial intelligence?",
  "conversation_id": 1,
  "use_rag": false
}
```

**Response:**
```json
{
  "conversation_id": 1,
  "message": {
    "id": 3,
    "conversation_id": 1,
    "role": "assistant",
    "content": "Artificial intelligence (AI) is a branch of computer science...",
    "timestamp": "2025-09-16T11:30:00Z"
  }
}
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

### Validation Error Format
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

- Chat endpoints: 10 requests per minute per user
- Authentication endpoints: 5 requests per minute per IP
- Other endpoints: 100 requests per minute per user

## WebSocket Events (Future Enhancement)

```javascript
// Connection
ws://localhost:8000/ws/chat/{conversation_id}

// Message types
{
  "type": "chat_message",
  "data": {
    "message": "Hello",
    "use_rag": false
  }
}

{
  "type": "typing_start",
  "data": {}
}

{
  "type": "typing_stop",
  "data": {}
}
```

## Examples

### JavaScript/Fetch Example
```javascript
// Login
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    username: 'myuser',
    password: 'mypassword'
  })
});

const { access_token } = await loginResponse.json();

// Send chat message with streaming
const chatResponse = await fetch('/api/v1/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    message: 'Hello, AI!',
    use_rag: true
  })
});

const reader = chatResponse.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      console.log('Received:', data);
    }
  }
}
```

### Python/Requests Example
```python
import requests
import json

# Login
login_data = {
    'username': 'myuser',
    'password': 'mypassword'
}

response = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    data=login_data
)

token = response.json()['access_token']

# Send chat message
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

chat_data = {
    'message': 'What is machine learning?',
    'use_rag': True
}

response = requests.post(
    'http://localhost:8000/api/v1/chat/simple',
    headers=headers,
    json=chat_data
)

result = response.json()
print(result['message']['content'])
```

### cURL Examples
```bash
# Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"

# Chat (simple)
curl -X POST "http://localhost:8000/api/v1/chat/simple" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "message": "Hello, how are you?",
    "use_rag": false
  }'
```

## Schema Definitions

### User Schema
```json
{
  "id": "integer",
  "username": "string",
  "email": "string (email format)",
  "is_active": "boolean",
  "created_at": "string (ISO 8601 datetime)"
}
```

### Message Schema
```json
{
  "id": "integer",
  "conversation_id": "integer",
  "role": "string (user|assistant|system)",
  "content": "string",
  "timestamp": "string (ISO 8601 datetime)"
}
```

### Conversation Schema
```json
{
  "id": "integer",
  "title": "string|null",
  "user_id": "integer|null",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)|null",
  "messages": "array of Message objects"
}
```

## Testing

You can test the API using the interactive documentation at:
```
http://localhost:8000/docs
```

Or the alternative ReDoc documentation at:
```
http://localhost:8000/redoc
```