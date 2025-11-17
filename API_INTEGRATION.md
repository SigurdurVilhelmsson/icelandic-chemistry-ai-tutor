# API Integration Guide

## Icelandic Chemistry AI Tutor - Vercel Serverless API Bridge

This document explains how the Vercel serverless API bridge works, connecting the React frontend (hosted on Vercel) with the Python backend (hosted on Linode).

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [How Serverless Functions Work](#how-serverless-functions-work)
3. [API Endpoints](#api-endpoints)
4. [Environment Setup](#environment-setup)
5. [Local Development](#local-development)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)
10. [Production Best Practices](#production-best-practices)

---

## Architecture Overview

```
┌─────────────────┐      ┌──────────────────────┐      ┌─────────────────┐
│                 │      │                      │      │                 │
│  React Frontend │─────▶│  Vercel Serverless   │─────▶│  Python Backend │
│  (Vercel)       │      │  Functions (Bridge)  │      │  (Linode)       │
│                 │◀─────│                      │◀─────│                 │
└─────────────────┘      └──────────────────────┘      └─────────────────┘
```

### Why This Architecture?

1. **Separation of Concerns**: Frontend and backend can be developed, deployed, and scaled independently
2. **Edge Computing**: Vercel's serverless functions run at the edge, close to users
3. **Cost Efficiency**: Only pay for actual usage (no idle server costs)
4. **Scalability**: Automatic scaling based on traffic
5. **Security**: Backend URL and credentials not exposed to frontend

---

## How Serverless Functions Work

### What Are Serverless Functions?

Serverless functions are event-driven code snippets that:
- Run in isolated containers
- Start only when invoked (cold start)
- Scale automatically
- Shut down after execution

### Vercel Serverless Functions

- **Location**: `/frontend/api/*.ts` files automatically become API endpoints
- **URL Mapping**: `/api/chat.ts` → `https://your-domain.vercel.app/api/chat`
- **Runtime**: Node.js (supports TypeScript)
- **Timeout**: Configurable (30s for chat, 5s for health)
- **Memory**: Configurable (1024MB for chat, 256MB for health)

### Request Flow

1. User sends request to `https://your-domain.vercel.app/api/chat`
2. Vercel Edge Middleware processes CORS and rate limiting
3. Request routed to appropriate serverless function
4. Function forwards request to Python backend on Linode
5. Backend processes request and returns response
6. Function returns response to user

---

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

**Response (Success):**
```json
{
  "answer": "Efnafræði er vísindi um...",
  "session_id": "abc123"
}
```

**Response (Error):**
```json
{
  "error": "Villa kom upp, reyndu aftur"
}
```

**Error Codes:**
- `400` - Invalid request (Ógild spurning)
- `405` - Method not allowed
- `429` - Rate limit exceeded (Of margar beiðnir, bíddu aðeins)
- `500` - Server error (Villa kom upp, reyndu aftur)
- `503` - Backend unavailable (Ekki tókst að tengjast)
- `504` - Timeout (Beiðni tók of langan tíma)

**Features:**
- 30-second timeout
- Request validation
- Automatic retry on network errors
- Comprehensive error handling

---

### GET /api/health

Health check endpoint for monitoring.

**Response (Healthy):**
```json
{
  "status": "ok",
  "timestamp": "2025-11-17T12:00:00.000Z",
  "backend": {
    "status": "ok",
    "version": "1.0.0"
  }
}
```

**Response (Unhealthy):**
```json
{
  "status": "error",
  "message": "Backend unavailable",
  "timestamp": "2025-11-17T12:00:00.000Z"
}
```

**Features:**
- 5-second timeout
- Backend connectivity check
- Timestamp for monitoring
- Works with any HTTP method

---

## Environment Setup

### Required Environment Variables

Set these in Vercel Dashboard (Settings → Environment Variables):

| Variable | Value | Description |
|----------|-------|-------------|
| `PYTHON_BACKEND_URL` | `https://your-linode-server.com` | Python backend URL |
| `NODE_ENV` | `production` | Environment mode |

### Setting Environment Variables

1. Go to your Vercel project
2. Navigate to Settings → Environment Variables
3. Add each variable:
   - Name: `PYTHON_BACKEND_URL`
   - Value: Your Linode backend URL
   - Environments: Production, Preview, Development

### Local Environment Variables

Create `.env.local` in `/frontend` directory:

```bash
PYTHON_BACKEND_URL=http://localhost:8000
NODE_ENV=development
```

**Important:** Never commit `.env.local` to version control!

---

## Local Development

### Prerequisites

- Node.js 18+ installed
- Vercel CLI installed: `npm i -g vercel`

### Setup Steps

1. **Install Dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Create Environment File:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your values
   ```

3. **Start Development Server:**
   ```bash
   npm run dev
   # or
   vercel dev
   ```

4. **Test API Endpoints:**
   ```bash
   # Health check
   curl http://localhost:3000/api/health

   # Chat endpoint
   curl -X POST http://localhost:3000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"question": "Hvað er efnafræði?"}'
   ```

### Using Vercel Dev

`vercel dev` provides the most accurate local development experience:

```bash
vercel dev
```

Benefits:
- Simulates Vercel's production environment
- Supports environment variables
- Hot reload on file changes
- Mimics serverless function behavior

---

## Testing

### Running Tests

```bash
# Run all tests
npm test

# Watch mode (re-run on changes)
npm run test:watch

# Coverage report
npm run test:coverage
```

### Test Structure

```
frontend/api/_tests/
├── chat.test.ts          # Chat endpoint tests
├── health.test.ts        # Health endpoint tests
└── vitest.config.ts      # Test configuration
```

### What's Tested

**Chat Endpoint:**
- ✅ Request validation (method, question format)
- ✅ Successful requests with/without session_id
- ✅ Timeout handling
- ✅ Backend error handling
- ✅ Network error handling
- ✅ Missing configuration handling

**Health Endpoint:**
- ✅ Successful health checks
- ✅ Backend unavailability
- ✅ Timeout handling
- ✅ Configuration errors
- ✅ Response format validation

### Writing New Tests

Example test template:

```typescript
import { describe, it, expect, vi } from 'vitest';
import handler from '../your-endpoint';

describe('Your Endpoint', () => {
  it('should handle valid request', async () => {
    // Setup mocks
    // Create request/response
    // Call handler
    // Assert expectations
  });
});
```

---

## Deployment

### Automatic Deployment

Vercel automatically deploys when you push to GitHub:

1. **Push to Branch:**
   ```bash
   git push origin main
   ```

2. **Vercel Builds:**
   - Runs build process
   - Deploys serverless functions
   - Generates preview URL

3. **Production Deployment:**
   - Merging to `main` deploys to production
   - Custom domains automatically updated

### Manual Deployment

```bash
# Deploy to production
vercel --prod

# Deploy preview
vercel
```

### Deployment Checklist

Before deploying to production:

- [ ] Environment variables configured in Vercel
- [ ] Tests passing (`npm test`)
- [ ] Backend URL is correct
- [ ] CORS headers configured
- [ ] Rate limiting tested
- [ ] Error messages in Icelandic
- [ ] Timeout values appropriate

### Deployment Logs

View deployment logs:
```bash
vercel logs
```

Or in Vercel Dashboard:
- Go to Deployments
- Click on deployment
- View Function Logs

---

## Monitoring

### Health Monitoring

Set up monitoring for `/api/health`:

**Using Uptime Robot (Free):**
1. Create account at uptimerobot.com
2. Add monitor:
   - Type: HTTP(s)
   - URL: `https://your-domain.vercel.app/api/health`
   - Interval: 5 minutes

**Using Vercel Analytics:**
- Automatically enabled in Vercel Dashboard
- View under Analytics tab
- Shows request counts, errors, response times

### Logging

**View Logs:**
```bash
# Real-time logs
vercel logs --follow

# Function-specific logs
vercel logs --function api/chat
```

**Log Levels:**
- Console.log → Info
- Console.error → Error
- Console.warn → Warning

**Best Practices:**
- Don't log sensitive data (passwords, tokens)
- Include timestamps
- Use structured logging (JSON format)
- Log request IDs for tracing

### Key Metrics to Monitor

1. **Error Rate:**
   - Target: < 1%
   - Alert if > 5%

2. **Response Time:**
   - P50: < 500ms
   - P95: < 2s
   - P99: < 5s

3. **Backend Availability:**
   - Target: 99.9%
   - Health check every 5 minutes

4. **Rate Limit Triggers:**
   - Monitor 429 responses
   - Adjust limits if needed

---

## Troubleshooting

### Common Issues

#### 1. "PYTHON_BACKEND_URL not configured"

**Symptom:** 500 error, logs show missing environment variable

**Solution:**
```bash
# Check environment variables
vercel env ls

# Add if missing
vercel env add PYTHON_BACKEND_URL
```

#### 2. "Beiðni tók of langan tíma" (Timeout)

**Symptom:** 504 error after 30 seconds

**Possible Causes:**
- Backend is slow or unresponsive
- Network issues between Vercel and Linode
- Backend endpoint down

**Solutions:**
1. Check backend health: `curl https://your-backend.com/health`
2. Check backend logs on Linode
3. Verify network connectivity
4. Consider increasing timeout (in `vercel.json`)

#### 3. "Ekki tókst að tengjast" (Connection Failed)

**Symptom:** 503 error, cannot reach backend

**Possible Causes:**
- Backend URL incorrect
- Backend server down
- Firewall blocking Vercel IPs
- SSL certificate issues

**Solutions:**
1. Verify `PYTHON_BACKEND_URL` is correct
2. Test backend directly: `curl https://your-backend.com/health`
3. Check Linode firewall settings
4. Verify SSL certificate is valid

#### 4. CORS Errors

**Symptom:** Browser console shows CORS error

**Solution:**
- Check `vercel.json` CORS headers
- Verify middleware is working
- Ensure backend also sends CORS headers

#### 5. Rate Limiting Issues

**Symptom:** 429 errors, "Of margar beiðnir"

**Solutions:**
1. Check rate limit configuration in `_middleware.ts`
2. Implement proper session management
3. Consider using Vercel KV for distributed rate limiting
4. Increase limits if legitimate traffic

### Debug Mode

Enable verbose logging:

```typescript
// In your function
console.log('[DEBUG]', {
  request: req,
  headers: req.headers,
  body: req.body,
});
```

### Getting Help

1. **Check Vercel Status:** https://www.vercel-status.com/
2. **Vercel Documentation:** https://vercel.com/docs
3. **View Logs:** `vercel logs --follow`
4. **Community:** https://github.com/vercel/vercel/discussions

---

## Production Best Practices

### Security

1. **Environment Variables:**
   - Never commit secrets to git
   - Use Vercel's encrypted environment variables
   - Rotate secrets regularly

2. **Rate Limiting:**
   - Implement per-IP and per-session limits
   - Use Vercel KV for distributed rate limiting
   - Monitor for abuse patterns

3. **Input Validation:**
   - Validate all user input
   - Sanitize before sending to backend
   - Limit request size

4. **CORS:**
   - Restrict origins in production
   - Use specific domains, not `*`
   - Validate Origin header

### Performance

1. **Caching:**
   - Cache health check responses
   - Use CDN for static assets
   - Implement Redis caching on backend

2. **Timeout Strategy:**
   - Set appropriate timeouts (30s for chat, 5s for health)
   - Implement retry logic with exponential backoff
   - Use circuit breaker pattern

3. **Cold Start Optimization:**
   - Minimize dependencies
   - Keep functions small
   - Use warming strategies if needed

### Reliability

1. **Error Handling:**
   - Handle all error types
   - Provide user-friendly messages
   - Log errors for debugging

2. **Monitoring:**
   - Set up uptime monitoring
   - Configure alerts
   - Track error rates

3. **Graceful Degradation:**
   - Show cached responses on backend failure
   - Provide offline mode
   - Queue requests when possible

### Cost Optimization

1. **Function Configuration:**
   - Use appropriate memory settings
   - Optimize timeout values
   - Minimize function size

2. **Monitoring Usage:**
   - Track function invocations
   - Monitor bandwidth usage
   - Review Vercel usage dashboard

---

## API Rate Limits

Current configuration (in `_middleware.ts`):
- **Window:** 60 seconds
- **Max Requests:** 30 per window
- **Identifier:** Session ID or IP address

To modify:
```typescript
const RATE_LIMIT_WINDOW = 60000; // milliseconds
const RATE_LIMIT_MAX_REQUESTS = 30; // requests
```

For production, consider:
- Implementing Vercel KV for distributed rate limiting
- Different limits for authenticated vs anonymous users
- Tiered rate limits based on user plan

---

## Contributing

When making changes to the API:

1. Update tests
2. Run test suite: `npm test`
3. Update this documentation
4. Test locally with `vercel dev`
5. Deploy to preview environment
6. Test preview deployment
7. Merge to main for production deployment

---

## Version History

- **v1.0.0** (2025-11-17): Initial implementation
  - Chat endpoint
  - Health check endpoint
  - CORS middleware
  - Rate limiting
  - Comprehensive error handling

---

## Support

For issues or questions:
1. Check this documentation
2. Review troubleshooting section
3. Check Vercel logs: `vercel logs`
4. Review backend logs on Linode
5. Open GitHub issue if problem persists
