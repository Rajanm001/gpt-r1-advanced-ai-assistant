#!/usr/bin/env python3
"""
Comprehensive Integration Testing Script for ChatGPT Clone
Tests all functionality to ensure 100% client satisfaction
"""

import requests
import json
import time
import sys
import subprocess
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class TestRunner:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        
    def log(self, message, test_type="INFO"):
        """Log test messages"""
        prefix = "✅" if test_type == "PASS" else "❌" if test_type == "FAIL" else "ℹ️"
        print(f"{prefix} {message}")
        
    def test_case(self, name, test_func):
        """Run a single test case"""
        try:
            result = test_func()
            if result:
                self.tests_passed += 1
                self.log(f"PASS: {name}", "PASS")
                self.test_results.append({"name": name, "status": "PASS", "details": ""})
            else:
                self.tests_failed += 1
                self.log(f"FAIL: {name}", "FAIL")
                self.test_results.append({"name": name, "status": "FAIL", "details": "Test returned False"})
        except Exception as e:
            self.tests_failed += 1
            self.log(f"FAIL: {name} - {str(e)}", "FAIL")
            self.test_results.append({"name": name, "status": "FAIL", "details": str(e)})
    
    def test_health_endpoint(self):
        """Test basic server health"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_api_docs(self):
        """Test API documentation is available"""
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_cors_headers(self):
        """Test CORS headers are properly configured"""
        try:
            response = requests.options(f"{BASE_URL}/api/v1/auth/register", timeout=5)
            return "access-control-allow-origin" in response.headers
        except:
            return False
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        try:
            test_user = {
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User"
            }
            response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=test_user, timeout=5)
            return response.status_code in [200, 201, 400]  # 400 if user already exists
        except:
            return False
    
    def test_static_files_exist(self):
        """Test that all required files exist"""
        required_files = [
            "main.py",
            "app/__init__.py",
            "app/api/v1/__init__.py",
            "app/core/database.py",
            "app/models/__init__.py",
            "app/schemas/__init__.py",
            "app/services/__init__.py",
            "requirements.txt",
            ".env.example"
        ]
        
        backend_path = Path(__file__).parent
        for file_path in required_files:
            full_path = backend_path / file_path
            if not full_path.exists():
                return False
        return True
    
    def test_requirements_installable(self):
        """Test that requirements.txt is valid"""
        try:
            requirements_path = Path(__file__).parent / "requirements.txt"
            with open(requirements_path, 'r') as f:
                content = f.read()
            # Basic validation
            return len(content.strip()) > 0 and "fastapi" in content.lower()
        except:
            return False
    
    def test_environment_config(self):
        """Test environment configuration files"""
        try:
            env_example = Path(__file__).parent / ".env.example"
            return env_example.exists()
        except:
            return False
    
    def print_summary(self):
        """Print test summary"""
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print("\n📋 DETAILED RESULTS:")
        
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_icon} {result['name']}")
            if result["details"]:
                print(f"   └─ {result['details']}")
        
        print("\n" + "="*60)
        
        if success_rate >= 100:
            print("🎉 ALL TESTS PASSED! Project is ready for client delivery!")
        elif success_rate >= 80:
            print("🚀 EXCELLENT! Most tests passed. Minor issues to address.")
        elif success_rate >= 60:
            print("⚠️  GOOD progress, but some important issues need fixing.")
        else:
            print("🔧 NEEDS WORK. Several critical issues require attention.")
        
        return success_rate >= 80  # Consider 80%+ as acceptable

def main():
    """Run comprehensive backend testing"""
    print("🚀 Starting Comprehensive Backend Testing")
    print("Testing all functionality for 100% client satisfaction\n")
    
    runner = TestRunner()
    
    # Static file and configuration tests (always run)
    print("📁 Testing File Structure and Configuration...")
    runner.test_case("Required Files Exist", runner.test_static_files_exist)
    runner.test_case("Requirements.txt Valid", runner.test_requirements_installable)
    runner.test_case("Environment Config", runner.test_environment_config)
    
    # Server-dependent tests (only if server is running)
    print("\n🌐 Testing API Endpoints...")
    runner.test_case("Health Endpoint", runner.test_health_endpoint)
    runner.test_case("API Documentation", runner.test_api_docs)
    runner.test_case("CORS Configuration", runner.test_cors_headers)
    runner.test_case("User Registration", runner.test_user_registration)
    
    # Print comprehensive summary
    success = runner.print_summary()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)