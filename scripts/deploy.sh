#!/bin/bash
# Deploy both backend and frontend

set -e

echo "🚀 Deploying Chemistry AI Tutor..."

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Deploy backend
echo ""
echo "========================================="
echo "BACKEND DEPLOYMENT"
echo "========================================="
./scripts/deploy_backend.sh

# Deploy frontend
echo ""
echo "========================================="
echo "FRONTEND DEPLOYMENT"
echo "========================================="
./scripts/deploy_frontend.sh

echo ""
echo "========================================="
echo "✅ DEPLOYMENT COMPLETE"
echo "========================================="
echo ""
echo "Services:"
echo "  Frontend: https://$(hostname -f 2>/dev/null || echo 'your-domain')"
echo "  Backend: http://localhost:8000"
echo "  Health: https://$(hostname -f 2>/dev/null || echo 'your-domain')/health"
echo ""
echo "Logs:"
echo "  Backend: docker-compose -f backend/docker-compose.yml logs -f"
echo "  Nginx: sudo tail -f /var/log/nginx/access.log"
