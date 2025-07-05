import React from 'react';
import { 
  Brain, 
  Target, 
  Gauge, 
  Zap, 
  Tag, 
  Lightbulb, 
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';
import { QueryAnalysis } from '../../types';

interface QueryAnalysisDisplayProps {
  analysis: QueryAnalysis;
}

export const QueryAnalysisDisplay: React.FC<QueryAnalysisDisplayProps> = ({ analysis }) => {
  const getIntentIcon = (intent: string) => {
    switch (intent.toLowerCase()) {
      case 'technical_help':
        return '🔧';
      case 'api_usage':
        return '⚡';
      case 'troubleshooting':
        return '🚨';
      case 'configuration':
        return '⚙️';
      case 'documentation':
        return '📚';
      case 'general_inquiry':
        return '❓';
      case 'specific_feature':
        return '🎯';
      default:
        return '💬';
    }
  };

  const getComplexityColor = (level: number) => {
    if (level <= 3) return 'text-green-600 bg-green-100';
    if (level <= 7) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getComplexityLabel = (level: number) => {
    if (level <= 3) return 'Basic';
    if (level <= 7) return 'Intermediate';
    return 'Advanced';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getStrategyDisplayName = (strategy: string) => {
    const strategies: Record<string, string> = {
      'semantic_only': 'Semantic Only',
      'filtered': 'Filtered Search',
      'hybrid': 'Hybrid Search',
      'contextual': 'Contextual Search',
      'concept_based': 'Concept-Based Search'
    };
    return strategies[strategy] || strategy;
  };

  const getStrategyDescription = (strategy: string) => {
    const descriptions: Record<string, string> = {
      'semantic_only': 'Reine Vektorähnlichkeitssuche mit Embeddings',
      'filtered': 'Metadatenbasierte Filterung mit semantischer Suche',
      'hybrid': 'Kombination aus semantischer, Keyword- und Filtersuche',
      'contextual': 'Query-Erweiterung mit domänenspezifischem Kontext',
      'concept_based': 'Fokus auf domänenspezifische Konzepte und Terminologie'
    };
    return descriptions[strategy] || 'Unbekannte Strategie';
  };

  return (
    <div className="p-6 bg-blue-50">
      <div className="flex items-center space-x-2 mb-6">
        <Brain className="w-6 h-6 text-blue-600" />
        <h3 className="text-lg font-semibold text-blue-900">Query-Analyse</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Primary Intent */}
        <div className="bg-white p-4 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-2 mb-2">
            <Target className="w-5 h-5 text-blue-600" />
            <span className="font-medium text-gray-900">Intent</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{getIntentIcon(analysis.primary_intent)}</span>
            <div>
              <div className="font-semibold text-gray-900 capitalize">
                {analysis.primary_intent.replace('_', ' ')}
              </div>
            </div>
          </div>
        </div>

        {/* Confidence Score */}
        <div className="bg-white p-4 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-2 mb-2">
            <CheckCircle className="w-5 h-5 text-blue-600" />
            <span className="font-medium text-gray-900">Vertrauen</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded-full text-sm font-medium ${getConfidenceColor(analysis.confidence)}`}>
              {Math.round(analysis.confidence * 100)}%
            </span>
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${analysis.confidence * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Complexity Level */}
        <div className="bg-white p-4 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-2 mb-2">
            <Gauge className="w-5 h-5 text-blue-600" />
            <span className="font-medium text-gray-900">Komplexität</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded-full text-sm font-medium ${getComplexityColor(analysis.complexity_level)}`}>
              {getComplexityLabel(analysis.complexity_level)}
            </span>
            <span className="text-gray-600 text-sm">
              Level {analysis.complexity_level}/10
            </span>
          </div>
        </div>

        {/* Search Strategy */}
        <div className="bg-white p-4 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-2 mb-2">
            <Zap className="w-5 h-5 text-blue-600" />
            <span className="font-medium text-gray-900">Strategie</span>
          </div>
          <div>
            <div className="font-semibold text-gray-900 text-sm">
              {getStrategyDisplayName(analysis.search_strategy)}
            </div>
            <div className="text-xs text-gray-600 mt-1">
              {getStrategyDescription(analysis.search_strategy)}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-4">
          {/* Detected Entities */}
          {analysis.detected_entities && analysis.detected_entities.length > 0 && (
            <div className="bg-white p-4 rounded-lg border border-blue-200">
              <div className="flex items-center space-x-2 mb-3">
                <Tag className="w-5 h-5 text-blue-600" />
                <span className="font-medium text-gray-900">Erkannte Entitäten</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {analysis.detected_entities.map((entity, index) => (
                  <span 
                    key={index}
                    className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                  >
                    {entity}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Query Categories */}
          {analysis.query_categories && analysis.query_categories.length > 0 && (
            <div className="bg-white p-4 rounded-lg border border-blue-200">
              <div className="flex items-center space-x-2 mb-3">
                <Info className="w-5 h-5 text-blue-600" />
                <span className="font-medium text-gray-900">Kategorien</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {analysis.query_categories.map((category, index) => (
                  <span 
                    key={index}
                    className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full"
                  >
                    {category}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column */}
        <div className="space-y-4">
          {/* Preferred Document Types */}
          {analysis.preferred_doc_types && analysis.preferred_doc_types.length > 0 && (
            <div className="bg-white p-4 rounded-lg border border-blue-200">
              <div className="flex items-center space-x-2 mb-3">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                <span className="font-medium text-gray-900">Empfohlene Dokumenttypen</span>
              </div>
              <div className="space-y-2">
                {analysis.preferred_doc_types.map((docType, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-gray-700">{docType}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Enhancement Suggestions */}
          {analysis.enhancement_suggestions && analysis.enhancement_suggestions.length > 0 && (
            <div className="bg-white p-4 rounded-lg border border-blue-200">
              <div className="flex items-center space-x-2 mb-3">
                <Lightbulb className="w-5 h-5 text-blue-600" />
                <span className="font-medium text-gray-900">Verbesserungsvorschläge</span>
              </div>
              <div className="space-y-2">
                {analysis.enhancement_suggestions.map((suggestion, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{suggestion}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Analysis Summary */}
      <div className="mt-6 p-4 bg-white rounded-lg border border-blue-200">
        <h4 className="font-medium text-gray-900 mb-2">📊 Analyse-Zusammenfassung</h4>
        <div className="text-sm text-gray-700 space-y-1">
          <p>
            <strong>Intent:</strong> Die Query wurde als "{analysis.primary_intent.replace('_', ' ')}" klassifiziert 
            mit einer Konfidenz von {Math.round(analysis.confidence * 100)}%.
          </p>
          <p>
            <strong>Komplexität:</strong> Die Anfrage hat eine Komplexitätsstufe von {analysis.complexity_level}/10 
            ({getComplexityLabel(analysis.complexity_level)}).
          </p>
          <p>
            <strong>Empfehlung:</strong> Die optimale Suchstrategie ist "{getStrategyDisplayName(analysis.search_strategy)}" 
            für beste Ergebnisse.
          </p>
        </div>
      </div>
    </div>
  );
};