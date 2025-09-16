#!/usr/bin/env python3
"""
GPT.R1 - Final Production Validation Script
Author: Rajan Mishra
Comprehensive validation for production deployment
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path

class GPTr1Validator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.validation_results = {}
        
    def print_header(self):
        """Print validation header."""
        print("🎯" + "=" * 70)
        print("  GPT.R1 - PRODUCTION VALIDATION SUITE")
        print("  👨‍💻 Created by: Rajan Mishra")
        print("  🚀 Advanced AI Assistant - Enterprise Ready")
        print("=" * 72)
        
    def validate_environment(self):
        """Validate environment setup."""
        print("\n1️⃣ ENVIRONMENT VALIDATION")
        print("-" * 35)
        
        checks = []
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 11):
            print(f"  ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
            checks.append(True)
        else:
            print(f"  ❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (Required: 3.11+)")
            checks.append(False)
            
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                print(f"  ✅ Node.js {node_version}")
                checks.append(True)
            else:
                print("  ❌ Node.js not found")
                checks.append(False)
        except FileNotFoundError:
            print("  ❌ Node.js not installed")
            checks.append(False)
            
        # Check required files
        required_files = [
            'backend/main.py',
            'backend/requirements.txt',
            'frontend/package.json',
            'backend/.env',
            'README.md'
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"  ✅ {file_path}")
                checks.append(True)
            else:
                print(f"  ❌ {file_path} missing")
                checks.append(False)
                
        self.validation_results['environment'] = {
            'passed': all(checks),
            'score': sum(checks) / len(checks) * 100
        }
        
    def validate_backend(self):
        """Validate backend functionality."""
        print("\n2️⃣ BACKEND VALIDATION")
        print("-" * 35)
        
        checks = []
        
        # Check if backend is running
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                print("  ✅ Backend server running")
                checks.append(True)
            else:
                print(f"  ❌ Backend health check failed: {response.status_code}")
                checks.append(False)
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Backend not accessible: {e}")
            checks.append(False)
            return
            
        # Test API endpoints
        endpoints = [
            ('/', 'Root endpoint'),
            ('/api/v1/openapi.json', 'OpenAPI docs'),
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ {description}")
                    checks.append(True)
                else:
                    print(f"  ❌ {description} failed: {response.status_code}")
                    checks.append(False)
            except Exception as e:
                print(f"  ❌ {description} error: {e}")
                checks.append(False)
                
        # Test authentication endpoints
        auth_data = {
            "username": "validation_user",
            "email": "validation@test.com",
            "password": "ValidationPass123!"
        }
        
        try:
            # Try to register
            response = requests.post(f"{self.backend_url}/api/v1/auth/register", json=auth_data)
            if response.status_code in [200, 400]:  # 400 if user already exists
                print("  ✅ Authentication registration")
                checks.append(True)
            else:
                print(f"  ❌ Authentication registration failed: {response.status_code}")
                checks.append(False)
        except Exception as e:
            print(f"  ❌ Authentication error: {e}")
            checks.append(False)
            
        self.validation_results['backend'] = {
            'passed': all(checks),
            'score': sum(checks) / len(checks) * 100
        }
        
    def validate_frontend(self):
        """Validate frontend functionality."""
        print("\n3️⃣ FRONTEND VALIDATION")
        print("-" * 35)
        
        checks = []
        
        # Check if frontend is accessible
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                print("  ✅ Frontend server running")
                checks.append(True)
            else:
                print(f"  ❌ Frontend not accessible: {response.status_code}")
                checks.append(False)
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Frontend connection failed: {e}")
            checks.append(False)
            
        # Check build files
        frontend_files = [
            'frontend/next.config.js',
            'frontend/tailwind.config.js',
            'frontend/tsconfig.json'
        ]
        
        for file_path in frontend_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"  ✅ {file_path.split('/')[-1]}")
                checks.append(True)
            else:
                print(f"  ❌ {file_path.split('/')[-1]} missing")
                checks.append(False)
                
        self.validation_results['frontend'] = {
            'passed': all(checks),
            'score': sum(checks) / len(checks) * 100
        }
        
    def validate_features(self):
        """Validate key features."""
        print("\n4️⃣ FEATURE VALIDATION")
        print("-" * 35)
        
        checks = []
        
        # Check OpenAI configuration
        try:
            response = requests.get(f"{self.backend_url}/")
            if response.status_code == 200:
                data = response.json()
                if "GPT.R1" in data.get("message", ""):
                    print("  ✅ GPT.R1 branding")
                    checks.append(True)
                else:
                    print("  ❌ GPT.R1 branding missing")
                    checks.append(False)
                    
                if "features" in data:
                    print(f"  ✅ Features listed ({len(data['features'])} features)")
                    checks.append(True)
                else:
                    print("  ❌ Features not listed")
                    checks.append(False)
        except Exception as e:
            print(f"  ❌ Feature check failed: {e}")
            checks.append(False)
            
        # Check database
        try:
            db_path = self.project_root / "backend" / "chatgpt_clone.db"
            if db_path.exists():
                print("  ✅ Database file exists")
                checks.append(True)
            else:
                print("  ❌ Database file missing")
                checks.append(False)
        except Exception as e:
            print(f"  ❌ Database check failed: {e}")
            checks.append(False)
            
        # Check test files
        test_files = [
            'backend/tests/test_comprehensive.py',
            'backend/test_performance.py'
        ]
        
        for file_path in test_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"  ✅ {file_path.split('/')[-1]}")
                checks.append(True)
            else:
                print(f"  ❌ {file_path.split('/')[-1]} missing")
                checks.append(False)
                
        self.validation_results['features'] = {
            'passed': all(checks),
            'score': sum(checks) / len(checks) * 100
        }
        
    def validate_security(self):
        """Validate security measures."""
        print("\n5️⃣ SECURITY VALIDATION")
        print("-" * 35)
        
        checks = []
        
        # Check CORS configuration
        try:
            response = requests.options(f"{self.backend_url}/api/v1/auth/register")
            if 'access-control-allow-origin' in response.headers:
                print("  ✅ CORS configured")
                checks.append(True)
            else:
                print("  ❌ CORS not configured")
                checks.append(False)
        except Exception as e:
            print(f"  ❌ CORS check failed: {e}")
            checks.append(False)
            
        # Check authentication protection
        try:
            response = requests.get(f"{self.backend_url}/api/v1/auth/me")
            if response.status_code == 401:
                print("  ✅ Protected endpoints secured")
                checks.append(True)
            else:
                print("  ❌ Protected endpoints not secured")
                checks.append(False)
        except Exception as e:
            print(f"  ❌ Auth protection check failed: {e}")
            checks.append(False)
            
        # Check environment file security
        env_path = self.project_root / "backend" / ".env"
        if env_path.exists():
            with open(env_path, 'r') as f:
                env_content = f.read()
                if "OPENAI_API_KEY=" in env_content and "SECRET_KEY=" in env_content:
                    print("  ✅ Environment variables configured")
                    checks.append(True)
                else:
                    print("  ❌ Missing critical environment variables")
                    checks.append(False)
        else:
            print("  ❌ Environment file missing")
            checks.append(False)
            
        self.validation_results['security'] = {
            'passed': all(checks),
            'score': sum(checks) / len(checks) * 100
        }
        
    def generate_final_report(self):
        """Generate final validation report."""
        print("\n🏆 FINAL VALIDATION REPORT")
        print("=" * 50)
        
        total_score = 0
        total_sections = 0
        all_passed = True
        
        for section, results in self.validation_results.items():
            status = "✅ PASS" if results['passed'] else "❌ FAIL"
            print(f"  {section.upper():<15} {status:>10} ({results['score']:.1f}%)")
            total_score += results['score']
            total_sections += 1
            if not results['passed']:
                all_passed = False
                
        overall_score = total_score / total_sections if total_sections > 0 else 0
        
        print("-" * 50)
        print(f"  OVERALL SCORE: {overall_score:.1f}%")
        
        if overall_score >= 95:
            grade = "A+ (PRODUCTION READY)"
            status = "🏅"
        elif overall_score >= 90:
            grade = "A (EXCELLENT)"
            status = "🥇"
        elif overall_score >= 85:
            grade = "B+ (VERY GOOD)"
            status = "🥈"
        elif overall_score >= 80:
            grade = "B (GOOD)"
            status = "🥉"
        else:
            grade = "C (NEEDS IMPROVEMENT)"
            status = "📝"
            
        print(f"  GRADE: {status} {grade}")
        
        if all_passed and overall_score >= 90:
            print("\n🎉 CONGRATULATIONS!")
            print("  GPT.R1 is ready for production deployment!")
            print("  All validation checks passed successfully.")
            print("  🚀 Ready to upload to GitHub!")
        else:
            print("\n⚠️  ISSUES DETECTED")
            print("  Please address the failed checks before deployment.")
            
        return all_passed and overall_score >= 90
        
    def create_deployment_checklist(self):
        """Create deployment checklist."""
        checklist = """
🚀 GPT.R1 - DEPLOYMENT CHECKLIST
================================

Pre-Deployment:
□ All validation tests passed
□ OpenAI API key configured
□ Environment variables set
□ Database initialized
□ Dependencies installed

GitHub Upload:
□ Repository created
□ Files committed and pushed
□ README.md updated
□ License added
□ .gitignore configured

Production Setup:
□ Server provisioned
□ Domain configured
□ SSL certificates installed
□ Environment variables set
□ Database backup configured
□ Monitoring enabled

Post-Deployment:
□ Health checks passing
□ Performance metrics normal
□ Error rates acceptable
□ User acceptance testing
□ Documentation updated

🎯 SUCCESS CRITERIA:
- Response time < 500ms
- Uptime > 99.9%
- Error rate < 0.1%
- User satisfaction > 95%

Created by: Rajan Mishra
Project: GPT.R1 - Advanced AI Assistant
"""
        
        with open(self.project_root / "DEPLOYMENT_CHECKLIST.md", 'w') as f:
            f.write(checklist)
            
        print("\n📋 Deployment checklist created: DEPLOYMENT_CHECKLIST.md")
        
    def run_validation(self):
        """Run complete validation suite."""
        self.print_header()
        
        self.validate_environment()
        self.validate_backend()
        self.validate_frontend()
        self.validate_features()
        self.validate_security()
        
        is_ready = self.generate_final_report()
        self.create_deployment_checklist()
        
        print("\n" + "=" * 72)
        print("  GPT.R1 - VALIDATION COMPLETE")
        print("  👨‍💻 Rajan Mishra | Advanced AI Assistant")
        print("=" * 72)
        
        return is_ready

if __name__ == "__main__":
    validator = GPTr1Validator()
    success = validator.run_validation()
    
    if success:
        print("\n🎊 GPT.R1 is production-ready!")
        sys.exit(0)
    else:
        print("\n🔧 Please fix issues before deployment.")
        sys.exit(1)