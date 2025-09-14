/**
 * Dialog component - Modal dialog implementation
 */
'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { X } from 'lucide-react'

interface DialogProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children: React.ReactNode
}

interface DialogContextValue {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const DialogContext = React.createContext<DialogContextValue | null>(null)

export function Dialog({ open = false, onOpenChange, children }: DialogProps) {
  return (
    <DialogContext.Provider value={{ open, onOpenChange: onOpenChange || (() => {}) }}>
      {children}
      {open && (
        <div 
          className="fixed inset-0 z-50 bg-black/30"
          onClick={() => onOpenChange?.(false)}
        />
      )}
    </DialogContext.Provider>
  )
}

interface DialogContentProps {
  className?: string
  children: React.ReactNode
}

export function DialogContent({ className, children }: DialogContentProps) {
  const context = React.useContext(DialogContext)
  if (!context?.open) return null

  return (
    <div className="fixed left-[50%] top-[50%] z-[60] translate-x-[-50%] translate-y-[-50%]">
      <div 
        className={cn(
          "bg-white dark:bg-gray-800 rounded-lg shadow-lg max-w-lg w-full mx-4 max-h-[85vh] overflow-auto p-6",
          className
        )}
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  )
}

interface DialogHeaderProps {
  className?: string
  children: React.ReactNode
}

export function DialogHeader({ className, children }: DialogHeaderProps) {
  return (
    <div className={cn("flex flex-col space-y-1.5 text-center sm:text-left p-6 pb-4", className)}>
      {children}
    </div>
  )
}

interface DialogTitleProps {
  className?: string
  children: React.ReactNode
}

export function DialogTitle({ className, children }: DialogTitleProps) {
  return (
    <h3 className={cn("text-lg font-semibold leading-none tracking-tight", className)}>
      {children}
    </h3>
  )
}

interface DialogDescriptionProps {
  className?: string
  children: React.ReactNode
}

export function DialogDescription({ className, children }: DialogDescriptionProps) {
  return (
    <p className={cn("text-sm text-gray-500 dark:text-gray-400", className)}>
      {children}
    </p>
  )
}

interface DialogFooterProps {
  className?: string
  children: React.ReactNode
}

export function DialogFooter({ className, children }: DialogFooterProps) {
  return (
    <div className={cn("flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 p-6 pt-4", className)}>
      {children}
    </div>
  )
}

interface DialogCloseProps {
  className?: string
  children?: React.ReactNode
}

export function DialogClose({ className, children }: DialogCloseProps) {
  const context = React.useContext(DialogContext)
  
  return (
    <button
      className={cn(
        "absolute right-4 top-4 rounded-sm opacity-70 ring-offset-white transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 disabled:pointer-events-none dark:ring-offset-gray-950 dark:focus:ring-gray-800",
        className
      )}
      onClick={() => context?.onOpenChange(false)}
    >
      {children || <X className="h-4 w-4" />}
    </button>
  )
}