import { useState, useCallback } from 'react';
import { apiService } from '../services/apiService';

export const useFileUpload = () => {
  const [isUploading, setIsUploading] = useState(false);

  const uploadFile = useCallback(async (file: File) => {
    setIsUploading(true);
    try {
      const response = await apiService.uploadFile(file);
      if (response.success) {
        return response.data;
      }
      throw new Error(response.error || 'Upload fehlgeschlagen');
    } finally {
      setIsUploading(false);
    }
  }, []);

  return {
    isUploading,
    uploadFile
  };
};