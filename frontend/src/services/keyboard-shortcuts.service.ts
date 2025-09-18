/**
 * Keyboard Shortcuts Service
 * Professional keyboard navigation and shortcuts for power users
 */

export interface KeyboardShortcut {
  key: string
  ctrlKey?: boolean
  altKey?: boolean
  shiftKey?: boolean
  metaKey?: boolean
  action: string
  description: string
  category: 'navigation' | 'editing' | 'actions' | 'system'
  handler: () => void | Promise<void>
}

export interface ShortcutCategory {
  navigation: KeyboardShortcut[]
  editing: KeyboardShortcut[]
  actions: KeyboardShortcut[]
  system: KeyboardShortcut[]
}

class KeyboardShortcutsService {
  private shortcuts: Map<string, KeyboardShortcut> = new Map()
  private isEnabled = true
  private excludedElements = ['INPUT', 'TEXTAREA', 'SELECT']

  constructor() {
    this.setupEventListeners()
    this.loadDefaultShortcuts()
  }

  private setupEventListeners(): void {
    if (typeof window === 'undefined') return

    document.addEventListener('keydown', this.handleKeyDown.bind(this))

    // Prevent default browser shortcuts that conflict
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey) {
        const key = e.key.toLowerCase()
        // Prevent browser shortcuts for our custom ones
        if (['s', 'n', 'o', 'f', 'd', 'z', 'y'].includes(key)) {
          if (this.shortcuts.has(this.getShortcutKey(e))) {
            e.preventDefault()
          }
        }
      }
    })
  }

  private handleKeyDown(event: KeyboardEvent): void {
    if (!this.isEnabled) return

    // Skip if user is typing in input fields
    const target = event.target as HTMLElement
    if (this.excludedElements.includes(target.tagName)) return

    const shortcutKey = this.getShortcutKey(event)
    const shortcut = this.shortcuts.get(shortcutKey)

    if (shortcut) {
      event.preventDefault()
      event.stopPropagation()

      try {
        const result = shortcut.handler()
        if (result instanceof Promise) {
          result.catch(console.error)
        }
      } catch (error) {
        console.error('Error executing keyboard shortcut:', error)
      }
    }
  }

  private getShortcutKey(event: KeyboardEvent): string {
    const modifiers = []
    if (event.ctrlKey) modifiers.push('ctrl')
    if (event.altKey) modifiers.push('alt')
    if (event.shiftKey) modifiers.push('shift')
    if (event.metaKey) modifiers.push('meta')

    return [...modifiers, event.key.toLowerCase()].join('+')
  }

  private loadDefaultShortcuts(): void {
    // Navigation shortcuts
    this.registerShortcut({
      key: 'h',
      ctrlKey: true,
      action: 'go-home',
      description: 'Zur Startseite navigieren',
      category: 'navigation',
      handler: () => {
        window.location.href = '/'
      }
    })

    this.registerShortcut({
      key: 'd',
      ctrlKey: true,
      action: 'go-documents',
      description: 'Zu Dokumenten navigieren',
      category: 'navigation',
      handler: () => {
        window.location.href = '/documents'
      }
    })

    this.registerShortcut({
      key: 'c',
      ctrlKey: true,
      action: 'go-chat',
      description: 'Zum Chat navigieren',
      category: 'navigation',
      handler: () => {
        window.location.href = '/chat'
      }
    })

    this.registerShortcut({
      key: 'x',
      ctrlKey: true,
      action: 'go-xml',
      description: 'Zum XML-Wizard navigieren',
      category: 'navigation',
      handler: () => {
        window.location.href = '/xml'
      }
    })

    // System shortcuts
    this.registerShortcut({
      key: '/',
      action: 'open-search',
      description: 'Globale Suche öffnen',
      category: 'system',
      handler: () => {
        const searchInput = document.querySelector('[data-search-input]') as HTMLInputElement
        if (searchInput) {
          searchInput.focus()
          searchInput.select()
        }
      }
    })

    this.registerShortcut({
      key: 'Escape',
      action: 'close-modal',
      description: 'Modals und Overlays schließen',
      category: 'system',
      handler: () => {
        // Close any open modals
        const closeButtons = document.querySelectorAll('[data-close-modal]')
        closeButtons.forEach(button => (button as HTMLElement).click())

        // Clear focus
        const activeElement = document.activeElement as HTMLElement
        if (activeElement && activeElement.blur) {
          activeElement.blur()
        }
      }
    })

    this.registerShortcut({
      key: '?',
      shiftKey: true,
      action: 'show-help',
      description: 'Keyboard Shortcuts anzeigen',
      category: 'system',
      handler: () => {
        this.showShortcutsModal()
      }
    })

    // Actions
    this.registerShortcut({
      key: 'n',
      ctrlKey: true,
      action: 'new-document',
      description: 'Neues Dokument erstellen',
      category: 'actions',
      handler: () => {
        const newButton = document.querySelector('[data-action="new-document"]') as HTMLElement
        if (newButton) {
          newButton.click()
        }
      }
    })

    this.registerShortcut({
      key: 's',
      ctrlKey: true,
      action: 'save',
      description: 'Speichern',
      category: 'actions',
      handler: () => {
        const saveButton = document.querySelector('[data-action="save"]') as HTMLElement
        if (saveButton) {
          saveButton.click()
        }
      }
    })

    this.registerShortcut({
      key: 'Enter',
      ctrlKey: true,
      action: 'submit-form',
      description: 'Formular absenden',
      category: 'actions',
      handler: () => {
        const submitButton = document.querySelector('[data-action="submit"]') as HTMLElement
        if (submitButton) {
          submitButton.click()
        }
      }
    })

    // Editing shortcuts
    this.registerShortcut({
      key: 'z',
      ctrlKey: true,
      action: 'undo',
      description: 'Rückgängig machen',
      category: 'editing',
      handler: () => {
        // Will be handled by undo/redo service
        window.dispatchEvent(new CustomEvent('streamworks:undo'))
      }
    })

    this.registerShortcut({
      key: 'y',
      ctrlKey: true,
      action: 'redo',
      description: 'Wiederholen',
      category: 'editing',
      handler: () => {
        // Will be handled by undo/redo service
        window.dispatchEvent(new CustomEvent('streamworks:redo'))
      }
    })

    this.registerShortcut({
      key: 'a',
      ctrlKey: true,
      action: 'select-all',
      description: 'Alle auswählen',
      category: 'editing',
      handler: () => {
        window.dispatchEvent(new CustomEvent('streamworks:select-all'))
      }
    })

    this.registerShortcut({
      key: 'Delete',
      action: 'delete-selected',
      description: 'Ausgewählte Elemente löschen',
      category: 'editing',
      handler: () => {
        window.dispatchEvent(new CustomEvent('streamworks:delete-selected'))
      }
    })
  }

  registerShortcut(shortcut: Omit<KeyboardShortcut, 'key'> & { key: string; ctrlKey?: boolean; altKey?: boolean; shiftKey?: boolean; metaKey?: boolean }): void {
    const shortcutKey = this.buildShortcutKey(shortcut)

    const fullShortcut: KeyboardShortcut = {
      key: shortcut.key,
      ctrlKey: shortcut.ctrlKey,
      altKey: shortcut.altKey,
      shiftKey: shortcut.shiftKey,
      metaKey: shortcut.metaKey,
      action: shortcut.action,
      description: shortcut.description,
      category: shortcut.category,
      handler: shortcut.handler
    }

    this.shortcuts.set(shortcutKey, fullShortcut)
  }

  private buildShortcutKey(shortcut: { key: string; ctrlKey?: boolean; altKey?: boolean; shiftKey?: boolean; metaKey?: boolean }): string {
    const modifiers = []
    if (shortcut.ctrlKey) modifiers.push('ctrl')
    if (shortcut.altKey) modifiers.push('alt')
    if (shortcut.shiftKey) modifiers.push('shift')
    if (shortcut.metaKey) modifiers.push('meta')

    return [...modifiers, shortcut.key.toLowerCase()].join('+')
  }

  unregisterShortcut(action: string): void {
    for (const [key, shortcut] of this.shortcuts.entries()) {
      if (shortcut.action === action) {
        this.shortcuts.delete(key)
        break
      }
    }
  }

  getAllShortcuts(): ShortcutCategory {
    const categories: ShortcutCategory = {
      navigation: [],
      editing: [],
      actions: [],
      system: []
    }

    for (const shortcut of this.shortcuts.values()) {
      categories[shortcut.category].push(shortcut)
    }

    return categories
  }

  getShortcutText(shortcut: KeyboardShortcut): string {
    const modifiers = []
    const isMac = typeof window !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0

    if (shortcut.ctrlKey) modifiers.push(isMac ? '⌘' : 'Ctrl')
    if (shortcut.altKey) modifiers.push(isMac ? '⌥' : 'Alt')
    if (shortcut.shiftKey) modifiers.push(isMac ? '⇧' : 'Shift')
    if (shortcut.metaKey) modifiers.push(isMac ? '⌘' : 'Meta')

    const key = shortcut.key === ' ' ? 'Space' :
                shortcut.key === 'Escape' ? 'Esc' :
                shortcut.key.length === 1 ? shortcut.key.toUpperCase() : shortcut.key

    return [...modifiers, key].join(isMac ? '' : '+')
  }

  enable(): void {
    this.isEnabled = true
  }

  disable(): void {
    this.isEnabled = false
  }

  isShortcutsEnabled(): boolean {
    return this.isEnabled
  }

  private showShortcutsModal(): void {
    // Create modal content
    const modal = document.createElement('div')
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50'
    modal.onclick = (e) => {
      if (e.target === modal) {
        document.body.removeChild(modal)
      }
    }

    const content = document.createElement('div')
    content.className = 'bg-white dark:bg-gray-800 rounded-lg p-6 max-w-4xl max-h-[80vh] overflow-y-auto'

    const shortcuts = this.getAllShortcuts()

    content.innerHTML = `
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">⌨️ Keyboard Shortcuts</h2>
        <button class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" onclick="this.closest('.fixed').remove()">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <div class="grid md:grid-cols-2 gap-6">
        ${Object.entries(shortcuts).map(([category, categoryShortcuts]) => `
          <div>
            <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3 capitalize">
              ${category === 'navigation' ? '🧭 Navigation' :
                category === 'editing' ? '✏️ Bearbeiten' :
                category === 'actions' ? '⚡ Aktionen' : '⚙️ System'}
            </h3>
            <div class="space-y-2">
              ${categoryShortcuts.map(shortcut => `
                <div class="flex justify-between items-center py-2 px-3 bg-gray-50 dark:bg-gray-700 rounded">
                  <span class="text-gray-700 dark:text-gray-300">${shortcut.description}</span>
                  <kbd class="px-2 py-1 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded text-sm font-mono">
                    ${this.getShortcutText(shortcut)}
                  </kbd>
                </div>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </div>

      <div class="mt-6 text-center">
        <p class="text-sm text-gray-500 dark:text-gray-400">
          Drücke <kbd class="px-2 py-1 bg-gray-200 dark:bg-gray-600 rounded">Esc</kbd> um zu schließen
        </p>
      </div>
    `

    modal.appendChild(content)
    document.body.appendChild(modal)

    // Focus trap
    const focusableElements = content.querySelectorAll('button')
    if (focusableElements.length > 0) {
      (focusableElements[0] as HTMLElement).focus()
    }
  }
}

export const keyboardShortcutsService = new KeyboardShortcutsService()