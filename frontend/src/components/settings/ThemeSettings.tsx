'use client'

import { useTheme } from 'next-themes'
import { useSettings, AccentColor, SidebarLayout } from '@/hooks/useSettings'
import { Sun, Moon, Monitor, Palette, Layout, Zap } from 'lucide-react'

const accentColors: { value: AccentColor; label: string; color: string; preview: string }[] = [
  { value: 'blue', label: 'Blau', color: 'bg-blue-500', preview: 'from-blue-500 to-blue-600' },
  { value: 'green', label: 'Grün', color: 'bg-green-500', preview: 'from-green-500 to-green-600' },
  { value: 'purple', label: 'Violett', color: 'bg-purple-500', preview: 'from-purple-500 to-purple-600' },
  { value: 'orange', label: 'Orange', color: 'bg-orange-500', preview: 'from-orange-500 to-orange-600' },
  { value: 'red', label: 'Rot', color: 'bg-red-500', preview: 'from-red-500 to-red-600' },
  { value: 'teal', label: 'Türkis', color: 'bg-teal-500', preview: 'from-teal-500 to-teal-600' },
]

const sidebarLayouts: { value: SidebarLayout; label: string; description: string }[] = [
  { value: 'compact', label: 'Kompakt', description: 'Schmalere Sidebar für mehr Platz' },
  { value: 'standard', label: 'Standard', description: 'Ausgewogene Größe mit Beschreibungen' },
  { value: 'extended', label: 'Erweitert', description: 'Breite Sidebar mit zusätzlichen Infos' },
]

export function ThemeSettings() {
  const { theme, setTheme } = useTheme()
  const { accentColor, sidebarLayout, enableAnimations, updateSettings } = useSettings()

  return (
    <div className="space-y-8">
      {/* Theme Mode */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Sun className="w-5 h-5 mr-2" />
          Theme-Modus
        </h3>
        <div className="grid grid-cols-3 gap-3">
          {[
            { value: 'light', label: 'Hell', icon: Sun },
            { value: 'dark', label: 'Dunkel', icon: Moon },
            { value: 'system', label: 'System', icon: Monitor },
          ].map((option) => {
            const Icon = option.icon
            return (
              <button
                key={option.value}
                onClick={() => setTheme(option.value)}
                className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                  theme === option.value
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
                }`}
              >
                <Icon className="w-6 h-6 mx-auto mb-2" />
                <div className="text-sm font-medium">{option.label}</div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Accent Colors */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Palette className="w-5 h-5 mr-2" />
          Akzentfarbe
        </h3>
        <div className="grid grid-cols-3 gap-3">
          {accentColors.map((color) => (
            <button
              key={color.value}
              onClick={() => updateSettings({ accentColor: color.value })}
              className={`p-4 rounded-xl border-2 transition-all duration-200 group ${
                accentColor === color.value
                  ? `border-${color.value}-500 bg-gradient-to-br ${color.preview} text-white`
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full mx-auto mb-2 ${
                  accentColor === color.value ? 'bg-white/20' : color.color
                }`}
              />
              <div className="text-sm font-medium">{color.label}</div>
            </button>
          ))}
        </div>
        
        {/* Live Preview */}
        <div className="mt-4 p-4 rounded-lg bg-gray-50 dark:bg-gray-800">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Vorschau:</p>
          <div className="flex items-center space-x-2">
            <button className={`px-4 py-2 rounded-lg text-white text-sm font-medium bg-gradient-to-r ${accentColors.find(c => c.value === accentColor)?.preview}`}>
              Beispiel Button
            </button>
            <div className={`w-3 h-3 rounded-full ${accentColors.find(c => c.value === accentColor)?.color}`} />
          </div>
        </div>
      </div>

      {/* Sidebar Layout */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Layout className="w-5 h-5 mr-2" />
          Sidebar-Layout
        </h3>
        <div className="space-y-2">
          {sidebarLayouts.map((layout) => (
            <label
              key={layout.value}
              className={`flex items-center p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                sidebarLayout === layout.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
              }`}
            >
              <input
                type="radio"
                name="sidebarLayout"
                value={layout.value}
                checked={sidebarLayout === layout.value}
                onChange={(e) => updateSettings({ sidebarLayout: e.target.value as SidebarLayout })}
                className="sr-only"
              />
              <div className="flex-1">
                <div className="font-medium text-gray-900 dark:text-white">{layout.label}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">{layout.description}</div>
              </div>
              <div className={`w-4 h-4 rounded-full border-2 ${
                sidebarLayout === layout.value
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-300 dark:border-gray-600'
              }`} />
            </label>
          ))}
        </div>
      </div>

      {/* Animations */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Zap className="w-5 h-5 mr-2" />
          Animationen
        </h3>
        <label className="flex items-center justify-between p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 cursor-pointer">
          <div>
            <div className="font-medium text-gray-900 dark:text-white">Animationen aktivieren</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Fade- und Slide-Animationen für bessere Übergänge
            </div>
          </div>
          <div className="relative">
            <input
              type="checkbox"
              checked={enableAnimations}
              onChange={(e) => updateSettings({ enableAnimations: e.target.checked })}
              className="sr-only"
            />
            <div
              className={`w-11 h-6 rounded-full transition-colors duration-200 ${
                enableAnimations ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
              }`}
            >
              <div
                className={`w-5 h-5 bg-white rounded-full shadow transition-transform duration-200 ${
                  enableAnimations ? 'translate-x-5' : 'translate-x-0.5'
                } mt-0.5`}
              />
            </div>
          </div>
        </label>
      </div>
    </div>
  )
}