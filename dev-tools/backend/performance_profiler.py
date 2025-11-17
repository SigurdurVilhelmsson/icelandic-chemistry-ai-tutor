#!/usr/bin/env python3
"""
Performance Profiler
====================
Profile the RAG pipeline to identify bottlenecks and slow operations.

Usage:
    python dev-tools/backend/performance_profiler.py
    python dev-tools/backend/performance_profiler.py --queries 20
    python dev-tools/backend/performance_profiler.py --file test_queries.txt

Features:
- Profile complete RAG pipeline execution
- Break down time spent in each stage
- Identify bottlenecks
- Compare performance across queries
- Export profiling results
- Provide optimization recommendations
"""

import sys
import time
import statistics
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from src.rag_pipeline import RAGPipeline
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore
from src.llm_client import ClaudeClient


@dataclass
class QueryProfile:
    """Profile data for a single query."""
    query: str
    total_time: float
    embedding_time: float
    search_time: float
    context_prep_time: float
    llm_time: float
    citation_time: float
    tokens_used: int
    chunks_retrieved: int


class PerformanceProfiler:
    """Profile RAG pipeline performance."""

    def __init__(self, db_path: str = None):
        """Initialize the profiler."""
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / "backend" / "data" / "chroma_db")

        self.db_path = db_path
        self.pipeline = None
        self.profiles: List[QueryProfile] = []

    def initialize(self):
        """Initialize the RAG pipeline."""
        print("Initializing RAG pipeline...")
        try:
            self.pipeline = RAGPipeline(chroma_db_path=self.db_path)
            print("✓ Pipeline initialized\n")
        except Exception as e:
            print(f"✗ Failed to initialize: {e}\n")
            sys.exit(1)

    def profile_query(self, query: str, verbose: bool = False) -> QueryProfile:
        """
        Profile a single query through the pipeline.

        Args:
            query: The query to profile
            verbose: Print detailed timing info

        Returns:
            QueryProfile with timing data
        """
        if verbose:
            print(f"\nProfiling: \"{query}\"")

        total_start = time.time()

        # Stage 1: Generate embedding
        embedding_start = time.time()
        try:
            embedding_gen = EmbeddingGenerator()
            embeddings = embedding_gen.generate_embeddings([query])
            embedding = embeddings[0] if embeddings else None
        except Exception as e:
            if verbose:
                print(f"  ✗ Embedding failed: {e}")
            embedding = None
        embedding_time = time.time() - embedding_start

        # Stage 2: Vector search
        search_start = time.time()
        try:
            search_results = self.pipeline.vector_store.search(query, n_results=5)
            chunks_retrieved = len(search_results.get('documents', [[]])[0])
        except Exception as e:
            if verbose:
                print(f"  ✗ Search failed: {e}")
            search_results = None
            chunks_retrieved = 0
        search_time = time.time() - search_start

        # Stage 3: Context preparation
        context_start = time.time()
        context_chunks = []
        if search_results:
            documents = search_results.get('documents', [[]])[0]
            metadatas = search_results.get('metadatas', [[]])[0]

            for doc, meta in zip(documents[:4], metadatas[:4]):
                context_chunks.append({
                    'document': doc,
                    'metadata': meta
                })
        context_prep_time = time.time() - context_start

        # Stage 4: LLM call
        llm_start = time.time()
        tokens_used = 0
        try:
            if context_chunks:
                result = self.pipeline.llm_client.generate_answer(query, context_chunks, max_chunks=4)
                tokens_used = result.get('tokens_used', {}).get('total', 0)
        except Exception as e:
            if verbose:
                print(f"  ✗ LLM call failed: {e}")
        llm_time = time.time() - llm_start

        # Stage 5: Citation generation (included in LLM time)
        citation_time = 0  # Citations are generated as part of LLM response

        total_time = time.time() - total_start

        profile = QueryProfile(
            query=query,
            total_time=total_time,
            embedding_time=embedding_time,
            search_time=search_time,
            context_prep_time=context_prep_time,
            llm_time=llm_time,
            citation_time=citation_time,
            tokens_used=tokens_used,
            chunks_retrieved=chunks_retrieved
        )

        if verbose:
            print(f"  Total time: {total_time:.2f}s")

        return profile

    def profile_queries(self, queries: List[str], verbose: bool = False) -> List[QueryProfile]:
        """
        Profile multiple queries.

        Args:
            queries: List of queries to profile
            verbose: Print progress

        Returns:
            List of QueryProfile objects
        """
        print(f"\nProfiling {len(queries)} queries...")
        print("="*70 + "\n")

        self.profiles = []

        for i, query in enumerate(queries, 1):
            if verbose:
                print(f"[{i}/{len(queries)}] ", end="")

            profile = self.profile_query(query, verbose=verbose)
            self.profiles.append(profile)

        print("\n✓ Profiling complete\n")
        return self.profiles

    def analyze_results(self):
        """Analyze profiling results and show summary."""
        if not self.profiles:
            print("No profiles to analyze. Run profiling first.\n")
            return

        print("="*70)
        print("Performance Analysis".center(70))
        print("="*70 + "\n")

        # Calculate averages
        avg_total = statistics.mean(p.total_time for p in self.profiles)
        avg_embedding = statistics.mean(p.embedding_time for p in self.profiles)
        avg_search = statistics.mean(p.search_time for p in self.profiles)
        avg_context = statistics.mean(p.context_prep_time for p in self.profiles)
        avg_llm = statistics.mean(p.llm_time for p in self.profiles)
        avg_citation = statistics.mean(p.citation_time for p in self.profiles)

        print(f"Average response time: {avg_total:.2f}s")
        print(f"  (based on {len(self.profiles)} queries)\n")

        # Breakdown
        print("Time breakdown:")
        print(f"  - Embedding generation: {avg_embedding:.2f}s ({avg_embedding/avg_total*100:.0f}%)")
        print(f"  - Vector search:        {avg_search:.2f}s ({avg_search/avg_total*100:.0f}%)")
        print(f"  - Context preparation:  {avg_context:.2f}s ({avg_context/avg_total*100:.0f}%)")
        print(f"  - LLM call:             {avg_llm:.2f}s ({avg_llm/avg_total*100:.0f}%)")
        print(f"  - Citation generation:  {avg_citation:.2f}s ({avg_citation/avg_total*100:.0f}%)")

        # Visual bar chart
        print("\nVisual breakdown:")
        max_width = 50
        bars = [
            ("Embedding", avg_embedding),
            ("Search", avg_search),
            ("Context", avg_context),
            ("LLM", avg_llm),
            ("Citations", avg_citation)
        ]

        for label, time_val in bars:
            bar_width = int((time_val / avg_total) * max_width)
            bar = "█" * bar_width
            print(f"  {label:<12} {bar} {time_val:.2f}s")

        # Identify bottleneck
        print("\n" + "-"*70)
        bottleneck = max(bars, key=lambda x: x[1])
        print(f"Bottleneck: {bottleneck[0]} ({bottleneck[1]:.2f}s)")

        # Recommendations
        self._provide_recommendations(bottleneck[0], avg_total, avg_llm, avg_embedding, avg_search)

        # Statistics
        print("\n" + "="*70)
        print("Statistics".center(70))
        print("="*70 + "\n")

        print(f"Total queries profiled: {len(self.profiles)}")
        print(f"Fastest query: {min(p.total_time for p in self.profiles):.2f}s")
        print(f"Slowest query: {max(p.total_time for p in self.profiles):.2f}s")

        if len(self.profiles) > 1:
            stdev = statistics.stdev(p.total_time for p in self.profiles)
            print(f"Standard deviation: {stdev:.2f}s")

        # Token usage
        total_tokens = sum(p.tokens_used for p in self.profiles)
        avg_tokens = statistics.mean(p.tokens_used for p in self.profiles) if self.profiles else 0
        print(f"\nAverage tokens per query: {avg_tokens:.0f}")
        print(f"Total tokens used: {total_tokens:,}")

        # Chunks retrieved
        avg_chunks = statistics.mean(p.chunks_retrieved for p in self.profiles) if self.profiles else 0
        print(f"Average chunks retrieved: {avg_chunks:.1f}")

        print("\n")

    def _provide_recommendations(
        self,
        bottleneck: str,
        avg_total: float,
        avg_llm: float,
        avg_embedding: float,
        avg_search: float
    ):
        """Provide optimization recommendations based on bottleneck."""
        print("\n" + "="*70)
        print("Recommendations".center(70))
        print("="*70 + "\n")

        if bottleneck == "LLM" and avg_llm > 1.0:
            print("💡 LLM calls are the main bottleneck:")
            print("   - Consider caching common queries")
            print("   - Reduce context size (fewer chunks)")
            print("   - Use shorter max_tokens setting")
            print("   - Implement streaming responses for better UX")

        elif bottleneck == "Embedding" and avg_embedding > 0.5:
            print("💡 Embedding generation is slow:")
            print("   - Consider caching embeddings for common queries")
            print("   - Batch multiple queries if possible")
            print("   - Check network latency to OpenAI API")

        elif bottleneck == "Search" and avg_search > 0.3:
            print("💡 Vector search is slow:")
            print("   - Consider reducing n_results parameter")
            print("   - Optimize ChromaDB configuration")
            print("   - Check if database is too large")
            print("   - Consider using approximate search")

        elif bottleneck == "Context":
            print("💡 Context preparation is slow:")
            print("   - Reduce number of chunks included")
            print("   - Optimize chunk formatting logic")

        else:
            print("✓ Performance is well-balanced!")
            print("  No major bottlenecks detected.")

        # General recommendations
        if avg_total > 3.0:
            print("\n⚠️  Overall response time is slow (>3s):")
            print("   - Consider implementing response caching")
            print("   - Add loading indicators in UI")
            print("   - Profile API latency separately")

    def show_detailed_breakdown(self):
        """Show detailed breakdown for each query."""
        if not self.profiles:
            print("No profiles to show. Run profiling first.\n")
            return

        print("\n" + "="*70)
        print("Detailed Breakdown Per Query".center(70))
        print("="*70 + "\n")

        for i, profile in enumerate(self.profiles, 1):
            print(f"Query {i}: {profile.total_time:.2f}s")
            print(f'  "{profile.query[:60]}..."')
            print(f"  - Embedding:  {profile.embedding_time:.2f}s")
            print(f"  - Search:     {profile.search_time:.2f}s")
            print(f"  - Context:    {profile.context_prep_time:.2f}s")
            print(f"  - LLM:        {profile.llm_time:.2f}s")
            print(f"  - Tokens:     {profile.tokens_used:,}")
            print(f"  - Chunks:     {profile.chunks_retrieved}")
            print()

    def export_results(self, filename: str):
        """Export profiling results to JSON."""
        if not self.profiles:
            print("No profiles to export. Run profiling first.\n")
            return

        filepath = Path(filename)

        try:
            data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'num_queries': len(self.profiles),
                'profiles': [asdict(p) for p in self.profiles],
                'summary': {
                    'avg_total_time': statistics.mean(p.total_time for p in self.profiles),
                    'avg_embedding_time': statistics.mean(p.embedding_time for p in self.profiles),
                    'avg_search_time': statistics.mean(p.search_time for p in self.profiles),
                    'avg_context_time': statistics.mean(p.context_prep_time for p in self.profiles),
                    'avg_llm_time': statistics.mean(p.llm_time for p in self.profiles),
                    'avg_tokens': statistics.mean(p.tokens_used for p in self.profiles),
                    'total_tokens': sum(p.tokens_used for p in self.profiles)
                }
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"\n✓ Results exported to: {filepath.absolute()}\n")
        except Exception as e:
            print(f"\n✗ Export failed: {e}\n")

    def compare_profiles(self, profile_files: List[str]):
        """Compare multiple profiling runs."""
        print("\n" + "="*70)
        print("Profile Comparison".center(70))
        print("="*70 + "\n")

        profiles_data = []

        for filepath in profile_files:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    profiles_data.append((filepath, data))
            except Exception as e:
                print(f"✗ Could not load {filepath}: {e}")

        if len(profiles_data) < 2:
            print("Need at least 2 profiles to compare.\n")
            return

        # Compare
        print(f"{'Profile':<30} {'Avg Time':<12} {'Queries':<10} {'Avg Tokens':<12}")
        print("-"*70)

        for filepath, data in profiles_data:
            name = Path(filepath).stem
            avg_time = data['summary']['avg_total_time']
            num_queries = data['num_queries']
            avg_tokens = data['summary']['avg_tokens']

            print(f"{name[:30]:<30} {avg_time:<12.2f} {num_queries:<10} {avg_tokens:<12.0f}")

        print("\n")


def get_test_queries() -> List[str]:
    """Get a set of test queries."""
    return [
        "Hvað er atóm?",
        "Útskýrðu efnatengi",
        "Hvað er lotukerfið?",
        "Hver er munurinn á jón og atómi?",
        "Hvað eru rafeindirnar?",
        "Útskýrðu kjarneindlíkan Rutherfords",
        "Hvað er efnafræði?",
        "Hvað þýðir atómmassi?",
        "Hvað er efnaformúla?",
        "Hverjir eru fyrstu frumefnin í lotukerfinu?"
    ]


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Profile RAG pipeline performance")
    parser.add_argument('--queries', type=int, default=10,
                        help='Number of test queries to run')
    parser.add_argument('--file', type=str,
                        help='File with queries (one per line)')
    parser.add_argument('--export', type=str,
                        help='Export results to JSON file')
    parser.add_argument('--detailed', action='store_true',
                        help='Show detailed breakdown per query')
    parser.add_argument('--verbose', action='store_true',
                        help='Show progress while profiling')
    parser.add_argument('--compare', nargs='+',
                        help='Compare multiple profile JSON files')

    args = parser.parse_args()

    profiler = PerformanceProfiler()

    # Compare mode
    if args.compare:
        profiler.compare_profiles(args.compare)
        return

    # Load queries
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                queries = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"✗ Could not load queries from file: {e}\n")
            return
    else:
        test_queries = get_test_queries()
        queries = test_queries[:args.queries]

    # Initialize and profile
    profiler.initialize()
    profiler.profile_queries(queries, verbose=args.verbose)

    # Analyze
    profiler.analyze_results()

    if args.detailed:
        profiler.show_detailed_breakdown()

    if args.export:
        profiler.export_results(args.export)


if __name__ == "__main__":
    main()
