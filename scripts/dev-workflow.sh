#!/bin/bash
# StreamWorks-KI Development Workflow Script
# Automatisierter Development-Workflow mit Docker

set -e

echo "🚀 StreamWorks-KI Development Workflow"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.dev.yml"

# Function to print status
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

print_section() {
    echo -e "${PURPLE}🔸 $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_section "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is required but not installed"
        exit 1
    fi
    
    print_status "Prerequisites check completed"
}

# Start development environment
start_dev_environment() {
    print_section "Starting development environment..."
    
    cd "$PROJECT_ROOT"
    
    # Pull latest images
    print_info "Pulling latest Docker images..."
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Start services
    print_info "Starting all services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    print_status "Development environment started"
}

# Wait for services to be ready
wait_for_services() {
    print_section "Waiting for services to be ready..."
    
    services=("postgres" "postgres-admin" "backend" "frontend")
    
    for service in "${services[@]}"; do
        print_info "Waiting for $service to be healthy..."
        
        timeout=120
        counter=0
        
        while [ $counter -lt $timeout ]; do
            if docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "healthy\|Up"; then
                print_status "$service is ready"
                break
            fi
            
            if [ $((counter % 10)) -eq 0 ]; then
                echo -n "Waiting for $service"
            fi
            echo -n "."
            sleep 2
            counter=$((counter + 2))
        done
        
        if [ $counter -ge $timeout ]; then
            print_error "$service failed to start within $timeout seconds"
            show_service_logs "$service"
            exit 1
        fi
        echo ""
    done
    
    print_status "All services are ready"
}

# Show service logs
show_service_logs() {
    local service=$1
    print_warning "Last 20 lines of $service logs:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20 "$service"
}

# Install dependencies
install_dependencies() {
    print_section "Installing/updating dependencies..."
    
    # Backend dependencies
    print_info "Installing backend dependencies..."
    docker-compose -f "$COMPOSE_FILE" exec backend pip install -r requirements-dev.txt
    
    # Frontend dependencies
    print_info "Installing frontend dependencies..."
    docker-compose -f "$COMPOSE_FILE" exec frontend npm ci
    
    print_status "Dependencies installed"
}

# Setup development database
setup_dev_database() {
    print_section "Setting up development database..."
    
    # Wait for PostgreSQL specifically
    print_info "Waiting for PostgreSQL to be ready..."
    docker-compose -f "$COMPOSE_FILE" exec postgres pg_isready -U streamworks -d streamworks_ki_dev
    
    # Run database migrations
    print_info "Running database migrations..."
    docker-compose -f "$COMPOSE_FILE" exec backend alembic upgrade head
    
    # Load test data
    print_info "Loading test data..."
    docker-compose -f "$COMPOSE_FILE" exec backend python -c "
from app.scripts.load_test_data import load_development_data
import asyncio
asyncio.run(load_development_data())
print('✅ Test data loaded successfully')
"
    
    print_status "Development database setup completed"
}

# Open development tools
open_dev_tools() {
    print_section "Opening development tools..."
    
    # Wait a moment for services to fully start
    sleep 3
    
    # Open browser windows (macOS)
    if command -v open &> /dev/null; then
        print_info "Opening pgAdmin..."
        open "http://localhost:8080"
        
        print_info "Opening frontend application..."
        open "http://localhost:3000"
        
        print_info "Opening backend API docs..."
        open "http://localhost:8000/docs"
    else
        print_info "Please manually open these URLs:"
        echo "  - Frontend: http://localhost:3000"
        echo "  - Backend API: http://localhost:8000/docs"
        echo "  - pgAdmin: http://localhost:8080"
    fi
    
    print_status "Development tools opened"
}

# Show development information
show_dev_info() {
    print_section "Development Environment Information"
    echo ""
    echo -e "${CYAN}🌐 Service URLs:${NC}"
    echo "  Frontend:     http://localhost:3000"
    echo "  Backend API:  http://localhost:8000"
    echo "  API Docs:     http://localhost:8000/docs"
    echo "  pgAdmin:      http://localhost:8080"
    echo "  ChromaDB:     http://localhost:8001"
    echo "  Redis:        localhost:6379"
    echo ""
    echo -e "${CYAN}🔐 Database Credentials:${NC}"
    echo "  Host:         localhost"
    echo "  Port:         5432"
    echo "  Database:     streamworks_ki_dev"
    echo "  Username:     streamworks"
    echo "  Password:     streamworks_dev_2025"
    echo ""
    echo -e "${CYAN}🔧 pgAdmin Credentials:${NC}"
    echo "  Email:        dev@streamworks-ki.local"
    echo "  Password:     dev_admin_2025"
    echo ""
    echo -e "${CYAN}📁 Development Commands:${NC}"
    echo "  View logs:    docker-compose -f docker-compose.dev.yml logs -f [service]"
    echo "  Stop all:     docker-compose -f docker-compose.dev.yml down"
    echo "  Restart:      docker-compose -f docker-compose.dev.yml restart [service]"
    echo "  Shell access: docker-compose -f docker-compose.dev.yml exec [service] bash"
    echo ""
    echo -e "${CYAN}🧪 Testing Commands:${NC}"
    echo "  Backend tests: docker-compose -f docker-compose.dev.yml exec backend pytest"
    echo "  Frontend tests: docker-compose -f docker-compose.dev.yml exec frontend npm test"
    echo ""
    echo -e "${CYAN}🔄 Hot Reload Status:${NC}"
    echo "  Backend:      ✅ Enabled (uvicorn --reload)"
    echo "  Frontend:     ✅ Enabled (Vite HMR)"
    echo ""
}

# Show help
show_help() {
    echo "StreamWorks-KI Development Workflow Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     Start complete development environment"
    echo "  stop      Stop development environment"
    echo "  restart   Restart development environment"
    echo "  logs      Show logs for all services"
    echo "  status    Show status of all services"
    echo "  clean     Clean up containers and volumes"
    echo "  help      Show this help message"
    echo ""
}

# Main workflow
main() {
    case "${1:-start}" in
        "start")
            check_prerequisites
            start_dev_environment
            wait_for_services
            setup_dev_database
            open_dev_tools
            show_dev_info
            print_status "Development environment is ready! 🎉"
            ;;
        "stop")
            print_section "Stopping development environment..."
            docker-compose -f "$COMPOSE_FILE" down
            print_status "Development environment stopped"
            ;;
        "restart")
            print_section "Restarting development environment..."
            docker-compose -f "$COMPOSE_FILE" restart
            print_status "Development environment restarted"
            ;;
        "logs")
            docker-compose -f "$COMPOSE_FILE" logs -f
            ;;
        "status")
            docker-compose -f "$COMPOSE_FILE" ps
            ;;
        "clean")
            print_section "Cleaning up development environment..."
            docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
            docker system prune -f
            print_status "Development environment cleaned"
            ;;
        "help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"