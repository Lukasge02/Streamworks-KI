/**
 * German Localization for Toast Messages
 * Professional German translations for all toast notifications
 */

export interface ToastMessages {
  // General Actions
  success: {
    saved: string
    updated: string
    deleted: string
    uploaded: string
    downloaded: string
    copied: string
    completed: string
    created: string
  }

  // File Operations
  file: {
    uploading: string
    processing: string
    uploadSuccess: string
    uploadError: string
    downloadSuccess: string
    downloadError: string
    deleteSuccess: string
    deleteError: string
    tooLarge: string
    invalidType: string
    quotaExceeded: string
  }

  // Document Operations
  document: {
    analyzing: string
    analyzed: string
    processing: string
    processed: string
    chunking: string
    chunked: string
    embedding: string
    embedded: string
    indexing: string
    indexed: string
  }

  // Chat Operations
  chat: {
    thinking: string
    generating: string
    streamingResponse: string
    responseComplete: string
    errorOccurred: string
    sessionCreated: string
    sessionDeleted: string
    historyCleared: string
  }

  // XML Generation
  xml: {
    generating: string
    generated: string
    validating: string
    validated: string
    exporting: string
    exported: string
    templateSaved: string
    configUpdated: string
  }

  // System Messages
  system: {
    connecting: string
    connected: string
    disconnected: string
    reconnecting: string
    syncingData: string
    dataSynced: string
    backupCreated: string
    restoreCompleted: string
    settingsUpdated: string
    themeChanged: string
  }

  // Error Messages
  error: {
    networkError: string
    serverError: string
    unauthorized: string
    forbidden: string
    notFound: string
    timeout: string
    validationError: string
    unknownError: string
    sessionExpired: string
    quotaReached: string
  }

  // Progress Messages
  progress: {
    initializing: string
    processing: string
    uploading: string
    analyzing: string
    finishing: string
    almostDone: string
  }

  // Actions (for toast action buttons)
  actions: {
    retry: string
    undo: string
    details: string
    dismiss: string
    viewFile: string
    openChat: string
    configure: string
    upgrade: string
  }
}

export const toastMessages: ToastMessages = {
  success: {
    saved: 'Erfolgreich gespeichert',
    updated: 'Erfolgreich aktualisiert',
    deleted: 'Erfolgreich gelöscht',
    uploaded: 'Erfolgreich hochgeladen',
    downloaded: 'Erfolgreich heruntergeladen',
    copied: 'In die Zwischenablage kopiert',
    completed: 'Vorgang abgeschlossen',
    created: 'Erfolgreich erstellt'
  },

  file: {
    uploading: 'Datei wird hochgeladen...',
    processing: 'Datei wird verarbeitet...',
    uploadSuccess: 'Datei erfolgreich hochgeladen',
    uploadError: 'Fehler beim Hochladen der Datei',
    downloadSuccess: 'Datei erfolgreich heruntergeladen',
    downloadError: 'Fehler beim Herunterladen der Datei',
    deleteSuccess: 'Datei erfolgreich gelöscht',
    deleteError: 'Fehler beim Löschen der Datei',
    tooLarge: 'Datei ist zu groß (max. 100MB)',
    invalidType: 'Ungültiger Dateityp',
    quotaExceeded: 'Speicherplatz überschritten'
  },

  document: {
    analyzing: 'Dokument wird analysiert...',
    analyzed: 'Dokumentanalyse abgeschlossen',
    processing: 'Dokument wird verarbeitet...',
    processed: 'Dokumentverarbeitung abgeschlossen',
    chunking: 'Dokument wird segmentiert...',
    chunked: 'Dokumentsegmentierung abgeschlossen',
    embedding: 'Embeddings werden erstellt...',
    embedded: 'Embeddings erfolgreich erstellt',
    indexing: 'Dokument wird indexiert...',
    indexed: 'Dokument erfolgreich indexiert'
  },

  chat: {
    thinking: 'KI denkt nach...',
    generating: 'Antwort wird generiert...',
    streamingResponse: 'Antwort wird übertragen...',
    responseComplete: 'Antwort vollständig',
    errorOccurred: 'Fehler bei der Antwortgenerierung',
    sessionCreated: 'Neue Chat-Session erstellt',
    sessionDeleted: 'Chat-Session gelöscht',
    historyCleared: 'Chat-Verlauf geleert'
  },

  xml: {
    generating: 'XML wird generiert...',
    generated: 'XML erfolgreich generiert',
    validating: 'XML wird validiert...',
    validated: 'XML erfolgreich validiert',
    exporting: 'XML wird exportiert...',
    exported: 'XML erfolgreich exportiert',
    templateSaved: 'Template gespeichert',
    configUpdated: 'Konfiguration aktualisiert'
  },

  system: {
    connecting: 'Verbindung wird hergestellt...',
    connected: 'Erfolgreich verbunden',
    disconnected: 'Verbindung getrennt',
    reconnecting: 'Neuverbindung...',
    syncingData: 'Daten werden synchronisiert...',
    dataSynced: 'Daten synchronisiert',
    backupCreated: 'Backup erstellt',
    restoreCompleted: 'Wiederherstellung abgeschlossen',
    settingsUpdated: 'Einstellungen aktualisiert',
    themeChanged: 'Design geändert'
  },

  error: {
    networkError: 'Netzwerkfehler - Bitte überprüfen Sie Ihre Verbindung',
    serverError: 'Serverfehler - Bitte versuchen Sie es später erneut',
    unauthorized: 'Nicht autorisiert - Bitte melden Sie sich an',
    forbidden: 'Zugriff verweigert - Fehlende Berechtigung',
    notFound: 'Ressource nicht gefunden',
    timeout: 'Zeitüberschreitung - Vorgang zu langsam',
    validationError: 'Validierungsfehler - Eingabe überprüfen',
    unknownError: 'Unbekannter Fehler aufgetreten',
    sessionExpired: 'Session abgelaufen - Bitte neu anmelden',
    quotaReached: 'Kontingent erschöpft - Upgrade erforderlich'
  },

  progress: {
    initializing: 'Initialisierung...',
    processing: 'Verarbeitung läuft...',
    uploading: 'Upload läuft...',
    analyzing: 'Analyse läuft...',
    finishing: 'Abschließende Arbeiten...',
    almostDone: 'Fast fertig...'
  },

  actions: {
    retry: 'Wiederholen',
    undo: 'Rückgängig',
    details: 'Details anzeigen',
    dismiss: 'Schließen',
    viewFile: 'Datei anzeigen',
    openChat: 'Chat öffnen',
    configure: 'Konfigurieren',
    upgrade: 'Upgrade'
  }
}

/**
 * Helper function to get localized toast message
 */
export function getToastMessage(category: keyof ToastMessages, key: string): string {
  const categoryMessages = toastMessages[category] as any
  return categoryMessages?.[key] || key
}

/**
 * Helper function for error messages with fallback
 */
export function getErrorMessage(errorCode: string, fallback?: string): string {
  const errorKey = errorCode.toLowerCase().replace(/-/g, '')
  const message = (toastMessages.error as any)[errorKey]
  return message || fallback || toastMessages.error.unknownError
}