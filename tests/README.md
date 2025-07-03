# DocuScribe AI Tests

This folder contains comprehensive tests for the DocuScribe AI system.

## Test Files

### Core Test Files

- **`test_system.py`** - Complete system integration tests for all agents
- **`test_feedback_agent.py`** - Specific tests for FeedbackAgent with LLM support  
- **`test_icd_mapper.py`** - Tests for ICD-10 mapping functionality

### Performance Test Files

- **`focused_performance_test.py`** - Quick performance benchmarks for core components
- **`performance_test.py`** - Comprehensive performance analysis with detailed metrics

### Test Utilities

- **`run_tests.py`** - Test runner script to execute all or specific tests
- **`__init__.py`** - Makes this a proper Python package
- **`performance_results/`** - Directory containing performance test results

## Running Tests

### From Project Root

```bash
# Run all tests
python run_tests.py

# Run specific test suites
python run_tests.py system
python run_tests.py feedback  
python run_tests.py icd
python run_tests.py performance      # Quick performance test
python run_tests.py performance-full # Comprehensive performance test
```

### From Tests Folder

```bash
cd tests/

# Run all tests
python run_tests.py

# Run individual test files
python test_system.py
python test_feedback_agent.py
python test_icd_mapper.py
python focused_performance_test.py
python performance_test.py
```

### Using Python Module Syntax

```bash
# From project root
python -m tests.test_system
python -m tests.test_feedback_agent
python -m tests.test_icd_mapper
python -m tests.focused_performance_test
python -m tests.performance_test
```

## Test Coverage

### System Integration Tests (`test_system.py`)
- ✅ TranscriptionAgent: Text processing and cleaning
- ✅ ContextAgent: SOAP section analysis (LLM + rule-based)  
- ✅ ConceptAgent: Medical concept extraction (LLM + rule-based)
- ✅ ICDMapperAgent: ICD-10 code mapping
- ✅ ScribeAgent: SOAP note generation (LLM-powered)
- ✅ FormatterAgent: Output formatting
- ✅ FHIR formatting functionality

### FeedbackAgent Tests (`test_feedback_agent.py`) 
- ✅ Basic feedback processing with LLM support
- ✅ Positive feedback handling
- ✅ Feedback report generation
- ✅ LLM fallback to rule-based processing
- ✅ Hybrid analysis merging

### ICD Mapper Tests (`test_icd_mapper.py`)
- ✅ ICD-10 database loading (74,260+ codes)
- ✅ Medical concept to ICD code mapping
- ✅ Code validation and format checking
- ✅ Confidence scoring and categorization

## Expected Test Results

When all tests pass, you should see:
- **System Tests**: All 7 agents working correctly
- **FeedbackAgent**: Hybrid LLM + rule-based functionality
- **ICD Mapper**: 74,260+ codes loaded and mapping working
- **Overall**: 100% success rate

## Environment Requirements

Tests work in multiple configurations:
- ✅ **LLM Enabled**: Full hybrid LLM + rule-based functionality
- ✅ **LLM Disabled**: Complete rule-based fallback operation
- ✅ **No API Keys**: System degrades gracefully to rule-based only

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the project root
2. **Missing Data Files**: Ensure `data/` folder contains ICD-10 data
3. **LLM Failures**: Tests include fallback verification - this is expected behavior

### Test Failures

If tests fail:
1. Check the error messages for specific issues
2. Verify environment variables are set correctly  
3. Ensure all dependencies are installed
4. Check that data files are in the correct location

The test suite is designed to be robust and should pass even without LLM configuration.
