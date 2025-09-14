/**
 * Checkbox component - Checkbox input implementation
 */
'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Check, Minus } from 'lucide-react'

interface CheckboxProps {
  id?: string
  checked?: boolean | 'indeterminate'
  onCheckedChange?: (checked: boolean) => void
  disabled?: boolean
  className?: string
  'aria-label'?: string
  'aria-labelledby'?: string
  'aria-describedby'?: string
}

export const Checkbox = React.forwardRef<HTMLButtonElement, CheckboxProps>(
  ({ id, checked, onCheckedChange, disabled, className, ...props }, ref) => {
    const handleClick = () => {
      if (!disabled && onCheckedChange) {
        const newChecked = checked === 'indeterminate' ? true : !checked
        onCheckedChange(newChecked)
      }
    }

    const handleKeyDown = (event: React.KeyboardEvent) => {
      if (event.key === ' ' || event.key === 'Enter') {
        event.preventDefault()
        handleClick()
      }
    }

    return (
      <button
        ref={ref}
        id={id}
        type="button"
        role="checkbox"
        aria-checked={checked === 'indeterminate' ? 'mixed' : checked}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        className={cn(
          "peer h-4 w-4 shrink-0 rounded-sm border border-primary ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          "border-gray-300 dark:border-gray-600",
          "hover:border-blue-500 dark:hover:border-blue-400",
          "focus:border-blue-500 focus:ring-blue-500/20 dark:focus:border-blue-400 dark:focus:ring-blue-400/20",
          checked === true && "bg-blue-600 text-white border-blue-600 dark:bg-blue-500 dark:border-blue-500",
          checked === 'indeterminate' && "bg-blue-600 text-white border-blue-600 dark:bg-blue-500 dark:border-blue-500",
          disabled && "bg-gray-100 dark:bg-gray-800 cursor-not-allowed",
          className
        )}
        {...props}
      >
        {checked === true && (
          <Check className="h-3 w-3" strokeWidth={3} />
        )}
        {checked === 'indeterminate' && (
          <Minus className="h-3 w-3" strokeWidth={3} />
        )}
      </button>
    )
  }
)

Checkbox.displayName = 'Checkbox'