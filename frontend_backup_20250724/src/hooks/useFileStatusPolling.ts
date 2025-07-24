import { useState, useEffect, useCallback, useRef } from 'react';
import { apiService } from '../services/apiService';

interface FileStatus {
  id: string;
  filename: string;
  status: 'uploaded' | 'indexing' | 'indexed' | 'error';
  chunk_count?: number;
  error_message?: string;
  progress?: number;
  last_updated?: string;
}

interface UseFileStatusPollingProps {
  enabled?: boolean;
  interval?: number;
  onStatusChange?: (fileId: string, status: FileStatus) => void;
}

export const useFileStatusPolling = ({
  enabled = true,
  interval = 2000,
  onStatusChange
}: UseFileStatusPollingProps = {}) => {
  const [fileStatuses, setFileStatuses] = useState<Map<string, FileStatus>>(new Map());
  const [isPolling, setIsPolling] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const trackedFiles = useRef<Set<string>>(new Set());

  // Add file to tracking
  const trackFile = useCallback((fileId: string, filename: string) => {
    trackedFiles.current.add(fileId);
    
    // Set initial status
    const initialStatus: FileStatus = {
      id: fileId,
      filename,
      status: 'uploaded',
      progress: 0,
      last_updated: new Date().toISOString()
    };
    
    setFileStatuses(prev => {
      const newMap = new Map(prev);
      newMap.set(fileId, initialStatus);
      return newMap;
    });
    
    onStatusChange?.(fileId, initialStatus);
  }, [onStatusChange]);

  // Remove file from tracking
  const untrackFile = useCallback((fileId: string) => {
    trackedFiles.current.delete(fileId);
    setFileStatuses(prev => {
      const newMap = new Map(prev);
      newMap.delete(fileId);
      return newMap;
    });
  }, []);

  // Poll for status updates
  const pollStatuses = useCallback(async () => {
    if (trackedFiles.current.size === 0) return;

    try {
      const fileIds = Array.from(trackedFiles.current);
      
      // Get current status for all tracked files
      const statusPromises = fileIds.map(async (fileId) => {
        try {
          const response = await apiService.get(`/api/v1/training/files/${fileId}/status`);
          return response.success ? { fileId, ...(response.data as any) } : null;
        } catch (error) {
          console.error(`Error polling status for ${fileId}:`, error);
          return null;
        }
      });

      const results = await Promise.all(statusPromises);
      
      results.forEach((result: any) => {
        if (result) {
          const { fileId, ...statusData } = result;
          const newStatus: FileStatus = {
            id: fileId,
            filename: statusData.filename || 'Unknown',
            status: statusData.processing_status || 'uploaded',
            chunk_count: statusData.chunk_count,
            error_message: statusData.error_message,
            progress: getProgressFromStatus(statusData.processing_status),
            last_updated: new Date().toISOString()
          };

          setFileStatuses(prev => {
            const oldStatus = prev.get(fileId);
            if (!oldStatus || oldStatus.status !== newStatus.status) {
              onStatusChange?.(fileId, newStatus);
            }
            
            const newMap = new Map(prev);
            newMap.set(fileId, newStatus);
            return newMap;
          });

          // Auto-remove completed files after 30 seconds
          if (newStatus.status === 'indexed' || newStatus.status === 'error') {
            setTimeout(() => {
              untrackFile(fileId);
            }, 30000);
          }
        }
      });
    } catch (error) {
      console.error('Error polling file statuses:', error);
    }
  }, [onStatusChange, untrackFile]);

  // Start polling
  const startPolling = useCallback(() => {
    if (isPolling || !enabled) return;
    
    setIsPolling(true);
    intervalRef.current = setInterval(pollStatuses, interval);
  }, [isPolling, enabled, pollStatuses, interval]);

  // Stop polling
  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
  }, []);

  // Auto-start/stop polling based on tracked files
  useEffect(() => {
    if (trackedFiles.current.size > 0 && enabled) {
      startPolling();
    } else {
      stopPolling();
    }
  }, [enabled, startPolling, stopPolling]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return {
    fileStatuses,
    isPolling,
    trackFile,
    untrackFile,
    startPolling,
    stopPolling,
    pollStatuses
  };
};

// Helper function to get progress percentage from status
const getProgressFromStatus = (status: string): number => {
  switch (status) {
    case 'uploaded': return 25;
    case 'indexing': return 75;
    case 'indexed': return 100;
    case 'error': return 0;
    default: return 0;
  }
};

// Hook for single file status
export const useFileStatus = (fileId: string, filename: string) => {
  const { fileStatuses, trackFile, untrackFile } = useFileStatusPolling();
  
  useEffect(() => {
    if (fileId && filename) {
      trackFile(fileId, filename);
      
      return () => {
        untrackFile(fileId);
      };
    }
  }, [fileId, filename, trackFile, untrackFile]);

  return fileStatuses.get(fileId);
};