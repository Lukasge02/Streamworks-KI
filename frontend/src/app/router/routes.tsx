import { createBrowserRouter } from 'react-router-dom';
import { Layout } from '@/shared/components/Layout/Layout';
import { Dashboard } from '@/features/dashboard/Dashboard';
import { Chat } from '@/features/chat/Chat';
import { Documents } from '@/features/documents/Documents';
import { XMLGenerator } from '@/features/xml-generator/XMLGenerator';
import { Analytics } from '@/features/analytics/Analytics';
import { Monitoring } from '@/features/monitoring/Monitoring';
import { Training } from '@/features/training/Training';
import { Settings } from '@/features/settings/Settings';
import { EnterpriseComponentsDemo } from '@/components/Demo/EnterpriseComponentsDemo';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'chat',
        element: <Chat />,
      },
      {
        path: 'documents',
        element: <Documents />,
      },
      {
        path: 'xml-generator',
        element: <XMLGenerator />,
      },
      {
        path: 'analytics',
        element: <Analytics />,
      },
      {
        path: 'monitoring',
        element: <Monitoring />,
      },
      {
        path: 'training',
        element: <Training />,
      },
      {
        path: 'settings',
        element: <Settings />,
      },
      {
        path: 'demo',
        element: <EnterpriseComponentsDemo />,
      },
    ],
  },
]);