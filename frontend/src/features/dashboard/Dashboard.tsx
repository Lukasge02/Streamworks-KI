import { Card, CardHeader, CardContent, LoadingSpinner } from '@/shared/components';
import { useSystemStatus } from '@/shared/hooks';
import { Activity, Users, FileText, MessageSquare, CheckCircle, XCircle, Clock } from 'lucide-react';

export function Dashboard() {
  const { services, isLoading, overallStatus } = useSystemStatus();
  
  const stats = [
    { label: 'Dokumente', value: '1,234', icon: FileText, color: 'text-blue-600' },
    { label: 'Chat Sessions', value: '567', icon: MessageSquare, color: 'text-green-600' },
    { label: 'System Health', value: overallStatus === 'healthy' ? '100%' : '...', icon: Activity, color: 'text-purple-600' },
    { label: 'Active Users', value: '23', icon: Users, color: 'text-orange-600' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
          Dashboard
        </h1>
        <p className="text-neutral-600 dark:text-neutral-400">
          Welcome to StreamWorks-KI Enterprise Dashboard
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card key={index} variant="elevated" hover>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
                    {stat.label}
                  </p>
                  <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                    {stat.value}
                  </p>
                </div>
                <div className={`p-3 rounded-lg bg-neutral-100 dark:bg-neutral-800 ${stat.color}`}>
                  <stat.icon size={24} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card variant="elevated">
          <CardHeader>
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
              System Status
            </h3>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <LoadingSpinner />
                  <span className="ml-2 text-sm text-neutral-600 dark:text-neutral-400">
                    Checking system status...
                  </span>
                </div>
              ) : (
                services.map((service, index) => {
                  const getStatusInfo = () => {
                    if (service.error) {
                      return {
                        label: 'Error',
                        color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
                        icon: XCircle
                      };
                    }
                    if (service.data?.status === 'healthy' || service.data?.ready === true) {
                      return {
                        label: 'Healthy',
                        color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
                        icon: CheckCircle
                      };
                    }
                    return {
                      label: 'Unknown',
                      color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
                      icon: Clock
                    };
                  };

                  const statusInfo = getStatusInfo();
                  const StatusIcon = statusInfo.icon;

                  return (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm text-neutral-600 dark:text-neutral-400">
                        {service.name}
                      </span>
                      <div className="flex items-center space-x-2">
                        <StatusIcon size={14} className={statusInfo.color.includes('green') ? 'text-green-600' : statusInfo.color.includes('red') ? 'text-red-600' : 'text-yellow-600'} />
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </CardContent>
        </Card>

        <Card variant="elevated">
          <CardHeader>
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
              Quick Actions
            </h3>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <button className="w-full text-left p-3 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors">
                <div className="font-medium text-neutral-900 dark:text-neutral-100">
                  Start New Chat
                </div>
                <div className="text-sm text-neutral-600 dark:text-neutral-400">
                  Ask questions about your documents
                </div>
              </button>
              
              <button className="w-full text-left p-3 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors">
                <div className="font-medium text-neutral-900 dark:text-neutral-100">
                  Upload Documents
                </div>
                <div className="text-sm text-neutral-600 dark:text-neutral-400">
                  Add new files to knowledge base
                </div>
              </button>
              
              <button className="w-full text-left p-3 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors">
                <div className="font-medium text-neutral-900 dark:text-neutral-100">
                  Generate XML
                </div>
                <div className="text-sm text-neutral-600 dark:text-neutral-400">
                  Create StreamWorks configurations
                </div>
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}