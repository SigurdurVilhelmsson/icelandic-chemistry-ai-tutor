"""
Integration Tests for RAG Pipeline
Tests Icelandic question answering with proper citations.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestRAGPipeline:
    """
    Test suite for RAG pipeline functionality.
    """

    def __init__(self):
        """Initialize test suite."""
        self.pipeline = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'total': 0
        }

    def setup(self):
        """Setup test environment."""
        logger.info("Setting up test environment")

        try:
            # Initialize RAG pipeline
            self.pipeline = RAGPipeline(
                chroma_db_path="./data/chroma_db",
                top_k=5,
                max_context_chunks=4
            )

            # Check database has content
            stats = self.pipeline.get_pipeline_stats()
            db_chunks = stats['database']['total_chunks']

            if db_chunks == 0:
                raise RuntimeError(
                    "Database is empty. Run ingestion first: "
                    "python -m src.ingest --data-dir ./data/sample"
                )

            logger.info(f"Pipeline initialized with {db_chunks} chunks")

        except Exception as e:
            logger.error(f"Setup failed: {e}")
            raise

    def run_test(self, test_name: str, test_func):
        """
        Run a single test.

        Args:
            test_name: Name of the test
            test_func: Test function to execute
        """
        self.test_results['total'] += 1

        logger.info(f"\n{'='*60}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*60}")

        try:
            test_func()
            self.test_results['passed'] += 1
            logger.info(f"✓ PASSED: {test_name}")

        except AssertionError as e:
            self.test_results['failed'] += 1
            logger.error(f"✗ FAILED: {test_name}")
            logger.error(f"Assertion Error: {e}")

        except Exception as e:
            self.test_results['failed'] += 1
            logger.error(f"✗ FAILED: {test_name}")
            logger.error(f"Error: {e}")

    def test_question_atom(self):
        """Test question about atoms in Icelandic."""
        question = "Hvað er atóm?"

        start_time = time.time()
        result = self.pipeline.ask(question)
        response_time = (time.time() - start_time) * 1000

        # Log response
        logger.info(f"Question: {question}")
        logger.info(f"Answer: {result['answer'][:200]}...")
        logger.info(f"Citations: {len(result['citations'])}")
        logger.info(f"Response time: {response_time:.2f}ms")

        # Assertions
        assert result['answer'], "Answer should not be empty"
        assert len(result['answer']) > 50, "Answer should be substantial"
        assert len(result['citations']) > 0, "Should have citations"
        assert response_time < 5000, f"Response too slow: {response_time}ms"

        # Check for Icelandic content
        icelandic_words = ['atóm', 'efni', 'róteindum', 'rafeind']
        answer_lower = result['answer'].lower()
        found_icelandic = any(word.lower() in answer_lower for word in icelandic_words)
        assert found_icelandic, "Answer should contain Icelandic chemistry terms"

        logger.info("All assertions passed")

    def test_question_chemical_bonds(self):
        """Test question about chemical bonds in Icelandic."""
        question = "Útskýrðu efnatengi"

        start_time = time.time()
        result = self.pipeline.ask(question)
        response_time = (time.time() - start_time) * 1000

        # Log response
        logger.info(f"Question: {question}")
        logger.info(f"Answer: {result['answer'][:200]}...")
        logger.info(f"Citations: {len(result['citations'])}")
        logger.info(f"Response time: {response_time:.2f}ms")

        # Assertions
        assert result['answer'], "Answer should not be empty"
        assert len(result['answer']) > 50, "Answer should be substantial"
        assert len(result['citations']) > 0, "Should have citations"
        assert response_time < 5000, f"Response too slow: {response_time}ms"

        # Check for relevant terms
        relevant_terms = ['tengi', 'atóm', 'rafeind', 'jón']
        answer_lower = result['answer'].lower()
        found_relevant = any(term.lower() in answer_lower for term in relevant_terms)
        assert found_relevant, "Answer should mention chemical bonding concepts"

        logger.info("All assertions passed")

    def test_question_periodic_table(self):
        """Test question about periodic table in Icelandic."""
        question = "Hvað er lotukerfið?"

        start_time = time.time()
        result = self.pipeline.ask(question)
        response_time = (time.time() - start_time) * 1000

        # Log response
        logger.info(f"Question: {question}")
        logger.info(f"Answer: {result['answer'][:200]}...")
        logger.info(f"Citations: {len(result['citations'])}")
        logger.info(f"Response time: {response_time:.2f}ms")

        # Assertions
        assert result['answer'], "Answer should not be empty"
        assert len(result['answer']) > 50, "Answer should be substantial"
        assert len(result['citations']) > 0, "Should have citations"
        assert response_time < 5000, f"Response too slow: {response_time}ms"

        # Check for relevant terms
        relevant_terms = ['lotukerfið', 'grunnefni', 'efnahóp']
        answer_lower = result['answer'].lower()
        found_relevant = any(term.lower() in answer_lower for term in relevant_terms)
        assert found_relevant, "Answer should mention periodic table concepts"

        logger.info("All assertions passed")

    def test_citations_format(self):
        """Test that citations are properly formatted."""
        question = "Hvað eru efnahvörf?"

        result = self.pipeline.ask(question)

        logger.info(f"Checking citations for: {question}")
        logger.info(f"Number of citations: {len(result['citations'])}")

        # Assertions
        assert len(result['citations']) > 0, "Should have citations"

        for i, citation in enumerate(result['citations']):
            logger.info(f"Citation {i+1}: Kafli {citation['chapter']}.{citation['section']} - {citation['title']}")

            assert 'chapter' in citation, "Citation should have chapter"
            assert 'section' in citation, "Citation should have section"
            assert 'title' in citation, "Citation should have title"
            assert 'text_preview' in citation, "Citation should have text preview"

            assert citation['chapter'], "Chapter should not be empty"
            assert citation['section'], "Section should not be empty"
            assert citation['title'], "Title should not be empty"

        logger.info("All citation assertions passed")

    def test_icelandic_characters(self):
        """Test that Icelandic characters are preserved correctly."""
        question = "Útskýrðu atómið með íslenskum hugtökum"

        result = self.pipeline.ask(question)

        # Check for Icelandic special characters in response
        icelandic_chars = ['á', 'ð', 'þ', 'æ', 'ö', 'ó', 'í', 'ú', 'ý', 'é']
        answer = result['answer']

        found_chars = [char for char in icelandic_chars if char in answer.lower()]

        logger.info(f"Found Icelandic characters: {', '.join(found_chars)}")

        assert len(found_chars) > 0, "Answer should contain Icelandic special characters"

        logger.info("Icelandic character test passed")

    def test_response_time(self):
        """Test that responses are generated within acceptable time."""
        question = "Hvað er málmtengi?"

        times = []

        # Run multiple queries to get average
        for i in range(3):
            start_time = time.time()
            self.pipeline.ask(question)
            elapsed = (time.time() - start_time) * 1000
            times.append(elapsed)
            logger.info(f"Query {i+1}: {elapsed:.2f}ms")

        avg_time = sum(times) / len(times)
        max_time = max(times)

        logger.info(f"Average response time: {avg_time:.2f}ms")
        logger.info(f"Max response time: {max_time:.2f}ms")

        assert avg_time < 3000, f"Average response time too slow: {avg_time:.2f}ms"
        assert max_time < 5000, f"Max response time too slow: {max_time:.2f}ms"

        logger.info("Response time test passed")

    def test_health_check(self):
        """Test pipeline health check."""
        health = self.pipeline.health_check()

        logger.info(f"Health status: {health['status']}")
        logger.info(f"Validation: {health.get('validation', {})}")

        assert health['status'] in ['healthy', 'degraded'], "Invalid health status"

        if 'validation' in health:
            validation = health['validation']
            assert validation.get('vector_store'), "Vector store should be valid"
            assert validation.get('llm_client'), "LLM client should be valid"

        logger.info("Health check test passed")

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total tests: {self.test_results['total']}")
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")

        if self.test_results['failed'] == 0:
            print("\n✓ All tests passed!")
        else:
            print(f"\n✗ {self.test_results['failed']} test(s) failed")

        print("="*60 + "\n")

        return self.test_results['failed'] == 0


def main():
    """Main test execution."""
    print("\n" + "="*60)
    print("ICELANDIC CHEMISTRY AI TUTOR - INTEGRATION TESTS")
    print("="*60 + "\n")

    # Initialize test suite
    test_suite = TestRAGPipeline()

    try:
        # Setup
        test_suite.setup()

        # Run tests
        test_suite.run_test("Question: Hvað er atóm?", test_suite.test_question_atom)
        test_suite.run_test("Question: Útskýrðu efnatengi", test_suite.test_question_chemical_bonds)
        test_suite.run_test("Question: Hvað er lotukerfið?", test_suite.test_question_periodic_table)
        test_suite.run_test("Citations format validation", test_suite.test_citations_format)
        test_suite.run_test("Icelandic character handling", test_suite.test_icelandic_characters)
        test_suite.run_test("Response time performance", test_suite.test_response_time)
        test_suite.run_test("Health check", test_suite.test_health_check)

        # Print summary
        success = test_suite.print_summary()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
