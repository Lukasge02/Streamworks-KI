import React from 'react';
import { Settings } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-lg border-b border-blue-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-4">
            <img 
              src="/logo.png" 
              alt="StreamWorks-KI Logo" 
              className="h-12 w-auto object-contain"
            />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">StreamWorks-KI</h1>
              <p className="text-sm text-gray-600">Intelligente Workload-Automatisierung</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 px-3 py-1 rounded-full">
              <span className="text-green-800 text-sm font-medium">Beta v1.0</span>
            </div>
            <Settings className="h-5 w-5 text-gray-500 cursor-pointer hover:text-gray-700" />
          </div>
        </div>
      </div>
    </header>
  );
};