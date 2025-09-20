'use client'

import { createContext, useContext, useEffect, useRef, useState } from 'react'
import { useDocumentStore } from '@/stores/documentStore'
import { DocumentEvent, UploadJobProgress, OptimisticOperation } from '@/types/document.types'

interface DocumentSyncContextType {
  isConnected: boolean
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
  lastSyncTime: string | null
  reconnectAttempts: number
  maxReconnectAttempts: number
}

const DocumentSyncContext = createContext<DocumentSyncContextType>({
  isConnected: false,
  connectionStatus: 'disconnected',
  lastSyncTime: null,
  reconnectAttempts: 0,
  maxReconnectAttempts: 5
})

export const useDocumentSync = () => useContext(DocumentSyncContext)

interface DocumentSyncProviderProps {
  children: React.ReactNode
  wsUrl?: string
  autoReconnect?: boolean
  maxReconnectAttempts?: number
  reconnectInterval?: number
}

export function DocumentSyncProvider({
  children,
  wsUrl = 'ws://localhost:8000/ws/documents',
  autoReconnect = true,
  maxReconnectAttempts = 5,
  reconnectInterval = 3000
}: DocumentSyncProviderProps) {
  const documentStore = useDocumentStore()
  
  // Connection state
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const [lastSyncTime, setLastSyncTime] = useState<string | null>(null)
  
  // WebSocket refs
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const isManualClose = useRef(false)
  
  // Connection management
  const connect = async () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }
    
    try {
      setConnectionStatus('connecting')
      
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws
      
      ws.onopen = () => {
        console.log('Document sync WebSocket connected')
        setConnectionStatus('connected')
        setReconnectAttempts(0)
        documentStore.setConnectionStatus(true)
        
        // Start heartbeat
        startHeartbeat()
        
        // Request initial document list
        ws.send(JSON.stringify({
          type: 'request_documents',
          timestamp: new Date().toISOString()
        }))
        
        setLastSyncTime(new Date().toISOString())
      }
      
      ws.onmessage = (event) => {
        try {
          // Handle empty or invalid messages
          if (!event.data || typeof event.data !== 'string') {
            console.warn('Received empty or invalid WebSocket message')
            return
          }

          const message = JSON.parse(event.data)

          // Validate message structure
          if (!message || typeof message !== 'object') {
            console.warn('Received invalid WebSocket message structure')
            return
          }

          handleWebSocketMessage(message)
          setLastSyncTime(new Date().toISOString())
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
          // Don't break the connection on parse errors, just log and continue
          // This prevents browser extension conflicts from breaking the connection
        }
      }
      
      ws.onclose = (event) => {
        console.log('Document sync WebSocket disconnected:', event.code, event.reason)
        setConnectionStatus('disconnected')
        documentStore.setConnectionStatus(false)
        stopHeartbeat()
        
        // Auto-reconnect if not manual close
        if (!isManualClose.current && autoReconnect && reconnectAttempts < maxReconnectAttempts) {
          scheduleReconnect()
        } else if (reconnectAttempts >= maxReconnectAttempts) {
          setConnectionStatus('error')
        }
      }
      
      ws.onerror = (error) => {
        console.error('Document sync WebSocket error:', error)
        setConnectionStatus('error')
        documentStore.setConnectionStatus(false)
      }
      
    } catch (error) {
      console.error('Failed to connect to document sync WebSocket:', error)
      setConnectionStatus('error')
      
      if (autoReconnect && reconnectAttempts < maxReconnectAttempts) {
        scheduleReconnect()
      }
    }
  }
  
  const disconnect = () => {
    isManualClose.current = true
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    stopHeartbeat()
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect')
      wsRef.current = null
    }
    
    setConnectionStatus('disconnected')
    documentStore.setConnectionStatus(false)
  }
  
  const scheduleReconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    setReconnectAttempts(prev => prev + 1)
    
    reconnectTimeoutRef.current = setTimeout(() => {
      console.log(`Attempting to reconnect (${reconnectAttempts + 1}/${maxReconnectAttempts})...`)
      connect()
    }, reconnectInterval * Math.pow(2, reconnectAttempts)) // Exponential backoff
  }
  
  const startHeartbeat = () => {
    heartbeatIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'ping',
          timestamp: new Date().toISOString()
        }))
      }
    }, 30000) // Every 30 seconds
  }
  
  const stopHeartbeat = () => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
      heartbeatIntervalRef.current = null
    }
  }
  
  const handleWebSocketMessage = (message: any) => {
    // Validate message type exists
    if (!message.type) {
      console.warn('Received WebSocket message without type:', message)
      return
    }

    try {
      switch (message.type) {
        case 'documents_list':
          // Initial document list
          if (Array.isArray(message.data)) {
            documentStore.setDocuments(message.data)
          } else {
            console.warn('Received invalid documents_list data:', message.data)
          }
          break

        case 'document_added':
          if (message.data && typeof message.data === 'object') {
            documentStore.handleWebSocketEvent({
              type: 'document_added',
              data: message.data,
              timestamp: message.timestamp || new Date().toISOString(),
              source: 'websocket'
            } as DocumentEvent)
          } else {
            console.warn('Received invalid document_added data:', message.data)
          }
          break

        case 'document_updated':
          if (message.data && typeof message.data === 'object') {
            documentStore.handleWebSocketEvent({
              type: 'document_updated',
              data: message.data,
              timestamp: message.timestamp || new Date().toISOString(),
              source: 'websocket'
            } as DocumentEvent)
          } else {
            console.warn('Received invalid document_updated data:', message.data)
          }
          break

        case 'document_deleted':
          if (message.data && typeof message.data === 'object') {
            documentStore.handleWebSocketEvent({
              type: 'document_deleted',
              data: message.data,
              timestamp: message.timestamp || new Date().toISOString(),
              source: 'websocket'
            } as DocumentEvent)
          } else {
            console.warn('Received invalid document_deleted data:', message.data)
          }
          break
  
        case 'upload_progress':
          // LEGACY: Upload progress now handled by SimpleUploadDropzone + useUploadProgress
          // This case is kept for backward compatibility but is not actively used
          console.log('Upload progress via DocumentSync (legacy):', message.data)
          break

        case 'operation_confirmed':
          // Remove optimistic operation when confirmed
          if (message.operation_id && typeof message.operation_id === 'string') {
            documentStore.removeOptimisticOperation(message.operation_id)
          }
          break

        case 'operation_failed':
          // Rollback failed operation
          if (message.operation_id && typeof message.operation_id === 'string') {
            documentStore.rollbackOperation(message.operation_id)
          }
          break

        case 'connection_established':
          // Connection established confirmation
          if (message.message) {
            console.log('Document sync connection confirmed:', message.message)
          }
          break

        case 'pong':
          // Heartbeat response
          break

        case 'error':
          if (message.error) {
            console.error('WebSocket error message:', message.error)
          }
          break

        default:
          console.warn('Unknown WebSocket message type:', message.type)
      }
    } catch (error) {
      console.error('Error handling WebSocket message:', error, 'Message:', message)
    }
  }
  
  // Send optimistic operation to backend
  const sendOptimisticOperation = (operation: OptimisticOperation) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'optimistic_operation',
        operation_id: operation.id,
        operation_type: operation.type,
        entity: operation.entity,
        data: operation.data,
        timestamp: operation.timestamp
      }))
    } else {
      console.warn('WebSocket not connected, cannot send optimistic operation')
      // Rollback immediately if not connected
      operation.rollback()
      documentStore.removeOptimisticOperation(operation.id)
    }
  }
  
  // Initialize connection on mount
  useEffect(() => {
    isManualClose.current = false
    connect()

    return () => {
      isManualClose.current = true
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      stopHeartbeat()
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close(1000, 'Component unmounting')
      }
      wsRef.current = null
      setConnectionStatus('disconnected')
    }
  }, [])
  
  // Expose connection methods globally
  useEffect(() => {
    // @ts-ignore - Add to window for debugging
    window.documentSync = {
      connect,
      disconnect,
      sendOptimisticOperation,
      connectionStatus,
      reconnectAttempts,
      isConnected: connectionStatus === 'connected'
    }
  }, [connectionStatus, reconnectAttempts])
  
  const contextValue: DocumentSyncContextType = {
    isConnected: connectionStatus === 'connected',
    connectionStatus,
    lastSyncTime,
    reconnectAttempts,
    maxReconnectAttempts
  }
  
  return (
    <DocumentSyncContext.Provider value={contextValue}>
      {children}
    </DocumentSyncContext.Provider>
  )
}