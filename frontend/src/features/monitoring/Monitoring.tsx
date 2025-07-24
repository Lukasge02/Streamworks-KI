import { Card, CardHeader, CardContent } from '@/shared/components';
import { Activity, Server } from 'lucide-react';

export function Monitoring() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
          System Monitoring
        </h1>
        <p className="text-neutral-600 dark:text-neutral-400">
          Real-time system health and performance monitoring
        </p>
      </div>

      <Card variant="elevated" className="h-[600px]">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Activity size={20} className="text-primary-600" />
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
              System Health Monitor
            </h3>
          </div>
        </CardHeader>
        <CardContent className="h-full flex flex-col">
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center mx-auto">
                <Server size={32} className="text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-neutral-900 dark:text-neutral-100">
                  Monitoring Dashboard Coming Soon
                </h3>
                <p className="text-neutral-600 dark:text-neutral-400">
                  Real-time system monitoring and alerts
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}