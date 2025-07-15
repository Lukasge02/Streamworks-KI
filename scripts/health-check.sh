#!/bin/bash

# Health Check Script for StreamWorks-KI Production
# Comprehensive monitoring and alerting script

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.production.yml"
LOG_FILE="${PROJECT_ROOT}/logs/health-check.log"
ALERT_FILE="${PROJECT_ROOT}/logs/alerts.log"

# Service endpoints
FRONTEND_URL="http://localhost:80/health"
BACKEND_URL="http://localhost:8000/health"
BACKEND_DETAILED_URL="http://localhost:8000/health/detailed"
METRICS_URL="http://localhost:8000/metrics"
PROMETHEUS_URL="http://localhost:9090/-/healthy"
GRAFANA_URL="http://localhost:3000/api/health"

# Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=90
DISK_THRESHOLD=85
RESPONSE_TIME_THRESHOLD=5000  # milliseconds
ERROR_RATE_THRESHOLD=5        # percentage

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "${timestamp} [${level}] ${message}" >> "$LOG_FILE"
    
    case $level in
        "ERROR")
            echo -e "${RED}[ERROR]${NC} ${message}" >&2
            echo "${timestamp} [ALERT] ${message}" >> "$ALERT_FILE"
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

# Check if a service is running
check_service_status() {
    local service=$1
    local status=$(docker-compose -f "$COMPOSE_FILE" ps "$service" --format "json" 2>/dev/null | jq -r '.State' 2>/dev/null || echo "not found")
    
    if [[ "$status" == "running" ]]; then
        log "INFO" "✓ $service is running"
        return 0
    else
        log "ERROR" "✗ $service is $status"
        return 1
    fi
}

# Check HTTP endpoint
check_http_endpoint() {
    local url=$1
    local name=$2
    local timeout=${3:-10}
    
    local start_time=$(date +%s%3N)
    local response=$(curl -s -w "HTTP_CODE:%{http_code};TIME:%{time_total}" \
                          --max-time "$timeout" \
                          "$url" 2>/dev/null || echo "HTTP_CODE:000;TIME:999")
    local end_time=$(date +%s%3N)
    
    local http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
    local response_time=$(echo "$response" | grep -o "TIME:[0-9.]*" | cut -d: -f2)
    local response_time_ms=$(echo "$response_time * 1000" | bc -l | cut -d. -f1)
    
    if [[ "$http_code" == "200" ]]; then
        if [[ "$response_time_ms" -gt "$RESPONSE_TIME_THRESHOLD" ]]; then
            log "WARN" "⚠ $name is slow (${response_time_ms}ms)"
        else
            log "INFO" "✓ $name is healthy (${response_time_ms}ms)"
        fi
        return 0
    else
        log "ERROR" "✗ $name failed (HTTP $http_code)"
        return 1
    fi
}

# Check system resources
check_system_resources() {
    log "INFO" "Checking system resources..."
    
    # CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    cpu_usage=${cpu_usage%.*}  # Remove decimal part
    
    if [[ "$cpu_usage" -gt "$CPU_THRESHOLD" ]]; then
        log "ERROR" "High CPU usage: ${cpu_usage}%"
        return 1
    elif [[ "$cpu_usage" -gt $((CPU_THRESHOLD - 10)) ]]; then
        log "WARN" "Elevated CPU usage: ${cpu_usage}%"
    else
        log "INFO" "✓ CPU usage normal: ${cpu_usage}%"
    fi
    
    # Memory usage
    local memory_info=$(free | grep Mem)
    local total_mem=$(echo "$memory_info" | awk '{print $2}')
    local used_mem=$(echo "$memory_info" | awk '{print $3}')
    local memory_usage=$((used_mem * 100 / total_mem))
    
    if [[ "$memory_usage" -gt "$MEMORY_THRESHOLD" ]]; then
        log "ERROR" "High memory usage: ${memory_usage}%"
        return 1
    elif [[ "$memory_usage" -gt $((MEMORY_THRESHOLD - 10)) ]]; then
        log "WARN" "Elevated memory usage: ${memory_usage}%"
    else
        log "INFO" "✓ Memory usage normal: ${memory_usage}%"
    fi
    
    # Disk usage
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [[ "$disk_usage" -gt "$DISK_THRESHOLD" ]]; then
        log "ERROR" "High disk usage: ${disk_usage}%"
        return 1
    elif [[ "$disk_usage" -gt $((DISK_THRESHOLD - 10)) ]]; then
        log "WARN" "Elevated disk usage: ${disk_usage}%"
    else
        log "INFO" "✓ Disk usage normal: ${disk_usage}%"
    fi
    
    return 0
}

# Check database connectivity
check_database() {
    log "INFO" "Checking database connectivity..."
    
    if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" &>/dev/null; then
        log "INFO" "✓ Database is accessible"
        
        # Check database size
        local db_size=$(docker-compose -f "$COMPOSE_FILE" exec -T postgres \
            psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c \
            "SELECT pg_size_pretty(pg_database_size('$POSTGRES_DB'));" 2>/dev/null | tr -d ' ')
        
        log "INFO" "Database size: $db_size"
        return 0
    else
        log "ERROR" "✗ Database is not accessible"
        return 1
    fi
}

# Check Redis connectivity
check_redis() {
    log "INFO" "Checking Redis connectivity..."
    
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping | grep -q "PONG"; then
        log "INFO" "✓ Redis is accessible"
        
        # Check Redis memory usage
        local redis_memory=$(docker-compose -f "$COMPOSE_FILE" exec -T redis \
            redis-cli info memory | grep "used_memory_human" | cut -d: -f2 | tr -d '\r')
        
        log "INFO" "Redis memory usage: $redis_memory"
        return 0
    else
        log "ERROR" "✗ Redis is not accessible"
        return 1
    fi
}

# Check Ollama service
check_ollama() {
    log "INFO" "Checking Ollama service..."
    
    local ollama_health=$(curl -s "http://localhost:11434/api/tags" 2>/dev/null || echo "failed")
    
    if echo "$ollama_health" | grep -q "models"; then
        log "INFO" "✓ Ollama is accessible"
        
        # Check available models
        local model_count=$(echo "$ollama_health" | jq '.models | length' 2>/dev/null || echo "0")
        log "INFO" "Ollama models available: $model_count"
        return 0
    else
        log "ERROR" "✗ Ollama is not accessible"
        return 1
    fi
}

# Check application metrics
check_application_metrics() {
    log "INFO" "Checking application metrics..."
    
    # Get metrics from backend
    local metrics=$(curl -s "$METRICS_URL" 2>/dev/null || echo "failed")
    
    if [[ "$metrics" != "failed" ]]; then
        # Check error rate
        local error_requests=$(echo "$metrics" | grep 'http_requests_total{.*status_code="5' | awk -F' ' '{sum+=$2} END {print sum+0}')
        local total_requests=$(echo "$metrics" | grep 'http_requests_total{' | awk -F' ' '{sum+=$2} END {print sum+0}')
        
        if [[ "$total_requests" -gt 0 ]]; then
            local error_rate=$(echo "scale=2; $error_requests * 100 / $total_requests" | bc -l)
            local error_rate_int=${error_rate%.*}
            
            if [[ "$error_rate_int" -gt "$ERROR_RATE_THRESHOLD" ]]; then
                log "ERROR" "High error rate: ${error_rate}%"
                return 1
            else
                log "INFO" "✓ Error rate normal: ${error_rate}%"
            fi
        else
            log "INFO" "✓ No requests processed yet"
        fi
        
        # Check concurrent requests
        local concurrent_requests=$(echo "$metrics" | grep 'http_requests_concurrent' | awk '{print $2}')
        log "INFO" "Concurrent requests: ${concurrent_requests:-0}"
        
        return 0
    else
        log "ERROR" "✗ Could not retrieve application metrics"
        return 1
    fi
}

# Check Docker resources
check_docker_resources() {
    log "INFO" "Checking Docker container resources..."
    
    # Get container stats
    local container_stats=$(docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}")
    
    echo "$container_stats" | tail -n +2 | while read -r line; do
        local container=$(echo "$line" | awk '{print $1}')
        local cpu_perc=$(echo "$line" | awk '{print $2}' | sed 's/%//')
        local mem_usage=$(echo "$line" | awk '{print $3}')
        
        # Extract numeric CPU percentage
        cpu_perc=${cpu_perc%.*}
        
        if [[ "$cpu_perc" -gt 80 ]]; then
            log "WARN" "Container $container high CPU: ${cpu_perc}%"
        fi
        
        log "DEBUG" "Container $container - CPU: ${cpu_perc}%, Memory: $mem_usage"
    done
}

# Check log files for errors
check_logs_for_errors() {
    log "INFO" "Checking recent logs for errors..."
    
    local log_dirs=("${PROJECT_ROOT}/logs/backend" "${PROJECT_ROOT}/logs/nginx")
    local error_count=0
    
    for log_dir in "${log_dirs[@]}"; do
        if [[ -d "$log_dir" ]]; then
            # Check for errors in the last 5 minutes
            local recent_errors=$(find "$log_dir" -name "*.log" -mmin -5 -exec grep -l "ERROR\|CRITICAL\|FATAL" {} \; 2>/dev/null | wc -l)
            
            if [[ "$recent_errors" -gt 0 ]]; then
                error_count=$((error_count + recent_errors))
                log "WARN" "Found errors in recent logs: $log_dir"
            fi
        fi
    done
    
    if [[ "$error_count" -gt 0 ]]; then
        log "WARN" "Total log files with recent errors: $error_count"
        return 1
    else
        log "INFO" "✓ No recent errors in logs"
        return 0
    fi
}

# Send alert email
send_alert() {
    local subject="$1"
    local message="$2"
    
    if [[ -n "${ALERT_EMAIL_TO:-}" ]] && [[ -n "${SMTP_HOST:-}" ]]; then
        echo "$message" | mail -s "$subject" "$ALERT_EMAIL_TO" 2>/dev/null || {
            log "WARN" "Failed to send alert email"
        }
    fi
}

# Generate health report
generate_health_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="${PROJECT_ROOT}/logs/health-report-$(date +%Y%m%d).json"
    
    local services_status="{"
    local overall_status="healthy"
    
    # Check each service
    local services=("frontend" "backend" "postgres" "redis" "ollama")
    for service in "${services[@]}"; do
        if check_service_status "$service" &>/dev/null; then
            services_status+='"'$service'":"running",'
        else
            services_status+='"'$service'":"failed",'
            overall_status="unhealthy"
        fi
    done
    services_status="${services_status%,}}"
    
    # Get system metrics
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//' | cut -d'.' -f1)
    local memory_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    # Create JSON report
    cat > "$report_file" << EOF
{
  "timestamp": "$timestamp",
  "overall_status": "$overall_status",
  "services": $services_status,
  "system_metrics": {
    "cpu_usage_percent": $cpu_usage,
    "memory_usage_percent": $memory_usage,
    "disk_usage_percent": $disk_usage
  },
  "endpoints": {
    "frontend_health": "$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "000")",
    "backend_health": "$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL" 2>/dev/null || echo "000")",
    "prometheus_health": "$(curl -s -o /dev/null -w "%{http_code}" "$PROMETHEUS_URL" 2>/dev/null || echo "000")"
  }
}
EOF
    
    log "INFO" "Health report generated: $report_file"
}

# Main health check function
main_health_check() {
    local start_time=$(date '+%Y-%m-%d %H:%M:%S')
    local failed_checks=0
    
    log "INFO" "Starting comprehensive health check at $start_time"
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$(dirname "$ALERT_FILE")"
    
    # Load environment if available
    if [[ -f "${PROJECT_ROOT}/.env.production" ]]; then
        set -a
        source "${PROJECT_ROOT}/.env.production"
        set +a
    fi
    
    # Service status checks
    log "INFO" "=== Service Status Checks ==="
    local services=("frontend" "backend" "postgres" "redis" "ollama")
    for service in "${services[@]}"; do
        check_service_status "$service" || ((failed_checks++))
    done
    
    # HTTP endpoint checks
    log "INFO" "=== HTTP Endpoint Checks ==="
    check_http_endpoint "$FRONTEND_URL" "Frontend" || ((failed_checks++))
    check_http_endpoint "$BACKEND_URL" "Backend" || ((failed_checks++))
    check_http_endpoint "$PROMETHEUS_URL" "Prometheus" || ((failed_checks++))
    check_http_endpoint "$GRAFANA_URL" "Grafana" || ((failed_checks++))
    
    # System resource checks
    log "INFO" "=== System Resource Checks ==="
    check_system_resources || ((failed_checks++))
    
    # Application-specific checks
    log "INFO" "=== Application-Specific Checks ==="
    check_database || ((failed_checks++))
    check_redis || ((failed_checks++))
    check_ollama || ((failed_checks++))
    check_application_metrics || ((failed_checks++))
    
    # Docker resource checks
    log "INFO" "=== Docker Resource Checks ==="
    check_docker_resources
    
    # Log checks
    log "INFO" "=== Log Analysis ==="
    check_logs_for_errors || ((failed_checks++))
    
    # Generate report
    generate_health_report
    
    # Summary
    local end_time=$(date '+%Y-%m-%d %H:%M:%S')
    log "INFO" "Health check completed at $end_time"
    
    if [[ "$failed_checks" -eq 0 ]]; then
        log "INFO" "✓ All health checks passed"
        exit 0
    else
        log "ERROR" "✗ $failed_checks health checks failed"
        
        # Send alert if configured
        send_alert "StreamWorks-KI Health Check Alert" \
                  "Health check failed with $failed_checks issues. Check logs for details."
        
        exit 1
    fi
}

# Handle script arguments
case "${1:-check}" in
    "check")
        main_health_check
        ;;
    "services")
        log "INFO" "Checking service status only..."
        services=("frontend" "backend" "postgres" "redis" "ollama")
        for service in "${services[@]}"; do
            check_service_status "$service"
        done
        ;;
    "endpoints")
        log "INFO" "Checking HTTP endpoints only..."
        check_http_endpoint "$FRONTEND_URL" "Frontend"
        check_http_endpoint "$BACKEND_URL" "Backend"
        check_http_endpoint "$PROMETHEUS_URL" "Prometheus"
        ;;
    "resources")
        log "INFO" "Checking system resources only..."
        check_system_resources
        check_docker_resources
        ;;
    "report")
        generate_health_report
        cat "${PROJECT_ROOT}/logs/health-report-$(date +%Y%m%d).json" | jq .
        ;;
    *)
        echo "Usage: $0 {check|services|endpoints|resources|report}"
        echo "  check     - Full health check (default)"
        echo "  services  - Check service status only"
        echo "  endpoints - Check HTTP endpoints only"
        echo "  resources - Check system resources only"
        echo "  report    - Generate and display health report"
        exit 1
        ;;
esac