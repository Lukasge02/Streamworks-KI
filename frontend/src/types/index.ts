/**
 * Barrel exports for all type definitions
 */

// API Types
export * from './api';

// UI Types  
export * from './ui';

// Store Types
export interface StoreSlice<T> {
  get: () => T;
  set: (partial: T | Partial<T> | ((state: T) => T | Partial<T>)) => void;
  subscribe: (listener: (state: T, prevState: T) => void) => () => void;
}

// Error Types
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
  retry?: () => void;
}

// Utility Types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type Prettify<T> = {
  [K in keyof T]: T[K];
} & {};