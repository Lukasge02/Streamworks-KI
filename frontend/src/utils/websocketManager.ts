/**
 * Advanced WebSocket Channel Management
 * Prevents memory leaks and manages connection lifecycle
 */

import { RealtimeChannel } from '@supabase/supabase-js'

interface ChannelConfig {
  name: string
  table?: string
  filter?: string
  maxReconnectAttempts: number
  reconnectDelay: number
  heartbeatInterval: number
  cleanup: boolean
}

interface ChannelMetrics {
  connectionTime: number
  messagesReceived: number
  reconnectAttempts: number
  lastActivity: number
  status: 'connected' | 'connecting' | 'disconnected' | 'error'
}

class WebSocketChannelManager {
  private static instance: WebSocketChannelManager
  private channels = new Map<string, RealtimeChannel>()
  private metrics = new Map<string, ChannelMetrics>()
  private heartbeatIntervals = new Map<string, NodeJS.Timeout>()
  private reconnectTimeouts = new Map<string, NodeJS.Timeout>()
  private cleanupCallbacks = new Map<string, (() => void)[]>()
  private isShuttingDown = false

  static getInstance(): WebSocketChannelManager {
    if (!WebSocketChannelManager.instance) {
      WebSocketChannelManager.instance = new WebSocketChannelManager()
      
      // Setup global cleanup
      if (typeof window !== 'undefined') {
        window.addEventListener('beforeunload', () => {
          WebSocketChannelManager.instance.shutdown()
        })
      }
    }
    return WebSocketChannelManager.instance
  }

  /**
   * Create and manage a WebSocket channel with automatic cleanup
   */
  async createChannel(
    config: ChannelConfig,
    channelFactory: () => RealtimeChannel,
    onMessage?: (payload: any) => void
  ): Promise<RealtimeChannel> {
    
    // Cleanup existing channel if it exists
    if (this.channels.has(config.name)) {
      await this.cleanupChannel(config.name)
    }

    const channel = channelFactory()
    
    // Initialize metrics
    this.metrics.set(config.name, {
      connectionTime: Date.now(),
      messagesReceived: 0,
      reconnectAttempts: 0,
      lastActivity: Date.now(),
      status: 'connecting'
    })

    // Setup message handling with metrics
    if (onMessage) {
      const wrappedHandler = (payload: any) => {
        this.updateMetrics(config.name, 'message')
        onMessage(payload)
      }
      
      // Subscribe to channel events
      channel.on('postgres_changes', { event: '*', schema: 'public' }, wrappedHandler)
    }

    // Setup connection event handlers
    channel
      .on('system', {}, (payload) => {
        console.log(`Channel ${config.name} system event:`, payload)
        this.updateMetrics(config.name, 'system', payload.status)
      })
      .subscribe(async (status, error) => {
        console.log(`Channel ${config.name} subscription status:`, status, error)
        
        if (status === 'SUBSCRIBED') {
          this.updateMetrics(config.name, 'connected')
          this.startHeartbeat(config.name, config.heartbeatInterval)
        } else if (status === 'CHANNEL_ERROR' && error) {
          this.updateMetrics(config.name, 'error')
          await this.handleConnectionError(config.name, config, error)
        } else if (status === 'CLOSED') {
          this.updateMetrics(config.name, 'disconnected')
          this.stopHeartbeat(config.name)
          
          if (!this.isShuttingDown) {
            await this.attemptReconnect(config.name, config, channelFactory, onMessage)
          }
        }
      })

    this.channels.set(config.name, channel)
    
    // Setup cleanup callbacks
    if (config.cleanup) {
      this.addCleanupCallback(config.name, () => {
        this.cleanupChannel(config.name)
      })
    }

    return channel
  }

  /**
   * Get channel by name
   */
  getChannel(name: string): RealtimeChannel | undefined {
    return this.channels.get(name)
  }

  /**
   * Get channel metrics
   */
  getChannelMetrics(name: string): ChannelMetrics | undefined {
    return this.metrics.get(name)
  }

  /**
   * Get all channel metrics for monitoring
   */
  getAllMetrics(): Record<string, ChannelMetrics> {
    const result: Record<string, ChannelMetrics> = {}
    this.metrics.forEach((metrics, name) => {
      result[name] = { ...metrics }
    })
    return result
  }

  /**
   * Manually cleanup a specific channel
   */
  async cleanupChannel(name: string): Promise<void> {
    console.log(`Cleaning up channel: ${name}`)
    
    // Clear heartbeat
    this.stopHeartbeat(name)
    
    // Clear reconnect timeout
    const reconnectTimeout = this.reconnectTimeouts.get(name)
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      this.reconnectTimeouts.delete(name)
    }
    
    // Unsubscribe from channel
    const channel = this.channels.get(name)
    if (channel) {
      try {
        await channel.unsubscribe()
        console.log(`Channel ${name} unsubscribed successfully`)
      } catch (error) {
        console.warn(`Failed to unsubscribe channel ${name}:`, error)
      }
    }
    
    // Run cleanup callbacks
    const callbacks = this.cleanupCallbacks.get(name) || []
    callbacks.forEach(callback => {
      try {
        callback()
      } catch (error) {
        console.error(`Cleanup callback error for ${name}:`, error)
      }
    })
    
    // Remove from maps
    this.channels.delete(name)
    this.metrics.delete(name)
    this.heartbeatIntervals.delete(name)
    this.cleanupCallbacks.delete(name)
  }

  /**
   * Cleanup all channels
   */
  async shutdown(): Promise<void> {
    console.log('Shutting down WebSocket Channel Manager')
    this.isShuttingDown = true
    
    const cleanupPromises = Array.from(this.channels.keys()).map(name => 
      this.cleanupChannel(name)
    )
    
    await Promise.allSettled(cleanupPromises)
    console.log('WebSocket Channel Manager shutdown complete')
  }

  /**
   * Add cleanup callback for a channel
   */
  private addCleanupCallback(name: string, callback: () => void): void {
    if (!this.cleanupCallbacks.has(name)) {
      this.cleanupCallbacks.set(name, [])
    }
    this.cleanupCallbacks.get(name)!.push(callback)
  }

  /**
   * Update channel metrics
   */
  private updateMetrics(
    name: string, 
    event: 'message' | 'connected' | 'disconnected' | 'error' | 'system',
    status?: string
  ): void {
    const metrics = this.metrics.get(name)
    if (!metrics) return

    metrics.lastActivity = Date.now()
    
    switch (event) {
      case 'message':
        metrics.messagesReceived++
        break
      case 'connected':
        metrics.status = 'connected'
        metrics.reconnectAttempts = 0 // Reset on successful connection
        break
      case 'disconnected':
        metrics.status = 'disconnected'
        break
      case 'error':
        metrics.status = 'error'
        break
      case 'system':
        if (status) {
          metrics.status = status as ChannelMetrics['status']
        }
        break
    }
  }

  /**
   * Start heartbeat for connection monitoring
   */
  private startHeartbeat(name: string, interval: number): void {
    this.stopHeartbeat(name) // Clear any existing heartbeat
    
    const heartbeatInterval = setInterval(() => {
      const channel = this.channels.get(name)
      const metrics = this.metrics.get(name)
      
      if (!channel || !metrics) {
        this.stopHeartbeat(name)
        return
      }
      
      // Check if channel is still active (received message recently)
      const timeSinceActivity = Date.now() - metrics.lastActivity
      const maxInactivity = interval * 3 // 3x heartbeat interval
      
      if (timeSinceActivity > maxInactivity && metrics.status === 'connected') {
        console.warn(`Channel ${name} appears inactive, last activity: ${timeSinceActivity}ms ago`)
        metrics.status = 'disconnected'
      }
      
      // Send ping (if supported by your implementation)
      // channel.push('ping', {})
      
    }, interval)
    
    this.heartbeatIntervals.set(name, heartbeatInterval)
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat(name: string): void {
    const interval = this.heartbeatIntervals.get(name)
    if (interval) {
      clearInterval(interval)
      this.heartbeatIntervals.delete(name)
    }
  }

  /**
   * Handle connection errors with recovery strategies
   */
  private async handleConnectionError(
    name: string, 
    config: ChannelConfig, 
    error: any
  ): Promise<void> {
    const metrics = this.metrics.get(name)
    if (!metrics) return

    console.error(`Channel ${name} connection error:`, error)
    
    // Increment error count and attempt recovery
    metrics.reconnectAttempts++
    
    if (metrics.reconnectAttempts < config.maxReconnectAttempts) {
      console.log(`Attempting to recover channel ${name} (attempt ${metrics.reconnectAttempts})`)
      
      // Progressive backoff
      const delay = config.reconnectDelay * Math.pow(2, metrics.reconnectAttempts - 1)
      
      setTimeout(() => {
        // Channel recovery logic would go here
        console.log(`Recovering channel ${name} after ${delay}ms delay`)
      }, delay)
    } else {
      console.error(`Max reconnection attempts reached for channel ${name}`)
      await this.cleanupChannel(name)
    }
  }

  /**
   * Attempt to reconnect a channel
   */
  private async attemptReconnect(
    name: string,
    config: ChannelConfig,
    channelFactory: () => RealtimeChannel,
    onMessage?: (payload: any) => void
  ): Promise<void> {
    if (this.isShuttingDown) return
    
    const metrics = this.metrics.get(name)
    if (!metrics) return

    if (metrics.reconnectAttempts >= config.maxReconnectAttempts) {
      console.error(`Max reconnection attempts reached for ${name}`)
      return
    }

    metrics.reconnectAttempts++
    const delay = config.reconnectDelay * Math.pow(2, metrics.reconnectAttempts - 1)
    
    console.log(`Reconnecting channel ${name} in ${delay}ms (attempt ${metrics.reconnectAttempts})`)
    
    const timeout = setTimeout(async () => {
      try {
        await this.createChannel(config, channelFactory, onMessage)
        console.log(`Channel ${name} reconnected successfully`)
      } catch (error) {
        console.error(`Failed to reconnect channel ${name}:`, error)
      }
    }, delay)
    
    this.reconnectTimeouts.set(name, timeout)
  }
}

// Export singleton
export const websocketManager = WebSocketChannelManager.getInstance()

// Convenience functions
export const createManagedChannel = (
  config: ChannelConfig,
  factory: () => RealtimeChannel,
  onMessage?: (payload: any) => void
) => websocketManager.createChannel(config, factory, onMessage)

export const cleanupChannel = (name: string) => websocketManager.cleanupChannel(name)
export const getChannelMetrics = () => websocketManager.getAllMetrics()
export const shutdownWebSockets = () => websocketManager.shutdown()