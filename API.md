# API Documentation

This document provides comprehensive API documentation for the ChatGPT Clone backend.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
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

#### Login User
```http
POST /auth/login
```

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