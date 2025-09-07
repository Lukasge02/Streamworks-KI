'use client'

import { useState } from 'react'
import { useSettings } from '@/hooks/useSettings'
import { Database, Download, Upload, Trash2, HardDrive, AlertTriangle, CheckCircle } from 'lucide-react'

export function DataSettings() {
  const { exportSettings, importSettings, resetSettings } = useSettings()
  const [showClearConfirm, setShowClearConfirm] = useState(false)
  const [importStatus, setImportStatus] = useState<'idle' | 'success' | 'error'>('idle')

  const handleExportSettings = () => {
    try {
      const settingsData = exportSettings()
      const blob = new Blob([settingsData], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `streamworks-settings-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  const handleImportSettings = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.json'
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          try {
            const settingsData = e.target?.result as string
            importSettings(settingsData)
            setImportStatus('success')
            setTimeout(() => setImportStatus('idle'), 3000)
          } catch (error) {
            console.error('Import failed:', error)
            setImportStatus('error')
            setTimeout(() => setImportStatus('idle'), 3000)
          }
        }
        reader.readAsText(file)
      }
    }
    input.click()
  }

  const handleClearCache = () => {
    // Clear React Query cache, localStorage items etc.
    if (window.localStorage) {
      const keysToKeep = ['streamworks-settings']
      const keysToRemove = []
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key && !keysToKeep.includes(key)) {
          keysToRemove.push(key)
        }
      }
      
      keysToRemove.forEach(key => localStorage.removeItem(key))
    }
    
    // Clear session storage
    if (window.sessionStorage) {
      sessionStorage.clear()
    }
    
    setShowClearConfirm(false)
  }

  const getStorageSize = () => {
    if (!window.localStorage) return 'Nicht verfügbar'
    
    let totalSize = 0
    for (let key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        totalSize += localStorage.getItem(key)?.length || 0
      }
    }
    
    // Convert to KB
    const sizeKB = Math.round(totalSize / 1024 * 100) / 100
    return sizeKB < 1024 ? `${sizeKB} KB` : `${Math.round(sizeKB / 1024 * 100) / 100} MB`
  }

  return (
    <div className="space-y-8">
      {/* Export/Import Settings */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Database className="w-5 h-5 mr-2" />
          Einstellungen verwalten
        </h3>
        
        <div className="space-y-4">
          {/* Export */}
          <div className="flex items-center justify-between p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
            <div className="flex items-start space-x-3">
              <Download className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
              <div>
                <div className="font-medium text-gray-900 dark:text-white">Einstellungen exportieren</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Speichert alle Ihre Einstellungen als JSON-Datei
                </div>
              </div>
            </div>
            <button
              onClick={handleExportSettings}
              className="px-4 py-2 text-sm font-medium text-blue-700 dark:text-blue-300 bg-blue-100 dark:bg-blue-900/30 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
            >
              Exportieren
            </button>
          </div>

          {/* Import */}
          <div className="flex items-center justify-between p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
            <div className="flex items-start space-x-3">
              <Upload className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
              <div>
                <div className="font-medium text-gray-900 dark:text-white">Einstellungen importieren</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Lädt Einstellungen aus einer zuvor exportierten Datei
                </div>
              </div>
            </div>
            <button
              onClick={handleImportSettings}
              className="px-4 py-2 text-sm font-medium text-green-700 dark:text-green-300 bg-green-100 dark:bg-green-900/30 rounded-lg hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors"
            >
              Importieren
            </button>
          </div>

          {/* Import Status */}
          {importStatus !== 'idle' && (
            <div className={`p-3 rounded-lg flex items-center space-x-2 ${
              importStatus === 'success' 
                ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700'
                : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700'
            }`}>
              {importStatus === 'success' ? (
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
              )}
              <p className={`text-sm font-medium ${
                importStatus === 'success' 
                  ? 'text-green-800 dark:text-green-200'
                  : 'text-red-800 dark:text-red-200'
              }`}>
                {importStatus === 'success' 
                  ? 'Einstellungen erfolgreich importiert!'
                  : 'Fehler beim Importieren der Einstellungen.'
                }
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Storage Info */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <HardDrive className="w-5 h-5 mr-2" />
          Speicher-Information
        </h3>
        
        <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Lokaler Speicher belegt:</span>
            <span className="text-sm font-mono text-gray-900 dark:text-white">
              {getStorageSize()}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Einstellungen gespeichert:</span>
            <span className="text-sm font-medium text-green-600 dark:text-green-400">
              Ja
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Cache-Status:</span>
            <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
              Aktiv
            </span>
          </div>
        </div>
      </div>

      {/* Clear Data */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Trash2 className="w-5 h-5 mr-2" />
          Daten löschen
        </h3>
        
        <div className="space-y-4">
          {/* Clear Cache */}
          <div className="flex items-center justify-between p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
            <div>
              <div className="font-medium text-gray-900 dark:text-white">Cache leeren</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Löscht gespeicherte Daten und temporäre Dateien (Einstellungen bleiben erhalten)
              </div>
            </div>
            <button
              onClick={() => setShowClearConfirm(true)}
              className="px-4 py-2 text-sm font-medium text-orange-700 dark:text-orange-300 bg-orange-100 dark:bg-orange-900/30 rounded-lg hover:bg-orange-200 dark:hover:bg-orange-900/50 transition-colors"
            >
              Cache leeren
            </button>
          </div>

          {/* Reset All */}
          <div className="flex items-center justify-between p-4 rounded-xl border border-red-200 dark:border-red-700 bg-red-50 dark:bg-red-900/20">
            <div>
              <div className="font-medium text-red-900 dark:text-red-200">Alle Einstellungen zurücksetzen</div>
              <div className="text-sm text-red-700 dark:text-red-300">
                Setzt alle Einstellungen auf Standardwerte zurück. Diese Aktion kann nicht rückgängig gemacht werden.
              </div>
            </div>
            <button
              onClick={() => {
                if (confirm('Alle Einstellungen zurücksetzen? Diese Aktion kann nicht rückgängig gemacht werden.')) {
                  resetSettings()
                }
              }}
              className="px-4 py-2 text-sm font-medium text-red-700 dark:text-red-300 bg-red-100 dark:bg-red-900/30 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors"
            >
              Zurücksetzen
            </button>
          </div>
        </div>
      </div>

      {/* Data Privacy Note */}
      <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700">
        <h4 className="font-medium text-blue-900 dark:text-blue-200 mb-2 flex items-center">
          <Database className="w-4 h-4 mr-2" />
          Datenschutz-Hinweis
        </h4>
        <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
          <li>• Alle Einstellungen werden nur lokal in Ihrem Browser gespeichert</li>
          <li>• Keine Daten werden an externe Server übertragen</li>
          <li>• Beim Löschen der Browser-Daten gehen auch Ihre Einstellungen verloren</li>
          <li>• Exportierte Einstellungen enthalten keine persönlichen Dokumente</li>
        </ul>
      </div>

      {/* Clear Cache Confirmation */}
      {showClearConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Cache wirklich leeren?
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
              Dies löscht alle gespeicherten temporären Daten, aber Ihre Einstellungen bleiben erhalten. 
              Die Anwendung muss möglicherweise einige Daten neu laden.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowClearConfirm(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                Abbrechen
              </button>
              <button
                onClick={handleClearCache}
                className="px-4 py-2 text-sm font-medium text-white bg-orange-600 rounded-lg hover:bg-orange-700 transition-colors"
              >
                Cache leeren
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}