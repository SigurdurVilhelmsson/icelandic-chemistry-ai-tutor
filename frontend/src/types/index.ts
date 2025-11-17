/**
 * Type definitions for Icelandic Chemistry AI Tutor
 */

export interface Citation {
  chapter: string;
  section: string;
  title: string;
  chunk_text: string;
}

export interface Message {
  id: string;
  role: 'student' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  timestamp: string;
}

export interface ConversationSummary {
  sessionId: string;
  firstQuestion: string;
  lastUpdated: Date;
  messageCount: number;
}

export interface ChatState {
  sessionId: string;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export interface StoredConversation {
  sessionId: string;
  messages: Message[];
  lastUpdated: string;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
}
