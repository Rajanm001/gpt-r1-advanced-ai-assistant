#!/usr/bin/env python3
"""
Direct LLM Test - Test the new clean service
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.multi_llm_service import MultiLLMService

async def test_llm():
    print("🧪 Testing Direct LLM Service...")
    
    service = MultiLLMService()
    messages = [{"role": "user", "content": "What is 2+2? Give me just the number."}]
    
    print("📤 Sending: What is 2+2? Give me just the number.")
    print("📥 Response: ", end="", flush=True)
    
    full_response = ""
    try:
        async for chunk in service.get_llm_response(messages):
            if chunk:
                print(chunk, end="", flush=True)
                full_response += chunk
        
        print(f"\n\n✅ Success! Full response: '{full_response}'")
        
        if any(word in full_response.lower() for word in ["4", "four", "2+2", "equals"]):
            print("✅ LLM is working correctly - gave mathematical answer!")
        else:
            print("❌ LLM response seems off - might be hallucinating")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())