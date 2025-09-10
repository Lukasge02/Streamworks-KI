/**
 * Utility functions for consistent time formatting that avoid hydration mismatches
 */

/**
 * Format time for display - only works on client side to avoid hydration issues
 */
export const formatTimeForDisplay = (date: Date | string, isClient: boolean): string => {
  if (!isClient) return ''
  
  // Convert string timestamps to Date objects
  const dateObj = typeof date === 'string' ? new Date(date) : date
  
  // Validate the date is valid
  if (!dateObj || isNaN(dateObj.getTime())) return ''
  
  return dateObj.toLocaleTimeString('de-DE', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  })
}

/**
 * Format relative time for display - only works on client side to avoid hydration issues
 */
export const formatRelativeTimeForDisplay = (date: Date | string, isClient: boolean): string => {
  if (!isClient) return ''
  
  // Convert string timestamps to Date objects
  const dateObj = typeof date === 'string' ? new Date(date) : date
  
  // Validate the date is valid
  if (!dateObj || isNaN(dateObj.getTime())) return ''
  
  const now = new Date()
  const diffMs = now.getTime() - dateObj.getTime()
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMinutes < 1) return 'Gerade eben'
  if (diffMinutes < 60) return `vor ${diffMinutes}m`
  if (diffHours < 24) return `vor ${diffHours}h`
  if (diffDays === 1) return 'Gestern'
  if (diffDays < 7) return `vor ${diffDays} Tagen`
  return dateObj.toLocaleDateString('de-DE')
}

/**
 * Create a default session title that's consistent across server/client
 */
export const createDefaultSessionTitle = (): string => {
  const now = new Date()
  return `Chat ${now.getDate().toString().padStart(2, '0')}.${(now.getMonth() + 1).toString().padStart(2, '0')}.${now.getFullYear()}`
}