"""
Database Inspection Utility
CLI tool for inspecting and analyzing ChromaDB content.
"""

import os
import json
import random
import logging
import argparse
from pathlib import Path
from typing import Optional
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


class DatabaseInspector:
    """
    Inspect and analyze ChromaDB vector database.
    """

    def __init__(self, chroma_db_path: str = "./data/chroma_db"):
        """
        Initialize inspector.

        Args:
            chroma_db_path: Path to ChromaDB storage
        """
        self.chroma_db_path = chroma_db_path
        self.vector_store = VectorStore(persist_directory=chroma_db_path)

        # Initialize collection
        try:
            embedding_function = get_embedding_function()
            self.vector_store.initialize_collection(embedding_function)
            logger.info(f"Loaded database from {chroma_db_path}")
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            raise

    def show_stats(self) -> None:
        """Display database statistics."""
        print("\n" + "=" * 60)
        print("DATABASE STATISTICS")
        print("=" * 60)

        try:
            stats = self.vector_store.get_stats()

            print(f"\nTotal chunks: {stats['total_chunks']}")
            print(f"Unique chapters: {stats['unique_chapters']}")
            print(f"Unique sections: {stats['unique_sections']}")

            if stats['chapters']:
                print(f"\nChapters: {', '.join(stats['chapters'])}")

            print("\n" + "=" * 60)

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            print(f"Error: {e}")

    def show_sample(self, n: int = 3) -> None:
        """
        Display random sample chunks.

        Args:
            n: Number of chunks to display
        """
        print("\n" + "=" * 60)
        print(f"RANDOM SAMPLE ({n} chunks)")
        print("=" * 60)

        try:
            # Get all documents
            all_docs = self.vector_store.get_all_documents()

            if not all_docs['ids']:
                print("\nNo documents found in database.")
                return

            # Select random samples
            total = len(all_docs['ids'])
            sample_size = min(n, total)
            indices = random.sample(range(total), sample_size)

            for i, idx in enumerate(indices, 1):
                doc_id = all_docs['ids'][idx]
                document = all_docs['documents'][idx]
                metadata = all_docs['metadatas'][idx]

                print(f"\n--- Chunk {i}/{sample_size} ---")
                print(f"ID: {doc_id}")
                print(f"Chapter: {metadata.get('chapter', 'N/A')}")
                print(f"Section: {metadata.get('section', 'N/A')}")
                print(f"Title: {metadata.get('title', 'N/A')}")
                print(f"Word count: {metadata.get('word_count', 'N/A')}")
                print(f"\nContent preview (first 200 chars):")
                print(document[:200] + "..." if len(document) > 200 else document)

            print("\n" + "=" * 60)

        except Exception as e:
            logger.error(f"Error showing sample: {e}")
            print(f"Error: {e}")

    def search_by_chapter(self, chapter: str) -> None:
        """
        Display all chunks from a specific chapter.

        Args:
            chapter: Chapter number
        """
        print("\n" + "=" * 60)
        print(f"CHUNKS FROM CHAPTER {chapter}")
        print("=" * 60)

        try:
            # Get all documents
            all_docs = self.vector_store.get_all_documents()

            if not all_docs['ids']:
                print("\nNo documents found in database.")
                return

            # Filter by chapter
            chapter_chunks = []
            for i, metadata in enumerate(all_docs['metadatas']):
                if metadata.get('chapter') == chapter:
                    chapter_chunks.append({
                        'id': all_docs['ids'][i],
                        'document': all_docs['documents'][i],
                        'metadata': metadata
                    })

            if not chapter_chunks:
                print(f"\nNo chunks found for chapter {chapter}")
                return

            print(f"\nFound {len(chapter_chunks)} chunks in chapter {chapter}\n")

            for i, chunk in enumerate(chapter_chunks, 1):
                print(f"--- Chunk {i}/{len(chapter_chunks)} ---")
                print(f"ID: {chunk['id']}")
                print(f"Section: {chunk['metadata'].get('section', 'N/A')}")
                print(f"Title: {chunk['metadata'].get('title', 'N/A')}")
                print(f"Word count: {chunk['metadata'].get('word_count', 'N/A')}")
                print(f"\nContent preview:")
                doc = chunk['document']
                print(doc[:300] + "..." if len(doc) > 300 else doc)
                print()

            print("=" * 60)

        except Exception as e:
            logger.error(f"Error searching chapter: {e}")
            print(f"Error: {e}")

    def verify_metadata(self) -> None:
        """Verify metadata integrity."""
        print("\n" + "=" * 60)
        print("METADATA VERIFICATION")
        print("=" * 60)

        try:
            all_docs = self.vector_store.get_all_documents()

            if not all_docs['ids']:
                print("\nNo documents found in database.")
                return

            issues = []
            required_fields = ['chapter', 'section', 'title', 'filename', 'word_count']

            for i, metadata in enumerate(all_docs['metadatas']):
                doc_id = all_docs['ids'][i]

                # Check for missing fields
                for field in required_fields:
                    if field not in metadata:
                        issues.append(f"Chunk {doc_id}: Missing field '{field}'")

                # Validate chapter format
                chapter = metadata.get('chapter')
                if chapter and not str(chapter).isdigit():
                    issues.append(f"Chunk {doc_id}: Invalid chapter format '{chapter}'")

                # Validate section format
                section = metadata.get('section')
                if section and not str(section).isdigit():
                    issues.append(f"Chunk {doc_id}: Invalid section format '{section}'")

            print(f"\nTotal chunks checked: {len(all_docs['ids'])}")

            if issues:
                print(f"\nFound {len(issues)} issues:\n")
                for issue in issues[:10]:  # Show first 10
                    print(f"  - {issue}")
                if len(issues) > 10:
                    print(f"  ... and {len(issues) - 10} more")
            else:
                print("\n✓ All metadata valid!")

            print("\n" + "=" * 60)

        except Exception as e:
            logger.error(f"Error verifying metadata: {e}")
            print(f"Error: {e}")

    def export_to_json(self, output_file: str) -> None:
        """
        Export database to JSON file.

        Args:
            output_file: Path to output JSON file
        """
        print(f"\nExporting database to {output_file}...")

        try:
            all_docs = self.vector_store.get_all_documents()

            if not all_docs['ids']:
                print("No documents to export.")
                return

            # Format data
            export_data = {
                'total_chunks': len(all_docs['ids']),
                'chunks': []
            }

            for i in range(len(all_docs['ids'])):
                chunk_data = {
                    'id': all_docs['ids'][i],
                    'document': all_docs['documents'][i],
                    'metadata': all_docs['metadatas'][i]
                }
                export_data['chunks'].append(chunk_data)

            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            print(f"✓ Exported {len(all_docs['ids'])} chunks to {output_file}")

        except Exception as e:
            logger.error(f"Error exporting: {e}")
            print(f"Error: {e}")


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Inspect ChromaDB vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.inspect_db stats                    # Show statistics
  python -m src.inspect_db sample 5                 # Show 5 random chunks
  python -m src.inspect_db search 1                 # Show all chunks from chapter 1
  python -m src.inspect_db verify                   # Verify metadata integrity
  python -m src.inspect_db export output.json       # Export to JSON
        """
    )

    parser.add_argument(
        'command',
        choices=['stats', 'sample', 'search', 'verify', 'export'],
        help='Command to execute'
    )
    parser.add_argument(
        'argument',
        nargs='?',
        help='Command argument (n for sample, chapter for search, file for export)'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        default='./data/chroma_db',
        help='Path to ChromaDB storage'
    )

    args = parser.parse_args()

    # Initialize inspector
    try:
        inspector = DatabaseInspector(chroma_db_path=args.db_path)
    except Exception as e:
        print(f"Error initializing inspector: {e}")
        return

    # Execute command
    try:
        if args.command == 'stats':
            inspector.show_stats()

        elif args.command == 'sample':
            n = int(args.argument) if args.argument else 3
            inspector.show_sample(n)

        elif args.command == 'search':
            if not args.argument:
                print("Error: Chapter number required for search command")
                return
            inspector.search_by_chapter(args.argument)

        elif args.command == 'verify':
            inspector.verify_metadata()

        elif args.command == 'export':
            if not args.argument:
                print("Error: Output filename required for export command")
                return
            inspector.export_to_json(args.argument)

    except Exception as e:
        print(f"Error executing command: {e}")
        logger.error(f"Command failed: {e}")


if __name__ == "__main__":
    main()
