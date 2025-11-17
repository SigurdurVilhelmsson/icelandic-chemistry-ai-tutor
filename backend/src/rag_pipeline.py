"""
RAG Pipeline - Core Orchestration
Coordinates retrieval and generation for chemistry tutoring.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .vector_store import VectorStore
from .embeddings import get_embedding_function
from .llm_client import ClaudeClient

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline for Icelandic chemistry tutoring.

    Orchestrates:
    1. Question processing
    2. Semantic search in vector store
    3. Context preparation
    4. Answer generation with Claude
    5. Response formatting with citations
    """

    def __init__(
        self,
        chroma_db_path: str = "./data/chroma_db",
        top_k: int = 5,
        max_context_chunks: int = 4
    ):
        """
        Initialize the RAG pipeline.

        Args:
            chroma_db_path: Path to ChromaDB storage
            top_k: Number of documents to retrieve
            max_context_chunks: Maximum chunks to use in context
        """
        self.top_k = top_k
        self.max_context_chunks = max_context_chunks

        logger.info("Initializing RAG Pipeline")

        # Initialize components
        try:
            # Vector store
            self.vector_store = VectorStore(persist_directory=chroma_db_path)
            embedding_function = get_embedding_function()
            self.vector_store.initialize_collection(embedding_function)

            # LLM client
            self.llm_client = ClaudeClient()

            logger.info("RAG Pipeline initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing RAG pipeline: {e}")
            raise

    def ask(
        self,
        question: str,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a question and generate an answer with citations.

        Args:
            question: User's question in Icelandic
            metadata_filter: Optional filter (e.g., {"chapter": "1"})

        Returns:
            Dictionary with answer, citations, and metadata
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        logger.info(f"Processing question: '{question}'")
        start_time = datetime.now()

        try:
            # Step 1: Retrieve relevant documents
            logger.info(f"Retrieving top {self.top_k} documents")
            search_results = self.vector_store.search(
                query=question,
                n_results=self.top_k,
                where=metadata_filter
            )

            # Step 2: Format retrieved chunks
            chunks = self._format_search_results(search_results)

            if not chunks:
                logger.warning("No relevant documents found")
                return {
                    "answer": "Því miður fann ég engin viðeigandi gögn til að svara þessari spurningu. Vinsamlegast reyndu að orða spurninguna öðruvísi eða spyrðu um annað efni.",
                    "citations": [],
                    "metadata": {
                        "question": question,
                        "timestamp": datetime.now().isoformat(),
                        "chunks_found": 0,
                        "response_time_ms": (datetime.now() - start_time).total_seconds() * 1000
                    }
                }

            logger.info(f"Found {len(chunks)} relevant chunks")

            # Step 3: Generate answer using Claude
            logger.info("Generating answer with Claude")
            llm_response = self.llm_client.generate_answer(
                question=question,
                context_chunks=chunks,
                max_chunks=self.max_context_chunks
            )

            # Step 4: Format final response
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000

            result = {
                "answer": llm_response["answer"],
                "citations": llm_response["citations"],
                "metadata": {
                    "question": question,
                    "timestamp": end_time.isoformat(),
                    "chunks_found": len(chunks),
                    "chunks_used": min(len(chunks), self.max_context_chunks),
                    "response_time_ms": round(response_time, 2),
                    "model": llm_response["model"],
                    "tokens_used": llm_response["tokens_used"]
                }
            }

            logger.info(f"Answer generated successfully in {response_time:.2f}ms")
            return result

        except Exception as e:
            logger.error(f"Error processing question: {e}")
            raise

    def _format_search_results(self, results: Dict[str, Any]) -> list:
        """
        Format ChromaDB search results into structured chunks.

        Args:
            results: Raw search results from ChromaDB

        Returns:
            List of formatted chunks with metadata
        """
        chunks = []

        if not results or not results.get('documents'):
            return chunks

        documents = results['documents'][0]  # First query results
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0]
        ids = results.get('ids', [[]])[0]

        for i, doc in enumerate(documents):
            chunk = {
                'document': doc,
                'metadata': metadatas[i] if i < len(metadatas) else {},
                'distance': distances[i] if i < len(distances) else None,
                'id': ids[i] if i < len(ids) else None
            }
            chunks.append(chunk)

        return chunks

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG pipeline.

        Returns:
            Dictionary with pipeline configuration and DB stats
        """
        try:
            db_stats = self.vector_store.get_stats()

            return {
                "configuration": {
                    "top_k": self.top_k,
                    "max_context_chunks": self.max_context_chunks,
                    "model": self.llm_client.model
                },
                "database": db_stats
            }

        except Exception as e:
            logger.error(f"Error getting pipeline stats: {e}")
            raise

    def validate_setup(self) -> Dict[str, bool]:
        """
        Validate that all components are properly configured.

        Returns:
            Dictionary with validation results
        """
        results = {
            "vector_store": False,
            "embeddings": False,
            "llm_client": False,
            "icelandic_support": False
        }

        try:
            # Check vector store
            stats = self.vector_store.get_stats()
            results["vector_store"] = stats["total_chunks"] > 0

            # Check embeddings (implicitly validated by vector store)
            results["embeddings"] = True

            # Check LLM client
            results["llm_client"] = self.llm_client is not None

            # Check Icelandic support
            results["icelandic_support"] = self.llm_client.validate_icelandic_support()

            logger.info(f"Validation results: {results}")

        except Exception as e:
            logger.error(f"Error during validation: {e}")

        return results

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the pipeline.

        Returns:
            Dictionary with health status
        """
        try:
            stats = self.get_pipeline_stats()
            validation = self.validate_setup()

            all_valid = all(validation.values())

            return {
                "status": "healthy" if all_valid else "degraded",
                "timestamp": datetime.now().isoformat(),
                "validation": validation,
                "stats": stats
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
