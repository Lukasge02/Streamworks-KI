import React from 'react';
import { MessageSquare, Database, Grid, Code } from 'lucide-react';
import { TabType } from '../../types';
import { useAppStore } from '../../store/appStore';

const tabs = [
  { id: 'chat' as TabType, label: 'AI Chat', icon: MessageSquare, description: 'Intelligente Unterhaltung', color: 'from-blue-500 to-purple-600' },
  { id: 'training' as TabType, label: 'Training Data', icon: Database, description: 'Dokumentenverwaltung', color: 'from-green-500 to-teal-600' },
  { id: 'chunks' as TabType, label: 'Vector Database', icon: Grid, description: 'ChromaDB Chunks', color: 'from-orange-500 to-red-600' },
  { id: 'xml' as TabType, label: 'XML Generator', icon: Code, description: 'Stream-Generierung', color: 'from-purple-500 to-pink-600' }
];

export const NavigationTabs: React.FC = () => {
  const { activeTab, setActiveTab } = useAppStore();

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200/50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-2">
          {tabs.map(({ id, label, icon: Icon, description, color }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex items-center space-x-3 py-4 px-6 rounded-t-xl font-medium text-sm transition-all relative group ${
                activeTab === id
                  ? `bg-gradient-to-r ${color} text-white shadow-lg`
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
              }`}
            >
              <div className={`p-2 rounded-lg ${
                activeTab === id
                  ? 'bg-white/20'
                  : 'bg-gray-100 group-hover:bg-gray-200'
              }`}>
                <Icon className="h-4 w-4" />
              </div>
              <div className="text-left">
                <div className="font-semibold">{label}</div>
                <div className={`text-xs ${
                  activeTab === id ? 'text-white/80' : 'text-gray-500'
                }`}>
                  {description}
                </div>
              </div>
              {activeTab === id && (
                <div className="absolute -bottom-px left-0 right-0 h-1 bg-gradient-to-r from-white/50 to-white/50 rounded-t-full"></div>
              )}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};