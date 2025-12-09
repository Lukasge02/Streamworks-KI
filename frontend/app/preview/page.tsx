'use client';

import { useEffect, useState, Suspense, useCallback } from 'react';
import Link from 'next/link';

import { useSearchParams } from 'next/navigation';
import Editor from '@monaco-editor/react';
import Header from '../components/Header';

interface ValidationIssue {
  message: string;
  line: number;
  severity: 'error' | 'warning';
}

interface ValidationResult {
  is_valid: boolean;
  issues: ValidationIssue[];
  stream_name: string;
  element_count: number;
  xml_length: number;
}

interface PreviewData {
  xml: string;
  job_type: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  params: Record<string, any>;
  validation: ValidationResult;
}

// Parameter Kategorien wie im Chat
interface ParamConfig {
  key: string;
  label: string;
  required: boolean;
  type?: string;
  options?: string[];
}

interface SectionConfig {
  title: string;
  params: ParamConfig[];
}

const PARAMETER_SECTIONS: Record<string, SectionConfig> = {
  stream: {
    title: "Stream-Parameter",
    params: [
      { key: 'stream_name', label: 'Stream Name', required: true },
      { key: 'stream_documentation', label: 'Dokumentation', required: false },
      { key: 'stream_path', label: 'Stream Pfad', required: false },
      { key: 'short_description', label: 'Kurzbeschreibung', required: false },
    ]
  },
  fileTransfer: {
    title: "File Transfer",
    params: [
      { key: 'source_agent', label: 'Quell-Server', required: true },
      { key: 'target_agent', label: 'Ziel-Server', required: true },
      { key: 'source_file_pattern', label: 'Quell-Datei', required: true },
      { key: 'target_file_path', label: 'Ziel-Pfad', required: true },
      { key: 'source_file_delete_flag', label: 'Quelle löschen', required: false, type: 'dropdown', options: ['', 'true', 'false'] },
      { key: 'target_file_exists_handling', label: 'Überschreiben', required: false, type: 'dropdown', options: ['', 'Overwrite', 'Skip', 'Abort'] },
    ]
  },
  timing: {
    title: "Timing & Schedule",
    params: [
      { key: 'schedule', label: 'Zeitplan', required: false, type: 'dropdown', options: ['', 'täglich', 'wöchentlich', 'monatlich', 'stündlich', 'werktags'] },
      { key: 'start_time', label: 'Startzeit', required: false, type: 'time' },
    ]
  },
  contact: {
    title: "Kontakt",
    params: [
      { key: 'contact_first_name', label: 'Vorname', required: false },
      { key: 'contact_last_name', label: 'Nachname', required: false },
      { key: 'company_name', label: 'Firma', required: false },
    ]
  }
};

function PreviewContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');

  const [data, setData] = useState<PreviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [xmlContent, setXmlContent] = useState('');
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [params, setParams] = useState<Record<string, any>>({});
  const [toast, setToast] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<string[]>(['stream', 'fileTransfer']);
  const [isRegenerating, setIsRegenerating] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [editorRef, setEditorRef] = useState<any>(null);

  // Load initial data
  useEffect(() => {
    if (!sessionId) {
      setError('Keine Session-ID angegeben');
      setLoading(false);
      return;
    }
    fetch(`http://localhost:8000/api/xml/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    })
      .then(res => {
        if (!res.ok) throw new Error('Session nicht gefunden');
        return res.json();
      })
      .then((data: PreviewData) => {
        setData(data);
        setXmlContent(data.xml);
        setParams(data.params);
        setLoading(false);
      })
      .catch(err => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const errorMessage = (err as any).message || 'Ein Fehler ist aufgetreten';
        setError(errorMessage);
        setLoading(false);
      });
  }, [sessionId]);

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 2500);
  };

  // Regenerate XML when params change (debounced)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const regenerateXML = useCallback(async (updatedParams: Record<string, any>) => {
    if (!sessionId || isRegenerating) return;

    setIsRegenerating(true);
    try {
      const res = await fetch('http://localhost:8000/api/xml/regenerate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, updated_params: updatedParams }),
      });
      if (!res.ok) throw new Error('Fehler beim Regenerieren');
      const newData = await res.json();
      setXmlContent(newData.xml);
      setData(prev => prev ? { ...prev, validation: newData.validation } : null);
    } catch (err) {
      console.error('Regenerate error:', err);
    } finally {
      setIsRegenerating(false);
    }
  }, [sessionId, isRegenerating]);

  // Handle parameter change - updates params and triggers XML regeneration
  const handleParamChange = useCallback((key: string, value: string) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const newParams: Record<string, any> = { ...params, [key]: value };
    setParams(newParams);

    // Debounce the regeneration
    const timeoutId = setTimeout(() => {
      regenerateXML(newParams);
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [params, regenerateXML]);

  const toggleSection = (section: string) => {
    setExpandedSections(prev =>
      prev.includes(section)
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  const copyXML = () => {
    navigator.clipboard.writeText(xmlContent);
    showToast('📋 In Zwischenablage kopiert');
  };

  const downloadXML = () => {
    const streamName = params.stream_name || 'stream';
    const filename = streamName.startsWith('GECK003_') ? streamName : `GECK003_${streamName}`;
    const blob = new Blob([xmlContent], { type: 'application/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.xml`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('⬇ Download gestartet');
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handleEditorDidMount = (editor: any) => {
    setEditorRef(editor);
  };

  const scrollToLine = (line: number) => {
    if (editorRef && line > 0) {
      editorRef.revealLineInCenter(line);
      editorRef.setPosition({ column: 1, lineNumber: line });
      editorRef.focus();
      // Highlight the line briefly
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const decorations = editorRef.deltaDecorations([], [
        {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          range: new (window as any).monaco.Range(line, 1, line, 1),
          options: {
            isWholeLine: true,
            className: 'myLineDecoration',
            glyphMarginClassName: 'myGlyphMarginClass'
          }
        }
      ]);

      setTimeout(() => {
        editorRef.deltaDecorations(decorations, []);
      }, 1000);
    }
  };

  if (loading) {
    return (
      <div className="preview-page">
        <Header sessionId={sessionId} />
        <div className="loading-container">
          <div className="spinner" />
          <p>XML wird geladen...</p>
        </div>
        <style jsx>{styles}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div className="preview-page">
        <Header sessionId={sessionId} />
        <div className="error-container">
          <h2>❌ Fehler</h2>
          <p>{error}</p>
          <Link href="/" className="btn btn-primary">Zurück zum Chat</Link>
        </div>
        <style jsx>{styles}</style>
      </div>
    );
  }

  return (
    <div className="preview-page">
      <Header sessionId={sessionId} />

      <main className="preview-main">
        {/* Sidebar */}
        <aside className="preview-sidebar">
          {/* Validation Status */}
          <div className="sidebar-section">
            <div className={`status-card ${data?.validation.is_valid ? 'valid' : 'invalid'}`}>
              <span className="status-icon">{data?.validation.is_valid ? '✓' : '✗'}</span>
              <span className="status-text">
                {data?.validation.is_valid
                  ? 'XML Validierung erfolgreich'
                  : `${data?.validation.issues.length} Fehler`}
              </span>
              {isRegenerating && <span className="regenerating">⟳</span>}
            </div>
            {data?.validation.issues && data.validation.issues.length > 0 && (
              <div className="issues-list">
                {data.validation.issues.map((issue, i) => (
                  <button
                    key={i}
                    className={`issue-item ${issue.severity}`}
                    onClick={() => scrollToLine(issue.line)}
                    title="Klicken um zur Zeile zu springen"
                  >
                    <span className="issue-line">Zeile {issue.line}</span>
                    <span className="issue-msg">{issue.message}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
          {/* ... */}

          {/* Parameter Sections - Accordion Style like Chat */}
          <div className="params-container">
            <h3 className="params-header">
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Parameter bearbeiten
            </h3>

            {Object.entries(PARAMETER_SECTIONS).map(([sectionKey, section]) => (
              <div key={sectionKey} className="param-section">
                <button
                  className="section-toggle"
                  onClick={() => toggleSection(sectionKey)}
                >
                  <span>{section.title}</span>
                  <svg
                    className={`toggle-icon ${expandedSections.includes(sectionKey) ? 'expanded' : ''}`}
                    width="16"
                    height="16"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {expandedSections.includes(sectionKey) && (
                  <div className="section-content">
                    {section.params.map(param => {
                      const value = params[param.key] || '';
                      return (
                        <div key={param.key} className="param-row">
                          <span className="param-label">
                            {param.label}
                            {param.required && <span className="required">*</span>}
                          </span>
                          {param.type === 'dropdown' ? (
                            <select
                              className="param-input"
                              value={value}
                              onChange={e => handleParamChange(param.key, e.target.value)}
                            >
                              {param.options?.map(opt => (
                                <option key={opt} value={opt}>{opt || '—'}</option>
                              ))}
                            </select>
                          ) : param.type === 'time' ? (
                            <input
                              type="time"
                              className="param-input"
                              value={value}
                              onChange={e => handleParamChange(param.key, e.target.value)}
                            />
                          ) : (
                            <input
                              type="text"
                              className="param-input"
                              value={value}
                              placeholder="—"
                              onChange={e => handleParamChange(param.key, e.target.value)}
                            />
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </div>
        </aside>

        {/* Editor Area */}
        <div className="preview-editor">
          <div className="editor-toolbar">
            <span className="toolbar-title">XML Vorschau</span>
            <div className="toolbar-actions">
              <button className="btn btn-outline" onClick={copyXML}>📋 Kopieren</button>
              <button className="btn btn-success" onClick={downloadXML}>⬇ Herunterladen</button>
            </div>
          </div>
          <div className="editor-container">
            <Editor
              onMount={handleEditorDidMount}
              height="100%"
              defaultLanguage="xml"
              value={xmlContent}
              onChange={(value) => setXmlContent(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: true },
                fontSize: 13,
                lineNumbers: 'on',
                wordWrap: 'on',
                scrollBeyondLastLine: false,
                formatOnPaste: true,
                automaticLayout: true,
              }}
            />
          </div>
        </div>
      </main>

      {/* Toast */}
      {toast && <div className="toast show">{toast}</div>}

      <style jsx>{styles}</style>
    </div>
  );
}

const styles = `
  .preview-page {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 50%, #e0f2fe 100%);
    font-family: 'Inter', -apple-system, sans-serif;
  }

  .loading-container, .error-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #e2e8f0;
    border-top-color: #0082D9;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .preview-main {
    flex: 1;
    display: flex;
    overflow: hidden;
  }

  /* Sidebar */
  .preview-sidebar {
    width: 380px;
    background: white;
    border-right: 1px solid #e5e7eb;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }

  .sidebar-section {
    padding: 1rem;
    border-bottom: 1px solid #e5e7eb;
  }

  .status-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    border-radius: 12px;
    transition: all 0.2s ease;
  }

  .status-card.valid {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border: 1px solid #a7f3d0;
  }

  .status-card.invalid {
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    border: 1px solid #fecaca;
  }

  .status-icon {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.875rem;
  }

  .status-card.valid .status-icon {
    background: #10b981;
    color: white;
  }

  .status-card.invalid .status-icon {
    background: #ef4444;
    color: white;
  }

  .status-text {
    flex: 1;
    font-weight: 600;
    font-size: 0.875rem;
  }

  .status-card.valid .status-text { color: #047857; }
  .status-card.invalid .status-text { color: #b91c1c; }

  .regenerating {
    animation: spin 1s linear infinite;
    font-size: 1rem;
  }

  .issues-list {
    margin-top: 0.75rem;
  }

  .issue-item {
    display: flex;
    flex-direction: column;
    width: 100%;
    text-align: left;
    font-size: 0.8125rem;
    color: #b91c1c;
    padding: 0.625rem 0.75rem;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .issue-item:hover {
    background: #fee2e2;
    transform: translateX(2px);
  }

  .issue-line {
    font-weight: 600;
    font-size: 0.75rem;
    margin-bottom: 0.25rem;
    color: #991b1b;
  }

  .issue-item.warning {
    background: #fffbeb;
    color: #92400e;
    border-color: #fcd34d;
  }

  .issue-item.warning:hover {
    background: #fef3c7;
  }

  .issue-item.warning .issue-line {
    color: #92400e;
  }
  
  .myLineDecoration {
    background: rgba(0, 130, 217, 0.2);
    width: 100% !important;
  }

  /* Parameters Container */
  .params-container {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
  }

  .params-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #0082D9;
    font-size: 1rem;
    font-weight: 700;
    margin: 0 0 1rem 0;
  }

  .param-section {
    margin-bottom: 0.75rem;
  }

  .section-toggle {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.875rem 1rem;
    background: #f8f9fa;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.875rem;
    color: #1a1a1a;
    transition: all 0.2s;
  }

  .section-toggle:hover {
    background: #f1f5f9;
    border-color: #0082D9;
  }

  .toggle-icon {
    transition: transform 0.2s;
    color: #6b7280;
  }

  .toggle-icon.expanded {
    transform: rotate(180deg);
  }

  .section-content {
    background: white;
    border: 1px solid #e5e7eb;
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 0.5rem;
  }

  .param-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    border-bottom: 1px solid #f0f2f5;
    transition: background 0.2s;
  }

  .param-row:hover {
    background: #f9fafb;
  }

  .param-row:last-child {
    border-bottom: none;
  }

  .param-label {
    font-size: 0.8125rem;
    color: #4b5563;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-weight: 500;
  }

  .required {
    color: #ef4444;
    font-size: 0.75rem;
  }

  .param-input {
    width: 150px;
    padding: 0.5rem 0.75rem;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 0.8125rem;
    color: #1e293b;
    transition: all 0.2s;
  }

  .param-input:focus {
    outline: none;
    border-color: #0082D9;
    box-shadow: 0 0 0 3px rgba(0, 130, 217, 0.15);
  }

  /* Editor */
  .preview-editor {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .editor-toolbar {
    padding: 1rem 1.25rem;
    background: white;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .toolbar-title {
    font-weight: 700;
    font-size: 1rem;
    color: #111827;
  }

  .toolbar-actions {
    display: flex;
    gap: 0.5rem;
  }

  .editor-container {
    flex: 1;
    overflow: hidden;
  }

  /* Buttons */
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.625rem 1.25rem;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
  }

  .btn:active {
    transform: scale(0.98);
  }

  .btn-outline {
    background: white;
    color: #4b5563;
    border: 2px solid #e2e8f0;
  }

  .btn-outline:hover {
    background: #f8fafc;
    border-color: #0082D9;
    color: #0082D9;
  }

  .btn-success {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
  }

  .btn-success:hover {
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
  }

  .btn-primary {
    background: linear-gradient(135deg, #0082D9 0%, #006BB3 100%);
    color: white;
    box-shadow: 0 2px 4px rgba(0, 130, 217, 0.3);
  }

  .btn-primary:hover {
    background: linear-gradient(135deg, #006BB3 0%, #005A99 100%);
    box-shadow: 0 4px 8px rgba(0, 130, 217, 0.4);
  }

  /* Toast */
  .toast {
    position: fixed;
    bottom: 1.5rem;
    left: 50%;
    transform: translateX(-50%) translateY(100px);
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    color: white;
    padding: 0.875rem 1.75rem;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.875rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    z-index: 100;
  }

  .toast.show {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
  }
`;

// Wrap with Suspense for useSearchParams
export default function PreviewPage() {
  return (
    <Suspense fallback={
      <div className="preview-page" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <div style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '3px solid #e2e8f0',
            borderTopColor: '#004899',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
          <p>Lade Preview...</p>
        </div>
      </div>
    }>
      <PreviewContent />
    </Suspense>
  );
}
