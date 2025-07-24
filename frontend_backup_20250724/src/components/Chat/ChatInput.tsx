import React, { useState, useRef } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { Message } from '../../types';
import { useFileUpload } from '../../hooks/useFileUpload';
import { FormatUtils } from '../../utils/formatUtils';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  onFileUpload: (message: Message) => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, onFileUpload }) => {
  const [input, setInput] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { isUploading, uploadFile } = useFileUpload();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      try {
        const analysis = await uploadFile(file);
        if (analysis) {
          onFileUpload({
            id: FormatUtils.generateMessageId(),
            text: `Datei analysiert: ${file.name}\n\n${analysis}`,
            sender: 'ai',
            timestamp: new Date(),
            type: 'text'
          });
        }
      } catch (error) {
        console.error('Upload error:', error);
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4">
      <div className="flex items-center space-x-2">
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <Paperclip className="h-5 w-5" />
        </button>
        
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileChange}
          className="hidden"
          accept=".bat,.cmd,.ps1,.xml"
        />
        
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Nachricht eingeben..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        
        <button
          type="submit"
          disabled={!input.trim()}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </form>
  );
};