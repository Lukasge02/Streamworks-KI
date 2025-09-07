/** @type {import('next').NextConfig} */
const nextConfig = {
  // App Router is enabled by default in Next.js 14
  
  // Performance optimizations
  swcMinify: true,
  compress: true,
  
  // Bundle analyzer configuration
  experimental: {
    optimizePackageImports: ['lucide-react', '@heroicons/react'],
    bundlePagesExternals: false,
    esmExternals: true,
  },
  
  // API Proxy for Development
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/graph/:path*',
        destination: 'http://localhost:8000/graph/:path*',
      },
    ];
  },
  
  // Environment Variables
  env: {
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'Streamworks RAG MVP',
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
  },
  
  // Build Output
  output: 'standalone',
  
  // Image Configuration
  images: {
    domains: ['localhost'],
  },
  
  // Webpack Configuration for optimization
  webpack: (config, { isServer, webpack }) => {
    // Ignore node modules warnings
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };
    
    // Tree shaking and optimization
    config.optimization = {
      ...config.optimization,
      usedExports: true,
      sideEffects: false,
    };
    
    // Monaco Editor optimization - lazy load
    if (!isServer) {
      config.resolve.alias = {
        ...config.resolve.alias,
        'monaco-editor': 'monaco-editor/esm/vs/editor/editor.api.js',
      };
    }
    
    return config;
  },
};

module.exports = nextConfig;