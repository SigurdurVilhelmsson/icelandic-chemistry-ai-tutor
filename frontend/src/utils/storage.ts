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
 */
export function saveConversation(sessionId: string, messages: Message[]): void {
  try {
    const conversations = getAllConversations();

    const storedConversation: StoredConversation = {
      sessionId,
      messages: messages.map(msg => ({
        ...msg,
        timestamp: msg.timestamp instanceof Date ? msg.timestamp.toISOString() : msg.timestamp
      })) as any,
      lastUpdated: new Date().toISOString()
    };

    conversations[sessionId] = storedConversation;
    localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations));
    localStorage.setItem(CURRENT_SESSION_KEY, sessionId);
  } catch (error) {
    console.error('Error saving conversation:', error);
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
      timestamp: new Date(msg.timestamp as any)
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
 */
export function deleteConversation(sessionId: string): void {
  try {
    const conversations = getAllConversations();
    delete conversations[sessionId];
    localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations));

    // If we're deleting the current session, clear that too
    if (localStorage.getItem(CURRENT_SESSION_KEY) === sessionId) {
      localStorage.removeItem(CURRENT_SESSION_KEY);
    }
  } catch (error) {
    console.error('Error deleting conversation:', error);
  }
}

/**
 * Get the current session ID
 */
export function getCurrentSessionId(): string | null {
  return localStorage.getItem(CURRENT_SESSION_KEY);
}

/**
 * Clear all conversations
 */
export function clearAllConversations(): void {
  try {
    localStorage.removeItem(CONVERSATIONS_KEY);
    localStorage.removeItem(CURRENT_SESSION_KEY);
  } catch (error) {
    console.error('Error clearing conversations:', error);
  }
}
