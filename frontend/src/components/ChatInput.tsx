/**
 * Chat Input Component
 * Multi-line textarea with auto-resize and keyboard shortcuts
 */

import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const MAX_CHARACTERS = 500;

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = 'Skrifaðu spurninguna þína hér...'
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const scrollHeight = textarea.scrollHeight;
      const maxHeight = 5 * 24; // 5 lines * 24px per line
      textarea.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
    }
  }, [message]);

  const handleSubmit = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !disabled) {
      onSend(trimmedMessage);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const remainingChars = MAX_CHARACTERS - message.length;
  const isOverLimit = remainingChars < 0;

  return (
    <div className="border-t border-gray-300 bg-white p-4">
      <div className="max-w-4xl mx-auto">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={`w-full resize-none rounded-lg border ${
              isOverLimit ? 'border-red-500' : 'border-gray-300'
            } px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed`}
            aria-label="Skilaboð"
          />

          <button
            onClick={handleSubmit}
            disabled={disabled || !message.trim() || isOverLimit}
            className="absolute right-2 bottom-2 p-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            aria-label="Senda skilaboð"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <div>
            Ýttu á <kbd className="px-1 py-0.5 bg-gray-200 rounded">Enter</kbd> til að senda,{' '}
            <kbd className="px-1 py-0.5 bg-gray-200 rounded">Shift+Enter</kbd> fyrir nýja línu
          </div>
          <div className={isOverLimit ? 'text-red-500 font-medium' : ''}>
            {remainingChars} stafir eftir
          </div>
        </div>
      </div>
    </div>
  );
}
