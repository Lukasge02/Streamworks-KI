'use client'

import { useState, Fragment } from 'react'
import { Dialog, Transition, Tab } from '@headlessui/react'
import { motion } from 'framer-motion'
import { 
  X, 
  Palette, 
  Settings, 
  FolderOpen, 
  Bell, 
  Globe, 
  Database,
  Download,
  Upload,
  RotateCcw
} from 'lucide-react'
import { useSettings } from '@/hooks/useSettings'
import { ThemeSettings } from './ThemeSettings'
import { SystemSettings } from './SystemSettings'
import { DocumentSettings } from './DocumentSettings' 
import { NotificationSettings } from './NotificationSettings'
import { LocalizationSettings } from './LocalizationSettings'
import { DataSettings } from './DataSettings'

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
}

const tabs = [
  { id: 'theme', name: 'Erscheinungsbild', icon: Palette },
  { id: 'system', name: 'System', icon: Settings },
  { id: 'documents', name: 'Dokumente', icon: FolderOpen },
  { id: 'notifications', name: 'Benachrichtigungen', icon: Bell },
  { id: 'localization', name: 'Sprache & Region', icon: Globe },
  { id: 'data', name: 'Daten & Export', icon: Database },
]

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [selectedTab, setSelectedTab] = useState(0)
  const { resetSettings, exportSettings, importSettings } = useSettings()
  const [showResetConfirm, setShowResetConfirm] = useState(false)

  const handleExport = () => {
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

  const handleImport = () => {
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
          } catch (error) {
            console.error('Import failed:', error)
          }
        }
        reader.readAsText(file)
      }
    }
    input.click()
  }

  const handleReset = () => {
    resetSettings()
    setShowResetConfirm(false)
  }

  const renderTabContent = () => {
    switch (tabs[selectedTab].id) {
      case 'theme':
        return <ThemeSettings />
      case 'system':
        return <SystemSettings />
      case 'documents':
        return <DocumentSettings />
      case 'notifications':
        return <NotificationSettings />
      case 'localization':
        return <LocalizationSettings />
      case 'data':
        return <DataSettings />
      default:
        return <ThemeSettings />
    }
  }

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white dark:bg-gray-800 shadow-xl transition-all">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  {/* Header */}
                  <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                    <div>
                      <Dialog.Title className="text-xl font-bold text-gray-900 dark:text-white">
                        Einstellungen
                      </Dialog.Title>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        Passe Streamworks nach deinen Wünschen an
                      </p>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={handleExport}
                        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title="Einstellungen exportieren"
                      >
                        <Download className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                      </button>
                      
                      <button
                        onClick={handleImport}
                        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title="Einstellungen importieren"
                      >
                        <Upload className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                      </button>
                      
                      <button
                        onClick={() => setShowResetConfirm(true)}
                        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title="Alle Einstellungen zurücksetzen"
                      >
                        <RotateCcw className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                      </button>
                      
                      <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                      >
                        <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                      </button>
                    </div>
                  </div>

                  <div className="flex">
                    {/* Tab Navigation */}
                    <div className="w-64 p-4 border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                      <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
                        <Tab.List className="space-y-1">
                          {tabs.map((tab, index) => {
                            const Icon = tab.icon
                            return (
                              <Tab key={tab.id} as={Fragment}>
                                {({ selected }) => (
                                  <button
                                    className={`w-full flex items-center space-x-3 px-3 py-3 rounded-lg text-left transition-all duration-200 ${
                                      selected
                                        ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium'
                                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-200'
                                    }`}
                                  >
                                    <Icon className={`w-5 h-5 ${
                                      selected ? 'text-blue-600 dark:text-blue-400' : ''
                                    }`} />
                                    <span className="text-sm">{tab.name}</span>
                                  </button>
                                )}
                              </Tab>
                            )
                          })}
                        </Tab.List>
                      </Tab.Group>
                    </div>

                    {/* Tab Content */}
                    <div className="flex-1 p-6">
                      <motion.div
                        key={selectedTab}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.2 }}
                        className="max-h-96 overflow-y-auto"
                      >
                        {renderTabContent()}
                      </motion.div>
                    </div>
                  </div>

                  {/* Reset Confirmation Dialog */}
                  <Transition appear show={showResetConfirm} as={Fragment}>
                    <Dialog as="div" className="relative z-50" onClose={() => setShowResetConfirm(false)}>
                      <Transition.Child
                        as={Fragment}
                        enter="ease-out duration-300"
                        enterFrom="opacity-0"
                        enterTo="opacity-100"
                        leave="ease-in duration-200"
                        leaveFrom="opacity-100"
                        leaveTo="opacity-0"
                      >
                        <div className="fixed inset-0 bg-black/25" />
                      </Transition.Child>

                      <div className="fixed inset-0 overflow-y-auto">
                        <div className="flex min-h-full items-center justify-center p-4">
                          <Transition.Child
                            as={Fragment}
                            enter="ease-out duration-300"
                            enterFrom="opacity-0 scale-95"
                            enterTo="opacity-100 scale-100"
                            leave="ease-in duration-200"
                            leaveFrom="opacity-100 scale-100"
                            leaveTo="opacity-0 scale-95"
                          >
                            <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-6 text-left align-middle shadow-xl transition-all">
                              <Dialog.Title className="text-lg font-medium text-gray-900 dark:text-white">
                                Einstellungen zurücksetzen?
                              </Dialog.Title>
                              <div className="mt-2">
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                  Alle Einstellungen werden auf die Standardwerte zurückgesetzt. Diese Aktion kann nicht rückgängig gemacht werden.
                                </p>
                              </div>

                              <div className="mt-4 flex justify-end space-x-3">
                                <button
                                  onClick={() => setShowResetConfirm(false)}
                                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                                >
                                  Abbrechen
                                </button>
                                <button
                                  onClick={handleReset}
                                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
                                >
                                  Zurücksetzen
                                </button>
                              </div>
                            </Dialog.Panel>
                          </Transition.Child>
                        </div>
                      </div>
                    </Dialog>
                  </Transition>
                </motion.div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}