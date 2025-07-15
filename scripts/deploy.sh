#!/bin/bash

# StreamWorks-KI Production Deployment Script
# This script handles the complete deployment process

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_ROOT}/.env.production"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.production.yml"
BACKUP_DIR="${PROJECT_ROOT}/backups"
LOG_FILE="${PROJECT_ROOT}/logs/deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
    
    case $level in
        "ERROR")
            echo -e "${RED}[ERROR]${NC} ${message}" >&2
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} ${message}"
            ;;
        "INFO")
            echo -e "${GREEN}[INFO]${NC} ${message}"
            ;;
        "DEBUG")
            echo -e "${BLUE}[DEBUG]${NC} ${message}"
            ;;
    esac
}

# Error handler
error_exit() {
    log "ERROR" "$1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error_exit "Docker is not installed"
    fi
    
    if ! docker info &> /dev/null; then
        error_exit "Docker is not running"
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error_exit "Docker Compose is not installed"
    fi
    
    # Check if environment file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        error_exit "Environment file not found: $ENV_FILE"
    fi
    
    # Check if compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error_exit "Docker Compose file not found: $COMPOSE_FILE"
    fi
    
    log "INFO" "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log "INFO" "Creating necessary directories..."
    
    local dirs=(
        "${PROJECT_ROOT}/logs"
        "${PROJECT_ROOT}/logs/nginx"
        "${PROJECT_ROOT}/logs/backend"
        "${PROJECT_ROOT}/logs/postgres"
        "${PROJECT_ROOT}/data"
        "${PROJECT_ROOT}/data/chromadb"
        "${PROJECT_ROOT}/data/uploads"
        "${PROJECT_ROOT}/data/models"
        "${BACKUP_DIR}"
        "${PROJECT_ROOT}/ssl"
        "${PROJECT_ROOT}/config/prometheus"
        "${PROJECT_ROOT}/config/grafana"
        "${PROJECT_ROOT}/config/postgres"
        "${PROJECT_ROOT}/config/redis"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        log "DEBUG" "Created directory: $dir"
    done
    
    # Set proper permissions
    chmod 755 "${PROJECT_ROOT}/logs"
    chmod 755 "${PROJECT_ROOT}/data"
    chmod 700 "${PROJECT_ROOT}/ssl"
    
    log "INFO" "Directories created successfully"
}

# Load environment variables
load_environment() {
    log "INFO" "Loading environment variables..."
    
    if [[ -f "$ENV_FILE" ]]; then
        set -a  # automatically export all variables
        source "$ENV_FILE"
        set +a
        log "INFO" "Environment variables loaded from $ENV_FILE"
    else
        error_exit "Environment file not found: $ENV_FILE"
    fi
    
    # Set build-time variables
    export BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    export VERSION=${VERSION:-"latest"}
    export VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    
    log "INFO" "Build variables set: VERSION=$VERSION, VCS_REF=$VCS_REF"
}

# Backup current deployment
backup_deployment() {
    log "INFO" "Creating deployment backup..."
    
    local backup_timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_path="${BACKUP_DIR}/backup_${backup_timestamp}"
    
    mkdir -p "$backup_path"
    
    # Backup environment file
    if [[ -f "$ENV_FILE" ]]; then
        cp "$ENV_FILE" "${backup_path}/"
    fi
    
    # Backup database if running
    if docker-compose -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        log "INFO" "Backing up database..."
        docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
            -U "$POSTGRES_USER" \
            -d "$POSTGRES_DB" \
            --clean --if-exists --create \
            > "${backup_path}/database.sql" 2>/dev/null || {
            log "WARN" "Database backup failed, continuing..."
        }
    fi
    
    # Backup ChromaDB data
    if [[ -d "${PROJECT_ROOT}/data/chromadb" ]]; then
        cp -r "${PROJECT_ROOT}/data/chromadb" "${backup_path}/" 2>/dev/null || {
            log "WARN" "ChromaDB backup failed, continuing..."
        }
    fi
    
    # Keep only last 10 backups
    find "$BACKUP_DIR" -name "backup_*" -type d | sort -r | tail -n +11 | xargs rm -rf 2>/dev/null || true
    
    log "INFO" "Backup created: $backup_path"
}

# Build Docker images
build_images() {
    log "INFO" "Building Docker images..."
    
    # Build backend image
    log "INFO" "Building backend image..."
    docker build \
        -f "${PROJECT_ROOT}/backend/Dockerfile.production" \
        -t "streamworks-ki/backend:${VERSION}" \
        --build-arg BUILD_DATE="$BUILD_DATE" \
        --build-arg VERSION="$VERSION" \
        --build-arg VCS_REF="$VCS_REF" \
        "${PROJECT_ROOT}/backend" || error_exit "Backend build failed"
    
    # Build frontend image
    log "INFO" "Building frontend image..."
    docker build \
        -f "${PROJECT_ROOT}/frontend/Dockerfile.production" \
        -t "streamworks-ki/frontend:${VERSION}" \
        --build-arg BUILD_DATE="$BUILD_DATE" \
        --build-arg VERSION="$VERSION" \
        --build-arg VCS_REF="$VCS_REF" \
        --build-arg VITE_API_URL="/api/v1" \
        "${PROJECT_ROOT}/frontend" || error_exit "Frontend build failed"
    
    log "INFO" "Docker images built successfully"
}

# Deploy services
deploy_services() {
    log "INFO" "Deploying services..."
    
    # Pull external images
    log "INFO" "Pulling external images..."
    docker-compose -f "$COMPOSE_FILE" pull postgres redis ollama prometheus grafana elasticsearch kibana
    
    # Stop existing services gracefully
    log "INFO" "Stopping existing services..."
    docker-compose -f "$COMPOSE_FILE" down --timeout 30
    
    # Start infrastructure services first
    log "INFO" "Starting infrastructure services..."
    docker-compose -f "$COMPOSE_FILE" up -d postgres redis
    
    # Wait for infrastructure to be ready
    log "INFO" "Waiting for infrastructure services..."
    sleep 30
    
    # Check database connectivity
    local retries=0
    while ! docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" &>/dev/null; do
        retries=$((retries + 1))
        if [[ $retries -gt 30 ]]; then
            error_exit "Database failed to start after 30 attempts"
        fi
        log "DEBUG" "Waiting for database... (attempt $retries/30)"
        sleep 2
    done
    
    # Start Ollama
    log "INFO" "Starting Ollama service..."
    docker-compose -f "$COMPOSE_FILE" up -d ollama
    sleep 20
    
    # Start application services
    log "INFO" "Starting application services..."
    docker-compose -f "$COMPOSE_FILE" up -d backend
    
    # Wait for backend to be ready
    log "INFO" "Waiting for backend service..."
    sleep 30
    
    local backend_retries=0
    while ! curl -f http://localhost:8000/health &>/dev/null; do
        backend_retries=$((backend_retries + 1))
        if [[ $backend_retries -gt 60 ]]; then
            error_exit "Backend failed to start after 60 attempts"
        fi
        log "DEBUG" "Waiting for backend... (attempt $backend_retries/60)"
        sleep 2
    done
    
    # Start frontend
    log "INFO" "Starting frontend service..."
    docker-compose -f "$COMPOSE_FILE" up -d frontend
    
    # Start monitoring services
    log "INFO" "Starting monitoring services..."
    docker-compose -f "$COMPOSE_FILE" up -d prometheus grafana elasticsearch kibana
    
    log "INFO" "All services deployed successfully"
}

# Verify deployment
verify_deployment() {
    log "INFO" "Verifying deployment..."
    
    # Check service health
    local services=("frontend" "backend" "postgres" "redis" "ollama")
    
    for service in "${services[@]}"; do
        if docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "Up"; then
            log "INFO" "✓ $service is running"
        else
            log "ERROR" "✗ $service is not running"
            return 1
        fi
    done
    
    # Check HTTP endpoints
    local endpoints=(
        "http://localhost:80/health|Frontend health check"
        "http://localhost:8000/health|Backend health check"
        "http://localhost:8000/metrics|Metrics endpoint"
        "http://localhost:9090/-/healthy|Prometheus health"
        "http://localhost:3000/api/health|Grafana health"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS='|' read -r endpoint description <<< "$endpoint_info"
        
        if curl -f -s "$endpoint" &>/dev/null; then
            log "INFO" "✓ $description"
        else
            log "WARN" "✗ $description failed"
        fi
    done
    
    # Check database connectivity
    if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" &>/dev/null; then
        log "INFO" "✓ Database connectivity"
    else
        log "ERROR" "✗ Database connectivity failed"
        return 1
    fi
    
    log "INFO" "Deployment verification completed"
}

# Setup monitoring alerts
setup_monitoring() {
    log "INFO" "Setting up monitoring and alerts..."
    
    # Create Prometheus configuration
    cat > "${PROJECT_ROOT}/config/prometheus/prometheus.yml" << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'streamworks-ki-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
EOF
    
    # Create alert rules
    mkdir -p "${PROJECT_ROOT}/config/prometheus/rules"
    cat > "${PROJECT_ROOT}/config/prometheus/rules/alerts.yml" << EOF
groups:
  - name: streamworks-ki-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          
      - alert: HighMemoryUsage
        expr: system_memory_usage_percent > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
EOF
    
    log "INFO" "Monitoring setup completed"
}

# Post-deployment tasks
post_deployment() {
    log "INFO" "Running post-deployment tasks..."
    
    # Initialize Ollama models if needed
    log "INFO" "Checking Ollama models..."
    if docker-compose -f "$COMPOSE_FILE" exec -T ollama ollama list | grep -q "mistral:7b-instruct"; then
        log "INFO" "✓ Mistral model is available"
    else
        log "INFO" "Pulling Mistral model..."
        docker-compose -f "$COMPOSE_FILE" exec -T ollama ollama pull mistral:7b-instruct || {
            log "WARN" "Failed to pull Mistral model, will retry in background"
        }
    fi
    
    # Run database migrations if needed
    log "INFO" "Running database migrations..."
    docker-compose -f "$COMPOSE_FILE" exec -T backend python -m alembic upgrade head || {
        log "WARN" "Database migrations failed, continuing..."
    }
    
    # Set up log rotation
    log "INFO" "Setting up log rotation..."
    cat > "/tmp/streamworks-ki-logrotate" << EOF
${PROJECT_ROOT}/logs/*/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f ${COMPOSE_FILE} restart frontend backend
    endscript
}
EOF
    
    sudo mv "/tmp/streamworks-ki-logrotate" "/etc/logrotate.d/streamworks-ki" 2>/dev/null || {
        log "WARN" "Could not set up log rotation (requires sudo)"
    }
    
    log "INFO" "Post-deployment tasks completed"
}

# Print deployment summary
print_summary() {
    log "INFO" "Deployment Summary"
    echo "===========================================" | tee -a "$LOG_FILE"
    echo "Deployment completed successfully!" | tee -a "$LOG_FILE"
    echo "Services:" | tee -a "$LOG_FILE"
    echo "  - Frontend: http://localhost:80" | tee -a "$LOG_FILE"
    echo "  - Backend API: http://localhost:8000" | tee -a "$LOG_FILE"
    echo "  - Metrics: http://localhost:8000/metrics" | tee -a "$LOG_FILE"
    echo "  - Prometheus: http://localhost:9090" | tee -a "$LOG_FILE"
    echo "  - Grafana: http://localhost:3000" | tee -a "$LOG_FILE"
    echo "  - Kibana: http://localhost:5601" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "Logs location: ${PROJECT_ROOT}/logs" | tee -a "$LOG_FILE"
    echo "Backup location: ${BACKUP_DIR}" | tee -a "$LOG_FILE"
    echo "===========================================" | tee -a "$LOG_FILE"
}

# Main deployment function
main() {
    local start_time=$(date '+%Y-%m-%d %H:%M:%S')
    
    log "INFO" "Starting StreamWorks-KI deployment at $start_time"
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Run deployment steps
    check_prerequisites
    create_directories
    load_environment
    backup_deployment
    build_images
    setup_monitoring
    deploy_services
    verify_deployment
    post_deployment
    print_summary
    
    local end_time=$(date '+%Y-%m-%d %H:%M:%S')
    log "INFO" "Deployment completed successfully at $end_time"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "verify")
        load_environment
        verify_deployment
        ;;
    "backup")
        load_environment
        backup_deployment
        ;;
    "logs")
        docker-compose -f "$COMPOSE_FILE" logs -f "${2:-}"
        ;;
    "status")
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    "stop")
        docker-compose -f "$COMPOSE_FILE" down
        ;;
    "restart")
        docker-compose -f "$COMPOSE_FILE" restart "${2:-}"
        ;;
    *)
        echo "Usage: $0 {deploy|verify|backup|logs|status|stop|restart}"
        echo "  deploy  - Full deployment (default)"
        echo "  verify  - Verify current deployment"
        echo "  backup  - Create backup"
        echo "  logs    - Show logs (optionally specify service)"
        echo "  status  - Show service status"
        echo "  stop    - Stop all services"
        echo "  restart - Restart services (optionally specify service)"
        exit 1
        ;;
esac