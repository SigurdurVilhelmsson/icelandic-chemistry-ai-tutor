/**
 * Navigation utilities for Kvenno structure
 */

/**
 * Detect which year section the app is deployed to based on URL path
 * Returns '1', '2', '3', or undefined if not in a year section
 */
export function detectYearFromPath(): '1' | '2' | '3' | undefined {
  const path = window.location.pathname;

  if (path.includes('/1-ar/')) return '1';
  if (path.includes('/2-ar/')) return '2';
  if (path.includes('/3-ar/')) return '3';

  return undefined;
}

/**
 * Get the hub path for a given year
 */
export function getHubPath(year?: '1' | '2' | '3'): string {
  if (!year) return '/';
  return `/${year}-ar/`;
}

/**
 * Get the app path for a given year
 */
export function getAppPath(year?: '1' | '2' | '3'): string {
  if (!year) return '/ai-tutor/';
  return `/${year}-ar/ai-tutor/`;
}
