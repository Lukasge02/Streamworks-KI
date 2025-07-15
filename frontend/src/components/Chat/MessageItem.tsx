import React from 'react';
import { Message } from '../../types';
import { Copy, Download, Bot, User } from 'lucide-react';
import { FormatUtils } from '../../utils/formatUtils';

interface MessageItemProps {
  message: Message;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const isAI = message.sender === 'ai';
  
  const handleCopy = () => {
    FormatUtils.copyToClipboard(message.text);
  };
  
  const handleDownload = () => {
    if (message.type === 'xml') {
      const blob = new Blob([message.text], { type: 'application/xml' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'stream.xml';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className={`flex ${isAI ? 'justify-start' : 'justify-end'}`}>
      <div className={`flex max-w-2xl ${isAI ? 'flex-row' : 'flex-row-reverse'}`}>
        <div className={`flex-shrink-0 ${isAI ? 'mr-3' : 'ml-3'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isAI ? 'bg-blue-100' : 'bg-gray-100'
          }`}>
            {isAI ? <Bot className="h-5 w-5 text-blue-600" /> : <User className="h-5 w-5 text-gray-600" />}
          </div>
        </div>
        
        <div>
          <div className={`rounded-lg px-4 py-2 ${
            isAI ? 'bg-white border border-gray-200' : 'bg-blue-600 text-white'
          }`}>
            {message.type === 'xml' ? (
              <pre className="text-sm overflow-x-auto">{message.text}</pre>
            ) : (
              <p className="text-sm">{message.text}</p>
            )}
          </div>
          
          <div className="flex items-center mt-1 space-x-2">
            <span className="text-xs text-gray-500">
              {FormatUtils.formatTimestamp(message.timestamp)}
            </span>
            {isAI && (
              <>
                <button
                  onClick={handleCopy}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  title="Kopieren"
                >
                  <Copy className="h-3 w-3" />
                </button>
                {message.type === 'xml' && (
                  <button
                    onClick={handleDownload}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                    title="Download"
                  >
                    <Download className="h-3 w-3" />
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};