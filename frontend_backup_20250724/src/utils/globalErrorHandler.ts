import { ErrorReporter, ConnectionMonitor } from './errorUtils';

/**
 * Global error handler for unhandled errors and promise rejections
 */
export class GlobalErrorHandler {
  private static isInitialized = false;

  static init(): void {
    if (this.isInitialized) return;

    // Handle unhandled errors
    window.addEventListener('error', (event) => {
      console.error('Unhandled error:', event.error);
      ErrorReporter.report(event.error || new Error(event.message), {
        type: 'unhandled_error',
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      });
    });

    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled promise rejection:', event.reason);
      
      const error = event.reason instanceof Error 
        ? event.reason 
        : new Error(String(event.reason));
        
      ErrorReporter.report(error, {
        type: 'unhandled_promise_rejection',
        promise: event.promise,
      });
      
      // Prevent the default browser behavior (logging to console)
      event.preventDefault();
    });

    // Initialize connection monitoring
    ConnectionMonitor.init();

    // Handle page visibility changes to clear error session on new session
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        // Page became visible - could be a new session
        const lastActivity = localStorage.getItem('lastActivity');
        const now = Date.now();
        const oneHour = 60 * 60 * 1000;
        
        if (!lastActivity || now - parseInt(lastActivity) > oneHour) {
          ErrorReporter.clearSession();
        }
        
        localStorage.setItem('lastActivity', now.toString());
      }
    });

    // Handle page unload to save error session state
    window.addEventListener('beforeunload', () => {
      localStorage.setItem('lastActivity', Date.now().toString());
    });

    this.isInitialized = true;
    console.log('Global error handler initialized');
  }

  static cleanup(): void {
    if (!this.isInitialized) return;

    window.removeEventListener('error', this.handleError);
    window.removeEventListener('unhandledrejection', this.handleUnhandledRejection);
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
    window.removeEventListener('beforeunload', this.handleBeforeUnload);

    this.isInitialized = false;
    console.log('Global error handler cleaned up');
  }

  private static handleError = (event: ErrorEvent) => {
    console.error('Unhandled error:', event.error);
    ErrorReporter.report(event.error || new Error(event.message), {
      type: 'unhandled_error',
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
    });
  };

  private static handleUnhandledRejection = (event: PromiseRejectionEvent) => {
    console.error('Unhandled promise rejection:', event.reason);
    
    const error = event.reason instanceof Error 
      ? event.reason 
      : new Error(String(event.reason));
      
    ErrorReporter.report(error, {
      type: 'unhandled_promise_rejection',
      promise: event.promise,
    });
    
    event.preventDefault();
  };

  private static handleVisibilityChange = () => {
    if (!document.hidden) {
      const lastActivity = localStorage.getItem('lastActivity');
      const now = Date.now();
      const oneHour = 60 * 60 * 1000;
      
      if (!lastActivity || now - parseInt(lastActivity) > oneHour) {
        ErrorReporter.clearSession();
      }
      
      localStorage.setItem('lastActivity', now.toString());
    }
  };

  private static handleBeforeUnload = () => {
    localStorage.setItem('lastActivity', Date.now().toString());
  };
}

// Auto-initialize in browser environment
if (typeof window !== 'undefined') {
  GlobalErrorHandler.init();
}