"""
Embedding Generation using OpenAI API
Handles batch processing, rate limiting, and cost tracking.
"""

import os
import logging
import time
from typing import List
from openai import OpenAI
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generates embeddings using OpenAI's text-embedding-3-small model.
    Supports batch processing and rate limit handling.
    """

    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        """
        Initialize the embedding generator.

        Args:
            api_key: OpenAI API key (defaults to env variable)
            model: Embedding model name
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        self.model = model
        self.client = OpenAI(api_key=self.api_key)

        # Batch size for processing
        self.batch_size = 100

        # Cost tracking
        self.total_tokens = 0
        # text-embedding-3-small costs $0.00002 per 1K tokens
        self.cost_per_1k_tokens = 0.00002

        logger.info(f"Initialized EmbeddingGenerator with model: {model}")

    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = None
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts with batch processing.

        Args:
            texts: List of text strings
            batch_size: Number of texts to process in each batch

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        batch_size = batch_size or self.batch_size
        embeddings = []

        logger.info(f"Generating embeddings for {len(texts)} texts in batches of {batch_size}")

        # Process in batches to handle rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(texts) + batch_size - 1) // batch_size

            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")

            try:
                # Generate embeddings for batch
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )

                # Extract embeddings
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

                # Track tokens and costs
                tokens_used = response.usage.total_tokens
                self.total_tokens += tokens_used
                cost = (tokens_used / 1000) * self.cost_per_1k_tokens

                logger.info(
                    f"Batch {batch_num} complete: {tokens_used} tokens, "
                    f"${cost:.6f} cost"
                )

                # Rate limiting: small delay between batches
                if i + batch_size < len(texts):
                    time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error generating embeddings for batch {batch_num}: {e}")

                # Retry with exponential backoff
                for retry in range(3):
                    wait_time = 2 ** retry
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

                    try:
                        response = self.client.embeddings.create(
                            input=batch,
                            model=self.model
                        )
                        batch_embeddings = [item.embedding for item in response.data]
                        embeddings.extend(batch_embeddings)

                        tokens_used = response.usage.total_tokens
                        self.total_tokens += tokens_used
                        logger.info(f"Retry successful for batch {batch_num}")
                        break
                    except Exception as retry_error:
                        if retry == 2:  # Last retry
                            logger.error(f"All retries failed for batch {batch_num}: {retry_error}")
                            raise
                        continue

        logger.info(
            f"Embedding generation complete: {len(embeddings)} embeddings, "
            f"{self.total_tokens} total tokens, "
            f"${(self.total_tokens / 1000) * self.cost_per_1k_tokens:.6f} total cost"
        )

        return embeddings

    def get_cost_summary(self) -> dict:
        """
        Get summary of embedding costs.

        Returns:
            Dictionary with token usage and cost information
        """
        total_cost = (self.total_tokens / 1000) * self.cost_per_1k_tokens
        return {
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "model": self.model,
            "cost_per_1k_tokens": self.cost_per_1k_tokens
        }


class ChromaEmbeddingFunction:
    """
    Wrapper for OpenAI embeddings compatible with ChromaDB.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize ChromaDB-compatible embedding function.

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        # Use ChromaDB's built-in OpenAI embedding function
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=self.api_key,
            model_name="text-embedding-3-small"
        )

        logger.info("Initialized ChromaDB OpenAI embedding function")

    def __call__(self, input: List[str]) -> List[List[float]]:
        """
        Generate embeddings (callable interface for ChromaDB).

        Args:
            input: List of text strings

        Returns:
            List of embedding vectors
        """
        return self.embedding_function(input)


def get_embedding_function() -> ChromaEmbeddingFunction:
    """
    Factory function to get an embedding function instance.

    Returns:
        ChromaDB-compatible embedding function
    """
    return ChromaEmbeddingFunction()
