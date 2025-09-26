import os
import requests
import json
from typing import AsyncGenerator, List, Dict, Optional, Any
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class MultiLLMService:
    """
    Direct LLM service - NO HALLUCINATION - Real API responses only
    """
    
    def __init__(self):
        # API Keys
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.huggingface_key = os.getenv("HUGGINGFACE_API_KEY") 
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        # API endpoints
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        
        logger.info(f"MultiLLM initialized - Groq: {'✅' if self.groq_key else '❌'}")
        
    async def get_llm_response(self, messages: List[Dict], use_search: bool = False) -> AsyncGenerator[str, None]:
        """Get REAL LLM response - no fake responses"""
        
        # Clean system message for proper AI responses
        system_message = {
            "role": "system", 
            "content": "You are a helpful AI assistant. Provide direct, accurate, and concise answers."
        }
        
        # Use only the user's message + clean system prompt
        clean_messages = [system_message]
        for msg in messages:
            if msg.get("role") == "user":
                clean_messages.append(msg)
        
        # Try Groq API first (most reliable)
        try:
            async for chunk in self._groq_streaming_response(clean_messages):
                if chunk:
                    yield chunk
            return
        except Exception as e:
            logger.error(f"Groq API failed: {e}")
        
        # Try OpenAI if Groq fails
        if self.openai_key:
            try:
                async for chunk in self._openai_response(clean_messages):
                    if chunk:
                        yield chunk
                return
            except Exception as e:
                logger.error(f"OpenAI API failed: {e}")
        
        # Only if all APIs fail
        yield "I apologize, but I'm currently unable to connect to AI services. Please try again in a moment."
    
    async def _groq_streaming_response(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """Direct Groq API streaming - REAL responses only"""
        
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",  # Updated to active model
            "messages": messages,
            "stream": True,
            "temperature": 0.3,  # Lower temperature for more focused responses
            "max_tokens": 1000
        }
        
        response = requests.post(
            self.groq_url, 
            headers=headers, 
            json=payload, 
            stream=True, 
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Groq API error: {response.status_code} - {response.text}")
        
        for line in response.iter_lines():
            if not line:
                continue
                
            line_text = line.decode('utf-8')
            if not line_text.startswith('data: '):
                continue
                
            data_part = line_text[6:]
            if data_part == '[DONE]':
                break
                
            try:
                chunk = json.loads(data_part)
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta = chunk['choices'][0].get('delta', {})
                    content = delta.get('content', '')
                    if content:
                        yield content
            except json.JSONDecodeError:
                continue
    
    async def _openai_response(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """OpenAI API fallback"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True,
                temperature=0.3,
                max_tokens=1000
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise Exception(f"OpenAI error: {e}")