# Kvenno.app Deployment Guide - AI Tutor App

This document explains how to deploy the AI Chemistry Tutor to multiple paths on kvenno.app following the unified site structure.

## Deployment Paths

This app is deployed to **three locations** on kvenno.app:

- `/1-ar/ai-tutor/` - 1st year chemistry
- `/2-ar/ai-tutor/` - 2nd year chemistry
- `/3-ar/ai-tutor/` - 3rd year chemistry

Each deployment uses the same codebase but with different base paths configured.

## Building for Each Path

### 1st Year Deployment

```bash
# Set base path for 1st year
export VITE_BASE_PATH=/1-ar/ai-tutor/

# Build
npm run build

# Copy to server
scp -r dist/* user@server:/var/www/kvenno.app/1-ar/ai-tutor/
```

### 2nd Year Deployment

```bash
# Set base path for 2nd year
export VITE_BASE_PATH=/2-ar/ai-tutor/

# Build
npm run build

# Copy to server
scp -r dist/* user@server:/var/www/kvenno.app/2-ar/ai-tutor/
```

### 3rd Year Deployment

```bash
# Set base path for 3rd year
export VITE_BASE_PATH=/3-ar/ai-tutor/

# Build
npm run build

# Copy to server
scp -r dist/* user@server:/var/www/kvenno.app/3-ar/ai-tutor/
```

## Automated Deployment Script

You can use this script to deploy to all three paths automatically:

```bash
#!/bin/bash
# deploy_all_years.sh

set -e

echo "Building and deploying AI Tutor to all year paths..."

# Array of years
YEARS=("1" "2" "3")

for YEAR in "${YEARS[@]}"; do
  echo ""
  echo "=== Deploying to ${YEAR}-ar/ai-tutor/ ==="

  # Set base path
  export VITE_BASE_PATH=/${YEAR}-ar/ai-tutor/

  # Clean previous build
  rm -rf dist/

  # Build with base path
  npm run build

  # Copy to server (adjust path as needed)
  scp -r dist/* user@server:/var/www/kvenno.app/${YEAR}-ar/ai-tutor/

  echo "✓ Deployed to ${YEAR}-ar/ai-tutor/"
done

echo ""
echo "All deployments complete!"
```

Make it executable:
```bash
chmod +x deploy_all_years.sh
```

## Nginx Configuration

Your nginx configuration should route requests correctly:

```nginx
server {
    listen 80;
    server_name kvenno.app;
    root /var/www/kvenno.app;

    # 1st year AI tutor
    location /1-ar/ai-tutor/ {
        alias /var/www/kvenno.app/1-ar/ai-tutor/;
        try_files $uri $uri/ /1-ar/ai-tutor/index.html;
    }

    # 2nd year AI tutor
    location /2-ar/ai-tutor/ {
        alias /var/www/kvenno.app/2-ar/ai-tutor/;
        try_files $uri $uri/ /2-ar/ai-tutor/index.html;
    }

    # 3rd year AI tutor
    location /3-ar/ai-tutor/ {
        alias /var/www/kvenno.app/3-ar/ai-tutor/;
        try_files $uri $uri/ /3-ar/ai-tutor/index.html;
    }

    # Backend API (shared across all deployments)
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Backend Configuration

The backend is **shared** across all three deployments. It doesn't need to know which year the frontend is deployed to - the frontend handles year detection from the URL path.

### Backend API Endpoint

Make sure your `.env` file points to the correct API endpoint:

```env
VITE_API_ENDPOINT=https://kvenno.app/api
```

Or for local development:

```env
VITE_API_ENDPOINT=http://localhost:8000
```

## Year Detection

The app automatically detects which year section it's deployed to by examining the URL path:

- If path contains `/1-ar/`, shows "1. ár" in breadcrumbs and back button
- If path contains `/2-ar/`, shows "2. ár" in breadcrumbs and back button
- If path contains `/3-ar/`, shows "3. ár" in breadcrumbs and back button

This is handled in `src/utils/navigation.ts`:

```typescript
export function detectYearFromPath(): '1' | '2' | '3' | undefined {
  const path = window.location.pathname;

  if (path.includes('/1-ar/')) return '1';
  if (path.includes('/2-ar/')) return '2';
  if (path.includes('/3-ar/')) return '3';

  return undefined;
}
```

## Testing Locally

To test locally with different base paths:

```bash
# Test 1st year path
VITE_BASE_PATH=/1-ar/ai-tutor/ npm run dev

# Test 2nd year path
VITE_BASE_PATH=/2-ar/ai-tutor/ npm run dev

# Test 3rd year path
VITE_BASE_PATH=/3-ar/ai-tutor/ npm run dev
```

Then visit: `http://localhost:5173/[year]-ar/ai-tutor/`

## Verifying Deployment

After deployment, verify each path works correctly:

1. **Check navigation:**
   - Breadcrumbs show correct year
   - "Til baka" button links to correct hub
   - Site header "Kvenno Efnafræði" links to `/`

2. **Check functionality:**
   - Can send questions and receive answers
   - Sidebar opens/closes
   - Conversations save/load correctly
   - Export works

3. **Check styling:**
   - Kvenno orange color (#f36b22) throughout
   - Buttons have 8px border radius
   - Max-width of 1200px applied
   - Responsive on mobile

## Rollback

If you need to rollback a deployment:

```bash
# Restore from backup
scp -r backup/1-ar/ai-tutor/* user@server:/var/www/kvenno.app/1-ar/ai-tutor/
```

Always keep backups of working deployments!

## Notes

- Each deployment is **independent** - updating one doesn't affect the others
- They all share the **same backend API**
- Chemistry content in the backend should be filtered by year level if needed
- The app's UI and navigation automatically adapt to the deployment path

---

*Last updated: 2025-11-20*
