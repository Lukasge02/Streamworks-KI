#!/bin/bash
# 🏆 ENTERPRISE BACKEND STARTUP SCRIPT
# Updated for Enterprise RAG System with Intelligent Chunking

echo "🏆 Starting StreamWorks-KI Backend (Enterprise RAG System)..."

# Set working directory
cd /Applications/Programmieren/Visual\ Studio/Bachelorarbeit/Streamworks-KI/backend

# Activate virtual environment
source venv/bin/activate

# Create Enterprise directory structure
echo "📁 Creating Enterprise directory structure..."
mkdir -p data/uploads
mkdir -p data/documents/qa_docs
mkdir -p data/documents/stream-xml
mkdir -p data/documents/streamworks-api
mkdir -p data/vector_db_production
mkdir -p data/conversations

# Legacy directories for backward compatibility
mkdir -p data/documents/qa/streamworks-f1
mkdir -p data/documents/qa/sharepoint
mkdir -p data/documents/qa/confluence
mkdir -p data/vector_db

# Set environment variables
export PYTHONPATH=/Applications/Programmieren/Visual\ Studio/Bachelorarbeit/Streamworks-KI/backend

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Wait a moment
sleep 2

# Start the Enterprise backend
echo "✅ Starting Enterprise uvicorn server with intelligent chunking..."
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000