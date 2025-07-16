#!/bin/bash
# Hybrid Development Setup
# Docker nur für Datenbank, Rest lokal

set -e

echo "🚀 StreamWorks-KI Hybrid Development Setup"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 1. Starte nur Datenbank-Services mit Docker
print_info "Starting database services with Docker..."
docker compose up -d postgres postgres-admin

# 2. Warte auf PostgreSQL
print_info "Waiting for PostgreSQL to be ready..."
sleep 10

# 3. Backend lokal starten
print_info "Setting up backend locally..."
cd backend

# Virtual Environment erstellen falls nicht vorhanden
if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Virtual Environment aktivieren
source venv/bin/activate

# Dependencies installieren
print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -e .
pip install -r requirements-dev-simple.txt

# Environment Variables setzen
export DATABASE_URL="postgresql://streamworks:streamworks_dev_2025@localhost:5432/streamworks_ki_dev"
export PYTHONPATH="$PROJECT_ROOT/backend"

# Backend starten
print_info "Starting backend server..."
print_warning "Backend will start on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 4. Frontend lokal starten
print_info "Setting up frontend locally..."
cd "$PROJECT_ROOT/frontend"

# Dependencies installieren
print_info "Installing Node.js dependencies..."
npm install

# Frontend starten
print_info "Starting frontend server..."
print_warning "Frontend will start on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

# 5. URLs öffnen
sleep 5
print_status "Development environment ready!"
echo ""
echo "🌐 Services running:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  pgAdmin:   http://localhost:8080"
echo ""
echo "🔐 Database credentials:"
echo "  Host:      localhost:5432"
echo "  Database:  streamworks_ki_dev"
echo "  Username:  streamworks"
echo "  Password:  streamworks_dev_2025"
echo ""
echo "🔧 pgAdmin credentials:"
echo "  Email:     dev@streamworks-ki.local"
echo "  Password:  dev_admin_2025"
echo ""

# URLs öffnen
if command -v open >/dev/null 2>&1; then
    open "http://localhost:3000"
    open "http://localhost:8000/docs"
    open "http://localhost:8080"
fi

# Warte auf Strg+C
print_info "Press Ctrl+C to stop all services..."
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker compose down; exit" INT
wait