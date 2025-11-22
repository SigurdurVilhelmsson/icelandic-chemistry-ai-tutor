#!/bin/bash
# deploy-all-paths.sh
# Deploy AI Tutor frontend to all three year paths on kvenno.app
#
# This script builds and deploys the AI Tutor frontend to:
# - /1-ar/ai-tutor/
# - /2-ar/ai-tutor/
# - /3-ar/ai-tutor/
#
# Each path requires a separate build with VITE_BASE_PATH configured

set -e

APP_NAME="ai-tutor"
PATHS=("1-ar" "2-ar" "3-ar")
SERVER_USER="${DEPLOY_USER:-siggi}"
SERVER_HOST="${DEPLOY_HOST:-your-server}"
SERVER_BASE_PATH="/var/www/kvenno.app"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AI Tutor - Multi-Path Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
  echo -e "${YELLOW}Changing to frontend directory...${NC}"
  cd frontend
fi

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
npm install

for PATH_NAME in "${PATHS[@]}"; do
  echo ""
  echo -e "${BLUE}========================================${NC}"
  echo -e "${BLUE}Building for /${PATH_NAME}/${APP_NAME}/${NC}"
  echo -e "${BLUE}========================================${NC}"

  # Set environment variables for this build
  export VITE_BASE_PATH=/${PATH_NAME}/${APP_NAME}/
  export VITE_API_ENDPOINT=https://kvenno.app

  # Clean dist directory
  echo -e "${YELLOW}🧹 Cleaning dist directory...${NC}"
  rm -rf dist

  # Build
  echo -e "${YELLOW}🔨 Building with:${NC}"
  echo -e "${YELLOW}  VITE_BASE_PATH=${VITE_BASE_PATH}${NC}"
  echo -e "${YELLOW}  VITE_API_ENDPOINT=${VITE_API_ENDPOINT}${NC}"
  npm run build

  # Verify build succeeded
  if [ ! -d "dist" ]; then
    echo -e "${RED}❌ Build failed for /${PATH_NAME}/${APP_NAME}/${NC}"
    exit 1
  fi

  # Copy to temporary directory on server
  echo -e "${YELLOW}📤 Uploading to server...${NC}"
  ssh ${SERVER_USER}@${SERVER_HOST} "mkdir -p /tmp/ai-tutor-${PATH_NAME}"
  scp -r dist/* ${SERVER_USER}@${SERVER_HOST}:/tmp/ai-tutor-${PATH_NAME}/

  # Deploy to production on server
  echo -e "${YELLOW}🚀 Deploying to production...${NC}"
  ssh ${SERVER_USER}@${SERVER_HOST} << EOF
    # Create target directory if it doesn't exist
    sudo mkdir -p ${SERVER_BASE_PATH}/${PATH_NAME}/${APP_NAME}

    # Copy files to production
    sudo cp -r /tmp/ai-tutor-${PATH_NAME}/* ${SERVER_BASE_PATH}/${PATH_NAME}/${APP_NAME}/

    # Set permissions
    sudo chown -R www-data:www-data ${SERVER_BASE_PATH}/${PATH_NAME}/${APP_NAME}/
    sudo chmod -R 755 ${SERVER_BASE_PATH}/${PATH_NAME}/${APP_NAME}/

    # Clean up temporary files
    rm -rf /tmp/ai-tutor-${PATH_NAME}
EOF

  echo -e "${GREEN}✓ Deployed to /${PATH_NAME}/${APP_NAME}/${NC}"
done

# Reload nginx
echo ""
echo -e "${YELLOW}🔄 Reloading nginx...${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} "sudo nginx -t && sudo systemctl reload nginx"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ All deployments complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Deployed to:"
for PATH_NAME in "${PATHS[@]}"; do
  echo -e "  ${BLUE}✓${NC} https://kvenno.app/${PATH_NAME}/${APP_NAME}/"
done
echo ""
echo -e "${YELLOW}Note: Make sure to test each deployment path!${NC}"
