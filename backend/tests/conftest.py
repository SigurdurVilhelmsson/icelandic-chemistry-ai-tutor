"""
Pytest configuration and shared fixtures for Icelandic Chemistry AI Tutor tests.

This module provides reusable fixtures, mocks, and test utilities for all test modules.
All fixtures defined here are automatically available to all test files.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient


# ============================================================================
# Path Configuration
# ============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Return the fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory) -> Path:
    """Create a temporary directory for test data."""
    return tmp_path_factory.mktemp("test_data")


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def sample_content(fixtures_dir: Path) -> Dict[str, Any]:
    """Load sample Icelandic chemistry content for testing."""
    content_file = fixtures_dir / "sample_content.json"
    with open(content_file, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope="session")
def expected_responses(fixtures_dir: Path) -> Dict[str, Any]:
    """Load expected responses for regression testing."""
    responses_file = fixtures_dir / "expected_responses.json"
    with open(responses_file, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def sample_chunks(sample_content: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return list of sample content chunks."""
    return sample_content["chunks"]


@pytest.fixture
def sample_chunk(sample_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return a single sample chunk."""
    return sample_chunks[0]


# ============================================================================
# Mock Embedding Fixtures
# ============================================================================

@pytest.fixture
def mock_embedding_dimension() -> int:
    """Return the dimension of mock embeddings (OpenAI text-embedding-3-small)."""
    return 1536


@pytest.fixture
def mock_embedding(mock_embedding_dimension: int) -> List[float]:
    """Generate a single mock embedding vector."""
    # Use fixed seed for reproducibility
    np.random.seed(42)
    embedding = np.random.rand(mock_embedding_dimension).tolist()
    return embedding


@pytest.fixture
def mock_embeddings(mock_embedding_dimension: int, sample_chunks: List[Dict[str, Any]]) -> Dict[str, List[float]]:
    """Generate mock embeddings for all sample chunks."""
    np.random.seed(42)
    embeddings = {}
    for chunk in sample_chunks:
        chunk_id = chunk["id"]
        embeddings[chunk_id] = np.random.rand(mock_embedding_dimension).tolist()
    return embeddings


@pytest.fixture
def mock_openai_embedding_response(mock_embedding: List[float]):
    """Mock OpenAI embedding API response."""
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": mock_embedding,
                "index": 0
            }
        ],
        "model": "text-embedding-3-small",
        "usage": {
            "prompt_tokens": 8,
            "total_tokens": 8
        }
    }


@pytest.fixture
def mock_openai_client(mock_openai_embedding_response):
    """Mock OpenAI client for embedding generation."""
    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = Mock(
        data=[Mock(embedding=mock_openai_embedding_response["data"][0]["embedding"])]
    )
    return mock_client


# ============================================================================
# Mock LLM (Claude) Fixtures
# ============================================================================

@pytest.fixture
def mock_claude_response() -> str:
    """Mock Claude API response for a typical chemistry question."""
    return """Atóm er minnsta eining efnis sem getur tekið þátt í efnahvörfum.
Atóm samanstendur af kjarna sem inniheldur róteindir (jákvæðar) og nifteindir (hlutlausar),
og rafeindaskýi þar sem neikvæðar rafeindir hringsólast um kjarnann í ákveðnum orkustigum."""


@pytest.fixture
def mock_claude_response_with_citations() -> Dict[str, Any]:
    """Mock complete Claude response with citations."""
    return {
        "answer": """Atóm er minnsta eining efnis sem getur tekið þátt í efnahvörfum.
Atóm samanstendur af kjarna og rafeindaskýi. Kjarninn inniheldur róteindir og nifteindir,
sem báðar eru mun þyngri en rafeindir.""",
        "citations": [
            {
                "chapter_number": 1,
                "section_number": "1.1",
                "chapter_title": "Efnafræðileg uppbygging efna",
                "section_title": "Atóm og atómgerð",
                "chunk_text": "Atóm er minnsta eining efnis..."
            }
        ],
        "confidence": 0.95,
        "timestamp": "2025-01-15T10:30:00Z"
    }


@pytest.fixture
def mock_claude_client(mock_claude_response: str):
    """Mock Claude client for LLM generation."""
    with patch('anthropic.Anthropic') as mock_anthropic:
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=mock_claude_response)]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client
        yield mock_client


# ============================================================================
# Vector Store Fixtures
# ============================================================================

@pytest.fixture
def temp_chroma_db(tmp_path) -> Path:
    """Create a temporary ChromaDB directory."""
    db_path = tmp_path / "chroma_test_db"
    db_path.mkdir(exist_ok=True)
    return db_path


@pytest.fixture
def mock_vector_store(mock_embeddings: Dict[str, List[float]]):
    """Mock vector store with pre-populated data."""
    mock_store = MagicMock()

    def mock_search(query_embedding: List[float], n_results: int = 5, **kwargs):
        """Mock search that returns relevant chunks."""
        # Simulate similarity search by returning first n_results chunks
        chunk_ids = list(mock_embeddings.keys())[:n_results]
        return {
            "ids": [chunk_ids],
            "documents": [[f"Mock content for {cid}" for cid in chunk_ids]],
            "metadatas": [[{"chapter_number": 1, "section_number": "1.1"} for _ in chunk_ids]],
            "distances": [[0.1 * i for i in range(len(chunk_ids))]]
        }

    mock_store.search.side_effect = mock_search
    mock_store.get_stats.return_value = {
        "total_chunks": len(mock_embeddings),
        "collections": ["icelandic_chemistry"]
    }

    return mock_store


# ============================================================================
# FastAPI Test Client Fixtures
# ============================================================================

@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    # Import here to avoid circular imports
    from src.main import app
    return TestClient(app)


@pytest.fixture
def mock_app_dependencies():
    """Mock all external dependencies for FastAPI app."""
    with patch('src.main.rag_pipeline') as mock_rag, \
         patch('src.main.vector_store') as mock_vs, \
         patch('src.main.llm_client') as mock_llm:

        # Configure mock RAG pipeline
        mock_rag.ask.return_value = {
            "answer": "Mock answer",
            "citations": [],
            "confidence": 0.9
        }
        mock_rag.health_check.return_value = {"status": "healthy"}

        yield {
            "rag_pipeline": mock_rag,
            "vector_store": mock_vs,
            "llm_client": mock_llm
        }


# ============================================================================
# Content Processing Fixtures
# ============================================================================

@pytest.fixture
def sample_markdown_simple() -> str:
    """Simple markdown content for testing."""
    return """# Kafli 1: Atómfræði

## 1.1 Hvað er atóm?

Atóm er minnsta eining efnis. Það samanstendur af kjarna og rafeindum.

## 1.2 Atómgerð

Kjarninn inniheldur róteindir og nifteindir.
"""


@pytest.fixture
def sample_markdown_complex() -> str:
    """Complex markdown with equations, lists, and special characters."""
    return """# Kafli 2: Efnafræði

## 2.1 Efnahvörf

Efnahvarf er ferli þar sem efni breytast:

- Hvarfefni → Afurðir
- Orkubreyting á sér stað
- Massavarðveisla gildir

### 2.1.1 Efnajafna

Almenn efnajafna:

```
aA + bB → cC + dD
```

Þar sem a, b, c, d eru stuðlar.

## 2.2 Sérstakir stafir

Íslenskir stafir: á, é, í, ó, ú, ý, þ, æ, ö, ð
"""


@pytest.fixture
def sample_markdown_file(tmp_path, sample_markdown_simple: str) -> Path:
    """Create a temporary markdown file."""
    md_file = tmp_path / "test_chapter.md"
    md_file.write_text(sample_markdown_simple, encoding='utf-8')
    return md_file


# ============================================================================
# Icelandic Language Test Data
# ============================================================================

@pytest.fixture
def icelandic_test_cases() -> List[Dict[str, str]]:
    """Test cases for Icelandic character handling."""
    return [
        {
            "input": "Hvað er atóm?",
            "expected_chars": ["á", "ó"],
            "description": "Basic question with accented characters"
        },
        {
            "input": "Útskýrðu efnatengi með þ, æ og ö",
            "expected_chars": ["Ú", "ý", "þ", "æ", "ö"],
            "description": "Complex query with multiple special characters"
        },
        {
            "input": "Rafeindaskipan ítalsks frumefnis",
            "expected_chars": ["í"],
            "description": "Scientific terminology"
        },
        {
            "input": "Hvað þýðir pH-gildi?",
            "expected_chars": ["þ", "í"],
            "description": "Mixed Icelandic and abbreviations"
        }
    ]


# ============================================================================
# Error Simulation Fixtures
# ============================================================================

@pytest.fixture
def mock_api_timeout():
    """Simulate API timeout error."""
    def timeout_error(*args, **kwargs):
        import time
        time.sleep(0.1)  # Small delay to simulate timeout
        raise TimeoutError("API request timed out")
    return timeout_error


@pytest.fixture
def mock_api_error():
    """Simulate API error."""
    def api_error(*args, **kwargs):
        raise Exception("API Error: Service unavailable")
    return api_error


@pytest.fixture
def mock_db_error():
    """Simulate database error."""
    def db_error(*args, **kwargs):
        raise Exception("Database Error: Connection failed")
    return db_error


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def performance_timer():
    """Context manager for measuring execution time."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.elapsed = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, *args):
            self.end_time = time.time()
            self.elapsed = self.end_time - self.start_time

    return Timer


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_db(temp_chroma_db):
    """Automatically cleanup test database after each test."""
    yield
    # Cleanup code runs after test
    if temp_chroma_db.exists():
        import shutil
        shutil.rmtree(temp_chroma_db, ignore_errors=True)


@pytest.fixture(autouse=True)
def reset_environment_variables():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


# ============================================================================
# Pytest Hooks (Test Execution Control)
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (> 1 second)"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location/name."""
    for item in items:
        # Mark tests in test_integration.py as integration tests
        if "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark tests with "slow" in name as slow
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)

        # Mark tests in e2e directory
        if "/e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


# ============================================================================
# Utility Functions for Tests
# ============================================================================

@pytest.fixture
def assert_icelandic_preserved():
    """Helper to assert Icelandic characters are preserved."""
    def _assert(text: str):
        icelandic_chars = ['á', 'é', 'í', 'ó', 'ú', 'ý', 'þ', 'æ', 'ö', 'ð',
                          'Á', 'É', 'Í', 'Ó', 'Ú', 'Ý', 'Þ', 'Æ', 'Ö', 'Ð']
        # Check that text is properly encoded
        assert isinstance(text, str), "Text must be string"
        # Try encoding/decoding to ensure no corruption
        try:
            text.encode('utf-8').decode('utf-8')
        except UnicodeError:
            pytest.fail("Icelandic characters not properly encoded")
    return _assert


@pytest.fixture
def validate_citation_format():
    """Helper to validate citation format."""
    def _validate(citation: Dict[str, Any]):
        required_fields = ["chapter_number", "section_number", "chapter_title", "section_title"]
        for field in required_fields:
            assert field in citation, f"Citation missing required field: {field}"
        assert isinstance(citation["chapter_number"], int), "Chapter number must be integer"
        assert isinstance(citation["section_number"], str), "Section number must be string"
    return _validate


# ============================================================================
# Environment Setup
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ["TESTING"] = "true"
    os.environ["OPENAI_API_KEY"] = "test-key-mock"
    os.environ["ANTHROPIC_API_KEY"] = "test-key-mock"
    os.environ["CHROMA_DB_PATH"] = "/tmp/test_chroma_db"
    yield
    # Cleanup
    for key in ["TESTING", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "CHROMA_DB_PATH"]:
        os.environ.pop(key, None)
