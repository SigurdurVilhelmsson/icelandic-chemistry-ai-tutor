// API configuration for Linode deployment
const API_BASE_URL = import.meta.env.VITE_API_ENDPOINT || 'http://localhost:8000';

export interface ChatResponse {
  response: string;
  session_id: string;
}

export async function sendMessage(
  question: string,
  sessionId: string
): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        session_id: sessionId
      }),
      signal: AbortSignal.timeout(30000),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Beiðni tók of langan tíma');
    }
    throw new Error('Villa kom upp, reyndu aftur');
  }
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      signal: AbortSignal.timeout(5000),
    });
    return response.ok;
  } catch {
    return false;
  }
}
