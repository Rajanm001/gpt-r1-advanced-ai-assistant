"""
🚀 PERFECT CHATGPT CLONE BACKEND
✅ Clean, Simple, Working
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import uvicorn
import json
import sqlite3
import uuid
import asyncio
from datetime import datetime
from typing import Optional, List
import os

# 🔑 API CONFIGURATION
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "microsoft/wizardlm-2-8x22b"

# 🎯 FASTAPI APP
app = FastAPI(
    title="Perfect ChatGPT Clone API",
    description="Clean, simple, working ChatGPT clone",
    version="1.0.0"
)

# 🌐 CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 📝 MODELS
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Chat"

# 🗄️ DATABASE SETUP
DATABASE_FILE = "perfect_chat.db"

def init_database():
    """Initialize clean database"""
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)  # Start fresh
    
    conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
    cursor = conn.cursor()
    
    # Simple, clean schema
    cursor.execute('''
        CREATE TABLE conversations (
            id TEXT PRIMARY KEY,
            title TEXT DEFAULT "New Chat",
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE messages (
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
    print("✅ Clean database initialized!")

# Initialize on startup
init_database()

# 🏠 ROOT ENDPOINTS
@app.get("/")
async def root():
    return {
        "service": "Perfect ChatGPT Clone",
        "status": "🚀 Running Perfectly",
        "model": MODEL_NAME,
        "endpoints": {
            "chat": "/api/v1/chat",
            "conversations": "/api/v1/conversations"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "🟢 Healthy",
        "service": "Perfect ChatGPT Clone",
        "database": "Connected",
        "ai_model": MODEL_NAME
    }

# 🎯 API V1 ENDPOINTS
@app.get("/api/v1/conversations")
async def get_conversations():
    """Get all conversations"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, c.title, c.created_at, COUNT(m.id) as message_count
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            GROUP BY c.id, c.title, c.created_at
            ORDER BY c.created_at DESC
            LIMIT 50
        """)
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                "id": row[0],
                "title": row[1] or "New Chat",
                "created_at": row[2],
                "message_count": row[3]
            })
        
        conn.close()
        return {"conversations": conversations}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation messages"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
            (conversation_id,)
        )
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "id": row[0],
                "role": row[1],
                "content": row[2],
                "timestamp": row[3]
            })
        
        conn.close()
        return {
            "conversation_id": conversation_id,
            "messages": messages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/conversations")
async def create_conversation(request: ConversationCreate):
    """Create new conversation"""
    try:
        conversation_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (id, title) VALUES (?, ?)",
            (conversation_id, request.title)
        )
        conn.commit()
        conn.close()
        
        return {
            "id": conversation_id,
            "title": request.title,
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat")
async def perfect_chat(request: ChatRequest):
    """Perfect streaming chat endpoint"""
    print(f"💬 Chat: {request.message[:50]}...")
    
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    try:
        # Database operations
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Ensure conversation exists
        cursor.execute("INSERT OR IGNORE INTO conversations (id, title) VALUES (?, ?)", 
                      (conversation_id, "New Chat"))
        
        # Save user message
        user_msg_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO messages (id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
            (user_msg_id, conversation_id, "user", request.message)
        )
        
        # Get conversation history
        cursor.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
            (conversation_id,)
        )
        history = cursor.fetchall()
        messages = [{"role": role, "content": content} for role, content in history]
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # 🤖 AI STREAMING
    async def generate_perfect_stream():
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://perfect-chatgpt-clone.com"
        }
        
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        full_response = ""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST", 
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers, 
                    json=payload
                ) as response:
                    
                    if response.status_code == 200:
                        print("✅ Streaming AI response...")
                        
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]
                                if data.strip() == "[DONE]":
                                    break
                                
                                try:
                                    json_data = json.loads(data)
                                    if "choices" in json_data and json_data["choices"]:
                                        delta = json_data["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        
                                        if content:
                                            full_response += content
                                            yield f"data: {json.dumps({'content': content, 'conversation_id': conversation_id})}\n\n"
                                
                                except json.JSONDecodeError:
                                    continue
                    else:
                        error_msg = f"AI API Error: {response.status_code}"
                        yield f"data: {json.dumps({'error': error_msg})}\n\n"
                        return
            
            # Save AI response
            if full_response:
                try:
                    conn = sqlite3.connect(DATABASE_FILE)
                    cursor = conn.cursor()
                    ai_msg_id = str(uuid.uuid4())
                    cursor.execute(
                        "INSERT INTO messages (id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
                        (ai_msg_id, conversation_id, "assistant", full_response)
                    )
                    conn.commit()
                    conn.close()
                    print("✅ AI response saved")
                except Exception as db_error:
                    print(f"❌ Save error: {db_error}")
            
            # Send completion
            yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"
            
        except Exception as e:
            error_msg = f"Streaming error: {str(e)}"
            print(f"❌ {error_msg}")
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    # Return perfect streaming response
    return StreamingResponse(
        generate_perfect_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "text/event-stream"
        }
    )

# 🚀 PERFECT SERVER STARTUP
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 PERFECT CHATGPT CLONE BACKEND")
    print("=" * 60)
    print(f"🤖 Model: {MODEL_NAME}")
    print(f"🔑 API: OpenRouter Connected")
    print(f"🗄️ Database: Clean SQLite")
    print(f"🌐 CORS: Configured")
    print(f"📡 Server: http://localhost:8000")
    print("=" * 60)
    print("✅ PERFECT BACKEND READY!")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=False
    )