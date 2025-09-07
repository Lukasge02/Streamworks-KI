'use client'

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { useTheme } from 'next-themes'

export type ThemeMode = 'light' | 'dark' | 'system'
export type AccentColor = 'blue' | 'green' | 'purple' | 'orange' | 'red' | 'teal'
export type SidebarLayout = 'compact' | 'standard' | 'extended'
export type ToastPosition = 'top-right' | 'top-center' | 'bottom-right' | 'bottom-center'
export type UploadSizeUnit = 'MB' | 'GB'
export type SortOrder = 'name' | 'date' | 'size' | 'type'
export type Language = 'de' | 'en'
export type DateFormat = 'DD.MM.YYYY' | 'MM/DD/YYYY' | 'YYYY-MM-DD'
export type TimeFormat = '24h' | '12h'

export interface SettingsState {
  // Appearance Settings
  accentColor: AccentColor
  sidebarLayout: SidebarLayout
  enableAnimations: boolean
  
  // System & Performance Settings  
  autoRefreshInterval: number // in seconds, 0 = disabled
  debugMode: boolean
  cacheTimeMinutes: number
  
  // Upload Settings
  maxUploadSize: number
  maxUploadSizeUnit: UploadSizeUnit
  allowedFileTypes: string[]
  
  // Document Settings
  defaultFolder: string | null
  thumbnailSize: 'small' | 'medium' | 'large'
  defaultSortOrder: SortOrder
  autoBackup: boolean
  
  // Chat & AI Settings
  chatResponseLength: 'short' | 'medium' | 'detailed'
  autoScrollChat: boolean
  codeHighlightTheme: 'github' | 'monokai' | 'solarized'
  aiLanguage: Language
  
  // Notification Settings
  toastPosition: ToastPosition
  enableSounds: boolean
  enableBrowserNotifications: boolean
  showUploadProgress: boolean
  
  // Localization Settings
  language: Language
  dateFormat: DateFormat
  timeFormat: TimeFormat
  
  // Actions
  updateSettings: (settings: Partial<Omit<SettingsState, 'updateSettings' | 'resetSettings' | 'exportSettings' | 'importSettings'>>) => void
  resetSettings: () => void
  exportSettings: () => string
  importSettings: (settingsJson: string) => void
}

const defaultSettings: Omit<SettingsState, 'updateSettings' | 'resetSettings' | 'exportSettings' | 'importSettings'> = {
  // Appearance
  accentColor: 'blue',
  sidebarLayout: 'standard',
  enableAnimations: true,
  
  // System & Performance
  autoRefreshInterval: 30,
  debugMode: false,
  cacheTimeMinutes: 5,
  
  // Upload Settings
  maxUploadSize: 50,
  maxUploadSizeUnit: 'MB',
  allowedFileTypes: ['.pdf', '.docx', '.txt', '.md', '.png', '.jpg', '.jpeg'],
  
  // Document Settings
  defaultFolder: null,
  thumbnailSize: 'medium',
  defaultSortOrder: 'date',
  autoBackup: false,
  
  // Chat & AI Settings
  chatResponseLength: 'medium',
  autoScrollChat: true,
  codeHighlightTheme: 'github',
  aiLanguage: 'de',
  
  // Notification Settings
  toastPosition: 'top-right',
  enableSounds: false,
  enableBrowserNotifications: false,
  showUploadProgress: true,
  
  // Localization
  language: 'de',
  dateFormat: 'DD.MM.YYYY',
  timeFormat: '24h',
}

export const useSettings = create<SettingsState>()(
  persist(
    (set, get) => ({
      ...defaultSettings,
      
      updateSettings: (newSettings) => {
        set((state) => ({
          ...state,
          ...newSettings,
        }))
      },
      
      resetSettings: () => {
        set((state) => ({
          ...defaultSettings,
          updateSettings: state.updateSettings,
          resetSettings: state.resetSettings,
          exportSettings: state.exportSettings,
          importSettings: state.importSettings,
        }))
      },
      
      exportSettings: () => {
        const currentState = get()
        const settingsToExport = { ...currentState }
        // Remove functions from export
        delete (settingsToExport as any).updateSettings
        delete (settingsToExport as any).resetSettings
        delete (settingsToExport as any).exportSettings
        delete (settingsToExport as any).importSettings
        
        return JSON.stringify(settingsToExport, null, 2)
      },
      
      importSettings: (settingsJson: string) => {
        try {
          const importedSettings = JSON.parse(settingsJson)
          // Validate imported settings by merging with defaults
          const validatedSettings = {
            ...defaultSettings,
            ...importedSettings,
          }
          
          set((state) => ({
            ...validatedSettings,
            updateSettings: state.updateSettings,
            resetSettings: state.resetSettings,
            exportSettings: state.exportSettings,
            importSettings: state.importSettings,
          }))
        } catch (error) {
          console.error('Failed to import settings:', error)
          throw new Error('Invalid settings format')
        }
      },
    }),
    {
      name: 'streamworks-settings',
      storage: createJSONStorage(() => localStorage),
      version: 1,
    }
  )
)

// Hook to sync theme with next-themes
export const useThemeSync = () => {
  const { setTheme } = useTheme()
  const accentColor = useSettings((state) => state.accentColor)
  
  return {
    setTheme,
    accentColor,
  }
}