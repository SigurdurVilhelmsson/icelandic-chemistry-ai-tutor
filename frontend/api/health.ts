import type { VercelRequest, VercelResponse } from '@vercel/node';

/**
 * Vercel Serverless Function - Health Check Endpoint
 * Verifies that both the Vercel serverless function and Python backend are operational
 *
 * Features:
 * - Backend connectivity check
 * - Fast timeout (5 seconds)
 * - Simple status response
 * - Error logging
 */
export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  // Accept all HTTP methods for health checks
  try {
    const backendUrl = process.env.PYTHON_BACKEND_URL;

    if (!backendUrl) {
      console.error('[Health API] PYTHON_BACKEND_URL not configured');
      return res.status(503).json({
        status: 'error',
        message: 'Backend URL not configured'
      });
    }

    // Check backend health
    const response = await fetch(`${backendUrl}/health`, {
      signal: AbortSignal.timeout(5000), // 5s timeout for health checks
    });

    if (!response.ok) {
      console.error('[Health API] Backend unhealthy:', response.status);
      throw new Error('Backend unhealthy');
    }

    // Optional: Parse backend response for additional details
    const backendData = await response.json().catch(() => ({}));

    return res.status(200).json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      backend: backendData,
    });

  } catch (error: unknown) {
    const err = error as Error;
    console.error('[Health API] Error:', {
      name: err.name,
      message: err.message,
      timestamp: new Date().toISOString(),
    });

    return res.status(503).json({
      status: 'error',
      message: err.name === 'AbortError' || err.name === 'TimeoutError'
        ? 'Backend timeout'
        : 'Backend unavailable',
      timestamp: new Date().toISOString(),
    });
  }
}
