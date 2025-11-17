# Icelandic Chemistry AI Tutor

An intelligent content processing pipeline for OpenStax Chemistry textbooks translated into Icelandic. This system processes markdown content, creates optimized chunks with metadata, generates embeddings, and stores them in a vector database for semantic search and AI-powered tutoring.

## Features

- **Intelligent Chunking**: Smart content segmentation that respects paragraph, list, and equation boundaries
- **Icelandic Language Support**: Full Unicode support for Icelandic characters (á, é, í, ó, ú, ý, þ, æ, ö, ð)
- **Metadata Extraction**: Automatic extraction of chapter numbers, sections, titles, and context
- **Quality Validation**: Comprehensive validation of markdown structure and content
- **Batch Processing**: Efficient processing of multiple chapters with progress tracking
- **Vector Database**: Integration with ChromaDB for semantic search capabilities
- **Multilingual Embeddings**: Uses sentence-transformers for high-quality text embeddings

## Project Structure

```
icelandic-chemistry-ai-tutor/
├── backend/
│   ├── src/
│   │   ├── content_processor.py    # Smart markdown chunking and processing
│   │   ├── batch_ingest.py         # Batch processing and ingestion
│   │   └── chapter_validator.py    # Content validation
│   ├── scripts/
│   │   └── process_openstack.sh    # Automation pipeline script
│   └── tests/
│       ├── test_processor.py       # Comprehensive test suite
│       └── fixtures/
│           └── sample_chapter.md   # Sample Icelandic chemistry content
├── data/
│   ├── chapters/                   # Input markdown files
│   └── logs/                       # Processing logs and reports
├── chroma_db/                      # ChromaDB vector database
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 2GB+ RAM (for embedding models)
- 1GB+ disk space (for models and database)

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor.git
cd icelandic-chemistry-ai-tutor
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

This will install:
- `chromadb` - Vector database
- `sentence-transformers` - Multilingual embeddings
- `tqdm` - Progress bars
- Additional NLP and testing tools

3. **Verify installation**

```bash
python -c "import chromadb, sentence_transformers; print('Installation successful!')"
```

## Usage

### Quick Start

1. **Place your markdown files in the input directory**

```bash
mkdir -p data/chapters
cp your_chapter.md data/chapters/
```

2. **Run the complete pipeline**

```bash
./backend/scripts/process_openstack.sh
```

This will:
- Validate all markdown files
- Process content into optimized chunks
- Generate embeddings
- Store in ChromaDB
- Generate comprehensive reports

### Individual Components

#### Content Processor

Process a single markdown file:

```python
from backend.src.content_processor import ContentProcessor

processor = ContentProcessor()

with open('data/chapters/kafli_1.md', 'r', encoding='utf-8') as f:
    content = f.read()

chunks = processor.process_file(content, 'kafli_1.md')

for chunk in chunks:
    print(f"Section {chunk.metadata.section_number}: {chunk.metadata.word_count} words")
```

#### Chapter Validator

Validate markdown content:

```bash
python backend/src/chapter_validator.py data/chapters/
```

Or programmatically:

```python
from backend.src.chapter_validator import ChapterValidator

validator = ChapterValidator()
result = validator.validate_file('data/chapters/kafli_1.md')

if result.valid:
    print("✓ Valid chapter")
else:
    print("✗ Validation errors:", result.errors)
```

#### Batch Ingestion

Process multiple files:

```bash
python backend/src/batch_ingest.py \
    --input data/chapters/ \
    --output chroma_db \
    --batch-size 100 \
    --verbose
```

Options:
- `--input DIR`: Input directory containing markdown files
- `--output DIR`: Output directory for ChromaDB
- `--batch-size N`: Number of chunks to process at once (default: 100)
- `--collection NAME`: ChromaDB collection name
- `--embedding-model MODEL`: Sentence transformer model to use
- `--no-validate`: Skip validation step
- `--verbose`: Enable verbose logging

### Automation Script

Run the complete pipeline with custom options:

```bash
# Basic usage
./backend/scripts/process_openstack.sh

# Custom directories and batch size
./backend/scripts/process_openstack.sh \
    --input my_chapters \
    --output my_db \
    --batch-size 200

# Skip validation for faster processing
./backend/scripts/process_openstack.sh --skip-validation

# Verbose mode with email notification
./backend/scripts/process_openstack.sh \
    --verbose \
    --email admin@example.com
```

## Content Format

### Expected Markdown Structure

Chapters should follow this format:

```markdown
# Kafli 1: Chapter Title

## 1.1 Section Title

Paragraph content here...

Multiple paragraphs are supported.

## 1.2 Another Section

- Bullet lists
- Are preserved
- As single units

### Subsections

Equations are preserved:

$$E = mc^2$$

Inline equations like $x = y$ also work.
```

### Chunking Rules

The content processor follows these rules:

1. **Target chunk size**: 400-600 words
2. **Minimum chunk size**: 200 words
3. **Maximum chunk size**: 1000 words
4. **Never split**:
   - Mid-paragraph
   - Mid-list (bullet or numbered)
   - Mid-equation
   - Nested lists
5. **Preserve context**: Section headers are included in each chunk

### Metadata

Each chunk includes comprehensive metadata:

```json
{
  "chapter_number": 1,
  "section_number": "1.1",
  "chapter_title": "Essential Ideas",
  "section_title": "Chemistry in Context",
  "chunk_index": 0,
  "word_count": 542,
  "language": "is"
}
```

## Testing

### Run Tests

```bash
# Run all tests
python -m pytest backend/tests/

# Run with coverage
python -m pytest backend/tests/ --cov=backend/src

# Run specific test file
python backend/tests/test_processor.py

# Verbose output
python backend/tests/test_processor.py -v
```

### Test Coverage

The test suite includes:

- ✓ Simple chapters (2 sections, 5 paragraphs)
- ✓ Complex chapters (equations, lists, images)
- ✓ Icelandic edge cases (all special characters)
- ✓ Large chapters (>10,000 words)
- ✓ Malformed markdown
- ✓ Empty sections
- ✓ Nested lists
- ✓ Mixed content types
- ✓ Validation edge cases

### Sample Data

Test with the provided sample chapter:

```bash
python backend/src/content_processor.py backend/tests/fixtures/sample_chapter.md
```

## Configuration

### Environment Variables

```bash
export PYTHON=python3              # Python command
export INPUT_DIR=data/chapters     # Default input directory
export OUTPUT_DIR=chroma_db        # Default output directory
export BATCH_SIZE=100              # Default batch size
```

### Embedding Models

The default embedding model is `paraphrase-multilingual-MiniLM-L12-v2`, which supports Icelandic and 50+ other languages.

Alternative models:

```bash
# Larger, more accurate (requires more RAM)
python backend/src/batch_ingest.py \
    --embedding-model paraphrase-multilingual-mpnet-base-v2

# Smaller, faster
python backend/src/batch_ingest.py \
    --embedding-model distiluse-base-multilingual-cased-v2
```

## Database

### ChromaDB

The processed content is stored in ChromaDB with:
- Document content (full chunk text)
- Embeddings (vector representations)
- Metadata (chapter, section, word count, etc.)

### Querying

```python
import chromadb

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("chemistry_chapters")

# Semantic search
results = collection.query(
    query_texts=["Hvað er atóm?"],  # "What is an atom?"
    n_results=5
)

for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
    print(f"Chapter {metadata['chapter_number']}, Section {metadata['section_number']}")
    print(doc[:200] + "...")
```

## Logging

Logs are stored in `data/logs/`:

- `ingest_YYYYMMDD_HHMMSS.log` - Main processing log
- `pipeline_YYYYMMDD_HHMMSS.log` - Pipeline execution log
- `stats_YYYYMMDD_HHMMSS.json` - Processing statistics
- `errors_YYYYMMDD_HHMMSS.json` - Error details
- `report_YYYYMMDD_HHMMSS.txt` - Summary report

## Performance

### Benchmarks

- **Processing speed**: ~100-200 chunks/second
- **Embedding generation**: ~50-100 texts/second (CPU)
- **Memory usage**: ~2GB (with default model)
- **Disk usage**: ~500KB per 1000 chunks

### Optimization Tips

1. **Increase batch size** for faster processing (if you have enough RAM)
2. **Use GPU** for embedding generation (10x faster)
3. **Skip validation** if content is already validated
4. **Use smaller embedding model** for faster processing

## Troubleshooting

### Common Issues

**ImportError: No module named 'chromadb'**
```bash
pip install chromadb sentence-transformers
```

**UnicodeDecodeError**
- Ensure files are saved as UTF-8
- Check for BOM (Byte Order Mark) at start of file

**Validation fails**
- Check chapter heading format: `# Kafli N: Title`
- Ensure section headings follow: `## N.M Title`
- Verify UTF-8 encoding

**Out of memory**
- Reduce batch size: `--batch-size 50`
- Use smaller embedding model
- Process files individually

## Development

### Code Style

```bash
# Format code
black backend/

# Lint
flake8 backend/

# Type check
mypy backend/src/
```

### Adding New Features

1. Add functionality to appropriate module in `backend/src/`
2. Write tests in `backend/tests/`
3. Update documentation
4. Run test suite
5. Submit pull request

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues, questions, or contributions:
- GitHub Issues: [Issues](https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor/issues)
- Documentation: This README and inline code documentation

## Acknowledgments

- OpenStax for open-source chemistry textbooks
- Icelandic translation contributors
- Sentence Transformers for multilingual embeddings
- ChromaDB for vector database infrastructure

---

**Version**: 1.0.0
**Last Updated**: November 2025
**Author**: Sigurdur Vilhelmsson
