import asyncio
import json
from typing import List, Dict, AsyncGenerator
import openai
from openai import AsyncOpenAI
from app.core.config import settings


class OpenAIService:
    """Service for OpenAI API interactions with fallback for testing."""
    
    def __init__(self):
        # Handle test environment where API key might not be real
        self.is_configured = settings.is_openai_configured()
        
        if self.is_configured:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            # Mock client for testing
            self.client = None
            
        self.model = settings.MODEL_NAME
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
    
    async def create_chat_completion_stream(
        self, 
        messages: List[Dict], 
        system_prompt: str = None
    ) -> AsyncGenerator[str, None]:
        """Create streaming chat completion with fallback for testing."""
        try:
            # If OpenAI is not configured, return a proper response
            if not self.is_configured:
                # Get the last user message
                user_message = ""
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        user_message = msg.get("content", "")
                        break
                
                # Create an intelligent response based on the user's message
                mock_response = self._create_intelligent_response(user_message)
                
                # Simulate streaming
                words = mock_response.split()
                for i, word in enumerate(words):
                    yield word + (" " if i < len(words) - 1 else "")
                    await asyncio.sleep(0.02)  # Simulate realistic typing
                return
            
            # Convert messages to OpenAI format
            openai_messages = []
            
            if system_prompt:
                openai_messages.append({"role": "system", "content": system_prompt})
            
            for message in messages:
                if isinstance(message, dict):
                    openai_messages.append(message)
                else:
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
    
    def _create_intelligent_response(self, user_message: str) -> str:
        """Create intelligent responses based on user input (for testing)."""
        user_msg_lower = user_message.lower()
        
        # Greetings
        if any(word in user_msg_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! I'm GPT.R1, your advanced AI assistant created by Rajan Mishra. I'm here to help you with any questions or tasks you might have. How can I assist you today?"
        
        # Questions about the system
        elif any(word in user_msg_lower for word in ["what", "who", "how", "why", "when", "where"]):
            if "you" in user_msg_lower or "gpt" in user_msg_lower:
                return "I'm GPT.R1, an advanced AI assistant built by Rajan Mishra using cutting-edge technology. I can help with various tasks including answering questions, providing explanations, writing assistance, and much more. I'm designed to be helpful, accurate, and efficient."
            else:
                return f"That's an interesting question about '{user_message}'. I'd be happy to help you explore this topic. Could you provide a bit more context so I can give you the most relevant and helpful response?"
        
        # Programming or technical questions
        elif any(word in user_msg_lower for word in ["code", "programming", "python", "javascript", "tech", "api", "database"]):
            return f"Great question about {user_message}! As GPT.R1, I'm well-equipped to help with programming and technical topics. I can assist with code examples, debugging, best practices, and explanations. What specific aspect would you like me to focus on?"
        
        # Creative or writing tasks
        elif any(word in user_msg_lower for word in ["write", "create", "story", "poem", "essay", "article"]):
            return f"I'd be delighted to help you with your creative writing task: '{user_message}'. As GPT.R1, I can assist with various forms of creative writing, from stories and poems to articles and essays. What style or approach would you prefer?"
        
        # Help or assistance requests
        elif any(word in user_msg_lower for word in ["help", "assist", "support", "guide"]):
            return "I'm here to help! As GPT.R1, I can assist you with a wide range of tasks including answering questions, writing, coding, problem-solving, research, and much more. Please let me know what specific help you need, and I'll do my best to provide you with accurate and useful assistance."
        
        # Default intelligent response
        else:
            return f"Thank you for your message: '{user_message}'. As GPT.R1, I understand you're looking for assistance with this topic. I'm designed to be helpful and provide thoughtful responses. Could you tell me a bit more about what you're trying to achieve or what specific information you're looking for? This will help me provide you with the most relevant and useful response."
    
    async def create_chat_completion(
        self, 
        messages: List[Dict], 
        system_prompt: str = None
    ) -> str:
        """Create non-streaming chat completion."""
        try:
            if not self.is_configured:
                user_message = ""
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        user_message = msg.get("content", "")
                        break
                return self._create_intelligent_response(user_message)
            
            # Convert messages to OpenAI format
            openai_messages = []
            
            if system_prompt:
                openai_messages.append({"role": "system", "content": system_prompt})
            
            for message in messages:
                if isinstance(message, dict):
                    openai_messages.append(message)
                else:
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

    async def stream_chat_completion(self, messages: List[Dict], enhanced_query: str = None) -> AsyncGenerator[str, None]:
        """Alias for backwards compatibility."""
        async for chunk in self.create_chat_completion_stream(messages):
            yield chunk


# Create service instance
openai_service = OpenAIService()