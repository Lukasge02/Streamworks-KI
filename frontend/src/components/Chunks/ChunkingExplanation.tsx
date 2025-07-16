import React from 'react';
import { Info, Scissors, Brain, FileText, Layers, Target } from 'lucide-react';

export const ChunkingExplanation: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center space-x-3 mb-4">
        <Info className="w-6 h-6 text-blue-500" />
        <h3 className="text-lg font-semibold text-gray-900">🔬 Wie funktioniert das Chunking?</h3>
      </div>
      
      <div className="space-y-4">
        {/* Chunking Strategy Overview */}
        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Enterprise Intelligent Chunking Strategy</h4>
          <p className="text-sm text-blue-800">
            Das System verwendet eine hybride intelligente Chunking-Strategie, die mehrere Ansätze kombiniert:
          </p>
        </div>

        {/* Chunking Methods */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Scissors className="w-5 h-5 text-purple-500" />
              <h5 className="font-medium text-gray-900">Semantic Overlap Chunking</h5>
            </div>
            <p className="text-sm text-gray-600">
              Chunks überlappen sich um ~10%, um Kontext zu bewahren. Dadurch gehen keine wichtigen 
              Informationen an Chunk-Grenzen verloren.
            </p>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <FileText className="w-5 h-5 text-green-500" />
              <h5 className="font-medium text-gray-900">Markdown-Aware Splitting</h5>
            </div>
            <p className="text-sm text-gray-600">
              Erkennt Markdown-Strukturen (Headers, Listen, Code-Blöcke) und trennt intelligent 
              an natürlichen Grenzen.
            </p>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Brain className="w-5 h-5 text-blue-500" />
              <h5 className="font-medium text-gray-900">Content-Based Sizing</h5>
            </div>
            <p className="text-sm text-gray-600">
              Target-Größe: 400-800 Zeichen. Anpassung basierend auf Inhaltsdichte und 
              semantischer Kohärenz.
            </p>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Layers className="w-5 h-5 text-orange-500" />
              <h5 className="font-medium text-gray-900">Quality Scoring</h5>
            </div>
            <p className="text-sm text-gray-600">
              Jeder Chunk wird auf Qualität bewertet: Semantic Density, Readability, 
              Information Completeness.
            </p>
          </div>
        </div>

        {/* Chunking Process */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">📋 Chunking-Prozess</h4>
          <ol className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start">
              <span className="font-medium text-gray-900 mr-2">1.</span>
              <span><strong>PDF zu Markdown:</strong> Konvertierung mit Enterprise Markdown Converter</span>
            </li>
            <li className="flex items-start">
              <span className="font-medium text-gray-900 mr-2">2.</span>
              <span><strong>Content Analysis:</strong> Erkennung von Strukturen, Headers, Listen</span>
            </li>
            <li className="flex items-start">
              <span className="font-medium text-gray-900 mr-2">3.</span>
              <span><strong>Intelligent Splitting:</strong> Aufteilung basierend auf semantischen Grenzen</span>
            </li>
            <li className="flex items-start">
              <span className="font-medium text-gray-900 mr-2">4.</span>
              <span><strong>Overlap Generation:</strong> 10% Überlappung zwischen aufeinanderfolgenden Chunks</span>
            </li>
            <li className="flex items-start">
              <span className="font-medium text-gray-900 mr-2">5.</span>
              <span><strong>Quality Assessment:</strong> Bewertung jedes Chunks (0.0 - 1.0)</span>
            </li>
            <li className="flex items-start">
              <span className="font-medium text-gray-900 mr-2">6.</span>
              <span><strong>Embedding Generation:</strong> E5 Multilingual Embeddings für jeden Chunk</span>
            </li>
            <li className="flex items-start">
              <span className="font-medium text-gray-900 mr-2">7.</span>
              <span><strong>ChromaDB Storage:</strong> Speicherung mit Metadaten für optimales Retrieval</span>
            </li>
          </ol>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="bg-green-50 rounded-lg p-3 text-center">
            <Target className="w-6 h-6 text-green-600 mx-auto mb-1" />
            <div className="text-sm font-medium text-green-900">Target Size</div>
            <div className="text-xs text-green-700">400-800 chars</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-3 text-center">
            <Layers className="w-6 h-6 text-blue-600 mx-auto mb-1" />
            <div className="text-sm font-medium text-blue-900">Overlap</div>
            <div className="text-xs text-blue-700">~10%</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-3 text-center">
            <Brain className="w-6 h-6 text-purple-600 mx-auto mb-1" />
            <div className="text-sm font-medium text-purple-900">Quality Threshold</div>
            <div className="text-xs text-purple-700">≥ 0.6</div>
          </div>
        </div>

        {/* Technical Details */}
        <div className="border-t border-gray-200 pt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">🛠️ Technische Details</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-600">
            <div>
              <strong>Embedding Model:</strong> intfloat/multilingual-e5-large
            </div>
            <div>
              <strong>Vector DB:</strong> ChromaDB (Persistent)
            </div>
            <div>
              <strong>Chunking Library:</strong> Enterprise Intelligent Chunker
            </div>
            <div>
              <strong>Quality Metrics:</strong> Semantic Density, Readability, Completeness
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};