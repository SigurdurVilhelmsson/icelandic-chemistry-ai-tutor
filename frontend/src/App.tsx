/**
 * Main App Component
 */

import React from 'react';
import { ChatProvider, useChat } from './contexts/ChatContext';
import { ChatInterface } from './components/ChatInterface';
import { ToastContainer } from './components/Toast';

function AppContent() {
  const { toasts, dismissToast } = useChat();

  return (
    <>
      <ChatInterface />
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </>
  );
}

function App() {
  return (
    <ChatProvider>
      <AppContent />
    </ChatProvider>
  );
}

export default App;
