/**
 * UI Store - Manages global UI state, modals, notifications, and theme
 */

import { create } from 'zustand';
import { subscribeWithSelector, devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type { 
  Notification, 
  Modal, 
  LoadingState,
  Theme 
} from '../types/ui';

interface UiStore {
  // Theme State
  theme: Theme;
  isDark: boolean;
  
  // Layout State
  sidebarCollapsed: boolean;
  sidebarWidth: number;
  
  // Loading States
  globalLoading: LoadingState;
  componentLoading: Record<string, LoadingState>;
  
  // Notifications
  notifications: Notification[];
  
  // Modals
  modals: Modal[];
  
  // Search State
  globalSearch: {
    isOpen: boolean;
    query: string;
    results: any[];
    loading: boolean;
  };
  
  // Keyboard shortcuts
  shortcutsEnabled: boolean;
  commandPaletteOpen: boolean;
  
  // Actions
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setSidebarWidth: (width: number) => void;
  
  // Loading actions
  setGlobalLoading: (loading: LoadingState) => void;
  setComponentLoading: (component: string, loading: LoadingState) => void;
  clearComponentLoading: (component: string) => void;
  
  // Notification actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  
  // Modal actions
  openModal: (modal: Omit<Modal, 'id'>) => void;
  closeModal: (id: string) => void;
  closeAllModals: () => void;
  
  // Search actions
  openGlobalSearch: () => void;
  closeGlobalSearch: () => void;
  setGlobalSearchQuery: (query: string) => void;
  setGlobalSearchResults: (results: any[]) => void;
  setGlobalSearchLoading: (loading: boolean) => void;
  
  // Command palette
  toggleCommandPalette: () => void;
  setShortcutsEnabled: (enabled: boolean) => void;
}

export const useUiStore = create<UiStore>()(
  devtools(
    persist(
      subscribeWithSelector(
        immer((set, get) => ({
          // Initial state
          theme: 'system',
          isDark: window.matchMedia('(prefers-color-scheme: dark)').matches,
          sidebarCollapsed: false,
          sidebarWidth: 256,
          globalLoading: { isLoading: false },
          componentLoading: {},
          notifications: [],
          modals: [],
          globalSearch: {
            isOpen: false,
            query: '',
            results: [],
            loading: false,
          },
          shortcutsEnabled: true,
          commandPaletteOpen: false,

          // Theme actions
          setTheme: (theme) => {
            set((draft) => {
              draft.theme = theme;
              
              if (theme === 'system') {
                draft.isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
              } else {
                draft.isDark = theme === 'dark';
              }
            });
            
            // Apply theme to document
            const { isDark } = get();
            document.documentElement.classList.toggle('dark', isDark);
          },

          toggleTheme: () => {
            const { theme } = get();
            
            if (theme === 'system') {
              get().setTheme('light');
            } else if (theme === 'light') {
              get().setTheme('dark');
            } else {
              get().setTheme('light');
            }
          },

          // Layout actions
          toggleSidebar: () => {
            set((draft) => {
              draft.sidebarCollapsed = !draft.sidebarCollapsed;
            });
          },

          setSidebarWidth: (width) => {
            set((draft) => {
              draft.sidebarWidth = Math.max(200, Math.min(400, width));
            });
          },

          // Loading actions
          setGlobalLoading: (loading) => {
            set((draft) => {
              draft.globalLoading = loading;
            });
          },

          setComponentLoading: (component, loading) => {
            set((draft) => {
              draft.componentLoading[component] = loading;
            });
          },

          clearComponentLoading: (component) => {
            set((draft) => {
              delete draft.componentLoading[component];
            });
          },

          // Notification actions
          addNotification: (notification) => {
            const id = `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            const timestamp = new Date().toISOString();
            
            const fullNotification: Notification = {
              id,
              timestamp,
              duration: notification.duration ?? (notification.type === 'error' ? 0 : 5000),
              ...notification,
            };

            set((draft) => {
              draft.notifications.unshift(fullNotification);
              
              // Limit to 10 notifications
              if (draft.notifications.length > 10) {
                draft.notifications = draft.notifications.slice(0, 10);
              }
            });

            // Auto-remove notification if it has a duration
            if (fullNotification.duration && fullNotification.duration > 0) {
              setTimeout(() => {
                get().removeNotification(id);
              }, fullNotification.duration);
            }
          },

          removeNotification: (id) => {
            set((draft) => {
              draft.notifications = draft.notifications.filter(n => n.id !== id);
            });
          },

          clearNotifications: () => {
            set((draft) => {
              draft.notifications = [];
            });
          },

          // Modal actions
          openModal: (modal) => {
            const id = `modal_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            
            set((draft) => {
              draft.modals.push({ id, ...modal });
            });
          },

          closeModal: (id) => {
            set((draft) => {
              draft.modals = draft.modals.filter(m => m.id !== id);
            });
          },

          closeAllModals: () => {
            set((draft) => {
              draft.modals = [];
            });
          },

          // Search actions
          openGlobalSearch: () => {
            set((draft) => {
              draft.globalSearch.isOpen = true;
            });
          },

          closeGlobalSearch: () => {
            set((draft) => {
              draft.globalSearch.isOpen = false;
              draft.globalSearch.query = '';
              draft.globalSearch.results = [];
              draft.globalSearch.loading = false;
            });
          },

          setGlobalSearchQuery: (query) => {
            set((draft) => {
              draft.globalSearch.query = query;
            });
          },

          setGlobalSearchResults: (results) => {
            set((draft) => {
              draft.globalSearch.results = results;
              draft.globalSearch.loading = false;
            });
          },

          setGlobalSearchLoading: (loading) => {
            set((draft) => {
              draft.globalSearch.loading = loading;
            });
          },

          // Command palette
          toggleCommandPalette: () => {
            set((draft) => {
              draft.commandPaletteOpen = !draft.commandPaletteOpen;
            });
          },

          setShortcutsEnabled: (enabled) => {
            set((draft) => {
              draft.shortcutsEnabled = enabled;
            });
          },
        }))
      ),
      {
        name: 'streamworks-ui-store',
        partialize: (state) => ({
          theme: state.theme,
          sidebarCollapsed: state.sidebarCollapsed,
          sidebarWidth: state.sidebarWidth,
          shortcutsEnabled: state.shortcutsEnabled,
        }),
      }
    ),
    {
      name: 'UiStore',
    }
  )
);

// Theme system integration
const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
mediaQuery.addEventListener('change', (e) => {
  const { theme, setTheme } = useUiStore.getState();
  if (theme === 'system') {
    setTheme('system'); // This will update isDark based on system preference
  }
});

// Selectors
export const useUiSelectors = {
  currentTheme: () => {
    const { theme, isDark } = useUiStore();
    return { theme, isDark };
  },
  
  activeModals: () => {
    const { modals } = useUiStore();
    return modals;
  },
  
  topModal: () => {
    const { modals } = useUiStore();
    return modals[modals.length - 1] || null;
  },
  
  recentNotifications: () => {
    const { notifications } = useUiStore();
    return notifications.slice(0, 5);
  },
  
  hasActiveLoading: () => {
    const { globalLoading, componentLoading } = useUiStore();
    return globalLoading.isLoading || Object.values(componentLoading).some(loading => loading.isLoading);
  },
  
  loadingComponents: () => {
    const { componentLoading } = useUiStore();
    return Object.entries(componentLoading)
      .filter(([_, loading]) => loading.isLoading)
      .map(([component, loading]) => ({ component, ...loading }));
  },
};

// Utility functions for common UI patterns
export const uiActions = {
  showSuccess: (message: string, title = 'Success') => {
    useUiStore.getState().addNotification({
      type: 'success',
      title,
      message,
    });
  },
  
  showError: (message: string, title = 'Error') => {
    useUiStore.getState().addNotification({
      type: 'error',
      title,
      message,
      persistent: true,
    });
  },
  
  showWarning: (message: string, title = 'Warning') => {
    useUiStore.getState().addNotification({
      type: 'warning',
      title,
      message,
    });
  },
  
  showInfo: (message: string, title = 'Info') => {
    useUiStore.getState().addNotification({
      type: 'info',
      title,
      message,
    });
  },
  
  confirm: (title: string, message: string): Promise<boolean> => {
    return new Promise((resolve) => {
      useUiStore.getState().openModal({
        type: 'confirm',
        title,
        content: message,
        actions: [
          {
            label: 'Cancel',
            action: () => resolve(false),
            variant: 'secondary',
          },
          {
            label: 'Confirm',
            action: () => resolve(true),
            variant: 'primary',
          },
        ],
      });
    });
  },
  
  setLoading: (component: string, loading: boolean, message?: string) => {
    const store = useUiStore.getState();
    if (loading) {
      store.setComponentLoading(component, { isLoading: true, message });
    } else {
      store.clearComponentLoading(component);
    }
  },
};