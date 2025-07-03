import React from 'react';
import { Header } from './components/Layout/Header';
import { NavigationTabs } from './components/Layout/NavigationTabs';
import { ChatInterface } from './components/Chat/ChatInterface';
import { StreamGeneratorForm } from './components/StreamGenerator/StreamGeneratorForm';
import { DocumentationTab } from './components/Documentation/DocumentationTab';
import { useAppStore } from './store/appStore';
import './App.css';

function App() {
  const { activeTab } = useAppStore();

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'chat':
        return <ChatInterface />;
      case 'generator':
        return <StreamGeneratorForm />;
      case 'docs':
        return <DocumentationTab />;
      default:
        return <ChatInterface />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      <NavigationTabs />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderActiveTab()}
      </main>
    </div>
  );
}

export default App;