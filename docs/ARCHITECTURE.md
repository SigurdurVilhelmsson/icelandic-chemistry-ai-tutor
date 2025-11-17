# Architecture Documentation

## System Architecture Overview

The Icelandic Chemistry AI Tutor is a single-server RAG (Retrieval-Augmented Generation) application deployed on Linode. This document provides a comprehensive technical overview of the system architecture, components, and data flow.

---

## Table of Contents

- [High-Level Architecture](#high-level-architecture)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Security Architecture](#security-architecture)
- [Deployment Architecture](#deployment-architecture)
- [Database Schema](#database-schema)
- [API Design](#api-design)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Internet / Users                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS (443)
                            │ HTTP (80) → redirect to HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Linode Server (Ubuntu 24.04)                   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                     Nginx Web Server                        │  │
│  │  - TLS Termination (Let's Encrypt)                         │  │
│  │  - Static file serving (React build)                       │  │
│  │  - Reverse proxy for API                                   │  │
│  │  - Rate limiting                                            │  │
│  │  - CORS headers                                             │  │
│  └────┬───────────────────────────────┬─────────────────────────┘
│       │                               │                          │
│       │ Static Files                  │ /api/* requests         │
│       ▼                               ▼                          │
│  ┌─────────────────┐         ┌─────────────────────────────┐    │
│  │  React Frontend │         │   FastAPI Backend           │    │
│  │  (Port 80/443)  │         │   (Port 8000)               │    │
│  │                 │         │                             │    │
│  │  - TypeScript   │         │  ┌────────────────────────┐ │    │
│  │  - Vite build   │         │  │   RAG Pipeline         │ │    │
│  │  - Tailwind CSS │         │  │  - LangChain           │ │    │
│  └─────────────────┘         │  │  - Prompt engineering  │ │    │
│                              │  │  - Context retrieval   │ │    │
│                              │  └───────┬────────────────┘ │    │
│                              │          │                  │    │
│                              │  ┌───────▼────────────────┐ │    │
│                              │  │  Vector Store          │ │    │
│                              │  │  (Chroma DB)           │ │    │
│                              │  │  - Embeddings storage  │ │    │
│                              │  │  - Semantic search     │ │    │
│                              │  └────────────────────────┘ │    │
│                              │                             │    │
│                              │  External API Calls:        │    │
│                              │  ┌────────────────────────┐ │    │
│                              │  │ Anthropic Claude API   │ │    │
│                              │  │ (claude-sonnet-4)      │ │    │
│                              │  └────────────────────────┘ │    │
│                              │  ┌────────────────────────┐ │    │
│                              │  │ OpenAI Embeddings API  │ │    │
│                              │  │ (text-embedding-3)     │ │    │
│                              │  └────────────────────────┘ │    │
│                              └─────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Persistent Storage                       │ │
│  │  - /data/chroma_db/      (Vector database)                 │ │
│  │  - /data/chapters/       (Chemistry content)               │ │
│  │  - /logs/                (Application logs)                │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Frontend (React + TypeScript)

**Purpose:** User interface for students and teachers to interact with the AI tutor.

**Technology:**
- React 18 with TypeScript
- Vite for development and building
- Tailwind CSS for styling
- React Router for navigation

**Key Features:**
- Chat interface for asking chemistry questions
- Conversation history management
- Citation display for sources
- Responsive design for mobile/desktop
- Icelandic language support

**File Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── CitationCard.tsx
│   │   └── ...
│   ├── utils/
│   │   ├── api.ts              # API client
│   │   ├── storage.ts          # LocalStorage management
│   │   └── formatting.ts
│   ├── App.tsx
│   └── main.tsx
├── public/
└── index.html
```

**Build Process:**
```bash
npm run build
# Creates optimized production build in dist/
```

**Deployment:**
- Built static files served by Nginx
- Located at: `/var/www/chemistry-ai/frontend/`

---

### 2. Backend (FastAPI + Python)

**Purpose:** API server handling RAG pipeline, vector search, and LLM interactions.

**Technology:**
- Python 3.11
- FastAPI for REST API
- LangChain for RAG orchestration
- Pydantic for data validation
- Uvicorn as ASGI server

**Key Components:**

#### 2.1 API Layer (`main.py`)
- REST endpoints for chat, health checks
- CORS middleware configuration
- Request/response validation
- Error handling

#### 2.2 RAG Pipeline (`rag_pipeline.py`)
- Question processing and embedding
- Context retrieval from vector store
- Prompt construction
- LLM API calls (Claude Sonnet 4)
- Response formatting with citations

#### 2.3 Vector Store (`vector_store.py`)
- Chroma DB integration
- Document embedding and indexing
- Semantic similarity search
- Metadata filtering

**File Structure:**
```
backend/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── rag_pipeline.py         # RAG implementation
│   ├── vector_store.py         # Vector DB operations
│   ├── models.py               # Pydantic models
│   ├── config.py               # Configuration
│   └── utils.py                # Utility functions
├── data/
│   ├── chroma_db/              # Vector database
│   ├── chapters/               # Chemistry content
│   └── sample/                 # Sample data
├── tests/
├── requirements.txt
└── Dockerfile
```

**API Endpoints:**
```
POST   /ask                     # Ask chemistry question
GET    /health                  # Health check
GET    /metrics                 # System metrics
POST   /feedback                # User feedback
```

---

### 3. Vector Database (Chroma DB)

**Purpose:** Store and retrieve document embeddings for semantic search.

**Technology:**
- Chroma DB (open-source vector database)
- OpenAI text-embedding-3-small for embeddings
- Persistent storage on disk

**Data Model:**
```python
Document = {
    "id": str,                   # Unique identifier
    "content": str,              # Chemistry content text
    "embedding": List[float],    # 1536-dim vector (OpenAI)
    "metadata": {
        "chapter": str,          # Chapter number/name
        "section": str,          # Section identifier
        "page": int,             # Page number
        "title": str,            # Content title
        "language": "is"         # Icelandic
    }
}
```

**Indexing Process:**
1. Split chemistry chapters into semantic chunks
2. Generate embeddings using OpenAI API
3. Store in Chroma with metadata
4. Build vector index for fast retrieval

**Query Process:**
1. User question → embedding
2. Similarity search in vector space
3. Return top-k most relevant chunks
4. Include metadata for citations

---

### 4. Nginx Web Server

**Purpose:** Reverse proxy, static file server, TLS termination.

**Configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend (static files)
    location / {
        root /var/www/chemistry-ai/frontend;
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
}
```

**Features:**
- HTTP → HTTPS redirect
- TLS 1.3 encryption
- Static file caching
- Gzip compression
- Rate limiting (10 req/s per IP)
- Security headers

---

## Data Flow

### Question Answering Flow

```
1. User Input
   │
   ▼
2. Frontend: User types question in Icelandic
   │
   ▼
3. API Request: POST /ask
   {
     "question": "Hvað er sýra?",
     "conversation_id": "uuid"
   }
   │
   ▼
4. Backend: RAG Pipeline
   │
   ├─► a) Embed question using OpenAI API
   │       Input: "Hvað er sýra?"
   │       Output: [0.123, -0.456, ...] (1536-dim vector)
   │
   ├─► b) Query Chroma DB for similar content
   │       Input: Question embedding
   │       Output: Top 5 relevant chunks with metadata
   │
   ├─► c) Construct prompt for Claude
   │       System: "Þú ert efnafræðikennari..."
   │       Context: Retrieved chunks
   │       Question: "Hvað er sýra?"
   │
   ├─► d) Call Claude Sonnet 4 API
   │       Model: claude-sonnet-4-20250514
   │       Max tokens: 1024
   │       Temperature: 0.3
   │
   └─► e) Format response with citations
           Output: {
             "answer": "Sýra er efni sem...",
             "citations": [
               {"chapter": 2, "section": "2.1", "page": 45}
             ]
           }
   │
   ▼
5. API Response: Return JSON to frontend
   │
   ▼
6. Frontend: Display answer with citations
   │
   ▼
7. User: Reads answer, can ask follow-up
```

---

## Technology Stack

### Backend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.11 | Core programming language |
| Web Framework | FastAPI | 0.104+ | REST API server |
| ASGI Server | Uvicorn | 0.24+ | Production server |
| LLM Orchestration | LangChain | 0.1+ | RAG pipeline |
| Vector Database | Chroma | 0.4+ | Embedding storage |
| LLM API | Claude Sonnet 4 | Latest | Question answering |
| Embeddings API | OpenAI | Latest | Text embeddings |
| Validation | Pydantic | 2.0+ | Data models |

### Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | React | 18+ | UI library |
| Language | TypeScript | 5.0+ | Type safety |
| Build Tool | Vite | 5.0+ | Dev server & bundler |
| Styling | Tailwind CSS | 3.0+ | CSS framework |
| HTTP Client | Fetch API | Native | API requests |
| Storage | LocalStorage | Native | Conversation history |

### Infrastructure Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Hosting | Linode | Server infrastructure |
| OS | Ubuntu 24.04 LTS | Operating system |
| Web Server | Nginx | Reverse proxy & static files |
| SSL | Let's Encrypt | TLS certificates |
| Containerization | Docker | Backend containerization |
| Process Manager | systemd | Service management |

---

## Security Architecture

### 1. Network Security

**HTTPS Enforcement:**
- All HTTP traffic redirected to HTTPS
- TLS 1.3 with modern cipher suites
- HSTS headers enabled

**Firewall:**
```bash
# UFW Configuration
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP (redirect)
sudo ufw allow 443/tcp     # HTTPS
sudo ufw default deny incoming
sudo ufw enable
```

**Rate Limiting:**
- 10 requests/second per IP
- Burst allowance: 20 requests
- Prevents DDoS and abuse

### 2. Application Security

**API Key Management:**
- Stored in `.env` files (gitignored)
- Never exposed to frontend
- Rotated regularly

**CORS Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**Input Validation:**
- Pydantic models for all requests
- SQL injection prevention (no SQL)
- XSS prevention (sanitized output)

### 3. Data Security

**Sensitive Data:**
- No PII collected
- Conversations stored client-side only
- No user authentication required

**API Keys:**
- Anthropic API key (backend only)
- OpenAI API key (backend only)
- Never logged or exposed

---

## Deployment Architecture

### Single-Server Deployment (Linode)

**Server Specifications:**
- **Plan:** Linode Shared CPU (2GB RAM minimum)
- **OS:** Ubuntu 24.04 LTS
- **Region:** EU (Frankfurt recommended for Iceland)
- **Storage:** 50GB SSD

**Directory Structure:**
```
/opt/chemistry-ai/
├── backend/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── src/
│   ├── data/
│   └── .env
│
├── frontend/
│   └── dist/              # Built files
│
└── nginx/
    └── chemistry-ai.conf

/var/www/chemistry-ai/
└── frontend/              # Served by Nginx
    ├── index.html
    ├── assets/
    └── ...

/var/log/
├── nginx/
│   ├── access.log
│   └── error.log
└── chemistry-ai/
    └── backend.log
```

**Service Management:**
```bash
# Backend (Docker)
docker-compose -f /opt/chemistry-ai/backend/docker-compose.yml up -d

# Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# SSL Renewal
sudo systemctl enable certbot-renew.timer
```

---

## Database Schema

### Chroma Vector Database

**Collection:** `chemistry_chapters_is`

**Schema:**
```python
{
    "id": str,                          # UUID
    "document": str,                    # Text content
    "embedding": List[float],           # 1536-dimensional vector
    "metadata": {
        "chapter": int,                 # Chapter number (1-21)
        "chapter_title": str,           # "Efnasambönd og formúlur"
        "section": str,                 # "2.1"
        "section_title": str,           # "Jónatengi"
        "page": int,                    # Page number
        "chunk_index": int,             # Chunk within section
        "language": str,                # "is"
        "source": str,                  # "OpenStax Chemistry 2e"
    }
}
```

**Indexes:**
- HNSW index for approximate nearest neighbor search
- Metadata indexes for filtering

---

## API Design

### REST API Endpoints

#### POST /ask

**Purpose:** Ask a chemistry question

**Request:**
```json
{
  "question": "Hvað er sýra?",
  "conversation_id": "optional-uuid",
  "max_results": 3
}
```

**Response:**
```json
{
  "answer": "Sýra er efni sem gefur frá sér vetnisatóm (H⁺) þegar það leysist í vatni...",
  "citations": [
    {
      "chapter": 2,
      "section": "2.3",
      "title": "Sýrur og basar",
      "page": 67,
      "excerpt": "Sýrur eru efni sem..."
    }
  ],
  "conversation_id": "uuid",
  "response_time_ms": 1234
}
```

**Error Response:**
```json
{
  "error": "Invalid question format",
  "code": "VALIDATION_ERROR",
  "details": {}
}
```

#### GET /health

**Purpose:** Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "chroma": "healthy",
    "anthropic_api": "healthy",
    "openai_api": "healthy"
  },
  "timestamp": "2025-11-17T12:00:00Z"
}
```

---

## Scalability Considerations

### Current Limitations (Single Server)
- Max concurrent users: ~100
- Max requests/second: ~10
- Single point of failure

### Future Scaling Options

**Option 1: Vertical Scaling**
- Upgrade Linode plan (4GB → 8GB RAM)
- Increase rate limits
- Cost: ~2x current

**Option 2: Horizontal Scaling**
- Add load balancer
- Multiple backend instances
- Shared Chroma DB (PostgreSQL backend)
- Cost: ~3-4x current

**Option 3: Managed Services**
- Use Pinecone/Weaviate for vectors
- API Gateway for rate limiting
- CDN for frontend
- Cost: ~5x current

---

## Monitoring & Observability

### Health Checks
- Endpoint: `GET /health`
- Frequency: Every 5 minutes
- Monitors: API, Chroma DB, External APIs

### Logging
- Application logs: `/var/log/chemistry-ai/`
- Nginx logs: `/var/log/nginx/`
- Docker logs: `docker-compose logs`

### Metrics
- Request count
- Response time (P50, P95, P99)
- Error rate
- API token usage

### Alerts
- Server down
- High error rate (>5%)
- Slow responses (>5s)
- API quota exceeded

---

## Backup & Recovery

### Backup Strategy

**What to Backup:**
1. Chroma vector database (`/data/chroma_db/`)
2. Chemistry content (`/data/chapters/`)
3. Nginx configuration (`/etc/nginx/`)
4. Environment files (`.env`)

**Backup Schedule:**
```bash
# Daily backup at 2 AM
0 2 * * * /opt/chemistry-ai/scripts/backup.sh
```

**Backup Script:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /backup/chemistry-ai-$DATE.tar.gz \
  /opt/chemistry-ai/backend/data \
  /etc/nginx/sites-available/chemistry-ai.conf
```

**Recovery:**
```bash
# Restore from backup
tar -xzf /backup/chemistry-ai-20251117.tar.gz -C /
docker-compose restart
```

---

## Performance Optimization

### Backend Optimizations
- Caching frequently asked questions
- Batch embedding requests
- Connection pooling for APIs
- Async I/O with FastAPI

### Frontend Optimizations
- Code splitting
- Lazy loading components
- CDN for static assets
- Service worker caching

### Database Optimizations
- HNSW index tuning (ef_construction, M)
- Metadata filtering before embedding search
- Periodic re-indexing

---

## Conclusion

This architecture provides a robust, single-server deployment suitable for the MVP phase of the Icelandic Chemistry AI Tutor. The design prioritizes:

✅ Simplicity - Easy to deploy and maintain
✅ Cost-effectiveness - Single server keeps costs low
✅ Security - HTTPS, rate limiting, secure API keys
✅ Scalability - Can upgrade to multi-server later
✅ Reliability - Health checks, backups, monitoring

For production scaling beyond 100 concurrent users, consider the horizontal scaling options outlined in the Scalability section.
