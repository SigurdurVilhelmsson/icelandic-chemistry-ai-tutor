/**
 * Message Component
 * Displays individual chat messages with role-based styling
 */

import React, { useState } from 'react';
import { Copy, Check, ChevronDown, ChevronUp } from 'lucide-react';
import { format } from 'date-fns';
import { Message as MessageType } from '../types';
import { CitationCard } from './CitationCard';

interface MessageProps {
  message: MessageType;
}

export function Message({ message }: MessageProps) {
  const [copied, setCopied] = useState(false);
  const [citationsExpanded, setCitationsExpanded] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const formatContent = (content: string) => {
    // Simple markdown rendering for bold, italic, and lists
    return content
      .split('\n')
      .map((line, index) => {
        // Bold: **text**
        line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Italic: *text*
        line = line.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // List items: - text or * text
        if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
          return `<li key="${index}">${line.substring(2)}</li>`;
        }

        return `<p key="${index}">${line}</p>`;
      })
      .join('');
  };

  if (message.role === 'student') {
    return (
      <div className="flex justify-end mb-4 animate-fadeIn">
        <div className="max-w-[80%] md:max-w-[70%]">
          <div className="bg-blue-100 text-gray-900 rounded-lg px-4 py-3 shadow-sm">
            <div className="whitespace-pre-wrap break-words">{message.content}</div>
          </div>
          <div className="text-xs text-gray-500 mt-1 text-right">
            {format(message.timestamp, 'HH:mm')}
          </div>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex justify-start mb-4 animate-fadeIn">
      <div className="max-w-[80%] md:max-w-[70%]">
        <div className="bg-gray-100 text-gray-900 rounded-lg px-4 py-3 shadow-sm">
          <div
            className="prose prose-sm max-w-none whitespace-pre-wrap break-words"
            dangerouslySetInnerHTML={{ __html: formatContent(message.content) }}
          />

          {message.citations && message.citations.length > 0 && (
            <div className="mt-4 pt-3 border-t border-gray-300">
              <button
                onClick={() => setCitationsExpanded(!citationsExpanded)}
                className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900 mb-2"
                aria-label={citationsExpanded ? 'Fela heimildir' : 'Sjá heimildir'}
              >
                {citationsExpanded ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
                Heimildir ({message.citations.length})
              </button>

              {citationsExpanded && (
                <div className="space-y-2 mt-2">
                  {message.citations.map((citation, index) => (
                    <CitationCard key={index} citation={citation} />
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="flex items-center justify-between mt-3 pt-2 border-t border-gray-300">
            <div className="text-xs text-gray-500">
              {format(message.timestamp, 'HH:mm')}
            </div>

            <button
              onClick={handleCopy}
              className="flex items-center gap-1 text-xs text-gray-600 hover:text-gray-900 transition-colors"
              aria-label="Afrita texta"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3" />
                  Afritað
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  Afrita
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
