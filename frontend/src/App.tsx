/**
 * Main App Component
 */

import React from 'react';
import { ChatProvider, useChat } from './contexts/ChatContext';
import { ChatInterface } from './components/ChatInterface';
import { ToastContainer } from './components/Toast';
import { SiteHeader } from './components/SiteHeader';
import { Breadcrumbs } from './components/Breadcrumbs';
import { detectYearFromPath } from './utils/navigation';

function AppContent() {
  const { toasts, dismissToast } = useChat();
  const currentYear = detectYearFromPath();

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Site-wide header */}
      <SiteHeader />

      {/* Breadcrumbs */}
      <Breadcrumbs year={currentYear} appName="AI Kennsluaðili" />

      {/* Main content */}
      <div className="flex-1 overflow-hidden">
        <ChatInterface currentYear={currentYear} />
      </div>

      {/* Toast notifications */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
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
