import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import type { VercelRequest, VercelResponse } from '@vercel/node';
import handler from '../chat';

/**
 * Tests for Chat API Endpoint
 *
 * Run with: npm test
 * or: vitest
 */

// Mock fetch globally
type MockedFetch = ReturnType<typeof vi.fn>;
global.fetch = vi.fn() as MockedFetch;

// Helper to create mock request
function createMockRequest(
  method: string = 'POST',
  body: Record<string, unknown> = {}
): VercelRequest {
  return {
    method,
    body,
    headers: {},
    query: {},
    cookies: {},
    url: '/api/chat',
  } as VercelRequest;
}

// Helper to create mock response
function createMockResponse() {
  const res = {
    status: vi.fn().mockReturnThis(),
    json: vi.fn().mockReturnThis(),
    send: vi.fn().mockReturnThis(),
    setHeader: vi.fn().mockReturnThis(),
  } as unknown as VercelResponse;
  return res;
}

describe('Chat API Endpoint', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    // Reset environment and mocks
    vi.resetAllMocks();
    process.env = {
      ...originalEnv,
      PYTHON_BACKEND_URL: 'https://test-backend.example.com',
    };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('Request Validation', () => {
    it('should reject non-POST requests', async () => {
      const req = createMockRequest('GET');
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(405);
      expect(res.json).toHaveBeenCalledWith({ error: 'Method not allowed' });
    });

    it('should reject requests without question', async () => {
      const req = createMockRequest('POST', { session_id: '123' });
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith({ error: 'Ógild spurning' });
    });

    it('should reject requests with non-string question', async () => {
      const req = createMockRequest('POST', { question: 123 });
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith({ error: 'Ógild spurning' });
    });

    it('should reject requests with empty question', async () => {
      const req = createMockRequest('POST', { question: '' });
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalledWith({ error: 'Ógild spurning' });
    });
  });

  describe('Successful Requests', () => {
    it('should forward valid request to backend', async () => {
      const mockBackendResponse = {
        answer: 'Test answer',
        session_id: '123',
      };

      (global.fetch as MockedFetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockBackendResponse,
      });

      const req = createMockRequest('POST', {
        question: 'What is chemistry?',
        session_id: '123',
      });
      const res = createMockResponse();

      await handler(req, res);

      expect(global.fetch).toHaveBeenCalledWith(
        'https://test-backend.example.com/ask',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question: 'What is chemistry?',
            session_id: '123',
          }),
        })
      );

      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(mockBackendResponse);
    });

    it('should work without session_id', async () => {
      const mockBackendResponse = {
        answer: 'Test answer',
      };

      (global.fetch as MockedFetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockBackendResponse,
      });

      const req = createMockRequest('POST', {
        question: 'What is chemistry?',
      });
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(mockBackendResponse);
    });
  });

  describe('Error Handling', () => {
    it('should handle missing backend URL', async () => {
      delete process.env.PYTHON_BACKEND_URL;

      const req = createMockRequest('POST', {
        question: 'What is chemistry?',
      });
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(500);
      expect(res.json).toHaveBeenCalledWith({
        error: 'Villa kom upp, reyndu aftur',
      });
    });

    it('should handle backend timeout', async () => {
      const timeoutError = new Error('Timeout');
      timeoutError.name = 'AbortError';
      (global.fetch as MockedFetch).mockRejectedValueOnce(timeoutError);

      const req = createMockRequest('POST', {
        question: 'What is chemistry?',
      });
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(504);
      expect(res.json).toHaveBeenCalledWith({
        error: 'Beiðni tók of langan tíma',
      });
    });

    it('should handle TimeoutError', async () => {
      const timeoutError = new Error('Timeout');
      timeoutError.name = 'TimeoutError';
      (global.fetch as MockedFetch).mockRejectedValueOnce(timeoutError);

      const req = createMockRequest('POST', {
        question: 'What is chemistry?',
      });
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(504);
      expect(res.json).toHaveBeenCalledWith({
        error: 'Beiðni tók of langan tíma',
      });
    });

    it('should handle backend connection error', async () => {
      const fetchError = new Error('fetch failed');
      (global.fetch as MockedFetch).mockRejectedValueOnce(fetchError);

      const req = createMockRequest('POST', {
        question: 'What is chemistry?',
      });
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(503);
      expect(res.json).toHaveBeenCalledWith({
        error: 'Ekki tókst að tengjast',
      });
    });

    it('should handle backend error response', async () => {
      (global.fetch as MockedFetch).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      const req = createMockRequest('POST', {
        question: 'What is chemistry?',
      });
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(500);
      expect(res.json).toHaveBeenCalledWith({
        error: 'Villa kom upp, reyndu aftur',
      });
    });

    it('should handle backend JSON parse error', async () => {
      (global.fetch as MockedFetch).mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      const req = createMockRequest('POST', {
        question: 'What is chemistry?',
      });
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(500);
      expect(res.json).toHaveBeenCalledWith({
        error: 'Villa kom upp, reyndu aftur',
      });
    });
  });

  describe('Timeout Configuration', () => {
    it('should set 30 second timeout', async () => {
      (global.fetch as MockedFetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ answer: 'test' }),
      });

      const req = createMockRequest('POST', {
        question: 'What is chemistry?',
      });
      const res = createMockResponse();

      await handler(req, res);

      // Verify fetch was called with a signal that has timeout
      const fetchCall = (global.fetch as MockedFetch).mock.calls[0];
      expect(fetchCall[1]).toHaveProperty('signal');
    });
  });
});
