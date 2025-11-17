#!/usr/bin/env python3
"""
RAG Pipeline Debugger
=====================
Interactive CLI tool for debugging the RAG pipeline step-by-step.

Usage:
    python dev-tools/backend/rag_debugger.py

Features:
- Step-by-step execution of RAG pipeline
- View retrieved chunks with similarity scores
- Display full context sent to LLM
- Show token counts and API costs
- Export debug logs as JSON
- Compare different search strategies
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from src.rag_pipeline import RAGPipeline
from src.vector_store import VectorStore
from src.llm_client import ClaudeClient
from src.embeddings import EmbeddingGenerator


@dataclass
class DebugStep:
    """Represents a single step in the debug trace."""
    step_number: int
    step_name: str
    timestamp: float
    duration_ms: float
    data: Dict[str, Any]


class RAGDebugger:
    """Interactive debugger for RAG pipeline."""

    def __init__(self, db_path: str = None):
        """Initialize the debugger."""
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / "backend" / "data" / "chroma_db")

        self.db_path = db_path
        self.pipeline = None
        self.debug_trace: List[DebugStep] = []
        self.last_question: Optional[str] = None
        self.last_result: Optional[Dict] = None

        # Pricing (as of Jan 2025)
        self.EMBEDDING_COST_PER_1K = 0.00002  # OpenAI text-embedding-3-small
        self.CLAUDE_INPUT_COST_PER_1M = 3.0    # Claude Sonnet 4
        self.CLAUDE_OUTPUT_COST_PER_1M = 15.0

    def initialize(self):
        """Initialize the RAG pipeline."""
        print("Initializing RAG pipeline...")
        try:
            self.pipeline = RAGPipeline(chroma_db_path=self.db_path)
            print("✓ Pipeline initialized successfully\n")
        except Exception as e:
            print(f"✗ Failed to initialize pipeline: {e}\n")
            sys.exit(1)

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_header(self):
        """Print the debugger header."""
        print("=" * 70)
        print("RAG Pipeline Debugger".center(70))
        print("=" * 70)
        print()

    def debug_question(self, question: str, n_results: int = 5, max_chunks: int = 4) -> Dict:
        """
        Debug a question through the entire RAG pipeline.

        Args:
            question: The question to debug
            n_results: Number of chunks to retrieve
            max_chunks: Maximum chunks to use in context

        Returns:
            Debug result dictionary
        """
        self.debug_trace = []
        self.last_question = question
        start_time = time.time()

        print(f"\n{'='*70}")
        print(f"[DEBUG] Question: {question}")
        print(f"{'='*70}\n")

        # Step 1: Query received
        step_start = time.time()
        self._add_step(1, "Query received", {
            "question": question,
            "question_length": len(question),
            "word_count": len(question.split())
        })
        print(f"[1] Query received: \"{question}\"")
        print(f"    Length: {len(question)} chars, {len(question.split())} words\n")

        # Step 2: Generate embedding
        step_start = time.time()
        try:
            embedding_gen = EmbeddingGenerator()
            embeddings = embedding_gen.generate_embeddings([question])
            embedding = embeddings[0] if embeddings else None
            embedding_tokens = len(question.split()) * 1.3  # Rough estimate
            embedding_cost = (embedding_tokens / 1000) * self.EMBEDDING_COST_PER_1K

            step_duration = (time.time() - step_start) * 1000
            self._add_step(2, "Embedding generated", {
                "dimensions": len(embedding) if embedding else 0,
                "estimated_tokens": int(embedding_tokens),
                "cost_usd": embedding_cost,
                "duration_ms": step_duration
            })
            print(f"[2] Embedding generated")
            print(f"    Dimensions: {len(embedding) if embedding else 0}")
            print(f"    Estimated tokens: {int(embedding_tokens)}")
            print(f"    Cost: ${embedding_cost:.6f}")
            print(f"    Time: {step_duration:.0f}ms\n")
        except Exception as e:
            print(f"[2] ✗ Embedding generation failed: {e}\n")
            return {"error": str(e)}

        # Step 3: Vector search
        step_start = time.time()
        try:
            vector_store = self.pipeline.vector_store
            search_results = vector_store.search(question, n_results=n_results)

            step_duration = (time.time() - step_start) * 1000

            # Process results
            chunks_data = []
            documents = search_results.get('documents', [[]])[0]
            metadatas = search_results.get('metadatas', [[]])[0]
            distances = search_results.get('distances', [[]])[0]
            ids = search_results.get('ids', [[]])[0]

            for i, (doc, meta, dist, chunk_id) in enumerate(zip(documents, metadatas, distances, ids)):
                # Convert distance to similarity score (0-1)
                similarity = 1 / (1 + dist)
                chunks_data.append({
                    "rank": i + 1,
                    "id": chunk_id,
                    "score": similarity,
                    "distance": dist,
                    "chapter": meta.get('chapter', 'N/A'),
                    "section": meta.get('section', 'N/A'),
                    "title": meta.get('title', 'N/A'),
                    "text_preview": doc[:100] + "..." if len(doc) > 100 else doc,
                    "text_full": doc,
                    "word_count": meta.get('word_count', 0)
                })

            self._add_step(3, "Vector search completed", {
                "n_results": len(chunks_data),
                "chunks": chunks_data,
                "duration_ms": step_duration
            })

            print(f"[3] Vector search retrieved {len(chunks_data)} chunks:")
            for chunk in chunks_data:
                print(f"    - Chunk {chunk['rank']} (score: {chunk['score']:.2f})")
                print(f"      Chapter {chunk['chapter']}, Section {chunk['section']}: \"{chunk['title']}\"")
                print(f"      Preview: {chunk['text_preview']}")
                print()
            print(f"    Time: {step_duration:.0f}ms\n")

        except Exception as e:
            print(f"[3] ✗ Vector search failed: {e}\n")
            return {"error": str(e)}

        # Step 4: Prepare context
        step_start = time.time()
        context_chunks = chunks_data[:max_chunks]
        context_text = ""
        for i, chunk in enumerate(context_chunks, 1):
            context_text += f"\n--- Kafli {chunk['chapter']}, Kafli {chunk['section']}: {chunk['title']} ---\n"
            context_text += chunk['text_full']
            context_text += "\n"

        # Estimate tokens (rough: 1 token ≈ 0.75 words for Icelandic)
        context_tokens = int(len(context_text.split()) * 0.75)
        question_tokens = int(len(question.split()) * 0.75)
        system_tokens = 150  # Approximate system prompt size
        total_input_tokens = context_tokens + question_tokens + system_tokens

        step_duration = (time.time() - step_start) * 1000
        self._add_step(4, "Context prepared", {
            "chunks_used": len(context_chunks),
            "estimated_tokens": total_input_tokens,
            "context_length": len(context_text),
            "context_preview": context_text[:200] + "..." if len(context_text) > 200 else context_text
        })

        print(f"[4] Context prepared for Claude")
        print(f"    Chunks used: {len(context_chunks)} of {len(chunks_data)} retrieved")
        print(f"    Estimated tokens: {total_input_tokens:,}")
        print(f"      - Context: {context_tokens:,}")
        print(f"      - Question: {question_tokens}")
        print(f"      - System: {system_tokens}")
        print()

        # Step 5: Call Claude
        step_start = time.time()
        try:
            # Format chunks for pipeline
            formatted_chunks = [
                {
                    'document': chunk['text_full'],
                    'metadata': {
                        'chapter': chunk['chapter'],
                        'section': chunk['section'],
                        'title': chunk['title'],
                        'word_count': chunk['word_count']
                    }
                }
                for chunk in context_chunks
            ]

            llm_client = self.pipeline.llm_client
            answer_data = llm_client.generate_answer(question, formatted_chunks, max_chunks=max_chunks)

            step_duration = (time.time() - step_start) * 1000

            # Calculate costs
            input_tokens = answer_data.get('tokens_used', {}).get('input', total_input_tokens)
            output_tokens = answer_data.get('tokens_used', {}).get('output', 0)
            total_tokens = answer_data.get('tokens_used', {}).get('total', input_tokens + output_tokens)

            input_cost = (input_tokens / 1_000_000) * self.CLAUDE_INPUT_COST_PER_1M
            output_cost = (output_tokens / 1_000_000) * self.CLAUDE_OUTPUT_COST_PER_1M
            total_cost = input_cost + output_cost + embedding_cost

            self._add_step(5, "Claude response received", {
                "answer": answer_data.get('answer', ''),
                "answer_length": len(answer_data.get('answer', '')),
                "citations_count": len(answer_data.get('citations', [])),
                "citations": answer_data.get('citations', []),
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens
                },
                "costs": {
                    "embedding": embedding_cost,
                    "input": input_cost,
                    "output": output_cost,
                    "total": total_cost
                },
                "duration_ms": step_duration,
                "model": answer_data.get('model', 'unknown')
            })

            answer = answer_data.get('answer', '')
            citations = answer_data.get('citations', [])

            print(f"[5] Claude response received")
            print(f"    Answer length: {len(answer)} chars")
            print(f"    Tokens used:")
            print(f"      - Input: {input_tokens:,}")
            print(f"      - Output: {output_tokens:,}")
            print(f"      - Total: {total_tokens:,}")
            print(f"    Time: {step_duration:.0f}ms")
            print()
            print(f"    Answer preview:")
            preview_length = 150
            answer_preview = answer[:preview_length] + "..." if len(answer) > preview_length else answer
            print(f"    \"{answer_preview}\"")
            print()

        except Exception as e:
            print(f"[5] ✗ Claude API call failed: {e}\n")
            return {"error": str(e)}

        # Step 6: Citations
        step_start = time.time()
        print(f"[6] Citations generated: {len(citations)} sources")
        for i, citation in enumerate(citations, 1):
            print(f"    {i}. Chapter {citation.get('chapter')}, Section {citation.get('section')}: {citation.get('title')}")
        print()

        # Summary
        total_time = time.time() - start_time
        print(f"{'='*70}")
        print(f"Summary:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  API costs:")
        print(f"    - Embedding: ${embedding_cost:.6f}")
        print(f"    - Claude input: ${input_cost:.6f}")
        print(f"    - Claude output: ${output_cost:.6f}")
        print(f"    - Total: ${total_cost:.6f}")
        print(f"{'='*70}\n")

        # Store result
        self.last_result = {
            "question": question,
            "answer": answer,
            "citations": citations,
            "chunks_retrieved": chunks_data,
            "chunks_used": context_chunks,
            "tokens": {
                "input": input_tokens,
                "output": output_tokens,
                "total": total_tokens
            },
            "costs": {
                "embedding": embedding_cost,
                "input": input_cost,
                "output": output_cost,
                "total": total_cost
            },
            "total_time_s": total_time,
            "debug_trace": [asdict(step) for step in self.debug_trace]
        }

        return self.last_result

    def _add_step(self, step_number: int, step_name: str, data: Dict[str, Any]):
        """Add a step to the debug trace."""
        if self.debug_trace:
            last_step = self.debug_trace[-1]
            duration = (time.time() - last_step.timestamp) * 1000
        else:
            duration = 0

        step = DebugStep(
            step_number=step_number,
            step_name=step_name,
            timestamp=time.time(),
            duration_ms=duration,
            data=data
        )
        self.debug_trace.append(step)

    def view_full_chunks(self):
        """View full text of all retrieved chunks."""
        if not self.last_result:
            print("No results available. Run a query first.\n")
            return

        print("\n" + "="*70)
        print("Full Chunk Texts")
        print("="*70 + "\n")

        for chunk in self.last_result['chunks_retrieved']:
            print(f"--- Chunk {chunk['rank']} (Score: {chunk['score']:.2f}) ---")
            print(f"Chapter {chunk['chapter']}, Section {chunk['section']}: {chunk['title']}")
            print(f"Words: {chunk['word_count']}")
            print()
            print(chunk['text_full'])
            print("\n" + "-"*70 + "\n")

    def view_full_context(self):
        """View the full context sent to Claude."""
        if not self.last_result:
            print("No results available. Run a query first.\n")
            return

        print("\n" + "="*70)
        print("Full Context Sent to Claude")
        print("="*70 + "\n")

        for i, chunk in enumerate(self.last_result['chunks_used'], 1):
            print(f"\n--- Kafli {chunk['chapter']}, Kafli {chunk['section']}: {chunk['title']} ---\n")
            print(chunk['text_full'])
            print()

    def export_debug_log(self, filename: Optional[str] = None):
        """Export debug log as JSON."""
        if not self.last_result:
            print("No results available. Run a query first.\n")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_debug_{timestamp}.json"

        filepath = Path(filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.last_result, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Debug log exported to: {filepath.absolute()}\n")
        except Exception as e:
            print(f"\n✗ Failed to export: {e}\n")

    def interactive_mode(self):
        """Run the debugger in interactive mode."""
        self.clear_screen()
        self.print_header()
        self.initialize()

        while True:
            if self.last_question:
                print(f"\nLast question: {self.last_question}")

            print("\n[Options]")
            print("  c - Change question / New query")
            print("  v - View full chunk texts")
            print("  x - View full context sent to Claude")
            print("  s - Search with different parameters")
            print("  e - Export debug log (JSON)")
            print("  r - Re-run last question")
            print("  q - Quit")

            choice = input("\nEnter choice: ").strip().lower()

            if choice == 'q':
                print("\nGoodbye!\n")
                break
            elif choice == 'c':
                question = input("\nEnter question: ").strip()
                if question:
                    self.debug_question(question)
            elif choice == 'v':
                self.view_full_chunks()
            elif choice == 'x':
                self.view_full_context()
            elif choice == 's':
                question = input("Question: ").strip()
                if question:
                    try:
                        n_results = int(input("Number of chunks to retrieve (default 5): ").strip() or "5")
                        max_chunks = int(input("Max chunks to use in context (default 4): ").strip() or "4")
                        self.debug_question(question, n_results=n_results, max_chunks=max_chunks)
                    except ValueError:
                        print("Invalid number. Using defaults.\n")
                        self.debug_question(question)
            elif choice == 'e':
                filename = input("Filename (press Enter for auto): ").strip() or None
                self.export_debug_log(filename)
            elif choice == 'r':
                if self.last_question:
                    self.debug_question(self.last_question)
                else:
                    print("\nNo previous question to re-run.\n")
            else:
                print("\nInvalid choice. Try again.\n")


def main():
    """Main entry point."""
    debugger = RAGDebugger()
    debugger.interactive_mode()


if __name__ == "__main__":
    main()
