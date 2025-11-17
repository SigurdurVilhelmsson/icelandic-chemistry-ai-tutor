/**
 * Citation Card Component
 * Displays source information with collapsible full text
 */

import React, { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp } from 'lucide-react';
import { Citation } from '../types';

interface CitationCardProps {
  citation: Citation;
}

export function CitationCard({ citation }: CitationCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const truncatedText = citation.chunk_text.length > 100
    ? citation.chunk_text.substring(0, 100) + '...'
    : citation.chunk_text;

  return (
    <div className="border border-gray-300 rounded-lg p-3 bg-white hover:shadow-md transition-shadow">
      <div className="flex items-start gap-2 mb-2">
        <BookOpen className="w-4 h-4 text-blue-600 mt-1 flex-shrink-0" />
        <div className="flex-1">
          <div className="text-sm font-medium text-gray-900">
            📚 Heimild: {citation.chapter}, {citation.section}
          </div>
          <div className="text-xs text-gray-600 mt-1">
            Titill: {citation.title}
          </div>
        </div>
      </div>

      <div className="text-sm text-gray-700 mt-2">
        {isExpanded ? citation.chunk_text : truncatedText}
      </div>

      {citation.chunk_text.length > 100 && (
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 mt-2 font-medium"
          aria-label={isExpanded ? 'Fela texta' : 'Sjá allan texta'}
        >
          {isExpanded ? (
            <>
              <ChevronUp className="w-3 h-3" />
              Fela texta
            </>
          ) : (
            <>
              <ChevronDown className="w-3 h-3" />
              Sjá allan texta
            </>
          )}
        </button>
      )}
    </div>
  );
}
