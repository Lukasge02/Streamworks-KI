'use client'

import { useState, useCallback } from 'react'
import { ToastProps, ToastType } from '@/components/ui/Toast'

let toastCounter = 0

export function useToast() {
  const [toasts, setToasts] = useState<ToastProps[]>([])

  const addToast = useCallback((
    type: ToastType,
    title: string,
    message?: string,
    duration?: number
  ) => {
    const id = `toast-${++toastCounter}`
    const newToast: ToastProps = {
      id,
      type,
      title,
      message,
      duration,
      onClose: removeToast,
    }

    setToasts(prev => [...prev, newToast])
    return id
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const clearAllToasts = useCallback(() => {
    setToasts([])
  }, [])

  // Convenience methods
  const success = useCallback((title: string, message?: string) => 
    addToast('success', title, message), [addToast])
  
  const error = useCallback((title: string, message?: string) => 
    addToast('error', title, message), [addToast])
  
  const warning = useCallback((title: string, message?: string) => 
    addToast('warning', title, message), [addToast])
  
  const info = useCallback((title: string, message?: string) => 
    addToast('info', title, message), [addToast])

  return {
    toasts,
    addToast,
    removeToast,
    clearAllToasts,
    success,
    error,
    warning,
    info,
  }
}