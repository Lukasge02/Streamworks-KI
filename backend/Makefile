# StreamWorks-KI Development Makefile
# Super-efficient development commands

.PHONY: help install test test-unit test-integration test-performance lint format clean dev build docker

# Default target
help:
	@echo "🚀 StreamWorks-KI Development Commands"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make install          Install all dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test            Run all tests"
	@echo "  make test-unit       Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make test-performance Run performance benchmarks"
	@echo "  make test-coverage   Run tests with coverage report"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "  make lint            Run linting (flake8)"
	@echo "  make format          Format code (black + isort)"
	@echo "  make type-check      Run type checking (mypy)"
	@echo "  make security        Security scan (bandit)"
	@echo "  make quality         All quality checks"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make dev             Start development server"
	@echo "  make dev-bg          Start server in background"
	@echo "  make stop            Stop background server"
	@echo ""
	@echo "🏗️ Build & Deploy:"
	@echo "  make build           Build for production"
	@echo "  make docker          Build Docker image"
	@echo "  make docker-run      Run Docker container"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean           Clean temporary files"
	@echo "  make reset           Reset environment"

# Installation
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

# Testing
test:
	@echo "🧪 Running all tests..."
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-unit:
	@echo "🧪 Running unit tests..."
	pytest tests/unit/ -v -m "not slow" --cov=app --cov-report=term

test-integration:
	@echo "🧪 Running integration tests..."
	pytest tests/integration/ -v --cov=app --cov-report=term

test-performance:
	@echo "⚡ Running performance benchmarks..."
	pytest tests/performance/ -v -m performance --tb=short

test-coverage:
	@echo "📊 Running tests with detailed coverage..."
	pytest tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=80

test-fast:
	@echo "🏃 Running fast tests only..."
	pytest tests/unit/ -v -m "not slow" --tb=short

# Code Quality
lint:
	@echo "🔍 Running linting..."
	flake8 app/ tests/ --count --show-source --statistics

format:
	@echo "🎨 Formatting code..."
	black app/ tests/
	isort app/ tests/

type-check:
	@echo "🔍 Running type checking..."
	mypy app/ --ignore-missing-imports

security:
	@echo "🔒 Running security scan..."
	bandit -r app/ -f json -o bandit-report.json || true
	@echo "Security report: bandit-report.json"

quality: lint type-check security
	@echo "✅ All quality checks completed"

# Development
dev:
	@echo "🚀 Starting development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-bg:
	@echo "🚀 Starting development server in background..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
	@echo "Server started. Log: uvicorn.log"

stop:
	@echo "🛑 Stopping development server..."
	pkill -f "uvicorn app.main:app" || echo "No server running"

# Health checks
health:
	@echo "🏥 Checking API health..."
	curl -s http://localhost:8000/health | jq . || echo "Server not running or jq not installed"

health-full:
	@echo "🏥 Full health check..."
	curl -s http://localhost:8000/api/v1/health/ | jq . || echo "Server not running or jq not installed"

# Performance monitoring
metrics:
	@echo "📊 Getting performance metrics..."
	curl -s http://localhost:8000/api/v1/metrics | jq . || echo "Server not running or jq not installed"

profile:
	@echo "⚡ Running performance profiler..."
	python -m cProfile -o profile.stats -m uvicorn app.main:app --host 0.0.0.0 --port 8001 &
	sleep 5
	@echo "Profiler started on port 8001"

# Build & Deploy
build:
	@echo "🏗️ Building for production..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "Build completed"

docker:
	@echo "🐳 Building Docker image..."
	docker build -t streamworks-ki:latest .

docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p 8000:8000 streamworks-ki:latest

# Database operations
db-init:
	@echo "🗄️ Initializing database..."
	python -c "from app.models.database import init_db; import asyncio; asyncio.run(init_db())"

db-reset:
	@echo "🗄️ Resetting database..."
	rm -f streamworks_ki.db
	make db-init

# Maintenance
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -f profile.stats
	rm -f uvicorn.log
	rm -f bandit-report.json
	rm -f performance_report.json

reset: clean
	@echo "🔄 Resetting environment..."
	rm -rf .venv/
	make install-dev
	make db-reset

# CI/CD helpers
ci-test:
	@echo "🤖 Running CI test suite..."
	pytest tests/ --cov=app --cov-report=xml --cov-fail-under=80 -v

ci-quality:
	@echo "🤖 Running CI quality checks..."
	flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
	black app/ --check
	mypy app/ --ignore-missing-imports

# Documentation
docs:
	@echo "📚 Generating documentation..."
	sphinx-build -b html docs/ docs/_build/

docs-serve:
	@echo "📚 Serving documentation..."
	cd docs/_build && python -m http.server 8080

# Git helpers
commit-check:
	@echo "✅ Pre-commit checks..."
	pre-commit run --all-files

push-check: test quality
	@echo "✅ Ready for push!"

# Monitoring
logs:
	@echo "📝 Showing server logs..."
	tail -f uvicorn.log

logs-live:
	@echo "📝 Live server logs..."
	tail -f uvicorn.log | grep -E "(ERROR|WARNING|INFO)"

# Quick development cycle
quick: format lint test-fast
	@echo "🏃 Quick development cycle completed!"

full-check: format lint type-check test test-performance
	@echo "🎯 Full development check completed!"

# Demo & presentation
demo:
	@echo "🎭 Starting demo environment..."
	make dev-bg
	sleep 3
	make health
	@echo "Demo ready at http://localhost:8000"

demo-stop:
	@echo "🎭 Stopping demo..."
	make stop