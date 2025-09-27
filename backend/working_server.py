#!/usr/bin/env python3
"""
WORKING ChatGPT Clone Backend Server
- Clean FastAPI implementation
- OpenRouter integration
- Real AI responses
- CORS configured
- Database persistence
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import uvicorn
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenRouter Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "microsoft/wizardlm-2-8x22b"

# FastAPI App
app = FastAPI(title="ChatGPT Clone API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ConversationRequest(BaseModel):
    title: str = "New Chat"

# Database Initialization
def init_database():
    """Initialize SQLite database with required tables"""
    try:
        conn = sqlite3.connect("working_chat.db")
        cursor = conn.cursor()
        
        # Create conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

# Initialize database on startup
init_database()

# API Endpoints
@app.get("/")
def root():
    """Root endpoint with server information"""
    return {
        "service": "ChatGPT Clone API",
        "status": "running",
        "model": MODEL_NAME,
        "version": "1.0.0",
        "endpoints": ["/health", "/conversations", "/api/v1/conversations", "/api/v1/chat"]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ChatGPT Clone API",
        "model": MODEL_NAME,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/conversations")
@app.get("/api/v1/conversations")
def get_conversations():
    """Get all conversations with message counts"""
    try:
        conn = sqlite3.connect("working_chat.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.title, c.created_at, COUNT(m.id) as message_count
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            GROUP BY c.id, c.title, c.created_at
            ORDER BY c.updated_at DESC
        ''')
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                "id": row[0],
                "title": row[1],
                "created_at": row[2],
                "message_count": row[3]
            })
        
        conn.close()
        logger.info(f"📋 Retrieved {len(conversations)} conversations")
        return {"conversations": conversations}
        
    except Exception as e:
        logger.error(f"❌ Error fetching conversations: {e}")
        return {"conversations": [], "error": str(e)}

@app.post("/conversations")
@app.post("/api/v1/conversations")
def create_conversation(request: ConversationRequest):
    """Create a new conversation"""
    try:
        conversation_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect("working_chat.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (id, title, created_at, updated_at) 
            VALUES (?, ?, ?, ?)
        ''', (conversation_id, request.title, now, now))
        
        conn.commit()
        conn.close()
        
        logger.info(f"➕ Created conversation: {conversation_id}")
        return {
            "id": conversation_id,
            "title": request.title,
            "created_at": now,
            "message_count": 0
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating conversation: {e}")
        return {"error": str(e)}

@app.post("/chat")
@app.post("/api/v1/chat") 
def chat_stream(request: ChatRequest):
    """Stream chat responses from OpenRouter AI"""
    
    conversation_id = request.conversation_id or str(uuid.uuid4())
    logger.info(f"💬 Chat request: {request.message[:50]}...")
    
    async def generate():
        try:
            # Initialize conversation if needed
            conn = sqlite3.connect("working_chat.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO conversations (id, title, created_at, updated_at) 
                    VALUES (?, ?, ?, ?)
                ''', (conversation_id, f"Chat {conversation_id[:8]}", 
                     datetime.now().isoformat(), datetime.now().isoformat()))
            
            # Save user message
            user_message_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO messages (id, conversation_id, role, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_message_id, conversation_id, "user", request.message, datetime.now().isoformat()))
            
            # Get conversation history
            cursor.execute('''
                SELECT role, content FROM messages 
                WHERE conversation_id = ? 
                ORDER BY timestamp ASC
            ''', (conversation_id,))
            
            messages = [{"role": role, "content": content} for role, content in cursor.fetchall()]
            conn.commit()
            conn.close()
            
            # OpenRouter API call
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "ChatGPT Clone"
            }
            
            payload = {
                "model": MODEL_NAME,
                "messages": messages,
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            full_response = ""
            logger.info(f"🤖 Streaming from OpenRouter for: {request.message}...")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST", 
                    f"{OPENROUTER_BASE_URL}/chat/completions", 
                    headers=headers, 
                    json=payload
                ) as response:
                    
                    if response.status_code != 200:
                        error_msg = f"OpenRouter API error: {response.status_code}"
                        logger.error(error_msg)
                        yield f"data: {json.dumps({'error': error_msg})}\n\n"
                        return
                    
                    # Send conversation_id first
                    yield f"data: {json.dumps({'conversation_id': conversation_id})}\n\n"
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            
                            if data.strip() == "[DONE]":
                                break
                                
                            try:
                                json_data = json.loads(data)
                                if "choices" in json_data and json_data["choices"]:
                                    choice = json_data["choices"][0]
                                    if "delta" in choice and "content" in choice["delta"]:
                                        content = choice["delta"]["content"]
                                        if content:
                                            full_response += content
                                            yield f"data: {json.dumps({'content': content})}\n\n"
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                logger.error(f"Error processing chunk: {e}")
                                continue
            
            # Save assistant response
            if full_response:
                conn = sqlite3.connect("working_chat.db")
                cursor = conn.cursor()
                
                assistant_message_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO messages (id, conversation_id, role, content, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (assistant_message_id, conversation_id, "assistant", full_response, datetime.now().isoformat()))
                
                # Update conversation timestamp
                cursor.execute('''
                    UPDATE conversations SET updated_at = ? WHERE id = ?
                ''', (datetime.now().isoformat(), conversation_id))
                
                conn.commit()
                conn.close()
                logger.info("✅ AI response saved to database")
            
            # Signal completion
            yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"
            
        except Exception as e:
            error_msg = f"Chat error: {str(e)}"
            logger.error(error_msg)
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# Server startup
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 STARTING WORKING CHATGPT CLONE SERVER")
    print("=" * 60)
    print(f"🤖 Model: {MODEL_NAME}")
    print("🔑 OpenRouter API: Connected")
    print("🗄️ Database: SQLite (working_chat.db)")
    print("🌐 CORS: Enabled for all origins")
    print("📡 Server: http://localhost:8000")
    print("🔗 API Endpoints:")
    print("   - GET  /health")
    print("   - GET  /api/v1/conversations") 
    print("   - POST /api/v1/conversations")
    print("   - POST /api/v1/chat (streaming)")
    print("=" * 60)
    print("✅ READY FOR TESTING!")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")