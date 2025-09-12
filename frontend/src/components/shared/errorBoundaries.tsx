/**
 * Comprehensive Error Boundaries for StreamWorks
 * Provides centralized error handling and recovery mechanisms
 */

import React, { Component, ReactNode, ErrorInfo } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, RefreshCw, Home, Bug, FileText } from 'lucide-react'

// ================================
// ERROR TYPES
// ================================

export enum ErrorType {
  NETWORK = 'network',
  API = 'api',
  VALIDATION = 'validation',
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  DATABASE = 'database',
  FILE_UPLOAD = 'file_upload',
  CHAT = 'chat',
  UNKNOWN = 'unknown'
}

export interface AppError {
  type: ErrorType
  message: string
  code?: string
  details?: any
  timestamp: string
  stack?: string
  recoverable: boolean
}

// ================================
// BASE ERROR BOUNDARY
// ================================

interface ErrorBoundaryState {
  hasError: boolean
  error: AppError | null
  errorInfo: ErrorInfo | null
}

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: AppError, errorInfo: ErrorInfo) => void
  allowedErrorTypes?: ErrorType[]
}

class StreamWorksErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    const normalizedError = StreamWorksErrorBoundary.staticNormalizeError(error)
    return {
      hasError: true,
      error: normalizedError,
      errorInfo: null
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const normalizedError = this.normalizeError(error)
    
    this.setState({
      error: normalizedError,
      errorInfo
    })

    // Call error handler if provided
    this.props.onError?.(normalizedError, errorInfo)

    // Log error for debugging
    console.error('Error caught by boundary:', {
      error: normalizedError,
      errorInfo
    })
  }

  static staticNormalizeError(error: Error): AppError {
    // Extract error type from error message or stack
    const errorType = StreamWorksErrorBoundary.staticExtractErrorType(error)
    
    return {
      type: errorType,
      message: error.message || 'An unexpected error occurred',
      code: StreamWorksErrorBoundary.staticExtractErrorCode(error),
      timestamp: new Date().toISOString(),
      stack: error.stack,
      recoverable: StreamWorksErrorBoundary.staticIsRecoverable(errorType)
    }
  }

  static staticExtractErrorType(error: Error): ErrorType {
    const message = error.message.toLowerCase()
    
    if (message.includes('network') || message.includes('fetch')) return ErrorType.NETWORK
    if (message.includes('api') || message.includes('http')) return ErrorType.API
    if (message.includes('validation') || message.includes('invalid')) return ErrorType.VALIDATION
    if (message.includes('auth') || message.includes('unauthorized')) return ErrorType.AUTHENTICATION
    if (message.includes('permission') || message.includes('forbidden')) return ErrorType.AUTHORIZATION
    if (message.includes('database') || message.includes('sql')) return ErrorType.DATABASE
    if (message.includes('upload') || message.includes('file')) return ErrorType.FILE_UPLOAD
    if (message.includes('chat') || message.includes('rag')) return ErrorType.CHAT
    
    return ErrorType.UNKNOWN
  }

  static staticExtractErrorCode(error: Error): string | undefined {
    const match = error.message.match(/\[([A-Z_]+)\]/)
    return match ? match[1] : undefined
  }

  static staticIsRecoverable(errorType: ErrorType): boolean {
    const recoverableTypes = [
      ErrorType.NETWORK,
      ErrorType.API,
      ErrorType.VALIDATION,
      ErrorType.FILE_UPLOAD
    ]
    return recoverableTypes.includes(errorType)
  }

  private normalizeError(error: Error): AppError {
    // Extract error type from error message or stack
    const errorType = this.extractErrorType(error)
    
    return {
      type: errorType,
      message: error.message || 'An unexpected error occurred',
      code: this.extractErrorCode(error),
      timestamp: new Date().toISOString(),
      stack: error.stack,
      recoverable: this.isRecoverable(errorType)
    }
  }

  private extractErrorType(error: Error): ErrorType {
    const message = error.message.toLowerCase()
    
    if (message.includes('network') || message.includes('fetch')) return ErrorType.NETWORK
    if (message.includes('api') || message.includes('http')) return ErrorType.API
    if (message.includes('validation') || message.includes('invalid')) return ErrorType.VALIDATION
    if (message.includes('auth') || message.includes('unauthorized')) return ErrorType.AUTHENTICATION
    if (message.includes('permission') || message.includes('forbidden')) return ErrorType.AUTHORIZATION
    if (message.includes('database') || message.includes('sql')) return ErrorType.DATABASE
    if (message.includes('upload') || message.includes('file')) return ErrorType.FILE_UPLOAD
    if (message.includes('chat') || message.includes('rag')) return ErrorType.CHAT
    
    return ErrorType.UNKNOWN
  }

  private extractErrorCode(error: Error): string | undefined {
    const match = error.message.match(/\[([A-Z_]+)\]/)
    return match ? match[1] : undefined
  }

  private isRecoverable(errorType: ErrorType): boolean {
    const recoverableTypes = [
      ErrorType.NETWORK,
      ErrorType.API,
      ErrorType.VALIDATION,
      ErrorType.FILE_UPLOAD
    ]
    return recoverableTypes.includes(errorType)
  }

  private shouldHandleError(error: AppError): boolean {
    if (!this.props.allowedErrorTypes) return true
    return this.props.allowedErrorTypes.includes(error.type)
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
  }

  private handleReload = () => {
    window.location.reload()
  }

  private handleGoHome = () => {
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError && this.state.error && this.shouldHandleError(this.state.error)) {
      const { fallback } = this.props
      
      if (fallback) {
        return <>{fallback}</>
      }

      return (
        <ErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          onReset={this.handleReset}
          onReload={this.handleReload}
          onGoHome={this.handleGoHome}
        />
      )
    }

    return this.props.children
  }
}

// ================================
// ERROR FALLBACK COMPONENTS
// ================================

interface ErrorFallbackProps {
  error: AppError
  errorInfo: ErrorInfo | null
  onReset: () => void
  onReload: () => void
  onGoHome: () => void
}

function ErrorFallback({ 
  error, 
  errorInfo, 
  onReset, 
  onReload, 
  onGoHome 
}: ErrorFallbackProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="max-w-lg w-full">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-6 w-6 text-red-600" />
            <CardTitle className="text-red-600">Something went wrong</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Error Details */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-red-800">
                {error.type.toUpperCase()} ERROR
              </span>
              {error.code && (
                <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                  {error.code}
                </span>
              )}
            </div>
            <p className="text-sm text-red-700">{error.message}</p>
            {error.timestamp && (
              <p className="text-xs text-red-600 mt-2">
                Time: {new Date(error.timestamp).toLocaleString()}
              </p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-2">
            {error.recoverable && (
              <Button onClick={onReset} className="flex-1">
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            )}
            <Button onClick={onReload} variant="outline" className="flex-1">
              <RefreshCw className="h-4 w-4 mr-2" />
              Reload Page
            </Button>
            <Button onClick={onGoHome} variant="outline" className="flex-1">
              <Home className="h-4 w-4 mr-2" />
              Go Home
            </Button>
          </div>

          {/* Debug Info (Development Only) */}
          {process.env.NODE_ENV === 'development' && errorInfo && (
            <details className="mt-4">
              <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                Debug Information
              </summary>
              <div className="mt-2 bg-gray-100 rounded-lg p-4">
                <div className="space-y-2">
                  <div>
                    <h4 className="text-xs font-medium text-gray-700 mb-1">Component Stack:</h4>
                    <pre className="text-xs bg-gray-200 p-2 rounded overflow-x-auto">
                      {errorInfo.componentStack}
                    </pre>
                  </div>
                  {error.stack && (
                    <div>
                      <h4 className="text-xs font-medium text-gray-700 mb-1">Error Stack:</h4>
                      <pre className="text-xs bg-gray-200 p-2 rounded overflow-x-auto">
                        {error.stack}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            </details>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// ================================
// SPECIALIZED ERROR BOUNDARIES
// ================================

function NetworkErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <StreamWorksErrorBoundary 
      allowedErrorTypes={[ErrorType.NETWORK, ErrorType.API]}
      fallback={
        <NetworkErrorFallback />
      }
    >
      {children}
    </StreamWorksErrorBoundary>
  )
}

function ChatErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <StreamWorksErrorBoundary 
      allowedErrorTypes={[ErrorType.CHAT, ErrorType.API, ErrorType.NETWORK]}
      fallback={
        <ChatErrorFallback />
      }
    >
      {children}
    </StreamWorksErrorBoundary>
  )
}

function DocumentErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <StreamWorksErrorBoundary 
      allowedErrorTypes={[ErrorType.FILE_UPLOAD, ErrorType.API, ErrorType.NETWORK]}
      fallback={
        <DocumentErrorFallback />
      }
    >
      {children}
    </StreamWorksErrorBoundary>
  )
}

// ================================
// SPECIALIZED FALLBACKS
// ================================

function NetworkErrorFallback() {
  return (
    <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
      <div className="flex items-center space-x-3">
        <AlertTriangle className="h-5 w-5 text-yellow-600" />
        <div className="flex-1">
          <h3 className="text-sm font-medium text-yellow-800">Network Error</h3>
          <p className="text-sm text-yellow-700 mt-1">
            Unable to connect to the server. Please check your internet connection.
          </p>
          <Button 
            size="sm" 
            variant="outline" 
            className="mt-3"
            onClick={() => window.location.reload()}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    </div>
  )
}

function ChatErrorFallback() {
  return (
    <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
      <div className="flex items-center space-x-3">
        <Bug className="h-5 w-5 text-red-600" />
        <div className="flex-1">
          <h3 className="text-sm font-medium text-red-800">Chat Error</h3>
          <p className="text-sm text-red-700 mt-1">
            There was an error with the chat system. Please try starting a new conversation.
          </p>
          <Button 
            size="sm" 
            variant="outline" 
            className="mt-3"
            onClick={() => window.location.reload()}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Restart Chat
          </Button>
        </div>
      </div>
    </div>
  )
}

function DocumentErrorFallback() {
  return (
    <div className="p-6 bg-orange-50 border border-orange-200 rounded-lg">
      <div className="flex items-center space-x-3">
        <FileText className="h-5 w-5 text-orange-600" />
        <div className="flex-1">
          <h3 className="text-sm font-medium text-orange-800">Document Error</h3>
          <p className="text-sm text-orange-700 mt-1">
            There was an error processing your document. Please try uploading it again.
          </p>
          <Button 
            size="sm" 
            variant="outline" 
            className="mt-3"
            onClick={() => window.location.reload()}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry Upload
          </Button>
        </div>
      </div>
    </div>
  )
}

// ================================
// ERROR HOOK
// ================================

function useErrorHandler() {
  const [error, setError] = React.useState<AppError | null>(null)

  const handleError = React.useCallback((err: unknown) => {
    let normalizedError: AppError

    if (err instanceof Error) {
      normalizedError = {
        type: ErrorType.UNKNOWN,
        message: err.message,
        timestamp: new Date().toISOString(),
        stack: err.stack,
        recoverable: true
      }
    } else if (typeof err === 'string') {
      normalizedError = {
        type: ErrorType.UNKNOWN,
        message: err,
        timestamp: new Date().toISOString(),
        recoverable: true
      }
    } else {
      normalizedError = {
        type: ErrorType.UNKNOWN,
        message: 'An unknown error occurred',
        timestamp: new Date().toISOString(),
        recoverable: true
      }
    }

    setError(normalizedError)
    console.error('Error handled by hook:', normalizedError)
  }, [])

  const clearError = React.useCallback(() => {
    setError(null)
  }, [])

  return {
    error,
    handleError,
    clearError
  }
}

// ================================
// ERROR REPORTING
// ================================

function reportError(error: AppError, context?: any) {
  // In production, this would send to error tracking service
  console.error('Error reported:', {
    error,
    context,
    userAgent: navigator.userAgent,
    url: window.location.href,
    timestamp: new Date().toISOString()
  })

  // Example: Send to Sentry, LogRocket, etc.
  // if (typeof window !== 'undefined' && window.Sentry) {
  //   window.Sentry.captureException(error)
  // }
}

// ================================
// GLOBAL ERROR HANDLER
// ================================

function setupGlobalErrorHandlers() {
  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason)
    
    const error: AppError = {
      type: ErrorType.UNKNOWN,
      message: event.reason?.message || 'Unhandled promise rejection',
      timestamp: new Date().toISOString(),
      recoverable: false
    }

    reportError(error, { type: 'unhandledrejection' })
  })

  // Handle uncaught errors
  window.addEventListener('error', (event) => {
    console.error('Uncaught error:', event.error)
    
    const error: AppError = {
      type: ErrorType.UNKNOWN,
      message: event.error?.message || 'Uncaught error',
      timestamp: new Date().toISOString(),
      recoverable: false
    }

    reportError(error, { type: 'uncaughterror' })
  })
}

// ================================
// EXPORTS
// ================================

export {
  StreamWorksErrorBoundary,
  NetworkErrorBoundary,
  ChatErrorBoundary,
  DocumentErrorBoundary,
  useErrorHandler,
  reportError,
  setupGlobalErrorHandlers
}