import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Bot, User, Copy, Check, Loader2 } from 'lucide-react';
import { Message } from '../../types';
import { apiService } from '../../services/apiService';
import { motion, AnimatePresence } from 'framer-motion';

interface ChatMessage extends Message {
  metadata?: {
    sources?: string[];
    confidence?: number;
    processing_time?: number;
  };
}

export const ModernChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const sendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      text: message,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setInput('');

    try {
      const response = await apiService.sendDualModeMessage(message, 'qa');

      const aiMessage: ChatMessage = {
        id: crypto.randomUUID(),
        text: response.response,
        sender: 'ai',
        timestamp: new Date(),
        type: 'text',
        metadata: {
          sources: response.sources,
          confidence: response.metadata?.confidence,
          processing_time: response.processing_time
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
        type: 'text'
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const copyToClipboard = (text: string, messageId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(messageId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const formatMarkdown = (text: string): string => {
    let html = text;
    
    // Headers
    html = html.replace(/### (.*?)$/gm, '<h3 class="text-lg font-bold mt-4 mb-2 text-gray-800">$1</h3>');
    html = html.replace(/## (.*?)$/gm, '<h2 class="text-xl font-bold mt-6 mb-3 text-gray-900">$1</h2>');
    
    // Bold text
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-gray-900">$1</strong>');
    
    // Code blocks
    html = html.replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto my-4"><code>$1</code></pre>');
    
    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code class="bg-gray-200 px-2 py-1 rounded text-sm font-mono text-gray-800">$1</code>');
    
    // Bullet points
    html = html.replace(/^• (.*)$/gm, '<li class="ml-4 mb-1">• $1</li>');
    html = html.replace(/(<li.*?<\/li>\n?)+/g, '<ul class="my-3">$&</ul>');
    
    // Line breaks
    html = html.replace(/\n\n+/g, '</p><p class="mb-4">');
    html = html.replace(/\n/g, '<br/>');
    
    // Wrap in paragraph
    if (!html.startsWith('<')) {
      html = '<p class="mb-4">' + html + '</p>';
    }
    
    return html;
  };

  return (
    <div className="relative h-[calc(100vh-200px)] bg-gradient-to-br from-gray-50 via-white to-gray-50 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-lg border border-gray-200/50">
      {/* Decorative Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-400/10 rounded-full blur-3xl"></div>
      </div>

      {/* Header */}
      <div className="relative bg-white/80 backdrop-blur-md border-b border-gray-200/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <Bot className="w-7 h-7 text-white" />
              </div>
              <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">StreamWorks AI Assistant</h2>
              <p className="text-sm text-gray-500">Powered by Advanced RAG Technology</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-yellow-500 animate-pulse" />
            <span className="text-sm font-medium text-gray-600">Online</span>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="relative flex-1 overflow-y-auto px-6 py-4 space-y-6" style={{ height: 'calc(100% - 140px)' }}>
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="absolute inset-0 flex items-center justify-center"
            >
              <div className="text-center max-w-md">
                <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-2xl">
                  <Bot className="w-12 h-12 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-800 mb-3">
                  Willkommen bei StreamWorks AI
                </h3>
                <p className="text-gray-600 mb-6">
                  Ihre intelligente Assistenz für alle Fragen rund um StreamWorks. 
                  Stellen Sie mir eine Frage und ich helfe Ihnen gerne weiter!
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {['Wie erstelle ich einen Batch?', 'Was ist ein Agent?', 'Hilfe bei XML-Konfiguration'].map((suggestion, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInput(suggestion)}
                      className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-all hover:shadow-md"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-3xl ${message.sender === 'user' ? 'ml-12' : 'mr-12'}`}>
                <div className="flex items-start space-x-3">
                  {message.sender === 'ai' && (
                    <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                      <Bot className="w-6 h-6 text-white" />
                    </div>
                  )}
                  
                  <div className="flex-1">
                    <div className={`relative group ${
                      message.sender === 'user'
                        ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                        : 'bg-white/80 backdrop-blur-sm border border-gray-200/50'
                    } rounded-2xl px-5 py-4 shadow-lg`}>
                      
                      {/* Copy button for AI messages */}
                      {message.sender === 'ai' && (
                        <button
                          onClick={() => copyToClipboard(message.text, message.id)}
                          className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-gray-100 rounded-lg"
                        >
                          {copiedId === message.id ? (
                            <Check className="w-4 h-4 text-green-600" />
                          ) : (
                            <Copy className="w-4 h-4 text-gray-500" />
                          )}
                        </button>
                      )}

                      {/* Message content */}
                      <div className={message.sender === 'user' ? 'text-white' : 'text-gray-800'}>
                        {message.sender === 'user' ? (
                          <p>{message.text}</p>
                        ) : (
                          <div 
                            className="prose prose-sm max-w-none"
                            dangerouslySetInnerHTML={{ __html: formatMarkdown(message.text) }}
                          />
                        )}
                      </div>

                      {/* Metadata footer */}
                      {message.sender === 'ai' && message.metadata && (
                        <div className="mt-4 pt-3 border-t border-gray-200/50">
                          <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500">
                            {message.metadata.confidence !== undefined && (
                              <div className="flex items-center space-x-1">
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                <span>{Math.round(message.metadata.confidence * 100)}% Vertrauen</span>
                              </div>
                            )}
                            {message.metadata.processing_time && (
                              <div className="flex items-center space-x-1">
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                <span>{message.metadata.processing_time.toFixed(2)}s Verarbeitung</span>
                              </div>
                            )}
                            {message.metadata.sources && message.metadata.sources.length > 0 && (
                              <div className="flex items-center space-x-1">
                                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                                <span>{message.metadata.sources.length} Quellen</span>
                              </div>
                            )}
                          </div>
                          
                          {/* Sources */}
                          {message.metadata.sources && message.metadata.sources.length > 0 && (
                            <details className="mt-2">
                              <summary className="cursor-pointer text-xs text-gray-600 hover:text-gray-800">
                                Quellen anzeigen
                              </summary>
                              <div className="mt-2 space-y-1">
                                {message.metadata.sources.map((source, idx) => (
                                  <div key={idx} className="text-xs text-gray-500 pl-3">
                                    • {source}
                                  </div>
                                ))}
                              </div>
                            </details>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Timestamp */}
                    <div className={`mt-1 text-xs ${
                      message.sender === 'user' ? 'text-right text-gray-500' : 'text-gray-400'
                    }`}>
                      {new Date(message.timestamp).toLocaleTimeString('de-DE', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>

                  {message.sender === 'user' && (
                    <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-gray-600 to-gray-700 rounded-xl flex items-center justify-center shadow-lg">
                      <User className="w-6 h-6 text-white" />
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}

          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="max-w-3xl mr-12">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg animate-pulse">
                    <Bot className="w-6 h-6 text-white" />
                  </div>
                  <div className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl px-5 py-4 shadow-lg">
                    <div className="flex items-center space-x-3">
                      <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                      <div className="space-y-2">
                        <div className="h-2 w-32 bg-gray-200 rounded animate-pulse"></div>
                        <div className="h-2 w-24 bg-gray-200 rounded animate-pulse"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="absolute bottom-0 left-0 right-0 bg-white/80 backdrop-blur-md border-t border-gray-200/50 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="relative flex items-center">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Stellen Sie Ihre Frage zu StreamWorks..."
              disabled={isLoading}
              className="flex-1 px-6 py-4 pr-20 bg-gray-50/50 border border-gray-300/50 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent disabled:opacity-50 transition-all text-gray-800 placeholder-gray-500"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="absolute right-2 px-6 py-2.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center space-x-2 group"
            >
              <Send className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              <span className="font-medium">Senden</span>
            </button>
          </div>
          <div className="mt-2 text-xs text-gray-500 text-center">
            Powered by E5 Multilingual Embeddings & Mistral 7B
          </div>
        </div>
      </form>
    </div>
  );
};