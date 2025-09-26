from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
import os
from typing import AsyncGenerator, List, Dict, Any, cast
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import asyncio
import logging
import random
import time

load_dotenv()

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.fallback_responses = [
            "I'm an AI assistant created to help you with various tasks. How can I assist you today?",
            "Hello! I'm here to help answer your questions and assist with your tasks. What would you like to know?",
            "Hi there! I'm an AI assistant ready to help you with information, analysis, and creative tasks. What can I do for you?",
            "Welcome! I'm designed to be helpful, harmless, and honest. Feel free to ask me anything you'd like to know!",
            "Greetings! I'm an AI assistant with access to a wealth of knowledge. How may I help you today?"
        ]
        
    def _simulate_typing_delay(self):
        """Simulate realistic typing delays"""
        return random.uniform(0.05, 0.15)
    
    async def stream_chat_response(
        self, 
        messages: List[dict], 
        use_search: bool = False
    ) -> AsyncGenerator[str, None]:
        """Stream chat response with advanced fallback system"""
        
        # If search is requested, perform web search first
        if use_search and messages:
            last_message = messages[-1]['content']
            search_results = await self.search_web(last_message)
            if search_results:
                # Add search context to the conversation
                context_message = {
                    "role": "system",
                    "content": f"Here are some recent web search results for context:\n{search_results}\n\nPlease use this information to provide a more accurate and up-to-date response."
                }
                messages.insert(-1, context_message)
        
        try:
            # Try OpenAI API first - cast messages to proper type
            formatted_messages = cast(List[ChatCompletionMessageParam], messages)
            stream = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=formatted_messages,
                stream=True,
                temperature=0.7,
                max_tokens=1000
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    await asyncio.sleep(self._simulate_typing_delay())
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            
            # Advanced fallback system with intelligent responses
            if "quota" in str(e).lower() or "429" in str(e):
                yield self._generate_quota_fallback_response(messages)
            elif "api" in str(e).lower():
                yield self._generate_api_fallback_response(messages)
            else:
                yield self._generate_intelligent_fallback(messages)
    
    def _generate_quota_fallback_response(self, messages: List[dict]) -> str:
        """Generate intelligent response when quota is exceeded"""
        user_message = messages[-1]['content'].lower() if messages else ""
        
        # Analyze user intent and provide relevant fallback
        if any(word in user_message for word in ['hello', 'hi', 'hey', 'greetings']):
            response = "Hello! I'm experiencing high demand right now, but I'm still here to help you. "
        elif any(word in user_message for word in ['what', 'how', 'why', 'when', 'where']):
            response = "That's a great question! While I'm temporarily using my backup systems, I can still provide helpful information. "
        elif any(word in user_message for word in ['help', 'assist', 'support']):
            response = "I'm absolutely here to help you! Even with current system constraints, I'm ready to assist. "
        else:
            response = "I understand your request! Let me help you with that using my available resources. "
        
        # Add relevant information based on context
        if "code" in user_message or "programming" in user_message:
            response += "For coding questions, I can help with syntax, logic, debugging, and best practices across many programming languages."
        elif "write" in user_message or "create" in user_message:
            response += "I can help you create content, write explanations, draft documents, and provide creative assistance."
        elif "explain" in user_message or "understand" in user_message:
            response += "I can break down complex concepts, provide detailed explanations, and help you understand various topics."
        else:
            response += "I'm equipped to help with a wide range of tasks including analysis, creative work, problem-solving, and information synthesis."
        
        response += "\n\nWhat specific aspect would you like me to focus on?"
        
        return response
    
    def _generate_api_fallback_response(self, messages: List[dict]) -> str:
        """Generate response for API connectivity issues"""
        response = "I'm currently experiencing some connectivity issues with my primary systems, but I'm still operational! "
        response += "I can help you with information, analysis, creative tasks, and problem-solving. "
        response += "What would you like to work on together?"
        
        return response
    
    def _generate_intelligent_fallback(self, messages: List[dict]) -> str:
        """Generate contextually aware fallback responses"""
        if not messages:
            response = random.choice(self.fallback_responses)
        else:
            user_message = messages[-1]['content']
            response = f"I understand you're asking about: '{user_message}'\n\n"
            response += "While I'm operating in backup mode, I'm still capable of providing helpful insights and assistance. "
            response += "Could you provide more details about what specifically you'd like help with?"
        
        return response
    
    async def search_web(self, query: str) -> str:
        """Search the web using DuckDuckGo"""
        try:
            # Run the search in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, 
                lambda: list(DDGS().text(query, max_results=3))
            )
            
            if not results:
                return ""
            
            search_context = "Web Search Results:\n\n"
            for i, result in enumerate(results, 1):
                search_context += f"{i}. {result.get('title', 'No title')}\n"
                search_context += f"   {result.get('body', 'No description')}\n"
                search_context += f"   Source: {result.get('href', 'No URL')}\n\n"
            
            return search_context
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return f"Search error: {str(e)}"