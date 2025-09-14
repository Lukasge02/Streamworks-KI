/**
 * Deep comparison hooks for React components
 * Prevents unnecessary re-renders from reference changes without content changes
 */
import { useRef, useEffect, useState } from 'react'

/**
 * Deep comparison function for objects
 */
function deepEqual(a: any, b: any): boolean {
  if (a === b) return true

  if (a == null || b == null) return false

  if (typeof a !== typeof b) return false

  if (typeof a !== 'object') return false

  if (Array.isArray(a) !== Array.isArray(b)) return false

  const keysA = Object.keys(a)
  const keysB = Object.keys(b)

  if (keysA.length !== keysB.length) return false

  for (let key of keysA) {
    if (!keysB.includes(key)) return false
    if (!deepEqual(a[key], b[key])) return false
  }

  return true
}

/**
 * Hook that returns true when the value has deeply changed
 */
export function useDeepCompare<T>(value: T): boolean {
  const ref = useRef<T>()
  const hasChanged = !deepEqual(value, ref.current)

  if (hasChanged) {
    ref.current = value
  }

  return hasChanged
}

/**
 * Hook that returns the value only when it has deeply changed
 * Similar to useMemo but with deep comparison
 */
export function useDeepCompareMemo<T>(value: T): T {
  const ref = useRef<T>(value)

  if (!deepEqual(value, ref.current)) {
    ref.current = value
  }

  return ref.current
}

/**
 * Hook that tracks changes in form data and provides change metadata
 */
export function useFormChangeTracking<T extends Record<string, any>>(formData: T) {
  const previousRef = useRef<T>(formData)
  const hasChanged = useDeepCompare(formData)

  useEffect(() => {
    if (hasChanged) {
      previousRef.current = formData
    }
  }, [hasChanged, formData])

  const getChangedFields = (): string[] => {
    if (!hasChanged) return []

    const changed: string[] = []
    const prev = previousRef.current || {}

    const checkFields = (current: any, previous: any, path = '') => {
      Object.keys(current).forEach(key => {
        const currentPath = path ? `${path}.${key}` : key
        const currentValue = current[key]
        const previousValue = previous[key]

        if (typeof currentValue === 'object' && currentValue !== null) {
          checkFields(currentValue, previousValue || {}, currentPath)
        } else if (!deepEqual(currentValue, previousValue)) {
          changed.push(currentPath)
        }
      })
    }

    checkFields(formData, prev)
    return changed
  }

  return {
    hasChanged,
    changedFields: getChangedFields(),
    previousData: previousRef.current
  }
}

/**
 * Debounced deep comparison hook
 * Only triggers change after specified delay of no changes
 */
export function useDebouncedDeepCompare<T>(value: T, delay: number = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)
  const timeoutRef = useRef<NodeJS.Timeout>()

  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    timeoutRef.current = setTimeout(() => {
      if (!deepEqual(value, debouncedValue)) {
        setDebouncedValue(value)
      }
    }, delay)

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [value, delay])

  return debouncedValue
}