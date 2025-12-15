# StreamWorks KI - Makefile for easy development and deployment

.PHONY: help dev prod stop clean logs setup test

BACKEND_VENV := $(abspath backend/.venv/bin/python)

PYTHON ?= $(shell \
    if [ -x "$(BACKEND_VENV)" ]; then \
        echo "$(BACKEND_VENV)"; \
    elif command -v /opt/homebrew/bin/python3.10 >/dev/null 2>&1; then \
        echo "/opt/homebrew/bin/python3.10"; \
    elif command -v python3.10 >/dev/null 2>&1; then \
        command -v python3.10; \
    elif command -v python3.11 >/dev/null 2>&1; then \
        command -v python3.11; \
    elif command -v python3 >/dev/null 2>&1; then \
        command -v python3; \
    else \
        command -v python; \
    fi)
PIP := $(PYTHON) -m pip

# Default target
help:
	@echo "StreamWorks KI - Development Commands"
	@echo "======================================"
	@echo "make setup       - Initial setup (install dependencies)"
	@echo "make dev        - Start development environment (local)"
	@echo "make backend    - Start backend only (Python 3.10)"
	@echo "make docker     - Start with Docker Compose"
	@echo "make prod       - Start production environment"
	@echo "make stop       - Stop all services"
	@echo "make clean      - Clean up containers and volumes"
	@echo "make logs       - Show logs from all services"
	@echo "make format     - Format code (Ruff + Prettier)"
	@echo "make verify-db  - Verify database connection"
	@echo "make test       - Run tests"
	@echo "make upload-test - Test document upload"

# Format code
format:
	@echo "🎨 Formatting code..."
	cd backend && $(PYTHON) -m ruff format .
	cd frontend && npm run format

# Verify DB
verify-db:
	@echo "🔍 Verifying DB..."
	cd backend && $(PYTHON) scripts/verify_db.py

# Clean docs
clean-docs:
	@echo "🧹 Cleaning docs..."
	cd backend && $(PYTHON) scripts/cleanup_docs.py

# Seed data
seed:
	@echo "🌱 Seeding data..."
	cd backend && $(PYTHON) scripts/seed_data.py

# Setup development environment
setup:
	@echo "🚀 Setting up StreamWorks KI..."
	cd backend && $(PIP) install -r requirements.txt
	cd frontend && npm install
	cp .env.example .env
	@echo "✅ Setup complete! Edit .env with your API keys"

# Start development (local)
dev:
	@echo "🚀 Starting development environment..."
	@tmux new-session -d -s streamworks-backend 'cd backend && $(PYTHON) -m uvicorn main:app --reload --port 8000'
	@tmux new-session -d -s streamworks-frontend 'cd frontend && npm run dev'
	@echo "✅ Development environment started!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Use 'tmux attach -t streamworks-backend' or 'tmux attach -t streamworks-frontend' to view logs"

# Start backend only with reliable startup script
backend:
	@echo "🚀 Starting backend with Python 3.10..."
	cd backend && ./start_backend.sh

# Start with Docker
docker:
	@echo "🐳 Starting Docker environment..."
	docker-compose up -d
	@echo "✅ Docker environment started!"
	@echo "Waiting for services to be healthy..."
	@sleep 10
	docker-compose ps

# Start production environment
prod:
	@echo "🚀 Starting production environment..."
	docker-compose --profile production up -d
	@echo "✅ Production environment started!"

# Stop all services
stop:
	@echo "🛑 Stopping services..."
	@tmux kill-session -t streamworks-backend 2>/dev/null || true
	@tmux kill-session -t streamworks-frontend 2>/dev/null || true
	docker-compose down
	@echo "✅ All services stopped"

# Clean up Docker
clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Cleanup complete"

# Show logs
logs:
	docker-compose logs -f

# Run tests
test:
	@echo "🧪 Running tests..."
	cd backend && $(PYTHON) -m pytest tests/ -v
	cd frontend && npm test

# Test document upload
upload-test:
	@echo "📄 Testing document upload..."
	@echo "Creating test document..."
	@echo "StreamWorks Test Document\n\nThis is a test document for the RAG system." > test-document.txt
	@echo "Uploading document..."
	@curl -X POST -F "file=@test-document.txt" \
		-F "doctype=manual" \
		-F "tags=test" \
		-F "visibility=internal" \
		-F "language=de" \
		http://localhost:8000/api/upload
	@rm test-document.txt
	@echo "\n✅ Upload test complete"

# Database migrations
migrate:
	@echo "🗄️ Running database migrations..."
	cd backend && alembic upgrade head
	@echo "✅ Migrations complete"

# Backup data
backup:
	@echo "💾 Backing up data..."
	@mkdir -p backups
	docker exec streamworks-postgres pg_dump -U streamworks streamworks_ki > backups/postgres_$(shell date +%Y%m%d_%H%M%S).sql
	tar -czf backups/documents_$(shell date +%Y%m%d_%H%M%S).tar.gz storage/documents/
	@echo "✅ Backup complete"

# Monitor system
monitor:
	@echo "📊 System Monitoring"
	@echo "===================="
	@curl -s http://localhost:8000/api/system/health | jq .
	@echo "\n📚 Documents:"
	@curl -s http://localhost:8000/api/documents | jq length
	@echo "\n💾 Storage:"
	@du -sh storage/documents/ 2>/dev/null || echo "No documents stored"
