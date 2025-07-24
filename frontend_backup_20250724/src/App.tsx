import { Header } from './components/Layout/Header';
import { NavigationSidebar } from './components/Layout/NavigationTabs';
import { ModernChatInterface } from './components/Chat/ModernChatInterface';
import { SimpleTrainingData } from './components/TrainingData/SimpleTrainingData';
import { XMLGeneratorTab } from './components/XML/XMLGeneratorTab';
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
            <XMLGeneratorTab />
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