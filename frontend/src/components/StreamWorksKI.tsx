import React, { useState } from 'react';
import { Send, Upload, FileText, Settings, HelpCircle, Menu, X } from 'lucide-react';

const StreamworksKI: React.FC = () => {
  const [messages, setMessages] = useState<Array<{id: number; text: string; isUser: boolean}>>([]);
  const [inputValue, setInputValue] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('chat');

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      const newMessage = {
        id: Date.now(),
        text: inputValue,
        isUser: true
      };
      setMessages([...messages, newMessage]);
      setInputValue('');
      
      // Simulierte KI-Antwort
      setTimeout(() => {
        const aiResponse = {
          id: Date.now() + 1,
          text: "Ich bin Streamworks-KI. Wie kann ich Ihnen bei der Workload-Automatisierung helfen?",
          isUser: false
        };
        setMessages(prev => [...prev, aiResponse]);
      }, 1000);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${isSidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 bg-white shadow-lg overflow-hidden`}>
        <div className="p-4 border-b">
          <h2 className="text-xl font-bold text-gray-800">Streamworks-KI</h2>
        </div>
        <nav className="p-4">
          <button
            onClick={() => setActiveTab('chat')}
            className={`w-full text-left p-3 rounded-lg mb-2 flex items-center gap-3 ${
              activeTab === 'chat' ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-100'
            }`}
          >
            <Send size={18} />
            Chat
          </button>
          <button
            onClick={() => setActiveTab('generator')}
            className={`w-full text-left p-3 rounded-lg mb-2 flex items-center gap-3 ${
              activeTab === 'generator' ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-100'
            }`}
          >
            <FileText size={18} />
            Stream Generator
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`w-full text-left p-3 rounded-lg mb-2 flex items-center gap-3 ${
              activeTab === 'upload' ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-100'
            }`}
          >
            <Upload size={18} />
            File Upload
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`w-full text-left p-3 rounded-lg mb-2 flex items-center gap-3 ${
              activeTab === 'settings' ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-100'
            }`}
          >
            <Settings size={18} />
            Einstellungen
          </button>
          <button
            onClick={() => setActiveTab('help')}
            className={`w-full text-left p-3 rounded-lg mb-2 flex items-center gap-3 ${
              activeTab === 'help' ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-100'
            }`}
          >
            <HelpCircle size={18} />
            Hilfe
          </button>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-sm p-4 flex items-center justify-between">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          <h1 className="text-2xl font-semibold text-gray-800">
            {activeTab === 'chat' && 'Intelligenter Chat'}
            {activeTab === 'generator' && 'Stream Generator'}
            {activeTab === 'upload' && 'File Upload'}
            {activeTab === 'settings' && 'Einstellungen'}
            {activeTab === 'help' && 'Hilfe & Dokumentation'}
          </h1>
          <div className="w-10"></div>
        </header>

        {/* Content Area */}
        <div className="flex-1 p-6 overflow-auto">
          {activeTab === 'chat' && (
            <div className="max-w-4xl mx-auto h-full flex flex-col">
              <div className="flex-1 bg-white rounded-lg shadow-md p-4 mb-4 overflow-y-auto chat-scrollbar">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 mt-8">
                    <p className="mb-2">Willkommen bei Streamworks-KI!</p>
                    <p>Stellen Sie mir Fragen zur Workload-Automatisierung.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                            message.isUser
                              ? 'bg-primary-600 text-white'
                              : 'bg-gray-200 text-gray-800'
                          }`}
                        >
                          {message.text}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ihre Nachricht..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500"
                  />
                  <button
                    onClick={handleSendMessage}
                    className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
                  >
                    <Send size={18} />
                    Senden
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'generator' && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">XML Stream Generator</h2>
                <form className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Stream Name
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500"
                      placeholder="z.B. DAILY_BACKUP"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Beschreibung
                    </label>
                    <textarea
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500"
                      rows={3}
                      placeholder="Beschreiben Sie den gewünschten Workflow..."
                    />
                  </div>
                  <button
                    type="submit"
                    className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    Stream generieren
                  </button>
                </form>
              </div>
            </div>
          )}

          {activeTab === 'upload' && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Batch File Upload</h2>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <Upload size={48} className="mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600 mb-2">
                    Ziehen Sie Ihre Batch-Dateien hierher oder klicken Sie zum Auswählen
                  </p>
                  <input
                    type="file"
                    className="hidden"
                    id="file-upload"
                    multiple
                    accept=".bat,.cmd,.ps1"
                  />
                  <label
                    htmlFor="file-upload"
                    className="inline-block bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors cursor-pointer"
                  >
                    Dateien auswählen
                  </label>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Einstellungen</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      API Endpoint
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500"
                      defaultValue="http://localhost:8000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Sprache
                    </label>
                    <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500">
                      <option>Deutsch</option>
                      <option>English</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'help' && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Hilfe & Dokumentation</h2>
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold mb-2">Erste Schritte</h3>
                    <p className="text-gray-600">
                      Streamworks-KI ist eine intelligente Assistenz für die Workload-Automatisierung...
                    </p>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-2">Häufige Fragen</h3>
                    <ul className="list-disc list-inside text-gray-600 space-y-1">
                      <li>Wie erstelle ich einen neuen Stream?</li>
                      <li>Was sind die unterstützten Dateiformate?</li>
                      <li>Wie konfiguriere ich die API-Verbindung?</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StreamworksKI;