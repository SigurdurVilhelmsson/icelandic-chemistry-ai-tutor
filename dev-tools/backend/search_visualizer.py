#!/usr/bin/env python3
"""
Search Visualizer
=================
Terminal-based visualization of vector search results.

Usage:
    python dev-tools/backend/search_visualizer.py "query text"
    python dev-tools/backend/search_visualizer.py  # Interactive mode

Features:
- Visualize similarity scores with bar charts
- Show chunk metadata and distribution
- Compare different search parameters
- View embedding dimensions
- Analyze result patterns by chapter/section
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from src.vector_store import VectorStore
from src.embeddings import EmbeddingGenerator


class SearchVisualizer:
    """Visualize vector search results in the terminal."""

    def __init__(self, db_path: str = None):
        """Initialize the visualizer."""
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / "backend" / "data" / "chroma_db")

        self.db_path = db_path
        self.vector_store = None
        self.embedding_gen = None
        self.terminal_width = 70

    def initialize(self):
        """Initialize components."""
        print("Initializing search visualizer...")
        try:
            self.vector_store = VectorStore(persist_directory=self.db_path)
            self.embedding_gen = EmbeddingGenerator()
            print("✓ Visualizer initialized\n")
        except Exception as e:
            print(f"✗ Failed to initialize: {e}\n")
            sys.exit(1)

    def visualize_search(self, query: str, n_results: int = 10, threshold: float = 0.0):
        """
        Visualize search results for a query.

        Args:
            query: Search query
            n_results: Number of results to retrieve
            threshold: Minimum similarity threshold (0-1)
        """
        print("\n" + "="*self.terminal_width)
        print("Search Results Visualization".center(self.terminal_width))
        print("="*self.terminal_width)
        print(f"\nQuery: \"{query}\"")

        # Generate and show embedding info
        try:
            embeddings = self.embedding_gen.generate_embeddings([query])
            embedding = embeddings[0] if embeddings else None

            if embedding:
                print(f"\nQuery embedding: {len(embedding)} dimensions")
                # Show first few dimensions as preview
                preview = ", ".join([f"{x:.3f}" for x in embedding[:5]])
                print(f"First 5 dimensions: [{preview}, ...]")
        except Exception as e:
            print(f"\n✗ Error generating embedding: {e}")
            return

        # Perform search
        try:
            results = self.vector_store.search(query, n_results=n_results)
        except Exception as e:
            print(f"\n✗ Error performing search: {e}")
            return

        # Extract results
        documents = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0]
        ids = results.get('ids', [[]])[0]

        if not documents:
            print("\n✗ No results found")
            return

        # Convert distances to similarity scores
        similarities = [1 / (1 + dist) for dist in distances]

        # Filter by threshold
        filtered_results = [
            (sim, doc, meta, chunk_id)
            for sim, doc, meta, chunk_id in zip(similarities, documents, metadatas, ids)
            if sim >= threshold
        ]

        if not filtered_results:
            print(f"\n✗ No results above threshold {threshold:.2f}")
            return

        print(f"\n\nResults (by similarity):")
        print("-"*self.terminal_width)

        # Display each result with bar chart
        max_bar_width = 50
        for i, (sim, doc, meta, chunk_id) in enumerate(filtered_results, 1):
            # Calculate bar length
            bar_length = int(sim * max_bar_width)
            bar = "█" * bar_length

            # Get metadata
            chapter = meta.get('chapter', 'N/A')
            section = meta.get('section', 'N/A')
            title = meta.get('title', 'N/A')

            # Display
            print(f"\n{i}. {bar} ({sim:.2f})")
            print(f"   Chapter {chapter}, Section {section}: {title}")
            print(f"   ID: {chunk_id}")

            # Show preview
            preview_length = 100
            preview = doc[:preview_length]
            if len(doc) > preview_length:
                preview += "..."
            print(f"   Preview: {preview}")

        # Show metadata distribution
        print("\n" + "="*self.terminal_width)
        print("Metadata Distribution")
        print("="*self.terminal_width)

        # Chapter distribution
        chapters = [meta.get('chapter', 'N/A') for _, _, meta, _ in filtered_results]
        chapter_counts = Counter(chapters)

        print("\nChapter distribution:")
        max_count = max(chapter_counts.values()) if chapter_counts else 1
        for chapter, count in sorted(chapter_counts.items()):
            bar_length = int((count / max_count) * 30)
            bar = "█" * bar_length
            print(f"  Chapter {chapter}: {bar} {count} chunk(s)")

        # Section distribution
        sections = [meta.get('section', 'N/A') for _, _, meta, _ in filtered_results]
        section_counts = Counter(sections)

        if len(section_counts) > 1:
            print("\nSection distribution:")
            max_count = max(section_counts.values())
            for section, count in sorted(section_counts.items())[:10]:  # Show top 10
                bar_length = int((count / max_count) * 30)
                bar = "█" * bar_length
                print(f"  Section {section}: {bar} {count} chunk(s)")

        # Score distribution
        print("\nScore distribution:")
        score_ranges = [
            ("0.9-1.0 (Excellent)", 0.9, 1.0),
            ("0.8-0.9 (Very Good)", 0.8, 0.9),
            ("0.7-0.8 (Good)", 0.7, 0.8),
            ("0.6-0.7 (Fair)", 0.6, 0.7),
            ("0.0-0.6 (Poor)", 0.0, 0.6),
        ]

        for label, min_score, max_score in score_ranges:
            count = sum(1 for sim, _, _, _ in filtered_results if min_score <= sim < max_score)
            if count > 0:
                bar_length = int((count / len(filtered_results)) * 30)
                bar = "█" * bar_length
                print(f"  {label}: {bar} {count}")

        # Summary statistics
        print("\n" + "="*self.terminal_width)
        print("Summary Statistics")
        print("="*self.terminal_width)
        print(f"Total results: {len(filtered_results)}")
        print(f"Average similarity: {sum(sim for sim, _, _, _ in filtered_results) / len(filtered_results):.3f}")
        print(f"Max similarity: {max(sim for sim, _, _, _ in filtered_results):.3f}")
        print(f"Min similarity: {min(sim for sim, _, _, _ in filtered_results):.3f}")

        # Calculate average words per chunk
        total_words = sum(meta.get('word_count', 0) for _, _, meta, _ in filtered_results)
        avg_words = total_words / len(filtered_results) if filtered_results else 0
        print(f"Average words per chunk: {avg_words:.0f}")

        print("\n")

    def compare_queries(self, queries: List[str], n_results: int = 5):
        """
        Compare search results for multiple queries.

        Args:
            queries: List of queries to compare
            n_results: Number of results per query
        """
        print("\n" + "="*self.terminal_width)
        print("Query Comparison".center(self.terminal_width))
        print("="*self.terminal_width + "\n")

        all_results = {}

        for query in queries:
            try:
                results = self.vector_store.search(query, n_results=n_results)
                documents = results.get('documents', [[]])[0]
                distances = results.get('distances', [[]])[0]
                metadatas = results.get('metadatas', [[]])[0]

                similarities = [1 / (1 + dist) for dist in distances]
                all_results[query] = {
                    'similarities': similarities,
                    'documents': documents,
                    'metadatas': metadatas,
                    'avg_similarity': sum(similarities) / len(similarities) if similarities else 0
                }
            except Exception as e:
                print(f"✗ Error searching '{query}': {e}")
                continue

        # Display comparison
        for query, data in all_results.items():
            print(f"\nQuery: \"{query}\"")
            print(f"Average similarity: {data['avg_similarity']:.3f}")

            # Bar chart
            max_bar_width = 40
            bar_length = int(data['avg_similarity'] * max_bar_width)
            bar = "█" * bar_length
            print(f"{bar}")

            # Show top result
            if data['similarities']:
                top_meta = data['metadatas'][0]
                print(f"Top result: Chapter {top_meta.get('chapter')}, Section {top_meta.get('section')}")

        print("\n")

    def interactive_mode(self):
        """Run in interactive mode."""
        self.clear_screen()
        print("="*self.terminal_width)
        print("Search Visualizer - Interactive Mode".center(self.terminal_width))
        print("="*self.terminal_width)
        print()

        self.initialize()

        while True:
            print("\n[Options]")
            print("  s - Search and visualize")
            print("  c - Compare multiple queries")
            print("  t - Try different parameters")
            print("  q - Quit")

            choice = input("\nEnter choice: ").strip().lower()

            if choice == 'q':
                print("\nGoodbye!\n")
                break
            elif choice == 's':
                query = input("\nEnter search query: ").strip()
                if query:
                    self.visualize_search(query)
            elif choice == 'c':
                print("\nEnter queries to compare (one per line, empty line to finish):")
                queries = []
                while True:
                    query = input(f"Query {len(queries) + 1}: ").strip()
                    if not query:
                        break
                    queries.append(query)

                if len(queries) >= 2:
                    self.compare_queries(queries)
                else:
                    print("Need at least 2 queries to compare")
            elif choice == 't':
                query = input("\nEnter search query: ").strip()
                if query:
                    try:
                        n_results = int(input("Number of results (default 10): ").strip() or "10")
                        threshold = float(input("Similarity threshold 0-1 (default 0.0): ").strip() or "0.0")
                        self.visualize_search(query, n_results=n_results, threshold=threshold)
                    except ValueError:
                        print("Invalid parameters. Using defaults.")
                        self.visualize_search(query)
            else:
                print("\nInvalid choice. Try again.")

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name != 'nt' else 'cls')


def main():
    """Main entry point."""
    visualizer = SearchVisualizer()

    # Check if query provided as argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        visualizer.initialize()
        visualizer.visualize_search(query)
    else:
        # Interactive mode
        visualizer.interactive_mode()


if __name__ == "__main__":
    main()
