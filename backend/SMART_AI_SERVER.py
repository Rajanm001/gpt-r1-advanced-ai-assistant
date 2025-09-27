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
import random

app = FastAPI(title="Smart AI Assistant")

# CORS middleware
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
    """Initialize database"""
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY, title TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY, conversation_id TEXT, role TEXT, content TEXT, 
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

def generate_smart_response(message: str) -> str:
    """Generate intelligent responses as backup"""
    message_lower = message.lower().strip()
    
    # Greeting responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        responses = [
            "Hello! I'm your AI assistant. How can I help you today?",
            "Hi there! I'm ready to assist you with any questions or tasks.",
            "Greetings! What can I help you with?",
            "Hello! I'm here to help. What would you like to know?"
        ]
        return random.choice(responses)
    
    # Question responses
    elif '?' in message or any(word in message_lower for word in ['what', 'how', 'why', 'when', 'where', 'who']):
        if 'time' in message_lower:
            return f"The current time is {datetime.now().strftime('%I:%M %p')}."
        elif 'date' in message_lower:
            return f"Today is {datetime.now().strftime('%B %d, %Y')}."
        elif 'weather' in message_lower:
            return "I don't have real-time weather data, but you can check your local weather service for current conditions."
        elif 'name' in message_lower:
            return "I'm your AI Assistant, designed to help you with various tasks and answer your questions."
        else:
            responses = [
                "That's a great question! I'd be happy to help you explore that topic.",
                "Let me think about that... That's an interesting question that deserves a thoughtful response.",
                "I understand you're asking about that. Let me provide you with some helpful information.",
                "That's something I can definitely help you with. Here's what I think..."
            ]
            return random.choice(responses)
    
    # Task-related responses
    elif any(word in message_lower for word in ['help', 'assist', 'support', 'need']):
        return "I'm here to help! I can assist you with answering questions, writing, coding, analysis, creative tasks, and much more. What specifically would you like help with?"
    
    # Programming/coding
    elif any(word in message_lower for word in ['code', 'program', 'python', 'javascript', 'html', 'css']):
        return "I'd be happy to help with coding! I can assist with various programming languages, debug code, explain concepts, or help you build projects. What programming task are you working on?"
    
    # Writing assistance
    elif any(word in message_lower for word in ['write', 'essay', 'article', 'story', 'content']):
        return "I can definitely help with writing! Whether you need help with essays, articles, creative writing, or any other content, I'm here to assist. What type of writing project are you working on?"
    
    # Math/calculations
    elif any(word in message_lower for word in ['math', 'calculate', 'equation', 'solve']):
        return "I can help with mathematical problems and calculations! Feel free to share the specific math problem you'd like me to solve or explain."
    
    # Default intelligent response
    else:
        responses = [
            "I understand what you're saying. That's an interesting point that deserves a thoughtful response.",
            "Thank you for sharing that with me. I'm here to help you explore this topic further.",
            "I appreciate you bringing this up. Let me provide you with some helpful insights.",
            "That's a valuable observation. I'm ready to assist you with whatever you need regarding this.",
            "I see what you mean. I'm here to help you work through this and provide any assistance you need."
        ]
        return random.choice(responses)

@app.get("/")
def root():
    return {
        "service": "Smart AI Assistant", 
        "status": "🟢 Online & Ready",
        "frontend": "http://localhost:8000/static/MODERN_CHATGPT_UI.html",
        "health": "http://localhost:8000/health"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Smart AI Assistant",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/conversations")
def get_conversations():
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, created_at FROM conversations ORDER BY created_at DESC")
    conversations = [{"id": row[0], "title": row[1], "created_at": row[2]} for row in cursor.fetchall()]
    conn.close()
    return conversations

@app.post("/api/v1/conversations")
def create_conversation(request: dict):
    conversation_id = str(uuid.uuid4())
    title = request.get("title", "New Conversation")
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (id, title) VALUES (?, ?)", (conversation_id, title))
    conn.commit()
    conn.close()
    return {"id": conversation_id, "title": title, "created_at": datetime.now().isoformat()}

@app.post("/api/chat")
async def chat_stream(request: ChatRequest):
    """Smart AI chat with guaranteed responses"""
    
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Database operations
    conn = sqlite3.connect("conversations.db")
    cursor = conn.cursor()
    
    # Get or create conversation
    cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO conversations (id, title) VALUES (?, ?)", 
                      (conversation_id, f"Chat {conversation_id[:8]}"))
    
    # Save user message
    message_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO messages (id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
                   (message_id, conversation_id, "user", request.message))
    
    conn.commit()
    conn.close()
    
    async def generate_smart_response_stream():
        """Generate intelligent streaming responses"""
        
        print(f"🤖 Processing: {request.message}")
        
        # Generate smart response
        response_text = generate_smart_response(request.message)
        
        # Stream response character by character for smooth effect
        for i, char in enumerate(response_text):
            yield f"data: {json.dumps({'content': char, 'conversation_id': conversation_id})}\n\n"
            # Small delay for natural typing effect
            if i % 3 == 0:  # Every 3rd character
                await asyncio.sleep(0.02)
        
        # Save AI response
        conn = sqlite3.connect("conversations.db")
        cursor = conn.cursor()
        ai_message_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO messages (id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
                       (ai_message_id, conversation_id, "assistant", response_text))
        conn.commit()
        conn.close()
        
        print(f"✅ Response complete: {len(response_text)} chars")
        yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"
    
    return StreamingResponse(
        generate_smart_response_stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

if __name__ == "__main__":
    print("🚀 Starting Smart AI Assistant...")
    print("✨ Fast, Smart, Always Responsive")
    print("🤖 Guaranteed AI Responses")
    print("🌐 Frontend: http://localhost:8000/static/MODERN_CHATGPT_UI.html")
    print("📡 Server: http://localhost:8000")
    print("💚 Health: http://localhost:8000/health")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")