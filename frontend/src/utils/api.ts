/**
 * API client for communicating with the backend
 */

import { ChatResponse } from '../types';

const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT || 'http://localhost:8000';
const TIMEOUT_MS = 30000; // 30 seconds
const MAX_RETRIES = 3;

/**
 * Custom error for API failures
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public originalError?: Error
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Delay function for retry logic
 */
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Fetch with timeout
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeoutMs: number
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError('Beiðni tók of langan tíma');
    }
    throw error;
  }
}

/**
 * Send a message to the backend with retry logic
 */
export async function sendMessage(
  question: string,
  sessionId: string
): Promise<ChatResponse> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const response = await fetchWithTimeout(
        `${API_ENDPOINT}/ask`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question,
            session_id: sessionId
          })
        },
        TIMEOUT_MS
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          errorData.detail || `Villa kom upp: ${response.status}`,
          response.status
        );
      }

      const data = await response.json();

      return {
        answer: data.answer,
        citations: data.citations || [],
        timestamp: data.timestamp || new Date().toISOString()
      };
    } catch (error) {
      lastError = error as Error;

      // Don't retry on client errors (4xx)
      if (error instanceof ApiError && error.status && error.status >= 400 && error.status < 500) {
        throw error;
      }

      // Wait before retrying (exponential backoff)
      if (attempt < MAX_RETRIES - 1) {
        await delay(Math.pow(2, attempt) * 1000);
      }
    }
  }

  throw new ApiError(
    'Ekki tókst að tengjast þjóninum. Vinsamlegast reyndu aftur.',
    undefined,
    lastError || undefined
  );
}

/**
 * Health check endpoint
 */
export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetchWithTimeout(
      `${API_ENDPOINT}/health`,
      { method: 'GET' },
      5000 // 5 second timeout for health check
    );

    return response.ok;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
}

/**
 * Get API endpoint (for debugging)
 */
export function getApiEndpoint(): string {
  return API_ENDPOINT;
}
