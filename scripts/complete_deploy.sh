#!/bin/bash
# Complete deployment script - deploys both backend and frontend
# Run from project root: ./scripts/complete_deploy.sh

set -e

echo "================================================"
echo "  Chemistry AI Tutor - Complete Deployment"
echo "================================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Step 1: Pull latest code (optional - uncomment if using git)
# echo "📥 Pulling latest code..."
# cd "$PROJECT_DIR"
# git pull origin main
# print_status "Code updated"
# echo ""

# Step 2: Build and deploy backend
echo "🐍 Deploying backend..."
cd "$PROJECT_DIR/backend"

if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found in backend directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Make sure to create one with required API keys"
fi

# Stop existing containers
echo "  Stopping existing containers..."
docker-compose down

# Build new images
echo "  Building new images..."
docker-compose build

# Start containers
echo "  Starting containers..."
docker-compose up -d

print_status "Backend deployed"
echo ""

# Wait for backend to be healthy
echo "⏳ Waiting for backend to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Backend is healthy"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Attempt $RETRY_COUNT/$MAX_RETRIES - waiting..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_error "Backend health check failed after $MAX_RETRIES attempts"
    echo ""
    echo "Check backend logs with: docker-compose logs"
    exit 1
fi
echo ""

# Step 3: Build and deploy frontend
echo "⚛️  Building frontend..."
cd "$PROJECT_DIR/frontend"

if [ ! -f "package.json" ]; then
    print_error "package.json not found in frontend directory"
    exit 1
fi

echo "  Installing dependencies..."
npm install

echo "  Building production bundle..."
npm run build

if [ ! -d "dist" ]; then
    print_error "Build failed - dist directory not found"
    exit 1
fi

print_status "Frontend built successfully"
echo ""

# Deploy to nginx
echo "📦 Deploying frontend to nginx..."
sudo cp -r dist/* /var/www/chemistry-ai/frontend/dist/
sudo chown -R www-data:www-data /var/www/chemistry-ai/frontend/dist
print_status "Frontend deployed"
echo ""

# Step 4: Test and reload nginx
echo "🧪 Testing nginx configuration..."
if sudo nginx -t > /dev/null 2>&1; then
    print_status "Nginx configuration valid"
else
    print_error "Nginx configuration test failed"
    sudo nginx -t
    exit 1
fi
echo ""

echo "🔄 Reloading nginx..."
sudo systemctl reload nginx
print_status "Nginx reloaded"
echo ""

# Step 5: Final health check
echo "🏥 Running final health checks..."

# Check backend
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Backend health check passed"
else
    print_warning "Backend health check failed"
fi

# Check nginx
if sudo systemctl is-active --quiet nginx; then
    print_status "Nginx is running"
else
    print_error "Nginx is not running"
fi

# Check if port 443 is listening
if sudo netstat -tuln | grep -q ":443 "; then
    print_status "HTTPS port 443 is listening"
elif sudo ss -tuln | grep -q ":443 "; then
    print_status "HTTPS port 443 is listening"
else
    print_warning "HTTPS port 443 is not listening - SSL may not be configured"
fi

echo ""
echo "================================================"
echo "  Deployment Complete!"
echo "================================================"
echo ""
echo "Your application should be available at:"
echo "  https://your-domain.com"
echo ""
echo "Useful commands:"
echo "  Backend logs:    docker-compose logs -f"
echo "  Nginx access:    sudo tail -f /var/log/nginx/chemistry-ai-access.log"
echo "  Nginx errors:    sudo tail -f /var/log/nginx/chemistry-ai-error.log"
echo "  Backend status:  docker-compose ps"
echo "  Nginx status:    sudo systemctl status nginx"
echo ""
echo "================================================"
