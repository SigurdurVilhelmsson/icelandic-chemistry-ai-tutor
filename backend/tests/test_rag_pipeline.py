"""
Tests for RAG Pipeline - Core question answering functionality.

This module tests the complete RAG (Retrieval-Augmented Generation) pipeline
including vector search, context formatting, LLM generation, and citation extraction.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, List, Any

# Import modules to test
from src.rag_pipeline import RAGPipeline
from src.vector_store import VectorStore
from src.llm_client import ClaudeClient
from src.embeddings import EmbeddingGenerator


# ============================================================================
# RAG Pipeline Initialization Tests
# ============================================================================

@pytest.mark.unit
class TestRAGPipelineInitialization:
    """Test RAG pipeline initialization and configuration."""

    def test_pipeline_creation(self, mock_vector_store, mock_claude_client, mock_openai_client):
        """Test that RAG pipeline can be created with dependencies."""
        with patch('src.rag_pipeline.VectorStore', return_value=mock_vector_store), \
             patch('src.rag_pipeline.ClaudeClient', return_value=mock_claude_client), \
             patch('src.rag_pipeline.EmbeddingGenerator', return_value=mock_openai_client):

            pipeline = RAGPipeline(
                vector_store=mock_vector_store,
                llm_client=mock_claude_client,
                embedding_generator=mock_openai_client
            )

            assert pipeline is not None
            assert pipeline.vector_store == mock_vector_store
            assert pipeline.llm_client == mock_claude_client
            assert pipeline.embedding_generator == mock_openai_client

    def test_pipeline_default_config(self, mock_vector_store, mock_claude_client, mock_openai_client):
        """Test default configuration values."""
        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            llm_client=mock_claude_client,
            embedding_generator=mock_openai_client
        )

        # Verify default configuration
        assert pipeline.top_k >= 3  # At least 3 chunks retrieved
        assert pipeline.max_context_chunks > 0


# ============================================================================
# RAG Pipeline Question Answering Tests
# ============================================================================

@pytest.mark.unit
class TestRAGPipelineQuestionAnswering:
    """Test the core question answering functionality."""

    @patch('src.embeddings.EmbeddingGenerator')
    @patch('src.llm_client.ClaudeClient')
    @patch('src.vector_store.VectorStore')
    def test_ask_simple_question(
        self,
        mock_vs_class,
        mock_llm_class,
        mock_emb_class,
        mock_embedding,
        sample_chunks
    ):
        """Test asking a simple question and getting an answer."""
        # Setup mocks
        mock_vs = MagicMock()
        mock_llm = MagicMock()
        mock_emb = MagicMock()

        mock_vs_class.return_value = mock_vs
        mock_llm_class.return_value = mock_llm
        mock_emb_class.return_value = mock_emb

        # Mock embedding generation
        mock_emb.generate_embedding.return_value = mock_embedding

        # Mock vector search results
        mock_vs.search.return_value = {
            "ids": [[sample_chunks[0]["id"]]],
            "documents": [[sample_chunks[0]["content"]]],
            "metadatas": [[sample_chunks[0]["metadata"]]],
            "distances": [[0.15]]
        }

        # Mock LLM response
        mock_llm.generate_answer.return_value = {
            "answer": "Atóm er minnsta eining efnis.",
            "citations": [sample_chunks[0]["metadata"]]
        }

        # Create pipeline and ask question
        pipeline = RAGPipeline(
            vector_store=mock_vs,
            llm_client=mock_llm,
            embedding_generator=mock_emb
        )

        result = pipeline.ask("Hvað er atóm?")

        # Verify result structure
        assert "answer" in result
        assert "citations" in result
        assert isinstance(result["answer"], str)
        assert isinstance(result["citations"], list)
        assert len(result["answer"]) > 0

        # Verify methods were called
        mock_emb.generate_embedding.assert_called_once()
        mock_vs.search.assert_called_once()
        mock_llm.generate_answer.assert_called_once()

    @patch('src.embeddings.EmbeddingGenerator')
    @patch('src.llm_client.ClaudeClient')
    @patch('src.vector_store.VectorStore')
    def test_ask_with_icelandic_characters(
        self,
        mock_vs_class,
        mock_llm_class,
        mock_emb_class,
        mock_embedding,
        assert_icelandic_preserved
    ):
        """Test that Icelandic characters are preserved throughout pipeline."""
        # Setup mocks
        mock_vs = MagicMock()
        mock_llm = MagicMock()
        mock_emb = MagicMock()

        mock_vs_class.return_value = mock_vs
        mock_llm_class.return_value = mock_llm
        mock_emb_class.return_value = mock_emb

        mock_emb.generate_embedding.return_value = mock_embedding
        mock_vs.search.return_value = {
            "ids": [["chunk_001"]],
            "documents": [["Atóm er minnsta eining efnis með þ, æ, ö, ð."]],
            "metadatas": [[{"chapter_number": 1, "section_number": "1.1"}]],
            "distances": [[0.1]]
        }

        mock_llm.generate_answer.return_value = {
            "answer": "Atóm samanstendur af þremur meginhlutum: kjarna með róteindir og nifteindir, og rafeindaskýi með öllum rafeindunum.",
            "citations": []
        }

        pipeline = RAGPipeline(
            vector_store=mock_vs,
            llm_client=mock_llm,
            embedding_generator=mock_emb
        )

        question = "Hvað er atóm með þ, æ, ö, ð?"
        result = pipeline.ask(question)

        # Verify Icelandic characters preserved in answer
        assert_icelandic_preserved(result["answer"])
        assert "þ" in result["answer"] or "ð" in result["answer"]  # At least some Icelandic chars

    def test_ask_empty_query(self, mock_vector_store, mock_claude_client, mock_openai_client):
        """Test error handling for empty query."""
        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            llm_client=mock_claude_client,
            embedding_generator=mock_openai_client
        )

        with pytest.raises(ValueError, match="Query cannot be empty"):
            pipeline.ask("")

    def test_ask_very_long_query(
        self,
        mock_vector_store,
        mock_claude_client,
        mock_openai_client,
        mock_embedding
    ):
        """Test handling of very long queries."""
        mock_openai_client.generate_embedding.return_value = mock_embedding
        mock_vector_store.search.return_value = {
            "ids": [["chunk_001"]],
            "documents": [["Mock content"]],
            "metadatas": [[{"chapter_number": 1}]],
            "distances": [[0.1]]
        }
        mock_claude_client.generate_answer.return_value = {
            "answer": "This query was very long.",
            "citations": []
        }

        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            llm_client=mock_claude_client,
            embedding_generator=mock_openai_client
        )

        # Create a very long query (500+ words)
        long_query = " ".join(["Hvað er atóm?"] * 100)

        result = pipeline.ask(long_query)

        # Should handle gracefully (truncate or process)
        assert "answer" in result
        assert isinstance(result["answer"], str)


# ============================================================================
# Citation Generation Tests
# ============================================================================

@pytest.mark.unit
class TestRAGPipelineCitations:
    """Test citation extraction and formatting."""

    @patch('src.embeddings.EmbeddingGenerator')
    @patch('src.llm_client.ClaudeClient')
    @patch('src.vector_store.VectorStore')
    def test_citations_included_in_response(
        self,
        mock_vs_class,
        mock_llm_class,
        mock_emb_class,
        mock_embedding,
        sample_chunks
    ):
        """Test that citations are properly included in response."""
        mock_vs = MagicMock()
        mock_llm = MagicMock()
        mock_emb = MagicMock()

        mock_vs_class.return_value = mock_vs
        mock_llm_class.return_value = mock_llm
        mock_emb_class.return_value = mock_emb

        mock_emb.generate_embedding.return_value = mock_embedding
        mock_vs.search.return_value = {
            "ids": [[sample_chunks[0]["id"], sample_chunks[1]["id"]]],
            "documents": [[sample_chunks[0]["content"], sample_chunks[1]["content"]]],
            "metadatas": [[sample_chunks[0]["metadata"], sample_chunks[1]["metadata"]]],
            "distances": [[0.1, 0.2]]
        }

        mock_llm.generate_answer.return_value = {
            "answer": "Test answer",
            "citations": [sample_chunks[0]["metadata"], sample_chunks[1]["metadata"]]
        }

        pipeline = RAGPipeline(
            vector_store=mock_vs,
            llm_client=mock_llm,
            embedding_generator=mock_emb
        )

        result = pipeline.ask("Test question")

        # Verify citations structure
        assert "citations" in result
        assert len(result["citations"]) >= 1
        assert isinstance(result["citations"], list)

        # Verify citation format
        citation = result["citations"][0]
        assert "chapter_number" in citation
        assert "section_number" in citation

    def test_citation_format_validation(
        self,
        mock_vector_store,
        mock_claude_client,
        mock_openai_client,
        mock_embedding,
        sample_chunk,
        validate_citation_format
    ):
        """Test that citations have proper format."""
        mock_openai_client.generate_embedding.return_value = mock_embedding
        mock_vector_store.search.return_value = {
            "ids": [[sample_chunk["id"]]],
            "documents": [[sample_chunk["content"]]],
            "metadatas": [[sample_chunk["metadata"]]],
            "distances": [[0.1]]
        }

        mock_claude_client.generate_answer.return_value = {
            "answer": "Test answer",
            "citations": [sample_chunk["metadata"]]
        }

        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            llm_client=mock_claude_client,
            embedding_generator=mock_openai_client
        )

        result = pipeline.ask("Test question")

        # Validate each citation
        for citation in result["citations"]:
            validate_citation_format(citation)


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.unit
class TestRAGPipelineErrorHandling:
    """Test error handling in RAG pipeline."""

    def test_vector_store_failure(
        self,
        mock_vector_store,
        mock_claude_client,
        mock_openai_client,
        mock_embedding,
        mock_db_error
    ):
        """Test handling of vector store failures."""
        mock_openai_client.generate_embedding.return_value = mock_embedding
        mock_vector_store.search.side_effect = mock_db_error

        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            llm_client=mock_claude_client,
            embedding_generator=mock_openai_client
        )

        with pytest.raises(Exception, match="Database Error"):
            pipeline.ask("Test question")

    def test_llm_api_failure(
        self,
        mock_vector_store,
        mock_claude_client,
        mock_openai_client,
        mock_embedding,
        mock_api_error
    ):
        """Test handling of LLM API failures."""
        mock_openai_client.generate_embedding.return_value = mock_embedding
        mock_vector_store.search.return_value = {
            "ids": [["chunk_001"]],
            "documents": [["Test content"]],
            "metadatas": [[{"chapter_number": 1}]],
            "distances": [[0.1]]
        }
        mock_claude_client.generate_answer.side_effect = mock_api_error

        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            llm_client=mock_claude_client,
            embedding_generator=mock_openai_client
        )

        with pytest.raises(Exception, match="API Error"):
            pipeline.ask("Test question")

    def test_embedding_generation_failure(
        self,
        mock_vector_store,
        mock_claude_client,
        mock_openai_client,
        mock_api_error
    ):
        """Test handling of embedding generation failures."""
        mock_openai_client.generate_embedding.side_effect = mock_api_error

        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            llm_client=mock_claude_client,
            embedding_generator=mock_openai_client
        )

        with pytest.raises(Exception, match="API Error"):
            pipeline.ask("Test question")


# ============================================================================
# Pipeline Statistics and Health Check Tests
# ============================================================================

@pytest.mark.unit
class TestRAGPipelineStats:
    """Test pipeline statistics and health checks."""

    def test_get_pipeline_stats(
        self,
        mock_vector_store,
        mock_claude_client,
        mock_openai_client
    ):
        """Test retrieving pipeline statistics."""
        mock_vector_store.get_stats.return_value = {
            "total_chunks": 100,
            "collections": ["icelandic_chemistry"]
        }

        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            llm_client=mock_claude_client,
            embedding_generator=mock_openai_client
        )

        stats = pipeline.get_pipeline_stats()

        assert "configuration" in stats
        assert "database" in stats
        assert stats["database"]["total_chunks"] == 100

    def test_health_check_healthy(
        self,
        mock_vector_store,
        mock_claude_client,
        mock_openai_client
    ):
        """Test health check when all components are healthy."""
        mock_vector_store.get_stats.return_value = {"total_chunks": 100}

        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            llm_client=mock_claude_client,
            embedding_generator=mock_openai_client
        )

        health = pipeline.health_check()

        assert health["status"] == "healthy"
        assert "components" in health

    def test_health_check_unhealthy(
        self,
        mock_vector_store,
        mock_claude_client,
        mock_openai_client,
        mock_db_error
    ):
        """Test health check when components are unhealthy."""
        mock_vector_store.get_stats.side_effect = mock_db_error

        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            llm_client=mock_claude_client,
            embedding_generator=mock_openai_client
        )

        health = pipeline.health_check()

        assert health["status"] == "unhealthy"


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.slow
@pytest.mark.performance
class TestRAGPipelinePerformance:
    """Test RAG pipeline performance benchmarks."""

    def test_response_time_under_threshold(
        self,
        mock_vector_store,
        mock_claude_client,
        mock_openai_client,
        mock_embedding,
        performance_timer,
        expected_responses
    ):
        """Test that responses are generated within time threshold."""
        mock_openai_client.generate_embedding.return_value = mock_embedding
        mock_vector_store.search.return_value = {
            "ids": [["chunk_001"]],
            "documents": [["Test content"]],
            "metadatas": [[{"chapter_number": 1, "section_number": "1.1"}]],
            "distances": [[0.1]]
        }
        mock_claude_client.generate_answer.return_value = {
            "answer": "Test answer",
            "citations": []
        }

        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            llm_client=mock_claude_client,
            embedding_generator=mock_openai_client
        )

        with performance_timer() as timer:
            result = pipeline.ask("Hvað er atóm?")

        # Performance threshold from expected_responses.json
        max_time = expected_responses["performance_benchmarks"]["max_response_time_seconds"]
        assert timer.elapsed < max_time, f"Response took {timer.elapsed}s, expected < {max_time}s"
        assert "answer" in result


# ============================================================================
# Integration-like Tests (with mocked external dependencies)
# ============================================================================

@pytest.mark.integration
class TestRAGPipelineIntegration:
    """Integration tests for complete RAG pipeline flow."""

    @patch('src.embeddings.EmbeddingGenerator')
    @patch('src.llm_client.ClaudeClient')
    @patch('src.vector_store.VectorStore')
    def test_complete_rag_flow(
        self,
        mock_vs_class,
        mock_llm_class,
        mock_emb_class,
        mock_embedding,
        sample_chunks,
        expected_responses
    ):
        """Test complete RAG flow from question to answer with citations."""
        # Setup comprehensive mocks
        mock_vs = MagicMock()
        mock_llm = MagicMock()
        mock_emb = MagicMock()

        mock_vs_class.return_value = mock_vs
        mock_llm_class.return_value = mock_llm
        mock_emb_class.return_value = mock_emb

        # Use test case from expected_responses
        test_case = expected_responses["test_cases"][0]  # "Hvað er atóm?"

        mock_emb.generate_embedding.return_value = mock_embedding
        mock_vs.search.return_value = {
            "ids": [[sample_chunks[0]["id"]]],
            "documents": [[sample_chunks[0]["content"]]],
            "metadatas": [[sample_chunks[0]["metadata"]]],
            "distances": [[0.1]]
        }

        # Generate answer that contains expected keywords
        answer = "Atóm er minnsta eining efnis sem getur tekið þátt í efnahvörfum. Það samanstendur af kjarna með róteindir og nifteindir, og rafeindaskýi."
        mock_llm.generate_answer.return_value = {
            "answer": answer,
            "citations": [sample_chunks[0]["metadata"]]
        }

        pipeline = RAGPipeline(
            vector_store=mock_vs,
            llm_client=mock_llm,
            embedding_generator=mock_emb
        )

        result = pipeline.ask(test_case["question"])

        # Verify answer contains expected keywords
        for keyword in test_case["expected_answer_contains"]:
            assert keyword.lower() in result["answer"].lower(), \
                f"Expected keyword '{keyword}' not found in answer"

        # Verify citations
        assert len(result["citations"]) > 0
        citation = result["citations"][0]
        expected_citation = test_case["expected_citations"][0]
        assert citation["chapter_number"] == expected_citation["chapter"]
        assert citation["section_number"] == expected_citation["section"]
