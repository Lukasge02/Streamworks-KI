/**
 * Source Grounding Component for LangExtract
 * Shows the source text and confidence for extracted parameters
 */

'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Target,
  ChevronDown,
  ChevronRight,
  Quote,
  Zap,
  AlertCircle,
  CheckCircle,
  Info,
  FileText,
  Eye,
  Link
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'

// ================================
// TYPES
// ================================

interface SourceGroundingItem {
  parameter: string
  source: string
  confidence: number
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  extractedParameters?: Record<string, any>
  sourceGrounding?: SourceGroundingItem[]
  timestamp: string
}

interface SourceGroundingProps {
  messages: Message[]
  streamParameters: Record<string, any>
  jobParameters: Record<string, any>
  className?: string
}

interface GroupedGrounding {
  [parameter: string]: SourceGroundingItem[]
}

// ================================
// COMPONENT
// ================================

export default function SourceGrounding({
  messages = [],
  streamParameters = {},
  jobParameters = {},
  className = ''
}: SourceGroundingProps) {

  // Extract source grounding from messages
  const sourceGrounding: SourceGroundingItem[] = messages
    .filter(msg => msg.role === 'assistant' && msg.sourceGrounding)
    .flatMap(msg => msg.sourceGrounding || [])

  // Get the latest message for context
  const currentMessage = messages[messages.length - 1]?.content

  const [expandedParameters, setExpandedParameters] = useState<Set<string>>(new Set())
  const [showLowConfidence, setShowLowConfidence] = useState(false)
  const [selectedMessage, setSelectedMessage] = useState<number | null>(null)

  // Get grounding for selected message or all messages
  const relevantGrounding = selectedMessage !== null && messages[selectedMessage]?.sourceGrounding
    ? messages[selectedMessage].sourceGrounding || []
    : sourceGrounding

  // Group by parameter
  const groupedGrounding: GroupedGrounding = relevantGrounding.reduce((acc, item) => {
    if (!acc[item.parameter]) {
      acc[item.parameter] = []
    }
    acc[item.parameter].push(item)
    return acc
  }, {} as GroupedGrounding)

  // Filter by confidence if needed
  const filteredGrounding = Object.entries(groupedGrounding).reduce((acc, [param, items]) => {
    const filteredItems = showLowConfidence
      ? items
      : items.filter(item => item.confidence >= 0.5)

    if (filteredItems.length > 0) {
      acc[param] = filteredItems.sort((a, b) => b.confidence - a.confidence)
    }
    return acc
  }, {} as GroupedGrounding)

  const toggleParameter = (parameter: string) => {
    setExpandedParameters(prev => {
      const newSet = new Set(prev)
      if (newSet.has(parameter)) {
        newSet.delete(parameter)
      } else {
        newSet.add(parameter)
      }
      return newSet
    })
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'emerald'
    if (confidence >= 0.6) return 'yellow'
    return 'red'
  }

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 0.8) return CheckCircle
    if (confidence >= 0.6) return AlertCircle
    return AlertCircle
  }

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'Hoch'
    if (confidence >= 0.6) return 'Mittel'
    return 'Niedrig'
  }

  const highlightSourceInMessage = (source: string, message: string) => {
    if (!message || !source) return message

    const sourceIndex = message.toLowerCase().indexOf(source.toLowerCase())
    if (sourceIndex === -1) return message

    const before = message.substring(0, sourceIndex)
    const highlighted = message.substring(sourceIndex, sourceIndex + source.length)
    const after = message.substring(sourceIndex + source.length)

    return (
      <>
        {before}
        <mark className="bg-yellow-200 px-1 rounded">{highlighted}</mark>
        {after}
      </>
    )
  }

  if (sourceGrounding.length === 0) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="text-center">
          <Search className="w-8 h-8 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">Keine Quellenangaben verfügbar</p>
          <p className="text-gray-400 text-sm mt-1">
            Parameter werden in zukünftigen Nachrichten mit Quellen verknüpft
          </p>
        </div>
      </Card>
    )
  }

  const totalParameters = Object.keys(filteredGrounding).length
  const highConfidenceCount = Object.values(filteredGrounding)
    .flat()
    .filter(item => item.confidence >= 0.8).length
  const lowConfidenceCount = sourceGrounding.filter(item => item.confidence < 0.5).length

  return (
    <motion.div
      className={`space-y-4 ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <Card>
        <div className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <Target className="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Quellenangaben</h3>
                <p className="text-sm text-gray-600">
                  Verknüpfung zwischen Parametern und Eingabe-Text
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">
                {totalParameters} Parameter
              </Badge>
              <Badge variant="default" className="text-xs">
                {highConfidenceCount} sicher
              </Badge>
              {lowConfidenceCount > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowLowConfidence(!showLowConfidence)}
                  className="h-6 text-xs"
                >
                  {showLowConfidence ? 'Unsichere ausblenden' : `+${lowConfidenceCount} unsichere`}
                </Button>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Message Selector */}
      {messages.length > 0 && (
        <Card className="bg-blue-50 border-blue-200">
          <div className="p-4">
            <div className="flex items-start gap-2 mb-3">
              <FileText className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <h4 className="font-medium text-blue-900">Nachrichten mit Quellenangaben</h4>
            </div>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {messages
                .map((msg, index) => ({ msg, index }))
                .filter(({ msg }) => msg.role === 'assistant' && msg.sourceGrounding && msg.sourceGrounding.length > 0)
                .map(({ msg, index }) => (
                  <button
                    key={index}
                    className={`w-full text-left p-2 rounded border text-xs transition-colors ${
                      selectedMessage === index
                        ? 'bg-blue-100 border-blue-300'
                        : 'bg-white border-blue-200 hover:bg-blue-50'
                    }`}
                    onClick={() => setSelectedMessage(selectedMessage === index ? null : index)}
                  >
                    <div className="font-medium text-blue-900 mb-1">
                      Nachricht #{index + 1} - {msg.sourceGrounding?.length || 0} Quellen
                    </div>
                    <div className="text-blue-700 truncate">
                      {msg.content.substring(0, 80)}...
                    </div>
                  </button>
                ))
              }
            </div>
          </div>
        </Card>
      )}

      {/* Current Message Context */}
      {selectedMessage !== null && messages[selectedMessage] && (
        <Card className="bg-gray-50 border-gray-200">
          <div className="p-4">
            <div className="flex items-start gap-2 mb-2">
              <Quote className="w-4 h-4 text-gray-600 mt-0.5 flex-shrink-0" />
              <h4 className="font-medium text-gray-900">Ausgewählte Nachricht</h4>
            </div>
            <div className="text-sm text-gray-800 bg-white p-3 rounded border border-gray-200">
              {messages[selectedMessage].content}
            </div>
          </div>
        </Card>
      )}

      {/* Grounding Items */}
      <div className="space-y-3">
        <AnimatePresence>
          {Object.entries(filteredGrounding).map(([parameter, items], index) => {
            const isExpanded = expandedParameters.has(parameter)
            const bestConfidence = Math.max(...items.map(item => item.confidence))
            const ConfidenceIcon = getConfidenceIcon(bestConfidence)
            const confidenceColor = getConfidenceColor(bestConfidence)

            return (
              <motion.div
                key={parameter}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="overflow-hidden">
                  <Collapsible
                    open={isExpanded}
                    onOpenChange={() => toggleParameter(parameter)}
                  >
                    <CollapsibleTrigger asChild>
                      <Button
                        variant="ghost"
                        className="w-full h-auto p-4 justify-start hover:bg-gray-50"
                      >
                        <div className="flex items-center gap-3 w-full">
                          <div className="flex items-center gap-2">
                            {isExpanded ? (
                              <ChevronDown className="w-4 h-4 text-gray-500" />
                            ) : (
                              <ChevronRight className="w-4 h-4 text-gray-500" />
                            )}
                            <ConfidenceIcon className={`w-4 h-4 text-${confidenceColor}-600`} />
                          </div>

                          <div className="flex-1 text-left">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-gray-900">
                                {parameter.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </span>
                              <Badge
                                variant={confidenceColor === 'emerald' ? 'default' : 'secondary'}
                                className="text-xs"
                              >
                                {getConfidenceLabel(bestConfidence)} ({Math.round(bestConfidence * 100)}%)
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-600 mt-1">
                              {items.length} Quellenangabe{items.length !== 1 ? 'n' : ''}
                            </p>
                          </div>

                          <Eye className="w-4 h-4 text-gray-400" />
                        </div>
                      </Button>
                    </CollapsibleTrigger>

                    <CollapsibleContent>
                      <div className="border-t border-gray-200 p-4 space-y-3">
                        {items.map((item, itemIndex) => {
                          const ItemConfidenceIcon = getConfidenceIcon(item.confidence)
                          const itemColor = getConfidenceColor(item.confidence)

                          return (
                            <motion.div
                              key={itemIndex}
                              className={`p-3 rounded-lg border-2 border-${itemColor}-200 bg-${itemColor}-50`}
                              initial={{ opacity: 0, scale: 0.95 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ delay: itemIndex * 0.05 }}
                            >
                              <div className="flex items-start gap-3">
                                <Quote className={`w-4 h-4 text-${itemColor}-600 mt-0.5 flex-shrink-0`} />
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    <ItemConfidenceIcon className={`w-3 h-3 text-${itemColor}-600`} />
                                    <span className={`text-xs font-medium text-${itemColor}-800`}>
                                      Vertrauen: {Math.round(item.confidence * 100)}%
                                    </span>
                                  </div>

                                  <blockquote className={`text-sm text-${itemColor}-900 bg-white p-2 rounded border border-${itemColor}-200 italic`}>
                                    "{item.source}"
                                  </blockquote>

                                  {currentMessage && (
                                    <div className="mt-2">
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        className="h-auto p-1 text-xs"
                                        onClick={(e) => {
                                          e.stopPropagation()
                                          // Could implement scroll to source in message
                                        }}
                                      >
                                        <Link className="w-3 h-3 mr-1" />
                                        In Nachricht anzeigen
                                      </Button>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </motion.div>
                          )
                        })}
                      </div>
                    </CollapsibleContent>
                  </Collapsible>
                </Card>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>

      {/* Summary Footer */}
      <Card className="bg-gray-50">
        <div className="p-4">
          <div className="flex justify-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-emerald-500 rounded-full"></div>
              <span className="text-gray-600">Hohe Sicherheit</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span className="text-gray-600">Mittlere Sicherheit</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-gray-600">Niedrige Sicherheit</span>
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}