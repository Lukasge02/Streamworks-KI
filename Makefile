# StreamWorks-KI Makefile
# Vereinfachte Commands für Development und Production

.PHONY: help dev prod test clean logs status install onboarding

# Default target
.DEFAULT_GOAL := help

# Colors for terminal output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Project configuration
PROJECT_NAME := streamworks-ki
DEV_COMPOSE := docker-compose.dev.yml
PROD_COMPOSE := docker-compose.production.yml

## 🎯 Main Commands

help: ## 📚 Show this help message
	@echo "$(BLUE)StreamWorks-KI Development Commands$(RESET)"
	@echo "=================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)📋 Quick Start:$(RESET)"
	@echo "  make onboarding  # Complete setup for new developers"
	@echo "  make dev         # Start development environment"
	@echo "  make prod        # Deploy to production"
	@echo ""

onboarding: ## 🚀 Complete onboarding for new developers
	@echo "$(BLUE)🎉 Welcome to StreamWorks-KI!$(RESET)"
	@echo "============================="
	@echo ""
	@echo "$(YELLOW)📋 This script will:$(RESET)"
	@echo "  1. Check your system requirements"
	@echo "  2. Set up your development environment"
	@echo "  3. Start all services with Docker"
	@echo "  4. Open development tools"
	@echo "  5. Load test data"
	@echo ""
	@read -p "Press Enter to continue..." dummy
	@$(MAKE) install
	@$(MAKE) dev
	@echo ""
	@echo "$(GREEN)🎉 Onboarding completed!$(RESET)"
	@echo ""
	@$(MAKE) info

dev: ## 🛠️ Start hybrid development environment (Docker DB + local dev)
	@echo "$(BLUE)🛠️ Starting hybrid development environment...$(RESET)"
	@./scripts/dev.sh start

dev-stop: ## ⏹️ Stop development environment
	@echo "$(YELLOW)⏹️ Stopping development environment...$(RESET)"
	@./scripts/dev.sh stop

dev-restart: ## 🔄 Restart development environment
	@echo "$(YELLOW)🔄 Restarting development environment...$(RESET)"
	@./scripts/dev.sh restart

prod: ## 🚀 Deploy to production
	@echo "$(BLUE)🚀 Deploying to production...$(RESET)"
	@./scripts/setup_postgresql.sh
	@docker-compose -f $(PROD_COMPOSE) up -d --build
	@echo "$(GREEN)✅ Production deployment completed!$(RESET)"

## 📊 Monitoring & Logs

logs: ## 📋 Show logs for all services
	@docker-compose -f $(DEV_COMPOSE) logs -f

logs-backend: ## 📋 Show backend logs
	@docker-compose -f $(DEV_COMPOSE) logs -f backend

logs-frontend: ## 📋 Show frontend logs
	@docker-compose -f $(DEV_COMPOSE) logs -f frontend

logs-db: ## 📋 Show database logs
	@docker-compose -f $(DEV_COMPOSE) logs -f postgres

status: ## 📊 Show status of all services
	@echo "$(BLUE)📊 Service Status:$(RESET)"
	@docker-compose -f $(DEV_COMPOSE) ps
	@echo ""
	@echo "$(BLUE)🔍 Health Checks:$(RESET)"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep streamworks-ki

## 🧪 Testing

test: ## 🧪 Run all tests
	@echo "$(BLUE)🧪 Running all tests...$(RESET)"
	@docker-compose -f $(DEV_COMPOSE) exec backend pytest tests/ -v
	@docker-compose -f $(DEV_COMPOSE) exec frontend npm test

test-backend: ## 🧪 Run backend tests
	@docker-compose -f $(DEV_COMPOSE) exec backend pytest tests/ -v

test-frontend: ## 🧪 Run frontend tests
	@docker-compose -f $(DEV_COMPOSE) exec frontend npm test

test-performance: ## ⚡ Run performance tests
	@docker-compose -f $(DEV_COMPOSE) exec backend pytest tests/performance/ -v

## 🔧 Development Tools

shell-backend: ## 🐚 Open backend shell
	@docker-compose -f $(DEV_COMPOSE) exec backend bash

shell-frontend: ## 🐚 Open frontend shell
	@docker-compose -f $(DEV_COMPOSE) exec frontend sh

shell-db: ## 🐚 Open database shell
	@docker-compose -f $(DEV_COMPOSE) exec postgres psql -U streamworks -d streamworks_ki_dev

install: ## 📦 Install/update dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(RESET)"
	@docker-compose -f $(DEV_COMPOSE) exec backend pip install -r requirements-dev.txt || true
	@docker-compose -f $(DEV_COMPOSE) exec frontend npm ci || true

migrate: ## 🔄 Run database migrations
	@echo "$(BLUE)🔄 Running database migrations...$(RESET)"
	@docker-compose -f $(DEV_COMPOSE) exec backend alembic upgrade head

migrate-create: ## 📝 Create new migration
	@read -p "Migration name: " name && \
	docker-compose -f $(DEV_COMPOSE) exec backend alembic revision --autogenerate -m "$$name"

## 🧹 Cleanup

clean: ## 🧹 Clean up containers and volumes
	@echo "$(YELLOW)🧹 Cleaning up...$(RESET)"
	@./scripts/dev-workflow.sh clean

clean-all: ## 🧹 Clean everything (containers, volumes, images)
	@echo "$(RED)🧹 Cleaning everything...$(RESET)"
	@docker-compose -f $(DEV_COMPOSE) down -v --remove-orphans
	@docker-compose -f $(PROD_COMPOSE) down -v --remove-orphans || true
	@docker system prune -af
	@docker volume prune -f

## 📖 Information

info: ## ℹ️ Show development environment information
	@echo "$(BLUE)🌐 StreamWorks-KI Development Environment$(RESET)"
	@echo "========================================"
	@echo ""
	@echo "$(GREEN)🌐 Service URLs:$(RESET)"
	@echo "  Frontend:     http://localhost:3000"
	@echo "  Backend API:  http://localhost:8000"
	@echo "  API Docs:     http://localhost:8000/docs"
	@echo "  pgAdmin:      http://localhost:8080"
	@echo "  ChromaDB:     http://localhost:8001"
	@echo ""
	@echo "$(GREEN)🔐 Database Credentials:$(RESET)"
	@echo "  Host:         localhost:5432"
	@echo "  Database:     streamworks_ki_dev"
	@echo "  Username:     streamworks"
	@echo "  Password:     streamworks_dev_2025"
	@echo ""
	@echo "$(GREEN)🔧 pgAdmin Credentials:$(RESET)"
	@echo "  Email:        dev@streamworks-ki.local"
	@echo "  Password:     dev_admin_2025"
	@echo ""
	@echo "$(GREEN)📁 Useful Commands:$(RESET)"
	@echo "  make logs     # View all logs"
	@echo "  make test     # Run tests"
	@echo "  make shell-*  # Access service shells"
	@echo "  make clean    # Clean up"
	@echo ""

urls: ## 🌐 Open all development URLs
	@echo "$(BLUE)🌐 Opening development tools...$(RESET)"
	@if command -v open >/dev/null 2>&1; then \
		open http://localhost:3000 && \
		open http://localhost:8000/docs && \
		open http://localhost:8080; \
	else \
		echo "Please open these URLs manually:"; \
		echo "  - Frontend: http://localhost:3000"; \
		echo "  - API Docs: http://localhost:8000/docs"; \
		echo "  - pgAdmin: http://localhost:8080"; \
	fi

## 🏗️ Build Commands

build: ## 🏗️ Build all containers
	@echo "$(BLUE)🏗️ Building containers...$(RESET)"
	@docker-compose -f $(DEV_COMPOSE) build

build-backend: ## 🏗️ Build backend container
	@docker-compose -f $(DEV_COMPOSE) build backend

build-frontend: ## 🏗️ Build frontend container
	@docker-compose -f $(DEV_COMPOSE) build frontend

pull: ## ⬇️ Pull latest images
	@echo "$(BLUE)⬇️ Pulling latest images...$(RESET)"
	@docker-compose -f $(DEV_COMPOSE) pull

## 🎛️ Advanced Commands

reset: ## 🔄 Reset entire development environment
	@echo "$(YELLOW)🔄 Resetting development environment...$(RESET)"
	@$(MAKE) clean
	@$(MAKE) dev

backup-db: ## 💾 Backup development database
	@echo "$(BLUE)💾 Creating database backup...$(RESET)"
	@mkdir -p backups
	@docker-compose -f $(DEV_COMPOSE) exec postgres pg_dump -U streamworks streamworks_ki_dev > backups/dev_backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Database backup created in backups/$(RESET)"

restore-db: ## 📥 Restore database from backup
	@echo "$(YELLOW)📥 Available backups:$(RESET)"
	@ls -la backups/*.sql 2>/dev/null || echo "No backups found"
	@read -p "Enter backup filename: " backup && \
	docker-compose -f $(DEV_COMPOSE) exec -T postgres psql -U streamworks -d streamworks_ki_dev < "$$backup"

## 📈 Monitoring

monitor: ## 📈 Show system resource usage
	@echo "$(BLUE)📈 System Resource Usage:$(RESET)"
	@docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

health: ## 🔍 Check health of all services
	@echo "$(BLUE)🔍 Service Health Check:$(RESET)"
	@docker-compose -f $(DEV_COMPOSE) ps | grep -E "(healthy|unhealthy|starting)"