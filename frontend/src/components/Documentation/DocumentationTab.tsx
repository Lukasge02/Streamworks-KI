import React from 'react';
import { Book, Code, FileCode, Terminal } from 'lucide-react';

export const DocumentationTab: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Book className="h-6 w-6 text-blue-600" />
          <h2 className="text-xl font-bold text-gray-900">Erste Schritte</h2>
        </div>
        <div className="space-y-4 text-gray-600">
          <p>
            StreamWorks-KI ist eine intelligente Assistenz für die Automatisierung von Workloads.
            Die KI hilft Ihnen bei der Erstellung von XML-Streams und der Analyse von Batch-Dateien.
          </p>
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Hauptfunktionen:</h3>
            <ul className="list-disc list-inside space-y-1">
              <li>Intelligenter Chat für Fragen und Antworten</li>
              <li>Automatische XML-Stream-Generierung</li>
              <li>Batch-Datei-Analyse und -Optimierung</li>
              <li>Integration mit bestehenden StreamWorks-Systemen</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Code className="h-6 w-6 text-green-600" />
          <h2 className="text-xl font-bold text-gray-900">API-Referenz</h2>
        </div>
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Endpoints:</h3>
            <div className="space-y-2">
              <div className="bg-gray-50 p-3 rounded-lg font-mono text-sm">
                <span className="text-green-600">POST</span> /api/chat
              </div>
              <div className="bg-gray-50 p-3 rounded-lg font-mono text-sm">
                <span className="text-green-600">POST</span> /api/generate-stream
              </div>
              <div className="bg-gray-50 p-3 rounded-lg font-mono text-sm">
                <span className="text-green-600">POST</span> /api/upload
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-4">
          <FileCode className="h-6 w-6 text-purple-600" />
          <h2 className="text-xl font-bold text-gray-900">XML-Stream Format</h2>
        </div>
        <div className="space-y-4">
          <p className="text-gray-600">
            StreamWorks verwendet ein strukturiertes XML-Format für die Definition von Workflows:
          </p>
          <pre className="bg-gray-50 p-3 rounded-lg overflow-x-auto text-sm">
{`<?xml version="1.0" encoding="UTF-8"?>
<stream>
  <n>StreamName</n>
  <job>
    <n>JobName</n>
    <startTime>08:00</startTime>
    <dataSource>/path/to/data</dataSource>
    <outputPath>/path/to/output</outputPath>
    <schedule>daily</schedule>
  </job>
</stream>`}
          </pre>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Terminal className="h-6 w-6 text-orange-600" />
          <h2 className="text-xl font-bold text-gray-900">Beispiel-Befehle</h2>
        </div>
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Chat-Anfragen:</h3>
            <ul className="space-y-2 text-gray-600">
              <li>• "Erstelle einen Stream für tägliche Backups"</li>
              <li>• "Analysiere meine Batch-Datei"</li>
              <li>• "Was ist der beste Zeitpunkt für einen Job?"</li>
              <li>• "Wie optimiere ich meinen Workflow?"</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};