#!/usr/bin/env python3
"""
GPT.R1 - Test Runner
Comprehensive test execution script with detailed reporting
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
import argparse

class GPTTestRunner:
    """Comprehensive test runner for GPT.R1 system"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.test_results = {}
        self.backend_path = Path(__file__).parent.parent
        self.test_path = Path(__file__).parent
    
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
    
    def run_command(self, command: list, description: str) -> tuple:
        """Run command and capture output"""
        print(f"\n🔄 {description}...")
        print(f"Command: {' '.join(command)}")
        
        start_time = time.time()
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self.backend_path,
                timeout=300  # 5 minute timeout
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            success = result.returncode == 0
            
            if success:
                print(f"✅ {description} completed in {execution_time:.2f}s")
            else:
                print(f"❌ {description} failed after {execution_time:.2f}s")
                print(f"Error: {result.stderr}")
            
            return success, execution_time, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} timed out after 5 minutes")
            return False, 300, "", "Command timed out"
        except Exception as e:
            print(f"💥 {description} crashed: {str(e)}")
            return False, 0, "", str(e)
    
    def install_test_dependencies(self):
        """Install test dependencies"""
        self.print_section("Installing Test Dependencies")
        
        commands = [
            (["pip", "install", "-r", "tests/requirements-test.txt"], "Installing test requirements"),
            (["pip", "install", "-e", "."], "Installing backend package in development mode")
        ]
        
        all_success = True
        for command, description in commands:
            success, execution_time, stdout, stderr = self.run_command(command, description)
            if not success:
                all_success = False
        
        return all_success
    
    def run_basic_tests(self):
        """Run basic functionality tests"""
        self.print_section("Basic Functionality Tests")
        
        command = [
            "python", "-m", "pytest",
            "tests/test_api_endpoints.py::TestHealthEndpoints",
            "tests/test_database.py::TestDatabaseConnection",
            "-v", "--tb=short"
        ]
        
        success, execution_time, stdout, stderr = self.run_command(
            command, "Basic functionality tests"
        )
        
        self.test_results["basic"] = {
            "success": success,
            "execution_time": execution_time,
            "stdout": stdout,
            "stderr": stderr
        }
        
        return success
    
    def run_database_tests(self):
        """Run database tests"""
        self.print_section("Database Tests")
        
        command = [
            "python", "-m", "pytest",
            "tests/test_database.py",
            "-v", "--tb=short"
        ]
        
        success, execution_time, stdout, stderr = self.run_command(
            command, "Database CRUD and operations tests"
        )
        
        self.test_results["database"] = {
            "success": success,
            "execution_time": execution_time,
            "stdout": stdout,
            "stderr": stderr
        }
        
        return success
    
    def run_service_tests(self):
        """Run service layer tests"""
        self.print_section("Service Layer Tests")
        
        command = [
            "python", "-m", "pytest",
            "tests/test_services.py",
            "-v", "--tb=short"
        ]
        
        success, execution_time, stdout, stderr = self.run_command(
            command, "Service layer functionality tests"
        )
        
        self.test_results["services"] = {
            "success": success,
            "execution_time": execution_time,
            "stdout": stdout,
            "stderr": stderr
        }
        
        return success
    
    def run_api_tests(self):
        """Run API endpoint tests"""
        self.print_section("API Endpoint Tests")
        
        command = [
            "python", "-m", "pytest",
            "tests/test_api_endpoints.py",
            "-v", "--tb=short"
        ]
        
        success, execution_time, stdout, stderr = self.run_command(
            command, "API endpoint and streaming tests"
        )
        
        self.test_results["api"] = {
            "success": success,
            "execution_time": execution_time,
            "stdout": stdout,
            "stderr": stderr
        }
        
        return success
    
    def run_integration_tests(self):
        """Run integration tests"""
        self.print_section("Integration Tests")
        
        command = [
            "python", "-m", "pytest",
            "tests/test_integration.py",
            "-v", "--tb=short"
        ]
        
        success, execution_time, stdout, stderr = self.run_command(
            command, "End-to-end integration tests"
        )
        
        self.test_results["integration"] = {
            "success": success,
            "execution_time": execution_time,
            "stdout": stdout,
            "stderr": stderr
        }
        
        return success
    
    def run_comprehensive_tests(self):
        """Run comprehensive test suite"""
        self.print_section("Comprehensive Test Suite")
        
        command = [
            "python", "-m", "pytest",
            "tests/test_comprehensive_suite.py",
            "-v", "--tb=short"
        ]
        
        success, execution_time, stdout, stderr = self.run_command(
            command, "Complete comprehensive test suite"
        )
        
        self.test_results["comprehensive"] = {
            "success": success,
            "execution_time": execution_time,
            "stdout": stdout,
            "stderr": stderr
        }
        
        return success
    
    def run_performance_tests(self):
        """Run performance tests"""
        self.print_section("Performance Tests")
        
        command = [
            "python", "-m", "pytest",
            "tests/test_integration.py::TestPerformanceIntegration",
            "tests/test_database.py::TestDatabasePerformance",
            "-v", "--tb=short"
        ]
        
        success, execution_time, stdout, stderr = self.run_command(
            command, "Performance and load tests"
        )
        
        self.test_results["performance"] = {
            "success": success,
            "execution_time": execution_time,
            "stdout": stdout,
            "stderr": stderr
        }
        
        return success
    
    def run_security_tests(self):
        """Run security tests"""
        self.print_section("Security Tests")
        
        command = [
            "python", "-m", "pytest",
            "tests/test_integration.py::TestSecurityIntegration",
            "tests/test_api_endpoints.py::TestRequestValidation",
            "-v", "--tb=short"
        ]
        
        success, execution_time, stdout, stderr = self.run_command(
            command, "Security and validation tests"
        )
        
        self.test_results["security"] = {
            "success": success,
            "execution_time": execution_time,
            "stdout": stdout,
            "stderr": stderr
        }
        
        return success
    
    def run_coverage_analysis(self):
        """Run test coverage analysis"""
        self.print_section("Coverage Analysis")
        
        commands = [
            (["python", "-m", "pytest", "--cov=backend/app", "--cov-report=term-missing", 
              "tests/", "-v"], "Running tests with coverage"),
            (["python", "-m", "pytest", "--cov=backend/app", "--cov-report=html", 
              "tests/"], "Generating HTML coverage report")
        ]
        
        coverage_success = True
        for command, description in commands:
            success, execution_time, stdout, stderr = self.run_command(command, description)
            if not success:
                coverage_success = False
        
        self.test_results["coverage"] = {
            "success": coverage_success,
            "execution_time": sum(r.get("execution_time", 0) for r in self.test_results.values()),
            "stdout": "Coverage analysis completed",
            "stderr": ""
        }
        
        return coverage_success
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.print_header("TEST EXECUTION REPORT")
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n📊 Test Execution Summary")
        print(f"   Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Total Duration: {total_time:.2f} seconds")
        print(f"   Test Suites: {len(self.test_results)}")
        
        # Calculate overall statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Results Overview")
        print(f"   ✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"   ❌ Failed: {failed_tests}/{total_tests} ({100-success_rate:.1f}%)")
        
        # Detailed results
        print(f"\n📋 Detailed Results")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            execution_time = result["execution_time"]
            print(f"   {test_name.upper():<15} {status} ({execution_time:.2f}s)")
        
        # Quality score calculation
        quality_score = self.calculate_quality_score()
        print(f"\n🎯 Overall Quality Score: {quality_score:.1f}/100")
        
        # Recommendations
        self.print_recommendations(quality_score)
        
        return quality_score >= 85  # Success threshold
    
    def calculate_quality_score(self) -> float:
        """Calculate overall quality score"""
        # Weight different test categories
        weights = {
            "basic": 15,
            "database": 20,
            "services": 20,
            "api": 20,
            "integration": 15,
            "comprehensive": 5,
            "performance": 3,
            "security": 2
        }
        
        weighted_score = 0
        total_weight = 0
        
        for test_name, weight in weights.items():
            if test_name in self.test_results:
                score = 100 if self.test_results[test_name]["success"] else 0
                weighted_score += score * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0
    
    def print_recommendations(self, quality_score: float):
        """Print improvement recommendations"""
        print(f"\n💡 Recommendations")
        
        if quality_score >= 90:
            print("   🌟 Excellent! System is production-ready.")
            print("   🚀 Consider adding more edge case tests for robustness.")
        elif quality_score >= 85:
            print("   🎯 Good quality! System meets job requirements.")
            print("   📈 Consider optimizing performance and adding more tests.")
        elif quality_score >= 70:
            print("   ⚠️  Acceptable but needs improvement.")
            print("   🔧 Focus on fixing failed tests and improving coverage.")
        else:
            print("   🚨 Critical issues need attention.")
            print("   🛠️  Prioritize fixing core functionality tests.")
        
        # Specific recommendations based on failed tests
        failed_tests = [name for name, result in self.test_results.items() if not result["success"]]
        if failed_tests:
            print(f"\n🔨 Priority fixes needed for: {', '.join(failed_tests)}")
    
    def run_quick_tests(self):
        """Run quick essential tests only"""
        self.print_header("Quick Essential Tests")
        
        # Run only critical tests
        success = True
        success &= self.run_basic_tests()
        success &= self.run_api_tests()
        
        return success
    
    def run_full_test_suite(self):
        """Run complete test suite"""
        self.print_header("Complete Test Suite Execution")
        
        # Install dependencies first
        if not self.install_test_dependencies():
            print("❌ Failed to install test dependencies")
            return False
        
        # Run all test categories
        test_categories = [
            self.run_basic_tests,
            self.run_database_tests,
            self.run_service_tests,
            self.run_api_tests,
            self.run_integration_tests,
            self.run_comprehensive_tests,
            self.run_performance_tests,
            self.run_security_tests
        ]
        
        overall_success = True
        for test_category in test_categories:
            try:
                success = test_category()
                if not success:
                    overall_success = False
            except Exception as e:
                print(f"💥 Test category failed with exception: {str(e)}")
                overall_success = False
        
        # Generate coverage report
        try:
            self.run_coverage_analysis()
        except Exception as e:
            print(f"⚠️ Coverage analysis failed: {str(e)}")
        
        # Generate final report
        return self.generate_test_report()

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="GPT.R1 Test Runner")
    parser.add_argument(
        "--mode",
        choices=["quick", "full", "basic", "integration", "performance"],
        default="full",
        help="Test execution mode"
    )
    
    args = parser.parse_args()
    
    runner = GPTTestRunner()
    
    try:
        if args.mode == "quick":
            success = runner.run_quick_tests()
        elif args.mode == "basic":
            success = runner.run_basic_tests()
        elif args.mode == "integration":
            success = runner.run_integration_tests()
        elif args.mode == "performance":
            success = runner.run_performance_tests()
        else:  # full
            success = runner.run_full_test_suite()
        
        # Final summary
        print("\n" + "="*80)
        if success:
            print("🎉 TEST SUITE PASSED - System ready for deployment!")
        else:
            print("🚨 TEST SUITE FAILED - Issues need attention")
        print("="*80)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test runner failed with exception: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())