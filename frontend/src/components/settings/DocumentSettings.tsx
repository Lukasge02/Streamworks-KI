'use client'

import { useSettings, SortOrder } from '@/hooks/useSettings'
import { Folder, Image, ArrowUpDown, Shield } from 'lucide-react'

export function DocumentSettings() {
  const { 
    defaultFolder,
    thumbnailSize,
    defaultSortOrder,
    autoBackup,
    updateSettings 
  } = useSettings()

  const thumbnailSizes = [
    { value: 'small', label: 'Klein', description: 'Kompakte Ansicht mit mehr Dokumenten' },
    { value: 'medium', label: 'Mittel', description: 'Ausgewogene Größe für gute Lesbarkeit' },
    { value: 'large', label: 'Groß', description: 'Große Vorschaubilder für bessere Übersicht' },
  ] as const

  const sortOrders = [
    { value: 'name', label: 'Name', description: 'Alphabetisch nach Dateinamen sortieren' },
    { value: 'date', label: 'Datum', description: 'Nach Upload-Datum sortieren (neueste zuerst)' },
    { value: 'size', label: 'Größe', description: 'Nach Dateigröße sortieren (größte zuerst)' },
    { value: 'type', label: 'Typ', description: 'Nach Dateityp gruppieren' },
  ] as const

  const mockFolders = [
    { id: 'none', name: 'Kein Standard-Ordner', description: 'Benutzer muss Ordner manuell auswählen' },
    { id: 'general', name: 'Allgemeine Dokumente', description: 'Für nicht kategorisierte Dokumente' },
    { id: 'contracts', name: 'Verträge', description: 'Rechtliche Dokumente und Verträge' },
    { id: 'reports', name: 'Berichte', description: 'Geschäftsberichte und Analysen' },
    { id: 'presentations', name: 'Präsentationen', description: 'PowerPoint und andere Präsentationen' },
  ]

  return (
    <div className="space-y-8">
      {/* Default Folder */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Folder className="w-5 h-5 mr-2" />
          Standard-Ordner für neue Dokumente
        </h3>
        <div className="space-y-2">
          {mockFolders.map((folder) => (
            <label
              key={folder.id}
              className={`flex items-center p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                (defaultFolder === folder.id) || (defaultFolder === null && folder.id === 'none')
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
              }`}
            >
              <input
                type="radio"
                name="defaultFolder"
                value={folder.id === 'none' ? '' : folder.id}
                checked={(defaultFolder === folder.id) || (defaultFolder === null && folder.id === 'none')}
                onChange={(e) => updateSettings({ defaultFolder: e.target.value || null })}
                className="sr-only"
              />
              <div className="flex-1">
                <div className="font-medium text-gray-900 dark:text-white">{folder.name}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">{folder.description}</div>
              </div>
              <div className={`w-4 h-4 rounded-full border-2 ${
                (defaultFolder === folder.id) || (defaultFolder === null && folder.id === 'none')
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-300 dark:border-gray-600'
              }`} />
            </label>
          ))}
        </div>
      </div>

      {/* Thumbnail Size */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Image className="w-5 h-5 mr-2" />
          Vorschaubild-Größe
        </h3>
        <div className="grid grid-cols-3 gap-3">
          {thumbnailSizes.map((size) => (
            <button
              key={size.value}
              onClick={() => updateSettings({ thumbnailSize: size.value })}
              className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                thumbnailSize === size.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
              }`}
            >
              <div className={`mx-auto mb-2 border-2 border-gray-400 dark:border-gray-500 ${
                size.value === 'small' ? 'w-6 h-6' : 
                size.value === 'medium' ? 'w-8 h-8' : 'w-10 h-10'
              }`} />
              <div className="text-sm font-medium">{size.label}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{size.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Default Sort Order */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <ArrowUpDown className="w-5 h-5 mr-2" />
          Standard-Sortierung
        </h3>
        <div className="space-y-2">
          {sortOrders.map((sort) => (
            <label
              key={sort.value}
              className={`flex items-center p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                defaultSortOrder === sort.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
              }`}
            >
              <input
                type="radio"
                name="defaultSortOrder"
                value={sort.value}
                checked={defaultSortOrder === sort.value}
                onChange={(e) => updateSettings({ defaultSortOrder: e.target.value as SortOrder })}
                className="sr-only"
              />
              <div className="flex-1">
                <div className="font-medium text-gray-900 dark:text-white">{sort.label}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">{sort.description}</div>
              </div>
              <div className={`w-4 h-4 rounded-full border-2 ${
                defaultSortOrder === sort.value
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-300 dark:border-gray-600'
              }`} />
            </label>
          ))}
        </div>
      </div>

      {/* Auto Backup */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
          <Shield className="w-5 h-5 mr-2" />
          Sicherung
        </h3>
        <label className="flex items-center justify-between p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 cursor-pointer">
          <div>
            <div className="font-medium text-gray-900 dark:text-white">Automatische Sicherung</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Erstellt automatisch Backups wichtiger Dokumente
            </div>
          </div>
          <div className="relative">
            <input
              type="checkbox"
              checked={autoBackup}
              onChange={(e) => updateSettings({ autoBackup: e.target.checked })}
              className="sr-only"
            />
            <div
              className={`w-11 h-6 rounded-full transition-colors duration-200 ${
                autoBackup ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
              }`}
            >
              <div
                className={`w-5 h-5 bg-white rounded-full shadow transition-transform duration-200 ${
                  autoBackup ? 'translate-x-5' : 'translate-x-0.5'
                } mt-0.5`}
              />
            </div>
          </div>
        </label>
        
        {autoBackup && (
          <div className="mt-4 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700">
            <div className="flex items-start">
              <Shield className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5 mr-2 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-green-800 dark:text-green-200">
                  Auto-Backup aktiviert
                </p>
                <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                  Dokumente werden täglich gesichert und für 30 Tage aufbewahrt.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Preview */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Vorschau der aktuellen Einstellungen
        </h3>
        <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Standard-Ordner:</span>
            <span className="text-gray-900 dark:text-white">
              {defaultFolder ? mockFolders.find(f => f.id === defaultFolder)?.name : 'Kein Standard-Ordner'}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Thumbnail-Größe:</span>
            <span className="text-gray-900 dark:text-white capitalize">{thumbnailSize}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Sortierung:</span>
            <span className="text-gray-900 dark:text-white">
              {sortOrders.find(s => s.value === defaultSortOrder)?.label}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Auto-Backup:</span>
            <span className={`font-medium ${autoBackup ? 'text-green-600 dark:text-green-400' : 'text-gray-500'}`}>
              {autoBackup ? 'Aktiviert' : 'Deaktiviert'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}