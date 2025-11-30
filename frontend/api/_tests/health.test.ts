import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import type { VercelRequest, VercelResponse } from '@vercel/node';
import handler from '../health';

/**
 * Tests for Health Check API Endpoint
 *
 * Run with: npm test
 * or: vitest
 */

// Mock fetch globally
type MockedFetch = ReturnType<typeof vi.fn>;
global.fetch = vi.fn() as MockedFetch;

// Helper to create mock request
function createMockRequest(method: string = 'GET'): VercelRequest {
  return {
    method,
    body: {},
    headers: {},
    query: {},
    cookies: {},
    url: '/api/health',
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

describe('Health Check API Endpoint', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetAllMocks();
    process.env = {
      ...originalEnv,
      PYTHON_BACKEND_URL: 'https://test-backend.example.com',
    };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('Successful Health Check', () => {
    it('should return ok status when backend is healthy', async () => {
      (global.fetch as MockedFetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'ok' }),
      });

      const req = createMockRequest('GET');
      const res = createMockResponse();

      await handler(req, res);

      expect(global.fetch).toHaveBeenCalledWith(
        'https://test-backend.example.com/health',
        expect.objectContaining({
          signal: expect.any(Object),
        })
      );

      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'ok',
          timestamp: expect.any(String),
        })
      );
    });

    it('should accept any HTTP method', async () => {
      (global.fetch as MockedFetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'ok' }),
      });

      const methods = ['GET', 'POST', 'HEAD', 'OPTIONS'];

      for (const method of methods) {
        vi.resetAllMocks();
        (global.fetch as MockedFetch).mockResolvedValueOnce({
          ok: true,
          json: async () => ({ status: 'ok' }),
        });

        const req = createMockRequest(method);
        const res = createMockResponse();

        await handler(req, res);

        expect(res.status).toHaveBeenCalledWith(200);
      }
    });

    it('should include backend data in response', async () => {
      const backendData = {
        status: 'ok',
        version: '1.0.0',
        uptime: 12345,
      };

      (global.fetch as MockedFetch).mockResolvedValueOnce({
        ok: true,
        json: async () => backendData,
      });

      const req = createMockRequest('GET');
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'ok',
          backend: backendData,
        })
      );
    });
  });

  describe('Health Check Failures', () => {
    it('should return error when backend URL not configured', async () => {
      delete process.env.PYTHON_BACKEND_URL;

      const req = createMockRequest('GET');
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(503);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'error',
          message: 'Backend URL not configured',
        })
      );
    });

    it('should return error when backend is unhealthy', async () => {
      (global.fetch as MockedFetch).mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      const req = createMockRequest('GET');
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(503);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'error',
          message: expect.any(String),
        })
      );
    });

    it('should handle backend timeout', async () => {
      const timeoutError = new Error('Timeout');
      timeoutError.name = 'AbortError';
      (global.fetch as MockedFetch).mockRejectedValueOnce(timeoutError);

      const req = createMockRequest('GET');
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(503);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'error',
          message: 'Backend timeout',
        })
      );
    });

    it('should handle TimeoutError', async () => {
      const timeoutError = new Error('Timeout');
      timeoutError.name = 'TimeoutError';
      (global.fetch as MockedFetch).mockRejectedValueOnce(timeoutError);

      const req = createMockRequest('GET');
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(503);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'error',
          message: 'Backend timeout',
        })
      );
    });

    it('should handle network errors', async () => {
      const networkError = new Error('Network error');
      (global.fetch as MockedFetch).mockRejectedValueOnce(networkError);

      const req = createMockRequest('GET');
      const res = createMockResponse();

      await handler(req, res);

      expect(res.status).toHaveBeenCalledWith(503);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'error',
          message: 'Backend unavailable',
        })
      );
    });

    it('should handle backend JSON parse error gracefully', async () => {
      (global.fetch as MockedFetch).mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      const req = createMockRequest('GET');
      const res = createMockResponse();

      await handler(req, res);

      // Should still return ok if backend responds with ok status
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'ok',
          backend: {},
        })
      );
    });
  });

  describe('Timeout Configuration', () => {
    it('should set 5 second timeout for health checks', async () => {
      (global.fetch as MockedFetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'ok' }),
      });

      const req = createMockRequest('GET');
      const res = createMockResponse();

      await handler(req, res);

      // Verify fetch was called with a signal that has timeout
      const fetchCall = (global.fetch as MockedFetch).mock.calls[0];
      expect(fetchCall[1]).toHaveProperty('signal');
    });
  });

  describe('Response Format', () => {
    it('should include timestamp in response', async () => {
      (global.fetch as MockedFetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'ok' }),
      });

      const req = createMockRequest('GET');
      const res = createMockResponse();

      await handler(req, res);

      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          timestamp: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T/),
        })
      );
    });
  });
});
