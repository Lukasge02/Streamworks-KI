import React, { useState } from 'react';
import { 
  ChevronDown, ChevronRight, Info, 
  CheckCircle, AlertCircle 
} from 'lucide-react';
import { 
  FILE_FORMAT_CATEGORIES, 
  TOTAL_SUPPORTED_FORMATS,
  getColorClasses,
  FileFormatCategory
} from '../../utils/fileFormats';

interface FormatInfoPanelProps {
  showDetailed?: boolean;
  className?: string;
}

const FormatInfoPanel: React.FC<FormatInfoPanelProps> = ({ 
  showDetailed = false, 
  className = '' 
}) => {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [showAll, setShowAll] = useState(showDetailed);

  const toggleCategory = (categoryName: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryName)) {
      newExpanded.delete(categoryName);
    } else {
      newExpanded.add(categoryName);
    }
    setExpandedCategories(newExpanded);
  };

  const CategoryCard: React.FC<{ category: FileFormatCategory }> = ({ category }) => {
    const isExpanded = expandedCategories.has(category.name);
    const colors = getColorClasses(category.color);

    return (
      <div className={`border ${colors.border} rounded-lg overflow-hidden`}>
        <button
          onClick={() => toggleCategory(category.name)}
          className={`w-full p-3 ${colors.bg} hover:opacity-80 transition-opacity flex items-center justify-between`}
        >
          <div className="flex items-center gap-3">
            <span className="text-lg">{category.icon}</span>
            <div className="text-left">
              <h4 className={`font-medium ${colors.text}`}>
                {category.name}
              </h4>
              <p className={`text-xs ${colors.text} opacity-75`}>
                {category.extensions.length} formats
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-xs ${colors.text} font-mono`}>
              {category.extensions.length}
            </span>
            {isExpanded ? (
              <ChevronDown className={`h-4 w-4 ${colors.text}`} />
            ) : (
              <ChevronRight className={`h-4 w-4 ${colors.text}`} />
            )}
          </div>
        </button>
        
        {isExpanded && (
          <div className="p-3 bg-white border-t">
            <p className="text-sm text-gray-600 mb-3">
              {category.description}
            </p>
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-1">
              {category.extensions.map(ext => (
                <span
                  key={ext}
                  className={`inline-block px-2 py-1 text-xs font-mono rounded ${colors.bg} ${colors.text}`}
                >
                  {ext}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (!showAll) {
    return (
      <div className={`bg-blue-50 border border-blue-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-start gap-3">
          <Info className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="font-medium text-blue-900 mb-1">
              Unterstützte Dateiformate
            </h3>
            <p className="text-sm text-blue-700 mb-2">
              {TOTAL_SUPPORTED_FORMATS} verschiedene Dateiformate werden unterstützt:
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
              {FILE_FORMAT_CATEGORIES.map(category => (
                <div key={category.name} className="flex items-center gap-2">
                  <span className="text-sm">{category.icon}</span>
                  <span className="text-xs text-blue-700">
                    {category.extensions.length} {category.name.split(' ')[0]}
                  </span>
                </div>
              ))}
            </div>
            <button
              onClick={() => setShowAll(true)}
              className="text-sm text-blue-600 hover:text-blue-800 underline"
            >
              Alle Formate anzeigen →
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold mb-1">
              Multi-Format Document Processor
            </h3>
            <p className="text-blue-100 text-sm">
              {TOTAL_SUPPORTED_FORMATS} Dateiformate in {FILE_FORMAT_CATEGORIES.length} Kategorien
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{TOTAL_SUPPORTED_FORMATS}</div>
            <div className="text-blue-100 text-xs">Formate</div>
          </div>
        </div>
      </div>

      <div className="grid gap-3">
        {FILE_FORMAT_CATEGORIES.map(category => (
          <CategoryCard key={category.name} category={category} />
        ))}
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-green-900 mb-1">
              Intelligente Verarbeitung
            </h4>
            <p className="text-sm text-green-700 mb-2">
              Jedes Format wird mit optimierter Chunking-Strategie verarbeitet:
            </p>
            <ul className="text-xs text-green-600 space-y-1">
              <li>• <strong>Code-Dateien:</strong> Funktions-/Klassen-basiertes Chunking</li>
              <li>• <strong>Markdown:</strong> Header-basierte Strukturierung</li>
              <li>• <strong>XML:</strong> Element-basierte Segmentierung</li>
              <li>• <strong>JSON:</strong> Struktur-bewusste Aufteilung</li>
              <li>• <strong>CSV:</strong> Row-basierte Verarbeitung</li>
              <li>• <strong>HTML:</strong> Tag-basierte Sectioning</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-yellow-900 mb-1">
              Upload-Beschränkungen
            </h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Maximale Dateigröße: 50MB pro Datei</li>
              <li>• Batch-Upload: Bis zu 20 Dateien gleichzeitig</li>
              <li>• Automatische Format-Erkennung und Validierung</li>
              <li>• Intelligente Kategorisierung nach Dateiinhalt</li>
            </ul>
          </div>
        </div>
      </div>

      {showDetailed && (
        <div className="text-center">
          <button
            onClick={() => setShowAll(false)}
            className="text-sm text-gray-600 hover:text-gray-800 underline"
          >
            ← Weniger anzeigen
          </button>
        </div>
      )}
    </div>
  );
};

export default FormatInfoPanel;