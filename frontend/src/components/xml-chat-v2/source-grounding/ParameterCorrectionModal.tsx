/**
 * Parameter Correction Modal
 * Interaktives Modal für Source-Grounded Parameter-Korrekturen
 */

'use client'

import React, { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X,
  Save,
  Undo,
  AlertTriangle,
  CheckCircle,
  Eye,
  MapPin,
  Target,
  Type,
  Hash,
  ToggleLeft,
  Calendar,
  List,
  FileText,
  Lightbulb,
  Zap
} from 'lucide-react'

// Types
interface SourceGroundedParameter {
  name: string
  value: any
  confidence: number
  source_text: string
  character_offsets: [number, number]
  scope: 'stream' | 'job'
  data_type: string
  extraction_method: 'langextract' | 'unified' | 'hybrid'
  user_confirmed: boolean
  tooltip_info?: string
}

interface ParameterCorrectionModalProps {
  isOpen: boolean
  parameter: SourceGroundedParameter | null
  fullText: string
  onClose: () => void
  onSave: (parameterName: string, newValue: any, reason?: string) => void
  onCancel: () => void
  suggestions?: string[]
}

interface ValidationResult {
  isValid: boolean
  errors: string[]
  warnings: string[]
}

// Data type input components
const StringInput: React.FC<{
  value: string
  onChange: (value: string) => void
  placeholder?: string
  suggestions?: string[]
}> = ({ value, onChange, placeholder, suggestions = [] }) => {
  const [showSuggestions, setShowSuggestions] = useState(false)

  return (
    <div className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        onFocus={() => setShowSuggestions(true)}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
      />

      {/* Suggestions Dropdown */}
      <AnimatePresence>
        {showSuggestions && suggestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-40 overflow-y-auto"
          >
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => {
                  onChange(suggestion)
                  setShowSuggestions(false)
                }}
                className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

const NumberInput: React.FC<{
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  step?: number
}> = ({ value, onChange, min, max, step = 1 }) => (
  <input
    type="number"
    value={value}
    onChange={(e) => onChange(Number(e.target.value))}
    min={min}
    max={max}
    step={step}
    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  />
)

const BooleanInput: React.FC<{
  value: boolean
  onChange: (value: boolean) => void
}> = ({ value, onChange }) => (
  <div className="flex items-center gap-4">
    <button
      onClick={() => onChange(true)}
      className={`
        flex items-center gap-2 px-4 py-3 rounded-lg border-2 transition-all
        ${value
          ? 'border-green-500 bg-green-50 text-green-700'
          : 'border-gray-300 bg-white text-gray-600 hover:border-gray-400'
        }
      `}
    >
      <CheckCircle className="w-5 h-5" />
      Ja / True
    </button>
    <button
      onClick={() => onChange(false)}
      className={`
        flex items-center gap-2 px-4 py-3 rounded-lg border-2 transition-all
        ${!value
          ? 'border-red-500 bg-red-50 text-red-700'
          : 'border-gray-300 bg-white text-gray-600 hover:border-gray-400'
        }
      `}
    >
      <X className="w-5 h-5" />
      Nein / False
    </button>
  </div>
)

const EnumInput: React.FC<{
  value: string
  onChange: (value: string) => void
  options: string[]
}> = ({ value, onChange, options }) => (
  <select
    value={value}
    onChange={(e) => onChange(e.target.value)}
    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  >
    {options.map((option) => (
      <option key={option} value={option}>
        {option}
      </option>
    ))}
  </select>
)

// Main Modal Component
const ParameterCorrectionModal: React.FC<ParameterCorrectionModalProps> = ({
  isOpen,
  parameter,
  fullText,
  onClose,
  onSave,
  onCancel,
  suggestions = []
}) => {
  const [editedValue, setEditedValue] = useState<any>(null)
  const [correctionReason, setCorrectionReason] = useState('')
  const [validationResult, setValidationResult] = useState<ValidationResult>({
    isValid: true,
    errors: [],
    warnings: []
  })

  // Reset state when parameter changes
  useEffect(() => {
    if (parameter) {
      setEditedValue(parameter.value)
      setCorrectionReason('')
      setValidationResult({ isValid: true, errors: [], warnings: [] })
    }
  }, [parameter])

  // Generate context preview
  const contextPreview = useMemo(() => {
    if (!parameter || !fullText) return null

    const [start, end] = parameter.character_offsets
    const contextStart = Math.max(0, start - 30)
    const contextEnd = Math.min(fullText.length, end + 30)
    const preview = fullText.slice(contextStart, contextEnd)

    return {
      before: preview.slice(0, start - contextStart),
      highlighted: preview.slice(start - contextStart, end - contextStart),
      after: preview.slice(end - contextStart)
    }
  }, [parameter, fullText])

  // Validate the edited value
  const validateValue = (value: any): ValidationResult => {
    const errors: string[] = []
    const warnings: string[] = []

    if (!parameter) return { isValid: true, errors, warnings }

    // Type validation
    switch (parameter.data_type) {
      case 'integer':
        if (isNaN(Number(value)) || !Number.isInteger(Number(value))) {
          errors.push('Wert muss eine ganze Zahl sein')
        }
        break
      case 'number':
        if (isNaN(Number(value))) {
          errors.push('Wert muss eine Nummer sein')
        }
        break
      case 'boolean':
        if (typeof value !== 'boolean') {
          errors.push('Wert muss true oder false sein')
        }
        break
      case 'string':
        if (typeof value !== 'string') {
          warnings.push('Wert wird als String behandelt')
        }
        break
    }

    // Required field validation
    if (!value && value !== 0 && value !== false) {
      if (parameter.scope === 'stream') {
        errors.push('Stream-Parameter dürfen nicht leer sein')
      } else {
        warnings.push('Job-Parameter sollte einen Wert haben')
      }
    }

    // Length validation for strings
    if (typeof value === 'string') {
      if (value.length > 500) {
        warnings.push('Sehr langer Wert - überprüfen Sie die Korrektheit')
      }
      if (parameter.name.includes('Name') && value.length > 50) {
        warnings.push('Name-Parameter sollten kürzer als 50 Zeichen sein')
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    }
  }

  // Update validation when value changes
  useEffect(() => {
    if (editedValue !== null) {
      setValidationResult(validateValue(editedValue))
    }
  }, [editedValue, parameter])

  // Get appropriate input component based on data type
  const renderValueInput = () => {
    if (!parameter) return null

    const commonProps = {
      value: editedValue,
      onChange: setEditedValue
    }

    switch (parameter.data_type) {
      case 'integer':
        return <NumberInput {...commonProps} step={1} />
      case 'number':
        return <NumberInput {...commonProps} step={0.1} />
      case 'boolean':
        return <BooleanInput {...commonProps} />
      case 'enum':
        // In a real implementation, you'd get enum options from schema
        const enumOptions = ['Option1', 'Option2', 'Option3']
        return <EnumInput {...commonProps} options={enumOptions} />
      default:
        return (
          <StringInput
            {...commonProps}
            placeholder={`Neuer Wert für ${parameter.name}...`}
            suggestions={suggestions}
          />
        )
    }
  }

  const getDataTypeIcon = (dataType: string) => {
    switch (dataType) {
      case 'string': return Type
      case 'integer':
      case 'number': return Hash
      case 'boolean': return ToggleLeft
      case 'enum': return List
      case 'date': return Calendar
      default: return FileText
    }
  }

  const handleSave = () => {
    if (parameter && validationResult.isValid) {
      onSave(parameter.name, editedValue, correctionReason || undefined)
      onClose()
    }
  }

  const hasChanges = editedValue !== parameter?.value

  if (!isOpen || !parameter) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={(e) => e.target === e.currentTarget && onClose()}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        >
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className={`
                  p-3 rounded-xl
                  ${parameter.scope === 'stream'
                    ? 'bg-blue-100 text-blue-600'
                    : 'bg-purple-100 text-purple-600'
                  }
                `}>
                  <Target className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Parameter bearbeiten</h2>
                  <p className="text-gray-600 mt-1">
                    Korrigieren Sie den extrahierten Wert für bessere Genauigkeit
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Parameter Info */}
            <div className="bg-gray-50 p-4 rounded-xl">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900">{parameter.name}</h3>
                <div className="flex items-center gap-2">
                  <span className={`
                    px-3 py-1 rounded-full text-sm font-medium
                    ${parameter.scope === 'stream'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-purple-100 text-purple-800'
                    }
                  `}>
                    {parameter.scope}
                  </span>
                  <div className="flex items-center gap-1 text-gray-500">
                    {React.createElement(getDataTypeIcon(parameter.data_type), { className: "w-4 h-4" })}
                    <span className="text-sm">{parameter.data_type}</span>
                  </div>
                </div>
              </div>

              {/* Current Value */}
              <div className="mb-3">
                <div className="text-sm text-gray-600 mb-1">Aktueller Wert:</div>
                <div className="font-mono text-sm bg-white p-2 rounded border">
                  {typeof parameter.value === 'object'
                    ? JSON.stringify(parameter.value, null, 2)
                    : String(parameter.value)
                  }
                </div>
              </div>

              {/* Confidence */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Extraktions-Konfidenz:</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div
                      className={`
                        h-2 rounded-full
                        ${parameter.confidence >= 0.8 ? 'bg-green-500' :
                          parameter.confidence >= 0.6 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }
                      `}
                      style={{ width: `${parameter.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold">
                    {(parameter.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Source Context */}
            {contextPreview && (
              <div className="bg-blue-50 p-4 rounded-xl">
                <div className="flex items-center gap-2 mb-3">
                  <MapPin className="w-5 h-5 text-blue-600" />
                  <h4 className="font-semibold text-blue-900">Quelle im Text</h4>
                </div>
                <div className="font-mono text-sm bg-white p-3 rounded border leading-relaxed">
                  <span className="text-gray-500">{contextPreview.before}</span>
                  <span className="bg-yellow-200 px-1 py-0.5 rounded font-semibold">
                    {contextPreview.highlighted}
                  </span>
                  <span className="text-gray-500">{contextPreview.after}</span>
                </div>
                <div className="text-xs text-blue-600 mt-2">
                  Position: {parameter.character_offsets[0]}-{parameter.character_offsets[1]}
                </div>
              </div>
            )}

            {/* Value Editor */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Neuer Wert:
              </label>
              {renderValueInput()}

              {/* Validation Messages */}
              <AnimatePresence>
                {validationResult.errors.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg"
                  >
                    <div className="flex items-center gap-2 text-red-800">
                      <AlertTriangle className="w-4 h-4" />
                      <span className="font-semibold">Validierungsfehler:</span>
                    </div>
                    <ul className="mt-1 text-sm text-red-700 list-disc list-inside">
                      {validationResult.errors.map((error, index) => (
                        <li key={index}>{error}</li>
                      ))}
                    </ul>
                  </motion.div>
                )}

                {validationResult.warnings.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg"
                  >
                    <div className="flex items-center gap-2 text-yellow-800">
                      <Lightbulb className="w-4 h-4" />
                      <span className="font-semibold">Hinweise:</span>
                    </div>
                    <ul className="mt-1 text-sm text-yellow-700 list-disc list-inside">
                      {validationResult.warnings.map((warning, index) => (
                        <li key={index}>{warning}</li>
                      ))}
                    </ul>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Correction Reason */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Grund für Änderung (optional):
              </label>
              <textarea
                value={correctionReason}
                onChange={(e) => setCorrectionReason(e.target.value)}
                placeholder="Beschreiben Sie warum diese Korrektur notwendig ist..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={3}
              />
            </div>

            {/* Extraction Method Info */}
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Zap className="w-4 h-4" />
              <span>Extrahiert mit: {parameter.extraction_method}</span>
              <span>•</span>
              <span>Konfidenz: {(parameter.confidence * 100).toFixed(1)}%</span>
            </div>
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-gray-200 bg-gray-50 rounded-b-2xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Eye className="w-4 h-4" />
                <span>
                  {hasChanges ? 'Änderungen erkannt' : 'Keine Änderungen'}
                </span>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={onCancel}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Abbrechen
                </button>

                {hasChanges && (
                  <button
                    onClick={() => setEditedValue(parameter.value)}
                    className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                  >
                    <Undo className="w-4 h-4" />
                    Zurücksetzen
                  </button>
                )}

                <motion.button
                  onClick={handleSave}
                  disabled={!hasChanges || !validationResult.isValid}
                  className={`
                    flex items-center gap-2 px-6 py-2 rounded-lg font-semibold transition-all
                    ${hasChanges && validationResult.isValid
                      ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }
                  `}
                  whileHover={hasChanges && validationResult.isValid ? { scale: 1.02 } : undefined}
                  whileTap={hasChanges && validationResult.isValid ? { scale: 0.98 } : undefined}
                >
                  <Save className="w-4 h-4" />
                  Speichern
                </motion.button>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default ParameterCorrectionModal
export type { SourceGroundedParameter, ValidationResult }