from app.services.multi_llm_service import MultiLLMService
from typing import AsyncGenerator, List, Dict
import logging

logger = logging.getLogger(__name__)

class ChatService:
    """
    Clean Chat Service - Direct LLM Integration
    NO FAKE RESPONSES - Only real LLM output
    """
    
    def __init__(self):
        self.llm_service = MultiLLMService()
        logger.info("ChatService initialized with clean MultiLLM service")
    
    async def stream_chat_response(
        self, 
        messages: List[dict], 
        use_search: bool = False
    ) -> AsyncGenerator[str, None]:
        """Stream real LLM response - NO HALLUCINATION"""
        
        logger.info(f"Processing chat with {len(messages)} messages")
        
        # Pass directly to LLM service - let it handle everything
        try:
            async for chunk in self.llm_service.get_llm_response(messages, use_search):
                if chunk:
                    yield chunk
        except Exception as e:
            logger.error(f"Chat service error: {e}")
            yield f"I'm sorry, I encountered an error: {str(e)}"