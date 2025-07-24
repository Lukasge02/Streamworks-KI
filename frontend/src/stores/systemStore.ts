/**
 * System Store - Manages health status, monitoring, and system alerts
 */

import { create } from 'zustand';
import { subscribeWithSelector, devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type { 
  SystemStatus, 
  HealthCheck, 
  SystemMetrics,
  SystemAlert 
} from '../types/api';
import { streamWorksAPI } from '../services/api';

interface SystemStore {
  // State
  systemStatus: SystemStatus | null;
  healthChecks: Record<string, HealthCheck>;
  metrics: SystemMetrics | null;
  alerts: SystemAlert[];
  isConnected: boolean;
  lastUpdate: string | null;
  isLoading: boolean;
  error: string | null;
  
  // WebSocket state
  wsConnected: boolean;
  reconnectAttempts: number;
  maxReconnectAttempts: number;
  
  // Actions
  loadSystemStatus: () => Promise<void>;
  loadHealthChecks: (service?: string) => Promise<void>;
  loadMetrics: () => Promise<void>;
  acknowledgeAlert: (alertId: string) => void;
  clearAlert: (alertId: string) => void;
  clearAllAlerts: () => void;
  
  // WebSocket actions
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
  handleSystemAlert: (alert: SystemAlert) => void;
  handleMetricsUpdate: (metrics: SystemMetrics) => void;
  
  // Utility actions
  startHealthMonitoring: () => void;
  stopHealthMonitoring: () => void;
  clearError: () => void;
}

let healthMonitorInterval: NodeJS.Timeout | null = null;
let wsUnsubscribers: (() => void)[] = [];

export const useSystemStore = create<SystemStore>()(
  devtools(
    subscribeWithSelector(
      immer((set, get) => ({
        // Initial state
        systemStatus: null,
        healthChecks: {},
        metrics: null,
        alerts: [],
        isConnected: true,
        lastUpdate: null,
        isLoading: false,
        error: null,
        wsConnected: false,
        reconnectAttempts: 0,
        maxReconnectAttempts: 5,

        // Actions
        loadSystemStatus: async () => {
          set((draft) => {
            draft.isLoading = true;
            draft.error = null;
          });

          try {
            const response = await streamWorksAPI.getSystemStatus();
            
            set((draft) => {
              draft.systemStatus = response.data;
              draft.isConnected = true;
              draft.lastUpdate = new Date().toISOString();
              draft.isLoading = false;
              draft.reconnectAttempts = 0;
            });
          } catch (error) {
            set((draft) => {
              draft.error = error instanceof Error ? error.message : 'Failed to load system status';
              draft.isConnected = false;
              draft.isLoading = false;
              draft.reconnectAttempts += 1;
            });
          }
        },

        loadHealthChecks: async (service) => {
          set((draft) => {
            draft.isLoading = true;
            draft.error = null;
          });

          try {
            const response = await streamWorksAPI.getHealthCheck(service);
            
            set((draft) => {
              if (Array.isArray(response.data)) {
                // Multiple health checks
                response.data.forEach(check => {
                  draft.healthChecks[check.service] = check;
                });
              } else {
                // Single health check
                draft.healthChecks[response.data.service] = response.data;
              }
              
              draft.isConnected = true;
              draft.lastUpdate = new Date().toISOString();
              draft.isLoading = false;
            });
          } catch (error) {
            set((draft) => {
              draft.error = error instanceof Error ? error.message : 'Failed to load health checks';
              draft.isConnected = false;
              draft.isLoading = false;
            });
          }
        },

        loadMetrics: async () => {
          try {
            const response = await streamWorksAPI.getSystemMetrics();
            
            set((draft) => {
              draft.metrics = response.data;
              draft.lastUpdate = new Date().toISOString();
            });
          } catch (error) {
            console.warn('Failed to load metrics:', error);
            // Don't set error for metrics as it's non-critical
          }
        },

        acknowledgeAlert: (alertId) => {
          set((draft) => {
            const alert = draft.alerts.find(a => a.id === alertId);
            if (alert) {
              alert.acknowledged = true;
              alert.timestamp = new Date().toISOString();
            }
          });
        },

        clearAlert: (alertId) => {
          set((draft) => {
            draft.alerts = draft.alerts.filter(a => a.id !== alertId);
          });
        },

        clearAllAlerts: () => {
          set((draft) => {
            draft.alerts = [];
          });
        },

        // WebSocket actions
        connectWebSocket: () => {
          if (get().wsConnected) return;

          try {
            // Subscribe to system alerts
            const alertUnsubscriber = streamWorksAPI.subscribeToSystemAlerts((alert) => {
              get().handleSystemAlert(alert);
            });
            
            wsUnsubscribers.push(alertUnsubscriber);

            set((draft) => {
              draft.wsConnected = true;
              draft.reconnectAttempts = 0;
            });
          } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            
            // Attempt reconnection
            const { reconnectAttempts, maxReconnectAttempts } = get();
            if (reconnectAttempts < maxReconnectAttempts) {
              setTimeout(() => {
                set((draft) => {
                  draft.reconnectAttempts += 1;
                });
                get().connectWebSocket();
              }, Math.pow(2, reconnectAttempts) * 1000); // Exponential backoff
            }
          }
        },

        disconnectWebSocket: () => {
          wsUnsubscribers.forEach(unsubscribe => unsubscribe());
          wsUnsubscribers = [];
          
          set((draft) => {
            draft.wsConnected = false;
          });
        },

        handleSystemAlert: (alert) => {
          set((draft) => {
            // Check if alert already exists
            const existingIndex = draft.alerts.findIndex(a => a.id === alert.id);
            
            if (existingIndex !== -1) {
              // Update existing alert
              draft.alerts[existingIndex] = alert;
            } else {
              // Add new alert
              draft.alerts.unshift(alert);
              
              // Limit to 50 alerts
              if (draft.alerts.length > 50) {
                draft.alerts = draft.alerts.slice(0, 50);
              }
            }
          });
        },

        handleMetricsUpdate: (metrics) => {
          set((draft) => {
            draft.metrics = metrics;
            draft.lastUpdate = new Date().toISOString();
          });
        },

        // Utility actions
        startHealthMonitoring: () => {
          if (healthMonitorInterval) return;

          // Initial load
          get().loadSystemStatus();
          get().loadHealthChecks();
          get().loadMetrics();
          get().connectWebSocket();

          // Set up periodic updates
          healthMonitorInterval = setInterval(() => {
            const store = get();
            
            // Only update if connected
            if (store.isConnected) {
              store.loadSystemStatus();
              store.loadMetrics();
            } else {
              // Try to reconnect
              store.loadSystemStatus();
            }
          }, 30000); // Every 30 seconds
        },

        stopHealthMonitoring: () => {
          if (healthMonitorInterval) {
            clearInterval(healthMonitorInterval);
            healthMonitorInterval = null;
          }
          
          get().disconnectWebSocket();
        },

        clearError: () => {
          set((draft) => {
            draft.error = null;
          });
        },
      }))
    ),
    {
      name: 'SystemStore',
    }
  )
);

// Selectors
export const useSystemSelectors = {
  overallHealth: () => {
    const { systemStatus } = useSystemStore();
    return systemStatus?.overall_status || 'unknown';
  },
  
  criticalAlerts: () => {
    const { alerts } = useSystemStore();
    return alerts.filter(alert => 
      alert.level === 'critical' && !alert.acknowledged
    );
  },
  
  unacknowledgedAlerts: () => {
    const { alerts } = useSystemStore();
    return alerts.filter(alert => !alert.acknowledged);
  },
  
  serviceStatus: (serviceName: string) => {
    const { healthChecks } = useSystemStore();
    return healthChecks[serviceName] || null;
  },
  
  isSystemHealthy: () => {
    const { systemStatus } = useSystemStore();
    return systemStatus?.overall_status === 'healthy';
  },
  
  connectionStatus: () => {
    const { isConnected, wsConnected, reconnectAttempts, maxReconnectAttempts } = useSystemStore();
    
    return {
      isConnected,
      wsConnected,
      isReconnecting: reconnectAttempts > 0 && reconnectAttempts < maxReconnectAttempts,
      hasMaxReconnectAttemptsReached: reconnectAttempts >= maxReconnectAttempts,
    };
  },
  
  systemPerformance: () => {
    const { metrics } = useSystemStore();
    
    if (!metrics) return null;
    
    return {
      cpu: metrics.cpu_usage,
      memory: metrics.memory_usage,
      disk: metrics.disk_usage,
      connections: metrics.active_connections,
      requestsPerMinute: metrics.requests_per_minute,
      errorRate: metrics.error_rate,
    };
  },
};

// Auto-start monitoring when store is created
useSystemStore.getState().startHealthMonitoring();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  useSystemStore.getState().stopHealthMonitoring();
});