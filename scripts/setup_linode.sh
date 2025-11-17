#!/bin/bash
# Initial Linode server setup for Chemistry AI Tutor

set -e

echo "============================================"
echo "Chemistry AI Tutor - Linode Server Setup"
echo "============================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Don't run this as root! Run as regular user with sudo access."
    exit 1
fi

echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh

echo "🔧 Installing Docker Compose..."
sudo apt-get install -y docker-compose

echo "📚 Installing additional tools..."
sudo apt-get install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    ufw \
    certbot \
    python3-certbot-nginx

echo "🔥 Configuring firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

echo "📁 Creating application directories..."
sudo mkdir -p /var/www/chemistry-ai/frontend
sudo mkdir -p /var/www/certbot
sudo chown -R $USER:$USER /var/www/chemistry-ai

echo "📂 Cloning repository..."
if [ ! -d "$HOME/icelandic-chemistry-ai-tutor" ]; then
    cd $HOME
    read -p "Enter your GitHub username: " GITHUB_USER
    git clone https://github.com/$GITHUB_USER/icelandic-chemistry-ai-tutor.git
    cd icelandic-chemistry-ai-tutor
else
    echo "Repository already exists, skipping clone."
    cd $HOME/icelandic-chemistry-ai-tutor
fi

echo "🔐 Setting up environment variables..."
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo ""
    echo "⚠️  IMPORTANT: Edit backend/.env and add your API keys:"
    echo "   nano backend/.env"
    echo ""
fi

if [ ! -f "frontend/.env" ]; then
    cp frontend/.env.example frontend/.env
    echo "⚠️  IMPORTANT: Edit frontend/.env and add your domain:"
    echo "   nano frontend/.env"
    echo ""
fi

echo "✅ Linode server setup complete!"
echo ""
echo "NEXT STEPS:"
echo "1. Edit backend/.env with API keys"
echo "2. Edit frontend/.env with your domain"
echo "3. Run: ./scripts/setup_nginx.sh"
echo "4. Run: docker-compose up -d"
echo "5. Run: ./scripts/deploy_frontend.sh"
echo "6. Get SSL certificate: sudo certbot --nginx -d yourdomain.com"
echo ""
echo "⚠️  LOG OUT AND BACK IN for Docker group membership to take effect!"
