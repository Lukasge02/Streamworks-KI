import React from 'react';
import { Database, BarChart3, FileText } from 'lucide-react';

export const SimpleChunksTab: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-600 to-red-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">🧩 Chunks Übersicht</h1>
        <p className="text-orange-100">Detaillierte Analyse der Chunk-Qualität und -Verteilung</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Chunks</p>
              <p className="text-2xl font-bold text-gray-900">34</p>
            </div>
            <BarChart3 className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Indexierte Dateien</p>
              <p className="text-2xl font-bold text-gray-900">6</p>
            </div>
            <FileText className="w-8 h-8 text-green-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Durchschn. Qualität</p>
              <p className="text-2xl font-bold text-gray-900">80%</p>
            </div>
            <Database className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Quality Distribution */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Qualitätsverteilung</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">12</div>
            <div className="text-sm text-gray-600">Exzellent</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">15</div>
            <div className="text-sm text-gray-600">Gut</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">7</div>
            <div className="text-sm text-gray-600">Akzeptabel</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">0</div>
            <div className="text-sm text-gray-600">Niedrig</div>
          </div>
        </div>
      </div>

      {/* System Info */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">ℹ️ System-Information</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Chunks Größe (klein)</span>
            <span className="text-sm font-medium text-gray-900">2</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Chunks Größe (mittel)</span>
            <span className="text-sm font-medium text-gray-900">29</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Chunks Größe (groß)</span>
            <span className="text-sm font-medium text-gray-900">3</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Durchschnittliche Länge</span>
            <span className="text-sm font-medium text-gray-900">667 Zeichen</span>
          </div>
        </div>
      </div>
    </div>
  );
};