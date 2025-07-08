#!/bin/bash
# StreamWorks-KI PostgreSQL Setup Script
# Automated PostgreSQL migration and setup

set -e

echo "🐘 StreamWorks-KI PostgreSQL Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
SQLITE_DB="$BACKEND_DIR/streamworks_ki.db"

echo -e "${BLUE}📁 Project root: $PROJECT_ROOT${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

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

# Start PostgreSQL with Docker Compose
echo -e "${BLUE}🐘 Starting PostgreSQL container...${NC}"
cd "$PROJECT_ROOT"

if docker-compose up -d postgres; then
    print_status "PostgreSQL container started"
else
    print_error "Failed to start PostgreSQL container"
    exit 1
fi

# Wait for PostgreSQL to be ready
echo -e "${BLUE}⏳ Waiting for PostgreSQL to be ready...${NC}"
timeout=60
counter=0

while [ $counter -lt $timeout ]; do
    if docker-compose exec -T postgres pg_isready -U streamworks -d streamworks_ki &> /dev/null; then
        print_status "PostgreSQL is ready"
        break
    fi
    
    if [ $counter -eq 0 ]; then
        echo -n "Waiting"
    fi
    echo -n "."
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    print_error "PostgreSQL failed to start within $timeout seconds"
    exit 1
fi

echo ""

# Install PostgreSQL dependencies
echo -e "${BLUE}📦 Installing PostgreSQL dependencies...${NC}"
cd "$BACKEND_DIR"

if [ -f "requirements_postgres.txt" ]; then
    if pip install -r requirements_postgres.txt; then
        print_status "PostgreSQL dependencies installed"
    else
        print_error "Failed to install PostgreSQL dependencies"
        exit 1
    fi
else
    print_warning "requirements_postgres.txt not found, using regular requirements.txt"
    pip install asyncpg psycopg2-binary
fi

# Setup environment
echo -e "${BLUE}⚙️  Setting up environment...${NC}"
if [ -f "../.env.postgres" ]; then
    cp "../.env.postgres" ".env"
    print_status "PostgreSQL environment configured"
else
    print_warning ".env.postgres not found, manual configuration needed"
fi

# Run migration if SQLite database exists
if [ -f "$SQLITE_DB" ]; then
    echo -e "${BLUE}🔄 Migrating data from SQLite to PostgreSQL...${NC}"
    
    # Backup SQLite database first
    cp "$SQLITE_DB" "${SQLITE_DB}.backup.$(date +%Y%m%d_%H%M%S)"
    print_status "SQLite database backed up"
    
    # Run migration
    if python3 -m app.scripts.migrate_to_postgresql --sqlite-path "$SQLITE_DB"; then
        print_status "Data migration completed successfully"
    else
        print_error "Data migration failed"
        echo -e "${YELLOW}You can run migration manually with:${NC}"
        echo "cd $BACKEND_DIR"
        echo "python3 -m app.scripts.migrate_to_postgresql --sqlite-path streamworks_ki.db"
    fi
else
    print_warning "No SQLite database found, starting with fresh PostgreSQL setup"
fi

# Test PostgreSQL connection
echo -e "${BLUE}🧪 Testing PostgreSQL connection...${NC}"
cd "$BACKEND_DIR"

if python3 -c "
import asyncio
from app.models.database_postgres import postgres_db_manager

async def test():
    if await postgres_db_manager.initialize():
        health = await postgres_db_manager.get_health_status()
        print(f'Connection: {health[\"status\"]}')
        return health['status'] == 'healthy'
    return False

if asyncio.run(test()):
    print('✅ PostgreSQL connection successful')
else:
    print('❌ PostgreSQL connection failed')
    exit(1)
"; then
    print_status "PostgreSQL connection test passed"
else
    print_error "PostgreSQL connection test failed"
    exit 1
fi

# Performance verification
echo -e "${BLUE}📊 Running performance verification...${NC}"

PERFORMANCE_TEST=$(python3 -c "
import asyncio
import time
from app.models.database_postgres import postgres_db_manager

async def performance_test():
    await postgres_db_manager.initialize()
    
    # Test query performance
    start_time = time.time()
    health = await postgres_db_manager.get_health_status()
    query_time = (time.time() - start_time) * 1000
    
    print(f'Query time: {query_time:.2f}ms')
    print(f'Pool size: {health.get(\"connection_pool\", {}).get(\"pool_size\", \"N/A\")}')
    print(f'Database size: {health.get(\"database_stats\", {}).get(\"database_size_mb\", \"N/A\")}MB')
    
    return query_time < 100  # Should be under 100ms

if asyncio.run(performance_test()):
    print('✅ Performance test passed')
else:
    print('⚠️ Performance test warning - check configuration')
")

if echo "$PERFORMANCE_TEST" | grep -q "✅ Performance test passed"; then
    print_status "Performance verification completed"
else
    print_warning "Performance test had warnings"
fi

# Final summary
echo ""
echo -e "${GREEN}🎉 PostgreSQL Setup Complete!${NC}"
echo "=================================="
echo ""
echo -e "${BLUE}📊 Connection Details:${NC}"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: streamworks_ki"
echo "  User: streamworks"
echo ""
echo -e "${BLUE}🔧 Management Tools:${NC}"
echo "  PgAdmin: http://localhost:8080"
echo "  Email: admin@streamworks-ki.local"
echo "  Password: admin_secure_2025"
echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo "  1. Start the application:"
echo "     cd $BACKEND_DIR"
echo "     python3 -m uvicorn app.main:app --reload --port 8000"
echo ""
echo "  2. Test RAG performance with PostgreSQL"
echo "  3. Monitor query performance in PgAdmin"
echo ""
echo -e "${YELLOW}📝 Note: Update your application to use PostgreSQL config${NC}"
echo "  - Use: from app.core.config_postgres import settings"
echo "  - Use: from app.models.database_postgres import get_postgres_db"

echo ""
echo -e "${GREEN}✅ Setup completed successfully!${NC}"