import os
import asyncio
import logging
from typing import AsyncGenerator, List, Dict, cast, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class MultiLLMService:
    """
    Premium AI Service - OpenAI + Claude Integration
    Real AI responses only - No hallucination
    """
    
    def __init__(self):
        # API Keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.claude_key = os.getenv("CLAUDE_API_KEY")
        
        # Initialize clients safely
        self.openai_client = None
        self.claude_client = None
        
        # Try to initialize OpenAI
        try:
            from openai import OpenAI
            if self.openai_key:
                self.openai_client = OpenAI(api_key=self.openai_key)
                logger.info("✅ OpenAI initialized successfully")
        except Exception as e:
            logger.warning(f"OpenAI initialization failed: {e}")
        
        # Try to initialize Claude
        try:
            import anthropic
            if self.claude_key:
                self.claude_client = anthropic.Anthropic(api_key=self.claude_key)
                logger.info("✅ Claude initialized successfully")
        except Exception as e:
            logger.warning(f"Claude initialization failed: {e}")
        
        logger.info(f"Premium LLM Service ready - OpenAI: {'✅' if self.openai_client else '❌'}, Claude: {'✅' if self.claude_client else '❌'}")
        
    async def get_llm_response(self, messages: List[Dict], use_search: bool = False) -> AsyncGenerator[str, None]:
        """Get premium AI response"""
        
        # Clean system message
        system_message = {
            "role": "system", 
            "content": "You are Rajan Bot, a helpful AI assistant. Provide clear, accurate, and concise responses."
        }
        
        # Format messages
        formatted_messages = [system_message]
        for msg in messages:
            if msg.get("role") in ["user", "assistant"] and msg.get("content"):
                formatted_messages.append({
                    "role": msg["role"],
                    "content": str(msg["content"])
                })
        
        # Try OpenAI first
        if self.openai_client:
            try:
                async for chunk in self._openai_response(formatted_messages):
                    if chunk:
                        yield chunk
                return
            except Exception as e:
                logger.error(f"OpenAI failed: {e}")
        
        # Try Claude as backup
        if self.claude_client:
            try:
                async for chunk in self._claude_response(formatted_messages):
                    if chunk:
                        yield chunk
                return
            except Exception as e:
                logger.error(f"Claude failed: {e}")
        
        # Ultimate fallback
        yield "Hello! I'm Rajan Bot. I'm currently having trouble connecting to AI services. Please check the API keys and try again."
    
    async def _openai_response(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """OpenAI streaming response"""
        
        try:
            # Import here to avoid issues
            from openai.types.chat import ChatCompletionMessageParam
            
            # Convert messages to proper format
            openai_messages = []
            for msg in messages:
                openai_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Cast to proper type
            typed_messages = cast(List[ChatCompletionMessageParam], openai_messages)
            
            stream = self.openai_client.chat.completions.create(
                model="gpt-4",  # Use reliable model
                messages=typed_messages,
                stream=True,
                temperature=0.7,
                max_tokens=1500
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    await asyncio.sleep(0.01)
                    
        except Exception as e:
            raise Exception(f"OpenAI error: {e}")
    
    async def _claude_response(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """Claude response (non-streaming for simplicity)"""
        
        try:
            # Extract system and user messages
            system_content = ""
            claude_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                elif msg["role"] in ["user", "assistant"]:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Get response from Claude
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                system=system_content,
                messages=claude_messages,
                max_tokens=1500,
                temperature=0.7
            )
            
            # Yield the response in chunks for streaming effect
            content = response.content[0].text if response.content else "No response from Claude"
            words = content.split()
            
            for i in range(0, len(words), 3):  # 3 words at a time
                chunk = " ".join(words[i:i+3]) + " "
                yield chunk
                await asyncio.sleep(0.05)  # Streaming effect
                
        except Exception as e:
            raise Exception(f"Claude error: {e}")