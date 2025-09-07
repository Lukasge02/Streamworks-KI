'use client'

import { useEffect } from 'react'
import { useSettings, AccentColor } from './useSettings'

const accentColorMap: Record<AccentColor, string> = {
  blue: '#3b82f6',
  green: '#22c55e', 
  purple: '#a855f7',
  orange: '#f97316',
  red: '#ef4444',
  teal: '#14b8a6',
}

export function useThemeEnhancer() {
  const { accentColor, enableAnimations } = useSettings()
  
  useEffect(() => {
    const root = document.documentElement
    
    // Apply accent color as CSS custom property
    root.style.setProperty('--accent-color', accentColorMap[accentColor])
    root.style.setProperty('--accent-color-light', `${accentColorMap[accentColor]}20`)
    root.style.setProperty('--accent-color-dark', `${accentColorMap[accentColor]}80`)
    
    // Add accent color class to body for dynamic styling
    document.body.classList.remove('accent-blue', 'accent-green', 'accent-purple', 'accent-orange', 'accent-red', 'accent-teal')
    document.body.classList.add(`accent-${accentColor}`)
    
    // Control animations
    if (enableAnimations) {
      document.body.classList.remove('no-animations')
      document.body.classList.add('animations-enabled')
    } else {
      document.body.classList.remove('animations-enabled')
      document.body.classList.add('no-animations')
    }
  }, [accentColor, enableAnimations])
  
  return {
    accentColor,
    accentColorHex: accentColorMap[accentColor],
    enableAnimations,
  }
}