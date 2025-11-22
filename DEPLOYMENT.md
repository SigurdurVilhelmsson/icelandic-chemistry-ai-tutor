# Deployment Guide - Linode Single Server

## kvenno.app Platform Context

**This app is deployed as part of the kvenno.app platform.** See [KVENNO-STRUCTURE.md](KVENNO-STRUCTURE.md) for the complete platform structure.

### Deployment Paths

This AI Chemistry Tutor is deployed to multiple paths on kvenno.app:
- `/1-ar/ai-tutor/` - 1st year chemistry
- `/2-ar/ai-tutor/` - 2nd year chemistry
- `/3-ar/ai-tutor/` - 3rd year chemistry

### Multi-Path Deployment Strategy

⚠️ **IMPORTANT**: Each deployment path requires a **separate build** with its own `VITE_BASE_PATH`:

- `/1-ar/ai-tutor/` - Build with `VITE_BASE_PATH=/1-ar/ai-tutor/`
- `/2-ar/ai-tutor/` - Build with `VITE_BASE_PATH=/2-ar/ai-tutor/`
- `/3-ar/ai-tutor/` - Build with `VITE_BASE_PATH=/3-ar/ai-tutor/`

**Why?** React apps need to know their deployment path for asset loading, internal routing, and API endpoints. Building once and copying to multiple locations will break routing and asset loading.

**Deployment Tools**:
- Use `scripts/deploy-all-paths.sh` to build and deploy to all three paths automatically
- Or manually build for each path (see Section 9 of [KVENNO-STRUCTURE.md](KVENNO-STRUCTURE.md))

**Backend**: Single shared instance serves all year levels (runs on port 8000, accessible via nginx proxy)

### Backend Architecture

**Note on Backend Implementation:**
- This project uses **Python FastAPI** (not Node.js as shown in KVENNO-STRUCTURE.md examples)
- Backend runs on port 8000 in Docker container
- Endpoints: `/ask` (chat), `/health` (health check)
- Nginx proxies these endpoints from public domain to backend
- API keys (Anthropic, OpenAI) stored securely in `backend/.env`

The KVENNO-STRUCTURE.md shows Node.js/Express examples for reference, but the security principles are the same:
- ✅ API keys ONLY in backend, never in frontend
- ✅ Frontend calls backend, backend calls external APIs
- ✅ Nginx proxies requests to backend
- ✅ CORS configured to only allow kvenno.app origins

See Section 3 of [KVENNO-STRUCTURE.md](KVENNO-STRUCTURE.md) for detailed security architecture and Section 9 for deployment workflow.

---

## Architecture Overview

Everything runs on one Linode server (kvenno.app):
- **Nginx (Port 80/443)**: Serves frontend at multiple paths + proxies API requests to backend
- **FastAPI (Port 8000)**: Backend (Docker container, only accessible from localhost)
- **Chroma DB**: Persistent volume in Docker

## Prerequisites

- Linode server (Ubuntu 24.04 recommended)
- Domain name (optional, but recommended)
- SSH access to server
- API keys (Anthropic, OpenAI)

## Initial Setup

### 1. Server Setup

SSH into your Linode server:
```bash
ssh user@your-server-ip
```

Clone repository:
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/icelandic-chemistry-ai-tutor.git
cd icelandic-chemistry-ai-tutor
```

Run initial setup:
```bash
chmod +x scripts/*.sh
./scripts/setup_linode.sh
```

**Important:** Log out and back in for Docker group membership to take effect.

### 2. Configure Environment Variables

Backend configuration:
```bash
nano backend/.env
```

Add:
```
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
CHROMA_DB_PATH=/app/data/chroma_db
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://kvenno.app
# For local development, also add: http://localhost:5173
```

Frontend configuration:
```bash
nano frontend/.env
```

Add:
```
VITE_API_ENDPOINT=https://kvenno.app
# Note: Frontend will append /ask, /health, etc.
# For local testing: http://localhost:8000

VITE_BASE_PATH=/
# Will be set by deploy-all-paths.sh for each build
# Or manually set before building:
# - For 1st year: /1-ar/ai-tutor/
# - For 2nd year: /2-ar/ai-tutor/
# - For 3rd year: /3-ar/ai-tutor/
```

⚠️ **CRITICAL SECURITY**: Never add API keys to frontend/.env!
- ❌ NEVER: `VITE_ANTHROPIC_API_KEY=...` (Keys must ONLY be in backend/.env)
- ✅ CORRECT: API keys in `backend/.env`, not frontend

### 3. Setup Nginx

```bash
./scripts/setup_nginx.sh
```

Enter your domain when prompted (or press Enter for localhost testing).

### 4. Deploy Application

```bash
./scripts/complete_deploy.sh
```

### 5. Get SSL Certificate (Production Only)

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Enable auto-renewal:
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Updating the Application

### Multi-Path Frontend Deployment (Recommended for kvenno.app)

Deploy frontend to all three year paths (requires separate builds):

```bash
cd ~/icelandic-chemistry-ai-tutor
./scripts/deploy-all-paths.sh
```

This script will:
1. Build the frontend three times with different `VITE_BASE_PATH` values
2. Deploy each build to its respective path on the server
3. Set correct permissions
4. Reload nginx

**Before running**, ensure you set these environment variables:
```bash
export DEPLOY_USER=siggi  # Your SSH username
export DEPLOY_HOST=your-server  # Your server hostname or IP
```

See `scripts/deploy-all-paths.sh` for configuration options.

### Legacy Single-Path Deployment (For Testing Only)

⚠️ **Note**: These scripts deploy to a single path and are mainly for local testing.

**Quick Update (Both Frontend + Backend)**:
```bash
cd ~/icelandic-chemistry-ai-tutor
./scripts/deploy.sh
```

**Backend Only**:
```bash
./scripts/deploy_backend.sh
```

**Frontend Only** (single build, single path):
```bash
./scripts/deploy_frontend.sh
```

## Monitoring

### Check Backend Status

```bash
docker-compose -f backend/docker-compose.yml ps
docker-compose -f backend/docker-compose.yml logs -f
```

### Check Nginx Status

```bash
sudo systemctl status nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### View Status Page

Visit: https://yourdomain.com and open browser console to check /health endpoint

Or use the monitoring script:
```bash
nohup python3 monitoring/health_check.py &
tail -f /var/log/chemistry-ai-health.log
```

## Backup & Restore

### Create Backup

```bash
./scripts/backup.sh
```

Backups are stored in: `~/backups/chemistry-ai/`

### Restore from Backup

```bash
./scripts/restore.sh ~/backups/chemistry-ai/chemistry-ai-backup-YYYYMMDD_HHMMSS.tar.gz
```

### Automated Backups

Add to crontab:
```bash
crontab -e
```

Add line:
```
0 2 * * * /home/USERNAME/icelandic-chemistry-ai-tutor/scripts/backup.sh
```

## Troubleshooting

### Backend Not Starting

Check logs:
```bash
docker-compose -f backend/docker-compose.yml logs
```

Common issues:
- Missing API keys in .env
- Port 8000 already in use: `sudo lsof -i :8000`
- Docker not running: `sudo systemctl start docker`

### Frontend Not Loading

Check nginx:
```bash
sudo nginx -t
sudo systemctl status nginx
```

Check files exist:
```bash
ls -la /var/www/chemistry-ai/frontend/
```

### API Calls Failing

Check nginx proxy:
```bash
sudo tail -f /var/log/nginx/error.log
```

Check backend is accessible:
```bash
curl http://localhost:8000/health
```

Check CORS settings in `backend/src/main.py`

### SSL Certificate Issues

Check certificate status:
```bash
sudo certbot certificates
```

Renew manually:
```bash
sudo certbot renew --nginx
```

## Security

### Firewall Status

```bash
sudo ufw status
```

Should show:
- 22/tcp (SSH)
- 80/tcp (HTTP)
- 443/tcp (HTTPS)

### Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Docker Security

Keep Docker updated:
```bash
sudo apt-get install --only-upgrade docker-ce docker-ce-cli containerd.io
```

## Performance Tuning

### Monitor Resources

```bash
htop
docker stats
```

### Nginx Performance

Edit `/etc/nginx/nginx.conf`:
- Increase worker_connections if needed
- Enable caching for static assets
- Adjust timeouts based on usage

### Backend Performance

Edit `backend/docker-compose.yml`:
- Adjust memory limits if needed
- Monitor Chroma DB size

## Maintenance

### Daily Tasks
- Check health monitoring logs
- Verify backups are running

### Weekly Tasks
- Review nginx access logs
- Check disk space: `df -h`
- Update system packages

### Monthly Tasks
- Review and clean old backups
- Check SSL certificate expiry
- Update Docker images

## Getting Help

1. Check logs first (backend, nginx)
2. Verify environment variables
3. Ensure all services are running
4. Check firewall rules
5. Review GitHub issues

## Useful Commands Reference

```bash
# Backend
docker-compose -f backend/docker-compose.yml up -d     # Start
docker-compose -f backend/docker-compose.yml down      # Stop
docker-compose -f backend/docker-compose.yml restart   # Restart
docker-compose -f backend/docker-compose.yml logs -f   # Logs

# Nginx
sudo systemctl start nginx      # Start
sudo systemctl stop nginx       # Stop
sudo systemctl restart nginx    # Restart
sudo systemctl reload nginx     # Reload config
sudo nginx -t                   # Test config

# Monitoring
curl http://localhost:8000/health                      # Backend health
curl https://yourdomain.com/health                     # Public health
sudo tail -f /var/log/nginx/access.log                 # Nginx access
sudo tail -f /var/log/nginx/error.log                  # Nginx errors
docker-compose -f backend/docker-compose.yml logs -f   # Backend logs
```
