#!/bin/bash
# StreamWorks-KI Professional Development Workflow
# Docker für Infrastruktur, lokale Entwicklung für Code

set -e

# Colors für bessere UX
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# PID files für process management
BACKEND_PID_FILE="/tmp/streamworks-ki-backend.pid"
FRONTEND_PID_FILE="/tmp/streamworks-ki-frontend.pid"

# Functions
print_header() {
    echo -e "${PURPLE}🚀 $1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_dependencies() {
    print_info "Checking system dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed"
        exit 1
    fi
    
    print_status "All dependencies are available"
}

start_infrastructure() {
    print_info "Starting infrastructure services (PostgreSQL, pgAdmin, Redis)..."
    
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev-db.yml up -d
    
    print_info "Waiting for database to be ready..."
    local timeout=60
    local counter=0
    
    while [ $counter -lt $timeout ]; do
        if docker compose -f docker-compose.dev-db.yml exec -T postgres pg_isready -U streamworks -d streamworks_ki_dev &> /dev/null; then
            print_status "Database is ready"
            break
        fi
        
        if [ $((counter % 10)) -eq 0 ]; then
            echo -n "Waiting for database"
        fi
        echo -n "."
        sleep 2
        counter=$((counter + 2))
    done
    
    if [ $counter -ge $timeout ]; then
        print_error "Database failed to start within $timeout seconds"
        docker compose -f docker-compose.dev-db.yml logs postgres
        exit 1
    fi
    echo ""
    
    print_status "Infrastructure services started successfully"
}

setup_backend() {
    print_info "Setting up backend development environment..."
    
    cd "$BACKEND_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_info "Installing Python dependencies..."
    pip install -e .
    
    # Install development dependencies if available
    if [ -f "requirements-dev-simple.txt" ]; then
        pip install -r requirements-dev-simple.txt
    elif [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    fi
    
    print_status "Backend environment setup completed"
}

setup_frontend() {
    print_info "Setting up frontend development environment..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    print_info "Installing Node.js dependencies..."
    npm install
    
    print_status "Frontend environment setup completed"
}

start_backend() {
    print_info "Starting backend development server..."
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Set environment variables
    export DATABASE_URL="postgresql://streamworks:streamworks_dev_2025@localhost:5432/streamworks_ki_dev"
    export PYTHONPATH="$BACKEND_DIR"
    export ENVIRONMENT="development"
    export LOG_LEVEL="DEBUG"
    export ENABLE_CORS="true"
    
    # Start backend server in background
    print_info "Backend starting on http://localhost:8000"
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/streamworks-backend.log 2>&1 &
    echo $! > "$BACKEND_PID_FILE"
    
    print_status "Backend server started (PID: $(cat $BACKEND_PID_FILE))"
}

start_frontend() {
    print_info "Starting frontend development server..."
    
    cd "$FRONTEND_DIR"
    
    # Set environment variables
    export VITE_API_URL="http://localhost:8000"
    export NODE_ENV="development"
    
    # Start frontend server in background
    print_info "Frontend starting on http://localhost:3000"
    nohup npm run dev > /tmp/streamworks-frontend.log 2>&1 &
    echo $! > "$FRONTEND_PID_FILE"
    
    print_status "Frontend server started (PID: $(cat $FRONTEND_PID_FILE))"
}

wait_for_services() {
    print_info "Waiting for services to be ready..."
    
    # Wait for backend
    local timeout=30
    local counter=0
    while [ $counter -lt $timeout ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            print_status "Backend is ready"
            break
        fi
        sleep 2
        counter=$((counter + 2))
    done
    
    # Wait for frontend
    counter=0
    while [ $counter -lt $timeout ]; do
        if curl -f http://localhost:3000 &> /dev/null; then
            print_status "Frontend is ready"
            break
        fi
        sleep 2
        counter=$((counter + 2))
    done
}

open_development_tools() {
    print_info "Opening development tools..."
    
    sleep 3  # Give services time to fully start
    
    if command -v open &> /dev/null; then
        print_info "Opening browser windows..."
        open "http://localhost:3000"      # Frontend
        open "http://localhost:8000/docs" # Backend API docs
        open "http://localhost:8080"      # pgAdmin
    else
        print_warning "Browser auto-open not available. Please manually open:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend:  http://localhost:8000/docs"
        echo "  pgAdmin:  http://localhost:8080"
    fi
}

show_development_info() {
    echo ""
    print_header "StreamWorks-KI Development Environment Ready!"
    echo ""
    echo -e "${CYAN}🌐 Service URLs:${NC}"
    echo "  Frontend Application:  http://localhost:3000"
    echo "  Backend API:           http://localhost:8000"
    echo "  API Documentation:     http://localhost:8000/docs"
    echo "  Database Admin:        http://localhost:8080"
    echo "  Redis (if needed):     localhost:6379"
    echo ""
    echo -e "${CYAN}🔐 Database Connection:${NC}"
    echo "  Host:       localhost"
    echo "  Port:       5432"
    echo "  Database:   streamworks_ki_dev"
    echo "  Username:   streamworks"
    echo "  Password:   streamworks_dev_2025"
    echo ""
    echo -e "${CYAN}🔧 pgAdmin Credentials:${NC}"
    echo "  Email:      dev@streamworks-ki.local"
    echo "  Password:   dev_admin_2025"
    echo ""
    echo -e "${CYAN}📁 Development Commands:${NC}"
    echo "  Stop all:        $0 stop"
    echo "  Restart all:     $0 restart"
    echo "  Show logs:       $0 logs"
    echo "  Show status:     $0 status"
    echo "  Clean & reset:   $0 clean"
    echo ""
    echo -e "${CYAN}📝 Log Files:${NC}"
    echo "  Backend:  /tmp/streamworks-backend.log"
    echo "  Frontend: /tmp/streamworks-frontend.log"
    echo ""
    echo -e "${CYAN}🔄 Hot Reload Status:${NC}"
    echo "  Backend:  ✅ Enabled (file changes auto-reload)"
    echo "  Frontend: ✅ Enabled (Vite HMR active)"
    echo ""
}

stop_services() {
    print_info "Stopping development services..."
    
    # Stop backend
    if [ -f "$BACKEND_PID_FILE" ]; then
        local backend_pid=$(cat "$BACKEND_PID_FILE")
        if kill "$backend_pid" 2>/dev/null; then
            print_status "Backend server stopped"
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    # Stop frontend
    if [ -f "$FRONTEND_PID_FILE" ]; then
        local frontend_pid=$(cat "$FRONTEND_PID_FILE")
        if kill "$frontend_pid" 2>/dev/null; then
            print_status "Frontend server stopped"
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    # Stop infrastructure
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev-db.yml down
    
    print_status "All services stopped"
}

show_logs() {
    echo -e "${BLUE}=== Backend Logs ===${NC}"
    tail -f /tmp/streamworks-backend.log &
    
    echo -e "${BLUE}=== Frontend Logs ===${NC}"
    tail -f /tmp/streamworks-frontend.log &
    
    echo "Press Ctrl+C to stop log viewing"
    wait
}

show_status() {
    echo -e "${BLUE}📊 Service Status${NC}"
    echo "=================="
    
    # Check infrastructure
    docker compose -f docker-compose.dev-db.yml ps
    
    echo ""
    echo -e "${BLUE}🖥️  Development Servers${NC}"
    echo "======================"
    
    # Check backend
    if [ -f "$BACKEND_PID_FILE" ] && kill -0 $(cat "$BACKEND_PID_FILE") 2>/dev/null; then
        echo "Backend:  ✅ Running (PID: $(cat $BACKEND_PID_FILE))"
    else
        echo "Backend:  ❌ Not running"
    fi
    
    # Check frontend
    if [ -f "$FRONTEND_PID_FILE" ] && kill -0 $(cat "$FRONTEND_PID_FILE") 2>/dev/null; then
        echo "Frontend: ✅ Running (PID: $(cat $FRONTEND_PID_FILE))"
    else
        echo "Frontend: ❌ Not running"
    fi
    
    echo ""
    echo -e "${BLUE}🌐 Health Checks${NC}"
    echo "================"
    
    # Test URLs
    if curl -f -s http://localhost:8000/health > /dev/null; then
        echo "Backend API:  ✅ Healthy"
    else
        echo "Backend API:  ❌ Unreachable"
    fi
    
    if curl -f -s http://localhost:3000 > /dev/null; then
        echo "Frontend:     ✅ Healthy"
    else
        echo "Frontend:     ❌ Unreachable"
    fi
    
    if curl -f -s http://localhost:8080/misc/ping > /dev/null; then
        echo "pgAdmin:      ✅ Healthy"
    else
        echo "pgAdmin:      ❌ Unreachable"
    fi
}

clean_environment() {
    print_warning "Cleaning development environment..."
    
    stop_services
    
    # Clean Docker
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev-db.yml down -v --remove-orphans
    
    # Clean Python cache
    cd "$BACKEND_DIR"
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Clean Node modules cache
    cd "$FRONTEND_DIR"
    rm -rf .vite 2>/dev/null || true
    rm -rf dist 2>/dev/null || true
    
    # Clean log files
    rm -f /tmp/streamworks-*.log
    
    print_status "Environment cleaned"
}

# Main command handling
main() {
    case "${1:-start}" in
        "start")
            print_header "Starting StreamWorks-KI Development Environment"
            check_dependencies
            start_infrastructure
            setup_backend
            setup_frontend
            start_backend
            start_frontend
            wait_for_services
            open_development_tools
            show_development_info
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            main start
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "clean")
            clean_environment
            ;;
        "help"|"-h"|"--help")
            echo "StreamWorks-KI Development Script"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start    Start complete development environment (default)"
            echo "  stop     Stop all services"
            echo "  restart  Restart all services"
            echo "  logs     Show live logs from all services"
            echo "  status   Show status of all services"
            echo "  clean    Clean environment and remove data"
            echo "  help     Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for available commands"
            exit 1
            ;;
    esac
}

# Cleanup on script exit
trap "stop_services 2>/dev/null" EXIT

# Run main function
main "$@"