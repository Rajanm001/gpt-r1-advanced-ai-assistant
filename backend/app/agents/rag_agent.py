"""
RAG Agent with DuckDuckGo Search Integration
Enhanced AI responses with internet search capabilities
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from ddgs import DDGS
from bs4 import BeautifulSoup
import re
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGAgent:
    """
    Advanced RAG (Retrieval-Augmented Generation) Agent
    Combines OpenAI responses with real-time internet search
    """
    
    def __init__(self):
        self.search_engine = DDGS()
        self.max_search_results = 5
        self.max_content_length = 2000
        self.timeout = 10
        
    async def should_search(self, query: str) -> bool:
        """
        Determine if query needs internet search
        """
        search_indicators = [
            'latest', 'recent', 'current', 'today', 'now', 'news',
            'what happened', 'update', 'price', 'stock', 'weather',
            'when did', 'who is', 'what is happening', '2024', '2025'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in search_indicators)
    
    async def search_web(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform DuckDuckGo search and return formatted results
        """
        try:
            logger.info(f"🔍 Searching web for: {query}")
            
            # Perform search with enhanced parameters
            search_results = []
            with DDGS() as ddgs:
                results = ddgs.text(
                    query,
                    max_results=self.max_search_results,
                    safesearch='moderate',
                    region='us-en'
                )
                
                for result in results:
                    search_results.append({
                        'title': result.get('title', ''),
                        'body': result.get('body', ''),
                        'href': result.get('href', ''),
                        'timestamp': datetime.now().isoformat()
                    })
            
            logger.info(f"✅ Found {len(search_results)} search results")
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Search error: {str(e)}")
            return []
    
    async def extract_content(self, url: str) -> str:
        """
        Extract clean content from webpage
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style", "nav", "footer", "header"]):
                            script.decompose()
                        
                        # Extract text content
                        text = soup.get_text()
                        
                        # Clean up text
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = ' '.join(chunk for chunk in chunks if chunk)
                        
                        # Limit content length
                        return text[:self.max_content_length]
                        
        except Exception as e:
            logger.error(f"❌ Content extraction error for {url}: {str(e)}")
            return ""
    
    def format_search_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Format search results into context for AI
        """
        if not search_results:
            return ""
        
        context = "\n📊 REAL-TIME SEARCH RESULTS:\n"
        context += "=" * 50 + "\n"
        
        for i, result in enumerate(search_results, 1):
            context += f"\n🔗 Result {i}:\n"
            context += f"📰 Title: {result['title']}\n"
            context += f"📝 Summary: {result['body']}\n"
            context += f"🌐 Source: {result['href']}\n"
            context += f"⏰ Retrieved: {result['timestamp']}\n"
            context += "-" * 30 + "\n"
        
        context += "\n💡 Please use this current information to provide an accurate, up-to-date response.\n"
        return context
    
    async def enhance_query(self, original_query: str, search_results: List[Dict[str, Any]]) -> str:
        """
        Enhance original query with search context
        """
        if not search_results:
            return original_query
        
        search_context = self.format_search_context(search_results)
        
        enhanced_query = f"""
{original_query}

{search_context}

Instructions:
1. Use the real-time search results above to provide current, accurate information
2. Cite specific sources when referencing the search results
3. If search results are relevant, prioritize them over general knowledge
4. Maintain a conversational, helpful tone
5. If search results don't fully answer the question, combine them with your knowledge
"""
        return enhanced_query
    
    async def process_query(self, query: str) -> tuple[str, bool]:
        """
        Main method to process query with RAG enhancement
        Returns: (enhanced_query, used_search)
        """
        try:
            # Check if search is needed
            if await self.should_search(query):
                logger.info("🤖 RAG Agent activated - performing search enhancement")
                
                # Perform web search
                search_results = await self.search_web(query)
                
                if search_results:
                    # Enhance query with search context
                    enhanced_query = await self.enhance_query(query, search_results)
                    return enhanced_query, True
                else:
                    logger.warning("⚠️ Search returned no results, using original query")
                    return query, False
            else:
                logger.info("🤖 RAG Agent: No search needed for this query")
                return query, False
                
        except Exception as e:
            logger.error(f"❌ RAG Agent error: {str(e)}")
            return query, False

# Global RAG agent instance
rag_agent = RAGAgent()

async def enhance_with_rag(query: str) -> tuple[str, bool]:
    """
    Convenience function to enhance query with RAG
    """
    return await rag_agent.process_query(query)