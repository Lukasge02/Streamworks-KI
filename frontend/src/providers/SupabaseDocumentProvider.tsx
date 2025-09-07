'use client'

import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { supabase, documentService, realtimeHelper } from '@/lib/supabase'
import type { Document, Chunk } from '@/lib/supabase'
import { useDocumentStore } from '@/stores/documentStore'
import { RealtimeChannel } from '@supabase/supabase-js'
import { documentTransformer, createDocumentEvent, withRetry } from '@/utils/documentTransformation'
import { resilience, withFullResilience } from '@/utils/resilience'
import { websocketManager, createManagedChannel } from '@/utils/websocketManager'

interface SupabaseDocumentContextType {
  isConnected: boolean
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
  lastSyncTime: string | null
  documents: Document[]
  loading: boolean
  error: string | null
  // Actions
  fetchDocuments: () => Promise<void>
  getDocument: (id: number) => Promise<Document | null>
  getDocumentChunks: (documentId: number) => Promise<Chunk[]>
  deleteDocument: (id: number) => Promise<boolean>
  subscribeToChanges: () => void
  unsubscribeFromChanges: () => void
}

const SupabaseDocumentContext = createContext<SupabaseDocumentContextType>({
  isConnected: false,
  connectionStatus: 'disconnected',
  lastSyncTime: null,
  documents: [],
  loading: false,
  error: null,
  fetchDocuments: async () => {},
  getDocument: async () => null,
  getDocumentChunks: async () => [],
  deleteDocument: async () => false,
  subscribeToChanges: () => {},
  unsubscribeFromChanges: () => {},
})

export const useSupabaseDocuments = () => useContext(SupabaseDocumentContext)

interface SupabaseDocumentProviderProps {
  children: React.ReactNode
  autoSync?: boolean
  enableRealtime?: boolean
}

export function SupabaseDocumentProvider({
  children,
  autoSync = true,
  enableRealtime = true
}: SupabaseDocumentProviderProps) {
  const documentStore = useDocumentStore()
  
  // State
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const [lastSyncTime, setLastSyncTime] = useState<string | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [realtimeChannel, setRealtimeChannel] = useState<RealtimeChannel | null>(null)

  // Fetch documents from Supabase with retry logic
  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      setConnectionStatus('connecting')
      
      const docs = await withFullResilience(
        () => documentService.getDocuments(),
        'supabase-documents',
        {
          maxRetries: 3,
          baseDelay: 1000,
          retryCondition: (error) => error.status !== 403 // Don't retry auth errors
        },
        {
          failureThreshold: 5,
          resetTimeout: 60000 // 1 minute
        }
      )
      
      setDocuments(docs)
      setLastSyncTime(new Date().toISOString())
      
      // Use unified transformation
      const formattedDocs = documentTransformer.supabaseArrayToUnified(docs)
      documentStore.setDocuments(formattedDocs)
      setConnectionStatus('connected')
      
    } catch (err) {
      console.error('Failed to fetch documents:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch documents')
      setConnectionStatus('error')
    } finally {
      setLoading(false)
    }
  }, [documentStore])

  // Get single document with resilience
  const getDocument = useCallback(async (id: number): Promise<Document | null> => {
    try {
      return await withFullResilience(
        () => documentService.getDocument(id),
        'supabase-single-document',
        { maxRetries: 2, baseDelay: 500 },
        { failureThreshold: 3, resetTimeout: 30000 }
      )
    } catch (err) {
      console.error('Failed to get document:', err)
      return null
    }
  }, [])

  // Get document chunks
  const getDocumentChunks = useCallback(async (documentId: number): Promise<Chunk[]> => {
    try {
      return await documentService.getDocumentChunks(documentId)
    } catch (err) {
      console.error('Failed to get document chunks:', err)
      return []
    }
  }, [])

  // Delete document
  const deleteDocument = useCallback(async (id: number): Promise<boolean> => {
    try {
      const success = await documentService.deleteDocument(id)
      if (success) {
        // Remove from local state
        setDocuments(prev => prev.filter(doc => doc.id !== id))
        
        // Update document store
        documentStore.deleteDocument(id.toString())
        
        setLastSyncTime(new Date().toISOString())
      }
      return success
    } catch (err) {
      console.error('Failed to delete document:', err)
      return false
    }
  }, [documentStore])

  // Subscribe to real-time changes with managed WebSocket
  const subscribeToChanges = useCallback(async () => {
    if (!enableRealtime) return

    try {
      const channel = await createManagedChannel(
        {
          name: 'supabase-documents-realtime',
          table: 'documents',
          maxReconnectAttempts: 5,
          reconnectDelay: 2000,
          heartbeatInterval: 30000,
          cleanup: true
        },
        () => realtimeHelper.subscribeToAllChanges(() => {}),
        (payload) => {
        console.log('Supabase real-time event:', payload)
        
        switch (payload.eventType) {
          case 'INSERT':
            if (payload.table === 'documents' && payload.new) {
              const newDoc = payload.new as Document
              setDocuments(prev => [newDoc, ...prev])
              
              // Use unified transformation and event creation
              const event = createDocumentEvent('document_added', newDoc, 'supabase')
              documentStore.handleWebSocketEvent(event)
            }
            break

          case 'UPDATE':
            if (payload.table === 'documents' && payload.new) {
              const updatedDoc = payload.new as Document
              setDocuments(prev => 
                prev.map(doc => doc.id === updatedDoc.id ? updatedDoc : doc)
              )
              
              // Use unified transformation and event creation
              const event = createDocumentEvent('document_updated', updatedDoc, 'supabase')
              documentStore.handleWebSocketEvent(event)
            }
            break

          case 'DELETE':
            if (payload.table === 'documents' && payload.old) {
              const deletedId = (payload.old as Document).id
              setDocuments(prev => prev.filter(doc => doc.id !== deletedId))
              
              // Use unified event creation for deletions
              const event = createDocumentEvent('document_deleted', { id: deletedId }, 'supabase')
              documentStore.handleWebSocketEvent(event)
            }
            break
        }
        
        setLastSyncTime(new Date().toISOString())
      })
      
      setRealtimeChannel(channel)
      setConnectionStatus('connected')
      
    } catch (err) {
      console.error('Failed to subscribe to real-time changes:', err)
      setConnectionStatus('error')
    }
  }, [enableRealtime, documentStore])

  // Unsubscribe from real-time changes
  const unsubscribeFromChanges = useCallback(() => {
    if (realtimeChannel) {
      supabase.removeChannel(realtimeChannel)
      setRealtimeChannel(null)
    }
  }, [realtimeChannel])

  // Health check
  const checkConnection = useCallback(async () => {
    try {
      setConnectionStatus('connecting')
      const isHealthy = await import('@/lib/supabase').then(m => m.healthCheck.checkSupabaseConnection())
      setConnectionStatus(isHealthy ? 'connected' : 'error')
      return isHealthy
    } catch (err) {
      setConnectionStatus('error')
      return false
    }
  }, [])

  // Initialize
  useEffect(() => {
    const initialize = async () => {
      const isConnected = await checkConnection()
      
      if (isConnected && autoSync) {
        await fetchDocuments()
      }
      
      if (isConnected && enableRealtime) {
        subscribeToChanges()
      }
    }

    initialize()

    return () => {
      unsubscribeFromChanges()
    }
  }, [autoSync, enableRealtime, checkConnection, fetchDocuments, subscribeToChanges, unsubscribeFromChanges])

  // Expose methods globally for debugging
  useEffect(() => {
    // @ts-ignore
    window.supabaseDocuments = {
      fetchDocuments,
      getDocument,
      getDocumentChunks,
      deleteDocument,
      subscribeToChanges,
      unsubscribeFromChanges,
      connectionStatus,
      documents,
      isConnected: connectionStatus === 'connected'
    }
  }, [
    fetchDocuments,
    getDocument,
    getDocumentChunks,
    deleteDocument,
    subscribeToChanges,
    unsubscribeFromChanges,
    connectionStatus,
    documents
  ])

  const contextValue: SupabaseDocumentContextType = {
    isConnected: connectionStatus === 'connected',
    connectionStatus,
    lastSyncTime,
    documents,
    loading,
    error,
    fetchDocuments,
    getDocument,
    getDocumentChunks,
    deleteDocument,
    subscribeToChanges,
    unsubscribeFromChanges
  }

  return (
    <SupabaseDocumentContext.Provider value={contextValue}>
      {children}
    </SupabaseDocumentContext.Provider>
  )
}