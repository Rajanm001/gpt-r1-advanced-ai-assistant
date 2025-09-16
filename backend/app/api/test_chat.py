"""
GPT.R1 - Simple Chat API for Testing (No Auth Required)
Testing endpoint to debug chat functionality
Created by: Rajan Mishra
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Dict, Optional
import json
import asyncio
from datetime import datetime

from ..services.openai_service import OpenAIService

router = APIRouter()
openai_service = OpenAIService()

@router.post("/api/v1/chat/test")
async def test_chat(request: dict):
    """
    Simple Chat Test Endpoint (No Authentication Required)
    For debugging and testing chat functionality
    """
    try:
        message = request.get("message", "")
        
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Create a simple message history for testing
        messages = [
            {"role": "user", "content": message}
        ]
        
        async def generate_response():
            """Generator for streaming response"""
            try:
                full_response = ""
                
                # Stream the response
                async for chunk in openai_service.create_chat_completion_stream(
                    messages=messages
                ):
                    if chunk:
                        full_response += chunk
                        yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                        await asyncio.sleep(0.01)
                
                # Send completion signal
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.post("/api/v1/chat/simple")
async def simple_chat(request: dict):
    """
    Simple non-streaming chat for basic testing
    """
    try:
        message = request.get("message", "")
        
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Create response
        response_text = f"GPT.R1 Response to: '{message}'\n\nHello! I'm GPT.R1, Rajan Mishra's advanced AI assistant. I'm working perfectly and ready to help you with any questions or tasks. This is a test response to show that the chat functionality is working properly."
        
        return {
            "message": response_text,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/api/v1/test/status")
async def test_status():
    """
    Test endpoint to check if API is working
    """
    return {
        "status": "working",
        "service": "GPT.R1 Chat API",
        "author": "Rajan Mishra",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "test_chat": "/api/v1/chat/test",
            "simple_chat": "/api/v1/chat/simple",
            "main_chat": "/api/v1/chat"
        }
    }