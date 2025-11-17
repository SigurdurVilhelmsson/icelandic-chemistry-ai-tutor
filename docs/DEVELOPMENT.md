# Development Guide

Complete guide for setting up, developing, testing, and deploying the Icelandic Chemistry AI Tutor.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Local Development Setup](#local-development-setup)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Getting Started

### Prerequisites

**Required:**
- Python 3.11+
- Node.js 18+ and npm
- Git
- Code editor (VS Code recommended)

**For Deployment:**
- Linode account
- Domain name (optional but recommended)
- API keys:
  - Anthropic API key (Claude)
  - OpenAI API key (Embeddings)

**Recommended Tools:**
- Docker Desktop (for testing containerized backend)
- Postman or curl (for API testing)
- Python virtual environment tool (venv, conda, or poetry)

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor.git
cd icelandic-chemistry-ai-tutor
```

### 2. Backend Setup

#### a) Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### b) Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### c) Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

**.env file structure:**
```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO

# CORS Settings (for local development)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Database Settings
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# LLM Settings
MODEL_NAME=claude-sonnet-4-20250514
MAX_TOKENS=1024
TEMPERATURE=0.3

# Embedding Settings
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

#### d) Initialize Vector Database

```bash
# Run the initialization script to populate Chroma DB
python scripts/init_vector_db.py

# This will:
# 1. Load chemistry chapters from data/chapters/
# 2. Split into semantic chunks
# 3. Generate embeddings using OpenAI
# 4. Store in Chroma DB at data/chroma_db/
```

#### e) Start Backend Server

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# The API will be available at:
# http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### 3. Frontend Setup

#### a) Install Dependencies

```bash
cd frontend
npm install
```

#### b) Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env
nano .env
```

**.env file structure:**
```bash
# API URL (local backend)
VITE_API_URL=http://localhost:8000

# Application Settings
VITE_APP_NAME=Efnafræði AI
VITE_APP_DESCRIPTION=AI aðstoðarkennari í efnafræði
```

#### c) Start Development Server

```bash
npm run dev

# The frontend will be available at:
# http://localhost:5173
```

### 4. Verify Setup

Open your browser and navigate to `http://localhost:5173`. You should see the chemistry AI interface. Try asking a question in Icelandic to verify the full stack is working.

**Test Question:** "Hvað er atóm?"

---

## Development Workflow

### Project Structure

```
icelandic-chemistry-ai-tutor/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── rag_pipeline.py      # RAG implementation
│   │   ├── vector_store.py      # Chroma DB operations
│   │   ├── models.py            # Pydantic models
│   │   ├── config.py            # Configuration management
│   │   └── utils.py             # Utility functions
│   ├── data/
│   │   ├── chroma_db/           # Vector database (gitignored)
│   │   ├── chapters/            # Chemistry content
│   │   └── sample/              # Sample data for testing
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_rag_pipeline.py
│   │   └── test_vector_store.py
│   ├── scripts/
│   │   ├── init_vector_db.py
│   │   └── add_content.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── CitationCard.tsx
│   │   │   ├── LoadingIndicator.tsx
│   │   │   └── ErrorMessage.tsx
│   │   ├── utils/
│   │   │   ├── api.ts           # API client
│   │   │   ├── storage.ts       # LocalStorage wrapper
│   │   │   └── formatting.ts    # Text formatting
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript types
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env.example
│
├── scripts/
│   ├── setup_linode.sh          # Server initialization
│   ├── deploy.sh                # Full deployment
│   ├── deploy_backend.sh        # Backend only
│   ├── deploy_frontend.sh       # Frontend only
│   ├── backup.sh                # Database backup
│   └── restore.sh               # Database restore
│
├── nginx/
│   ├── nginx.conf               # Main nginx config
│   └── chemistry-ai.conf        # Site-specific config
│
├── monitoring/
│   ├── health_check.py          # Health monitoring script
│   └── status.html              # Status dashboard
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── API_REFERENCE.md
│   ├── USER_GUIDE_IS.md
│   ├── TEACHER_GUIDE_IS.md
│   └── CONTRIBUTING.md
│
├── .gitignore
├── LICENSE
└── README.md
```

### Adding New Features

#### Backend Feature Development

1. **Create a new branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Implement the feature:**
```python
# Example: Adding a new endpoint in src/main.py

from fastapi import APIRouter
from .models import NewFeatureRequest, NewFeatureResponse

router = APIRouter()

@router.post("/new-feature", response_model=NewFeatureResponse)
async def new_feature(request: NewFeatureRequest):
    # Your implementation
    return NewFeatureResponse(...)
```

3. **Write tests:**
```python
# tests/test_new_feature.py

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_new_feature():
    response = client.post("/new-feature", json={
        "param": "value"
    })
    assert response.status_code == 200
    assert response.json()["result"] == "expected"
```

4. **Run tests:**
```bash
pytest tests/test_new_feature.py -v
```

#### Frontend Feature Development

1. **Create new component:**
```typescript
// src/components/NewFeature.tsx

import React from 'react';

interface NewFeatureProps {
  data: string;
}

export const NewFeature: React.FC<NewFeatureProps> = ({ data }) => {
  return (
    <div className="new-feature">
      {/* Your component JSX */}
    </div>
  );
};
```

2. **Add types:**
```typescript
// src/types/index.ts

export interface NewFeatureData {
  id: string;
  value: string;
}
```

3. **Integrate with API:**
```typescript
// src/utils/api.ts

export async function callNewFeature(param: string): Promise<NewFeatureData> {
  const response = await fetch(`${API_URL}/new-feature`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ param }),
  });

  if (!response.ok) {
    throw new Error('Feature call failed');
  }

  return response.json();
}
```

4. **Test in browser:**
```bash
npm run dev
# Navigate to http://localhost:5173
```

### Code Style Guidelines

#### Python (Backend)

**Follow PEP 8:**
```bash
# Install linters
pip install black flake8 mypy

# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

**Example:**
```python
from typing import List, Optional
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    """Request model for asking questions."""

    question: str
    conversation_id: Optional[str] = None
    max_results: int = 3


async def process_question(request: QuestionRequest) -> dict:
    """
    Process a chemistry question using RAG pipeline.

    Args:
        request: Question request with parameters

    Returns:
        Dictionary with answer and citations
    """
    # Implementation
    pass
```

#### TypeScript (Frontend)

**Follow Airbnb Style Guide:**
```bash
# Install linters
npm install --save-dev eslint prettier

# Format code
npm run format

# Check linting
npm run lint
```

**Example:**
```typescript
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const formatMessage = (message: ChatMessage): string => {
  const time = message.timestamp.toLocaleTimeString('is-IS');
  return `[${time}] ${message.role}: ${message.content}`;
};
```

---

## Testing

### Backend Testing

#### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_rag_pipeline.py

# Run with verbose output
pytest -v
```

**Example Test:**
```python
# tests/test_rag_pipeline.py

import pytest
from src.rag_pipeline import RAGPipeline
from src.vector_store import VectorStore

@pytest.fixture
def rag_pipeline():
    vector_store = VectorStore(persist_directory="./data/test_chroma_db")
    return RAGPipeline(vector_store=vector_store)

def test_answer_question(rag_pipeline):
    question = "Hvað er atóm?"
    result = rag_pipeline.answer(question)

    assert "atóm" in result["answer"].lower()
    assert len(result["citations"]) > 0
    assert result["citations"][0]["chapter"] is not None
```

#### Integration Tests

```python
# tests/test_integration.py

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_full_question_flow():
    # Test the complete flow from API to response
    response = client.post("/ask", json={
        "question": "Hvað er sýra?",
        "max_results": 3
    })

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert len(data["citations"]) > 0
```

#### API Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hvað er atóm?"}'

# With pretty printing
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hvað er efnasamband?"}' | jq
```

### Frontend Testing

#### Component Tests

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

**Example Test:**
```typescript
// src/components/MessageBubble.test.tsx

import { render, screen } from '@testing-library/react';
import { MessageBubble } from './MessageBubble';

describe('MessageBubble', () => {
  it('renders user message correctly', () => {
    render(
      <MessageBubble
        role="user"
        content="Hvað er atóm?"
        timestamp={new Date()}
      />
    );

    expect(screen.getByText('Hvað er atóm?')).toBeInTheDocument();
  });

  it('applies correct styling for assistant', () => {
    const { container } = render(
      <MessageBubble
        role="assistant"
        content="Atóm er minnsta eining..."
        timestamp={new Date()}
      />
    );

    expect(container.firstChild).toHaveClass('assistant-message');
  });
});
```

#### E2E Testing (Optional)

```bash
# Install Playwright
npm install --save-dev @playwright/test

# Run E2E tests
npm run test:e2e
```

**Example E2E Test:**
```typescript
// tests/e2e/chat.spec.ts

import { test, expect } from '@playwright/test';

test('user can ask a question and receive answer', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Type question
  await page.fill('textarea[placeholder*="Spurðu"]', 'Hvað er atóm?');

  // Submit
  await page.click('button[type="submit"]');

  // Wait for response
  await page.waitForSelector('.assistant-message');

  // Check response contains expected content
  const response = await page.textContent('.assistant-message');
  expect(response).toContain('atóm');
});
```

---

## Deployment

### Initial Server Setup (Linode)

#### 1. Create Linode Server

```bash
# Via Linode CLI (optional)
linode-cli linodes create \
  --type g6-standard-2 \
  --region eu-central \
  --image linode/ubuntu24.04 \
  --root_pass YOUR_SECURE_PASSWORD \
  --label chemistry-ai-server
```

Or use the Linode web interface:
- **Image:** Ubuntu 24.04 LTS
- **Region:** Frankfurt (closest to Iceland)
- **Plan:** Shared CPU 2GB ($12/month)

#### 2. SSH into Server

```bash
# Get your server IP from Linode dashboard
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y
```

#### 3. Run Setup Script

```bash
# Clone repository
git clone https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor.git
cd icelandic-chemistry-ai-tutor

# Make scripts executable
chmod +x scripts/*.sh

# Run initial setup
./scripts/setup_linode.sh

# This script will:
# - Install Docker and Docker Compose
# - Install Nginx
# - Install Certbot for SSL
# - Create necessary directories
# - Set up firewall (UFW)
# - Configure system user
```

**Log out and back in** for Docker permissions to take effect.

#### 4. Configure Environment

```bash
# Backend environment
cp backend/.env.example backend/.env
nano backend/.env
# Add your API keys

# Frontend environment
cp frontend/.env.example frontend/.env
nano frontend/.env
# Add your domain
```

#### 5. Setup Nginx

```bash
./scripts/setup_nginx.sh

# This will:
# - Copy nginx configuration
# - Create symlink in sites-enabled
# - Test nginx configuration
# - Reload nginx
```

#### 6. Deploy Application

```bash
./scripts/complete_deploy.sh

# This will:
# - Build frontend (npm run build)
# - Copy frontend to /var/www/chemistry-ai/
# - Build and start backend Docker container
# - Initialize vector database
# - Restart nginx
```

#### 7. Get SSL Certificate

```bash
# Replace yourdomain.com with your actual domain
sudo certbot --nginx -d yourdomain.com

# Follow the prompts:
# - Enter email
# - Agree to terms
# - Choose to redirect HTTP to HTTPS (recommended)

# Test auto-renewal
sudo certbot renew --dry-run
```

#### 8. Verify Deployment

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend (replace with your domain)
curl https://yourdomain.com

# Check logs
docker-compose -f backend/docker-compose.yml logs -f
```

### Update Deployment

#### Full Update

```bash
# On server
cd icelandic-chemistry-ai-tutor
git pull origin main
./scripts/deploy.sh
```

#### Backend Only

```bash
cd icelandic-chemistry-ai-tutor
git pull origin main
./scripts/deploy_backend.sh
```

#### Frontend Only

```bash
cd icelandic-chemistry-ai-tutor
git pull origin main
./scripts/deploy_frontend.sh
```

### Deployment Scripts

#### `scripts/deploy.sh` (Full Deployment)

```bash
#!/bin/bash
set -e

echo "🚀 Starting full deployment..."

# Pull latest code
git pull origin main

# Deploy backend
echo "📦 Deploying backend..."
cd backend
docker-compose down
docker-compose build
docker-compose up -d
cd ..

# Deploy frontend
echo "🎨 Deploying frontend..."
cd frontend
npm install
npm run build
sudo rm -rf /var/www/chemistry-ai/frontend/*
sudo cp -r dist/* /var/www/chemistry-ai/frontend/
cd ..

# Restart nginx
echo "🔄 Restarting nginx..."
sudo systemctl reload nginx

echo "✅ Deployment complete!"
echo "🌐 Visit: https://yourdomain.com"
```

#### `scripts/backup.sh` (Database Backup)

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/chemistry-ai"

mkdir -p $BACKUP_DIR

echo "📦 Creating backup..."

# Backup vector database
tar -czf $BACKUP_DIR/chroma_db_$DATE.tar.gz \
  backend/data/chroma_db/

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
  backend/.env \
  frontend/.env \
  nginx/chemistry-ai.conf

echo "✅ Backup complete: $BACKUP_DIR"

# Keep only last 7 backups
ls -t $BACKUP_DIR/*.tar.gz | tail -n +8 | xargs -r rm

echo "🗑️  Old backups cleaned up"
```

---

## Troubleshooting

### Common Issues

#### Backend won't start

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

#### CORS errors in frontend

**Problem:** Browser console shows CORS error

**Solution:**
```python
# In backend/src/main.py, check CORS settings:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Vector database empty

**Problem:** Questions return "I don't have enough information"

**Solution:**
```bash
cd backend
python scripts/init_vector_db.py
# Check that data/chapters/ has content
```

#### SSL certificate errors

**Problem:** `certbot` fails to get certificate

**Solution:**
```bash
# Make sure:
# 1. Domain DNS points to your server IP
# 2. Nginx is running: sudo systemctl status nginx
# 3. Port 80 is open: sudo ufw allow 80

# Try again:
sudo certbot --nginx -d yourdomain.com
```

#### Docker permission denied

**Problem:** `permission denied while trying to connect to Docker daemon`

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in
exit
ssh user@server
```

### Logs and Debugging

#### Backend Logs

```bash
# Docker logs
docker-compose -f backend/docker-compose.yml logs -f

# Application logs
tail -f backend/logs/app.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

#### Frontend Logs

```bash
# Build logs
npm run build 2>&1 | tee build.log

# Development server
npm run dev
# Check browser console (F12)
```

#### Database Logs

```bash
# Chroma DB logs are in backend logs
docker-compose -f backend/docker-compose.yml logs | grep chroma
```

### Performance Issues

#### Slow response times

**Diagnosis:**
```bash
# Check API response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# curl-format.txt:
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_total:  %{time_total}\n
```

**Solutions:**
1. Cache frequent questions
2. Optimize chunk size in vector DB
3. Reduce `max_results` parameter
4. Upgrade server plan

#### High memory usage

```bash
# Check memory
free -h

# Check Docker memory
docker stats

# Solution: Increase server RAM or optimize chunk size
```

---

## Best Practices

### Development

1. **Always work in a branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Write tests for new features**
   - Aim for >80% code coverage
   - Test edge cases

3. **Use type hints (Python) and types (TypeScript)**
   ```python
   def process_question(question: str) -> dict:
       ...
   ```

4. **Keep environment variables in .env**
   - Never commit .env files
   - Document all variables in .env.example

5. **Write clear commit messages**
   ```bash
   git commit -m "feat: Add citation formatting to responses"
   git commit -m "fix: Handle empty question input"
   git commit -m "docs: Update API reference"
   ```

### Deployment

1. **Test locally before deploying**
   ```bash
   # Run full test suite
   cd backend && pytest
   cd frontend && npm test
   ```

2. **Use deployment scripts**
   - Don't deploy manually
   - Scripts ensure consistency

3. **Backup before major changes**
   ```bash
   ./scripts/backup.sh
   ```

4. **Monitor after deployment**
   ```bash
   # Watch logs for 5 minutes
   docker-compose -f backend/docker-compose.yml logs -f
   ```

5. **Keep dependencies updated**
   ```bash
   # Backend
   pip list --outdated
   pip install --upgrade package-name

   # Frontend
   npm outdated
   npm update
   ```

### Security

1. **Never commit secrets**
   - Use .gitignore
   - Check before committing: `git diff --cached`

2. **Rotate API keys regularly**
   - Every 3-6 months
   - After team member changes

3. **Keep server updated**
   ```bash
   sudo apt update && sudo apt upgrade
   ```

4. **Monitor security advisories**
   - GitHub Dependabot alerts
   - CVE databases

5. **Use HTTPS everywhere**
   - No exceptions for production

---

## Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [LangChain Documentation](https://python.langchain.com/)
- [Chroma Documentation](https://docs.trychroma.com/)

### Tools
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Linode Guides](https://www.linode.com/docs/)

### Community
- GitHub Issues: Report bugs and request features
- Project Email: sigurdurev@kvenno.is

---

## Next Steps

After completing local setup:

1. ✅ Verify backend API at http://localhost:8000/docs
2. ✅ Verify frontend at http://localhost:5173
3. ✅ Test asking questions in Icelandic
4. ✅ Read [API_REFERENCE.md](API_REFERENCE.md) for API details
5. ✅ Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
6. ✅ Start contributing! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Happy coding! 🚀**
