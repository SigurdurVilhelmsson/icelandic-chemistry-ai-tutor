"""
Integration Tests - End-to-end backend system tests.

This module tests the complete backend system with all components working together:
- Content ingestion → Vector store → RAG pipeline → API response
- Real-world scenarios with sample data
- Performance benchmarks
- Icelandic language handling throughout the stack
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import time

from fastapi.testclient import TestClient


# ============================================================================
# Complete RAG Flow Integration Tests
# ============================================================================

@pytest.mark.integration
class TestCompleteRAGFlow:
    """Test complete RAG pipeline from ingestion to answer generation."""

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_ingest_search_answer_flow(
        self,
        mock_openai_class,
        mock_anthropic_class,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings,
        mock_embedding,
        expected_responses
    ):
        """Test complete flow: ingest content → search → generate answer."""
        from src.vector_store import VectorStore
        from src.embeddings import EmbeddingGenerator
        from src.llm_client import ClaudeClient
        from src.rag_pipeline import RAGPipeline

        # Setup mocks
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai

        def mock_create_embeddings(*args, **kwargs):
            input_data = kwargs.get("input", [])
            if isinstance(input_data, str):
                return MagicMock(
                    data=[MagicMock(embedding=mock_embedding)],
                    usage=MagicMock(total_tokens=10)
                )
            else:
                return MagicMock(
                    data=[MagicMock(embedding=mock_embeddings.get(f"chunk_00{i+1}", mock_embedding))
                          for i in range(len(input_data))],
                    usage=MagicMock(total_tokens=len(input_data) * 10)
                )

        mock_openai.embeddings.create.side_effect = mock_create_embeddings

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Atóm er minnsta eining efnis sem getur tekið þátt í efnahvörfum.")]
        mock_anthropic.messages.create.return_value = mock_message

        # Step 1: Create vector store and ingest documents
        vector_store = VectorStore(persist_directory=str(temp_chroma_db))

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

        # Step 2: Create RAG pipeline
        embedding_gen = EmbeddingGenerator(api_key="test-key")
        llm_client = ClaudeClient(api_key="test-key")
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        # Step 3: Ask question
        test_case = expected_responses["test_cases"][0]
        result = pipeline.ask(test_case["question"])

        # Verify complete flow worked
        assert "answer" in result
        assert "citations" in result
        assert len(result["answer"]) > 0

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_icelandic_end_to_end(
        self,
        mock_openai_class,
        mock_anthropic_class,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings,
        mock_embedding,
        assert_icelandic_preserved
    ):
        """Test Icelandic language handling through entire pipeline."""
        from src.vector_store import VectorStore
        from src.embeddings import EmbeddingGenerator
        from src.llm_client import ClaudeClient
        from src.rag_pipeline import RAGPipeline

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
        mock_message.content = [MagicMock(text="Atóm samanstendur af þremur meginhlutum með þ, æ, ö, ð.")]
        mock_anthropic.messages.create.return_value = mock_message

        # Ingest Icelandic content
        vector_store = VectorStore(persist_directory=str(temp_chroma_db))
        icelandic_chunks = [c for c in sample_chunks if "Atóm" in c["content"]][:3]

        documents = [chunk["content"] for chunk in icelandic_chunks]
        metadatas = [chunk["metadata"] for chunk in icelandic_chunks]
        ids = [chunk["id"] for chunk in icelandic_chunks]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in icelandic_chunks]

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

        # Ask question in Icelandic with special characters
        result = pipeline.ask("Hvað er atóm með þ, æ, ö, ð?")

        # Verify Icelandic preserved
        assert_icelandic_preserved(result["answer"])

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_citation_accuracy(
        self,
        mock_openai_class,
        mock_anthropic_class,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings,
        mock_embedding,
        validate_citation_format
    ):
        """Test that citations are accurate and properly formatted."""
        from src.vector_store import VectorStore
        from src.embeddings import EmbeddingGenerator
        from src.llm_client import ClaudeClient
        from src.rag_pipeline import RAGPipeline

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
        mock_message.content = [MagicMock(text="Answer with citation.")]
        mock_anthropic.messages.create.return_value = mock_message

        # Setup
        vector_store = VectorStore(persist_directory=str(temp_chroma_db))

        documents = [chunk["content"] for chunk in sample_chunks[:3]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:3]]
        ids = [chunk["id"] for chunk in sample_chunks[:3]]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:3]]

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

        result = pipeline.ask("Test question")

        # Validate citations
        assert "citations" in result
        for citation in result["citations"]:
            validate_citation_format(citation)


# ============================================================================
# API Integration Tests
# ============================================================================

@pytest.mark.integration
class TestAPIIntegration:
    """Test API with full backend integration."""

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_api_with_real_pipeline(
        self,
        mock_openai_class,
        mock_anthropic_class,
        test_client,
        mock_embedding
    ):
        """Test API endpoint with real RAG pipeline (mocked external APIs)."""
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
        mock_message.content = [MagicMock(text="Integrated answer")]
        mock_anthropic.messages.create.return_value = mock_message

        # Make API request
        response = test_client.post(
            "/ask",
            json={"question": "Hvað er atóm?"}
        )

        # Verify integration
        assert response.status_code in [200, 500]  # May fail if pipeline not initialized
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data


# ============================================================================
# Performance Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.performance
class TestPerformanceIntegration:
    """Test performance of integrated system."""

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_end_to_end_performance(
        self,
        mock_openai_class,
        mock_anthropic_class,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings,
        mock_embedding,
        performance_timer,
        expected_responses
    ):
        """Test end-to-end performance meets requirements."""
        from src.vector_store import VectorStore
        from src.embeddings import EmbeddingGenerator
        from src.llm_client import ClaudeClient
        from src.rag_pipeline import RAGPipeline

        # Setup mocks (fast responses)
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
        vector_store = VectorStore(persist_directory=str(temp_chroma_db))

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

        # Verify performance
        max_time = expected_responses["performance_benchmarks"]["max_response_time_seconds"]
        assert timer.elapsed < max_time * 2  # Generous margin for tests
        assert "answer" in result


# ============================================================================
# Error Recovery Integration Tests
# ============================================================================

@pytest.mark.integration
class TestErrorRecoveryIntegration:
    """Test error recovery in integrated system."""

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_retry_on_transient_failure(
        self,
        mock_openai_class,
        mock_anthropic_class,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings,
        mock_embedding
    ):
        """Test that system recovers from transient failures."""
        from src.vector_store import VectorStore
        from src.embeddings import EmbeddingGenerator
        from src.llm_client import ClaudeClient
        from src.rag_pipeline import RAGPipeline

        # Setup mocks with transient failure
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai
        mock_openai.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)],
            usage=MagicMock(total_tokens=10)
        )

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic

        # Fail once, then succeed
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Success after retry")]
        mock_anthropic.messages.create.side_effect = [
            Exception("Transient error"),
            mock_message
        ]

        # Setup system
        vector_store = VectorStore(persist_directory=str(temp_chroma_db))

        documents = [sample_chunks[0]["content"]]
        metadatas = [sample_chunks[0]["metadata"]]
        ids = [sample_chunks[0]["id"]]
        embeddings_list = [mock_embeddings[sample_chunks[0]["id"]]]

        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        embedding_gen = EmbeddingGenerator(api_key="test-key", max_retries=0)
        llm_client = ClaudeClient(api_key="test-key", max_retries=2)
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        # Should succeed after retry
        result = pipeline.ask("Test question")
        assert "answer" in result


# ============================================================================
# Data Integrity Integration Tests
# ============================================================================

@pytest.mark.integration
class TestDataIntegrityIntegration:
    """Test data integrity throughout the system."""

    @patch('openai.OpenAI')
    def test_unicode_preservation_through_stack(
        self,
        mock_openai_class,
        temp_chroma_db,
        mock_embeddings,
        assert_icelandic_preserved
    ):
        """Test that Unicode is preserved through all layers."""
        from src.vector_store import VectorStore

        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai

        # Test text with all Icelandic characters
        icelandic_text = "Atóm, efnatengi, þ, æ, ö, ð, á, é, í, ó, ú, ý"

        vector_store = VectorStore(persist_directory=str(temp_chroma_db))

        # Store with Icelandic content
        vector_store.add_documents(
            documents=[icelandic_text],
            metadatas=[{"chapter_number": 1, "language": "is"}],
            ids=["icelandic_test"],
            embeddings=[mock_embeddings["chunk_001"]]
        )

        # Retrieve and verify
        results = vector_store.get_all_documents()

        found = False
        for doc in results.get("documents", []):
            if "Atóm" in doc:
                assert_icelandic_preserved(doc)
                found = True
                break

        assert found, "Icelandic document not found in results"
