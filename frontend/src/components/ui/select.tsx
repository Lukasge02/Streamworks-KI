/**
 * Select component - Custom select dropdown implementation
 */
'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { ChevronDown, Check } from 'lucide-react'

interface SelectContextValue {
  value?: string
  onValueChange?: (value: string) => void
  open: boolean
  onOpenChange: (open: boolean) => void
  placeholder?: string
  disabled?: boolean
}

const SelectContext = React.createContext<SelectContextValue | null>(null)

interface SelectProps {
  value?: string
  onValueChange?: (value: string) => void
  disabled?: boolean
  children: React.ReactNode
}

export function Select({ value, onValueChange, disabled, children }: SelectProps) {
  const [open, setOpen] = React.useState(false)
  
  return (
    <SelectContext.Provider value={{ 
      value, 
      onValueChange, 
      open, 
      onOpenChange: setOpen,
      disabled 
    }}>
      <div className="relative">
        {children}
      </div>
    </SelectContext.Provider>
  )
}

interface SelectTriggerProps {
  className?: string
  children: React.ReactNode
}

export function SelectTrigger({ className, children }: SelectTriggerProps) {
  const context = React.useContext(SelectContext)
  
  const handleClick = () => {
    if (!context?.disabled) {
      context?.onOpenChange(!context.open)
    }
  }

  return (
    <button
      type="button"
      className={cn(
        "flex items-center justify-between w-full px-3 py-2 text-sm bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-gray-800 dark:border-gray-600 dark:text-white dark:hover:bg-gray-700",
        context?.open && "ring-2 ring-blue-500 border-blue-500",
        className
      )}
      onClick={handleClick}
      disabled={context?.disabled}
      aria-expanded={context?.open}
      aria-haspopup="listbox"
    >
      <span className="truncate">{children}</span>
      <ChevronDown className={cn(
        "ml-2 h-4 w-4 flex-shrink-0 transition-transform",
        context?.open && "transform rotate-180"
      )} />
    </button>
  )
}

interface SelectValueProps {
  placeholder?: string
  className?: string
}

export function SelectValue({ placeholder, className }: SelectValueProps) {
  const context = React.useContext(SelectContext)
  
  return (
    <span className={cn("truncate", className)}>
      {context?.value || placeholder}
    </span>
  )
}

interface SelectContentProps {
  className?: string
  children: React.ReactNode
}

export function SelectContent({ className, children }: SelectContentProps) {
  const context = React.useContext(SelectContext)
  if (!context?.open) return null

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 z-40"
        onClick={() => context.onOpenChange(false)}
      />
      
      {/* Content */}
      <div
        className={cn(
          "absolute z-50 mt-1 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg max-h-60 overflow-auto",
          className
        )}
        role="listbox"
      >
        {children}
      </div>
    </>
  )
}

interface SelectItemProps {
  value: string
  className?: string
  disabled?: boolean
  children: React.ReactNode
}

export function SelectItem({ value, className, disabled, children }: SelectItemProps) {
  const context = React.useContext(SelectContext)
  const isSelected = context?.value === value
  
  const handleClick = () => {
    if (!disabled) {
      context?.onValueChange?.(value)
      context?.onOpenChange(false)
    }
  }

  return (
    <button
      type="button"
      className={cn(
        "flex items-center justify-between w-full px-3 py-2 text-sm text-left hover:bg-gray-100 dark:hover:bg-gray-700 focus:bg-gray-100 dark:focus:bg-gray-700 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed",
        "first:rounded-t-md last:rounded-b-md",
        isSelected && "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400",
        className
      )}
      onClick={handleClick}
      disabled={disabled}
      role="option"
      aria-selected={isSelected}
    >
      <span className="truncate">{children}</span>
      {isSelected && <Check className="ml-2 h-4 w-4 flex-shrink-0" />}
    </button>
  )
}

interface SelectLabelProps {
  className?: string
  children: React.ReactNode
}

export function SelectLabel({ className, children }: SelectLabelProps) {
  return (
    <div className={cn(
      "px-3 py-2 text-sm font-semibold text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-gray-700",
      className
    )}>
      {children}
    </div>
  )
}

interface SelectSeparatorProps {
  className?: string
}

export function SelectSeparator({ className }: SelectSeparatorProps) {
  return (
    <div className={cn(
      "h-px bg-gray-200 dark:bg-gray-700 mx-1 my-1",
      className
    )} />
  )
}