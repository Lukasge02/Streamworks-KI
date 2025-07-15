import { Header } from './components/Layout/Header';
import { NavigationTabs } from './components/Layout/NavigationTabs';
import { DualModeChat } from './components/Chat/DualModeChat';
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
            <DualModeChat />
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
      default:
        return (
          <ErrorBoundary>
            <DualModeChat />
          </ErrorBoundary>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
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
      />
    </div>
  );
}

export default App;