#!/bin/bash
# Einfacher Start für Docker-Test

set -e

echo "🐳 Docker Simple Test"
echo "===================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Docker Status prüfen
print_info "Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

print_status "Docker is running"

# Einfacher Start
print_info "Starting simple PostgreSQL setup..."

cd "$(dirname "$0")/.."
docker compose -f docker-compose.simple.yml up -d

print_info "Waiting for PostgreSQL..."
sleep 10

if docker compose -f docker-compose.simple.yml ps postgres | grep -q "healthy\|Up"; then
    print_status "PostgreSQL is running!"
    print_info "pgAdmin: http://localhost:8080"
    print_info "Email: dev@streamworks-ki.local"
    print_info "Password: dev_admin_2025"
else
    echo "❌ PostgreSQL failed to start"
    docker compose -f docker-compose.simple.yml logs postgres
    exit 1
fi