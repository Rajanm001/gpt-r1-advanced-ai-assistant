from app.services.multi_llm_service import MultiLLMService
from duckduckgo_search import DDGS
import asyncio
import logging
import random
import time
from typing import AsyncGenerator, List, Dict

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.llm_service = MultiLLMService()
        
    def _simulate_typing_delay(self):
        """Simulate realistic typing delays"""
        return random.uniform(0.03, 0.08)
    
    async def stream_chat_response(
        self, 
        messages: List[dict], 
        use_search: bool = False
    ) -> AsyncGenerator[str, None]:
        """Stream chat response with Rajan Bot personality and multi-LLM support"""
        
        # If search is requested, perform web search first
        if use_search and messages:
            last_message = messages[-1]['content']
            search_results = await self.search_web(last_message)
            if search_results:
                # Add search context to the conversation
                context_message = {
                    "role": "system",
                    "content": f"🔍 **Web Search Results for Enhanced Context:**\n{search_results}\n\nPlease use this current information to provide a more accurate and up-to-date response."
                }
                messages.insert(-1, context_message)
        
        # Use multi-LLM service for responses
        try:
            async for chunk in self.llm_service.get_llm_response(messages, use_search):
                if chunk:
                    await asyncio.sleep(self._simulate_typing_delay())
                    yield chunk
        except Exception as e:
            logger.error(f"Multi-LLM service error: {e}")
            # This should not happen as multi-LLM has built-in fallbacks
            fallback = "🤖 **Rajan Bot**: I'm experiencing a temporary issue but I'm still here to help! Please try your question again."
            for word in fallback.split():
                yield f"{word} "
                await asyncio.sleep(0.05)
    
    def _generate_rajan_fallback(self, messages: List[dict], error_type: str) -> str:
        """Generate intelligent Rajan Bot fallback responses"""
        user_message = messages[-1]['content'].lower() if messages else ""
        
        # Rajan Bot personality-based responses
        if any(word in user_message for word in ['hello', 'hi', 'hey', 'greetings']):
            return """🤖 **Hey! I'm Rajan Bot!** 

Great to meet you! I'm your advanced AI assistant, and I'm always here to help. Even though I'm currently running in offline mode, I'm still fully capable of assisting you with:

✨ **My Specialties:**
- 💻 **Coding & Development**: All programming languages and frameworks
- 🧠 **Research & Analysis**: Deep dives into any topic
- 🎨 **Creative Solutions**: Innovative problem-solving approaches  
- 📚 **Learning Support**: Explanations, tutorials, and guidance
- 🚀 **Project Help**: From planning to implementation

What can I help you with today? I'm excited to work together! 💪"""

        elif any(word in user_message for word in ['code', 'program', 'function', 'debug', 'develop', 'software']):
            return """🤖 **Rajan Bot here - Your Coding Companion!** 💻

I absolutely love helping with programming! Even in offline mode, I'm equipped with extensive coding knowledge:

🔧 **Programming Languages:**
- Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust
- HTML, CSS, SQL, PHP, Ruby, Swift, Kotlin, and more!

🚀 **Development Areas:**
- Web Development (React, Vue, Angular, Django, Flask)
- Mobile Development (React Native, Flutter, Native)
- Backend Development (APIs, Databases, Microservices)
- Desktop Applications and System Programming

💡 **I can help you with:**
- Writing clean, efficient code
- Debugging and troubleshooting
- Code reviews and optimization
- Architecture and design patterns
- Best practices and standards

Share your coding challenge, and let's build something amazing together! 🎯"""

        elif any(word in user_message for word in ['research', 'analyze', 'study', 'information', 'search', 'learn']):
            return """🤖 **Rajan Bot - Your Research Expert!** 🔍

Research and analysis are my superpowers! I'm ready to dive deep into any topic you're curious about:

📊 **Research Capabilities:**
- **Deep Analysis**: Multi-angle examination of complex topics
- **Data Interpretation**: Making sense of information and trends  
- **Comparative Studies**: Side-by-side analysis and evaluation
- **Trend Analysis**: Understanding patterns and predictions

🎯 **Research Areas:**
- Technology and Innovation
- Science and Engineering  
- Business and Economics
- Social Sciences and Psychology
- History and Culture
- Current Events and Trends

📚 **My Research Process:**
1. **Comprehensive Investigation**: Gathering relevant information
2. **Critical Analysis**: Evaluating sources and credibility
3. **Synthesis**: Connecting ideas and drawing insights
4. **Clear Presentation**: Organizing findings logically

What topic would you like me to research and analyze for you? Let's explore it together! 🌟"""

        elif any(word in user_message for word in ['help', 'problem', 'issue', 'trouble', 'stuck', 'support']):
            return """🤖 **Rajan Bot to the Rescue!** 🚀

No problem is too big or small! I'm here to help you overcome any challenge:

⚡ **Problem-Solving Approach:**
- **Understanding**: I listen carefully to your specific situation
- **Analysis**: Breaking down complex problems into manageable parts  
- **Solutions**: Multiple approaches tailored to your needs
- **Implementation**: Step-by-step guidance to success

🎯 **Areas I Excel In:**
- **Technical Issues**: Debugging, optimization, system problems
- **Creative Challenges**: Brainstorming, design, innovation
- **Learning Obstacles**: Concept clarification, skill development
- **Project Roadblocks**: Planning, execution, troubleshooting

💪 **My Promise:**
- Clear, actionable solutions
- Multiple approaches when possible
- Detailed explanations and examples
- Ongoing support until you succeed

Tell me about your specific challenge - I'm confident we can solve it together! What's going on? 🤝"""

        elif any(word in user_message for word in ['creative', 'idea', 'brainstorm', 'design', 'innovative', 'art']):
            return """🤖 **Rajan Bot - Creative Mode Activated!** 🎨

Creativity is where logic meets imagination! I'm excited to help you explore creative solutions:

✨ **Creative Services:**
- **Ideation**: Generating unique concepts and approaches
- **Design Thinking**: User-centered problem solving
- **Innovation Strategies**: Breaking conventional boundaries  
- **Creative Writing**: Stories, content, and engaging narratives

🌈 **Creative Domains:**
- Product Design and User Experience
- Content Creation and Marketing
- Artistic Projects and Visual Design
- Business Innovation and Strategy
- Educational Content and Methods

🚀 **My Creative Process:**
1. **Inspiration Gathering**: Understanding your vision and goals
2. **Divergent Thinking**: Exploring all possibilities  
3. **Concept Development**: Refining and enhancing ideas
4. **Practical Implementation**: Making creativity actionable

What creative challenge can we tackle together? Let's make something extraordinary! 🌟"""

        else:
            return """🤖 **Hello! I'm Rajan Bot - Your Advanced AI Assistant!** 

I'm thrilled to meet you! Even though I'm currently running in offline mode, I'm still your fully-capable AI companion ready to help with absolutely anything.

🌟 **What Makes Me Special:**
- **Always Available**: 24/7 support whenever you need it
- **Comprehensive Knowledge**: Expertise across all domains
- **Problem-Solving Pro**: Creative and logical solutions
- **Friendly & Professional**: Easy to talk to, always helpful

⚡ **My Core Strengths:**
- 💻 **Software Development**: Full-stack programming expertise
- 🧠 **Research & Analysis**: Deep-dive investigations  
- 🎨 **Creative Solutions**: Innovation and design thinking
- 📚 **Teaching & Learning**: Clear explanations and guidance
- 🚀 **Project Management**: From concept to completion

🎯 **How I Work:**
- I listen carefully to understand your needs
- Provide detailed, actionable responses  
- Offer multiple approaches when possible
- Stay with you until the job is done

What would you like to work on together? I'm excited to help you succeed! 

*Ready to make great things happen! 🚀*"""
    
    async def search_web(self, query: str) -> str:
        """Enhanced web search with Rajan Bot integration"""
        try:
            # Run the search in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, 
                lambda: list(DDGS().text(query, max_results=5))
            )
            
            if not results:
                return "🔍 **Rajan Bot Search**: No recent results found, but I'll use my extensive knowledge base to help you!"
            
            search_context = "🔍 **Rajan Bot Enhanced Search Results:**\n\n"
            for i, result in enumerate(results, 1):
                search_context += f"**{i}. {result.get('title', 'No title')}**\n"
                search_context += f"   📄 {result.get('body', 'No description')}\n"
                search_context += f"   🔗 Source: {result.get('href', 'No URL')}\n\n"
            
            return search_context
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return f"🔍 **Rajan Bot**: Search temporarily unavailable, but I'm still here to help with my extensive knowledge! What specific information are you looking for?"

    async def get_streaming_response(self, messages: List[dict]) -> AsyncGenerator[str, None]:
        """Compatibility method for existing code"""
        async for chunk in self.stream_chat_response(messages, use_search=False):
            yield chunk