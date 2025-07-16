import React from 'react';
import { BarChart3, Database, Activity } from 'lucide-react';

const SimpleAnalytics: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">📊 Analytics Dashboard</h1>
        <p className="text-indigo-100">System-Metriken und Performance-Übersicht</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Dateien</p>
              <p className="text-2xl font-bold text-gray-900">6</p>
            </div>
            <Database className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Chunks</p>
              <p className="text-2xl font-bold text-gray-900">71</p>
            </div>
            <BarChart3 className="w-8 h-8 text-green-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">System Status</p>
              <p className="text-2xl font-bold text-gray-900">Online</p>
            </div>
            <Activity className="w-8 h-8 text-green-500" />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">📈 System-Übersicht</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Indexierte Dateien</span>
            <span className="text-sm font-medium text-gray-900">6 von 6</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Durchschnittliche Chunk-Größe</span>
            <span className="text-sm font-medium text-gray-900">~667 Zeichen</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Qualitätsbewertung</span>
            <span className="text-sm font-medium text-green-600">Gut (80%+)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleAnalytics;