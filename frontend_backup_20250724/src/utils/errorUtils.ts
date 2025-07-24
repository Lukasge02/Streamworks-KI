import { ChunksApiError } from '../services/chunksApiService';

// Error types and interfaces
export interface ErrorState {
  message: string;
  code?: string;
  retryable: boolean;
  timestamp: number;
}

export interface ErrorReport {
  id: string;
  message: string;
  stack?: string;
  componentStack?: string;
  timestamp: string;
  userAgent: string;
  url: string;
  userId?: string;
  context?: Record<string, any>;
}

// Error classification
export enum ErrorType {
  NETWORK = 'NETWORK',
  SERVER = 'SERVER', 
  CLIENT = 'CLIENT',
  VALIDATION = 'VALIDATION',
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  NOT_FOUND = 'NOT_FOUND',
  TIMEOUT = 'TIMEOUT',
  CANCELLED = 'CANCELLED',
  UNKNOWN = 'UNKNOWN',
}

// Error severity levels
export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium', 
  HIGH = 'high',
  CRITICAL = 'critical',
}

/**
 * Error classification utility
 */
export class ErrorClassifier {
  static classify(error: any): ErrorType {
    if (error instanceof ChunksApiError) {
      if (error.code === 'CANCELLED') return ErrorType.CANCELLED;
      if (error.status === 0) return ErrorType.NETWORK;
      if (error.status === 401) return ErrorType.AUTHENTICATION;
      if (error.status === 403) return ErrorType.AUTHORIZATION;
      if (error.status === 404) return ErrorType.NOT_FOUND;
      if (error.status === 408 || error.status === 504) return ErrorType.TIMEOUT;
      if (error.status && error.status >= 400 && error.status < 500) return ErrorType.CLIENT;
      if (error.status && error.status >= 500) return ErrorType.SERVER;
    }

    if (error.name === 'AbortError' || error.name === 'TimeoutError') {
      return ErrorType.CANCELLED;
    }

    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return ErrorType.NETWORK;
    }

    if (error.message?.toLowerCase().includes('network')) {
      return ErrorType.NETWORK;
    }

    if (error.message?.toLowerCase().includes('timeout')) {
      return ErrorType.TIMEOUT;
    }

    return ErrorType.UNKNOWN;
  }

  static getSeverity(errorType: ErrorType): ErrorSeverity {
    switch (errorType) {
      case ErrorType.NETWORK:
      case ErrorType.TIMEOUT:
      case ErrorType.CANCELLED:
        return ErrorSeverity.LOW;
      
      case ErrorType.CLIENT:
      case ErrorType.VALIDATION:
      case ErrorType.NOT_FOUND:
        return ErrorSeverity.MEDIUM;
      
      case ErrorType.AUTHENTICATION:
      case ErrorType.AUTHORIZATION:
        return ErrorSeverity.MEDIUM;
      
      case ErrorType.SERVER:
        return ErrorSeverity.HIGH;
      
      case ErrorType.UNKNOWN:
      default:
        return ErrorSeverity.CRITICAL;
    }
  }
}

/**
 * User-friendly error message generator
 */
export class ErrorMessageGenerator {
  private static networkMessages = [
    'Connection issue detected. Please check your internet and try again.',
    'Unable to reach the server. Please verify your connection.',
    'Network timeout occurred. Please try again.',
  ];

  private static serverMessages = [
    'Server is temporarily unavailable. Please try again later.',
    'We\'re experiencing technical difficulties. Our team has been notified.',
    'Service is currently down for maintenance. Please check back soon.',
  ];

  private static clientMessages = [
    'Invalid request. Please check your input and try again.',
    'The requested operation could not be completed.',
    'Please verify your input and try again.',
  ];

  static generate(error: any, context?: string): string {
    const errorType = ErrorClassifier.classify(error);
    const baseContext = context ? `${context}: ` : '';

    switch (errorType) {
      case ErrorType.NETWORK:
        return baseContext + this.getRandomMessage(this.networkMessages);
      
      case ErrorType.SERVER:
        return baseContext + this.getRandomMessage(this.serverMessages);
      
      case ErrorType.CLIENT:
      case ErrorType.VALIDATION:
        return baseContext + this.getRandomMessage(this.clientMessages);
      
      case ErrorType.AUTHENTICATION:
        return baseContext + 'Please log in to continue.';
      
      case ErrorType.AUTHORIZATION:
        return baseContext + 'You don\'t have permission to perform this action.';
      
      case ErrorType.NOT_FOUND:
        return baseContext + 'The requested resource was not found.';
      
      case ErrorType.TIMEOUT:
        return baseContext + 'Request timed out. Please try again.';
      
      case ErrorType.CANCELLED:
        return baseContext + 'Operation was cancelled.';
      
      case ErrorType.UNKNOWN:
      default:
        // Use original error message if available and user-friendly
        if (error.message && this.isUserFriendly(error.message)) {
          return baseContext + error.message;
        }
        return baseContext + 'An unexpected error occurred. Please try again.';
    }
  }

  private static getRandomMessage(messages: string[]): string {
    return messages[Math.floor(Math.random() * messages.length)];
  }

  private static isUserFriendly(message: string): boolean {
    const technicalTerms = [
      'stack trace', 'undefined', 'null', 'function', 'object',
      'TypeError', 'ReferenceError', 'SyntaxError', 'fetch',
      'promise', 'async', 'await', 'callback'
    ];

    return !technicalTerms.some(term => 
      message.toLowerCase().includes(term.toLowerCase())
    );
  }
}

/**
 * Error state creator utility
 */
export class ErrorStateCreator {
  static create(error: any, context?: string): ErrorState {
    const errorType = ErrorClassifier.classify(error);
    const message = ErrorMessageGenerator.generate(error, context);
    
    return {
      message,
      code: error instanceof ChunksApiError ? error.code : errorType,
      retryable: this.isRetryable(error, errorType),
      timestamp: Date.now(),
    };
  }

  private static isRetryable(error: any, errorType: ErrorType): boolean {
    // Cancelled operations are not retryable
    if (errorType === ErrorType.CANCELLED) return false;
    
    // Authentication/authorization errors need user action
    if (errorType === ErrorType.AUTHENTICATION || errorType === ErrorType.AUTHORIZATION) {
      return false;
    }
    
    // Validation errors need input correction
    if (errorType === ErrorType.VALIDATION) return false;
    
    // Not found errors are typically not retryable
    if (errorType === ErrorType.NOT_FOUND) return false;
    
    // If error has explicit retryable flag, use it
    if (error instanceof ChunksApiError) {
      return error.retryable;
    }
    
    // Network, server, timeout, and unknown errors are retryable
    return [
      ErrorType.NETWORK,
      ErrorType.SERVER,
      ErrorType.TIMEOUT,
      ErrorType.UNKNOWN,
    ].includes(errorType);
  }
}

/**
 * Error reporting utility
 */
export class ErrorReporter {
  private static readonly MAX_REPORTS_PER_SESSION = 50;
  private static reportCount = 0;
  private static reportedErrors = new Set<string>();

  static async report(error: Error, context?: Record<string, any>): Promise<void> {
    // Prevent spam reporting
    if (this.reportCount >= this.MAX_REPORTS_PER_SESSION) {
      return;
    }

    // Create error signature to prevent duplicate reports
    const errorSignature = this.createErrorSignature(error);
    if (this.reportedErrors.has(errorSignature)) {
      return;
    }

    this.reportedErrors.add(errorSignature);
    this.reportCount++;

    const report: ErrorReport = {
      id: `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      userId: this.getUserId(),
      context,
    };

    // Log in development
    if (true) {
      console.group('🐛 Error Report');
      console.error('Error:', error);
      console.info('Report:', report);
      console.groupEnd();
    }

    // Send to error reporting service
    try {
      await this.sendReport(report);
    } catch (reportingError) {
      console.warn('Failed to send error report:', reportingError);
    }
  }

  private static createErrorSignature(error: Error): string {
    // Create a signature based on error message and first few lines of stack
    const stackLines = error.stack?.split('\n').slice(0, 3).join('|') || '';
    return `${error.message}|${stackLines}`;
  }

  private static getUserId(): string {
    try {
      return localStorage.getItem('userId') || 'anonymous';
    } catch {
      return 'anonymous';
    }
  }

  private static async sendReport(report: ErrorReport): Promise<void> {
    // Replace with your actual error reporting endpoint
    await fetch('/api/v1/errors/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(report),
    }).catch(() => {
      // Silent fail for error reporting
    });
  }

  static clearSession(): void {
    this.reportCount = 0;
    this.reportedErrors.clear();
  }
}

/**
 * Connection status monitor
 */
export class ConnectionMonitor {
  private static listeners: Set<(online: boolean) => void> = new Set();
  private static isInitialized = false;

  static init(): void {
    if (this.isInitialized) return;

    window.addEventListener('online', () => {
      this.notifyListeners(true);
    });

    window.addEventListener('offline', () => {
      this.notifyListeners(false);
    });

    this.isInitialized = true;
  }

  static isOnline(): boolean {
    return navigator.onLine;
  }

  static addListener(callback: (online: boolean) => void): () => void {
    this.init();
    this.listeners.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(callback);
    };
  }

  private static notifyListeners(online: boolean): void {
    this.listeners.forEach(callback => {
      try {
        callback(online);
      } catch (error) {
        console.warn('Connection monitor listener error:', error);
      }
    });
  }
}

/**
 * Offline error creation utility
 */
export function createOfflineError(): ErrorState {
  return {
    message: 'You are currently offline',
    code: 'OFFLINE',
    retryable: true,
    timestamp: Date.now(),
  };
}

/**
 * Network error creation utility
 */
export function createNetworkError(details?: string): ErrorState {
  return {
    message: details || 'Network connection failed',
    code: 'NETWORK_ERROR',
    retryable: true,
    timestamp: Date.now(),
  };
}