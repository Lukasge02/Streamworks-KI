/**
 * Centralized file format configuration for Streamworks-KI
 * Matches the backend multi-format processor capabilities
 */

export interface FileFormatCategory {
  name: string;
  extensions: string[];
  description: string;
  icon: string;
  color: string;
}

export const FILE_FORMAT_CATEGORIES: FileFormatCategory[] = [
  {
    name: 'Text & Documentation',
    extensions: ['.txt', '.md', '.rtf', '.log'],
    description: 'Plain text, Markdown, rich text, and log files',
    icon: '📝',
    color: 'blue'
  },
  {
    name: 'Office Documents',
    extensions: ['.pdf', '.docx', '.doc', '.odt'],
    description: 'PDF, Word documents, and OpenDocument text',
    icon: '📄',
    color: 'green'
  },
  {
    name: 'Structured Data',
    extensions: ['.csv', '.tsv', '.xlsx', '.xls', '.json', '.jsonl', '.yaml', '.yml', '.toml'],
    description: 'Spreadsheets, JSON, YAML, and structured data formats',
    icon: '📊',
    color: 'purple'
  },
  {
    name: 'XML Family',
    extensions: ['.xml', '.xsd', '.xsl', '.svg', '.rss', '.atom'],
    description: 'XML documents, schemas, stylesheets, and feeds',
    icon: '🏗️',
    color: 'orange'
  },
  {
    name: 'Code & Scripts',
    extensions: ['.py', '.js', '.ts', '.java', '.sql', '.ps1', '.bat', '.sh', '.bash'],
    description: 'Source code, scripts, and database queries',
    icon: '💻',
    color: 'indigo'
  },
  {
    name: 'Web & Markup',
    extensions: ['.html', '.htm'],
    description: 'HTML web pages and markup documents',
    icon: '🌐',
    color: 'teal'
  },
  {
    name: 'Configuration',
    extensions: ['.ini', '.cfg', '.conf'],
    description: 'Configuration files and settings',
    icon: '⚙️',
    color: 'gray'
  },
  {
    name: 'Email',
    extensions: ['.msg', '.eml'],
    description: 'Email messages and mailbox files',
    icon: '📧',
    color: 'red'
  }
];

// All supported extensions in a flat array
export const SUPPORTED_EXTENSIONS = FILE_FORMAT_CATEGORIES.flatMap(category => category.extensions);

// Total count of supported formats
export const TOTAL_SUPPORTED_FORMATS = SUPPORTED_EXTENSIONS.length;

// Get category for a file extension
export const getCategoryForExtension = (extension: string): FileFormatCategory | null => {
  const normalizedExt = extension.toLowerCase();
  if (!normalizedExt.startsWith('.')) {
    return getCategoryForExtension('.' + normalizedExt);
  }
  
  return FILE_FORMAT_CATEGORIES.find(category => 
    category.extensions.includes(normalizedExt)
  ) || null;
};

// Check if file extension is supported
export const isSupportedExtension = (extension: string): boolean => {
  return SUPPORTED_EXTENSIONS.includes(extension.toLowerCase());
};

// Get file extension from filename
export const getFileExtension = (filename: string): string => {
  const parts = filename.split('.');
  return parts.length > 1 ? '.' + parts[parts.length - 1].toLowerCase() : '';
};

// Validate file for upload
export interface FileValidationResult {
  isValid: boolean;
  error?: string;
  category?: FileFormatCategory;
}

export const validateFile = (file: File, maxSizeBytes: number = 50 * 1024 * 1024): FileValidationResult => {
  const extension = getFileExtension(file.name);
  
  // Check extension
  if (!isSupportedExtension(extension)) {
    return {
      isValid: false,
      error: `Unsupported file type: ${extension}. Supported: ${SUPPORTED_EXTENSIONS.join(', ')}`
    };
  }
  
  // Check size
  if (file.size > maxSizeBytes) {
    return {
      isValid: false,
      error: `File too large: ${(file.size / 1024 / 1024).toFixed(1)}MB. Max: ${(maxSizeBytes / 1024 / 1024).toFixed(1)}MB`
    };
  }
  
  const category = getCategoryForExtension(extension);
  return {
    isValid: true,
    category: category || undefined
  };
};

// Format file size for display
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

// Dropzone accept configuration
export const getDropzoneAcceptConfig = () => {
  const config: Record<string, string[]> = {};
  
  FILE_FORMAT_CATEGORIES.forEach(category => {
    if (category.name === 'Office Documents') {
      config['application/*'] = category.extensions;
    } else {
      config['text/*'] = (config['text/*'] || []).concat(category.extensions);
    }
  });
  
  return config;
};

// Color classes for Tailwind CSS
export const getColorClasses = (color: string) => {
  const colorMap: Record<string, { bg: string; text: string; border: string }> = {
    blue: { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-200' },
    green: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-200' },
    purple: { bg: 'bg-purple-100', text: 'text-purple-800', border: 'border-purple-200' },
    orange: { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-200' },
    indigo: { bg: 'bg-indigo-100', text: 'text-indigo-800', border: 'border-indigo-200' },
    teal: { bg: 'bg-teal-100', text: 'text-teal-800', border: 'border-teal-200' },
    gray: { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-200' },
    red: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-200' }
  };
  
  return colorMap[color] || colorMap.blue;
};