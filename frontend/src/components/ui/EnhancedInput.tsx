/**
 * Enhanced Input Component
 * Professional input with instant validation feedback and micro-interactions
 */
'use client'

import React, { forwardRef, useState, useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'
import { microInteractionsService } from '@/services/micro-interactions.service'
import { Eye, EyeOff, Check, X, AlertCircle, Search, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export interface ValidationRule {
  test: (value: string) => boolean
  message: string
  type?: 'error' | 'warning'
}

export interface EnhancedInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string
  description?: string
  error?: string
  success?: boolean
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'filled' | 'flushed' | 'unstyled'
  validation?: ValidationRule[]
  instantValidation?: boolean
  showPasswordToggle?: boolean
  debounceMs?: number
  onValidation?: (isValid: boolean, errors: string[]) => void
}

const inputSizes = {
  sm: 'px-3 py-2 text-sm',
  md: 'px-4 py-2.5 text-sm',
  lg: 'px-4 py-3 text-base'
}

const inputVariants = {
  default: 'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 rounded-lg',
  filled: 'border-0 bg-gray-100 dark:bg-gray-700 rounded-lg',
  flushed: 'border-0 border-b-2 border-gray-300 dark:border-gray-600 rounded-none bg-transparent',
  unstyled: 'border-0 bg-transparent'
}

export const EnhancedInput = forwardRef<HTMLInputElement, EnhancedInputProps>(({
  label,
  description,
  error,
  success,
  loading,
  leftIcon,
  rightIcon,
  size = 'md',
  variant = 'default',
  validation = [],
  instantValidation = true,
  showPasswordToggle = false,
  debounceMs = 300,
  onValidation,
  className,
  type: inputType = 'text',
  value,
  onChange,
  onFocus,
  onBlur,
  ...props
}, ref) => {
  const [internalValue, setInternalValue] = useState(value || '')
  const [isFocused, setIsFocused] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [validationErrors, setValidationErrors] = useState<string[]>([])
  const [validationWarnings, setValidationWarnings] = useState<string[]>([])
  const [isValid, setIsValid] = useState(true)
  const inputRef = useRef<HTMLInputElement>(null)
  const debounceRef = useRef<NodeJS.Timeout>()

  const combinedRef = ref || inputRef
  const actualType = showPasswordToggle && inputType === 'password'
    ? (showPassword ? 'text' : 'password')
    : inputType

  const isPasswordType = inputType === 'password' || showPasswordToggle

  // Validation logic
  const validateInput = (val: string) => {
    const errors: string[] = []
    const warnings: string[] = []

    validation.forEach(rule => {
      if (!rule.test(val)) {
        if (rule.type === 'warning') {
          warnings.push(rule.message)
        } else {
          errors.push(rule.message)
        }
      }
    })

    setValidationErrors(errors)
    setValidationWarnings(warnings)

    const valid = errors.length === 0
    setIsValid(valid)
    onValidation?.(valid, errors)

    return valid
  }

  // Debounced validation
  useEffect(() => {
    if (!instantValidation || !validation.length) return

    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    debounceRef.current = setTimeout(() => {
      validateInput(String(internalValue))
    }, debounceMs)

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [internalValue, validation, instantValidation, debounceMs])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setInternalValue(newValue)
    onChange?.(e)
  }

  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(true)

    // Add focus micro-interaction
    if (typeof combinedRef === 'object' && combinedRef?.current) {
      microInteractionsService.createButtonPress(combinedRef.current.parentElement as HTMLElement)
    }

    onFocus?.(e)
  }

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(false)

    // Validate on blur if not instant validation
    if (!instantValidation && validation.length) {
      validateInput(String(internalValue))
    }

    onBlur?.(e)
  }

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  // Determine validation state
  const hasError = error || validationErrors.length > 0
  const hasWarning = validationWarnings.length > 0
  const hasSuccess = success || (validation.length > 0 && isValid && internalValue && !hasError)

  // Focus ring color based on state
  const getFocusRingColor = () => {
    if (hasError) return 'focus:ring-red-500 focus:border-red-500'
    if (hasWarning) return 'focus:ring-yellow-500 focus:border-yellow-500'
    if (hasSuccess) return 'focus:ring-green-500 focus:border-green-500'
    return 'focus:ring-primary-500 focus:border-primary-500'
  }

  // Border color based on state
  const getBorderColor = () => {
    if (isFocused) return ''
    if (hasError) return 'border-red-300 dark:border-red-600'
    if (hasWarning) return 'border-yellow-300 dark:border-yellow-600'
    if (hasSuccess) return 'border-green-300 dark:border-green-600'
    return 'border-gray-300 dark:border-gray-600'
  }

  return (
    <div className="w-full">
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      {/* Input Container */}
      <div className="relative">
        <div className={cn(
          'relative flex items-center transition-all duration-200',
          inputVariants[variant],
          getBorderColor(),
          getFocusRingColor(),
          {
            'ring-2 ring-current/20': isFocused,
            'shadow-sm': variant === 'default',
            'hover:shadow-md': variant === 'default' && !props.disabled,
          }
        )}>
          {/* Left Icon */}
          {leftIcon && (
            <div className="absolute left-3 flex items-center pointer-events-none">
              <div className={cn(
                'text-gray-400 transition-colors duration-200',
                isFocused && 'text-primary-500',
                hasError && 'text-red-500',
                hasSuccess && 'text-green-500'
              )}>
                {leftIcon}
              </div>
            </div>
          )}

          {/* Input Field */}
          <input
            ref={combinedRef}
            type={actualType}
            value={internalValue}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            className={cn(
              'w-full bg-transparent border-0 focus:outline-none focus:ring-0 placeholder-gray-400 text-gray-900 dark:text-gray-100',
              inputSizes[size],
              {
                'pl-10': leftIcon,
                'pr-10': rightIcon || loading || hasSuccess || hasError || isPasswordType,
              },
              className
            )}
            {...props}
          />

          {/* Right Icons */}
          <div className="absolute right-3 flex items-center space-x-1">
            {/* Loading */}
            {loading && (
              <Loader2 className="h-4 w-4 text-gray-400 animate-spin" />
            )}

            {/* Validation States */}
            {!loading && hasSuccess && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="text-green-500"
              >
                <Check className="h-4 w-4" />
              </motion.div>
            )}

            {!loading && hasError && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="text-red-500"
              >
                <X className="h-4 w-4" />
              </motion.div>
            )}

            {!loading && hasWarning && !hasError && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="text-yellow-500"
              >
                <AlertCircle className="h-4 w-4" />
              </motion.div>
            )}

            {/* Password Toggle */}
            {isPasswordType && !loading && (
              <button
                type="button"
                onClick={togglePasswordVisibility}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            )}

            {/* Custom Right Icon */}
            {rightIcon && !loading && !hasSuccess && !hasError && !hasWarning && !isPasswordType && (
              <div className="text-gray-400">
                {rightIcon}
              </div>
            )}
          </div>
        </div>

        {/* Progress Bar for validation strength */}
        {validation.length > 0 && internalValue && (
          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            className="mt-1 h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
          >
            <motion.div
              className={cn(
                'h-full transition-all duration-300',
                hasError ? 'bg-red-500' : hasWarning ? 'bg-yellow-500' : 'bg-green-500'
              )}
              style={{
                width: `${((validation.length - validationErrors.length - validationWarnings.length) / validation.length) * 100}%`
              }}
            />
          </motion.div>
        )}
      </div>

      {/* Description */}
      {description && !hasError && !hasWarning && (
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {description}
        </p>
      )}

      {/* Validation Messages */}
      <AnimatePresence>
        {(error || validationErrors.length > 0) && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-2 space-y-1"
          >
            {error && (
              <p className="text-sm text-red-600 dark:text-red-400 flex items-center">
                <X className="h-3 w-3 mr-1 flex-shrink-0" />
                {error}
              </p>
            )}
            {validationErrors.map((err, index) => (
              <p key={index} className="text-sm text-red-600 dark:text-red-400 flex items-center">
                <X className="h-3 w-3 mr-1 flex-shrink-0" />
                {err}
              </p>
            ))}
          </motion.div>
        )}

        {validationWarnings.length > 0 && !hasError && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-2 space-y-1"
          >
            {validationWarnings.map((warning, index) => (
              <p key={index} className="text-sm text-yellow-600 dark:text-yellow-400 flex items-center">
                <AlertCircle className="h-3 w-3 mr-1 flex-shrink-0" />
                {warning}
              </p>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
})

EnhancedInput.displayName = 'EnhancedInput'