/**
 * CSV export utility for conversations
 * Reuses LabReports pattern
 */

import { Message } from '../types';
import { format } from 'date-fns';

/**
 * Export conversation to CSV format
 */
export function exportConversationToCSV(sessionId: string, messages: Message[]): void {
  try {
    // Create CSV header
    const headers = ['session_id', 'timestamp', 'role', 'content', 'citations'];

    // Create CSV rows
    const rows = messages.map(msg => {
      const citationsStr = msg.citations
        ? JSON.stringify(msg.citations).replace(/"/g, '""')
        : '';

      return [
        sessionId,
        format(msg.timestamp, 'yyyy-MM-dd\'T\'HH:mm:ss'),
        msg.role,
        `"${msg.content.replace(/"/g, '""')}"`,
        `"${citationsStr}"`
      ].join(',');
    });

    // Combine header and rows
    const csvContent = [headers.join(','), ...rows].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `samtal_${sessionId}_${format(new Date(), 'yyyy-MM-dd_HH-mm')}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error exporting conversation:', error);
    throw new Error('Villa kom upp við að flytja út samtal');
  }
}

/**
 * Export conversation to JSON format
 */
export function exportConversationToJSON(sessionId: string, messages: Message[]): void {
  try {
    const data = {
      sessionId,
      exportDate: new Date().toISOString(),
      messages: messages.map(msg => ({
        ...msg,
        timestamp: msg.timestamp.toISOString()
      }))
    };

    const jsonContent = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `samtal_${sessionId}_${format(new Date(), 'yyyy-MM-dd_HH-mm')}.json`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error exporting conversation:', error);
    throw new Error('Villa kom upp við að flytja út samtal');
  }
}

/**
 * Copy conversation to clipboard as text
 */
export function copyConversationToClipboard(messages: Message[]): Promise<void> {
  try {
    const text = messages
      .map(msg => {
        const role = msg.role === 'student' ? 'Spurning' : 'Svar';
        const timestamp = format(msg.timestamp, 'dd.MM.yyyy HH:mm');
        let content = `[${role}] ${timestamp}\n${msg.content}\n`;

        if (msg.citations && msg.citations.length > 0) {
          content += '\nHeimildir:\n';
          msg.citations.forEach(cit => {
            content += `- ${cit.title} (${cit.chapter}, ${cit.section})\n`;
          });
        }

        return content;
      })
      .join('\n---\n\n');

    return navigator.clipboard.writeText(text);
  } catch (error) {
    console.error('Error copying to clipboard:', error);
    throw new Error('Villa kom upp við að afrita samtal');
  }
}
