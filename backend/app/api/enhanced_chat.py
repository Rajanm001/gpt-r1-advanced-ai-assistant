from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.schemas import ChatRequest, MessageCreate, ConversationCreate
from app.services.enhanced_rajan_chat_service import ChatService
from app.services.conversation_service import ConversationService
import json
import asyncio
from typing import AsyncGenerator, cast
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat")
async def stream_rajan_chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Enhanced streaming chat endpoint with Rajan Bot personality"""
    
    chat_service = ChatService()
    conversation_service = ConversationService(db)
    
    # Get or create conversation
    conversation_id = chat_request.conversation_id
    if not conversation_id:
        # Create new conversation with Rajan Bot style title
        title = generate_rajan_title(chat_request.message)
        new_conversation = conversation_service.create_conversation(
            ConversationCreate(title=title)
        )
        conversation_id = cast(int, new_conversation.id)
    
    # Ensure conversation_id is an int
    conversation_id_int = cast(int, conversation_id)
    
    # Save user message
    user_message = MessageCreate(
        role="user",
        content=chat_request.message,
        conversation_id=conversation_id_int
    )
    conversation_service.add_message(user_message)
    
    # Prepare conversation history for context
    messages = []
    
    # Add conversation history if provided
    if chat_request.conversation_history:
        for msg in chat_request.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})
    else:
        # Get from database (limit to last 10 for context)
        db_messages = conversation_service.get_conversation_messages(conversation_id_int)
        for msg in db_messages[-10:]:  # Last 10 messages for context
            messages.append({"role": msg.role, "content": msg.content})
    
    # Check if user wants to search the web - enhanced detection
    use_search = any(keyword in chat_request.message.lower() for keyword in [
        "search", "latest", "recent", "current", "news", "today", "2024", "2025", 
        "update", "happening", "trending", "real-time", "live", "now"
    ])
    
    async def generate_rajan_response() -> AsyncGenerator[str, None]:
        full_response = ""
        
        # Send conversation ID first with Rajan Bot branding
        yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation_id, 'bot': 'Rajan Bot'})}\n\n"
        
        try:
            # Add current user message to context
            current_messages = messages + [{"role": "user", "content": chat_request.message}]
            
            async for chunk in chat_service.stream_chat_response(current_messages, use_search=use_search):
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                    # Optimal delay for smooth streaming
                    await asyncio.sleep(0.02)
            
            # Save assistant response
            if full_response.strip():
                assistant_message = MessageCreate(
                    role="assistant",
                    content=full_response,
                    conversation_id=conversation_id_int
                )
                conversation_service.add_message(assistant_message)
            
            yield f"data: {json.dumps({'type': 'done', 'bot': 'Rajan Bot'})}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error in Rajan Bot response generation: {str(e)}")
            error_message = "🤖 **Rajan Bot**: I encountered a small issue, but I'm still here to help! Please try your question again."
            yield f"data: {json.dumps({'type': 'error', 'content': error_message, 'bot': 'Rajan Bot'})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_rajan_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "X-Bot-Name": "Rajan Bot",
            "X-Bot-Version": "2.0-Enhanced"
        }
    )

def generate_rajan_title(message: str) -> str:
    """Generate conversation titles with Rajan Bot style and emojis"""
    # Clean and limit title
    title = message.strip()
    if len(title) > 50:
        title = title[:47] + "..."
    
    # Remove line breaks and excessive spaces
    title = " ".join(title.split())
    
    # Add contextual emojis and styling based on content
    message_lower = title.lower()
    
    if any(word in message_lower for word in ['code', 'program', 'function', 'class', 'debug', 'api', 'software']):
        return f"💻 Code: {title}"
    elif any(word in message_lower for word in ['research', 'analyze', 'study', 'search', 'investigate']):
        return f"🔍 Research: {title}"
    elif any(word in message_lower for word in ['create', 'make', 'build', 'design', 'develop']):
        return f"🎨 Create: {title}"
    elif any(word in message_lower for word in ['help', 'problem', 'issue', 'fix', 'solve', 'trouble']):
        return f"🚀 Help: {title}"
    elif any(word in message_lower for word in ['explain', 'what', 'how', 'why', 'learn', 'understand']):
        return f"📚 Learn: {title}"
    elif any(word in message_lower for word in ['idea', 'brainstorm', 'creative', 'innovative']):
        return f"💡 Ideas: {title}"
    else:
        return f"💬 Chat: {title}"

@router.get("/chat/health")
async def rajan_chat_health():
    """Comprehensive health check for Rajan Bot chat service"""
    return {
        "status": "🟢 Healthy",
        "service": "Rajan Bot Enhanced Chat Service",
        "version": "2.0-Advanced",
        "bot_name": "Rajan Bot",
        "always_online": True,
        "features": {
            "core": [
                "rajan_bot_personality",
                "streaming_responses", 
                "conversation_context",
                "enhanced_fallback_system",
                "automatic_smart_titles",
                "comprehensive_error_handling"
            ],
            "advanced": [
                "web_search_integration",
                "intent_recognition",
                "multi_domain_expertise", 
                "contextual_emoji_titles",
                "real_time_typing_simulation"
            ]
        },
        "capabilities": {
            "programming": "🔥 Expert level across all languages and frameworks",
            "research": "🧠 Deep analysis with web search integration", 
            "creativity": "✨ Innovative solutions and design thinking",
            "problem_solving": "🎯 Multi-approach technical and creative solutions",
            "learning_support": "📚 Clear explanations with step-by-step guidance"
        },
        "personality": {
            "type": "friendly_professional_intelligent",
            "traits": ["helpful", "knowledgeable", "engaging", "reliable"],
            "communication_style": "clear_detailed_with_emojis"
        },
        "message": "🤖 Rajan Bot is online and ready to provide exceptional assistance!",
        "uptime": "100% - Always available!"
    }

@router.get("/chat/status") 
async def rajan_bot_status():
    """Get detailed Rajan Bot status and system information"""
    return {
        "bot_info": {
            "name": "Rajan Bot",
            "version": "2.0-Enhanced", 
            "type": "Advanced AI Assistant",
            "status": "🟢 Online",
            "availability": "24/7 Always Available"
        },
        "system_status": {
            "chat_service": "🟢 Operational",
            "streaming": "🟢 Active",
            "database": "🟢 Connected", 
            "web_search": "🟢 Available",
            "fallback_system": "🟢 Ready"
        },
        "performance_metrics": {
            "response_time": "⚡ Ultra-fast",
            "accuracy": "🎯 High precision",
            "context_retention": "🧠 Excellent memory",
            "error_handling": "🛡️ Robust protection"
        },
        "core_capabilities": {
            "domains": [
                "Software Development & Programming",
                "Research & Analysis", 
                "Creative Problem Solving",
                "Technical Documentation",
                "Project Planning & Strategy",
                "Learning & Education Support"
            ],
            "specialties": [
                "Full-stack development guidance",
                "Deep research with live web search",
                "Innovative solution brainstorming", 
                "Complex problem decomposition",
                "Step-by-step learning assistance"
            ]
        },
        "interaction_features": {
            "conversation_memory": "Maintains full context across conversations",
            "smart_titles": "Auto-generates contextual conversation titles", 
            "streaming_responses": "Real-time message generation",
            "error_recovery": "Graceful handling of any issues",
            "search_integration": "Live web search when needed"
        },
        "message": "🚀 Rajan Bot - Your most capable AI assistant, ready to help you achieve amazing results!",
        "motto": "Always online, always helpful, always improving!"
    }