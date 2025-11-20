/**
 * Breadcrumbs Component
 * Shows navigation hierarchy according to Kvenno structure
 */

import React from 'react';
import { ChevronRight } from 'lucide-react';

interface BreadcrumbsProps {
  year?: '1' | '2' | '3';
  appName?: string;
}

export function Breadcrumbs({ year, appName = 'AI Kennsluaðili' }: BreadcrumbsProps) {
  // Determine year label and path
  const yearLabel = year ? `${year}. ár` : null;
  const yearPath = year ? `/${year}-ar/` : null;

  return (
    <nav aria-label="Breadcrumb" className="py-3 px-4 bg-gray-50 border-b border-gray-200">
      <ol className="flex items-center gap-2 text-sm text-gray-600 max-w-screen-2xl mx-auto">
        {/* Home */}
        <li>
          <a
            href="/"
            className="hover:text-gray-900 transition-colors"
            style={{ color: '#666' }}
          >
            Heim
          </a>
        </li>

        {/* Year Section */}
        {yearLabel && yearPath && (
          <>
            <li>
              <ChevronRight className="w-4 h-4" />
            </li>
            <li>
              <a
                href={yearPath}
                className="hover:text-gray-900 transition-colors"
                style={{ color: '#666' }}
              >
                {yearLabel}
              </a>
            </li>
          </>
        )}

        {/* Current App */}
        {appName && (
          <>
            <li>
              <ChevronRight className="w-4 h-4" />
            </li>
            <li className="font-medium text-gray-900" aria-current="page">
              {appName}
            </li>
          </>
        )}
      </ol>
    </nav>
  );
}
