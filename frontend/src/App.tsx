import { RouterProvider } from 'react-router-dom';
import { QueryProvider } from '@/app/providers/QueryProvider';
import { ThemeProvider } from '@/app/providers/ThemeProvider';
import { ToastProvider, ErrorBoundary } from '@/shared/components';
import { router } from '@/app/router/routes';

function App() {
  return (
    <ErrorBoundary>
      <QueryProvider>
        <ThemeProvider>
          <ToastProvider position="top-right">
            <RouterProvider router={router} />
          </ToastProvider>
        </ThemeProvider>
      </QueryProvider>
    </ErrorBoundary>
  );
}

export default App;