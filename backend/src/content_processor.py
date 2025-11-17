"""
OpenStax Chemistry Content Processor
Intelligent markdown chunking with metadata extraction for Icelandic content.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of content blocks"""
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    LIST = "list"
    EQUATION = "equation"
    CODE = "code"
    IMAGE = "image"


@dataclass
class ContentBlock:
    """Represents a single content block"""
    type: ContentType
    content: str
    level: Optional[int] = None  # For headings
    word_count: int = 0

    def __post_init__(self):
        if self.word_count == 0:
            self.word_count = len(self.content.split())


@dataclass
class ChunkMetadata:
    """Metadata for a content chunk"""
    chapter_number: int
    section_number: str
    chapter_title: str
    section_title: str
    chunk_index: int
    word_count: int
    language: str = "is"

    def to_dict(self) -> Dict:
        return {
            "chapter_number": self.chapter_number,
            "section_number": self.section_number,
            "chapter_title": self.chapter_title,
            "section_title": self.section_title,
            "chunk_index": self.chunk_index,
            "word_count": self.word_count,
            "language": self.language
        }


@dataclass
class ProcessedChunk:
    """A processed content chunk with metadata"""
    content: str
    metadata: ChunkMetadata

    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "metadata": self.metadata.to_dict()
        }


class ContentProcessor:
    """Process OpenStax Chemistry markdown content into chunks"""

    # Chunk size constraints (in words)
    MIN_CHUNK_SIZE = 200
    TARGET_MIN_SIZE = 400
    TARGET_MAX_SIZE = 600
    MAX_CHUNK_SIZE = 1000

    # Patterns for markdown elements
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    CHAPTER_PATTERN = re.compile(r'^#\s+Kafli\s+(\d+):\s*(.+)$', re.MULTILINE | re.IGNORECASE)
    SECTION_PATTERN = re.compile(r'^##\s+(\d+\.\d+)\s+(.+)$', re.MULTILINE)
    LIST_ITEM_PATTERN = re.compile(r'^[\s]*[-*+]\s+.+$|^[\s]*\d+\.\s+.+$', re.MULTILINE)
    EQUATION_PATTERN = re.compile(r'\$\$.+?\$\$|\$.+?\$', re.DOTALL)
    CODE_PATTERN = re.compile(r'```[\s\S]+?```|`[^`]+`')
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^\)]+)\)')

    def __init__(self):
        self.current_chapter_number = 0
        self.current_chapter_title = ""

    def process_file(self, content: str, filepath: str = "") -> List[ProcessedChunk]:
        """
        Process a markdown file into chunks with metadata

        Args:
            content: The markdown content as string
            filepath: Optional filepath for logging

        Returns:
            List of ProcessedChunk objects
        """
        logger.info(f"Processing file: {filepath}")

        # Validate encoding
        if not self._validate_encoding(content):
            raise ValueError(f"Invalid UTF-8 encoding in {filepath}")

        # Extract chapter information
        chapter_info = self._extract_chapter_info(content)
        if not chapter_info:
            raise ValueError(f"Could not extract chapter information from {filepath}")

        self.current_chapter_number = chapter_info['chapter_number']
        self.current_chapter_title = chapter_info['chapter_title']

        # Split into sections
        sections = self._split_into_sections(content)
        logger.info(f"Found {len(sections)} sections")

        # Process each section into chunks
        all_chunks = []
        chunk_index = 0

        for section in sections:
            section_chunks = self._process_section(section, chunk_index)
            all_chunks.extend(section_chunks)
            chunk_index += len(section_chunks)

        logger.info(f"Created {len(all_chunks)} chunks from {filepath}")
        return all_chunks

    def _validate_encoding(self, content: str) -> bool:
        """Validate that content is valid UTF-8"""
        try:
            # Try to encode and decode
            content.encode('utf-8').decode('utf-8')
            return True
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False

    def _extract_chapter_info(self, content: str) -> Optional[Dict]:
        """Extract chapter number and title from content"""
        match = self.CHAPTER_PATTERN.search(content)
        if match:
            return {
                'chapter_number': int(match.group(1)),
                'chapter_title': match.group(2).strip()
            }
        return None

    def _split_into_sections(self, content: str) -> List[Dict]:
        """Split content into sections (h2 level)"""
        sections = []
        lines = content.split('\n')

        current_section = None
        current_content_lines = []

        for line in lines:
            # Check if this is a section header (##)
            section_match = self.SECTION_PATTERN.match(line)

            if section_match:
                # Save previous section if exists
                if current_section:
                    current_section['content'] = '\n'.join(current_content_lines)
                    sections.append(current_section)

                # Start new section
                current_section = {
                    'section_number': section_match.group(1),
                    'section_title': section_match.group(2).strip(),
                    'header': line
                }
                current_content_lines = [line]
            elif current_section:
                current_content_lines.append(line)

        # Add last section
        if current_section:
            current_section['content'] = '\n'.join(current_content_lines)
            sections.append(current_section)

        return sections

    def _process_section(self, section: Dict, start_chunk_index: int) -> List[ProcessedChunk]:
        """Process a section into one or more chunks"""
        content = section['content']
        section_number = section['section_number']
        section_title = section['section_title']

        # Parse content into blocks
        blocks = self._parse_content_blocks(content)

        # Group blocks into chunks
        chunk_groups = self._group_blocks_into_chunks(blocks)

        # Create ProcessedChunk objects
        chunks = []
        for i, chunk_blocks in enumerate(chunk_groups):
            chunk_content = self._render_chunk(chunk_blocks, section['header'])
            word_count = sum(block.word_count for block in chunk_blocks)

            metadata = ChunkMetadata(
                chapter_number=self.current_chapter_number,
                section_number=section_number,
                chapter_title=self.current_chapter_title,
                section_title=section_title,
                chunk_index=start_chunk_index + i,
                word_count=word_count
            )

            # Quality check
            if word_count < self.MIN_CHUNK_SIZE:
                logger.warning(f"Chunk {metadata.chunk_index} is below minimum size: {word_count} words")
            elif word_count > self.MAX_CHUNK_SIZE:
                logger.warning(f"Chunk {metadata.chunk_index} exceeds maximum size: {word_count} words")

            chunks.append(ProcessedChunk(content=chunk_content, metadata=metadata))

        return chunks

    def _parse_content_blocks(self, content: str) -> List[ContentBlock]:
        """Parse content into content blocks"""
        blocks = []
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # Check for headings
            heading_match = self.HEADING_PATTERN.match(line)
            if heading_match:
                level = len(heading_match.group(1))
                blocks.append(ContentBlock(
                    type=ContentType.HEADING,
                    content=line,
                    level=level,
                    word_count=len(heading_match.group(2).split())
                ))
                i += 1
                continue

            # Check for code blocks
            if line.strip().startswith('```'):
                code_lines = [line]
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    code_lines.append(lines[i])
                    i += 1
                blocks.append(ContentBlock(
                    type=ContentType.CODE,
                    content='\n'.join(code_lines),
                    word_count=0  # Code blocks don't count towards word count
                ))
                continue

            # Check for list items
            if self.LIST_ITEM_PATTERN.match(line):
                list_lines = [line]
                i += 1
                # Continue collecting list items
                while i < len(lines):
                    next_line = lines[i]
                    # Check if continuation of list (item or indented content)
                    if (self.LIST_ITEM_PATTERN.match(next_line) or
                        (next_line.strip() and next_line.startswith((' ', '\t')))):
                        list_lines.append(next_line)
                        i += 1
                    elif not next_line.strip():
                        # Empty line might be part of list
                        list_lines.append(next_line)
                        i += 1
                    else:
                        break

                list_content = '\n'.join(list_lines)
                blocks.append(ContentBlock(
                    type=ContentType.LIST,
                    content=list_content
                ))
                continue

            # Check for equations (LaTeX)
            if '$$' in line or (line.strip().startswith('$') and line.strip().endswith('$')):
                equation_lines = [line]
                if '$$' in line and line.count('$$') == 1:
                    # Multi-line equation
                    i += 1
                    while i < len(lines) and '$$' not in lines[i]:
                        equation_lines.append(lines[i])
                        i += 1
                    if i < len(lines):
                        equation_lines.append(lines[i])
                        i += 1
                else:
                    i += 1

                blocks.append(ContentBlock(
                    type=ContentType.EQUATION,
                    content='\n'.join(equation_lines),
                    word_count=0  # Equations don't count towards word count
                ))
                continue

            # Regular paragraph
            para_lines = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                # Continue paragraph until we hit empty line or special content
                if (not next_line.strip() or
                    self.HEADING_PATTERN.match(next_line) or
                    self.LIST_ITEM_PATTERN.match(next_line) or
                    next_line.strip().startswith('```') or
                    '$$' in next_line):
                    break
                para_lines.append(next_line)
                i += 1

            para_content = '\n'.join(para_lines)
            blocks.append(ContentBlock(
                type=ContentType.PARAGRAPH,
                content=para_content
            ))

        return blocks

    def _group_blocks_into_chunks(self, blocks: List[ContentBlock]) -> List[List[ContentBlock]]:
        """Group content blocks into chunks respecting constraints"""
        chunks = []
        current_chunk = []
        current_word_count = 0

        for block in blocks:
            # Skip section headers (we'll add them separately)
            if block.type == ContentType.HEADING and block.level == 2:
                continue

            block_words = block.word_count

            # Always keep special content types together
            if block.type in [ContentType.CODE, ContentType.EQUATION, ContentType.LIST]:
                # If adding this would exceed max size and we have content, start new chunk
                if (current_chunk and
                    current_word_count + block_words > self.MAX_CHUNK_SIZE):
                    chunks.append(current_chunk)
                    current_chunk = [block]
                    current_word_count = block_words
                else:
                    current_chunk.append(block)
                    current_word_count += block_words
                continue

            # For paragraphs, check if we should start a new chunk
            if current_word_count >= self.TARGET_MIN_SIZE:
                # We're above minimum target
                if current_word_count + block_words > self.TARGET_MAX_SIZE:
                    # Adding this would exceed target max, start new chunk
                    chunks.append(current_chunk)
                    current_chunk = [block]
                    current_word_count = block_words
                    continue

            # Add to current chunk
            current_chunk.append(block)
            current_word_count += block_words

            # Check if we've hit max size
            if current_word_count >= self.MAX_CHUNK_SIZE:
                chunks.append(current_chunk)
                current_chunk = []
                current_word_count = 0

        # Add remaining blocks
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _render_chunk(self, blocks: List[ContentBlock], section_header: str) -> str:
        """Render blocks back to markdown, including section header"""
        lines = [section_header, '']

        for block in blocks:
            lines.append(block.content)
            lines.append('')  # Add spacing between blocks

        return '\n'.join(lines).strip()

    def validate_chunk(self, chunk: ProcessedChunk) -> Tuple[bool, List[str]]:
        """
        Validate a chunk meets quality requirements

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Check minimum size
        if chunk.metadata.word_count < self.MIN_CHUNK_SIZE:
            errors.append(f"Chunk word count {chunk.metadata.word_count} below minimum {self.MIN_CHUNK_SIZE}")

        # Check maximum size
        if chunk.metadata.word_count > self.MAX_CHUNK_SIZE:
            errors.append(f"Chunk word count {chunk.metadata.word_count} exceeds maximum {self.MAX_CHUNK_SIZE}")

        # Check metadata completeness
        if not chunk.metadata.chapter_title:
            errors.append("Missing chapter title")
        if not chunk.metadata.section_title:
            errors.append("Missing section title")
        if chunk.metadata.chapter_number <= 0:
            errors.append("Invalid chapter number")

        # Check encoding
        try:
            chunk.content.encode('utf-8').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            errors.append("Invalid UTF-8 encoding")

        # Check not empty
        if not chunk.content.strip():
            errors.append("Empty content")

        # Check for orphaned headers (header with no content)
        lines = chunk.content.strip().split('\n')
        if len(lines) == 1 and lines[0].startswith('#'):
            errors.append("Orphaned header (header with no content)")

        return len(errors) == 0, errors


def main():
    """Example usage"""
    processor = ContentProcessor()

    # Example Icelandic content
    sample_content = """# Kafli 1: Efnafræði í daglegu lífi

## 1.1 Inngangur að efnafræði

Efnafræði er vísindi um efni og eiginleika þeirra. Í þessum kafla munum við skoða grunnhugtök efnafræðinnar og hvernig þau tengjast daglegu lífi okkar.

Atóm eru grunneiningar efnis. Þau samanstanda af róteindum, nifteindum og rafeindium. Rafeindirnar hringla utan um kjarnann sem inniheldur róteindir og nifteindir.

## 1.2 Efnatengi

Efnatengi myndast þegar atóm deila rafeindum eða flytja rafeindur á milli sín. Það eru þrjár megingerðir efnatengja:

- Samgilt tengi: Atóm deila rafeindum
- Jónatengi: Atóm flytja rafeindur
- Málmtengi: Rafeindur hreyfist frjálslega

Dæmi um efnatengi er vatn (H₂O) þar sem súrefnisatóm deilir rafeindum með tveimur vetnisatómum.
"""

    chunks = processor.process_file(sample_content, "sample.md")

    for chunk in chunks:
        print(f"\n{'='*60}")
        print(f"Chunk {chunk.metadata.chunk_index}")
        print(f"Section: {chunk.metadata.section_number} - {chunk.metadata.section_title}")
        print(f"Word count: {chunk.metadata.word_count}")
        print(f"{'='*60}")
        print(chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content)

        is_valid, errors = processor.validate_chunk(chunk)
        if not is_valid:
            print(f"\nValidation errors: {errors}")


if __name__ == "__main__":
    main()
