/**
 * Enhanced Button Component
 * Professional button with ripple effects, loading states, and micro-interactions
 */
'use client'

import React, { forwardRef, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { microInteractionsService } from '@/services/micro-interactions.service'
import { Loader2 } from 'lucide-react'

export interface EnhancedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'ghost' | 'outline'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  loading?: boolean
  loadingText?: string
  ripple?: boolean
  rippleColor?: string
  icon?: React.ReactNode
  rightIcon?: React.ReactNode
  fullWidth?: boolean
  rounded?: boolean
  elevation?: 'none' | 'sm' | 'md' | 'lg'
}

const buttonVariants = {
  default: 'bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700',
  primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500 shadow-primary-500/20',
  secondary: 'bg-arvato-gray-medium text-white hover:bg-gray-600 focus:ring-gray-500',
  success: 'bg-arvato-accent-green text-white hover:bg-green-600 focus:ring-green-500 shadow-green-500/20',
  warning: 'bg-arvato-accent-yellow text-white hover:bg-yellow-600 focus:ring-yellow-500 shadow-yellow-500/20',
  danger: 'bg-arvato-accent-red text-white hover:bg-red-600 focus:ring-red-500 shadow-red-500/20',
  ghost: 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800',
  outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 dark:border-primary-400 dark:text-primary-400 dark:hover:bg-primary-900/20'
}

const buttonSizes = {
  xs: 'px-2.5 py-1.5 text-xs',
  sm: 'px-3 py-2 text-sm',
  md: 'px-4 py-2.5 text-sm',
  lg: 'px-6 py-3 text-base',
  xl: 'px-8 py-4 text-lg'
}

const buttonElevations = {
  none: '',
  sm: 'shadow-sm',
  md: 'shadow-md',
  lg: 'shadow-lg shadow-current/10'
}

export const EnhancedButton = forwardRef<HTMLButtonElement, EnhancedButtonProps>(({
  variant = 'default',
  size = 'md',
  loading = false,
  loadingText,
  ripple = true,
  rippleColor,
  icon,
  rightIcon,
  fullWidth = false,
  rounded = false,
  elevation = 'sm',
  className,
  children,
  disabled,
  onClick,
  onMouseDown,
  ...props
}, ref) => {
  const buttonRef = useRef<HTMLButtonElement>(null)
  const combinedRef = ref || buttonRef

  useEffect(() => {
    const button = typeof combinedRef === 'object' && combinedRef?.current
    if (!button) return

    // Add interactive class for enhanced hover effects
    button.classList.add('streamworks-interactive')

    return () => {
      button.classList.remove('streamworks-interactive')
    }
  }, [combinedRef])

  const handleMouseDown = (event: React.MouseEvent<HTMLButtonElement>) => {
    const button = event.currentTarget

    // Create ripple effect
    if (ripple && !disabled && !loading) {
      const color = rippleColor || (variant === 'ghost' || variant === 'outline' ?
        'rgba(59, 130, 246, 0.3)' : 'rgba(255, 255, 255, 0.4)')

      microInteractionsService.createRipple(button, event.nativeEvent, { color })
      microInteractionsService.createButtonPress(button)
    }

    onMouseDown?.(event)
  }

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || loading) return
    onClick?.(event)
  }

  const isDisabled = disabled || loading

  return (
    <button
      ref={combinedRef}
      type="button"
      disabled={isDisabled}
      className={cn(
        // Base styles
        'relative inline-flex items-center justify-center font-medium transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-900',
        'transform-gpu will-change-transform',

        // Responsive and interaction states
        'active:scale-[0.98] hover:-translate-y-0.5',
        'disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none',

        // Variants
        buttonVariants[variant],

        // Sizes
        buttonSizes[size],

        // Elevation
        buttonElevations[elevation],

        // Conditional styles
        {
          'w-full': fullWidth,
          'rounded-full': rounded,
          'rounded-lg': !rounded,
          'overflow-hidden': ripple,
          'hover:shadow-xl': elevation === 'lg' && !isDisabled,
          'ring-2 ring-primary-500/20': variant === 'primary' && !isDisabled,
        },

        className
      )}
      onClick={handleClick}
      onMouseDown={handleMouseDown}
      {...props}
    >
      {/* Loading state */}
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-current/10 rounded-lg">
          <Loader2 className="h-4 w-4 animate-spin text-current mr-2" />
          {loadingText && <span>{loadingText}</span>}
        </div>
      )}

      {/* Button content */}
      <div className={cn(
        'flex items-center justify-center space-x-2 transition-opacity duration-200',
        { 'opacity-0': loading }
      )}>
        {icon && <span className="flex-shrink-0">{icon}</span>}
        {children && <span>{children}</span>}
        {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
      </div>

      {/* Subtle gradient overlay for depth */}
      {elevation !== 'none' && (
        <div className="absolute inset-0 rounded-lg bg-gradient-to-t from-black/5 to-transparent pointer-events-none" />
      )}
    </button>
  )
})

EnhancedButton.displayName = 'EnhancedButton'