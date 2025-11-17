"""
E2E Icelandic Language Handling Tests

This module tests comprehensive Icelandic language support:
- All Icelandic special characters: á, é, í, ó, ú, ý, þ, æ, ö, ð
- Chemistry terminology in Icelandic
- Mixed English/Icelandic content
- Unicode edge cases
- Character preservation through entire stack
"""

import pytest
from unittest.mock import patch, MagicMock


# ============================================================================
# Icelandic Character Tests
# ============================================================================

@pytest.mark.e2e
@pytest.mark.icelandic
class TestAllIcelandicCharacters:
    """Test all Icelandic special characters."""

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_lowercase_special_characters(
        self,
        mock_openai_class,
        mock_anthropic_class,
        tmp_path,
        mock_embedding,
        assert_icelandic_preserved
    ):
        """Test lowercase Icelandic characters: á, é, í, ó, ú, ý, þ, æ, ö, ð"""
        from backend.src.vector_store import VectorStore
        from backend.src.embeddings import EmbeddingGenerator
        from backend.src.llm_client import ClaudeClient
        from backend.src.rag_pipeline import RAGPipeline

        # Setup mocks
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai
        mock_openai.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)],
            usage=MagicMock(total_tokens=10)
        )

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic

        test_text = "Prófun með öllum íslenskum stöfum: á, é, í, ó, ú, ý, þ, æ, ö, ð"
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=test_text)]
        mock_anthropic.messages.create.return_value = mock_message

        # Create system
        db_path = tmp_path / "chroma_db"
        vector_store = VectorStore(persist_directory=str(db_path))

        # Store Icelandic content
        vector_store.add_documents(
            documents=[test_text],
            metadatas=[{"chapter_number": 1, "language": "is"}],
            ids=["icelandic_chars_test"],
            embeddings=[mock_embedding]
        )

        embedding_gen = EmbeddingGenerator(api_key="test-key")
        llm_client = ClaudeClient(api_key="test-key")
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        # Ask question with Icelandic characters
        result = pipeline.ask("Hvað um íslenska stafi: á, é, í, ó, ú, ý, þ, æ, ö, ð?")

        # Verify preservation
        assert_icelandic_preserved(result["answer"])
        assert "á" in result["answer"] or "þ" in result["answer"] or "ð" in result["answer"]

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_uppercase_special_characters(
        self,
        mock_openai_class,
        mock_anthropic_class,
        tmp_path,
        mock_embedding,
        assert_icelandic_preserved
    ):
        """Test uppercase Icelandic characters: Á, É, Í, Ó, Ú, Ý, Þ, Æ, Ö, Ð"""
        from backend.src.vector_store import VectorStore
        from backend.src.embeddings import EmbeddingGenerator
        from backend.src.llm_client import ClaudeClient
        from backend.src.rag_pipeline import RAGPipeline

        # Setup mocks
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai
        mock_openai.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)],
            usage=MagicMock(total_tokens=10)
        )

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic

        test_text = "ÍSLAND: Á, É, Í, Ó, Ú, Ý, Þ, Æ, Ö, Ð"
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=test_text)]
        mock_anthropic.messages.create.return_value = mock_message

        db_path = tmp_path / "chroma_db"
        vector_store = VectorStore(persist_directory=str(db_path))

        vector_store.add_documents(
            documents=[test_text],
            metadatas=[{"chapter_number": 1}],
            ids=["uppercase_test"],
            embeddings=[mock_embedding]
        )

        embedding_gen = EmbeddingGenerator(api_key="test-key")
        llm_client = ClaudeClient(api_key="test-key")
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        result = pipeline.ask("ÍSLAND")

        assert_icelandic_preserved(result["answer"])


# ============================================================================
# Chemistry Terminology Tests
# ============================================================================

@pytest.mark.e2e
@pytest.mark.icelandic
class TestIcelandicChemistryTerms:
    """Test Icelandic chemistry terminology."""

    @pytest.mark.parametrize("term,expected_in_answer", [
        ("atóm", ["atóm"]),
        ("rafeind", ["rafeind"]),
        ("efnatengi", ["efnatengi"]),
        ("róteind", ["róteind"]),
        ("nifteind", ["nifteind"]),
        ("efnahvarf", ["efnahvarf"]),
        ("sameind", ["sameind"]),
        ("efnafræði", ["efnafræði"]),
    ])
    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_chemistry_terms(
        self,
        mock_openai_class,
        mock_anthropic_class,
        tmp_path,
        mock_embedding,
        term,
        expected_in_answer
    ):
        """Test specific Icelandic chemistry terms."""
        from backend.src.vector_store import VectorStore
        from backend.src.embeddings import EmbeddingGenerator
        from backend.src.llm_client import ClaudeClient
        from backend.src.rag_pipeline import RAGPipeline

        # Setup mocks
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai
        mock_openai.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)],
            usage=MagicMock(total_tokens=10)
        )

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic

        # Create answer containing the term
        answer_with_term = f"Í efnafræði er {term} mikilvægt hugtak."
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=answer_with_term)]
        mock_anthropic.messages.create.return_value = mock_message

        db_path = tmp_path / "chroma_db"
        vector_store = VectorStore(persist_directory=str(db_path))

        content = f"{term.capitalize()} er mikilvægt í efnafræði."
        vector_store.add_documents(
            documents=[content],
            metadatas=[{"chapter_number": 1}],
            ids=[f"term_{term}"],
            embeddings=[mock_embedding]
        )

        embedding_gen = EmbeddingGenerator(api_key="test-key")
        llm_client = ClaudeClient(api_key="test-key")
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        result = pipeline.ask(f"Hvað er {term}?")

        # Verify term appears in answer
        for expected_word in expected_in_answer:
            assert expected_word in result["answer"].lower()


# ============================================================================
# Mixed Language Tests
# ============================================================================

@pytest.mark.e2e
@pytest.mark.icelandic
class TestMixedLanguage:
    """Test mixed English/Icelandic content."""

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_mixed_english_icelandic(
        self,
        mock_openai_class,
        mock_anthropic_class,
        tmp_path,
        mock_embedding,
        assert_icelandic_preserved
    ):
        """Test content with both English and Icelandic."""
        from backend.src.vector_store import VectorStore
        from backend.src.embeddings import EmbeddingGenerator
        from backend.src.llm_client import ClaudeClient
        from backend.src.rag_pipeline import RAGPipeline

        # Setup mocks
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai
        mock_openai.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)],
            usage=MagicMock(total_tokens=10)
        )

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic

        mixed_text = "Atóm (atom) samanstendur af kjarna (nucleus) og rafeindum (electrons)."
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=mixed_text)]
        mock_anthropic.messages.create.return_value = mock_message

        db_path = tmp_path / "chroma_db"
        vector_store = VectorStore(persist_directory=str(db_path))

        vector_store.add_documents(
            documents=[mixed_text],
            metadatas=[{"chapter_number": 1}],
            ids=["mixed_lang"],
            embeddings=[mock_embedding]
        )

        embedding_gen = EmbeddingGenerator(api_key="test-key")
        llm_client = ClaudeClient(api_key="test-key")
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        result = pipeline.ask("Hvað er atóm?")

        # Verify Icelandic preserved
        assert_icelandic_preserved(result["answer"])

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_english_query_icelandic_content(
        self,
        mock_openai_class,
        mock_anthropic_class,
        tmp_path,
        mock_embedding
    ):
        """Test English query with Icelandic content."""
        from backend.src.vector_store import VectorStore
        from backend.src.embeddings import EmbeddingGenerator
        from backend.src.llm_client import ClaudeClient
        from backend.src.rag_pipeline import RAGPipeline

        # Setup mocks
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai
        mock_openai.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)],
            usage=MagicMock(total_tokens=10)
        )

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Please ask in Icelandic: Vinsamlegast spurðu á íslensku.")]
        mock_anthropic.messages.create.return_value = mock_message

        db_path = tmp_path / "chroma_db"
        vector_store = VectorStore(persist_directory=str(db_path))

        icelandic_content = "Atóm er minnsta eining efnis."
        vector_store.add_documents(
            documents=[icelandic_content],
            metadatas=[{"chapter_number": 1, "language": "is"}],
            ids=["icelandic_content"],
            embeddings=[mock_embedding]
        )

        embedding_gen = EmbeddingGenerator(api_key="test-key")
        llm_client = ClaudeClient(api_key="test-key")
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        # Ask in English
        result = pipeline.ask("What is an atom?")

        # Should handle gracefully (either answer or suggest Icelandic)
        assert "answer" in result
        assert len(result["answer"]) > 0


# ============================================================================
# Unicode Edge Cases
# ============================================================================

@pytest.mark.e2e
@pytest.mark.icelandic
class TestUnicodeEdgeCases:
    """Test Unicode edge cases."""

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_combining_characters(
        self,
        mock_openai_class,
        mock_anthropic_class,
        tmp_path,
        mock_embedding
    ):
        """Test handling of Unicode combining characters."""
        from backend.src.vector_store import VectorStore
        from backend.src.embeddings import EmbeddingGenerator
        from backend.src.llm_client import ClaudeClient
        from backend.src.rag_pipeline import RAGPipeline

        # Setup mocks
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai
        mock_openai.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)],
            usage=MagicMock(total_tokens=10)
        )

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Unicode test passed")]
        mock_anthropic.messages.create.return_value = mock_message

        db_path = tmp_path / "chroma_db"
        vector_store = VectorStore(persist_directory=str(db_path))

        # Text with potential Unicode normalization issues
        text_with_accents = "café résumé naïve"
        vector_store.add_documents(
            documents=[text_with_accents],
            metadatas=[{"chapter_number": 1}],
            ids=["unicode_test"],
            embeddings=[mock_embedding]
        )

        embedding_gen = EmbeddingGenerator(api_key="test-key")
        llm_client = ClaudeClient(api_key="test-key")
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        # Should handle without errors
        result = pipeline.ask("Test unicode")
        assert "answer" in result

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_emoji_handling(
        self,
        mock_openai_class,
        mock_anthropic_class,
        tmp_path,
        mock_embedding
    ):
        """Test handling of emoji in content (should be rare but possible)."""
        from backend.src.vector_store import VectorStore
        from backend.src.embeddings import EmbeddingGenerator
        from backend.src.llm_client import ClaudeClient
        from backend.src.rag_pipeline import RAGPipeline

        # Setup mocks
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai
        mock_openai.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)],
            usage=MagicMock(total_tokens=10)
        )

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Text without emoji")]
        mock_anthropic.messages.create.return_value = mock_message

        db_path = tmp_path / "chroma_db"
        vector_store = VectorStore(persist_directory=str(db_path))

        # Text with emoji
        text_with_emoji = "Atóm ⚛️ er minnsta eining 🔬"
        vector_store.add_documents(
            documents=[text_with_emoji],
            metadatas=[{"chapter_number": 1}],
            ids=["emoji_test"],
            embeddings=[mock_embedding]
        )

        embedding_gen = EmbeddingGenerator(api_key="test-key")
        llm_client = ClaudeClient(api_key="test-key")
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        # Should handle gracefully
        result = pipeline.ask("Atóm")
        assert "answer" in result


# ============================================================================
# Character Encoding Tests
# ============================================================================

@pytest.mark.e2e
@pytest.mark.icelandic
class TestCharacterEncoding:
    """Test proper character encoding throughout the system."""

    @patch('anthropic.Anthropic')
    @patch('openai.OpenAI')
    def test_utf8_encoding_preservation(
        self,
        mock_openai_class,
        mock_anthropic_class,
        tmp_path,
        mock_embedding,
        assert_icelandic_preserved
    ):
        """Test that UTF-8 encoding is preserved."""
        from backend.src.vector_store import VectorStore
        from backend.src.embeddings import EmbeddingGenerator
        from backend.src.llm_client import ClaudeClient
        from backend.src.rag_pipeline import RAGPipeline

        # Setup mocks
        mock_openai = MagicMock()
        mock_openai_class.return_value = mock_openai
        mock_openai.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=mock_embedding)],
            usage=MagicMock(total_tokens=10)
        )

        mock_anthropic = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic

        # All Icelandic characters
        all_chars = "aábcdðeéfghiíjklmnoóprstuúvxyýþæö"
        test_text = f"Öll íslensk stafróf: {all_chars.upper()} {all_chars}"

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=test_text)]
        mock_anthropic.messages.create.return_value = mock_message

        db_path = tmp_path / "chroma_db"
        vector_store = VectorStore(persist_directory=str(db_path))

        vector_store.add_documents(
            documents=[test_text],
            metadatas=[{"chapter_number": 1}],
            ids=["alphabet_test"],
            embeddings=[mock_embedding]
        )

        embedding_gen = EmbeddingGenerator(api_key="test-key")
        llm_client = ClaudeClient(api_key="test-key")
        pipeline = RAGPipeline(
            vector_store=vector_store,
            llm_client=llm_client,
            embedding_generator=embedding_gen
        )

        result = pipeline.ask("Íslenska stafrófið")

        # Verify all characters preserved
        assert_icelandic_preserved(result["answer"])

        # Verify can be encoded/decoded
        try:
            result["answer"].encode('utf-8').decode('utf-8')
        except UnicodeError:
            pytest.fail("UTF-8 encoding/decoding failed")
