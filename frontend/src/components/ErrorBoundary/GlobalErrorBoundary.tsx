/**
 * Global Error Boundary with enhanced error handling and reporting
 */

import { Component, type ReactNode, type ErrorInfo } from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';
import { Card, CardContent } from '../../shared/components/UI/Card';
import { Button } from '../../shared/components/UI/Button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
  errorId: string;
}

export class GlobalErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { 
      hasError: false,
      errorId: '',
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Generate unique error ID for tracking
    const errorId = `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return { 
      hasError: true, 
      error,
      errorId,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });
    
    // Log error details
    console.error('GlobalErrorBoundary caught an error:', {
      error,
      errorInfo,
      errorId: this.state.errorId,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    });

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);

    // Report to error tracking service (e.g., Sentry)
    this.reportError(error, errorInfo);
  }

  private reportError = (error: Error, errorInfo: ErrorInfo) => {
    // In a real application, you would send this to an error tracking service
    const errorReport = {
      errorId: this.state.errorId,
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      userId: this.getUserId(), // If available
    };

    // Example: Send to monitoring service
    if (import.meta.env.PROD) {
      fetch('/api/v1/errors/report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorReport),
      }).catch(reportingError => {
        console.error('Failed to report error:', reportingError);
      });
    }
  };

  private getUserId = (): string | null => {
    // Get user ID from localStorage or auth store
    try {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        return user.id || null;
      }
    } catch {
      // Ignore parsing errors
    }
    return null;
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  private handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  private handleReportBug = () => {
    const subject = encodeURIComponent(`Bug Report: ${this.state.error?.message || 'Unknown Error'}`);
    const body = encodeURIComponent(`
Error ID: ${this.state.errorId}
Error Message: ${this.state.error?.message || 'Unknown'}
Timestamp: ${new Date().toISOString()}
URL: ${window.location.href}
User Agent: ${navigator.userAgent}

Additional Details:
- Please describe what you were doing when this error occurred
- Any steps to reproduce the issue

Technical Details:
${this.state.error?.stack || 'No stack trace available'}
    `.trim());

    const mailtoUrl = `mailto:support@streamworks-ki.com?subject=${subject}&body=${body}`;
    window.open(mailtoUrl);
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900 flex items-center justify-center p-6">
          <Card variant="elevated" className="max-w-2xl w-full">
            <CardContent className="p-8">
              <div className="text-center space-y-6">
                <div className="w-20 h-20 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto">
                  <AlertTriangle size={40} className="text-red-600 dark:text-red-400" />
                </div>

                <div>
                  <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">
                    Etwas ist schiefgelaufen
                  </h1>
                  <p className="text-neutral-600 dark:text-neutral-400 mb-4">
                    Ein unerwarteter Fehler ist aufgetreten. Wir entschuldigen uns für die Unannehmlichkeiten.
                  </p>
                  
                  <div className="bg-neutral-100 dark:bg-neutral-800 rounded-lg p-4 mb-6">
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      <strong>Fehler-ID:</strong> {this.state.errorId}
                    </p>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      <strong>Zeitpunkt:</strong> {new Date().toLocaleString('de-DE')}
                    </p>
                  </div>

                  {import.meta.env.DEV && this.state.error && (
                    <details className="text-left text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-4 rounded-lg mb-6">
                      <summary className="cursor-pointer font-medium mb-3 select-none">
                        🔧 Entwickler-Details (nur im Development-Modus)
                      </summary>
                      <div className="space-y-3">
                        <div>
                          <strong>Fehlermeldung:</strong>
                          <pre className="whitespace-pre-wrap mt-1 text-xs">
                            {this.state.error.message}
                          </pre>
                        </div>
                        
                        {this.state.error.stack && (
                          <div>
                            <strong>Stack Trace:</strong>
                            <pre className="whitespace-pre-wrap mt-1 text-xs overflow-auto max-h-40">
                              {this.state.error.stack}
                            </pre>
                          </div>
                        )}
                        
                        {this.state.errorInfo?.componentStack && (
                          <div>
                            <strong>Component Stack:</strong>
                            <pre className="whitespace-pre-wrap mt-1 text-xs overflow-auto max-h-40">
                              {this.state.errorInfo.componentStack}
                            </pre>
                          </div>
                        )}
                      </div>
                    </details>
                  )}
                </div>

                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <Button
                    variant="primary"
                    onClick={this.handleReset}
                    leftIcon={<RefreshCw size={16} />}
                  >
                    Erneut versuchen
                  </Button>
                  
                  <Button
                    variant="secondary"
                    onClick={this.handleGoHome}
                    leftIcon={<Home size={16} />}
                  >
                    Zur Startseite
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={this.handleReportBug}
                    leftIcon={<Bug size={16} />}
                  >
                    Fehler melden
                  </Button>
                </div>

                <div className="pt-4 border-t border-neutral-200 dark:border-neutral-700">
                  <p className="text-xs text-neutral-500 dark:text-neutral-400">
                    Wenn das Problem weiterhin besteht, kontaktieren Sie bitte den Support.
                  </p>
                  <button
                    onClick={this.handleReload}
                    className="text-xs text-primary-600 dark:text-primary-400 hover:underline mt-2"
                  >
                    Seite neu laden
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// Higher-order component for wrapping components with error boundary
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode,
  onError?: (error: Error, errorInfo: ErrorInfo) => void
) {
  const WrappedComponent = (props: P) => (
    <GlobalErrorBoundary fallback={fallback} onError={onError}>
      <Component {...props} />
    </GlobalErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
}

// Hook for programmatic error handling
export function useErrorHandler() {
  const handleError = (error: Error, context?: string) => {
    console.error(`Error in ${context || 'unknown context'}:`, error);
    
    // Create a synthetic error boundary trigger
    throw error;
  };

  return { handleError };
}