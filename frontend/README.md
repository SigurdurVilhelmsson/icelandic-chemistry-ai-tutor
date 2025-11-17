# Icelandic Chemistry AI Tutor - Frontend

React frontend with Vercel serverless API bridge to Python backend.

## Quick Start

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your backend URL

# Start development server
npm run dev
# or use Vercel CLI for more accurate local testing
npm run vercel-dev

# Run tests
npm test

# Build for production
npm run build
```

## Project Structure

```
frontend/
├── api/                      # Vercel Serverless Functions
│   ├── chat.ts              # Main chat endpoint
│   ├── health.ts            # Health check endpoint
│   ├── _middleware.ts       # CORS and rate limiting
│   └── _tests/              # API tests
│       ├── chat.test.ts
│       ├── health.test.ts
│       └── vitest.config.ts
├── src/                      # React application (to be implemented)
├── vercel.json              # Vercel configuration
├── package.json             # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
└── .env.example             # Environment variables template
```

## API Endpoints

### POST /api/chat
Main endpoint for chemistry questions.

**Request:**
```json
{
  "question": "Hvað er efnafræði?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "answer": "Efnafræði er vísindi um...",
  "session_id": "abc123"
}
```

### GET /api/health
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-17T12:00:00.000Z"
}
```

## Environment Variables

Required environment variables (set in Vercel Dashboard or `.env.local`):

- `PYTHON_BACKEND_URL` - URL of Python backend on Linode
- `NODE_ENV` - Environment mode (development/production)

## Testing

```bash
# Run all tests
npm test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

## Deployment

### Automatic (GitHub Integration)

Push to main branch:
```bash
git push origin main
```

Vercel automatically builds and deploys.

### Manual

```bash
# Deploy to production
npm run deploy

# Or using Vercel CLI
vercel --prod
```

## Documentation

See [API_INTEGRATION.md](../API_INTEGRATION.md) for comprehensive documentation on:
- Architecture overview
- How serverless functions work
- Environment setup
- Local development
- Testing
- Deployment
- Monitoring
- Troubleshooting

## Development

### Local Development with Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Start development server
vercel dev
```

This provides the most accurate local development experience, simulating Vercel's production environment.

### Testing API Locally

```bash
# Health check
curl http://localhost:3000/api/health

# Chat endpoint
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Hvað er efnafræði?"}'
```

## Features

- ✅ TypeScript support
- ✅ Serverless API functions
- ✅ CORS handling
- ✅ Rate limiting
- ✅ Request validation
- ✅ Error handling (Icelandic messages)
- ✅ Timeout management
- ✅ Comprehensive testing
- ✅ Health monitoring
- ✅ Production-ready configuration

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript
- **Testing**: Vitest
- **Deployment**: Vercel
- **API**: Vercel Serverless Functions

## License

See LICENSE file in root directory.
