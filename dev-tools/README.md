# Developer Tools for RAG System

Comprehensive suite of debugging and inspection tools for the Icelandic Chemistry AI Tutor RAG system.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Backend Tools](#backend-tools)
  - [RAG Debugger](#1-rag-debugger)
  - [Database Inspector](#2-database-inspector)
  - [Search Visualizer](#3-search-visualizer)
  - [Token Tracker](#4-token-tracker)
  - [Performance Profiler](#5-performance-profiler)
- [Frontend Tools](#frontend-tools)
  - [API Logger](#api-logger)
  - [Developer Panel](#developer-panel)
- [Scripts](#scripts)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## 🎯 Overview

This developer tools suite provides comprehensive debugging capabilities for the RAG pipeline:

- **Step-by-step pipeline debugging** with detailed timing and cost information
- **Database inspection** with web UI for browsing and searching chunks
- **Vector search visualization** to understand similarity scores
- **Token usage tracking** with cost projections and budget alerts
- **Performance profiling** to identify bottlenecks
- **Frontend API logging** with request/response inspection

---

## 🚀 Quick Start

### Start Development Server with Tools

```bash
# Start backend with dev tools
./dev-tools/scripts/dev_server.sh

# Start backend + database inspector
./dev-tools/scripts/dev_server.sh --with-inspector
```

### Run Individual Tools

```bash
# RAG Debugger (interactive)
python dev-tools/backend/rag_debugger.py

# Database Inspector (web UI on port 5001)
python dev-tools/backend/db_inspector.py

# Search Visualizer
python dev-tools/backend/search_visualizer.py "Hvað er atóm?"

# Token Tracker
python dev-tools/backend/token_tracker.py --summary

# Performance Profiler
python dev-tools/backend/performance_profiler.py
```

---

## 🔧 Backend Tools

### 1. RAG Debugger

**Purpose:** Interactive CLI tool for step-by-step debugging of the RAG pipeline.

**File:** `backend/rag_debugger.py`

**Usage:**

```bash
# Interactive mode
python dev-tools/backend/rag_debugger.py
```

**Features:**

- Step-by-step execution of RAG pipeline
- View embedding generation with dimensions
- Inspect vector search results and similarity scores
- Display context sent to Claude with token counts
- Show LLM response with citations
- Calculate API costs in real-time
- Export debug logs as JSON

**Example Session:**

```
RAG Pipeline Debugger
=====================

[1] Query received: "Hvað er atóm?"
    Length: 14 chars, 3 words

[2] Embedding generated
    Dimensions: 1536
    Estimated tokens: 4
    Cost: $0.000080
    Time: 234ms

[3] Vector search retrieved 5 chunks:
    - Chunk 1 (score: 0.89)
      Chapter 1, Section 1.1: "Atómbygging"
      Preview: Atóm er minnsta eining efnis...

[4] Context prepared for Claude
    Chunks used: 4 of 5 retrieved
    Estimated tokens: 2,341

[5] Claude response received
    Answer length: 523 chars
    Tokens used:
      - Input: 2,341
      - Output: 523
      - Total: 2,864
    Time: 1,850ms

[6] Citations generated: 2 sources

Summary:
  Total time: 2.8s
  API costs:
    - Embedding: $0.000080
    - Claude input: $0.007023
    - Claude output: $0.007845
    - Total: $0.014948

[Options]
v - View full chunk texts
c - Change question / New query
x - View full context sent to Claude
s - Search with different parameters
e - Export debug log (JSON)
r - Re-run last question
q - Quit
```

**When to Use:**

- Debugging unexpected or incorrect answers
- Understanding which chunks are retrieved for a query
- Optimizing context size and chunk selection
- Tracking down embedding or search issues
- Calculating API costs for specific queries

---

### 2. Database Inspector

**Purpose:** Web-based GUI for browsing and inspecting the ChromaDB vector database.

**File:** `backend/db_inspector.py`

**Usage:**

```bash
python dev-tools/backend/db_inspector.py
# Access at: http://localhost:5001/
```

**Features:**

- **Statistics Dashboard:** Total chunks, chapters, sections, word count
- **Search:** Full-text semantic search across all chunks
- **Filtering:** Filter by chapter and section metadata
- **Browse:** View all chunks in a sortable table
- **Details:** Inspect full chunk content with metadata
- **Export:** Download database as CSV or JSON
- **Delete:** Remove individual chunks (with confirmation)

**UI Components:**

```
┌─────────────────────────────────────────────┐
│  Database Inspector                          │
├─────────────────────────────────────────────┤
│  Stats: 1,234 chunks | 15 chapters | 45 sections
├─────────────────────────────────────────────┤
│  Search: [_______________] [Search]          │
│  Chapter: [All ▼] Section: [All ▼]          │
├─────────────────────────────────────────────┤
│  Results Table                               │
│  ID | Chapter | Section | Title | Preview   │
│  ────────────────────────────────────────── │
│  ch_1 | 1 | 1.1 | Atóm | Atóm er... [View]  │
└─────────────────────────────────────────────┘
```

**When to Use:**

- Inspecting database contents after ingestion
- Verifying chunk quality and metadata
- Finding specific chunks by content or metadata
- Debugging ingestion issues
- Exporting database for backup or analysis

---

### 3. Search Visualizer

**Purpose:** Terminal-based visualization of vector search results with similarity scores.

**File:** `backend/search_visualizer.py`

**Usage:**

```bash
# Direct query
python dev-tools/backend/search_visualizer.py "Hvað er atóm?"

# Interactive mode
python dev-tools/backend/search_visualizer.py
```

**Features:**

- Visual bar charts for similarity scores
- Metadata distribution by chapter/section
- Score distribution analysis
- Compare multiple queries
- Adjust search parameters (n_results, threshold)

**Example Output:**

```
Search Results Visualization
====================================================================

Query: "Hvað er atóm?"

Query embedding: 1536 dimensions
First 5 dimensions: [0.123, -0.456, 0.789, 0.234, -0.123, ...]

Results (by similarity):
--------------------------------------------------------------------

1. █████████████████████████ (0.89)
   Chapter 1, Section 1.1: Atómbygging
   ID: chunk_0
   Preview: Atóm er minnsta eining efnis sem heldur efnafræðilegum...

2. ██████████████████████ (0.82)
   Chapter 1, Section 1.2: Atómkjarni
   ID: chunk_1
   Preview: Atómkjarninn er í miðju atómsins og inniheldur...

====================================================================
Metadata Distribution
====================================================================

Chapter distribution:
  Chapter 1: ███████████████ 4 chunk(s)
  Chapter 2: ████ 1 chunk(s)

Score distribution:
  0.9-1.0 (Excellent): ██████ 1
  0.8-0.9 (Very Good): ████████████ 2
  0.7-0.8 (Good): ████████ 2

====================================================================
Summary Statistics
====================================================================
Total results: 5
Average similarity: 0.798
Max similarity: 0.890
Min similarity: 0.680
Average words per chunk: 425
```

**When to Use:**

- Understanding search quality and relevance
- Tuning similarity thresholds
- Analyzing query patterns
- Comparing search strategies
- Debugging low-quality search results

---

### 4. Token Tracker

**Purpose:** Track and analyze API token usage and costs.

**File:** `backend/token_tracker.py`

**Usage:**

```bash
# Show today's usage
python dev-tools/backend/token_tracker.py --summary

# Show weekly usage
python dev-tools/backend/token_tracker.py --summary --period week

# Daily breakdown
python dev-tools/backend/token_tracker.py --daily --days 7

# Check budget
python dev-tools/backend/token_tracker.py --budget

# Export usage data
python dev-tools/backend/token_tracker.py --export usage.csv
```

**As a Module:**

```python
from dev_tools.backend.token_tracker import TokenTracker

tracker = TokenTracker()

# Log embedding call
tracker.log_embedding(text="Hvað er atóm?", tokens=4, cost=0.00008)

# Log LLM call
tracker.log_llm_call(
    prompt_tokens=2341,
    response_tokens=523,
    cost=0.014
)

# Get summary
tracker.summary(period="today")

# Check budget
tracker.check_budget(daily_budget=5.0, monthly_budget=100.0)
```

**Example Output:**

```
======================================================================
Token Usage Summary (Today)
======================================================================

Embeddings (OpenAI):
  Calls: 145
  Tokens: 18,234
  Cost: $0.3647
  Avg tokens/call: 126

LLM (Claude Sonnet 4):
  Calls: 67
  Prompt tokens: 156,789
  Response tokens: 34,567
  Total tokens: 191,356
  Cost: $0.9884
  Avg prompt tokens/call: 2,341
  Avg response tokens/call: 516

----------------------------------------------------------------------
Total cost (today): $1.3531

Projections:
  Estimated monthly: $40.59
  Estimated yearly: $493.88
```

**Budget Alerts:**

```
======================================================================
Budget Status
======================================================================

Daily Budget: $1.3531 / $5.00 (27.1%)
  ✓ Within daily budget

Monthly Budget: $38.42 / $100.00 (38.4%)
  ✓ Within monthly budget
```

**When to Use:**

- Monitoring API costs
- Setting and tracking budgets
- Identifying cost spikes
- Planning infrastructure costs
- Optimizing API usage

---

### 5. Performance Profiler

**Purpose:** Profile RAG pipeline performance to identify bottlenecks.

**File:** `backend/performance_profiler.py`

**Usage:**

```bash
# Profile 10 test queries
python dev-tools/backend/performance_profiler.py

# Profile 20 queries
python dev-tools/backend/performance_profiler.py --queries 20

# Profile from file
python dev-tools/backend/performance_profiler.py --file test_queries.txt

# Detailed breakdown
python dev-tools/backend/performance_profiler.py --detailed

# Export results
python dev-tools/backend/performance_profiler.py --export profile_results.json

# Compare profiles
python dev-tools/backend/performance_profiler.py --compare profile1.json profile2.json
```

**Example Output:**

```
======================================================================
Performance Analysis
======================================================================

Average response time: 2.31s
  (based on 10 queries)

Time breakdown:
  - Embedding generation: 0.28s (12%)
  - Vector search:        0.19s (8%)
  - Context preparation:  0.12s (5%)
  - LLM call:             1.65s (71%)
  - Citation generation:  0.07s (3%)

Visual breakdown:
  Embedding     ██████ 0.28s
  Search        ████ 0.19s
  Context       ██ 0.12s
  LLM           █████████████████████████████████████ 1.65s
  Citations     █ 0.07s

----------------------------------------------------------------------
Bottleneck: LLM (1.65s)

======================================================================
Recommendations
======================================================================

💡 LLM calls are the main bottleneck:
   - Consider caching common queries
   - Reduce context size (fewer chunks)
   - Use shorter max_tokens setting
   - Implement streaming responses for better UX

======================================================================
Statistics
======================================================================

Total queries profiled: 10
Fastest query: 1.98s
Slowest query: 2.67s
Standard deviation: 0.23s

Average tokens per query: 2,864
Total tokens used: 28,640
Average chunks retrieved: 5.0
```

**When to Use:**

- Identifying performance bottlenecks
- Optimizing slow operations
- Comparing before/after optimizations
- Planning scaling strategies
- Understanding response time distribution

---

## 🎨 Frontend Tools

### API Logger

**Purpose:** React component for logging and inspecting API calls in development.

**File:** `frontend/api_logger.tsx`

**Integration:**

```typescript
// In your App.tsx or layout
import { APILoggerProvider, useAPILogger } from './dev-tools/frontend/api_logger';
import { DevPanel } from './dev-tools/frontend/dev_panel';

function App() {
  return (
    <APILoggerProvider>
      <YourApp />
      <DevPanel />
    </APILoggerProvider>
  );
}

// In your API calls
function useChatAPI() {
  const { log } = useAPILogger();

  const askQuestion = async (question: string) => {
    return log(
      () => fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      }),
      {
        endpoint: '/api/ask',
        method: 'POST',
        requestBody: { question }
      }
    );
  };

  return { askQuestion };
}
```

**Features:**

- Automatic request/response logging
- Color-coded status codes
- Timing information
- Expandable request/response bodies
- Filter by endpoint
- Export logs as JSON
- Clear logs

---

### Developer Panel

**Purpose:** Comprehensive developer information panel (only visible in development).

**File:** `frontend/dev_panel.tsx`

**Features:**

- **API Calls Tab:** View all logged API requests/responses
- **Metrics Tab:** Performance metrics (avg response time, success rate, errors)
- **Cache Tab:** Inspect response cache (if implemented)
- **Environment Tab:** Environment variables, browser info, useful links

**Usage:**

```typescript
import { DevPanel } from './dev-tools/frontend/dev_panel';

function App() {
  return (
    <>
      <YourApp />
      <DevPanel /> {/* Only shows in NODE_ENV=development */}
    </>
  );
}
```

**UI:**

```
┌──────────────────────────────────────┐
│ 🔧 Developer Panel              [✕]  │
├──────────────────────────────────────┤
│ API Calls | Metrics | Cache | Env   │
├──────────────────────────────────────┤
│                                      │
│  Performance Metrics                 │
│  ┌────────┬────────┬────────┐      │
│  │  15    │ 2.3s   │  100%  │      │
│  │ Calls  │ Avg    │Success │      │
│  └────────┴────────┴────────┘      │
│                                      │
│  [Export CSV] [Export JSON]         │
│                                      │
└──────────────────────────────────────┘
```

---

## 📜 Scripts

### dev_server.sh

**Purpose:** Start the backend with debugging enabled and optionally launch dev tools.

**File:** `scripts/dev_server.sh`

**Usage:**

```bash
# Start backend only
./dev-tools/scripts/dev_server.sh

# Start backend + database inspector
./dev-tools/scripts/dev_server.sh --with-inspector

# Custom port
./dev-tools/scripts/dev_server.sh --port 8080

# Help
./dev-tools/scripts/dev_server.sh --help
```

**Features:**

- Automatic environment setup
- Checks port availability
- Starts backend with debug logging
- Optionally starts database inspector
- Shows all available dev tools
- Graceful shutdown with Ctrl+C

---

## 🔍 Troubleshooting

### Common Issues

#### 1. "Module not found" errors

```bash
# Make sure you're in the project root
cd /path/to/icelandic-chemistry-ai-tutor

# Activate virtual environment
source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

#### 2. Database not found

```bash
# Check database path
ls backend/data/chroma_db/

# If empty, run ingestion
cd backend
python -m src.ingest --data-dir ./data/sample
```

#### 3. API key errors

```bash
# Set environment variables
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Or create .env file in backend/
echo "OPENAI_API_KEY=sk-..." >> backend/.env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> backend/.env
```

#### 4. Port already in use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
./dev-tools/scripts/dev_server.sh --port 8080
```

#### 5. Flask/DB Inspector not starting

```bash
# Install Flask if missing
pip install flask

# Run with verbose output
python dev-tools/backend/db_inspector.py
```

---

## 💡 Best Practices

### Development Workflow

1. **Start with the RAG Debugger** when investigating specific queries
2. **Use Database Inspector** to verify data quality after ingestion
3. **Profile regularly** to catch performance regressions
4. **Track tokens** to avoid surprise API bills
5. **Monitor metrics** in the dev panel during frontend development

### When to Use Each Tool

| Tool | Best For |
|------|----------|
| **RAG Debugger** | Debugging incorrect answers, understanding retrieval |
| **Database Inspector** | Verifying ingestion, browsing chunks |
| **Search Visualizer** | Tuning search parameters, understanding relevance |
| **Token Tracker** | Cost monitoring, budget planning |
| **Performance Profiler** | Identifying bottlenecks, optimization |
| **API Logger** | Frontend debugging, request/response inspection |
| **Dev Panel** | General development, quick metrics |

### Performance Tips

From profiling experience:

- **Embedding generation:** Usually 200-400ms, cache common queries
- **Vector search:** Should be <300ms, consider reducing n_results if slow
- **LLM calls:** 1-3s is normal, implement streaming for better UX
- **Context preparation:** Should be <100ms, optimize if slower
- **Total response:** Aim for <3s for good user experience

### Cost Optimization

From token tracking:

- **Embeddings:** ~$0.0001 per query (negligible)
- **LLM calls:** ~$0.01-0.03 per query (main cost)
- **Monthly estimate:** $40-100 for moderate usage
- **Optimization:** Cache frequent queries, reduce context size

### Debug Checklist

When investigating issues:

- [ ] Check RAG Debugger for retrieved chunks
- [ ] Verify chunks exist in Database Inspector
- [ ] Check similarity scores in Search Visualizer
- [ ] Review token usage in Token Tracker
- [ ] Profile performance if slow
- [ ] Check API logs in Dev Panel
- [ ] Verify environment variables

---

## 📚 Additional Resources

- **Backend Code:** `backend/src/`
- **API Docs:** `http://localhost:8000/docs` (when running)
- **Project Architecture:** `docs/ARCHITECTURE.md`
- **API Reference:** `docs/API_REFERENCE.md`

---

## 🤝 Contributing

When adding new dev tools:

1. Place Python tools in `dev-tools/backend/`
2. Place TypeScript/React tools in `dev-tools/frontend/`
3. Add CLI entry point if applicable
4. Update this README with usage instructions
5. Include example output
6. Add to the dev_server.sh menu if appropriate

---

## 📝 License

Part of the Icelandic Chemistry AI Tutor project.

---

**Questions or Issues?**

Open an issue on GitHub or contact the development team.
