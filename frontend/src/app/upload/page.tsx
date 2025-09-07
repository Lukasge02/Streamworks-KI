'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Upload, 
  CheckCircle, 
  AlertTriangle, 
  Info, 
  Settings,
  FileText,
  Database,
  Zap
} from 'lucide-react';

import { ProfessionalUploadDropzone } from '@/components/professional-upload';

interface UploadStats {
  totalUploads: number;
  successfulUploads: number;
  failedUploads: number;
  totalChunks: number;
  processingTimeTotal: number;
}

export default function UnifiedUploadPage() {
  const [stats, setStats] = useState<UploadStats>({
    totalUploads: 0,
    successfulUploads: 0,
    failedUploads: 0,
    totalChunks: 0,
    processingTimeTotal: 0
  });
  
  const [recentUploads, setRecentUploads] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<Array<{id: string, type: 'success' | 'error' | 'info', message: string}>>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleUploadComplete = (result: any) => {
    console.log('Upload completed:', result);
    
    // Update stats
    setStats(prev => ({
      totalUploads: prev.totalUploads + 1,
      successfulUploads: prev.successfulUploads + 1,
      failedUploads: prev.failedUploads,
      totalChunks: prev.totalChunks + (result.chunk_count || 0),
      processingTimeTotal: prev.processingTimeTotal + (result.processing_time_seconds || 0)
    }));

    // Add to recent uploads
    setRecentUploads(prev => [{
      ...result,
      timestamp: new Date().toISOString()
    }, ...prev.slice(0, 4)]);

    // Show success alert
    addAlert('success', `Successfully uploaded "${result.filename}" with ${result.chunk_count} chunks!`);
  };

  const handleUploadError = (error: string) => {
    console.error('Upload error:', error);
    
    // Update stats
    setStats(prev => ({
      ...prev,
      totalUploads: prev.totalUploads + 1,
      failedUploads: prev.failedUploads + 1
    }));

    // Show error alert
    addAlert('error', `Upload failed: ${error}`);
  };

  const addAlert = (type: 'success' | 'error' | 'info', message: string) => {
    const id = Date.now().toString();
    setAlerts(prev => [...prev, { id, type, message }]);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setAlerts(prev => prev.filter(alert => alert.id !== id));
    }, 5000);
  };

  const clearRecentUploads = () => {
    setRecentUploads([]);
    addAlert('info', 'Recent uploads cleared');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Upload className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Unified Document Upload
              </h1>
              <p className="text-gray-600 mt-1">
                Single, high-quality pipeline for all document types
              </p>
            </div>
          </div>

          {/* Feature Badges */}
          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary" className="flex items-center gap-1">
              <Zap className="w-3 h-3" />
              Real-time Progress
            </Badge>
            <Badge variant="secondary" className="flex items-center gap-1">
              <Database className="w-3 h-3" />
              Unified Storage
            </Badge>
            <Badge variant="secondary" className="flex items-center gap-1">
              <FileText className="w-3 h-3" />
              Multiple Formats
            </Badge>
            <Badge variant="secondary" className="flex items-center gap-1">
              <Settings className="w-3 h-3" />
              Advanced Options
            </Badge>
          </div>
        </div>

        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="space-y-2 mb-6">
            {alerts.map(alert => (
              <Alert 
                key={alert.id} 
                className={
                  alert.type === 'error' ? 'border-red-200 bg-red-50' :
                  alert.type === 'success' ? 'border-green-200 bg-green-50' :
                  'border-blue-200 bg-blue-50'
                }
              >
                {alert.type === 'error' ? (
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                ) : alert.type === 'success' ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <Info className="h-4 w-4 text-blue-600" />
                )}
                <AlertDescription className={
                  alert.type === 'error' ? 'text-red-800' :
                  alert.type === 'success' ? 'text-green-800' :
                  'text-blue-800'
                }>
                  {alert.message}
                </AlertDescription>
              </Alert>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Upload Area */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="upload" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="upload" className="flex items-center gap-2">
                  <Upload className="w-4 h-4" />
                  Upload Documents
                </TabsTrigger>
                <TabsTrigger value="advanced" className="flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  Advanced Settings
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="upload" className="mt-6">
                <ProfessionalUploadDropzone
                  onUploadComplete={handleUploadComplete}
                  onUploadError={handleUploadError}
                  maxFiles={10}
                  maxSizeBytes={100 * 1024 * 1024}
                  folderId="default"
                />
              </TabsContent>
              
              <TabsContent value="advanced" className="mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Advanced Upload Configuration</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">Show Advanced Options</h4>
                        <p className="text-sm text-gray-600">
                          Enable advanced processing options in upload form
                        </p>
                      </div>
                      <Button
                        variant={showAdvanced ? "default" : "outline"}
                        onClick={() => setShowAdvanced(!showAdvanced)}
                      >
                        {showAdvanced ? 'Enabled' : 'Disabled'}
                      </Button>
                    </div>
                    
                    <div className="pt-4 border-t">
                      <h4 className="font-medium mb-2">Supported Features</h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• Multiple chunking strategies (Standard, Aggressive, Conservative, Hybrid)</li>
                        <li>• Automatic vector database indexing</li>
                        <li>• Document deduplication and replacement</li>
                        <li>• Multi-language support (German, English, Auto-detect)</li>
                        <li>• Visibility controls (Internal, Public, Restricted)</li>
                        <li>• Real-time progress monitoring</li>
                        <li>• Asynchronous and synchronous processing modes</li>
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Upload Statistics */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Session Statistics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {stats.totalUploads}
                    </div>
                    <div className="text-xs text-blue-800">Total Uploads</div>
                  </div>
                  
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {stats.successfulUploads}
                    </div>
                    <div className="text-xs text-green-800">Successful</div>
                  </div>
                  
                  <div className="text-center p-3 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {stats.totalChunks}
                    </div>
                    <div className="text-xs text-orange-800">Total Chunks</div>
                  </div>
                  
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {stats.failedUploads}
                    </div>
                    <div className="text-xs text-purple-800">Failed</div>
                  </div>
                </div>

                {stats.processingTimeTotal > 0 && (
                  <div className="mt-4 text-center">
                    <div className="text-sm text-gray-600">
                      Average processing time: {(stats.processingTimeTotal / Math.max(stats.successfulUploads, 1)).toFixed(1)}s
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Uploads */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Recent Uploads</CardTitle>
                  {recentUploads.length > 0 && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={clearRecentUploads}
                    >
                      Clear
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {recentUploads.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <Upload className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No uploads yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {recentUploads.map((upload, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium truncate">
                            {upload.filename}
                          </div>
                          <div className="text-xs text-gray-600">
                            {upload.chunk_count} chunks • {upload.category}
                          </div>
                          <div className="text-xs text-gray-500">
                            ID: {upload.document_id?.slice(-8)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* System Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">System Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Upload Endpoint</span>
                    <Badge variant="secondary">Unified (/api/upload)</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Storage</span>
                    <Badge variant="secondary">StreamWorks Unified</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Processing</span>
                    <Badge variant="secondary">Real-time Job Manager</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Vector DB</span>
                    <Badge variant="secondary">ChromaDB</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}