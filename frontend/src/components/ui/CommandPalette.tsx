/**
 * Command Palette Component
 * Professional command palette for power users with fuzzy search
 */
'use client'

import React, { useState, useEffect, useRef, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import {
  Search,
  ArrowRight,
  Command,
  Home,
  FileText,
  MessageSquare,
  Code,
  Folder,
  Download,
  Upload,
  Settings,
  HelpCircle,
  Keyboard,
  RotateCcw,
  RotateCw,
  Trash2,
  Copy,
  Move,
  Plus,
  Filter,
  Sun,
  Moon,
  Monitor
} from 'lucide-react'

export interface CommandAction {
  id: string
  title: string
  description?: string
  category: string
  keywords: string[]
  icon?: React.ReactNode
  shortcut?: string
  action: () => void | Promise<void>
  disabled?: boolean
}

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [category, setCategory] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  // Define all available commands
  const allCommands: CommandAction[] = useMemo(() => [
    // Navigation
    {
      id: 'nav-home',
      title: 'Zur Startseite',
      description: 'Zurück zum Dashboard',
      category: 'Navigation',
      keywords: ['home', 'dashboard', 'start', 'main'],
      icon: <Home className="h-4 w-4" />,
      shortcut: 'Ctrl+H',
      action: () => window.location.href = '/'
    },
    {
      id: 'nav-documents',
      title: 'Dokumente',
      description: 'Dokumentenverwaltung öffnen',
      category: 'Navigation',
      keywords: ['documents', 'files', 'dokumente', 'dateien'],
      icon: <FileText className="h-4 w-4" />,
      shortcut: 'Ctrl+D',
      action: () => window.location.href = '/documents'
    },
    {
      id: 'nav-chat',
      title: 'Chat',
      description: 'RAG Chat Interface öffnen',
      category: 'Navigation',
      keywords: ['chat', 'conversation', 'ai', 'rag'],
      icon: <MessageSquare className="h-4 w-4" />,
      shortcut: 'Ctrl+C',
      action: () => window.location.href = '/chat'
    },
    {
      id: 'nav-xml',
      title: 'XML Wizard',
      description: 'XML Generator öffnen',
      category: 'Navigation',
      keywords: ['xml', 'wizard', 'generator', 'code'],
      icon: <Code className="h-4 w-4" />,
      shortcut: 'Ctrl+X',
      action: () => window.location.href = '/xml'
    },

    // Actions
    {
      id: 'action-new-document',
      title: 'Neues Dokument',
      description: 'Neues Dokument hochladen',
      category: 'Aktionen',
      keywords: ['new', 'create', 'upload', 'document', 'neu', 'erstellen'],
      icon: <Plus className="h-4 w-4" />,
      shortcut: 'Ctrl+N',
      action: () => {
        const uploadBtn = document.querySelector('[data-action="new-document"]') as HTMLElement
        uploadBtn?.click()
      }
    },
    {
      id: 'action-new-folder',
      title: 'Neuer Ordner',
      description: 'Neuen Ordner erstellen',
      category: 'Aktionen',
      keywords: ['new', 'folder', 'create', 'neu', 'ordner'],
      icon: <Folder className="h-4 w-4" />,
      action: () => {
        const folderBtn = document.querySelector('[data-action="new-folder"]') as HTMLElement
        folderBtn?.click()
      }
    },
    {
      id: 'action-download',
      title: 'Herunterladen',
      description: 'Ausgewählte Dateien herunterladen',
      category: 'Aktionen',
      keywords: ['download', 'save', 'export', 'herunterladen'],
      icon: <Download className="h-4 w-4" />,
      action: () => {
        window.dispatchEvent(new CustomEvent('streamworks:bulk-download'))
      }
    },
    {
      id: 'action-delete',
      title: 'Löschen',
      description: 'Ausgewählte Elemente löschen',
      category: 'Aktionen',
      keywords: ['delete', 'remove', 'trash', 'löschen'],
      icon: <Trash2 className="h-4 w-4" />,
      shortcut: 'Del',
      action: () => {
        window.dispatchEvent(new CustomEvent('streamworks:delete-selected'))
      }
    },
    {
      id: 'action-copy',
      title: 'Kopieren',
      description: 'Ausgewählte Elemente kopieren',
      category: 'Aktionen',
      keywords: ['copy', 'duplicate', 'kopieren'],
      icon: <Copy className="h-4 w-4" />,
      shortcut: 'Ctrl+C',
      action: () => {
        window.dispatchEvent(new CustomEvent('streamworks:copy-selected'))
      }
    },
    {
      id: 'action-move',
      title: 'Verschieben',
      description: 'Ausgewählte Elemente verschieben',
      category: 'Aktionen',
      keywords: ['move', 'relocate', 'verschieben'],
      icon: <Move className="h-4 w-4" />,
      action: () => {
        window.dispatchEvent(new CustomEvent('streamworks:move-selected'))
      }
    },

    // Edit
    {
      id: 'edit-undo',
      title: 'Rückgängig',
      description: 'Letzte Aktion rückgängig machen',
      category: 'Bearbeiten',
      keywords: ['undo', 'revert', 'rückgängig'],
      icon: <RotateCcw className="h-4 w-4" />,
      shortcut: 'Ctrl+Z',
      action: () => {
        window.dispatchEvent(new CustomEvent('streamworks:undo'))
      }
    },
    {
      id: 'edit-redo',
      title: 'Wiederholen',
      description: 'Letzte Aktion wiederholen',
      category: 'Bearbeiten',
      keywords: ['redo', 'repeat', 'wiederholen'],
      icon: <RotateCw className="h-4 w-4" />,
      shortcut: 'Ctrl+Y',
      action: () => {
        window.dispatchEvent(new CustomEvent('streamworks:redo'))
      }
    },
    {
      id: 'edit-select-all',
      title: 'Alle auswählen',
      description: 'Alle sichtbaren Elemente auswählen',
      category: 'Bearbeiten',
      keywords: ['select', 'all', 'auswählen', 'alle'],
      icon: <Filter className="h-4 w-4" />,
      shortcut: 'Ctrl+A',
      action: () => {
        window.dispatchEvent(new CustomEvent('streamworks:select-all'))
      }
    },

    // System
    {
      id: 'system-settings',
      title: 'Einstellungen',
      description: 'Systemeinstellungen öffnen',
      category: 'System',
      keywords: ['settings', 'preferences', 'config', 'einstellungen'],
      icon: <Settings className="h-4 w-4" />,
      action: () => {
        console.log('Open settings modal')
      }
    },
    {
      id: 'system-shortcuts',
      title: 'Keyboard Shortcuts',
      description: 'Tastenkürzel anzeigen',
      category: 'System',
      keywords: ['shortcuts', 'hotkeys', 'keyboard', 'tastenkürzel'],
      icon: <Keyboard className="h-4 w-4" />,
      shortcut: '?',
      action: () => {
        window.dispatchEvent(new CustomEvent('streamworks:show-shortcuts'))
      }
    },
    {
      id: 'system-help',
      title: 'Hilfe',
      description: 'Hilfe und Dokumentation',
      category: 'System',
      keywords: ['help', 'docs', 'support', 'hilfe'],
      icon: <HelpCircle className="h-4 w-4" />,
      action: () => {
        window.open('/help', '_blank')
      }
    },
    {
      id: 'system-theme-light',
      title: 'Helles Theme',
      description: 'Zum hellen Theme wechseln',
      category: 'System',
      keywords: ['theme', 'light', 'hell'],
      icon: <Sun className="h-4 w-4" />,
      action: () => {
        document.documentElement.classList.remove('dark')
        localStorage.setItem('theme', 'light')
      }
    },
    {
      id: 'system-theme-dark',
      title: 'Dunkles Theme',
      description: 'Zum dunklen Theme wechseln',
      category: 'System',
      keywords: ['theme', 'dark', 'dunkel'],
      icon: <Moon className="h-4 w-4" />,
      action: () => {
        document.documentElement.classList.add('dark')
        localStorage.setItem('theme', 'dark')
      }
    },
    {
      id: 'system-theme-auto',
      title: 'Auto Theme',
      description: 'Automatisches Theme basierend auf System',
      category: 'System',
      keywords: ['theme', 'auto', 'system', 'automatisch'],
      icon: <Monitor className="h-4 w-4" />,
      action: () => {
        localStorage.removeItem('theme')
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
          document.documentElement.classList.add('dark')
        } else {
          document.documentElement.classList.remove('dark')
        }
      }
    }
  ], [])

  // Filter commands based on query and category
  const filteredCommands = useMemo(() => {
    let commands = allCommands

    // Filter by category if selected
    if (category) {
      commands = commands.filter(cmd => cmd.category === category)
    }

    // Filter by search query
    if (query) {
      const lowerQuery = query.toLowerCase()
      commands = commands.filter(cmd =>
        cmd.title.toLowerCase().includes(lowerQuery) ||
        cmd.description?.toLowerCase().includes(lowerQuery) ||
        cmd.keywords.some(keyword => keyword.toLowerCase().includes(lowerQuery))
      )

      // Sort by relevance (exact match first, then starts with, then contains)
      commands.sort((a, b) => {
        const aTitle = a.title.toLowerCase()
        const bTitle = b.title.toLowerCase()

        if (aTitle === lowerQuery) return -1
        if (bTitle === lowerQuery) return 1
        if (aTitle.startsWith(lowerQuery)) return -1
        if (bTitle.startsWith(lowerQuery)) return 1
        return 0
      })
    }

    return commands
  }, [allCommands, query, category])

  // Get unique categories
  const categories = useMemo(() => {
    return Array.from(new Set(allCommands.map(cmd => cmd.category)))
  }, [allCommands])

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex(prev => Math.min(prev + 1, filteredCommands.length - 1))
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex(prev => Math.max(prev - 1, 0))
          break
        case 'Enter':
          e.preventDefault()
          if (filteredCommands[selectedIndex]) {
            executeCommand(filteredCommands[selectedIndex])
          }
          break
        case 'Escape':
          e.preventDefault()
          if (category) {
            setCategory(null)
            setQuery('')
          } else {
            onClose()
          }
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, filteredCommands, selectedIndex, category, onClose])

  // Reset selection when commands change
  useEffect(() => {
    setSelectedIndex(0)
  }, [filteredCommands])

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Scroll selected item into view
  useEffect(() => {
    if (listRef.current) {
      const selectedElement = listRef.current.children[selectedIndex] as HTMLElement
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest' })
      }
    }
  }, [selectedIndex])

  const executeCommand = async (command: CommandAction) => {
    if (command.disabled) return

    try {
      await command.action()
      onClose()
      setQuery('')
      setCategory(null)
    } catch (error) {
      console.error('Failed to execute command:', error)
    }
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-start justify-center p-4 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -20 }}
          className="w-full max-w-2xl mt-20"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            {/* Header */}
            <div className="flex items-center px-4 py-3 border-b border-gray-200 dark:border-gray-700">
              <Search className="h-5 w-5 text-gray-400 mr-3" />
              <input
                ref={inputRef}
                type="text"
                placeholder={category ? `In ${category} suchen...` : 'Befehl suchen...'}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="flex-1 bg-transparent text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none"
              />
              {category && (
                <button
                  onClick={() => {
                    setCategory(null)
                    setQuery('')
                  }}
                  className="text-xs px-2 py-1 bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded-md hover:bg-primary-200 dark:hover:bg-primary-800 transition-colors"
                >
                  {category} ✕
                </button>
              )}
            </div>

            {/* Categories (when no query) */}
            {!query && !category && (
              <div className="p-3 border-b border-gray-200 dark:border-gray-700">
                <div className="flex flex-wrap gap-2">
                  {categories.map((cat) => (
                    <button
                      key={cat}
                      onClick={() => setCategory(cat)}
                      className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Commands List */}
            <div
              ref={listRef}
              className="max-h-96 overflow-y-auto"
            >
              {filteredCommands.length === 0 ? (
                <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                  <Search className="h-8 w-8 mx-auto mb-3 opacity-50" />
                  <p>Keine Befehle gefunden</p>
                  <p className="text-sm mt-1">Versuchen Sie andere Suchbegriffe</p>
                </div>
              ) : (
                filteredCommands.map((command, index) => (
                  <div
                    key={command.id}
                    className={cn(
                      'flex items-center px-4 py-3 cursor-pointer transition-colors',
                      index === selectedIndex
                        ? 'bg-primary-50 dark:bg-primary-900/20 border-r-2 border-primary-500'
                        : 'hover:bg-gray-50 dark:hover:bg-gray-700/50',
                      command.disabled && 'opacity-50 cursor-not-allowed'
                    )}
                    onClick={() => executeCommand(command)}
                  >
                    {/* Icon */}
                    <div className="flex-shrink-0 mr-3">
                      {command.icon || <Command className="h-4 w-4" />}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {command.title}
                        </h3>
                        {command.shortcut && (
                          <kbd className="hidden sm:inline-block px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded border">
                            {command.shortcut}
                          </kbd>
                        )}
                      </div>
                      {command.description && (
                        <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                          {command.description}
                        </p>
                      )}
                    </div>

                    {/* Arrow */}
                    <ArrowRight className="h-4 w-4 text-gray-400 ml-2 flex-shrink-0" />
                  </div>
                ))
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <div className="flex items-center space-x-4">
                  <span>↑↓ Navigieren</span>
                  <span>↵ Ausführen</span>
                  <span>Esc Schließen</span>
                </div>
                <div className="flex items-center">
                  <Command className="h-3 w-3 mr-1" />
                  <span>Streamworks-KI</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}