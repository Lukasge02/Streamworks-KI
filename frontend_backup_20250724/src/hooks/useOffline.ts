import { useState, useEffect, useCallback } from 'react';
import { ConnectionMonitor } from '../utils/errorUtils';

interface OfflineManagerOptions {
  onOnline?: () => void;
  onOffline?: () => void;
  pingUrl?: string;
  pingInterval?: number;
  retryAttempts?: number;
}

interface OfflineState {
  isOnline: boolean;
  isConnecting: boolean;
  lastOnline: Date | null;
  consecutiveFailures: number;
}

/**
 * Hook for managing offline state and connectivity
 */
export function useOffline(options: OfflineManagerOptions = {}) {
  const {
    onOnline,
    onOffline,
    pingUrl = '/api/v1/health',
    pingInterval = 30000, // 30 seconds
    retryAttempts = 3
  } = options;

  const [state, setState] = useState<OfflineState>({
    isOnline: navigator.onLine,
    isConnecting: false,
    lastOnline: navigator.onLine ? new Date() : null,
    consecutiveFailures: 0,
  });

  // Test actual connectivity by pinging the server
  const testConnectivity = useCallback(async (): Promise<boolean> => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(pingUrl, {
        method: 'HEAD',
        signal: controller.signal,
        cache: 'no-cache',
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch {
      return false;
    }
  }, [pingUrl]);

  // Handle connectivity change
  const handleConnectivityChange = useCallback(async (navigatorOnline: boolean) => {
    setState(prev => ({ ...prev, isConnecting: true }));

    let actuallyOnline = navigatorOnline;

    // If navigator says we're online, verify with server ping
    if (navigatorOnline) {
      let attempts = 0;
      while (attempts < retryAttempts && !actuallyOnline) {
        actuallyOnline = await testConnectivity();
        if (!actuallyOnline) {
          attempts++;
          if (attempts < retryAttempts) {
            await new Promise(resolve => setTimeout(resolve, 1000 * attempts));
          }
        }
      }
    }

    setState(prev => ({
      isOnline: actuallyOnline,
      isConnecting: false,
      lastOnline: actuallyOnline ? new Date() : prev.lastOnline,
      consecutiveFailures: actuallyOnline ? 0 : prev.consecutiveFailures + 1,
    }));

    // Call callbacks
    if (actuallyOnline && !state.isOnline) {
      onOnline?.();
    } else if (!actuallyOnline && state.isOnline) {
      onOffline?.();
    }
  }, [testConnectivity, retryAttempts, onOnline, onOffline, state.isOnline]);

  // Manual connectivity check
  const checkConnectivity = useCallback(async () => {
    await handleConnectivityChange(navigator.onLine);
  }, [handleConnectivityChange]);

  // Retry connection
  const retryConnection = useCallback(async () => {
    await handleConnectivityChange(true);
  }, [handleConnectivityChange]);

  // Set up event listeners and periodic checks
  useEffect(() => {
    // Listen to browser online/offline events
    const unsubscribe = ConnectionMonitor.addListener(handleConnectivityChange);

    // Periodic connectivity check when online
    let intervalId: NodeJS.Timeout | null = null;
    
    if (state.isOnline && pingInterval > 0) {
      intervalId = setInterval(async () => {
        const isActuallyOnline = await testConnectivity();
        if (!isActuallyOnline) {
          await handleConnectivityChange(false);
        }
      }, pingInterval);
    }

    return () => {
      unsubscribe();
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [handleConnectivityChange, testConnectivity, pingInterval, state.isOnline]);

  return {
    ...state,
    checkConnectivity,
    retryConnection,
  };
}

/**
 * Hook for offline-first data management
 */
export function useOfflineData<T>(
  key: string,
  fetcher: () => Promise<T>,
  options: {
    fallbackData?: T;
    syncOnReconnect?: boolean;
    syncInterval?: number;
  } = {}
) {
  const { fallbackData, syncOnReconnect = true, syncInterval = 60000 } = options;
  
  const [data, setData] = useState<T | undefined>(fallbackData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [lastSync, setLastSync] = useState<Date | null>(null);
  const [needsSync, setNeedsSync] = useState(false);

  const { isOnline } = useOffline({
    onOnline: () => {
      if (syncOnReconnect && needsSync) {
        sync();
      }
    }
  });

  // Load data from localStorage
  const loadFromStorage = useCallback((): T | undefined => {
    try {
      const stored = localStorage.getItem(`offline-data-${key}`);
      if (stored) {
        const parsed = JSON.parse(stored);
        setLastSync(new Date(parsed.timestamp));
        return parsed.data;
      }
    } catch (error) {
      console.warn('Failed to load offline data:', error);
    }
    return undefined;
  }, [key]);

  // Save data to localStorage
  const saveToStorage = useCallback((data: T) => {
    try {
      localStorage.setItem(`offline-data-${key}`, JSON.stringify({
        data,
        timestamp: new Date().toISOString(),
      }));
    } catch (error) {
      console.warn('Failed to save offline data:', error);
    }
  }, [key]);

  // Sync data from server
  const sync = useCallback(async (force = false) => {
    if (!isOnline && !force) {
      setNeedsSync(true);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const newData = await fetcher();
      setData(newData);
      saveToStorage(newData);
      setLastSync(new Date());
      setNeedsSync(false);
    } catch (error) {
      setError(error as Error);
      if (!isOnline) {
        setNeedsSync(true);
      }
    } finally {
      setLoading(false);
    }
  }, [isOnline, fetcher, saveToStorage]);

  // Initialize data
  useEffect(() => {
    const storedData = loadFromStorage();
    if (storedData) {
      setData(storedData);
    }

    // Sync immediately if online
    if (isOnline) {
      sync();
    } else {
      setNeedsSync(true);
    }
  }, []);

  // Periodic sync when online
  useEffect(() => {
    if (!isOnline || syncInterval <= 0) return;

    const intervalId = setInterval(() => {
      sync();
    }, syncInterval);

    return () => clearInterval(intervalId);
  }, [isOnline, sync, syncInterval]);

  return {
    data,
    loading,
    error,
    lastSync,
    needsSync,
    isOnline,
    sync: () => sync(false),
    forceSync: () => sync(true),
  };
}

/**
 * Hook for managing offline queue
 */
export function useOfflineQueue<T>(
  processor: (item: T) => Promise<void>,
  options: {
    storageKey?: string;
    maxItems?: number;
    processOnReconnect?: boolean;
  } = {}
) {
  const {
    storageKey = 'offline-queue',
    maxItems = 100,
    processOnReconnect = true
  } = options;

  const [queue, setQueue] = useState<T[]>([]);
  const [processing, setProcessing] = useState(false);
  const [errors, setErrors] = useState<Error[]>([]);

  const { isOnline } = useOffline({
    onOnline: () => {
      if (processOnReconnect && queue.length > 0) {
        processQueue();
      }
    }
  });

  // Load queue from storage
  const loadQueue = useCallback(() => {
    try {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        setQueue(parsed);
      }
    } catch (error) {
      console.warn('Failed to load offline queue:', error);
    }
  }, [storageKey]);

  // Save queue to storage
  const saveQueue = useCallback((newQueue: T[]) => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(newQueue));
    } catch (error) {
      console.warn('Failed to save offline queue:', error);
    }
  }, [storageKey]);

  // Add item to queue
  const enqueue = useCallback((item: T) => {
    setQueue(prev => {
      const newQueue = [...prev, item];
      if (newQueue.length > maxItems) {
        newQueue.shift(); // Remove oldest item
      }
      saveQueue(newQueue);
      return newQueue;
    });

    // Process immediately if online
    if (isOnline) {
      processQueue();
    }
  }, [isOnline, maxItems, saveQueue]);

  // Process queue
  const processQueue = useCallback(async () => {
    if (processing || queue.length === 0 || !isOnline) return;

    setProcessing(true);
    setErrors([]);

    const newQueue = [...queue];
    const newErrors: Error[] = [];

    while (newQueue.length > 0 && isOnline) {
      const item = newQueue.shift()!;
      try {
        await processor(item);
      } catch (error) {
        newErrors.push(error as Error);
        // Put item back at the beginning for retry
        newQueue.unshift(item);
        break;
      }
    }

    setQueue(newQueue);
    setErrors(newErrors);
    saveQueue(newQueue);
    setProcessing(false);
  }, [processing, queue, isOnline, processor, saveQueue]);

  // Clear queue
  const clearQueue = useCallback(() => {
    setQueue([]);
    setErrors([]);
    saveQueue([]);
  }, [saveQueue]);

  // Initialize
  useEffect(() => {
    loadQueue();
  }, [loadQueue]);

  return {
    queue,
    processing,
    errors,
    isOnline,
    enqueue,
    processQueue,
    clearQueue,
    queueSize: queue.length,
  };
}