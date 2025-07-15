import React from 'react';
import { Settings, Sparkles, Zap } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 shadow-2xl border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="w-14 h-14 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-lg border border-white/20">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white animate-pulse"></div>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white mb-1">StreamWorks-KI</h1>
              <p className="text-blue-100 text-sm font-medium">Powered by Advanced AI Technology</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 px-4 py-2 rounded-full">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-yellow-400 animate-pulse" />
                <span className="text-white text-sm font-medium">Production Ready</span>
              </div>
            </div>
            <button className="p-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl hover:bg-white/20 transition-all">
              <Settings className="h-5 w-5 text-white" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};