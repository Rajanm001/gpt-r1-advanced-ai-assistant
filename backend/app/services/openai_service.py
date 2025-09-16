import asyncio
import json
from typing import List, Dict, AsyncGenerator
import openai
from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas import Message


class OpenAIService:
    """Service for OpenAI API interactions."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.MODEL_NAME
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
    
    async def create_chat_completion_stream(
        self, 
        messages: List[Message], 
        system_prompt: str = None
    ) -> AsyncGenerator[str, None]:
        """Create streaming chat completion."""
        try:
            # Convert messages to OpenAI format
            openai_messages = []
            
            if system_prompt:
                openai_messages.append({"role": "system", "content": system_prompt})
            
            for message in messages:
                openai_messages.append({
                    "role": message.role,
                    "content": message.content
                })
            
            # Create streaming completion
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    async def create_chat_completion(
        self, 
        messages: List[Message], 
        system_prompt: str = None
    ) -> str:
        """Create non-streaming chat completion."""
        try:
            # Convert messages to OpenAI format
            openai_messages = []
            
            if system_prompt:
                openai_messages.append({"role": "system", "content": system_prompt})
            
            for message in messages:
                openai_messages.append({
                    "role": message.role,
                    "content": message.content
                })
            
            # Create completion
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error: {str(e)}"


# Create service instance
openai_service = OpenAIService()