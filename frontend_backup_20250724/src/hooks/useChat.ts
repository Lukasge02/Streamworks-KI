import { useState, useCallback } from 'react';
import { Message } from '../types';
import { apiService } from '../services/apiService';
import { FormatUtils } from '../utils/formatUtils';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hallo! Ich bin SKI - die Streamworks-KI. Wie kann ich Ihnen bei der Workload-Automatisierung helfen?',
      sender: 'ai',
      timestamp: new Date(),
      type: 'text'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;

    // User message
    const userMessage: Message = {
      id: FormatUtils.generateMessageId(),
      text,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await apiService.sendMessage(text);
      
      if (response.success && response.data) {
        const aiMessage: Message = {
          id: FormatUtils.generateMessageId(),
          text: response.data,
          sender: 'ai',
          timestamp: new Date(),
          type: FormatUtils.isXmlContent(response.data) ? 'xml' : 'text'
        };
        
        setMessages(prev => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addMessage = useCallback((message: Message) => {
    setMessages(prev => [...prev, message]);
  }, []);

  return {
    messages,
    isLoading,
    sendMessage,
    addMessage
  };
};