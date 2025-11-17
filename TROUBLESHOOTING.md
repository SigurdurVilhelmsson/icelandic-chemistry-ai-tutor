# Troubleshooting Guide

## Common Issues & Solutions

### Backend Issues

#### Backend container won't start

**Symptoms:**
- `docker-compose up` fails
- Container exits immediately

**Solutions:**
```bash
# Check logs
docker-compose -f backend/docker-compose.yml logs

# Common causes:
# 1. Missing API keys
grep "API_KEY" backend/.env

# 2. Port already in use
sudo lsof -i :8000
# Kill process if needed: sudo kill -9 <PID>

# 3. Docker daemon not running
sudo systemctl start docker

# 4. Rebuild from scratch
docker-compose -f backend/docker-compose.yml down -v
docker-compose -f backend/docker-compose.yml up -d --build
```

#### Backend health check fails

**Symptoms:**
- `/health` endpoint returns errors
- Container is running but not responsive

**Solutions:**
```bash
# Check if backend is actually running
curl http://localhost:8000/health

# Check container logs
docker-compose -f backend/docker-compose.yml logs --tail=100

# Check Chroma DB
docker-compose -f backend/docker-compose.yml exec backend ls -la /app/data/chroma_db

# Restart container
docker-compose -f backend/docker-compose.yml restart
```

#### Slow responses

**Symptoms:**
- API calls take >5 seconds
- Timeouts

**Solutions:**
```bash
# Check container resources
docker stats

# Check API key limits (Anthropic/OpenAI)
# Review usage in console

# Reduce chunk count in retrieval
# Edit backend/src/rag_pipeline.py

# Check Chroma DB size
du -sh backend/data/chroma_db
```

### Frontend Issues

#### Frontend not loading

**Symptoms:**
- Blank page
- 404 errors

**Solutions:**
```bash
# Check if files exist
ls -la /var/www/chemistry-ai/frontend/

# Check nginx is serving correctly
curl -I https://yourdomain.com

# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Rebuild and redeploy
cd frontend
npm run build
sudo cp -r dist/* /var/www/chemistry-ai/frontend/
```

#### API calls failing from frontend

**Symptoms:**
- Network errors in browser console
- CORS errors

**Solutions:**
```bash
# 1. Check CORS settings
# Edit backend/src/main.py
# Ensure ALLOWED_ORIGINS includes your domain

# 2. Check nginx proxy
sudo nginx -t
sudo tail -f /var/log/nginx/error.log

# 3. Check backend is accessible
curl http://localhost:8000/health

# 4. Check environment variable
grep "VITE_API_ENDPOINT" frontend/.env
# Should match your domain
```

#### Build fails

**Symptoms:**
- `npm run build` errors
- TypeScript errors

**Solutions:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+

# Check for TypeScript errors
npm run build -- --mode development
```

### Nginx Issues

#### Nginx won't start

**Symptoms:**
- `systemctl start nginx` fails
- Configuration test fails

**Solutions:**
```bash
# Test configuration
sudo nginx -t

# Common errors:
# 1. SSL certificate not found
sudo certbot certificates
# Get certificate: sudo certbot --nginx -d yourdomain.com

# 2. Port 80/443 already in use
sudo lsof -i :80
sudo lsof -i :443

# 3. Syntax error in config
sudo nano /etc/nginx/sites-available/chemistry-ai
# Check for typos, missing semicolons

# Reload after fixes
sudo systemctl restart nginx
```

#### 502 Bad Gateway

**Symptoms:**
- Frontend loads but API calls fail
- Nginx returns 502

**Solutions:**
```bash
# Backend not running
docker-compose -f backend/docker-compose.yml ps
docker-compose -f backend/docker-compose.yml up -d

# Backend not accessible from nginx
curl http://localhost:8000/health

# Nginx proxy misconfigured
sudo nano /etc/nginx/sites-available/chemistry-ai
# Check proxy_pass http://localhost:8000

# SELinux blocking (if enabled)
sudo setsebool -P httpd_can_network_connect 1
```

#### SSL Certificate Issues

**Symptoms:**
- Browser shows "Not Secure"
- Certificate expired warnings

**Solutions:**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew --nginx

# Force renewal (if close to expiry)
sudo certbot renew --force-renewal --nginx

# Check auto-renewal is enabled
sudo systemctl status certbot.timer

# Enable if not running
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Docker Issues

#### Docker daemon not running

**Symptoms:**
- `docker: command not found`
- `Cannot connect to Docker daemon`

**Solutions:**
```bash
# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Check status
sudo systemctl status docker

# Check user permissions
sudo usermod -aG docker $USER
# Log out and back in
```

#### Disk space full

**Symptoms:**
- Deployments fail
- Docker build errors

**Solutions:**
```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a
docker volume prune

# Clean old backups
rm ~/backups/chemistry-ai/chemistry-ai-backup-old*.tar.gz

# Clean logs
sudo truncate -s 0 /var/log/nginx/access.log
sudo truncate -s 0 /var/log/nginx/error.log
```

### Database Issues

#### Chroma DB corrupted

**Symptoms:**
- Backend crashes on startup
- Search returns no results

**Solutions:**
```bash
# Restore from backup
./scripts/restore.sh ~/backups/chemistry-ai/chemistry-ai-backup-LATEST.tar.gz

# Or rebuild database
docker-compose -f backend/docker-compose.yml down
rm -rf backend/data/chroma_db/*
docker-compose -f backend/docker-compose.yml up -d
# Re-run ingestion
python backend/src/ingest.py
```

### Performance Issues

#### High memory usage

**Solutions:**
```bash
# Check what's using memory
htop

# Restart Docker containers
docker-compose -f backend/docker-compose.yml restart

# Limit Docker memory (edit docker-compose.yml)
services:
  backend:
    mem_limit: 2g
```

#### High CPU usage

**Solutions:**
```bash
# Check processes
top

# Check backend load
docker stats

# Review Chroma DB queries
# May need to optimize chunking strategy
```

### Deployment Issues

#### Git pull fails

**Solutions:**
```bash
# Uncommitted changes
git stash
git pull
git stash pop

# Merge conflicts
git reset --hard origin/main
```

#### Permission denied

**Solutions:**
```bash
# Docker permission
sudo chmod 666 /var/run/docker.sock

# File permissions
sudo chown -R $USER:$USER ~/icelandic-chemistry-ai-tutor

# Nginx directory
sudo chown -R $USER:$USER /var/www/chemistry-ai
```

## Getting More Help

### Enable Debug Logging

Backend:
```bash
# Edit backend/.env
LOG_LEVEL=DEBUG

# Restart
docker-compose -f backend/docker-compose.yml restart
```

### Collect Diagnostic Info
```bash
# System info
uname -a
docker --version
docker-compose --version
nginx -v

# Service status
sudo systemctl status nginx
docker-compose -f backend/docker-compose.yml ps

# Logs
docker-compose -f backend/docker-compose.yml logs --tail=100 > backend-logs.txt
sudo tail -100 /var/log/nginx/error.log > nginx-logs.txt

# Disk space
df -h > disk-usage.txt
```

### Contact Support

Include:
1. Error message
2. Steps to reproduce
3. Diagnostic logs
4. What you've already tried

## Prevention

### Regular Maintenance
```bash
# Weekly
./scripts/backup.sh
sudo apt-get update && sudo apt-get upgrade -y
docker system prune

# Monthly
sudo certbot renew
# Review and clean old logs
# Check disk space
```

### Monitoring

Set up health monitoring:
```bash
nohup python3 monitoring/health_check.py &
```

### Automated Backups

Add to crontab:
```bash
0 2 * * * /home/USER/icelandic-chemistry-ai-tutor/scripts/backup.sh
```
