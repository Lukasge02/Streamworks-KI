/**
 * Utility functions for StreamWorks-KI application
 * All functions are pure and designed to be testable
 */

import type { ApiError } from '../types';
import { FILE_CONFIG, ERROR_MESSAGES } from '../constants';

/**
 * Formats file size from bytes to human-readable string
 * @param bytes - File size in bytes
 * @param decimals - Number of decimal places (default: 2)
 * @returns Formatted file size string
 * 
 * @example
 * formatFileSize(1024) // "1.00 KB"
 * formatFileSize(1048576, 1) // "1.0 MB"
 */
export function formatFileSize(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

/**
 * Formats a date string or Date object to various formats
 * @param date - Date string or Date object
 * @param format - Format type
 * @returns Formatted date string
 * 
 * @example
 * formatDate(new Date(), 'short') // "24.07.2025"
 * formatDate('2025-07-24T10:30:00Z', 'with-time') // "24.07.2025 10:30"
 */
export function formatDate(
  date: string | Date, 
  format: 'short' | 'long' | 'with-time' | 'time-only' | 'relative' = 'short'
): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return 'Ungültiges Datum';
  }
  
  const now = new Date();
  const diff = now.getTime() - dateObj.getTime();
  
  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString('de-DE', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      });
      
    case 'long':
      return dateObj.toLocaleDateString('de-DE', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
      });
      
    case 'with-time':
      return dateObj.toLocaleString('de-DE', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
      
    case 'time-only':
      return dateObj.toLocaleTimeString('de-DE', {
        hour: '2-digit',
        minute: '2-digit',
      });
      
    case 'relative':
      return formatRelativeTime(diff);
      
    default:
      return dateObj.toLocaleDateString('de-DE');
  }
}

/**
 * Formats relative time difference
 * @param diff - Time difference in milliseconds
 * @returns Relative time string
 */
function formatRelativeTime(diff: number): string {
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (seconds < 60) return 'gerade eben';
  if (minutes < 60) return `vor ${minutes} Min${minutes === 1 ? '' : '.'}`;
  if (hours < 24) return `vor ${hours} Std${hours === 1 ? '' : '.'}`;
  if (days < 7) return `vor ${days} Tag${days === 1 ? '' : 'en'}`;
  if (days < 30) return `vor ${Math.floor(days / 7)} Woche${Math.floor(days / 7) === 1 ? '' : 'n'}`;
  if (days < 365) return `vor ${Math.floor(days / 30)} Monat${Math.floor(days / 30) === 1 ? '' : 'en'}`;
  
  return `vor ${Math.floor(days / 365)} Jahr${Math.floor(days / 365) === 1 ? '' : 'en'}`;
}

/**
 * Generates a unique ID string
 * @param prefix - Optional prefix for the ID
 * @returns Unique identifier string
 * 
 * @example
 * generateId() // "abc123def456"
 * generateId('user') // "user_abc123def456"
 */
export function generateId(prefix?: string): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  const id = `${timestamp}${random}`;
  
  return prefix ? `${prefix}_${id}` : id;
}

/**
 * Validates a file against allowed types and size limits
 * @param file - File object to validate
 * @returns Validation result with success status and error message
 * 
 * @example
 * const result = validateFile(file);
 * if (!result.valid) {
 *   console.error(result.error);
 * }
 */
export function validateFile(file: File): { valid: boolean; error?: string } {
  // Check file size
  if (file.size > FILE_CONFIG.MAX_FILE_SIZE) {
    return {
      valid: false,
      error: `${ERROR_MESSAGES.FILE_TOO_LARGE} (${formatFileSize(file.size)})`,
    };
  }
  
  // Check file type
  const extension = `.${file.name.split('.').pop()?.toLowerCase()}`;
  const allowedTypes = Object.keys(FILE_CONFIG.ALLOWED_TYPES);
  
  if (!allowedTypes.includes(extension)) {
    return {
      valid: false,
      error: `${ERROR_MESSAGES.FILE_TYPE_NOT_SUPPORTED}: ${extension}`,
    };
  }
  
  return { valid: true };
}

/**
 * Validates multiple files for batch upload
 * @param files - Array of File objects
 * @returns Validation result with valid files and errors
 */
export function validateFiles(files: File[]): {
  validFiles: File[];
  errors: Array<{ file: string; error: string }>;
} {
  if (files.length > FILE_CONFIG.MAX_BATCH_SIZE) {
    return {
      validFiles: [],
      errors: [{ file: 'batch', error: ERROR_MESSAGES.BATCH_SIZE_EXCEEDED }],
    };
  }
  
  const validFiles: File[] = [];
  const errors: Array<{ file: string; error: string }> = [];
  
  files.forEach((file) => {
    const validation = validateFile(file);
    if (validation.valid) {
      validFiles.push(file);
    } else {
      errors.push({ file: file.name, error: validation.error || 'Unknown error' });
    }
  });
  
  return { validFiles, errors };
}

/**
 * Debounce function to limit the rate of function calls
 * @param func - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function
 * 
 * @example
 * const debouncedSearch = debounce((query: string) => {
 *   console.log('Searching:', query);
 * }, 300);
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

/**
 * Throttle function to limit the rate of function calls
 * @param func - Function to throttle
 * @param delay - Delay in milliseconds
 * @returns Throttled function
 * 
 * @example
 * const throttledScroll = throttle(() => {
 *   console.log('Scrolling');
 * }, 100);
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      func(...args);
    }
  };
}

/**
 * Handles API errors and returns user-friendly messages
 * @param error - Error object (ApiError or generic Error)
 * @returns User-friendly error message
 * 
 * @example
 * try {
 *   await apiCall();
 * } catch (error) {
 *   const message = handleApiError(error);
 *   showNotification(message, 'error');
 * }
 */
export function handleApiError(error: unknown): string {
  // Handle ApiError objects
  if (typeof error === 'object' && error !== null && 'status_code' in error) {
    const apiError = error as ApiError;
    
    switch (apiError.status_code) {
      case 400:
        return apiError.detail || ERROR_MESSAGES.BAD_REQUEST;
      case 401:
        return ERROR_MESSAGES.AUTH_REQUIRED;
      case 403:
        return ERROR_MESSAGES.PERMISSION_DENIED;
      case 404:
        return ERROR_MESSAGES.NOT_FOUND;
      case 413:
        return ERROR_MESSAGES.FILE_TOO_LARGE;
      case 422:
        return apiError.detail || ERROR_MESSAGES.BAD_REQUEST;
      case 429:
        return ERROR_MESSAGES.RATE_LIMITED;
      case 500:
        return ERROR_MESSAGES.SERVER_ERROR;
      default:
        return apiError.detail || ERROR_MESSAGES.UNEXPECTED_ERROR;
    }
  }
  
  // Handle network errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return ERROR_MESSAGES.NETWORK_ERROR;
  }
  
  // Handle generic errors
  if (error instanceof Error) {
    return error.message || ERROR_MESSAGES.UNEXPECTED_ERROR;
  }
  
  return ERROR_MESSAGES.UNEXPECTED_ERROR;
}

/**
 * Safely parses JSON with error handling
 * @param jsonString - JSON string to parse
 * @param fallback - Fallback value if parsing fails
 * @returns Parsed object or fallback value
 * 
 * @example
 * const data = safeJsonParse(response, {});
 */
export function safeJsonParse<T>(jsonString: string, fallback: T): T {
  try {
    return JSON.parse(jsonString) as T;
  } catch {
    return fallback;
  }
}

/**
 * Safely stringifies JSON with error handling
 * @param obj - Object to stringify
 * @param fallback - Fallback string if stringification fails
 * @returns JSON string or fallback
 * 
 * @example
 * const jsonString = safeJsonStringify(data, '{}');
 */
export function safeJsonStringify(obj: any, fallback: string = '{}'): string {
  try {
    return JSON.stringify(obj);
  } catch {
    return fallback;
  }
}

/**
 * Clamps a number between min and max values
 * @param value - Value to clamp
 * @param min - Minimum value
 * @param max - Maximum value
 * @returns Clamped value
 * 
 * @example
 * clamp(15, 0, 10) // 10
 * clamp(-5, 0, 10) // 0
 * clamp(5, 0, 10) // 5
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Capitalizes the first letter of a string
 * @param str - String to capitalize
 * @returns Capitalized string
 * 
 * @example
 * capitalize('hello world') // "Hello world"
 */
export function capitalize(str: string): string {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Truncates a string to a specified length with ellipsis
 * @param str - String to truncate
 * @param length - Maximum length
 * @param suffix - Suffix to add (default: '...')
 * @returns Truncated string
 * 
 * @example
 * truncate('This is a long string', 10) // "This is a..."
 */
export function truncate(str: string, length: number, suffix: string = '...'): string {
  if (str.length <= length) return str;
  return str.substring(0, length - suffix.length) + suffix;
}

/**
 * Creates a delay/sleep function
 * @param ms - Milliseconds to delay
 * @returns Promise that resolves after the delay
 * 
 * @example
 * await sleep(1000); // Wait 1 second
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Checks if a value is empty (null, undefined, empty string, empty array, empty object)
 * @param value - Value to check
 * @returns Boolean indicating if value is empty
 * 
 * @example
 * isEmpty('') // true
 * isEmpty([]) // true
 * isEmpty({}) // true
 * isEmpty(null) // true
 * isEmpty('hello') // false
 */
export function isEmpty(value: any): boolean {
  if (value == null) return true;
  if (typeof value === 'string') return value.trim().length === 0;
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
}

/**
 * Creates a deep copy of an object
 * @param obj - Object to clone
 * @returns Deep cloned object
 * 
 * @example
 * const copy = deepClone(originalObject);
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime()) as T;
  if (obj instanceof Array) return obj.map(item => deepClone(item)) as T;
  if (typeof obj === 'object') {
    const cloned = {} as T;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key]);
      }
    }
    return cloned;
  }
  return obj;
}

// All utility functions are already exported above with their declarations