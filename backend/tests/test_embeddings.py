"""
Tests for Embedding Generation - OpenAI text-embedding-3-small integration.

This module tests the EmbeddingGenerator class which handles:
- Generating embeddings via OpenAI API
- Batch processing
- Rate limiting
- Cost tracking
- Error handling and retries
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import List
import time

import numpy as np

# Import modules to test
from src.embeddings import EmbeddingGenerator, ChromaEmbeddingFunction


# ============================================================================
# Embedding Generator Initialization Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.api
class TestEmbeddingGeneratorInitialization:
    """Test embedding generator initialization."""

    @patch('openai.OpenAI')
    def test_create_embedding_generator(self, mock_openai_class):
        """Test creating embedding generator instance."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        generator = EmbeddingGenerator(api_key="test-key")

        assert generator is not None
        assert generator.model == "text-embedding-3-small"
        mock_openai_class.assert_called_once()

    @patch('openai.OpenAI')
    def test_custom_model(self, mock_openai_class):
        """Test creating generator with custom model."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        custom_model = "text-embedding-3-large"
        generator = EmbeddingGenerator(api_key="test-key", model=custom_model)

        assert generator.model == custom_model


# ============================================================================
# Single Embedding Generation Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.api
class TestSingleEmbeddingGeneration:
    """Test generating single embeddings."""

    @patch('openai.OpenAI')
    def test_generate_embedding_simple_text(
        self,
        mock_openai_class,
        mock_embedding
    ):
        """Test generating embedding for simple text."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock API response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=mock_embedding)]
        mock_client.embeddings.create.return_value = mock_response

        generator = EmbeddingGenerator(api_key="test-key")
        result = generator.generate_embedding("Hvað er atóm?")

        # Verify embedding structure
        assert isinstance(result, list)
        assert len(result) == 1536  # text-embedding-3-small dimension
        assert all(isinstance(x, float) for x in result)

        # Verify API was called correctly
        mock_client.embeddings.create.assert_called_once()
        call_args = mock_client.embeddings.create.call_args
        assert call_args.kwargs["model"] == "text-embedding-3-small"
        assert "Hvað er atóm?" in call_args.kwargs["input"]

    @patch('openai.OpenAI')
    def test_generate_embedding_icelandic_text(
        self,
        mock_openai_class,
        mock_embedding,
        assert_icelandic_preserved
    ):
        """Test that Icelandic characters are handled correctly."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=mock_embedding)]
        mock_client.embeddings.create.return_value = mock_response

        generator = EmbeddingGenerator(api_key="test-key")

        icelandic_text = "Atóm með þ, æ, ö, ð, á, é, í, ó, ú, ý"
        result = generator.generate_embedding(icelandic_text)

        # Verify embedding was generated
        assert isinstance(result, list)
        assert len(result) == 1536

        # Verify API received correct text (captured in call args)
        call_args = mock_client.embeddings.create.call_args
        received_text = call_args.kwargs["input"]
        assert_icelandic_preserved(received_text)

    @patch('openai.OpenAI')
    def test_generate_embedding_empty_text(self, mock_openai_class):
        """Test handling of empty text."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        generator = EmbeddingGenerator(api_key="test-key")

        with pytest.raises(ValueError, match=".*empty.*"):
            generator.generate_embedding("")

    @patch('openai.OpenAI')
    def test_generate_embedding_very_long_text(
        self,
        mock_openai_class,
        mock_embedding
    ):
        """Test handling of very long text (token limit considerations)."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=mock_embedding)]
        mock_client.embeddings.create.return_value = mock_response

        generator = EmbeddingGenerator(api_key="test-key")

        # Create very long text (1000+ words)
        long_text = " ".join(["Atóm er minnsta eining efnis."] * 200)

        result = generator.generate_embedding(long_text)

        # Should handle gracefully (truncate or process in chunks)
        assert isinstance(result, list)
        assert len(result) == 1536


# ============================================================================
# Batch Embedding Generation Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.api
class TestBatchEmbeddingGeneration:
    """Test batch embedding generation."""

    @patch('openai.OpenAI')
    def test_generate_embeddings_batch(
        self,
        mock_openai_class,
        mock_embedding_dimension
    ):
        """Test generating embeddings for multiple texts in batch."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock batch response
        np.random.seed(42)
        batch_embeddings = [
            np.random.rand(mock_embedding_dimension).tolist()
            for _ in range(3)
        ]
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=emb) for emb in batch_embeddings
        ]
        mock_client.embeddings.create.return_value = mock_response

        generator = EmbeddingGenerator(api_key="test-key", batch_size=100)

        texts = [
            "Hvað er atóm?",
            "Útskýrðu lotukerfið",
            "Hvað er efnatengi?"
        ]

        results = generator.generate_embeddings_batch(texts)

        # Verify results
        assert len(results) == 3
        assert all(len(emb) == 1536 for emb in results)

        # Verify API called once for batch
        mock_client.embeddings.create.assert_called_once()

    @patch('openai.OpenAI')
    def test_batch_with_rate_limiting(
        self,
        mock_openai_class,
        mock_embedding_dimension
    ):
        """Test that rate limiting is applied between batches."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock responses for multiple batches
        np.random.seed(42)

        def mock_create_embeddings(*args, **kwargs):
            input_texts = kwargs["input"]
            batch_size = len(input_texts) if isinstance(input_texts, list) else 1
            embeddings = [
                np.random.rand(mock_embedding_dimension).tolist()
                for _ in range(batch_size)
            ]
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(embedding=emb) for emb in embeddings
            ]
            return mock_response

        mock_client.embeddings.create.side_effect = mock_create_embeddings

        # Create generator with small batch size to force multiple batches
        generator = EmbeddingGenerator(
            api_key="test-key",
            batch_size=2,
            rate_limit_delay=0.1  # Small delay for testing
        )

        # Generate embeddings for 5 texts (will require 3 batches)
        texts = [f"Text {i}" for i in range(5)]

        start_time = time.time()
        results = generator.generate_embeddings_batch(texts)
        elapsed = time.time() - start_time

        # Verify results
        assert len(results) == 5

        # Verify rate limiting caused delays (3 batches = 2 delays)
        # Should take at least 0.2 seconds (2 delays * 0.1s each)
        assert elapsed >= 0.15  # Allow some tolerance

    @patch('openai.OpenAI')
    def test_empty_batch(self, mock_openai_class):
        """Test handling of empty batch."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        generator = EmbeddingGenerator(api_key="test-key")

        results = generator.generate_embeddings_batch([])

        # Should return empty list
        assert results == []
        # Should not call API
        mock_client.embeddings.create.assert_not_called()


# ============================================================================
# Cost Tracking Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.api
class TestCostTracking:
    """Test cost tracking functionality."""

    @patch('openai.OpenAI')
    def test_cost_calculation(
        self,
        mock_openai_class,
        mock_embedding
    ):
        """Test that costs are calculated correctly."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=mock_embedding)]
        mock_response.usage = MagicMock(total_tokens=100)
        mock_client.embeddings.create.return_value = mock_response

        generator = EmbeddingGenerator(api_key="test-key")

        # Generate some embeddings
        generator.generate_embedding("Test text")

        # Get cost statistics
        cost_info = generator.get_cost_info()

        assert "total_tokens" in cost_info
        assert "total_cost" in cost_info
        assert cost_info["total_tokens"] == 100
        # text-embedding-3-small costs $0.00002 per 1K tokens
        expected_cost = (100 / 1000) * 0.00002
        assert cost_info["total_cost"] == pytest.approx(expected_cost, rel=1e-6)

    @patch('openai.OpenAI')
    def test_cumulative_cost_tracking(
        self,
        mock_openai_class,
        mock_embedding
    ):
        """Test that costs accumulate across multiple calls."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        def mock_create(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=mock_embedding)]
            mock_response.usage = MagicMock(total_tokens=50)
            return mock_response

        mock_client.embeddings.create.side_effect = mock_create

        generator = EmbeddingGenerator(api_key="test-key")

        # Generate embeddings multiple times
        generator.generate_embedding("Test 1")
        generator.generate_embedding("Test 2")
        generator.generate_embedding("Test 3")

        cost_info = generator.get_cost_info()

        # Should track cumulative tokens and cost
        assert cost_info["total_tokens"] == 150  # 50 * 3
        expected_cost = (150 / 1000) * 0.00002
        assert cost_info["total_cost"] == pytest.approx(expected_cost, rel=1e-6)


# ============================================================================
# Error Handling and Retry Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.api
class TestEmbeddingErrorHandling:
    """Test error handling and retry logic."""

    @patch('openai.OpenAI')
    def test_api_error_handling(self, mock_openai_class):
        """Test handling of API errors."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Simulate API error
        mock_client.embeddings.create.side_effect = Exception("API Error: Rate limit exceeded")

        generator = EmbeddingGenerator(api_key="test-key", max_retries=0)

        with pytest.raises(Exception, match="API Error"):
            generator.generate_embedding("Test text")

    @patch('openai.OpenAI')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_retry_on_failure(
        self,
        mock_sleep,
        mock_openai_class,
        mock_embedding
    ):
        """Test retry logic on temporary failures."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Fail twice, then succeed
        mock_client.embeddings.create.side_effect = [
            Exception("Temporary error"),
            Exception("Temporary error"),
            MagicMock(data=[MagicMock(embedding=mock_embedding)], usage=MagicMock(total_tokens=10))
        ]

        generator = EmbeddingGenerator(api_key="test-key", max_retries=3)

        result = generator.generate_embedding("Test text")

        # Should succeed after retries
        assert isinstance(result, list)
        assert len(result) == 1536

        # Verify retries occurred
        assert mock_client.embeddings.create.call_count == 3

    @patch('openai.OpenAI')
    def test_max_retries_exceeded(self, mock_openai_class):
        """Test behavior when max retries are exceeded."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Always fail
        mock_client.embeddings.create.side_effect = Exception("Persistent error")

        generator = EmbeddingGenerator(api_key="test-key", max_retries=2)

        with pytest.raises(Exception, match="Persistent error"):
            generator.generate_embedding("Test text")

        # Should have tried 3 times (initial + 2 retries)
        assert mock_client.embeddings.create.call_count == 3

    @patch('openai.OpenAI')
    def test_timeout_handling(self, mock_openai_class, mock_api_timeout):
        """Test handling of API timeouts."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_client.embeddings.create.side_effect = mock_api_timeout

        generator = EmbeddingGenerator(api_key="test-key", max_retries=0)

        with pytest.raises(TimeoutError):
            generator.generate_embedding("Test text")


# ============================================================================
# ChromaEmbeddingFunction Tests
# ============================================================================

@pytest.mark.unit
class TestChromaEmbeddingFunction:
    """Test ChromaDB-compatible embedding function wrapper."""

    @patch('openai.OpenAI')
    def test_chroma_function_initialization(self, mock_openai_class):
        """Test creating ChromaDB embedding function."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        func = ChromaEmbeddingFunction(api_key="test-key")

        assert func is not None

    @patch('openai.OpenAI')
    def test_chroma_function_call(
        self,
        mock_openai_class,
        mock_embedding_dimension
    ):
        """Test calling ChromaDB embedding function."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock batch embeddings
        np.random.seed(42)
        batch_embeddings = [
            np.random.rand(mock_embedding_dimension).tolist()
            for _ in range(2)
        ]
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=emb) for emb in batch_embeddings
        ]
        mock_client.embeddings.create.return_value = mock_response

        func = ChromaEmbeddingFunction(api_key="test-key")

        # ChromaDB calls the function with list of texts
        texts = ["Text 1", "Text 2"]
        results = func(texts)

        # Verify results
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(len(emb) == 1536 for emb in results)


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.slow
@pytest.mark.performance
class TestEmbeddingPerformance:
    """Test embedding generation performance."""

    @patch('openai.OpenAI')
    def test_batch_processing_efficiency(
        self,
        mock_openai_class,
        mock_embedding_dimension,
        performance_timer
    ):
        """Test that batch processing is efficient."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        def mock_create(*args, **kwargs):
            input_data = kwargs["input"]
            count = len(input_data) if isinstance(input_data, list) else 1
            np.random.seed(42)
            embeddings = [
                np.random.rand(mock_embedding_dimension).tolist()
                for _ in range(count)
            ]
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(embedding=emb) for emb in embeddings
            ]
            mock_response.usage = MagicMock(total_tokens=count * 10)
            return mock_response

        mock_client.embeddings.create.side_effect = mock_create

        generator = EmbeddingGenerator(
            api_key="test-key",
            batch_size=100,
            rate_limit_delay=0.0  # No delay for performance test
        )

        # Generate embeddings for 10 texts
        texts = [f"Chemistry text {i}" for i in range(10)]

        with performance_timer() as timer:
            results = generator.generate_embeddings_batch(texts)

        # Verify results
        assert len(results) == 10

        # Should be fast (< 0.5 seconds with mocked API)
        # Real API would be slower, but mocked should be very fast
        assert timer.elapsed < 1.0

        # Should batch efficiently (single API call for 10 texts)
        assert mock_client.embeddings.create.call_count == 1


# ============================================================================
# Integration-like Tests
# ============================================================================

@pytest.mark.integration
class TestEmbeddingIntegration:
    """Integration tests for embedding generation."""

    @patch('openai.OpenAI')
    def test_complete_embedding_workflow(
        self,
        mock_openai_class,
        sample_chunks,
        mock_embedding_dimension
    ):
        """Test complete workflow of embedding generation for documents."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        def mock_create(*args, **kwargs):
            input_data = kwargs["input"]
            count = len(input_data) if isinstance(input_data, list) else 1
            np.random.seed(42)
            embeddings = [
                np.random.rand(mock_embedding_dimension).tolist()
                for _ in range(count)
            ]
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(embedding=emb) for emb in embeddings
            ]
            mock_response.usage = MagicMock(total_tokens=count * 20)
            return mock_response

        mock_client.embeddings.create.side_effect = mock_create

        generator = EmbeddingGenerator(api_key="test-key", batch_size=5)

        # Generate embeddings for sample documents
        documents = [chunk["content"] for chunk in sample_chunks[:10]]

        results = generator.generate_embeddings_batch(documents)

        # Verify all embeddings generated
        assert len(results) == 10
        assert all(len(emb) == 1536 for emb in results)

        # Verify cost tracking
        cost_info = generator.get_cost_info()
        assert cost_info["total_tokens"] > 0
        assert cost_info["total_cost"] > 0

    @patch('openai.OpenAI')
    def test_icelandic_content_end_to_end(
        self,
        mock_openai_class,
        icelandic_test_cases,
        mock_embedding
    ):
        """Test end-to-end embedding generation for Icelandic content."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=mock_embedding)]
        mock_response.usage = MagicMock(total_tokens=10)
        mock_client.embeddings.create.return_value = mock_response

        generator = EmbeddingGenerator(api_key="test-key")

        # Test all Icelandic test cases
        for test_case in icelandic_test_cases:
            result = generator.generate_embedding(test_case["input"])

            # Verify embedding generated successfully
            assert isinstance(result, list)
            assert len(result) == 1536

            # Verify Icelandic characters were preserved in API call
            call_args = mock_client.embeddings.create.call_args
            assert test_case["input"] in str(call_args)
