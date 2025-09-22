/**
 * Smart Suggestions Component
 * Shows AI-powered suggestions and quick actions
 */

'use client'

import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Lightbulb,
  ArrowRight,
  Sparkles,
  Clock,
  Target,
  Zap,
  CheckCircle,
  Info,
  AlertTriangle,
  Copy
} from 'lucide-react'
import { toast } from 'sonner'

// ================================
// TYPES
// ================================

interface SmartSuggestionsProps {
  suggestions: string[]
  streamType?: 'SAP' | 'FILE_TRANSFER' | 'STANDARD' | null
  nextParameter?: string
  completionPercentage: number
  onSuggestionClick?: (suggestion: string) => void
  className?: string
}

interface ExampleSuggestion {
  text: string
  category: string
}

// ================================
// EXAMPLE SUGGESTIONS BY STREAM TYPE
// ================================

const EXAMPLE_SUGGESTIONS = {
  SAP: [
    "Erstelle einen SAP Kalender Export von ZTV nach PA1",
    "Ich brauche einen automatischen Report-Export aus SAP",
    "Erstelle einen täglichen Datenexport mit Mandant 100"
  ],
  FILE_TRANSFER: [
    "Übertrage XML-Dateien von Windows zu Linux per SFTP",
    "Automatischer Transfer von C:\\temp zu /var/export",
    "Sichere Dateiübertragung mit Verschlüsselung"
  ],
  STANDARD: [
    "Führe ein Python-Skript täglich um 08:00 aus",
    "Automatische Datenverarbeitung mit Batch-Job",
    "Erstelle einen Windows-Service für Hintergrundaufgaben"
  ]
}

// ================================
// COMPONENT
// ================================

export default function SmartSuggestions({
  suggestions = [],
  streamType,
  nextParameter,
  completionPercentage,
  onSuggestionClick,
  className = ''
}: SmartSuggestionsProps) {
  const exampleSuggestions = streamType ? EXAMPLE_SUGGESTIONS[streamType] || [] : []

  const handleExampleClick = (value: string) => {
    onSuggestionClick?.(value)
    toast.success(`Beispiel eingefügt: ${value}`)
  }

  const handleCopyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      toast.success('In Zwischenablage kopiert!')
    } catch (error) {
      toast.error('Kopieren fehlgeschlagen')
    }
  }

  return (
    <motion.div
      className={`space-y-4 ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >

      {/* AI Suggestions */}
      <AnimatePresence>
        {suggestions.length > 0 && (
          <motion.div
            className="bg-white border border-gray-200 rounded-lg overflow-hidden"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="bg-yellow-50 border-b border-yellow-200 p-3">
              <div className="flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-yellow-600" />
                <h4 className="font-medium text-yellow-900">KI-Hinweise</h4>
              </div>
            </div>
            <div className="p-3 space-y-2">
              {suggestions.map((suggestion, index) => (
                <motion.div
                  key={index}
                  className="flex items-start gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer transition-colors"
                  onClick={() => toast.info(suggestion)}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{suggestion}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>


    </motion.div>
  )
}