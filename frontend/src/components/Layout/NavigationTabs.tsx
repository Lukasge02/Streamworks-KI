import React from 'react';
import { MessageSquare, Database, Grid } from 'lucide-react';
import { TabType } from '../../types';
import { useAppStore } from '../../store/appStore';

const tabs = [
  { id: 'chat' as TabType, label: 'Chat', icon: MessageSquare },
  { id: 'training' as TabType, label: 'Training Data', icon: Database },
  { id: 'chunks' as TabType, label: 'ChromaDB Chunks', icon: Grid }
];

export const NavigationTabs: React.FC = () => {
  const { activeTab, setActiveTab } = useAppStore();

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-8">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};