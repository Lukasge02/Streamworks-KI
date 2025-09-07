'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Settings, X, Zap, Brain, Database, Layers } from 'lucide-react'

interface AdminSettingsPanelProps {
  isOpen: boolean
  onClose: () => void
  confidenceThreshold: number
  setConfidenceThreshold: (value: number) => void
  topK: number
  setTopK: (value: number) => void
}

export const AdminSettingsPanel = ({
  isOpen,
  onClose,
  confidenceThreshold,
  setConfidenceThreshold,
  topK,
  setTopK
}: AdminSettingsPanelProps) => {
  const [advancedMode, setAdvancedMode] = useState(false)

  // Keyboard shortcut to open (Ctrl+Shift+A)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'A') {
        e.preventDefault()
        if (!isOpen) {
          // Only developers know this shortcut
          console.log('🔧 Admin Settings Panel opened')
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen])

  const confidenceDescription = (threshold: number) => {
    if (threshold >= 0.9) return 'Sehr streng - nur hochqualitative Antworten'
    if (threshold >= 0.8) return 'Streng - zuverlässige Antworten bevorzugt'
    if (threshold >= 0.7) return 'Ausgewogen - gute Balance zwischen Qualität und Verfügbarkeit'
    if (threshold >= 0.6) return 'Liberal - mehr Antworten, evtl. weniger genau'
    return 'Sehr liberal - alle verfügbaren Antworten'
  }

  const topKDescription = (k: number) => {
    if (k <= 3) return 'Fokussiert - nur die besten Quellen'
    if (k <= 6) return 'Standard - ausgewogene Quellenanzahl'
    if (k <= 10) return 'Umfassend - viele relevante Quellen'
    return 'Maximal - alle verfügbaren Quellen'
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-50"
            onClick={onClose}
          />
          
          {/* Panel */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white dark:bg-gray-800 rounded-xl shadow-2xl z-50 border border-gray-200 dark:border-gray-700"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Settings className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    RAG System Settings
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Erweiterte Konfiguration für Entwickler
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Confidence Threshold */}
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Brain className="w-4 h-4 text-blue-500" />
                  <label className="text-sm font-medium text-gray-900 dark:text-white">
                    Confidence Threshold
                  </label>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
                    {Math.round(confidenceThreshold * 100)}%
                  </span>
                </div>
                
                <input
                  type="range"
                  min="0.3"
                  max="0.95"
                  step="0.05"
                  value={confidenceThreshold}
                  onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider"
                />
                
                <div className="grid grid-cols-5 text-xs text-gray-500 dark:text-gray-400">
                  <span>30%</span>
                  <span>50%</span>
                  <span>70%</span>
                  <span>85%</span>
                  <span>95%</span>
                </div>
                
                <p className="text-xs text-gray-600 dark:text-gray-300 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  {confidenceDescription(confidenceThreshold)}
                </p>
              </div>

              {/* Top-K Sources */}
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Layers className="w-4 h-4 text-green-500" />
                  <label className="text-sm font-medium text-gray-900 dark:text-white">
                    Source Count (Top-K)
                  </label>
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                    {topK} Quellen
                  </span>
                </div>
                
                <input
                  type="range"
                  min="1"
                  max="20"
                  step="1"
                  value={topK}
                  onChange={(e) => setTopK(parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 slider"
                />
                
                <div className="grid grid-cols-4 text-xs text-gray-500 dark:text-gray-400">
                  <span>1</span>
                  <span>5</span>
                  <span>10</span>
                  <span>20</span>
                </div>
                
                <p className="text-xs text-gray-600 dark:text-gray-300 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  {topKDescription(topK)}
                </p>
              </div>

              {/* Advanced Mode Toggle */}
              <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <div className="flex items-center space-x-2">
                  <Zap className="w-4 h-4 text-yellow-600" />
                  <span className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
                    Advanced Mode
                  </span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={advancedMode}
                    onChange={(e) => setAdvancedMode(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-yellow-600"></div>
                </label>
              </div>

              {/* Advanced Settings */}
              <AnimatePresence>
                {advancedMode && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="space-y-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border-l-4 border-purple-500"
                  >
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white flex items-center">
                      <Database className="w-4 h-4 mr-2 text-purple-500" />
                      Advanced RAG Settings
                    </h3>
                    
                    <div className="text-xs text-gray-600 dark:text-gray-300 space-y-1">
                      <div>• Embedding Model: text-embedding-3-large</div>
                      <div>• Vector Dimensions: 3072</div>
                      <div>• LLM Model: gpt-4o-mini</div>
                      <div>• Chunk Size: 1000 tokens</div>
                      <div>• Reranking: Disabled</div>
                    </div>
                    
                    <div className="text-xs text-purple-600 dark:text-purple-400">
                      💡 Diese Einstellungen können in der Backend-Konfiguration angepasst werden
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700 rounded-b-xl">
              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Tastenkürzel: <kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-600 rounded text-xs font-mono">Ctrl+Shift+A</kbd>
                </div>
                <button
                  onClick={onClose}
                  className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Fertig
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}