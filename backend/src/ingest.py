"""
Content Ingestion Script
Loads markdown files, chunks content, and stores in ChromaDB.
"""

import os
import re
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

from .vector_store import VectorStore
from .embeddings import get_embedding_function

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContentChunker:
    """
    Chunks markdown content while preserving structure and metadata.
    """

    def __init__(self, min_words: int = 300, max_words: int = 800):
        """
        Initialize chunker with word limits.

        Args:
            min_words: Minimum words per chunk
            max_words: Maximum words per chunk
        """
        self.min_words = min_words
        self.max_words = max_words

    def chunk_markdown(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """
        Chunk markdown content while preserving paragraph boundaries.

        Args:
            content: Markdown content
            filename: Source filename

        Returns:
            List of chunks with metadata
        """
        logger.info(f"Chunking content from {filename}")

        chunks = []
        current_chapter = "1"
        current_section = "1"
        current_title = "Untitled"

        # Split into paragraphs
        paragraphs = content.split('\n\n')

        current_chunk = []
        current_word_count = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check for chapter header (# Kafli X)
            chapter_match = re.match(r'^#\s+Kafli\s+(\d+)', para)
            if chapter_match:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk,
                        current_chapter,
                        current_section,
                        current_title,
                        filename
                    ))
                    current_chunk = []
                    current_word_count = 0

                current_chapter = chapter_match.group(1)
                current_title = para.replace('#', '').strip()
                continue

            # Check for section header (## X.Y Title)
            section_match = re.match(r'^##\s+(\d+)\.(\d+)\s+(.+)', para)
            if section_match:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk,
                        current_chapter,
                        current_section,
                        current_title,
                        filename
                    ))
                    current_chunk = []
                    current_word_count = 0

                current_chapter = section_match.group(1)
                current_section = section_match.group(2)
                current_title = section_match.group(3).strip()
                continue

            # Count words
            word_count = len(para.split())

            # Check if adding this paragraph exceeds max_words
            if current_word_count + word_count > self.max_words and current_word_count >= self.min_words:
                # Save current chunk
                chunks.append(self._create_chunk(
                    current_chunk,
                    current_chapter,
                    current_section,
                    current_title,
                    filename
                ))
                current_chunk = [para]
                current_word_count = word_count
            else:
                # Add to current chunk
                current_chunk.append(para)
                current_word_count += word_count

        # Save final chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                current_chunk,
                current_chapter,
                current_section,
                current_title,
                filename
            ))

        logger.info(f"Created {len(chunks)} chunks from {filename}")
        return chunks

    def _create_chunk(
        self,
        paragraphs: List[str],
        chapter: str,
        section: str,
        title: str,
        filename: str
    ) -> Dict[str, Any]:
        """
        Create a chunk with metadata.

        Args:
            paragraphs: List of paragraph strings
            chapter: Chapter number
            section: Section number
            title: Section title
            filename: Source filename

        Returns:
            Dictionary with text and metadata
        """
        text = '\n\n'.join(paragraphs)
        word_count = len(text.split())

        return {
            'text': text,
            'metadata': {
                'chapter': chapter,
                'section': section,
                'title': title,
                'filename': filename,
                'word_count': word_count
            }
        }


class ContentIngester:
    """
    Ingests markdown files into the vector store.
    """

    def __init__(self, data_dir: str = "./data/sample", chroma_db_path: str = "./data/chroma_db"):
        """
        Initialize ingester.

        Args:
            data_dir: Directory containing markdown files
            chroma_db_path: Path to ChromaDB storage
        """
        self.data_dir = Path(data_dir)
        self.chroma_db_path = chroma_db_path

        # Initialize components
        self.chunker = ContentChunker(min_words=300, max_words=800)
        self.vector_store = VectorStore(persist_directory=chroma_db_path)

        logger.info(f"Initialized ContentIngester with data_dir: {data_dir}")

    def ingest_all(self, reset: bool = False) -> None:
        """
        Ingest all markdown files from data directory.

        Args:
            reset: If True, reset vector store before ingesting
        """
        logger.info("Starting content ingestion")

        # Reset if requested
        if reset:
            logger.warning("Resetting vector store")
            self.vector_store.reset()

        # Initialize collection
        embedding_function = get_embedding_function()
        self.vector_store.initialize_collection(embedding_function)

        # Find all markdown files
        md_files = list(self.data_dir.glob("*.md"))

        if not md_files:
            logger.warning(f"No markdown files found in {self.data_dir}")
            return

        logger.info(f"Found {len(md_files)} markdown files")

        # Process each file
        all_chunks = []
        for md_file in md_files:
            logger.info(f"Processing {md_file.name}")

            try:
                # Read file (UTF-8 for Icelandic characters)
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Chunk content
                chunks = self.chunker.chunk_markdown(content, md_file.name)
                all_chunks.extend(chunks)

            except Exception as e:
                logger.error(f"Error processing {md_file.name}: {e}")
                continue

        if not all_chunks:
            logger.warning("No chunks created from files")
            return

        logger.info(f"Total chunks to ingest: {len(all_chunks)}")

        # Prepare data for vector store
        documents = [chunk['text'] for chunk in all_chunks]
        metadatas = [chunk['metadata'] for chunk in all_chunks]
        ids = [f"chunk_{i}" for i in range(len(all_chunks))]

        # Add to vector store (embeddings generated automatically)
        try:
            logger.info("Adding chunks to vector store (generating embeddings)...")
            self.vector_store.add_documents(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            logger.info("Ingestion complete!")

            # Show statistics
            stats = self.vector_store.get_stats()
            logger.info(f"Database statistics: {stats}")

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    def ingest_file(self, filepath: str) -> None:
        """
        Ingest a single markdown file.

        Args:
            filepath: Path to markdown file
        """
        logger.info(f"Ingesting single file: {filepath}")

        # Initialize collection
        embedding_function = get_embedding_function()
        self.vector_store.initialize_collection(embedding_function)

        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Chunk content
        chunks = self.chunker.chunk_markdown(content, Path(filepath).name)

        if not chunks:
            logger.warning("No chunks created")
            return

        # Prepare data
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]

        # Generate unique IDs based on existing count
        stats = self.vector_store.get_stats()
        start_id = stats['total_chunks']
        ids = [f"chunk_{start_id + i}" for i in range(len(chunks))]

        # Add to vector store
        self.vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"Ingested {len(chunks)} chunks from {filepath}")


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Ingest chemistry content into vector database"
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='./data/sample',
        help='Directory containing markdown files'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        default='./data/chroma_db',
        help='Path to ChromaDB storage'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset database before ingesting'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Ingest a single file instead of directory'
    )

    args = parser.parse_args()

    # Initialize ingester
    ingester = ContentIngester(
        data_dir=args.data_dir,
        chroma_db_path=args.db_path
    )

    # Ingest content
    try:
        if args.file:
            ingester.ingest_file(args.file)
        else:
            ingester.ingest_all(reset=args.reset)

        logger.info("Ingestion successful!")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise


if __name__ == "__main__":
    main()
