/**
 * Chat Interface Component
 * Main container for the chat application
 */

import React, { useEffect, useRef, useState } from 'react';
import {
  Menu,
  Download,
  Trash2,
  Loader2,
  FlaskConical
} from 'lucide-react';
import { useChat } from '../contexts/ChatContext';
import { Message } from './Message';
import { ChatInput } from './ChatInput';
import { ConversationSidebar } from './ConversationSidebar';
import { Modal } from './Modal';

export function ChatInterface() {
  const {
    messages,
    isLoading,
    sessionId,
    sendMessage,
    loadConversation,
    newConversation,
    clearConversation,
    exportConversation
  } = useChat();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showClearModal, setShowClearModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  const handleClearConversation = () => {
    clearConversation();
    setShowClearModal(false);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <ConversationSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onLoadConversation={loadConversation}
        onNewConversation={newConversation}
        currentSessionId={sessionId}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-white border-b border-gray-300 px-4 py-3 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors md:hidden"
              aria-label="Opna valmynd"
            >
              <Menu className="w-5 h-5" />
            </button>

            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="hidden md:block p-2 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Opna/Loka hliðarslá"
            >
              <Menu className="w-5 h-5" />
            </button>

            <FlaskConical className="w-6 h-6 text-blue-600" />
            <h1 className="text-lg md:text-xl font-bold text-gray-900">
              Efnafræði Aðstoðarkennari
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={exportConversation}
              disabled={messages.length === 0}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Flytja út samtal"
              title="Flytja út samtal"
            >
              <Download className="w-5 h-5" />
            </button>

            <button
              onClick={() => setShowClearModal(true)}
              disabled={messages.length === 0}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Hreinsa samtal"
              title="Hreinsa samtal"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Messages Area */}
        <div
          ref={messagesContainerRef}
          className="flex-1 overflow-y-auto px-4 py-6"
        >
          <div className="max-w-4xl mx-auto">
            {messages.length === 0 && !isLoading ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-12">
                <FlaskConical className="w-16 h-16 text-blue-600 mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Spurðu mig um efnafræði!
                </h2>
                <p className="text-gray-600 max-w-md">
                  Ég er hér til að hjálpa þér að læra um efnafræði. Spurðu mig um atóm,
                  sameindir, efnahvörf og fleira.
                </p>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <Message key={message.id} message={message} />
                ))}

                {isLoading && (
                  <div className="flex justify-start mb-4">
                    <div className="bg-gray-100 rounded-lg px-4 py-3 shadow-sm">
                      <div className="flex items-center gap-2 text-gray-600">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm">Hugsar...</span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </>
            )}
          </div>
        </div>

        {/* Input Area */}
        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </div>

      {/* Clear Confirmation Modal */}
      <Modal
        isOpen={showClearModal}
        onClose={() => setShowClearModal(false)}
        onConfirm={handleClearConversation}
        title="Hreinsa samtal"
        message="Ertu viss um að þú viljir hreinsa samtalið? Þetta eyðir öllum skilaboðum."
        confirmText="Já, hreinsa"
        cancelText="Hætta við"
      />
    </div>
  );
}
