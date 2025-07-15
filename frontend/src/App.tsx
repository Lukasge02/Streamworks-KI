import { Header } from './components/Layout/Header';
import { NavigationTabs } from './components/Layout/NavigationTabs';
import { ModernChatInterface } from './components/Chat/ModernChatInterface';
import TrainingDataTabV2Fixed from './components/TrainingData/TrainingDataTabV2Fixed';
import { EnhancedChunksTab } from './components/Chunks/EnhancedChunksTab';
import { ErrorBoundary } from './components/ErrorHandling/ErrorBoundary';
import { useAppStore } from './store/appStore';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

function App() {
  const { activeTab } = useAppStore();

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'chat':
        return (
          <ErrorBoundary>
            <ModernChatInterface />
          </ErrorBoundary>
        );
      case 'training':
        return (
          <ErrorBoundary>
            <TrainingDataTabV2Fixed />
          </ErrorBoundary>
        );
      case 'chunks':
        return <EnhancedChunksTab />;
      case 'xml':
        return (
          <ErrorBoundary>
            <div className="h-[calc(100vh-200px)] bg-gradient-to-br from-gray-50 via-white to-gray-50 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-lg border border-gray-200/50 flex items-center justify-center">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">XML Generator</h3>
                <p className="text-gray-600">Coming Soon - Stream XML Generation</p>
              </div>
            </div>
          </ErrorBoundary>
        );
      default:
        return (
          <ErrorBoundary>
            <ModernChatInterface />
          </ErrorBoundary>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <Header />
      <NavigationTabs />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderActiveTab()}
      </main>
      <ToastContainer
        position="bottom-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
        className="backdrop-blur-sm"
      />
    </div>
  );
}

export default App;