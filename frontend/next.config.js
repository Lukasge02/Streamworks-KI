/** @type {import('next').NextConfig} */
const nextConfig = {
  // Performance optimizations (swcMinify is now default in Next.js 15)
  compress: true,
  
  // Cache optimization for development stability
  onDemandEntries: {
    maxInactiveAge: 25 * 1000,
    pagesBufferLength: 2,
  },
  
  // Experimental features (simplified)
  experimental: {
    optimizePackageImports: ['lucide-react', '@heroicons/react'],
    // Stable incremental cache for development
    incrementalCacheHandlerPath: require.resolve('./cache-handler.js'),
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
  
  // Optimized Webpack Configuration for Next.js 15
  webpack: (config, { isServer }) => {
    // Basic fallbacks for client-side
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    
    return config;
  },
};

module.exports = nextConfig;