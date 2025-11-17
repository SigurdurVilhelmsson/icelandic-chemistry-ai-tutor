#!/bin/bash
# Deploy frontend only

set -e

echo "⚛️  Building and deploying frontend..."

cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build
echo "🔨 Building..."
npm run build

# Deploy to nginx directory
echo "📂 Deploying to nginx..."
sudo rm -rf /var/www/chemistry-ai/frontend/*
sudo cp -r dist/* /var/www/chemistry-ai/frontend/

# Reload nginx
echo "🔄 Reloading nginx..."
sudo nginx -t
sudo systemctl reload nginx

echo "✅ Frontend deployed!"
echo "Visit: https://$(hostname -f 2>/dev/null || echo 'your-domain')"
