/**
 * Monaco Code Editor Component
 * Enterprise-grade code editor with syntax highlighting, validation, and advanced features
 */

import React, { useRef, useEffect, useState } from 'react';
import Editor from '@monaco-editor/react';
import type { editor } from 'monaco-editor';
import { Maximize2, Minimize2, Search, Copy, Download, RefreshCw } from 'lucide-react';
import { Button } from './Button';
import { useUiStore } from '../../../stores/uiStore';
import { copyToClipboard, downloadBlob } from '../../utils';
import { motion, AnimatePresence } from 'framer-motion';

type Language = 'xml' | 'json' | 'javascript' | 'typescript' | 'yaml' | 'sql' | 'markdown';
type Theme = 'vs-dark' | 'vs-light' | 'streamworks-dark' | 'streamworks-light';

interface CodeEditorProps {
  language: Language;
  value: string;
  onChange?: (value: string) => void;
  height?: string;
  theme?: Theme;
  readOnly?: boolean;
  showMinimap?: boolean;
  showLineNumbers?: boolean;
  wordWrap?: 'on' | 'off' | 'wordWrapColumn' | 'bounded';
  fontSize?: number;
  tabSize?: number;
  insertSpaces?: boolean;
  className?: string;
  placeholder?: string;
  exportable?: boolean;
  onValidate?: (markers: editor.IMarkerData[]) => void;
  options?: editor.IStandaloneEditorConstructionOptions;
}

interface CustomTheme {
  base: 'vs' | 'vs-dark';
  inherit: boolean;
  rules: Array<{
    token: string;
    foreground?: string;
    background?: string;
    fontStyle?: string;
  }>;
  colors: {
    [key: string]: string;
  };
}

const streamWorksKeywords = [
  'StreamWorks', 'streamworks', 'stream-works',
  'data-source', 'data-target', 'transformation',
  'pipeline', 'connector', 'adapter', 'mapping',
  'schedule', 'trigger', 'validation', 'schema'
];

export function CodeEditor({
  language,
  value,
  onChange,
  height = '400px',
  theme,
  readOnly = false,
  showMinimap = true,
  showLineNumbers = true,
  wordWrap = 'on',
  fontSize = 14,
  tabSize = 2,
  insertSpaces = true,
  className = '',
  placeholder,
  onValidate,
  options = {},
}: CodeEditorProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const { isDark } = useUiStore();
  
  // Determine theme based on UI store if not explicitly set
  const effectiveTheme = theme || (isDark ? 'streamworks-dark' : 'streamworks-light');

  useEffect(() => {
    // Register custom themes when component mounts
    registerCustomThemes();
  }, []);

  const registerCustomThemes = async () => {
    try {
      const monaco = await import('monaco-editor');
      // StreamWorks Dark Theme
      const streamworksDarkTheme: CustomTheme = {
        base: 'vs-dark',
        inherit: true,
        rules: [
          { token: 'comment', foreground: '6A9955', fontStyle: 'italic' },
          { token: 'keyword', foreground: '569CD6', fontStyle: 'bold' },
          { token: 'string', foreground: 'CE9178' },
          { token: 'number', foreground: 'B5CEA8' },
          { token: 'tag', foreground: '92C5F8' },
          { token: 'attribute.name', foreground: '9CDCFE' },
          { token: 'attribute.value', foreground: 'CE9178' },
          { token: 'streamworks-keyword', foreground: 'FF6B35', fontStyle: 'bold' },
        ],
        colors: {
          'editor.background': '#1E1E1E',
          'editor.foreground': '#D4D4D4',
          'editor.lineHighlightBackground': '#2A2D2E',
          'editor.selectionBackground': '#264F78',
          'editor.findMatchBackground': '#A8AC94',
          'editor.findMatchHighlightBackground': '#EA5C004D',
        },
      };

      // StreamWorks Light Theme
      const streamworksLightTheme: CustomTheme = {
        base: 'vs',
        inherit: true,
        rules: [
          { token: 'comment', foreground: '008000', fontStyle: 'italic' },
          { token: 'keyword', foreground: '0000FF', fontStyle: 'bold' },
          { token: 'string', foreground: 'A31515' },
          { token: 'number', foreground: '098658' },
          { token: 'tag', foreground: '800000' },
          { token: 'attribute.name', foreground: 'FF0000' },
          { token: 'attribute.value', foreground: '0451A5' },
          { token: 'streamworks-keyword', foreground: 'FF6B35', fontStyle: 'bold' },
        ],
        colors: {
          'editor.background': '#FFFFFF',
          'editor.foreground': '#000000',
          'editor.lineHighlightBackground': '#F5F5F5',
          'editor.selectionBackground': '#ADD6FF',
          'editor.findMatchBackground': '#A8AC94',
          'editor.findMatchHighlightBackground': '#EA5C004D',
        },
      };

      monaco.editor.defineTheme('streamworks-dark', streamworksDarkTheme);
      monaco.editor.defineTheme('streamworks-light', streamworksLightTheme);
    } catch (error) {
      console.warn('Failed to register Monaco themes:', error);
    }
  };

  const handleEditorDidMount = (editor: editor.IStandaloneCodeEditor, monaco: any) => {
    editorRef.current = editor;
    setIsLoading(false);

    // Add StreamWorks-specific keywords for XML
    if (language === 'xml') {
      monaco.languages.setMonarchTokensProvider('xml', {
        tokenizer: {
          root: [
            [/StreamWorks|streamworks|stream-works/, 'streamworks-keyword'],
            [/data-source|data-target|transformation/, 'streamworks-keyword'],
            [/pipeline|connector|adapter|mapping/, 'streamworks-keyword'],
            [/schedule|trigger|validation|schema/, 'streamworks-keyword'],
          ],
        },
      });
    }

    // Auto-completion for StreamWorks keywords
    monaco.languages.registerCompletionItemProvider(language, {
      provideCompletionItems: (model: any, position: any) => {
        const suggestions = streamWorksKeywords.map((keyword) => ({
          label: keyword,
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: keyword,
          documentation: `StreamWorks keyword: ${keyword}`,
        }));

        // Add XML-specific completions
        if (language === 'xml') {
          suggestions.push(
            {
              label: 'streamworks-config',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: '<streamworks-config>\n\t<data-sources>\n\t\t$0\n\t</data-sources>\n</streamworks-config>',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Basic StreamWorks configuration template',
            },
            {
              label: 'data-source',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: '<data-source id="$1" type="$2">\n\t<connection-string>$3</connection-string>\n\t<schema>$4</schema>\n</data-source>',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Data source configuration',
            }
          );
        }

        return { suggestions };
      },
    });

    // Validation
    if (onValidate) {
      const model = editor.getModel();
      if (model) {
        const disposable = monaco.editor.onDidChangeMarkers((uris) => {
          if (uris.includes(model.uri)) {
            const markers = monaco.editor.getModelMarkers({ resource: model.uri });
            onValidate(markers);
          }
        });

        // Clean up on unmount
        return () => disposable.dispose();
      }
    }
  };

  const handleChange = (newValue: string | undefined) => {
    if (onChange && newValue !== undefined) {
      onChange(newValue);
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const toggleSearch = () => {
    setShowSearch(!showSearch);
    if (!showSearch && editorRef.current) {
      editorRef.current.getAction('actions.find').run();
    }
  };

  const formatCode = () => {
    if (editorRef.current) {
      editorRef.current.getAction('editor.action.formatDocument').run();
    }
  };

  const copyCode = async () => {
    const success = await copyToClipboard(value);
    if (success) {
      console.log('Code copied to clipboard');
    } else {
      console.error('Failed to copy code');
    }
  };

  const downloadCode = () => {
    const fileExtension = language === 'javascript' || language === 'typescript' 
      ? `.${language === 'typescript' ? 'ts' : 'js'}` 
      : `.${language}`;
    const blob = new Blob([value], { type: 'text/plain' });
    downloadBlob(blob, `code${fileExtension}`);
  };

  const editorOptions: editor.IStandaloneEditorConstructionOptions = {
    readOnly,
    minimap: { enabled: showMinimap },
    lineNumbers: showLineNumbers ? 'on' : 'off',
    wordWrap,
    fontSize,
    tabSize,
    insertSpaces,
    automaticLayout: true,
    scrollBeyondLastLine: false,
    renderWhitespace: 'selection',
    bracketPairColorization: { enabled: true },
    suggest: {
      showKeywords: true,
      showSnippets: true,
      showFunctions: true,
    },
    quickSuggestions: {
      other: true,
      comments: false,
      strings: false,
    },
    folding: true,
    foldingStrategy: 'indentation',
    showFoldingControls: 'always',
    unfoldOnClickAfterEndOfLine: true,
    ...options,
  };

  const containerClass = `
    relative bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg overflow-hidden
    ${isFullscreen ? 'fixed inset-0 z-50' : ''}
    ${className}
  `;

  return (
    <AnimatePresence>
      <motion.div
        className={containerClass}
        initial={isFullscreen ? { scale: 0.95, opacity: 0 } : false}
        animate={isFullscreen ? { scale: 1, opacity: 1 } : false}
        exit={isFullscreen ? { scale: 0.95, opacity: 0 } : false}
        transition={{ duration: 0.2 }}
      >
        {/* Toolbar */}
        <div className="flex items-center justify-between px-4 py-2 bg-neutral-50 dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
              {language.toUpperCase()}
            </span>
            {isLoading && (
              <div className="flex items-center space-x-1 text-xs text-neutral-500">
                <RefreshCw size={12} className="animate-spin" />
                <span>Loading...</span>
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleSearch}
              title="Find & Replace (Ctrl+F)"
              className="h-8 w-8 p-0"
            >
              <Search size={14} />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={formatCode}
              title="Format Code (Shift+Alt+F)"
              className="h-8 w-8 p-0"
              disabled={readOnly}
            >
              <RefreshCw size={14} />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={copyCode}
              title="Copy to Clipboard"
              className="h-8 w-8 p-0"
            >
              <Copy size={14} />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={downloadCode}
              title="Download File"
              className="h-8 w-8 p-0"
            >
              <Download size={14} />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleFullscreen}
              title={isFullscreen ? 'Exit Fullscreen (Esc)' : 'Enter Fullscreen (F11)'}
              className="h-8 w-8 p-0"
            >
              {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
            </Button>
          </div>
        </div>

        {/* Editor */}
        <div className="relative" style={{ height: isFullscreen ? 'calc(100vh - 60px)' : height }}>
          <Editor
            language={language}
            value={value}
            onChange={handleChange}
            onMount={handleEditorDidMount}
            theme={effectiveTheme}
            options={editorOptions}
            loading={
              <div className="flex items-center justify-center h-full">
                <div className="flex items-center space-x-2 text-neutral-500">
                  <RefreshCw size={20} className="animate-spin" />
                  <span>Loading Monaco Editor...</span>
                </div>
              </div>
            }
          />
          
          {/* Placeholder for empty editor */}
          {!value && placeholder && (
            <div className="absolute inset-0 flex items-start justify-start pointer-events-none">
              <div className="text-neutral-400 dark:text-neutral-500 text-sm mt-4 ml-16">
                {placeholder}
              </div>
            </div>
          )}
        </div>

        {/* Fullscreen overlay backdrop */}
        {isFullscreen && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-40"
            onClick={toggleFullscreen}
          />
        )}
      </motion.div>
    </AnimatePresence>
  );
}

// Utility hook for Monaco Editor actions
export function useCodeEditor() {
  const [editor, setEditor] = useState<editor.IStandaloneCodeEditor | null>(null);

  const actions = {
    format: () => editor?.getAction('editor.action.formatDocument').run(),
    find: () => editor?.getAction('actions.find').run(),
    replace: () => editor?.getAction('editor.action.startFindReplaceAction').run(),
    toggleWordWrap: () => editor?.getAction('editor.action.toggleWordWrap').run(),
    toggleMinimap: () => editor?.getAction('editor.action.toggleMinimap').run(),
    insertSnippet: (snippet: string) => {
      if (editor) {
        editor.trigger('keyboard', 'type', { text: snippet });
      }
    },
    setLanguage: async (language: string) => {
      try {
        const monaco = await import('monaco-editor');
        const model = editor?.getModel();
        if (model) {
          monaco.editor.setModelLanguage(model, language);
        }
      } catch (error) {
        console.warn('Failed to set Monaco language:', error);
      }
    },
  };

  return { setEditor, actions };
}