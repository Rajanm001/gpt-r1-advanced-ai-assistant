"""
Comprehensive Production Testing Suite for GPT.R1
Tests all critical components for production readiness
"""

import asyncio
import requests
import json
import time
from datetime import datetime

class ProductionTestSuite:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8001"
        self.frontend_url = "http://localhost:3000"
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}: {details}")
        
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/health", timeout=5)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                details += f", Response: {response.json()}"
        except Exception as e:
            success = False
            details = f"Connection failed: {str(e)}"
        
        self.log_test("Backend Health Check", success, details)
        return success
    
    def test_frontend_accessibility(self):
        """Test frontend accessibility"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            success = response.status_code == 200
            details = f"Frontend accessible, Status: {response.status_code}"
        except Exception as e:
            success = False
            details = f"Frontend not accessible: {str(e)}"
        
        self.log_test("Frontend Accessibility", success, details)
        return success
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        try:
            test_user = {
                "username": f"testuser_{int(time.time())}",
                "email": f"test_{int(time.time())}@example.com",
                "password": "TestPassword123!",
                "confirm_password": "TestPassword123!"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/register",
                json=test_user,
                timeout=10
            )
            
            success = response.status_code in [200, 201]
            details = f"Status: {response.status_code}"
            if success:
                details += ", User registered successfully"
            else:
                details += f", Error: {response.text}"
                
        except Exception as e:
            success = False
            details = f"Registration failed: {str(e)}"
        
        self.log_test("User Registration", success, details)
        return success, test_user if success else None
    
    def test_user_login(self, user_data):
        """Test user login endpoint"""
        if not user_data:
            self.log_test("User Login", False, "No user data available")
            return False, None
            
        try:
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                json=login_data,  # Send as JSON instead of form data
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            token = None
            
            if success:
                token_data = response.json()
                token = token_data.get("access_token")
                details += f", Token received: {bool(token)}"
            else:
                details += f", Error: {response.text}"
                
        except Exception as e:
            success = False
            details = f"Login failed: {str(e)}"
        
        self.log_test("User Login", success, details)
        return success, token
    
    def test_protected_endpoint(self, token):
        """Test protected endpoint with authentication"""
        if not token:
            self.log_test("Protected Endpoint Access", False, "No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{self.backend_url}/api/v1/conversations/",
                headers=headers,
                timeout=10
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                conversations = response.json()
                details += f", Conversations: {len(conversations)}"
            else:
                details += f", Error: {response.text}"
                
        except Exception as e:
            success = False
            details = f"Protected endpoint failed: {str(e)}"
        
        self.log_test("Protected Endpoint Access", success, details)
        return success
    
    def test_conversation_creation(self, token):
        """Test conversation creation"""
        if not token:
            self.log_test("Conversation Creation", False, "No token available")
            return False, None
            
        try:
            headers = {"Authorization": f"Bearer {token}"}
            conversation_data = {"title": f"Test Conversation {int(time.time())}"}
            
            response = requests.post(
                f"{self.backend_url}/api/v1/conversations/",
                json=conversation_data,
                headers=headers,
                timeout=10
            )
            
            success = response.status_code in [200, 201]
            details = f"Status: {response.status_code}"
            conversation_id = None
            
            if success:
                conv_data = response.json()
                conversation_id = conv_data.get("id")
                details += f", Conversation ID: {conversation_id}"
            else:
                details += f", Error: {response.text}"
                
        except Exception as e:
            success = False
            details = f"Conversation creation failed: {str(e)}"
        
        self.log_test("Conversation Creation", success, details)
        return success, conversation_id
    
    def test_database_operations(self):
        """Test database connectivity and operations"""
        try:
            # Import here to test database connection
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__)))
            
            from app.core.database import engine
            from sqlalchemy import text
            
            async def check_db():
                async with engine.begin() as conn:
                    result = await conn.execute(text("SELECT 1"))
                    return result.fetchone() is not None
            
            success = asyncio.run(check_db())
            details = "Database connection and query successful"
            
        except Exception as e:
            success = False
            details = f"Database test failed: {str(e)}"
        
        self.log_test("Database Operations", success, details)
        return success
    
    def test_rag_agent(self):
        """Test RAG agent functionality"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__)))
            
            from app.agents.rag_agent import enhance_with_rag
            
            async def test_rag():
                query = "What is artificial intelligence?"
                enhanced_query, search_used = await enhance_with_rag(query)
                return enhanced_query is not None, search_used
            
            enhanced_available, search_used = asyncio.run(test_rag())
            success = enhanced_available
            details = f"RAG enhancement working, Search used: {search_used}"
            
        except Exception as e:
            success = False
            details = f"RAG test failed: {str(e)}"
        
        self.log_test("RAG Agent", success, details)
        return success
    
    def run_comprehensive_tests(self):
        """Run all production tests"""
        print("🚀 Starting Comprehensive Production Test Suite")
        print("=" * 60)
        
        # Test 1: Backend Health
        backend_healthy = self.test_backend_health()
        
        # Test 2: Frontend Accessibility
        frontend_accessible = self.test_frontend_accessibility()
        
        # Test 3: Database Operations
        database_working = self.test_database_operations()
        
        # Test 4: RAG Agent
        rag_working = self.test_rag_agent()
        
        # Test 5: User Registration & Authentication Flow
        if backend_healthy:
            registration_success, user_data = self.test_user_registration()
            if registration_success:
                login_success, token = self.test_user_login(user_data)
                if login_success:
                    self.test_protected_endpoint(token)
                    self.test_conversation_creation(token)
        
        # Generate Report
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 PRODUCTION READINESS:")
        if passed_tests == total_tests:
            print("✅ SYSTEM IS PRODUCTION READY!")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ SYSTEM IS MOSTLY READY (Minor issues to fix)")
        else:
            print("❌ SYSTEM NEEDS SIGNIFICANT WORK BEFORE PRODUCTION")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = ProductionTestSuite()
    production_ready = tester.run_comprehensive_tests()
    
    if production_ready:
        print("\n🎉 ALL SYSTEMS GO! Ready for production deployment!")
    else:
        print("\n🔧 Please fix the issues above before production deployment.")