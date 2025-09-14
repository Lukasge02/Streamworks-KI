/**
 * usePersistedState Hook
 * Provides state that persists to localStorage automatically
 */
'use client'

import { useState, useEffect, useCallback } from 'react'

/**
 * Custom hook for persisting state in localStorage
 * @param key - localStorage key
 * @param initialValue - initial value if no stored value exists
 * @returns [state, setState] tuple similar to useState
 */
export function usePersistedState<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  // Initialize state with value from localStorage or initialValue
  const [state, setState] = useState<T>(() => {
    if (typeof window === 'undefined') {
      // Return initialValue during SSR
      return initialValue
    }
    
    try {
      const storedValue = localStorage.getItem(key)
      if (storedValue !== null) {
        return JSON.parse(storedValue)
      }
    } catch (error) {
      console.warn(`Failed to parse localStorage value for key "${key}":`, error)
    }
    
    return initialValue
  })

  // Update localStorage whenever state changes
  const setValue = useCallback((value: T | ((prev: T) => T)) => {
    setState((prevState) => {
      const newValue = typeof value === 'function' ? (value as (prev: T) => T)(prevState) : value
      
      if (typeof window !== 'undefined') {
        try {
          localStorage.setItem(key, JSON.stringify(newValue))
        } catch (error) {
          console.warn(`Failed to save to localStorage for key "${key}":`, error)
        }
      }
      
      return newValue
    })
  }, [key])

  return [state, setValue]
}

/**
 * Hook for persisting view mode (grid/list) preference
 */
export function usePersistedViewMode(initialValue: 'grid' | 'list' = 'grid') {
  return usePersistedState('xml-streams-view-mode', initialValue)
}

/**
 * Hook for persisting sort preferences
 */
export function usePersistedSortBy(initialValue: string = 'updated_desc') {
  return usePersistedState('xml-streams-sort-by', initialValue)
}

/**
 * Hook for persisting filter sidebar state
 */
export function usePersistedFiltersVisible(initialValue: boolean = false) {
  return usePersistedState('xml-streams-filters-visible', initialValue)
}

/**
 * Hook for persisting stream filters
 */
export function usePersistedFilters(initialValue: any = {}) {
  return usePersistedState('xml-streams-filters', initialValue)
}

/**
 * Clear all persisted XML streams preferences
 */
export function clearXMLStreamsPreferences() {
  if (typeof window !== 'undefined') {
    try {
      localStorage.removeItem('xml-streams-view-mode')
      localStorage.removeItem('xml-streams-sort-by')
      localStorage.removeItem('xml-streams-filters-visible')
      localStorage.removeItem('xml-streams-filters')
    } catch (error) {
      console.warn('Failed to clear XML streams preferences:', error)
    }
  }
}