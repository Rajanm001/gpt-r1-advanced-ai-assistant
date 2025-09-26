"""
🚀 DIRECTOR-LEVEL TESTING SUITE
Complete system validation for ChatGPT Clone
"""
import asyncio
import requests
import json
import time
import sys
from typing import Dict, Any

class DirectorTestSuite:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_results = {}
        
    def print_header(self, title: str):
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    def print_test(self, test_name: str, result: bool, details: str = ""):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    📋 {details}")
        self.test_results[test_name] = result
    
    def test_backend_health(self):
        """Test backend server health"""
        self.print_header("BACKEND HEALTH TESTS")
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            self.print_test(
                "Backend Health Endpoint",
                response.status_code == 200,
                f"Status: {response.status_code}, Response: {response.text}"
            )
        except Exception as e:
            self.print_test("Backend Health Endpoint", False, f"Error: {str(e)}")
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        self.print_header("API ENDPOINT TESTS")
        
        # Test conversations endpoint
        try:
            response = requests.get(f"{self.backend_url}/api/v1/conversations", timeout=5)
            self.print_test(
                "Conversations List Endpoint",
                response.status_code == 200,
                f"Status: {response.status_code}, Count: {len(response.json())}"
            )
        except Exception as e:
            self.print_test("Conversations List Endpoint", False, f"Error: {str(e)}")
        
        # Test API documentation
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=5)
            self.print_test(
                "API Documentation",
                response.status_code == 200,
                "OpenAPI docs accessible"
            )
        except Exception as e:
            self.print_test("API Documentation", False, f"Error: {str(e)}")
    
    def test_frontend_accessibility(self):
        """Test frontend server accessibility"""
        self.print_header("FRONTEND ACCESSIBILITY TESTS")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            self.print_test(
                "Frontend Server Running",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            self.print_test("Frontend Server Running", False, f"Error: {str(e)}")
    
    def test_database_functionality(self):
        """Test database operations"""
        self.print_header("DATABASE FUNCTIONALITY TESTS")
        
        try:
            # Test creating a conversation
            conversation_data = {"title": "Test Conversation"}
            response = requests.post(
                f"{self.backend_url}/api/v1/conversations",
                json=conversation_data,
                timeout=5
            )
            
            if response.status_code == 200:
                conv_id = response.json()["id"]
                self.print_test(
                    "Database Write Operation",
                    True,
                    f"Created conversation ID: {conv_id}"
                )
                
                # Test reading the conversation
                read_response = requests.get(
                    f"{self.backend_url}/api/v1/conversations/{conv_id}",
                    timeout=5
                )
                self.print_test(
                    "Database Read Operation",
                    read_response.status_code == 200,
                    f"Retrieved conversation: {read_response.json()['title']}"
                )
            else:
                self.print_test("Database Write Operation", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.print_test("Database Operations", False, f"Error: {str(e)}")
    
    def test_performance(self):
        """Test system performance"""
        self.print_header("PERFORMANCE TESTS")
        
        # Test response time
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            self.print_test(
                "Response Time < 100ms",
                response_time < 100,
                f"Response time: {response_time:.2f}ms"
            )
        except Exception as e:
            self.print_test("Response Time Test", False, f"Error: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.print_header("COMPREHENSIVE TEST REPORT")
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {total - passed}")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        if pass_rate >= 90:
            print(f"\n🏆 EXCELLENT: Director-level quality achieved!")
        elif pass_rate >= 70:
            print(f"\n✅ GOOD: System is functional")
        else:
            print(f"\n⚠️  NEEDS ATTENTION: Some issues detected")
        
        return pass_rate >= 90
    
    def run_all_tests(self):
        """Execute complete test suite"""
        print("🚀 DIRECTOR-LEVEL TESTING SUITE")
        print("🎯 Validating ChatGPT Clone Excellence")
        print("⏱️  Starting comprehensive testing...")
        
        self.test_backend_health()
        self.test_api_endpoints()
        self.test_frontend_accessibility()
        self.test_database_functionality()
        self.test_performance()
        
        return self.generate_report()

if __name__ == "__main__":
    print("🎯 DIRECTOR AI TESTING SUITE")
    print("=" * 60)
    
    # Wait a moment for servers to be ready
    print("⏳ Initializing test environment...")
    time.sleep(2)
    
    # Run comprehensive tests
    test_suite = DirectorTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 SYSTEM VALIDATION COMPLETE")
        print("✅ All systems operational - Ready for client delivery!")
        sys.exit(0)
    else:
        print("\n⚠️  SYSTEM NEEDS ATTENTION")
        print("❌ Some tests failed - Please review and fix")
        sys.exit(1)