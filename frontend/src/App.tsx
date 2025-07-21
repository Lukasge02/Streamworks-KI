import { Header } from './components/Layout/Header';
import { NavigationSidebar } from './components/Layout/NavigationTabs';
import { ModernChatInterface } from './components/Chat/ModernChatInterface';
import { SimpleTrainingData } from './components/TrainingData/SimpleTrainingData';
import SettingsTab from './components/Settings/SettingsTab';
import { ErrorBoundary } from './components/ErrorHandling/ErrorBoundary';
import { DarkModeInitializer } from './components/Layout/DarkModeInitializer';
import { useAppStore } from './store/appStore';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';
// Enterprise Components
// import EnterpriseTrainingData from './components/Training/EnterpriseTrainingData';

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
            <div className="h-full overflow-y-auto">
              <SimpleTrainingData />
            </div>
          </ErrorBoundary>
        );
      case 'xml':
        return (
          <ErrorBoundary>
            <div className="h-full bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-lg border border-gray-200/50 dark:border-gray-700/50 flex items-center justify-center">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-2">XML Generator</h3>
                <p className="text-gray-600 dark:text-gray-300">Coming Soon - Stream XML Generation</p>
              </div>
            </div>
          </ErrorBoundary>
        );
      case 'settings':
        return (
          <ErrorBoundary>
            <SettingsTab />
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
    <div className="h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 overflow-hidden flex flex-col">
      <Header />
      <div className="flex-1 flex overflow-hidden">
        <NavigationSidebar />
        <main className="flex-1 px-4 py-4 overflow-hidden">
          {renderActiveTab()}
        </main>
      </div>
      <DarkModeInitializer />
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