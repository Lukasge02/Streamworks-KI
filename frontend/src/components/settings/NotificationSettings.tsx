'use client'

import { useSettings, ToastPosition } from '@/hooks/useSettings'
import { Bell, Volume2, Monitor, BarChart3, MapPin } from 'lucide-react'

export function NotificationSettings() {
  const { 
    toastPosition,
    enableSounds,
    enableBrowserNotifications,
    showUploadProgress,
    updateSettings 
  } = useSettings()

  const toastPositions: { value: ToastPosition; label: string; description: string }[] = [
    { value: 'top-right', label: 'Oben rechts', description: 'Standard-Position für Desktop-Apps' },
    { value: 'top-center', label: 'Oben mittig', description: 'Zentral und gut sichtbar' },
    { value: 'bottom-right', label: 'Unten rechts', description: 'Weniger störend beim Arbeiten' },
    { value: 'bottom-center', label: 'Unten mittig', description: 'Wie mobile App-Benachrichtigungen' },
  ]

  const requestBrowserPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission()
      if (permission === 'granted') {
        updateSettings({ enableBrowserNotifications: true })
        new Notification('Streamworks', {
          body: 'Browser-Benachrichtigungen wurden aktiviert!',
          icon: '/favicon.ico'
        })
      }
    }
  }

  const testToastPosition = () => {
    // This would trigger a test toast in the actual app
    console.log(`Testing toast at position: ${toastPosition}`)
  }

  return (
    <div className="space-y-8">
      {/* Toast Position */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <MapPin className="w-5 h-5 mr-2" />
          Toast-Benachrichtigungen Position
        </h3>
        <div className="space-y-2">
          {toastPositions.map((position) => (
            <label
              key={position.value}
              className={`flex items-center p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                toastPosition === position.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
              }`}
            >
              <input
                type="radio"
                name="toastPosition"
                value={position.value}
                checked={toastPosition === position.value}
                onChange={(e) => updateSettings({ toastPosition: e.target.value as ToastPosition })}
                className="sr-only"
              />
              <div className="flex-1">
                <div className="font-medium text-gray-900 dark:text-white">{position.label}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">{position.description}</div>
              </div>
              <div className={`w-4 h-4 rounded-full border-2 ${
                toastPosition === position.value
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-300 dark:border-gray-600'
              }`} />
            </label>
          ))}
        </div>
        
        {/* Test Button */}
        <div className="mt-4">
          <button
            onClick={testToastPosition}
            className="px-4 py-2 text-sm font-medium text-blue-700 dark:text-blue-300 bg-blue-100 dark:bg-blue-900/30 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
          >
            Position testen
          </button>
        </div>

        {/* Visual Preview */}
        <div className="mt-6 relative bg-gray-100 dark:bg-gray-700 rounded-lg h-32 overflow-hidden">
          <div className="absolute inset-0 flex items-center justify-center text-sm text-gray-500 dark:text-gray-400">
            Vorschau-Bereich
          </div>
          <div
            className={`absolute w-32 h-8 bg-blue-500 rounded-lg flex items-center justify-center text-white text-xs font-medium transition-all duration-300 ${
              toastPosition === 'top-right' ? 'top-2 right-2' :
              toastPosition === 'top-center' ? 'top-2 left-1/2 transform -translate-x-1/2' :
              toastPosition === 'bottom-right' ? 'bottom-2 right-2' :
              'bottom-2 left-1/2 transform -translate-x-1/2'
            }`}
          >
            Test Toast
          </div>
        </div>
      </div>

      {/* Sound Settings */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Volume2 className="w-5 h-5 mr-2" />
          Audio-Feedback
        </h3>
        <label className="flex items-center justify-between p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 cursor-pointer">
          <div>
            <div className="font-medium text-gray-900 dark:text-white">Sounds aktivieren</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Spielt Töne bei Erfolg, Fehlern und wichtigen Ereignissen ab
            </div>
          </div>
          <div className="relative">
            <input
              type="checkbox"
              checked={enableSounds}
              onChange={(e) => updateSettings({ enableSounds: e.target.checked })}
              className="sr-only"
            />
            <div
              className={`w-11 h-6 rounded-full transition-colors duration-200 ${
                enableSounds ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
              }`}
            >
              <div
                className={`w-5 h-5 bg-white rounded-full shadow transition-transform duration-200 ${
                  enableSounds ? 'translate-x-5' : 'translate-x-0.5'
                } mt-0.5`}
              />
            </div>
          </div>
        </label>
      </div>

      {/* Browser Notifications */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Monitor className="w-5 h-5 mr-2" />
          Browser-Benachrichtigungen
        </h3>
        
        <div className="space-y-4">
          <label className="flex items-center justify-between p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 cursor-pointer">
            <div>
              <div className="font-medium text-gray-900 dark:text-white">Desktop-Benachrichtigungen</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Zeigt wichtige Ereignisse auch bei minimiertem Browser an
              </div>
            </div>
            <div className="relative">
              <input
                type="checkbox"
                checked={enableBrowserNotifications}
                onChange={(e) => {
                  if (e.target.checked) {
                    requestBrowserPermission()
                  } else {
                    updateSettings({ enableBrowserNotifications: false })
                  }
                }}
                className="sr-only"
              />
              <div
                className={`w-11 h-6 rounded-full transition-colors duration-200 ${
                  enableBrowserNotifications ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                }`}
              >
                <div
                  className={`w-5 h-5 bg-white rounded-full shadow transition-transform duration-200 ${
                    enableBrowserNotifications ? 'translate-x-5' : 'translate-x-0.5'
                  } mt-0.5`}
                />
              </div>
            </div>
          </label>

          {/* Browser Permission Status */}
          {'Notification' in window && (
            <div className={`p-3 rounded-lg ${
              Notification.permission === 'granted' ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700' :
              Notification.permission === 'denied' ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700' :
              'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700'
            }`}>
              <p className={`text-sm font-medium ${
                Notification.permission === 'granted' ? 'text-green-800 dark:text-green-200' :
                Notification.permission === 'denied' ? 'text-red-800 dark:text-red-200' :
                'text-yellow-800 dark:text-yellow-200'
              }`}>
                Browser-Berechtigung: {
                  Notification.permission === 'granted' ? 'Erteilt' :
                  Notification.permission === 'denied' ? 'Verweigert' :
                  'Ausstehend'
                }
              </p>
              {Notification.permission === 'denied' && (
                <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                  Bitte aktivieren Sie Benachrichtigungen in den Browser-Einstellungen
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Upload Progress */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2" />
          Upload-Anzeigen
        </h3>
        <label className="flex items-center justify-between p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 cursor-pointer">
          <div>
            <div className="font-medium text-gray-900 dark:text-white">Upload-Fortschritt anzeigen</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Zeigt detaillierte Fortschrittsbalken und Status-Updates während Uploads
            </div>
          </div>
          <div className="relative">
            <input
              type="checkbox"
              checked={showUploadProgress}
              onChange={(e) => updateSettings({ showUploadProgress: e.target.checked })}
              className="sr-only"
            />
            <div
              className={`w-11 h-6 rounded-full transition-colors duration-200 ${
                showUploadProgress ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
              }`}
            >
              <div
                className={`w-5 h-5 bg-white rounded-full shadow transition-transform duration-200 ${
                  showUploadProgress ? 'translate-x-5' : 'translate-x-0.5'
                } mt-0.5`}
              />
            </div>
          </div>
        </label>
      </div>

      {/* Preview Summary */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Benachrichtigungs-Übersicht
        </h3>
        <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Toast-Position:</span>
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {toastPositions.find(p => p.value === toastPosition)?.label}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Audio-Feedback:</span>
            <span className={`text-sm font-medium ${enableSounds ? 'text-green-600 dark:text-green-400' : 'text-gray-500'}`}>
              {enableSounds ? 'Aktiviert' : 'Deaktiviert'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Browser-Benachrichtigungen:</span>
            <span className={`text-sm font-medium ${enableBrowserNotifications ? 'text-green-600 dark:text-green-400' : 'text-gray-500'}`}>
              {enableBrowserNotifications ? 'Aktiviert' : 'Deaktiviert'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">Upload-Fortschritt:</span>
            <span className={`text-sm font-medium ${showUploadProgress ? 'text-green-600 dark:text-green-400' : 'text-gray-500'}`}>
              {showUploadProgress ? 'Sichtbar' : 'Ausgeblendet'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}