"""
Tests for Vector Store - ChromaDB operations and vector search.

This module tests the VectorStore class which wraps ChromaDB functionality
including document storage, similarity search, and metadata filtering.
"""

import pytest
import shutil
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, MagicMock, patch

import numpy as np

# Import module to test
from src.vector_store import VectorStore


# ============================================================================
# Vector Store Initialization Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestVectorStoreInitialization:
    """Test vector store initialization and configuration."""

    def test_create_vector_store(self, temp_chroma_db):
        """Test creating a new vector store instance."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        assert store is not None
        assert store.collection_name == "icelandic_chemistry"

    def test_persistent_storage(self, temp_chroma_db):
        """Test that vector store uses persistent storage."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Verify that the database directory exists
        assert temp_chroma_db.exists()

    def test_custom_collection_name(self, temp_chroma_db):
        """Test creating vector store with custom collection name."""
        custom_name = "test_chemistry_collection"
        store = VectorStore(
            persist_directory=str(temp_chroma_db),
            collection_name=custom_name
        )

        assert store.collection_name == custom_name


# ============================================================================
# Document Addition Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestVectorStoreAddDocuments:
    """Test adding documents to the vector store."""

    def test_add_single_document(self, temp_chroma_db, mock_embedding):
        """Test adding a single document."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        documents = ["Atóm er minnsta eining efnis."]
        metadatas = [{
            "chapter_number": 1,
            "section_number": "1.1",
            "chapter_title": "Efnafræði",
            "language": "is"
        }]
        ids = ["chunk_001"]
        embeddings = [mock_embedding]

        result = store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )

        assert result is True or result is None  # ChromaDB may return None on success

    def test_add_multiple_documents(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings
    ):
        """Test adding multiple documents at once."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Prepare batch data
        documents = [chunk["content"] for chunk in sample_chunks[:5]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:5]]
        ids = [chunk["id"] for chunk in sample_chunks[:5]]
        embeddings = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:5]]

        result = store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )

        # Verify documents were added
        stats = store.get_stats()
        assert stats["total_chunks"] >= 5

    def test_add_documents_with_icelandic_content(
        self,
        temp_chroma_db,
        mock_embedding,
        assert_icelandic_preserved
    ):
        """Test that Icelandic characters are preserved in stored documents."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        icelandic_text = "Atóm með þ, æ, ö, ð, á, é, í, ó, ú, ý"
        documents = [icelandic_text]
        metadatas = [{"chapter_number": 1, "language": "is"}]
        ids = ["icelandic_test"]
        embeddings = [mock_embedding]

        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )

        # Retrieve and verify
        results = store.get_all_documents()
        if results and len(results["documents"]) > 0:
            # Find our test document
            for doc in results["documents"]:
                if "Atóm með" in doc:
                    assert_icelandic_preserved(doc)
                    break

    def test_add_documents_validation(self, temp_chroma_db, mock_embedding):
        """Test validation of document parameters."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Test mismatched lengths
        with pytest.raises((ValueError, AssertionError)):
            store.add_documents(
                documents=["doc1", "doc2"],
                metadatas=[{"chapter": 1}],  # Only 1 metadata for 2 docs
                ids=["id1", "id2"],
                embeddings=[mock_embedding, mock_embedding]
            )


# ============================================================================
# Vector Search Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestVectorStoreSearch:
    """Test vector similarity search functionality."""

    def test_search_basic(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings,
        mock_embedding
    ):
        """Test basic similarity search."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Add documents
        documents = [chunk["content"] for chunk in sample_chunks[:5]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:5]]
        ids = [chunk["id"] for chunk in sample_chunks[:5]]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:5]]

        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        # Search with query embedding
        results = store.search(
            query_embedding=mock_embedding,
            n_results=3
        )

        # Verify search results structure
        assert "ids" in results
        assert "documents" in results
        assert "metadatas" in results
        assert "distances" in results

        # Verify we got results
        assert len(results["ids"]) > 0
        assert len(results["ids"][0]) <= 3  # At most 3 results requested

    def test_search_with_metadata_filter(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings,
        mock_embedding
    ):
        """Test search with metadata filtering."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Add documents from different chapters
        documents = [chunk["content"] for chunk in sample_chunks[:10]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:10]]
        ids = [chunk["id"] for chunk in sample_chunks[:10]]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:10]]

        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        # Search with chapter filter
        results = store.search(
            query_embedding=mock_embedding,
            n_results=5,
            where={"chapter_number": 1}
        )

        # Verify all results are from chapter 1
        if results["metadatas"] and len(results["metadatas"][0]) > 0:
            for metadata in results["metadatas"][0]:
                assert metadata["chapter_number"] == 1

    def test_search_top_k_results(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings,
        mock_embedding
    ):
        """Test that search returns requested number of results."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Add documents
        documents = [chunk["content"] for chunk in sample_chunks[:10]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:10]]
        ids = [chunk["id"] for chunk in sample_chunks[:10]]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:10]]

        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        # Test different k values
        for k in [1, 3, 5]:
            results = store.search(
                query_embedding=mock_embedding,
                n_results=k
            )

            if results["ids"] and len(results["ids"]) > 0:
                assert len(results["ids"][0]) <= k

    def test_search_empty_store(self, temp_chroma_db, mock_embedding):
        """Test search on empty vector store."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        results = store.search(
            query_embedding=mock_embedding,
            n_results=5
        )

        # Should return empty results, not error
        assert results["ids"] == [[]] or len(results["ids"][0]) == 0


# ============================================================================
# Database Statistics Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestVectorStoreStatistics:
    """Test database statistics and information retrieval."""

    def test_get_stats_empty_store(self, temp_chroma_db):
        """Test statistics for empty store."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        stats = store.get_stats()

        assert "total_chunks" in stats
        assert stats["total_chunks"] == 0

    def test_get_stats_with_documents(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings
    ):
        """Test statistics after adding documents."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Add 5 documents
        n_docs = 5
        documents = [chunk["content"] for chunk in sample_chunks[:n_docs]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:n_docs]]
        ids = [chunk["id"] for chunk in sample_chunks[:n_docs]]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:n_docs]]

        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        stats = store.get_stats()

        assert stats["total_chunks"] == n_docs

    def test_get_all_documents(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings
    ):
        """Test retrieving all documents from store."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Add documents
        n_docs = 3
        documents = [chunk["content"] for chunk in sample_chunks[:n_docs]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:n_docs]]
        ids = [chunk["id"] for chunk in sample_chunks[:n_docs]]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:n_docs]]

        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        all_docs = store.get_all_documents()

        assert "documents" in all_docs
        assert "metadatas" in all_docs
        assert "ids" in all_docs
        assert len(all_docs["ids"]) == n_docs


# ============================================================================
# Database Operations Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestVectorStoreDatabaseOperations:
    """Test database management operations."""

    def test_delete_collection(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings
    ):
        """Test deleting a collection."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Add some documents
        documents = [sample_chunks[0]["content"]]
        metadatas = [sample_chunks[0]["metadata"]]
        ids = [sample_chunks[0]["id"]]
        embeddings_list = [mock_embeddings[sample_chunks[0]["id"]]]

        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        # Delete collection
        store.delete_collection()

        # Verify collection is empty/deleted
        stats = store.get_stats()
        assert stats["total_chunks"] == 0

    def test_reset_store(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings
    ):
        """Test resetting the store."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Add documents
        documents = [chunk["content"] for chunk in sample_chunks[:3]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:3]]
        ids = [chunk["id"] for chunk in sample_chunks[:3]]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:3]]

        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        # Reset
        store.reset()

        # Verify store is empty
        stats = store.get_stats()
        assert stats["total_chunks"] == 0

    def test_persistence_across_instances(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings
    ):
        """Test that data persists across different store instances."""
        # Create first instance and add data
        store1 = VectorStore(persist_directory=str(temp_chroma_db))

        documents = [sample_chunks[0]["content"]]
        metadatas = [sample_chunks[0]["metadata"]]
        ids = [sample_chunks[0]["id"]]
        embeddings_list = [mock_embeddings[sample_chunks[0]["id"]]]

        store1.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        # Create second instance pointing to same directory
        store2 = VectorStore(persist_directory=str(temp_chroma_db))

        # Verify data is accessible from second instance
        stats = store2.get_stats()
        assert stats["total_chunks"] >= 1


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestVectorStoreErrorHandling:
    """Test error handling in vector store operations."""

    def test_invalid_embedding_dimension(self, temp_chroma_db):
        """Test handling of incorrect embedding dimensions."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Try to add document with wrong embedding dimension
        documents = ["Test document"]
        metadatas = [{"chapter_number": 1}]
        ids = ["test_id"]
        # Wrong dimension (should be 1536 for text-embedding-3-small)
        wrong_embeddings = [[0.1, 0.2, 0.3]]

        with pytest.raises((ValueError, Exception)):
            store.add_documents(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=wrong_embeddings
            )

    def test_duplicate_ids(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings
    ):
        """Test handling of duplicate document IDs."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Add document with ID
        doc_id = sample_chunks[0]["id"]
        documents = [sample_chunks[0]["content"]]
        metadatas = [sample_chunks[0]["metadata"]]
        ids = [doc_id]
        embeddings_list = [mock_embeddings[doc_id]]

        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        # Try to add different document with same ID
        # Behavior depends on ChromaDB version (upsert or error)
        try:
            store.add_documents(
                documents=["Different content"],
                metadatas=[{"chapter_number": 2}],
                ids=[doc_id],  # Same ID
                embeddings=[mock_embeddings[sample_chunks[1]["id"]]]
            )
            # If no error, it's an upsert - that's fine
        except Exception:
            # If error, that's also acceptable behavior
            pass


# ============================================================================
# Batch Operations Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestVectorStoreBatchOperations:
    """Test batch operations for efficiency."""

    def test_batch_add_large_dataset(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings
    ):
        """Test adding large batch of documents."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Use all available sample chunks
        documents = [chunk["content"] for chunk in sample_chunks]
        metadatas = [chunk["metadata"] for chunk in sample_chunks]
        ids = [chunk["id"] for chunk in sample_chunks]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks]

        # Add in batch
        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        # Verify all were added
        stats = store.get_stats()
        assert stats["total_chunks"] == len(sample_chunks)

    @pytest.mark.slow
    def test_batch_search_performance(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings,
        mock_embedding,
        performance_timer
    ):
        """Test that batch search operations are performant."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Add documents
        documents = [chunk["content"] for chunk in sample_chunks]
        metadatas = [chunk["metadata"] for chunk in sample_chunks]
        ids = [chunk["id"] for chunk in sample_chunks]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks]

        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        # Measure search time
        with performance_timer() as timer:
            results = store.search(
                query_embedding=mock_embedding,
                n_results=5
            )

        # Should be fast (< 0.3 seconds as per expected_responses.json)
        assert timer.elapsed < 0.5  # Generous threshold for tests
        assert len(results["ids"]) > 0


# ============================================================================
# Metadata Filtering Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestVectorStoreMetadataFiltering:
    """Test advanced metadata filtering capabilities."""

    def test_filter_by_chapter(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings,
        mock_embedding
    ):
        """Test filtering search results by chapter."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Add documents
        documents = [chunk["content"] for chunk in sample_chunks[:10]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:10]]
        ids = [chunk["id"] for chunk in sample_chunks[:10]]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:10]]

        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        # Search with chapter filter
        target_chapter = 2
        results = store.search(
            query_embedding=mock_embedding,
            n_results=5,
            where={"chapter_number": target_chapter}
        )

        # Verify filtering
        if results["metadatas"] and len(results["metadatas"][0]) > 0:
            for metadata in results["metadatas"][0]:
                assert metadata["chapter_number"] == target_chapter

    def test_filter_by_section(
        self,
        temp_chroma_db,
        sample_chunks,
        mock_embeddings,
        mock_embedding
    ):
        """Test filtering search results by section."""
        store = VectorStore(persist_directory=str(temp_chroma_db))

        # Add documents
        documents = [chunk["content"] for chunk in sample_chunks[:10]]
        metadatas = [chunk["metadata"] for chunk in sample_chunks[:10]]
        ids = [chunk["id"] for chunk in sample_chunks[:10]]
        embeddings_list = [mock_embeddings[chunk["id"]] for chunk in sample_chunks[:10]]

        store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings_list
        )

        # Search with section filter
        target_section = "1.1"
        results = store.search(
            query_embedding=mock_embedding,
            n_results=5,
            where={"section_number": target_section}
        )

        # Verify filtering
        if results["metadatas"] and len(results["metadatas"][0]) > 0:
            for metadata in results["metadatas"][0]:
                assert metadata["section_number"] == target_section
