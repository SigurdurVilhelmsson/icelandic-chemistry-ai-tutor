#!/bin/bash
# Deploy backend only

set -e

echo "🐍 Deploying backend..."

cd backend

# Pull latest code (if needed)
git pull origin main 2>/dev/null || true

# Rebuild and restart containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for health check
echo "⏳ Waiting for backend to be healthy..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health &>/dev/null; then
        echo "✅ Backend is healthy!"
        docker-compose logs --tail=20
        exit 0
    fi
    echo "Attempt $i/30..."
    sleep 2
done

echo "❌ Backend health check failed!"
echo "Logs:"
docker-compose logs --tail=50
exit 1
