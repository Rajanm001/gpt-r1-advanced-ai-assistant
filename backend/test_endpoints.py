"""
Endpoint verification script to ensure all required API endpoints exist
"""

import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8001"

async def test_endpoints():
    """Test all required endpoints for 100% satisfaction"""
    
    endpoints_to_test = [
        # Health endpoints
        ("GET", "/health", "Health check"),
        ("GET", "/api/v1/health", "Detailed health check"),
        
        # Chat endpoints 
        ("POST", "/api/v1/chat/stream", "Streaming chat endpoint"),
        
        # Conversation endpoints
        ("GET", "/api/v1/conversations", "List conversations"),
        ("POST", "/api/v1/conversations", "Create conversation"),
        ("GET", "/api/v1/conversations/123", "Get specific conversation"),
        ("PUT", "/api/v1/conversations/123", "Update conversation"),
        ("DELETE", "/api/v1/conversations/123", "Delete conversation"),
        
        # Authentication endpoints
        ("POST", "/api/v1/auth/register", "User registration"),
        ("POST", "/api/v1/auth/login", "User login"),
        ("GET", "/api/v1/auth/me", "Get current user"),
        ("POST", "/api/v1/auth/logout", "User logout"),
        
        # API info
        ("GET", "/api", "API information"),
        ("GET", "/", "Root endpoint"),
    ]
    
    async with httpx.AsyncClient() as client:
        print("🔍 Testing API endpoints for completeness...")
        print("=" * 60)
        
        total_endpoints = len(endpoints_to_test)
        working_endpoints = 0
        
        for method, endpoint, description in endpoints_to_test:
            try:
                if method == "GET":
                    response = await client.get(f"{BASE_URL}{endpoint}", timeout=5.0)
                elif method == "POST":
                    # Use dummy data for POST requests
                    dummy_data = {"test": "data"}
                    response = await client.post(
                        f"{BASE_URL}{endpoint}", 
                        json=dummy_data, 
                        timeout=5.0
                    )
                elif method == "PUT":
                    dummy_data = {"title": "Test"}
                    response = await client.put(
                        f"{BASE_URL}{endpoint}", 
                        json=dummy_data, 
                        timeout=5.0
                    )
                elif method == "DELETE":
                    response = await client.delete(f"{BASE_URL}{endpoint}", timeout=5.0)
                
                # Check if endpoint exists (not necessarily returns 200)
                if response.status_code != 404:
                    status = "✅ EXISTS"
                    working_endpoints += 1
                else:
                    status = "❌ NOT FOUND"
                
                print(f"{status} | {method:6} | {endpoint:30} | {description}")
                
            except Exception as e:
                print(f"❌ ERROR  | {method:6} | {endpoint:30} | {str(e)[:40]}...")
        
        print("=" * 60)
        print(f"📊 Endpoint Coverage: {working_endpoints}/{total_endpoints} ({working_endpoints/total_endpoints*100:.1f}%)")
        
        if working_endpoints >= total_endpoints * 0.9:
            print("🎉 EXCELLENT: API endpoints are comprehensive!")
        elif working_endpoints >= total_endpoints * 0.7:
            print("⚠️  GOOD: Most endpoints exist, minor gaps remain")
        else:
            print("❌ NEEDS WORK: Significant endpoint gaps detected")

if __name__ == "__main__":
    asyncio.run(test_endpoints())