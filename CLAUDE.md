# CLAUDE.md - AI Assistant Guide

**Project:** Icelandic Chemistry AI Tutor
**Last Updated:** 2025-11-18
**Purpose:** Guide for AI assistants working on this codebase

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Development Workflows](#development-workflows)
4. [Key Conventions](#key-conventions)
5. [Testing Practices](#testing-practices)
6. [Common Tasks](#common-tasks)
7. [Important Patterns](#important-patterns)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

### What This Is
A RAG (Retrieval-Augmented Generation) based AI teaching assistant for Icelandic high school chemistry students. It provides 24/7 personalized learning support entirely in Icelandic, using curriculum-aligned content.

### Core Technology Stack
- **Backend:** Python 3.11, FastAPI, LangChain, ChromaDB
- **LLM:** Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- **Embeddings:** OpenAI `text-embedding-3-small`
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **Infrastructure:** Docker, Nginx, Linode, Let's Encrypt

### Key Characteristics
1. **Bilingual Code:** Code/variables in English, all user-facing text in Icelandic
2. **UTF-8 Everywhere:** Full Icelandic character support (á, ð, é, í, ó, ú, ý, þ, æ, ö)
3. **RAG-First:** All answers cite sources from curriculum content
4. **Education-Focused:** System prompts tuned for teaching, not just answering
5. **Cost-Conscious:** Token tracking and monitoring throughout

### Funding & Context
- **Funded by:** RANNÍS Sprotasjóður (3.6M ISK, 2025-2026)
- **Status:** MVP Phase
- **Schools:** Kvennaskólinn í Reykjavík, Fjölbrautaskólinn við Ármúla
- **License:** MIT

---

## 📁 Codebase Structure

### Root Directory Layout
```
icelandic-chemistry-ai-tutor/
├── backend/              # Python FastAPI application
├── frontend/             # React TypeScript application
├── nginx/                # Web server configuration
├── scripts/              # Deployment and utility scripts
├── dev-tools/            # Developer debugging tools
├── monitoring/           # Health monitoring tools
├── docs/                 # Project documentation
├── .github/              # GitHub workflows and templates
└── [config files]        # Root-level configuration
```

### Backend Structure (`/backend/src/`)

**Core Application Files:**

```python
backend/src/
├── main.py                    # FastAPI app entry point
│   # - CORS middleware configuration
│   # - Health check at /health
│   # - Main /ask endpoint
│   # - Pydantic request/response models
│
├── rag_pipeline.py            # RAG orchestration coordinator
│   # - RAGPipeline class: question → embedding → search → LLM → response
│   # - Config: top_k=5, max_context_chunks=4
│   # - Returns: answer, citations, metadata, timing, token usage
│
├── vector_store.py            # ChromaDB interface
│   # - VectorStore class with persistent storage
│   # - Collection: "icelandic_chemistry"
│   # - Methods: add_documents(), search(), get_stats()
│   # - Persistent path: ./data/chroma_db
│
├── llm_client.py              # Claude API client
│   # - Model: claude-sonnet-4-20250514
│   # - Icelandic system prompt for chemistry tutoring
│   # - Retry logic with exponential backoff
│   # - Returns: answer with citations, token usage
│
├── embeddings.py              # OpenAI embedding generation
│   # - Model: text-embedding-3-small
│   # - Batch processing support (batch_size=100)
│   # - Cost tracking: $0.00002 per 1K tokens
│   # - ChromaEmbeddingFunction wrapper for ChromaDB
│
├── content_processor.py       # Markdown chunking
│   # - Chunk constraints: MIN=200, TARGET_MIN=400, TARGET_MAX=600, MAX=1000 words
│   # - Preserves structure: headings, lists, equations, code blocks
│   # - Extracts metadata: chapter, section, title
│   # - UTF-8 validation for Icelandic characters
│
├── ingest.py                  # Content ingestion CLI
│   # - ContentChunker (min_words=300, max_words=800)
│   # - ContentIngester for batch processing
│   # - CLI: --reset, --file, --data-dir, --db-path
│
├── batch_ingest.py            # Advanced batch processing
│   # - ProcessingStats dataclass for tracking
│   # - Progress bars with tqdm
│   # - File validation and error handling
│
├── chapter_validator.py       # Content quality validation
│   # - UTF-8 encoding checks
│   # - Metadata completeness
│   # - Word count validation
│
└── inspect_db.py              # Database debugging utilities
    # - View statistics
    # - Search/query testing
    # - Export capabilities
```

**Backend Testing Structure:**

```python
backend/tests/
├── conftest.py                # Shared fixtures (CRITICAL FILE)
│   # Fixture categories:
│   # - Paths: project_root, fixtures_dir, test_data_dir
│   # - Test data: sample_content, sample_chunks, expected_responses
│   # - Mocks: mock_embeddings, mock_openai_client, mock_claude_client
│   # - Vector store: temp_chroma_db, mock_vector_store
│   # - FastAPI: test_client, mock_app_dependencies
│   # - Icelandic: icelandic_test_cases
│   # - Performance: performance_timer
│
├── fixtures/                  # Test data files
│   ├── sample_content.json    # Sample Icelandic chemistry content
│   ├── expected_responses.json # Expected AI responses
│   └── mock_embeddings.json   # Mock embedding vectors
│
├── test_rag_pipeline.py       # RAG pipeline tests
├── test_vector_store.py       # ChromaDB tests
├── test_llm_client.py         # Claude API client tests
├── test_embeddings.py         # Embedding generation tests
├── test_content_processor.py  # Content chunking tests
├── test_api_endpoints.py      # FastAPI endpoint tests
├── test_integration.py        # End-to-end integration tests
└── test_processor.py          # Additional processor tests
```

**Test Markers** (defined in `pytest.ini`):
- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests across components
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Tests taking >1 second
- `@pytest.mark.api` - Tests with external API interactions (mocked)
- `@pytest.mark.db` - Database interaction tests
- `@pytest.mark.icelandic` - Icelandic language handling tests
- `@pytest.mark.performance` - Performance benchmarks
- `@pytest.mark.smoke` - Critical functionality smoke tests

### Frontend Structure (`/frontend/src/`)

```typescript
frontend/src/
├── main.tsx                   # Entry point (renders App)
├── App.tsx                    # Root component (wraps ChatProvider)
│
├── components/                # React components (all .tsx)
│   ├── ChatInterface.tsx      # Main chat container
│   │   # Layout: Sidebar + Header + Messages + Input
│   │   # Uses useChat() hook, auto-scrolls
│   │   # Features: export, clear, history
│   │
│   ├── ChatInput.tsx          # Message input
│   │   # Textarea with auto-resize
│   │   # Send on Ctrl/Cmd+Enter
│   │   # Disabled during loading
│   │
│   ├── Message.tsx            # Individual message display
│   │   # Differentiates student/assistant
│   │   # Renders citations with CitationCard
│   │   # Markdown support, timestamps
│   │
│   ├── CitationCard.tsx       # Source citation display
│   │   # Shows chapter/section info
│   │   # Expandable text preview
│   │
│   ├── ConversationSidebar.tsx # History sidebar
│   │   # Lists past conversations
│   │   # Load/delete functionality
│   │   # Responsive mobile drawer
│   │
│   ├── Modal.tsx              # Reusable modal dialogs
│   │   # Confirmation dialogs
│   │   # Backdrop/keyboard navigation
│   │
│   └── Toast.tsx              # Notification system
│       # Success/error/info types
│       # Auto-dismiss after 5s
│
├── contexts/                  # State management
│   └── ChatContext.tsx        # Global chat state
│       # Pattern: Context + Reducer
│       # State: sessionId, messages, isLoading, error, toasts
│       # Methods: sendMessage, loadConversation, newConversation,
│       #          clearConversation, exportConversation, showToast
│       # Auto-saves to localStorage
│       # Auto-loads last conversation on mount
│
├── utils/                     # Utility functions
│   ├── api.ts                 # API client with retry logic
│   │   # sendMessage(question, sessionId): Promise<ChatResponse>
│   │   # healthCheck(): Promise<boolean>
│   │   # Retry with exponential backoff (MAX_RETRIES=3)
│   │   # Timeout: 30s, don't retry 4xx errors
│   │
│   ├── storage.ts             # localStorage wrapper
│   │   # generateSessionId(), saveConversation(), loadConversation()
│   │   # deleteConversation(), listConversations()
│   │   # clearAllConversations(), getCurrentSessionId()
│   │
│   └── export.ts              # CSV export utility
│       # exportConversationToCSV(sessionId, messages)
│       # Format: Timestamp, Role, Message, Citations
│
└── types/                     # TypeScript type definitions
    └── index.ts               # Core types
        # Citation, Message, ChatResponse, ChatState, ToastMessage
```

### Development Tools (`/dev-tools/`)

```
dev-tools/
├── backend/                   # Backend debugging tools
│   ├── rag_debugger.py        # Interactive RAG pipeline debugger
│   │   # - Step-by-step execution visualization
│   │   # - Token counting and cost calculation
│   │   # - Context inspection
│   │   # - Export debug logs as JSON
│   │
│   ├── db_inspector.py        # ChromaDB web UI (Flask, port 5001)
│   │   # - Browse/search/filter chunks
│   │   # - Export to CSV/JSON
│   │   # - Statistics dashboard
│   │
│   ├── search_visualizer.py  # Visual similarity search analysis
│   │   # - Terminal bar charts
│   │   # - Similarity score distribution
│   │   # - Metadata analysis
│   │
│   ├── token_tracker.py       # API cost monitoring
│   │   # - Track embedding/LLM token usage
│   │   # - Cost projections (daily/monthly)
│   │   # - Budget alerts
│   │
│   └── performance_profiler.py # Pipeline performance analysis
│       # - Time breakdown by component
│       # - Bottleneck identification
│       # - Export profiling data
│
└── scripts/                   # Helper scripts
    └── dev_server.sh          # Development server launcher
        # - Environment setup
        # - Port checking
        # - Optional DB inspector launch
```

### Deployment Scripts (`/scripts/`)

```bash
scripts/
├── setup_linode.sh            # Initial Linode server setup
├── setup_nginx.sh             # Nginx configuration
├── deploy.sh                  # Full deployment (backend + frontend)
├── deploy_backend.sh          # Backend only deployment
├── deploy_frontend.sh         # Frontend only deployment
├── complete_deploy.sh         # Complete deployment pipeline
├── build_and_deploy.sh        # Build then deploy
├── backup.sh                  # ChromaDB backup
├── restore.sh                 # ChromaDB restore
├── renew_ssl.sh               # SSL certificate renewal
├── run_all_tests.sh           # Run complete test suite
├── test_coverage.sh           # Generate coverage report
└── quick_test_setup.sh        # Quick test environment setup
```

### Documentation (`/docs/`)

Comprehensive project documentation:
- `ARCHITECTURE.md` - System architecture and design decisions
- `API_REFERENCE.md` - API endpoint documentation
- `DEVELOPMENT.md` - Development guide and local setup
- `CONTRIBUTING.md` - Contribution guidelines
- `USER_GUIDE_IS.md` - Icelandic user guide for students
- `TEACHER_GUIDE_IS.md` - Icelandic teacher guide

---

## 🔧 Development Workflows

### Initial Setup

**Backend Setup:**
```bash
cd /home/user/icelandic-chemistry-ai-tutor/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add ANTHROPIC_API_KEY and OPENAI_API_KEY

# Run development server
uvicorn src.main:app --reload --port 8000
```

**Frontend Setup:**
```bash
cd /home/user/icelandic-chemistry-ai-tutor/frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
nano .env  # Set VITE_API_ENDPOINT=http://localhost:8000

# Run development server
npm run dev
```

**Access Points:**
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Common Development Commands

**Backend:**
```bash
# Run all tests
pytest tests/ -v

# Run specific test markers
pytest tests/ -m unit -v
pytest tests/ -m integration -v
pytest tests/ -m icelandic -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_rag_pipeline.py -v

# Run in parallel (faster)
pytest tests/ -n auto

# Lint and format
black src/ tests/
flake8 src/ tests/
mypy src/
isort src/ tests/

# Ingest content
python -m src.ingest --file data/chapters/chapter1.md
python -m src.batch_ingest --data-dir data/chapters/

# Inspect database
python -m src.inspect_db
python dev-tools/backend/db_inspector.py  # Web UI on port 5001

# Debug RAG pipeline
python dev-tools/backend/rag_debugger.py
```

**Frontend:**
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint

# Type check
npx tsc --noEmit
```

**Docker (Full Stack):**
```bash
# Build and run backend
cd backend
docker-compose up --build

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Git Workflow

**Branch Naming:**
- Feature branches: `claude/feature-name-{sessionId}`
- Always work on the designated branch (check task description)
- Never push to `main` directly

**Commit Conventions:**
```bash
# Good commit messages
git commit -m "Add Icelandic character validation to content processor"
git commit -m "Fix citation extraction for multi-paragraph chunks"
git commit -m "Update RAG pipeline to use max_context_chunks=4"

# Run tests before committing
pytest tests/ -v
npm run lint

# Push to designated branch
git push -u origin claude/feature-name-{sessionId}
```

**Recent Development Pattern:**
Looking at git history, this project follows a PR-based workflow:
- Features developed in `claude/*` branches
- PRs merged after review
- Recent PRs: testing infrastructure, dev tools, content generation

---

## 🎨 Key Conventions

### Naming Conventions

**Python (Backend):**
```python
# Files: snake_case.py
# main.py, rag_pipeline.py, content_processor.py

# Classes: PascalCase
class RAGPipeline:
class VectorStore:
class ContentChunker:

# Functions/methods: snake_case
def process_content(text: str) -> List[Dict]:
def generate_embedding(text: str) -> List[float]:

# Constants: UPPER_SNAKE_CASE
MAX_CHUNK_SIZE = 1000
DEFAULT_TOP_K = 5
ICELANDIC_CHARS = "áðéíóúýþæö"

# Private methods: _leading_underscore
def _validate_chunk(self, chunk: str) -> bool:
```

**TypeScript (Frontend):**
```typescript
// Files: PascalCase.tsx for components, camelCase.ts for utilities
// ChatInterface.tsx, Message.tsx, api.ts, storage.ts

// Components: PascalCase
function ChatInterface() { }
function CitationCard() { }

// Functions: camelCase
function sendMessage(question: string): Promise<ChatResponse>
function generateSessionId(): string

// Constants: UPPER_SNAKE_CASE
const MAX_RETRIES = 3;
const TIMEOUT_MS = 30000;

// Interfaces: PascalCase (no I prefix)
interface Message { }
interface ChatState { }
```

### Icelandic Language Handling

**Critical Pattern:**
- **Code/variables:** English (for international collaboration)
- **User-facing text:** Icelandic (UI labels, messages, prompts)
- **Comments:** English (for code documentation)

**Examples:**

```typescript
// ✅ CORRECT
function sendMessage(question: string) {
  showToast('Villa kom upp', 'error');  // Icelandic UI message
  const errorText = 'Ekki tókst að tengjast';  // Icelandic for users
}

// ❌ INCORRECT
function sendaSkeyti(spurning: string) {  // Don't translate code
  showToast('Error occurred', 'error');   // UI must be Icelandic
}
```

**Icelandic Character Validation:**
```python
# Always validate UTF-8 encoding
ICELANDIC_CHARS = "áðéíóúýþæö"

def contains_icelandic(text: str) -> bool:
    """Check if text contains Icelandic characters"""
    return any(char.lower() in ICELANDIC_CHARS for char in text)

# In content processing
def validate_encoding(text: str) -> bool:
    """Ensure text preserves Icelandic characters"""
    try:
        text.encode('utf-8').decode('utf-8')
        return True
    except UnicodeError:
        return False
```

### Import Organization

**Python:**
```python
"""Module docstring describing purpose"""

# 1. Standard library imports
import os
import logging
from typing import List, Dict, Optional

# 2. Third-party imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb

# 3. Local imports (relative)
from .vector_store import VectorStore
from .embeddings import get_embedding_function

# Logger setup (after imports)
logger = logging.getLogger(__name__)
```

**TypeScript:**
```typescript
// 1. React imports
import React, { useState, useEffect, useCallback } from 'react';

// 2. Third-party imports
import { Search, Send, Trash } from 'lucide-react';

// 3. Local imports (organized by type)
import { useChat } from '../contexts/ChatContext';
import { Message, Citation } from '../types';
import { sendMessage } from '../utils/api';
```

### Error Handling Patterns

**Backend Error Handling:**
```python
# Pattern: Log, handle specific errors, raise HTTPException
logger = logging.getLogger(__name__)

try:
    logger.info(f"Processing question: '{question[:100]}...'")
    result = await process_question(question)
    logger.info("Successfully processed question")
    return result

except ValueError as e:
    logger.error(f"Validation error: {e}")
    raise HTTPException(status_code=400, detail=str(e))

except anthropic.APIError as e:
    logger.error(f"Claude API error: {e}")
    raise HTTPException(status_code=503, detail="AI service unavailable")

except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

**Frontend Error Handling:**
```typescript
// Pattern: Try/catch with user-friendly Icelandic messages
try {
  dispatch({ type: 'SET_LOADING', payload: true });

  const response = await apiSendMessage(question, sessionId);

  // Handle success
  dispatch({ type: 'ADD_MESSAGE', payload: response });
  showToast('Svar móttekið', 'success');

} catch (error) {
  // User-friendly error messages in Icelandic
  const errorMessage = error instanceof ApiError
    ? error.message
    : 'Villa kom upp við að senda skilaboð';

  dispatch({ type: 'SET_ERROR', payload: errorMessage });
  showToast(errorMessage, 'error');

  // Log for debugging
  console.error('Error sending message:', error);
}
```

**API Client Retry Pattern:**
```typescript
// Retry with exponential backoff
const MAX_RETRIES = 3;

for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
  try {
    const response = await fetchWithTimeout(url, options);
    return response;

  } catch (error) {
    // Don't retry client errors (4xx)
    if (error instanceof ApiError &&
        error.status >= 400 && error.status < 500) {
      throw error;
    }

    // Retry server errors with backoff
    if (attempt < MAX_RETRIES - 1) {
      const delay = Math.pow(2, attempt) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
      continue;
    }

    throw error;
  }
}
```

### Documentation Style

**Python Docstrings (Google style):**
```python
def process_question(
    question: str,
    top_k: int = 5,
    max_context_chunks: int = 4
) -> Dict[str, Any]:
    """
    Process a chemistry question using RAG pipeline.

    Generates embedding, searches vector store, formats context,
    and calls Claude API for answer generation.

    Args:
        question: User's question in Icelandic
        top_k: Number of chunks to retrieve from vector store
        max_context_chunks: Maximum chunks to include in LLM context

    Returns:
        Dictionary containing:
            - answer: AI-generated answer in Icelandic
            - citations: List of source citations
            - metadata: Token usage, timing info

    Raises:
        ValueError: If question is empty or too long
        RuntimeError: If vector store or LLM API fails

    Example:
        >>> result = process_question("Hvað er súra?")
        >>> print(result['answer'])
        "Súra er efni sem gefur frá sér vetnisróteind (H⁺)..."
    """
```

**TypeScript JSDoc:**
```typescript
/**
 * Send a message to the AI tutor and receive a response
 *
 * Implements retry logic with exponential backoff for transient errors.
 * Does not retry client errors (4xx status codes).
 *
 * @param question - User's question in Icelandic
 * @param sessionId - Unique session identifier for conversation tracking
 * @returns Promise resolving to chat response with answer and citations
 *
 * @throws {ApiError} With status code and message if request fails
 *
 * @example
 * ```typescript
 * const response = await sendMessage("Hvað er súra?", "session_123");
 * console.log(response.answer);
 * console.log(response.citations);
 * ```
 */
export async function sendMessage(
  question: string,
  sessionId: string
): Promise<ChatResponse> {
  // Implementation
}
```

---

## 🧪 Testing Practices

### Test Organization

**Test File Structure:**
```python
"""Tests for RAG pipeline functionality"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.rag_pipeline import RAGPipeline

# Use markers for categorization
@pytest.mark.unit
class TestRAGPipelineInit:
    """Test RAGPipeline initialization"""

    def test_default_initialization(self):
        """Test pipeline initializes with default parameters"""
        pipeline = RAGPipeline()
        assert pipeline.top_k == 5
        assert pipeline.max_context_chunks == 4

    def test_custom_initialization(self):
        """Test pipeline initializes with custom parameters"""
        pipeline = RAGPipeline(top_k=10, max_context_chunks=6)
        assert pipeline.top_k == 10

@pytest.mark.integration
class TestRAGPipelineQuestionAnswering:
    """Test end-to-end question answering"""

    @patch('src.embeddings.EmbeddingGenerator')
    @patch('src.llm_client.ClaudeClient')
    @patch('src.vector_store.VectorStore')
    def test_ask_chemistry_question(
        self,
        mock_vs_class,
        mock_llm_class,
        mock_emb_class
    ):
        """Test asking a chemistry question returns valid response"""
        # Arrange
        mock_vs = Mock()
        mock_vs.search.return_value = [...]  # Mock search results

        mock_llm = Mock()
        mock_llm.generate.return_value = {...}  # Mock LLM response

        # Act
        pipeline = RAGPipeline()
        result = pipeline.ask("Hvað er súra?")

        # Assert
        assert 'answer' in result
        assert 'citations' in result
        assert isinstance(result['citations'], list)
```

### Using Fixtures (conftest.py)

**Common Test Fixtures:**
```python
# In conftest.py - these are available to all tests

@pytest.fixture
def sample_icelandic_content():
    """Sample Icelandic chemistry content for testing"""
    return {
        "chapter": "1",
        "section": "1.1",
        "title": "Inngangur að efnafræði",
        "content": "Efnafræði er vísindi um efni og eiginleika þeirra..."
    }

@pytest.fixture
def mock_claude_response():
    """Mock response from Claude API"""
    return {
        "answer": "Súra er efni sem gefur frá sér vetnisróteind (H⁺).",
        "citations": [
            {
                "chapter": "8",
                "section": "8.1",
                "title": "Súrur og basar",
                "chunk_text": "Súra er efni sem..."
            }
        ],
        "token_usage": {"input": 150, "output": 50}
    }

@pytest.fixture
def temp_chroma_db(tmp_path):
    """Temporary ChromaDB instance for testing"""
    db_path = tmp_path / "test_chroma_db"
    return VectorStore(persist_directory=str(db_path))

# Use in tests
def test_vector_search(temp_chroma_db, sample_icelandic_content):
    """Test vector search returns relevant results"""
    temp_chroma_db.add_documents([sample_icelandic_content])
    results = temp_chroma_db.search("efni", top_k=5)
    assert len(results) > 0
```

### Test Execution Patterns

**Run Specific Test Categories:**
```bash
# Unit tests only (fast)
pytest tests/ -m unit -v

# Integration tests
pytest tests/ -m integration -v

# Icelandic language tests
pytest tests/ -m icelandic -v

# Slow tests only
pytest tests/ -m slow -v

# Exclude slow tests
pytest tests/ -m "not slow" -v

# Smoke tests (critical functionality)
pytest tests/ -m smoke -v

# Combine markers
pytest tests/ -m "unit and not slow" -v
```

**Coverage Requirements:**
```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html

# Fail if coverage below threshold
pytest tests/ --cov=src --cov-fail-under=80
```

### Mocking External APIs

**Mock Claude API:**
```python
@pytest.fixture
def mock_claude_client():
    """Mock Claude API client"""
    with patch('anthropic.Anthropic') as mock:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Mocked answer")]
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)
        mock_client.messages.create.return_value = mock_response
        mock.return_value = mock_client
        yield mock_client

def test_llm_call(mock_claude_client):
    """Test LLM client makes correct API call"""
    from src.llm_client import ClaudeClient

    client = ClaudeClient()
    response = client.generate("Test question")

    # Verify API was called correctly
    mock_claude_client.messages.create.assert_called_once()
    assert "answer" in response
```

**Mock OpenAI Embeddings:**
```python
@pytest.fixture
def mock_embedding_function():
    """Mock OpenAI embedding function"""
    with patch('openai.OpenAI') as mock:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock.return_value = mock_client
        yield mock_client
```

### Testing Icelandic Content

**Icelandic Character Preservation:**
```python
@pytest.mark.icelandic
def test_icelandic_characters_preserved():
    """Test that Icelandic characters are preserved through pipeline"""
    question = "Hvað er súra og basi í efnafræði?"

    # Process through pipeline
    result = process_question(question)

    # Check Icelandic characters preserved
    icelandic_chars = "áðéíóúýþæö"
    assert any(char in result['answer'] for char in icelandic_chars)

@pytest.mark.icelandic
def test_content_encoding():
    """Test content maintains UTF-8 encoding"""
    content = "Efnafræði rannsakar efni og eiginleika þeirra"

    # Encode and decode
    encoded = content.encode('utf-8')
    decoded = encoded.decode('utf-8')

    assert content == decoded
```

---

## 📋 Common Tasks

### Adding New Features

**1. Backend Feature (e.g., new RAG parameter):**

```python
# Step 1: Update the core module (src/rag_pipeline.py)
class RAGPipeline:
    def __init__(
        self,
        top_k: int = 5,
        max_context_chunks: int = 4,
        new_parameter: str = "default"  # Add new parameter
    ):
        self.new_parameter = new_parameter

# Step 2: Add tests (tests/test_rag_pipeline.py)
@pytest.mark.unit
def test_new_parameter():
    """Test new parameter works as expected"""
    pipeline = RAGPipeline(new_parameter="custom")
    assert pipeline.new_parameter == "custom"

# Step 3: Update documentation
# - Update docstring in rag_pipeline.py
# - Update docs/API_REFERENCE.md if needed

# Step 4: Run tests
# pytest tests/test_rag_pipeline.py -v
```

**2. Frontend Feature (e.g., new UI component):**

```typescript
// Step 1: Create component (src/components/NewFeature.tsx)
interface NewFeatureProps {
  // Props interface
}

export function NewFeature({ ...props }: NewFeatureProps) {
  // Component logic
  return (
    <div className="...">
      {/* Icelandic UI text */}
    </div>
  );
}

// Step 2: Add to parent component
import { NewFeature } from './NewFeature';

function ParentComponent() {
  return (
    <>
      <ExistingComponent />
      <NewFeature />
    </>
  );
}

// Step 3: Update types if needed (src/types/index.ts)
export interface NewFeatureData {
  // Type definition
}

// Step 4: Test manually and lint
// npm run lint
// npm run dev
```

### Debugging RAG Pipeline

**Use the RAG Debugger:**
```bash
# Interactive debugging
python dev-tools/backend/rag_debugger.py

# Features:
# - Step through pipeline execution
# - View embedding generation
# - Inspect vector search results
# - See context formatting
# - View LLM prompts and responses
# - Token count and cost calculation
# - Export debug logs
```

**Manual Pipeline Testing:**
```python
# In Python REPL or Jupyter notebook
from src.rag_pipeline import RAGPipeline
from src.vector_store import VectorStore

# Initialize pipeline
pipeline = RAGPipeline(top_k=5, max_context_chunks=4)

# Test question
question = "Hvað er súra?"

# Get results
result = pipeline.ask(question)

# Inspect results
print(f"Answer: {result['answer']}")
print(f"Citations: {len(result['citations'])}")
print(f"Tokens: {result['metadata']['token_usage']}")

# Inspect vector search
embedding = pipeline.embedding_generator.generate(question)
search_results = pipeline.vector_store.search(embedding, top_k=10)
for i, result in enumerate(search_results):
    print(f"{i}. Score: {result['score']}, Chapter: {result['metadata']['chapter']}")
```

### Inspecting Database

**Web UI (Recommended):**
```bash
python dev-tools/backend/db_inspector.py

# Opens Flask app on http://localhost:5001
# Features:
# - Browse all chunks
# - Search by keyword
# - Filter by chapter/section
# - View metadata
# - Export to CSV/JSON
# - Statistics dashboard
```

**CLI Inspection:**
```bash
python -m src.inspect_db

# Interactive menu:
# 1. View database statistics
# 2. Search database
# 3. List all documents
# 4. Export database
# 5. Query by metadata
```

**Programmatic Inspection:**
```python
from src.vector_store import VectorStore

# Initialize vector store
vs = VectorStore()

# Get statistics
stats = vs.get_stats()
print(f"Total chunks: {stats['count']}")
print(f"Collections: {stats['collections']}")

# Get all documents
docs = vs.get_all_documents()
for doc in docs[:5]:  # First 5
    print(f"ID: {doc['id']}")
    print(f"Chapter: {doc['metadata']['chapter']}")
    print(f"Text: {doc['document'][:100]}...")
    print()

# Search
results = vs.search("súra", top_k=5)
for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Chapter: {result['metadata']['chapter']}")
    print(f"Text: {result['document'][:100]}...")
    print()
```

### Adding New Content

**Single File Ingestion:**
```bash
# Ingest a single chapter file
python -m src.ingest --file data/chapters/chapter_08_sura_og_basar.md

# With custom parameters
python -m src.ingest \
  --file data/chapters/chapter_08.md \
  --db-path ./data/chroma_db \
  --reset  # WARNING: Clears existing database
```

**Batch Ingestion:**
```bash
# Ingest all files in a directory
python -m src.batch_ingest --data-dir data/chapters/

# Features:
# - Progress bars
# - Error handling per file
# - Statistics reporting
# - Automatic chunking
# - Embedding generation
```

**Validate Content First:**
```bash
# Validate before ingesting
python -m src.chapter_validator data/chapters/new_chapter.md

# Checks:
# - UTF-8 encoding
# - Icelandic characters preserved
# - Required metadata present
# - Word count within limits
# - Markdown formatting
```

### Updating Dependencies

**Backend Dependencies:**
```bash
cd backend

# View outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt

# Test after update
pytest tests/ -v
```

**Frontend Dependencies:**
```bash
cd frontend

# View outdated packages
npm outdated

# Update specific package
npm update package-name

# Update all packages (careful!)
npm update

# Test after update
npm run build
npm run lint
```

**Check for Breaking Changes:**
- Read changelog for major version updates
- Test thoroughly before committing
- Update code if API changes
- Update documentation

### Deployment

**Full Deployment to Linode:**
```bash
# Deploy both backend and frontend
./scripts/deploy.sh

# Backend only
./scripts/deploy_backend.sh

# Frontend only
./scripts/deploy_frontend.sh

# Complete deployment with build
./scripts/complete_deploy.sh
```

**Pre-Deployment Checklist:**
1. ✅ All tests passing: `pytest tests/ -v`
2. ✅ Linting clean: `black src/`, `flake8 src/`
3. ✅ Frontend builds: `npm run build`
4. ✅ Environment variables set: `.env` files configured
5. ✅ Database backed up: `./scripts/backup.sh`
6. ✅ Git committed: `git status` clean

**Post-Deployment Verification:**
```bash
# Check health endpoint
curl https://yourdomain.com/health

# Check API
curl -X POST https://yourdomain.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hvað er efnafræði?"}'

# Check logs
docker-compose -f backend/docker-compose.yml logs -f

# Check nginx
sudo tail -f /var/log/nginx/access.log
```

---

## 🔑 Important Patterns

### RAG Pipeline Flow

**Complete Question-Answer Flow:**

```
1. User Input (Icelandic)
   └─> "Hvað er súra?"

2. Generate Query Embedding
   └─> OpenAI text-embedding-3-small
   └─> [0.123, -0.456, ..., 0.789] (1536 dimensions)
   └─> Cost: ~$0.00000002

3. Vector Search (ChromaDB)
   └─> Similarity search with embedding
   └─> top_k=5 most similar chunks
   └─> Returns: [{chunk, metadata, score}, ...]

4. Filter & Rank
   └─> Select best chunks based on:
       - Similarity score
       - Metadata relevance
       - Diversity (different sections)
   └─> Keep max_context_chunks=4

5. Format Context
   └─> Combine chunks with metadata:
       "Kafli 8, Hluti 8.1: Súrur og basar
        [chunk text]

        Kafli 8, Hluti 8.2: Eiginleikar súrna
        [chunk text]

        ..."

6. LLM Generation (Claude)
   └─> System prompt: "Þú ert efnafræðikennari..."
   └─> User prompt: context + question
   └─> Model: claude-sonnet-4-20250514
   └─> max_tokens=2048, temperature=0.7
   └─> Cost: ~$0.01-0.03 per query

7. Extract Citations
   └─> Parse Claude response for source references
   └─> Map back to original chunks
   └─> Format for frontend display

8. Return Response
   └─> {
         "answer": "Súra er efni sem...",
         "citations": [...],
         "metadata": {
           "token_usage": {...},
           "timing": {...}
         }
       }
```

### State Management (Frontend)

**Context + Reducer Pattern:**

```typescript
// State structure
interface ChatState {
  sessionId: string;        // Unique conversation ID
  messages: Message[];      // Conversation history
  isLoading: boolean;       // Loading indicator
  error: string | null;     // Error message
}

// Actions modify state
type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | ...

// Reducer is pure function
function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };
    // ...
  }
}

// Context provides state + dispatch
const ChatContext = createContext<ChatContextType | undefined>(undefined);

// Provider wraps app
export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Side effects (localStorage, API calls)
  useEffect(() => {
    saveConversation(state.sessionId, state.messages);
  }, [state.messages]);

  // Exposed methods
  const sendMessage = useCallback(async (question: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    const response = await api.sendMessage(question);
    dispatch({ type: 'ADD_MESSAGE', payload: response });
  }, []);

  return (
    <ChatContext.Provider value={{ ...state, sendMessage }}>
      {children}
    </ChatContext.Provider>
  );
}

// Components use hook
function ChatInterface() {
  const { messages, sendMessage, isLoading } = useChat();
  // ...
}
```

### Content Processing Pipeline

**Markdown Chunking Strategy:**

```python
# Goal: Create semantically meaningful chunks
# Constraints:
# - MIN: 200 words (too small = no context)
# - TARGET_MIN: 400 words (ideal minimum)
# - TARGET_MAX: 600 words (ideal maximum)
# - MAX: 1000 words (too large = poor retrieval)

def process_markdown(content: str) -> List[Dict]:
    """
    Process markdown while preserving structure
    """

    # 1. Parse markdown structure
    sections = parse_markdown_sections(content)
    # Recognizes: headers, lists, code blocks, equations

    # 2. Extract metadata
    metadata = extract_metadata(content)
    # Pattern match: "# Kafli 8: Title" → chapter="8", title="Title"

    # 3. Create chunks
    chunks = []
    current_chunk = []
    current_word_count = 0

    for section in sections:
        word_count = count_words(section)

        # If adding section would exceed MAX
        if current_word_count + word_count > MAX_CHUNK_SIZE:
            # Save current chunk if it's >= MIN
            if current_word_count >= MIN_CHUNK_SIZE:
                chunks.append({
                    'text': '\n\n'.join(current_chunk),
                    'metadata': metadata,
                    'word_count': current_word_count
                })

            # Start new chunk
            current_chunk = [section]
            current_word_count = word_count

        else:
            # Add to current chunk
            current_chunk.append(section)
            current_word_count += word_count

        # If current chunk is in TARGET range, save it
        if TARGET_MIN <= current_word_count <= TARGET_MAX:
            chunks.append({
                'text': '\n\n'.join(current_chunk),
                'metadata': metadata,
                'word_count': current_word_count
            })
            current_chunk = []
            current_word_count = 0

    # 4. Validate UTF-8 encoding
    for chunk in chunks:
        validate_icelandic_encoding(chunk['text'])

    return chunks
```

### Error Recovery

**Backend Error Recovery:**
```python
# LLM client with retry logic
class ClaudeClient:
    MAX_RETRIES = 3
    BASE_DELAY = 1  # seconds

    def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate response with exponential backoff retry"""

        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.client.messages.create(...)
                return self._parse_response(response)

            except anthropic.RateLimitError as e:
                # Rate limit - wait and retry
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.BASE_DELAY * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {delay}s")
                    time.sleep(delay)
                    continue
                raise

            except anthropic.APIError as e:
                # Server error - retry
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.BASE_DELAY * (2 ** attempt)
                    logger.error(f"API error, retrying in {delay}s: {e}")
                    time.sleep(delay)
                    continue
                raise

            except Exception as e:
                # Unexpected error - don't retry
                logger.error(f"Unexpected error: {e}")
                raise

        raise RuntimeError("Max retries exceeded")
```

**Frontend Error Recovery:**
```typescript
// API client with retry and timeout
async function sendMessage(
  question: string,
  sessionId: string
): Promise<ChatResponse> {

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      // Fetch with timeout
      const response = await fetchWithTimeout(
        `${API_ENDPOINT}/ask`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, sessionId })
        },
        TIMEOUT_MS
      );

      if (!response.ok) {
        throw new ApiError(
          `HTTP ${response.status}`,
          response.status
        );
      }

      return await response.json();

    } catch (error) {
      // Don't retry client errors
      if (error instanceof ApiError &&
          error.status >= 400 && error.status < 500) {
        throw error;
      }

      // Retry server errors
      if (attempt < MAX_RETRIES - 1) {
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }

      // Max retries exceeded
      throw new ApiError(
        'Ekki tókst að tengjast þjónustunni',
        undefined,
        error
      );
    }
  }
}

// Helper for timeout
async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeout: number
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}
```

### Cost Tracking

**Token Usage Monitoring:**
```python
# Track tokens throughout pipeline
class RAGPipeline:
    def ask(self, question: str) -> Dict[str, Any]:
        """Process question and track costs"""

        start_time = time.time()
        total_cost = 0.0

        # 1. Embedding generation
        embedding_start = time.time()
        embedding = self.embedding_generator.generate(question)
        embedding_time = time.time() - embedding_start

        # Calculate embedding cost
        # text-embedding-3-small: $0.00002 per 1K tokens
        # Rough estimate: ~1 token per 4 characters
        embedding_tokens = len(question) // 4
        embedding_cost = (embedding_tokens / 1000) * 0.00002
        total_cost += embedding_cost

        # 2. Vector search (no cost)
        search_results = self.vector_store.search(embedding)

        # 3. LLM generation
        llm_start = time.time()
        response = self.llm_client.generate(question, context)
        llm_time = time.time() - llm_start

        # Calculate LLM cost
        # Claude Sonnet 4: ~$3 per 1M input, ~$15 per 1M output
        input_tokens = response['token_usage']['input']
        output_tokens = response['token_usage']['output']
        llm_cost = (input_tokens / 1_000_000 * 3.0) + \
                   (output_tokens / 1_000_000 * 15.0)
        total_cost += llm_cost

        total_time = time.time() - start_time

        return {
            'answer': response['answer'],
            'citations': response['citations'],
            'metadata': {
                'timing': {
                    'total': total_time,
                    'embedding': embedding_time,
                    'llm': llm_time
                },
                'token_usage': {
                    'embedding': embedding_tokens,
                    'input': input_tokens,
                    'output': output_tokens,
                    'total': embedding_tokens + input_tokens + output_tokens
                },
                'cost': {
                    'embedding': embedding_cost,
                    'llm': llm_cost,
                    'total': total_cost
                }
            }
        }
```

---

## 🐛 Troubleshooting

### Common Issues

**Backend Issues:**

**1. "ModuleNotFoundError: No module named 'src'"**
```bash
# Solution: Run from backend directory or use python -m
cd /home/user/icelandic-chemistry-ai-tutor/backend
python -m src.main

# Or set PYTHONPATH
export PYTHONPATH=/home/user/icelandic-chemistry-ai-tutor/backend:$PYTHONPATH
```

**2. "CORS error" in frontend**
```bash
# Check ALLOWED_ORIGINS in backend/.env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,https://yourdomain.com

# Verify CORS middleware in main.py
# Check browser console for actual error message
```

**3. "ChromaDB: No such collection"**
```bash
# Solution: Ingest content first
cd backend
python -m src.batch_ingest --data-dir data/chapters/

# Or check if database exists
ls -la data/chroma_db/
```

**4. "Anthropic API key not found"**
```bash
# Solution: Set environment variable
export ANTHROPIC_API_KEY=sk-ant-...

# Or add to backend/.env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> backend/.env

# Verify it's loaded
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY'))"
```

**5. "Rate limit exceeded" from OpenAI**
```python
# Solution: Add delays in batch_ingest.py
# Already implemented in embeddings.py:

def batch_embed(texts: List[str], batch_size: int = 100):
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        embeddings = embed(batch)
        time.sleep(1)  # Rate limiting delay
        yield embeddings
```

**Frontend Issues:**

**1. "VITE_API_ENDPOINT is not defined"**
```bash
# Solution: Create frontend/.env
echo "VITE_API_ENDPOINT=http://localhost:8000" > frontend/.env

# Restart dev server
npm run dev
```

**2. "Failed to fetch" when sending messages**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check proxy in vite.config.ts
# Check browser network tab for actual error

# Try direct API call
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Test"}'
```

**3. "localStorage quota exceeded"**
```typescript
// Solution: Clear old conversations
// In browser console:
localStorage.clear()

// Or add storage limit in storage.ts:
const MAX_CONVERSATIONS = 50;

export function saveConversation(sessionId: string, messages: Message[]) {
  const conversations = listConversations();
  if (conversations.length >= MAX_CONVERSATIONS) {
    // Delete oldest
    const oldest = conversations[0];
    deleteConversation(oldest.sessionId);
  }
  // ... save
}
```

**Testing Issues:**

**1. "No tests found"**
```bash
# Solution: Check you're in backend directory
cd /home/user/icelandic-chemistry-ai-tutor/backend

# Check pytest can find tests
pytest --collect-only

# Verify pytest.ini testpaths
cat pytest.ini
```

**2. "Fixture not found"**
```python
# Solution: Ensure conftest.py is present
ls tests/conftest.py

# Check fixture scope and names
pytest --fixtures

# Import fixture explicitly if needed
from conftest import fixture_name
```

**3. "Tests pass locally but fail in CI"**
```bash
# Common causes:
# - Environment variables not set
# - Different Python version
# - Missing dependencies
# - Timezone differences
# - File path differences (Windows vs Linux)

# Solution: Check CI logs carefully
# Match CI environment locally with Docker
```

**Database Issues:**

**1. "Database is empty after ingestion"**
```bash
# Check ingestion logs
python -m src.batch_ingest --data-dir data/chapters/ 2>&1 | tee ingest.log

# Verify files were processed
grep "Processing" ingest.log

# Check database
python -m src.inspect_db

# Try single file first
python -m src.ingest --file data/chapters/chapter_01.md
```

**2. "Search returns no results"**
```python
# Debug search
from src.vector_store import VectorStore

vs = VectorStore()
stats = vs.get_stats()
print(f"Total docs: {stats['count']}")

# Try broader search
results = vs.search("efni", top_k=10)
print(f"Found {len(results)} results")

# Check embeddings are working
from src.embeddings import get_embedding_function
embed_fn = get_embedding_function()
embedding = embed_fn(["test"])
print(f"Embedding length: {len(embedding[0])}")
```

**Deployment Issues:**

**1. "Docker build fails"**
```bash
# Check Dockerfile syntax
docker build -t chemistry-backend ./backend

# Check .dockerignore
cat backend/.dockerignore

# Build with no cache
docker build --no-cache -t chemistry-backend ./backend
```

**2. "Container exits immediately"**
```bash
# Check container logs
docker logs <container-id>

# Run interactively
docker run -it chemistry-backend /bin/bash

# Check environment variables
docker run chemistry-backend env
```

**3. "SSL certificate issues"**
```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Check certificate expiry
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal
```

### Debug Checklist

When encountering an issue, check in order:

**Backend:**
1. ✅ Virtual environment activated: `which python`
2. ✅ Dependencies installed: `pip list | grep fastapi`
3. ✅ Environment variables set: `echo $ANTHROPIC_API_KEY`
4. ✅ Database exists: `ls data/chroma_db/`
5. ✅ Server running: `curl http://localhost:8000/health`
6. ✅ Logs show no errors: Check terminal output

**Frontend:**
1. ✅ Node modules installed: `ls node_modules/`
2. ✅ Environment variables set: `cat .env`
3. ✅ Build works: `npm run build`
4. ✅ Dev server running: `curl http://localhost:5173`
5. ✅ Browser console clean: No errors in DevTools
6. ✅ Network requests working: Check Network tab

**Full Stack:**
1. ✅ Backend health check: `curl http://localhost:8000/health`
2. ✅ CORS configured: Check `ALLOWED_ORIGINS`
3. ✅ API call works: Send test question via curl
4. ✅ Frontend connects: Check browser Network tab
5. ✅ Database has content: `python -m src.inspect_db`

### Getting Help

**Check Documentation:**
1. `docs/DEVELOPMENT.md` - Development setup issues
2. `docs/API_REFERENCE.md` - API endpoint issues
3. `docs/ARCHITECTURE.md` - System design questions
4. `README.md` - Quick start issues

**Debug Tools:**
- Backend: `dev-tools/backend/rag_debugger.py`
- Database: `dev-tools/backend/db_inspector.py`
- Performance: `dev-tools/backend/performance_profiler.py`
- Tokens: `dev-tools/backend/token_tracker.py`

**Logs:**
- Backend: Terminal output from `uvicorn`
- Frontend: Browser DevTools Console
- Docker: `docker-compose logs -f`
- Nginx: `/var/log/nginx/error.log`

---

## 🎯 Best Practices Summary

### DO:
- ✅ Write all user-facing text in Icelandic
- ✅ Validate UTF-8 encoding for Icelandic characters
- ✅ Use descriptive variable names in English
- ✅ Add docstrings to all functions
- ✅ Write tests for new features
- ✅ Use type hints (Python) and interfaces (TypeScript)
- ✅ Log important operations
- ✅ Handle errors gracefully with user-friendly messages
- ✅ Track token usage and costs
- ✅ Use fixtures from conftest.py for tests
- ✅ Run linters before committing (black, flake8, eslint)
- ✅ Commit frequently with clear messages
- ✅ Use provided dev tools for debugging

### DON'T:
- ❌ Translate code/variable names to Icelandic
- ❌ Write English text in UI components
- ❌ Commit API keys or secrets
- ❌ Push to main branch directly
- ❌ Skip tests when adding features
- ❌ Ignore type errors (mypy, tsc)
- ❌ Use console.log in production (use proper logging)
- ❌ Hardcode configuration (use environment variables)
- ❌ Deploy without testing locally first
- ❌ Modify production database without backup

### Code Quality:
- **Python:** black, flake8, mypy, isort
- **TypeScript:** eslint, prettier (via eslint config)
- **Tests:** pytest with coverage >80%
- **Documentation:** Google-style docstrings, JSDoc comments

---

## 📚 Additional Resources

### External Documentation:
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [React Docs](https://react.dev/)
- [TypeScript Docs](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)

### Project-Specific:
- Funding: [RANNÍS Website](https://www.rannis.is/)
- Content: OpenStax Chemistry 2e (translated to Icelandic)
- Schools: [Kvennaskólinn](https://kvenno.is/), [FÁ](https://fa.is/)

---

**Last Updated:** 2025-11-18
**Maintained By:** AI Assistants working on this project
**Questions?** Check docs/ directory or project README.md
