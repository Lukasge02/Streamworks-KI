'use client'

import { useState, useEffect, useCallback } from 'react'
import { chatApiService, ChatSession, ChatMessage, ChatResponse } from '../services/chatApiService'

// Enhanced Chat Hook that integrates with the new backend API
// Provides compatibility with existing ChatStorage interface while using Supabase backend

export interface EnhancedChatMessage extends ChatMessage {
  timestamp: Date
  type: 'user' | 'assistant'  // Map role to type for UI compatibility
}

export interface EnhancedChatSession {
  id: string
  title: string
  messages: EnhancedChatMessage[]
  created_at: Date
  updated_at: Date
  message_count: number
  last_message_at?: Date
}

export function useEnhancedChat() {
  const [sessions, setSessions] = useState<EnhancedChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Load user sessions from backend
  const loadSessions = useCallback(async () => {
    try {
      setIsLoading(true)
      const backendSessions = await chatApiService.getUserSessions()
      
      // Transform to enhanced format with empty messages (loaded on demand)
      const enhancedSessions: EnhancedChatSession[] = backendSessions.map(session => ({
        id: session.id,
        title: session.title,
        messages: [], // Messages loaded separately
        created_at: new Date(session.created_at),
        updated_at: new Date(session.updated_at),
        message_count: session.message_count,
        last_message_at: session.last_message_at ? new Date(session.last_message_at) : undefined
      }))
      
      setSessions(enhancedSessions)
      setError(null)
    } catch (err) {
      console.error('Failed to load sessions:', err)
      setError('Failed to load chat sessions')
    } finally {
      setIsLoading(false)
    }
  }, [])
  
  // Load messages for a specific session
  const loadSessionMessages = useCallback(async (sessionId: string) => {
    try {
      const backendMessages = await chatApiService.getSessionMessages(sessionId)
      
      // Transform messages to enhanced format
      const enhancedMessages: EnhancedChatMessage[] = backendMessages.map(msg => ({
        id: msg.id,
        type: msg.role as 'user' | 'assistant',
        content: msg.content,
        timestamp: new Date(msg.created_at),
        confidence_score: msg.confidence_score,
        processing_time: msg.processing_time_ms ? `${msg.processing_time_ms}ms` : undefined,
        sources: msg.sources,
        created_at: msg.created_at,
        role: msg.role,
        sequence_number: msg.sequence_number
      }))
      
      // Update session with loaded messages
      setSessions(prev => prev.map(session => 
        session.id === sessionId 
          ? { ...session, messages: enhancedMessages }
          : session
      ))
      
    } catch (err) {
      console.error('Failed to load messages:', err)
      setError('Failed to load messages')
    }
  }, [])
  
  // Create new session
  const createNewSession = useCallback(async (title?: string): Promise<string> => {
    try {
      setIsLoading(true)
      const sessionId = await chatApiService.createSession(title)
      
      const now = new Date()
      const newSession: EnhancedChatSession = {
        id: sessionId,
        title: title || `Chat ${new Date().toLocaleDateString()}`,
        messages: [],
        created_at: now,
        updated_at: now,
        message_count: 0
      }
      
      setSessions(prev => [newSession, ...prev])
      setCurrentSessionId(sessionId)
      setError(null)
      
      return sessionId
    } catch (err) {
      console.error('Failed to create session:', err)
      setError('Failed to create session')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])
  
  // Send message using new API
  const sendMessage = useCallback(async (
    query: string, 
    sessionId?: string
  ): Promise<ChatResponse> => {
    const targetSessionId = sessionId || currentSessionId
    if (!targetSessionId) {
      throw new Error('No session selected')
    }
    
    try {
      setIsLoading(true)
      
      // Add user message optimistically to UI
      const userMessage: EnhancedChatMessage = {
        id: `temp_${Date.now()}`,
        type: 'user',
        content: query,
        timestamp: new Date(),
        created_at: new Date().toISOString(),
        role: 'user',
        sequence_number: 0 // Will be corrected by backend
      }
      
      setSessions(prev => prev.map(session => 
        session.id === targetSessionId
          ? { 
              ...session, 
              messages: [...session.messages, userMessage],
              updated_at: new Date()
            }
          : session
      ))
      
      // Send to backend
      const response = await chatApiService.sendMessage(targetSessionId, query)
      
      // Replace temp message and add assistant response
      const assistantMessage: EnhancedChatMessage = {
        id: response.message_id,
        type: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        confidence_score: response.confidence_score,
        processing_time: response.processing_time_ms ? `${response.processing_time_ms}ms` : undefined,
        sources: response.sources,
        created_at: new Date().toISOString(),
        role: 'assistant',
        sequence_number: 0
      }
      
      setSessions(prev => prev.map(session => 
        session.id === targetSessionId
          ? {
              ...session,
              messages: [
                ...session.messages.filter(m => m.id !== userMessage.id),
                { ...userMessage, id: `user_${response.message_id}` },
                assistantMessage
              ],
              message_count: session.message_count + 2,
              updated_at: new Date()
            }
          : session
      ))
      
      setError(null)
      return response
      
    } catch (err) {
      console.error('Failed to send message:', err)
      setError('Failed to send message')
      
      // Remove optimistic message on error
      setSessions(prev => prev.map(session => 
        session.id === targetSessionId
          ? {
              ...session,
              messages: session.messages.filter(m => !m.id.startsWith('temp_'))
            }
          : session
      ))
      
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [currentSessionId])
  
  // Update session title
  const updateSessionTitle = useCallback(async (sessionId: string, title: string) => {
    try {
      await chatApiService.updateSessionTitle(sessionId, title)
      
      setSessions(prev => prev.map(session => 
        session.id === sessionId 
          ? { ...session, title, updated_at: new Date() }
          : session
      ))
      
      setError(null)
    } catch (err) {
      console.error('Failed to update session title:', err)
      setError('Failed to update session title')
    }
  }, [])
  
  // Delete session
  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await chatApiService.deleteSession(sessionId)
      
      setSessions(prev => prev.filter(session => session.id !== sessionId))
      
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null)
      }
      
      setError(null)
    } catch (err) {
      console.error('Failed to delete session:', err)
      setError('Failed to delete session')
    }
  }, [currentSessionId])
  
  // Compatibility methods for existing UI
  const addMessage = useCallback((message: Omit<EnhancedChatMessage, 'id' | 'timestamp'>) => {
    // This is handled by sendMessage now, but keep for compatibility
    console.warn('addMessage called - use sendMessage instead')
  }, [])
  
  const cleanupEmptySessions = useCallback(() => {
    setSessions(prev => prev.filter(session => session.message_count > 0))
  }, [])
  
  const clearAllSessions = useCallback(() => {
    setSessions([])
    setCurrentSessionId(null)
  }, [])
  
  // Auto-load sessions on mount
  useEffect(() => {
    loadSessions()
  }, [loadSessions])
  
  // Auto-load messages when switching sessions
  useEffect(() => {
    if (currentSessionId) {
      const session = sessions.find(s => s.id === currentSessionId)
      if (session && session.messages.length === 0 && session.message_count > 0) {
        loadSessionMessages(currentSessionId)
      }
    }
  }, [currentSessionId, sessions, loadSessionMessages])
  
  // Get current session
  const currentSession = sessions.find(s => s.id === currentSessionId) || null
  
  return {
    // State
    sessions,
    currentSession,
    currentSessionId,
    isLoading,
    error,
    
    // Session management
    createNewSession,
    setCurrentSessionId,
    updateSessionTitle,
    deleteSession,
    loadSessions,
    loadSessionMessages,
    
    // Message handling
    sendMessage,
    addMessage, // Deprecated but kept for compatibility
    
    // Utilities
    cleanupEmptySessions,
    clearAllSessions
  }
}