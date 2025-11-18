# Efnafræði AI Aðstoðarkennari
### Icelandic Chemistry AI Teaching Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![RANNÍS](https://img.shields.io/badge/Funded%20by-RANN%C3%8DS-blue)](https://www.rannis.is/)

AI-powered chemistry tutor for Icelandic high school students, providing 24/7 personalized learning support in Icelandic.

---

## 🎯 Project Overview

This project delivers a RAG (Retrieval-Augmented Generation) based AI teaching assistant that:
- Answers chemistry questions in Icelandic
- Provides accurate citations from curriculum-aligned content
- Available 24/7 for all students
- Runs entirely on open-source technology

**Funded by:** RANNÍS Sprotasjóður 2025-2026
**Grant:** 3.6M ISK over 12 months
**Status:** Active Development - MVP Phase (November 2025)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Linode Server (Ubuntu 24.04)          │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │  Nginx (Port 80/443)                      │   │
│  │  - Serves React frontend                  │   │
│  │  - Proxies /ask to backend                │   │
│  └────────────┬─────────────────────────────┘   │
│               │                                  │
│  ┌────────────▼─────────────────────────────┐   │
│  │  FastAPI Backend (Port 8000)             │   │
│  │  - RAG pipeline (LangChain)              │   │
│  │  - Claude Sonnet 4 API                   │   │
│  │  - Chroma vector database                │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Linode server (2GB RAM minimum)
- Ubuntu 24.04 LTS
- Domain name (optional but recommended)
- API keys: Anthropic, OpenAI

### Installation

```bash
# 1. Clone repository
git clone https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor.git
cd icelandic-chemistry-ai-tutor

# 2. Run setup
chmod +x scripts/*.sh
./scripts/setup_linode.sh
# Log out and back in for Docker permissions

# 3. Configure environment
cp backend/.env.example backend/.env
nano backend/.env  # Add API keys

cp frontend/.env.example frontend/.env
nano frontend/.env  # Add domain

# 4. Setup nginx
./scripts/setup_nginx.sh

# 5. Deploy
./scripts/complete_deploy.sh

# 6. Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# 7. Ingest chemistry content
cd backend
python -m src.batch_ingest --data-dir ../data/chapters/
```

**Visit:** `https://yourdomain.com`

**Note:** Chemistry chapter content needs to be added to `/data/chapters/` directory before the system can answer questions. Use the content generation tools in `/tools/` to create curriculum-aligned content.

---

## 📁 Project Structure

```
icelandic-chemistry-ai-tutor/
├── backend/                 # Python FastAPI application
│   ├── src/                # Source code
│   │   ├── main.py         # FastAPI app
│   │   ├── rag_pipeline.py # RAG implementation
│   │   ├── vector_store.py # Chroma DB integration
│   │   ├── llm_client.py   # Claude API client
│   │   ├── embeddings.py   # OpenAI embeddings
│   │   ├── content_processor.py # Markdown chunking
│   │   ├── batch_ingest.py # Batch content ingestion
│   │   └── ...
│   ├── tests/              # Backend tests with pytest
│   │   ├── conftest.py     # Shared test fixtures
│   │   └── test_*.py       # Test modules
│   └── data/               # Sample data
│       └── sample/         # Sample content files
│
├── data/                   # Project-level data
│   ├── chapters/           # Chemistry chapter content (to be added)
│   └── logs/               # Application logs
│
├── frontend/               # React + TypeScript application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── utils/          # API client, storage
│   │   └── App.tsx
│   └── public/
│
├── nginx/                  # Nginx configuration
│   ├── nginx.conf
│   └── chemistry-ai.conf
│
├── scripts/                # Deployment scripts
│   ├── setup_linode.sh     # Initial setup
│   ├── deploy.sh           # Full deployment
│   ├── backup.sh           # Database backup
│   └── ...
│
├── dev-tools/              # Developer debugging tools
│   ├── backend/            # RAG debugger, DB inspector, etc.
│   ├── frontend/           # API logger, dev panel
│   └── scripts/            # Helper scripts
│
├── tools/                  # Content generation utilities
│   ├── content_generator.py # AI-powered content generator
│   └── templates/          # Content templates
│
├── monitoring/             # Health monitoring
│   ├── health_check.py
│   └── status.html
│
├── docs/                   # Project documentation
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── DEPLOYMENT.md
│   └── ...
│
└── [Root Documentation]    # Key reference files
    ├── README.md           # This file
    ├── CLAUDE.md           # AI assistant guide
    ├── API_INTEGRATION.md  # External API integration
    ├── DEPLOYMENT.md       # Production deployment
    ├── ENVIRONMENT_VARIABLES.md
    ├── SECURITY.md         # Security practices
    ├── TESTING.md          # Testing strategies
    └── TROUBLESHOOTING.md  # Common issues
```

---

## 🛠️ Technology Stack

### Backend

- **Python 3.11** - Programming language
- **FastAPI** - Web framework
- **LangChain** - LLM orchestration
- **Chroma DB** - Vector database
- **Claude Sonnet 4** - LLM (Anthropic)
- **OpenAI Embeddings** - text-embedding-3-small

### Frontend

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling

### Infrastructure

- **Docker** - Containerization
- **Nginx** - Web server + reverse proxy
- **Let's Encrypt** - SSL certificates
- **Linode** - Hosting

---

## 📚 Documentation

### Core Documentation

- **[CLAUDE.md](CLAUDE.md)** - Comprehensive guide for AI assistants working on this project
- **[API Integration](API_INTEGRATION.md)** - External API integration guide (Claude, OpenAI)
- **[Deployment](DEPLOYMENT.md)** - Production deployment instructions
- **[Environment Variables](ENVIRONMENT_VARIABLES.md)** - Environment configuration reference
- **[Security](SECURITY.md)** - Security practices and guidelines
- **[Testing](TESTING.md)** - Testing strategies and best practices
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

### Detailed Guides

- [Architecture](docs/ARCHITECTURE.md) - Detailed system design
- [Development Guide](docs/DEVELOPMENT.md) - Local setup and development
- [API Reference](docs/API_REFERENCE.md) - API documentation
- [User Guide (IS)](docs/USER_GUIDE_IS.md) - For students
- [Teacher Guide (IS)](docs/TEACHER_GUIDE_IS.md) - For teachers
- [Contributing](docs/CONTRIBUTING.md) - Contribution guidelines

---

## 🔧 Development

### Local Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with API keys
uvicorn src.main:app --reload

# Frontend
cd frontend
npm install
cp .env.example .env
# Edit .env
npm run dev
```

Visit: `http://localhost:5173`

### Running Tests

```bash
# Backend - all tests
cd backend
pytest tests/ -v

# Backend - specific test categories
pytest tests/ -m unit           # Unit tests only
pytest tests/ -m integration    # Integration tests
pytest tests/ -m icelandic      # Icelandic language tests

# Backend - with coverage
pytest tests/ --cov=src --cov-report=html

# Frontend
cd frontend
npm test
```

### Content Generation

Before the system can answer questions, chemistry content must be generated and ingested:

```bash
# Generate Icelandic chemistry content
cd tools
python content_generator.py

# Ingest content into vector database
cd ../backend
python -m src.batch_ingest --data-dir ../data/chapters/

# Validate content
python -m src.chapter_validator ../data/chapters/chapter_01.md

# Inspect database
python -m src.inspect_db
```

See `tools/README.md` for detailed content generation instructions.

### Developer Tools

The project includes helpful debugging and development tools:

```bash
# Backend debugging tools (run from backend/ directory)
python dev-tools/backend/rag_debugger.py          # Interactive RAG pipeline debugger
python dev-tools/backend/db_inspector.py          # Web UI for database inspection (port 5001)
python dev-tools/backend/search_visualizer.py     # Visual similarity search analysis
python dev-tools/backend/token_tracker.py         # API cost monitoring
python dev-tools/backend/performance_profiler.py  # Pipeline performance analysis

# Content generation tools
cd tools
python content_generator.py                       # AI-powered content generator
```

See `dev-tools/README.md` and `tools/README.md` for detailed usage.

---

## 🚢 Deployment

### Full Deployment

```bash
./scripts/deploy.sh
```

### Backend Only

```bash
./scripts/deploy_backend.sh
```

### Frontend Only

```bash
./scripts/deploy_frontend.sh
```

See [Deployment Guide](docs/DEVELOPMENT.md#deployment) for details.

---

## 📊 Monitoring

### Health Check

```bash
curl https://yourdomain.com/health
```

### View Logs

```bash
# Backend
docker-compose -f backend/docker-compose.yml logs -f

# Nginx
sudo tail -f /var/log/nginx/access.log
```

### Status Dashboard

Visit: `https://yourdomain.com/status`

---

## 🔐 Security

- All API keys stored in `.env` (never committed)
- HTTPS only (enforced by nginx)
- CORS properly configured
- Rate limiting enabled
- Regular security updates

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md).

### Quick Contribution Guide

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE).

---

## 🙏 Acknowledgments

- **Funded by:** [RANNÍS](https://www.rannis.is/) Sprotasjóður 2025-2026
- **Content:** OpenStax Chemistry 2e (translated to Icelandic)
- **Schools:** Kvennaskólinn í Reykjavík, Fjölbrautaskólinn við Ármúla
- **Contributors:** See [Contributors](https://github.com/SigurdurVilhelmsson/icelandic-chemistry-ai-tutor/graphs/contributors)

---

## 📞 Contact

**Project Lead:** Sigurður Einar Vilhelmsson
**Email:** sigurdurev@kvenno.is
**School:** Kvennaskólinn í Reykjavík

---

## 📈 Project Status

### Current Status (November 2025)

**✅ Completed:**
- Core RAG pipeline implementation
- FastAPI backend with Claude Sonnet 4 integration
- React frontend with TypeScript
- Comprehensive test suite with pytest
- Developer debugging tools
- Complete documentation suite
- Deployment scripts and infrastructure

**🔄 In Progress:**
- Chemistry chapter content generation and ingestion
- Vector database population with curriculum content
- Production deployment and testing
- User interface refinements

**⏳ Planned:**
- Phase 3: Student Pilot (Feb-Apr 2026)
- Phase 4: Analysis & Research (May-Jun 2026)
- Phase 5: Final Report (Jul 2026)

---

**Built with ❤️ for Icelandic students**
