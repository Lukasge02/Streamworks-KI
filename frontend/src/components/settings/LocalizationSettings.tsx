'use client'

import { useSettings, Language, DateFormat, TimeFormat } from '@/hooks/useSettings'
import { Globe, Calendar, Clock } from 'lucide-react'

export function LocalizationSettings() {
  const { 
    language,
    dateFormat,
    timeFormat,
    updateSettings 
  } = useSettings()

  const languages = [
    { value: 'de' as Language, label: 'Deutsch', flag: '🇩🇪' },
    { value: 'en' as Language, label: 'English', flag: '🇺🇸' },
  ]

  const dateFormats: { value: DateFormat; label: string; example: string }[] = [
    { value: 'DD.MM.YYYY', label: 'Deutsch (DD.MM.YYYY)', example: '25.12.2024' },
    { value: 'MM/DD/YYYY', label: 'Amerikanisch (MM/DD/YYYY)', example: '12/25/2024' },
    { value: 'YYYY-MM-DD', label: 'ISO (YYYY-MM-DD)', example: '2024-12-25' },
  ]

  const timeFormats: { value: TimeFormat; label: string; example: string }[] = [
    { value: '24h', label: '24-Stunden Format', example: '14:30' },
    { value: '12h', label: '12-Stunden Format', example: '2:30 PM' },
  ]

  const getCurrentDate = () => {
    const now = new Date()
    return now
  }

  const formatDatePreview = (format: DateFormat) => {
    const date = getCurrentDate()
    switch (format) {
      case 'DD.MM.YYYY':
        return date.toLocaleDateString('de-DE')
      case 'MM/DD/YYYY':
        return date.toLocaleDateString('en-US')
      case 'YYYY-MM-DD':
        return date.toISOString().split('T')[0]
      default:
        return date.toLocaleDateString()
    }
  }

  const formatTimePreview = (format: TimeFormat) => {
    const date = getCurrentDate()
    if (format === '24h') {
      return date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
    } else {
      return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
    }
  }

  return (
    <div className="space-y-8">
      {/* Language */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Globe className="w-5 h-5 mr-2" />
          Sprache
        </h3>
        <div className="space-y-2">
          {languages.map((lang) => (
            <label
              key={lang.value}
              className={`flex items-center p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                language === lang.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
              }`}
            >
              <input
                type="radio"
                name="language"
                value={lang.value}
                checked={language === lang.value}
                onChange={(e) => updateSettings({ language: e.target.value as Language })}
                className="sr-only"
              />
              <div className="text-2xl mr-3">{lang.flag}</div>
              <div className="flex-1">
                <div className="font-medium text-gray-900 dark:text-white">{lang.label}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {lang.value === 'de' ? 'Benutzeroberfläche auf Deutsch' : 'Interface in English'}
                </div>
              </div>
              <div className={`w-4 h-4 rounded-full border-2 ${
                language === lang.value
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-300 dark:border-gray-600'
              }`} />
            </label>
          ))}
        </div>
        
        <div className="mt-4 p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            <strong>Hinweis:</strong> Sprachänderungen werden nach dem nächsten Neuladen der Seite wirksam.
          </p>
        </div>
      </div>

      {/* Date Format */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Calendar className="w-5 h-5 mr-2" />
          Datumsformat
        </h3>
        <div className="space-y-2">
          {dateFormats.map((format) => (
            <label
              key={format.value}
              className={`flex items-center p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                dateFormat === format.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
              }`}
            >
              <input
                type="radio"
                name="dateFormat"
                value={format.value}
                checked={dateFormat === format.value}
                onChange={(e) => updateSettings({ dateFormat: e.target.value as DateFormat })}
                className="sr-only"
              />
              <div className="flex-1">
                <div className="font-medium text-gray-900 dark:text-white">{format.label}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Beispiel: {format.example}
                </div>
              </div>
              <div className="text-sm font-mono text-blue-600 dark:text-blue-400 mr-4">
                {formatDatePreview(format.value)}
              </div>
              <div className={`w-4 h-4 rounded-full border-2 ${
                dateFormat === format.value
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-300 dark:border-gray-600'
              }`} />
            </label>
          ))}
        </div>
      </div>

      {/* Time Format */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Clock className="w-5 h-5 mr-2" />
          Zeitformat
        </h3>
        <div className="space-y-2">
          {timeFormats.map((format) => (
            <label
              key={format.value}
              className={`flex items-center p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                timeFormat === format.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
              }`}
            >
              <input
                type="radio"
                name="timeFormat"
                value={format.value}
                checked={timeFormat === format.value}
                onChange={(e) => updateSettings({ timeFormat: e.target.value as TimeFormat })}
                className="sr-only"
              />
              <div className="flex-1">
                <div className="font-medium text-gray-900 dark:text-white">{format.label}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Beispiel: {format.example}
                </div>
              </div>
              <div className="text-sm font-mono text-blue-600 dark:text-blue-400 mr-4">
                {formatTimePreview(format.value)}
              </div>
              <div className={`w-4 h-4 rounded-full border-2 ${
                timeFormat === format.value
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-300 dark:border-gray-600'
              }`} />
            </label>
          ))}
        </div>
      </div>

      {/* Preview */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Vorschau der aktuellen Einstellungen
        </h3>
        <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Sprache:</span>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {languages.find(l => l.value === language)?.label}
              </span>
              <span className="text-lg">
                {languages.find(l => l.value === language)?.flag}
              </span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Aktuelles Datum:</span>
            <span className="text-sm font-mono text-gray-900 dark:text-white">
              {formatDatePreview(dateFormat)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Aktuelle Zeit:</span>
            <span className="text-sm font-mono text-gray-900 dark:text-white">
              {formatTimePreview(timeFormat)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Vollständig:</span>
            <span className="text-sm font-mono text-gray-900 dark:text-white">
              {formatDatePreview(dateFormat)} {formatTimePreview(timeFormat)}
            </span>
          </div>
        </div>
      </div>

      {/* Localization Note */}
      <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700">
        <h4 className="font-medium text-blue-900 dark:text-blue-200 mb-2">Lokalisierung</h4>
        <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
          <li>• Sprache betrifft die gesamte Benutzeroberfläche</li>
          <li>• Datum und Zeit werden in allen Listen und Dialogen verwendet</li>
          <li>• Ihre Einstellungen werden automatisch gespeichert</li>
        </ul>
      </div>
    </div>
  )
}