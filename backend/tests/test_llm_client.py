"""
Tests for LLM Client - Claude API integration for answer generation.

This module tests the ClaudeClient class which handles:
- Claude API communication
- Prompt formatting for Icelandic chemistry tutoring
- Response parsing and citation extraction
- Retry logic and error handling
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from typing import List, Dict, Any

# Import module to test
from src.llm_client import ClaudeClient


# ============================================================================
# Claude Client Initialization Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.api
class TestClaudeClientInitialization:
    """Test Claude client initialization."""

    @patch('anthropic.Anthropic')
    def test_create_claude_client(self, mock_anthropic_class):
        """Test creating Claude client instance."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        client = ClaudeClient(api_key="test-key")

        assert client is not None
        assert client.model == "claude-sonnet-4-20250514"
        mock_anthropic_class.assert_called_once()

    @patch('anthropic.Anthropic')
    def test_custom_configuration(self, mock_anthropic_class):
        """Test creating client with custom configuration."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        client = ClaudeClient(
            api_key="test-key",
            max_tokens=4096,
            temperature=0.5
        )

        assert client.max_tokens == 4096
        assert client.temperature == 0.5


# ============================================================================
# Answer Generation Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.api
class TestAnswerGeneration:
    """Test answer generation functionality."""

    @patch('anthropic.Anthropic')
    def test_generate_answer_simple_question(self, mock_anthropic_class):
        """Test generating answer for simple question."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        # Mock Claude response
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Atóm er minnsta eining efnis sem getur tekið þátt í efnahvörfum.")]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test-key")

        question = "Hvað er atóm?"
        context_chunks = [
            {"content": "Atóm er minnsta eining efnis.", "metadata": {"chapter_number": 1}}
        ]

        result = client.generate_answer(question, context_chunks)

        # Verify result structure
        assert "answer" in result
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0

        # Verify API was called
        mock_client.messages.create.assert_called_once()

    @patch('anthropic.Anthropic')
    def test_generate_answer_with_citations(self, mock_anthropic_class):
        """Test that citations are extracted from context."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Atóm samanstendur af kjarna og rafeindum.")]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test-key")

        context_chunks = [
            {
                "content": "Atóm er minnsta eining efnis.",
                "metadata": {
                    "chapter_number": 1,
                    "section_number": "1.1",
                    "chapter_title": "Efnafræði",
                    "section_title": "Atóm"
                }
            }
        ]

        result = client.generate_answer("Hvað er atóm?", context_chunks)

        # Verify citations are included
        assert "citations" in result
        assert isinstance(result["citations"], list)
        assert len(result["citations"]) > 0

    @patch('anthropic.Anthropic')
    def test_generate_answer_icelandic_preserved(
        self,
        mock_anthropic_class,
        assert_icelandic_preserved
    ):
        """Test that Icelandic characters are preserved in answer."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        icelandic_answer = "Atóm með þ, æ, ö, ð hefur sérstaka eiginleika."
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=icelandic_answer)]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test-key")

        context_chunks = [{"content": "Test", "metadata": {"chapter_number": 1}}]
        result = client.generate_answer("Test question", context_chunks)

        # Verify Icelandic characters preserved
        assert_icelandic_preserved(result["answer"])

    @patch('anthropic.Anthropic')
    def test_generate_answer_empty_context(self, mock_anthropic_class):
        """Test handling of empty context."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        client = ClaudeClient(api_key="test-key")

        with pytest.raises(ValueError, match=".*context.*"):
            client.generate_answer("Hvað er atóm?", [])


# ============================================================================
# Prompt Formatting Tests
# ============================================================================

@pytest.mark.unit
class TestPromptFormatting:
    """Test prompt formatting for Claude API."""

    @patch('anthropic.Anthropic')
    def test_system_prompt_icelandic_tutor(self, mock_anthropic_class):
        """Test that system prompt is configured for Icelandic chemistry tutoring."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Test answer")]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test-key")

        context_chunks = [{"content": "Test", "metadata": {"chapter_number": 1}}]
        client.generate_answer("Test question", context_chunks)

        # Verify system prompt was passed
        call_args = mock_client.messages.create.call_args
        system_prompt = call_args.kwargs.get("system", "")

        # Should mention Icelandic and chemistry
        assert "icelandic" in system_prompt.lower() or "íslensk" in system_prompt.lower()
        assert "chemistry" in system_prompt.lower() or "efnafræði" in system_prompt.lower()

    @patch('anthropic.Anthropic')
    def test_context_formatting(self, mock_anthropic_class):
        """Test that context chunks are properly formatted in prompt."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Test answer")]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test-key")

        context_chunks = [
            {"content": "First chunk content", "metadata": {"chapter_number": 1}},
            {"content": "Second chunk content", "metadata": {"chapter_number": 2}}
        ]

        client.generate_answer("Test question", context_chunks)

        # Verify context was included in message
        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs.get("messages", [])

        # Context should be in user message
        user_message = next((m for m in messages if m["role"] == "user"), None)
        assert user_message is not None
        assert "First chunk content" in str(user_message)


# ============================================================================
# Response Parsing Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.api
class TestResponseParsing:
    """Test parsing of Claude API responses."""

    @patch('anthropic.Anthropic')
    def test_parse_simple_text_response(self, mock_anthropic_class):
        """Test parsing simple text response."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        answer_text = "This is the answer."
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=answer_text)]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test-key")
        context_chunks = [{"content": "Test", "metadata": {"chapter_number": 1}}]
        result = client.generate_answer("Test?", context_chunks)

        assert result["answer"] == answer_text

    @patch('anthropic.Anthropic')
    def test_parse_multipart_response(self, mock_anthropic_class):
        """Test parsing response with multiple content blocks."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [
            MagicMock(text="Part 1. "),
            MagicMock(text="Part 2.")
        ]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test-key")
        context_chunks = [{"content": "Test", "metadata": {"chapter_number": 1}}]
        result = client.generate_answer("Test?", context_chunks)

        # Should combine parts
        assert "Part 1" in result["answer"]
        assert "Part 2" in result["answer"]


# ============================================================================
# Error Handling and Retry Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.api
class TestErrorHandling:
    """Test error handling and retry logic."""

    @patch('anthropic.Anthropic')
    def test_api_error_handling(self, mock_anthropic_class):
        """Test handling of API errors."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_client.messages.create.side_effect = Exception("API Error")

        client = ClaudeClient(api_key="test-key", max_retries=0)
        context_chunks = [{"content": "Test", "metadata": {"chapter_number": 1}}]

        with pytest.raises(Exception, match="API Error"):
            client.generate_answer("Test?", context_chunks)

    @patch('anthropic.Anthropic')
    @patch('time.sleep')
    def test_retry_on_failure(self, mock_sleep, mock_anthropic_class):
        """Test retry logic on temporary failures."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Success after retry")]

        # Fail twice, then succeed
        mock_client.messages.create.side_effect = [
            Exception("Temporary error"),
            Exception("Temporary error"),
            mock_message
        ]

        client = ClaudeClient(api_key="test-key", max_retries=3)
        context_chunks = [{"content": "Test", "metadata": {"chapter_number": 1}}]

        result = client.generate_answer("Test?", context_chunks)

        # Should succeed after retries
        assert "answer" in result
        assert mock_client.messages.create.call_count == 3

    @patch('anthropic.Anthropic')
    def test_timeout_handling(self, mock_anthropic_class, mock_api_timeout):
        """Test handling of API timeouts."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_client.messages.create.side_effect = mock_api_timeout

        client = ClaudeClient(api_key="test-key", max_retries=0)
        context_chunks = [{"content": "Test", "metadata": {"chapter_number": 1}}]

        with pytest.raises(TimeoutError):
            client.generate_answer("Test?", context_chunks)


# ============================================================================
# Icelandic Language Validation Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.icelandic
class TestIcelandicSupport:
    """Test Icelandic language support validation."""

    @patch('anthropic.Anthropic')
    def test_validate_icelandic_support(self, mock_anthropic_class):
        """Test Icelandic character validation."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        client = ClaudeClient(api_key="test-key")

        # Should validate Icelandic characters
        is_valid = client.validate_icelandic_support()

        # Implementation should return True for Claude (supports Unicode)
        assert is_valid is True or is_valid is None

    @patch('anthropic.Anthropic')
    def test_all_icelandic_characters(
        self,
        mock_anthropic_class,
        icelandic_test_cases,
        assert_icelandic_preserved
    ):
        """Test all Icelandic special characters."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        def mock_create(*args, **kwargs):
            # Echo back the question in answer
            messages = kwargs.get("messages", [])
            user_msg = next((m for m in messages if m["role"] == "user"), {})
            question_text = user_msg.get("content", "")
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text=f"Answer to: {question_text}")]
            return mock_message

        mock_client.messages.create.side_effect = mock_create

        client = ClaudeClient(api_key="test-key")

        for test_case in icelandic_test_cases:
            context_chunks = [{"content": "Test", "metadata": {"chapter_number": 1}}]
            result = client.generate_answer(test_case["input"], context_chunks)

            # Verify Icelandic characters preserved
            assert_icelandic_preserved(result["answer"])


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.slow
@pytest.mark.performance
class TestClaudeClientPerformance:
    """Test Claude client performance."""

    @patch('anthropic.Anthropic')
    def test_response_time(
        self,
        mock_anthropic_class,
        performance_timer,
        expected_responses
    ):
        """Test that LLM responses are within time threshold."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Quick answer")]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test-key")
        context_chunks = [{"content": "Test", "metadata": {"chapter_number": 1}}]

        with performance_timer() as timer:
            result = client.generate_answer("Test?", context_chunks)

        # Should be fast with mocked API
        max_time = expected_responses["performance_benchmarks"]["max_llm_time_seconds"]
        # Give generous margin for mocked tests
        assert timer.elapsed < max_time * 2
        assert "answer" in result
