#!/bin/bash
# Install and configure nginx

set -e

echo "🌐 Setting up nginx..."

# Install nginx
sudo apt-get update
sudo apt-get install -y nginx

# Stop nginx for configuration
sudo systemctl stop nginx

# Backup default config
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d)

# Copy our configs
sudo cp nginx/nginx.conf /etc/nginx/nginx.conf
sudo cp nginx/chemistry-ai.conf /etc/nginx/sites-available/chemistry-ai

# Prompt for domain
read -p "Enter your domain (or press Enter for localhost testing): " DOMAIN

if [ -n "$DOMAIN" ]; then
    # Replace placeholder with actual domain
    sudo sed -i "s/server_name _;/server_name $DOMAIN www.$DOMAIN;/g" /etc/nginx/sites-available/chemistry-ai
    sudo sed -i "s|/etc/letsencrypt/live/DOMAIN|/etc/letsencrypt/live/$DOMAIN|g" /etc/nginx/sites-available/chemistry-ai
    echo "✅ Configured for domain: $DOMAIN"
else
    echo "⚠️  Using default configuration (localhost testing)"
fi

# Enable site
sudo ln -sf /etc/nginx/sites-available/chemistry-ai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Create certbot directory
sudo mkdir -p /var/www/certbot

# Test configuration
echo "🔍 Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    sudo systemctl start nginx
    sudo systemctl enable nginx
    echo "✅ Nginx installed and running"
else
    echo "❌ Nginx configuration has errors"
    exit 1
fi

echo ""
echo "NEXT STEPS:"
if [ -n "$DOMAIN" ]; then
    echo "1. Ensure DNS points to this server"
    echo "2. Get SSL certificate: sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
    echo "3. Enable auto-renewal: sudo systemctl enable certbot.timer"
fi
echo "4. Deploy application: ./scripts/complete_deploy.sh"
