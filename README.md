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
**Status:** MVP Phase (August 2025 - July 2026)

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
git clone https://github.com/YOUR_USERNAME/icelandic-chemistry-ai-tutor.git
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
```

**Visit:** `https://yourdomain.com`

---

## 📁 Project Structure

```
icelandic-chemistry-ai-tutor/
├── backend/                 # Python FastAPI application
│   ├── src/                # Source code
│   │   ├── main.py         # FastAPI app
│   │   ├── rag_pipeline.py # RAG implementation
│   │   ├── vector_store.py # Chroma DB integration
│   │   └── ...
│   ├── data/               # Content and database
│   │   ├── chroma_db/      # Vector database
│   │   ├── chapters/       # OpenStax chapters
│   │   └── sample/         # Sample content
│   └── tests/              # Backend tests
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
├── monitoring/             # Health monitoring
│   ├── health_check.py
│   └── status.html
│
└── docs/                   # Documentation
    ├── ARCHITECTURE.md
    ├── DEVELOPMENT.md
    ├── DEPLOYMENT.md
    └── ...
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
# Backend
cd backend
pytest tests/

# Frontend
cd frontend
npm test
```

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

- ✅ Phase 1: Foundation & Setup (Aug-Oct 2025)
- ✅ Phase 2: Development & Testing (Nov 2025-Jan 2026)
- 🔄 Phase 3: Student Pilot (Feb-Apr 2026)
- ⏳ Phase 4: Analysis & Research (May-Jun 2026)
- ⏳ Phase 5: Final Report (Jul 2026)

---

**Built with ❤️ for Icelandic students**
