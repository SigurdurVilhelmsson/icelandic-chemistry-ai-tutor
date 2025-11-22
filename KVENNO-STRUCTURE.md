# KVENNO.APP - Unified Site Structure

This document defines the complete structure, design system, and navigation patterns for kvenno.app. **Copy this file to every repo** to give Claude Code the full context when working on individual projects.

## 1. Site Structure & URL Routing

```
kvenno.app/
├── /                           (Landing page - repo: ChemistryTools-Landing)
│
├── /1-ar/                      (1st year hub - repo: ChemistryTools-Landing)
│   ├── /1-ar/ai-tutor/         (AI Chemistry Tutor - repo: icelandic-chemistry-ai-tutor)
│   ├── /1-ar/games/            (Chemistry Games 1st yr - repo: ChemistryGames)
│   └── /1-ar/[future-tools]/   (Future expansion)
│
├── /2-ar/                      (2nd year hub - repo: ChemistryTools-Landing)
│   ├── /2-ar/lab-reports/      (Lab Reports App - repo: LabReports)
│   ├── /2-ar/ai-tutor/         (AI Chemistry Tutor - repo: icelandic-chemistry-ai-tutor)
│   ├── /2-ar/games/            (Chemistry Games 2nd yr - repo: ChemistryGames)
│   └── /2-ar/[future-tools]/   (Future expansion)
│
├── /3-ar/                      (3rd year hub - repo: ChemistryTools-Landing)
│   ├── /3-ar/lab-reports/      (Lab Reports App - repo: LabReports)
│   ├── /3-ar/ai-tutor/         (AI Chemistry Tutor - repo: icelandic-chemistry-ai-tutor)
│   ├── /3-ar/games/            (Chemistry Games 3rd yr - repo: ChemistryGames)
│   └── /3-ar/[future-tools]/   (Future expansion)
│
├── /val/                       (Elective courses hub - repo: ChemistryTools-Landing)
│   └── /val/[tools]/           (Elective tools TBD)
│
└── /f-bekkir/                  (Social sciences track - repo: ChemistryTools-Landing)
    └── /f-bekkir/[tools]/      (Social sciences tools TBD)
```

### Shared vs Year-Specific Apps

**Shared Across Years** (same repo, deployed to multiple paths):
- AI Chemistry Tutor (`icelandic-chemistry-ai-tutor`) - Used in 1st, 2nd, and 3rd year
- Lab Reports (`LabReports`) - Used in 2nd and 3rd year

**Year-Specific** (separate repos):
- Chemistry Games (`ChemistryGames`) - Different content/difficulty per year:
  - Games for 1st year → /1-ar/games/
  - Games for 2nd year → /2-ar/games/
  - Games for 3rd year → /3-ar/games/
- Landing/Hub Pages (`ChemistryTools-Landing`) - Static HTML hub pages

**Future Tools**:
- Can be either shared or year-specific depending on content
- Document in this file which approach is used for each new tool

### Deployment Strategy for Shared Apps

**CRITICAL**: Shared apps (AI Tutor, Lab Reports) require **separate builds** for each deployment path.

#### Why Multiple Builds Are Required

React apps need to know their deployment path for:
- Asset loading (JS, CSS files)
- Internal routing (React Router)
- API endpoints (relative paths)

Building once and copying to multiple locations will break routing and asset loading.

#### Building for Multiple Paths

**Lab Reports** (2 builds required):
```bash
# Build 1: For 2nd year
export VITE_BASE_PATH=/2-ar/lab-reports/
npm run build
# Deploy dist/* to /var/www/kvenno.app/2-ar/lab-reports/

# Build 2: For 3rd year
export VITE_BASE_PATH=/3-ar/lab-reports/
npm run build
# Deploy dist/* to /var/www/kvenno.app/3-ar/lab-reports/
```

**AI Tutor** (3 builds required):
```bash
# Build 1: For 1st year
export VITE_BASE_PATH=/1-ar/ai-tutor/
npm run build
# Deploy dist/* to /var/www/kvenno.app/1-ar/ai-tutor/

# Build 2: For 2nd year
export VITE_BASE_PATH=/2-ar/ai-tutor/
npm run build
# Deploy dist/* to /var/www/kvenno.app/2-ar/ai-tutor/

# Build 3: For 3rd year
export VITE_BASE_PATH=/3-ar/ai-tutor/
npm run build
# Deploy dist/* to /var/www/kvenno.app/3-ar/ai-tutor/
```

#### Automated Deployment Script

Each shared app repo should include a deployment script:

```bash
#!/bin/bash
# deploy-all-paths.sh

set -e

APP_NAME="app-name"  # e.g., "lab-reports" or "ai-tutor"
PATHS=("2-ar" "3-ar")  # Adjust for each app

for PATH in "${PATHS[@]}"; do
  echo "Building for /${PATH}/${APP_NAME}/"
  
  export VITE_BASE_PATH=/${PATH}/${APP_NAME}/
  npm run build
  
  # Copy to server (adjust as needed)
  scp -r dist/* user@server:/var/www/kvenno.app/${PATH}/${APP_NAME}/
  
  echo "✓ Deployed to /${PATH}/${APP_NAME}/"
done
```

#### Deployment Checklist for Shared Apps

Before deploying:
- [ ] Update `VITE_BASE_PATH` for each build
- [ ] Clean `dist/` directory between builds
- [ ] Verify each deployment path exists on server
- [ ] Test routing works at each deployed URL
- [ ] Check breadcrumbs show correct year
- [ ] Verify "Til baka" button links to correct hub

## 2. Authentication & Access Control

### Overview

The kvenno.app site uses a mixed access model:
- **Open access**: Landing page, hub pages, and games (no authentication required)
- **Authenticated access**: Lab Reports and AI Tutor (require Azure AD login)

### Authentication Method

**Azure AD (Microsoft Entra ID)** via the Menntaský project
- Integrated with all Icelandic secondary schools and universities
- Users authenticate with their @kvenno.is school accounts
- Implemented using Microsoft Authentication Library (MSAL) for React

### Which Apps Require Authentication

**🔒 Protected Apps:**
- Lab Reports (`/2-ar/lab-reports/`, `/3-ar/lab-reports/`)
- AI Chemistry Tutor (`/1-ar/ai-tutor/`, `/2-ar/ai-tutor/`, `/3-ar/ai-tutor/`)

**🌐 Open Access:**
- Landing page (`/`)
- All hub pages (`/1-ar/`, `/2-ar/`, `/3-ar/`, `/val/`, `/f-bekkir/`)
- All games (`/1-ar/games/`, `/2-ar/games/`, `/3-ar/games/`)

### Role-Based Access Control

**Teachers:**
- Identified by email address (maintained in `TEACHER_EMAILS` array)
- Access to teacher features in Lab Reports (grading interface)
- Future: May expand to additional management features

**Students:**
- All other @kvenno.is users
- Access to student features only
- Cannot access teacher-specific pages

### Authentication Implementation Details

**For detailed implementation instructions**, see:
- `AZURE-AD-README.md` - Start here for overview
- `AZURE-AD-IMPLEMENTATION-GUIDE.md` - Step-by-step implementation
- `AZURE-AD-CHECKLIST.md` - Track your progress
- `AZURE-AD-QUICK-REFERENCE.md` - Quick lookups while coding

**Key Technologies:**
- `@azure/msal-browser` - Core authentication library
- `@azure/msal-react` - React integration and hooks
- Client-side authentication (no backend auth server needed)
- Automatic token refresh
- Secure token storage (handled by MSAL)

**Configuration:**
```typescript
// Environment variables required (.env)
VITE_AZURE_CLIENT_ID=your-client-id
VITE_AZURE_TENANT_ID=your-tenant-id
```

**Deployment Considerations:**
- Each deployment path needs its own redirect URI registered in Azure AD
- Authentication works independently at each path
- Tokens are scoped per domain, not per path
- Multi-path builds work correctly with proper MSAL configuration

### Security Notes

⚠️ **Important Security Considerations:**

1. **Client-side role checks are for UX only**
   - Current implementation hides/shows features based on role
   - For critical operations, validate roles server-side (future enhancement)
   - Never trust client-side checks for authorization

2. **Credentials management**
   - All Azure AD credentials stored in `.env` files
   - `.env` files must be in `.gitignore`
   - Never commit actual credentials to git

3. **Token handling**
   - MSAL handles token storage securely
   - Tokens automatically refresh before expiration
   - Logout clears all tokens properly

4. **Multi-factor authentication**
   - Can be required at Azure AD level
   - Recommended for teacher accounts
   - Configure in Azure AD portal, not in app code

### Adding New Teachers

To add a new teacher:
1. Open `src/utils/roles.ts` in LabReports or AI Tutor
2. Add email to `TEACHER_EMAILS` array:
   ```typescript
   const TEACHER_EMAILS = [
     'existing.teacher@kvenno.is',
     'new.teacher@kvenno.is',  // Add here
   ];
   ```
3. Commit and redeploy the app
4. Test that new teacher can access teacher features

### Future Authentication Enhancements

**Planned improvements:**
- Move from email list to Azure AD security groups
- Server-side role validation for critical operations
- Session timeout warnings for users
- Audit logging for teacher actions
- Admin panel for teacher management

## 3. Backend API & Security

### Critical Security Requirement

⚠️ **NEVER expose API keys in frontend code!**

Both LabReports and AI Tutor need to call the Claude API, but **API keys must NOT be stored in frontend environment variables** (variables starting with `VITE_`).

**Why this is critical:**
- Vite bundles environment variables into JavaScript at build time
- `VITE_` prefixed variables are embedded in the client-side code
- Anyone can open browser DevTools and extract your API key
- Exposed keys can be stolen and rack up huge API bills
- This violates Anthropic's terms of service

### Required Backend Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │ HTTPS   │   Backend    │  HTTPS  │  Claude API │
│  (React App)├────────>│  (Node.js)   ├────────>│ (Anthropic) │
│             │         │  Port 8000   │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
                              ↓
                        API Key stored
                        securely in .env
```

**Flow:**
1. React app sends request to `/api/analyze` (your backend)
2. Backend validates request (can check authentication)
3. Backend calls Claude API with secure key
4. Backend returns response to React app

### Backend Setup on Linode Server

**Step 1: Create backend directory**

```bash
# SSH to your server
ssh siggi@server

# Create backend directory
sudo mkdir -p /var/www/kvenno.app/backend
cd /var/www/kvenno.app/backend

# Initialize Node.js project
npm init -y

# Install dependencies
npm install express @anthropic-ai/sdk cors dotenv
```

**Step 2: Create the backend server**

```bash
sudo nano /var/www/kvenno.app/backend/server.js
```

```javascript
// server.js
const express = require('express');
const Anthropic = require('@anthropic-ai/sdk');
const cors = require('cors');
require('dotenv').config();

const app = express();

// CORS configuration - only allow requests from your domain
app.use(cors({
  origin: ['https://kvenno.app', 'https://www.kvenno.app'],
  credentials: true
}));

app.use(express.json({ limit: '10mb' }));

// Initialize Anthropic client
const anthropic = new Anthropic({
  apiKey: process.env.CLAUDE_API_KEY,
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Claude API endpoint for LabReports
app.post('/api/analyze', async (req, res) => {
  try {
    const { prompt, systemPrompt, maxTokens = 4000 } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: maxTokens,
      system: systemPrompt || '',
      messages: [{ role: 'user', content: prompt }],
    });

    res.json(response);
  } catch (error) {
    console.error('Claude API error:', error);
    res.status(500).json({ 
      error: 'Failed to process request',
      message: error.message 
    });
  }
});

// Claude API endpoint for AI Tutor (streaming support if needed)
app.post('/api/chat', async (req, res) => {
  try {
    const { messages, systemPrompt, maxTokens = 2000 } = req.body;

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: 'Messages array is required' });
    }

    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: maxTokens,
      system: systemPrompt || '',
      messages: messages,
    });

    res.json(response);
  } catch (error) {
    console.error('Claude API error:', error);
    res.status(500).json({ 
      error: 'Failed to process chat request',
      message: error.message 
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

const PORT = process.env.PORT || 8000;
app.listen(PORT, '127.0.0.1', () => {
  console.log(`Backend API running on http://127.0.0.1:${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});
```

**Step 3: Create environment file with API key**

```bash
# Create .env file (NEVER commit this to git!)
sudo nano /var/www/kvenno.app/backend/.env
```

```bash
# Backend environment variables
CLAUDE_API_KEY=your-actual-claude-api-key-here
PORT=8000
NODE_ENV=production
```

```bash
# Secure the .env file
sudo chmod 600 /var/www/kvenno.app/backend/.env
sudo chown www-data:www-data /var/www/kvenno.app/backend/.env
```

**Step 4: Create systemd service to keep backend running**

```bash
sudo nano /etc/systemd/system/kvenno-backend.service
```

```ini
[Unit]
Description=Kvenno.app Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/kvenno.app/backend
Environment=NODE_ENV=production
ExecStart=/usr/bin/node /var/www/kvenno.app/backend/server.js
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=kvenno-backend

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable kvenno-backend
sudo systemctl start kvenno-backend

# Check status
sudo systemctl status kvenno-backend

# View logs
sudo journalctl -u kvenno-backend -f
```

**Step 5: Update nginx to proxy API requests**

Add this to your nginx kvenno.app server block (uncomment the existing API section):

```nginx
# Backend API proxy
location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Increase timeout for long API calls
    proxy_read_timeout 120s;
    proxy_connect_timeout 10s;
}
```

```bash
# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

### Frontend Configuration

**In React apps (LabReports, AI Tutor):**

```bash
# .env (in your LOCAL repo, for building)
VITE_API_ENDPOINT=https://kvenno.app/api

# For local development, you might use:
# VITE_API_ENDPOINT=http://localhost:8000/api
```

**Update your API utility file:**

```typescript
// src/utils/api.ts
const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT || 'https://kvenno.app/api';

export async function analyzeReport(prompt: string, systemPrompt?: string) {
  const response = await fetch(`${API_ENDPOINT}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt,
      systemPrompt,
      maxTokens: 4000,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
```

### Environment Variables Summary

**Frontend (React apps) - .env in repo root:**
```bash
# These are SAFE to be public (baked into client JavaScript)
VITE_AZURE_CLIENT_ID=public-azure-client-id
VITE_AZURE_TENANT_ID=public-azure-tenant-id
VITE_API_ENDPOINT=https://kvenno.app/api
VITE_BASE_PATH=/2-ar/lab-reports/  # Set before each build
```

**Backend (Node.js server) - .env on server only:**
```bash
# These are SECRETS (never commit, never expose)
CLAUDE_API_KEY=sk-ant-api-key-here
PORT=8000
NODE_ENV=production
```

### Security Best Practices

**DO:**
✅ Store API keys in backend `.env` file only
✅ Set restrictive file permissions (600) on `.env`
✅ Run backend as non-root user (www-data)
✅ Use CORS to restrict API access to your domain
✅ Add rate limiting to prevent abuse
✅ Monitor API usage and costs
✅ Use systemd to auto-restart backend if it crashes
✅ Log errors for debugging

**DON'T:**
❌ Never put API keys in `VITE_` environment variables
❌ Never commit `.env` files to git
❌ Never expose backend to public internet directly (use nginx proxy)
❌ Never trust frontend validation alone (validate in backend too)
❌ Never skip authentication checks in backend endpoints

### Backend Management Commands

```bash
# Start backend
sudo systemctl start kvenno-backend

# Stop backend
sudo systemctl stop kvenno-backend

# Restart backend (after code changes)
sudo systemctl restart kvenno-backend

# Check status
sudo systemctl status kvenno-backend

# View real-time logs
sudo journalctl -u kvenno-backend -f

# View recent logs
sudo journalctl -u kvenno-backend -n 100

# Update backend code
cd /var/www/kvenno.app/backend
sudo nano server.js  # Make changes
sudo systemctl restart kvenno-backend
```

### Testing the Backend

```bash
# Test health endpoint
curl https://kvenno.app/api/health

# Test from your local machine during development
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, test message"}'
```

### Troubleshooting

**Backend won't start:**
```bash
# Check logs
sudo journalctl -u kvenno-backend -n 50

# Common issues:
# - Missing dependencies: cd /var/www/kvenno.app/backend && npm install
# - Port already in use: sudo lsof -i :8000
# - Permission issues: sudo chown -R www-data:www-data /var/www/kvenno.app/backend
```

**API requests timing out:**
```bash
# Check if backend is running
sudo systemctl status kvenno-backend

# Check nginx is proxying correctly
sudo tail -f /var/log/nginx/error.log

# Increase timeout in nginx if needed (already set to 120s)
```

**High API costs:**
```bash
# Add rate limiting to backend
npm install express-rate-limit

# In server.js:
const rateLimit = require('express-rate-limit');
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api/', limiter);
```

### Future Backend Enhancements

**Planned improvements:**
- Add authentication middleware (verify Azure AD tokens)
- Add rate limiting per user (not just per IP)
- Add request logging and analytics
- Add API key rotation system
- Add backend validation of user roles
- Add caching for repeated requests
- Add request queue for high load
- Add API usage monitoring dashboard

## 4. Design System

### Brand Colors
- **Primary Orange**: `#f36b22` (Kvennaskólinn í Reykjavík brand color)
- **Background**: White or light gray (`#f5f5f5` for sections)
- **Text**: Dark gray/black (`#333333` for body text)
- **Accent/Links**: Consider darker shade of orange or complementary color

### Typography
- **Headings**: Sans-serif, bold
- **Body**: Sans-serif, regular weight
- **Specific fonts**: TBD - currently using system defaults

### Button/Tile Styling
All navigation buttons and tool tiles should use:
- Border: 2px solid #f36b22 (or filled background #f36b22 with white text)
- Border radius: 8px
- Padding: 16px 24px
- Hover state: Slightly darker shade or shadow effect
- Font size: 16-18px for buttons

### Layout Patterns
- **Maximum content width**: 1200px, centered
- **Spacing**: Consistent 16px or 24px grid
- **Responsive**: Mobile-first, stack tiles vertically on small screens

## 3. Header Component

Every page on kvenno.app must include a consistent header with:

```
┌─────────────────────────────────────────────┐
│ [Logo/Site Name]              [Admin] [Info] │
└─────────────────────────────────────────────┘
```

### Header Requirements:
- **Site name/logo**: "Efnafræðivefur Kvennó" or similar, links to `/`
- **Right-aligned buttons**: 
  - "Admin" (for teacher access)
  - "Info" (for help/about)
- **Background**: White with bottom border or subtle shadow
- **Height**: ~60px
- **Sticky**: Consider making header sticky on scroll

### Header Code Template:
```jsx
// Add to every app
<header className="site-header">
  <div className="header-content">
    <a href="/" className="site-logo">Efnafræðivefur Kvennó</a>
    <div className="header-actions">
      <button className="header-btn">Admin</button>
      <button className="header-btn">Info</button>
    </div>
  </div>
</header>
```

## 4. Navigation & Breadcrumbs

### Breadcrumb Pattern
Every sub-page must show its location in the hierarchy:

```
Heim > 1. ár > Lab Reports
```

- Always start with "Heim" (Home) linking to `/`
- Show current section (e.g., "1. ár")
- Show current app name (not linked)
- Style: Small text, gray, with > or / separators

### Back Navigation
Each app should also include a clear "Til baka" (Back) button that goes to its parent hub.

## 5. Landing Page (/)

The root landing page contains:
1. **Header** (as defined above)
2. **Intro section**: Brief welcome text about Kvennaskólinn chemistry tools
3. **Main navigation tiles**: Four large buttons/cards:
   - **1. ár** → `/1-ar/`
   - **2. ár** → `/2-ar/`
   - **3. ár** → `/3-ar/`
   - **Val** → `/val/`

### Landing Page Layout:
```
┌─────────────────────────────────┐
│          Header                  │
├─────────────────────────────────┤
│                                  │
│  Welcome to Kvenno Chemistry     │
│  [Intro paragraph]               │
│                                  │
│  ┌──────────┐  ┌──────────┐    │
│  │  1. ár   │  │  2. ár   │    │
│  └──────────┘  └──────────┘    │
│                                  │
│  ┌──────────┐  ┌──────────┐    │
│  │  3. ár   │  │   Val    │    │
│  └──────────┘  └──────────┘    │
│                                  │
└─────────────────────────────────┘
```

## 6. Year/Section Hub Pages

Each hub page (1.ár, 2.ár, 3.ár, Val) has:
1. **Header** (consistent)
2. **Breadcrumbs**: `Heim > [Section Name]`
3. **Section title**: e.g., "1. árs verkfæri"
4. **Tool tiles**: Grid of available apps/tools
5. **Future expansion space**: Placeholder tiles for upcoming tools

### Tool Tile Structure:
Each tool tile should display:
- Icon or image (optional)
- Tool name (e.g., "Lab Reports")
- Brief description (1-2 sentences)
- Click → Navigate to tool

## 7. Individual App Pages

Each app (Lab Reports, AI Tutor, etc.) must include:

1. **Header** (consistent across site)
2. **Breadcrumbs**: `Heim > [Section] > [App Name]`
3. **App-specific content**
4. **Footer with navigation**: Link back to hub and home

### App Deployment:
- Each app is a separate React build
- Deployed to its designated path (e.g., `/1-ar/lab-reports/`)
- Uses `basename` in React Router if needed
- Must handle its own routing within its path

## 8. This App's Details

> **NOTE**: Update this section for each repo

- **Repo Name**: [e.g., lab-reports-app]
- **Deployed To**: [e.g., /1-ar/lab-reports/]
- **Purpose**: [Brief description of what this app does]
- **Current Status**: [In development / Deployed / Planning]

## 9. Deployment Notes

### Repository Structure on GitHub

**ChemistryTools-Landing** (Static HTML):
```
ChemistryTools-Landing/
├── index.html              # Landing page
├── styles.css              # Landing page styles
├── KVENNO-STRUCTURE.md
├── README.md
├── 1-ar/
│   └── index.html         # 1st year hub page
├── 2-ar/
│   └── index.html         # 2nd year hub page
├── 3-ar/
│   └── index.html         # 3rd year hub page
├── val/
│   └── index.html         # Electives hub page
├── f-bekkir/
│   └── index.html         # Social sciences hub page
└── media/                  # Favicon, images, etc.
```

**ChemistryGames** (Static HTML):
```
ChemistryGames/
├── KVENNO-STRUCTURE.md
├── README.md
├── 1-ar/
│   ├── index.html         # Games hub for 1st year
│   └── einingagreining.html  # Individual game files
├── 2-ar/
│   └── index.html
└── 3-ar/
    └── index.html
```

**LabReports** (React/Vite):
```
LabReports/
├── src/                    # React source code
├── api/                    # Serverless functions
├── KVENNO-STRUCTURE.md
├── DEPLOYMENT.md
├── package.json
├── vite.config.ts
└── ... (standard Vite structure)
```

**icelandic-chemistry-ai-tutor** (React/Vite):
```
icelandic-chemistry-ai-tutor/
├── src/                    # React source code
├── KVENNO-STRUCTURE.md
├── DEPLOYMENT.md
├── package.json
├── vite.config.ts
└── ... (standard Vite structure)
```

### Deployment Workflow

**Step 1: Deploy ChemistryTools-Landing**
```bash
# On local machine with WSL
cd ChemistryTools-Landing

# Copy entire structure to server
scp -r * siggi@server:/tmp/landing-deploy/

# SSH to server
ssh siggi@server

# Copy to production
sudo cp -r /tmp/landing-deploy/* /var/www/kvenno.app/
sudo chown -R www-data:www-data /var/www/kvenno.app/
sudo chmod -R 755 /var/www/kvenno.app/

# Clean up
rm -rf /tmp/landing-deploy/
```

**Step 2: Deploy ChemistryGames**
```bash
# On local machine
cd ChemistryGames

# Copy each year's games
scp -r 1-ar/* siggi@server:/tmp/games-1ar/
scp -r 2-ar/* siggi@server:/tmp/games-2ar/
scp -r 3-ar/* siggi@server:/tmp/games-3ar/

# SSH to server
ssh siggi@server

# Copy to production
sudo cp -r /tmp/games-1ar/* /var/www/kvenno.app/1-ar/games/
sudo cp -r /tmp/games-2ar/* /var/www/kvenno.app/2-ar/games/
sudo cp -r /tmp/games-3ar/* /var/www/kvenno.app/3-ar/games/

sudo chown -R www-data:www-data /var/www/kvenno.app/*/games/
sudo chmod -R 755 /var/www/kvenno.app/*/games/

# Clean up
rm -rf /tmp/games-*
```

**Step 3: Deploy LabReports** (2 builds)
```bash
# On local machine
cd LabReports

# Build for 2nd year
export VITE_BASE_PATH=/2-ar/lab-reports/
npm run build

# Copy to server
scp -r dist/* siggi@server:/tmp/lab-reports-2ar/

# Build for 3rd year
export VITE_BASE_PATH=/3-ar/lab-reports/
npm run build

# Copy to server
scp -r dist/* siggi@server:/tmp/lab-reports-3ar/

# SSH to server
ssh siggi@server

# Deploy to production
sudo mkdir -p /var/www/kvenno.app/2-ar/lab-reports
sudo mkdir -p /var/www/kvenno.app/3-ar/lab-reports

sudo cp -r /tmp/lab-reports-2ar/* /var/www/kvenno.app/2-ar/lab-reports/
sudo cp -r /tmp/lab-reports-3ar/* /var/www/kvenno.app/3-ar/lab-reports/

sudo chown -R www-data:www-data /var/www/kvenno.app/*/lab-reports/
sudo chmod -R 755 /var/www/kvenno.app/*/lab-reports/

# Clean up
rm -rf /tmp/lab-reports-*
```

**Step 4: Deploy AI Tutor** (3 builds)
```bash
# On local machine
cd icelandic-chemistry-ai-tutor

# Build for 1st year
export VITE_BASE_PATH=/1-ar/ai-tutor/
npm run build
scp -r dist/* siggi@server:/tmp/ai-tutor-1ar/

# Build for 2nd year
export VITE_BASE_PATH=/2-ar/ai-tutor/
npm run build
scp -r dist/* siggi@server:/tmp/ai-tutor-2ar/

# Build for 3rd year
export VITE_BASE_PATH=/3-ar/ai-tutor/
npm run build
scp -r dist/* siggi@server:/tmp/ai-tutor-3ar/

# SSH to server
ssh siggi@server

# Deploy to production
sudo mkdir -p /var/www/kvenno.app/1-ar/ai-tutor
sudo mkdir -p /var/www/kvenno.app/2-ar/ai-tutor
sudo mkdir -p /var/www/kvenno.app/3-ar/ai-tutor

sudo cp -r /tmp/ai-tutor-1ar/* /var/www/kvenno.app/1-ar/ai-tutor/
sudo cp -r /tmp/ai-tutor-2ar/* /var/www/kvenno.app/2-ar/ai-tutor/
sudo cp -r /tmp/ai-tutor-3ar/* /var/www/kvenno.app/3-ar/ai-tutor/

sudo chown -R www-data:www-data /var/www/kvenno.app/*/ai-tutor/
sudo chmod -R 755 /var/www/kvenno.app/*/ai-tutor/

# Clean up
rm -rf /tmp/ai-tutor-*
```

### Final Server Directory Structure

After all deployments:
```
/var/www/kvenno.app/
├── index.html                      # Landing page
├── styles.css
├── media/
│
├── 1-ar/
│   ├── index.html                  # Hub page (static)
│   ├── games/
│   │   ├── index.html              # Games hub (static)
│   │   └── *.html                  # Game files (static)
│   └── ai-tutor/
│       └── [React build]           # AI Tutor (build 1)
│
├── 2-ar/
│   ├── index.html                  # Hub page (static)
│   ├── games/
│   │   ├── index.html              # Games hub (static)
│   │   └── *.html                  # Game files (static)
│   ├── lab-reports/
│   │   └── [React build]           # Lab Reports (build 1)
│   └── ai-tutor/
│       └── [React build]           # AI Tutor (build 2)
│
└── 3-ar/
    ├── index.html                  # Hub page (static)
    ├── games/
    │   ├── index.html              # Games hub (static)
    │   └── *.html                  # Game files (static)
    ├── lab-reports/
    │   └── [React build]           # Lab Reports (build 2)
    └── ai-tutor/
        └── [React build]           # AI Tutor (build 3)
```

### Server Setup (nginx)
- All apps served from `/var/www/kvenno.app/`
- nginx configuration handles routing to correct directories
- Each React app built with `npm run build`
- Build outputs copied to appropriate subdirectories

### Build Commands:
```bash
npm run build
# Then copy build/* to /var/www/kvenno.app/[app-path]/
```

### Environment Variables:
Each app may need:
- `PUBLIC_URL` or `basename` for correct routing
- API endpoints if calling backend services
- Authentication tokens

## 10. Development Workflow with Claude Code

When working on any repo with Claude Code:

1. **Always start with**: "Read KVENNO-STRUCTURE.md first"
2. **Reference design system**: Use #f36b22, consistent button styles
3. **Include header**: Copy header component into your app
4. **Test navigation**: Make sure links work correctly
5. **Breadcrumbs**: Add appropriate breadcrumb trail
6. **Responsive**: Test on mobile sizes

### Updating This File:
When you make design decisions or structural changes:
1. Update KVENNO-STRUCTURE.md in one repo
2. Copy the updated file to all other repos
3. Ask Claude Code in each repo: "Review KVENNO-STRUCTURE.md and update this app to match current standards"

## 11. Icelandic Language

All user-facing text must be in Icelandic:
- "Heim" not "Home"
- "Til baka" not "Back"
- "Verkfæri" not "Tools"
- Consistent terminology across all apps

## 12. Authentication & Access Control

Some apps require teacher authentication:
- Lab Reports app: Teacher grading interface
- Future admin features

**Consistent login approach**:
- School Google account SSO (preferred)
- Backend handles authentication
- JWT tokens for session management
- Clear visual indication of login status

---

## Quick Reference

**Primary Color**: #f36b22  
**Max Width**: 1200px  
**Header Height**: ~60px  
**Button Radius**: 8px  

**Key Links**:
- Home: `/`
- 1st Year: `/1-ar/`
- 2nd Year: `/2-ar/`
- 3rd Year: `/3-ar/`
- Electives: `/val/`

---

*Last updated: 2025-11-22*  
*Maintainer: Sigurður E. Vilhelmsson, Kvennaskólinn í Reykjavík*
