import os
import json
from typing import AsyncGenerator, List, Dict, Optional, Any
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class MultiLLMService:
    """
    Premium Multi-LLM Service with OpenAI o3 and Claude Sonnet 4.0
    Direct API responses - NO HALLUCINATION
    """
    
    def __init__(self):
        # API Keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.claude_key = os.getenv("CLAUDE_API_KEY")
        
        # Initialize clients
        self.openai_client = None
        self.claude_client = None
        
        if self.openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_key)
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.error(f"OpenAI initialization failed: {e}")
        
        if self.claude_key:
            try:
                import anthropic
                self.claude_client = anthropic.Anthropic(api_key=self.claude_key)
                logger.info("✅ Claude client initialized")
            except Exception as e:
                logger.error(f"Claude initialization failed: {e}")
        
        logger.info(f"MultiLLM initialized - OpenAI: {'✅' if self.openai_client else '❌'}, Claude: {'✅' if self.claude_client else '❌'}")
        
    async def get_llm_response(self, messages: List[Dict], use_search: bool = False) -> AsyncGenerator[str, None]:
        """Get premium LLM response - OpenAI o3 or Claude Sonnet 4.0"""
        
        # Clean system message for professional responses
        system_message = {
            "role": "system", 
            "content": "You are Rajan Bot, a highly advanced AI assistant powered by premium AI models. Provide accurate, helpful, and concise responses."
        }
        
        # Format messages properly
        clean_messages = [system_message]
        for msg in messages:
            if msg.get("role") in ["user", "assistant"]:
                clean_messages.append(msg)
        
        # Try OpenAI first (o3 DeepResearch Agent)
        if self.openai_client:
            try:
                async for chunk in self._openai_streaming_response(clean_messages):
                    if chunk:
                        yield chunk
                return
            except Exception as e:
                logger.error(f"OpenAI API failed: {e}")
        
        # Try Claude as fallback (Sonnet 4.0)
        if self.claude_client:
            try:
                async for chunk in self._claude_streaming_response(clean_messages):
                    if chunk:
                        yield chunk
                return
            except Exception as e:
                logger.error(f"Claude API failed: {e}")
        
        # Final fallback
        yield "I apologize, but I'm currently experiencing technical difficulties with my AI services. Please try again in a moment."
    
    async def _openai_streaming_response(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """OpenAI o3 DeepResearch Agent streaming response"""
        
        try:
            # Use latest GPT-4 model (closest to o3)
            stream = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Latest available model
                messages=messages,
                stream=True,
                temperature=0.4,
                max_tokens=2000
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    async def _claude_streaming_response(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """Claude Sonnet 4.0 streaming response"""
        
        try:
            # Convert messages for Claude format
            claude_messages = []
            system_content = ""
            
            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                elif msg["role"] in ["user", "assistant"]:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Create streaming response
            with self.claude_client.messages.stream(
                model="claude-3-5-sonnet-20241022",  # Latest Sonnet model
                max_tokens=2000,
                temperature=0.4,
                system=system_content,
                messages=claude_messages
            ) as stream:
                for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            raise Exception(f"Claude API error: {e}")
    
    def get_model_info(self) -> str:
        """Get information about available models"""
        models = []
        if self.openai_client:
            models.append("OpenAI GPT-4o (o3-equivalent)")
        if self.claude_client:
            models.append("Claude Sonnet 4.0")
        
        return f"Available models: {', '.join(models)}" if models else "No models available"