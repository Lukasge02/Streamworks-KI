import React from 'react';
import { AlertTriangle, X, RefreshCw, Wifi, WifiOff } from 'lucide-react';

interface ErrorState {
  message: string;
  code?: string;
  retryable: boolean;
  timestamp: number;
}

interface ErrorAlertProps {
  error: ErrorState;
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
  variant?: 'banner' | 'card' | 'inline';
  showTimestamp?: boolean;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  error,
  onRetry,
  onDismiss,
  className = '',
  variant = 'card',
  showTimestamp = false,
}) => {
  const isNetworkError = error.code === 'NETWORK_ERROR' || 
                        error.message.toLowerCase().includes('network') ||
                        error.message.toLowerCase().includes('fetch');
  
  const isOfflineError = error.code === 'OFFLINE' || 
                        error.message.toLowerCase().includes('offline');

  const getErrorIcon = () => {
    if (isOfflineError) return WifiOff;
    if (isNetworkError) return Wifi;
    return AlertTriangle;
  };

  const getErrorTitle = () => {
    if (isOfflineError) return 'No Internet Connection';
    if (isNetworkError) return 'Connection Problem';
    return 'Error';
  };

  const getErrorDescription = () => {
    if (isOfflineError) {
      return 'You appear to be offline. Please check your internet connection.';
    }
    if (isNetworkError) {
      return 'Unable to connect to the server. Please try again.';
    }
    return error.message;
  };

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const Icon = getErrorIcon();

  const baseClasses = "flex items-start space-x-3 p-4 border-l-4";
  const variantClasses = {
    banner: "bg-red-50 border-red-400 rounded-none w-full",
    card: "bg-red-50 border-red-400 rounded-lg",
    inline: "bg-red-50 border-red-400 rounded",
  };

  const iconClasses = isOfflineError 
    ? "text-gray-500" 
    : isNetworkError 
      ? "text-orange-500" 
      : "text-red-500";

  return (
    <div className={`${baseClasses} ${variantClasses[variant]} ${className}`}>
      {/* Error Icon */}
      <div className="flex-shrink-0">
        <Icon className={`h-5 w-5 ${iconClasses}`} />
      </div>

      {/* Error Content */}
      <div className="flex-grow min-w-0">
        <div className="flex items-start justify-between">
          <div className="flex-grow">
            <h3 className="text-sm font-medium text-gray-900">
              {getErrorTitle()}
            </h3>
            <p className="mt-1 text-sm text-gray-600">
              {getErrorDescription()}
            </p>
            
            {/* Error Code */}
            {error.code && (
              <p className="mt-1 text-xs text-gray-500 font-mono">
                Code: {error.code}
              </p>
            )}
            
            {/* Timestamp */}
            {showTimestamp && (
              <p className="mt-1 text-xs text-gray-400">
                {formatTimestamp(error.timestamp)}
              </p>
            )}
          </div>

          {/* Dismiss Button */}
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="flex-shrink-0 ml-3 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Dismiss error"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Action Buttons */}
        {(onRetry && error.retryable) && (
          <div className="mt-3">
            <button
              onClick={onRetry}
              className="inline-flex items-center px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Preset error alerts for common scenarios
export const NetworkErrorAlert: React.FC<Omit<ErrorAlertProps, 'error'> & { customMessage?: string }> = ({
  customMessage,
  ...props
}) => (
  <ErrorAlert
    error={{
      message: customMessage || 'Network connection failed',
      code: 'NETWORK_ERROR',
      retryable: true,
      timestamp: Date.now(),
    }}
    {...props}
  />
);

export const OfflineErrorAlert: React.FC<Omit<ErrorAlertProps, 'error'> & { customMessage?: string }> = ({
  customMessage,
  ...props
}) => (
  <ErrorAlert
    error={{
      message: customMessage || 'You are currently offline',
      code: 'OFFLINE',
      retryable: true,
      timestamp: Date.now(),
    }}
    {...props}
  />
);

export const ServerErrorAlert: React.FC<Omit<ErrorAlertProps, 'error'> & { customMessage?: string }> = ({
  customMessage,
  ...props
}) => (
  <ErrorAlert
    error={{
      message: customMessage || 'Server error occurred',
      code: 'SERVER_ERROR',
      retryable: true,
      timestamp: Date.now(),
    }}
    {...props}
  />
);