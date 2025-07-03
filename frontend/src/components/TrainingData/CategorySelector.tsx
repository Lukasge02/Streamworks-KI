import React from 'react';
import { Brain, FileText } from 'lucide-react';
import { FileCategory } from './TrainingDataTab';

interface CategorySelectorProps {
  selectedCategory: FileCategory;
  onCategoryChange: (category: FileCategory) => void;
}

export const CategorySelector: React.FC<CategorySelectorProps> = ({
  selectedCategory,
  onCategoryChange
}) => {
  const categories = [
    {
      id: 'help_data' as FileCategory,
      name: 'StreamWorks Hilfe',
      description: 'Q&A Knowledge Base (TXT, CSV, BAT, MD, PS1)',
      icon: Brain,
      color: 'blue',
      extensions: ['.txt', '.csv', '.bat', '.md', '.ps1']
    },
    {
      id: 'stream_templates' as FileCategory,
      name: 'Stream Templates',
      description: 'XML/XSD Templates für Stream-Generierung',
      icon: FileText,
      color: 'green',
      extensions: ['.xml', '.xsd']
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Daten-Kategorie auswählen</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {categories.map((category) => {
          const Icon = category.icon;
          const isSelected = selectedCategory === category.id;
          
          return (
            <button
              key={category.id}
              onClick={() => onCategoryChange(category.id)}
              className={`
                text-left p-4 rounded-lg border-2 transition-all duration-200
                ${isSelected 
                  ? `border-${category.color}-500 bg-${category.color}-50 ring-2 ring-${category.color}-200` 
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }
              `}
            >
              <div className="flex items-start space-x-3">
                <div className={`
                  p-2 rounded-lg
                  ${isSelected 
                    ? `bg-${category.color}-500 text-white` 
                    : 'bg-gray-100 text-gray-600'
                  }
                `}>
                  <Icon className="w-5 h-5" />
                </div>
                
                <div className="flex-1">
                  <h3 className={`
                    font-medium mb-1
                    ${isSelected ? `text-${category.color}-900` : 'text-gray-900'}
                  `}>
                    {category.name}
                  </h3>
                  
                  <p className={`
                    text-sm mb-2
                    ${isSelected ? `text-${category.color}-700` : 'text-gray-600'}
                  `}>
                    {category.description}
                  </p>
                  
                  <div className="flex flex-wrap gap-1">
                    {category.extensions.map((ext) => (
                      <span
                        key={ext}
                        className={`
                          px-2 py-1 text-xs rounded font-mono
                          ${isSelected 
                            ? `bg-${category.color}-100 text-${category.color}-800` 
                            : 'bg-gray-100 text-gray-600'
                          }
                        `}
                      >
                        {ext}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              {isSelected && (
                <div className="mt-3 flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full bg-${category.color}-500`}></div>
                  <span className={`text-sm font-medium text-${category.color}-700`}>
                    Ausgewählt
                  </span>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};