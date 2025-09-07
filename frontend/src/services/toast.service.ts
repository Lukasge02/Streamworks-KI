/**
 * Enhanced Toast Notification Service
 * Provides rich notifications with actions, persistence, and real-time integration
 */

import { NotificationEvent } from './realtime.service'

export interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info' | 'loading'
  title: string
  message: string
  duration?: number
  persistent?: boolean
  dismissible?: boolean
  actions?: Array<{
    label: string
    action: () => void
    variant?: 'primary' | 'secondary'
  }>
  progress?: {
    current: number
    total: number
    label?: string
  }
  created_at: Date
}

export type ToastOptions = Omit<Toast, 'id' | 'created_at'>

class ToastService {
  private toasts: Toast[] = []
  private listeners: Set<(toasts: Toast[]) => void> = new Set()
  private idCounter = 0

  /**
   * Add a new toast notification
   */
  add(options: ToastOptions): string {
    const id = `toast-${++this.idCounter}`
    const toast: Toast = {
      id,
      ...options,
      created_at: new Date(),
      duration: options.duration ?? (options.type === 'error' ? 8000 : 5000),
      dismissible: options.dismissible ?? true,
    }

    this.toasts.push(toast)
    this.notifyListeners()

    // Auto-remove non-persistent toasts
    if (!toast.persistent && toast.duration && toast.duration > 0) {
      setTimeout(() => {
        this.remove(id)
      }, toast.duration)
    }

    return id
  }

  /**
   * Remove a toast by ID
   */
  remove(id: string): void {
    const index = this.toasts.findIndex(t => t.id === id)
    if (index !== -1) {
      this.toasts.splice(index, 1)
      this.notifyListeners()
    }
  }

  /**
   * Update an existing toast
   */
  update(id: string, updates: Partial<ToastOptions>): void {
    const index = this.toasts.findIndex(t => t.id === id)
    if (index !== -1) {
      this.toasts[index] = { ...this.toasts[index], ...updates }
      this.notifyListeners()
    }
  }

  /**
   * Clear all toasts
   */
  clear(): void {
    this.toasts = []
    this.notifyListeners()
  }

  /**
   * Clear toasts by type
   */
  clearByType(type: Toast['type']): void {
    this.toasts = this.toasts.filter(t => t.type !== type)
    this.notifyListeners()
  }

  /**
   * Get all current toasts
   */
  getToasts(): Toast[] {
    return [...this.toasts]
  }

  /**
   * Subscribe to toast updates
   */
  subscribe(callback: (toasts: Toast[]) => void): () => void {
    this.listeners.add(callback)
    callback([...this.toasts]) // Immediately call with current state

    return () => {
      this.listeners.delete(callback)
    }
  }

  /**
   * Notify all listeners
   */
  private notifyListeners(): void {
    const toasts = [...this.toasts]
    this.listeners.forEach(callback => {
      try {
        callback(toasts)
      } catch (error) {
        console.error('Error in toast listener:', error)
      }
    })
  }

  // Convenience methods
  success(title: string, message?: string, options?: Partial<ToastOptions>): string {
    return this.add({
      type: 'success',
      title,
      message: message || '',
      ...options,
    })
  }

  error(title: string, message?: string, options?: Partial<ToastOptions>): string {
    return this.add({
      type: 'error',
      title,
      message: message || '',
      ...options,
    })
  }

  warning(title: string, message?: string, options?: Partial<ToastOptions>): string {
    return this.add({
      type: 'warning',
      title,
      message: message || '',
      ...options,
    })
  }

  info(title: string, message?: string, options?: Partial<ToastOptions>): string {
    return this.add({
      type: 'info',
      title,
      message: message || '',
      ...options,
    })
  }

  loading(title: string, message?: string, options?: Partial<ToastOptions>): string {
    return this.add({
      type: 'loading',
      title,
      message: message || '',
      persistent: true,
      dismissible: false,
      ...options,
    })
  }

  /**
   * Create progress toast that can be updated
   */
  progress(title: string, initial: { current: number, total: number, label?: string }): {
    id: string
    update: (progress: { current: number, total: number, label?: string }) => void
    complete: (successMessage?: string) => void
    error: (errorMessage: string) => void
  } {
    const id = this.add({
      type: 'loading',
      title,
      message: initial.label || `${initial.current}/${initial.total}`,
      persistent: true,
      dismissible: false,
      progress: initial,
    })

    return {
      id,
      update: (progress) => {
        this.update(id, {
          message: progress.label || `${progress.current}/${progress.total}`,
          progress,
        })
      },
      complete: (successMessage) => {
        this.update(id, {
          type: 'success',
          title: 'Abgeschlossen',
          message: successMessage || 'Vorgang erfolgreich abgeschlossen',
          persistent: false,
          dismissible: true,
          duration: 3000,
        })
      },
      error: (errorMessage) => {
        this.update(id, {
          type: 'error',
          title: 'Fehler',
          message: errorMessage,
          persistent: false,
          dismissible: true,
          duration: 8000,
        })
      },
    }
  }

  /**
   * Handle real-time notification events
   */
  handleRealTimeNotification(notification: NotificationEvent): void {
    const actions = notification.actions?.map(action => ({
      label: action.label,
      action: () => {
        // Handle action - could emit events or call APIs
        console.log('Toast action:', action.action)
      }
    }))

    this.add({
      type: notification.type,
      title: notification.title,
      message: notification.message,
      duration: notification.duration,
      actions,
    })
  }
}

// Export singleton
export const toastService = new ToastService()

/**
 * React Hook for using toasts
 */
import { useState, useEffect } from 'react'

export function useToasts() {
  const [toasts, setToasts] = useState<Toast[]>([])

  useEffect(() => {
    return toastService.subscribe(setToasts)
  }, [])

  return {
    toasts,
    add: toastService.add.bind(toastService),
    remove: toastService.remove.bind(toastService),
    update: toastService.update.bind(toastService),
    clear: toastService.clear.bind(toastService),
    success: toastService.success.bind(toastService),
    error: toastService.error.bind(toastService),
    warning: toastService.warning.bind(toastService),
    info: toastService.info.bind(toastService),
    loading: toastService.loading.bind(toastService),
    progress: toastService.progress.bind(toastService),
  }
}

// Note: Global window.toast is handled by the old toast system for backward compatibility