# Testing Infrastructure - Icelandic Chemistry AI Tutor

Comprehensive test suite for the Icelandic Chemistry AI Tutor application.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Coverage Reports](#coverage-reports)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## Overview

This test suite provides comprehensive coverage for:

- ✅ **Backend API** - FastAPI endpoints
- ✅ **RAG Pipeline** - Question answering logic
- ✅ **Vector Store** - ChromaDB operations
- ✅ **LLM Client** - Claude API integration (mocked)
- ✅ **Embeddings** - OpenAI embedding generation (mocked)
- ✅ **Content Processing** - Markdown parsing and chunking
- ✅ **Icelandic Language** - Unicode and character preservation
- ✅ **E2E Flows** - Complete user journeys
- ✅ **Integration** - Component interactions

### Test Statistics

- **Total Test Files**: 10+
- **Test Coverage Target**: >80%
- **Icelandic Character Tests**: ✓
- **Mocked External APIs**: ✓ (No API costs during testing)

## Test Structure

```
icelandic-chemistry-ai-tutor/
├── backend/
│   ├── tests/
│   │   ├── conftest.py                    # Shared fixtures and mocks
│   │   ├── fixtures/
│   │   │   ├── sample_content.json        # Test data
│   │   │   ├── mock_embeddings.json       # Mock embeddings
│   │   │   └── expected_responses.json    # Expected Q&A pairs
│   │   ├── test_rag_pipeline.py           # RAG system tests
│   │   ├── test_vector_store.py           # ChromaDB tests
│   │   ├── test_embeddings.py             # Embedding tests
│   │   ├── test_llm_client.py             # Claude API tests
│   │   ├── test_content_processor.py      # Content processing tests
│   │   ├── test_api_endpoints.py          # FastAPI endpoint tests
│   │   └── test_integration.py            # Integration tests
│   ├── pytest.ini                          # Pytest configuration
│   └── .coveragerc                         # Coverage configuration
├── tests/
│   └── e2e/
│       ├── test_full_flow.py              # Complete user journey tests
│       └── test_icelandic_handling.py     # Icelandic language tests
└── scripts/
    ├── run_all_tests.sh                    # Run complete test suite
    └── test_coverage.sh                    # Generate coverage reports
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run All Tests

```bash
# From project root
./scripts/run_all_tests.sh
```

### 3. View Coverage

```bash
./scripts/test_coverage.sh --open
```

## Running Tests

### Run All Tests

```bash
cd backend
pytest tests/
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/ -m unit

# Integration tests
pytest tests/ -m integration

# Icelandic language tests
pytest tests/ -m icelandic

# API tests
pytest tests/ -m api

# Database tests
pytest tests/ -m db
```

### Run Specific Test Files

```bash
# RAG pipeline tests
pytest tests/test_rag_pipeline.py

# Vector store tests
pytest tests/test_vector_store.py

# E2E tests
pytest tests/e2e/
```

### Run with Options

```bash
# Verbose output
pytest tests/ -v

# Show print statements
pytest tests/ -s

# Stop on first failure
pytest tests/ -x

# Run in parallel (faster)
pytest tests/ -n auto

# Skip slow tests
pytest tests/ -m "not slow"
```

## Test Categories

### Markers

Tests are organized using pytest markers:

- `unit` - Unit tests for individual components
- `integration` - Integration tests across multiple components
- `e2e` - End-to-end tests
- `slow` - Tests that take >1 second
- `api` - Tests that interact with external APIs (mocked)
- `db` - Tests that interact with the database
- `icelandic` - Tests for Icelandic language handling
- `performance` - Performance and benchmarking tests

### Examples

```bash
# Run only fast unit tests
pytest tests/ -m "unit and not slow"

# Run integration and E2E tests
pytest tests/ -m "integration or e2e"

# Run all Icelandic tests
pytest tests/ -m icelandic
```

## Coverage Reports

### Generate Coverage Report

```bash
./scripts/test_coverage.sh
```

### Options

```bash
# Set coverage threshold
./scripts/test_coverage.sh --threshold 85

# Open HTML report in browser
./scripts/test_coverage.sh --open

# Check coverage without failing
./scripts/test_coverage.sh --check
```

### Coverage Outputs

1. **HTML Report**: `backend/htmlcov/index.html` - Interactive browseable report
2. **Terminal Summary**: Shows coverage % and missing lines
3. **XML Report**: `backend/coverage.xml` - For CI/CD integration
4. **JSON Report**: `backend/coverage.json` - For programmatic access

### Coverage Thresholds

- **Overall Target**: 80%
- **Critical Modules**: 90%+
  - RAG Pipeline
  - Vector Store
  - LLM Client
  - API Endpoints

## Writing Tests

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
class TestMyComponent:
    """Test description."""

    def test_basic_functionality(self, sample_fixture):
        """Test what this does."""
        # Arrange
        component = MyComponent()

        # Act
        result = component.do_something()

        # Assert
        assert result == expected_value
```

### Using Fixtures

Fixtures are defined in `conftest.py` and automatically available:

```python
def test_with_fixtures(
    sample_chunks,           # Sample Icelandic content
    mock_embedding,          # Mock embedding vector
    mock_claude_client,      # Mock Claude API client
    assert_icelandic_preserved  # Helper to check Icelandic chars
):
    """Example using fixtures."""
    # Use fixtures in your test
    pass
```

### Mocking External APIs

```python
@patch('openai.OpenAI')
@patch('anthropic.Anthropic')
def test_with_mocked_apis(
    mock_anthropic_class,
    mock_openai_class,
    mock_embedding
):
    """Test without calling real APIs."""
    # Setup mocks
    mock_openai = MagicMock()
    mock_openai_class.return_value = mock_openai
    mock_openai.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=mock_embedding)]
    )

    # Test your code
    # ...
```

### Testing Icelandic Content

```python
def test_icelandic_preservation(assert_icelandic_preserved):
    """Test that Icelandic characters are preserved."""
    text = "Atóm með þ, æ, ö, ð"

    # Process text...
    result = process(text)

    # Verify Icelandic characters preserved
    assert_icelandic_preserved(result)
```

## Performance Testing

### Running Performance Tests

```bash
# Run only performance tests
pytest tests/ -m performance

# Include performance in regular run
pytest tests/
```

### Performance Benchmarks

From `expected_responses.json`:

- **Max Response Time**: 3.0 seconds
- **Max Embedding Time**: 0.5 seconds
- **Max LLM Time**: 2.0 seconds
- **Max Vector Search Time**: 0.3 seconds

### Example Performance Test

```python
@pytest.mark.performance
def test_response_time(performance_timer, expected_responses):
    """Test that responses meet time requirements."""
    with performance_timer() as timer:
        result = pipeline.ask("Test question")

    max_time = expected_responses["performance_benchmarks"]["max_response_time_seconds"]
    assert timer.elapsed < max_time
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests with coverage
        run: |
          cd backend
          pytest tests/ --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          files: ./backend/coverage.xml
```

### GitLab CI Example

```yaml
test:
  stage: test
  image: python:3.11
  script:
    - cd backend
    - pip install -r requirements.txt
    - pytest tests/ --cov=src --cov-report=xml --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: backend/coverage.xml
```

## Test Configuration

### pytest.ini

Key configurations:

```ini
[pytest]
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
addopts =
    -v
    --cov=src
    --cov-report=html
    --tb=short
```

### .coveragerc

Coverage settings:

```ini
[run]
source = src
branch = True

[report]
fail_under = 80
show_missing = True
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Make sure you're in the backend directory
cd backend
pytest tests/
```

#### 2. Missing Dependencies

```bash
# Reinstall requirements
pip install -r requirements.txt
```

#### 3. ChromaDB Lock Issues

```bash
# Clean up test databases
rm -rf /tmp/test_chroma_db
```

#### 4. API Key Warnings

Tests use mock APIs, so you don't need real API keys. The test environment sets dummy keys:

```python
os.environ["OPENAI_API_KEY"] = "test-key-mock"
os.environ["ANTHROPIC_API_KEY"] = "test-key-mock"
```

#### 5. Slow Tests

```bash
# Skip slow tests
pytest tests/ -m "not slow"

# Run in parallel
pytest tests/ -n auto
```

### Debug Mode

```bash
# Run with debug output
pytest tests/ -vvs --tb=long

# Drop into debugger on failure
pytest tests/ --pdb

# Show local variables
pytest tests/ -l
```

## Best Practices

### 1. **Always Mock External APIs**

```python
@patch('openai.OpenAI')
def test_feature(mock_openai):
    # Never call real APIs in tests
    pass
```

### 2. **Use Descriptive Test Names**

```python
# Good
def test_rag_pipeline_handles_empty_query_with_error():
    pass

# Bad
def test_error():
    pass
```

### 3. **Test One Thing Per Test**

```python
# Good - focused test
def test_embedding_generation_returns_correct_dimension():
    pass

def test_embedding_generation_handles_empty_text():
    pass

# Bad - testing multiple things
def test_embeddings():
    # Tests dimension, empty text, errors, etc.
    pass
```

### 4. **Use Fixtures for Setup**

```python
# Good - reusable fixture
@pytest.fixture
def configured_pipeline():
    return RAGPipeline(...)

def test_feature(configured_pipeline):
    result = configured_pipeline.ask("Test")
    assert result

# Bad - repeated setup
def test_feature():
    pipeline = RAGPipeline(...)  # Setup repeated in every test
    result = pipeline.ask("Test")
    assert result
```

### 5. **Test Icelandic Characters**

Always verify Icelandic character preservation:

```python
def test_feature(assert_icelandic_preserved):
    result = process_icelandic_text("Atóm með þ, æ, ö")
    assert_icelandic_preserved(result)
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Icelandic Character Reference](https://en.wikipedia.org/wiki/Icelandic_orthography)

## Contributing

When adding new features:

1. ✅ Write tests first (TDD)
2. ✅ Ensure >80% coverage
3. ✅ Test Icelandic character handling
4. ✅ Mock all external APIs
5. ✅ Add appropriate markers
6. ✅ Update this documentation

## License

Same as project license.
