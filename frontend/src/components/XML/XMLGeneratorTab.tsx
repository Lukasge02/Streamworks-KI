import React, { useState, useCallback, useEffect } from 'react';
import { 
  MessageSquare, 
  FileText, 
  Play, 
  Download, 
  Copy, 
  Check, 
  AlertCircle,
  Settings,
  Code,
  Zap,
  File
} from 'lucide-react';
import Editor from '@monaco-editor/react';

interface XMLTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  parameters?: string[];
  file_path?: string;
}

interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export const XMLGeneratorTab: React.FC = () => {
  const [activeMode, setActiveMode] = useState<'chat' | 'form' | 'template'>('chat');
  const [chatInput, setChatInput] = useState('');
  const [formData, setFormData] = useState({
    streamName: '',
    description: '',
    sourceSystem: '',
    targetSystem: '',
    dataFormat: 'JSON',
    schedule: 'daily'
  });
  const [generatedXML, setGeneratedXML] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [copied, setCopied] = useState(false);
  const [templates, setTemplates] = useState<XMLTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<XMLTemplate | null>(null);
  const [templateParameters, setTemplateParameters] = useState<{[key: string]: string}>({});

  // Load templates on component mount
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const response = await fetch('/api/v1/xml/templates');
        const result = await response.json();
        setTemplates(result.templates || []);
      } catch (error) {
        console.error('Failed to load templates:', error);
      }
    };
    
    loadTemplates();
  }, []);

  const handleChatGeneration = useCallback(async () => {
    if (!chatInput.trim()) return;
    
    setIsGenerating(true);
    try {
      const response = await fetch('/api/v1/xml/generate-from-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: chatInput,
          context: 'streamworks'
        }),
      });
      
      const result = await response.json();
      setGeneratedXML(result.xml);
      setValidation(result.validation);
      
    } catch (error) {
      console.error('XML Generation failed:', error);
    } finally {
      setIsGenerating(false);
    }
  }, [chatInput]);

  const handleFormGeneration = useCallback(async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/v1/xml/generate-from-form', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      const result = await response.json();
      setGeneratedXML(result.xml);
      setValidation(result.validation);
      
    } catch (error) {
      console.error('XML Generation failed:', error);
    } finally {
      setIsGenerating(false);
    }
  }, [formData]);

  const handleTemplateGeneration = useCallback(async () => {
    if (!selectedTemplate) return;
    
    setIsGenerating(true);
    try {
      const response = await fetch('/api/v1/xml/generate-from-template', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template_id: selectedTemplate.id,
          parameters: templateParameters
        }),
      });
      
      const result = await response.json();
      setGeneratedXML(result.xml);
      setValidation(result.validation);
      
    } catch (error) {
      console.error('Template XML Generation failed:', error);
    } finally {
      setIsGenerating(false);
    }
  }, [selectedTemplate, templateParameters]);

  const copyToClipboard = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(generatedXML);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Copy failed:', error);
    }
  }, [generatedXML]);

  const downloadXML = useCallback(() => {
    const blob = new Blob([generatedXML], { type: 'application/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `streamworks-config-${Date.now()}.xml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [generatedXML]);

  return (
    <div className="h-full flex bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900">
      {/* Left Panel - Input Interface */}
      <div className="w-1/2 flex flex-col border-r border-gray-200/50 dark:border-gray-700/50">
        {/* Mode Selector */}
        <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
            <Code className="w-8 h-8 mr-3 text-purple-600" />
            StreamWorks XML Generator
          </h2>
          
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveMode('chat')}
              className={`flex-1 flex items-center justify-center px-3 py-3 rounded-xl font-medium transition-all duration-300 text-sm ${
                activeMode === 'chat'
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/25'
                  : 'bg-white/60 dark:bg-gray-800/60 text-gray-700 dark:text-gray-300 hover:bg-white/80 hover:shadow-md border border-gray-200/50 dark:border-gray-700/50'
              }`}
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              KI-Chat
            </button>
            <button
              onClick={() => setActiveMode('form')}
              className={`flex-1 flex items-center justify-center px-3 py-3 rounded-xl font-medium transition-all duration-300 text-sm ${
                activeMode === 'form'
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/25'
                  : 'bg-white/60 dark:bg-gray-800/60 text-gray-700 dark:text-gray-300 hover:bg-white/80 hover:shadow-md border border-gray-200/50 dark:border-gray-700/50'
              }`}
            >
              <FileText className="w-4 h-4 mr-2" />
              Formular
            </button>
            <button
              onClick={() => setActiveMode('template')}
              className={`flex-1 flex items-center justify-center px-3 py-3 rounded-xl font-medium transition-all duration-300 text-sm ${
                activeMode === 'template'
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/25'
                  : 'bg-white/60 dark:bg-gray-800/60 text-gray-700 dark:text-gray-300 hover:bg-white/80 hover:shadow-md border border-gray-200/50 dark:border-gray-700/50'
              }`}
            >
              <File className="w-4 h-4 mr-2" />
              Templates
            </button>
          </div>
        </div>

        {/* Input Area */}
        <div className="flex-1 flex flex-col p-6 bg-white/60 dark:bg-gray-900/60 backdrop-blur-sm">
          {activeMode === 'chat' && (
            <>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                <Zap className="w-5 h-5 mr-2 text-purple-600" />
                KI-Powered XML Generation
              </h3>
              <div className="flex-1 flex flex-col space-y-4">
                <textarea
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Beschreibe deine StreamWorks-Konfiguration...

Beispiele:
• Erstelle einen Stream von SAP zu Salesforce für Kundendaten
• Ich brauche eine tägliche Synchronisation zwischen HR-System und Active Directory  
• Konfiguriere einen Event-basierten Stream für Bestellungen"
                  className="flex-1 p-4 border border-gray-300 dark:border-gray-600 rounded-xl bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none text-gray-900 dark:text-gray-100 placeholder-gray-500"
                  rows={12}
                />
                <button
                  onClick={handleChatGeneration}
                  disabled={!chatInput.trim() || isGenerating}
                  className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-medium shadow-lg shadow-purple-500/25 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      KI generiert XML...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5 mr-2" />
                      XML generieren
                    </>
                  )}
                </button>
              </div>
            </>
          )}

          {activeMode === 'form' && (
            <>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                <Settings className="w-5 h-5 mr-2 text-purple-600" />
                StreamWorks Konfiguration
              </h3>
              <div className="flex-1 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Stream Name
                  </label>
                  <input
                    type="text"
                    value={formData.streamName}
                    onChange={(e) => setFormData(prev => ({ ...prev, streamName: e.target.value }))}
                    placeholder="z.B. SAP-Salesforce-Sync"
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white/80 dark:bg-gray-800/80 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Beschreibung
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Kurze Beschreibung des Streams..."
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white/80 dark:bg-gray-800/80 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Quell-System
                    </label>
                    <input
                      type="text"
                      value={formData.sourceSystem}
                      onChange={(e) => setFormData(prev => ({ ...prev, sourceSystem: e.target.value }))}
                      placeholder="z.B. SAP ERP"
                      className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white/80 dark:bg-gray-800/80 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Ziel-System
                    </label>
                    <input
                      type="text"
                      value={formData.targetSystem}
                      onChange={(e) => setFormData(prev => ({ ...prev, targetSystem: e.target.value }))}
                      placeholder="z.B. Salesforce"
                      className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white/80 dark:bg-gray-800/80 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Datenformat
                    </label>
                    <select
                      value={formData.dataFormat}
                      onChange={(e) => setFormData(prev => ({ ...prev, dataFormat: e.target.value }))}
                      className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white/80 dark:bg-gray-800/80 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    >
                      <option value="JSON">JSON</option>
                      <option value="XML">XML</option>
                      <option value="CSV">CSV</option>
                      <option value="XLSX">Excel</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Zeitplan
                    </label>
                    <select
                      value={formData.schedule}
                      onChange={(e) => setFormData(prev => ({ ...prev, schedule: e.target.value }))}
                      className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white/80 dark:bg-gray-800/80 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    >
                      <option value="realtime">Echtzeit</option>
                      <option value="hourly">Stündlich</option>
                      <option value="daily">Täglich</option>
                      <option value="weekly">Wöchentlich</option>
                    </select>
                  </div>
                </div>

                <button
                  onClick={handleFormGeneration}
                  disabled={!formData.streamName || !formData.sourceSystem || !formData.targetSystem || isGenerating}
                  className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-medium shadow-lg shadow-purple-500/25 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Konfiguration wird erstellt...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5 mr-2" />
                      XML konfigurieren
                    </>
                  )}
                </button>
              </div>
            </>
          )}

          {activeMode === 'template' && (
            <>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center">
                <File className="w-5 h-5 mr-2 text-purple-600" />
                XML Templates
              </h3>
              <div className="flex-1 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Template auswählen
                  </label>
                  <select
                    value={selectedTemplate?.id || ''}
                    onChange={(e) => {
                      const template = templates.find(t => t.id === e.target.value);
                      setSelectedTemplate(template || null);
                      if (template?.parameters) {
                        const newParams: {[key: string]: string} = {};
                        template.parameters.forEach(param => {
                          newParams[param] = '';
                        });
                        setTemplateParameters(newParams);
                      }
                    }}
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white/80 dark:bg-gray-800/80 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  >
                    <option value="">-- Template wählen --</option>
                    {templates.map((template) => (
                      <option key={template.id} value={template.id}>
                        {template.name} ({template.category})
                      </option>
                    ))}
                  </select>
                </div>

                {selectedTemplate && (
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/30 rounded-xl border border-blue-200 dark:border-blue-800">
                    <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">{selectedTemplate.name}</h4>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mb-3">{selectedTemplate.description}</p>
                    
                    {selectedTemplate.parameters && selectedTemplate.parameters.length > 0 && (
                      <div className="space-y-3">
                        <h5 className="text-sm font-medium text-blue-900 dark:text-blue-100">Template Parameter:</h5>
                        {selectedTemplate.parameters.map((param) => (
                          <div key={param}>
                            <label className="block text-xs font-medium text-blue-800 dark:text-blue-200 mb-1">
                              {param}
                            </label>
                            <input
                              type="text"
                              value={templateParameters[param] || ''}
                              onChange={(e) => setTemplateParameters(prev => ({
                                ...prev,
                                [param]: e.target.value
                              }))}
                              placeholder={`Wert für ${param}`}
                              className="w-full p-2 text-sm border border-blue-300 dark:border-blue-600 rounded-lg bg-white/80 dark:bg-gray-800/80 focus:ring-2 focus:ring-blue-500"
                            />
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                <button
                  onClick={handleTemplateGeneration}
                  disabled={!selectedTemplate || isGenerating}
                  className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-medium shadow-lg shadow-purple-500/25 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Template wird verarbeitet...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5 mr-2" />
                      XML aus Template generieren
                    </>
                  )}
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Right Panel - XML Preview */}
      <div className="w-1/2 flex flex-col bg-white/60 dark:bg-gray-900/60 backdrop-blur-sm">
        {/* Header */}
        <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 flex items-center">
              <Code className="w-6 h-6 mr-2 text-purple-600" />
              Generated XML
            </h3>
            
            {generatedXML && (
              <div className="flex space-x-2">
                <button
                  onClick={copyToClipboard}
                  className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-300 flex items-center"
                >
                  {copied ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                  {copied ? 'Kopiert!' : 'Kopieren'}
                </button>
                <button
                  onClick={downloadXML}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all duration-300 flex items-center"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </button>
              </div>
            )}
          </div>
          
          {/* Validation Status */}
          {validation && (
            <div className="mt-4 p-3 rounded-lg flex items-start space-x-2">
              {validation.isValid ? (
                <>
                  <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-green-800 dark:text-green-400 font-medium">XML ist valid!</p>
                    {validation.warnings.length > 0 && (
                      <ul className="text-yellow-700 dark:text-yellow-400 text-sm mt-1">
                        {validation.warnings.map((warning, index) => (
                          <li key={index}>• {warning}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-red-800 dark:text-red-400 font-medium">Validierung fehlgeschlagen</p>
                    <ul className="text-red-700 dark:text-red-400 text-sm mt-1">
                      {validation.errors.map((error, index) => (
                        <li key={index}>• {error}</li>
                      ))}
                    </ul>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* XML Content */}
        <div className="flex-1 p-6">
          {generatedXML ? (
            <div className="h-full border border-gray-300 dark:border-gray-600 rounded-xl overflow-hidden">
              <Editor
                height="100%"
                language="xml"
                theme="vs-dark"
                value={generatedXML}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  wordWrap: 'on',
                  formatOnPaste: true,
                  formatOnType: true,
                  fontSize: 13,
                  lineNumbers: 'on',
                  folding: true,
                  renderWhitespace: 'selection',
                  tabSize: 2,
                  insertSpaces: true,
                }}
                onMount={(editor) => {
                  // Auto-format XML on mount
                  editor.getAction('editor.action.formatDocument')?.run();
                }}
              />
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500 dark:text-gray-400">
              <div className="text-center">
                <Code className="w-20 h-20 mx-auto mb-4 text-gray-300 dark:text-gray-600" />
                <h4 className="text-lg font-medium mb-2">Bereit für XML-Generation</h4>
                <p>Verwende Chat, Formular oder Templates, um StreamWorks XML zu generieren</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};