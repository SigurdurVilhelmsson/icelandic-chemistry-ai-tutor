#!/usr/bin/env python3
"""
Batch Ingestion Script for OpenStax Chemistry Content
Processes markdown files and stores them in Chroma DB with embeddings.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from tqdm import tqdm
import time

# Import local modules
from content_processor import ContentProcessor, ProcessedChunk
from chapter_validator import ChapterValidator

# Optional imports with fallbacks
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: chromadb not installed. Install with: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Install with: pip install sentence-transformers")


@dataclass
class ProcessingStats:
    """Statistics for batch processing"""
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    total_chunks: int = 0
    total_words: int = 0
    skipped_files: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return 0.0

    def format_elapsed_time(self) -> str:
        """Format elapsed time as human readable string"""
        seconds = self.elapsed_time()
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        d = asdict(self)
        d['elapsed_time'] = self.format_elapsed_time()
        return d


@dataclass
class ProcessingError:
    """Represents a processing error"""
    filepath: str
    error_type: str
    error_message: str
    timestamp: str

    def to_dict(self) -> Dict:
        return asdict(self)


class BatchIngestor:
    """Batch processor for OpenStax Chemistry content"""

    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        batch_size: int = 100,
        collection_name: str = "chemistry_chapters",
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        validate: bool = True,
        verbose: bool = False
    ):
        """
        Initialize batch ingestor

        Args:
            input_dir: Directory containing markdown files
            output_dir: Directory for Chroma DB
            batch_size: Number of chunks to process at once
            collection_name: Name of Chroma collection
            embedding_model: Name of sentence-transformers model
            validate: Whether to validate files before processing
            verbose: Enable verbose logging
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.batch_size = batch_size
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        self.validate = validate
        self.verbose = verbose

        # Initialize components
        self.processor = ContentProcessor()
        self.validator = ChapterValidator() if validate else None

        # Statistics and errors
        self.stats = ProcessingStats()
        self.errors: List[ProcessingError] = []

        # Setup logging
        self._setup_logging()

        # Initialize embeddings and database
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None

        if EMBEDDINGS_AVAILABLE:
            self.logger.info(f"Loading embedding model: {embedding_model}")
            self.embedding_model = SentenceTransformer(embedding_model)
        else:
            self.logger.warning("Sentence transformers not available - running in dry-run mode")

        if CHROMADB_AVAILABLE:
            self._init_chromadb()
        else:
            self.logger.warning("ChromaDB not available - running in dry-run mode")

    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = logging.DEBUG if self.verbose else logging.INFO

        # Create logs directory
        log_dir = Path("data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"ingest_{timestamp}.log"

        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.log_file = log_file
        self.logger.info(f"Logging to: {log_file}")

    def _init_chromadb(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # Initialize client
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.output_dir),
                settings=Settings(anonymized_telemetry=False)
            )

            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Icelandic Chemistry OpenStax content"}
            )

            self.logger.info(f"ChromaDB initialized at: {self.output_dir}")
            self.logger.info(f"Collection: {self.collection_name}")

        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in input directory"""
        self.logger.info(f"Scanning for markdown files in: {self.input_dir}")

        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {self.input_dir}")

        # Find all .md files recursively
        md_files = list(self.input_dir.glob("**/*.md"))

        self.logger.info(f"Found {len(md_files)} markdown files")
        return md_files

    def process_file(self, filepath: Path) -> Optional[List[ProcessedChunk]]:
        """
        Process a single markdown file

        Args:
            filepath: Path to markdown file

        Returns:
            List of ProcessedChunk objects or None if processing failed
        """
        self.logger.info(f"Processing: {filepath}")

        try:
            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Validate if enabled
            if self.validate:
                validation_result = self.validator.validate_content(content, str(filepath))

                if not validation_result.valid:
                    self.logger.error(f"Validation failed for {filepath}")
                    for error in validation_result.errors:
                        self.logger.error(f"  - {error}")

                    # Record error
                    self._record_error(
                        filepath=str(filepath),
                        error_type="ValidationError",
                        error_message="; ".join(validation_result.errors)
                    )
                    return None

                # Log warnings
                for warning in validation_result.warnings:
                    self.logger.warning(f"  {warning}")

            # Process content into chunks
            chunks = self.processor.process_file(content, str(filepath))

            self.logger.info(f"Created {len(chunks)} chunks from {filepath}")
            return chunks

        except Exception as e:
            self.logger.error(f"Error processing {filepath}: {e}", exc_info=True)
            self._record_error(
                filepath=str(filepath),
                error_type=type(e).__name__,
                error_message=str(e)
            )
            return None

    def _record_error(self, filepath: str, error_type: str, error_message: str):
        """Record a processing error"""
        error = ProcessingError(
            filepath=filepath,
            error_type=error_type,
            error_message=error_message,
            timestamp=datetime.now().isoformat()
        )
        self.errors.append(error)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        if not self.embedding_model:
            # Return dummy embeddings if model not available
            self.logger.warning("No embedding model - returning dummy embeddings")
            return [[0.0] * 384 for _ in texts]

        try:
            embeddings = self.embedding_model.encode(
                texts,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embeddings.tolist()

        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}")
            raise

    def store_chunks(self, chunks: List[ProcessedChunk]):
        """
        Store chunks in ChromaDB with embeddings

        Args:
            chunks: List of ProcessedChunk objects
        """
        if not chunks:
            return

        if not self.collection:
            self.logger.warning("No ChromaDB collection - skipping storage")
            return

        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]

            # Extract content and metadata
            texts = [chunk.content for chunk in batch]
            metadatas = [chunk.metadata.to_dict() for chunk in batch]

            # Generate IDs (chapter_section_chunk format)
            ids = [
                f"ch{chunk.metadata.chapter_number}_"
                f"sec{chunk.metadata.section_number}_"
                f"chunk{chunk.metadata.chunk_index}"
                for chunk in batch
            ]

            try:
                # Generate embeddings
                self.logger.debug(f"Generating embeddings for batch of {len(batch)} chunks")
                embeddings = self.generate_embeddings(texts)

                # Store in ChromaDB
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas
                )

                self.logger.debug(f"Stored batch of {len(batch)} chunks")

            except Exception as e:
                self.logger.error(f"Error storing batch: {e}", exc_info=True)
                raise

    def process_all(self) -> ProcessingStats:
        """
        Process all markdown files in input directory

        Returns:
            ProcessingStats object
        """
        self.stats.start_time = time.time()

        # Find all markdown files
        md_files = self.find_markdown_files()
        self.stats.total_files = len(md_files)

        if self.stats.total_files == 0:
            self.logger.warning("No markdown files found")
            self.stats.end_time = time.time()
            return self.stats

        # Process each file with progress bar
        self.logger.info(f"Processing {self.stats.total_files} files...")

        all_chunks = []

        for filepath in tqdm(md_files, desc="Processing files", unit="file"):
            chunks = self.process_file(filepath)

            if chunks:
                all_chunks.extend(chunks)
                self.stats.processed_files += 1
                self.stats.total_chunks += len(chunks)
                self.stats.total_words += sum(c.metadata.word_count for c in chunks)
            else:
                self.stats.failed_files += 1

        # Store all chunks in batches
        if all_chunks:
            self.logger.info(f"Storing {len(all_chunks)} chunks in ChromaDB...")

            # Progress bar for storage
            for i in tqdm(
                range(0, len(all_chunks), self.batch_size),
                desc="Storing chunks",
                unit="batch"
            ):
                batch = all_chunks[i:i + self.batch_size]
                self.store_chunks(batch)

        self.stats.end_time = time.time()
        return self.stats

    def generate_summary_report(self) -> str:
        """Generate a summary report of processing"""
        lines = [
            "\n" + "="*60,
            "BATCH PROCESSING SUMMARY",
            "="*60,
            f"Files processed: {self.stats.processed_files}/{self.stats.total_files}",
            f"Failed files: {self.stats.failed_files}",
            f"Skipped files: {self.stats.skipped_files}",
            f"Total chunks: {self.stats.total_chunks}",
            f"Total words: {self.stats.total_words:,}",
            f"Time taken: {self.stats.format_elapsed_time()}",
            "="*60
        ]

        if self.errors:
            lines.append(f"\nErrors: {len(self.errors)}")
            lines.append("-"*60)
            for error in self.errors[:10]:  # Show first 10 errors
                lines.append(f"  {error.filepath}")
                lines.append(f"    {error.error_type}: {error.error_message}")

            if len(self.errors) > 10:
                lines.append(f"  ... and {len(self.errors) - 10} more errors")
                lines.append(f"  See error log for full details")

        return "\n".join(lines)

    def save_error_report(self):
        """Save detailed error report to JSON file"""
        if not self.errors:
            return

        log_dir = Path("data/logs")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_file = log_dir / f"errors_{timestamp}.json"

        error_data = {
            "timestamp": timestamp,
            "total_errors": len(self.errors),
            "errors": [error.to_dict() for error in self.errors]
        }

        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Error report saved to: {error_file}")

    def save_stats_report(self):
        """Save processing statistics to JSON file"""
        log_dir = Path("data/logs")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stats_file = log_dir / f"stats_{timestamp}.json"

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats.to_dict(), f, indent=2, ensure_ascii=False)

        self.logger.info(f"Statistics saved to: {stats_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Batch ingest OpenStax Chemistry markdown content into ChromaDB"
    )

    parser.add_argument(
        "--input",
        type=str,
        default="data/chapters",
        help="Input directory containing markdown files (default: data/chapters)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="chroma_db",
        help="Output directory for ChromaDB (default: chroma_db)"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for processing chunks (default: 100)"
    )

    parser.add_argument(
        "--collection",
        type=str,
        default="chemistry_chapters",
        help="ChromaDB collection name (default: chemistry_chapters)"
    )

    parser.add_argument(
        "--embedding-model",
        type=str,
        default="paraphrase-multilingual-MiniLM-L12-v2",
        help="Sentence transformer model for embeddings"
    )

    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation step"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Create ingestor
    ingestor = BatchIngestor(
        input_dir=args.input,
        output_dir=args.output,
        batch_size=args.batch_size,
        collection_name=args.collection,
        embedding_model=args.embedding_model,
        validate=not args.no_validate,
        verbose=args.verbose
    )

    # Process all files
    try:
        stats = ingestor.process_all()

        # Generate and print summary
        summary = ingestor.generate_summary_report()
        print(summary)

        # Save reports
        ingestor.save_stats_report()
        if ingestor.errors:
            ingestor.save_error_report()

        # Exit with appropriate code
        sys.exit(0 if stats.failed_files == 0 else 1)

    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        sys.exit(130)

    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
