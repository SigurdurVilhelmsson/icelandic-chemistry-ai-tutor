#!/bin/bash
# Build frontend and deploy to nginx
# Run from project root: ./scripts/build_and_deploy.sh

set -e

echo "================================================"
echo "  Chemistry AI Tutor - Build & Deploy Frontend"
echo "================================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check if frontend directory exists
if [ ! -d "$PROJECT_DIR/frontend" ]; then
    echo "❌ Error: frontend directory not found at $PROJECT_DIR/frontend"
    exit 1
fi

# Build frontend
echo "📦 Installing frontend dependencies..."
cd "$PROJECT_DIR/frontend"
npm install

echo "🔨 Building frontend..."
npm run build

# Check if build was successful
if [ ! -d "$PROJECT_DIR/frontend/dist" ]; then
    echo "❌ Error: Build failed - dist directory not found"
    exit 1
fi

# Deploy to nginx directory
echo "📤 Deploying to nginx directory..."
sudo cp -r dist/* /var/www/chemistry-ai/frontend/dist/

# Set proper permissions
echo "🔐 Setting permissions..."
sudo chown -R www-data:www-data /var/www/chemistry-ai/frontend/dist

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
sudo nginx -t

# Reload nginx
echo "🔄 Reloading nginx..."
sudo systemctl reload nginx

# Check nginx status
if sudo systemctl is-active --quiet nginx; then
    echo ""
    echo "✅ Frontend deployed successfully!"
    echo ""
    echo "================================================"
    echo "  Deployment Complete"
    echo "================================================"
    echo ""
    echo "Your application should now be available at:"
    echo "  https://your-domain.com"
    echo ""
    echo "Check logs:"
    echo "  sudo tail -f /var/log/nginx/chemistry-ai-access.log"
    echo "  sudo tail -f /var/log/nginx/chemistry-ai-error.log"
    echo ""
else
    echo "⚠️  Warning: nginx is not running"
    echo "Start nginx with: sudo systemctl start nginx"
fi
