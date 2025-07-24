import React from 'react';
import { Monitor, Moon, Sun, Settings } from 'lucide-react';
import { useAppStore } from '../../store/appStore';

const SettingsTab: React.FC = () => {
  const { themeMode, setThemeMode } = useAppStore();

  const themeOptions = [
    { id: 'system', name: 'System', icon: Monitor, description: 'Folgt den Systemeinstellungen' },
    { id: 'light', name: 'Hell', icon: Sun, description: 'Helles Design' },
    { id: 'dark', name: 'Dunkel', icon: Moon, description: 'Dunkles Design' }
  ];

  return (
    <div className="h-full bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 rounded-2xl shadow-2xl backdrop-blur-lg border border-gray-200/50 dark:border-gray-700/50 flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50 p-6">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-gray-500 to-gray-600 dark:from-gray-600 dark:to-gray-700 rounded-xl flex items-center justify-center shadow-lg">
            <Settings className="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">Einstellungen</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">Konfiguration und Einstellungen</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-xl space-y-6">
          {/* Theme Settings */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 rounded-xl p-4">
            <h3 className="text-base font-semibold text-gray-800 dark:text-gray-100 mb-3">Design-Theme</h3>
            
            <div className="flex space-x-1 p-1 bg-gray-100 dark:bg-gray-700 rounded-lg">
              {themeOptions.map((option) => (
                <button
                  key={option.id}
                  onClick={() => {
                    console.log('Theme button clicked:', option.id);
                    setThemeMode(option.id as any);
                  }}
                  className={`flex-1 flex items-center justify-center space-x-2 p-2 rounded-md transition-all ${
                    themeMode === option.id
                      ? 'bg-white dark:bg-gray-600 text-gray-800 dark:text-gray-100 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
                  }`}
                >
                  <option.icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{option.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Other Settings Sections */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 rounded-xl p-4">
            <h3 className="text-base font-semibold text-gray-800 dark:text-gray-100 mb-3">Weitere Einstellungen</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Weitere Optionen werden hier in Zukunft verfügbar sein.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsTab;