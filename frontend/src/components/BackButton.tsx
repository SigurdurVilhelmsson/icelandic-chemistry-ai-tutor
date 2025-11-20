/**
 * Back Button Component
 * Navigation button to return to parent hub
 */

import React from 'react';
import { ArrowLeft } from 'lucide-react';

interface BackButtonProps {
  year?: '1' | '2' | '3';
}

export function BackButton({ year }: BackButtonProps) {
  // Determine back path
  const backPath = year ? `/${year}-ar/` : '/';
  const backLabel = year ? `Til baka í ${year}. ár` : 'Til baka';

  return (
    <a
      href={backPath}
      className="inline-flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all hover:opacity-80"
      style={{
        border: '2px solid #f36b22',
        color: '#f36b22'
      }}
      aria-label={backLabel}
    >
      <ArrowLeft className="w-4 h-4" />
      <span>{backLabel}</span>
    </a>
  );
}
