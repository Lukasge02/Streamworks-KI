import { Link, useLocation } from 'react-router-dom';
import * as Icons from 'lucide-react';
import { NAVIGATION_ITEMS, APP_CONFIG } from '@/shared/constants';
import { useThemeStore } from '@/app/store/themeStore';

interface SidebarProps {
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export function Sidebar({ isCollapsed = false, onToggleCollapse }: SidebarProps) {
  const location = useLocation();
  const { isDark, toggleTheme } = useThemeStore();

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const getIcon = (iconName: string) => {
    const IconComponent = Icons[iconName as keyof typeof Icons] as any;
    return IconComponent ? <IconComponent size={20} /> : <Icons.Box size={20} />;
  };

  return (
    <div
      className={`
        h-screen bg-white dark:bg-neutral-900 border-r border-neutral-200 dark:border-neutral-800
        transition-all duration-300 flex flex-col
        ${isCollapsed ? 'w-16' : 'w-64'}
      `}
    >
      {/* Header */}
      <div className="p-4 border-b border-neutral-200 dark:border-neutral-800">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div>
              <h1 className="text-xl font-bold text-primary-600 dark:text-primary-400">
                {APP_CONFIG.NAME}
              </h1>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">
                v{APP_CONFIG.VERSION}
              </p>
            </div>
          )}
          
          <button
            onClick={onToggleCollapse}
            className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <Icons.PanelLeftClose size={16} className={isCollapsed ? 'rotate-180' : ''} />
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {NAVIGATION_ITEMS.map((item) => {
          const active = isActive(item.path);
          
          return (
            <Link
              key={item.id}
              to={item.path}
              className={`
                flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200
                group relative overflow-hidden
                ${active
                  ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                  : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 hover:text-neutral-900 dark:hover:text-neutral-200'
                }
              `}
              title={isCollapsed ? item.label : undefined}
            >
              <div
                className={`
                  flex-shrink-0 transition-colors duration-200
                  ${active ? 'text-primary-600 dark:text-primary-400' : ''}
                `}
              >
                {getIcon(item.icon)}
              </div>
              
              {!isCollapsed && (
                <span className="font-medium text-sm">
                  {item.label}
                </span>
              )}
              
              {/* Active indicator */}
              {active && (
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary-600 dark:bg-primary-400 rounded-r" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-neutral-200 dark:border-neutral-800">
        <button
          onClick={toggleTheme}
          className={`
            flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors w-full
            text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800
            hover:text-neutral-900 dark:hover:text-neutral-200
          `}
          title={isCollapsed ? (isDark ? 'Light mode' : 'Dark mode') : undefined}
        >
          <div className="flex-shrink-0">
            {isDark ? <Icons.Sun size={20} /> : <Icons.Moon size={20} />}
          </div>
          
          {!isCollapsed && (
            <span className="font-medium text-sm">
              {isDark ? 'Light Mode' : 'Dark Mode'}
            </span>
          )}
        </button>

        {!isCollapsed && (
          <div className="mt-4 pt-4 border-t border-neutral-200 dark:border-neutral-800">
            <div className="flex items-center space-x-2 text-xs text-neutral-500 dark:text-neutral-400">
              <Icons.Activity size={14} />
              <span>System Ready</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}