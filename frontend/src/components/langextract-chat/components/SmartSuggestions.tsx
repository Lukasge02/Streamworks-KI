/**
 * Smart Suggestions Component for LangExtract
 * Shows AI-powered suggestions and quick actions for parameter extraction
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
  MessageSquare,
  Copy,
  ExternalLink,
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-react'
import { toast } from 'sonner'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

// ================================
// TYPES
// ================================

interface SmartSuggestionsProps {
  onSuggestionClick?: (suggestion: string) => void
  sessionState?: 'loading' | 'initial' | 'active'
  suggestedQuestions?: string[]
  criticalMissing?: string[]
  completionPercentage?: number
  jobType?: string
  onQuestionClick?: (question: string) => void
  className?: string
}

// ================================
// EXAMPLE SUGGESTIONS BY JOB TYPE
// ================================

const EXAMPLE_SUGGESTIONS = {
  SAP: {
    basic: [
      "Ich brauche einen SAP Report Export aus System ZTV",
      "Erstelle einen automatischen Kalender Export",
      "Täglich um 08:00 soll Report ABC_REPORT ausgeführt werden"
    ],
    advanced: [
      "Export mit Mandant 100 und Sprache DE",
      "Benutzer SAP_USER soll den Report auf Agent AGENT_01 ausführen",
      "Parameter: DATUM von heute, FORMAT = XML"
    ]
  },
  FILE_TRANSFER: {
    basic: [
      "Übertrage XML-Dateien von Windows zu Linux",
      "Automatischer SFTP Transfer von C:\\temp nach /var/data",
      "Sichere Dateiübertragung mit Verschlüsselung"
    ],
    advanced: [
      "Quell-Agent: WIN_AGENT, Ziel-Agent: LINUX_AGENT",
      "Dateimuster: *.xml, Protokoll: SFTP",
      "Übertragung täglich um 02:00 mit Backup"
    ]
  },
  STANDARD: {
    basic: [
      "Führe Python-Skript täglich aus",
      "Automatische Datenverarbeitung per Batch",
      "Windows Service für Hintergrundaufgaben"
    ],
    advanced: [
      "Agent: BATCH_AGENT, Arbeitsverzeichnis: C:\\scripts",
      "Timeout: 3600 Sekunden, Wiederholungen: 3",
      "Umgebungsvariablen: ENV=prod, LOG_LEVEL=info"
    ]
  }
}

const CRITICAL_PARAMETER_HINTS = {
  stream_name: "Vergeben Sie einen eindeutigen, beschreibenden Namen",
  job_name: "Der Job-Name sollte die Funktion widerspiegeln",
  system_name: "Welches Zielsystem soll verwendet werden?",
  agent_name: "Auf welchem Agent soll der Job ausgeführt werden?",
  program: "Welches Programm oder Script soll ausgeführt werden?",
  source_path: "Von welchem Verzeichnis sollen Dateien übertragen werden?",
  target_path: "In welches Verzeichnis sollen Dateien übertragen werden?"
}

// ================================
// COMPONENT
// ================================

export default function SmartSuggestions({
  onSuggestionClick,
  sessionState = 'initial',
  suggestedQuestions = [],
  criticalMissing = [],
  completionPercentage = 0,
  jobType,
  onQuestionClick,
  className = ''
}: SmartSuggestionsProps) {

  const suggestions = jobType ? EXAMPLE_SUGGESTIONS[jobType as keyof typeof EXAMPLE_SUGGESTIONS] : null

  const handleExampleClick = (value: string) => {
    onSuggestionClick?.(value)
    toast.success('Beispiel eingefügt')
  }

  const handleQuestionClick = (question: string) => {
    onQuestionClick?.(question)
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
      className={`space-y-6 ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >

      {/* Critical Missing Parameters */}
      <AnimatePresence>
        {criticalMissing.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <Card className="border-red-200 bg-red-50">
              <div className="p-4">
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                  <h4 className="font-semibold text-red-900">Kritische Parameter fehlen</h4>
                  <Badge variant="destructive" className="text-xs">
                    {criticalMissing.length}
                  </Badge>
                </div>
                <div className="space-y-2">
                  {criticalMissing.map((param, index) => {
                    const hint = CRITICAL_PARAMETER_HINTS[param as keyof typeof CRITICAL_PARAMETER_HINTS]
                    return (
                      <motion.div
                        key={param}
                        className="flex items-start gap-2 p-2 bg-white rounded border border-red-200"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        <Target className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <span className="font-medium text-red-900 text-sm">
                            {param.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </span>
                          {hint && (
                            <p className="text-xs text-red-700 mt-1">{hint}</p>
                          )}
                        </div>
                      </motion.div>
                    )
                  })}
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* AI Suggested Questions */}
      <AnimatePresence>
        {suggestedQuestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <Card className="border-blue-200 bg-blue-50">
              <div className="p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="w-5 h-5 text-blue-600" />
                  <h4 className="font-semibold text-blue-900">KI-Vorschläge</h4>
                  <Badge variant="secondary" className="text-xs">
                    {suggestedQuestions.length}
                  </Badge>
                </div>
                <div className="space-y-2">
                  {suggestedQuestions.map((question, index) => (
                    <motion.button
                      key={index}
                      className="w-full text-left p-3 bg-white rounded-lg border border-blue-200 hover:border-blue-300 hover:shadow-sm transition-all group"
                      onClick={() => handleQuestionClick(question)}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <div className="flex items-start gap-2">
                        <MessageSquare className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-blue-900 flex-1">{question}</span>
                        <ArrowRight className="w-4 h-4 text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    </motion.button>
                  ))}
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Example Suggestions by Job Type */}
      {suggestions && (
        <Card>
          <div className="p-4">
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb className="w-5 h-5 text-yellow-600" />
              <h4 className="font-semibold text-gray-900">Beispiele für {jobType}</h4>
            </div>

            {/* Basic Examples */}
            <div className="mb-4">
              <h5 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                <Info className="w-3 h-3" />
                Grundlegende Beispiele
              </h5>
              <div className="space-y-2">
                {suggestions.basic.map((example, index) => (
                  <motion.button
                    key={index}
                    className="w-full text-left p-2 text-sm text-gray-700 bg-gray-50 rounded hover:bg-gray-100 transition-colors group"
                    onClick={() => handleExampleClick(example)}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex-1">{example}</span>
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Copy
                          className="w-3 h-3 text-gray-500 cursor-pointer hover:text-gray-700"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleCopyToClipboard(example)
                          }}
                        />
                        <ExternalLink className="w-3 h-3 text-gray-500" />
                      </div>
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Advanced Examples */}
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                <Zap className="w-3 h-3" />
                Erweiterte Beispiele
              </h5>
              <div className="space-y-2">
                {suggestions.advanced.map((example, index) => (
                  <motion.button
                    key={index}
                    className="w-full text-left p-2 text-sm text-gray-700 bg-gray-50 rounded hover:bg-gray-100 transition-colors group"
                    onClick={() => handleExampleClick(example)}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: (suggestions.basic.length + index) * 0.05 }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex-1">{example}</span>
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Copy
                          className="w-3 h-3 text-gray-500 cursor-pointer hover:text-gray-700"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleCopyToClipboard(example)
                          }}
                        />
                        <ExternalLink className="w-3 h-3 text-gray-500" />
                      </div>
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Progress Status */}
      <Card className="bg-gradient-to-r from-emerald-50 to-blue-50">
        <div className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {completionPercentage >= 80 ? (
                <CheckCircle className="w-5 h-5 text-emerald-600" />
              ) : completionPercentage >= 40 ? (
                <Clock className="w-5 h-5 text-yellow-600" />
              ) : (
                <Target className="w-5 h-5 text-gray-500" />
              )}
              <span className="font-medium text-gray-900">
                Fortschritt: {completionPercentage}%
              </span>
            </div>
            <Badge
              variant={completionPercentage >= 80 ? "default" : "secondary"}
              className="text-xs"
            >
              {completionPercentage >= 80 ? 'Fast vollständig' :
               completionPercentage >= 40 ? 'In Bearbeitung' : 'Gestartet'}
            </Badge>
          </div>

          <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
            <motion.div
              className={`h-2 rounded-full ${
                completionPercentage >= 80 ? 'bg-emerald-500' :
                completionPercentage >= 40 ? 'bg-yellow-500' : 'bg-gray-400'
              }`}
              initial={{ width: 0 }}
              animate={{ width: `${completionPercentage}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          </div>

          {completionPercentage < 100 && (
            <p className="text-xs text-gray-600 mt-2">
              {completionPercentage >= 80
                ? 'Nur noch wenige Parameter fehlen'
                : completionPercentage >= 40
                ? 'Guter Fortschritt, weiter so!'
                : 'Beschreiben Sie Ihren gewünschten Stream detaillierter'
              }
            </p>
          )}
        </div>
      </Card>

    </motion.div>
  )
}