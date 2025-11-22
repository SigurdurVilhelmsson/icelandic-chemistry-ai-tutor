# Environment Variables Reference

## 🔐 Critical Security Requirements

⚠️ **NEVER expose API keys in frontend code!**

**Key Security Rules:**
1. **API keys MUST ONLY be in `backend/.env`** - Never in frontend environment variables
2. **NEVER use `VITE_` prefix for secrets** - Vite embeds these in client JavaScript
3. **Frontend variables are PUBLIC** - Anyone can extract them from browser DevTools
4. **Backend variables are PRIVATE** - Stored securely on server, never sent to browsers

See [KVENNO-STRUCTURE.md](KVENNO-STRUCTURE.md) Section 3 for complete backend security architecture.

---

## Backend (.env)

Located at: `backend/.env`

⚠️ **All secrets (API keys) must be stored here, NOT in frontend/.env**

### Required

**ANTHROPIC_API_KEY**
- Your Anthropic API key for Claude Sonnet 4
- Get from: https://console.anthropic.com/
- Format: `sk-ant-...`
- Used for: Generating AI responses
- ⚠️ **CRITICAL**: Must ONLY be in backend/.env, never in frontend

**OPENAI_API_KEY**
- Your OpenAI API key for embeddings
- Get from: https://platform.openai.com/api-keys
- Format: `sk-...`
- Used for: Text embeddings (text-embedding-3-small)
- ⚠️ **CRITICAL**: Must ONLY be in backend/.env, never in frontend

### Optional

**CHROMA_DB_PATH**
- Path to Chroma vector database
- Default: `/app/data/chroma_db`
- Used for: Storing content embeddings

**LOG_LEVEL**
- Logging level: DEBUG, INFO, WARNING, ERROR
- Default: `INFO`
- Used for: Controlling log verbosity

**ALLOWED_ORIGINS**
- Comma-separated list of allowed CORS origins
- Production: `https://kvenno.app,https://www.kvenno.app`
- Development: Add `http://localhost:5173`
- Used for: CORS security - restricts which domains can call the API

---

## Frontend (.env)

Located at: `frontend/.env`

⚠️ **All variables here are PUBLIC and embedded in client JavaScript**

### Required

**VITE_API_ENDPOINT**
- Base URL of backend API
- Development: `http://localhost:8000`
- Production: `https://kvenno.app`
- Used for: API calls from frontend (frontend will append /ask, /health, etc.)
- Note: Points to the base domain; nginx proxies /ask and /health to backend on port 8000

**VITE_BASE_PATH**
- Base path for multi-path deployment on kvenno.app
- Required for asset loading and routing to work correctly
- **MUST be set before building for each deployment path**
- Values:
  - 1st year: `/1-ar/ai-tutor/`
  - 2nd year: `/2-ar/ai-tutor/`
  - 3rd year: `/3-ar/ai-tutor/`
  - Development/testing: `/`
- Used by: Vite build process to configure asset paths
- See: [KVENNO-STRUCTURE.md](KVENNO-STRUCTURE.md) Section 1 for deployment strategy

### Optional (for future authentication)

**VITE_AZURE_CLIENT_ID**
- Azure AD application client ID (public value, safe to expose)
- Get from: Azure AD app registration
- Used for: User authentication with school accounts
- Note: This is a PUBLIC identifier, not a secret

**VITE_AZURE_TENANT_ID**
- Azure AD tenant ID (public value, safe to expose)
- Get from: Azure AD app registration
- Used for: User authentication with school accounts
- Note: This is a PUBLIC identifier, not a secret

## System Environment Variables

### Nginx

These are set in nginx configuration files, not .env:

**Domain Configuration**
- Edit: `nginx/chemistry-ai.conf`
- Replace: `server_name _` with your domain
- Replace: SSL certificate paths with your domain

### Docker Compose

**ALLOWED_ORIGINS**
- Set in `docker-compose.yml`
- Controls CORS policy
- Should match your domain

## Setting Environment Variables

### Development (Local)
```bash
# Backend
cp backend/.env.example backend/.env
nano backend/.env

# Frontend
cp frontend/.env.example frontend/.env
nano frontend/.env
```

### Production (Linode)

Same as development, but use production values:
- VITE_API_ENDPOINT → Your domain
- ALLOWED_ORIGINS → Your domain

### Docker Compose

Variables in `docker-compose.yml` can reference `.env`:
```yaml
environment:
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

### GitHub Actions (CI/CD)

Set secrets in GitHub repository settings:
- LINODE_HOST
- LINODE_USER
- LINODE_SSH_KEY

## Multi-Path Deployment Workflow

The AI Tutor is deployed to three different paths on kvenno.app. Each requires a **separate build**.

### Building for Each Path

```bash
# Build 1: For 1st year
export VITE_BASE_PATH=/1-ar/ai-tutor/
export VITE_API_ENDPOINT=https://kvenno.app
npm run build
# Deploy dist/* to /var/www/kvenno.app/1-ar/ai-tutor/

# Build 2: For 2nd year
export VITE_BASE_PATH=/2-ar/ai-tutor/
export VITE_API_ENDPOINT=https://kvenno.app
npm run build
# Deploy dist/* to /var/www/kvenno.app/2-ar/ai-tutor/

# Build 3: For 3rd year
export VITE_BASE_PATH=/3-ar/ai-tutor/
export VITE_API_ENDPOINT=https://kvenno.app
npm run build
# Deploy dist/* to /var/www/kvenno.app/3-ar/ai-tutor/
```

### Automated Deployment

Use the provided script to deploy to all paths:
```bash
./scripts/deploy-all-paths.sh
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

---

## Security Best Practices

### Critical Rules

1. **NEVER put API keys in VITE_ environment variables**
   - ❌ WRONG: `VITE_ANTHROPIC_API_KEY=sk-ant-...` (NEVER DO THIS!)
   - ✅ CORRECT: `ANTHROPIC_API_KEY=sk-ant-...` in `backend/.env` only
   - Why: VITE_ variables are embedded in client JavaScript and can be extracted by anyone

2. **Understand public vs private variables**
   - **PRIVATE** (backend/.env only): API keys, database credentials, secrets
   - **PUBLIC** (frontend VITE_ variables): API endpoints, Azure AD client IDs, base paths
   - If it's secret, it goes in backend/.env. If it's not secret, it can be VITE_

3. **Use backend as API proxy**
   - Frontend calls backend at `/ask`, `/health` endpoints
   - Backend (FastAPI on port 8000) calls Claude/OpenAI with secure keys
   - Nginx proxies these paths from public domain to backend
   - Frontend never directly accesses Claude/OpenAI APIs

### General Best Practices

4. **Never commit .env files to Git**
   - Already in .gitignore
   - Always use .env.example as template
   - Never share actual .env files publicly

5. **Rotate API keys regularly**
   - Especially if compromised
   - Update both .env and restart services
   - Monitor API usage for anomalies

6. **Use different keys for dev/prod**
   - Helps track usage and costs
   - Limits blast radius if compromised
   - Makes it easier to revoke dev keys

7. **Limit API key permissions**
   - Anthropic: Use project-specific keys
   - OpenAI: Set usage limits and budgets
   - Monitor spending regularly

8. **Secure .env file permissions**
   ```bash
   chmod 600 backend/.env  # Only owner can read/write
   ```

## Troubleshooting

### Backend won't start

Check if API keys are set:
```bash
grep "API_KEY" backend/.env
```

Should not show placeholder values.

### API calls fail with CORS errors

Check ALLOWED_ORIGINS:
```bash
grep "ALLOWED_ORIGINS" backend/.env
```

Should include your frontend domain.

### Frontend can't reach backend

Check VITE_API_ENDPOINT:
```bash
grep "VITE_API_ENDPOINT" frontend/.env
```

Should match your backend URL.

### After changing environment variables

Rebuild and restart:
```bash
# Backend
docker-compose -f backend/docker-compose.yml down
docker-compose -f backend/docker-compose.yml up -d --build

# Frontend (if changed)
cd frontend
npm run build
sudo cp -r dist/* /var/www/chemistry-ai/frontend/
```
