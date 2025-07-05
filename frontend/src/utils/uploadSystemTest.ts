/**
 * Upload System Test Utilities
 * Verifies that the upload system properly supports all 39+ formats
 */

import { 
  SUPPORTED_EXTENSIONS, 
  TOTAL_SUPPORTED_FORMATS,
  validateFile,
  getCategoryForExtension,
  FILE_FORMAT_CATEGORIES 
} from './fileFormats';

export interface UploadSystemTestResult {
  success: boolean;
  totalFormats: number;
  testedFormats: number;
  passedValidation: number;
  failedValidation: number;
  missingCategories: string[];
  formatBreakdown: {
    [category: string]: {
      tested: number;
      passed: number;
      failed: number;
    };
  };
  errors: string[];
}

/**
 * Creates mock files for testing all supported formats
 */
export const createMockFiles = (): File[] => {
  const mockFiles: File[] = [];
  
  SUPPORTED_EXTENSIONS.forEach(ext => {
    // Create a small mock file for each extension
    const content = `Mock content for ${ext} file\nThis is test data for format validation.`;
    const blob = new Blob([content], { type: 'text/plain' });
    const file = new File([blob], `test${ext}`, { type: 'text/plain' });
    
    // Mock the file size to be reasonable (1KB)
    Object.defineProperty(file, 'size', {
      value: 1024,
      writable: false
    });
    
    mockFiles.push(file);
  });
  
  return mockFiles;
};

/**
 * Tests the upload system with all supported formats
 */
export const testUploadSystem = (): UploadSystemTestResult => {
  const result: UploadSystemTestResult = {
    success: false,
    totalFormats: TOTAL_SUPPORTED_FORMATS,
    testedFormats: 0,
    passedValidation: 0,
    failedValidation: 0,
    missingCategories: [],
    formatBreakdown: {},
    errors: []
  };

  try {
    const mockFiles = createMockFiles();
    result.testedFormats = mockFiles.length;

    // Initialize format breakdown
    FILE_FORMAT_CATEGORIES.forEach(category => {
      result.formatBreakdown[category.name] = {
        tested: 0,
        passed: 0,
        failed: 0
      };
    });

    // Test each file
    mockFiles.forEach(file => {
      const validation = validateFile(file);
      const category = getCategoryForExtension(file.name.split('.').pop() || '');
      
      if (category) {
        result.formatBreakdown[category.name].tested++;
        
        if (validation.isValid) {
          result.passedValidation++;
          result.formatBreakdown[category.name].passed++;
        } else {
          result.failedValidation++;
          result.formatBreakdown[category.name].failed++;
          result.errors.push(`${file.name}: ${validation.error}`);
        }
      } else {
        result.missingCategories.push(file.name);
        if (validation.isValid) {
          result.passedValidation++;
        } else {
          result.failedValidation++;
          result.errors.push(`${file.name}: ${validation.error}`);
        }
      }
    });

    // Determine overall success
    result.success = result.failedValidation === 0 && result.missingCategories.length === 0;

    return result;
  } catch (error) {
    result.errors.push(`Test execution failed: ${error}`);
    return result;
  }
};

/**
 * Validates backend-frontend format consistency
 */
export const validateFormatConsistency = async (): Promise<{
  consistent: boolean;
  backendFormats: string[];
  frontendFormats: string[];
  missing: string[];
  extra: string[];
}> => {
  try {
    // Fetch supported formats from backend
    const response = await fetch('/api/v1/training/formats/supported');
    const data = await response.json();
    const backendFormats = data.supported_formats || [];
    
    // Compare with frontend formats
    const frontendFormats = SUPPORTED_EXTENSIONS.map(ext => ext.substring(1)); // Remove leading dot
    
    const missing = backendFormats.filter((format: string) => 
      !frontendFormats.includes(format)
    );
    
    const extra = frontendFormats.filter(format => 
      !backendFormats.includes(format)
    );
    
    return {
      consistent: missing.length === 0 && extra.length === 0,
      backendFormats,
      frontendFormats,
      missing,
      extra
    };
  } catch (error) {
    console.error('Failed to validate format consistency:', error);
    return {
      consistent: false,
      backendFormats: [],
      frontendFormats: SUPPORTED_EXTENSIONS.map(ext => ext.substring(1)),
      missing: [],
      extra: []
    };
  }
};

/**
 * Generates a comprehensive test report
 */
export const generateTestReport = (testResult: UploadSystemTestResult): string => {
  const report = [
    '=== StreamWorks-KI Upload System Test Report ===',
    '',
    `📊 Overall Status: ${testResult.success ? '✅ PASSED' : '❌ FAILED'}`,
    `📁 Total Formats: ${testResult.totalFormats}`,
    `🧪 Tested Formats: ${testResult.testedFormats}`,
    `✅ Passed Validation: ${testResult.passedValidation}`,
    `❌ Failed Validation: ${testResult.failedValidation}`,
    '',
    '📋 Format Breakdown by Category:',
  ];

  Object.entries(testResult.formatBreakdown).forEach(([category, stats]) => {
    const successRate = stats.tested > 0 ? ((stats.passed / stats.tested) * 100).toFixed(1) : '0';
    report.push(`  ${category}: ${stats.passed}/${stats.tested} (${successRate}%)`);
  });

  if (testResult.missingCategories.length > 0) {
    report.push('');
    report.push('⚠️  Files without categories:');
    testResult.missingCategories.forEach(file => {
      report.push(`  - ${file}`);
    });
  }

  if (testResult.errors.length > 0) {
    report.push('');
    report.push('❌ Validation Errors:');
    testResult.errors.forEach(error => {
      report.push(`  - ${error}`);
    });
  }

  report.push('');
  report.push('=== End Report ===');

  return report.join('\n');
};

/**
 * Console-friendly test runner
 */
export const runUploadSystemTest = async (): Promise<void> => {
  console.log('🚀 Starting Upload System Test...');
  
  // Test format validation
  const testResult = testUploadSystem();
  console.log(generateTestReport(testResult));
  
  // Test backend consistency
  console.log('🔄 Checking backend-frontend consistency...');
  const consistencyResult = await validateFormatConsistency();
  
  if (consistencyResult.consistent) {
    console.log('✅ Backend and frontend formats are consistent!');
  } else {
    console.log('❌ Backend and frontend formats are inconsistent:');
    if (consistencyResult.missing.length > 0) {
      console.log('  Missing in frontend:', consistencyResult.missing);
    }
    if (consistencyResult.extra.length > 0) {
      console.log('  Extra in frontend:', consistencyResult.extra);
    }
  }
  
  console.log('🏁 Upload System Test Complete');
};

// Export for use in browser console
if (typeof window !== 'undefined') {
  (window as any).uploadSystemTest = {
    run: runUploadSystemTest,
    testFormats: testUploadSystem,
    checkConsistency: validateFormatConsistency,
    createMockFiles,
    generateReport: generateTestReport
  };
}