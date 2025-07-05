import { Header } from './components/Layout/Header';
import { NavigationTabs } from './components/Layout/NavigationTabs';
import { DualModeChat } from './components/Chat/DualModeChat';
import { SmartSearchTab } from './components/SmartSearch/SmartSearchTab';
import { StreamGeneratorForm } from './components/StreamGenerator/StreamGeneratorForm';
import TrainingDataTabV2Fixed from './components/TrainingData/TrainingDataTabV2Fixed';
import { DocumentationTab } from './components/Documentation/DocumentationTab';
import { useAppStore } from './store/appStore';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

function App() {
  const { activeTab } = useAppStore();

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'chat':
        return <DualModeChat />;
      case 'search':
        return <SmartSearchTab />;
      case 'generator':
        return <StreamGeneratorForm />;
      case 'training':
        return <TrainingDataTabV2Fixed />;
      case 'docs':
        return <DocumentationTab />;
      default:
        return <DualModeChat />;
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