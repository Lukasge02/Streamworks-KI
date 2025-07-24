/**
 * Application constants and configuration values
 */

import type { ProcessingStatus, ThemeConfig } from '../types';

/**
 * API Configuration
 */
export const API_CONFIG = {
  /** Base URL for API requests */
  BASE_URL: import.meta.env['VITE_API_BASE_URL'] || 'http://localhost:8000/api/v1',
  /** Request timeout in milliseconds */
  TIMEOUT: 30000,
  /** Retry attempts for failed requests */
  RETRY_ATTEMPTS: 3,
  /** Retry delay in milliseconds */
  RETRY_DELAY: 1000,
} as const;

/**
 * File upload configuration
 */
export const FILE_CONFIG = {
  /** Maximum file size in bytes (50MB) */
  MAX_FILE_SIZE: 50 * 1024 * 1024,
  /** Maximum files per batch upload */
  MAX_BATCH_SIZE: 20,
  /** Allowed file types with descriptions */
  ALLOWED_TYPES: {
    // Text & Documentation
    '.txt': 'Plain Text',
    '.md': 'Markdown',
    '.rtf': 'Rich Text Format',
    '.log': 'Log File',
    
    // Office Documents
    '.pdf': 'PDF Document',
    '.docx': 'Word Document',
    '.doc': 'Word Document (Legacy)',
    '.odt': 'OpenDocument Text',
    
    // Structured Data
    '.csv': 'CSV Spreadsheet',
    '.tsv': 'TSV Spreadsheet',
    '.xlsx': 'Excel Spreadsheet',
    '.xls': 'Excel Spreadsheet (Legacy)',
    '.json': 'JSON Data',
    '.jsonl': 'JSON Lines',
    '.yaml': 'YAML Configuration',
    '.yml': 'YAML Configuration',
    '.toml': 'TOML Configuration',
    
    // XML Family
    '.xml': 'XML Document',
    '.xsd': 'XML Schema',
    '.xsl': 'XSL Stylesheet',
    '.svg': 'SVG Image',
    '.rss': 'RSS Feed',
    '.atom': 'Atom Feed',
    
    // Code & Scripts
    '.py': 'Python Script',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.java': 'Java Source',
    '.sql': 'SQL Script',
    '.ps1': 'PowerShell Script',
    '.bat': 'Batch File',
    '.sh': 'Shell Script',
    '.bash': 'Bash Script',
    
    // Web & Markup
    '.html': 'HTML Document',
    '.htm': 'HTML Document',
    
    // Configuration
    '.ini': 'INI Configuration',
    '.cfg': 'Configuration File',
    '.conf': 'Configuration File',
    
    // Email
    '.msg': 'Outlook Message',
    '.eml': 'Email Message',
  },
} as const;

/**
 * Processing status configurations
 */
export const PROCESSING_STATUSES: Record<ProcessingStatus, {
  label: string;
  color: string;
  icon: string;
  description: string;
}> = {
  pending: {
    label: 'Ausstehend',
    color: 'yellow',
    icon: 'Clock',
    description: 'Wartet auf Verarbeitung',
  },
  processing: {
    label: 'Verarbeitung',
    color: 'blue',
    icon: 'Loader',
    description: 'Wird gerade verarbeitet',
  },
  completed: {
    label: 'Abgeschlossen',
    color: 'green',
    icon: 'CheckCircle',
    description: 'Erfolgreich verarbeitet',
  },
  failed: {
    label: 'Fehlgeschlagen',
    color: 'red',
    icon: 'XCircle',
    description: 'Verarbeitung fehlgeschlagen',
  },
  cancelled: {
    label: 'Abgebrochen',
    color: 'gray',
    icon: 'Slash',
    description: 'Verarbeitung abgebrochen',
  },
  indexed: {
    label: 'Indiziert',
    color: 'purple',
    icon: 'Database',
    description: 'In Wissensdatenbank indiziert',
  },
  ready: {
    label: 'Bereit',
    color: 'green',
    icon: 'Check',
    description: 'Bereit zur Verwendung',
  },
} as const;

/**
 * System themes configuration
 */
export const SYSTEM_THEMES: ThemeConfig[] = [
  {
    id: 'light',
    name: 'Hell',
    colors: {
      primary: '#2563eb',
      secondary: '#64748b',
      accent: '#0ea5e9',
      background: '#ffffff',
      foreground: '#0f172a',
      muted: '#f1f5f9',
      border: '#e2e8f0',
    },
    dark: false,
  },
  {
    id: 'dark',
    name: 'Dunkel',
    colors: {
      primary: '#3b82f6',
      secondary: '#64748b',
      accent: '#0ea5e9',
      background: '#0f172a',
      foreground: '#f8fafc',
      muted: '#1e293b',
      border: '#334155',
    },
    dark: true,
  },
  {
    id: 'system',
    name: 'System',
    colors: {
      primary: '#2563eb',
      secondary: '#64748b',
      accent: '#0ea5e9',
      background: '#ffffff',
      foreground: '#0f172a',
      muted: '#f1f5f9',
      border: '#e2e8f0',
    },
    dark: false,
  },
] as const;

/**
 * Navigation items configuration
 */
export const NAVIGATION_ITEMS = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    path: '/',
    icon: 'LayoutDashboard',
  },
  {
    id: 'chat',
    label: 'KI Chat',
    path: '/chat',
    icon: 'MessageSquare',
  },
  {
    id: 'documents',
    label: 'Dokumente',
    path: '/documents',
    icon: 'FolderOpen',
  },
  {
    id: 'xml-generator',
    label: 'XML Generator',
    path: '/xml-generator',
    icon: 'Code',
  },
  {
    id: 'analytics',
    label: 'Analytics',
    path: '/analytics',
    icon: 'BarChart3',
  },
  {
    id: 'monitoring',
    label: 'Monitoring',
    path: '/monitoring',
    icon: 'Activity',
  },
  {
    id: 'training',
    label: 'Training Data',
    path: '/training',
    icon: 'BookOpen',
  },
  {
    id: 'settings',
    label: 'Einstellungen',
    path: '/settings',
    icon: 'Settings',
  },
] as const;

/**
 * Error messages
 */
export const ERROR_MESSAGES = {
  // Network errors
  NETWORK_ERROR: 'Netzwerkfehler: Server nicht erreichbar',
  TIMEOUT_ERROR: 'Anfrage-Timeout: Server antwortet nicht',
  CONNECTION_LOST: 'Verbindung verloren: Bitte versuchen Sie es erneut',
  
  // Authentication errors
  AUTH_REQUIRED: 'Anmeldung erforderlich',
  AUTH_EXPIRED: 'Sitzung abgelaufen: Bitte melden Sie sich erneut an',
  AUTH_INVALID: 'Ungültige Anmeldedaten',
  
  // File upload errors
  FILE_TOO_LARGE: 'Datei zu groß: Maximum 50MB erlaubt',
  FILE_TYPE_NOT_SUPPORTED: 'Dateityp nicht unterstützt',
  UPLOAD_FAILED: 'Datei-Upload fehlgeschlagen',
  BATCH_SIZE_EXCEEDED: 'Zu viele Dateien: Maximum 20 Dateien pro Batch',
  
  // Processing errors
  PROCESSING_FAILED: 'Verarbeitung fehlgeschlagen',
  INDEXING_FAILED: 'Indizierung fehlgeschlagen',
  CONVERSION_FAILED: 'Dateikonvertierung fehlgeschlagen',
  
  // API errors
  BAD_REQUEST: 'Ungültige Anfrage',
  NOT_FOUND: 'Ressource nicht gefunden',
  SERVER_ERROR: 'Serverfehler: Bitte versuchen Sie es später erneut',
  RATE_LIMITED: 'Zu viele Anfragen: Bitte warten Sie einen Moment',
  
  // Validation errors
  REQUIRED_FIELD: 'Dieses Feld ist erforderlich',
  INVALID_EMAIL: 'Ungültige E-Mail-Adresse',
  INVALID_URL: 'Ungültige URL',
  PASSWORD_TOO_SHORT: 'Passwort zu kurz: Mindestens 8 Zeichen',
  
  // Chat errors
  CHAT_FAILED: 'Chat-Anfrage fehlgeschlagen',
  MESSAGE_TOO_LONG: 'Nachricht zu lang: Maximum 4000 Zeichen',
  NO_RESPONSE: 'Keine Antwort vom KI-System',
  
  // XML errors
  XML_GENERATION_FAILED: 'XML-Generierung fehlgeschlagen',
  XML_VALIDATION_FAILED: 'XML-Validierung fehlgeschlagen',
  INVALID_XML: 'Ungültiges XML-Format',
  
  // Generic errors
  UNEXPECTED_ERROR: 'Unerwarteter Fehler aufgetreten',
  OPERATION_CANCELLED: 'Vorgang abgebrochen',
  PERMISSION_DENIED: 'Berechtigung verweigert',
} as const;

/**
 * Success messages
 */
export const SUCCESS_MESSAGES = {
  FILE_UPLOADED: 'Datei erfolgreich hochgeladen',
  FILES_UPLOADED: 'Dateien erfolgreich hochgeladen',
  DOCUMENT_PROCESSED: 'Dokument erfolgreich verarbeitet',
  CHAT_MESSAGE_SENT: 'Nachricht gesendet',
  XML_GENERATED: 'XML erfolgreich generiert',
  SETTINGS_SAVED: 'Einstellungen gespeichert',
  DATA_EXPORTED: 'Daten erfolgreich exportiert',
  OPERATION_COMPLETED: 'Vorgang erfolgreich abgeschlossen',
} as const;

/**
 * Application metadata
 */
export const APP_CONFIG = {
  /** Application name */
  NAME: 'StreamWorks-KI',
  /** Application version */
  VERSION: '1.0.0',
  /** Application description */
  DESCRIPTION: 'Enterprise-grade AI-powered document management and automation system',
  /** Company name */
  COMPANY: 'Arvato Systems',
  /** Support email */
  SUPPORT_EMAIL: 'support@streamworks-ki.com',
  /** Documentation URL */
  DOCS_URL: 'https://docs.streamworks-ki.com',
} as const;

/**
 * Local storage keys
 */
export const STORAGE_KEYS = {
  THEME: 'streamworks-theme',
  USER_PREFERENCES: 'streamworks-user-prefs',
  CHAT_HISTORY: 'streamworks-chat-history',
  DRAFT_MESSAGES: 'streamworks-drafts',
  SEARCH_HISTORY: 'streamworks-search-history',
} as const;

/**
 * Date and time formats
 */
export const DATE_FORMATS = {
  SHORT: 'dd.MM.yyyy',
  LONG: 'dd. MMMM yyyy',
  WITH_TIME: 'dd.MM.yyyy HH:mm',
  TIME_ONLY: 'HH:mm',
  ISO: "yyyy-MM-dd'T'HH:mm:ss.SSSxxx",
  RELATIVE: 'relative', // Special format for relative dates
} as const;

/**
 * Animation durations in milliseconds
 */
export const ANIMATION_DURATIONS = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
  VERY_SLOW: 1000,
} as const;

/**
 * Breakpoints for responsive design (matches Tailwind)
 */
export const BREAKPOINTS = {
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  '2XL': 1536,
} as const;

// All constants are already exported above with their declarations