import asyncio
from typing import List, Dict, Any
from ddgs import DDGS
import httpx
from app.core.config import settings


class RAGService:
    """RAG (Retrieval-Augmented Generation) service with DuckDuckGo search."""
    
    def __init__(self):
        self.max_results = 5
        self.max_snippet_length = 500
    
    async def search_web(self, query: str) -> List[Dict[str, Any]]:
        """Search the web using DuckDuckGo."""
        try:
            with DDGS() as ddgs:
                results = []
                search_results = ddgs.text(query, max_results=self.max_results)
                
                for result in search_results:
                    # Clean and truncate the snippet
                    snippet = result.get('body', '')[:self.max_snippet_length]
                    
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': snippet,
                        'source': 'DuckDuckGo'
                    })
                
                return results
                
        except Exception as e:
            print(f"Error in web search: {str(e)}")
            return []
    
    async def get_context_from_search(self, query: str) -> str:
        """Get context from web search for RAG."""
        search_results = await self.search_web(query)
        
        if not search_results:
            return "No relevant information found from web search."
        
        context_parts = []
        context_parts.append("Here's relevant information from the web:")
        
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"\n{i}. **{result['title']}**")
            context_parts.append(f"   Source: {result['url']}")
            context_parts.append(f"   Content: {result['snippet']}")
        
        return "\n".join(context_parts)
    
    def create_rag_system_prompt(self, context: str) -> str:
        """Create system prompt for RAG-enhanced responses."""
        return f"""You are a helpful AI assistant with access to current web information.

Context from web search:
{context}

Instructions:
1. Use the provided context to answer questions when relevant
2. If the context doesn't contain relevant information, rely on your training data
3. Always cite sources when using information from the context
4. Be clear about what information comes from the web search vs your training
5. Provide comprehensive and accurate responses
6. If asked about recent events, prioritize the web search context

Please provide a helpful and informative response based on the context above and the user's question."""


# Create service instance
rag_service = RAGService()