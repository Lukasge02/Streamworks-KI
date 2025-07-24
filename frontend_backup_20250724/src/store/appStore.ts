import { create } from 'zustand';
import { TabType } from '../types';

export type ThemeMode = 'light' | 'dark' | 'system';

interface AppState {
  activeTab: TabType;
  copiedMessageId: string | null;
  chatLoadingState: { sessionId: string | null; isLoading: boolean };
  themeMode: ThemeMode;
  isDarkMode: boolean;
  setActiveTab: (tab: TabType) => void;
  setCopiedMessageId: (id: string | null) => void;
  setChatLoadingState: (sessionId: string | null, isLoading: boolean) => void;
  setThemeMode: (mode: ThemeMode) => void;
}

const getSystemTheme = (): boolean => {
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
};

const applyTheme = (mode: ThemeMode): boolean => {
  const isDark = mode === 'dark' || (mode === 'system' && getSystemTheme());
  
  // Ensure DOM is ready
  if (typeof window !== 'undefined' && document.documentElement) {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }
  
  return isDark;
};

export const useAppStore = create<AppState>((set) => {
  // Initialize with system theme as default
  const savedMode = (typeof window !== 'undefined' ? localStorage.getItem('themeMode') : null) as ThemeMode || 'system';
  
  return {
    activeTab: 'chat',
    copiedMessageId: null,
    chatLoadingState: { sessionId: null, isLoading: false },
    themeMode: savedMode,
    isDarkMode: savedMode === 'dark' || (savedMode === 'system' && getSystemTheme()),
    setActiveTab: (tab) => set({ activeTab: tab }),
    setCopiedMessageId: (id) => set({ copiedMessageId: id }),
    setChatLoadingState: (sessionId, isLoading) => set({ chatLoadingState: { sessionId, isLoading } }),
    setThemeMode: (mode: ThemeMode) => {
      console.log('Setting theme mode to:', mode);
      
      if (typeof window !== 'undefined') {
        localStorage.setItem('themeMode', mode);
      }
      
      const newIsDark = applyTheme(mode);
      console.log('Applied theme, isDark:', newIsDark);
      
      set({ themeMode: mode, isDarkMode: newIsDark });
    }
  };
});