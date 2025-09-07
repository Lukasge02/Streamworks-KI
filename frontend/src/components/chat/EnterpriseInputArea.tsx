'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, Loader, Mic, Paperclip, Lightbulb, Settings, ArrowUp } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface EnterpriseInputAreaProps {
  input: string
  setInput: (value: string) => void
  isLoading: boolean
  onSubmit: (e: React.FormEvent) => void
  onSuggestionClick: (suggestion: string) => void
  placeholder?: string
  showSuggestions?: boolean
  maxLength?: number
}

const DEFAULT_SUGGESTIONS = [
  'Was ist Streamworks?',
  'Job Scheduling?',
  'XML Templates?'
]

export const EnterpriseInputArea: React.FC<EnterpriseInputAreaProps> = ({
  input,
  setInput,
  isLoading,
  onSubmit,
  onSuggestionClick,
  placeholder = "Stelle eine Frage zu deinen Streamworks Dokumenten...",
  showSuggestions = true,
  maxLength = 2000
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const [isFocused, setIsFocused] = useState(false)
  const [charCount, setCharCount] = useState(0)
  const [showAdvanced, setShowAdvanced] = useState(false)

  useEffect(() => {
    setCharCount(input.length)
  }, [input])

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
    }
  }, [input])

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      if (e.shiftKey) {
        // Allow new line with Shift+Enter
        return
      } else {
        // Submit with Enter
        e.preventDefault()
        if (input.trim() && !isLoading) {
          onSubmit(e as any)
        }
      }
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    if (value.length <= maxLength) {
      setInput(value)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      {/* Suggestion Pills */}
      <AnimatePresence>
        {showSuggestions && !input && !isFocused && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="px-6 pt-3 pb-2"
          >
            <div className="text-center mb-3">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400 flex items-center justify-center">
                <Lightbulb className="w-3 h-3 mr-1.5" />
                Beispielfragen
              </span>
            </div>
            <div className="flex items-center justify-center gap-2 flex-wrap max-w-2xl mx-auto">
              {DEFAULT_SUGGESTIONS.map((suggestion, index) => (
                <motion.button
                  key={suggestion}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => onSuggestionClick(suggestion)}
                  className="px-3 py-1.5 text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-full border border-blue-200 hover:border-blue-300 transition-all duration-200 cursor-pointer text-center dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-700 dark:hover:bg-blue-900/30"
                >
                  {suggestion}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Input Area */}
      <div className="px-6 pb-6">
        <form onSubmit={onSubmit} className="relative">
          {/* Input Container */}
          <div className={`relative rounded-2xl border transition-all duration-200 ${
            isFocused 
              ? 'border-primary-500 bg-white dark:bg-gray-800 shadow-md' 
              : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-500'
          }`}>
            
            {/* Textarea */}
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={placeholder}
              disabled={isLoading}
              className="w-full px-4 py-4 pr-16 bg-transparent border-none resize-none focus:outline-none placeholder:text-gray-500 dark:placeholder:text-gray-400 text-gray-900 dark:text-gray-100 text-sm leading-relaxed min-h-[52px] max-h-[120px]"
              rows={1}
            />

            {/* Input Actions */}
            <div className="absolute right-2 bottom-2 flex items-center space-x-1">
              {/* Character Counter */}
              {input.length > maxLength * 0.8 && (
                <span className={`text-xs px-2 py-1 rounded-full ${
                  charCount >= maxLength 
                    ? 'text-red-600 bg-red-100 dark:bg-red-900/30' 
                    : 'text-amber-600 bg-amber-100 dark:bg-amber-900/30'
                }`}>
                  {charCount}/{maxLength}
                </span>
              )}

              {/* Attachment Button */}
              <button
                type="button"
                disabled={isLoading}
                className="btn-enterprise-ghost p-2"
                title="Datei anhängen (Coming Soon)"
              >
                <Paperclip className="w-4 h-4" />
              </button>

              {/* Voice Input Button */}
              <button
                type="button"
                disabled={isLoading}
                className="btn-enterprise-ghost p-2"
                title="Spracheingabe (Coming Soon)"
              >
                <Mic className="w-4 h-4" />
              </button>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={!input.trim() || isLoading || charCount > maxLength}
                className={`p-2 rounded-lg transition-all duration-200 ${
                  input.trim() && !isLoading && charCount <= maxLength
                    ? 'btn-enterprise-primary'
                    : 'bg-gray-200 dark:bg-gray-600 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                }`}
                title={isLoading ? 'Denkt nach...' : 'Nachricht senden (Enter)'}
              >
                {isLoading ? (
                  <Loader className="w-4 h-4 animate-spin" />
                ) : (
                  <ArrowUp className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* Helper Text */}
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-4">
              <span>💡 Verwende Shift+Enter für neue Zeile</span>
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center space-x-1 hover:text-gray-700 dark:hover:text-gray-300 transition-colors text-xs"
              >
                <Settings className="w-3 h-3" />
                <span>Erweiterte Optionen</span>
              </button>
            </div>
            <div>
              {isLoading && (
                <span className="text-blue-600 dark:text-blue-400">
                  Verarbeite Anfrage...
                </span>
              )}
            </div>
          </div>

          {/* Advanced Options */}
          <AnimatePresence>
            {showAdvanced && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-3 card-enterprise p-4"
              >
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <label className="block text-gray-700 dark:text-gray-300 mb-1">
                      Suchtiefe:
                    </label>
                    <select className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm">
                      <option>Standard (5 Quellen)</option>
                      <option>Gründlich (10 Quellen)</option>
                      <option>Umfassend (15 Quellen)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-gray-700 dark:text-gray-300 mb-1">
                      Antworttyp:
                    </label>
                    <select className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm">
                      <option>Ausführlich</option>
                      <option>Zusammenfassung</option>
                      <option>Bulletpoints</option>
                    </select>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </form>
      </div>
    </div>
  )
}