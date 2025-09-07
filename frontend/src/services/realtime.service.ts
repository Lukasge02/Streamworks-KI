/**
 * Real-time Service for WebSocket connections and Server-Sent Events
 * Provides real-time updates for document processing, system metrics, and notifications
 */

import { UploadJobStatus } from '@/types/document.types'

export type RealTimeEventType = 
  | 'upload_progress'
  | 'document_processed' 
  | 'system_metrics'
  | 'notification'
  | 'batch_update'

export interface RealTimeEvent<T = any> {
  type: RealTimeEventType
  data: T
  timestamp: string
  id?: string
}

export interface SystemMetrics {
  upload_queue_size: number
  processing_queue_size: number
  active_uploads: number
  system_load: number
  memory_usage: number
  storage_usage: number
  average_processing_time: number
}

export interface NotificationEvent {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  duration?: number
  actions?: Array<{
    label: string
    action: string
  }>
}

class RealTimeService {
  private eventSource: EventSource | null = null
  private reconnectTimer: NodeJS.Timeout | null = null
  private listeners: Map<RealTimeEventType, Set<(data: any) => void>> = new Map()
  private isConnecting = false
  private maxReconnectAttempts = 5
  private reconnectAttempts = 0
  private baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

  constructor() {
    // Initialize listeners map
    const eventTypes: RealTimeEventType[] = [
      'upload_progress',
      'document_processed',
      'system_metrics',
      'notification',
      'batch_update'
    ]
    eventTypes.forEach(type => {
      this.listeners.set(type, new Set())
    })
  }

  /**
   * Connect to the real-time stream
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnecting || this.eventSource?.readyState === EventSource.OPEN) {
        resolve()
        return
      }

      this.isConnecting = true

      try {
        const url = `${this.baseUrl}/api/realtime/stream`
        this.eventSource = new EventSource(url)

        this.eventSource.onopen = () => {
          console.log('✅ Real-time connection established')
          this.isConnecting = false
          this.reconnectAttempts = 0
          resolve()
        }

        this.eventSource.onmessage = (event) => {
          try {
            const eventData: RealTimeEvent = JSON.parse(event.data)
            this.handleEvent(eventData)
          } catch (error) {
            console.error('Error parsing real-time event:', error)
          }
        }

        this.eventSource.onerror = (error) => {
          console.error('Real-time connection error:', error)
          this.isConnecting = false
          
          if (this.eventSource?.readyState === EventSource.CLOSED) {
            this.scheduleReconnect()
            reject(new Error('Connection failed'))
          }
        }

        // Handle specific event types
        this.setupEventHandlers()

      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  /**
   * Setup handlers for specific event types
   */
  private setupEventHandlers(): void {
    if (!this.eventSource) return

    // Upload progress events
    this.eventSource.addEventListener('upload_progress', (event) => {
      try {
        const data: UploadJobStatus = JSON.parse(event.data)
        this.emitEvent('upload_progress', data)
      } catch (error) {
        console.error('Error parsing upload progress:', error)
      }
    })

    // Document processed events
    this.eventSource.addEventListener('document_processed', (event) => {
      try {
        const data = JSON.parse(event.data)
        this.emitEvent('document_processed', data)
      } catch (error) {
        console.error('Error parsing document processed:', error)
      }
    })

    // System metrics events
    this.eventSource.addEventListener('system_metrics', (event) => {
      try {
        const data: SystemMetrics = JSON.parse(event.data)
        this.emitEvent('system_metrics', data)
      } catch (error) {
        console.error('Error parsing system metrics:', error)
      }
    })

    // Notification events
    this.eventSource.addEventListener('notification', (event) => {
      try {
        const data: NotificationEvent = JSON.parse(event.data)
        this.emitEvent('notification', data)
      } catch (error) {
        console.error('Error parsing notification:', error)
      }
    })

    // Batch update events
    this.eventSource.addEventListener('batch_update', (event) => {
      try {
        const data = JSON.parse(event.data)
        this.emitEvent('batch_update', data)
      } catch (error) {
        console.error('Error parsing batch update:', error)
      }
    })
  }

  /**
   * Disconnect from the real-time stream
   */
  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }

    this.reconnectAttempts = 0
    console.log('🔌 Real-time connection closed')
  }

  /**
   * Subscribe to specific event types
   */
  subscribe<T = any>(
    eventType: RealTimeEventType,
    callback: (data: T) => void
  ): () => void {
    const listeners = this.listeners.get(eventType)
    if (listeners) {
      listeners.add(callback)
    }

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(eventType)
      if (listeners) {
        listeners.delete(callback)
      }
    }
  }

  /**
   * Emit event to all subscribers
   */
  private emitEvent(eventType: RealTimeEventType, data: any): void {
    const listeners = this.listeners.get(eventType)
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in ${eventType} callback:`, error)
        }
      })
    }
  }

  /**
   * Handle incoming events
   */
  private handleEvent(event: RealTimeEvent): void {
    this.emitEvent(event.type, event.data)
  }

  /**
   * Schedule reconnection with exponential backoff
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Max reconnect attempts reached')
      return
    }

    const delay = Math.pow(2, this.reconnectAttempts) * 1000 // Exponential backoff
    this.reconnectAttempts++

    console.log(`🔄 Reconnecting in ${delay/1000}s (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    this.reconnectTimer = setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnection failed:', error)
      })
    }, delay)
  }

  /**
   * Get connection status
   */
  getStatus(): {
    connected: boolean
    connecting: boolean
    reconnectAttempts: number
  } {
    return {
      connected: this.eventSource?.readyState === EventSource.OPEN,
      connecting: this.isConnecting,
      reconnectAttempts: this.reconnectAttempts
    }
  }

  /**
   * Send heartbeat ping (if supported by backend)
   */
  ping(): void {
    if (this.eventSource?.readyState === EventSource.OPEN) {
      // Could send a heartbeat message if backend supports it
      fetch(`${this.baseUrl}/api/realtime/ping`, { method: 'POST' })
        .catch(error => console.warn('Heartbeat failed:', error))
    }
  }
}

// Export singleton instance
export const realTimeService = new RealTimeService()

/**
 * React Hook for using real-time events
 */
import { useEffect, useState, useCallback } from 'react'

export function useRealTime() {
  const [connected, setConnected] = useState(false)
  const [connecting, setConnecting] = useState(false)
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)

  useEffect(() => {
    // Connect on mount
    setConnecting(true)
    realTimeService.connect()
      .then(() => {
        setConnected(true)
        setConnecting(false)
      })
      .catch(() => {
        setConnecting(false)
      })

    // Subscribe to connection status updates
    const checkConnection = setInterval(() => {
      const status = realTimeService.getStatus()
      setConnected(status.connected)
      setConnecting(status.connecting)
    }, 1000)

    // Subscribe to system metrics
    const unsubscribeMetrics = realTimeService.subscribe<SystemMetrics>(
      'system_metrics',
      setMetrics
    )

    // Cleanup on unmount
    return () => {
      clearInterval(checkConnection)
      unsubscribeMetrics()
      realTimeService.disconnect()
    }
  }, [])

  const subscribe = useCallback(<T = any>(
    eventType: RealTimeEventType,
    callback: (data: T) => void
  ) => {
    return realTimeService.subscribe(eventType, callback)
  }, [])

  return {
    connected,
    connecting,
    metrics,
    subscribe,
    reconnect: () => realTimeService.connect(),
    disconnect: () => realTimeService.disconnect(),
  }
}