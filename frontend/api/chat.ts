import type { VercelRequest, VercelResponse } from '@vercel/node';

/**
 * Vercel Serverless Function - Chat Endpoint
 * Bridges React frontend with Python backend on Linode
 *
 * Features:
 * - Request validation
 * - Timeout handling (30 seconds)
 * - Error handling with Icelandic messages
 * - Logging for debugging
 * - Response formatting
 */
export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  // Only accept POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Generate request ID for tracing
  const requestId = `req_${Date.now()}_${Math.random().toString(36).substring(7)}`;

  // Extract request data
  const { question, session_id } = req.body;

  // Validate request
  if (!question || typeof question !== 'string') {
    console.log(`[${requestId}] Validation failed: Invalid question`);
    return res.status(400).json({ error: 'Ógild spurning' });
  }

  // Log request for debugging (exclude sensitive data)
  console.log(`[${requestId}] Received request:`, {
    questionLength: question.length,
    hasSessionId: !!session_id,
    timestamp: new Date().toISOString(),
  });

  try {
    // Get Python backend URL from environment
    const backendUrl = process.env.PYTHON_BACKEND_URL;

    if (!backendUrl) {
      console.error(`[${requestId}] PYTHON_BACKEND_URL not configured`);
      return res.status(500).json({
        error: 'Villa kom upp, reyndu aftur'
      });
    }

    // Call Python backend on Linode
    console.log(`[${requestId}] Forwarding to backend: ${backendUrl}/ask`);
    const response = await fetch(`${backendUrl}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Request-ID': requestId,
      },
      body: JSON.stringify({ question, session_id }),
      signal: AbortSignal.timeout(30000), // 30s timeout
    });

    if (!response.ok) {
      console.error(`[${requestId}] Backend error:`, response.status, response.statusText);
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();

    // Log successful response
    console.log(`[${requestId}] Request successful:`, {
      hasAnswer: !!data.answer,
      citationCount: data.citations?.length || 0,
      timestamp: new Date().toISOString(),
    });

    // Return to frontend
    return res.status(200).json(data);

  } catch (error: unknown) {
    const err = error as Error;
    console.error(`[${requestId}] Error:`, {
      name: err.name,
      message: err.message,
      timestamp: new Date().toISOString(),
    });

    // User-friendly errors in Icelandic
    if (err.name === 'AbortError' || err.name === 'TimeoutError') {
      return res.status(504).json({
        error: 'Beiðni tók of langan tíma'
      });
    }

    if (err.message && err.message.includes('fetch')) {
      return res.status(503).json({
        error: 'Ekki tókst að tengjast'
      });
    }

    return res.status(500).json({
      error: 'Villa kom upp, reyndu aftur'
    });
  }
}
