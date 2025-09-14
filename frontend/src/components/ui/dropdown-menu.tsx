/**
 * Dropdown Menu component - Dropdown menu implementation
 */
'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { ChevronDown } from 'lucide-react'

interface DropdownMenuContextValue {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const DropdownMenuContext = React.createContext<DropdownMenuContextValue | null>(null)

interface DropdownMenuProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children: React.ReactNode
}

export function DropdownMenu({ open = false, onOpenChange, children }: DropdownMenuProps) {
  return (
    <DropdownMenuContext.Provider value={{ open, onOpenChange: onOpenChange || (() => {}) }}>
      <div className="relative inline-block text-left">
        {children}
      </div>
    </DropdownMenuContext.Provider>
  )
}

interface DropdownMenuTriggerProps {
  asChild?: boolean
  className?: string
  children: React.ReactNode
}

export function DropdownMenuTrigger({ asChild, className, children }: DropdownMenuTriggerProps) {
  const context = React.useContext(DropdownMenuContext)
  
  const handleClick = () => {
    context?.onOpenChange(!context.open)
  }

  if (asChild) {
    return React.cloneElement(children as React.ReactElement, {
      onClick: handleClick,
      'aria-expanded': context?.open,
    })
  }

  return (
    <button
      className={cn(
        "flex items-center justify-between w-full px-3 py-2 text-sm font-medium text-left bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white dark:hover:bg-gray-700",
        className
      )}
      onClick={handleClick}
      aria-expanded={context?.open}
    >
      {children}
      <ChevronDown className={cn(
        "ml-2 h-4 w-4 transition-transform",
        context?.open && "transform rotate-180"
      )} />
    </button>
  )
}

interface DropdownMenuContentProps {
  className?: string
  align?: 'start' | 'end'
  children: React.ReactNode
}

export function DropdownMenuContent({ className, align = 'start', children }: DropdownMenuContentProps) {
  const context = React.useContext(DropdownMenuContext)
  if (!context?.open) return null

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 z-40"
        onClick={() => context.onOpenChange(false)}
      />
      
      {/* Menu */}
      <div
        className={cn(
          "absolute z-50 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg min-w-[8rem]",
          align === 'end' ? "right-0" : "left-0",
          className
        )}
      >
        {children}
      </div>
    </>
  )
}

interface DropdownMenuItemProps {
  className?: string
  disabled?: boolean
  onClick?: () => void
  children: React.ReactNode
}

export function DropdownMenuItem({ className, disabled, onClick, children }: DropdownMenuItemProps) {
  const context = React.useContext(DropdownMenuContext)
  
  const handleClick = () => {
    if (!disabled && onClick) {
      onClick()
      context?.onOpenChange(false)
    }
  }

  return (
    <button
      className={cn(
        "flex items-center w-full px-3 py-2 text-sm text-left hover:bg-gray-100 dark:hover:bg-gray-700 focus:bg-gray-100 dark:focus:bg-gray-700 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed",
        "first:rounded-t-md last:rounded-b-md",
        className
      )}
      disabled={disabled}
      onClick={handleClick}
    >
      {children}
    </button>
  )
}

interface DropdownMenuLabelProps {
  className?: string
  children: React.ReactNode
}

export function DropdownMenuLabel({ className, children }: DropdownMenuLabelProps) {
  return (
    <div className={cn(
      "px-3 py-2 text-sm font-semibold text-gray-900 dark:text-gray-100",
      className
    )}>
      {children}
    </div>
  )
}

interface DropdownMenuSeparatorProps {
  className?: string
}

export function DropdownMenuSeparator({ className }: DropdownMenuSeparatorProps) {
  return (
    <div className={cn(
      "h-px bg-gray-200 dark:bg-gray-700 mx-1 my-1",
      className
    )} />
  )
}