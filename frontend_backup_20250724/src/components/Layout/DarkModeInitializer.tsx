import { useEffect } from 'react';
import { useAppStore } from '../../store/appStore';

export const DarkModeInitializer: React.FC = () => {
  const { themeMode, setThemeMode } = useAppStore();

  useEffect(() => {
    // Initialize theme on mount
    const savedMode = localStorage.getItem('themeMode') || 'system';
    console.log('Initializing theme with saved mode:', savedMode);
    
    if (savedMode !== themeMode) {
      setThemeMode(savedMode as any);
    } else {
      // Force apply current theme
      setThemeMode(themeMode);
    }

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleSystemThemeChange = () => {
      const currentMode = useAppStore.getState().themeMode;
      if (currentMode === 'system') {
        console.log('System theme changed, updating...');
        setThemeMode('system');
      }
    };

    mediaQuery.addEventListener('change', handleSystemThemeChange);
    
    return () => {
      mediaQuery.removeEventListener('change', handleSystemThemeChange);
    };
  }, []);

  return null;
};