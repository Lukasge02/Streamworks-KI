#!/bin/bash
# PostgreSQL Migration - Deployment Script

echo "🚀 Starting PostgreSQL Migration..."

# 1. Start PostgreSQL und pgAdmin
echo "📦 Starting Docker containers..."
docker-compose up -d

# 2. Warten bis PostgreSQL bereit ist
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 30

# 3. Health check
echo "🏥 Checking PostgreSQL health..."
docker exec streamworks-ki-postgres pg_isready -U streamworks -d streamworks_ki
if [ $? -ne 0 ]; then
    echo "❌ PostgreSQL not ready. Waiting longer..."
    sleep 30
fi

# 4. Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install asyncpg psycopg2-binary pandas

# 5. Run migration script
echo "🔄 Running migration script..."
python scripts/migrate_to_postgres.py

# 6. Test setup
echo "🧪 Testing PostgreSQL setup..."
python scripts/test_postgres_setup.py

# 7. Start application
echo "🚀 Starting application..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo "✅ PostgreSQL migration completed!"
echo "🌐 pgAdmin available at: http://localhost:8080"
echo "📊 API docs available at: http://localhost:8000/docs"