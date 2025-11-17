# Environment Variables Reference

## Backend (.env)

Located at: `backend/.env`

### Required

**ANTHROPIC_API_KEY**
- Your Anthropic API key for Claude Sonnet 4
- Get from: https://console.anthropic.com/
- Format: `sk-ant-...`
- Used for: Generating AI responses

**OPENAI_API_KEY**
- Your OpenAI API key for embeddings
- Get from: https://platform.openai.com/api-keys
- Format: `sk-...`
- Used for: Text embeddings (text-embedding-3-small)

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
- Example: `https://yourdomain.com,http://localhost:5173`
- Used for: CORS security

## Frontend (.env)

Located at: `frontend/.env`

### Required

**VITE_API_ENDPOINT**
- URL of backend API
- Development: `http://localhost:8000`
- Production: `https://yourdomain.com`
- Used for: API calls from frontend

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

## Security Best Practices

1. **Never commit .env files to Git**
   - Already in .gitignore
   - Always use .env.example as template

2. **Rotate API keys regularly**
   - Especially if compromised
   - Update both .env and restart services

3. **Use different keys for dev/prod**
   - Helps track usage
   - Limits blast radius if compromised

4. **Limit API key permissions**
   - Anthropic: Use project-specific keys
   - OpenAI: Set usage limits

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
