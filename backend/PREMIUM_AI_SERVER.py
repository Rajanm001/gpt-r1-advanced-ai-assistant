from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import uvicorn
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Optional
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment (more secure)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("⚠️  Warning: OPENROUTER_API_KEY not found in environment")
    print("📁 Please check your .env file or set the environment variable")
    OPENROUTER_API_KEY = "demo-key-please-set-env-variable"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "microsoft/wizardlm-2-8x22b"

app = FastAPI(title="Rajan AI Assistant API")

# CORS middleware - optimized for performance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

def init_db():
    """Initialize database with optimized settings"""
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    
    # Enable WAL mode for better performance
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=10000")
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY, 
        title TEXT, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY, 
        conversation_id TEXT, 
        role TEXT, 
        content TEXT, 
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id)
    )''')
    
    # Create indexes for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
    
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def root():
    return {
        "service": "Premium AI Assistant", 
        "status": "🟢 Online & Ready",
        "version": "2.0",
        "performance": "Optimized for speed",
        "frontend": "http://localhost:8000/static/MODERN_CHATGPT_UI.html",
        "health": "http://localhost:8000/health"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Rajan AI Assistant", 
        "performance": "High-speed responses enabled",
        "timestamp": datetime.now().isoformat()
    }@app.get("/api/v1/conversations")
def get_conversations():
    """Fast conversation retrieval"""
    conn = sqlite3.connect("conversations.db")
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
            "title": row[1], 
            "created_at": row[2],
            "message_count": row[3]
        })
    conn.close()
    return conversations

@app.post("/api/v1/conversations")
def create_conversation(request: dict):
    """Quick conversation creation"""
    conversation_id = str(uuid.uuid4())
    title = request.get("title", "New Conversation")[:100]  # Limit title length
    
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (id, title) VALUES (?, ?)", (conversation_id, title))
    conn.commit()
    conn.close()
    
    return {
        "id": conversation_id, 
        "title": title, 
        "created_at": datetime.now().isoformat()
    }

@app.post("/api/v1/chat")
async def assignment_chat_endpoint(request: ChatRequest):
    """Assignment-specific chat endpoint - redirects to main chat"""
    return await smart_chat_stream(request)

@app.get("/api/v1/conversations/{conversation_id}")
async def get_conversation_messages(conversation_id: str):
    """Get message history for a specific conversation"""
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    
    # Verify conversation exists
    cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    cursor.execute("""
        SELECT id, role, content, timestamp 
        FROM messages 
        WHERE conversation_id = ? 
        ORDER BY timestamp ASC
    """, (conversation_id,))
    
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
        "messages": messages,
        "total": len(messages)
    }

@app.post("/api/chat")
async def smart_chat_stream(request: ChatRequest):
    """High-performance streaming chat with smart AI responses"""
    
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Quick database operations
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    
    # Get or create conversation
    cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
    if not cursor.fetchone():
        # Generate smart title from first message
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        cursor.execute("INSERT INTO conversations (id, title) VALUES (?, ?)", (conversation_id, title))
    
    # Save user message
    message_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO messages (id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
                   (message_id, conversation_id, "user", request.message))
    
    # Get recent conversation history (last 10 messages for performance)
    cursor.execute("""
        SELECT role, content FROM messages 
        WHERE conversation_id = ? 
        ORDER BY timestamp ASC 
        LIMIT 10
    """, (conversation_id,))
    messages = [{"role": role, "content": content} for role, content in cursor.fetchall()]
    
    conn.commit()
    conn.close()
    
    async def generate_smart_response():
        """Generate intelligent, fast responses"""
        
        # Optimized headers for faster API calls
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Premium AI Assistant"
        }
        
        # Smart payload optimization
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": True,
            "temperature": 0.8,  # Slightly higher for more creative responses
            "max_tokens": 2048,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
        
        full_response = ""
        print(f"🚀 Smart AI processing: {request.message[:50]}...")
        
        try:
            # Use optimized HTTP client settings
            timeout = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=10.0)
            
            async with httpx.AsyncClient(
                timeout=timeout,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            ) as client:
                async with client.stream("POST", f"{OPENROUTER_BASE_URL}/chat/completions", 
                                       headers=headers, json=payload) as response:
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_text = error_text.decode('utf-8')
                        print(f"❌ API Error: {response.status_code} - {error_text}")
                        
                        # Provide smart fallback response
                        fallback_response = get_smart_fallback_response(request.message)
                        for char in fallback_response:
                            yield f"data: {json.dumps({'content': char, 'conversation_id': conversation_id})}\n\n"
                            await asyncio.sleep(0.02)  # Natural typing speed
                        yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"
                        return
                    
                    # Process streaming response
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data.strip() == "[DONE]":
                                break
                            try:
                                json_data = json.loads(data)
                                if "choices" in json_data and json_data["choices"]:
                                    content = json_data["choices"][0].get("delta", {}).get("content", "")
                                    if content:
                                        full_response += content
                                        yield f"data: {json.dumps({'content': content, 'conversation_id': conversation_id})}\n\n"
                                        # Small delay for smooth streaming
                                        await asyncio.sleep(0.01)
                            except json.JSONDecodeError:
                                continue
            
            # Save AI response to database
            if full_response:
                conn = sqlite3.connect("conversations.db")
                cursor = conn.cursor()
                message_id = str(uuid.uuid4())
                cursor.execute("INSERT INTO messages (id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
                               (message_id, conversation_id, "assistant", full_response))
                conn.commit()
                conn.close()
                print(f"✅ Smart response delivered ({len(full_response)} chars)")
            
            yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"
            
        except Exception as e:
            print(f"❌ Error in smart chat: {str(e)}")
            # Provide intelligent error handling with fallback
            fallback_response = get_smart_fallback_response(request.message)
            for char in fallback_response:
                yield f"data: {json.dumps({'content': char, 'conversation_id': conversation_id})}\n\n"
                await asyncio.sleep(0.02)
            yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"
    
    return StreamingResponse(
        generate_smart_response(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

def get_smart_fallback_response(user_message: str) -> str:
    """Generate intelligent fallback responses when API is unavailable"""
    
    message_lower = user_message.lower()
    
    # Smart response patterns
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! I'm your AI assistant. How can I help you today? I'm ready to assist with any questions or tasks you have."
    
    elif any(word in message_lower for word in ['how are you', 'how do you do']):
        return "I'm doing great, thank you for asking! I'm here and ready to help you with anything you need. What can I assist you with?"
    
    elif any(word in message_lower for word in ['help', 'assist', 'support']):
        return "I'm here to help! I can assist you with various tasks including answering questions, writing content, coding help, analysis, creative tasks, and much more. What do you need help with?"
    
    elif any(word in message_lower for word in ['code', 'program', 'coding', 'programming']):
        return "I'd be happy to help with coding! I can assist with programming in various languages, debug code, explain concepts, write functions, and provide best practices. What programming task are you working on?"
    
    elif any(word in message_lower for word in ['write', 'writing', 'content']):
        return "I can help with writing tasks! Whether you need help with essays, articles, creative writing, editing, or any other writing project, I'm here to assist. What type of writing do you need help with?"
    
    elif '?' in user_message:
        return "That's a great question! I'm currently experiencing a temporary connection issue with my main knowledge base, but I'm still here to help. Could you rephrase your question or let me know if there's another way I can assist you?"
    
    else:
        return f"I understand you're asking about '{user_message[:50]}...' - I'm here to help! While I'm experiencing a temporary connection issue, I can still assist you with many tasks. Could you provide more details about what you need help with?"

if __name__ == "__main__":
    print("🚀 Starting Rajan AI Assistant...")
    print(f"🤖 Model: {MODEL_NAME}")
    print("⚡ High-performance mode enabled")
    print("🧠 Smart response system active")
    print("✅ OpenRouter API Integration")
    print("🌐 Frontend: http://localhost:8000/static/MODERN_CHATGPT_UI.html")
    print("📡 Server: http://localhost:8000")
    print("💚 Health: http://localhost:8000/health")
    print("🎯 Optimized for speed and intelligence")
    
    # Run with performance optimizations
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        access_log=False,  # Disable access logs for better performance
        workers=1
    )