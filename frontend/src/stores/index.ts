/**
 * Barrel exports for all Zustand stores
 */

// Store exports
export { useChatStore, useChatSelectors } from './chatStore';
export { useDocumentStore, useDocumentSelectors } from './documentStore';
export { useUiStore, useUiSelectors, uiActions } from './uiStore';
export { useSystemStore, useSystemSelectors } from './systemStore';

// Legacy theme store (keeping for compatibility)
export { useThemeStore } from '../app/store/themeStore';

// Store types
export type * from '../types/api';
export type * from '../types/ui';

// Store utilities
export const storeActions = {
  // Global actions that affect multiple stores
  resetAllStores: () => {
    // Reset stores to initial state (useful for logout)
    localStorage.removeItem('streamworks-chat-store');
    localStorage.removeItem('streamworks-ui-store');
    window.location.reload();
  },
  
  // Initialize all stores
  initializeStores: () => {
    // Any initialization logic for stores
    console.log('StreamWorks stores initialized');
  },
};