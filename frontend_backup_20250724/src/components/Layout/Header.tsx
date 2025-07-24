import React from 'react';
import { Sparkles } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 shadow-2xl border-b border-white/10">
      <div className="w-full px-4">
        <div className="flex items-center py-4 relative">
          <div className="flex items-center space-x-4">
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 px-4 py-2 rounded-full">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-yellow-400 animate-pulse" />
                <span className="text-white text-sm font-medium">Online</span>
              </div>
            </div>
            <div className="text-left">
              <h1 className="text-2xl font-bold text-white mb-1">Streamworks-KI</h1>
              <p className="text-blue-100 text-xs font-medium">Intelligente Workload-Automatisierung</p>
            </div>
          </div>
          
          <div className="absolute left-1/2 transform -translate-x-1/2 flex flex-col items-center">
            <div className="relative">
              <img 
                src="/logo.png" 
                alt="Streamworks-KI Logo" 
                className="w-40 h-40 object-contain drop-shadow-lg"
              />
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full border-2 border-white animate-pulse"></div>
            </div>
          </div>
          
          <div className="ml-auto flex items-center space-x-2">
            {/* Settings moved to sidebar */}
          </div>
        </div>
      </div>
    </header>
  );
};