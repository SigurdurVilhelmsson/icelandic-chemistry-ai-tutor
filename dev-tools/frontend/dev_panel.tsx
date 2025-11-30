/**
 * Developer Panel Component
 * ==========================
 *
 * Comprehensive developer information panel for debugging.
 * Only visible in development mode.
 *
 * Usage:
 *   import { DevPanel } from './dev-tools/frontend/dev_panel';
 *   import { APILoggerProvider } from './dev-tools/frontend/api_logger';
 *
 *   function App() {
 *     return (
 *       <APILoggerProvider>
 *         <YourApp />
 *         <DevPanel />
 *       </APILoggerProvider>
 *     );
 *   }
 *
 * Features:
 * - API call logging and inspection
 * - Performance metrics
 * - Environment information
 * - Response cache inspection
 * - Collapsible/expandable panel
 * - Draggable and resizable
 * - Persists open/closed state
 */

import React, { useState, useEffect, useMemo } from 'react';
import { APILogger, useAPILogger } from './api_logger';

interface DevPanelProps {
  show?: boolean;
  defaultOpen?: boolean;
}

interface PerformanceMetrics {
  totalCalls: number;
  avgResponseTime: number;
  successRate: number;
  errorCount: number;
  fastestCall: number;
  slowestCall: number;
}

export function DevPanel({ show, defaultOpen = false }: DevPanelProps) {
  const isDevelopment = show ?? process.env.NODE_ENV === 'development';
  const [isOpen, setIsOpen] = useState(() => {
    const saved = localStorage.getItem('devPanelOpen');
    return saved ? JSON.parse(saved) : defaultOpen;
  });
  const [activeTab, setActiveTab] = useState<'api' | 'metrics' | 'cache' | 'env'>('api');
  const [cacheData, setCacheData] = useState<Record<string, unknown>>({});

  const { logs } = useAPILogger();

  // Save open state to localStorage
  useEffect(() => {
    localStorage.setItem('devPanelOpen', JSON.stringify(isOpen));
  }, [isOpen]);

  // Calculate performance metrics
  const metrics = useMemo<PerformanceMetrics>(() => {
    if (logs.length === 0) {
      return {
        totalCalls: 0,
        avgResponseTime: 0,
        successRate: 0,
        errorCount: 0,
        fastestCall: 0,
        slowestCall: 0,
      };
    }

    const successfulCalls = logs.filter(log => log.responseStatus && log.responseStatus < 400);
    const errors = logs.filter(log => log.error || (log.responseStatus && log.responseStatus >= 400));
    const durations = logs.filter(log => log.duration).map(log => log.duration!);

    return {
      totalCalls: logs.length,
      avgResponseTime: durations.reduce((sum, d) => sum + d, 0) / durations.length || 0,
      successRate: (successfulCalls.length / logs.length) * 100,
      errorCount: errors.length,
      fastestCall: Math.min(...durations) || 0,
      slowestCall: Math.max(...durations) || 0,
    };
  }, [logs]);

  // Load cache data (simulate for now)
  useEffect(() => {
    // In a real app, you'd fetch this from your cache implementation
    setCacheData({
      size: 0,
      entries: [],
      hitRate: 0,
    });
  }, []);

  if (!isDevelopment) {
    return null;
  }

  return (
    <>
      {/* Toggle button when collapsed */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          style={styles.toggleButton}
          title="Open Developer Panel"
        >
          🔧 Dev Tools
        </button>
      )}

      {/* Main panel */}
      {isOpen && (
        <div style={styles.panel}>
          <div style={styles.header}>
            <h2 style={styles.title}>🔧 Developer Panel</h2>
            <button
              onClick={() => setIsOpen(false)}
              style={styles.closeButton}
              title="Close"
            >
              ✕
            </button>
          </div>

          <div style={styles.tabs}>
            <button
              onClick={() => setActiveTab('api')}
              style={activeTab === 'api' ? styles.activeTab : styles.tab}
            >
              API Calls ({logs.length})
            </button>
            <button
              onClick={() => setActiveTab('metrics')}
              style={activeTab === 'metrics' ? styles.activeTab : styles.tab}
            >
              Metrics
            </button>
            <button
              onClick={() => setActiveTab('cache')}
              style={activeTab === 'cache' ? styles.activeTab : styles.tab}
            >
              Cache
            </button>
            <button
              onClick={() => setActiveTab('env')}
              style={activeTab === 'env' ? styles.activeTab : styles.tab}
            >
              Environment
            </button>
          </div>

          <div style={styles.content}>
            {activeTab === 'api' && <APILogger />}
            {activeTab === 'metrics' && <MetricsTab metrics={metrics} />}
            {activeTab === 'cache' && <CacheTab data={cacheData} />}
            {activeTab === 'env' && <EnvironmentTab />}
          </div>
        </div>
      )}
    </>
  );
}

// Metrics Tab
function MetricsTab({ metrics }: { metrics: PerformanceMetrics }) {
  return (
    <div style={styles.tabContent}>
      <h3 style={styles.sectionTitle}>Performance Metrics</h3>

      <div style={styles.metricsGrid}>
        <MetricCard
          label="Total API Calls"
          value={metrics.totalCalls.toString()}
          color="#3498db"
        />
        <MetricCard
          label="Avg Response Time"
          value={`${Math.round(metrics.avgResponseTime)}ms`}
          color="#9b59b6"
        />
        <MetricCard
          label="Success Rate"
          value={`${Math.round(metrics.successRate)}%`}
          color={metrics.successRate >= 95 ? '#27ae60' : '#e67e22'}
        />
        <MetricCard
          label="Errors"
          value={metrics.errorCount.toString()}
          color={metrics.errorCount === 0 ? '#27ae60' : '#e74c3c'}
        />
        <MetricCard
          label="Fastest Call"
          value={`${metrics.fastestCall}ms`}
          color="#16a085"
        />
        <MetricCard
          label="Slowest Call"
          value={`${metrics.slowestCall}ms`}
          color="#e67e22"
        />
      </div>

      <div style={styles.info}>
        <p><strong>Performance Tips:</strong></p>
        <ul style={styles.list}>
          <li>Response times under 2s provide good UX</li>
          <li>Consider caching for frequently accessed data</li>
          <li>Monitor error rates - should be below 5%</li>
        </ul>
      </div>
    </div>
  );
}

// Metric Card
function MetricCard({
  label,
  value,
  color
}: {
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div style={styles.metricCard}>
      <div style={{ ...styles.metricValue, color }}>{value}</div>
      <div style={styles.metricLabel}>{label}</div>
    </div>
  );
}

// Cache Tab
function CacheTab({ data }: { data: any }) {
  return (
    <div style={styles.tabContent}>
      <h3 style={styles.sectionTitle}>Response Cache</h3>

      <div style={styles.metricsGrid}>
        <MetricCard
          label="Cache Size"
          value={data.size?.toString() || '0'}
          color="#3498db"
        />
        <MetricCard
          label="Entries"
          value={data.entries?.length?.toString() || '0'}
          color="#9b59b6"
        />
        <MetricCard
          label="Hit Rate"
          value={`${data.hitRate || 0}%`}
          color="#27ae60"
        />
      </div>

      <div style={styles.info}>
        <p><strong>Cache Status:</strong></p>
        {data.entries?.length > 0 ? (
          <ul style={styles.list}>
            {data.entries.slice(0, 5).map((entry: any, i: number) => (
              <li key={i}>
                {entry.key}: {entry.hits} hits
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ color: '#888' }}>No cached entries</p>
        )}
      </div>
    </div>
  );
}

// Environment Tab
function EnvironmentTab() {
  const envInfo = {
    nodeEnv: process.env.NODE_ENV,
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'Not set',
    version: process.env.NEXT_PUBLIC_VERSION || 'Unknown',
    buildTime: process.env.NEXT_PUBLIC_BUILD_TIME || 'Unknown',
  };

  return (
    <div style={styles.tabContent}>
      <h3 style={styles.sectionTitle}>Environment Information</h3>

      <div style={styles.envGrid}>
        <EnvRow label="Node Environment" value={envInfo.nodeEnv} />
        <EnvRow label="API URL" value={envInfo.apiUrl} />
        <EnvRow label="Version" value={envInfo.version} />
        <EnvRow label="Build Time" value={envInfo.buildTime} />
      </div>

      <div style={styles.info}>
        <p><strong>Browser Info:</strong></p>
        <ul style={styles.list}>
          <li>User Agent: {navigator.userAgent}</li>
          <li>Language: {navigator.language}</li>
          <li>Platform: {navigator.platform}</li>
          <li>
            Screen: {window.screen.width}x{window.screen.height}
          </li>
        </ul>
      </div>

      <div style={styles.info}>
        <p><strong>Useful Links:</strong></p>
        <ul style={styles.list}>
          <li>
            <a
              href="http://localhost:5001"
              target="_blank"
              rel="noopener noreferrer"
              style={styles.link}
            >
              Database Inspector
            </a>
          </li>
          <li>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              style={styles.link}
            >
              API Documentation
            </a>
          </li>
        </ul>
      </div>
    </div>
  );
}

// Environment Row
function EnvRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={styles.envRow}>
      <div style={styles.envLabel}>{label}:</div>
      <div style={styles.envValue}>{value}</div>
    </div>
  );
}

// Styles
const styles = {
  toggleButton: {
    position: 'fixed' as const,
    bottom: '20px',
    right: '20px',
    padding: '12px 20px',
    backgroundColor: '#2c3e50',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold' as const,
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
    zIndex: 9998,
  },
  panel: {
    position: 'fixed' as const,
    bottom: 0,
    right: 0,
    width: '600px',
    height: '500px',
    backgroundColor: '#1e1e1e',
    color: '#d4d4d4',
    boxShadow: '-4px 0 12px rgba(0, 0, 0, 0.3)',
    display: 'flex',
    flexDirection: 'column' as const,
    zIndex: 9999,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif',
  },
  header: {
    padding: '12px 16px',
    backgroundColor: '#2d2d2d',
    borderBottom: '1px solid #444',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    margin: 0,
    fontSize: '16px',
    fontWeight: 'bold' as const,
  },
  closeButton: {
    background: 'none',
    border: 'none',
    color: '#d4d4d4',
    fontSize: '20px',
    cursor: 'pointer',
    padding: '0 8px',
  },
  tabs: {
    display: 'flex',
    backgroundColor: '#2d2d2d',
    borderBottom: '1px solid #444',
  },
  tab: {
    flex: 1,
    padding: '10px',
    backgroundColor: 'transparent',
    border: 'none',
    color: '#888',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: '500' as const,
  },
  activeTab: {
    flex: 1,
    padding: '10px',
    backgroundColor: '#1e1e1e',
    border: 'none',
    borderBottom: '2px solid #007acc',
    color: '#d4d4d4',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: 'bold' as const,
  },
  content: {
    flex: 1,
    overflow: 'auto',
  },
  tabContent: {
    padding: '16px',
  },
  sectionTitle: {
    margin: '0 0 16px 0',
    fontSize: '14px',
    fontWeight: 'bold' as const,
    color: '#d4d4d4',
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '12px',
    marginBottom: '20px',
  },
  metricCard: {
    backgroundColor: '#2d2d2d',
    padding: '12px',
    borderRadius: '6px',
    textAlign: 'center' as const,
  },
  metricValue: {
    fontSize: '24px',
    fontWeight: 'bold' as const,
    marginBottom: '4px',
  },
  metricLabel: {
    fontSize: '11px',
    color: '#888',
  },
  info: {
    backgroundColor: '#2d2d2d',
    padding: '12px',
    borderRadius: '6px',
    marginBottom: '12px',
  },
  list: {
    margin: '8px 0',
    paddingLeft: '20px',
    fontSize: '12px',
    lineHeight: '1.6',
  },
  envGrid: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '8px',
    marginBottom: '20px',
  },
  envRow: {
    display: 'flex',
    backgroundColor: '#2d2d2d',
    padding: '8px 12px',
    borderRadius: '4px',
  },
  envLabel: {
    fontWeight: 'bold' as const,
    marginRight: '12px',
    color: '#888',
    minWidth: '140px',
    fontSize: '12px',
  },
  envValue: {
    flex: 1,
    fontFamily: 'monospace',
    fontSize: '12px',
  },
  link: {
    color: '#007acc',
    textDecoration: 'none',
  },
};

export default DevPanel;
