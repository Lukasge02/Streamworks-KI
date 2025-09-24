#!/bin/bash

# Streamworks Backend Startup Script
# Ensures reliable startup with Python 3.10 and proper dependency checks

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Streamworks Backend...${NC}"

# Check Python 3.10
if ! command -v /opt/homebrew/bin/python3.10 &> /dev/null; then
    echo -e "${RED}❌ Python 3.10 not found at /opt/homebrew/bin/python3.10${NC}"
    echo "Please install Python 3.10 via Homebrew: brew install python@3.10"
    exit 1
fi

echo -e "${GREEN}✅ Python 3.10 found${NC}"

# Check if Qdrant is running
if ! curl -s http://localhost:6333 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Qdrant not running. Starting Qdrant...${NC}"
    docker run -d -p 6333:6333 --name qdrant_streamworks qdrant/qdrant 2>/dev/null || {
        echo -e "${YELLOW}Qdrant container might already exist. Trying to start it...${NC}"
        docker start qdrant_streamworks 2>/dev/null || echo -e "${YELLOW}Could not start Qdrant. Please start manually.${NC}"
    }
    sleep 3
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Ollama not running. Please start Ollama manually if needed.${NC}"
fi

# Kill any process on port 8000
echo -e "${YELLOW}Checking port 8000...${NC}"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Port 8000 is in use. Killing existing process...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  No virtual environment found. Installing dependencies globally...${NC}"
fi

# Install/update dependencies
echo -e "${YELLOW}Installing/updating dependencies...${NC}"
/opt/homebrew/bin/python3.10 -m pip install -q --upgrade pip
/opt/homebrew/bin/python3.10 -m pip install -q -r requirements.txt

# Set environment variables
export PYTHONPATH="${PWD}:${PYTHONPATH}"
export PYTHONUNBUFFERED=1

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the backend
echo -e "${GREEN}🚀 Starting FastAPI backend on port 8000...${NC}"
echo -e "${YELLOW}Logs will be saved to logs/backend_$(date +%Y%m%d_%H%M%S).log${NC}"

# Run with explicit Python 3.10
/opt/homebrew/bin/python3.10 -u main.py 2>&1 | tee logs/backend_$(date +%Y%m%d_%H%M%S).log &

# Store the PID
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        echo -e "${GREEN}🎉 Streamworks Backend running at http://localhost:8000${NC}"
        echo -e "${GREEN}📚 API Docs: http://localhost:8000/docs${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"

        # Keep script running and handle shutdown
        trap "echo -e '\n${YELLOW}Shutting down backend...${NC}'; kill $BACKEND_PID 2>/dev/null; rm -f .backend.pid; exit" INT TERM
        wait $BACKEND_PID
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo -e "\n${RED}❌ Backend failed to start within 30 seconds${NC}"
echo -e "${YELLOW}Check logs/backend_*.log for details${NC}"
kill $BACKEND_PID 2>/dev/null
rm -f .backend.pid
exit 1