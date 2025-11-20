# Deployment Guide - Linode Single Server

## kvenno.app Platform Context

**This app is deployed as part of the kvenno.app platform.** See [Kvenno_structure.md](Kvenno_structure.md) for the complete platform structure.

### Deployment Paths

This AI Chemistry Tutor is deployed to multiple paths on kvenno.app:
- `/1-ar/ai-tutor/` - 1st year chemistry
- `/2-ar/ai-tutor/` - 2nd year chemistry
- `/3-ar/ai-tutor/` - 3rd year chemistry

### Multi-Path Deployment Strategy

The same React build is served from all three paths:
- **Nginx configuration**: Routes all `/*/ai-tutor/` paths to the same frontend build
- **React Router**: Uses dynamic `basename` based on current path
- **Backend**: Single shared instance serves all year levels

See Section 9 of [Kvenno_structure.md](Kvenno_structure.md) for detailed deployment configuration.

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
# Or for testing: http://localhost:8000
```

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

### Quick Update (Both Frontend + Backend)

```bash
cd ~/icelandic-chemistry-ai-tutor
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
