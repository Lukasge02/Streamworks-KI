import { useState, useCallback } from 'react';
import { StreamConfig } from '../types';
import { StreamService } from '../services/streamService';
import { apiService } from '../services/apiService';

export const useStreamGenerator = () => {
  const [config, setConfig] = useState<StreamConfig>({
    streamName: '',
    jobName: '',
    startTime: '',
    dataSource: '',
    outputPath: '',
    schedule: 'daily'
  });
  const [isGenerating, setIsGenerating] = useState(false);

  const updateConfig = useCallback((updates: Partial<StreamConfig>) => {
    setConfig(prev => ({ ...prev, ...updates }));
  }, []);

  const generateStream = useCallback(async () => {
    const errors = StreamService.validateStreamConfig(config);
    if (errors.length > 0) {
      throw new Error(errors.join(', '));
    }

    setIsGenerating(true);
    try {
      const response = await apiService.generateStream(config);
      if (response.success && response.data) {
        return response.data;
      }
      throw new Error(response.error || 'Generierung fehlgeschlagen');
    } finally {
      setIsGenerating(false);
    }
  }, [config]);

  const resetConfig = useCallback(() => {
    setConfig({
      streamName: '',
      jobName: '',
      startTime: '',
      dataSource: '',
      outputPath: '',
      schedule: 'daily'
    });
  }, []);

  return {
    config,
    isGenerating,
    updateConfig,
    generateStream,
    resetConfig
  };
};