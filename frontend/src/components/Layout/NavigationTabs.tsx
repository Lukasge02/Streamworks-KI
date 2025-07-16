import React, { useState } from 'react';
import { MessageSquare, Database, Grid, Code, ChevronLeft, ChevronRight, Settings, LogOut, BarChart3, Activity } from 'lucide-react';
import { TabType } from '../../types';

// Enterprise status indicator component
const StatusIndicator: React.FC<{ status: 'active' | 'processing' | 'maintenance' }> = ({ status }) => {
  const statusConfig = {
    active: { color: 'bg-green-500', pulse: false },
    processing: { color: 'bg-yellow-500', pulse: true },
    maintenance: { color: 'bg-red-500', pulse: true }
  };
  
  const config = statusConfig[status];
  
  return (
    <div className={`w-2 h-2 rounded-full ${config.color} ${config.pulse ? 'animate-pulse' : ''}`} />
  );
};
import { useAppStore } from '../../store/appStore';

const tabs = [
  { id: 'chat' as TabType, label: 'Q&A', icon: MessageSquare, description: 'Intelligente Unterhaltung', color: 'from-blue-500 to-purple-600' },
  { id: 'training' as TabType, label: 'Training Data', icon: Database, description: 'Enterprise Dokumentenverwaltung', color: 'from-green-500 to-teal-600' },
  { id: 'chunks' as TabType, label: 'Chunks Analysis', icon: Grid, description: 'Enterprise Chunk-Visualisierung', color: 'from-orange-500 to-red-600' },
  { id: 'analytics' as TabType, label: 'Analytics', icon: BarChart3, description: 'Performance & Quality Metrics', color: 'from-indigo-500 to-purple-600' },
  { id: 'xml' as TabType, label: 'XML Generator', icon: Code, description: 'Stream-Generierung', color: 'from-purple-500 to-pink-600' }
];

export const NavigationSidebar: React.FC = () => {
  const { activeTab, setActiveTab } = useAppStore();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <nav className={`bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-r border-gray-200/50 dark:border-gray-700/50 shadow-sm h-full transition-all duration-300 ${isCollapsed ? 'w-20' : 'w-64'}`}>
      <div className="p-4 h-full flex flex-col">
        <div className="flex-1 space-y-2">
          {tabs.map(({ id, label, icon: Icon, description, color }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`w-full flex items-center ${isCollapsed ? 'justify-center px-0' : 'space-x-3 px-3'} py-3 rounded-lg font-medium text-sm transition-all relative group ${
                activeTab === id
                  ? `bg-gradient-to-r ${color} text-white shadow-lg`
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
              title={isCollapsed ? `${label} - ${description}` : ''}
            >
              <div className={`${isCollapsed ? 'p-2' : 'p-2'} rounded-lg flex-shrink-0 ${
                activeTab === id
                  ? 'bg-white/20'
                  : 'bg-gray-100 dark:bg-gray-800 group-hover:bg-gray-200 dark:group-hover:bg-gray-700'
              }`}>
                <Icon className="h-4 w-4" />
              </div>
              {!isCollapsed && (
                <div className="text-left flex-1">
                  <div className="font-semibold">{label}</div>
                  <div className={`text-xs ${
                    activeTab === id ? 'text-white/80' : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    {description}
                  </div>
                </div>
              )}
            </button>
          ))}
        </div>
        <div className="mt-4 space-y-2">
          <button
            onClick={() => setActiveTab('settings')}
            className={`w-full flex items-center ${isCollapsed ? 'justify-center px-0' : 'space-x-3 px-3'} py-3 rounded-lg font-medium text-sm transition-all relative group ${
              activeTab === 'settings'
                ? 'bg-gradient-to-r from-gray-500 to-gray-600 text-white shadow-lg'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800'
            }`}
            title={isCollapsed ? 'Einstellungen - Konfiguration' : ''}
          >
            <div className={`${isCollapsed ? 'p-2' : 'p-2'} rounded-lg flex-shrink-0 ${
              activeTab === 'settings'
                ? 'bg-white/20'
                : 'bg-gray-100 dark:bg-gray-800 group-hover:bg-gray-200 dark:group-hover:bg-gray-700'
            }`}>
              <Settings className="h-4 w-4" />
            </div>
            {!isCollapsed && (
              <div className="text-left flex-1">
                <div className="font-semibold">Einstellungen</div>
                <div className={`text-xs ${
                  activeTab === 'settings' ? 'text-white/80' : 'text-gray-500 dark:text-gray-400'
                }`}>
                  Konfiguration
                </div>
              </div>
            )}
          </button>
          <button
            className={`w-full flex items-center ${isCollapsed ? 'justify-center px-0' : 'space-x-3 px-3'} py-3 rounded-lg font-medium text-sm transition-all text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800`}
            title={isCollapsed ? 'Abmelden' : ''}
          >
            <div className={`${isCollapsed ? 'p-3' : 'p-2'} rounded-lg flex-shrink-0 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700`}>
              <LogOut className="h-4 w-4" />
            </div>
            {!isCollapsed && (
              <div className="text-left flex-1">
                <div className="font-semibold">Abmelden</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Sitzung beenden</div>
              </div>
            )}
          </button>
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="mt-2 p-3 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-all w-full flex items-center justify-center"
            title={isCollapsed ? 'Sidebar ausfahren' : 'Sidebar einklappen'}
          >
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </nav>
  );
};