import os
import requests
import json
from typing import AsyncGenerator, List, Dict, Optional, Any
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class MultiLLMService:
    """
    Enhanced Multi-LLM service with proper error handling and fallbacks
    """
    
    def __init__(self):
        # API Keys
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.huggingface_key = os.getenv("HUGGINGFACE_API_KEY")
        
        # API endpoints
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.huggingface_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
    async def get_llm_response(self, messages: List[Dict], use_search: bool = False) -> AsyncGenerator[str, None]:
        """Try multiple LLM APIs with proper fallback chain"""
        
        # Add Rajan Bot system message
        system_message = {
            "role": "system", 
            "content": """You are Rajan Bot, an advanced AI assistant. You are friendly, professional, and highly intelligent. 
Provide comprehensive, accurate, and helpful answers with clear formatting."""
        }
        
        # Prepare messages
        formatted_messages = [system_message] + messages
        
        # Try APIs in order with proper error handling
        api_attempts = [
            ("Groq", self._try_groq_api),
            ("HuggingFace", self._try_huggingface_api),
            ("Fallback", self._generate_fallback_response)
        ]
        
        for api_name, api_method in api_attempts:
            try:
                logger.info(f"Attempting {api_name} API...")
                async for chunk in api_method(formatted_messages):
                    if chunk:
                        yield chunk
                logger.info(f"{api_name} API succeeded")
                return
            except Exception as e:
                logger.error(f"{api_name} failed: {e}")
                continue
        
        # Ultimate fallback
        yield "🤖 **Rajan Bot**: I'm currently experiencing technical difficulties but I'm here to help! Please try again or ask me something else."
    
    async def _try_groq_api(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """Try Groq API with proper request format"""
        if not self.groq_key:
            raise Exception("Groq API key not available")
            
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        
        # Use Groq-compatible model and format
        data = {
            "model": "llama3-8b-8192",  # Groq's fastest model
            "messages": messages,
            "stream": True,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(self.groq_url, headers=headers, json=data, stream=True, timeout=30)
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]
                            if data_str == '[DONE]':
                                break
                            try:
                                chunk_data = json.loads(data_str)
                                if 'choices' in chunk_data and chunk_data['choices']:
                                    delta = chunk_data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
            else:
                raise Exception(f"Groq API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise e
    
    async def _try_huggingface_api(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """Try Hugging Face API with simplified approach"""
        if not self.huggingface_key:
            raise Exception("Hugging Face API key not available")
            
        headers = {
            "Authorization": f"Bearer {self.huggingface_key}",
            "Content-Type": "application/json"
        }
        
        # Extract the last user message for HuggingFace
        user_message = messages[-1].get('content', '') if messages else ''
        
        data = {
            "inputs": user_message,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        try:
            response = requests.post(self.huggingface_url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and result:
                    generated_text = result[0].get('generated_text', '')
                    # Stream the response word by word for better UX
                    words = generated_text.split()
                    for word in words:
                        yield word + " "
                        await asyncio.sleep(0.05)  # Small delay for streaming effect
            else:
                raise Exception(f"Hugging Face API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Hugging Face API error: {e}")
            raise e
    
    async def _generate_fallback_response(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """Generate intelligent fallback response"""
        
        user_message = messages[-1].get('content', '').lower() if messages else ''
        
        # Analyze user intent and generate appropriate response
        if any(word in user_message for word in ['hello', 'hi', 'hey', 'greet']):
            response = """🤖 **Hey! I'm Rajan Bot - Your Advanced AI Assistant!** 

Great to meet you! I'm absolutely thrilled to help you with anything you need. Even though I'm currently running in offline mode, I'm still your fully-capable AI companion.

🌟 **What Makes Me Your Best AI Assistant:**
- **Always Available**: 24/7 support whenever you need help
- **Comprehensive Expertise**: Knowledge across all major domains  
- **Problem-Solving Pro**: Creative and logical solutions for any challenge
- **Friendly & Professional**: Easy to work with, always encouraging
- **Persistent Helper**: I stay with you until your goals are achieved

⚡ **My Core Specialties:**
- 💻 **Software Development**: Full-stack programming, debugging, architecture
- 🧠 **Research & Analysis**: Deep investigations, data interpretation, insights
- 🎨 **Creative Solutions**: Innovation, design thinking, content creation
- 📚 **Learning Support**: Explanations, tutorials, skill development
- 🚀 **Project Management**: Planning, execution, problem-solving

🎯 **How I Work With You:**
- **Active Listening**: I understand your exact needs and context
- **Comprehensive Responses**: Detailed, actionable, and well-structured answers
- **Multiple Approaches**: Various solutions when possible for flexibility
- **Clear Communication**: Professional yet friendly, easy to understand
- **Continuous Support**: Available for follow-ups and clarifications

**What would you like to work on together?** I'm excited to help you:
- Solve technical challenges
- Learn new skills and concepts  
- Create innovative solutions
- Research complex topics
- Plan and execute projects
- Or anything else you have in mind!

*Ready to achieve amazing results together!* 🚀✨ What's on your mind today?"""

        elif any(word in user_message for word in ['code', 'program', 'develop', 'debug', 'python', 'javascript', 'react', 'nodejs']):
            response = """🤖 **Rajan Bot - Your Coding Expert!** 

I'm here to help with all your programming needs! Even in offline mode, I can assist with:

💻 **Programming Languages:**
- Python, JavaScript, TypeScript, React, Node.js
- HTML, CSS, SQL, Java, C++, and more
- Full-stack development and architecture

🔧 **Development Support:**
- Code review and debugging
- Algorithm optimization
- Best practices and design patterns
- Project structure and organization
- Testing strategies

🚀 **What coding challenge can I help you solve today?**"""

        elif any(word in user_message for word in ['ai', 'artificial intelligence', 'machine learning', 'ml', 'tech', 'technology']):
            response = """🤖 **Rajan Bot - AI & Tech Specialist!**

Excellent question about AI and technology! Here's what I can share:

🧠 **Artificial Intelligence** is revolutionizing how we solve complex problems:

**Key AI Technologies:**
- **Machine Learning**: Systems that learn from data
- **Deep Learning**: Neural networks mimicking brain functions  
- **Natural Language Processing**: Understanding human language
- **Computer Vision**: Interpreting visual information
- **Robotics**: Intelligent automation and control

**Real-World Applications:**
- 🚗 Autonomous vehicles and smart transportation
- 🏥 Medical diagnosis and drug discovery
- 💼 Business intelligence and decision-making
- 🎯 Personalized recommendations and content
- 🔒 Cybersecurity and threat detection

**Current Trends:**
- Generative AI (like ChatGPT, DALL-E)
- Edge computing and mobile AI
- Ethical AI and responsible development
- AI-human collaboration tools

What specific aspect of AI or technology interests you most? I'd love to dive deeper!"""

        else:
            response = """🤖 **Rajan Bot - Ready to Help!**

I'm your advanced AI assistant, and I'm here to provide the best support possible! 

**I can help you with:**
- 💻 Programming and software development
- 🧠 Research and analysis
- 📊 Data interpretation and insights
- 🎨 Creative problem-solving
- 📚 Learning and education
- 🚀 Project planning and execution

**My Approach:**
- Comprehensive and detailed responses
- Multiple perspectives when helpful
- Clear, actionable guidance
- Professional yet friendly communication

**What would you like to explore together?** Please feel free to:
- Ask specific questions
- Request help with projects
- Seek explanations on topics
- Get creative solutions
- Or anything else you need!

I'm excited to help you achieve your goals! 🌟"""

        # Stream the response with realistic typing speed
        words = response.split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.03)  # Realistic typing delay


# Create global instance
llm_service = MultiLLMService()