'use client'

import { useSettings } from '@/hooks/useSettings'
import { Activity, Clock, HardDrive, Bug, Upload, Zap } from 'lucide-react'

export function SystemSettings() {
  const { 
    autoRefreshInterval, 
    debugMode, 
    cacheTimeMinutes,
    maxUploadSize,
    maxUploadSizeUnit,
    allowedFileTypes,
    updateSettings 
  } = useSettings()

  const refreshIntervals = [
    { value: 0, label: 'Aus' },
    { value: 15, label: '15 Sekunden' },
    { value: 30, label: '30 Sekunden' },
    { value: 60, label: '1 Minute' },
    { value: 300, label: '5 Minuten' },
  ]

  const cacheOptions = [
    { value: 1, label: '1 Minute' },
    { value: 5, label: '5 Minuten' },
    { value: 10, label: '10 Minuten' },
    { value: 30, label: '30 Minuten' },
    { value: 60, label: '1 Stunde' },
  ]

  const uploadSizes = [
    { value: 10, label: '10' },
    { value: 25, label: '25' },
    { value: 50, label: '50' },
    { value: 100, label: '100' },
    { value: 500, label: '500' },
  ]

  const handleFileTypeChange = (fileType: string, checked: boolean) => {
    if (checked) {
      updateSettings({ allowedFileTypes: [...allowedFileTypes, fileType] })
    } else {
      updateSettings({ allowedFileTypes: allowedFileTypes.filter(type => type !== fileType) })
    }
  }

  const commonFileTypes = [
    { value: '.pdf', label: 'PDF Dokumente' },
    { value: '.docx', label: 'Word Dokumente' },
    { value: '.txt', label: 'Text Dateien' },
    { value: '.md', label: 'Markdown Dateien' },
    { value: '.png', label: 'PNG Bilder' },
    { value: '.jpg', label: 'JPG Bilder' },
    { value: '.jpeg', label: 'JPEG Bilder' },
    { value: '.xlsx', label: 'Excel Dateien' },
    { value: '.pptx', label: 'PowerPoint Dateien' },
  ]

  return (
    <div className="space-y-8">
      {/* Auto-Refresh */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Activity className="w-5 h-5 mr-2" />
          Backend Health Check
        </h3>
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Auto-Refresh Intervall
          </label>
          <select
            value={autoRefreshInterval}
            onChange={(e) => updateSettings({ autoRefreshInterval: Number(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {refreshIntervals.map((interval) => (
              <option key={interval.value} value={interval.value}>
                {interval.label}
              </option>
            ))}
          </select>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Wie oft das System die Backend-Verbindung überprüfen soll
          </p>
        </div>
      </div>

      {/* Cache Settings */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <HardDrive className="w-5 h-5 mr-2" />
          Caching
        </h3>
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Cache-Dauer für API-Anfragen
          </label>
          <select
            value={cacheTimeMinutes}
            onChange={(e) => updateSettings({ cacheTimeMinutes: Number(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {cacheOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Längere Cache-Zeiten reduzieren Server-Anfragen, können aber veraltete Daten anzeigen
          </p>
        </div>
      </div>

      {/* Upload Settings */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Upload className="w-5 h-5 mr-2" />
          Upload-Einstellungen
        </h3>
        
        {/* Max Upload Size */}
        <div className="space-y-3 mb-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Maximale Dateigröße
          </label>
          <div className="flex space-x-2">
            <select
              value={maxUploadSize}
              onChange={(e) => updateSettings({ maxUploadSize: Number(e.target.value) })}
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {uploadSizes.map((size) => (
                <option key={size.value} value={size.value}>
                  {size.label}
                </option>
              ))}
            </select>
            <select
              value={maxUploadSizeUnit}
              onChange={(e) => updateSettings({ maxUploadSizeUnit: e.target.value as 'MB' | 'GB' })}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="MB">MB</option>
              <option value="GB">GB</option>
            </select>
          </div>
        </div>

        {/* Allowed File Types */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Erlaubte Dateitypen
          </label>
          <div className="grid grid-cols-2 gap-2">
            {commonFileTypes.map((fileType) => (
              <label
                key={fileType.value}
                className="flex items-center p-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <input
                  type="checkbox"
                  checked={allowedFileTypes.includes(fileType.value)}
                  onChange={(e) => handleFileTypeChange(fileType.value, e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
                />
                <span className="ml-3 text-sm text-gray-900 dark:text-white">{fileType.label}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Debug Mode */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Bug className="w-5 h-5 mr-2" />
          Entwickleroptionen
        </h3>
        <label className="flex items-center justify-between p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 cursor-pointer">
          <div>
            <div className="font-medium text-gray-900 dark:text-white">Debug-Modus</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Erweiterte Logs und Fehlermeldungen in der Entwicklerkonsole
            </div>
          </div>
          <div className="relative">
            <input
              type="checkbox"
              checked={debugMode}
              onChange={(e) => updateSettings({ debugMode: e.target.checked })}
              className="sr-only"
            />
            <div
              className={`w-11 h-6 rounded-full transition-colors duration-200 ${
                debugMode ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
              }`}
            >
              <div
                className={`w-5 h-5 bg-white rounded-full shadow transition-transform duration-200 ${
                  debugMode ? 'translate-x-5' : 'translate-x-0.5'
                } mt-0.5`}
              />
            </div>
          </div>
        </label>
        
        {debugMode && (
          <div className="mt-4 p-4 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700">
            <div className="flex items-start">
              <Zap className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-2 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                  Debug-Modus aktiv
                </p>
                <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                  Zusätzliche Informationen werden in der Browser-Konsole ausgegeben. 
                  Dies kann die Performance beeinträchtigen.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}