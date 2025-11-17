"""
Chapter Validator for OpenStax Chemistry Content
Validates markdown structure, encoding, and content quality.
"""

import re
import os
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of content validation"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    chapter_info: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "chapter_info": self.chapter_info
        }

    def __str__(self) -> str:
        status = "✓ VALID" if self.valid else "✗ INVALID"
        lines = [f"\nValidation Result: {status}"]

        if self.chapter_info:
            lines.append(f"\nChapter Info:")
            for key, value in self.chapter_info.items():
                lines.append(f"  {key}: {value}")

        if self.errors:
            lines.append(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                lines.append(f"  - {error}")

        if self.warnings:
            lines.append(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"  - {warning}")

        return '\n'.join(lines)


class ChapterValidator:
    """Validator for OpenStax Chemistry markdown chapters"""

    # File size limits
    MAX_FILE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    # Content requirements
    MIN_CONTENT_LENGTH = 100  # Minimum characters
    MIN_SECTIONS = 1
    MAX_SECTIONS = 50

    # Patterns
    CHAPTER_PATTERN = re.compile(r'^#\s+Kafli\s+(\d+):\s*(.+)$', re.MULTILINE | re.IGNORECASE)
    SECTION_PATTERN = re.compile(r'^##\s+(\d+\.\d+)\s+(.+)$', re.MULTILINE)
    SUBSECTION_PATTERN = re.compile(r'^###\s+(.+)$', re.MULTILINE)
    CORRUPTED_CHAR_PATTERN = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]')

    # Icelandic special characters (should be preserved)
    ICELANDIC_CHARS = 'áéíóúýþæöðÁÉÍÓÚÝÞÆÖÐ'

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset validator state"""
        self.errors = []
        self.warnings = []
        self.chapter_info = {}

    def validate_file(self, filepath: str) -> ValidationResult:
        """
        Validate a markdown chapter file

        Args:
            filepath: Path to the markdown file

        Returns:
            ValidationResult object
        """
        self.reset()
        logger.info(f"Validating file: {filepath}")

        # Check file exists
        if not os.path.exists(filepath):
            self.errors.append(f"File does not exist: {filepath}")
            return self._build_result()

        # Check file size
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            self.errors.append("File is empty")
            return self._build_result()

        if file_size > self.MAX_FILE_SIZE_BYTES:
            self.errors.append(
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds maximum "
                f"({self.MAX_FILE_SIZE_MB} MB)"
            )
            return self._build_result()

        # Read file content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError as e:
            self.errors.append(f"File is not valid UTF-8: {str(e)}")
            return self._build_result()
        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return self._build_result()

        # Validate content
        return self.validate_content(content, filepath)

    def validate_content(self, content: str, filepath: str = "") -> ValidationResult:
        """
        Validate markdown content

        Args:
            content: The markdown content as string
            filepath: Optional filepath for error messages

        Returns:
            ValidationResult object
        """
        if not content:
            self.errors.append("Content is empty")
            return self._build_result()

        # 1. Check encoding
        self._validate_encoding(content)

        # 2. Check for corrupted characters
        self._check_corrupted_characters(content)

        # 3. Check minimum content length
        if len(content) < self.MIN_CONTENT_LENGTH:
            self.errors.append(
                f"Content too short ({len(content)} chars, minimum {self.MIN_CONTENT_LENGTH})"
            )

        # 4. Validate markdown structure
        self._validate_structure(content)

        # 5. Extract and validate metadata
        self._extract_metadata(content)

        # 6. Check for required elements
        self._check_required_elements(content)

        # 7. Validate Icelandic content
        self._validate_icelandic_content(content)

        # 8. Check for common formatting issues
        self._check_formatting_issues(content)

        return self._build_result()

    def _validate_encoding(self, content: str):
        """Validate UTF-8 encoding"""
        try:
            content.encode('utf-8').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            self.errors.append(f"Invalid UTF-8 encoding: {str(e)}")

    def _check_corrupted_characters(self, content: str):
        """Check for corrupted or invalid characters"""
        matches = self.CORRUPTED_CHAR_PATTERN.findall(content)
        if matches:
            self.errors.append(
                f"Found {len(matches)} corrupted control characters in content"
            )

    def _validate_structure(self, content: str):
        """Validate markdown heading structure"""
        lines = content.split('\n')

        # Check for chapter heading (h1)
        chapter_match = self.CHAPTER_PATTERN.search(content)
        if not chapter_match:
            self.errors.append("Missing chapter heading (# Kafli X: Title)")
        else:
            # Validate chapter heading is first heading
            first_heading_line = None
            for i, line in enumerate(lines):
                if line.strip().startswith('#'):
                    first_heading_line = i
                    break

            if first_heading_line is not None:
                first_heading = lines[first_heading_line]
                if not self.CHAPTER_PATTERN.match(first_heading):
                    self.warnings.append(
                        "First heading is not a chapter heading (# Kafli X: Title)"
                    )

        # Check for sections (h2)
        sections = self.SECTION_PATTERN.findall(content)
        if len(sections) < self.MIN_SECTIONS:
            self.errors.append(
                f"Too few sections ({len(sections)}, minimum {self.MIN_SECTIONS})"
            )
        elif len(sections) > self.MAX_SECTIONS:
            self.warnings.append(
                f"Many sections ({len(sections)}, maximum {self.MAX_SECTIONS})"
            )

        # Check heading hierarchy
        self._validate_heading_hierarchy(lines)

    def _validate_heading_hierarchy(self, lines: List[str]):
        """Validate that headings follow proper hierarchy"""
        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        prev_level = 0

        for i, line in enumerate(lines):
            match = heading_pattern.match(line)
            if match:
                level = len(match.group(1))

                # Check if we skip levels (e.g., h1 -> h3)
                if prev_level > 0 and level > prev_level + 1:
                    self.warnings.append(
                        f"Line {i+1}: Heading hierarchy skip (h{prev_level} -> h{level})"
                    )

                prev_level = level

    def _extract_metadata(self, content: str):
        """Extract chapter and section metadata"""
        # Extract chapter info
        chapter_match = self.CHAPTER_PATTERN.search(content)
        if chapter_match:
            self.chapter_info['chapter_number'] = int(chapter_match.group(1))
            self.chapter_info['chapter_title'] = chapter_match.group(2).strip()

        # Extract sections
        sections = self.SECTION_PATTERN.findall(content)
        self.chapter_info['section_count'] = len(sections)
        self.chapter_info['sections'] = [
            {'number': num, 'title': title.strip()}
            for num, title in sections
        ]

        # Count subsections
        subsections = self.SUBSECTION_PATTERN.findall(content)
        self.chapter_info['subsection_count'] = len(subsections)

        # Word count
        words = content.split()
        self.chapter_info['word_count'] = len(words)

        # Line count
        self.chapter_info['line_count'] = len(content.split('\n'))

    def _check_required_elements(self, content: str):
        """Check that content has required elements"""
        # Must have at least one paragraph
        paragraphs = [
            line for line in content.split('\n')
            if line.strip() and not line.strip().startswith('#')
        ]
        if len(paragraphs) == 0:
            self.errors.append("No paragraph content found")

        # Check for section content
        sections = content.split('##')
        for i, section in enumerate(sections[1:], 1):  # Skip first split (before first ##)
            # Remove the section header line
            section_lines = section.split('\n')[1:]
            section_content = '\n'.join(section_lines).strip()

            if not section_content:
                self.warnings.append(f"Section {i} appears to be empty")
            elif len(section_content) < 50:
                self.warnings.append(f"Section {i} has very little content ({len(section_content)} chars)")

    def _validate_icelandic_content(self, content: str):
        """Validate Icelandic-specific content"""
        # Check for Icelandic characters (should have at least some)
        icelandic_char_count = sum(1 for char in content if char in self.ICELANDIC_CHARS)

        if icelandic_char_count == 0:
            self.warnings.append(
                "No Icelandic special characters found - content might not be in Icelandic"
            )

        self.chapter_info['icelandic_char_count'] = icelandic_char_count

        # Common Icelandic chemistry terms
        icelandic_chemistry_terms = [
            'atóm', 'efni', 'efnafræði', 'rafeind', 'róteind', 'nifteind',
            'efnatengi', 'sameind', 'jón', 'lofttegund', 'vökvi', 'fast ástand'
        ]

        found_terms = [term for term in icelandic_chemistry_terms if term in content.lower()]
        self.chapter_info['icelandic_chemistry_terms_found'] = found_terms

        if not found_terms:
            self.warnings.append(
                "No common Icelandic chemistry terms found - verify content is chemistry-related"
            )

    def _check_formatting_issues(self, content: str):
        """Check for common formatting issues"""
        lines = content.split('\n')

        # Check for trailing whitespace
        trailing_whitespace_lines = [
            i + 1 for i, line in enumerate(lines)
            if line and line != line.rstrip()
        ]
        if trailing_whitespace_lines:
            self.warnings.append(
                f"Found trailing whitespace on {len(trailing_whitespace_lines)} lines"
            )

        # Check for multiple consecutive blank lines
        blank_line_groups = []
        blank_count = 0
        for i, line in enumerate(lines):
            if not line.strip():
                blank_count += 1
            else:
                if blank_count > 3:
                    blank_line_groups.append((i - blank_count + 1, blank_count))
                blank_count = 0

        if blank_line_groups:
            self.warnings.append(
                f"Found {len(blank_line_groups)} groups of excessive blank lines (>3)"
            )

        # Check for inconsistent list markers
        list_markers = set()
        for line in lines:
            if re.match(r'^[\s]*[-*+]\s+', line):
                marker = re.match(r'^[\s]*([-*+])\s+', line).group(1)
                list_markers.add(marker)

        if len(list_markers) > 1:
            self.warnings.append(
                f"Inconsistent list markers found: {', '.join(list_markers)}"
            )

    def _build_result(self) -> ValidationResult:
        """Build the validation result"""
        return ValidationResult(
            valid=len(self.errors) == 0,
            errors=self.errors.copy(),
            warnings=self.warnings.copy(),
            chapter_info=self.chapter_info.copy()
        )


def validate_directory(directory: str, recursive: bool = True) -> Dict[str, ValidationResult]:
    """
    Validate all markdown files in a directory

    Args:
        directory: Directory path
        recursive: Whether to search recursively

    Returns:
        Dictionary mapping filepath to ValidationResult
    """
    validator = ChapterValidator()
    results = {}

    path = Path(directory)
    pattern = '**/*.md' if recursive else '*.md'

    for filepath in path.glob(pattern):
        result = validator.validate_file(str(filepath))
        results[str(filepath)] = result

    return results


def main():
    """Example usage"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python chapter_validator.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isfile(target):
        # Validate single file
        validator = ChapterValidator()
        result = validator.validate_file(target)
        print(result)
        sys.exit(0 if result.valid else 1)

    elif os.path.isdir(target):
        # Validate directory
        results = validate_directory(target)

        total = len(results)
        valid = sum(1 for r in results.values() if r.valid)
        invalid = total - valid

        print(f"\n{'='*60}")
        print(f"Validation Summary")
        print(f"{'='*60}")
        print(f"Total files: {total}")
        print(f"Valid: {valid}")
        print(f"Invalid: {invalid}")
        print(f"{'='*60}\n")

        # Show details for invalid files
        for filepath, result in results.items():
            if not result.valid:
                print(f"\nFile: {filepath}")
                print(result)

        sys.exit(0 if invalid == 0 else 1)

    else:
        print(f"Error: {target} is not a file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
