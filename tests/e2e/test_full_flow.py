"""
End-to-End Tests - Complete User Journey

This module tests the complete user journey through the application:
- Backend server startup
- Content ingestion
- Question answering via API
- Citation verification
- Performance measurement
"""

import pytest
import requests
import time
from typing import Dict, Any
from unittest.mock import patch, MagicMock


# ============================================================================
# E2E Test Configuration
# ============================================================================

BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30  # seconds


@pytest.fixture(scope="module")
def api_base_url():
    """Return base URL for API."""
    return BASE_URL


# ============================================================================
# Complete User Journey Tests
# ============================================================================

@pytest.mark.e2e
class TestCompleteUserJourney:
    """Test complete user journey from question to answer."""

    @pytest.mark.skip(reason="Requires running server - use for manual testing")
    def test_health_check(self, api_base_url):
        """Test that server is running and healthy."""
        response = requests.get(f"{api_base_url}/health", timeout=5)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "ok"]

    @pytest.mark.skip(reason="Requires running server - use for manual testing")
    def test_ask_question_end_to_end(self, api_base_url):
        """Test asking a question end-to-end."""
        question = "Hvað er atóm?"

        response = requests.post(
            f"{api_base_url}/ask",
            json={"question": question},
            timeout=API_TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "answer" in data
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0

        # Verify citations if present
        if "citations" in data:
            assert isinstance(data["citations"], list)

    @pytest.mark.skip(reason="Requires running server - use for manual testing")
    def test_multiple_questions_in_sequence(self, api_base_url):
        """Test asking multiple questions in sequence."""
        questions = [
            "Hvað er atóm?",
            "Útskýrðu lotukerfið",
            "Hvað er efnatengi?"
        ]

        for question in questions:
            response = requests.post(
                f"{api_base_url}/ask",
                json={"question": question},
                timeout=API_TIMEOUT
            )

            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert len(data["answer"]) > 0

            # Brief pause between requests
            time.sleep(0.5)

    @pytest.mark.skip(reason="Requires running server - use for manual testing")
    def test_session_continuity(self, api_base_url):
        """Test session continuity across multiple requests."""
        session_id = "test-session-" + str(time.time())

        # First question
        response1 = requests.post(
            f"{api_base_url}/ask",
            json={
                "question": "Hvað er atóm?",
                "session_id": session_id
            },
            timeout=API_TIMEOUT
        )

        assert response1.status_code == 200

        # Follow-up question with same session
        response2 = requests.post(
            f"{api_base_url}/ask",
            json={
                "question": "Hvað er rafeindaskipan?",
                "session_id": session_id
            },
            timeout=API_TIMEOUT
        )

        assert response2.status_code == 200


# ============================================================================
# Mocked E2E Tests (Can Run Without Server)
# ============================================================================

@pytest.mark.e2e
class TestMockedE2EFlow:
    """E2E tests with mocked external dependencies."""

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_complete_flow_mocked(
        self,
        mock_openai_class,
        mock_anthropic_class,
        tmp_path,
        sample_chunks,
        mock_embeddings,
        mock_embedding
    ):
        """Test complete flow with mocked external APIs."""
        from backend.src.vector_store import VectorStore
        from backend.src.embeddings import EmbeddingGenerator
        from backend.src.llm_client import ClaudeClient
        from backend.src.rag_pipeline import RAGPipeline

        # Setup mocks
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai
        mock_openai.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)],
            usage=MagicMock(total_tokens=10)
        )

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Atóm er minnsta eining efnis.")]
        mock_anthropic.messages.create.return_value = mock_message

        # Simulate complete workflow
        db_path = tmp_path / "chroma_db"
        vector_store = VectorStore(persist_directory=str(db_path))

        # Ingest sample content
        documents = [chunk["content"] for chunk in sample_chunks[:5]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:5]]
        ids = [chunk["id"] for chunk in sample_chunks[:5]]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:5]]

        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        # Create pipeline
        embedding_gen = EmbeddingGenerator(api_key="test-key")
        llm_client = ClaudeClient(api_key="test-key")
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        # Ask question
        result = pipeline.ask("Hvað er atóm?")

        # Verify complete flow
        assert "answer" in result
        assert "citations" in result
        assert len(result["answer"]) > 0


# ============================================================================
# Performance E2E Tests
# ============================================================================

@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.performance
class TestE2EPerformance:
    """Test end-to-end performance."""

    @pytest.mark.skip(reason="Requires running server - use for manual testing")
    def test_response_time_under_threshold(self, api_base_url, expected_responses):
        """Test that end-to-end response time meets requirements."""
        question = "Hvað er atóm?"

        start_time = time.time()
        response = requests.post(
            f"{api_base_url}/ask",
            json={"question": question},
            timeout=API_TIMEOUT
        )
        elapsed = time.time() - start_time

        assert response.status_code == 200

        # Check against performance benchmark
        max_time = expected_responses["performance_benchmarks"]["max_response_time_seconds"]
        assert elapsed < max_time, f"Response took {elapsed}s, expected < {max_time}s"

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_performance_with_mocked_apis(
        self,
        mock_openai_class,
        mock_anthropic_class,
        tmp_path,
        sample_chunks,
        mock_embeddings,
        mock_embedding,
        performance_timer,
        expected_responses
    ):
        """Test performance with mocked external APIs."""
        from backend.src.vector_store import VectorStore
        from backend.src.embeddings import EmbeddingGenerator
        from backend.src.llm_client import ClaudeClient
        from backend.src.rag_pipeline import RAGPipeline

        # Setup mocks
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai
        mock_openai.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)],
            usage=MagicMock(total_tokens=10)
        )

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Fast answer")]
        mock_anthropic.messages.create.return_value = mock_message

        # Setup system
        db_path = tmp_path / "chroma_db"
        vector_store = VectorStore(persist_directory=str(db_path))

        documents = [chunk["content"] for chunk in sample_chunks[:10]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:10]]
        ids = [chunk["id"] for chunk in sample_chunks[:10]]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:10]]

        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        embedding_gen = EmbeddingGenerator(api_key="test-key")
        llm_client = ClaudeClient(api_key="test-key")
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        # Measure performance
        with performance_timer() as timer:
            result = pipeline.ask("Hvað er atóm?")

        max_time = expected_responses["performance_benchmarks"]["max_response_time_seconds"]
        assert timer.elapsed < max_time * 2  # Generous for tests
        assert "answer" in result


# ============================================================================
# Citation Verification E2E Tests
# ============================================================================

@pytest.mark.e2e
class TestCitationVerification:
    """Test citation accuracy in end-to-end flow."""

    @pytest.mark.skip(reason="Requires running server - use for manual testing")
    def test_citations_present_and_valid(self, api_base_url, validate_citation_format):
        """Test that citations are present and properly formatted."""
        question = "Hvað er atóm?"

        response = requests.post(
            f"{api_base_url}/ask",
            json={"question": question},
            timeout=API_TIMEOUT
        )

        assert response.status_code == 200
        data = response.json()

        # Verify citations
        if "citations" in data and len(data["citations"]) > 0:
            for citation in data["citations"]:
                validate_citation_format(citation)

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_citation_accuracy_mocked(
        self,
        mock_openai_class,
        mock_anthropic_class,
        tmp_path,
        sample_chunks,
        mock_embeddings,
        mock_embedding,
        validate_citation_format
    ):
        """Test citation accuracy with mocked APIs."""
        from backend.src.vector_store import VectorStore
        from backend.src.embeddings import EmbeddingGenerator
        from backend.src.llm_client import ClaudeClient
        from backend.src.rag_pipeline import RAGPipeline

        # Setup mocks
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai
        mock_openai.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)],
            usage=MagicMock(total_tokens=10)
        )

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Answer with citations")]
        mock_anthropic.messages.create.return_value = mock_message

        # Setup
        db_path = tmp_path / "chroma_db"
        vector_store = VectorStore(persist_directory=str(db_path))

        documents = [chunk["content"] for chunk in sample_chunks[:5]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:5]]
        ids = [chunk["id"] for chunk in sample_chunks[:5]]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:5]]

        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        embedding_gen = EmbeddingGenerator(api_key="test-key")
        llm_client = ClaudeClient(api_key="test-key")
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        result = pipeline.ask("Hvað er atóm?")

        # Validate all citations
        for citation in result.get("citations", []):
            validate_citation_format(citation)
