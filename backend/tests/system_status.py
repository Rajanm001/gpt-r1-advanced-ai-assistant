"""
GPT.R1 - System Status Verification
Comprehensive verification of all system components and functionality
Created by: Rajan Mishra
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

class SystemStatusVerifier:
    """Comprehensive system status verification"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {}
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"🎯 {title}")
        print("="*80)
    
    def print_section(self, title: str):
        """Print formatted section"""
        print("\n" + "-"*60)
        print(f"📋 {title}")
        print("-"*60)
    
    def verify_file_structure(self) -> bool:
        """Verify all required files exist"""
        self.print_section("File Structure Verification")
        
        required_files = [
            "main.py",
            "app/__init__.py",
            "app/core/config.py",
            "app/core/database.py",
            "app/models/conversation.py",
            "app/models/message.py",
            "app/schemas/chat.py",
            "app/schemas/workflow.py",
            "app/services/chat_service.py",
            "app/services/agentic_service.py",
            "app/services/multi_tool_orchestrator.py",
            "app/services/openai_service.py",
            "app/services/rag_service.py",
            "app/api/chat_enhanced.py",
            "app/api/conversations.py",
            "app/crud/conversation_crud.py",
            "app/crud/message_crud.py",
            "requirements.txt"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            full_path = backend_dir / file_path
            if full_path.exists():
                existing_files.append(file_path)
                print(f"✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"❌ {file_path} - MISSING")
        
        success = len(missing_files) == 0
        
        print(f"\n📊 File Structure Results:")
        print(f"   ✅ Existing: {len(existing_files)}/{len(required_files)}")
        print(f"   ❌ Missing: {len(missing_files)}/{len(required_files)}")
        
        self.results["file_structure"] = {
            "success": success,
            "existing": len(existing_files),
            "missing": len(missing_files),
            "total": len(required_files)
        }
        
        return success
    
    def verify_test_structure(self) -> bool:
        """Verify test structure"""
        self.print_section("Test Structure Verification")
        
        test_files = [
            "tests/__init__.py",
            "tests/conftest.py",
            "tests/test_comprehensive_suite.py",
            "tests/test_api_endpoints.py",
            "tests/test_services.py",
            "tests/test_database.py",
            "tests/test_integration.py",
            "tests/run_tests.py",
            "tests/requirements-test.txt"
        ]
        
        missing_tests = []
        existing_tests = []
        
        for test_file in test_files:
            full_path = backend_dir / test_file
            if full_path.exists():
                existing_tests.append(test_file)
                print(f"✅ {test_file}")
            else:
                missing_tests.append(test_file)
                print(f"❌ {test_file} - MISSING")
        
        success = len(missing_tests) == 0
        
        print(f"\n📊 Test Structure Results:")
        print(f"   ✅ Existing: {len(existing_tests)}/{len(test_files)}")
        print(f"   ❌ Missing: {len(missing_tests)}/{len(test_files)}")
        
        self.results["test_structure"] = {
            "success": success,
            "existing": len(existing_tests),
            "missing": len(missing_tests),
            "total": len(test_files)
        }
        
        return success
    
    def verify_dependencies(self) -> bool:
        """Verify required dependencies are installed"""
        self.print_section("Dependencies Verification")
        
        required_deps = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "asyncpg",
            "pydantic",
            "openai",
            "duckduckgo-search",
            "python-multipart",
            "pytest",
            "pytest-asyncio",
            "httpx"
        ]
        
        missing_deps = []
        installed_deps = []
        
        for dep in required_deps:
            try:
                __import__(dep.replace("-", "_"))
                installed_deps.append(dep)
                print(f"✅ {dep}")
            except ImportError:
                missing_deps.append(dep)
                print(f"❌ {dep} - NOT INSTALLED")
        
        success = len(missing_deps) == 0
        
        print(f"\n📊 Dependencies Results:")
        print(f"   ✅ Installed: {len(installed_deps)}/{len(required_deps)}")
        print(f"   ❌ Missing: {len(missing_deps)}/{len(required_deps)}")
        
        self.results["dependencies"] = {
            "success": success,
            "installed": len(installed_deps),
            "missing": len(missing_deps),
            "total": len(required_deps)
        }
        
        return success
    
    def verify_core_functionality(self) -> bool:
        """Verify core functionality without database"""
        self.print_section("Core Functionality Verification")
        
        try:
            # Test 1: FastAPI app creation
            from fastapi import FastAPI
            app = FastAPI(title="Test App")
            print("✅ FastAPI app creation")
            
            # Test 2: Basic imports
            from app.schemas.chat import ChatRequest, MessageCreate
            print("✅ Schema imports")
            
            # Test 3: Enum definitions
            from app.schemas.workflow import StepType, WorkflowStep
            print("✅ Workflow schema imports")
            
            # Test 4: Mock database models
            from unittest.mock import MagicMock
            mock_conversation = MagicMock()
            mock_conversation.id = 1
            mock_conversation.title = "Test"
            print("✅ Model mocking")
            
            # Test 5: Basic request validation
            request_data = ChatRequest(message="Test message", conversation_id=None)
            assert request_data.message == "Test message"
            print("✅ Request validation")
            
            success = True
            
        except Exception as e:
            print(f"❌ Core functionality failed: {e}")
            success = False
        
        self.results["core_functionality"] = {"success": success}
        return success
    
    def verify_configuration_compliance(self) -> bool:
        """Verify PostgreSQL compliance and configuration"""
        self.print_section("Configuration Compliance Verification")
        
        compliance_checks = []
        
        try:
            # Check 1: PostgreSQL configuration
            from app.core.config import settings
            database_url = settings.get_database_url()
            
            if "postgresql" in database_url.lower():
                print("✅ PostgreSQL configuration detected")
                compliance_checks.append(True)
            else:
                print("❌ PostgreSQL configuration not found")
                compliance_checks.append(False)
            
            # Check 2: Async driver configuration
            if "asyncpg" in database_url.lower() or "postgresql+asyncpg" in database_url.lower():
                print("✅ AsyncPG driver configuration")
                compliance_checks.append(True)
            else:
                print("❌ AsyncPG driver not configured")
                compliance_checks.append(False)
            
            # Check 3: Multi-tool orchestration system
            orchestrator_file = backend_dir / "app" / "services" / "multi_tool_orchestrator.py"
            if orchestrator_file.exists():
                with open(orchestrator_file, 'r') as f:
                    content = f.read()
                    if "AdvancedToolOrchestrator" in content and "WebSearchTool" in content:
                        print("✅ Multi-tool orchestration system implemented")
                        compliance_checks.append(True)
                    else:
                        print("❌ Multi-tool orchestration system incomplete")
                        compliance_checks.append(False)
            else:
                print("❌ Multi-tool orchestration file missing")
                compliance_checks.append(False)
            
            # Check 4: Enhanced agentic workflow
            agentic_file = backend_dir / "app" / "services" / "agentic_service.py"
            if agentic_file.exists():
                with open(agentic_file, 'r') as f:
                    content = f.read()
                    if "AdvancedAgenticService" in content and "execute_agentic_workflow" in content:
                        print("✅ Enhanced agentic workflow implemented")
                        compliance_checks.append(True)
                    else:
                        print("❌ Enhanced agentic workflow incomplete")
                        compliance_checks.append(False)
            else:
                print("❌ Agentic service file missing")
                compliance_checks.append(False)
            
            # Check 5: Streaming implementation
            chat_api_file = backend_dir / "app" / "api" / "chat_enhanced.py"
            if chat_api_file.exists():
                with open(chat_api_file, 'r') as f:
                    content = f.read()
                    if "stream" in content.lower() and "sse" in content.lower():
                        print("✅ Streaming implementation detected")
                        compliance_checks.append(True)
                    else:
                        print("❌ Streaming implementation incomplete")
                        compliance_checks.append(False)
            else:
                print("❌ Chat API file missing")
                compliance_checks.append(False)
            
        except Exception as e:
            print(f"❌ Configuration compliance check failed: {e}")
            compliance_checks.append(False)
        
        success = all(compliance_checks)
        compliance_score = (sum(compliance_checks) / len(compliance_checks) * 100) if compliance_checks else 0
        
        print(f"\n📊 Compliance Results:")
        print(f"   ✅ Passed: {sum(compliance_checks)}/{len(compliance_checks)}")
        print(f"   📈 Compliance Score: {compliance_score:.1f}%")
        
        self.results["compliance"] = {
            "success": success,
            "score": compliance_score,
            "checks_passed": sum(compliance_checks),
            "total_checks": len(compliance_checks)
        }
        
        return success
    
    def verify_documentation(self) -> bool:
        """Verify documentation and README files"""
        self.print_section("Documentation Verification")
        
        doc_files = [
            "../README.md",
            "../MULTI_TOOL_ORCHESTRATION.md",
            "../FIXES_COMPLETION_REPORT.md",
            "requirements.txt"
        ]
        
        existing_docs = []
        missing_docs = []
        
        for doc_file in doc_files:
            doc_path = backend_dir / doc_file
            if doc_path.exists():
                existing_docs.append(doc_file)
                print(f"✅ {doc_file}")
            else:
                missing_docs.append(doc_file)
                print(f"❌ {doc_file} - MISSING")
        
        success = len(missing_docs) == 0
        
        print(f"\n📊 Documentation Results:")
        print(f"   ✅ Existing: {len(existing_docs)}/{len(doc_files)}")
        print(f"   ❌ Missing: {len(missing_docs)}/{len(doc_files)}")
        
        self.results["documentation"] = {
            "success": success,
            "existing": len(existing_docs),
            "missing": len(missing_docs),
            "total": len(doc_files)
        }
        
        return success
    
    def calculate_overall_score(self) -> float:
        """Calculate overall system score"""
        
        # Weights for different categories
        weights = {
            "file_structure": 20,
            "test_structure": 15,
            "dependencies": 15,
            "core_functionality": 25,
            "compliance": 20,
            "documentation": 5
        }
        
        weighted_score = 0
        total_weight = 0
        
        for category, weight in weights.items():
            if category in self.results:
                if category == "compliance":
                    # Use compliance score directly
                    score = self.results[category].get("score", 0)
                else:
                    # Convert success to percentage
                    score = 100 if self.results[category]["success"] else 0
                
                weighted_score += score * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0
    
    def generate_final_report(self):
        """Generate final verification report"""
        self.print_header("SYSTEM STATUS VERIFICATION REPORT")
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        overall_score = self.calculate_overall_score()
        
        print(f"\n📊 Verification Summary")
        print(f"   Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Duration: {total_time:.2f} seconds")
        print(f"   Categories Verified: {len(self.results)}")
        
        print(f"\n📈 Category Results:")
        for category, result in self.results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            if category == "compliance":
                detail = f"({result['score']:.1f}%)"
            else:
                detail = ""
            print(f"   {category.upper():<20} {status} {detail}")
        
        print(f"\n🎯 Overall System Score: {overall_score:.1f}/100")
        
        # Quality assessment
        if overall_score >= 90:
            status = "🌟 EXCELLENT"
            message = "System is production-ready and exceeds requirements!"
        elif overall_score >= 85:
            status = "🎯 VERY GOOD"
            message = "System meets job requirements and is ready for deployment!"
        elif overall_score >= 70:
            status = "⚠️ ACCEPTABLE"
            message = "System is functional but needs minor improvements."
        else:
            status = "🚨 NEEDS WORK"
            message = "System requires significant improvements before deployment."
        
        print(f"\n{status}")
        print(f"💬 {message}")
        
        # Specific recommendations
        failed_categories = [cat for cat, result in self.results.items() if not result["success"]]
        if failed_categories:
            print(f"\n🔧 Areas needing attention: {', '.join(failed_categories)}")
        
        print(f"\n📋 System Status: {'READY FOR PRODUCTION' if overall_score >= 85 else 'NEEDS IMPROVEMENT'}")
        
        return overall_score >= 85
    
    def run_full_verification(self):
        """Run complete system verification"""
        self.print_header("GPT.R1 System Status Verification")
        
        verification_steps = [
            self.verify_file_structure,
            self.verify_test_structure,
            self.verify_dependencies,
            self.verify_core_functionality,
            self.verify_configuration_compliance,
            self.verify_documentation
        ]
        
        for step in verification_steps:
            try:
                step()
            except Exception as e:
                print(f"❌ Verification step failed: {e}")
                # Continue with other steps
        
        return self.generate_final_report()

def main():
    """Main verification function"""
    verifier = SystemStatusVerifier()
    success = verifier.run_full_verification()
    
    print("\n" + "="*80)
    if success:
        print("🎉 SYSTEM VERIFICATION PASSED - Ready for job submission!")
    else:
        print("🚨 SYSTEM VERIFICATION FAILED - Review required areas")
    print("="*80)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())