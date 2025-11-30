/**
 * localStorage utility functions for managing conversations
 * Adapted from LabReports pattern
 */

import { Message, ConversationSummary, StoredConversation } from '../types';

const CONVERSATIONS_KEY = 'chemistry_conversations';
const CURRENT_SESSION_KEY = 'chemistry_current_session';

/**
 * Generate a unique session ID
 */
export function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Save a conversation to localStorage
 * @returns true if save was successful, false otherwise
 */
export function saveConversation(sessionId: string, messages: Message[]): boolean {
  try {
    const conversations = getAllConversations();

    const storedConversation: StoredConversation = {
      sessionId,
      messages: messages.map(msg => ({
        ...msg,
        timestamp: msg.timestamp instanceof Date ? msg.timestamp.toISOString() : msg.timestamp
      })) as unknown as Message[],
      lastUpdated: new Date().toISOString()
    };

    conversations[sessionId] = storedConversation;
    localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations));
    localStorage.setItem(CURRENT_SESSION_KEY, sessionId);
    return true;
  } catch (error) {
    console.error('Error saving conversation:', error);

    // Check for quota exceeded error
    if (error instanceof DOMException &&
        (error.name === 'QuotaExceededError' || error.code === 22)) {
      console.error('localStorage quota exceeded - clearing old conversations');
      // Try to clear some space by removing oldest conversations
      try {
        const conversations = getAllConversations();
        const conversationList = Object.entries(conversations)
          .sort(([, a], [, b]) =>
            new Date(a.lastUpdated).getTime() - new Date(b.lastUpdated).getTime()
          );

        // Remove oldest 25% of conversations
        const toRemove = Math.max(1, Math.floor(conversationList.length * 0.25));
        for (let i = 0; i < toRemove; i++) {
          delete conversations[conversationList[i][0]];
        }

        localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations));

        // Try saving again
        conversations[sessionId] = {
          sessionId,
          messages: messages.map(msg => ({
            ...msg,
            timestamp: msg.timestamp instanceof Date ? msg.timestamp.toISOString() : msg.timestamp
          })) as unknown as Message[],
          lastUpdated: new Date().toISOString()
        };
        localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations));
        return true;
      } catch (retryError) {
        console.error('Failed to save even after clearing space:', retryError);
        return false;
      }
    }
    return false;
  }
}

/**
 * Load a conversation from localStorage
 */
export function loadConversation(sessionId: string): Message[] | null {
  try {
    const conversations = getAllConversations();
    const conversation = conversations[sessionId];

    if (!conversation) {
      return null;
    }

    return conversation.messages.map(msg => ({
      ...msg,
      timestamp: new Date(msg.timestamp as string | Date)
    }));
  } catch (error) {
    console.error('Error loading conversation:', error);
    return null;
  }
}

/**
 * Get all conversations from localStorage
 */
function getAllConversations(): Record<string, StoredConversation> {
  try {
    const data = localStorage.getItem(CONVERSATIONS_KEY);
    return data ? JSON.parse(data) : {};
  } catch (error) {
    console.error('Error reading conversations:', error);
    return {};
  }
}

/**
 * List all conversation summaries
 */
export function listConversations(): ConversationSummary[] {
  try {
    const conversations = getAllConversations();

    return Object.values(conversations)
      .map(conv => ({
        sessionId: conv.sessionId,
        firstQuestion: conv.messages.find(m => m.role === 'student')?.content || 'Nýtt samtal',
        lastUpdated: new Date(conv.lastUpdated),
        messageCount: conv.messages.length
      }))
      .sort((a, b) => b.lastUpdated.getTime() - a.lastUpdated.getTime());
  } catch (error) {
    console.error('Error listing conversations:', error);
    return [];
  }
}

/**
 * Delete a conversation from localStorage
 * @returns true if delete was successful, false otherwise
 */
export function deleteConversation(sessionId: string): boolean {
  try {
    const conversations = getAllConversations();
    delete conversations[sessionId];
    localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations));

    // If we're deleting the current session, clear that too
    if (localStorage.getItem(CURRENT_SESSION_KEY) === sessionId) {
      localStorage.removeItem(CURRENT_SESSION_KEY);
    }
    return true;
  } catch (error) {
    console.error('Error deleting conversation:', error);
    return false;
  }
}

/**
 * Get the current session ID
 * @returns session ID or null if not found or error occurred
 */
export function getCurrentSessionId(): string | null {
  try {
    return localStorage.getItem(CURRENT_SESSION_KEY);
  } catch (error) {
    console.error('Error getting current session ID:', error);
    return null;
  }
}

/**
 * Clear all conversations
 * @returns true if clear was successful, false otherwise
 */
export function clearAllConversations(): boolean {
  try {
    localStorage.removeItem(CONVERSATIONS_KEY);
    localStorage.removeItem(CURRENT_SESSION_KEY);
    return true;
  } catch (error) {
    console.error('Error clearing conversations:', error);
    return false;
  }
}

/**
 * Check if localStorage is available and working
 * @returns true if localStorage is available, false otherwise
 */
export function isLocalStorageAvailable(): boolean {
  try {
    const testKey = '__localStorage_test__';
    localStorage.setItem(testKey, 'test');
    localStorage.removeItem(testKey);
    return true;
  } catch (error) {
    return false;
  }
}
