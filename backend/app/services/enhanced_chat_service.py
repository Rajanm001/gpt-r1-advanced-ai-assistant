from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from sqlalchemy.orm import Session
import os
import logging
import asyncio
from typing import List, Dict, AsyncGenerator, Any, cast
import json

logger = logging.getLogger(__name__)

class EnhancedChatService:
    """Enhanced chat service with superior response quality and features"""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def get_enhanced_streaming_response(
        self, 
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """Get enhanced streaming response with better quality"""
        
        try:
            # Enhanced parameters for better responses - cast messages to proper type
            formatted_messages = cast(List[ChatCompletionMessageParam], messages)
            stream = self.client.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for best quality
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield content
                    
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            
            # Intelligent fallback response
            fallback_response = self._generate_fallback_response(messages)
            for word in fallback_response.split():
                yield f"{word} "
                await asyncio.sleep(0.05)
    
    def _generate_fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate intelligent fallback when API fails"""
        
        user_message = messages[-1]["content"].lower() if messages else ""
        
        # Smart fallback based on message content
        if any(word in user_message for word in ['code', 'program', 'function']):
            return """I understand you're looking for help with coding. While I'm temporarily experiencing connectivity issues with my primary systems, I can still assist you with:

• Code review and debugging
• Algorithm explanations  
• Best practices and patterns
• Architecture guidance

Please rephrase your question and I'll do my best to help with the information I have available."""

        elif any(word in user_message for word in ['explain', 'what is', 'how does']):
            return """I'd be happy to explain that concept for you. While I'm currently experiencing some connectivity issues that limit my access to the most up-to-date information, I can provide explanations based on my training data.

Could you please rephrase your question? I'll give you the most comprehensive explanation I can with the knowledge I have available."""

        elif any(word in user_message for word in ['help', 'problem', 'issue']):
            return """I'm here to help! I'm currently experiencing some temporary connectivity issues, but I can still assist you with many topics including:

• General problem-solving approaches
• Technical troubleshooting steps
• Best practices and methodologies
• Conceptual explanations

Please let me know more details about what you need help with, and I'll do my best to guide you."""

        else:
            return """Thank you for your message! I'm currently experiencing some temporary connectivity issues that may affect my response quality, but I'm still here to help.

I can assist with a wide range of topics including:
• Technical questions and programming
• Explanations and tutorials  
• Problem-solving and analysis
• Creative and analytical tasks

Could you please rephrase or provide more context about what you're looking for? I'll give you the best response I can!"""

    async def analyze_message_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user message intent for better responses"""
        
        message_lower = message.lower()
        
        intent_analysis = {
            "type": "general",
            "complexity": "medium",
            "requires_code": False,
            "requires_explanation": False,
            "is_question": False,
            "sentiment": "neutral"
        }
        
        # Detect question patterns
        if any(word in message_lower for word in ['?', 'what', 'how', 'why', 'when', 'where', 'which']):
            intent_analysis["is_question"] = True
            
        # Detect code requests
        if any(word in message_lower for word in ['code', 'program', 'function', 'class', 'algorithm', 'script']):
            intent_analysis["requires_code"] = True
            intent_analysis["type"] = "programming"
            
        # Detect explanation requests  
        if any(word in message_lower for word in ['explain', 'describe', 'define', 'clarify', 'elaborate']):
            intent_analysis["requires_explanation"] = True
            intent_analysis["type"] = "explanation"
            
        # Detect complexity
        if len(message.split()) > 50 or any(word in message_lower for word in ['complex', 'detailed', 'comprehensive']):
            intent_analysis["complexity"] = "high"
        elif len(message.split()) < 10:
            intent_analysis["complexity"] = "low"
            
        # Basic sentiment detection
        if any(word in message_lower for word in ['please', 'help', 'thank', 'appreciate']):
            intent_analysis["sentiment"] = "polite"
        elif any(word in message_lower for word in ['urgent', 'asap', 'quickly', 'immediate']):
            intent_analysis["sentiment"] = "urgent"
            
        return intent_analysis
    
    def enhance_system_prompt(self, intent: Dict[str, Any]) -> str:
        """Create enhanced system prompt based on intent analysis"""
        
        base_prompt = """You are ChatGPT, an advanced AI assistant created by OpenAI. You are highly knowledgeable, helpful, and engaging."""
        
        if intent["type"] == "programming":
            return f"""{base_prompt}

For this programming-related query:
- Provide clear, well-commented code examples
- Explain the logic and approach
- Include best practices and potential improvements
- Consider edge cases and error handling
- Use proper formatting and syntax highlighting"""

        elif intent["type"] == "explanation":
            return f"""{base_prompt}

For this explanation request:
- Break down complex concepts into understandable parts
- Use analogies and examples where helpful
- Structure your response with clear headings
- Provide both high-level overview and detailed insights
- Include practical applications or implications"""

        elif intent["complexity"] == "high":
            return f"""{base_prompt}

For this complex query:
- Take a comprehensive, multi-faceted approach
- Address various aspects and considerations
- Provide detailed analysis and reasoning
- Include relevant examples and case studies
- Structure response with clear sections and conclusions"""

        else:
            return f"""{base_prompt}

Provide a helpful, accurate, and engaging response that directly addresses the user's needs. Be clear, concise, and thorough as appropriate."""