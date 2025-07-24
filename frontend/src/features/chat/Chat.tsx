import { Card, CardHeader, CardContent } from '@/shared/components';
import { MessageSquare, Bot } from 'lucide-react';

export function Chat() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
          KI Chat
        </h1>
        <p className="text-neutral-600 dark:text-neutral-400">
          Interact with your documents using AI-powered conversations
        </p>
      </div>

      <Card variant="elevated" className="h-[600px]">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <MessageSquare size={20} className="text-primary-600" />
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
              Chat Assistant
            </h3>
          </div>
        </CardHeader>
        <CardContent className="h-full flex flex-col">
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center mx-auto">
                <Bot size={32} className="text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-neutral-900 dark:text-neutral-100">
                  Chat Module Coming Soon
                </h3>
                <p className="text-neutral-600 dark:text-neutral-400">
                  RAG-powered conversations with your documents
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}