.PHONY: dev dev-backend dev-frontend infra install migrate docker-up docker-down docker-logs docker-rebuild docker-status

# ── Docker (Production / Server-Deployment) ──────────────────────────

# Alles starten: Qdrant + MinIO + Backend + Frontend
docker-up:
	docker compose up --build -d
	@echo ""
	@echo "Streamworks-KI laeuft:"
	@echo "  Frontend:      http://localhost:3000"
	@echo "  Backend API:   http://localhost:8000"
	@echo "  Health Check:  http://localhost:8000/health"
	@echo "  MinIO Console: http://localhost:9001"
	@echo ""
	@echo "Logs: make docker-logs"

# Alles stoppen
docker-down:
	docker compose down

# Logs aller Services verfolgen
docker-logs:
	docker compose logs -f

# Neu bauen (nach Code-Aenderungen)
docker-rebuild:
	docker compose up --build -d --force-recreate backend frontend

# Status aller Container anzeigen
docker-status:
	docker compose ps

# ── Lokale Entwicklung ───────────────────────────────────────────────

# Nur Infrastruktur starten (Qdrant + MinIO)
infra:
	docker compose up qdrant minio -d

# Alle Dependencies installieren
install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

# Backend starten (eigenes Terminal)
dev-backend:
	cd backend && python main.py

# Frontend starten (eigenes Terminal)
dev-frontend:
	cd frontend && npm run dev

# Hinweise fuer lokale Entwicklung
dev:
	@echo "Lokale Entwicklung (3 Terminals):"
	@echo "  1. make infra        # Qdrant + MinIO starten"
	@echo "  2. make dev-backend  # FastAPI auf :8000"
	@echo "  3. make dev-frontend # Next.js auf :3000"
	@echo ""
	@echo "Oder alles in Docker:  make docker-up"

# SQL-Migrationen ausfuehren
migrate:
	@echo "Run migrations in Supabase SQL Editor:"
	@echo "  backend/migrations/001_sessions.sql"
	@echo "  backend/migrations/002_streams.sql"
	@echo "  backend/migrations/003_dropdown_options.sql"
	@echo "  backend/migrations/004_chat.sql"
	@echo "  backend/migrations/005_seed_data.sql"
