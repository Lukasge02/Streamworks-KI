/**
 * Unified Loading States for StreamWorks
 * Provides consistent loading experiences across all components
 */

import React from 'react'
import { cn } from '@/components/shared/componentPatterns'
import { LoadingSkeleton } from '@/components/shared/componentPatterns'

// ================================
// LOADING STATE TYPES
// ================================

export type LoadingSize = 'sm' | 'md' | 'lg' | 'xl'
export type LoadingVariant = 'spinner' | 'skeleton' | 'dots' | 'pulse' | 'bar'
export type LoadingColor = 'primary' | 'secondary' | 'success' | 'warning' | 'error'

export interface LoadingStateProps {
  isLoading: boolean
  size?: LoadingSize
  variant?: LoadingVariant
  color?: LoadingColor
  className?: string
  text?: string
  overlay?: boolean
  center?: boolean
}

// ================================
// LOADING CONFIGURATION
// ================================

const sizeClasses = {
  sm: {
    spinner: 'w-4 h-4',
    skeleton: 'h-4',
    dots: 'w-2 h-2',
    pulse: 'w-8 h-8',
    bar: 'h-1'
  },
  md: {
    spinner: 'w-6 h-6',
    skeleton: 'h-6',
    dots: 'w-3 h-3',
    pulse: 'w-12 h-12',
    bar: 'h-2'
  },
  lg: {
    spinner: 'w-8 h-8',
    skeleton: 'h-8',
    dots: 'w-4 h-4',
    pulse: 'w-16 h-16',
    bar: 'h-3'
  },
  xl: {
    spinner: 'w-12 h-12',
    skeleton: 'h-12',
    dots: 'w-6 h-6',
    pulse: 'w-24 h-24',
    bar: 'h-4'
  }
}

const colorClasses = {
  primary: {
    spinner: 'border-blue-600 border-t-blue-600',
    skeleton: 'bg-blue-200',
    dots: 'bg-blue-600',
    pulse: 'bg-blue-600',
    bar: 'bg-blue-600'
  },
  secondary: {
    spinner: 'border-gray-600 border-t-gray-600',
    skeleton: 'bg-gray-200',
    dots: 'bg-gray-600',
    pulse: 'bg-gray-600',
    bar: 'bg-gray-600'
  },
  success: {
    spinner: 'border-green-600 border-t-green-600',
    skeleton: 'bg-green-200',
    dots: 'bg-green-600',
    pulse: 'bg-green-600',
    bar: 'bg-green-600'
  },
  warning: {
    spinner: 'border-yellow-600 border-t-yellow-600',
    skeleton: 'bg-yellow-200',
    dots: 'bg-yellow-600',
    pulse: 'bg-yellow-600',
    bar: 'bg-yellow-600'
  },
  error: {
    spinner: 'border-red-600 border-t-red-600',
    skeleton: 'bg-red-200',
    dots: 'bg-red-600',
    pulse: 'bg-red-600',
    bar: 'bg-red-600'
  }
}

// ================================
// SPINNER LOADING
// ================================

function LoadingSpinner({ 
  size = 'md', 
  color = 'primary', 
  className 
}: { 
  size?: LoadingSize
  color?: LoadingColor
  className?: string 
}) {
  return (
    <div 
      className={cn(
        'animate-spin rounded-full border-2 border-gray-300',
        sizeClasses[size].spinner,
        colorClasses[color].spinner,
        className
      )} 
    />
  )
}

// ================================
// DOTS LOADING
// ================================

function LoadingDots({ 
  size = 'md', 
  color = 'primary',
  className 
}: { 
  size?: LoadingSize
  color?: LoadingColor
  className?: string 
}) {
  return (
    <div className={cn('flex space-x-1', className)}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={cn(
            'rounded-full animate-bounce',
            sizeClasses[size].dots,
            colorClasses[color].dots
          )}
          style={{
            animationDelay: `${i * 0.1}s`
          }}
        />
      ))}
    </div>
  )
}

// ================================
// PULSE LOADING
// ================================

function LoadingPulse({ 
  size = 'md', 
  color = 'primary',
  className 
}: { 
  size?: LoadingSize
  color?: LoadingColor
  className?: string 
}) {
  return (
    <div 
      className={cn(
        'animate-pulse rounded-full',
        sizeClasses[size].pulse,
        colorClasses[color].pulse,
        className
      )} 
    />
  )
}

// ================================
// PROGRESS BAR LOADING
// ================================

function LoadingBar({ 
  progress = 0,
  color = 'primary',
  className 
}: { 
  progress?: number
  color?: LoadingColor
  className?: string 
}) {
  return (
    <div className={cn('w-full bg-gray-200 rounded-full overflow-hidden', className)}>
      <div 
        className={cn(
          'h-full transition-all duration-300 ease-out',
          colorClasses[color].bar
        )}
        style={{ width: `${progress}%` }}
      />
    </div>
  )
}

// ================================
// SKELETON LOADING
// ================================

export interface LoadingSkeletonProps {
  lines?: number
  size?: LoadingSize
  className?: string
  animate?: boolean
}

function LoadingSkeletonComponent({ 
  lines = 1, 
  size = 'md', 
  className,
  animate = true 
}: LoadingSkeletonProps) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={cn(
            'rounded',
            sizeClasses[size].skeleton,
            animate && 'animate-pulse',
            colorClasses.primary.skeleton,
            className
          )}
          style={{ 
            width: `${Math.random() * 40 + 60}%`,
            animationDelay: `${i * 0.1}s`
          }}
        />
      ))}
    </div>
  )
}

// ================================
// CARD LOADING
// ================================

function LoadingCard({ 
  className,
  avatar = false,
  title = true,
  content = true,
  footer = false
}: { 
  className?: string
  avatar?: boolean
  title?: boolean
  content?: boolean
  footer?: boolean
}) {
  return (
    <div className={cn('bg-white rounded-lg shadow-sm border border-gray-200 p-4', className)}>
      {avatar && (
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-gray-200 rounded-full animate-pulse" />
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
          </div>
        </div>
      )}
      
      {title && (
        <div className="mb-4">
          <div className="h-6 bg-gray-200 rounded animate-pulse w-2/3 mb-2" />
          <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
        </div>
      )}
      
      {content && (
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded animate-pulse" />
          <div className="h-4 bg-gray-200 rounded animate-pulse w-5/6" />
          <div className="h-4 bg-gray-200 rounded animate-pulse w-4/6" />
        </div>
      )}
      
      {footer && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex justify-between">
            <div className="h-8 bg-gray-200 rounded animate-pulse w-20" />
            <div className="h-8 bg-gray-200 rounded animate-pulse w-24" />
          </div>
        </div>
      )}
    </div>
  )
}

// ================================
// TABLE LOADING
// ================================

function LoadingTable({ 
  rows = 5,
  columns = 4,
  className 
}: { 
  rows?: number
  columns?: number
  className?: string 
}) {
  return (
    <div className={cn('overflow-hidden rounded-lg border border-gray-200', className)}>
      <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
        <div className="h-6 bg-gray-200 rounded animate-pulse w-32" />
      </div>
      <div className="divide-y divide-gray-200">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="px-6 py-4">
            <div className="grid grid-cols-4 gap-4">
              {Array.from({ length: columns }).map((_, colIndex) => (
                <div
                  key={colIndex}
                  className="h-4 bg-gray-200 rounded animate-pulse"
                  style={{ width: `${Math.random() * 40 + 60}%` }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ================================
// OVERLAY LOADING
// ================================

function LoadingOverlay({ 
  isLoading,
  text = 'Loading...',
  size = 'lg',
  color = 'primary',
  className 
}: LoadingStateProps & { text?: string }) {
  if (!isLoading) return null

  return (
    <div className={cn(
      'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50',
      className
    )}>
      <div className="bg-white rounded-lg p-6 flex flex-col items-center space-y-4">
        <LoadingSpinner size={size} color={color} />
        <p className="text-gray-700 font-medium">{text}</p>
      </div>
    </div>
  )
}

// ================================
// INLINE LOADING
// ================================

function InlineLoading({ 
  isLoading,
  text = 'Loading...',
  size = 'sm',
  variant = 'spinner',
  color = 'primary',
  className 
}: LoadingStateProps) {
  if (!isLoading) return null

  const LoadingComponent = {
    spinner: LoadingSpinner,
    dots: LoadingDots,
    pulse: LoadingPulse,
    skeleton: LoadingSkeletonComponent,
    bar: LoadingBar
  }[variant]

  return (
    <div className={cn('flex items-center space-x-2', className)}>
      <LoadingComponent size={size} color={color} />
      {text && (
        <span className="text-sm text-gray-600">{text}</span>
      )}
    </div>
  )
}

// ================================
// PAGE LOADING
// ================================

function PageLoading({ 
  message = 'Loading StreamWorks...',
  subtitle = 'Please wait a moment'
}: { 
  message?: string
  subtitle?: string 
}) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="mb-8">
          <LoadingSpinner size="xl" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{message}</h1>
        <p className="text-gray-600">{subtitle}</p>
        
        {/* Animated progress dots */}
        <div className="mt-8 flex justify-center space-x-2">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-3 h-3 bg-blue-600 rounded-full animate-bounce"
              style={{
                animationDelay: `${i * 0.1}s`
              }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

// ================================
// CONTENT LOADING
// ================================

function ContentLoading({
  isLoading,
  children,
  fallback,
  size = 'md',
  variant = 'spinner',
  className
}: {
  isLoading: boolean
  children: React.ReactNode
  fallback?: React.ReactNode
  size?: LoadingSize
  variant?: LoadingVariant
  className?: string
}) {
  if (!isLoading) return <>{children}</>

  if (fallback) return <>{fallback}</>

  const LoadingComponent = {
    spinner: LoadingSpinner,
    dots: LoadingDots,
    pulse: LoadingPulse,
    skeleton: LoadingSkeletonComponent,
    bar: LoadingBar
  }[variant]

  return (
    <div className={cn('flex items-center justify-center p-8', className)}>
      <LoadingComponent size={size} />
    </div>
  )
}

// ================================
// LOADING WITH PROGRESS
// ================================

export interface ProgressLoadingProps {
  isLoading: boolean
  progress?: number
  message?: string
  steps?: string[]
  currentStep?: number
  className?: string
}

function ProgressLoading({
  isLoading,
  progress,
  message = 'Processing...',
  steps = [],
  currentStep = 0,
  className
}: ProgressLoadingProps) {
  if (!isLoading) return null

  return (
    <div className={cn('bg-white rounded-lg p-6 space-y-4', className)}>
      {/* Progress bar */}
      {progress !== undefined && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-700">{message}</span>
            <span className="text-gray-500">{progress}%</span>
          </div>
          <LoadingBar progress={progress} />
        </div>
      )}

      {/* Steps */}
      {steps.length > 0 && (
        <div className="space-y-2">
          <div className="text-sm text-gray-700">Progress:</div>
          <div className="space-y-1">
            {steps.map((step, index) => (
              <div
                key={index}
                className={cn(
                  'flex items-center space-x-2 text-sm',
                  index <= currentStep ? 'text-green-600' : 'text-gray-400'
                )}
              >
                <div className={cn(
                  'w-4 h-4 rounded-full border-2',
                  index < currentStep ? 'bg-green-600 border-green-600' :
                  index === currentStep ? 'border-green-600' :
                  'border-gray-300'
                )}>
                  {index < currentStep && (
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
                <span>{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ================================
// LOADING HOOK
// ================================

function useLoadingState(initialState = false) {
  const [isLoading, setIsLoading] = React.useState(initialState)
  const [loadingMessage, setLoadingMessage] = React.useState<string | null>(null)
  const [loadingProgress, setLoadingProgress] = React.useState<number | null>(null)

  const startLoading = React.useCallback((message?: string) => {
    setIsLoading(true)
    setLoadingMessage(message || null)
    setLoadingProgress(null)
  }, [])

  const stopLoading = React.useCallback(() => {
    setIsLoading(false)
    setLoadingMessage(null)
    setLoadingProgress(null)
  }, [])

  const updateProgress = React.useCallback((progress: number) => {
    setLoadingProgress(progress)
  }, [])

  const updateMessage = React.useCallback((message: string) => {
    setLoadingMessage(message)
  }, [])

  return {
    isLoading,
    loadingMessage,
    loadingProgress,
    startLoading,
    stopLoading,
    updateProgress,
    updateMessage
  }
}

// ================================
// EXPORTS
// ================================

export {
  LoadingSpinner,
  LoadingDots,
  LoadingPulse,
  LoadingBar,
  LoadingSkeletonComponent as LoadingSkeleton,
  LoadingCard,
  LoadingTable,
  LoadingOverlay,
  InlineLoading,
  PageLoading,
  ContentLoading,
  ProgressLoading,
  useLoadingState
}