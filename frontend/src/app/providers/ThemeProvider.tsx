import { useEffect } from 'react';
import type { ReactNode } from 'react';
import { useUiStore } from '../../stores/uiStore';

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const { isDark } = useUiStore();

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  return <>{children}</>;
}