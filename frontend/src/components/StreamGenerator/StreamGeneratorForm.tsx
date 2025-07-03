import React from 'react';
import { Zap } from 'lucide-react';
import { useStreamGenerator } from '../../hooks/useStreamGenerator';
import { useChat } from '../../hooks/useChat';
import { useAppStore } from '../../store/appStore';
import { FormatUtils } from '../../utils/formatUtils';

export const StreamGeneratorForm: React.FC = () => {
  const { config, isGenerating, updateConfig, generateStream } = useStreamGenerator();
  const { addMessage } = useChat();
  const { setActiveTab } = useAppStore();

  const handleGenerate = async () => {
    try {
      const xml = await generateStream();
      
      // Add generated XML to chat
      addMessage({
        id: FormatUtils.generateMessageId(),
        text: xml,
        sender: 'ai',
        timestamp: new Date(),
        type: 'xml'
      });
      
      // Switch to chat tab
      setActiveTab('chat');
    } catch (error) {
      console.error('Generation error:', error);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Stream Generator</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Stream Name
            </label>
            <input
              type="text"
              value={config.streamName}
              onChange={(e) => updateConfig({ streamName: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="z.B. DailyDataProcessing"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Name
            </label>
            <input
              type="text"
              value={config.jobName}
              onChange={(e) => updateConfig({ jobName: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="z.B. ProcessCSVData"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Time
            </label>
            <input
              type="time"
              value={config.startTime}
              onChange={(e) => updateConfig({ startTime: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Source
            </label>
            <input
              type="text"
              value={config.dataSource}
              onChange={(e) => updateConfig({ dataSource: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="z.B. /data/input/*.csv"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Output Path
            </label>
            <input
              type="text"
              value={config.outputPath}
              onChange={(e) => updateConfig({ outputPath: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="z.B. /data/output/processed"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Schedule
            </label>
            <select
              value={config.schedule}
              onChange={(e) => updateConfig({ schedule: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="daily">Täglich</option>
              <option value="weekly">Wöchentlich</option>
              <option value="monthly">Monatlich</option>
              <option value="hourly">Stündlich</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="mt-6">
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
        >
          <Zap className="h-5 w-5" />
          <span>{isGenerating ? 'Generiere...' : 'XML-Stream generieren'}</span>
        </button>
      </div>
    </div>
  );
};