#!/bin/bash
# Install and configure nginx on Linode
# Run with: sudo ./scripts/setup_nginx.sh

set -e

echo "================================================"
echo "  Chemistry AI Tutor - Nginx Setup"
echo "================================================"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "⚠️  This script must be run as root (use sudo)"
   exit 1
fi

# Update package list
echo "📦 Updating package list..."
apt-get update -qq

# Install nginx
echo "🔧 Installing nginx..."
apt-get install -y nginx

# Stop nginx for configuration
echo "⏸️  Stopping nginx for configuration..."
systemctl stop nginx

# Backup default config
if [ -f /etc/nginx/nginx.conf ]; then
    echo "💾 Backing up default nginx.conf..."
    cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Copy our configs
echo "📄 Copying nginx configurations..."
cp "$PROJECT_DIR/nginx/nginx.conf" /etc/nginx/nginx.conf
cp "$PROJECT_DIR/nginx/chemistry-ai.conf" /etc/nginx/sites-available/chemistry-ai

# Enable site
echo "🔗 Enabling chemistry-ai site..."
ln -sf /etc/nginx/sites-available/chemistry-ai /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Create web root
echo "📁 Creating web root directory..."
mkdir -p /var/www/chemistry-ai/frontend/dist
mkdir -p /var/www/certbot

# Set ownership (to the user who called sudo)
REAL_USER=${SUDO_USER:-$USER}
chown -R $REAL_USER:$REAL_USER /var/www/chemistry-ai

# Generate Diffie-Hellman parameters for added security
if [ ! -f /etc/nginx/dhparam.pem ]; then
    echo "🔐 Generating Diffie-Hellman parameters (this may take a few minutes)..."
    openssl dhparam -out /etc/nginx/dhparam.pem 2048
fi

# Test configuration
echo "🧪 Testing nginx configuration..."
nginx -t

# Install Certbot for SSL
echo "🔒 Installing Certbot for SSL..."
apt-get install -y certbot python3-certbot-nginx

# Enable nginx to start on boot
echo "🚀 Enabling nginx to start on boot..."
systemctl enable nginx

echo ""
echo "✅ Nginx installed and configured successfully!"
echo ""
echo "================================================"
echo "  Next Steps:"
echo "================================================"
echo ""
echo "1. Update domain in nginx config:"
echo "   sudo nano /etc/nginx/sites-available/chemistry-ai"
echo "   Replace 'your-domain.com' with your actual domain"
echo ""
echo "2. Start nginx:"
echo "   sudo systemctl start nginx"
echo ""
echo "3. Deploy backend (from project root):"
echo "   cd backend"
echo "   docker-compose up -d"
echo ""
echo "4. Build and deploy frontend (from project root):"
echo "   cd frontend"
echo "   npm install"
echo "   npm run build"
echo "   sudo cp -r dist/* /var/www/chemistry-ai/frontend/dist/"
echo ""
echo "5. Get SSL certificate:"
echo "   sudo certbot --nginx -d your-domain.com -d www.your-domain.com"
echo ""
echo "6. Enable automatic SSL renewal:"
echo "   sudo systemctl enable certbot.timer"
echo "   sudo systemctl start certbot.timer"
echo ""
echo "================================================"
