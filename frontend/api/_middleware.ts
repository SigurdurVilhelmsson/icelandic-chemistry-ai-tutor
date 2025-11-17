import { NextRequest, NextResponse } from 'next/server';

/**
 * Vercel Edge Middleware
 * Handles CORS, rate limiting, and request preprocessing
 *
 * Note: This uses Vercel's Edge Middleware (runs on Edge Runtime)
 * For more info: https://vercel.com/docs/functions/edge-middleware
 *
 * Features:
 * - CORS configuration
 * - OPTIONS preflight handling
 * - Basic rate limiting (session-based)
 * - Request logging
 */

// Simple in-memory rate limiter (for production, use Vercel KV or Redis)
const rateLimitMap = new Map<string, { count: number; resetTime: number }>();

const RATE_LIMIT_WINDOW = 60000; // 1 minute
const RATE_LIMIT_MAX_REQUESTS = 30; // 30 requests per minute

function checkRateLimit(identifier: string): boolean {
  const now = Date.now();
  const record = rateLimitMap.get(identifier);

  if (!record || now > record.resetTime) {
    // Reset or create new record
    rateLimitMap.set(identifier, {
      count: 1,
      resetTime: now + RATE_LIMIT_WINDOW,
    });
    return true;
  }

  if (record.count >= RATE_LIMIT_MAX_REQUESTS) {
    return false;
  }

  record.count++;
  return true;
}

// Clean up old entries periodically (simple garbage collection)
setInterval(() => {
  const now = Date.now();
  for (const [key, record] of rateLimitMap.entries()) {
    if (now > record.resetTime) {
      rateLimitMap.delete(key);
    }
  }
}, 60000); // Clean up every minute

export default function middleware(req: NextRequest) {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new NextResponse(null, {
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '86400', // 24 hours
      },
    });
  }

  // Get rate limit identifier (session ID or IP)
  const sessionId = req.headers.get('x-session-id');
  const clientIp = req.headers.get('x-forwarded-for') || req.headers.get('x-real-ip') || 'unknown';
  const rateLimitId = sessionId || clientIp;

  // Check rate limit
  if (!checkRateLimit(rateLimitId)) {
    console.warn('[Middleware] Rate limit exceeded:', {
      identifier: rateLimitId,
      timestamp: new Date().toISOString(),
    });

    return new NextResponse(
      JSON.stringify({ error: 'Of margar beiðnir, bíddu aðeins' }),
      {
        status: 429,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Retry-After': '60',
        },
      }
    );
  }

  // Log request (for monitoring)
  console.log('[Middleware] Request:', {
    method: req.method,
    url: req.url,
    identifier: rateLimitId,
    timestamp: new Date().toISOString(),
  });

  // Continue to the API handler with CORS headers
  const response = NextResponse.next();
  response.headers.set('Access-Control-Allow-Origin', '*');
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  return response;
}

// Configure which paths this middleware runs on
export const config = {
  matcher: '/api/:path*',
};
