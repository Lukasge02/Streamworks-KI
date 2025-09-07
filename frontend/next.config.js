/** @type {import('next').NextConfig} */
const nextConfig = {
  // Performance optimizations
  swcMinify: true,
  compress: true,
  
  // Experimental features (simplified)
  experimental: {
    optimizePackageImports: ['lucide-react', '@heroicons/react'],
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
  
  // Simplified Webpack Configuration
  webpack: (config, { isServer }) => {
    // Resolve fallbacks for client-side
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