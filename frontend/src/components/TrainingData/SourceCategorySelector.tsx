import React, { useState, useEffect } from 'react';
import { SourceCategory, SourceCategoryInfo, apiService } from '../../services/apiService';

interface SourceCategorySelectorProps {
  selectedCategory: SourceCategory;
  onCategoryChange: (category: SourceCategory) => void;
  className?: string;
}

export const SourceCategorySelector: React.FC<SourceCategorySelectorProps> = ({
  selectedCategory,
  onCategoryChange,
  className = ""
}) => {
  const [categories, setCategories] = useState<SourceCategoryInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await apiService.getSourceCategories();
      if (response.success && response.data) {
        setCategories(response.data.categories);
      } else {
        console.error('Failed to load source categories:', response.error);
        // Fallback categories
        setCategories([
          { value: 'Testdaten', description: 'Training Data aus Testdaten', icon: '📚' },
          { value: 'StreamWorks Hilfe', description: 'Training Data aus StreamWorks Hilfe', icon: '🏢' },
          { value: 'SharePoint', description: 'Training Data aus SharePoint', icon: '☁️' }
        ]);
      }
    } catch (error) {
      console.error('Error loading categories:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="h-10 bg-gray-200 rounded"></div>
      </div>
    );
  }

  return (
    <div className={className}>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Datenquelle auswählen
      </label>
      <select
        value={selectedCategory}
        onChange={(e) => onCategoryChange(e.target.value as SourceCategory)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        {categories.map((category) => (
          <option key={category.value} value={category.value}>
            {category.icon} {category.value}
          </option>
        ))}
      </select>
      <p className="mt-1 text-xs text-gray-500">
        {categories.find(c => c.value === selectedCategory)?.description}
      </p>
    </div>
  );
};