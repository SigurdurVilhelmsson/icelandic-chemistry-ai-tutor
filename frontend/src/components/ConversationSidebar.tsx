/**
 * Conversation Sidebar Component
 * Lists all saved conversations with load/delete actions
 */

import React, { useState, useEffect } from 'react';
import { MessageSquare, Trash2, Plus, X } from 'lucide-react';
import { format } from 'date-fns';
import { is } from 'date-fns/locale';
import { listConversations, deleteConversation as deleteConversationStorage } from '../utils/storage';
import { ConversationSummary } from '../types';

interface ConversationSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onLoadConversation: (sessionId: string) => void;
  onNewConversation: () => void;
  currentSessionId: string;
}

export function ConversationSidebar({
  isOpen,
  onClose,
  onLoadConversation,
  onNewConversation,
  currentSessionId
}: ConversationSidebarProps) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  const loadConversations = () => {
    setConversations(listConversations());
  };

  useEffect(() => {
    if (isOpen) {
      loadConversations();
    }
  }, [isOpen]);

  const handleDelete = (sessionId: string) => {
    deleteConversationStorage(sessionId);
    loadConversations();
    setConfirmDelete(null);
  };

  const handleLoad = (sessionId: string) => {
    onLoadConversation(sessionId);
    onClose();
  };

  const handleNew = () => {
    onNewConversation();
    onClose();
  };

  if (!isOpen) {
    return null;
  }

  return (
    <>
      {/* Overlay for mobile */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Sidebar */}
      <div
        className={`fixed md:relative top-0 left-0 h-full w-80 bg-white border-r border-gray-300 z-50 transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-300">
            <h2 className="text-lg font-semibold text-gray-900">Samtöl</h2>
            <button
              onClick={onClose}
              className="md:hidden p-1 hover:bg-gray-100 rounded"
              aria-label="Loka"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* New Conversation Button */}
          <div className="p-4 border-b border-gray-200">
            <button
              onClick={handleNew}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              aria-label="Nýtt samtal"
            >
              <Plus className="w-4 h-4" />
              Nýtt samtal
            </button>
          </div>

          {/* Conversation List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {conversations.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Engin samtöl enn</p>
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.sessionId}
                  className={`border rounded-lg p-3 hover:bg-gray-50 transition-colors ${
                    conv.sessionId === currentSessionId
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300'
                  }`}
                >
                  <button
                    onClick={() => handleLoad(conv.sessionId)}
                    className="w-full text-left"
                  >
                    <div className="flex items-start gap-2">
                      <MessageSquare className="w-4 h-4 text-gray-400 mt-1 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-900 truncate">
                          {conv.firstQuestion.length > 50
                            ? conv.firstQuestion.substring(0, 50) + '...'
                            : conv.firstQuestion}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {format(conv.lastUpdated, 'dd.MM.yyyy HH:mm')}
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          {conv.messageCount} skilaboð
                        </div>
                      </div>
                    </div>
                  </button>

                  {confirmDelete === conv.sessionId ? (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <p className="text-xs text-gray-600 mb-2">Ertu viss?</p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleDelete(conv.sessionId)}
                          className="flex-1 px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                        >
                          Já, eyða
                        </button>
                        <button
                          onClick={() => setConfirmDelete(null)}
                          className="flex-1 px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                        >
                          Hætta við
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => setConfirmDelete(conv.sessionId)}
                      className="mt-2 w-full flex items-center justify-center gap-1 text-xs text-red-600 hover:text-red-800"
                      aria-label="Eyða samtali"
                    >
                      <Trash2 className="w-3 h-3" />
                      Eyða
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </>
  );
}
