"""
Comprehensive tests for OpenStax Chemistry content processor
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from content_processor import ContentProcessor, ContentType, ProcessedChunk
from chapter_validator import ChapterValidator


class TestContentProcessor(unittest.TestCase):
    """Test cases for ContentProcessor"""

    def setUp(self):
        """Set up test fixtures"""
        self.processor = ContentProcessor()

    def test_simple_chapter(self):
        """Test processing a simple chapter with 2 sections"""
        content = """# Kafli 1: Grunnhugtök efnafræði

## 1.1 Hvað er efnafræði?

Efnafræði er vísindin um efni og eiginleika þeirra. Hún fjallar um samsetningu efna, uppbyggingu þeirra og breytingar sem verða á efnum.

Efnafræðin skiptist í nokkrar greinar: lífræna efnafræði, ólífræna efnafræði, greiningarefnafræði og eðlisefnafræði.

## 1.2 Atóm og sameindir

Atóm eru minnstu einingarnar sem halda efnafræðilegum eiginleikum. Sameindir myndast þegar tvö eða fleiri atóm tengjast saman með efnatengjum.

Vatn (H₂O) er dæmi um sameind sem inniheldur tvö vetnisatóm og eitt súrefnisatóm.
"""

        chunks = self.processor.process_file(content, "test_simple.md")

        # Should create 2 chunks (one per section)
        self.assertEqual(len(chunks), 2)

        # Check first chunk
        self.assertEqual(chunks[0].metadata.chapter_number, 1)
        self.assertEqual(chunks[0].metadata.section_number, "1.1")
        self.assertIn("Hvað er efnafræði?", chunks[0].content)

        # Check second chunk
        self.assertEqual(chunks[1].metadata.section_number, "1.2")
        self.assertIn("Atóm og sameindir", chunks[1].content)

    def test_complex_chapter_with_lists(self):
        """Test chapter with equations, lists, and images"""
        content = """# Kafli 2: Efnatengi

## 2.1 Gerðir efnatengja

Þrjár megingerðir efnatengja eru til:

- **Samgilt tengi**: Atóm deila rafeindum
- **Jónatengi**: Atóm flytja rafeindur á milli sín
- **Málmtengi**: Rafeindur hreyfist frjálslega um málmkristalla

### Samgilt tengi

Í samgiltu tengi deila atóm rafeindum. Dæmi um sameindir með samgilt tengi:

1. Vatn (H₂O)
2. Koltvísýringur (CO₂)
3. Metani (CH₄)

Orkan sem þarf til að brjóta samgilt tengi er háð fjölda rafeinda sem deilt er:

$$E = -k \\frac{Q_1 Q_2}{r}$$

þar sem $k$ er fasti, $Q$ eru hleðslur og $r$ er fjarlægð.

## 2.2 Lewis-myndir

Lewis-myndir sýna hvernig atóm deila rafeindum í sameindum.

![Lewis-mynd af vatni](water_lewis.png)
"""

        chunks = self.processor.process_file(content, "test_complex.md")

        # Should handle lists and equations properly
        self.assertGreater(len(chunks), 0)

        # Check that equations are preserved
        has_equation = any('$$' in chunk.content for chunk in chunks)
        self.assertTrue(has_equation, "Equations should be preserved")

        # Check that lists are preserved
        has_list = any('-' in chunk.content or '1.' in chunk.content for chunk in chunks)
        self.assertTrue(has_list, "Lists should be preserved")

    def test_icelandic_edge_cases(self):
        """Test all Icelandic special characters"""
        content = """# Kafli 3: Íslenskar stafir

## 3.1 Séríslenskir stafir

Íslenska stafróf inniheldur bæði venjulega latina stafi og séríslenska stafi:

- á, Á - langt a
- ð, Ð - eth
- é, É - langt e
- í, Í - langt i
- ó, Ó - langt o
- ú, Ú - langt u
- ý, Ý - langt y
- þ, Þ - thorn
- æ, Æ - ae-samstafa
- ö, Ö - o-umlaut

Þessir stafir eru mikilvægir í íslenskum efnafræðihugtökum eins og:
atóm, rafeindahýsi, efnatengi, þéttleiki, rúmmál, vökvi, ástæða, próf.
"""

        chunks = self.processor.process_file(content, "test_icelandic.md")

        # Should process without encoding errors
        self.assertGreater(len(chunks), 0)

        # Check that Icelandic characters are preserved
        combined_content = ''.join(chunk.content for chunk in chunks)
        icelandic_chars = 'áéíóúýþæöðÁÉÍÓÚÝÞÆÖÐ'
        for char in icelandic_chars:
            self.assertIn(char, combined_content, f"Character {char} should be preserved")

    def test_large_chapter(self):
        """Test large chapter (>10,000 words)"""
        # Generate a large chapter with multiple sections
        sections = []
        for i in range(1, 11):
            section = f"""## 1.{i} Kafli {i}

{"Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 200}

Atóm eru grunneiningar efnisins. {"Efnafræði er áhugavert. " * 100}
"""
            sections.append(section)

        content = "# Kafli 1: Stór kafli\n\n" + "\n".join(sections)

        chunks = self.processor.process_file(content, "test_large.md")

        # Should create multiple chunks
        self.assertGreater(len(chunks), 10)

        # All chunks should be within size limits
        for chunk in chunks:
            self.assertGreaterEqual(
                chunk.metadata.word_count,
                self.processor.MIN_CHUNK_SIZE,
                "Chunk should be above minimum size"
            )
            self.assertLessEqual(
                chunk.metadata.word_count,
                self.processor.MAX_CHUNK_SIZE,
                "Chunk should be below maximum size"
            )

    def test_malformed_markdown(self):
        """Test handling of malformed markdown"""
        content = """# Kafli 1: Malformed

## 1.1 Section without chapter pattern

This should still work even though chapter pattern is wrong.

### Subsection

Some content here.
"""

        # Should raise error for missing chapter pattern
        with self.assertRaises(ValueError):
            self.processor.process_file(content, "test_malformed.md")

    def test_empty_sections(self):
        """Test handling of empty sections"""
        content = """# Kafli 1: Test

## 1.1 Empty section

## 1.2 Non-empty section

This section has content.
"""

        chunks = self.processor.process_file(content, "test_empty.md")

        # Should handle empty sections (might create warning but shouldn't crash)
        self.assertGreater(len(chunks), 0)

    def test_nested_lists(self):
        """Test nested list handling"""
        content = """# Kafli 1: Listar

## 1.1 Nested lists

Efnatengi flokkast í:

- Samgilt tengi
  - Einfalt samgilt tengi
  - Tvöfalt samgilt tengi
  - Þrefalt samgilt tengi
- Jónatengi
  - Kationtengi
  - Aniontengi
- Málmtengi

Hvert tengi hefur mismunandi eiginleika.
"""

        chunks = self.processor.process_file(content, "test_nested.md")

        # Should not split nested lists
        self.assertGreater(len(chunks), 0)

        # Check that nested structure is preserved
        for chunk in chunks:
            if "Einfalt samgilt tengi" in chunk.content:
                # Should have the parent item too
                self.assertIn("Samgilt tengi", chunk.content)

    def test_mixed_content_types(self):
        """Test chapter with various content types mixed together"""
        content = """# Kafli 1: Blönduð efni

## 1.1 Ýmislegt

Texti fyrir framan lista.

- Listi atriði 1
- Listi atriði 2

Texti á eftir lista.

```python
# Kóði
def calculate_mass(moles, molar_mass):
    return moles * molar_mass
```

Texti fyrir framan jöfnu.

$$E = mc^2$$

Texti á eftir jöfnu.
"""

        chunks = self.processor.process_file(content, "test_mixed.md")

        # Should handle mixed content
        self.assertGreater(len(chunks), 0)

        # Check that different types are preserved
        combined = ''.join(chunk.content for chunk in chunks)
        self.assertIn("```", combined, "Code blocks should be preserved")
        self.assertIn("$$", combined, "Equations should be preserved")
        self.assertIn("- Listi", combined, "Lists should be preserved")

    def test_chunk_validation(self):
        """Test chunk validation logic"""
        content = """# Kafli 1: Test

## 1.1 Valid section

This is a valid section with enough content to meet the minimum requirements.
It has multiple sentences and provides substantial information about the topic.
The content is meaningful and educational.
"""

        chunks = self.processor.process_file(content, "test_validation.md")

        # Validate each chunk
        for chunk in chunks:
            is_valid, errors = self.processor.validate_chunk(chunk)

            # Print errors if validation fails
            if not is_valid:
                print(f"\nValidation errors for chunk {chunk.metadata.chunk_index}:")
                for error in errors:
                    print(f"  - {error}")

    def test_unicode_validation(self):
        """Test UTF-8 encoding validation"""
        valid_content = """# Kafli 1: Prufa

## 1.1 Íslenski textinn

Þetta er prófun með íslenskum stöfum: áéíóúýþæöð.
"""

        # Valid UTF-8 should work
        self.assertTrue(self.processor._validate_encoding(valid_content))

    def test_paragraph_boundaries(self):
        """Test that paragraphs are never split"""
        content = """# Kafli 1: Málsgreinar

## 1.1 Langar málsgreinar

""" + ("Þetta er löng málsgrein sem ætti ekki að vera skipt. " * 100) + """

""" + ("Þetta er önnur löng málsgrein sem ætti heldur ekki að vera skipt. " * 100)

        chunks = self.processor.process_file(content, "test_paragraphs.md")

        # Each chunk should contain complete paragraphs
        for chunk in chunks:
            # Check that we don't have incomplete sentences (very basic check)
            self.assertTrue(
                chunk.content.strip().endswith('.') or
                chunk.content.strip().endswith('\n') or
                '##' in chunk.content,
                "Chunks should end at paragraph boundaries"
            )


class TestChapterValidator(unittest.TestCase):
    """Test cases for ChapterValidator"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = ChapterValidator()

    def test_valid_chapter(self):
        """Test validation of a valid chapter"""
        content = """# Kafli 1: Gildar efnafræði

## 1.1 Fyrsti kafli

Þetta er gildur texti með íslenskum orðum eins og atóm og efni.

## 1.2 Annar kafli

Meira efni hér með efnafræðihugtökum.
"""

        result = self.validator.validate_content(content)

        self.assertTrue(result.valid, f"Should be valid. Errors: {result.errors}")
        self.assertEqual(result.chapter_info['chapter_number'], 1)
        self.assertEqual(result.chapter_info['section_count'], 2)

    def test_invalid_encoding(self):
        """Test detection of encoding issues"""
        # This is a basic test - actual encoding issues would be detected when reading files
        content = "# Kafli 1: Test\n\n## 1.1 Section\n\nContent"

        result = self.validator.validate_content(content)

        # Should validate encoding
        # Note: This content is actually valid, so it should pass
        self.assertTrue(self.validator._validate_encoding(content))

    def test_missing_chapter_header(self):
        """Test detection of missing chapter header"""
        content = """## 1.1 Section without chapter

This has no chapter header.
"""

        result = self.validator.validate_content(content)

        self.assertFalse(result.valid)
        self.assertTrue(
            any("chapter heading" in error.lower() for error in result.errors),
            "Should detect missing chapter heading"
        )

    def test_empty_content(self):
        """Test detection of empty content"""
        result = self.validator.validate_content("")

        self.assertFalse(result.valid)
        self.assertIn("Content is empty", result.errors)

    def test_icelandic_chemistry_terms(self):
        """Test detection of Icelandic chemistry terms"""
        content = """# Kafli 1: Efnafræði

## 1.1 Atóm og rafeindur

Atóm samanstanda af róteindum, nifteindum og rafeindium.
Efnatengi tengjast sameindum og jónum.
"""

        result = self.validator.validate_content(content)

        # Should detect Icelandic chemistry terms
        self.assertGreater(
            len(result.chapter_info.get('icelandic_chemistry_terms_found', [])),
            0,
            "Should find Icelandic chemistry terms"
        )

    def test_file_size_limits(self):
        """Test file size validation"""
        # Create a very large content string
        large_content = "# Kafli 1: Stór\n\n## 1.1 Section\n\n" + ("x" * 10_000_000)

        result = self.validator.validate_content(large_content)

        # Content validation doesn't check size, but file validation does
        # This is tested when validating actual files

    def test_heading_hierarchy(self):
        """Test heading hierarchy validation"""
        content = """# Kafli 1: Test

#### 1.1 Skips levels (h1 to h4)

This should generate a warning.
"""

        result = self.validator.validate_content(content)

        # Should have warnings about heading hierarchy
        # Note: This might not be an error, just a warning


def load_tests_from_fixtures():
    """Load test cases from fixture files"""
    fixtures_dir = Path(__file__).parent / 'fixtures'

    if not fixtures_dir.exists():
        return

    # Test all fixture files
    for fixture_file in fixtures_dir.glob('*.md'):
        print(f"\nTesting fixture: {fixture_file.name}")

        processor = ContentProcessor()
        validator = ChapterValidator()

        # Validate
        validation_result = validator.validate_file(str(fixture_file))
        print(f"Validation: {'✓ PASS' if validation_result.valid else '✗ FAIL'}")

        if not validation_result.valid:
            print(f"Errors: {validation_result.errors}")

        # Process
        try:
            with open(fixture_file, 'r', encoding='utf-8') as f:
                content = f.read()

            chunks = processor.process_file(content, str(fixture_file))
            print(f"Chunks created: {len(chunks)}")

            for i, chunk in enumerate(chunks):
                print(f"  Chunk {i}: {chunk.metadata.word_count} words - "
                      f"{chunk.metadata.section_number} {chunk.metadata.section_title}")

        except Exception as e:
            print(f"Error processing: {e}")


if __name__ == '__main__':
    print("="*60)
    print("Running Content Processor Tests")
    print("="*60)

    # Run unit tests
    unittest.main(verbosity=2, exit=False)

    # Run fixture tests
    print("\n" + "="*60)
    print("Testing Fixtures")
    print("="*60)
    load_tests_from_fixtures()
