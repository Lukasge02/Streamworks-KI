/**
 * Stream Type Selector Component
 * Allows users to select SAP, File Transfer, or Standard stream types
 */

'use client'

import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Database,
  Server,
  FileCode,
  ArrowRight,
  Check,
  Sparkles
} from 'lucide-react'

// ================================
// TYPES
// ================================

export type StreamType = 'SAP' | 'FILE_TRANSFER' | 'STANDARD'

interface StreamTypeOption {
  id: StreamType
  label: string
  description: string
  features: string[]
  icon: React.ComponentType<{ className?: string }>
  color: string
  examples: string[]
}

interface StreamTypeSelectorProps {
  selectedType: StreamType | null
  onSelect: (type: StreamType) => void
  isVisible: boolean
  className?: string
}

// ================================
// STREAM TYPE DEFINITIONS
// ================================

const STREAM_TYPES: StreamTypeOption[] = [
  {
    id: 'SAP',
    label: 'SAP Integration',
    description: 'Datenexport und -import aus SAP-Systemen',
    features: [
      'jexa4S Integration',
      'SAP-Systeme (ZTV, PA1, PRD)',
      'Mandanten-Verwaltung',
      'Fabrikkalender Export',
      'Report-Ausführung'
    ],
    icon: Database,
    color: 'blue',
    examples: [
      'Kalender aus SAP exportieren',
      'jexa4S Report ausführen',
      'SAP-Daten übertragen'
    ]
  },
  {
    id: 'FILE_TRANSFER',
    label: 'File Transfer',
    description: 'Dateien zwischen Systemen übertragen',
    features: [
      'Agent-zu-Agent Transfer',
      'FTP/SFTP/RSYNC',
      'Dateifilterung',
      'Plattform-übergreifend',
      'Archivierung'
    ],
    icon: Server,
    color: 'green',
    examples: [
      'Dateien kopieren/verschieben',
      'Backup-Synchronisation',
      'Cross-Platform Transfer'
    ]
  },
  {
    id: 'STANDARD',
    label: 'Standard Job',
    description: 'Allgemeine Skript- und Befehlsausführung',
    features: [
      'Python/Batch/Shell Scripts',
      'Flexible Parameter',
      'Multi-Platform',
      'Custom Commands',
      'Environment Setup'
    ],
    icon: FileCode,
    color: 'purple',
    examples: [
      'Python Skripts ausführen',
      'Batch-Verarbeitung',
      'Custom Workflows'
    ]
  }
]

// ================================
// COMPONENT
// ================================

export default function StreamTypeSelector({
  selectedType,
  onSelect,
  isVisible,
  className = ''
}: StreamTypeSelectorProps) {
  if (!isVisible) return null

  return (
    <AnimatePresence>
      <motion.div
        className={`space-y-4 ${className}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
      >
        {/* Compact Header */}
        <motion.div
          className="text-center space-y-1"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-lg font-medium text-gray-900">
            Stream-Typ wählen
          </h2>
        </motion.div>

        {/* Compact Stream Type Cards */}
        <div className="grid grid-cols-3 gap-3">
          {STREAM_TYPES.map((streamType, index) => {
            const IconComponent = streamType.icon
            const isSelected = selectedType === streamType.id

            return (
              <motion.button
                key={streamType.id}
                className={`
                  relative p-4 text-center rounded-lg border transition-all duration-300
                  hover:shadow-md group
                  ${isSelected
                    ? `border-${streamType.color}-500 bg-${streamType.color}-50 shadow-md`
                    : 'border-gray-200 bg-white hover:border-gray-300'
                  }
                `}
                onClick={() => onSelect(streamType.id)}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                whileTap={{ scale: 0.95 }}
              >
                {/* Selection Indicator */}
                {isSelected && (
                  <motion.div
                    className={`absolute top-2 right-2 p-0.5 bg-${streamType.color}-500 text-white rounded-full`}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.1 }}
                  >
                    <Check className="w-3 h-3" />
                  </motion.div>
                )}

                {/* Icon */}
                <div className={`
                  inline-flex p-2 rounded-lg mb-2 transition-colors
                  ${isSelected
                    ? `bg-${streamType.color}-100 text-${streamType.color}-600`
                    : `bg-gray-100 text-gray-600 group-hover:bg-${streamType.color}-100 group-hover:text-${streamType.color}-600`
                  }
                `}>
                  <IconComponent className="w-5 h-5" />
                </div>

                {/* Title */}
                <h3 className={`
                  font-semibold text-sm mb-1 transition-colors
                  ${isSelected ? `text-${streamType.color}-900` : 'text-gray-900'}
                `}>
                  {streamType.label}
                </h3>
                <p className="text-gray-600 text-xs">
                  {streamType.description}
                </p>
              </motion.button>
            )
          })}
        </div>

        {/* Compact Help Text */}
        <motion.div
          className="text-center text-sm text-gray-500 py-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          Nicht sicher? Beschreiben Sie einfach, was Sie vorhaben
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}