# Chemistry AI Tutor - Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Linode Server                           │
│                   (Ubuntu 24.04 LTS)                        │
└─────────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┴────────────────┐
           │                                │
  ┌────────▼────────┐              ┌────────▼────────┐
  │  Nginx :80/443  │              │  FastAPI :8000  │
  │   (Frontend)    │──── Proxy ──▶│   (Backend)     │
  │                 │              │                 │
  │ Static Files    │              │  Docker         │
  │ SSL/TLS         │              │  Container      │
  └─────────────────┘              └─────────────────┘
           │                                │
    /var/www/chemistry-ai/         ChromaDB + AI
```

## Prerequisites

- Ubuntu 24.04 LTS Server (Linode or similar)
- Domain name pointing to your server's IP
- Root or sudo access
- Docker and Docker Compose installed
- Node.js 18+ and npm installed

## Quick Start

### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Clone repository
git clone <your-repo-url>
cd icelandic-chemistry-ai-tutor
```

### 2. Configure Environment Variables

```bash
# Backend configuration
cd backend
cp .env.example .env
nano .env
```

Update the `.env` file with your API keys:
```env
ANTHROPIC_API_KEY=your_actual_key_here
OPENAI_API_KEY=your_actual_key_here
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
LOG_LEVEL=INFO
```

### 3. Setup Nginx

```bash
# Run nginx setup script
cd ..
sudo ./scripts/setup_nginx.sh
```

### 4. Configure Your Domain

Edit the nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/chemistry-ai
```

Replace all instances of `your-domain.com` with your actual domain.

### 5. Deploy Backend

```bash
cd backend
docker-compose up -d

# Verify backend is running
curl http://localhost:8000/health
```

### 6. Build and Deploy Frontend

```bash
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/chemistry-ai/frontend/dist/
```

### 7. Start Nginx

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 8. Get SSL Certificate

```bash
# Get Let's Encrypt certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Enable automatic renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 9. Verify Deployment

Visit `https://your-domain.com` in your browser.

## Deployment Scripts

### Complete Deployment

Deploy both backend and frontend:
```bash
./scripts/complete_deploy.sh
```

### Frontend Only

Update just the frontend:
```bash
./scripts/build_and_deploy.sh
```

### SSL Renewal

Manually renew SSL certificates:
```bash
sudo ./scripts/renew_ssl.sh
```

### Backend Update

Update backend only:
```bash
cd backend
docker-compose down
docker-compose build
docker-compose up -d
```

## File Structure

```
icelandic-chemistry-ai-tutor/
├── nginx/
│   ├── nginx.conf              # Main nginx configuration
│   ├── chemistry-ai.conf       # Site-specific configuration
│   └── ssl/                    # SSL certificates (auto-generated)
├── scripts/
│   ├── setup_nginx.sh          # Initial nginx setup
│   ├── build_and_deploy.sh     # Frontend deployment
│   ├── renew_ssl.sh            # SSL certificate renewal
│   └── complete_deploy.sh      # Full deployment
├── backend/
│   ├── src/
│   │   └── main.py             # FastAPI application
│   ├── Dockerfile              # Backend container config
│   ├── docker-compose.yml      # Docker orchestration
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables
└── frontend/
    ├── src/                    # React source code
    ├── dist/                   # Built files (generated)
    └── package.json            # Node.js dependencies
```

## Configuration Files

### Nginx Main Config (`nginx/nginx.conf`)
- Worker processes and connections
- SSL/TLS settings
- Gzip compression
- Rate limiting zones
- Logging configuration

### Site Config (`nginx/chemistry-ai.conf`)
- HTTP to HTTPS redirect
- SSL certificate paths
- Security headers
- Static file serving
- API proxy configuration
- Rate limiting rules

### Docker Compose (`backend/docker-compose.yml`)
- Backend container configuration
- Port binding (localhost only)
- Volume mounts
- Health checks
- Environment variables
- Logging settings

## Security Features

### SSL/TLS
- TLS 1.2 and 1.3 only
- Strong cipher suites
- HSTS enabled
- SSL stapling

### Security Headers
- `Strict-Transport-Security`
- `X-Frame-Options`
- `X-Content-Type-Options`
- `X-XSS-Protection`
- `Content-Security-Policy`
- `Referrer-Policy`

### Rate Limiting
- API: 10 requests/second (burst: 20)
- General: 30 requests/second (burst: 50)

### Network Security
- Backend exposed only to localhost
- Docker network isolation
- Hidden files blocked
- Version information hidden

## Monitoring and Logs

### Backend Logs
```bash
# View backend logs
cd backend
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

### Nginx Logs
```bash
# Access log
sudo tail -f /var/log/nginx/chemistry-ai-access.log

# Error log
sudo tail -f /var/log/nginx/chemistry-ai-error.log

# All nginx logs
sudo tail -f /var/log/nginx/*.log
```

### System Monitoring
```bash
# Check nginx status
sudo systemctl status nginx

# Check backend status
cd backend && docker-compose ps

# Check SSL certificate expiry
sudo certbot certificates

# Check disk usage
df -h

# Check memory usage
free -h

# Check docker stats
docker stats
```

## Troubleshooting

### Frontend Not Loading

**Problem:** Blank page or 404 errors

**Solution:**
```bash
# Check if files exist
ls -la /var/www/chemistry-ai/frontend/dist/

# Check nginx error log
sudo tail -f /var/log/nginx/chemistry-ai-error.log

# Verify nginx config
sudo nginx -t

# Rebuild and redeploy
cd frontend
npm run build
sudo cp -r dist/* /var/www/chemistry-ai/frontend/dist/
sudo systemctl reload nginx
```

### API Not Working

**Problem:** API calls return 502 or timeout

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check backend logs
cd backend
docker-compose logs --tail=50

# Restart backend
docker-compose restart

# Check CORS settings
grep ALLOWED_ORIGINS backend/.env
```

### SSL Certificate Issues

**Problem:** Certificate expired or invalid

**Solution:**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew --force-renewal

# Reload nginx
sudo systemctl reload nginx
```

### High CPU/Memory Usage

**Problem:** Server running slow

**Solution:**
```bash
# Check Docker resource usage
docker stats

# Check system resources
htop

# Restart backend with limits
cd backend
docker-compose down
# Edit docker-compose.yml to add resource limits
docker-compose up -d
```

### Port Already in Use

**Problem:** Cannot start nginx or backend

**Solution:**
```bash
# Check what's using port 80/443
sudo lsof -i :80
sudo lsof -i :443

# Check what's using port 8000
sudo lsof -i :8000

# Kill the process or change configuration
```

## Maintenance

### Regular Updates

**Weekly:**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Check SSL certificate expiry
sudo certbot certificates
```

**Monthly:**
```bash
# Review logs for errors
sudo journalctl -u nginx --since "1 month ago" | grep error

# Review backend logs
cd backend && docker-compose logs --since 720h | grep -i error

# Clean up Docker
docker system prune -a
```

### Backup Strategy

**Configuration Backup:**
```bash
# Backup nginx config
sudo cp /etc/nginx/sites-available/chemistry-ai \
   ~/backups/chemistry-ai-$(date +%Y%m%d).conf

# Backup environment variables
cp backend/.env ~/backups/.env-$(date +%Y%m%d)
```

**Database Backup:**
```bash
# Backup ChromaDB data
cd backend
docker-compose exec backend tar -czf /app/data/chroma_backup.tar.gz /app/data/chroma_db
docker cp <container-id>:/app/data/chroma_backup.tar.gz ~/backups/
```

### Performance Optimization

**Nginx Caching:**
```nginx
# Add to chemistry-ai.conf
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;

location /ask {
    proxy_cache api_cache;
    proxy_cache_valid 200 10m;
    # ... rest of config
}
```

**Docker Resource Limits:**
```yaml
# Add to docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          memory: 1G
```

## Updating the Application

### Full Update
```bash
git pull origin main
./scripts/complete_deploy.sh
```

### Backend Only
```bash
git pull origin main
cd backend
docker-compose down
docker-compose build
docker-compose up -d
```

### Frontend Only
```bash
git pull origin main
./scripts/build_and_deploy.sh
```

## Rollback Procedure

If deployment fails:

```bash
# Rollback git
git reset --hard HEAD~1

# Restore previous backend
cd backend
docker-compose down
git checkout HEAD~1 -- .
docker-compose up -d

# Restore previous frontend
cd ../frontend
git checkout HEAD~1 -- .
npm install
npm run build
sudo cp -r dist/* /var/www/chemistry-ai/frontend/dist/
```

## Support and Resources

- **Nginx Documentation:** https://nginx.org/en/docs/
- **Docker Documentation:** https://docs.docker.com/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Let's Encrypt:** https://letsencrypt.org/docs/
- **Certbot:** https://certbot.eff.org/

## Production Checklist

Before going live:

- [ ] Domain DNS configured
- [ ] SSL certificate installed
- [ ] Environment variables set
- [ ] API keys configured
- [ ] CORS origins updated
- [ ] Rate limiting configured
- [ ] Logging enabled
- [ ] Health checks working
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] SSL auto-renewal enabled
- [ ] Security headers verified
- [ ] Firewall configured
- [ ] Documentation updated
