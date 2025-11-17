"""
Vector Store Management using ChromaDB
Handles persistent storage and retrieval of embedded chemistry content.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Manages ChromaDB vector store for chemistry content.
    Supports persistent storage, semantic search, and metadata filtering.
    """

    def __init__(self, persist_directory: str = "./data/chroma_db"):
        """
        Initialize ChromaDB with persistent storage.

        Args:
            persist_directory: Path to store ChromaDB data
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        logger.info(f"Initializing ChromaDB at {persist_directory}")

        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Collection name for chemistry content
        self.collection_name = "icelandic_chemistry"
        self.collection = None

    def initialize_collection(self, embedding_function) -> None:
        """
        Initialize or get existing collection.

        Args:
            embedding_function: Function to generate embeddings
        """
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=embedding_function
            )
            logger.info(f"Loaded existing collection '{self.collection_name}'")
        except Exception:
            # Create new collection if it doesn't exist
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=embedding_function,
                metadata={"description": "Icelandic chemistry educational content"}
            )
            logger.info(f"Created new collection '{self.collection_name}'")

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add documents to the vector store in batch.

        Args:
            documents: List of text chunks
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call initialize_collection first.")

        if not documents:
            logger.warning("No documents to add")
            return

        logger.info(f"Adding {len(documents)} documents to vector store")

        try:
            # Add documents in batch
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Successfully added {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for semantically similar documents.

        Args:
            query: Search query (in Icelandic)
            n_results: Number of results to return
            where: Optional metadata filter (e.g., {"chapter": "1"})

        Returns:
            Dictionary containing documents, metadatas, distances, and ids
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call initialize_collection first.")

        logger.info(f"Searching for: '{query}' (top {n_results} results)")

        try:
            # Perform semantic search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )

            logger.info(f"Found {len(results['documents'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Dictionary with total chunks, unique chapters, etc.
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call initialize_collection first.")

        try:
            count = self.collection.count()

            # Get all metadata to compute statistics
            if count > 0:
                results = self.collection.get()
                metadatas = results.get('metadatas', [])

                chapters = set()
                sections = set()
                for meta in metadatas:
                    if 'chapter' in meta:
                        chapters.add(meta['chapter'])
                    if 'section' in meta:
                        sections.add(meta['section'])

                return {
                    "total_chunks": count,
                    "unique_chapters": len(chapters),
                    "unique_sections": len(sections),
                    "chapters": sorted(list(chapters))
                }
            else:
                return {
                    "total_chunks": 0,
                    "unique_chapters": 0,
                    "unique_sections": 0,
                    "chapters": []
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            raise

    def get_all_documents(self) -> Dict[str, Any]:
        """
        Retrieve all documents from the collection.

        Returns:
            Dictionary containing all documents and metadata
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized. Call initialize_collection first.")

        try:
            return self.collection.get()
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise

    def delete_collection(self) -> None:
        """
        Delete the entire collection (use with caution).
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
            logger.info(f"Deleted collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise

    def reset(self) -> None:
        """
        Reset the vector store (delete all data).
        """
        logger.warning("Resetting vector store - all data will be deleted")
        try:
            self.client.reset()
            self.collection = None
            logger.info("Vector store reset complete")
        except Exception as e:
            logger.error(f"Error resetting vector store: {e}")
            raise
