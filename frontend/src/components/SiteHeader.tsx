/**
 * Site Header Component
 * Consistent header for kvenno.app following design standards
 */

import React from 'react';
import { UserCog, Info } from 'lucide-react';

export function SiteHeader() {
  const handleAdminClick = () => {
    // TODO: Implement admin authentication flow
    console.log('Admin clicked');
  };

  const handleInfoClick = () => {
    // TODO: Implement info/help modal or page
    console.log('Info clicked');
  };

  return (
    <header className="site-header bg-white border-b border-gray-200 shadow-sm" style={{ height: '60px' }}>
      <div className="header-content h-full max-w-screen-2xl mx-auto px-4 flex items-center justify-between">
        {/* Site Logo/Name - Links to home */}
        <a
          href="/"
          className="site-logo text-xl font-bold hover:opacity-80 transition-opacity flex items-center gap-2"
          style={{ color: '#f36b22' }}
        >
          Kvenno Efnafræði
        </a>

        {/* Header Actions */}
        <div className="header-actions flex items-center gap-3">
          <button
            onClick={handleAdminClick}
            className="header-btn px-4 py-2 rounded-lg font-medium transition-all hover:bg-gray-50 flex items-center gap-2"
            style={{
              border: '2px solid #f36b22',
              color: '#f36b22'
            }}
            aria-label="Admin aðgangur"
          >
            <UserCog className="w-4 h-4" />
            <span className="hidden sm:inline">Admin</span>
          </button>

          <button
            onClick={handleInfoClick}
            className="header-btn px-4 py-2 rounded-lg font-medium transition-all hover:bg-gray-50 flex items-center gap-2"
            style={{
              border: '2px solid #f36b22',
              color: '#f36b22'
            }}
            aria-label="Upplýsingar"
          >
            <Info className="w-4 h-4" />
            <span className="hidden sm:inline">Info</span>
          </button>
        </div>
      </div>
    </header>
  );
}
