/**
 * Component Architecture Patterns
 * Container/Presentational pattern with TypeScript support
 */

import React, { ReactNode } from 'react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

// ================================
// UTILITY FUNCTIONS
// ================================

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// ================================
// BASE COMPONENT PROPS
// ================================

interface BaseComponentProps {
  className?: string
  children?: ReactNode
  id?: string
  'data-testid'?: string
}

interface LoadingStateProps extends BaseComponentProps {
  isLoading: boolean
  loadingComponent?: ReactNode
  error?: string | null
  errorComponent?: ReactNode
}

// ================================
// LOADING COMPONENTS
// ================================

function LoadingSpinner({ className, size = 'md' }: { className?: string; size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  }

  return (
    <div className={cn('animate-spin rounded-full border-2 border-gray-300 border-t-blue-600', sizeClasses[size], className)} />
  )
}

function LoadingSkeleton({ className, lines = 1 }: { className?: string; lines?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={cn('h-4 bg-gray-200 rounded animate-pulse', className)}
          style={{ width: `${Math.random() * 40 + 60}%` }}
        />
      ))}
    </div>
  )
}

function LoadingCard({ className }: { className?: string }) {
  return (
    <div className={cn('bg-white rounded-lg shadow-sm border border-gray-200 p-4', className)}>
      <LoadingSkeleton lines={3} />
    </div>
  )
}

// ================================
// ERROR COMPONENTS
// ================================

function ErrorMessage({ 
  error, 
  onRetry,
  className 
}: { 
  error: string
  onRetry?: () => void
  className?: string 
}) {
  return (
    <div className={cn('bg-red-50 border border-red-200 rounded-lg p-4', className)}>
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-800">
            Error
          </h3>
          <div className="mt-2 text-sm text-red-700">
            {error}
          </div>
          {onRetry && (
            <div className="mt-4">
              <button
                onClick={onRetry}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Try again
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function ErrorBoundary({ 
  children, 
  fallback 
}: { 
  children: ReactNode
  fallback?: ReactNode 
}) {
  const [hasError, setError] = React.useState(false)
  const [error, setErrorState] = React.useState<Error | null>(null)

  React.useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      setError(true)
      setErrorState(event.error)
      console.error('Error caught by boundary:', event.error)
    }

    window.addEventListener('error', handleError)
    return () => window.removeEventListener('error', handleError)
  }, [])

  if (hasError) {
    return fallback || <ErrorMessage error={error?.message || 'An unexpected error occurred'} />
  }

  return <>{children}</>
}

// ================================
// LAYOUT COMPONENTS
// ================================

function Container({ 
  className, 
  children, 
  size = 'lg' 
}: BaseComponentProps & { 
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full' 
}) {
  const sizeClasses = {
    sm: 'max-w-screen-sm',
    md: 'max-w-screen-md',
    lg: 'max-w-screen-lg',
    xl: 'max-w-screen-xl',
    full: 'max-w-full'
  }

  return (
    <div className={cn('mx-auto px-4 sm:px-6 lg:px-8', sizeClasses[size], className)}>
      {children}
    </div>
  )
}

function Section({ 
  className, 
  children, 
  title, 
  description 
}: BaseComponentProps & { 
  title?: string
  description?: string 
}) {
  return (
    <section className={cn('py-12', className)}>
      <Container>
        {(title || description) && (
          <div className="text-center mb-12">
            {title && (
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                {title}
              </h2>
            )}
            {description && (
              <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                {description}
              </p>
            )}
          </div>
        )}
        {children}
      </Container>
    </section>
  )
}

function Grid({ 
  className, 
  children, 
  cols = 3 
}: BaseComponentProps & { 
  cols?: 1 | 2 | 3 | 4 | 6 
}) {
  const colsClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
    6: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6'
  }

  return (
    <div className={cn('grid gap-6', colsClasses[cols], className)}>
      {children}
    </div>
  )
}

// ================================
// DATA COMPONENTS
// ================================

function DataCard<T>({
  data,
  isLoading,
  error,
  render,
  loadingComponent,
  errorComponent,
  className
}: {
  data: T | null
  isLoading: boolean
  error: string | null
  render: (data: T) => ReactNode
  loadingComponent?: ReactNode
  errorComponent?: ReactNode
  className?: string
}) {
  if (isLoading) {
    return loadingComponent || <LoadingCard className={className} />
  }

  if (error) {
    return errorComponent || <ErrorMessage error={error} className={className} />
  }

  if (!data) {
    return (
      <div className={cn('text-center py-8 text-gray-500', className)}>
        No data available
      </div>
    )
  }

  return <>{render(data)}</>
}

function AsyncData<T>({
  query,
  render,
  loadingComponent,
  errorComponent,
  className
}: {
  query: {
    data: T | undefined
    isLoading: boolean
    error: any
  }
  render: (data: T) => ReactNode
  loadingComponent?: ReactNode
  errorComponent?: ReactNode
  className?: string
}) {
  return (
    <DataCard
      data={query.data || null}
      isLoading={query.isLoading}
      error={query.error?.message}
      render={render}
      loadingComponent={loadingComponent}
      errorComponent={errorComponent}
      className={className}
    />
  )
}

// ================================
// WITH STATE HOC
// ================================

interface WithStateProps {
  isLoading?: boolean
  error?: string | null
  isEmpty?: boolean
  onRetry?: () => void
}

function withState<T extends WithStateProps>(
  Component: React.ComponentType<T>,
  options: {
    loadingComponent?: ReactNode
    errorComponent?: ReactNode
    emptyComponent?: ReactNode
  } = {}
) {
  return function WithStateComponent(props: T) {
    const { isLoading, error, isEmpty, onRetry, ...componentProps } = props

    if (isLoading) {
      return options.loadingComponent || <LoadingCard />
    }

    if (error) {
      return options.errorComponent || <ErrorMessage error={error} onRetry={onRetry} />
    }

    if (isEmpty) {
      return options.emptyComponent || (
        <div className="text-center py-8 text-gray-500">
          No data available
        </div>
      )
    }

    return <Component {...(componentProps as T)} />
  }
}

// ================================
// CONDITIONAL RENDERING
// ================================

function Conditional({
  condition,
  children,
  fallback = null
}: {
  condition: boolean
  children: ReactNode
  fallback?: ReactNode
}) {
  return condition ? <>{children}</> : <>{fallback}</>
}

function Match({
  value,
  cases,
  default: defaultCase
}: {
  value: any
  cases: Record<string, ReactNode>
  default?: ReactNode
}) {
  const matchedCase = cases[value]
  return matchedCase !== undefined ? <>{matchedCase}</> : <>{defaultCase}</>
}

// ================================
// COMPOSED COMPONENTS
// ================================

function Card({ 
  className, 
  children, 
  hover = false 
}: BaseComponentProps & { 
  hover?: boolean 
}) {
  return (
    <div className={cn(
      'bg-white rounded-lg shadow-sm border border-gray-200',
      hover && 'hover:shadow-md transition-shadow duration-200',
      className
    )}>
      {children}
    </div>
  )
}

function CardHeader({ 
  className, 
  children 
}: BaseComponentProps) {
  return (
    <div className={cn('px-6 py-4 border-b border-gray-200', className)}>
      {children}
    </div>
  )
}

function CardContent({ 
  className, 
  children 
}: BaseComponentProps) {
  return (
    <div className={cn('px-6 py-4', className)}>
      {children}
    </div>
  )
}

function CardFooter({ 
  className, 
  children 
}: BaseComponentProps) {
  return (
    <div className={cn('px-6 py-4 border-t border-gray-200', className)}>
      {children}
    </div>
  )
}

// ================================
// CONTAINER/PRESENTATIONAL PATTERN
// ================================

interface ContainerComponentProps {
  // Data fetching logic
  fetchData: () => Promise<any>
  // State management
  initialState?: any
  // Event handlers
  onAction?: (data: any) => void
  // Other props
  [key: string]: any
}

function createContainer<P extends ContainerComponentProps>(
  Component: React.ComponentType<P>,
  useContainerLogic: (props: Omit<P, keyof ContainerComponentProps>) => {
    data: any
    isLoading: boolean
    error: string | null
    actions: Record<string, (...args: any[]) => any>
  }
) {
  return function ContainerComponent(props: P) {
    const { fetchData, onAction, ...componentProps } = props
    const { data, isLoading, error, actions } = useContainerLogic(componentProps as any)

    const handleAction = (actionData: any) => {
      actions[actionData.type]?.(actionData.payload)
      onAction?.(actionData)
    }

    return (
      <Component
        {...(componentProps as P)}
        data={data}
        isLoading={isLoading}
        error={error}
        actions={actions}
        onAction={handleAction}
      />
    )
  }
}

// ================================
// PERFORMANCE OPTIMIZATIONS
// ================================

function MemoComponent<T extends BaseComponentProps>(
  Component: React.ComponentType<T>,
  propsAreEqual?: (prevProps: T, nextProps: T) => boolean
) {
  return React.memo(Component, propsAreEqual)
}

function LazyComponent<T extends BaseComponentProps>(
  importFn: () => Promise<{ default: React.ComponentType<T> }>,
  fallback?: ReactNode
) {
  const LazyComponent = React.lazy(importFn)
  
  return function LazyWrapper(props: T) {
    return (
      <React.Suspense fallback={fallback || <LoadingCard />}>
        <LazyComponent {...props} />
      </React.Suspense>
    )
  }
}

// ================================
// TYPESCRIPT HELPERS
// ================================

type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>
type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
type RequiredBy<T, K extends keyof T> = T & Required<Pick<T, K>>
type MergeProps<T, U> = T & U

// ================================
// EXPORTS
// ================================

export {
  cn,
  LoadingSpinner,
  LoadingSkeleton,
  LoadingCard,
  ErrorMessage,
  ErrorBoundary,
  Container,
  Section,
  Grid,
  DataCard,
  AsyncData,
  withState,
  Conditional,
  Match,
  Card,
  CardHeader,
  CardContent,
  CardFooter,
  createContainer,
  MemoComponent,
  LazyComponent
}