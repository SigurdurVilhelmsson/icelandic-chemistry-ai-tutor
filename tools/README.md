# Icelandic Chemistry Content Generator

This directory contains tools for generating realistic Icelandic chemistry educational content for testing the RAG system.

## Overview

The content generator creates diverse, high-quality chemistry documents in Icelandic that cover chapters 1-5 of OpenStax Chemistry. It uses the Claude API to generate realistic educational content with proper terminology, structure, and variety.

## Features

- ✅ **AI-Powered Generation**: Uses Claude API for realistic, varied content
- ✅ **Comprehensive Coverage**: Covers all major topics in Chapters 1-5
- ✅ **Proper Icelandic Terminology**: 100+ chemistry terms accurately translated
- ✅ **Multiple Document Types**: Explanations, examples, problems, summaries
- ✅ **Configurable Difficulty**: Basic, intermediate, and advanced levels
- ✅ **RAG-Ready Metadata**: Complete metadata for vector store ingestion
- ✅ **Template Fallback**: Works without API using template-based generation

## Quick Start

### Generate 50 Sample Documents

```bash
# With Claude API (recommended)
export ANTHROPIC_API_KEY="your-api-key"
python tools/content_generator.py --count 50

# Without API (template-based)
python tools/content_generator.py --count 50 --no-api
```

### Complete Test Setup

```bash
# Run the automated setup script
./scripts/quick_test_setup.sh

# Or with custom settings
./scripts/quick_test_setup.sh 100 "1,2,3"  # 100 docs, chapters 1-3
```

## Usage

### Basic Usage

```bash
python tools/content_generator.py [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--count`, `-c` | Number of documents to generate | 50 |
| `--chapters` | Comma-separated chapter numbers (1-5) | "1,2,3,4,5" |
| `--difficulty` | Difficulty level: basic, intermediate, advanced | intermediate |
| `--output`, `-o` | Output directory path | tools/generated |
| `--no-api` | Use templates only (no API calls) | False |
| `--api-key` | Anthropic API key (or use env var) | $ANTHROPIC_API_KEY |

### Examples

```bash
# Generate 100 documents covering all chapters
python tools/content_generator.py --count 100

# Focus on specific chapters
python tools/content_generator.py --chapters 1,2,3 --count 30

# Generate basic difficulty content
python tools/content_generator.py --difficulty basic --count 25

# Custom output directory
python tools/content_generator.py --output data/test-content/

# Template-based (no API)
python tools/content_generator.py --no-api --count 20
```

## Content Coverage

### Chapter 1: Lykilhugtök efnafræðinnar (Essential Ideas)

- Chemistry in modern context
- States of matter (solid, liquid, gas)
- Physical and chemical properties
- Measurements and SI units
- Significant figures and calculations

### Chapter 2: Atóm, sameindir og jónir (Atoms, Molecules, Ions)

- Atomic theory
- Atomic structure (protons, neutrons, electrons)
- Isotopes and atomic symbols
- The periodic table organization
- Properties of elements

### Chapter 3: Efnasamsetning (Chemical Composition)

- Ionic bonding
- Covalent bonding
- Lewis structures
- Formal charge and resonance
- Molecular geometry (VSEPR)

### Chapter 4: Efnahvörf og efnajöfnuður (Reactions & Stoichiometry)

- Chemical equations and balancing
- Types of reactions (synthesis, decomposition, combustion)
- Stoichiometry and mole ratios
- Mole calculations and molar mass
- Limiting reactants and percent yield

### Chapter 5: Ítarlegri efnafræði (Advanced Topics)

- Thermochemistry basics (enthalpy, heat)
- Solution chemistry (concentration, molarity)
- Acids and bases (pH, neutralization)
- Redox reactions (oxidation, reduction)

## Document Types

The generator creates four types of documents with different characteristics:

### Explanations (40%)

- **Purpose**: Detailed conceptual explanations
- **Length**: 400-700 words
- **Focus**: Clear understanding of concepts
- **Example topics**: "What is atomic structure?", "Understanding chemical bonding"

### Examples (30%)

- **Purpose**: Worked examples with solutions
- **Length**: 300-600 words
- **Focus**: Step-by-step problem solving
- **Example topics**: "Balancing chemical equations", "Calculating molar mass"

### Problems (20%)

- **Purpose**: Practice problems with hints
- **Length**: 200-400 words
- **Focus**: Student practice and application
- **Example topics**: "Stoichiometry practice", "Electron configuration exercises"

### Summaries (10%)

- **Purpose**: Concise reviews and summaries
- **Length**: 300-500 words
- **Focus**: Key concepts and review
- **Example topics**: "Chapter 1 summary", "Key concepts in bonding"

## Icelandic Terminology

The generator includes comprehensive Icelandic chemistry terminology:

### Basic Concepts

| English | Icelandic |
|---------|-----------|
| atom | atóm |
| molecule | sameind |
| element | frumefni |
| compound | efnasamband |
| reaction | efnahvörf |

### Atomic Structure

| English | Icelandic |
|---------|-----------|
| electron | rafeind |
| proton | róteind |
| neutron | nifteind |
| nucleus | kjarninn |
| isotope | samsæta |

### Chemical Bonding

| English | Icelandic |
|---------|-----------|
| covalent bond | samgildt tengi |
| ionic bond | jónatengi |
| metallic bond | málmtengi |
| hydrogen bond | vetnistengi |
| electronegativity | rafsækni |

### States of Matter

| English | Icelandic |
|---------|-----------|
| solid | fast efni |
| liquid | vökvi |
| gas | loft |
| melting | bræðsla |
| boiling | seyðing |

### Stoichiometry

| English | Icelandic |
|---------|-----------|
| mole | mól |
| molar mass | mólmassi |
| limiting reactant | takmarkandi hvarfefni |
| percent yield | prósentuafkoma |

[See content_generator.py for complete terminology list - 100+ terms]

## Generated Document Structure

Each document includes:

### YAML Frontmatter

```yaml
---
chapter: 1
section: "1.2"
chapter_title: "Lykilhugtök efnafræðinnar"
section_title: "Ástand efnis"
language: "is"
word_count: 542
generated: true
difficulty: "intermediate"
topics:
  - solid
  - liquid
  - gas
  - phase transitions
doc_type: "explanation"
generated_at: "2025-11-17T10:30:45.123456"
---
```

### Content Structure

```markdown
# Kafli 1: Lykilhugtök efnafræðinnar

## 1.2 Ástand efnis

### Inngangur
[Introduction paragraph]

### Lykilhugtök
[Key concepts]

### Skýringar
[Detailed explanations]

### Dæmi
[Examples]

### Samantekt
[Summary]
```

## File Naming Convention

Generated files follow this pattern:

```
ch{chapter}_sec{section}_{type}_{index}.md
```

Examples:
- `ch1_sec1_1_explanation_001.md`
- `ch2_sec2_3_example_015.md`
- `ch3_sec3_2_problem_042.md`

## Output Statistics

After generation, you'll see detailed statistics:

```
============================================================
Generation Complete!
============================================================

✅ Generated: 50 documents
📊 Total words: 27,543
📈 Average words/doc: 550

📚 By chapter:
   Kafli 1: 10 docs
   Kafli 2: 10 docs
   Kafli 3: 10 docs
   Kafli 4: 10 docs
   Kafli 5: 10 docs

📝 By type:
   Explanation: 20 docs
   Example: 15 docs
   Problem: 10 docs
   Summary: 5 docs

💾 Saved to: /path/to/tools/generated
```

## Integration with RAG System

### Step 1: Generate Content

```bash
python tools/content_generator.py --count 50
```

### Step 2: Ingest into Vector Store

```bash
cd backend
python src/batch_ingest.py --input ../tools/generated/ --batch-size 10
```

### Step 3: Test Retrieval

```bash
# Start the backend
uvicorn src.main:app --reload

# Test with Icelandic query
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"question": "Hvað er atóm?", "language": "is"}'
```

## Quality Controls

The generator implements several quality controls:

1. **Word Count Validation**
   - Minimum: 200 words (problems) to 400 words (explanations)
   - Maximum: 400 words (problems) to 700 words (explanations)

2. **Content Diversity**
   - Varied sentence length and structure
   - Different explanation styles
   - Mix of formal and accessible language
   - Real-world examples and analogies

3. **Terminology Accuracy**
   - Proper Icelandic chemistry terms
   - Consistent usage across documents
   - Context-appropriate vocabulary

4. **Metadata Completeness**
   - All required fields present
   - Valid chapter/section numbers
   - Accurate topic tagging

5. **Encoding Validation**
   - UTF-8 encoding for Icelandic characters
   - Proper handling of special characters (á, ð, þ, etc.)

## Templates

Template files in `templates/` provide structure for manual editing:

### chapter_template.md

Base structure for chapter-level content with sections for:
- Introduction
- Key concepts
- Detailed explanations
- Examples
- Practice problems
- Summary
- Vocabulary

### section_template.md

Structure for section-level content with:
- Learning objectives
- Main content
- Key points
- Real-world connections
- Terminology table

## Troubleshooting

### API Key Issues

```bash
# Set API key in environment
export ANTHROPIC_API_KEY="your-api-key-here"

# Or pass directly
python tools/content_generator.py --api-key "your-api-key-here"

# Or use templates only
python tools/content_generator.py --no-api
```

### Import Errors

```bash
# Install required packages
pip install anthropic

# Or install all backend requirements
cd backend
pip install -r requirements.txt
```

### Unicode/Encoding Issues

The generator handles Icelandic characters (á, ð, é, í, ó, ú, ý, þ, æ, ö) automatically. All files are saved with UTF-8 encoding.

### Generation Fails

If API generation fails, the generator automatically falls back to template-based content.

## Directory Structure

```
tools/
├── README.md                 # This file
├── content_generator.py      # Main generator script
├── templates/
│   ├── chapter_template.md   # Chapter structure template
│   └── section_template.md   # Section structure template
└── generated/                # Output directory (gitignored)
    ├── ch1_sec1_1_*.md
    ├── ch1_sec1_2_*.md
    └── ...
```

## Development

### Adding New Topics

Edit `CHAPTER_TOPICS` in `content_generator.py`:

```python
CHAPTER_TOPICS = {
    6: {  # New chapter
        "title": "New Chapter Title",
        "sections": [
            {
                "num": "6.1",
                "title": "Section Title",
                "topics": ["topic1", "topic2"]
            }
        ]
    }
}
```

### Adding Terminology

Edit `CHEMISTRY_TERMS` in `content_generator.py`:

```python
CHEMISTRY_TERMS = {
    # ... existing terms
    "new term": "nýtt hugtak",
}
```

### Customizing Document Types

Edit `DOCUMENT_TYPES` in `content_generator.py`:

```python
DOCUMENT_TYPES = {
    "new_type": {
        "weight": 0.15,  # 15% of documents
        "min_words": 300,
        "max_words": 500,
        "prompt_style": "description for Claude"
    }
}
```

## Best Practices

1. **Start Small**: Generate 10-20 documents first to verify quality
2. **Review Output**: Check generated content before ingestion
3. **Mix Difficulties**: Use different difficulty levels for comprehensive testing
4. **Test Retrieval**: Verify that generated content is properly retrieved
5. **Iterate**: Adjust parameters based on testing results

## Performance

- **With API**: ~5-10 seconds per document (depending on length)
- **Without API**: <1 second per document (template-based)
- **Recommended**: Generate in batches of 50-100 documents

## License

This tool is part of the Icelandic Chemistry AI Tutor project.

## Support

For issues or questions:
1. Check this README
2. Review example output in `generated/`
3. Test with `--no-api` first
4. Verify ANTHROPIC_API_KEY is set correctly
5. Check backend/requirements.txt for dependencies
