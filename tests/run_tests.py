#!/usr/bin/env python3
"""
DocuScribe AI Test Runner

Runs all tests for the DocuScribe AI system.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """Run all test suites"""
    print("🧪 DocuScribe AI - Running All Tests")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: System Integration Test
    print("\n1. 🔧 Running System Integration Tests...")
    try:
        from tests.test_system import test_agents
        test_agents()
        print("✅ System integration tests passed")
        success_count += 1
    except Exception as e:
        print(f"❌ System integration tests failed: {e}")
    total_tests += 1
    
    # Test 2: FeedbackAgent LLM Tests
    print("\n2. 🤖 Running FeedbackAgent LLM Tests...")
    try:
        from tests.test_feedback_agent import test_feedback_agent
        test_feedback_agent()
        print("✅ FeedbackAgent LLM tests passed")
        success_count += 1
    except Exception as e:
        print(f"❌ FeedbackAgent LLM tests failed: {e}")
    total_tests += 1
    
    # Test 3: ICD Mapper Tests
    print("\n3. 📋 Running ICD Mapper Tests...")
    try:
        from tests.test_icd_mapper import test_icd_mapper
        test_icd_mapper()
        print("✅ ICD Mapper tests passed")
        success_count += 1
    except Exception as e:
        print(f"❌ ICD Mapper tests failed: {e}")
    total_tests += 1
    
    # Test 4: Performance Tests (optional)
    print("\n4. ⚡ Running Performance Tests...")
    try:
        from tests.focused_performance_test import main as run_performance_test
        run_performance_test()
        print("✅ Performance tests completed")
        success_count += 1
    except Exception as e:
        print(f"❌ Performance tests failed: {e}")
    total_tests += 1
    
    # Test 5: Evaluation System Tests
    print("\n5. 📊 Running Evaluation System Tests...")
    try:
        from tests.test_evaluation_simple import main as run_evaluation_test
        result = run_evaluation_test()
        if result:
            print("✅ Evaluation system tests passed")
            success_count += 1
        else:
            print("⚠️  Evaluation system tests completed with issues")
    except Exception as e:
        print(f"❌ Evaluation system tests failed: {e}")
    total_tests += 1
    
    # Summary
    print(f"\n🎯 Test Results Summary:")
    print(f"   Passed: {success_count}/{total_tests}")
    print(f"   Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("\n🎉 All tests passed! DocuScribe AI is ready for use.")
        return True
    else:
        print(f"\n⚠️  {total_tests - success_count} test(s) failed. Please check the errors above.")
        return False

def run_specific_test(test_name):
    """Run a specific test by name"""
    print(f"🧪 Running {test_name} test...")
    
    if test_name == "system":
        from tests.test_system import test_agents
        test_agents()
    elif test_name == "feedback":
        from tests.test_feedback_agent import test_feedback_agent
        test_feedback_agent()
    elif test_name == "icd":
        from tests.test_icd_mapper import test_icd_mapper
        test_icd_mapper()
    elif test_name == "performance":
        from tests.focused_performance_test import main as run_performance_test
        run_performance_test()
    elif test_name == "performance-full":
        from tests.performance_test import main as run_full_performance_test
        run_full_performance_test()
    elif test_name == "evaluation":
        from tests.test_evaluation_simple import main as run_evaluation_test
        run_evaluation_test()
    else:
        print(f"❌ Unknown test: {test_name}")
        print("Available tests: system, feedback, icd, performance, performance-full, evaluation")
        return False
    
    print(f"✅ {test_name} test completed")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1].lower()
        success = run_specific_test(test_name)
    else:
        # Run all tests
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
