import React, { useState } from 'react';
import { MessageCircle, Code, ChevronDown } from 'lucide-react';
import { Message } from '../../types';
import { apiService } from '../../services/apiService';

// Simple markdown to HTML formatter
function formatMarkdownToHtml(text: string): string {
  let html = text;
  
  // Headers
  html = html.replace(/### (.*?)$/gm, '<h3 class="text-lg font-semibold mt-4 mb-2 text-gray-900">$1</h3>');
  html = html.replace(/## (.*?)$/gm, '<h2 class="text-xl font-bold mt-4 mb-3 text-gray-900">$1</h2>');
  
  // Bold text
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>');
  
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code class="bg-gray-200 px-1 py-0.5 rounded text-sm font-mono">$1</code>');
  
  // Process bullet points
  const lines = html.split('\n');
  const processedLines = [];
  let inList = false;
  
  for (let line of lines) {
    if (line.startsWith('• ')) {
      if (!inList) {
        processedLines.push('<ul class="list-disc pl-4 mb-3">');
        inList = true;
      }
      processedLines.push(`<li class="mb-1">${line.substring(2)}</li>`);
    } else {
      if (inList) {
        processedLines.push('</ul>');
        inList = false;
      }
      processedLines.push(line);
    }
  }
  
  if (inList) {
    processedLines.push('</ul>');
  }
  
  html = processedLines.join('\n');
  
  // Line breaks and paragraphs
  html = html.replace(/\n\n+/g, '</p><p class="mb-3">');
  html = html.replace(/\n/g, '<br/>');
  
  // Wrap in paragraph if not already wrapped
  if (!html.startsWith('<')) {
    html = '<p class="mb-3">' + html + '</p>';
  }
  
  return html;
}

type ChatMode = 'qa' | 'xml_generator';

interface ChatMessage extends Message {
  mode?: ChatMode;
  metadata?: {
    sources?: string[];
    confidence?: number;
    xml_valid?: boolean;
    requirements?: any;
  };
}

interface DualModeChatProps {
  className?: string;
}

export const DualModeChat: React.FC<DualModeChatProps> = ({ className = '' }) => {
  const [selectedMode, setSelectedMode] = useState<ChatMode>('qa');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [input, setInput] = useState('');

  const modes = [
    {
      id: 'qa' as ChatMode,
      name: 'Q&A Expert',
      icon: MessageCircle,
      description: 'Beantwortet Fragen zur StreamWorks-Dokumentation',
      color: 'bg-blue-500',
      placeholder: 'Frage zur StreamWorks-Dokumentation...'
    },
    {
      id: 'xml_generator' as ChatMode,
      name: 'XML Generator',
      icon: Code,
      description: 'Erstellt XML-Streams basierend auf Anforderungen',
      color: 'bg-green-500',
      placeholder: 'Beschreibe den gewünschten Stream...'
    }
  ];

  const selectedModeConfig = modes.find(m => m.id === selectedMode)!;

  const sendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      text: message,
      sender: 'user',
      timestamp: new Date(),
      type: 'text',
      mode: selectedMode
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setInput('');

    try {
      // Call dual-mode API
      const response = await apiService.sendDualModeMessage(message, selectedMode);

      const aiMessage: ChatMessage = {
        id: crypto.randomUUID(),
        text: response.response,
        sender: 'ai',
        timestamp: new Date(),
        type: selectedMode === 'xml_generator' ? 'xml' : 'text',
        mode: response.mode_used as ChatMode,
        metadata: {
          sources: response.sources,
          confidence: response.metadata?.confidence,
          xml_valid: response.metadata?.xml_valid,
          requirements: response.metadata?.requirements
        }
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        text: 'Entschuldigung, bei der Verarbeitung Ihrer Anfrage ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.',
        sender: 'ai',
        timestamp: new Date(),
        type: 'text',
        mode: selectedMode
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className={`bg-white rounded-xl shadow-lg overflow-hidden ${className}`}>
      {/* Mode Selection Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="relative">
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="w-full max-w-md flex items-center justify-between px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className={`w-8 h-8 rounded-full ${selectedModeConfig.color} flex items-center justify-center`}>
                <selectedModeConfig.icon className="w-4 h-4 text-white" />
              </div>
              <div className="text-left">
                <div className="font-medium text-gray-900">{selectedModeConfig.name}</div>
                <div className="text-sm text-gray-500">{selectedModeConfig.description}</div>
              </div>
            </div>
            <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Dropdown Menu */}
          {isDropdownOpen && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-w-md">
              {modes.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => {
                    setSelectedMode(mode.id);
                    setIsDropdownOpen(false);
                  }}
                  className={`w-full flex items-center space-x-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors first:rounded-t-lg last:rounded-b-lg ${
                    selectedMode === mode.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                  }`}
                >
                  <div className={`w-8 h-8 rounded-full ${mode.color} flex items-center justify-center`}>
                    <mode.icon className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{mode.name}</div>
                    <div className="text-sm text-gray-500">{mode.description}</div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Enhanced Message List */}
      <div className="h-96 overflow-y-auto">
        <EnhancedMessageList 
          messages={messages} 
          isLoading={isLoading} 
          selectedMode={selectedMode}
          modes={modes}
        />
      </div>

      {/* Enhanced Input */}
      <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={selectedModeConfig.placeholder}
            disabled={isLoading}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <selectedModeConfig.icon className="w-4 h-4" />
            )}
            <span>{isLoading ? 'Arbeitet...' : 'Senden'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

interface EnhancedMessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
  selectedMode: ChatMode;
  modes: any[];
}

const EnhancedMessageList: React.FC<EnhancedMessageListProps> = ({ 
  messages, 
  isLoading, 
  selectedMode,
  modes 
}) => {
  return (
    <div className="p-4 space-y-4">
      {/* Welcome Message */}
      {messages.length === 0 && (
        <div className="text-center py-8">
          <div className="text-gray-500 mb-4">
            <MessageCircle className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Willkommen bei StreamWorks-KI!
            </h3>
            <p className="text-sm text-gray-600 max-w-md mx-auto">
              Wähle einen Modus und stelle deine Frage oder beschreibe deinen gewünschten Stream.
            </p>
          </div>
        </div>
      )}

      {/* Messages */}
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-3xl px-4 py-3 rounded-lg ${
              message.sender === 'user'
                ? 'bg-blue-500 text-white ml-12'
                : 'bg-gray-100 text-gray-800 mr-12'
            }`}
          >
            {/* AI Message Header */}
            {message.sender === 'ai' && message.mode && (
              <div className="flex items-center mb-2">
                <div className={`w-6 h-6 rounded-full ${
                  modes.find(m => m.id === message.mode)?.color || 'bg-gray-500'
                } flex items-center justify-center mr-2`}>
                  {React.createElement(
                    modes.find(m => m.id === message.mode)?.icon || MessageCircle,
                    { className: 'w-3 h-3 text-white' }
                  )}
                </div>
                <span className="text-xs font-medium text-gray-600">
                  {modes.find(m => m.id === message.mode)?.name}
                </span>
                {message.metadata?.confidence && (
                  <span className="ml-2 text-xs text-gray-500">
                    • {Math.round(message.metadata.confidence * 100)}% Vertrauen
                  </span>
                )}
              </div>
            )}

            {/* Message Content */}
            <div className={`prose prose-sm max-w-none ${
              message.sender === 'user' ? 'prose-invert' : ''
            }`}>
              {message.type === 'xml' ? (
                <pre className="bg-gray-800 text-green-400 p-3 rounded text-xs overflow-x-auto">
                  <code>{message.text.replace(/```xml\n?|\n?```/g, '')}</code>
                </pre>
              ) : (
                <div dangerouslySetInnerHTML={{ 
                  __html: formatMarkdownToHtml(message.text)
                }} />
              )}
            </div>

            {/* Sources Footer (Q&A Mode) */}
            {message.metadata?.sources && message.metadata.sources.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-200">
                <div className="text-xs text-gray-500">
                  <strong>📚 Quellen:</strong> {message.metadata.sources.join(', ')}
                </div>
              </div>
            )}

            {/* XML Validation Footer (XML Mode) */}
            {message.metadata?.xml_valid !== undefined && (
              <div className="mt-2 pt-2 border-t border-gray-200">
                <div className={`text-xs ${
                  message.metadata.xml_valid ? 'text-green-600' : 'text-red-600'
                }`}>
                  {message.metadata.xml_valid ? '✅ XML ist gültig' : '❌ XML-Validierung fehlgeschlagen'}
                </div>
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Loading Indicator */}
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-100 px-4 py-3 rounded-lg mr-12">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              <span className="text-sm text-gray-600">
                {modes.find(m => m.id === selectedMode)?.name} arbeitet...
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};