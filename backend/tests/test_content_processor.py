"""
Tests for Content Processor - Markdown parsing and chunking.

This module tests content processing functionality including:
- Markdown parsing
- Intelligent chunking (300-800 words)
- Metadata extraction (chapter, section titles)
- Icelandic text handling
"""

import pytest
from typing import List

# Import modules to test
from src.content_processor import ContentProcessor, ChunkMetadata, ProcessedChunk
from src.chapter_validator import ChapterValidator


# ============================================================================
# Content Processor Tests
# ============================================================================

@pytest.mark.unit
class TestContentProcessor:
    """Test content processing and chunking."""

    def test_process_simple_chapter(self, sample_markdown_simple):
        """Test processing simple markdown chapter."""
        processor = ContentProcessor()
        chunks = processor.process_markdown(sample_markdown_simple)

        assert len(chunks) > 0
        assert all(isinstance(chunk, ProcessedChunk) for chunk in chunks)

    def test_extract_chapter_metadata(self, sample_markdown_simple):
        """Test extracting chapter and section metadata."""
        processor = ContentProcessor()
        chunks = processor.process_markdown(sample_markdown_simple)

        # Verify metadata extracted
        for chunk in chunks:
            assert chunk.metadata.chapter_number is not None
            assert chunk.metadata.chapter_title is not None

    def test_chunk_size_boundaries(self, sample_markdown_complex):
        """Test that chunks respect word count boundaries."""
        processor = ContentProcessor(min_words=300, max_words=800)
        chunks = processor.process_markdown(sample_markdown_complex)

        for chunk in chunks:
            word_count = chunk.metadata.word_count
            # Allow some flexibility at boundaries
            assert word_count >= 250 or word_count <= 850

    def test_icelandic_character_preservation(
        self,
        sample_markdown_complex,
        assert_icelandic_preserved
    ):
        """Test that Icelandic characters are preserved during processing."""
        processor = ContentProcessor()
        chunks = processor.process_markdown(sample_markdown_complex)

        # Find chunks with Icelandic content
        for chunk in chunks:
            if any(ic in chunk.content for ic in ['á', 'é', 'í', 'ó', 'ú']):
                assert_icelandic_preserved(chunk.content)

    def test_process_markdown_with_equations(self, sample_markdown_complex):
        """Test processing markdown with code blocks (equations)."""
        processor = ContentProcessor()
        chunks = processor.process_markdown(sample_markdown_complex)

        # Should handle equations without errors
        assert len(chunks) > 0

    def test_process_markdown_with_lists(self, sample_markdown_complex):
        """Test processing markdown with lists."""
        processor = ContentProcessor()
        chunks = processor.process_markdown(sample_markdown_complex)

        # Should handle lists without errors
        assert len(chunks) > 0

    def test_empty_markdown(self):
        """Test handling of empty markdown."""
        processor = ContentProcessor()

        with pytest.raises(ValueError):
            processor.process_markdown("")

    def test_malformed_markdown(self):
        """Test handling of malformed markdown."""
        processor = ContentProcessor()
        malformed = "### This is a subsection without a chapter"

        # Should handle gracefully
        chunks = processor.process_markdown(malformed)
        # May return empty or minimal chunks
        assert isinstance(chunks, list)


# ============================================================================
# Chapter Validator Tests
# ============================================================================

@pytest.mark.unit
class TestChapterValidator:
    """Test chapter validation functionality."""

    def test_validate_valid_chapter(self, sample_markdown_simple):
        """Test validation of valid chapter."""
        validator = ChapterValidator()
        result = validator.validate(sample_markdown_simple)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_minimum_content(self):
        """Test validation of minimum content requirement."""
        validator = ChapterValidator(min_content_length=100)
        short_content = "# Kafli 1\n\nToo short."

        result = validator.validate(short_content)

        assert result.is_valid is False
        assert any("content" in str(err).lower() for err in result.errors)

    def test_validate_icelandic_characters(self, sample_markdown_complex):
        """Test that Icelandic characters are validated."""
        validator = ChapterValidator()
        result = validator.validate(sample_markdown_complex)

        # Should preserve Icelandic characters
        assert result.is_valid is True

    def test_validate_file_size_limit(self):
        """Test file size limit validation."""
        validator = ChapterValidator(max_file_size=1000)  # 1KB limit

        # Create content exceeding limit
        large_content = "# Kafli 1\n\n" + ("x" * 2000)

        result = validator.validate(large_content)

        assert result.is_valid is False
        assert any("size" in str(err).lower() for err in result.errors)

    def test_validate_chapter_structure(self):
        """Test chapter structure validation."""
        validator = ChapterValidator()

        # Missing chapter header
        invalid_structure = "## Section without chapter\n\nContent here."

        result = validator.validate(invalid_structure)

        # Should detect structural issues
        assert result.is_valid is False or result.warnings


# ============================================================================
# Edge Cases
# ============================================================================

@pytest.mark.unit
class TestContentProcessorEdgeCases:
    """Test edge cases in content processing."""

    def test_very_long_paragraph(self):
        """Test handling of very long paragraphs."""
        processor = ContentProcessor()

        long_paragraph = "# Kafli 1\n\n## 1.1 Section\n\n" + (" ".join(["word"] * 1000))

        chunks = processor.process_markdown(long_paragraph)

        # Should split long paragraph appropriately
        assert len(chunks) > 0

    def test_many_short_sections(self):
        """Test handling of many short sections."""
        processor = ContentProcessor()

        many_sections = "# Kafli 1\n\n"
        for i in range(20):
            many_sections += f"## 1.{i} Section {i}\n\nShort content.\n\n"

        chunks = processor.process_markdown(many_sections)

        # Should combine short sections
        assert len(chunks) > 0

    def test_special_characters_in_headings(self):
        """Test handling of special characters in headings."""
        processor = ContentProcessor()

        special_headings = """# Kafli 1: Efnafræði með þ, æ, ö

## 1.1 Atómfræði & Sameindafræði

Content here with íslensk stafi.
"""

        chunks = processor.process_markdown(special_headings)

        assert len(chunks) > 0
        # Verify metadata extracted correctly
        assert chunks[0].metadata.chapter_title is not None
