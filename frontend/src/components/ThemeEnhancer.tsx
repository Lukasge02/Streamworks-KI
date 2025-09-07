'use client'

import { useThemeEnhancer } from '@/hooks/useThemeEnhancer'

export function ThemeEnhancer() {
  // This component just runs the theme enhancement hook
  // No visible UI, just side effects
  useThemeEnhancer()
  return null
}