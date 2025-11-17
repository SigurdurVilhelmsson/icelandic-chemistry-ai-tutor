/**
 * API Logger Component
 * ====================
 *
 * Pretty API request/response logger for development.
 * Displays API calls in a developer panel with timing and status.
 *
 * Usage:
 *   import { APILogger, useAPILogger } from './dev-tools/frontend/api_logger';
 *
 *   function App() {
 *     const { log } = useAPILogger();
 *
 *     // Log an API call
 *     await log(async () => {
 *       return fetch('/api/ask', {
 *         method: 'POST',
 *         body: JSON.stringify({ question: 'test' })
 *       });
 *     }, { endpoint: '/api/ask', method: 'POST' });
 *
 *     return <APILogger />;
 *   }
 *
 * Features:
 * - Log all API requests and responses
 * - Display request/response bodies
 * - Show timing information
 * - Color-coded status codes
 * - Export logs as JSON
 * - Clear logs
 * - Filter by endpoint or status
 */

import React, { createContext, useContext, useState, useCallback } from 'react';

// Types
interface APILogEntry {
  id: string;
  timestamp: Date;
  endpoint: string;
  method: string;
  requestBody?: any;
  responseStatus?: number;
  responseBody?: any;
  duration?: number;
  error?: string;
}

interface APILoggerContextValue {
  logs: APILogEntry[];
  log: (fn: () => Promise<Response>, metadata: Partial<APILogEntry>) => Promise<Response>;
  clearLogs: () => void;
  exportLogs: () => void;
}

// Context
const APILoggerContext = createContext<APILoggerContextValue | undefined>(undefined);

// Provider
export function APILoggerProvider({ children }: { children: React.ReactNode }) {
  const [logs, setLogs] = useState<APILogEntry[]>([]);

  const log = useCallback(async (
    fn: () => Promise<Response>,
    metadata: Partial<APILogEntry>
  ): Promise<Response> => {
    const id = `${Date.now()}-${Math.random()}`;
    const timestamp = new Date();
    const startTime = performance.now();

    const entry: APILogEntry = {
      id,
      timestamp,
      endpoint: metadata.endpoint || 'unknown',
      method: metadata.method || 'GET',
      requestBody: metadata.requestBody,
    };

    try {
      const response = await fn();
      const endTime = performance.now();
      const duration = Math.round(endTime - startTime);

      // Clone response to read body
      const clonedResponse = response.clone();
      let responseBody;
      try {
        responseBody = await clonedResponse.json();
      } catch {
        responseBody = await clonedResponse.text();
      }

      const completedEntry: APILogEntry = {
        ...entry,
        responseStatus: response.status,
        responseBody,
        duration,
      };

      setLogs(prev => [completedEntry, ...prev]);

      return response;
    } catch (error) {
      const endTime = performance.now();
      const duration = Math.round(endTime - startTime);

      const errorEntry: APILogEntry = {
        ...entry,
        duration,
        error: error instanceof Error ? error.message : String(error),
      };

      setLogs(prev => [errorEntry, ...prev]);

      throw error;
    }
  }, []);

  const clearLogs = useCallback(() => {
    setLogs([]);
  }, []);

  const exportLogs = useCallback(() => {
    const dataStr = JSON.stringify(logs, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    const exportFileDefaultName = `api-logs-${new Date().toISOString()}.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  }, [logs]);

  return (
    <APILoggerContext.Provider value={{ logs, log, clearLogs, exportLogs }}>
      {children}
    </APILoggerContext.Provider>
  );
}

// Hook
export function useAPILogger() {
  const context = useContext(APILoggerContext);
  if (!context) {
    throw new Error('useAPILogger must be used within APILoggerProvider');
  }
  return context;
}

// Component
export function APILogger() {
  const { logs, clearLogs, exportLogs } = useAPILogger();
  const [filter, setFilter] = useState('');
  const [expandedLog, setExpandedLog] = useState<string | null>(null);

  const filteredLogs = logs.filter(log => {
    if (!filter) return true;
    return (
      log.endpoint.toLowerCase().includes(filter.toLowerCase()) ||
      log.method.toLowerCase().includes(filter.toLowerCase())
    );
  });

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>API Logger</h3>
        <div style={styles.controls}>
          <input
            type="text"
            placeholder="Filter by endpoint or method..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={styles.filterInput}
          />
          <button onClick={exportLogs} style={styles.button}>
            Export
          </button>
          <button onClick={clearLogs} style={styles.clearButton}>
            Clear
          </button>
        </div>
      </div>

      <div style={styles.logsContainer}>
        {filteredLogs.length === 0 ? (
          <div style={styles.emptyState}>
            No API calls logged yet
          </div>
        ) : (
          filteredLogs.map(log => (
            <LogEntry
              key={log.id}
              log={log}
              expanded={expandedLog === log.id}
              onToggle={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
            />
          ))
        )}
      </div>
    </div>
  );
}

// Log Entry Component
function LogEntry({
  log,
  expanded,
  onToggle
}: {
  log: APILogEntry;
  expanded: boolean;
  onToggle: () => void;
}) {
  const statusColor = getStatusColor(log.responseStatus);
  const timeStr = log.timestamp.toLocaleTimeString();

  return (
    <div style={styles.logEntry}>
      <div style={styles.logHeader} onClick={onToggle}>
        <span style={styles.timestamp}>[{timeStr}]</span>
        <span style={styles.method}>{log.method}</span>
        <span style={styles.endpoint}>{log.endpoint}</span>
        {log.responseStatus && (
          <span style={{ ...styles.status, color: statusColor }}>
            {log.responseStatus}
          </span>
        )}
        {log.duration && (
          <span style={styles.duration}>({log.duration}ms)</span>
        )}
        {log.error && (
          <span style={styles.error}>ERROR</span>
        )}
        <span style={styles.expandIcon}>{expanded ? '▼' : '▶'}</span>
      </div>

      {expanded && (
        <div style={styles.logDetails}>
          {log.requestBody && (
            <div style={styles.section}>
              <div style={styles.sectionTitle}>Request</div>
              <pre style={styles.code}>
                {JSON.stringify(log.requestBody, null, 2)}
              </pre>
            </div>
          )}

          {log.responseBody && (
            <div style={styles.section}>
              <div style={styles.sectionTitle}>
                Response {log.responseStatus && `(${log.responseStatus})`}
              </div>
              <pre style={styles.code}>
                {typeof log.responseBody === 'string'
                  ? log.responseBody
                  : JSON.stringify(log.responseBody, null, 2)}
              </pre>
            </div>
          )}

          {log.error && (
            <div style={styles.section}>
              <div style={styles.sectionTitle}>Error</div>
              <pre style={styles.errorCode}>
                {log.error}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Helper function
function getStatusColor(status?: number): string {
  if (!status) return '#999';
  if (status >= 200 && status < 300) return '#27ae60';
  if (status >= 300 && status < 400) return '#3498db';
  if (status >= 400 && status < 500) return '#e67e22';
  if (status >= 500) return '#e74c3c';
  return '#999';
}

// Styles
const styles = {
  container: {
    fontFamily: 'monospace',
    fontSize: '12px',
    backgroundColor: '#1e1e1e',
    color: '#d4d4d4',
    padding: '10px',
    borderRadius: '4px',
    maxHeight: '400px',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column' as const,
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px',
    paddingBottom: '10px',
    borderBottom: '1px solid #333',
  },
  title: {
    margin: 0,
    fontSize: '14px',
    fontWeight: 'bold',
  },
  controls: {
    display: 'flex',
    gap: '8px',
    alignItems: 'center',
  },
  filterInput: {
    padding: '4px 8px',
    fontSize: '11px',
    backgroundColor: '#2d2d2d',
    border: '1px solid #444',
    borderRadius: '3px',
    color: '#d4d4d4',
    outline: 'none',
  },
  button: {
    padding: '4px 12px',
    fontSize: '11px',
    backgroundColor: '#007acc',
    border: 'none',
    borderRadius: '3px',
    color: 'white',
    cursor: 'pointer',
  },
  clearButton: {
    padding: '4px 12px',
    fontSize: '11px',
    backgroundColor: '#e74c3c',
    border: 'none',
    borderRadius: '3px',
    color: 'white',
    cursor: 'pointer',
  },
  logsContainer: {
    overflowY: 'auto' as const,
    flex: 1,
  },
  emptyState: {
    textAlign: 'center' as const,
    padding: '20px',
    color: '#666',
  },
  logEntry: {
    marginBottom: '8px',
    backgroundColor: '#2d2d2d',
    borderRadius: '3px',
    overflow: 'hidden',
  },
  logHeader: {
    padding: '8px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    cursor: 'pointer',
    userSelect: 'none' as const,
  },
  timestamp: {
    color: '#888',
  },
  method: {
    fontWeight: 'bold',
    color: '#569cd6',
    minWidth: '50px',
  },
  endpoint: {
    flex: 1,
    color: '#dcdcaa',
  },
  status: {
    fontWeight: 'bold',
    minWidth: '30px',
  },
  duration: {
    color: '#888',
  },
  error: {
    color: '#e74c3c',
    fontWeight: 'bold',
  },
  expandIcon: {
    color: '#888',
    fontSize: '10px',
  },
  logDetails: {
    padding: '8px',
    borderTop: '1px solid #333',
    backgroundColor: '#252526',
  },
  section: {
    marginBottom: '12px',
  },
  sectionTitle: {
    color: '#888',
    marginBottom: '4px',
    fontSize: '11px',
    textTransform: 'uppercase' as const,
  },
  code: {
    margin: 0,
    padding: '8px',
    backgroundColor: '#1e1e1e',
    borderRadius: '3px',
    overflow: 'auto',
    maxHeight: '200px',
    fontSize: '11px',
  },
  errorCode: {
    margin: 0,
    padding: '8px',
    backgroundColor: '#3c1f1f',
    borderRadius: '3px',
    color: '#f48771',
    fontSize: '11px',
  },
};

// Utility function to wrap fetch calls
export function createLoggedFetch(log: APILoggerContextValue['log']) {
  return async function loggedFetch(
    input: RequestInfo | URL,
    init?: RequestInit
  ): Promise<Response> {
    const url = input instanceof Request ? input.url : input.toString();
    const method = init?.method || (input instanceof Request ? input.method : 'GET');

    let requestBody;
    if (init?.body) {
      try {
        requestBody = JSON.parse(init.body.toString());
      } catch {
        requestBody = init.body.toString();
      }
    }

    return log(
      () => fetch(input, init),
      {
        endpoint: url,
        method,
        requestBody,
      }
    );
  };
}
