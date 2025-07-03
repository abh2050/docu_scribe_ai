#!/usr/bin/env python3
"""
DocuScribe AI Test Launcher

Convenience script to run tests from the project root.

Usage:
    python run_tests.py           # Run all tests
    python run_tests.py system    # Run system integration tests
    python run_tests.py feedback  # Run feedback agent tests
    python run_tests.py icd       # Run ICD mapper tests
"""

import sys
from pathlib import Path

# Import the test runner from tests folder
sys.path.insert(0, str(Path(__file__).parent))

from tests.run_tests import run_all_tests, run_specific_test

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1].lower()
        success = run_specific_test(test_name)
    else:
        # Run all tests
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
