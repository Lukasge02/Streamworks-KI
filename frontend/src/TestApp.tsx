/**
 * Simple Test App to debug white screen issue
 */

import React from 'react';

function TestApp() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          StreamWorks-KI Test
        </h1>
        <p className="text-gray-600">
          If you can see this, the basic React app is working.
        </p>
        <div className="mt-4 p-4 bg-blue-50 rounded">
          <p className="text-blue-800 text-sm">
            ✅ React is working<br/>
            ✅ Tailwind CSS is working<br/>
            ✅ TypeScript is working
          </p>
        </div>
      </div>
    </div>
  );
}

export default TestApp;