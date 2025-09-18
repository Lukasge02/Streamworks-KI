/**
 * Skeleton Loader Component
 * Professional skeleton loading states with shimmer animations
 */
'use client'

import React, { useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'
import { microInteractionsService } from '@/services/micro-interactions.service'

export interface SkeletonLoaderProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded'
  animation?: 'pulse' | 'shimmer' | 'none'
  lines?: number
  height?: number | string
  width?: number | string
  children?: React.ReactNode
  loading?: boolean
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  className,
  variant = 'rectangular',
  animation = 'shimmer',
  lines = 1,
  height,
  width,
  children,
  loading = true
}) => {
  const skeletonRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!loading || !skeletonRef.current) return

    if (animation === 'shimmer') {
      microInteractionsService.createShimmer(skeletonRef.current)
    } else if (animation === 'pulse') {
      microInteractionsService.createPulse(skeletonRef.current, 'light')
    }

    return () => {
      if (skeletonRef.current) {
        skeletonRef.current.style.animation = ''
        skeletonRef.current.style.background = ''
      }
    }
  }, [loading, animation])

  if (!loading && children) {
    return <>{children}</>
  }

  if (!loading) {
    return null
  }

  const getVariantClasses = () => {
    switch (variant) {
      case 'text':
        return 'h-4 rounded'
      case 'circular':
        return 'rounded-full aspect-square'
      case 'rectangular':
        return 'rounded'
      case 'rounded':
        return 'rounded-lg'
      default:
        return 'rounded'
    }
  }

  const getDefaultDimensions = () => {
    if (variant === 'text') {
      return { width: '100%', height: '1rem' }
    }
    if (variant === 'circular') {
      return { width: '2.5rem', height: '2.5rem' }
    }
    return { width: '100%', height: '2rem' }
  }

  const defaultDimensions = getDefaultDimensions()
  const style = {
    width: width || defaultDimensions.width,
    height: height || defaultDimensions.height,
  }

  if (lines > 1) {
    return (
      <div className={cn('space-y-2', className)}>
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            ref={index === 0 ? skeletonRef : undefined}
            className={cn(
              'bg-gray-200 dark:bg-gray-700 animate-pulse',
              getVariantClasses(),
              // Last line is typically shorter
              index === lines - 1 && variant === 'text' && 'w-3/4'
            )}
            style={index === 0 ? style : undefined}
          />
        ))}
      </div>
    )
  }

  return (
    <div
      ref={skeletonRef}
      className={cn(
        'bg-gray-200 dark:bg-gray-700',
        getVariantClasses(),
        animation === 'pulse' && 'animate-pulse',
        className
      )}
      style={style}
    />
  )
}

// Specialized skeleton components for common use cases
export const SkeletonText: React.FC<Omit<SkeletonLoaderProps, 'variant'>> = (props) => (
  <SkeletonLoader variant="text" {...props} />
)

export const SkeletonCircle: React.FC<Omit<SkeletonLoaderProps, 'variant'>> = (props) => (
  <SkeletonLoader variant="circular" {...props} />
)

export const SkeletonCard: React.FC<{ loading?: boolean; children?: React.ReactNode; className?: string }> = ({
  loading = true,
  children,
  className
}) => {
  if (!loading && children) {
    return <>{children}</>
  }

  if (!loading) {
    return null
  }

  return (
    <div className={cn('p-4 border border-gray-200 dark:border-gray-700 rounded-lg space-y-3', className)}>
      <div className="flex items-start space-x-3">
        <SkeletonCircle width="3rem" height="3rem" />
        <div className="flex-1 space-y-2">
          <SkeletonText height="1.25rem" width="60%" />
          <SkeletonText height="1rem" width="40%" />
        </div>
      </div>
      <SkeletonText lines={3} />
      <div className="flex space-x-2">
        <SkeletonLoader width="4rem" height="2rem" variant="rounded" />
        <SkeletonLoader width="4rem" height="2rem" variant="rounded" />
      </div>
    </div>
  )
}

export const SkeletonTable: React.FC<{
  rows?: number
  columns?: number
  loading?: boolean
  children?: React.ReactNode
  className?: string
}> = ({
  rows = 5,
  columns = 4,
  loading = true,
  children,
  className
}) => {
  if (!loading && children) {
    return <>{children}</>
  }

  if (!loading) {
    return null
  }

  return (
    <div className={cn('space-y-3', className)}>
      {/* Header */}
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
        {Array.from({ length: columns }).map((_, index) => (
          <SkeletonText key={`header-${index}`} height="1.5rem" width="80%" />
        ))}
      </div>

      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={`row-${rowIndex}`}
          className="grid gap-4 py-2 border-b border-gray-100 dark:border-gray-800"
          style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <SkeletonText
              key={`cell-${rowIndex}-${colIndex}`}
              height="1rem"
              width={colIndex === 0 ? '90%' : '70%'}
            />
          ))}
        </div>
      ))}
    </div>
  )
}

export const SkeletonList: React.FC<{
  items?: number
  showAvatar?: boolean
  showActions?: boolean
  loading?: boolean
  children?: React.ReactNode
  className?: string
}> = ({
  items = 5,
  showAvatar = true,
  showActions = true,
  loading = true,
  children,
  className
}) => {
  if (!loading && children) {
    return <>{children}</>
  }

  if (!loading) {
    return null
  }

  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: items }).map((_, index) => (
        <div key={index} className="flex items-center space-x-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
          {showAvatar && <SkeletonCircle width="2.5rem" height="2.5rem" />}
          <div className="flex-1 space-y-2">
            <SkeletonText height="1.25rem" width="70%" />
            <SkeletonText height="1rem" width="50%" />
          </div>
          {showActions && (
            <div className="flex space-x-2">
              <SkeletonLoader width="2rem" height="2rem" variant="rounded" />
              <SkeletonLoader width="2rem" height="2rem" variant="rounded" />
            </div>
          )}
        </div>
      ))}
    </div>
  )
}