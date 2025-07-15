import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Debounce hook for delaying function execution
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Debounced callback hook
 */
export function useDebouncedCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number,
  deps: React.DependencyList = []
): T {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  const debouncedCallback = useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        callbackRef.current(...args);
      }, delay);
    },
    [delay, ...deps]
  ) as T;

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return debouncedCallback;
}

/**
 * Throttle hook for limiting function execution frequency
 */
export function useThrottle<T>(value: T, limit: number): T {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const lastRan = useRef<number>(Date.now());

  useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRan.current >= limit) {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }
    }, limit - (Date.now() - lastRan.current));

    return () => {
      clearTimeout(handler);
    };
  }, [value, limit]);

  return throttledValue;
}

/**
 * Throttled callback hook
 */
export function useThrottledCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number,
  deps: React.DependencyList = []
): T {
  const lastRan = useRef<number>(0);
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  const throttledCallback = useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now();
      if (now - lastRan.current >= delay) {
        callbackRef.current(...args);
        lastRan.current = now;
      }
    },
    [delay, ...deps]
  ) as T;

  return throttledCallback;
}

/**
 * Advanced debounce hook with immediate execution option
 */
export function useAdvancedDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number,
  options: {
    leading?: boolean;
    trailing?: boolean;
    maxWait?: number;
  } = {}
): [T, () => void, () => void] {
  const { leading = false, trailing = true, maxWait } = options;
  
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const maxTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const callbackRef = useRef(callback);
  const lastCallTimeRef = useRef<number>(0);
  const lastInvokeTimeRef = useRef<number>(0);
  
  callbackRef.current = callback;

  const invokeFunc = useCallback((...args: Parameters<T>) => {
    lastInvokeTimeRef.current = Date.now();
    return callbackRef.current(...args);
  }, []);

  const leadingEdge = useCallback((...args: Parameters<T>) => {
    lastInvokeTimeRef.current = Date.now();
    if (leading) {
      return invokeFunc(...args);
    }
  }, [leading, invokeFunc]);

  const trailingEdge = useCallback((...args: Parameters<T>) => {
    timeoutRef.current = null;
    if (trailing && lastCallTimeRef.current > lastInvokeTimeRef.current) {
      return invokeFunc(...args);
    }
  }, [trailing, invokeFunc]);

  const timerExpired = useCallback((...args: Parameters<T>) => {
    const time = Date.now();
    if (shouldInvoke(time)) {
      return trailingEdge(...args);
    }
    timeoutRef.current = setTimeout(
      () => timerExpired(...args),
      remainingWait(time)
    );
  }, []);

  const shouldInvoke = useCallback((time: number) => {
    const timeSinceLastCall = time - lastCallTimeRef.current;
    const timeSinceLastInvoke = time - lastInvokeTimeRef.current;
    
    return (
      lastCallTimeRef.current === 0 ||
      timeSinceLastCall >= delay ||
      timeSinceLastCall < 0 ||
      (maxWait !== undefined && timeSinceLastInvoke >= maxWait)
    );
  }, [delay, maxWait]);

  const remainingWait = useCallback((time: number) => {
    const timeSinceLastCall = time - lastCallTimeRef.current;
    const timeSinceLastInvoke = time - lastInvokeTimeRef.current;
    const timeWaiting = delay - timeSinceLastCall;
    
    return maxWait === undefined
      ? timeWaiting
      : Math.min(timeWaiting, maxWait - timeSinceLastInvoke);
  }, [delay, maxWait]);

  const debouncedCallback = useCallback(
    (...args: Parameters<T>) => {
      const time = Date.now();
      const isInvoking = shouldInvoke(time);
      
      lastCallTimeRef.current = time;
      
      if (isInvoking) {
        if (timeoutRef.current === null) {
          return leadingEdge(...args);
        }
        if (maxWait !== undefined) {
          timeoutRef.current = setTimeout(
            () => timerExpired(...args),
            delay
          );
          return leadingEdge(...args);
        }
      }
      
      if (timeoutRef.current === null) {
        timeoutRef.current = setTimeout(
          () => timerExpired(...args),
          delay
        );
      }
    },
    [delay, leadingEdge, timerExpired, shouldInvoke]
  ) as T;

  const cancel = useCallback(() => {
    if (timeoutRef.current !== null) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    if (maxTimeoutRef.current !== null) {
      clearTimeout(maxTimeoutRef.current);
      maxTimeoutRef.current = null;
    }
    lastInvokeTimeRef.current = 0;
    lastCallTimeRef.current = 0;
  }, []);

  const flush = useCallback((...args: Parameters<T>) => {
    if (timeoutRef.current !== null) {
      clearTimeout(timeoutRef.current);
      return trailingEdge(...args);
    }
  }, [trailingEdge]) as () => void;

  useEffect(() => {
    return () => {
      cancel();
    };
  }, [cancel]);

  return [debouncedCallback, cancel, flush];
}

/**
 * Smart search debounce hook with different delays for different query lengths
 */
export function useSmartSearchDebounce(
  callback: (query: string) => void,
  options: {
    shortQueryDelay?: number;  // For queries < 3 characters
    mediumQueryDelay?: number; // For queries 3-6 characters
    longQueryDelay?: number;   // For queries > 6 characters
    minLength?: number;        // Minimum query length to trigger search
  } = {}
): (query: string) => void {
  const {
    shortQueryDelay = 800,
    mediumQueryDelay = 400,
    longQueryDelay = 200,
    minLength = 1
  } = options;

  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  const smartDebouncedCallback = useCallback((query: string) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    if (query.length < minLength) {
      return;
    }

    let delay = shortQueryDelay;
    if (query.length > 6) {
      delay = longQueryDelay;
    } else if (query.length > 3) {
      delay = mediumQueryDelay;
    }

    timeoutRef.current = setTimeout(() => {
      callbackRef.current(query);
    }, delay);
  }, [shortQueryDelay, mediumQueryDelay, longQueryDelay, minLength]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return smartDebouncedCallback;
}