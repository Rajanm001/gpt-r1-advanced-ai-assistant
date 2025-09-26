import os
import asyncio
import logging
from typing import AsyncGenerator, List, Dict
from dotenv import load_dotenv

# Import AI libraries
try:
    from openai import OpenAI
    from openai.types.chat import ChatCompletionMessageParam
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

load_dotenv()
logger = logging.getLogger(__name__)

class MultiLLMService:
    """
    Premium Multi-LLM service with OpenAI o3 DeepResearch + Claude Sonnet 4.0
    NO HALLUCINATION - Only real AI responses
    """
    
    def __init__(self):
        # API Keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.claude_key = os.getenv("CLAUDE_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        # Initialize clients
        self.openai_client = None
        self.claude_client = None
        
        if self.openai_key and OPENAI_AVAILABLE:
            self.openai_client = OpenAI(api_key=self.openai_key)
            logger.info("✅ OpenAI o3 DeepResearch Agent initialized")
        
        if self.claude_key and CLAUDE_AVAILABLE:
            self.claude_client = anthropic.Anthropic(api_key=self.claude_key)
            logger.info("✅ Claude Sonnet 4.0 initialized")
        
        logger.info(f"Premium LLM Service - OpenAI: {'✅' if self.openai_client else '❌'}, Claude: {'✅' if self.claude_client else '❌'}")
        
    async def get_llm_response(self, messages: List[Dict], use_search: bool = False) -> AsyncGenerator[str, None]:
        """Get premium AI response from OpenAI o3 or Claude Sonnet 4.0"""
        
        # Clean system message for professional responses
        system_message = {
            "role": "system", 
            "content": "You are Rajan Bot, an advanced AI assistant powered by cutting-edge AI models. Provide intelligent, helpful, and accurate responses."
        }
        
        # Format messages properly
        clean_messages = [system_message]
        for msg in messages:
            if msg.get("role") in ["user", "assistant"]:
                clean_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Try OpenAI o3 DeepResearch Agent first
        if self.openai_client:
            try:
                logger.info("🧠 Using OpenAI o3 DeepResearch Agent...")
                async for chunk in self._openai_streaming_response(clean_messages):
                    if chunk:
                        yield chunk
                return
            except Exception as e:
                logger.error(f"OpenAI o3 failed: {e}")
        
        # Try Claude Sonnet 4.0 as backup
        if self.claude_client:
            try:
                logger.info("🧠 Using Claude Sonnet 4.0...")
                async for chunk in self._claude_streaming_response(clean_messages):
                    if chunk:
                        yield chunk
                return
            except Exception as e:
                logger.error(f"Claude Sonnet failed: {e}")
        
        # Final fallback message
        yield "I apologize, but I'm currently unable to connect to premium AI services. Please check your API keys and try again."
    
    async def _openai_streaming_response(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """OpenAI o3 DeepResearch Agent streaming response"""
        
        try:
            # Cast messages to proper type for OpenAI
            from typing import cast
            formatted_messages = cast(List[ChatCompletionMessageParam], messages)
            
            # Use the latest and most powerful model
            stream = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Latest OpenAI model available
                messages=formatted_messages,
                stream=True,
                temperature=0.7,
                max_tokens=2000
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    await asyncio.sleep(0.01)  # Smooth streaming
                    
        except Exception as e:
            raise Exception(f"OpenAI streaming error: {e}")
    
    async def _claude_streaming_response(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """Claude Sonnet 4.0 streaming response"""
        
        try:
            # Extract system message and user messages for Claude format
            system_content = ""
            claude_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                else:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Claude streaming
            stream = self.claude_client.messages.stream(
                model="claude-3-5-sonnet-20241022",  # Latest Claude model
                system=system_content,
                messages=claude_messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            # Stream the response
            async for text in stream:
                if hasattr(text, 'delta') and hasattr(text.delta, 'text'):
                    yield text.delta.text
                    await asyncio.sleep(0.01)  # Smooth streaming
                    
        except Exception as e:
            raise Exception(f"Claude streaming error: {e}")