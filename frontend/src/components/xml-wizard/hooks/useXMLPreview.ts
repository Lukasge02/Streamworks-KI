/**
 * useXMLPreview Hook
 * Reactive XML generation with live preview and smart defaults
 */
'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { WizardFormData, XMLGenerationResult } from '../types/wizard.types'

interface XMLPreviewConfig {
  debounceMs?: number
  enableAutoPreview?: boolean
  apiBaseUrl?: string
}

interface XMLPreviewState {
  xmlContent: string
  isGenerating: boolean
  lastGenerated: Date | null
  placeholderCount: number
  completionPercentage: number
  error: string | null
  generationTimeMs: number
}

const DEFAULT_CONFIG: XMLPreviewConfig = {
  debounceMs: 500,
  enableAutoPreview: true,
  apiBaseUrl: '/api/xml-generator'
}

export const useXMLPreview = (config: XMLPreviewConfig = {}) => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config }
  
  const [state, setState] = useState<XMLPreviewState>({
    xmlContent: '',
    isGenerating: false,
    lastGenerated: null,
    placeholderCount: 0,
    completionPercentage: 0,
    error: null,
    generationTimeMs: 0
  })
  
  // Refs for debouncing and cancellation
  const debounceTimer = useRef<NodeJS.Timeout | null>(null)
  const abortController = useRef<AbortController | null>(null)
  const lastFormData = useRef<string>('')
  
  const generatePreview = useCallback(async (formData: Partial<WizardFormData>) => {
    try {
      // Cancel previous request
      if (abortController.current) {
        abortController.current.abort()
      }
      
      // Create new abort controller
      abortController.current = new AbortController()
      
      setState(prev => ({ 
        ...prev, 
        isGenerating: true, 
        error: null 
      }))
      
      const response = await fetch(`${finalConfig.apiBaseUrl}/preview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
        signal: abortController.current.signal
      })
      
      if (!response.ok) {
        throw new Error(`Preview generation failed: ${response.statusText}`)
      }
      
      const result: XMLGenerationResult = await response.json()
      
      // Count placeholders
      const placeholderMatches = result.xmlContent?.match(/\{\{[^}]+\}\}/g) || []
      const placeholderCount = placeholderMatches.length
      
      // Calculate completion percentage (rough estimation)
      const totalFields = 15 // Estimated total fields in a complete stream
      const filledFields = Math.max(0, totalFields - placeholderCount)
      const completionPercentage = Math.min(100, Math.round((filledFields / totalFields) * 100))
      
      setState(prev => ({
        ...prev,
        xmlContent: result.xml_content || result.xmlContent || '',
        isGenerating: false,
        lastGenerated: new Date(),
        placeholderCount,
        completionPercentage,
        generationTimeMs: result.generation_time_ms || 0
      }))
      
    } catch (error: any) {
      if (error.name === 'AbortError') {
        // Request was cancelled, ignore
        return
      }
      
      console.error('XML Preview generation failed:', error)
      
      // Enhanced error handling with better user messages
      let errorMessage = 'Fehler bei der Preview-Generierung'
      if (error.message?.includes('fetch')) {
        errorMessage = 'Backend nicht erreichbar - bitte Backend starten'
      } else if (error.message?.includes('validation')) {
        errorMessage = 'Ungültige Eingabedaten - bitte Formular prüfen'
      } else if (error.message) {
        errorMessage = error.message
      }
      
      setState(prev => ({
        ...prev,
        isGenerating: false,
        error: errorMessage
      }))
    }
  }, [finalConfig.apiBaseUrl])
  
  const debouncedPreview = useCallback((formData: Partial<WizardFormData>) => {
    if (!finalConfig.enableAutoPreview) {
      return
    }
    
    // Check if form data actually changed
    const formDataString = JSON.stringify(formData)
    if (formDataString === lastFormData.current) {
      return
    }
    lastFormData.current = formDataString
    
    // Clear existing timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
    }
    
    // Set new timer
    debounceTimer.current = setTimeout(() => {
      generatePreview(formData)
    }, finalConfig.debounceMs)
  }, [generatePreview, finalConfig.debounceMs, finalConfig.enableAutoPreview])
  
  const forcePreview = useCallback((formData: Partial<WizardFormData>) => {
    // Clear debounce timer and generate immediately
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
    }
    generatePreview(formData)
  }, [generatePreview])
  
  const clearPreview = useCallback(() => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
    }
    if (abortController.current) {
      abortController.current.abort()
    }
    
    setState({
      xmlContent: '',
      isGenerating: false,
      lastGenerated: null,
      placeholderCount: 0,
      completionPercentage: 0,
      error: null,
      generationTimeMs: 0
    })
  }, [])
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
      }
      if (abortController.current) {
        abortController.current.abort()
      }
    }
  }, [])
  
  // Helper to generate initial preview immediately on mount
  useEffect(() => {
    if (finalConfig.enableAutoPreview) {
      // Generate initial empty preview immediately (no debounce)
      generatePreview({})
    }
  }, [finalConfig.enableAutoPreview, generatePreview])
  
  return {
    // State
    ...state,
    
    // Actions
    generatePreview: debouncedPreview,
    forcePreview,
    clearPreview,
    
    // Computed values
    hasPlaceholders: state.placeholderCount > 0,
    isComplete: state.placeholderCount === 0,
    isEmpty: !state.xmlContent.trim(),
    
    // Progress indicators
    progressInfo: {
      percentage: state.completionPercentage,
      placeholders: state.placeholderCount,
      generationTime: state.generationTimeMs,
      lastUpdate: state.lastGenerated
    }
  }
}

export type XMLPreviewHook = ReturnType<typeof useXMLPreview>