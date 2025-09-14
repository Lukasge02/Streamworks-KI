/**
 * useDebounced Hook
 * Provides debounced values and search functionality
 */
'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

/**
 * Hook that debounces a value
 * @param value - value to debounce
 * @param delay - delay in milliseconds (default: 300)
 * @returns debounced value
 */
export function useDebounced<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

/**
 * Hook that provides debounced search functionality
 * @param initialValue - initial search value
 * @param onSearchChange - callback when debounced search value changes
 * @param delay - debounce delay in milliseconds
 */
export function useDebouncedSearch(
  initialValue: string = '',
  onSearchChange?: (value: string) => void,
  delay: number = 500
) {
  const [searchValue, setSearchValue] = useState(initialValue)
  const [isSearching, setIsSearching] = useState(false)
  const debouncedSearchValue = useDebounced(searchValue, delay)
  const timeoutRef = useRef<NodeJS.Timeout>()

  // Handle immediate search value changes
  const handleSearchChange = useCallback((value: string) => {
    setSearchValue(value)
    setIsSearching(true)

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    // Set timeout to stop searching indicator
    timeoutRef.current = setTimeout(() => {
      setIsSearching(false)
    }, delay)
  }, [delay])

  // Handle debounced search value changes
  useEffect(() => {
    if (onSearchChange) {
      onSearchChange(debouncedSearchValue)
    }
    setIsSearching(false)
  }, [debouncedSearchValue, onSearchChange])

  // Cleanup
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return {
    searchValue,
    debouncedSearchValue,
    isSearching,
    setSearchValue: handleSearchChange,
    clearSearch: () => handleSearchChange('')
  }
}

/**
 * Hook for debounced API calls
 */
export function useDebouncedCallback<T extends any[]>(
  callback: (...args: T) => void,
  delay: number = 300
): (...args: T) => void {
  const timeoutRef = useRef<NodeJS.Timeout>()

  const debouncedCallback = useCallback((...args: T) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    timeoutRef.current = setTimeout(() => {
      callback(...args)
    }, delay)
  }, [callback, delay])

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return debouncedCallback
}