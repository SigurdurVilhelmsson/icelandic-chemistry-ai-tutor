/**
 * Chat Context for managing conversation state
 */

import React, { createContext, useContext, useReducer, useCallback, useEffect, useRef } from 'react';
import { Message, ChatState, ToastMessage } from '../types';
import {
  generateSessionId,
  saveConversation,
  loadConversation,
  getCurrentSessionId
} from '../utils/storage';
import { sendMessage as apiSendMessage } from '../utils/api';
import { exportConversationToCSV } from '../utils/export';

interface ChatContextType extends ChatState {
  sendMessage: (question: string) => Promise<void>;
  loadConversation: (sessionId: string) => void;
  newConversation: () => void;
  clearConversation: () => void;
  exportConversation: () => void;
  showToast: (message: string, type: ToastMessage['type']) => void;
  toasts: ToastMessage[];
  dismissToast: (id: string) => void;
}

type ChatAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'LOAD_MESSAGES'; payload: { sessionId: string; messages: Message[] } }
  | { type: 'NEW_CONVERSATION'; payload: string }
  | { type: 'CLEAR_CONVERSATION' }
  | { type: 'ADD_TOAST'; payload: ToastMessage }
  | { type: 'REMOVE_TOAST'; payload: string };

const initialState: ChatState = {
  sessionId: generateSessionId(),
  messages: [],
  isLoading: false,
  error: null
};

const ChatContext = createContext<ChatContextType | undefined>(undefined);

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };

    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };

    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
        error: null
      };

    case 'LOAD_MESSAGES':
      return {
        ...state,
        sessionId: action.payload.sessionId,
        messages: action.payload.messages,
        error: null
      };

    case 'NEW_CONVERSATION':
      return {
        ...state,
        sessionId: action.payload,
        messages: [],
        error: null,
        isLoading: false
      };

    case 'CLEAR_CONVERSATION':
      return {
        ...state,
        messages: [],
        error: null,
        isLoading: false
      };

    default:
      return state;
  }
}

interface ExtendedState extends ChatState {
  toasts: ToastMessage[];
}

function extendedReducer(
  state: ExtendedState,
  action: ChatAction
): ExtendedState {
  if (action.type === 'ADD_TOAST') {
    return {
      ...state,
      toasts: [...state.toasts, action.payload]
    };
  }

  if (action.type === 'REMOVE_TOAST') {
    return {
      ...state,
      toasts: state.toasts.filter(t => t.id !== action.payload)
    };
  }

  return {
    ...chatReducer(state, action),
    toasts: state.toasts
  };
}

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(extendedReducer, {
    ...initialState,
    toasts: []
  });

  // Track active toast timeouts for cleanup
  const toastTimeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // Load conversation from localStorage on mount
  useEffect(() => {
    const currentSessionId = getCurrentSessionId();
    if (currentSessionId) {
      const messages = loadConversation(currentSessionId);
      if (messages && messages.length > 0) {
        dispatch({
          type: 'LOAD_MESSAGES',
          payload: { sessionId: currentSessionId, messages }
        });
      }
    }
  }, []);

  // Define showToast before it's used in other useEffects
  const showToast = useCallback((message: string, type: ToastMessage['type']) => {
    const id = `toast_${Date.now()}_${Math.random()}`;
    dispatch({
      type: 'ADD_TOAST',
      payload: { id, message, type }
    });

    // Auto-dismiss after 5 seconds
    const timeoutId = setTimeout(() => {
      dispatch({ type: 'REMOVE_TOAST', payload: id });
      toastTimeoutsRef.current.delete(id);
    }, 5000);

    // Store timeout ID for cleanup
    toastTimeoutsRef.current.set(id, timeoutId);
  }, []);

  const dismissToast = useCallback((id: string) => {
    // Clear the timeout if it exists
    const timeoutId = toastTimeoutsRef.current.get(id);
    if (timeoutId) {
      clearTimeout(timeoutId);
      toastTimeoutsRef.current.delete(id);
    }
    dispatch({ type: 'REMOVE_TOAST', payload: id });
  }, []);

  // Save conversation whenever messages change
  useEffect(() => {
    if (state.messages.length > 0) {
      const success = saveConversation(state.sessionId, state.messages);
      if (!success) {
        // Only show error once per session using a flag
        interface WindowWithStorageError extends Window {
          __storage_error_shown?: boolean;
        }
        const win = window as unknown as WindowWithStorageError;
        if (!win.__storage_error_shown) {
          showToast('Viðvörun: Ekki tókst að vista samtal. Minni gæti verið fullt.', 'error');
          win.__storage_error_shown = true;
        }
      }
    }
  }, [state.messages, state.sessionId, showToast]);

  // Cleanup all toast timeouts on unmount
  useEffect(() => {
    return () => {
      toastTimeoutsRef.current.forEach((timeout) => clearTimeout(timeout));
      toastTimeoutsRef.current.clear();
    };
  }, []);

  const sendMessage = useCallback(async (question: string) => {
    if (!question.trim()) {
      return;
    }

    // Add student message
    const studentMessage: Message = {
      id: `msg_${Date.now()}_student`,
      role: 'student',
      content: question.trim(),
      timestamp: new Date()
    };

    dispatch({ type: 'ADD_MESSAGE', payload: studentMessage });
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      // Call API
      const response = await apiSendMessage(question.trim(), state.sessionId);

      // Add assistant message
      const assistantMessage: Message = {
        id: `msg_${Date.now()}_assistant`,
        role: 'assistant',
        content: response.answer,
        citations: response.citations,
        timestamp: new Date(response.timestamp)
      };

      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage });
      dispatch({ type: 'SET_LOADING', payload: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Villa kom upp';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      showToast(errorMessage, 'error');
    }
  }, [state.sessionId, showToast]);

  const loadConversationById = useCallback((sessionId: string) => {
    const messages = loadConversation(sessionId);
    if (messages) {
      dispatch({
        type: 'LOAD_MESSAGES',
        payload: { sessionId, messages }
      });
      showToast('Samtal hlaðið', 'success');
    } else {
      showToast('Ekki tókst að hlaða samtali', 'error');
    }
  }, [showToast]);

  const newConversation = useCallback(() => {
    const newSessionId = generateSessionId();
    dispatch({ type: 'NEW_CONVERSATION', payload: newSessionId });
    showToast('Nýtt samtal byrjað', 'success');
  }, [showToast]);

  const clearConversation = useCallback(() => {
    dispatch({ type: 'CLEAR_CONVERSATION' });
    showToast('Samtal hreinsað', 'success');
  }, [showToast]);

  const exportConversation = useCallback(() => {
    try {
      exportConversationToCSV(state.sessionId, state.messages);
      showToast('Samtal flutt út', 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Villa kom upp við útflutning';
      showToast(errorMessage, 'error');
    }
  }, [state.sessionId, state.messages, showToast]);

  const value: ChatContextType = {
    ...state,
    sendMessage,
    loadConversation: loadConversationById,
    newConversation,
    clearConversation,
    exportConversation,
    showToast,
    toasts: state.toasts,
    dismissToast
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat(): ChatContextType {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
