/**
 * Undo/Redo Service
 * Professional undo/redo functionality for complex user interactions
 */

export interface UndoableAction {
  id: string
  type: string
  description: string
  timestamp: Date
  execute: () => void | Promise<void>
  undo: () => void | Promise<void>
  metadata?: Record<string, any>
}

export interface UndoRedoState {
  canUndo: boolean
  canRedo: boolean
  undoDescription?: string
  redoDescription?: string
  historySize: number
}

class UndoRedoService {
  private undoStack: UndoableAction[] = []
  private redoStack: UndoableAction[] = []
  private maxHistorySize = 50
  private listeners: ((state: UndoRedoState) => void)[] = []

  constructor() {
    this.setupEventListeners()
  }

  private setupEventListeners(): void {
    if (typeof window === 'undefined') return

    // Listen for keyboard shortcuts
    window.addEventListener('streamworks:undo', () => {
      this.undo()
    })

    window.addEventListener('streamworks:redo', () => {
      this.redo()
    })
  }

  /**
   * Execute an action and add it to the undo stack
   */
  async executeAction(action: UndoableAction): Promise<void> {
    try {
      // Execute the action
      await action.execute()

      // Add to undo stack
      this.undoStack.push(action)

      // Clear redo stack (new action invalidates redo history)
      this.redoStack = []

      // Maintain max history size
      if (this.undoStack.length > this.maxHistorySize) {
        this.undoStack.shift()
      }

      // Notify listeners
      this.notifyStateChange()

    } catch (error) {
      console.error('Failed to execute action:', error)
      throw error
    }
  }

  /**
   * Undo the last action
   */
  async undo(): Promise<void> {
    if (this.undoStack.length === 0) return

    const action = this.undoStack.pop()!

    try {
      // Execute undo
      await action.undo()

      // Move to redo stack
      this.redoStack.push(action)

      // Maintain max history size
      if (this.redoStack.length > this.maxHistorySize) {
        this.redoStack.shift()
      }

      // Notify listeners
      this.notifyStateChange()

    } catch (error) {
      console.error('Failed to undo action:', error)
      // Put action back on undo stack
      this.undoStack.push(action)
      throw error
    }
  }

  /**
   * Redo the last undone action
   */
  async redo(): Promise<void> {
    if (this.redoStack.length === 0) return

    const action = this.redoStack.pop()!

    try {
      // Execute the action again
      await action.execute()

      // Move back to undo stack
      this.undoStack.push(action)

      // Notify listeners
      this.notifyStateChange()

    } catch (error) {
      console.error('Failed to redo action:', error)
      // Put action back on redo stack
      this.redoStack.push(action)
      throw error
    }
  }

  /**
   * Clear all history
   */
  clearHistory(): void {
    this.undoStack = []
    this.redoStack = []
    this.notifyStateChange()
  }

  /**
   * Get current state
   */
  getState(): UndoRedoState {
    const lastUndo = this.undoStack[this.undoStack.length - 1]
    const lastRedo = this.redoStack[this.redoStack.length - 1]

    return {
      canUndo: this.undoStack.length > 0,
      canRedo: this.redoStack.length > 0,
      undoDescription: lastUndo?.description,
      redoDescription: lastRedo?.description,
      historySize: this.undoStack.length + this.redoStack.length
    }
  }

  /**
   * Subscribe to state changes
   */
  subscribe(listener: (state: UndoRedoState) => void): () => void {
    this.listeners.push(listener)

    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(listener)
      if (index > -1) {
        this.listeners.splice(index, 1)
      }
    }
  }

  private notifyStateChange(): void {
    const state = this.getState()
    this.listeners.forEach(listener => listener(state))
  }

  /**
   * Create common actions
   */
  createDocumentAction(
    type: 'upload' | 'delete' | 'rename' | 'move',
    documentId: string,
    description: string,
    executeCallback: () => void | Promise<void>,
    undoCallback: () => void | Promise<void>
  ): UndoableAction {
    return {
      id: `doc-${type}-${documentId}-${Date.now()}`,
      type: `document-${type}`,
      description,
      timestamp: new Date(),
      execute: executeCallback,
      undo: undoCallback,
      metadata: { documentId, type }
    }
  }

  createFolderAction(
    type: 'create' | 'delete' | 'rename',
    folderId: string,
    description: string,
    executeCallback: () => void | Promise<void>,
    undoCallback: () => void | Promise<void>
  ): UndoableAction {
    return {
      id: `folder-${type}-${folderId}-${Date.now()}`,
      type: `folder-${type}`,
      description,
      timestamp: new Date(),
      execute: executeCallback,
      undo: undoCallback,
      metadata: { folderId, type }
    }
  }

  createChatAction(
    type: 'send' | 'delete' | 'edit',
    messageId: string,
    description: string,
    executeCallback: () => void | Promise<void>,
    undoCallback: () => void | Promise<void>
  ): UndoableAction {
    return {
      id: `chat-${type}-${messageId}-${Date.now()}`,
      type: `chat-${type}`,
      description,
      timestamp: new Date(),
      execute: executeCallback,
      undo: undoCallback,
      metadata: { messageId, type }
    }
  }

  createXMLAction(
    type: 'generate' | 'edit' | 'save',
    xmlId: string,
    description: string,
    executeCallback: () => void | Promise<void>,
    undoCallback: () => void | Promise<void>
  ): UndoableAction {
    return {
      id: `xml-${type}-${xmlId}-${Date.now()}`,
      type: `xml-${type}`,
      description,
      timestamp: new Date(),
      execute: executeCallback,
      undo: undoCallback,
      metadata: { xmlId, type }
    }
  }

  /**
   * Batch multiple actions into a single undoable action
   */
  createBatchAction(
    description: string,
    actions: UndoableAction[]
  ): UndoableAction {
    return {
      id: `batch-${Date.now()}`,
      type: 'batch',
      description,
      timestamp: new Date(),
      execute: async () => {
        for (const action of actions) {
          await action.execute()
        }
      },
      undo: async () => {
        // Undo in reverse order
        for (let i = actions.length - 1; i >= 0; i--) {
          await actions[i].undo()
        }
      },
      metadata: { actionCount: actions.length }
    }
  }

  /**
   * Get history for debugging/display
   */
  getHistory(): { undo: UndoableAction[], redo: UndoableAction[] } {
    return {
      undo: [...this.undoStack],
      redo: [...this.redoStack]
    }
  }

  /**
   * Set max history size
   */
  setMaxHistorySize(size: number): void {
    this.maxHistorySize = Math.max(1, size)

    // Trim existing stacks if necessary
    while (this.undoStack.length > this.maxHistorySize) {
      this.undoStack.shift()
    }
    while (this.redoStack.length > this.maxHistorySize) {
      this.redoStack.shift()
    }

    this.notifyStateChange()
  }

  getMaxHistorySize(): number {
    return this.maxHistorySize
  }
}

export const undoRedoService = new UndoRedoService()

// Import React for the hook
import React from 'react'

// React hook for easier integration
export const useUndoRedo = () => {
  const [state, setState] = React.useState<UndoRedoState>(undoRedoService.getState())

  React.useEffect(() => {
    const unsubscribe = undoRedoService.subscribe(setState)
    return unsubscribe
  }, [])

  return {
    ...state,
    undo: () => undoRedoService.undo(),
    redo: () => undoRedoService.redo(),
    executeAction: (action: UndoableAction) => undoRedoService.executeAction(action),
    clearHistory: () => undoRedoService.clearHistory()
  }
}