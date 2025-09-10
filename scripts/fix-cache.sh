#!/bin/bash

# Streamworks-KI Cache Fix Script
# Fixes common Next.js cache issues during development

echo "🧹 Streamworks-KI Cache Cleanup"
echo "================================"

# Change to project root
cd "$(dirname "$0")/.."

# Stop any running dev servers
echo "⏹️  Stopping development servers..."
pkill -f "next dev" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
sleep 2

# Clean frontend caches
echo "🗑️  Cleaning frontend caches..."
cd frontend
rm -rf .next .turbo node_modules/.cache 2>/dev/null || true
echo "   ✅ Removed .next, .turbo, node_modules/.cache"

# Clean backend cache if exists
cd ../backend
if [ -d "__pycache__" ]; then
    rm -rf __pycache__
    echo "   ✅ Removed Python cache"
fi

# Return to root
cd ..

echo "🎯 Cache cleanup complete!"
echo ""
echo "💡 Quick commands:"
echo "   cd frontend && npm run dev:clean  # Start with clean cache"
echo "   cd frontend && npm run fresh      # Full refresh + install"
echo ""
echo "🚀 Ready to restart development servers!"