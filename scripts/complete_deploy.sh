#!/bin/bash
# Complete deployment with all checks

set -e

echo "============================================"
echo "Chemistry AI Tutor - Complete Deployment"
echo "============================================"
echo ""

# Pre-flight checks
echo "🔍 Pre-flight checks..."

# Check if backend env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ backend/.env not found!"
    echo "Copy from backend/.env.example and configure"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running!"
    exit 1
fi

# Check if nginx is running
if ! sudo systemctl is-active --quiet nginx; then
    echo "❌ Nginx is not running!"
    exit 1
fi

echo "✅ Pre-flight checks passed"
echo ""

# Deploy
./scripts/deploy.sh

# Final health checks
echo ""
echo "🏥 Final health checks..."

# Backend health
if curl -f http://localhost:8000/health &>/dev/null; then
    echo "✅ Backend healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi

# Frontend health (check if index.html exists)
if [ -f "/var/www/chemistry-ai/frontend/index.html" ]; then
    echo "✅ Frontend deployed"
else
    echo "❌ Frontend files not found"
    exit 1
fi

# Nginx config valid
if sudo nginx -t &>/dev/null; then
    echo "✅ Nginx configuration valid"
else
    echo "❌ Nginx configuration invalid"
    exit 1
fi

echo ""
echo "============================================"
echo "✅ DEPLOYMENT SUCCESSFUL"
echo "============================================"
echo ""
echo "Your application is ready!"
echo ""
echo "Next steps:"
echo "1. Visit your site and test functionality"
echo "2. Monitor logs: docker-compose -f backend/docker-compose.yml logs -f"
echo "3. Set up automated backups: Add to crontab:"
echo "   0 2 * * * $PWD/scripts/backup.sh"
echo "4. Set up SSL renewal: sudo systemctl enable certbot.timer"
