import React from 'react';
import { Brain, FileText, CheckCircle, Clock, AlertCircle, BarChart3 } from 'lucide-react';

interface CategoryStats {
  total: number;
  ready: number;
  processing: number;
  error: number;
}

interface TrainingStatusProps {
  helpDataStats: CategoryStats;
  streamTemplateStats: CategoryStats;
}

export const TrainingStatus: React.FC<TrainingStatusProps> = ({
  helpDataStats,
  streamTemplateStats
}) => {
  const getProgressPercentage = (stats: CategoryStats): number => {
    if (stats.total === 0) return 0;
    return Math.round((stats.ready / stats.total) * 100);
  };

  const getStatusColor = (stats: CategoryStats): string => {
    if (stats.error > 0) return 'red';
    if (stats.processing > 0) return 'yellow';
    if (stats.ready === stats.total && stats.total > 0) return 'green';
    return 'gray';
  };

  const StatCard: React.FC<{
    title: string;
    description: string;
    icon: React.ElementType;
    stats: CategoryStats;
    color: string;
  }> = ({ title, description, icon: Icon, stats, color }) => {
    const progress = getProgressPercentage(stats);
    const statusColor = getStatusColor(stats);
    
    return (
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`p-3 rounded-lg bg-${color}-100`}>
              <Icon className={`w-6 h-6 text-${color}-600`} />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{title}</h3>
              <p className="text-sm text-gray-600">{description}</p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
            <div className="text-sm text-gray-500">Dateien</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-600">Fortschritt</span>
            <span className="font-medium text-gray-900">{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`bg-${statusColor}-500 h-2 rounded-full transition-all duration-300`}
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Status Details */}
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <div>
              <div className="font-medium text-gray-900">{stats.ready}</div>
              <div className="text-gray-500">Bereit</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-yellow-500" />
            <div>
              <div className="font-medium text-gray-900">{stats.processing}</div>
              <div className="text-gray-500">Verarbeitung</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-500" />
            <div>
              <div className="font-medium text-gray-900">{stats.error}</div>
              <div className="text-gray-500">Fehler</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const totalFiles = helpDataStats.total + streamTemplateStats.total;
  const totalReady = helpDataStats.ready + streamTemplateStats.ready;
  const overallProgress = totalFiles > 0 ? Math.round((totalReady / totalFiles) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold mb-2">Training Data Status</h2>
            <p className="text-blue-100">
              Übersicht über alle hochgeladenen Trainingsdaten
            </p>
          </div>
          
          <div className="text-right">
            <div className="text-3xl font-bold">{overallProgress}%</div>
            <div className="text-blue-100">Gesamt-Fortschritt</div>
          </div>
        </div>
        
        <div className="mt-4 flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5" />
            <span className="text-blue-100">
              {totalReady} von {totalFiles} Dateien bereit
            </span>
          </div>
        </div>
      </div>

      {/* Category Statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <StatCard
          title="StreamWorks Hilfe"
          description="Q&A Knowledge Base für intelligente Antworten"
          icon={Brain}
          stats={helpDataStats}
          color="blue"
        />
        
        <StatCard
          title="Stream Templates"
          description="XML/XSD Templates für Stream-Generierung"
          icon={FileText}
          stats={streamTemplateStats}
          color="green"
        />
      </div>

      {/* Training Readiness */}
      {totalFiles > 0 && (
        <div className="bg-white rounded-lg border shadow-sm p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Training-Bereitschaft</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg">
              <div className="flex items-center space-x-3 mb-2">
                <Brain className="w-5 h-5 text-blue-600" />
                <span className="font-medium">Q&A Fine-Tuning</span>
              </div>
              <div className={`
                text-sm px-3 py-1 rounded-full inline-block
                ${helpDataStats.ready > 0 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-600'
                }
              `}>
                {helpDataStats.ready > 0 
                  ? `Bereit mit ${helpDataStats.ready} Dateien`
                  : 'Warten auf Daten'
                }
              </div>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center space-x-3 mb-2">
                <FileText className="w-5 h-5 text-green-600" />
                <span className="font-medium">Template-Training</span>
              </div>
              <div className={`
                text-sm px-3 py-1 rounded-full inline-block
                ${streamTemplateStats.ready > 0 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-600'
                }
              `}>
                {streamTemplateStats.ready > 0 
                  ? `Bereit mit ${streamTemplateStats.ready} Templates`
                  : 'Warten auf Templates'
                }
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};