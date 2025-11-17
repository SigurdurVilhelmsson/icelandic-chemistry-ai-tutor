# Icelandic Chemistry AI Tutor - Backend

RAG-based AI tutoring system for Icelandic high school chemistry students. Provides intelligent answers to chemistry questions in Icelandic with proper citations.

## Features

- **Retrieval-Augmented Generation (RAG)**: Combines semantic search with Claude Sonnet 4 for accurate, cited answers
- **Icelandic Language Support**: Full support for Icelandic characters and chemistry terminology
- **Vector Database**: ChromaDB for efficient semantic search
- **REST API**: FastAPI-based API for easy integration
- **Citation System**: Automatic source citations with chapter/section references
- **Production-Ready**: Comprehensive error handling, logging, and testing

## Tech Stack

- **LLM**: Anthropic Claude Sonnet 4 (claude-sonnet-4-20250514)
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Store**: ChromaDB (persistent, local)
- **Web Framework**: FastAPI + Uvicorn
- **Language**: Python 3.11+

## Project Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── rag_pipeline.py      # Core RAG orchestration
│   ├── vector_store.py       # ChromaDB management
│   ├── embeddings.py         # Embedding generation
│   ├── llm_client.py         # Claude Sonnet 4 wrapper
│   ├── main.py               # FastAPI application
│   ├── ingest.py             # Content ingestion script
│   └── inspect_db.py         # Database inspection utility
├── data/
│   └── sample/
│       └── basic_chemistry.md  # Sample Icelandic content
├── tests/
│   └── test_rag.py           # Integration tests
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── run_tests.sh              # Automated test script
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11 or higher
- Anthropic API key
- OpenAI API key

### 2. Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### 4. Ingest Content

```bash
# Ingest sample chemistry content
python -m src.ingest --data-dir ./data/sample --reset

# Check database
python -m src.inspect_db stats
```

## Running the Backend

### Start API Server

```bash
# Development mode (with auto-reload)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Documentation

### POST /ask

Ask a chemistry question in Icelandic.

**Request:**
```json
{
  "question": "Hvað er atóm?",
  "session_id": "user_123",
  "chapter_filter": null
}
```

**Response:**
```json
{
  "answer": "Atóm er minnsta eining efnis...",
  "citations": [
    {
      "chapter": "1",
      "section": "1",
      "title": "Atómbygging",
      "text_preview": "Atóm er minnsta eining efnis..."
    }
  ],
  "timestamp": "2025-11-17T10:30:00",
  "metadata": {
    "chunks_found": 5,
    "response_time_ms": 1250.5
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "db_chunks": 8,
  "timestamp": "2025-11-17T10:30:00",
  "version": "1.0.0"
}
```

### GET /stats

Get pipeline statistics.

**Response:**
```json
{
  "configuration": {
    "top_k": 5,
    "max_context_chunks": 4,
    "model": "claude-sonnet-4-20250514"
  },
  "database": {
    "total_chunks": 8,
    "unique_chapters": 1,
    "unique_sections": 4
  }
}
```

## Testing

### Run All Tests

```bash
# Run integration tests
python -m tests.test_rag

# Or use the automated script
bash run_tests.sh
```

### Run Specific Test

```bash
# Run pytest with specific test
pytest tests/test_rag.py::TestRAGPipeline::test_question_atom -v
```

## Database Management

### Inspect Database

```bash
# Show statistics
python -m src.inspect_db stats

# Show 5 random chunks
python -m src.inspect_db sample 5

# Show all chunks from chapter 1
python -m src.inspect_db search 1

# Verify metadata integrity
python -m src.inspect_db verify

# Export to JSON
python -m src.inspect_db export output.json
```

### Re-ingest Content

```bash
# Reset and re-ingest
python -m src.ingest --data-dir ./data/sample --reset

# Add new file without reset
python -m src.ingest --file ./data/sample/new_content.md
```

## Content Format

Chemistry content should be in Markdown format with the following structure:

```markdown
# Kafli 1: Chapter Title

## 1.1 Section Title

Section content in Icelandic...

## 1.2 Another Section

More content...
```

The ingestion system will:
- Extract chapter and section numbers from headers
- Chunk content into 300-800 word segments
- Preserve paragraph boundaries
- Generate embeddings
- Store in ChromaDB with metadata

## Development

### Code Structure

- **rag_pipeline.py**: Main RAG orchestration logic
- **vector_store.py**: ChromaDB wrapper for vector operations
- **embeddings.py**: OpenAI embedding generation with batching
- **llm_client.py**: Claude API wrapper with Icelandic prompt
- **main.py**: FastAPI application with CORS and logging
- **ingest.py**: Content chunking and database population
- **inspect_db.py**: CLI tool for database inspection

### Adding New Features

1. Update relevant module (e.g., `rag_pipeline.py`)
2. Add tests in `tests/test_rag.py`
3. Update API endpoints in `main.py` if needed
4. Update this README

### Logging

Logs are configured via the `LOG_LEVEL` environment variable:

```bash
# Set log level
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## Performance

- **Response Time**: < 3 seconds average
- **Embedding Cost**: ~$0.00002 per 1K tokens
- **Claude Cost**: Based on usage
- **Database**: Persistent, no re-indexing needed

## Troubleshooting

### Database Empty Error

```bash
# Re-run ingestion
python -m src.ingest --data-dir ./data/sample --reset
```

### API Key Errors

```bash
# Verify .env file exists and has correct keys
cat .env

# Check environment variables are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY'))"
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Icelandic Character Issues

Ensure files are saved with UTF-8 encoding. The system handles Icelandic characters (á, ð, þ, æ, ö, ó, í, ú, ý, é) correctly throughout.

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## Contact

For questions or issues, please open an issue on GitHub.
