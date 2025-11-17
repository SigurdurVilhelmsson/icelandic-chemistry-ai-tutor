# API Reference

Complete API documentation for the Icelandic Chemistry AI Tutor backend.

---

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
- [Models](#models)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

---

## Overview

The Chemistry AI Tutor API is a REST API built with FastAPI. It provides endpoints for asking chemistry questions, retrieving health status, and managing conversations.

**API Version:** 1.0.0
**Protocol:** HTTPS
**Format:** JSON

---

## Authentication

Currently, the API does not require authentication for MVP phase. All endpoints are publicly accessible.

**Future:** Authentication will be added in Phase 2 for:
- Usage tracking
- Rate limiting per user
- Teacher dashboards

---

## Base URL

### Production
```
https://yourdomain.com/api
```

### Development (Local)
```
http://localhost:8000
```

All endpoints are relative to the base URL.

---

## Endpoints

### 1. Ask Question

Ask a chemistry question and receive an AI-generated answer with citations.

#### Request

```http
POST /ask
Content-Type: application/json
```

**Body:**
```json
{
  "question": "Hvað er sýra?",
  "conversation_id": "optional-uuid-v4",
  "max_results": 3
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | Yes | Chemistry question in Icelandic (1-500 chars) |
| `conversation_id` | string | No | UUID to maintain conversation context |
| `max_results` | integer | No | Number of context chunks to retrieve (1-10, default: 3) |

#### Response

**Success (200 OK):**
```json
{
  "answer": "Sýra er efni sem gefur frá sér vetnisatóm (H⁺) þegar það leysist í vatni. Sýrur hafa súrt bragð og breyta litum á litmuspapír í rautt. Dæmi um algengar sýrur eru saltsýra (HCl), brennisteinssýra (H₂SO₄) og ediksýra (CH₃COOH).",
  "citations": [
    {
      "chapter": 3,
      "chapter_title": "Sýrur og basar",
      "section": "3.1",
      "section_title": "Skilgreining á sýrum",
      "page": 67,
      "excerpt": "Sýrur eru efni sem gefa frá sér vetnisatóm..."
    },
    {
      "chapter": 3,
      "section": "3.2",
      "page": 72,
      "excerpt": "Algengar sýrur í daglegu lífi..."
    }
  ],
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response_time_ms": 1234,
  "chunks_retrieved": 3,
  "model_used": "claude-sonnet-4-20250514"
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | AI-generated answer in Icelandic |
| `citations` | array | List of source citations |
| `citations[].chapter` | integer | Chapter number in textbook |
| `citations[].chapter_title` | string | Chapter title in Icelandic |
| `citations[].section` | string | Section identifier (e.g., "3.1") |
| `citations[].section_title` | string | Section title in Icelandic |
| `citations[].page` | integer | Page number in textbook |
| `citations[].excerpt` | string | Relevant text excerpt |
| `conversation_id` | string | UUID for this conversation |
| `response_time_ms` | integer | API processing time in milliseconds |
| `chunks_retrieved` | integer | Number of chunks used for context |
| `model_used` | string | LLM model identifier |

**Error Responses:**

**400 Bad Request:**
```json
{
  "error": "Invalid question format",
  "code": "VALIDATION_ERROR",
  "details": {
    "field": "question",
    "message": "Question must be between 1 and 500 characters"
  }
}
```

**429 Too Many Requests:**
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after_seconds": 60
}
```

**500 Internal Server Error:**
```json
{
  "error": "Failed to process question",
  "code": "INTERNAL_ERROR",
  "details": {
    "message": "LLM API unavailable"
  }
}
```

#### Example

**cURL:**
```bash
curl -X POST https://yourdomain.com/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Hvað er atóm?",
    "max_results": 3
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "https://yourdomain.com/api/ask",
    json={
        "question": "Hvað er atóm?",
        "max_results": 3
    }
)

data = response.json()
print(data["answer"])
for citation in data["citations"]:
    print(f"Chapter {citation['chapter']}, Page {citation['page']}")
```

**JavaScript:**
```javascript
const response = await fetch('https://yourdomain.com/api/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'Hvað er atóm?',
    max_results: 3,
  }),
});

const data = await response.json();
console.log(data.answer);
```

---

### 2. Health Check

Check the health status of the API and its dependencies.

#### Request

```http
GET /health
```

**No parameters required.**

#### Response

**Success (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-17T12:00:00Z",
  "components": {
    "api": {
      "status": "healthy",
      "response_time_ms": 1
    },
    "chroma_db": {
      "status": "healthy",
      "collections": 1,
      "documents": 1247,
      "response_time_ms": 23
    },
    "anthropic_api": {
      "status": "healthy",
      "response_time_ms": 156
    },
    "openai_api": {
      "status": "healthy",
      "response_time_ms": 89
    }
  },
  "uptime_seconds": 86400
}
```

**Degraded (200 OK):**
```json
{
  "status": "degraded",
  "version": "1.0.0",
  "timestamp": "2025-11-17T12:00:00Z",
  "components": {
    "api": {
      "status": "healthy"
    },
    "chroma_db": {
      "status": "healthy"
    },
    "anthropic_api": {
      "status": "unhealthy",
      "error": "Connection timeout"
    },
    "openai_api": {
      "status": "healthy"
    }
  }
}
```

**Unhealthy (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "timestamp": "2025-11-17T12:00:00Z",
  "components": {
    "api": {
      "status": "healthy"
    },
    "chroma_db": {
      "status": "unhealthy",
      "error": "Database connection failed"
    }
  }
}
```

#### Example

**cURL:**
```bash
curl https://yourdomain.com/api/health
```

**Python:**
```python
import requests

response = requests.get("https://yourdomain.com/api/health")
health = response.json()

if health["status"] == "healthy":
    print("✅ API is healthy")
else:
    print(f"⚠️ API status: {health['status']}")
```

---

### 3. Metrics

Get usage metrics and statistics (for monitoring).

#### Request

```http
GET /metrics
```

**No parameters required.**

#### Response

**Success (200 OK):**
```json
{
  "total_requests": 1234,
  "successful_requests": 1200,
  "failed_requests": 34,
  "average_response_time_ms": 1456,
  "p50_response_time_ms": 1200,
  "p95_response_time_ms": 2300,
  "p99_response_time_ms": 3500,
  "requests_last_hour": 67,
  "requests_last_day": 890,
  "error_rate": 0.027,
  "uptime_seconds": 86400,
  "vector_db_size_mb": 245,
  "api_tokens_used": 456789
}
```

#### Example

**cURL:**
```bash
curl https://yourdomain.com/api/metrics
```

---

### 4. Feedback (Future)

Submit user feedback on answers.

#### Request

```http
POST /feedback
Content-Type: application/json
```

**Body:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "rating": 5,
  "comment": "Mjög gott svar!",
  "helpful": true
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `conversation_id` | string | Yes | UUID of the conversation |
| `rating` | integer | No | Rating 1-5 |
| `comment` | string | No | Text feedback (max 500 chars) |
| `helpful` | boolean | No | Whether answer was helpful |

#### Response

**Success (200 OK):**
```json
{
  "success": true,
  "message": "Takk fyrir endurgjöfina!"
}
```

---

## Models

### QuestionRequest

```python
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    conversation_id: Optional[str] = Field(None, regex=UUID4_REGEX)
    max_results: int = Field(3, ge=1, le=10)
```

**TypeScript:**
```typescript
interface QuestionRequest {
  question: string;           // 1-500 characters
  conversation_id?: string;   // UUID v4 format
  max_results?: number;       // 1-10, default: 3
}
```

### QuestionResponse

```python
class Citation(BaseModel):
    chapter: int
    chapter_title: str
    section: str
    section_title: Optional[str]
    page: int
    excerpt: str

class QuestionResponse(BaseModel):
    answer: str
    citations: List[Citation]
    conversation_id: str
    response_time_ms: int
    chunks_retrieved: int
    model_used: str
```

**TypeScript:**
```typescript
interface Citation {
  chapter: number;
  chapter_title: string;
  section: string;
  section_title?: string;
  page: number;
  excerpt: string;
}

interface QuestionResponse {
  answer: string;
  citations: Citation[];
  conversation_id: string;
  response_time_ms: number;
  chunks_retrieved: number;
  model_used: string;
}
```

### HealthResponse

```python
class ComponentHealth(BaseModel):
    status: Literal["healthy", "unhealthy"]
    response_time_ms: Optional[int]
    error: Optional[str]

class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    timestamp: datetime
    components: Dict[str, ComponentHealth]
    uptime_seconds: int
```

**TypeScript:**
```typescript
interface ComponentHealth {
  status: 'healthy' | 'unhealthy';
  response_time_ms?: number;
  error?: string;
}

interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: string;
  components: {
    [key: string]: ComponentHealth;
  };
  uptime_seconds: number;
}
```

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "field_name",
    "message": "Detailed message"
  }
}
```

### Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid request parameters |
| 400 | `INVALID_QUESTION` | Question format or content invalid |
| 404 | `NOT_FOUND` | Resource not found |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |
| 503 | `SERVICE_UNAVAILABLE` | Service temporarily unavailable |
| 503 | `LLM_API_ERROR` | External LLM API error |
| 503 | `VECTOR_DB_ERROR` | Vector database error |

### Example Error Handling

**Python:**
```python
import requests

try:
    response = requests.post(
        "https://yourdomain.com/api/ask",
        json={"question": "Hvað er atóm?"}
    )
    response.raise_for_status()
    data = response.json()

except requests.exceptions.HTTPError as e:
    error = e.response.json()

    if error["code"] == "RATE_LIMIT_EXCEEDED":
        print(f"Rate limited. Retry after {error['retry_after_seconds']}s")
    elif error["code"] == "VALIDATION_ERROR":
        print(f"Invalid input: {error['details']['message']}")
    else:
        print(f"Error: {error['error']}")

except requests.exceptions.ConnectionError:
    print("Could not connect to API")
```

**JavaScript:**
```javascript
try {
  const response = await fetch('https://yourdomain.com/api/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: 'Hvað er atóm?' }),
  });

  if (!response.ok) {
    const error = await response.json();

    switch (error.code) {
      case 'RATE_LIMIT_EXCEEDED':
        console.error(`Rate limited. Retry after ${error.retry_after_seconds}s`);
        break;
      case 'VALIDATION_ERROR':
        console.error(`Invalid input: ${error.details.message}`);
        break;
      default:
        console.error(`Error: ${error.error}`);
    }
    return;
  }

  const data = await response.json();
  console.log(data.answer);

} catch (error) {
  console.error('Network error:', error);
}
```

---

## Rate Limiting

### Limits

**Per IP Address:**
- 10 requests per second
- 100 requests per minute
- 1000 requests per hour

**Burst allowance:** 20 requests

### Headers

Rate limit information is included in response headers:

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1700000000
```

### Rate Limit Exceeded Response

**429 Too Many Requests:**
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after_seconds": 60
}
```

**Headers:**
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1700000060
```

---

## Examples

### Complete Conversation Flow

**Python Example:**

```python
import requests
import uuid

class ChemistryAIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.conversation_id = str(uuid.uuid4())

    def ask(self, question: str, max_results: int = 3) -> dict:
        """Ask a chemistry question."""
        response = requests.post(
            f"{self.base_url}/ask",
            json={
                "question": question,
                "conversation_id": self.conversation_id,
                "max_results": max_results
            }
        )
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        """Check API health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

# Usage
client = ChemistryAIClient("https://yourdomain.com/api")

# Check health
health = client.health_check()
print(f"API Status: {health['status']}")

# Ask questions
result1 = client.ask("Hvað er atóm?")
print(f"Answer: {result1['answer']}")
print(f"Citations: {len(result1['citations'])}")

# Follow-up question (same conversation)
result2 = client.ask("Hvað er rafeind?")
print(f"Answer: {result2['answer']}")
```

**JavaScript/TypeScript Example:**

```typescript
class ChemistryAIClient {
  private baseUrl: string;
  private conversationId: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.conversationId = crypto.randomUUID();
  }

  async ask(
    question: string,
    maxResults: number = 3
  ): Promise<QuestionResponse> {
    const response = await fetch(`${this.baseUrl}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        conversation_id: this.conversationId,
        max_results: maxResults,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }

    return response.json();
  }

  async healthCheck(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  }
}

// Usage
const client = new ChemistryAIClient('https://yourdomain.com/api');

// Check health
const health = await client.healthCheck();
console.log(`API Status: ${health.status}`);

// Ask questions
const result1 = await client.ask('Hvað er atóm?');
console.log(`Answer: ${result1.answer}`);
console.log(`Citations: ${result1.citations.length}`);

// Follow-up question
const result2 = await client.ask('Hvað er rafeind?');
console.log(`Answer: ${result2.answer}`);
```

### Batch Processing

**Python Example:**

```python
import asyncio
import aiohttp

async def ask_question(session, question: str):
    """Ask a single question asynchronously."""
    async with session.post(
        "https://yourdomain.com/api/ask",
        json={"question": question}
    ) as response:
        return await response.json()

async def batch_questions(questions: list[str]):
    """Ask multiple questions in parallel."""
    async with aiohttp.ClientSession() as session:
        tasks = [ask_question(session, q) for q in questions]
        results = await asyncio.gather(*tasks)
        return results

# Usage
questions = [
    "Hvað er atóm?",
    "Hvað er sameind?",
    "Hvað er jón?"
]

results = asyncio.run(batch_questions(questions))
for q, r in zip(questions, results):
    print(f"Q: {q}")
    print(f"A: {r['answer'][:100]}...")
    print()
```

---

## Interactive API Documentation

FastAPI provides interactive API documentation:

### Swagger UI

Visit: `https://yourdomain.com/api/docs`

Features:
- Try out endpoints directly in browser
- See request/response examples
- View all available endpoints
- Test authentication

### ReDoc

Visit: `https://yourdomain.com/api/redoc`

Features:
- Clean, readable documentation
- Detailed model schemas
- Code examples
- Printable format

---

## API Client Libraries

### Official Clients

**Python:**
```bash
pip install chemistry-ai-client
```

**JavaScript/TypeScript:**
```bash
npm install @chemistry-ai/client
```

### Community Clients

- Rust: Coming soon
- Go: Coming soon
- Ruby: Coming soon

---

## Versioning

The API follows semantic versioning (SemVer):

**Current version:** `1.0.0`

**Version format:** `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes

**Version header:**
```http
X-API-Version: 1.0.0
```

---

## Changelog

### Version 1.0.0 (2025-11-17)

**Initial release:**
- ✅ POST /ask - Ask chemistry questions
- ✅ GET /health - Health check
- ✅ GET /metrics - Usage metrics
- ✅ Rate limiting (10 req/s per IP)
- ✅ CORS support
- ✅ Error handling

### Future Versions

**Version 1.1.0 (Planned):**
- User authentication
- Conversation history API
- POST /feedback endpoint
- WebSocket support for streaming responses

**Version 2.0.0 (Planned):**
- Multi-language support
- Image-based questions
- Enhanced citations with page previews
- User management API

---

## Support

For API support:

- **Documentation:** https://docs.yourdomain.com
- **Email:** sigurdurev@kvenno.is
- **GitHub Issues:** https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor/issues

---

**API Reference v1.0.0**
**Last Updated:** 2025-11-17
